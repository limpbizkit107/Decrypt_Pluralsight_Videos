#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pluralsight Video Decryptor

This script decrypts Pluralsight videos that have been downloaded through the
official Pluralsight desktop application. It extracts course metadata from the
Pluralsight SQLite database and decrypts all video files, maintaining the
original course and module structure.
"""

import os
import sys
import getopt
import sqlite3
import multiprocessing
from multiprocessing import Pool
from os.path import join, basename, normpath


class Clip(object):
    """
    Represents a video clip to be decrypted.
    
    Attributes:
        _fpath (str): Path to the encrypted source file.
        _target_dir (str): Directory where the decrypted file will be saved.
        _target_fname (str): Filename for the decrypted output file.
    """
    
    def __init__(self, fpath, target_dir, target_fname):
        """
        Initialize a new Clip instance.
        
        Args:
            fpath (str): Path to the encrypted source file.
            target_dir (str): Directory where the decrypted file will be saved.
            target_fname (str): Filename for the decrypted output file.
        """
        self._fpath = fpath
        self._target_dir = target_dir
        self._target_fname = target_fname

    @property
    def fpath(self):
        """Get the path to the encrypted source file."""
        return self._fpath

    @property
    def target_dir(self):
        """Get the directory where the decrypted file will be saved."""
        return self._target_dir
        
    @property
    def target_fname(self):
        """Get the filename for the decrypted output file."""
        return self._target_fname


def decrypt_clip(clip):
    """
    Decrypt a single Pluralsight video clip.
    
    The decryption algorithm XORs each byte with the value 101.
    
    Args:
        clip (Clip): The clip object containing source and target information.
    """
    target_file_path = os.path.join(clip.target_dir, clip.target_fname)
    print("Decrypting: {}".format(target_file_path))
    
    with open(target_file_path, "wb") as output_file:
        with open(clip.fpath, "rb") as input_file:
            for byte in bytearray(input_file.read()):
                output_file.write(chr(byte ^ 101))


def extract_videos(database_path, source_dir, target_dir):
    """
    Extract metadata for all downloaded videos from the Pluralsight database.
    
    Args:
        database_path (str): Path to the Pluralsight SQLite database.
        source_dir (str): Directory containing encrypted video files.
        target_dir (str): Directory where decrypted videos will be saved.
        
    Returns:
        list: List of Clip objects to be decrypted.
    """
    clips_to_decrypt = []
    
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        print('Successfully connected to the Pluralsight database')
        
        # Get all downloaded courses
        downloaded_courses = list(cursor.execute(
            'SELECT ZHEADER FROM ZCOURSEDETAILSCD WHERE ZDOWNLOADED = 1'))
        
        for downloaded_course in downloaded_courses:
            # Get course details
            courses = list(cursor.execute(
                'SELECT ZTITLE, Z_PK FROM ZCOURSEHEADERCD WHERE Z_PK = ?', 
                (downloaded_course[0],)))
            
            for course in courses:
                course_name = course[0]
                course_id = course[1]
                
                # Get course modules
                course_modules = list(cursor.execute(
                    'SELECT ZTITLE, Z_PK FROM ZMODULECD WHERE ZCOURSE = ? ORDER BY Z_FOK_COURSE ASC',
                    (course_id,)))
                
                # Create directory structure for this course
                create_course_directory_structure(course_name, course_modules, target_dir)
                
                # Process modules
                for module in course_modules:
                    module_id = module[1]
                    module_name = module[0]
                    
                    # Get clips for this module
                    clips = list(cursor.execute(
                        'SELECT ZID, ZTITLE FROM ZCLIPCD WHERE ZMODULE = ? ORDER BY Z_FOK_MODULE ASC',
                        (module_id,)))
                    
                    # Process clips
                    for index, clip in enumerate(clips, 1):
                        clip_id = clip[0].replace("-", "")
                        clip_title = clip[1].replace("/", "_")
                        
                        source_path = os.path.join(source_dir, clip_id + ".psv")
                        target_directory = os.path.join(target_dir, course_name, module_name)
                        target_filename = "{}.{}.mp4".format(index, clip_title)
                        
                        clips_to_decrypt.append(Clip(source_path, target_directory, target_filename))
        
        conn.close()
        return clips_to_decrypt
        
    except sqlite3.Error as e:
        print("Database error: {}".format(e))
        sys.exit(1)
    except Exception as e:
        print("Error: {}".format(e))
        sys.exit(1)


def create_course_directory_structure(course, modules, output_dir):
    """
    Create the directory structure for a course and its modules.
    
    Args:
        course (str): The name of the course.
        modules (list): List of modules in the course.
        output_dir (str): Base directory where the course structure will be created.
        
    Returns:
        list: Updated modules list with numbered prefixes.
    """
    print("Creating folder structure for course: {}".format(course))
    
    # Create course directory if it doesn't exist
    course_dir = os.path.join(output_dir, course)
    if not os.path.isdir(course_dir):
        os.makedirs(course_dir)
    
    # Create module directories with number prefixes
    updated_modules = []
    for index, module in enumerate(modules, 1):
        module_name = module[0]
        module_dir = os.path.join(course_dir, "{}.{}".format(index, module_name))
        
        if not os.path.isdir(module_dir):
            os.makedirs(module_dir)
        
        # Update module tuple with numbered name
        updated_module = list(module)
        updated_module[0] = "{}.{}".format(index, module_name)
        updated_modules.append(tuple(updated_module))
    
    return updated_modules


def display_help():
    """Display usage information for the script."""
    help_text = """
Pluralsight Video Decryptor

Usage: 
    python decode.py -i <path_to_pluralsight_app> -o <output_directory>

Options:
    -h                      Show this help message and exit
    -i, --ifile=PATH        Path to the root folder where the Pluralsight app is installed
                            Example: "/Users/username/Library/Application Support/com.pluralsight.pluralsight-mac"
    -o, --ofile=PATH        Path to the output directory where decrypted videos will be saved
    """
    print(help_text)


def main(argv):
    """
    Main function to parse arguments and orchestrate the decryption process.
    
    Args:
        argv (list): Command line arguments.
    """
    input_path = ''
    output_path = ''
    
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        display_help()
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            display_help()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_path = arg
        elif opt in ("-o", "--ofile"):
            output_path = arg
    
    # Validate inputs
    if not input_path:
        print("Error: Input path is required")
        display_help()
        sys.exit(2)
    
    # Set default output path if not provided
    if not output_path:
        output_path = "./Extracted Courses/"
    
    print('Input path: "{}"'.format(input_path))
    print('Output path: "{}"'.format(output_path))
    
    # Set up paths
    database_path = os.path.join(input_path, "Model")
    source_dir = os.path.join(input_path, "ClipDownloads")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # Extract video metadata
    clips_to_decrypt = extract_videos(database_path, source_dir, output_path)
    
    if not clips_to_decrypt:
        print("No clips found to decrypt")
        sys.exit(0)
    
    print("Found {} clips to decrypt".format(len(clips_to_decrypt)))
    
    # Decrypt videos in parallel using all available CPU cores
    print("Starting decryption using {} CPU cores".format(multiprocessing.cpu_count()))
    pool = Pool(multiprocessing.cpu_count())
    pool.map(decrypt_clip, clips_to_decrypt)
    pool.close()
    pool.join()
    
    print("Decryption complete. Videos saved to: {}".format(output_path))


if __name__ == '__main__':
    main(sys.argv[1:])
