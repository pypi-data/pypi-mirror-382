#! /usr/bin/env python3
"""test_iminuit.py
   Fitting with iminiut

   This example illustrates the special features of iminuit:
    - definition of a custom cost function 
         used to implement least squares method with correlated errors   
    - profile likelihood for asymmetric errors
    - plotting of profile likeliood and confidence contours

    supports iminuit vers. < 2.0 and >= 2.0

.. moduleauthor:: Guenter Quast <g.quast@kit.edu>
"""

import numpy as np, matplotlib.pyplot as plt, PhyPraKit as ppk

def mFit(fitf, x, y, sx=None, sy=None, srelx=None, srely=None, 
         xabscor=None, xrelcor=None,        
         yabscor=None, yrelcor=None,        
         p0=None, run_minos=True, plot=True, plot_cor=True):
  """
    fit an arbitrary function f(x) to data
    with uncorrelated and correlated absolute and/or relative errors on y 
    with package iminuit

    Args:
      * fitf: model function to fit, arguments (float:x, float: *args)
      * x:  np-array, independent data
      * y:  np-array, dependent data
      * sx: scalar or 1d or 2d np-array , uncertainties on x data
      * sy: scalar or 1d or 2d np-array , uncertainties on x data
      * srelx: scalar or np-array, relative uncertainties x
      * srely: scalar or np-array, relative uncertainties y
      * yabscor: scalar or np-array, absolute, correlated error(s) on y
      * yrelcor: scalar or np-array, relative, correlated error(s) on y
      * p0: array-like, initial guess of parameters
      * run_minos: run minos profile likelihood scan if True
      * plot: show data and model if True
      * plot_cor: show profile liklihoods and conficence contours

    Returns:
      * np-array of float: parameter values
      * 2d np-array of float: parameter uncertaities [0]: neg. and [1]: pos. 
      * np-array: correlation matrix 
      * float: chi2  \chi-square of fit a minimum
  """  

  from iminuit import __version__, Minuit
  from inspect import signature, Parameter  

  # define custom cost function for iminuit
  class LSQwithCov:
    """
    custom Least-SQuares cost function with error matrix
    """
  
    def __init__(self, x, y, err, model):
    
      from iminuit.util import describe, make_func_code

      self.model = model 
      # set proper signature of model function for iminuit
      self.func_code = make_func_code(describe(model)[1:])
      self.x = np.asarray(x)
      self.y = np.asarray(y)
      # initialize uncertainties and eventually covariance matrix
      self.initCov(err)
    
    def initCov(self, err):
      # special init to reinitialize covariance matrix (if needed)
      self.err2 = np.asarray(err)
      self.errdim = self.err2.ndim
      if self.errdim == 2:
      # got a covariance matrix, need inverse
        self.iCov = np.matrix(self.err2).I
      else:
        self.err2 *= self.err2 
        self.iCov = 1./self.err2
      self.rebuildCov = False # use initial covariance matrix in fit

      self.ycov = self.err2
      self.xcov = None
      
    def init_ErrorComponents(self, ex, ey, erelx, erely, cabsx, crelx, cabsy, crely):
      # if set, covariance matrix will be recomputed each time in the fit
       self.ex = ex
       self.ey = ey
       self.erelx = erelx
       self.erely = erely
       self.cabsx = cabsx
       self.crelx = crelx
       self.cabsy = cabsy
       self.crely = crely
       # rebuild covariance matrix during fitting procedure
       self.rebuildCov=True

    def rebuild_Cov(self):
      """
      (Re-)Build the covariance matrix from components
      """
      nd = len(self.x)
      cov = np.zeros( (nd, nd) )
      # Start with y-uncertainties
      e_ = np.array(self.ey)*np.ones(nd) # ensure array of length nd
      if e_.ndim == 2: # already got a matrix, take as covariance matrix
        cov += e_
      else:
        cov += np.diag(e_*e_) # set diagonal elements of covariance matrix
      if self.erely is not None:
        er_ = np.array(self.erely)*np.ones(nd)
        cov += np.diag(er_*er_) * self.model(self.x, *self.mpar)            
      if self.cabsy is not None:
        if len(np.shape(np.array(self.cabsy))) < 2: # has one entry
          c_ = np.array(self.cabsy) * np.ones(nd)
          cov += np.outer(c_, c_) 
        else:            # got a list, add each list element
          for c in self.cabsy:
            c_ = np.array(self.cabsy)*np.ones(nd)
            cov += np.outer(c_, c_) 
      if self.crely is not None:
        if len(np.shape(np.array(self.crely))) < 2: # has one entry
          c_ = np.array(self.crely) * self.model(self.x, *self.mpar)
          cov += np.outer(c_, c_) 
        else:            # got a list, add each list element
          for c in self.crely:
            c_ = np.array(c) * self.model(self.x, *self.mpar)
            cov += np.outer(c_, c_)
      self.covy = cov
      
      if (self.ex is not None and self.ex !=0) or self.erelx is not None:
        covx = np.zeros( (len(x), len(x)) )
       # build covariance matrix for x
        e_ = np.array(self.ex)*np.ones(nd) # ensure array of length nd
        if e_.ndim == 2: # already got a matrix, take as covariance matrix
          covx += e_
        else:
          covx += np.diag(e_*e_) # set diagonal elements of covariance matrix
        if self.erelx is not None:
          er_ = np.array(self.erelx)*np.ones(nd)
          covx += np.diag(er_*er_) * self.x                      
        if self.cabsx is not None:
          if len(np.shape(np.array(self.cabsx))) < 2: # has one entry
            c_ = np.array(self.cabsx) * np.ones(nd)
            covx += np.outer(c_, c_) 
          else:            # got a list, add each list element
            for c in self.cabsx:
              c_ = np.array(self.cabsx)*np.ones(nd)
              covx += np.outer(c_, c_) 
        if self.crelx is not None:
          if len(np.shape(np.array(self.crelx))) < 2: # has one entry
            c_ = np.array(self.crelx) * self.x
            covx += np.outer(c_, c_) 
          else:            # got a list, add each list element
            for c in self.crelx:
              c_ = np.array(c) * self.x
              covx += np.outer(c_, c_) 
        self.covx = covx
        
       # determine derivatives of model function w.r.t. x, distance dx from smallest uncertaintey
        dx = np.sqrt(min(np.diag(covx)))/10.
        mprime = 0.5/dx * (self.model(self.x + dx, *self.mpar) - self.model(self.x - dx, *self.mpar))
        # project on y
        covx_projected = np.outer(mprime, mprime) * covx
        # add to covariance matrix to obtain full covariance matrix for fit
        cov += covx_projected
      else:
        covx_projected = None

 #     print('*!!! rebuild_Cov:')
 #     print('covy:\n',covy)
 #     print('covx=:\n',covx)
 #     print('deriv:}n',mprime)
 #     if covx is not None: print('covx_proj:\n',covx_projected)
 #     sys.exit()
      
      # set inverse covariance matrix 
      self.iCov = np.matrix(cov).I
      self.errdim = 2  # use full covariance matrix in fit

    def get_xCov(self):
      return self.covx

    def get_yCov(self):
      return self.covy
    
      
    def __call__(self, *par):  # we accept a variable number of model parameters
      resid = self.y - self.model(self.x, *par)
      if self.rebuildCov:
        self.mpar = par
        self.rebuild_Cov()
      if self.errdim < 2:
        # fast calculation for simple errors
        return np.sum(resid * self.iCov*resid)
      else:
        # with full inverse covariance matrix for correlated errors
        return np.inner(np.matmul(resid.T, self.iCov), resid)

  # --- end definition of class LSQwithCov ----

  # --- helper functions ----
  
  def buildCovarianceMatrix(nd, e, erel=None, eabscor=None, erelcor=None, data=None):
    """
    Build a covariance matrix from independent and correlated error components

    Independent errors must be given; they define the diagonal of the matrix.
    Correlated absolute and/or relative uncertainties enter in the diagonal 
    and off-diagonal elements of the covariance matrix. Covariance matrix
    elements of the individual components are added to from the complete
    Covariance Matrix.

    Args:
      * nd: number of data points
      * e: scalar, array of float, 2d-array of float: 
       independent uncertainties or a full covariance matrix
      * erel: scalar, array of float, 2d-array of float: 
       independent relative uncertainties or a full covariance matrix
      * eabscor: floats or array of float of list of arrays of float:
          absolute correlated uncertainties
      * erelcor: floats or array of float of list of arrays of float:
          relative correlated uncertainties
      * data: array of float: data, needed to compute relative uncertainties

    Returns:
      * nd x nd np-array of float: covariance matrix 
    """

    # 1. independent errors
    e_ = np.array(e)*np.ones(nd) # ensure array of length nd
    if e_.ndim == 2: # already got a matrix, take as covariance matrix
      cov = e_
    else:
      cov = np.diag(e_*e_) # set diagonal elements of covariance matrix

    # 2. add relative errors
    if erel is not None:
      er_ = np.array(erel)*np.ones(nd)  # ensure array of length nd
      cov += np.diag(er_*er_) * data    # set diagonal elements of covariance matrix
          
    # 3. add absolute, correlated error components  
    if eabscor is not None:
      if len(np.shape(np.array(eabscor))) < 2: # has one entry
        c_ = np.array(eabscor)*np.ones(nd)
        cov += np.outer(c_, c_) 
      else:            # got a list, add each component
        for c in eabscor:
          c_ = np.array(eabscor)*np.ones(nd)
          cov += np.outer(c_, c_) 

    # 4. add relative, correlated error components  
    if erelcor is not None:
      if len(np.shape(np.array(erelcor))) < 2: # has one entry
        c_ = np.array(erelcor) * data
        cov += np.outer(c_, c_) 
      else:            # got a list, add each component
        for c in erelcor:
          c_ = np.array(c) * data
          cov += np.outer(c_, c_) 

    return cov

  def plotModel(iminuitObject, model, x, y, ex, ey):
    """
    Plot model function and data 

    Args: 
      * iminuitObject
      * model function
      * np-array of float: x of data
      * np-array of float: y of data
      * np-array of float: x-uncertainties      
      * np-array of float: y-uncertainties      

    Returns:
      * matplotlib figure
    """
    
  # extract parameter properties
    pmerrs = []
    m = iminuitObject
    if __version__< '2':
      pnams = m.values.keys()  # parameter names
      pvals = np.array(m.values.values()) # best-fit values
      for pnam in m.merrors.keys():
        pmerrs.append([m.merrors[pnam][2], m.merrors[pnam][3]])
    else:   # vers. >=2.0 
      pnams = m.parameters      # parameter names
      pvals = np.array(m.values) # best-fit values
      for pnam in m.merrors.keys():
        pmerrs.append([m.merrors[pnam].lower, m.merrors[pnam].upper])
    pmerrs=np.array(pmerrs)
      
  # draw data and fitted line
    fig_model = plt.figure(figsize=(7.5, 6.5))
    plt.errorbar(x, y, ey, fmt="x", color='steelblue', label="data")
    if ex is not None:
      plt.errorbar(x, y, xerr=ex, fmt='.', color='steelblue')
    xplt=np.linspace(x[0], x[-1], 100)
    plt.plot(xplt, model(xplt, *pvals), color='orange', label="fit")
    plt.xlabel('x',size='x-large')
    plt.ylabel('y = f(x, *par)', size='x-large')
   # display legend with some fit info
    fit_info = [
    f"$\\chi^2$ / $n_\\mathrm{{dof}}$ = {chi2:.1f} / {ndof}",]
    for p, v, e in zip(parnames, parvals, pmerrs):
      fit_info.append(f"{p} = ${v:.3f}^{{+{e[1]:.2g}}}_{{{e[0]:.2g}}}$")
    plt.legend(title="\n".join(fit_info))
    return fig_model
  
# plot array of profiles and contours
  def plotContours(iminuitObject):
    """
    Plot grid of profile curves and contours lines from iminuit object

    Arg: 
      * iminuitObject

    Returns:
      * matplotlib figure 
    """
    
    npar = iminuitObject.nfit    # numer of parameters
    if __version__< '2':
      pnams = m.values.keys()  # parameter names
    else:
  # vers. >=2.0 
      pnams = m.parameters      # parameter names


    fsize=3.5
    cor_fig, axarr = plt.subplots(npar, npar,
                                figsize=(fsize*npar, fsize*npar))
    ip = -1
    for i in range(0, npar):
      ip += 1
      jp = -1
      for j in range(0, npar):
        jp += 1
        if ip > jp:
         # empty space
          axarr[jp, ip].axis('off')
        elif ip == jp:
         # plot profile
          plt.sca(axarr[ip, ip])
          iminuitObject.draw_mnprofile(pnams[i], subtract_min=True)
          plt.ylabel('$\Delta\chi^2$')
        else:
          plt.sca(axarr[jp, ip])
          m.draw_mncontour(pnams[i], pnams[j]) 
    return cor_fig 
            
# --- end function definitions ----
  
  # construct error matrix from input  
  nd = len(y)
  # build (initial) covariance matrix - ignore x-errors
  dcov = buildCovarianceMatrix(nd, sy, erel=srely, eabscor=yabscor,
                               erelcor=yrelcor, data=y) 
  
  # set the cost function
  costf = LSQwithCov(x, y, dcov, fitf)

  # inspect parameters of model function and set start values for fit
  sig=signature(fitf)
  parnames=list(sig.parameters.keys())
  ipardict={}
  if p0 is not None:
    for i, pnam in enumerate(parnames[1:]):
      ipardict[pnam] = p0[i]
  else:
    # try defaults of parameters from argument list
    for i, pnam in enumerate(parnames[1:]):
      dv = sig.parameters[pnam].default   
      if dv is not Parameter.empty:
        ipardict[pnam] = dv
      else:
        ipardict[pnam] = 0.  #  use zero in worst case

  # create Minuit object
  m = Minuit(costf, **ipardict, errordef=1.)  

  # perform fit
  m.migrad()  # finds minimum of cost function

  # possibly, need to iterate fit
  if sx is not None or srelx is not None or xabscor is not None or xrelcor is not None \
     or srely is not None or yrelcor is not None : 
    print('*==* mFit iterating to take into account parameter-dependent uncertainties')
    costf.init_ErrorComponents(sx, sy, srelx, srely, xabscor, xrelcor, yabscor, yrelcor)
    m.migrad()

  # possibly, improve error matrix, in most cases done in MIGRAD already
  ## m.hesse()

  # extract result parametes !!! this part depends on iminuit version !!!
  chi2 = m.fval               # chi2 
  npar = m.nfit               # numer of parameters
  ndof = len(x) - npar   # degrees of freedom
  if __version__< '2':
    parnames = m.values.keys()  # parameter names
    parvals = np.array(m.values.values()) # best-fit values
    parerrs = np.array(m.errors.values()) # parameter uncertainties
    cov=np.array(m.matrix())
  else:
  # vers. >=2.0 
    parnames = m.parameters      # parameter names
    parvals = np.array(m.values) # best-fit values
    parerrs = np.array(m.errors) # parameter uncertainties
    cov=np.array(m.covariance)
  cor = cov/np.outer(parerrs, parerrs)

  # run profile likelihood scan to check for asymmetric errors
  minos_err = m.minos()
  pmerrs = [] 
#  print("MINOS errors:")
  if __version__< '2':
    for pnam in m.merrors.keys():
      pmerrs.append([m.merrors[pnam][2], m.merrors[pnam][3]])
   #   print(f"{3*' '}{pnam}: {m.merrors[pnam][2]:.2g}",
   #                       f"+{m.merrors[pnam][3]:.2g}")
  else:
    for pnam in m.merrors.keys():
      pmerrs.append([m.merrors[pnam].lower, m.merrors[pnam].upper])
    #  print(f"{3*' '}{pnam}: {m.merrors[pnam].lower:.2g}",
    #                      f"+{m.merrors[pnam].upper:.2g}")      
  pmerrs=np.array(pmerrs)

  # produce graphical output if requested 
  if plot:
    ey = costf.get_yCov()
    if ey.ndim ==2:
      ey = np.sqrt(np.diag(ey))
    else:
      ey = np.sqrt(ey)
    ex = costf.get_xCov()
    if ex is not None:
      ex = np.sqrt(np.diag(ex))
  fig_model = plotModel(m, costf.model, x, y, ex, ey)

  if plot_cor:
    fig_cont = plotContours(m)

  return parvals, pmerrs, cor, chi2
      
if __name__ == "__main__": # --------------------------------------  
  #
  # Example of an application
  #
  # define the model function to fit
  def model(x, A=1., x0=1.):
    return A*np.exp(-x/x0)
  mpardict = {'A':1., 'x0':0.5}  # model parameters

# set error components 
  sabsy = 0.07
  srely = 0.05
  cabsy = 0.05
  crely = 0.03
  sabsx = 0.05
  srelx = 0.05
  cabsx = 0.05
  crelx = 0.03

# generate pseudo data
  np.random.seed(314159)      # initialize random generator
  nd=10
  data_x = np.linspace(0, 1, nd)       # x of data points
  sigy = np.sqrt(sabsy * sabsy + (srely*model(data_x, **mpardict))**2)
  sigx = np.sqrt(sabsx * sabsx + (srelx * data_x)**2)
  xt, yt, data_y = ppk.generateXYdata(data_x, model, sigx, sigy,
                                      xabscor=cabsx,
                                      xrelcor=crelx,
                                      yabscor=cabsy,
                                      yrelcor=crely,
                                      mpar=mpardict.values() )

# perform fit to data with iminuit
  parvals, parerrs, cor, chi2 = mFit(model, data_x, data_y,
                                     sx=sabsx,
                                     sy=sabsy,
                                     srelx=srelx,
                                     srely=srely,
                                     xabscor=cabsx,
                                     xrelcor=crelx,
                                     yabscor=cabsy,
                                     yrelcor=crely,
                                     p0=(1., 0.5),
                                     plot=True, plot_cor=True)

# Print results to illustrate how to use output
  print('\n*==* Fit Result:')
  print(f" chi2: {chi2:.3g}")
  print(f" parameter values:      ", parvals)
  print(f" neg. parameter errors: ", parerrs[:,0])
  print(f" pos. parameter errors: ", parerrs[:,1])
  print(f" correlations : \n", cor)
  
  plt.show()
