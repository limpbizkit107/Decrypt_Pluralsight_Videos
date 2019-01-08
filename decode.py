import os
import sqlite3
import multiprocessing
from multiprocessing import Pool
from os.path import join, basename, normpath

source_dir = "/Users/i337566/Library/Application Support/com.pluralsight.pluralsight-mac/ClipDownloads/"
target_dir = "./"
path_to_database = '/Users/i337566/Library/Application Support/com.pluralsight.pluralsight-mac/Model'
clipsArray =[]

class Clip(object):
    def __init__(self, fpath, target_dir, target_fname):
        self._fpath = fpath
        self._target_dir = target_dir
        self._target_fname = target_fname

    @property
    def fpath(self):
        return self._fpath

    @property
    def target_dir(self):
        return self._target_dir
    @property
    def target_fname(self):
        return self._target_fname

def deobs_pluralsight_multiple(clip):
    target_file_path = os.path.join(clip.target_dir, clip.target_fname)
    print "-->" + target_file_path
    with open(target_file_path, "wb") as ofh:
        for byte in bytearray(open(clip.fpath, "rb").read()):
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
                    #print ("Start decrypting: " +clip[0].replace("-","")+".psv" +" --> "+target_dir+"/"+course_name+"/"+module[0]+"/"+" --> "+str(index)+"."+clip[1].replace("/","_")+".mp4")
                    clipsArray.append(Clip(source_dir+clip[0].replace("-","")+".psv",target_dir+"/"+course_name+"/"+module[0]+"/",str(index)+"."+clip[1].replace("/","_")+".mp4"))
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


if __name__ == '__main__': 
    extract_videos(path_to_database)
    p = Pool(multiprocessing.cpu_count())
    p.map(deobs_pluralsight_multiple, clipsArray)



