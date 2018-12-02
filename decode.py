import os
from os.path import join, basename, normpath

def deobs_pluralsight(fpath, target_dir):
    fname = os.path.basename(fpath)
    target_fname = fname.replace('psv', 'mp4')
    target_file_path = os.path.join(target_dir, target_fname)

    with open(target_file_path, "wb") as ofh:
        for byte in bytearray(open(fpath, "rb").read()):
            ofh.write(chr(byte ^ 101))


def deobfuscate(arg,dirname,fnames): 
    if fnames:
        for fname in fnames:
            fpath = os.path.join(dirname, fname)
            print fpath
            deobs_pluralsight(fpath, target_dir)
            
            
source_dir = "/Users/macbookpro/Library/Application Support/com.pluralsight.pluralsight-mac/ClipDownloads/"
target_dir = "/Users/macbookpro/Desktop/Videos/"
    
if not os.path.isdir(target_dir):
    os.makedirs(target_dir)
    
os.path.walk(source_dir, deobfuscate, None)