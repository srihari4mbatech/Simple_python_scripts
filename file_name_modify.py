# This file contains code to change file name of TV Shows as per the standard of Plex

import os

def change_file_name():
    pass

def read_files(path_dire):
    if not isinstance(path_dire,str):
        return 0
    else:
        list_file=[]
        for path,dir_name,f_name in os.walk(path_dire):
            for t in f_name:
                list_file.append(t)
        return list_file

'''
Required format for plex is 
TV Show/
        Season 01/
                 Show-S01E01.mpt4
'''

if __name__== "__main__":
    dir_loc='/Volumes/Public/Shared Videos/TV Shows'
    dir_loc1=0
    lst_files= read_files(dir_loc)
    if lst_files==0:
        print("Please provide correct file path")
    else:
        print(lst_files)
    #change_file_name()