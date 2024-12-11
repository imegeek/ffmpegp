import os
import re
import sys
import json
import time
import shutil
import subprocess
import threading
from jsonpath_ng import parse

ffmpeg_path = shutil.which("ffmpeg")
ffprobe_path = shutil.which("ffprobe")
prev_bar_fill_length = None
input_filenames = []
error = True
stdline = []

if not ffmpeg_path:
    print(f"'\33[92mffmpeg\33[0m' \33[91mis not installed. Cannot continue.\33[0m")
    sys.exit(-1)

if ffmpeg_path and not ffprobe_path:
    print(f"'\33[92mffprobe\33[0m' \33[91mis missing. Cannot continue.\33[0m")
    sys.exit(-1)

def get_media_details(file_path):
    # Use ffprobe (a tool bundled with ffmpeg) to extract media details
    command = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', file_path
    ]
    
    try:
        # Run the command
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            print(f"Error occurred: {result.stderr}")
            return None

        # Parse the JSON result
        media_info = json.loads(result.stdout)
        return media_info
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def query_json(json_data, json_path):
    try:
        # Parse and apply the JSON path query
        jsonpath_expr = parse(json_path)
        result = [match.value for match in jsonpath_expr.find(json_data)]
        return result if result else None
    except Exception as e:
        print(f"Invalid JSON path or error: {e}")
        return None

def extract_output(path) -> str:
    output_filename, output_extension = os.path.splitext(path)
    output_directory, output_template = os.path.split(output_filename)
    return output_directory, output_filename, output_template, output_extension

def gradient_text(word, colors):
    """
    Apply multiple gradients to the given text.

    :param word: The word to apply the gradient to.
    :param colors: A list of tuples, each representing an RGB color for the gradients.
    :return: A string with the text colored according to the gradients.
    """

    if len(word) < 2 or len(colors) < 2:
        color = list(map(str, colors[0]))
        return f'\033[38;2;{";".join(color)}m{word}\033[0m'

    gradient_str = ""
    num_segments = len(colors) - 1
    segment_length = len(word) // num_segments
    remainder = len(word) % num_segments

    # Generate the gradient for each segment
    for segment_index in range(num_segments):
        start_color = colors[segment_index]
        end_color = colors[segment_index + 1]
        segment_size = segment_length + (1 if segment_index < remainder else 0)

        if segment_size > 1:
            step = [(end_color[i] - start_color[i]) / (segment_size - 1) for i in range(3)]
        else:
            step = [0, 0, 0]  # No transition needed if only one character in this segment

        for i in range(segment_size):
            char_index = segment_index * segment_length + min(segment_index, remainder) + i
            r = int(start_color[0] + step[0] * i)
            g = int(start_color[1] + step[1] * i)
            b = int(start_color[2] + step[2] * i)
            gradient_str += f'\033[38;2;{r};{g};{b}m{word[char_index]}\033[0m'
    
    return gradient_str

def duration_to_seconds(duration):
    h, m, s = map(float, duration.split(':'))
    return h * 3600 + m * 60 + s

def extract_time(log_line):
    # Define the regular expression pattern to extract the time
    time_pattern = r"time=(\d{2}:\d{2}:\d{2}\.\d{2})"
    
    # Search for the pattern in the log line
    match = re.search(time_pattern, log_line)
    
    # If a match is found, return the extracted time
    if match:
        return match.group(1)
    else:
        return "N/A"

def get_readable_file_size(file_path):
    size_bytes = os.path.getsize(file_path)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024

def print_progress_bar(start_time, iteration, total, pos_args, prefix='', suffix='', done='Complete', decimals=1, length=30, fill='━'):
    global prev_bar_fill_length

    if suffix:
        suffix = f"| {suffix} |"
    else:
        suffix = "|"

    if done:
        if "--colored" in pos_args:
            colors = [(255, 255, 100), (100, 200, 255)] # Yellow -> Cyan
            done = f"| {gradient_text(done, colors)} |"
        else:
            done = f"| \33[92m{done}\33[0m |"
    else:
        done = "|"

    color = "\33[93m"
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)

    # Capture end time
    end_time = time.time()

    # Calculate elapsed time
    elapsed_time = end_time - start_time

    # Format the difference as HH:MM:SS
    formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))

    if "--colored" in pos_args:
        colors = [(100, 200, 255), (255, 255, 100)]  # Cyan -> Yellow
        formatted_time = gradient_text(formatted_time, colors)
        colors = [(100, 200, 255), (255, 100, 255), (255, 255, 100)]  # Cyan -> Pink -> Yellow
        bar = f"{gradient_text(fill * filled_length, colors)}" + f'\33[90m{fill}\33[0m' * (length - filled_length)
    else:
        if float(percent) >= 30:
            color = "\33[92m"
        formatted_time = f"\33[96m{formatted_time}\33[0m"
        bar = f"{color}{fill * filled_length}" + f'\33[90m{fill}\33[0m' * (length - filled_length)

    if "--stdout" in pos_args:
        bar_fill = re.sub(r'\x1B\[[^m]*m', '', f"{prefix}progress={percent}% {suffix.replace("|", "").strip()} time={formatted_time}")
    else:
        bar_fill = f"{prefix}{bar} {percent}% {suffix} {formatted_time}"

    bar_fill_length = len(re.sub(r'\x1B\[[^m]*m', '', bar_fill))
        
    if prev_bar_fill_length is not None and bar_fill_length != prev_bar_fill_length:
        sys.stdout.write("\r" + " " * prev_bar_fill_length)
    prev_bar_fill_length = bar_fill_length

    sys.stdout.write(f'\r' + bar_fill)

    # Print New Line on Complete
    if iteration == total or int(round(float(percent), 0)) == 100:
        if "--colored" in pos_args:
            bar = gradient_text(fill * length, colors)
        else:
            bar = f"{color}{fill}\33[0m" * length

        if "--stdout" in pos_args:
            bar_fill = re.sub(r'\x1B\[[^m]*m', '', f"{prefix}progress=100% {suffix.replace("|", "").strip()} time={formatted_time}")
        else:
            bar_fill = f"{prefix}{bar} 100% {done} {formatted_time}"
            
        sys.stdout.write("\r" + " " * bar_fill_length)
        sys.stdout.write(f"\r" + bar_fill)
        return "OK"

def check_file(output_filename, output_path, pos_args, skip=False):
    if output_filename and os.path.exists(output_path):
        if '-y' not in pos_args:
            output_filename = output_filename.replace("\"", "")
            q = input(f"File \"{output_filename}\" already exists. Overwrite? [y/N] ").lower()
            if q and q != "y":
                if not skip:
                    sys.exit(0)
                else:
                    return True


def read_pipe(process, pipe, pos_args, input_file, prefix):
    global error, stdline
    progress = None
    frame = False
    stream = False

    while True:
        line = pipe.readline()
        if not line:
            break
        text = line.strip()
        stdline.append(text)

        if "Duration" in text and not stream:
            # Capture start time
            start_time = time.time()

            # Scrap total_duration
            total_duration = text.split()[1].strip(",")
            stream = True

        if stream and ("frame=" in text.split() or "size=" in text or "time=" in text):
            part_duration = extract_time(text)
            speed = text.split()[-1].split("=")[-1]

            if part_duration != "N/A" or speed != "N/A":
                try:
                    # Convert durations to seconds
                    total_seconds = duration_to_seconds(total_duration)
                    part_seconds = duration_to_seconds(part_duration)
                    iteration, total = map(lambda x : round(x, 0), [part_seconds, total_seconds])
                    frame = True

                    if error:
                        if '--log' in pos_args:
                            print("\n".join(stdline[:-1]))
                        else:
                            for index, path in enumerate(input_file):
                                inputs = []
                                path = path.replace("\"", "")
                                if "--stdout" in pos_args:
                                    inputs.append(f"input{index}:\"{path}\"")
                                else:
                                    print(f"Input #{index}: from \"{path}\"")

                            # if "--stdout" in pos_args:
                            #     print(json.dumps({
                            #         "input": inputs
                            #     }))
                    
                    if "--stdout" in pos_args:
                        suffix = f"speed={speed}"
                    elif "--colored" in pos_args:
                        colors = [(240, 120, 255), (255, 250, 100)]  # Pink -> Yellow
                        suffix = f'{gradient_text(f"speed:{speed}", colors)}'
                    else:
                        suffix = f"\33[92mspeed:{speed}\33[0m"

                    progress = print_progress_bar(start_time, iteration, total, pos_args, prefix=prefix, suffix=suffix)
                    if progress == "OK":
                        break
                    error = False
                except Exception:
                    break

    # Close the pipe after reading
    pipe.close()

    # Wait for the process to complete
    process.wait()

    if process.returncode == 0 and stream and frame and progress != "OK":
        print_progress_bar(start_time, total, total, pos_args, prefix=prefix, suffix=suffix)

def start_process(args, pos_args, input_file, prefix='', pid=None):
    global error, stdline

    try:
        command = f"ffmpeg {' '.join(args)}"
        if input_filenames:
            command = command + " -y"
        process = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, text=True, encoding='utf-8')
        pid = process.pid

        # Threads to read stdout and stderr
        stdout_thread = threading.Thread(target=read_pipe, args=(process, process.stdout, pos_args, input_file, prefix))
        stderr_thread = threading.Thread(target=read_pipe, args=(process, process.stderr, pos_args, input_file, prefix))

        # Start the threads
        stdout_thread.start()
        stderr_thread.start()

        # Wait for both threads to complete
        stdout_thread.join()
        stderr_thread.join()
                
        if error:
            output = "\n".join(stdline)
            print(output.replace("usage: ffmpeg", f"usage: ffmpegp").strip())
        else:
            print()

        # Set global variables to their initial values.
        error = True
        stdline = []

    except (EOFError, KeyboardInterrupt):
        if pid:
            try:
                os.kill(process.pid, 9)
            except Exception:
                pass
        print("\nProgram interrupted!")
        sys.exit(1)

try:
    raw_args = sys.argv[1:]
except Exception:
    pass

def main():    
    try:
        args = []
        pos_args = []
        mode = "single"
        skip_pos_args = ["--colored", "--stdout", "help", "--log", "-y"]
        skip_opt_args = ["--jq", "--dir", "--format="]
        opt_args = {key.rstrip('='): [] for key in skip_opt_args}

        for arg in skip_pos_args:
            if arg in raw_args:
                pos_args.append(arg)
                raw_args.remove(arg)

        for index, arg in enumerate(raw_args):
            for key in opt_args:
                if arg == key.rstrip('='):
                    pos_args.append(arg)
                    if index + 1 < len(raw_args):
                        next_arg = raw_args[index + 1]
                        if not next_arg.startswith("-"):
                            opt_args[key.rstrip('=')] = next_arg
                            raw_args.remove(next_arg)

                elif arg.startswith(key):
                    pos_args.append(arg)
                    value = arg.split('=')[1].split(',')
                    opt_args[key.rstrip('=')] = value

        for arg in skip_opt_args:
            ar = [a for a in raw_args if a.startswith(arg)]
            if ar:
                raw_args.remove(ar[0])

        if "help" in pos_args:
            colors = [(100, 200, 255), (255, 100, 255)]  # Cyan -> Pink
            print(gradient_text("ffmpegp is an enhanced version of FFmpeg, offering additional features and functionalities to extend its powerful media processing capabilities.\n", colors),
"""
positional:
    \33[92mfile_path\33[0m      Get media file details by path
    \33[92m--colored\33[0m      Show gradient color output
    \33[92m--log\33[0m          Show logs of running process
    \33[92m--stdout\33[0m       Turn off all colors and disable any ASCII, printing only texts.

optional:
    \33[92m--jq\33[0m           JSON path to query specific data (e.g., format.filename)
    \33[92m--dir\33[0m          Use this flag to start multi task mode. (default: current directory)
    \33[92m--format\33[0m       Set specific file format to find. (works with '--dir' tag) (default: all) (e.g., --format=mp4)

placeholders:
    \33[92m{}\33[0m: Represents the input filename.

        \33[92minput formats\33[0m:
            \33[93m•\33[0m "{}"
            \33[93m•\33[0m "directory/{}"
        
        \33[92moutput formats\33[0m:
            \33[93m•\33[0m "{}" 
            \33[93m•\33[0m "{}.ext" 
            \33[93m•\33[0m "directory/{}" 
            \33[93m•\33[0m "directory/{}.ext"

    (\33[1mNote\33[0m: \33[92m.ext\33[0m refers to the file extension.)

homepage: \33[4mhttps://github.com/imegeek/ffmpegp\33[0m
""")
            sys.exit(0)

        try:
            file = raw_args[0]
            if os.path.isfile(file):
                media_details = get_media_details(file)
                if media_details:
                    json_path = opt_args["--jq"]
                    if json_path:
                        # Query the JSON object using the provided JSON path
                        query_result = query_json(media_details, json_path)
                        if query_result:
                            print(json.dumps(query_result, indent=4))
                        else:
                            print(f"No results found for the JSON path: {json_path}")
                    else:
                        # Print full media details if no JSON path is provided
                        print(json.dumps(media_details, indent=4))
                sys.exit(0)
        except Exception:
            pass

        if "--dir" in pos_args:
            mode = "multi"
            formats = opt_args["--format"]
            
            if opt_args["--dir"]:
                directory = os.path.abspath(opt_args["--dir"])
            else:
                directory = os.getcwd()
        
            if not os.path.isdir(directory):
                print(f"provided '{opt_args['--dir']}' path not exist.")
                sys.exit(1)

        for arg in raw_args:
            if arg.startswith("-"):
                args.append(arg)
            else:
                args.append(f"\"{arg}\"")

        for index, arg in enumerate(raw_args):
            if index + 1 < len(raw_args):
                if "-i" == arg and raw_args[index + 1]:
                    input_filenames.append(raw_args[index + 1])

        if mode == "single":

            if input_filenames:
                output_filename = raw_args[-1]

                input_path = list(map(lambda filename : os.path.abspath(filename), input_filenames))

                if "{}" in output_filename:
                    output_directory, output_filename, output_template, output_extension = extract_output(output_filename)

                    directory, file = os.path.split(input_path[0])
                    file_name, input_extension = os.path.splitext(file)
                    if not output_extension:
                        output_extension = input_extension

                    output_path = os.path.join(output_directory, output_template.replace("{}", file_name)+output_extension)
                    output_filename = f"\"{output_path}\""
                    args[-1] = output_filename
                else:
                    output_path = os.path.abspath(output_filename)

                if input_path[0] != output_path:
                    check_file(output_filename=output_filename, output_path=output_path, pos_args=pos_args)
            
            start_process(args=args, pos_args=pos_args, input_file=input_filenames)

        elif mode == "multi":
            if input_filenames:
                output_filename = raw_args[-1]

                if any(key for key in input_filenames if "{}" in key) and "{}" in output_filename:
                    output_directory, output_filename, output_template, output_extension = extract_output(output_filename)
                else:
                    print("You need to include `{}` as a placeholder for matched file names.")
                    sys.exit(1)

            files = []

            for file in os.listdir(directory):
                full_path = os.path.join(directory, file)

                if os.path.isfile(full_path):
                    if not formats:
                        files.append(full_path)
                    elif any(file.endswith(fmt) for fmt in formats):
                        files.append(full_path)

            if len(files) == 0:
                print(f"provided '{directory}' path is empty.")
                sys.exit(1)
            else:
                path = directory
                file_count = len(files)
                file_string = "files" if file_count > 1 else "file"
                print(f"[{file_count} {file_string}] loaded from {path}\n")

            for index, path in enumerate(files):
                directory, file = os.path.split(path)
                file_name, input_extension = os.path.splitext(file)

                if not output_extension:
                    extension = input_extension
                else:
                    extension = output_extension

                input_filename = f"\"{path}\""
                output_path = os.path.join(output_directory, output_template.replace("{}", file_name)+extension)
                output_filename = f"\"{output_path}\""

                args[args.index("-i") + 1] = input_filename
                args[-1] = output_filename

                check_skip = check_file(skip=True, output_filename=output_filename, output_path=output_path, pos_args=pos_args)
                if check_skip:
                    continue

                start_process(args=args, pos_args=pos_args, input_file=[input_filename], prefix=f"{index+1:02}/{file_count:02} ")

    except (EOFError, KeyboardInterrupt):
        print("\nProgram interrupted!")
        sys.exit(1)

if __name__ == "__main__":
    main()