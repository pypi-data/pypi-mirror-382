#! /usr/bin/env python3
'''test_iminuit.py

   fit with iminuit

.. moduleauthor:: Guenter Quast <g.quast@kit.edu>
'''

import numpy as np
import matplotlib.pyplot as plt
import PhyPraKit as ppk

from iminuit import Minuit
from iminuit.cost import LeastSquares

# fit model
def model(x, a=0, b=0, c=0):
    return a+b*x+c*x*x

# generate pseudo data
np.random.seed(31415)      # initialize random generator
data_x = np.linspace(0, 1, 10)      # x of data points
mpardict = {'a':0., 'b':1., 'c':2.}  # model parameters
sigy_abs=0.1
xt, yt, data_y = ppk.generateXYdata(data_x, model, 0., sigy_abs,
                                      mpar=mpardict.values() )
# initialize cost function to minimize
cost_function = LeastSquares(data_x, data_y,sigy_abs, model)
ipardict = {'a':0., 'b':0., 'c':0.}     # start values for prameters
m = Minuit(cost_function, **ipardict )  

# perform fit

m.migrad()  # finds minimum of cost function
m.hesse()   # accurately computes uncertainties

# extract parametes vers. >=2.0 !!! depends on iminuit version !!!
parnames = m.parameters  # names
parvals = m.values # values
parerrs = m.errors # uncertainties
chi2 = m.fval               # chi2 
npar = m.nfit               # numer of parameters
ndof = len(data_x) - npar   # degrees of freedom

# draw data and fitted line
plt.errorbar(data_x, data_y, sigy_abs, fmt="o", label="data")
plt.plot(data_x, model(data_x, *parvals), label="fit")

# display legend with some fit info
fit_info = [
    f"$\\chi^2$ / $n_\\mathrm{{dof}}$ = {chi2:.1f} / {ndof}",]
for p, v, e in zip(parnames, parvals, parerrs):
    fit_info.append(f"{p} = ${v:.3f} \\pm {e:.3f}$")
plt.legend(title="\n".join(fit_info))

# run minos to check for asymmetric errors
m.minos()   # asymmetric errors from likelihood scan
print("MINOS errors:")
for pnam in m.merrors.keys():
  print(f"{3*' '}{pnam}: {m.merrors[pnam].lower:.2g}",
        f"+{m.merrors[pnam].upper:.2g}")

plt.show()
