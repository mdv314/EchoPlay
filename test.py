from RealtimeSTT import AudioToTextRecorder

def process_text(text):
    print(text)

if __name__ == '__main__':
    print("Wait until it says 'speak now'")
    recorder = AudioToTextRecorder(
        model="tiny",
        spinner=True,
        silero_sensitivity=0.9,
        realtime_batch_size=1,
        enable_realtime_transcription=True,
        realtime_model_type="tiny.en",
        post_speech_silence_duration=0.01,
        beam_size_realtime=1,
        allowed_latency_limit=100,
        device="cuda"
    )
    

    # recorder_config = {
    #     'spinner': False,
    #     'download_root': None, # default download root location. Ex. ~/.cache/huggingface/hub/ in Linux
    #     # 'input_device_index': 1,
    #     'model': "tiny",
    #     'realtime_model_type': 'tiny.en', # or small.en or distil-small.en or ...
    #     'language': 'en',
    #     'silero_sensitivity': 0.9,
    #     'webrtc_sensitivity': 2,
    #     'post_speech_silence_duration': 0,
    #     'min_length_of_recording': 5,        
    #     'min_gap_between_recordings': 0,                
    #     'enable_realtime_transcription': True,
    #     'realtime_processing_pause': 0.02,
    #     #'on_realtime_transcription_stabilized': text_detected,
    #     'silero_deactivity_detection': True,
    #     'early_transcription_on_silence': 0,
    #     'beam_size': 1,
    #     'beam_size_realtime': 1,
    #     # 'batch_size': 0,
    #     # 'realtime_batch_size': 0,        
    #     'no_log_file': True,
    # }

    # recorder = AudioToTextRecorder(**recorder_config)

    while True:
        recorder.text(process_text)