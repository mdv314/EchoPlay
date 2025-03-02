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

    # synonyms
    synonyms_path = os.path.join("profiles", "synonyms", "synonyms.json")
    if os.path.exists(synonyms_path):
        with open(synonyms_path, "r") as file:
            synonyms_data = json.load(file)
    else:
        synonyms_data = {"synonyms": []}  

    # Create a synonym lookup dictionary (keyword_match -> list of synonyms)
    synonym_map = {
        entry["keyword_match"]: entry["synonym_words"]
        for entry in synonyms_data.get("synonyms", [])
    }


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
        keymap_data = json.load(file)
    mode = keymap_data.get("mode") # gets mode (stored in default profiles)
    action_map = {}
    for item in keymap_data.get("keywords", []):
        keyword = item["keyword"]
        actions = deque(item["keymap"])

        # add profile mapping
        action_map[keyword] = actions

        # add synonym mappings
        if keyword in synonym_map:
            for synonym in synonym_map[keyword]:
                action_map[synonym] = actions  

    # action_map = {
    #     item["keyword"]: deque(item["keymap"])
    #     for item in keymap_data.get("keywords", [])
    # } # it just makes a double ended queue for the value with the key being keyword
    return action_map, mode



# multithreading  shared queue
#                 |      selected profile
#                 |      |
def process_queue(queue, profile_name, synonym_mode=False):
    action_map, mode = generate_map(profile_name)
    print("Mode: ", mode)
    print("Action Map: ")
    for action, commands in action_map.items():
        print(f"{action}: {list(commands)}")
    
     # If synonym_mode is enabled, enter the configuration routine
    if synonym_mode:
        print(f'=================SYNONYM MODE SYNONYM MODE=================')
        # --- SYNONYM CONFIGURATION PHASE ---
        # Re-load the profile keymap data (to iterate over the original keywords)
        filename_converted = profile_name + ".json"
        defaults_dir = os.path.join("profiles", "defaults")
        if profile_name in [os.path.splitext(f)[0] for f in os.listdir(defaults_dir) if os.path.isfile(os.path.join(defaults_dir, f))]:
            json_path = os.path.join("profiles", "defaults", filename_converted)
        else:
            json_path = os.path.join("profiles", filename_converted)
        with open(json_path, "r") as file:
            keymap_data = json.load(file)

        # Load the existing synonyms file (or create a default structure)
        synonyms_path = os.path.join("profiles", "synonyms", "synonyms.json")
        if os.path.exists(synonyms_path):
            with open(synonyms_path, "r") as file:
                synonyms_data = json.load(file)
        else:
            synonyms_data = {"synonyms": []}

        # Build a lookup: keyword -> list of synonyms
        synonym_lookup = {}
        for entry in synonyms_data.get("synonyms", []):
            synonym_lookup[entry["keyword_match"]] = entry["synonym_words"]

        # For each keyword in the profile, check if it has fewer than 2 synonyms.
        # If so, "prompt" the user (here we simply print a message) and then
        # take all items from the queue as the input string, select the first 3 words,
        # and store that as a synonym for the keyword.
        print(f'Waiting 10 seconds for voice model load up')
        time.sleep(10)
        for item in keymap_data.get("keywords", []):
            keyword = item["keyword"]
            current_syns = synonym_lookup.get(keyword, [])
            while len(current_syns) < 2:
                # Prompt the user to say the keyword once
                # (Replace the following print statement with your actual prompt logic)
                while not queue.empty():
                    trash = queue.get_nowait()
                print(f"Prompt: You have 8 seconds to say the keyword '{keyword}' once.")

                # Empty the queue into a string (words separated by spaces)
                queued_items = []
                time.sleep(8)
                while not queue.empty():
                    queued_items.append(queue.get())
                input_str = " ".join(queued_items)
                words = input_str.split()

                # Only take the first 3 words (if available)
                new_synonym = " ".join(words[:3]) if words else ""
                if new_synonym and new_synonym not in current_syns:
                    current_syns.append(new_synonym)
                    synonym_lookup[keyword] = current_syns
                    print(f"Added new synonym for '{keyword}': '{new_synonym}'")
                print(f"Waiting 4 seconds...")
                time.sleep(4)

        # Write the updated synonyms back to the synonyms file
        updated_synonyms = []
        for key, syns in synonym_lookup.items():
            updated_synonyms.append({"keyword_match": key, "synonym_words": syns})
        synonyms_data["synonyms"] = updated_synonyms
        with open(synonyms_path, "w") as file:
            json.dump(synonyms_data, file, indent=4)

        # Regenerate the action map to include the new synonyms
        action_map, mode = generate_map(profile_name)
        print("Updated Action Map with new synonyms:")
        for action, commands in action_map.items():
            print(f"{action}: {list(commands)}")
        print(f"======= Complete! =======")
        # --- END SYNONYM CONFIGURATION PHASE ---
    else:
        # buffer for inp 1 to 3
        lookahead = []
        while True:
            # xbox mode
            if mode == "xbox":

                # grab next queue item, block and wait if none
                item = queue.get()

                # stop button
                if item == "STOP":
                    print(f"Handler.py received STOP signal in shared queue. Stopping...")
                    sys.exit()
                
                # add item to buffer if not ending execution
                lookahead.append(item)

                # # clean input
                # lookahead[0] = input_cleaner(lookahead[0]) #remove to optimize
                print(f"Handler processing: {item}")

                # debug buffer dump
                for item_print in lookahead:
                    print(f"Buffer: {item_print}")

                # get the corresponding actions for the input
                execution_items = action_map.get(lookahead[0])

                # Stretch goal: implement timeout later
                # if 1 input valid
                if execution_items:
                    handle_xbox(execution_items, queue) # execute 1
                    lookahead.pop(0) # rm 1
                else: # if 1 input invalid
                    if len(lookahead) < 2: # wait
                        continue
                    inp_one_and_two = ' '.join( (lookahead[0], lookahead[1]) ) # input 1 + input 2 with spaces
                    execution_items = action_map.get(inp_one_and_two) # 1 + 2 validity check
                    # if 1 + 2 input valid
                    if execution_items:
                        handle_xbox(execution_items, queue) # execute 1 + 2
                        lookahead.pop(0) # rm 1
                        lookahead.pop(0) # rm 2
                    else: # if 1 + 2 input invalid
                        inp_two = lookahead[1] # input 2
                        execution_items = action_map.get(inp_two) # 2 validity check
                        # if 2 input valid
                        if execution_items:
                            handle_xbox(execution_items, queue) # execute 2
                            lookahead.pop(0) # rm 1
                            lookahead.pop(0) # rm 2
                        else: # if 2 input invalid
                            if len(lookahead) < 3: # wait
                                continue
                            inp_one_and_two_and_three = ' '.join( (lookahead[0], lookahead[1], lookahead[2]) ) # input 1 + input 2 + input 3 with spaces
                            execution_items = action_map.get(inp_one_and_two_and_three) # 1 + 2 + 3 validity check
                            # if 1 + 2 + 3 input valid
                            if execution_items:
                                handle_xbox(execution_items, queue) # execute 1 + 2 + 3 inputs
                                lookahead.pop(0) # rm 1
                                lookahead.pop(0) # rm 2
                                lookahead.pop(0) # rm 3
                            else: # if 1 + 2 + 3 invalid
                                inp_two_three = ' '.join( (lookahead[1], lookahead[2]) ) # input 2 + 3 with spaces
                                execution_items = action_map.get(inp_two_three) # 2 + 3 validity check
                                # if 2 + 3 valid
                                if execution_items:
                                    handle_xbox(execution_items, queue) # execute 2 + 3 inputs
                                    lookahead.pop(0) # rm 1
                                    lookahead.pop(0) # rm 2
                                    lookahead.pop(0) # rm 3
                                else: # 2 + 3 non-valid
                                    lookahead.pop(0) # rm 1
                                    lookahead.pop(0) # rm 2
                                
                                    





def handle_xbox(execution_items, queue):
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


if __name__ == "__main__":
    # in case its not ran by gui.py, runs.
    queue = multiprocessing.Queue()
    process_queue(queue)




