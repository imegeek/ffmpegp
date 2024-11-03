<div align="center">
<kbd>
  <img src="https://github.com/user-attachments/assets/73fc18dd-ae11-47d2-ad9a-3f6adcdcdda5" alt="ffmpegp-logo" />
</kbd>
</div><br>

ffmpegp (short for "FFmpeg Plus") is a Python-based utility designed to simplify working with media files using ffprobe and ffmpeg. This tool lets you easily extract media details, format conversions, and advanced querying via JSON paths, providing a convenient and efficient interface.

## Features

* **Media Metadata Extraction** : Get detailed media information via `ffprobe`.
* **JSONPath Querying** : Retrieve specific metadata using JSON path expressions.
* **Gradient Text** : Colored gradient output for enhanced readability.
* **Progress Bar** : Visual progress bar with customizable colors and time estimation.
* **File Size Conversion** : Converts file size to human-readable formats.
* **Time Conversion** : Converts media duration to seconds.
* **Enhanced Command Options** : Supports various flags for different modes and output styles.

## Prerequisites

Ensure `ffmpeg` and `ffprobe` are installed and accessible in your system's PATH. If either is missing, the script will display an error.

## Installation

Install **ffmpegp** using `pip`:

```
pip install ffmpegp
```

## Usage

Run the program as follows:

```
ffmpegp -i <file_path> [options]
```

### Arguments

* `file_path`: Path to the media file for which you want details.

### Options

| Option        | Description                                             |
| ------------- | ------------------------------------------------------- |
| `--colored` | Enable gradient color output.                           |
| `--log`     | Display logs of the running process.                    |
| `--stdout`  | Print only plain text without any colored output.       |
| `--jq`      | Query specific JSON data (e.g.,`format.filename`).    |
| `--dir`     | Enable multi-file processing mode in a directory.       |
| `--format`  | Specify file format when using `--dir`(default: all). |

## Example Commands

Get media details:

```
ffmpegp "video.mp4"
```

Get specific JSON data:

```
ffmpegp "video.mp4" --jq="format.filename"
```

Enable gradient color progress output:

```
ffmpegp -i "video.mp4" [options] --colored
```

Run in directory mode and select only (mp4) extension files and save files to "output" folder with same filename with diffrent file extension (mkv).:

```
ffmpegp -i "{}" <options> "/output/{}.mkv" --dir="./videos" --format="mp4"
```

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the GNU LESSER GENERAL PUBLIC LICENSE - see the [LICENSE](https://github.com/imegeek/ffmpegp/blob/master/LICENSE) file for details.
