from RealtimeSTT import AudioToTextRecorder
import multiprocessing
# from handler import input_cleaner

#delete this later, just for testing synonyms
import string
def input_cleaner(str_inp):
    cleaned = str_inp.translate(str.maketrans('', '', string.punctuation)).lower()
    return " ".join(cleaned.split())


def print_text(text):
    if text:
        # print(f" {text}")
        process_input(text, queue)
        # print(f" {text}")
    else:
        pass

# Gonna remove duplicates before writing (replacement for writer.py)
def process_input(text, queue):
    # use input cleaning function from handler to clean data
    f = open("model_output.txt", "a")
    text = input_cleaner(text)
    input = text.split(' ')
    
    ############# custom data structure #############
    # when the prev list is empty append the current input
    # if len(prev) == 0:
    #     for str in input:
    #         f.write(f"{str} ")
    #         queue.put(str)
    #         prev.append(str)
    #     f.write("\n")
    # # when the list isn't empty
    # else:
    f.write(f"prev before: {prev}\n")
    while prev != input[:len(prev)] and len(prev)>0:
        # the first n words of input (where n is the length of previous)
        prev.pop(0) 
    f.write(f"prev pop: {prev}\n")
    
    for str in input[len(prev):]:
        f.write(f"{str} ")        
        queue.put(str)
        prev.append(str)
    f.write(f"\n prev after: {prev}\n")
    f.write("----------------------------------------------")
    f.write(f"\n")

    f.close()
    pass
    


def placeholder(text):
    pass

def voice_model():
    print("WAIT")
    global prev
    prev = []

    recorder_config = {
        'spinner': False,
        'download_root': None, # default download root location. Ex. ~/.cache/huggingface/hub/ in Linux
        # 'input_device_index': 1,
        'realtime_model_type': 'tiny.en', # or small.en or distil-small.en or ...
        'language': 'en',
        'silero_sensitivity': 0.05,
        'webrtc_sensitivity': 3,
        'post_speech_silence_duration': 10.0,
        'min_length_of_recording': 1.1,        
        'min_gap_between_recordings': 0,                
        'enable_realtime_transcription': True,
        'realtime_processing_pause': 0.0,
        'on_realtime_transcription_update': print_text,
        #'on_realtime_transcription_stabilized': text_detected,
        'silero_deactivity_detection': True,
        'early_transcription_on_silence': 0,
        'beam_size': 5,
        'beam_size_realtime': 1,
        'batch_size': 0,
        'realtime_batch_size': 0,        
        'no_log_file': True,
        'ensure_sentence_ends_with_period': False,
        'ensure_sentence_starting_uppercase': False,
        'print_transcription_time': True,
        'allowed_latency_limit': 5,
        'device': "cuda",
        'desired_overlap_duration': 0.003
    }

    recorder = AudioToTextRecorder(**recorder_config)

    try:
        print("Start yapping")
        while True:
            recorder.text(placeholder)
    except KeyboardInterrupt:
        print("user stopped transcription")
        exit(0)

def run(multiprocessing_queue):
    global queue
    queue = multiprocessing_queue
    f = open("model_output.txt", "w")
    f.write("")
    f.close()
    voice_model()
    # print("In writer.run")
    # while True:
    #     user_inp = "be"
    #     if not user_inp:
    #         continue
    #     else:
    #         print(f"user input {user_inp}")
    #         multiprocessing_queue.put(input_cleaner(user_inp))
    #         break

if __name__ == "__main__":
    queue = multiprocessing.Queue()
    run(queue)