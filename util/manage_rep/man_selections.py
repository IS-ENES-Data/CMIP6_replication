# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 15:18:39 2018

@author: k202015
"""

# read in selection files and generate json files

import json
import configparser
config = configparser.ConfigParser()
import os
from tinydb import TinyDB, Query
from string import Template

#keys to exclude in selectin file generation
exclude_keys =['repl_center']

def cleanup(res_dict):
    new_dict = {}
    for key,val_d in res_dict.items():
        new_val_d = {}
        for vk,val in val_d.items():
            if isinstance(val,str):
                nval = val.split(' ')
            else:
                nval = val
            new_val_d[vk] = nval    
        new_dict[key]=new_val_d       
    return(new_dict)


def read_sel_files(sel_path):
    res_dict = {}
    for dirpath,dnames,fnames in os.walk(sel_path):
        for f in fnames:
            if f.endswith(".txt"): 
               print("reading: ",os.path.join(sel_path,f))
               config.read(os.path.join(sel_path,f))
               for sec in config.sections():
                  res_dict[f]=dict(config[sec])
                  res_dict[f]['repl_center'] = sec
    return cleanup(res_dict)                
            

def write_json(new_dict,directory): 
    for key,cdict in new_dict.items():
        jstring = json.dumps(cdict,indent=4)
        filename = key.split(".")[0]       
        with open(os.path.join(directory,filename+".json"),"w") as f:
             print("Writing: ",os.path.join(directory,filename+".json"))
             f.write(jstring)     

def store_json(new_dict,db_path):
    db = TinyDB(db_path)
    db.insert(new_dict)
    
    
def gen_sel(new_dict):
     sel_string = ''
     header = Template('#### Replica center: $center \n')
     selection = Template('$key = $val \n')                  
     my_header = header.substitute(center = new_dict['repl_center'])
     sel_string += my_header
     for key,val in new_dict.items():
         if key not in exclude_keys:
             nval = " ".join(val)   
             val_string = selection.substitute(key=key,val=nval)          
             sel_string += val_string
     return sel_string         
             