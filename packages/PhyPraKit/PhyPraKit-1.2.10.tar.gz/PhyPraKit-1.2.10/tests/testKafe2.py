#! /usr/bin/env python3
'''testKafe2.py

   simple linear regression with kafe2

.. moduleauthor:: Guenter Quast <g.quast@kit.edu>
'''


import numpy as np
import matplotlib.pyplot as plt
import PhyPraKit as ppk
from PhyPraKit import readCSV, autocorrelate, convolutionPeakfinder, histstat, meanFilter, linRegression, k2Fit

def model(x,a=1,b=0):
    return a*x+b

s= np.array([1,2,3,4])
t= np.array([0.7,2.3,3.3,3.6])
fehlerx = np.zeros(4)
fehlery = np.ones(4)

## k2Fit(model, s, t, fehlerx, fehlery)  # vers. <=1.1.0

# with new interface in PhyPraKit 1.1.1 
k2Fit(model, s, t) 
