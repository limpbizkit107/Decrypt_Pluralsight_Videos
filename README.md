# Pluralsight Video Decryptor

A Python utility for converting downloaded Pluralsight videos from their encrypted format to standard MP4 files for offline viewing.

## Overview

This tool allows users to decrypt Pluralsight course videos that have been downloaded through the official Pluralsight desktop application. It extracts all downloaded courses from the Pluralsight database, maintains the original course and module structure, and converts the encrypted `.psv` files to standard `.mp4` format.

## Features

- Automatically extracts all downloaded courses from the Pluralsight database
- Preserves course and module structure in the output directory
- Decrypts all video files in parallel using multiprocessing for maximum performance
- Renames video files with sequential numbering for proper ordering
- Comprehensive error handling and progress reporting
- Clean, modular code following Python best practices

## Requirements

- Python 2.x
- SQLite3
- Pluralsight desktop application with downloaded courses

## Installation

No installation is required. Simply download the script and run it from the command line.

## Usage

```bash
python decode.py -i <path_to_pluralsight_app> -o <output_directory>
```

### Parameters

- `-i, --ifile`: Path to the root folder where the Pluralsight app is installed
  - Example (macOS): `/Users/username/Library/Application Support/com.pluralsight.pluralsight-mac`
- `-o, --ofile`: Path to the output directory where decrypted videos will be saved (optional, defaults to "./Extracted Courses/")
- `-h`: Display help information

### Example

```bash
python decode.py -i "/Users/username/Library/Application Support/com.pluralsight.pluralsight-mac" -o "./My Courses/"
```

## How It Works

The script performs the following operations:

1. Connects to the Pluralsight SQLite database to retrieve metadata for all downloaded courses
2. Creates a directory structure matching the original course organization
3. For each video clip, applies an XOR decryption algorithm (XOR with key 101)
4. Utilizes all available CPU cores to perform decryption in parallel
5. Organizes the decrypted videos in a clean, hierarchical structure

## Output Structure

The decrypted videos will be organized in the following structure:

```
Extracted Courses/
└── Course Name/
    ├── 1.Module Name/
    │   ├── 1.Clip Title.mp4
    │   ├── 2.Clip Title.mp4
    │   └── ...
    ├── 2.Module Name/
    │   └── ...
    └── ...
```

## Technical Details

- **Decryption Algorithm**: Simple XOR operation with key 101
- **Parallelism**: Utilizes Python's multiprocessing library to leverage all available CPU cores
- **Database Access**: Uses SQLite3 to read the Pluralsight app's database
- **Error Handling**: Comprehensive error management for database operations, file handling, and more

## Disclaimer

This tool is for personal use only. Please respect Pluralsight's terms of service and copyright restrictions. Only use this tool with courses you have legitimate access to through a valid Pluralsight subscription.

## License

This project is provided for educational purposes only. Use at your own risk.

## Author

Original work by Stefan Minchev

## Last Updated

March 3, 2025
