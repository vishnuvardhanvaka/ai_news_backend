
import subprocess
import threading
from fastapi import FastAPI, WebSocket
import nest_asyncio
# from pyngrok import ngrok
import uvicorn
from asyncio import sleep

app = FastAPI()


class StreamProcess:
    def __init__(self, video_path, stream_key):
        self.video_path = video_path
        self.stream_key = stream_key
        self.process = None
        self.stop_event = threading.Event()

    def start(self):
        args = [
            '-stream_loop', '-1',
            '-re',
            '-i', self.video_path,
            '-c', 'copy',
            '-f', 'flv',
            '-fflags', 'nobuffer',
            '-flags', 'low_delay',
            f'rtmp://a.rtmp.youtube.com/live2/{self.stream_key}'
        ]
        self.process = subprocess.Popen(['ffmpeg'] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    def check_stream(self):
      if self.process and self.process.poll() is None:
        # print("Streaming process running")
        return True
      # print("Streaming process stopped")
      return False
    def stop(self):
        if self.process and self.process.poll() is None:
            self.stop_event.set()  # Signal the thread to stop
            self.process.terminate()  # Terminate the ffmpeg process

def stream_video(video_path, stream_key):
    stream_process = StreamProcess(video_path, stream_key)
    stream_thread = threading.Thread(target=stream_process.start)
    stream_thread.start()
    return stream_process



stream_process = None

@app.get('/startStreaming')
async def startStreaming():
    global stream_process
    video_path='./news_video.mp4'
    stream_key='68p2-txmk-79sm-hjfh-2d26'
    stream_process = stream_video(video_path,stream_key)
    return {"stream_status":stream_process.check_stream()}

@app.get('/stopStreaming')
async def stopStreaming():
    global stream_process
    if stream_process:
        stream_process.stop()
    return {"stream_status":stream_process.check_stream()}



