import os

"""
copyright 2016-2017 Dan Aukes
"""

import numpy
import os

def read(filename,format = None):
    with open(filename) as f:
        text = f.read()
    
    lines = text.split('\n')
    rows = []
    for line in lines:
        line = line.split('#')[0]
        line = line.strip()
        if len(line)>0:
            elements=line.split(' ')
            rows.append(elements)
    data = numpy.array(rows,dtype = numpy.float)
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

    import idealab_tools.data_exchange.dat

    folder = 'C:/Users/danaukes/code/code_pyfea/python/pyfea_examples/heat/results'
    
    data = read(os.path.join(folder,'U.txt'))
    data2 = idealab_tools.data_exchange.dat.read(os.path.join(folder,'U.dat'))    
    sos = ((data-data2)**2).sum()**.5
#    return data
