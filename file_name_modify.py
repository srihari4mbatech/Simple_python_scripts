# This file contains code to change file name of TV Shows as per the standard of Plex

import os

def change_file_name():
    pass

def read_files(path_dire):
    list_file=[]
    for t in os.list(path_dire):
        list_file.append(t)
    return list_file

if __name__== "__main__":
    change_file_name()