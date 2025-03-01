from RealtimeSTT import AudioToTextRecorder

def print_text(text):
    print(text)

def process_text(text):
    pass

if __name__ == '__main__':
    print("WAIT")

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
        'beam_size_realtime': 3,
        'batch_size': 0,
        'realtime_batch_size': 0,        
        'no_log_file': True,
        'ensure_sentence_ends_with_period': False,
        'ensure_sentence_starting_uppercase': False,
        'print_transcription_time': True,
        'allowed_latency_limit': 5,
        'disable_final_transcription': True,
    }

    recorder = AudioToTextRecorder(**recorder_config)

    try:
        while True:
            recorder.text(process_text)
    except KeyboardInterrupt:
        print("user stopped transcription")
        exit(0)