import os
import sqlite3
from os.path import join, basename, normpath

def deobs_pluralsight(fpath, target_dir, target_fname):
    target_file_path = os.path.join(target_dir, target_fname)

    with open(target_file_path, "wb") as ofh:
        for byte in bytearray(open(fpath, "rb").read()):
            ofh.write(chr(byte ^ 101))

def extract_videos(path_to_database):
    conn = sqlite3.connect(path_to_database)
    c = conn.cursor()
    print ('Connection to the database was successful')
    dowloaded_courses = list(c.execute('SELECT ZHEADER FROM ZCOURSEDETAILSCD WHERE ZDOWNLOADED = 1'))
    for downloaded_course in dowloaded_courses:
        courses = list(c.execute('SELECT ZTITLE, Z_PK FROM ZCOURSEHEADERCD WHERE Z_PK = '+str(downloaded_course[0])))
        for course in courses:
            course_name = course[0]
            course_modules = list(c.execute('SELECT ZTITLE, Z_PK FROM ZMODULECD WHERE ZCOURSE = '+str(course[1]) +' ORDER BY Z_FOK_COURSE ASC' ))
            create_course_dir_structute(course_name, course_modules)
            for module in course_modules:
                clips = list(c.execute('SELECT ZID, ZTITLE FROM ZCLIPCD WHERE ZMODULE = '+str(module[1])+' ORDER BY Z_FOK_MODULE ASC'))
                index = 1;
                for clip in clips:
                    print ("Start decrypting: " +clip[0].replace("-","")+".psv" +" --> "+target_dir+"/"+course_name+"/"+module[0]+"/"+" --> "+str(index)+"."+clip[1]+".mp4")
                    deobs_pluralsight(source_dir+clip[0].replace("-","")+".psv",target_dir+"/"+course_name+"/"+module[0]+"/", str(index)+"."+clip[1]+".mp4")
                    index+=1
    conn.close()

def create_course_dir_structute(course, modules):
    print ("creating folder structure for course: "+course)
    if not os.path.isdir(target_dir+course):
        os.makedirs(target_dir+course)
    index = 1;
    for module in modules:
        if not os.path.isdir(target_dir+course+"/"+str(index)+"."+module[0]):
            os.makedirs(target_dir+course+"/"+str(index)+"."+ module[0])
            lst = list(module)
            lst[0] = str(index)+"."+module[0]
            modules[index-1] = tuple(lst)
            index+=1

source_dir = "/Users/macbookpro/Library/Application Support/com.pluralsight.pluralsight-mac/ClipDownloads/"
target_dir = "/Volumes/Stefan/Pluralsight/"
path_to_database = '/Users/macbookpro/Library/Application Support/com.pluralsight.pluralsight-mac/Model'

extract_videos(path_to_database)


