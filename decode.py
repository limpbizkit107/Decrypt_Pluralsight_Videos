import os
import sqlite3
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

def connect_to_databese(path_to_database):
    conn = sqlite3.connect(path_to_database)
    c = conn.cursor()
    print 'conection to the database was sucssefull'
    courses = list(c.execute('SELECT ZTITLE, Z_PK FROM ZCOURSEHEADERCD'))
    for course in courses:
        course_name = course[0]
        course_modules = list(c.execute('SELECT ZTITLE, Z_FOK_COURSE FROM ZMODULECD WHERE ZCOURSE = '+str(course[1])))
        create_course_structute(course_name, course_modules)
    conn.close()

def create_course_structute(course, modules):
    print "creating folder structure for course: "+course
    if not os.path.isdir(course):
        os.makedirs(course)
    for module in modules:
        if not os.path.isdir(course+"/"+ module[0]):
            os.makedirs(course+"/"+ module[0])

source_dir = "/Users/macbookpro/Library/Application Support/com.pluralsight.pluralsight-mac/ClipDownloads/"
target_dir = "/Users/macbookpro/Desktop/Videos/"
path_to_database = '/Users/macbookpro/Library/Application Support/com.pluralsight.pluralsight-mac/Model'

# if not os.path.isdir(target_dir):
#     os.makedirs(target_dir)
    
# os.path.walk(source_dir, deobfuscate, None)
connect_to_databese(path_to_database)


