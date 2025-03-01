import string
import sys
import vgamepad as vg
import json
import os
import time
from collections import deque
import multiprocessing

gamepad = vg.VX360Gamepad()

def input_cleaner(str_inp):
    cleaned = str_inp.translate(str.maketrans('', '', string.punctuation)).lower()
    return " ".join(cleaned.split())

# Generates a map from the profile, key: keyword, value: [action1, action2, ...]
def generate_map(filename):
    filename_converted = filename+".json" # converts file name to path

    # looking for defaults
    defaults_dir = os.path.join("profiles","defaults")
    if not os.path.exists(defaults_dir):
            os.makedirs(defaults_dir)
    default_profiles = [os.path.splitext(f)[0] for f in os.listdir(defaults_dir) if os.path.isfile(os.path.join(defaults_dir, f))]
    
    if filename in default_profiles:
        json_path = os.path.join("profiles", "defaults", filename_converted)
    else:
        json_path = os.path.join("profiles", filename_converted)

    with open(json_path, "r") as file:
        keymap = json.load(file)
    mode = keymap.get("mode") # gets mode (stored in default profiles)
    action_map = {
        item["keyword"]: deque(item["keymap"])
        for item in keymap.get("keywords", [])
    } # it just makes a double ended queue for the value with the key being keyword
    return action_map, mode

# multithreading  shared queue
#                 |      selected profile
#                 |      |
def process_queue(queue, profile_name):
        action_map, mode = generate_map(profile_name)
        print("Mode: ", mode)
        print("Action Map: ")
        for action, commands in action_map.items():
            print(f"{action}: {list(commands)}")
        while True:
            # xbox mode
            if mode == "xbox":

                # await input to the shared multithreading queue
                TEST_input = queue.get()
                # stop escape from gui.py / writer.py
                if TEST_input == "STOP":
                    print(f"Handler.py received STOP signal in shared queue. Stopping...")
                    sys.exit()
                # clean input
                TEST_input = input_cleaner(TEST_input)
                print(f"Handler processing: {TEST_input}")

                # get the corresponding actions for the input
                execution_items = action_map.get(TEST_input)

                # if its a valid input (a key in the map)
                if execution_items:
                    iterator = iter(execution_items)
                    for item in iterator:
                        # xbox type handling
                        if isinstance(item, int) or isinstance(item, float): # If number, sleep for that many seconds
                            print(f"Sleep for {float(item)*1000} ms")
                            time.sleep(float(item))
                        elif item.startswith("press"): # pressing any button
                            new_item = item[5:]
                            print(f"Press: {new_item}")
                            gamepad.press_button(button=getattr(vg.XUSB_BUTTON, new_item))
                            gamepad.update()
                        elif item.startswith("release"): # releasing any button
                            new_item = item[7:]
                            print(f"Release: {new_item}")
                            gamepad.release_button(getattr(vg.XUSB_BUTTON, new_item))
                            gamepad.update()
                        elif item.find("joystick") != -1: # joystick inputs
                            x_val = next(iterator)
                            y_val = next(iterator)
                            print(f"Move {item}: X: {x_val}, Y: {y_val}")
                            getattr(gamepad,item)(x_val,y_val)
                            gamepad.update()
                        elif item.find("trigger") != -1: # trigger inputs
                            intensity = next(iterator)
                            print(f"Press {item}: intensity: {intensity}")
                            getattr(gamepad,item)(intensity)
                            gamepad.update()
                        else: # anything else (theres no button not covered here. this is for errors in making a new json file)
                            print(f"Invalid action item: {item}") 
                else: # if the input word is not in the profile as a keyword
                    print(f"Invalid input: {TEST_input}")


if __name__ == "__main__":
    # in case its not ran by gui.py, runs.
    queue = multiprocessing.Queue()
    process_queue(queue)




