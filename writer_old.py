import multiprocessing
import time
import json
import os
import sys

def write_to_queue(queue):
    """Writes messages to the queue."""
    time.sleep(1)
    json_path = os.path.join("profiles", "defaults", "xbox_controller.json")
    messages = extract_keywords(json_path)
    for i in range(len(messages)):
        queue.put(messages[i])
        print("writer: "+ messages[i])
        time.sleep(0.1)  # Simulate delay

    queue.put("STOP")  # Send stop signal to handler
    sys.exit()

def extract_keywords(json_file):
    """Reads a JSON file and extracts all keywords into a list."""
    with open(json_file, "r") as file:
        data = json.load(file)  # Load JSON data

    keywords = [entry["keyword"] for entry in data.get("keywords", [])]  # Extract keywords
    return keywords

if __name__ == "__main__":
    queue = multiprocessing.Queue()
    write_to_queue(queue)