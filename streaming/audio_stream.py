import queue
import sounddevice as sd


class AudioStream:

    def __init__(
        self,
        sample_rate=16000,
        chunk_size=1024
    ):

        self.sample_rate = sample_rate
        self.chunk_size = chunk_size

        self.audio_queue = queue.Queue()

        self.stream = None
        self.running = False

    def _audio_callback(
        self,
        indata,
        frames,
        time,
        status
    ):
        if status:
            print(status)

        self.audio_queue.put(indata.copy())

    def start(self):

        if self.running:
            return

        self.running = True

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.chunk_size,
            callback=self._audio_callback
        )

        self.stream.start()

        print("Audio stream started.")

    def stop(self):

        self.running = False

        if self.stream:
            self.stream.stop()
            self.stream.close()

        print("Audio stream stopped.")

    def get_chunk(self):

        return self.audio_queue.get()