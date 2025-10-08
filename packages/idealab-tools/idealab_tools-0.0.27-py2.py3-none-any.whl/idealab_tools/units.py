# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 21:10:09 2020

@author: danaukes
"""

def format(key,value):
    if value>1:
        s = key+'^'+str(value)
    elif value==1:
        s = key
    elif value==-1:
        s = key
    elif value<-1:
        s = key+'^'+str(-value)
    return s
    


class Unit(object):
    scaling = {}

    def __init__(self,**kwargs):
        self.base_units = kwargs
        self.clean()
        # self.build_scaling()
    
    # def build_scaling(self):
        # my_scaling = {}
        # for key1,value in self.base_units.items():
            # my_scaling[key] = 1
            
    
    def clean(self):
        for key in list(self.base_units):
            if self.base_units[key]==0:
                del self.base_units[key]
                
    @classmethod
    def set_scaling(cls,**kwargs):
        Unit.scaling.update(kwargs)
        
    def compute_scaling(self):
        scaling_factor = 1
        for key,value in self.scaling.items():
            if key in self.base_units:
                scaling_factor *= value**(self.base_units[key])
        return scaling_factor
    
        
    def __mul__(self,other):
        if isinstance(other,Unit):
            new_base_units = self.base_units.copy()
            for key,value in other.base_units.items():
                if key in self.base_units:
                    new_base_units[key]+=value
                else:
                    new_base_units[key]=value
            return Unit(**new_base_units)
        else:
            raise TypeError
        
    def __rmul__(self,other):
        scaling = self.compute_scaling()
        value = other * scaling
        return value
        

    def __truediv__(self,other):
        if isinstance(other,Unit):
            new_base_units = self.base_units.copy()
            for key,value in other.base_units.items():
                if key in self.base_units:
                    new_base_units[key]-=value
                else:
                    new_base_units[key]=-value
            return Unit(**new_base_units)
            
    def __str__(self):
        s = ''
        
        num_units = [format(key,value) for key,value in self.base_units.items() if value>0]
        den_units = [format(key,value) for key,value in self.base_units.items() if value<0]
        if len(den_units)>1:
            den = '/('+'*'.join(den_units)+')'
        elif len(den_units)==1:
            den = '/'+den_units[0]
        else:
            den = ''
            
        s+=' '+'*'.join(num_units)+den
        return s
    
    def __repr__(self):
        return str(self)


force = Unit(kilogram=1,meter=1,second=-2)
length = Unit(meter=1)
time = Unit(second=1)
mass = Unit(kilogram=1)
radian = Unit()
torque = force*length
linear_stiffness = force/length
rotational_stiffness = torque/radian
speed = length/time
linear_speed = speed
rotational_speed = radian/time
power = force*speed
energy = power*time
inertia = mass*length*length
linear_damping = force/speed
acceleration = length/time/time

if __name__=='__main__':
    pass
    # Unit.set_scaling(s=10)
