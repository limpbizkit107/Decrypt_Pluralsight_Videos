import os, sys, getopt
import sqlite3
import multiprocessing
from multiprocessing import Pool
from os.path import join, basename, normpath

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

def extract_videos(path_to_database, source_dir, target_dir):
    conn = sqlite3.connect(path_to_database)
    c = conn.cursor()
    print ('Connection to the database was successful')
    dowloaded_courses = list(c.execute('SELECT ZHEADER FROM ZCOURSEDETAILSCD WHERE ZDOWNLOADED = 1'))
    for downloaded_course in dowloaded_courses:
        courses = list(c.execute('SELECT ZTITLE, Z_PK FROM ZCOURSEHEADERCD WHERE Z_PK = '+str(downloaded_course[0])))
        for course in courses:
            course_name = course[0]
            course_modules = list(c.execute('SELECT ZTITLE, Z_PK FROM ZMODULECD WHERE ZCOURSE = '+str(course[1]) +' ORDER BY Z_FOK_COURSE ASC' ))
            create_course_dir_structute(course_name, course_modules, target_dir)
            for module in course_modules:
                clips = list(c.execute('SELECT ZID, ZTITLE FROM ZCLIPCD WHERE ZMODULE = '+str(module[1])+' ORDER BY Z_FOK_MODULE ASC'))
                index = 1;
                for clip in clips:
                    #print ("Start decrypting: " +clip[0].replace("-","")+".psv" +" --> "+target_dir+"/"+course_name+"/"+module[0]+"/"+" --> "+str(index)+"."+clip[1].replace("/","_")+".mp4")
                    clipsArray.append(Clip(source_dir+clip[0].replace("-","")+".psv",target_dir+"/"+course_name+"/"+module[0]+"/",str(index)+"."+clip[1].replace("/","_")+".mp4"))
                    index+=1
    conn.close()

def create_course_dir_structute(course, modules, output_dir):
    print ("creating folder structure for course: "+course)
    if not os.path.isdir(output_dir+course):
        os.makedirs(output_dir+course)
    index = 1;
    for module in modules:
        if not os.path.isdir(output_dir+course+"/"+str(index)+"."+module[0]):
            os.makedirs(output_dir+course+"/"+str(index)+"."+ module[0])
            lst = list(module)
            lst[0] = str(index)+"."+module[0]
            modules[index-1] = tuple(lst)
            index+=1

def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'decode.py -i <inputfile> -o <outputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'decode.py \n    -i <pathToPluralsightApp> - Path to the root folder where the pluralsight app is installed. \n          Example: -i "/Users/--*You-Local-User*--/Library/Application Support/com.pluralsight.pluralsight-mac" \n    -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
   print 'Input file is "', inputfile
   print 'Output file is "', outputfile

   path_to_database = inputfile + "/Model"
   source_dir = inputfile + "/ClipDownloads/"
   target_dir = "./Extracted Courses/"

   extract_videos(path_to_database, source_dir, target_dir)
   #Here we are using all of the available cpu's in parralel for decrypting
   p = Pool(multiprocessing.cpu_count())
   p.map(deobs_pluralsight_multiple, clipsArray)

if __name__ == '__main__':
    main(sys.argv[1:])
