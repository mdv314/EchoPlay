import vgamepad as vg
import json
import os
import time
from collections import deque

gamepad = vg.VX360Gamepad()


def generate_map(filename):
    filename_converted = filename+".json"
    json_path = os.path.join("profiles", filename_converted)

    with open(json_path, "r") as file:
        keymap = json.load(file)
    mode = keymap.get("mode")
    action_map = {
        item["keyword"]: deque(item["keymap"])
        for item in keymap.get("keywords", [])
    }
    return action_map, mode

if __name__ == "__main__":
    action_map, mode = generate_map("xbox_controller")
    print("Mode: ", mode)
    print("Action Map: ")
    for action, commands in action_map.items():
        print(f"{action}: {list(commands)}")
    while True:
        if mode == "xbox":
            TEST_input = input("DEV // Input command from map: ")
            execution_items = action_map.get(TEST_input)
            if execution_items:
                iterator = iter(execution_items)
                for item in iterator:
                    if isinstance(item, int) or isinstance(item, float): # If number, sleep for that many seconds
                        print(f"Sleep for {float(item)*1000} ms")
                        time.sleep(float(item))
                    elif item.startswith("press"):
                        new_item = item[5:]
                        print(f"Press: {new_item}")
                        gamepad.press_button(button=getattr(vg.XUSB_BUTTON, new_item))
                        gamepad.update()
                    elif item.startswith("release"):
                        new_item = item[7:]
                        print(f"Release: {new_item}")
                        gamepad.release_button(getattr(vg.XUSB_BUTTON, new_item))
                        gamepad.update()
                    elif item.find("joystick") != -1:
                        x_val = next(iterator)
                        y_val = next(iterator)
                        print(f"Move {item}: X: {x_val}, Y: {y_val}")
                        getattr(gamepad,item)(x_val,y_val)
                        gamepad.update()
                    elif item.find("trigger") != -1:
                        intensity = next(iterator)
                        print(f"Press {item}: intensity: {intensity}")
                        getattr(gamepad,item)(intensity)
                        gamepad.update()
                    else:
                        print(f"Invalid action item: {item}")
            else:
                print(f"Invalid input: {TEST_input}")






# def close_gamepad():
    # todo