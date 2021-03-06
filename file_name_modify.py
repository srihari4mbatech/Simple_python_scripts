# This file contains code to change file name of TV Shows as per the standard of Plex

import os,sys,stat

def change_file_name(**kwargs):
    import re
    show_name = kwargs['showname']
    season_num=kwargs['seas_num']
    epiosde_num= kwargs['epis_num']
    ext=kwargs['extn']
    return show_name+" - "+season_num+epiosde_num+ext

def change_file_Friends(F_name):
    '''
    Friends - [3x01] - The One with the Princess Leia Fantasy
    Friends S1E01] - The One Where Monica Gets A Roommate
    '''
    new_F_name=F_name.replace('[','S').replace(']','') if '[' in F_name else F_name.replace('- ','S')
    new_F_name=new_F_name.replace('x','E')
    #new_F_name=new_F_name.replace(']','')
    return new_F_name

def change_file_name24_s9(f_name):
    new_name='24 - S09'+f_name
    return new_name

def existing_file_name(path_file):
    pass

def parse_file_name(name_file):
    # for 24hours season09
    if "Season 09"  in name_file and ('mp4' in name_file or '.avi' in name_file):
        showname="24"
        season_name= "S09"
        Episode_num='E'+str(name_file.split('-')[2]).strip().replace('mp4','')
        ext='.mp4'
        return showname,season_name,Episode_num,ext
    else:
        return 0

def change_path(path):
    if 'Season' in path.split('/')[-2]:
       path2='/'.join(path.split('/')[:-1])
       #new_name='Agents Of S.H.I.E.L.D - '+change_file_Friends(path.split('/')[-1])
       new_name = 'Sherlock Homes - ' + change_file_Friends(path.split('/')[-1])
       return path,path2,new_name
    else:
        return path,path,""

def read_files(path_dire):
    if not isinstance(path_dire,str):
        return 0
    else:
        list_file,dir_list,path_list=[],[],[]
        path_lst =[r[0] for r in os.walk(path_dire) if len(r[0].split('/'))==6]
        print(path_lst)
        t= path_lst[-1] # Castle
        t=path_lst[1] #Friends
        t= path_lst[5] #24 Hours
        t=path_lst[8]# Agent of shield
        t=path_lst[0]#Arrow
        t=path_lst[2]#sherlock homes
        print(t)
        #for t in path_list[:-1]:
        #\[(.*?)\]
        for path,dir_name,f_name in os.walk(t):
             for f_names in os.listdir(path):
                  #new_name=change_file_Friends(f_names)
                  if parse_file_name(f_names)!=0:
                      existname=parse_file_name(f_names)
                      new_name=change_file_name(showname=existname[0],seas_num=existname[1],epis_num=existname[2],extn=existname[3])
                      #path,path2,new_name=change_path(path)
                      os.rename(path+'/'+f_names,path+'/'+new_name)
                  elif "sherlock" in t:
                      path, path2,new_name = change_path(path)
                      if path!=path2:
                         os.rename(path + '/' + f_names, path2 + '/' + new_name+'.'+f_names.split('.')[-1])
             for tk in f_name:
                  list_file.append(tk)
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