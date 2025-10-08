#! /usr/bin/env python3
'''test_iminuit.py

   fit with iminuit vers. < 2.0 and > 2.0

.. moduleauthor:: Guenter Quast <g.quast@kit.edu>
'''

import numpy as np
import matplotlib.pyplot as plt
import PhyPraKit as ppk

from iminuit import __version__, Minuit
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
cost_function = LeastSquares(data_x, data_y, sigy_abs, model)
ipardict = {'a':0., 'b':0., 'c':0.}  # start values for parameters
m = Minuit(cost_function, **ipardict, errordef=1. )  

# perform fit
m.migrad()  # finds minimum of cost functionr
# possibly, improve error matrix
## m.hesse()

# extract parametes !!! this depends on iminuit version !!!
chi2 = m.fval               # chi2 
npar = m.nfit               # numer of parameters
ndof = len(data_x) - npar   # degrees of freedom
if __version__< '2':
  parnames = m.values.keys()  # names
  parvals = m.values.values() # values
  parerrs = m.errors.values() # uncertainties
else:
  # vers. >=2.0 
  parnames = m.parameters  # names
  parvals = m.values # values
  parerrs = m.errors # uncertainties

# draw data and fitted line
plt.errorbar(data_x, data_y, sigy_abs, fmt="o", label="data")
plt.plot(data_x, model(data_x, *parvals), label="fit")

# display legend with some fit info
fit_info = [
    f"$\\chi^2$ / $n_\\mathrm{{dof}}$ = {chi2:.1f} / {ndof}",]
for p, v, e in zip(parnames, parvals, parerrs):
    fit_info.append(f"{p} = ${v:.3f} \\pm {e:.3f}$")
plt.legend(title="\n".join(fit_info))

# run minos profile likelihood scan to check for asymmetric errors
minos_err = m.minos()
print("MINOS errors:")
if __version__< '2':
 for pnam in m.merrors.keys():
   print(f"{3*' '}{pnam}: {m.merrors[pnam][2]:.2g}",
         f"+{m.merrors[pnam][3]:.2g}")
else:
  for pnam in m.merrors.keys():
    print(f"{3*' '}{pnam}: {m.merrors[pnam].lower:.2g}",
          f"+{m.merrors[pnam].upper:.2g}")

plt.show()
