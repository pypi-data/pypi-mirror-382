# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 11:57:44 2020

@author: danaukes
"""

import idealab_tools.pyuac as pyuac

import subprocess
# import os
# import sys
import winreg

def get_system_path(key,system = True):

    if system:
        reg_path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
        reg_key= winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
    else:
        reg_path = r'Environment'
        reg_key= winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)

    
    
    try:
        existing_path,keytype = winreg.QueryValueEx(reg_key, key)
        # winreg.SetValueEx(reg_key, key,0,keytype,system_environment_variables)
        winreg.CloseKey(reg_key)
    except NameError:
        # existing_path,keytype = winreg.CreateKeyEx(reg_key, key)
        existing_path = ''
        keytype = None
    except FileNotFoundError:
        existing_path = ''
        keytype = None
    
    existing_path = existing_path.strip().strip(';').split(';')
    return existing_path    

def add_system_path(key,prepend_paths,append_paths,system = True):

    existing_path  = get_system_path(key,system)
    
    my_path=[]
    my_path.extend(prepend_paths)
    my_path.extend(existing_path)
    my_path.extend(append_paths)

    path_string = ';'.join(my_path)

    if system:
        s = 'setx {key} "{path_string}" /m'.format(path_string=path_string,key=key)
    else:
        s = 'setx {key} "{path_string}"'.format(path_string=path_string,key=key)
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
    p = subprocess.run(s,stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True,text=True)
    return p.stdout


if __name__=='__main__':
    my_path = []
    results = add_to_path('PATH',my_path,[])
        
    python_path = []
    results = add_to_path('PYTHONPATH',python_path,[],system=False)
