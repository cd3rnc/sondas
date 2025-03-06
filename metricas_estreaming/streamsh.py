import subprocess

url = extract_youtube_url()[1]
resolution = " best"
script_path = "./execute_streaming.sh "+url+best
subprocess.run(["bash", script_path], text=True)
