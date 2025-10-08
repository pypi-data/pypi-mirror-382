#! /usr/bin/env python3
"""test_mnFit.py
   simple fit with user-defined cost function with iminiut

.. moduleauthor:: Guenter Quast <g.quast@kit.edu>

"""

import numpy as np, matplotlib.pyplot as plt
from PhyPraKit.phyFit import mnFit

if __name__ == "__main__": # --------------------------------------  
  #
  # Example of a simple minuit fit with user-defined cost function
  #  (unbinned Gaussian log-likelihood fit)
  #

  # define the model function to fit, a simple Gauß
  def fGauss(x,mu=0.,sigma=1.):
    return (np.exp(-(x-mu)**2/2./sigma**2)/np.sqrt(2.*np.pi)/sigma)
  # its negative log likelihood * 2.
  def n2lLGauss(x, mu, sigma):
    r= (dat-mu)/sigma
    return np.sum( r*r + 2.*np.log(sigma))
    
  # generate some Gaussian-distributed data
  dat = 2.+ 0.5*np.random.randn(1000)

  # define cost function
  def myCost(mu=1., sigma=1.):
    return n2lLGauss(dat, mu, sigma)
      
  Fit = mnFit("user")
  Fit.init_mnFit(myCost)
  fitResult = Fit.do_fit()
  # print(fitResult[1])  # migrad result
  print(fitResult[1])    # full minos result

  Fit.plotContours()  
  plt.show()

  pnams, pvals, perrs, cor, gof = Fit.getResult()
  

# Print results to illustrate how to use output
  print('\n*==* Fit Result:')
##  print(" chi2: {:.3g}".format(chi2))
  print(" parameter values:      ", pvals)
  print(" neg. parameter errors: ", perrs[:,0])
  print(" pos. parameter errors: ", perrs[:,1])
  print(" correlations : \n", cor)
  
