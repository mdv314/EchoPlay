from RealtimeSTT import AudioToTextRecorder

def process_text(text):
    print(text)

if __name__ == '__main__':
    print("Wait until it says 'speak now'")
    recorder = AudioToTextRecorder(
        model="tiny",
        silero_sensitivity=0.9,
        realtime_batch_size=8,
        enable_realtime_transcription=True,
        realtime_model_type="tiny.en",
        post_speech_silence_duration=0.01,
        beam_size_realtime=1,
        allowed_latency_limit=50
    )

    while True:
        recorder.text(process_text)