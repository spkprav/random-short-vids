import os
import subprocess
import re
import requests

# Import the necessary libraries
import ffmpeg

headers = {
    "Authorization": "<pexel API key>"
}

texts = [{
    "video": "waves crashing",
    "seconds": 3,
    "text": "Fact #1\nThe sound of waves crashing \nreduces stress and improves mood." # max 5 words & 3 lines
}, {
    "video": "counting money",
    "seconds": 3,
    "text": "Fact #2\nCounting money activates\npleasure center in the brain."
}, {
    "video": "indian food",
    "seconds": 3,
    "text": "Fact #3\nIndian food spices boost\nmetabolism and help digestion."
}, {
    "video": "storytelling",
    "seconds": 3,
    "text": "Fact #4\nStorytelling engages multiple areas\nof the brain and builds empathy."
}]

for i, data in enumerate(texts):
    params = {
        "query": data['video'],
        "per_page": 1,
        "orientation": "portrait"
    }
    response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
    video_files = response.json()['videos'][0]['video_files']
    video = next(obj for obj in video_files if obj['width'] == 1080)
    video_url = video['link']
    (
        ffmpeg
        .input(video_url)
        .filter('crop', 'ih*9/16', 'ih')
        .filter('scale', '720', '-2')
        .filter('fps', '25')
        .output(f"input.mp4")
        .run()
    )
    subprocess.run(['ffmpeg', '-t', f"{data['seconds']}", '-i', 'input.mp4', '-acodec', 'copy', f"trimmed_{i}.mp4"])
    subprocess.run(['ffmpeg', '-i', f"trimmed_{i}.mp4", '-vf', f"format=yuv444p, drawbox=y=ih/PHI:color=black@0.4:width=iw:height=250:t=fill, drawtext=fontfile=OpenSans-Regular.ttf:text=\'{data['text']}\':fontcolor=white:fontsize=32:x=(w-tw)/2:y=(h/PHI)+th, format=yuv420p", '-c:v', 'libx264', '-c:a', 'copy', '-movflags', '+faststart', f"input_{i}.mp4"])
    os.remove('input.mp4')
    os.remove(f"trimmed_{i}.mp4")

input_paths = [f for f in sorted(os.listdir()) if f.startswith('input_') and f.endswith('.mp4')]

open('concat.txt', 'w').writelines([('file %s\n' % input_path) for input_path in input_paths])

concat_command = f"ffmpeg -f concat -i concat.txt -c copy final.mp4"
os.system(concat_command)

os.remove('concat.txt')

for f in input_paths:
    os.remove(f)

print("Done! The output video is saved as final.mp4")


