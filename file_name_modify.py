# This file contains code to change file name of TV Shows as per the standard of Plex

import os,sys,stat

def change_file_name():
    pass

def read_files(path_dire):
    if not isinstance(path_dire,str):
        return 0
    else:
        list_file,dir_list,path_list=[],[],[]
        path_lst =[r[0] for r in os.walk(path_dire) if len(r[0].split('/'))==6]
        print(path_lst)
        t= path_lst[-1]
        print(t)
        #for t in path_list[:-1]:
        #\[(.*?)\]
        for path,dir_name,f_name in os.walk(t):
             for f_names in os.listdir(path):
                  new_name=change_file_Friends(f_names)
                  #os.chmod(path+'/'+f_names,0o777)
                  os.rename(path+'/'+f_names,path+'/'+new_name)
             for t in f_name:
                  list_file.append(t)
             dir_list.append(dir_name)
             path_list.append(path)
        return list_file,dir_list,path_list

'''
Required format for plex is 
TV Show/
        Season 01/
                 Show-S01E01.mpt4
'''

if __name__== "__main__":
    dir_loc='/Volumes/Public/Shared Videos/TV Shows'
    dir_loc1=0
    lst_files,dir_names,path_det= read_files(dir_loc)
    if lst_files==0:
        print("Please provide correct file path")
    else:
        print(lst_files)
        #print(dir_names)
        print(path_det)
    #change_file_name()