import subprocess

def run_ffmpegp_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"Running command: {command}")
        # print(result.stdout)  # This will print the captured standard output
        if result.returncode == 0:
            print("Command executed successfully.\n")
        else:
            print(f"Command failed with error: {result.stderr}\n")
    except Exception as e:
        print(f"Error executing command: {e}\n")


def test_ffmpegp_commands():
    # List of ffmpegp commands to test
    commands = [
        # Convert video to mp4
        "ffmpegp -i sample/input.avi output/output.mp4",
        
        # Extract audio from video
        "ffmpegp -i sample/input.mp4 -q:a 0 -map a output/output.mp3",
        
        # Resize video
        "ffmpegp -i sample/input.mp4 -vf scale=1280:720 output/output_720p.mp4",
        
        # Convert audio format
        "ffmpegp -i sample/input.mp2 output/output.wav",
        
        # Create video from images
        # "ffmpegp -framerate 1 -i img%d.jpg -c:v libx264 -r 30 -pix_fmt yuv420p slideshow.mp4",
        
        # Add watermark to video
        "ffmpegp -i sample/input.mp4 -i sample/input.png -filter_complex 'overlay=10:10' output/output_watermarked.mp4",
        
        # Merge audio and video
        "ffmpegp -i sample/input.mp4 -i sample/audio.mp3 -c:v copy -c:a aac output/output_with_audio.mp4",
        
        # Extract frames from video
        "ffmpegp -i sample/input.mp4 -vf fps=1 output/frame%d.png",
        
        # Compress video (reduce quality)
        "ffmpegp -i sample/input.mp4 -vcodec libx265 -crf 28 output/compressed.mp4",
        
        # Convert video to GIF
        "ffmpegp -i sample/input.mp4 output/output.gif"
    ]

    for command in commands:
        run_ffmpegp_command(command)

if __name__ == "__main__":
    test_ffmpegp_commands()

