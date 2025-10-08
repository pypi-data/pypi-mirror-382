import  numpy
import math
import sympy

class Quaternion(object):
    def __init__(self,a,b,c,d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __mul__(self,other):
        a = self.a*other.a - self.b*other.b - self.c*other.c - self.d*other.d
        b = self.a*other.b + self.b*other.a + self.c*other.d - self.d*other.c
        c = self.a*other.c + self.c*other.a + self.d*other.b - self.b*other.d
        d = self.a*other.d + self.d*other.a + self.b*other.c - self.c*other.b
        quat = Quaternion(a,b,c,d)
        return quat
    
    def __add__(self,other):
        a = self.a+other.a
        b = self.b+other.b
        c = self.c+other.c
        d = self.d+other.d
        q = Quaternion(a,b,c,d)
        return q
    
    def __neg__(self):
        return Quaternion(-self.a,-self.b,-self.c,-self.d)
    
    def __sub__(self,other):
        return (self + (-other))
    
    def __str__(self):
        s = '({})+({})i+({})j+({})k'.format(self.a,self.b,self.c,self.d)
        return s
    
    def __repr__(self):
        return str(self)
    
    def conj(self):
        return self.conjugate()

    def conjugate(self):
        return Quaternion(self.a,-self.b,-self.c,-self.d)

    def real(self):
        return self.a

    def imaginary(self):
        return self.b,self.c,self.d

    def to_numpy_vec(self):
        return numpy.array([self.imaginary()]).T
    
    def to_numpy(self):
        return numpy.array([[self.a,self.b,self.c,self.d]]).T

    def to_sympy(self):
        return sympy.Matrix([self.a,self.b,self.c,self.d])

    def len_squared(self):
        result = self*self.conj()
        return result
    
    def axis_angle(self,degrees=False):

        v = numpy.array([self.b,self.c,self.d])
        l = (v.dot(v))**.5
        u = v/l
        beta = math.atan2(l,self.a)
        theta = beta*2
        if degrees:
            theta*=180/math.pi

        return u,theta


        

    @staticmethod
    def from_axis_angle(v,theta,symbolic = False):
        v = numpy.array(v)
        v = v.flatten()
        l = (v.dot(v))**.5
        v = (v/l).tolist()
        if symbolic:
            import sympy
            a = sympy.cos(theta/2)
            s = sympy.sin(theta/2)
        else:
            a = math.cos(theta/2)
            s = math.sin(theta/2)
        b = s*v[0]
        c = s*v[1]
        d = s*v[2]
        q = Quaternion(a,b,c,d)
        return q
    
    @staticmethod
    def from_vec(vec):
        vec = vec.flatten()
        a = 0
        b, c, d = vec
        q = Quaternion(a,b,c,d)
        return q

    def to_rot(self):
        v1 = self*Quaternion(0,1,0,0)*self.conj()
        v2 = self*Quaternion(0,0,1,0)*self.conj()
        v3 = self*Quaternion(0,0,0,1)*self.conj()

        v1 = v1.simplify().to_numpy_vec()
        v2 = v2.simplify().to_numpy_vec()
        v3 = v3.simplify().to_numpy_vec()

        R = numpy.hstack([v1,v2,v3])

        return R
    
    def simplify(self):
        a = sympy.simplify(self.a)
        b = sympy.simplify(self.b)
        c = sympy.simplify(self.c)
        d = sympy.simplify(self.d)
        return Quaternion(a,b,c,d)

    def subs(self,dict1):
        try:
            a = self.a.subs(dict1)
        except AttributeError:
            a = self.a
        try:
            b = self.b.subs(dict1)
        except AttributeError:
            b = self.b
        try:
            c = self.c.subs(dict1)
        except AttributeError:
            c = self.c
        try:
            d = self.d.subs(dict1)
        except AttributeError:
            d = self.d                        

        return Quaternion(a,b,c,d)

def Rx(theta,symbolic=False):
    if symbolic:
        ct = sympy.cos(theta)
        st = sympy.sin(theta)
    else:
        ct = math.cos(theta)
        st = math.sin(theta)
        
    R = numpy.array([
        [1, 0, 0],
        [0, ct, -st],
        [0, st, ct]])

    return R

def Ry(theta,symbolic=False):

    if symbolic:
        ct = sympy.cos(theta)
        st = sympy.sin(theta)
    else:
        ct = math.cos(theta)
        st = math.sin(theta)
        
    R = numpy.array([
        [ct, 0, st],
        [0, 1, 0],
        [-st, 0, ct]])
    
    return R
    
def Rz(theta,symbolic=False):
    if symbolic:
        ct = sympy.cos(theta)
        st = sympy.sin(theta)
    else:
        ct = math.cos(theta)
        st = math.sin(theta)
        
    R = numpy.array([
        [ct, -st, 0],
        [st , ct, 0],
        [0,0,1]])

    return R


if __name__=='__main__':

    q1 = Quaternion.from_axis_angle([1,-1,.5],90*math.pi/180)
    R1 = q1.to_rot()
    # print(R1)
    q2 = Quaternion.from_axis_angle([1,0,0],math.pi+30*math.pi/180)
    R2 = q2.to_rot()
    print(q1,q2)    

    axis, angle = q1.axis_angle()
    print(axis,angle*180/math.pi)
