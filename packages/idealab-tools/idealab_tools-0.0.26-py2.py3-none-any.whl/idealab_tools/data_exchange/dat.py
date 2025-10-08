import os

"""
copyright 2016-2017 Dan Aukes
"""

import numpy

def read(filename,format = None):
    with open(filename) as f:
        text = f.read()
    
    text = text.split('\n')
    rows = []
    for row in text:
        row = row.split('%')[0]
        if len(row)>0:
            row = row.split()
            if format is not None:
                row = [format(entry) for entry in row]
            rows.append(row)
    
    data = numpy.array(rows,dtype = format)
    return data

def write(filename,array):
    lines = []
    for item in array:
        line = [str(item2) for item2 in item]
        string1= ' '.join(line)+'\n'
        lines.append(string1)
    with open(filename,'w') as f:
        f.writelines(lines)
    
if __name__=='__main__':
    filename = 'dirichlet.dat'
    data = load(filename,int)