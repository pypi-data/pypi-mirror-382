# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 11:26:29 2020

@author: danaukes
"""
# %%
from collections import OrderedDict
class GenericData(object):
    def __init__(self, **kwargs):
        self._keys = kwargs.keys()
        for key,value in kwargs.items():
            if isinstance(value,dict):
                setattr(self,key,GenericData(**value))
            else:
                setattr(self,key,value)
    def to_dict(self):
        output = {}
        for key in self._keys:
            value = getattr(self,key)
            if isinstance(value,GenericData):
                output[key] = value.to_dict()
            else:
                output[key] = value
        return output
    def to_ordered_dict(self):
        output = OrderedDict()
        for key in self._keys:
            value = getattr(self,key)
            if isinstance(value,GenericData):
                output[key] = value.to_ordered_dict()
            else:
                output[key] = value
        return output
# %%

if __name__=='__main__':

    dict1 = {'a':1,'b':[1,2,3],'c':{'a':1,'b':[1,2,3]}}

    a = GenericData(**dict1)
    print(a.to_dict())

