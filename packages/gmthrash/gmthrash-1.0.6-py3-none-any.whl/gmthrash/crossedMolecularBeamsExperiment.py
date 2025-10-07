#!/usr/bin/env python3
import pandas
import numpy as np
#from mpmath import gamma
from scipy.special import gamma
from scipy.optimize import fsolve
from scipy.integrate import simpson
from scipy.integrate import quad
from scipy import signal
import matplotlib.pyplot as plt
import sys
import re


inputfile = "input.pan"

imageLABfile = inputfile + ".LAB.png"
imageCMfile = inputfile + ".CM.png"

dataLABTOFfile = inputfile + ".MONTOF.dat"
dataLABANGfile = inputfile + ".MONBANG.dat"
dataCMPEfile = inputfile + ".MONPE.dat"
dataCMTfile = inputfile + ".MONT.dat"

print_flag = False

are_you_impatient = True

TOFplot_Tmin = 0.0
TOFplot_Tmax = 1000.0

######################################################################################################

class crossedmolecularbeamsexperiment:

  def __init__(self):

    self.degTOrad  = np.pi / 180.0

    pass

  def readPAN(self,inputfile):

    # Read the input file
    total_fields = []
    with open(inputfile) as f:
      all_lines = f.readlines()
      for i, line in enumerate(all_lines):
        all_lines[i] = all_lines[i].split("#")[0].split("!")[0]
    
        if (i == 0):
          commentline = all_lines[i]
        else:
          fields = re.split(r'\s+', all_lines[i])
          for field in fields:
            if (field != ""):
              total_fields.append(field)
    
    field = total_fields
    
    overallkey = field[0]
    self.PscatteringenergyPointForm = int(overallkey[2])
    self.Nproductchannels = int(overallkey[-2])
    if (self.Nproductchannels < 1):
      raise ValueError("The key on line 2 ("+overallkey+") has an incorrect number of product channels (2nd to last number) ... should be > 0")
    
    self.NvA = int(field[1])
    self.NvB = int(field[2])
    self.NthetaA = int(field[3])
    self.NthetaB = int(field[4])
    
    self.crossing_angle = float(field[5])      # Does not affect program (assumed 90)
    self.thetaAdivergence = float(field[6])
    self.thetaBdivergence = float(field[7])
    self.velocity_selected = int(field[8])     # Does not affect program
    
    self.vAmaxx = float(field[9])
    self.SA     = float(field[10])
    self.vBmaxx = float(field[11])
    self.SB     = float(field[12])
    
    Nfield = 12
    self.productchannelinfos = []
    for Nproductchannel in range(self.Nproductchannels):
      Nfield += 1
      mA = float(field[Nfield])
      Nfield += 1
      mB = float(field[Nfield])
    
      Nfield += 1
      branching_ratio = float(field[Nfield])
      Nfield += 1
      mP = float(field[Nfield])

      Nfield += 1
      NPtheta = int(field[Nfield])
      Nfield += 1
      PscatteringanglePointForm = int(field[Nfield])
      Nfield += 1

      productchannelinfo = {"mA":mA, "mB":mB, "branching_ratio":branching_ratio, "mP":mP, "NPtheta":NPtheta, "PscatteringanglePointForm":PscatteringanglePointForm}

      if (PscatteringanglePointForm):
        PscatteringanglePointForm_x = []
        for i in range(NPtheta):
          PscatteringanglePointForm_x.append(np.cos(self.degTOrad*float(field[Nfield])))
          Nfield += 1
        PscatteringanglePointForm_y = []
        for i in range(NPtheta):
          PscatteringanglePointForm_y.append(float(field[Nfield]))
          Nfield += 1

        # Reverse the order of the list to make it be in increasing order cos(theta)
        PscatteringanglePointForm_x.reverse()
        PscatteringanglePointForm_y.reverse()

        PthetaParameters = [PscatteringanglePointForm_x, PscatteringanglePointForm_y]
        def Ptheta(cthetaprod,PthetaParameters):
          return np.interp(cthetaprod,PthetaParameters[0],PthetaParameters[1])

      else:
        PthetaParameters = []
        for i in range(NPtheta):
          PthetaParameters.append(float(field[Nfield]))
          Nfield += 1

        def Ptheta(cthetaprod,PthetaParameters):
          cdoublethetaprod = 1.5e0*(cthetaprod**2) - 0.5e0
          return PthetaParameters[0] + PthetaParameters[1] * cthetaprod + PthetaParameters[2] * cdoublethetaprod

      productchannelinfo["Ptheta"] = Ptheta
      productchannelinfo["PthetaParameters"] = PthetaParameters
    
      if not (self.PscatteringenergyPointForm):

        PET_n    = float(field[Nfield])          # (goes with Emin)
        Nfield += 1
        PET_m    = float(field[Nfield])          # (goes with Emax)
        Nfield += 1
        PET_Emax = float(field[Nfield])*4.184    # In kcal/mol
        Nfield += 1
        PET_Emin = float(field[Nfield])*4.184    # In kcal/mol
        Nfield += 1

        PETParameters = (PET_n,PET_m,PET_Emax,PET_Emin)
        def PET(ET,Erel,PETParameters):
          return ((ET - PETParameters[3])**PETParameters[0]) * ((PETParameters[2]+Erel - ET)**PETParameters[1])

      else:

        x        = int(field[Nfield])            # The number of Erel to simulate for (for now, just ignore and assume it is 1)
        Nfield += 1
        dET      = float(field[Nfield])*4.184    # Spacing between translational energies ... in kcal/mol
        Nfield += 1
        ETstart  = float(field[Nfield])          #
        Nfield += 1
        ETstart  = float(field[Nfield])*4.184    # Redundant variable with above? ... in kcal/mol
        Nfield += 1
        Erel     = float(field[Nfield])*4.184    # The Erel for this P(ET) ... in kcal/mol
        Nfield += 1

        NPET    = int(field[Nfield])
        Nfield += 1
        PET_x = []
        PET_y = []
        for i in range(NPET):
          PET_x.append(ETstart + i*dET)
          PET_y.append(float(field[Nfield]))
          Nfield += 1

        PETParameters = (PET_x, PET_y)
        def PET(ET,Erel,PETParameters):
          return np.interp(ET,PETParameters[0],PETParameters[1])

      productchannelinfo["PET"] = PET
      productchannelinfo["PETParameters"] = PETParameters

      self.productchannelinfos.append(productchannelinfo)

    self.Nlabtheta = int(field[Nfield])
    Nfield += 1
    self.Nvscan = int(field[Nfield])
    Nfield += 1
    self.vscan0 = float(field[Nfield])
    Nfield += 1
    self.dvscan = float(field[Nfield])
    
    self.labthetas = []
    self.labthetaTOF = []
    self.labthetaintensities = []
    self.labthetaTOF_channelstart = []
    self.labthetaTOF_channelend = []
    self.labthetaTOF_channeloffset = []
    self.labthetaTOF_channelexclude = []
    self.labthetaTOFintensities = []
    for i in range(self.Nlabtheta):
      Nfield += 1
      self.labthetas.append(float(field[Nfield]))
      Nfield += 1
      self.labthetaintensities.append(float(field[Nfield]))
      Nfield += 1
      self.labthetaTOF.append(int(field[Nfield]))
    
      if (self.labthetaTOF[-1] == 0):
        Nfield += 1
        self.labthetaTOF_channelstart.append(int(field[Nfield]))
        Nfield += 1
        self.labthetaTOF_channelend.append(int(field[Nfield]))
        Nfield += 1
        self.labthetaTOF_channeloffset.append(int(field[Nfield]))
        Nfield += 1
        self.labthetaTOF_channelexclude.append(int(field[Nfield]))
    
        self.labthetaTOFintensities.append([])
        for j in range(self.labthetaTOF_channelstart[-1]-1, self.labthetaTOF_channelend[-1]):
          Nfield += 1
          self.labthetaTOFintensities[-1].append(float(field[Nfield]))
        self.labthetaTOFintensities[-1] = np.array(self.labthetaTOFintensities[-1])
    
    
    Nfield += 1
    self.ionflightconstant = float(field[Nfield])
    Nfield += 1
    self.ionflightmass = float(field[Nfield])
    Nfield += 1
    self.ionizerlength = float(field[Nfield])         # Does not affect program
    Nfield += 1
    self.L = float(field[Nfield])
    Nfield += 1
    self.dTOF = float(field[Nfield])
    Nfield += 1
    self.toffset = float(field[Nfield])
    
    Nfield += 1
    self.chopperwheel_freq = float(field[Nfield])
    Nfield += 1
    self.chopperwheel_diameter = float(field[Nfield])
    Nfield += 1
    self.chopperwheel_slitwidth = float(field[Nfield])
    Nfield += 1
    self.chopperwheel_Nslits = float(field[Nfield])
    
    Nfield += 1
    self.Ncollisionenergies = int(field[Nfield])
    self.Pcollisionenergies_x = np.zeros(self.Ncollisionenergies)
    self.Pcollisionenergies_y = np.zeros(self.Ncollisionenergies)
    for i in range(self.Ncollisionenergies):
      Nfield += 1
      self.Pcollisionenergies_x[i] = float(field[Nfield])*4.184     # In kcal/mol (?)
    for i in range(self.Ncollisionenergies):
      Nfield += 1
      self.Pcollisionenergies_y[i] = float(field[Nfield])
    
    print("# Done reading input!")
    print("# Input:")
    print("# " + commentline,end="")
    print("")

######################################################################################################

  # Get the reactive cross section function of the collision energy
  def Pcollisionenergies(self,x):
    return np.interp(x,self.Pcollisionenergies_x,self.Pcollisionenergies_y)

  # Get the primary beam velocity probability
  def PvA(self,v):
    return (v**2)*np.exp(-((((v/self.vAmp) - 1.0e0)*self.SA)**2))

  # Get the secondary beam velocity probability
  def PvB(self,v):
    return (v**2)*np.exp(-((((v/self.vBmp) - 1.0e0)*self.SB)**2))

######################################################################################################

  def setup_nonPANvariables(self):

    # Secret parameters (that I am guessing)
    self.detectorDiameter = 0.38  # in cm
    self.Ndetector = 5
    
    # Distance from primary beam nozzle A/B to the collision center
    self.LA = 0.10e-1 # in cm
    self.LB = 0.10e-1 # in cm
    
    self.LA = 2.71e-0 # in cm
    self.LB = 2.51e-0 # in cm

    # Distance from detector to the collision center
    self.LD = 32.92e-0 # in cm
    
    # Size of the detector's aperature
    self.detector_aperature = 0.20  # in mm
    
    # The number of points to convolve over in the ionizer
    self.Nionizer = 5
    
    # The interval for scanning v1s
    self.dv1s_scan = 0.001
    
    # Sus settings:
    
    # Don't scan over the detector diameter:
    if True:
      self.detectorDiameter = 0.0  # in cm
      self.Ndetector = 1
      pass

  def setup_postPANvariables(self):

    # Get conversions, constants, and units ready
    self.pisquared = np.pi * np.pi
    self.picubed   = self.pisquared * np.pi
    
    # Convert velocities to 10^5 cm/s (so they naturally convert to kJ/mol later in the equations)
    self.vAmaxx = self.vAmaxx * 1.0e-1
    self.vBmaxx = self.vBmaxx * 1.0e-1
    
    # Specify variables (sorry, the naming is confusing...)
    # maxx = maximum velocity       (vmax, input for GMTHRASH)   # Note: not the LITERAL maximum velocity
    #   mp = flow velocity          (v0, variable in formula)
    #   pp = most probable velocity (vpeak)
    self.vAmp = 2.0e0*self.vAmaxx/(1.0e0 + np.sqrt(1.0e0 + 8/(self.SA**2)))
    self.vBmp = 2.0e0*self.vBmaxx/(1.0e0 + np.sqrt(1.0e0 + 8/(self.SB**2)))
    self.vApp = (self.vAmp/2.0e0)*(1.0e0 + np.sqrt(1.0e0 + 4/(self.SA**2)))
    self.vBpp = (self.vBmp/2.0e0)*(1.0e0 + np.sqrt(1.0e0 + 4/(self.SB**2)))
    
    # And get the (rough) area under its curve from the first to last point
    Pcollisionenergies_vals = list(zip(self.Pcollisionenergies_x,self.Pcollisionenergies_y))
    self.Pcollisionenergiestotal_constant = 1.0e0 / sum([(valL[1]+valR[1])/(2*(valR[0]-valL[0])) for valL,valR in zip(Pcollisionenergies_vals[:-1],Pcollisionenergies_vals[1:])])
    
    # Prepare for the largest TOF to be simulated
    self.Ndata = max(self.labthetaTOF_channelend)
    
    ######################################################################################################

    # Make the thetaA and thetaB divergence smaller
    if True:
      self.thetaAdivergence = self.thetaAdivergence * -0.500
      self.thetaBdivergence = self.thetaBdivergence * -0.500
      pass
    
    # To make things go a bit faster (computationally)
    if are_you_impatient:
    # self.NvA = min(self.NvA,9)
    # self.NvB = min(self.NvB,5)
      self.NthetaA = min(self.NthetaA,3)
      self.NthetaB = min(self.NthetaB,1)
    
      self.NthetaA = min(self.NthetaA,1)
      self.NthetaB = min(self.NthetaB,1)
      pass
    
    ######################################################################################################
    
    # Prepare the digital filter (the "trapezoid filter function")
    
    # Use the wheel info to construct a shutter function
    filterchannels  = 1.0e5 / (np.pi * self.chopperwheel_diameter * self.chopperwheel_freq * 2.0 * self.dTOF)
    NchannelsBASE = filterchannels * (self.chopperwheel_slitwidth + self.detector_aperature)
    lengthA = min(self.chopperwheel_slitwidth,self.detector_aperature)
    NchannelsTOP = NchannelsBASE - 2*lengthA*filterchannels
    
    # This function (a trapezoid) has to be manually constructed
    Nwindowhalf = int(np.ceil(NchannelsBASE-0.5)+1)
    xwindows = np.arange(1-2*Nwindowhalf,2*Nwindowhalf,2)*0.5e0
    
    xvals = np.array([-NchannelsBASE,-NchannelsTOP,NchannelsTOP,NchannelsBASE])
    yvals = np.array([0.0,1.0,1.0,0.0])
    
    # And then the area under the curve for each channel must be estimated
    self.digitalfilterwindow = []
    for xpair in zip(xwindows[:-1],xwindows[1:]):
      x = np.linspace(xpair[0],xpair[1],100)
      y = np.interp(x, xvals, yvals)
    
      self.digitalfilterwindow.append(simpson(y,x=x))
    
    del x, y, xvals, yvals, xwindows
    
    # Finally, it is normalized
    self.digitalfilterwindow = np.array(self.digitalfilterwindow)
    self.digitalfilterwindow = self.digitalfilterwindow / sum(self.digitalfilterwindow)
    
    # You can also test other windows if you want:
    # filterwindow = signal.windows.hann(3)
    
    ######################################################################################################
    
    # Prepare the primary beam velocity scan
    funcAmax = max(self.PvA(self.vAmp),self.PvA(self.vApp))
    def funcA(v):
      return self.PvA(v) - funcAmax*0.01e0
    dvA = self.vAmp * (1.5e0/self.SA)
    self.vAmin = fsolve(funcA,self.vAmp-dvA)[0]
    self.vAmax = fsolve(funcA,self.vAmp+dvA)[0]
    assert(self.vAmin < self.vAmax)
    
    # Prepare the secondary beam velocity scan
    funcBmax = max(self.PvB(self.vBmp),self.PvB(self.vBpp))
    def funcB(v):
      return self.PvB(v) - funcBmax*0.01e0
    dvB = self.vBmp * (1.5e0/self.SB)
    self.vBmin = fsolve(funcB,self.vBmp-dvB)[0]
    self.vBmax = fsolve(funcB,self.vBmp+dvB)[0]
    assert(self.vBmin < self.vBmax)

    ######################################################################################################

    # Prepare the TOF "channels"
    self.tstart = -self.toffset - self.ionflightconstant * np.sqrt(self.ionflightmass) + 5.136   # Don't change this!
    self.invdTOF = 1.0e0 / self.dTOF

    self.channelstart = self.tstart * self.invdTOF + 0.5

    # Prepare the convolution over the ionizer length
    self.ionizer_convolution = (self.L + np.linspace(0,self.ionizerlength,self.Nionizer))
    
    self.TOFvelocitybounds = []
    for i in range(self.Nionizer):
      velocitybounds = self.invdTOF*10*self.ionizer_convolution[i]/(np.arange(self.Ndata+1)+self.channelstart)  # Add one more bin at the end to allow identification of overshooting
      velocitybounds_max = np.max(velocitybounds) *1.1
      velocitybounds[velocitybounds<0] = velocitybounds_max
      self.TOFvelocitybounds.append(-velocitybounds)              # Note: we want an ASCENDING order for bounds, so just make these negative velocities
      

######################################################################################################

  # Get the conversion between lab velocities and channels pre-hashed here
  def velocityTOchannel(self,vs):
    allchannels = []
    vs_neg = -vs
    for i in range(self.Nionizer):
      channels = np.searchsorted(self.TOFvelocitybounds[i],vs_neg,side='left') - 1  # Note: underflows are in bin index "-1" and overflows are in bin "self.Ndata"
      allchannels.append(channels)  
	
#   numpy searchsorted:
#     "left"  a[i-1] < v <= a[i]
#     "right" a[i-1] <= v < a[i]

    return allchannels

######################################################################################################

  # Do a forward convolution for a single product channel and detector angle

  def forwardConvolute(self,productchannelinfo,detectorinfo):

    # Unpack all the information of this product channel
    mA = productchannelinfo["mA"]
    mB = productchannelinfo["mB"]
    mP = productchannelinfo["mP"]
    NPtheta = productchannelinfo["NPtheta"]
    PscatteringanglePointForm = productchannelinfo["PscatteringanglePointForm"]
    Ptheta = productchannelinfo["Ptheta"]
    PthetaParameters = productchannelinfo["PthetaParameters"]
    PETfunc = productchannelinfo["PET"]
    PETParameters = productchannelinfo["PETParameters"]
#   PET_n = productchannelinfo["PET_n"]
#   PET_m = productchannelinfo["PET_m"]
#   PET_Emax = productchannelinfo["PET_Emax"]
#   PET_Emin = productchannelinfo["PET_Emin"]

    # Unpack all the information of this detctor angle
    cthetaD, sthetaD, xD0, dxDx, dxDy, dxDz, wDx, wDy, wDz = detectorinfo
  
    m = mA + mB
    mu = (mA*mB) / m
    muP = (mP*(m-mP)) / m
    invmuP = 1.0e0 / muP
  
    massconverter = 2*((m-mP)/(m*mP))
    invmassconverter = 1.0e0 / massconverter
  
    # Prepare the integrals of P(ET) and P(theta) so that they are correctly
    # normalized (important when there are multiple channels)
#   PETtotal_constant = 1.0e0 / (float(gamma(PET_m+1) * gamma(PET_n+1) / gamma(PET_m+PET_n+2)))
#   Pthetatotal_constant = 1.0e0 / ((Ptheta[0]+0.25e0*Ptheta[2])*np.pi)
    PETtotal_constant = 1.0e0
    Pthetatotal_constant = 1.0e0 / quad(Ptheta,-1.0e0,1.0e0,args=(PthetaParameters))[0]
    
    # In Weiss, the P(ET) -> P(u) transformation brings with it mass converter, as well as m/mP... just stick it in here
    PETtotal_constant = PETtotal_constant * ((m)/(mP)) / (massconverter)
  
    # Two things will be returned: the relative energies and the TOFintensities
    # All other important variables can be derived from these
    Erels = []
    TOFs = []
    
    # Iterate over the reactant beams' angular divergences
  # for thetaA, wthetaA in zip(*np.polynomial.legendre.leggauss(NthetaA)):
  #   thetaA = thetaA * thetaAdivergence
  #   for thetaB, wthetaB in zip(*np.polynomial.legendre.leggauss(NthetaB)):
  #     thetaB = thetaB * thetaBdivergence
    for thetaA in np.linspace(0.0e0, self.thetaAdivergence, self.NthetaA):
      wthetaA = 1.0e0
      for thetaB in np.linspace(0.0e0, self.thetaBdivergence, self.NthetaB):
        wthetaB = 1.0e0

        # If you want to change the crossing angle, change how the secondary
        # beam velocity vector vB is defined here, as well as how to solve
        # for their collision point xC
    
        vAunit = np.array([np.cos(thetaA*self.degTOrad), np.sin(thetaA*self.degTOrad), 0.0e0])
        vBunit = np.array([np.sin(thetaA*self.degTOrad), np.cos(thetaB*self.degTOrad), 0.0e0])
    
        # Use the primary beam angular divergences to figure out
        # where the particles collide
        slopeA = np.tan(thetaA*self.degTOrad)
        if (thetaB == 0):
          xCx = 0.0e0
          xCy = slopeA*(xCx - self.LA)
        else:
          slopeB = 1.0e0/np.tan(thetaB*self.degTOrad)
          xCx = (self.LA*slopeA - self.LB)/(slopeA - slopeB)
          xCy = slopeB*xCx - self.LB
        xC = np.array([xCx, xCy, 0.0])
        wC = np.array([wthetaA,wthetaB])
    
        # Iterate over the reactant beams' velocities
        for unitvAmag, wvAmag in zip(*np.polynomial.legendre.leggauss(self.NvA)):
          vAmag = self.vAmin + (unitvAmag+1.0e0)*0.5e0*(self.vAmax-self.vAmin)
          for unitvBmag, wvBmag in zip(*np.polynomial.legendre.leggauss(self.NvB)):
            vBmag = self.vBmin + (unitvBmag+1.0e0)*0.5e0*(self.vBmax-self.vBmin)
        
            vA = vAunit * vAmag
            vB = vBunit * vBmag
            
            vCM  = (mA*vA + mB*vB) / m
            vrel = vA - vB
            vrelsq = vrel[0]**2 + vrel[1]**2 + vrel[2]**2
            Erel = 0.5e0 * mu * vrelsq
  
            PvAB = (wvAmag * self.PvA(vAmag)) * (wvBmag * self.PvB(vBmag))
            PvAB = PvAB * np.sqrt(vAmag**2 + vBmag**2) 
  
            # Note that P(ET) should be normalized so we need to scale it by the integral:
            #   integral from ET_min to ET_max of P(ET) dET
            # which comes out to ((ET_max-ET_min)^(PET_m+PET_n+1)) * gamma(PET_m+1) * gamma(PET_n+1) / gamma(PET_m+PET_n+2)
            # where luckily those gamma function calls are constant, so are calculated outisde of this loop
            #           Note to self: provide proof that this integral is correct
#           invPETtotal = PETtotal_constant / ((PET_Emax+Erel-PET_Emin)**(PET_m+PET_n+1))
#           invPthetatotal = Pthetatotal_constant
            if (len(PETParameters)==4):
              PET_Emax = PETParameters[2]
              PET_Emin = PETParameters[3]
            else:
              PET_Emax = PETParameters[0][-1]
              PET_Emin = PETParameters[0][0]
            invPETtotal = PETtotal_constant / quad(PETfunc,PET_Emin,PET_Emax+Erel,args=(Erel,PETParameters))[0]
            invPthetatotal = Pthetatotal_constant
  
            # The collision energy dependence of the reaction cross section
            PvAB = PvAB * self.Pcollisionenergies(Erel)   # Normally, it is: ((Erel)**(-0.33e0))
  
            # The P(ET) and P(theta) curves have to be normalized for each collision energy
            PvAB = PvAB * invPETtotal * invPthetatotal
  
            
            # Iterate over detection points
            for dxDwD in zip(dxDx, dxDy, dxDz, wDx, wDy, wDz):
              dxD = np.array(dxDwD[:3])
              wD  = np.array(dxDwD[3:])
              xD = xD0 + dxD
  
              # Weight each Newton circle separately
              Pnewton = np.prod(wC) * np.prod(wD) * PvAB
            
              if True:
    
                TOF = np.zeros(self.Ndata)
    
                # Parametrize the line of collision-to-detection
                my = (xC[1]-xD[1])/(xC[0]-xD[0])
                mz = (xC[2]-xD[2])/(xC[0]-xD[0])
                  
                by = (xC[0]*xD[1]-xC[1]*xD[0])/(xC[0]-xD[0])
                bz = (xC[0]*xD[2]-xC[2]*xD[0])/(xC[0]-xD[0])
    
                # Calculate the edge of the Newton circle to potentially
                # skip some velocities to scan
                A  = (1.0e0 + my**2 + mz**2)
                B  = -2*(vCM[0] + my*(vCM[1]-by) + mz*(vCM[2]-bz))
                C0 = vCM[0]**2 + (by - vCM[1])**2 + (bz - vCM[2])**2
                vperp = C0 - B*B/(4*A)
                Eperpprod = 0.5e0*(m*mP/(m-mP))*vperp
                if (vperp < 0):
                  TOFs.append(TOF)
                  Erels.append(Erel)
                  continue

                
                # Calculate the bounds of the integral over v1sq
                v1smin = np.sqrt(max(vperp,massconverter*PET_Emin))
                v1smax = np.sqrt(massconverter*(PET_Emax + Erel))
                dv1s_prod = np.abs((v1smax - v1smin) * self.dv1s_scan)
                Pnewton = Pnewton * dv1s_prod
     
                # Create a vector of v1sq
                v1sq = np.arange(v1smin + (dv1s_prod)/2, v1smax, dv1s_prod)**2
  
                # Calculate the energy and get its probability
                Eprodtrans = v1sq*invmassconverter # (m*mP/(2*(m-mP)))
                Etrans = Eprodtrans
#               PET = ((Eprodtrans - PET_Emin)**PET_n) * ((PET_Emax+Erel - Eprodtrans)**PET_m)
                PET = PETfunc(Eprodtrans,Erel,PETParameters)
  
                # Solve for the Newton circle solutions (two roots)
                C = C0 - v1sq
                discriminant = B**2 - 4*A*C
                orig_indices = np.where(discriminant>=0)
                discriminant = np.sqrt(discriminant[orig_indices])
                dum1 = 0.5e0 / A
                roots = np.append((-B - discriminant), (-B + discriminant))
                orig_indices = np.append(orig_indices,orig_indices)
                roots_mask = roots>0
                roots = roots[roots_mask] * dum1
                orig_indices = orig_indices[roots_mask]
  
                # Convert these roots to lab velocities
                vLABx = roots
                vLABy = my*vLABx + by
                vLABz = mz*vLABx + bz
                ux = vLABx - vCM[0]
                uy = vLABy - vCM[1]
                uz = vLABz - vCM[2]
  
                # Get angular information and probabilities
                cthetaprod = (ux*vrel[0]+uy*vrel[1]+uz*vrel[2]) / np.sqrt(v1sq[orig_indices] * vrelsq)
#               cdoublethetaprod = 1.5e0*(cthetaprod**2) - 0.5e0
#               Pthetaprod = Ptheta[0] + Ptheta[1] * cthetaprod + Ptheta[2] * cdoublethetaprod
                Pthetaprod = Ptheta(cthetaprod,PthetaParameters)
                Pthetaprod_mask = Pthetaprod>0
                orig_indices = orig_indices[Pthetaprod_mask]
                Proot = PET[orig_indices]*Pthetaprod[Pthetaprod_mask]
  
                vLABx = vLABx[Pthetaprod_mask]
                vLABy = vLABy[Pthetaprod_mask]
                vLABz = vLABz[Pthetaprod_mask]
                ux = ux[Pthetaprod_mask]
                uy = uy[Pthetaprod_mask]
                uz = uz[Pthetaprod_mask]
                vLABsq = vLABx**2 + vLABy**2 + vLABz**2
                vLABmag = np.sqrt(vLABsq)
                uDOTvLAB = np.abs(ux*vLABx+uy*vLABy+uz*vLABz)

                dProot = (vLABsq) / uDOTvLAB
                Proot *= dProot
                
                if (len(vLABmag)==0): next
                
                allTOFchannels = self.velocityTOchannel(vLABmag)
                for TOFchannels in allTOFchannels:
                
                  # Add the probability to the TOF
                  for aProot, TOFchannel in zip(Proot,TOFchannels):
                    if (TOFchannel < self.Ndata):
                      if (TOFchannel < 0):
                        print("Invalid time")
  #                     raise ValueError("Invalid time")
                        continue
  
                      TOF[TOFchannel] += aProot 
                
  
                # Scale by the probability of that Newton circle
                TOFs.append(TOF * Pnewton)
                Erels.append(Erel)
  
    return Erels, TOFs
  
  
######################################################################################################

  def scanlabangles(self):

    print("# Simulating TOFs...")
    
    simulatedlabthetaintensities = []
    simulatedlabthetaTOFintensities = []
    
    # Iterate over each lab angle
    for NthetaDetector,thetaDetector in enumerate(self.labthetas):
    
      cthetaD = np.cos(thetaDetector*self.degTOrad)
      sthetaD = np.sin(thetaDetector*self.degTOrad)
      xD0 = np.array([cthetaD, sthetaD, 0.0e0]) * self.LD
    
      # Prepare the detection points (assume detector plane is perpendicular to detector angle)
      dxDx, wDx = np.polynomial.legendre.leggauss(self.Ndetector)
      dxDy, wDy = np.polynomial.legendre.leggauss(self.Ndetector)
      wDz = np.ones(self.Ndetector)
      dxDx = dxDx * (-sthetaD) *self. detectorDiameter*0.5
      dxDy = dxDy *  (cthetaD) * self.detectorDiameter*0.5
      dxDz = np.zeros(self.Ndetector)
    
      detectorinfo = (cthetaD, sthetaD, xD0, dxDx, dxDy, dxDz, wDx, wDy, wDz)
    
      # Iterate over each product channel
      totalTOFs = []
      totalErels = []
      for Nproductchannel in range(self.Nproductchannels):
    
        # Forward convolute!
        Erels, TOFs = self.forwardConvolute(self.productchannelinfos[Nproductchannel],detectorinfo)
        TOFs = np.array(TOFs)
    
        # Add TOFs over each Newton circle
        totalTOF = np.sum(TOFs,axis=0)*self.productchannelinfos[Nproductchannel]["branching_ratio"]
    
        # Convolute the TOF over the "trapezoidal slit function" (which broadens it)
        totalTOF = signal.convolve(totalTOF, self.digitalfilterwindow, mode="same")
    
        extrawindow = signal.windows.hann(9)
        totalTOF = signal.convolve(totalTOF, extrawindow, mode="same")
    
        totalTOFs.append(totalTOF)
        totalErels.append(sum(Erels)/len(Erels))
    
      TOFs = np.array(totalTOFs).reshape((self.Nproductchannels,self.Ndata))
      Erels = np.array(totalErels).reshape((self.Nproductchannels))
      del totalTOFs, totalErels
    
      # After collecting the TOFs, combine them to an overall TOF and
      # also normalize each
      TOFscalings = np.array([sum(TOFs[i]) for i in range(TOFs.shape[0])])
      TOForder = np.arange(self.Nproductchannels)
    
      # Keep track of the relative energies as well (for bookkeeping)
      mu = self.productchannelinfos[0]["mA"] * self.productchannelinfos[0]["mB"] / (self.productchannelinfos[0]["mA"]+self.productchannelinfos[0]["mB"])
      Erel = 0.5e0 * mu * (self.vApp**2 + self.vBpp**2)
      Erels = Erels / Erel
      
      
      if (print_flag):
    
        TOF = [sum(TOFs[:,i]) for i in range(TOFs.shape[1])]
        TOFscaling = np.max(TOF)
        if (TOFscaling == 0): TOFscaling = 1.0e0
    
        print(("# {:8s}   {:>8s}  "+self.Nproductchannels*" {:>8s}" + "      Relative cross section: {:12.6e}     labTheta: {:.2f}").format("Time(us)", "P(calc)", *["P("+str(i)+")" for i in range(self.Nproductchannels)], sum(TOFscalings), thetaDetector))
        for TOFchannel in range(self.Ndata):
          print(("  {:8.1f}   {:8.3f}  "+self.Nproductchannels*" {:8.3f}").format((TOFchannel)*self.dTOF + self.tstart, TOF[TOFchannel]/TOFscaling, *TOFs[:,TOFchannel]/TOFscaling))
    
        print("",end="",flush=True)
    
      else:
        print(("#  Relative cross section: {:12.6e}     labTheta: {:.2f}").format(sum(TOFscalings), thetaDetector))
    
      # Add them to our final tallies
      simulatedlabthetaintensities.append(TOFscalings)
      if (self.labthetaTOF[NthetaDetector] == 0):
        simulatedlabthetaTOFintensities.append(TOFs)
   

######################################################################################################
    
    # Figure out the ideal scaling of the simulated TOFs to the raw TOFs
    
    self.labthetaTOFintensities = np.array(self.labthetaTOFintensities)
    self.labthetaintensities = np.array(self.labthetaintensities)
    simulatedlabthetaTOFintensities = np.array(simulatedlabthetaTOFintensities)
    simulatedlabthetaintensities = np.array(simulatedlabthetaintensities)
    
    totalsimulatedlabthetaTOFintensities = np.sum(simulatedlabthetaTOFintensities[:,:,:],axis=1)
    totalsimulatedlabthetaintensities    = np.sum(simulatedlabthetaintensities[:,:],axis=1)
    
    
    # First, scale the angular intensities
    corr_rawsimulated       = sum(self.labthetaintensities*totalsimulatedlabthetaintensities)
    corr_simulatedsimulated = sum(totalsimulatedlabthetaintensities**2)
    scaling_rawsimulated = corr_rawsimulated / corr_simulatedsimulated
    simulatedlabthetaintensities = scaling_rawsimulated * simulatedlabthetaintensities
    totalsimulatedlabthetaintensities = scaling_rawsimulated * totalsimulatedlabthetaintensities
    
    # Second, scale the TOF intensities (not the same as the angular intensities, since the intergal is not over the entire channel)
    
    # Method 1: All scaled the same (I think this is wrong, since each has a different integral bound)
    if False:
      corr_rawsimulated       = 0.0e0
      corr_simulatedsimulated = 0.0e0
      for i in range(self.labthetaTOFintensities.shape[0]):
        corr_rawsimulated       += sum(self.labthetaTOFintensities[i]*totalsimulatedlabthetaTOFintensities[i])
        corr_simulatedsimulated += sum(totalsimulatedlabthetaTOFintensities[i]**2)
      scaling_rawsimulated = corr_rawsimulated / corr_simulatedsimulated
      simulatedlabthetaTOFintensities = scaling_rawsimulated * simulatedlabthetaTOFintensities
      totalsimulatedlabthetaTOFintensities = scaling_rawsimulated * totalsimulatedlabthetaTOFintensities
    
    # Method 2: Each scaled separately
    else:
      for i in range(self.labthetaTOFintensities.shape[0]):
        corr_rawsimulated       = sum(self.labthetaTOFintensities[i]*totalsimulatedlabthetaTOFintensities[i])
        corr_simulatedsimulated = sum(totalsimulatedlabthetaTOFintensities[i]**2)
        if (corr_simulatedsimulated > 0):
          scaling_rawsimulated = corr_rawsimulated / corr_simulatedsimulated
          simulatedlabthetaTOFintensities[i] = scaling_rawsimulated * simulatedlabthetaTOFintensities[i]
          totalsimulatedlabthetaTOFintensities[i] = scaling_rawsimulated * totalsimulatedlabthetaTOFintensities[i]
    
    
    print("# Done simulating TOFs!")
    print("")
    return simulatedlabthetaintensities, totalsimulatedlabthetaintensities, simulatedlabthetaTOFintensities, totalsimulatedlabthetaTOFintensities


######################################################################################################

  def plotLABfits(self,simulatedlabthetaintensities,simulatedlabthetaTOFintensities,imagename):

    fig = plt.figure(figsize=(13.0,5.0))
  
    # First, the angular intensities:
    ax1 = fig.add_axes([0.60, 0.15, 0.35, 0.80])
    ax1.set_xlabel('Lab Angle (o)')
    ax1.set_ylabel('Relative Intensity')
    ax1.scatter(self.labthetas, self.labthetaintensities, marker='o', s=50, color='black')
    ax1.plot(self.labthetas, totalsimulatedlabthetaintensities, linestyle='-', color='red')
  
    # Figure out how to layout the TOFs
    Nplots = int(sum(np.array(self.labthetaTOF)==0))
    if (Nplots > 10):
      Nrows = 3
    elif (Nplots > 3):
      Nrows = 2
    else:
      Nrows = 1
    Ncolumns = int(np.ceil(Nplots / Nrows))
  
    Nplot = -int((Nrows*Ncolumns-Nplots) / 2)
  
    ax2 = []
    plotDX = (0.45/Ncolumns)
    plotDY = (0.80/Nrows)
    plotX = 0.05
    plotY = 0.15 + (Nrows-1)*plotDY
  
    # Plot the TOFs from left-to-right, and top-to-bottom
    for i in range(Nrows):
  
      plotX = 0.05
      for j in range(Ncolumns):
  
        if ((Nplot >= 0) and (Nplot < Nplots)):
          ax2.append(fig.add_axes([plotX, plotY, plotDX, plotDY]))
  
  #       ax2[-1].set_xlim(left=tstart,right=Ndata*dTOF+tstart)
          ax2[-1].set_xlim(left=TOFplot_Tmin,right=TOFplot_Tmax)
          ax2[-1].set_ylim(bottom=np.min(self.labthetaTOFintensities)*0.5,top=np.max(self.labthetaTOFintensities)*1.1)
  
          if (i == Nrows-1):
            ax2[-1].set_xlabel('Time (us)')
            if (j > 0):
              old_xticks = ax2[-1].get_xticks()
              new_xticks = old_xticks[1:]
              ax2[-1].set_xticks(new_xticks)
              ax2[-1].set_xlim(left=TOFplot_Tmin,right=TOFplot_Tmax)  # flag
          else:
            ax2[-1].set_xticklabels("")
          if (j == 0):
            ax2[-1].set_ylabel('Intensity')
          else:
            ax2[-1].set_yticklabels("")
  
          plt.text(.99, .99, str(np.array(self.labthetas)[np.array(self.labthetaTOF)==0][Nplot]), ha='right', va='top', transform=ax2[-1].transAxes)
  
          ax2[-1].scatter(np.arange(self.labthetaTOF_channelstart[Nplot]-1,self.labthetaTOF_channelend[Nplot])*self.dTOF + self.tstart, self.labthetaTOFintensities[Nplot], marker='o', facecolors='none', edgecolors='black', s=10)
          ax2[-1].plot(np.arange(self.labthetaTOF_channelstart[Nplot]-1,self.labthetaTOF_channelend[Nplot])*self.dTOF + self.tstart, totalsimulatedlabthetaTOFintensities[Nplot], linestyle='-', color='red')
          Nplot += 1
  
        plotX += plotDX
  
      plotY -= plotDY
  
    fig.savefig(imagename)
    plt.close(fig)
  

  def plotCMfits(self,imagename):

    # If this is a multichannel fit, layout things differently
    if (self.Nproductchannels == 1):
      fig = plt.figure(figsize=(5.0,8.0))
      ax1 = fig.add_axes([0.15, 0.15, 0.80, 0.35])
      ax2 = fig.add_axes([0.15, 0.60, 0.80, 0.35])

    else:
      fig = plt.figure(figsize=(13.0,8.0))
      plotDX = 0.85 / (1 + self.Nproductchannels)
      ax1 = fig.add_axes([0.10, 0.15, plotDX-0.05, 0.35])
      ax2 = fig.add_axes([0.10, 0.60, plotDX-0.05, 0.35])
      axes1 = []
      axes2 = []
      totalweight = 0.0e0
      for Nproductchannel in range(self.Nproductchannels):
        axes1.append(fig.add_axes([plotDX + 0.15 + Nproductchannel*plotDX, 0.15, plotDX-0.05, 0.35]))
        axes1[-1].set_yticklabels("")
        axes1[-1].set_xlabel('Scattering Angle (o)')
        axes2.append(fig.add_axes([plotDX + 0.15 + Nproductchannel*plotDX, 0.60, plotDX-0.05, 0.35]))
        axes2[-1].set_yticklabels("")
        axes2[-1].set_xlabel('Translational Energy (kJ/mol)')
        totalweight += self.productchannelinfos[Nproductchannel]["branching_ratio"]

      for Nproductchannel in range(self.Nproductchannels):
        plt.text(.99, .99, "Weight: {:.1f}%".format(self.productchannelinfos[Nproductchannel]["branching_ratio"]*100.0/totalweight), ha='right', va='top', transform=axes2[Nproductchannel].transAxes)


    # First the scattering angle:

    ax1.set_xlabel('Scattering Angle (o)')
    ax1.set_ylabel('Intensity')
    x = np.linspace(0.0,180.0,300)
  
    # Iterate over each product channel
    PET_Emax_max = 0.0e0
    ys = []
    y = np.zeros(len(x))
    for Nproductchannel in range(self.Nproductchannels):
      Ptheta = self.productchannelinfos[Nproductchannel]["Ptheta"]
      PthetaParameters = self.productchannelinfos[Nproductchannel]["PthetaParameters"]
      Pthetatotal_constant = 1.0e0 / quad(Ptheta,-1.0e0,1.0e0,args=(PthetaParameters))[0]
      P1 = np.cos(x*self.degTOrad)
      P2 = 1.5e0*(P1**2) - 0.5e0
      ys.append(Ptheta(P1,PthetaParameters) * Pthetatotal_constant)
      y += ys[-1] * self.productchannelinfos[Nproductchannel]["branching_ratio"]

      mu = self.productchannelinfos[Nproductchannel]["mA"] * self.productchannelinfos[Nproductchannel]["mB"] / (self.productchannelinfos[Nproductchannel]["mA"]+self.productchannelinfos[Nproductchannel]["mB"])
      Erel = 0.5e0 * mu * (self.vApp**2 + self.vBpp**2)
      if (len(self.productchannelinfos[Nproductchannel]["PETParameters"])==4):
        PET_Emax = self.productchannelinfos[Nproductchannel]["PETParameters"][2]
      else:
        PET_Emax = self.productchannelinfos[Nproductchannel]["PETParameters"][0][-1]
      PET_Emax_max = max(PET_Emax_max,PET_Emax+Erel)

    ax1.set_xlim(left=0.0,right=180.0)
    ax1.set_ylim(bottom=0,top=np.max(y)*1.1)
    ax1.plot(x, y, linestyle='-', color='red')

    if (self.Nproductchannels > 1):
      for Nproductchannel in range(self.Nproductchannels):
        axes1[Nproductchannel].set_xlim(left=0.0,right=180.0)
        axes1[Nproductchannel].set_ylim(bottom=0,top=np.max(ys[Nproductchannel])*1.1)
        axes1[Nproductchannel].plot(x, ys[Nproductchannel], linestyle='-', color='red')

    # Second the translational energy:
  
    ax2.set_xlabel('Translational Energy (kJ/mol)')
    ax2.set_ylabel('Intensity')
    x = np.linspace(0.0,(PET_Emax_max)*1.1,300)
  
    ys = []
    y = np.zeros(len(x))
    for Nproductchannel in range(self.Nproductchannels):

      mu = self.productchannelinfos[Nproductchannel]["mA"] * self.productchannelinfos[Nproductchannel]["mB"] / (self.productchannelinfos[Nproductchannel]["mA"]+self.productchannelinfos[Nproductchannel]["mB"])
      Erel = 0.5e0 * mu * (self.vApp**2 + self.vBpp**2)
      PETfunc = self.productchannelinfos[Nproductchannel]["PET"]
      PETParameters = self.productchannelinfos[Nproductchannel]["PETParameters"]
      if (len(PETParameters)==4):
        PET_Emax = PETParameters[2]
        PET_Emin = PETParameters[3]
      else:
        PET_Emax = PETParameters[0][-1]
        PET_Emin = PETParameters[0][0]
      PETtotal_constant = 1.0e0 / quad(PETfunc,PET_Emin,PET_Emax+Erel,args=(Erel,PETParameters))[0]

      ys.append(np.zeros(len(x)))
      for i in range(len(x)):
        if ((x[i] > PET_Emin) and (x[i] < PET_Emax+Erel)):
          ys[-1][i] += PETfunc(x[i],Erel,PETParameters) * PETtotal_constant
          y[i] += ys[-1][i] * self.productchannelinfos[Nproductchannel]["branching_ratio"]
  
    if (np.max(y) > 0):
      y = y / np.max(y)
      ys = ys / np.max(y)
    ax2.set_xlim(left=0,right=(PET_Emax_max)*1.1)
    ax2.set_ylim(bottom=0,top=np.max(y)*1.1)
    ax2.plot(x, y, linestyle='-', color='red')

    if (self.Nproductchannels > 1):
      for Nproductchannel in range(self.Nproductchannels):
        axes2[Nproductchannel].set_xlim(left=0.0,right=(PET_Emax_max)*1.1)
        axes2[Nproductchannel].set_ylim(bottom=0,top=np.max(ys[Nproductchannel])*1.1)
        axes2[Nproductchannel].plot(x, ys[Nproductchannel], linestyle='-', color='red')

    fig.savefig(imagename)
    plt.close(fig)



######################################################################################################

  def writeCMdata(self,dataCMPEfile,dataCMTfile):
  
    # First, CM P(ET):

    PET_Emax = 0.0e0
    for Nproductchannel in range(len(self.productchannelinfos)):
      PETParameters = self.productchannelinfos[Nproductchannel]["PETParameters"]
      if (len(PETParameters)==4):
        tmpPET_Emax = PETParameters[2]
      else:
        tmpPET_Emax = PETParameters[0][-1]
      PET_Emax = max(PET_Emax,tmpPET_Emax)
    
    mu = self.productchannelinfos[0]["mA"] * self.productchannelinfos[0]["mB"] / (self.productchannelinfos[0]["mA"]+self.productchannelinfos[0]["mB"])
    Erel = 0.5e0 * mu * (self.vApp**2 + self.vBpp**2)
    x = np.linspace(0.0,(PET_Emax+Erel)*1.1,100)
    
    y = np.zeros((len(self.productchannelinfos),len(x)))
    for Nproductchannel in range(len(self.productchannelinfos)):
      PETfunc = self.productchannelinfos[Nproductchannel]["PET"]
      PETParameters = self.productchannelinfos[Nproductchannel]["PETParameters"]
      if (len(PETParameters)==4):
        PET_Emax = PETParameters[2]
        PET_Emin = PETParameters[3]
      else:
        PET_Emax = PETParameters[0][-1]
        PET_Emin = PETParameters[0][0]
      for i in range(len(x)):
        if (x[i] < PET_Emin):
          y[Nproductchannel,i]=0.0e0
        elif (x[i] > PET_Emax+Erel):
          y[Nproductchannel,i]=0.0e0
        else:
          y[Nproductchannel,i] = PETfunc(x[i],Erel,PETParameters)
      if (np.max(y[Nproductchannel]) > 0): y[Nproductchannel] = y[Nproductchannel] / np.max(y[Nproductchannel])

    f = open(dataCMPEfile,"w")
    f.write(("#{:7s} " + len(self.productchannelinfos)*" {:>5s}" + "\n").format("E(kcal)",*["P("+str(i)+")" for i in range(len(self.productchannelinfos))]) )
    for i in range(len(x)):
      f.write(("{:8.2f} " + len(self.productchannelinfos)*" {:5.2f}" + "\n").format(x[i]/4.184,*y[:,i]))
    f.close()

    
    # Second, CM P(theta):
    
    x = np.linspace(0.0,180.0,100)
    P1 = np.cos(x*self.degTOrad)
    P2 = 1.5e0*(P1**2) - 0.5e0
    
    y = []
    for Nproductchannel in range(len(self.productchannelinfos)):
      Ptheta = self.productchannelinfos[Nproductchannel]["Ptheta"]
      PthetaParameters = self.productchannelinfos[Nproductchannel]["PthetaParameters"]
      y.append(Ptheta(P1,PthetaParameters))
    y = np.array(y)

    f = open(dataCMTfile,"w")
    f.write(("#{:7s} " + len(self.productchannelinfos)*" {:>7s}" + "\n").format("Theta",*["P("+str(i)+")" for i in range(len(self.productchannelinfos))]) )
    for i in range(len(x)):
      f.write(("{:8.1f} " + len(self.productchannelinfos)*" {:7.3f}" + "\n").format(x[i],*y[:,i]))
    f.close()
    

  def writeLABdata(self,simulatedlabthetaintensities,totalsimulatedlabthetaintensities,simulatedlabthetaTOFintensities,totalsimulatedlabthetaTOFintensities,dataLABANGfile,dataLABTOFfile):
    
    # Third, MONBANG:
    
    f = open(dataLABANGfile,"w")
    f.write(("#{:5s}   {:8s}   {:8s}  "+self.Nproductchannels*" {:>8s}"+"\n").format("Angle", " rawInt.", "calcInt.", *["I("+str(i)+")" for i in range(self.Nproductchannels)]))
    for i,thetaDetector in enumerate(self.labthetas):
      f.write(("{:6.2f}   {:8d}   {:8.2f}  "+self.Nproductchannels*" {:8.2f}"+"\n").format(thetaDetector,int(self.labthetaintensities[i]), totalsimulatedlabthetaintensities[i], *simulatedlabthetaintensities[i]))
    f.close()
    
    
    # Fourth, MONTOF:
    
    j = 0
    f = open(dataLABTOFfile,"w")
    for i,thetaDetector in enumerate(self.labthetas):
      if (self.labthetaTOF[i] == 0):
        TOF = totalsimulatedlabthetaTOFintensities[j]
        f.write(("# {:8s}   {:>8s}   {:>8s}  "+self.Nproductchannels*" {:>8s}" + "      Relative cross section: {:12.6e}     labTheta: {:.2f}\n").format("Time(us)", "P(raw)", "P(calc)", *["P("+str(i)+")" for i in range(self.Nproductchannels)], totalsimulatedlabthetaintensities[i], thetaDetector))
        for TOFchannel in range(self.Ndata):
          f.write(("  {:8.1f}   {:8.3f}   {:8.3f}  "+self.Nproductchannels*" {:8.3f}"+"\n").format((TOFchannel)*self.dTOF + self.tstart, self.labthetaTOFintensities[j][TOFchannel], totalsimulatedlabthetaTOFintensities[j][TOFchannel],*simulatedlabthetaTOFintensities[j][:,TOFchannel]))
        j += 1
      else:
        f.write(("# {:8s}   {:>8s}   {:>8s}  "+self.Nproductchannels*" {:>8s}" + "      Relative cross section: {:12.6e}     labTheta: {:.2f}\n").format("Time(us)", "P(raw)", "P(calc)", *["P("+str(i)+")" for i in range(self.Nproductchannels)], totalsimulatedlabthetaintensities[i], thetaDetector))
    f.close()
  



