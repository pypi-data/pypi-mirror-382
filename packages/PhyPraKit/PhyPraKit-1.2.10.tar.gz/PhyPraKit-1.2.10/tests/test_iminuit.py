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

def mFit(fitf, x, y, sx = None, sy = None,
         srelx = None, srely = None, 
         xabscor = None, xrelcor = None,        
         yabscor = None, yrelcor = None,
         p0 = None, constraints = None, 
         plot = True, plot_cor = True ):
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
      * constraints: list or list of lists with [name or id, value, error]
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

  class Data_and_Uncertainties:
    """
    class to handle data and uncertainties
    """

    def __init__(self, x, y, err):
      self.x = np.asarray(x)
      self.y = np.asarray(y)
      # initialize uncertainties and eventually covariance matrix
      self.initCov(err)
      # model is possibly needed for parameter-dependent uncertainties
      self.model = None
      
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

      self.covy = self.err2
      self.covx = None
      self.cov = self.covy      

    def init_ErrorComponents(self, ex, ey, erelx, erely, cabsx, crelx, cabsy, crely, model):
      # if set, covariance matrix will be recomputed each time in the fit
      self.ex = ex
      self.ey = ey
      self.erelx = erelx
      self.erely = erely
      self.cabsx = cabsx
      self.crelx = crelx
      self.cabsy = cabsy
      self.crely = crely
      self.model = model

      # rebuild covariance matrix during fitting procedure
      self.rebuildCov=True  # flag used in cost function
      self.errdim = 2       # use full covariance matrix in cost function
      # build static part of covariance Matrix
      self.nd = len(self.x)
      self.staticCov = build_CovarianceMatrix(self.nd,
                    self.ey, eabscor = self.cabsy)

    def rebuild_Cov(self, mpar):
      """
      (Re-)Build the covariance matrix from components
      """
      # use pre-built parameter-independent part of Covariance Matrix
      self.cov = np.array(self.staticCov, copy=True)

      # parameter-dependent y-uncertainties
      if self.erely is not None or self.crely is not None:
        ydat = self.model(self.x, *mpar)       
        self.cov += build_CovarianceMatrix(self.nd,
                            erel=self.erely, erelcor=self.crely, data=ydat)
      self.covy = np.array(self.cov, copy=True)

      # add up x-uncertainties (all are parameter-dependent) 
      if (self.ex is not None and self.ex !=0) or self.erelx is not None:
        self.covx = build_CovarianceMatrix(self.nd,
                              self.ex, self.erelx,
                              self.cabsx, self.crelx,
                              self.x)
        
       # determine derivatives of model function w.r.t. x,
       #  distance dx from smallest uncertaintey
        dx = np.sqrt(min(np.diag(self.covx)))/10.
        mprime = 0.5/dx*(self.model(self.x+dx,*mpar)-self.model(self.x-dx,*mpar))
        # project on y and add to covariance matrix
        self.cov += np.outer(mprime, mprime) * self.covx

 #     print('*!!! rebuild_Cov:')
 #     print('covy:\n',covy)
 #     print('covx=:\n',covx)
 #     print('deriv:}n',mprime)
 #     if covx is not None: print('covx_proj:\n',covx_projected)
 #     sys.exit()
      
      # set inverse covariance matrix 
      self.iCov = np.matrix(self.cov).I

    def get_Cov(self):
      return self.cov
  
    def get_xCov(self):
      return self.covx

    def get_yCov(self):
      return self.covy
      
  # define custom cost function for iminuit
  class LSQwithCov:
    """
    custom Least-SQuares cost function with error matrix
    """
  
    def __init__(self, data, model):
      from iminuit.util import describe, make_func_code

      self.data = data
      self.model = model 
      # set proper signature of model function for iminuit
      self.pnams = describe(model)[1:]
      self.func_code = make_func_code(self.pnams)
      self.npar = len(self.pnams)
      # dictionary assigning parameter name to index
      self.pnam2id = {
        self.pnams[i] : i for i in range(0,self.npar)
        } 
      self.ndof = len(data.y) - self.npar
      self.nconstraints = 0

    def addConstraints(self, constraints):
      # add parameter constraints
      #  format: list or list of lists with [name, value, uncertainty]
      if isinstance(constraints[1], list):
         self.constraints = constraints
      else:
         self.constraints = [constraints]
      self.nconstraints = len(self.constraints)   
         
    def __call__(self, *par):  # accept a variable number of model parameters
      # called iteratively by minuit

      dc = 0. 
      #  first, take into account possible parameter constraints  
      if self.nconstraints:
        for c in self.constraints:
          if type(c[0])==type(' '):
            p_id = self.pnam2id[c[0]]
          else:
            p_id = c[0]
          r = ( par[p_id] - c[1]) / c[2] 
          dc += r*r

      # check if Covariance matrix needs rebuilding
      if self.data.rebuildCov:
        self.data.rebuild_Cov(par)

      # add chi2 of data wrt. model    
      resid = self.data.y - self.model(self.data.x, *par)
      if data.errdim < 2:
        # fast calculation for simple errors
        return dc + np.sum(resid * self.data.iCov*resid)
      else:
        # with full inverse covariance matrix for correlated errors
        return dc + np.inner(np.matmul(resid.T, self.data.iCov), resid)

  # --- end definition of class LSQwithCov ----

  # --- helper functions ----
  
  def build_CovarianceMatrix(nd, e=None, erel=None,
                             eabscor=None, erelcor=None, data=None):
    """
    Build a covariance matrix from independent and correlated 
    absolute or relative error components

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
      * data: array of float: data, needed only for relative uncertainties

    Returns:
      * nd x nd np-array of float: covariance matrix 
    """

    # 1. independent errors
    if e is not None:
      e_ = np.asarray(e)
      if e_.ndim == 2: # already got a matrix, take as covariance matrix
        cov = e_
      else:
        e_ = np.ones(nd)*np.array(e) # ensure array of length nd
        cov = np.diag(e_*e_) # set diagonal elements of covariance matrix
    else:
      cov = np.zeros( (nd, nd) )
      
    # 2. add relative errors
    if erel is not None:
      er_ = np.array(erel) * data  # ensure array of length nd
      cov += np.diag(er_*er_)      # set diagonal elements of covariance matrix
          
    # 3. add absolute, correlated error components  
    if eabscor is not None:
      eac=np.asarray(eabscor)
      if len(np.shape(eac )) < 2: # has one entry
        c_ = eac * np.ones(nd)
        cov += np.outer(c_, c_) 
      else:            # got a list, add each component
        for c in eabscor:
          c_ = np.array(c)*np.ones(nd)
          cov += np.outer(c_, c_) 

    # 4. add relative, correlated error components
    if erelcor is not None:
      ear=np.asarray(erelcor)
      if len(np.shape(ear) ) < 2: # has one entry
        c_ = ear * data
        cov += np.outer(c_, c_) 
      else:            # got a list, add each component
        for c in erelcor:
          c_ = np.array(c) * data
          cov += np.outer(c_, c_) 
    # return complete matrix
    return cov

  def plotModel(iminuitObject, costFunction):
    """
    Plot model function and data 

    Args: 
      * iminuitObject
      * cost Fuction of type LSQwithCov
 
    Returns:
      * matplotlib figure
    """
    
  # extract parameter properties
    pmerrs = []
    m = iminuitObject
    cf = costFunction

  # get parameters
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
    ndof =costFunction.ndof

  # get data
    x = cf.data.x
    y = cf.data.y
    ey = cf.data.get_yCov()
    if ey.ndim ==2:
      ey = np.sqrt(np.diag(ey))
    else:
      ey = np.sqrt(ey)
    ex = cf.data.get_xCov()
    if ex is not None:
      if ex.ndim ==2:
        ex = np.sqrt(np.diag(ex))
      else:
        ex = np.sqrt(ex)

  # draw data and fitted line
    fig_model = plt.figure(figsize=(7.5, 6.5))
    if ex is not None:
      plt.errorbar(x, y, xerr=ex, yerr=ey, fmt='x', label='data')
    else:
      plt.errorbar(x, y, ey, fmt="x", label='data')
    xplt=np.linspace(x[0], x[-1], 100)
    plt.plot(xplt, costFunction.model(xplt, *pvals), label="fit")
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
  dcov = build_CovarianceMatrix(nd, sy, erel=srely, eabscor=yabscor,
                               erelcor=yrelcor, data=y) 
  data = Data_and_Uncertainties(x, y, dcov)  

  # set the cost function
  costf = LSQwithCov(data, fitf)

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

  if constraints is not None:
    costf.addConstraints(constraints)
        
  # create Minuit object
  if __version__ < '2':
    m = Minuit(costf, **ipardict, errordef=1.)
  else:
    m = Minuit(costf, **ipardict)  
    m.errordef = 1.
  
  # perform fit
  m.migrad()  # finds minimum of cost function

  # possibly, need to iterate fit
  if sx is not None or srelx is not None or xabscor is not None or xrelcor is not None \
     or srely is not None or yrelcor is not None : 
    print('*==* mFit iterating to take into account parameter-dependent uncertainties')
    data.init_ErrorComponents(sx, sy,
                              srelx, srely,
                              xabscor, xrelcor,
                              yabscor, yrelcor,
                              costf.model)
    m.migrad()

  # possibly, improve error matrix, in most cases done in MIGRAD already
  ## m.hesse()

  # extract result parametes !!! this part depends on iminuit version !!!
  chi2 = m.fval               # chi2 
  npar = m.nfit               # numer of parameters
  ndof = len(x)+costf.nconstraints-npar   # degrees of freedom
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
    fig_model = plotModel(m, costf)
  
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
  srely = 0.05 # 5% of model value
  cabsy = 0.04
  crely = 0.03 # 3% of model value
  sabsx = 0.05
  srelx = 0.04 # 4%
  cabsx = 0.03
  crelx = 0.02 # 2%

# generate pseudo data
  np.random.seed(314)      # initialize random generator
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
#                                     constraints=['A', 1., 0.03],
#                                     constraints=[0, 1., 0.03],
                                     plot=True, plot_cor=False)

# Print results to illustrate how to use output
  print('\n*==* Fit Result:')
  print(f" chi2: {chi2:.3g}")
  print(f" parameter values:      ", parvals)
  print(f" neg. parameter errors: ", parerrs[:,0])
  print(f" pos. parameter errors: ", parerrs[:,1])
  print(f" correlations : \n", cor)
  
  plt.show()
