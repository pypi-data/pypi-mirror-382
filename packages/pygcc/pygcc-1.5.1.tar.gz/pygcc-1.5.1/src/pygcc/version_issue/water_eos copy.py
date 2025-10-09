#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 16:02:22 2021

@author: adedapo.awolayo and Ben Tutolo, University of Calgary

Copyright (c) 2020 - 2021, Adedapo Awolayo and Ben Tutolo, University of Calgary

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


Functions implemented here include water equation of state and dielectric properties
"""

import numpy as np, math
from scipy.optimize import root_scalar, fsolve, brentq
from scipy.linalg import lu_factor, lu_solve
from numpy import exp, log10, log

eps = 2.220446049250313e-16
J_to_cal = 4.184
np.random.seed(4321)

def convert_temperature(T, Out_Unit = 'C'):
    """
    This function converts temperatures from Celsius to Kelvin and vice-versa

    Parameters
    ----------
        T : float, vector
            Temperature in °C or K  \n
        Out_Unit  : string
            Expected temperature unit (C or K)  \n

    Returns
    ----------
        T : float, vector
            Temperature in °C or K

    Examples
    ----------
    >>> TC = 100; convert_temperature( TC, Out_Unit = 'K' )
        373.15
    >>> TK = 520; convert_temperature( TK, Out_Unit = 'C' )
        246.85
    """
    #Accepted units for input and output are:
    unit_markers = ['C', 'K']
    if not (Out_Unit in unit_markers):
        return None
    elif Out_Unit == 'K':
        return T + 273.15
    elif Out_Unit == 'C':
        return T - 273.15


def derivative(f, a, method = 'central', h = 0.001):
    '''Compute the derivative of f, f'(a) with step size h.
    Parameters
    ----------
    f : function
        Vectorized function of one variable
    a : number
        Compute derivative at x = a
    method : string
        Difference formula: 'forward', 'backward' or 'central'
    h : number
        Step size in difference formula
    Returns
    -------
    float
        Difference formula:
            central: f(a + h) - f(a - h))/2h
            forward: f(a + h) - f(a))/h
            backward: f(a) - f(a-h))/h
    '''
    if method == 'central':
        return (f(a + h) - f(a - h))/(2*h)
    elif method == 'forward':
        return (f(a + h) - f(a))/h
    elif method == 'backward':
        return (f(a) - f(a - h))/h
    else:
        raise ValueError("Method must be 'central', 'forward' or 'backward'.")


def readIAPWS95data():
    """
    returns all constants and coefficients needed for the IAPWS95 formulation, packed into a dictionary
    """

    # Constants for IAPWS-95-Formulation
    R       = 461.51805      			# R: specific gas constant in J/(kg*K)
    Tc      = 647.096        			# T_c: critical temperature of water in K
    rhoc    = 322            			# rho_c: critical density of water in kg/m^3
    Pc      = 22.06400000000213	        # P_c: critical pressure of water in MPa
    # n0(1:8)
    n0      = [-8.320446483749615, 6.683210527593193, 3.00632, 0.012436,
               0.97315, 1.27950, 0.96956, 0.24873]
    # gamma0(1:8)
    gamma0  = [0.0, 0.0, 0.0, 1.28728967, 3.53734222, 7.74073708, 9.24437796, 27.5075105]
    # n(1:56)
    n       = [0.12533547935523e-1,  0.78957634722828e+1, -0.87803203303561e+1,
               0.31802509345418e+0, -0.26145533859358e+0, -0.78199751687981e-2,
               0.88089493102134e-2, -0.66856572307965e+0,  0.20433810950965e+0,
               -0.66212605039687e-4, -0.19232721156002e+0, -0.25709043003438e+0,
               0.16074868486251e+0, -0.40092828925807e-1,  0.39343422603254e-6,
               -0.75941377088144e-5,  0.56250979351888e-3, -0.15608652257135e-4,
               0.11537996422951e-8,  0.36582165144204e-6, -0.13251180074668e-11,
               -0.62639586912454e-9, -0.10793600908932e+0,  0.17611491008752e-1,
               0.22132295167546e+0, -0.40247669763528e+0,  0.58083399985759e+0,
               0.49969146990806e-2, -0.31358700712549e-1, -0.74315929710341e+0,
               0.47807329915480e+0,  0.20527940895948e-1, -0.13636435110343e+0,
               0.14180634400617e-1,  0.83326504880713e-2, -0.29052336009585e-1,
               0.38615085574206e-1, -0.20393486513704e-1, -0.16554050063734e-2,
               0.19955571979541e-2,  0.15870308324157e-3, -0.16388568342530e-4,
               0.43613615723811e-1,  0.34994005463765e-1, -0.76788197844621e-1,
               0.22446277332006e-1, -0.62689710414685e-4, -0.55711118565645e-9,
               -0.19905718354408e+0,  0.31777497330738e+0, -0.11841182425981e+0,
               -0.31306260323435e+2,  0.31546140237781e+2, -0.25213154341695e+4,
               -0.14874640856724e+0,  0.31806110878444e+0]
    # c(1:51)
    c       = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
               2, 2, 3, 3, 3, 3, 4, 6, 6, 6, 6]
    # d(1:54)
    d       = [1,  1,  1,  2,  2,  3,  4,  1,  1,  1,  2,  2,  3,  4,  4,
               5,  7,  9, 10, 11, 13, 15,  1,  2,  2,  2,  3,  4,  4,  4,
               5,  6,  6,  7,  9,  9,  9,  9,  9, 10, 10, 12,  3,  4,  4,
               5, 14,  3,  6,  6,  6,  3,  3,  3]
    # t(1:54)
    t       = [-0.5, 0.875, 1, 0.5, 0.75, 0.375, 1, 4, 6, 12, 1, 5, 4, 2, 13,
               9, 3, 4, 11, 4, 13, 1, 7, 1, 9, 10, 10, 3, 7, 10, 10, 6, 10,
               10, 1, 2, 3, 4, 8, 6, 9, 8, 16, 22, 23, 23, 10, 50, 44, 46, 50, 0, 1, 4]
    # alpha(52:54)
    alpha   = [20, 20, 20]
    # beta(52:56)
    beta    = [150, 150, 250, 0.3, 0.3]
    # gamma(52:54)
    gamma   = [1.21, 1.21, 1.25]
    # epsilon(52:54)
    epsilon = [1, 1, 1]
    # a(55:56)
    a       = [3.5, 3.5]
    # b(55:56)
    b       = [0.85, 0.95]
    # A(55:56)
    A       = [0.32, 0.32]
    # B(55:56)
    B       = [0.2, 0.2]
    # C(55:56)
    C       = [28, 32]
    # D(55:56)
    D       = [700, 800]

    var = [R,Tc,Pc,rhoc,n0,gamma0,n,c,d,t,alpha,beta,gamma,epsilon,a,b,A,B,C,D]
    varname = ['R','Tc','Pc','rhoc','n0','gamma0','n','c','d','t','alpha','beta',
               'gamma','epsilon','a','b','A','B','C','D']
    coeffs = {}
    for i in range(len(var)):
        coeffs['%s' % varname[i]] = var[i]

    return coeffs

IAPWS95_COEFFS = readIAPWS95data()

class Dummy(object):
    """
    Class of functions to evaluate the IAPWS95 equation of state for calculating thermodynamic
    properties of water.    \n
    """

    def __init__(self):
        # vectorize the function above to permit array variables
        self.vEOSIAPWS95 = np.vectorize(self.EOSIAPWS95)
        self.vauxMeltingTemp = np.vectorize(self.auxMeltingTemp)
        self.vapxsatpropT = np.vectorize(self.apxsatpropT)
        self.vapxsatpropP = np.vectorize(self.apxsatpropP)
        self.vcalcsatpropT = np.vectorize(self.calcsatpropT)
        self.vcalcsatpropP = np.vectorize(self.calcsatpropP)
        self.vwaterviscosity = np.vectorize(self.waterviscosity)

    def EOSIAPWS95(self, TK, rho, FullEOSppt = False):
        """
        This function evaluates the IAPWS basic equation of state to calculate thermodynamic
        properties of water, which is written as a function of temperature and density.    \n
        Parameters
        ----------
            TK    :  temperature [K]    \n
            rho   :  density [kg/m3]    \n
            FullEOSppt: Option to output all or essential water properties [False or True]
        Returns
        ----------
            px    :  pressure [bar]    \n
            ax    :  Helmholtz energy [kJ/kg-K]    \n
            sx    :  Entropy [kJ/kg/K]    \n
            hx    :  Enthalpy [kJ/kg]    \n
            gx    :  Gibbs energy [kJ/kg]    \n
            vx    :  Volume [m3/kg]    \n
            pdx   :  Derivative of pressure with respect to delta in bar    \n
            adx   :  Helmholtz energy derivative with respect to delta    \n
            ztx   :  zeta value (needed to calculate viscosity)    \n
            ptx   :  Derivative of pressure with respect to tau in bar    \n
            ktx   :  Compressibility [/bar]    \n
            avx   :  Thermal expansion coefficient (thermal expansivity)    \n
            ux    :  Internal energy [kJ/kg]  if FullEOSppt is True  \n
            gdx   :  Gibbs energy derivative in kJ/kg   if FullEOSppt is True   \n
            bsx   :  Isentropic temperature-pressure coefficient [K-m3/kJ]    if FullEOSppt is True  \n
            dtx   :  Isothermal throttling coefficient [kJ/kg/bar]    if FullEOSppt is True  \n
            mux   :  Joule-Thomsen coefficient [K-m3/kJ]  if FullEOSppt is True  \n
            cpx   :  Isobaric heat capacity [kJ/kg/K]   if FullEOSppt is True   \n
            cvx   :  Isochoric heat capacity [kJ/kg/K]   if FullEOSppt is True   \n
            wx    :  Speed of sound [m/s]   if FullEOSppt is True   \n
        Usage
        ----------
          [px, ax, ux, sx, hx, gx, vx, pdx, adx, gdx, ztx, ptx, ktx, avx, bsx, dtx, mux, cpx, cvx, wx] = EOSIAPW95( TK, rho)
        """

        Tc = IAPWS95_COEFFS['Tc']
        Pc = IAPWS95_COEFFS['Pc']
        rhoc = IAPWS95_COEFFS['rhoc']
        # specific and molar gas constants
        R = IAPWS95_COEFFS['R']/1000 # kJ kg-1 K-1

        delta = rho/rhoc
        tau = Tc/TK

        # To avoid delta values of zero
        epxc = eps*delta
        if (delta <= epxc):
            delta = epxc
            rho = rhoc*delta

        # To avoid a singularity at the critical density (at any temperature), i.e.
        # if delta is unity, then delta - 1 is zero. This will lead to error when evaluating
        # (delta - 1)**n where n is negative, or in any division like (x/(d -1)).
        x1 = 1.0 - epxc
        x2 = 1.00 + epxc
        if (delta > x1) & (delta < x2):
            if (delta < 1.0):
                delta = x1
            else:
                delta = x2
            rho = rhoc*delta

        #%%---------------------------------------------------------
        # specific dimensionless Helmholtz free energy (phi) and its derivatives
        ## IAPWS95.residual
        def phir(delta, tau):
            """
             residual part of free energy, dimensionless
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK           dimensionless inverse temperature
            """

            # % unpack coefficients
            n = np.array(IAPWS95_COEFFS['n']);          c = np.array(IAPWS95_COEFFS['c'])
            d = np.array(IAPWS95_COEFFS['d']);          t = np.array(IAPWS95_COEFFS['t'])
            alpha = np.array(IAPWS95_COEFFS['alpha']);  beta = np.array(IAPWS95_COEFFS['beta'])
            gamma = np.array(IAPWS95_COEFFS['gamma']);  epsilon = np.array(IAPWS95_COEFFS['epsilon'])
            # a = np.array(IAPWS95_COEFFS['a']);
            b = np.array(IAPWS95_COEFFS['b'])

            y = np.dot(n[:7], (delta**d[:7] * tau**t[:7]))

            y = y + np.dot(n[7:51], (delta**d[7:51] * tau**t[7:51] * np.exp(-delta**c[7:51])))

            y = y + np.dot(n[51:54], ( delta**d[51:54] * tau**t[51:54] * np.exp(-alpha*(delta - epsilon)**2 \
                                                                                - beta[:3]*(tau - gamma)**2) ))

            y = y + np.dot(n[54:56], (Delta(delta,tau)**b * delta * Psi(delta,tau)))

            return y

        def phir_t(delta, tau):
            """
             partial derivative for tau of phir
             where phir = residual part of free energy, dimensionless
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK           dimensionless inverse temperature
            """

            # % unpack coefficients
            n = np.array(IAPWS95_COEFFS['n']);          c = np.array(IAPWS95_COEFFS['c'])
            d = np.array(IAPWS95_COEFFS['d']);          t = np.array(IAPWS95_COEFFS['t'])
            alpha = np.array(IAPWS95_COEFFS['alpha']);  beta = np.array(IAPWS95_COEFFS['beta'])
            gamma = np.array(IAPWS95_COEFFS['gamma']);  epsilon = np.array(IAPWS95_COEFFS['epsilon'])
            # a = np.array(IAPWS95_COEFFS['a']);
            b = np.array(IAPWS95_COEFFS['b'])

            y = np.dot(n[:7], (t[:7]*delta**d[:7] * tau**(t[:7]-1)))

            y = y + np.dot(n[7:51], (t[7:51]*delta**d[7:51] * tau**(t[7:51]-1) * np.exp(-delta**c[7:51])))

            y = y + np.dot(n[51:54], ( delta**d[51:54] * tau**t[51:54] * \
                                      np.exp(-alpha*(delta - epsilon)**2 - beta[:3]*(tau - gamma)**2)* \
                                      (t[51:54]/tau - 2*beta[:3]*(tau - gamma)) ))

            y = y + np.dot(n[54:56], (delta * (Delta_b_t(delta,tau) * Psi(delta,tau) + Delta(delta,tau)**b * \
                                               Psi_t(delta,tau))))

            return y

        def phir_tt(delta, tau):
            """
             second partial derivative for tau of phir
             where phir = residual part of free energy, dimensionless
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK           dimensionless inverse temperature
            """

            # % unpack coefficients
            n = np.array(IAPWS95_COEFFS['n']);          c = np.array(IAPWS95_COEFFS['c'])
            d = np.array(IAPWS95_COEFFS['d']);          t = np.array(IAPWS95_COEFFS['t'])
            alpha = np.array(IAPWS95_COEFFS['alpha']);  beta = np.array(IAPWS95_COEFFS['beta'])
            gamma = np.array(IAPWS95_COEFFS['gamma']);  epsilon = np.array(IAPWS95_COEFFS['epsilon'])
            # a = np.array(IAPWS95_COEFFS['a']);
            b = np.array(IAPWS95_COEFFS['b'])

            y = np.dot(n[:7], (t[:7]*(t[:7]-1)*delta**d[:7] * tau**(t[:7]-2)))

            y = y + np.dot(n[7:51], (t[7:51]*(t[7:51]-1)*delta**d[7:51] * \
                                     tau**(t[7:51]-2) * np.exp(-delta**c[7:51])))

            y = y + np.dot(n[51:54], ( delta**d[51:54] * tau**t[51:54] * \
                                      np.exp(-alpha*(delta - epsilon)**2 - \
                                             beta[:3]*(tau - gamma)**2)* \
                                          ( (t[51:54]/tau - 2*beta[:3]*(tau - gamma))**2 - \
                                           t[51:54]/tau**2 - 2*beta[:3] )))

            y = y + np.dot(n[54:56], (delta * (Delta_b_tt(delta,tau) * Psi(delta,tau) +\
                                               2*Delta_b_t(delta,tau) * Psi_t(delta,tau) +\
                                               Delta(delta,tau)**b * Psi_tt(delta,tau) )))

            return y

        def phir_d(delta, tau):
            """
             partial derivative for delta of phir
             where phir = residual part of free energy, dimensionless
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # % unpack coefficients
            n = np.array(IAPWS95_COEFFS['n']);          c = np.array(IAPWS95_COEFFS['c'])
            d = np.array(IAPWS95_COEFFS['d']);          t = np.array(IAPWS95_COEFFS['t'])
            alpha = np.array(IAPWS95_COEFFS['alpha']);  beta = np.array(IAPWS95_COEFFS['beta'])
            gamma = np.array(IAPWS95_COEFFS['gamma']);  epsilon = np.array(IAPWS95_COEFFS['epsilon'])
            b = np.array(IAPWS95_COEFFS['b'])

            y = np.dot(n[:7], (d[:7]*delta**(d[:7]-1) * tau**t[:7]))

            y = y + np.dot(n[7:51], ( np.exp(-delta**c[7:51]) * (delta**(d[7:51]-1) * tau**t[7:51] \
                                                           * (d[7:51] - c[7:51]*delta**c[7:51]))))

            y = y + np.dot(n[51:54], (delta**d[51:54] * tau**t[51:54] \
                                      * np.exp(-alpha*(delta - epsilon)**2 - beta[:3]*(tau - gamma)**2) \
                                          * (d[51:54]/delta - 2*alpha*(delta - epsilon))))

            tPsi = Psi(delta,tau)
            y = y + np.dot(n[54:56], (Delta(delta,tau)**b * (tPsi + delta*Psi_d(delta,tau)) \
                                      + (Delta_b_d(delta,tau)*delta*tPsi)))

            return y

        def phir_dd(delta, tau):
            """
             second partial derivative for delta of phir
             where phir = residual part of free energy, dimensionless
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # % unpack coefficients
            n = np.array(IAPWS95_COEFFS['n']);          c = np.array(IAPWS95_COEFFS['c'])
            d = np.array(IAPWS95_COEFFS['d']);          t = np.array(IAPWS95_COEFFS['t'])
            alpha = np.array(IAPWS95_COEFFS['alpha']);  beta = np.array(IAPWS95_COEFFS['beta'])
            gamma = np.array(IAPWS95_COEFFS['gamma']);  epsilon = np.array(IAPWS95_COEFFS['epsilon'])
            b = np.array(IAPWS95_COEFFS['b'])

            y = np.dot(n[:7], (d[:7]*(d[:7]-1)*delta**(d[:7]-2) * tau**t[:7]))

            y = y + np.dot(n[7:51], ( np.exp(-delta**c[7:51]) * ( delta**(d[7:51]-2) * tau**t[7:51] * \
                                                                 ((d[7:51] - c[7:51]*delta**c[7:51]) * \
                                                                  (d[7:51] - 1 - c[7:51]*delta**c[7:51]) - \
                                                                      (c[7:51])**2*delta**c[7:51]) ) ) )

            y = y + np.dot(n[51:54], ( tau**t[51:54]* np.exp(-alpha*(delta - epsilon)**2 \
                                                             -beta[:3]*(tau - gamma)**2) \
                                      * (-2*alpha*delta**d[51:54] + 4*alpha**2*delta**d[51:54]*(delta-epsilon)**2 \
                                         - 4*d[51:54]*alpha*delta**(d[51:54]-1)*(delta-epsilon) \
                                             + d[51:54]*(d[51:54]-1)*delta**(d[51:54]-2))) )

            tPsi = Psi(delta,tau)
            dPsi = Psi_d(delta,tau)
            y = y + np.dot(n[54:56], ( Delta(delta,tau)**b * (2*dPsi + delta* Psi_dd(delta,tau)) \
                                      + 2*Delta_b_d(delta,tau)*(tPsi + delta*dPsi) \
                                          + Delta_b_dd(delta,tau)*delta*tPsi) )
            return y

        def phir_dt(delta, tau):
            """
             partial derivative for delta and tau of phir
             where phir = residual part of free energy, dimensionless
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # % unpack coefficients
            n = np.array(IAPWS95_COEFFS['n']);          c = np.array(IAPWS95_COEFFS['c'])
            d = np.array(IAPWS95_COEFFS['d']);          t = np.array(IAPWS95_COEFFS['t'])
            alpha = np.array(IAPWS95_COEFFS['alpha']);  beta = np.array(IAPWS95_COEFFS['beta'])
            gamma = np.array(IAPWS95_COEFFS['gamma']);  epsilon = np.array(IAPWS95_COEFFS['epsilon'])
            b = np.array(IAPWS95_COEFFS['b'])

            y = np.dot(n[:7], (d[:7]*t[:7]*delta**(d[:7]-1) * tau**(t[:7]-1)))

            y = y + np.dot(n[7:51], (t[7:51]*  delta**(d[7:51]-1) * tau**(t[7:51]-1) \
                                     * (d[7:51] - c[7:51]*delta**c[7:51]) *np.exp(-delta**c[7:51]) ))

            y = y + np.dot(n[51:54], ( delta**d[51:54] * tau**t[51:54] \
                                      * np.exp(-alpha*(delta - epsilon)**2 - beta[:3]*(tau - gamma)**2) \
                                          * (d[51:54]/delta - 2*alpha*(delta - epsilon)) \
                                              *(t[51:54]/tau - 2*beta[:3]*(tau-gamma) )))

            tPsi = Psi(delta,tau)
            ttPsi = Psi_t(delta,tau)
            y = y + np.dot(n[54:56], ( Delta(delta,tau)**b * \
                                      (Psi_t(delta,tau) + delta*Psi_dt(delta,tau)) \
                                          + (Delta_b_d(delta,tau)*delta*ttPsi) \
                                              + Delta_b_t(delta,tau)*(tPsi+delta*Psi_d(delta,tau)) \
                                                  + Delta_b_dt(delta,tau)*delta*tPsi))
            return y

        ## IAPWS95.idealgas
        # Equation 6.5
        def phi0(delta, tau):
            """
             ideal gas part of free energy, dimensionless
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # unpack coefficients
            n0 = np.asarray(IAPWS95_COEFFS['n0'])
            gamma0 = np.asarray(IAPWS95_COEFFS['gamma0'])

            y = np.log(delta) + n0[0] + n0[1]*tau + n0[2]*np.log(tau)
            y = y + np.dot(n0[3:], np.log(1 - np.exp(-gamma0[3:]*tau)))
            return y

        # derivatives from Table 6.4
        def phi0_t(delta, tau):
            """
             partial derivative for tau of phi0
             where phi0 = ideal gas part of free energy, dimensionless
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # unpack coefficients
            n0 = np.asarray(IAPWS95_COEFFS['n0'])
            gamma0 = np.asarray(IAPWS95_COEFFS['gamma0'])

            y = n0[1] + n0[2]/tau
            y = y + np.dot(n0[3:], gamma0[3:]*(1/(1 - np.exp(-gamma0[3:]*tau))- 1.0))

            return y

        def phi0_tt(delta, tau):
            """
             second partial derivative for tau of phi0
             where phi0 = ideal gas part of free energy, dimensionless
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # unpack coefficients
            n0 = np.asarray(IAPWS95_COEFFS['n0'])
            gamma0 = np.asarray(IAPWS95_COEFFS['gamma0'])

            y = -n0[2]/tau**2
            y = y - np.dot(n0[3:], (gamma0[3:]**2*np.exp(-gamma0[3:]*tau)*(1-np.exp(-gamma0[3:]*tau))**-2 ))

            return y

        def phi0_d(delta, tau):
            """
             partial derivative for delta of phi0
             where phi0 = ideal gas part of free energy, dimensionless
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK           dimensionless inverse temperature
            """
            y = 1/delta
            return y

        def phi0_dd(delta, tau):
            """
             second partial derivative for delta of phi0
             where phi0 = ideal gas part of free energy, dimensionless
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """
            y = -1/delta**2
            return y

        def phi0_dt(delta, tau):
            """
             partial derivative for tau and delta of phi0
             where phi0 = ideal gas part of free energy, dimensionless
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """
            y = 0
            return y

        # Supporting functions for calculating the ideal-gas and residual parts in the IAPWS-95 formulation
        def Delta(delta, tau):
            """
             auxiliary function in IAPWS95 formulation
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # % unpack coefficients
            a = np.array(IAPWS95_COEFFS['a']);  B = np.array(IAPWS95_COEFFS['B'])

            return theta(delta, tau)**2 + B*((delta - 1)**2)**a

        def Delta_d(delta, tau):
            """
             Delta_d = (d Delta)/(d delta)
             auxiliary function in IAPWS95 formulation
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/T           dimensionless inverse temperature
            """

            # % unpack coefficients
            a = np.array(IAPWS95_COEFFS['a']); beta = np.array(IAPWS95_COEFFS['beta'])
            A = np.array(IAPWS95_COEFFS['A']); B = np.array(IAPWS95_COEFFS['B'])

            d1 = delta - 1
            y = d1 * ( A*theta(delta,tau)*2/beta[-2:]* (d1**2)**(1/(2*beta[-2:])-1)+ 2*B*a*(d1**2)**(a-1) )

            return y

        def Delta_dd(delta, tau):
            """
             Delta_dd = (d2 Delta)/(d delta2)
             auxiliary function in IAPWS95 formulation
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/T           dimensionless inverse temperature
            """

            # % unpack coefficients
            a = np.array(IAPWS95_COEFFS['a']); beta = np.array(IAPWS95_COEFFS['beta'])
            A = np.array(IAPWS95_COEFFS['A']); B = np.array(IAPWS95_COEFFS['B'])

            d1 = delta - 1
            y = 1/d1 * Delta_d(delta, tau) + \
                d1**2*( 4*B*a*(a-1)*(d1**2)**(a-2) + \
                       2*A**2*beta[-2:]**-2*((d1**2)**(1/(2*beta[-2:])-1))**2 + \
                           A*theta(delta,tau)*4/beta[-2:]*(1/(2*beta[-2:])-1)* (d1**2)**(1/(2*beta[-2:])-2))
            return y

        def Delta_b_d(delta, tau):
            """
             Delta_b_d = (d Delta^b)/(d delta)
             auxiliary function in IAPWS95 formulation
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # % unpack coefficients
            b = np.array(IAPWS95_COEFFS['b'])

            return b * Delta(delta,tau)**(b-1) * Delta_d(delta,tau)

        def Delta_b_dd(delta, tau):
            """
             Delta_b_dd = (d2 Delta^b)/(d delta2)
             auxiliary function in IAPWS95 formulation
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # % unpack coefficients
            b = np.array(IAPWS95_COEFFS['b'])
            y = b * ( Delta(delta,tau)**(b-1)*Delta_dd(delta,tau) + \
                      (b-1)*Delta(delta,tau)**(b-2)*(Delta_d(delta,tau))**2)

            return y

        def Delta_b_dt(delta, tau):
            """
             Delta_b_dt = (d2 Delta^b)/(d delta tau)
             auxiliary function in IAPWS95 formulation
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # % unpack coefficients
            b = np.array(IAPWS95_COEFFS['b'])
            beta = np.array(IAPWS95_COEFFS['beta'])
            A = np.array(IAPWS95_COEFFS['A'])

            d1 = delta - 1

            y = -A*b*2/beta[-2:]*Delta(delta,tau)**(b-1) * d1*(d1**2)**(1/(2*beta[-2:])-1) \
                      - 2*theta(delta,tau)*b*(b-1)*Delta(delta,tau)**(b-2) * Delta_d(delta,tau)

            return y

        def Delta_b_t(delta, tau):
            """
             Delta_b_t = (d Delta^b)/(d tau)
             auxiliary function in IAPWS95 formulation
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # % unpack coefficients
            b = np.array(IAPWS95_COEFFS['b'])

            return -2*theta(delta,tau)*b*Delta(delta,tau)**(b-1)

        def Delta_b_tt(delta, tau):
            """
             ∂2delta/∂x|y
             Delta_b_tt = (d2 Delta^b)/(d tau2)
             auxiliary function in IAPWS95 formulation
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # % unpack coefficients
            b = np.array(IAPWS95_COEFFS['b'])

            return 2*b*Delta(delta,tau)**(b-1) + 4*(theta(delta,tau))**2*b*(b-1)*Delta(delta,tau)**(b-2)

        def theta(delta, tau):
            """
             auxiliary function in IAPWS95 formulation
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # % unpack coefficients
            beta = np.array(IAPWS95_COEFFS['beta']);  A = np.array(IAPWS95_COEFFS['A'])

            return (1 - tau) + A*((delta - 1)**2)**(1./(2*beta[3:5]))

        def Psi(delta, tau):
            """
             auxiliary function in IAPWS95 formulation
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # % unpack coefficients
            C = np.array(IAPWS95_COEFFS['C'])
            D = np.array(IAPWS95_COEFFS['D'])

            return np.exp(-C*(delta-1)**2 - D*(tau - 1)**2)

        def Psi_d(delta, tau):
            """
             ∂Psi/∂delta
             Psi_d = (d Psi)/(d delta)
             auxiliary function in IAPWS95 formulation
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # % unpack coefficients
            C = np.array(IAPWS95_COEFFS['C'])

            return -2*C*(delta - 1)*Psi(delta, tau)

        def Psi_t(delta, tau):
            """
             Psi_t = ∂Psi/∂tau = (d Psi)/(d tau)
             auxiliary function in IAPWS95 formulation
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # % unpack coefficients
            D = np.array(IAPWS95_COEFFS['D'])

            return -2*D*(tau - 1)*Psi(delta,tau)

        def Psi_tt(delta, tau):
            """
             Psi_tt = ∂2Psi/∂tau2 = (d2 Psi)/(d tau2)
             auxiliary function in IAPWS95 formulation
             parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # % unpack coefficients
            D = np.array(IAPWS95_COEFFS['D'])

            return (2*D*(tau - 1)**2 - 1)*2*D*Psi(delta,tau)

        def Psi_dd(delta, tau):
            """
             Psi_dd = (d2 Psi)/(d delta2)
             auxiliary function in IAPWS95 formulation
             Parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # % unpack coefficients
            C = np.array(IAPWS95_COEFFS['C'])

            return (2*C*(delta - 1)**2 - 1)*2*C*Psi(delta, tau)

        def Psi_dt(delta, tau):
            """
             Psi_dt = (d Psi)/(d delta tau)
             auxiliary function in IAPWS95 formulation
             Parameters:
                 delta = rho/rhoc     dimensionless density
                 tau = Tc/TK          dimensionless inverse temperature
            """

            # % unpack coefficients
            C = np.array(IAPWS95_COEFFS['C'])
            D = np.array(IAPWS95_COEFFS['D'])

            return 4*C*D*(delta - 1)*(tau - 1)*Psi(delta, tau)

        # Calculate thermodynamic functions.
        # Helmholtz energy. The value is in J/kg-K.
        ax = (R*TK*( phi0(delta, tau) + phir(delta, tau) )   )

        # Pressure kpa to bar.
        px = rho*R*TK*( 1 + delta*phir_d(delta, tau) ) * 0.010

        # Internal energy. kJ/kg
        ux = R*TK*tau*( phi0_t(delta, tau) + phir_t(delta, tau) )

        # Entropy. kJ/kg/K
        sx = R*( tau*(phi0_t(delta, tau) + phir_t(delta, tau)) - phi0(delta, tau) - phir(delta, tau) )

        # Enthalpy. kJ/kg
        hx = R*TK*( 1 + tau*(phi0_t(delta, tau) + phir_t(delta, tau)) + delta*phir_d(delta, tau) )

        # Gibbs energy. kJ/kg
        # Alternate formulas for the Gibbs energy. gx = hx - TK*sx = ax + hx - ux
        gx = R*TK*( 1 + phi0(delta, tau) + phir(delta, tau) + delta*phir_d(delta, tau) )

        # Volume. m3/kg
        vx = (1/rho)

        if FullEOSppt == True:
            # Isochoric heat capacity. kJ/kg/K
            cvx = -R*tau**2*( phi0_tt(delta, tau) + phir_tt(delta, tau) )

            # Isobaric heat capacity. kJ/kg/K
            x1 = ( 1 + delta*phir_d(delta, tau) - delta*tau*phir_dt(delta, tau) )**2
            x2 = 1 + 2*delta*phir_d(delta, tau) + delta**2*phir_dd(delta, tau)
            cpx = x1*0
            cpx = float(cvx + R*(x1.item()/x2.item())) if (abs(x2.item()) > 1e-15) else 1.0 + 100

            # Speed of sound. m/s
            x1 = ( 1 + delta*phir_d(delta, tau) - delta*tau*phir_dt(delta, tau) )**2
            x2 = tau**2*( phi0_tt(delta, tau) + phir_tt(delta, tau) )
            x3 = x1/x2
            xxt = R*TK*( 1 + 2*delta*phir_d(delta, tau) + delta**2*phir_dd(delta, tau) - x3 )
            wx = np.where(xxt > 0, np.sqrt(xxt), 0)
            wx = wx*np.sqrt(1000.00)  # convert Speed of sound from sqrt(kJ/kg) to m/s

            # Joule-Thomsen coefficient. K-m3/kJ (equivalent to the usual K/MPa)
            x1 = delta*phir_d(delta, tau) + delta**2*phir_dd(delta, tau) + delta*tau*phir_dt(delta, tau)
            x2 = ( 1 + delta*phir_d(delta, tau) - delta*tau*phir_dt(delta, tau) )**2
            x3 = ( phi0_tt(delta, tau) + phir_tt(delta, tau) )*( 1.0 + 2*delta*phir_d(delta, tau) + \
                                                                delta**2*phir_dd(delta, tau) )
            mux = (( - x1/( x2 - tau**2*x3 ) )/(R*rho) )

            # Isothermal throttling coefficient.
            x1 = 1 + delta*phir_d(delta, tau) - delta*tau*phir_dt(delta, tau)
            x2 = 1 + 2*delta*phir_d(delta, tau) + delta**2*phir_dd(delta, tau)
            dtx = (( 1 - ( x1/x2 ) )/rho )
            dtx = 0.010*dtx   # convert Isothermal throttling coefficient from m3/kg to the usual kJ/kg/bar.

            # Isentropic temperature-pressure coefficient. (the same units as for the Joule-Thomson coefficient)
            x1 = 1.0 + delta*phir_d(delta, tau) - delta*tau*phir_dt(delta, tau)
            x2 = x1**2
            x3 = ( phi0_tt(delta, tau) + phir_tt(delta, tau) )*( 1 + 2*delta*phir_d(delta, tau) + \
                                                                delta**2*phir_dd(delta, tau) )
            bsx = (( x1/( x2 - tau**2*x3 ) )/(R*rho) )

            # Gibbs energy derivative.
            gdx = (R*TK*( phi0_d(delta, tau) + 2*phir_d(delta, tau) + delta*phir_dd(delta, tau) ))
        # Derivative of pressure with respect to delta (needed to perform Newton-Raphson
        # iteration to matched desired pressure) in bar.
        pdx = ( px/delta ) + delta*rhoc*R*TK*( phir_d(delta, tau) + delta*phir_dd(delta, tau) ) * 0.010

        # Derivative of pressure with respect to tau (needed to calculate the thermal expansion
        # coefficient) in bar.
        ptx = ( -px/tau ) + px*delta*phir_dt(delta, tau)/(1 + delta*phir_d(delta, tau))

        # Compressibility. Here the value is in /bar.
        ktx = 1.0/(delta*pdx)

        # Calculate zeta value (needed to calculate viscosity). Note: ztx  is dimensionless
        # An alternative formula is: ztx = delta*Pc*ktx
        ztx = Pc/pdx

        # Thermal expansion coefficient (thermal expansivity). This calculation is based on the Maxwell relation:
        avx = ktx*ptx*( -tau/TK )

        # Helmholtz energy derivative with respect to delta
        adx = (R*TK*( phi0_d(delta, tau) + phir_d(delta, tau) ))

        if FullEOSppt == True:
            output = px, ax, sx, hx, gx, vx, pdx, adx, ztx, ptx, ktx, avx, ux, gdx, bsx, dtx, mux, cpx, cvx, wx
        else:
            output = px, ax, sx, hx, gx, vx, pdx, adx, ztx, ptx, ktx, avx

        return output

    def auxMeltingPressure(self, TK, P):
        """
        This function calculates the melting pressure of ice as a function of temperature.

        This model is described in IAPWS R14-08(2011), Revised Release on the Pressure along
        the Melting and Sublimation Curves of Ordinary Water Substance, as may be found at:
        http://www.iapws.org/relguide/MeltSub.html

        Five ice phases are covered here. The melting pressure is not a single-valued function
        of temperature as there is some overlap in the temperature ranges of the individual phases.
        There is no overlap in the temperature ranges of Ices III, V, VI, and VII, which together
        span the range 251.165 - 715K. The melting pressure is continuous and monotonically increasing
        over this range, albeit with discontinuities in slope at the triple points where two ice
        phases and liquid are in equilibrium. The problem comes in with Ice Ih, whose temperature
        range completely overlaps that of Ice III and partially overlaps that of Ice V. For a
        temperature in the range for Ice Ih, there are two possible melting pressures.

        The possible ambiguity here in the meaning of melting pressure is not present if the
        temperature is greater than or equal to the triple point temperature of 273.16K, or
        if the pressure is greater than or equal to 2085.66 bar (the triple point pressure
        for Ice Ih-Ice III-liquid). If neither of these conditions are satisfied, then the Ice
        Ih-liquid curve will be used. To deal with the pressure condition noted above, this function
        assumes that an actual pressure is specified.

        Parameters
        ----------
            P     :   pressure [bar]
            TK    :   temperature [K]
        Returns
        ----------
            Pmelt :   melting pressure [bar]
        Usage
        ----------
          [Pmelt] = auxMeltingPressure( TK, P)

        """
        # Coefficients for calculating the melting pressure of Ice Ih.
        a = np.array([0.119539337e+07, 0.808183159e+05, 0.333826860e+04])
        b = np.array([0.300000e+01, 0.257500e+02, 0.103750e+03])
        PPa = P*1e5  # convert bar to Pa
        if (PPa <= 208.566e6):
            if (251.165 <=  TK <= 273.16):
                # Ice Ih.
                theta = TK/273.16
                pimelt = 1 + np.sum(a*( 1 - theta**b))
                Pmelt = pimelt*611.647   #e-06
            else:
                Pmelt = np.nan #2085.66
        else:
            if (251.165 <= TK < 256.164):
                # Ice III.
                theta = TK/251.165
                pimelt = 1 - 0.299948*( 1 - theta**60 )
                Pmelt = pimelt*208.566e6
            elif (256.164 <= TK < 273.31):
                # Ice V.
                theta = TK/256.164
                pimelt = 1 - 1.18721*( 1 - theta**8 )
                Pmelt = pimelt*350.1e6
            elif (273.31 <= TK < 355.0):
                # Ice VI.
                theta = TK/273.31
                pimelt = 1 - 1.07476*( 1 - theta**4.6 )
                Pmelt = pimelt*632.4e6
            elif (355.0 <= TK < 715.0):
                # Ice VII.
                theta = TK/355.0
                px =   0.173683e+01*( 1 - theta**(-1) ) - 0.544606e-01*( 1 - theta**5 ) \
                    + 0.806106e-07*( 1 - theta**22 )
                pimelt = np.exp(px)
                Pmelt = pimelt*2216.0e6
            elif (715.0 <= TK <= 2000.0):
                # This is out of range. Ice VII, extrapolated.
                theta = TK/355.0
                px =   0.173683e+01*( 1 - theta**(-1) ) - 0.544606e-01*( 1 - theta**5 ) \
                    + 0.806106e-07*( 1 - theta**22 )
                pimelt = np.exp(px)
                Pmelt = pimelt*2216.0e6
            else:
                Pmelt = np.nan

        return Pmelt*1e-5

    def auxMeltingTemp(self, P):
        """
        This function calculates the melting temperature of ice as a function of pressure.

        This inverts the model for the melting pressure as a function of temperature.
        That model is described in IAPWS R14-08(2011), Revised Release on the Pressure
        along the Melting and Sublimation Curves of Ordinary Water Substance as may be found at:
        http://www.iapws.org/relguide/MeltSub.html

        Inversion of the model for the melting pressure is done here using the secant method.
        This is chosen instead of the Newton-Raphson method to avoid potential problems with slope
        discontinuites at boundaries between the ice phases for pressures above 208.566 MPa,
        which is the equilibrium pressure for Ice Ih-Ice III-liquid. The corresponding equlibrium
        temperature is 251.165K. Putative melting temperatures should not be less than this for
        pressures above 208.566 Mpa, nor more than this for pressures less than this.
        Parameters
        ----------
            P     :   pressure [bar]
        Returns
        ----------
            Tmelt :   temperature [K]
        Usage
        ----------
          [Tmelt] = auxMeltingTemp( P)

        """
        # Calculates the melting temperature that corresponds to the actual pressure.
        # The variables t0 and t1 are initial values for the iteration.
        PPa = P*1e5  # convert bar to Pa
        if (PPa < 208.566e6):
            # In the Ice Ih field.
            tlim0 = 251.165
            tlim1 = 273.16
            t0 = tlim0
            t1 = tlim1
        elif (208.566e6 <= PPa < 350.1e6):
            # In the Ice III field.
            tlim0 = 251.165
            tlim1 = 256.164
            t0 = tlim0
            t1 = tlim1
        elif (350.1e6 <= PPa < 632.4e6):
            # In the Ice V field.
            tlim0 = 256.164
            tlim1 = 273.31
            t0 = tlim0
            t1 = tlim1
        elif (632.4e6 <= PPa < 2216.0e6):
            # In the Ice VI field.
            tlim0 = 273.31
            tlim1 = 355.0
            tx = tlim1 - tlim0
            t0 = tlim0 + 0.3*tx
            t1 = tlim0 + 0.7*tx
        elif (2216.0e6 <= PPa <= 10000.0e6):
            # In the Ice VII field.
            # Note: the upper limit here of 10000 MPa is an arbitrary cutoff suggested
            # by Figure 1 from IAPWS R14, but this is not part of the IAPWS R14 standard.
            tlim0 = 355.0
            tlim1 = 1000.0
            tx = tlim1 - tlim0
            t0 = tlim0 + 0.3*tx
            t1 = tlim0 + 0.7*tx
        elif (PPa > 20000.0e6):
            Tm = np.nan

        funct_melt = lambda t: self.auxMeltingPressure(t, P) - P
        Tm = root_scalar(funct_melt, method = 'secant',
                         bracket=[t0, t1], x0=t0, x1=t1, xtol = 1.0e-10).root

        Tmelt = Tm

        return Tmelt

    def waterviscosity(self, TC, P, rho):
        """
        This function calculates the viscosity of water using
        Ref:
            (1) "IAPWS Formulation 2008 for the Viscosity of Ordinary Water Substance" (IAPWS R12-08).
            (2) Huber M.L., Perkins R.A., Laesecke A., Friend D.G., Sengers J.V., Assael M.J., Metaxa I.N.,
                Vogel E., Mares R., and Miyagawa K. (2009) New International Formulation for the Viscosity
                of H2O. J. Phys. Chem. Ref. Data 38, 101-125.    \n
        Parameters
        ----------
            TC       temperature [°C]    \n
            P        pressure [bar]    \n
            rho      density [kg/m3]    \n
        Returns
        ----------
            visc     viscosity [Pa.s]
        Usage
        ----------
          [visc] = waterviscosity( TC, P, rho)
        """
        TK = convert_temperature( TC, Out_Unit = 'K' )  #convert to Kelvin
        PPa = P*1e5

        Tc = IAPWS95_COEFFS['Tc'] # K
        rhoc = IAPWS95_COEFFS['rhoc']

        H0 = [1.67752e+00, 2.20462e+00, 0.6366564e+00, -0.241605e+00]
        I1 = [0, 1, 2, 3, 0, 1, 2, 3, 5, 0, 1, 2, 3, 4, 0, 1, 0, 3, 4, 3, 5]
        J1 = [0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 4, 4, 5, 6, 6]
        H1 = [0.520094,  0.0850895, -1.08374, -0.289555, 0.222531, 0.999115, 1.8879700000000001,
              1.26613, 0.120573, -0.281378, -0.9068510000000001, -0.772479, -0.48983699999999997,
              -0.25704, 0.161913, 0.257399, -0.0325372, 0.0698452, 0.00872102, -0.00435673, -0.000593264]

        delta = rho/rhoc
        Tbar = TK/Tc
        muref = 1.00e-06   # Pa.s

        # Check range of validity.
        chk = False
        # triple point
        Ttr = 273.16 # K
        Ptr = 611.657 # Pa
        Ttmltx = self.auxMeltingTemp(P)

        if (PPa < Ptr):
            if (Ttr <= TK <= 1173.15):
                chk = True
        elif Ttmltx > 0.0:
            if (Ptr <= PPa <= 300.0e6):
                if (Ttmltx <= TK <= 1173.15):
                  chk = True
            elif (300.0e6 < PPa <= 350.0e6):
                if (Ttmltx <= TK <= 873.15):
                  chk = True
            elif (350.0e6 < PPa <= 500.0e6):
                if (Ttmltx <= TK <= 433.15):
                  chk = True
            elif (500.0e6 < PPa <= 1000.0e6):
                if (Ttmltx <= TK <= 373.15):
                  chk = True

        if (not chk) | (Ttmltx <= 0):
            mubar = np.nan
        else:
            # Calculate the viscosity in the dilute gas limit (mubar0)
            mubar0 = 100*np.sqrt(Tbar)/np.sum([x/Tbar**idx for idx, x in enumerate(H0)])

            s1=np.zeros([len(H1), 1])
            for x in range(len(H1)):
                s1[x] = H1[x]*((1/Tbar) -1)**I1[x] * (delta-1)**J1[x]
            # Calculate the contribution to viscosity due to finite density
            mubar1 = np.exp(delta * np.sum(s1))

            # critical enhancement
            xmu = 0.068
            qc = 1/1.9      #/nm
            qD = 1/1.1      #/nm
            nvc = 0.63
            gamma = 1.239
            xicl0 = 0.13
            gam0 = 0.06
            TR = 1.5
            Tkr = TR*Tc

            # Estimate the reference zeta value by directly evaluating the EOS model
            ztxr = self.EOSIAPWS95(Tkr, rho)[8]

            ztx = self.EOSIAPWS95(TK, rho)[8]

            # Get delchb (DELTA chibar, equation 21).
            delchb = delta*( ztx - (ztxr*TR*Tbar) )
            if (delchb < 0.0):
                delchb = 0.0
            # Get xicl (equation 20).
            xicl = xicl0*( (delchb/gam0)**(nvc/gamma) )
            # Get psid (equation 17).
            psid = math.acos(( 1.0 + (qD*xicl)**2 )**(-0.5))
            # Get www (w in equation 19).
            w = np.sqrt(abs( ((qc*xicl) - 1.0)/((qc*xicl) + 1.0) )) * math.tan(0.5*psid)
            # Get lcap (L(w) in equation 18)
            if ((qc*xicl) > 1):
                lcap = np.log( (1 + w)/(1 - w) )
            else:
                lcap = 2*math.atan( abs(w) )

            if (xicl <= 0.3817016416):
                ycap  = 0.2*(qc*xicl)*((qD*xicl)**5)* \
                    (1 - (qc*xicl) + (qc*xicl)**2  - ( 765.0/504.0 )*(qD*xicl)**2)
            else:
                ycap = ( 1/12 )*math.sin(3*psid) - ( 1/(4*(qc*xicl)) )*math.sin(2*psid) +\
                    ( 1/(qc*xicl)**2 )*( 1.0 - 1.25*(qc*xicl)**2 ) *math.sin(psid) \
                        -( 1.0/(qc*xicl)**3 ) *( ( 1.0 - 1.5*(qc*xicl)**2 ) \
                                                - ( abs((qc*xicl)**2 - 1) )**1.5 * lcap)

            if (645.91 < TK < 650.77) and (245.8 < rho < 405.3):
                mubar2 = np.exp(xmu * ycap)
            else:
                mubar2 = 1

            mubar = mubar0 * mubar1 *mubar2
        visc = mubar*muref
        return visc

    def apxsatpropT(self, TK):
        """
        This function evaluates the approximate pressure (psat) as a function of temperature along
        the vapor-liquid equilibrium curve, using equation 2.5 of Wagner and Pruss (2002).
        It also calculates the derivative of saturation pressure wrt temperature as well as the
        densities of the liquid and vapor phases using equations 2.6 and 2.7
        from the same source.    \n
        Parameters:
        ----------
            TK       temperature [K] (saturation temperature)    \n
        Returns:
        ----------
            Psat    saturation pressure [bar]    \n
            Psat_t  Derivative of saturation pressure with respect to temperature    \n
            rhosl   density of liquid [kg/m3]    \n
            rhosv   density of vapor [kg/m3]    \n
        Usage:
        ----------
          [Psat, Psat_t, rhosl, rhosv] = apxsatpropT( TK)
        """
        Tc = IAPWS95_COEFFS['Tc'] # K
        Pc = IAPWS95_COEFFS['Pc'] # MPa
        a = [-7.85951783, 1.84408259, -11.7866497, 22.6807411, -15.9618719, 1.80122502]

        rhoc = IAPWS95_COEFFS['rhoc']
        b = [1.99274064, 1.09965342, -0.510839303, -1.75493479, -45.5170352, -6.74694450e5]
        c = [-2.03150240, -2.68302940, -5.38626492, -17.2991605, -44.7586581, -63.9201063]

        # Check to see that the temperature is in the allowed range.
        if (TK < 273.15) | (TK > Tc):
            Psat = np.nan
            Psat_t = np.nan
            rhosl = np.nan
            rhosv = np.nan
        else:
            # Saturation pressure.
            th = 1 - TK/Tc
            t1 = a[0]*th + a[1]*th**1.5 + a[2]*th**3 + a[3]*th**3.5 + a[4]*th**4 + a[5]*th**7.5
            Psat = Pc*np.exp(Tc*t1/TK)
            # Derivative of saturation pressure with respect to temperature.
            x1 = a[0] + 1.5*a[1]*th**0.5 + 3.0*a[2]*th**2.0 + 3.5*a[3]*th**2.5 + 4.0*a[4]*th**3.0 + 7.5*a[5]*th**6.5
            x2 = np.log( Psat/Pc ) + x1
            Psat_t = -( Psat/TK )*x2
            # Density of liquid.
            th = (1 - TK/Tc)**(1/3)
            t1 = 1 + b[0]*th + b[1]*th**2 + b[2]*th**5 + b[3]*th**16 + b[4]*th**43 + b[5]*th**110
            rhosl = rhoc*t1
            # Density of vapor.
            th = np.sqrt(th)
            t2 = c[0]*th**2 + c[1]*th**4 + c[2]*th**8 + c[3]*th**18 + c[4]*th**37 + c[5]*th**71
            rhosv = rhoc*np.exp(t2)

        return Psat*10, Psat_t*10, rhosl, rhosv

    def apxsatpropP(self, P):
        """
        This function evaluates the approximate temperature (tsat) as a function of pressure along
        the vapor-liquid equilibrium curve, using equation 2.5 of Wagner and Pruss (2002).
        This is similar to apxsatpropT(TK), but evaluates the inverse problem (Tsat as a function
        of pressure instead of psat as a function of temperature). Newton-Raphson iteration is used.    \n
        Parameters:
        ----------
            P        pressure [bar]    \n
        Returns:
        ----------
            Tsat     saturation temperature [K]    \n
        Usage:
        ----------
          [Tsat] = apxsatpropP( P)
        """
        Tc = IAPWS95_COEFFS['Tc'] # K
        Pc = IAPWS95_COEFFS['Pc']*10 # bar
        # triple point
        Ttr = 273.16 # K
        Ptr = 611.657e-5 # bar
        P1atm = 1.01325e0  # bar
        Ts1atm = 373.124  # K

        # Check to see that the pressure is in the allowed range.
        if (P < Ptr) | (P > Pc):
            Tsat = np.nan
        else:
            # Choose a starting temperature value.
            if (P >= P1atm):
                # Interpolate between 100C, 1.01325 bar and Tcr, Pcr.
                dtdp = (Tc - Ts1atm)/(Pc - P1atm)
                TK = Ts1atm + dtdp*(P - P1atm)
            else:
                # Interpolate between the triple point and 100C, 1.013 bar
                dtdp = (Ts1atm - Ttr)/(P1atm - Ptr)
                TK = Ttr + dtdp*(P - Ptr)

            funct_tsat = lambda T: self.apxsatpropT(T)[0]*0.1 - P*0.1
            Tsat = fsolve(funct_tsat, TK, xtol=1.48e-10)[0]

        return Tsat

    def calcsatpropT(self, TK):
        """
        This function calculates the saturation properties as a function of specified temperature.
        This is achieved using Newton-Raphson iteration to refine values of pressure, vapor density,
        and liquid density, starting with results obtained using approximate equations included
        by Wagner and Pruss (2002) in their description of the IAPWS-95 model.    \n
        Parameters
        ----------
           TK      temperature [K]    \n
        Returns
        ----------
           Psat    saturation pressure [bar]    \n
           rhosl   density of liquid [kg/m3]    \n
           rhosv   density of vapor [kg/m3]    \n
        Usage
        ----------
          [Psat, rhosl, rhosv] = calcsatpropT( TK)
        """
        Tc = IAPWS95_COEFFS['Tc'] # K
        rhoc = IAPWS95_COEFFS['rhoc']
        bettl1 = 1.0e-8
        bettl2 = 1.0e-7
        btxtol = 1.0e-10
        qxiter = False

        alpha = np.zeros([3, 1]); beta = alpha
        aamatr = np.zeros([3, 3])
        deltas = np.zeros([3, 1]); arelax = 1

        if (TK <= 298.15):
            btxtol = bettl1
        elif (647.090 < TK < Tc):
            qxiter = True
        elif (TK > 647.090):
            btxtol = bettl2

        #  Calculate approximate saturation pressure and corresponding densities of liquid and vapor.
        #  These results are not those of the IAPWS-95 model itself, but can serve as starting estimates.
        [Psat, _, rhosl, rhosv] = self.apxsatpropT(TK)
        #  Save the values from the approximation.
        delta_svq = rhosv/rhoc
        delta_slq = rhosl/rhoc

        it = 0
        itermx = 50
        Psat0 = Psat
        deltasv0 = delta_svq
        deltasv = delta_svq
        deltasl0 = delta_slq
        deltasl = delta_slq


        while True:

            # Below is the return point to refine the saturation curve properties.
            # First calculate the vapor properties by calling EOSIAPWS95 with the vapor density.
            [Pxv, axv, _, _, _, _, Pdxv, adxv] = self.EOSIAPWS95(TK, rhosv)[:8]
            # Now calculate the liquid properties by calling EOSIAPWS95 with the liquid density.
            [Pxl, axl, _, _, _, _, Pdxl, adxl] = self.EOSIAPWS95(TK, rhosl)[:8]
            # The pdx for vapor cannot be negative. Under-relax to prevent this.
            if (Pdxv < 0):
                if (it <= 0):
                    #if (icutv >= 30):
                    #icutv = icutv + 1
                    rhosv = 0.995*rhosv
                    deltasv = rhosv/rhoc
                else:
                    #icutv = icutv + 1
                    arelax = 0.25
            #  The revised delta for vapor cannot be less than a good
            #  fraction of the value obtained from the intial approximation.
            if (deltasv < 0.9*delta_svq):
                arelax = 0.25

            #  The pdx for liquid cannot be negative. Under-relax to prevent this.
            if (Pdxl < 0):
                if (it <= 0):
                    #if (icutl >= 30):
                    #icutl = icutl + 1
                    rhosl = 1.001*rhosl
                    deltasl = rhosl/rhoc
                else:
                    #icutl = icutl + 1
                    arelax = 0.25
            # The revised delta for liquid cannot be less than a good
            # fraction of the value obtained from the intial approximation.
            if (deltasl > 1.1*delta_slq):
                arelax = 0.25

            #  The delta for liquid cannot be less than the delta for vapor.
            #  Corrected delta values must be positive to avoid
            #  a singularity in the equation-of-state model equations.
            #  Under-relax to prevent this.
            if (deltasl < deltasv) | (deltasv <= 0 or deltasl <= 0):
                arelax = 0.25

            deltas = deltas*arelax
            Psat = Psat0 + deltas[2, 0]
            deltasl = deltasl0 + deltas[1, 0]
            deltasv = deltasv0 + deltas[0, 0]
            rhosl = rhoc*deltasl
            rhosv = rhoc*deltasv

            # =============================================================================
            # Have obtained valid (outside the unstable zone) vapor and liquid properties for the current iteration.
            # Improve the calculated saturation properties by solving three equations in three unknowns.
            # The equations are all in terms of pressure. The unknowns to be found are Psat, deltasv, and deltasl.
            # Calculate the Maxwell crition pressure (Gibbs energy equality expressed through the
            # Helmholtz energies and the pressure)
            # =============================================================================

            dix = (1/deltasl) - (1/deltasv)
            # dltx = deltasl - deltasv
            if (abs(dix) > 1e-15):
                if (abs(axv - axl) > 1e-15):
                    # Normal calculation, result in kPa.
                    Pxm = rhoc*( axv - axl )/dix
                    Pxm = 0.01*Pxm     #    Convert from kPa to bar.
                else:
                    # There is no difference in the Helmholtz energies of the vapor and the liquid.
                    Pxm = 0
            else:
                # Exception intended for the critical point.
                if (abs(TK - Tc) <= 1e-10) & (abs(deltasv - 1.0) <= 1e-10) & (abs(deltasl - 1) <= 1e-10):
                    # Am at the critical point.
                    Pxm = Pxv
                else:
                    # Not at the critical point, but the vapor and liquid densities have converged.
                    Pxm = 0

            # Calculate residual functions.
            alpha[0, 0] = Pxm - Psat
            alpha[1, 0] = Pxv - Psat
            alpha[2, 0] = Pxl - Psat

            beta = abs(alpha/Psat)
            betamx = np.max(beta)
            # Note: using a convergence tolerance below 1.0d-11
            # may lead to non-convergence due to the limitations of 64-bit arithmetic.

            # print(it, ' Psat: %.6e' % Psat[0], 'betamx:  %.6e' % betamx)
            if (betamx <= btxtol) | (it >= itermx):
                # Iteration has converged.
                # P = Psat
                break
            elif (qxiter and it >= 5):
                break

            # Since this matrix is only 3x3, the simultaneous equations have the form:
            # aamatr(i,1)*deltas(1) + aamatr(i,2)*deltas(2) + aamatr(i,3)*deltas(3) = -alpha(i), i = 1,3
            # The Jacobian matrix J here is aamatr(kdim, kdim).
            aamatr[0, :] = [Pxm*(-(1/(dix*deltasv**2)) + (adxv/(axv - axl))),
                            Pxm*((1/(dix*deltasl**2)) - (adxl/(axv - axl))),
                            -1]
            aamatr[1, :] = [Pdxv,
                            0,
                            -1]
            aamatr[2, :] = [0,
                            Pdxl,
                            -1]

            deltas = -lu_solve(lu_factor(aamatr), alpha)

            #  Save current values.
            Psat0 = Psat
            deltasv0 = deltasv
            deltasl0 = deltasl
            Psat = Psat0 + deltas[2, 0]
            deltasl = deltasl0 + deltas[1, 0]
            deltasv = deltasv0 + deltas[0, 0]
            rhosl = rhoc*deltasl
            rhosv = rhoc*deltasv

            it = it + 1

        return Psat, rhosl, rhosv

    def calcsatpropP(self, P):
        """
        This function calculates the saturation properties as a function of specified pressure.
        This is done by iterating using Newton method on pressure to obtain the desired
        temperature. This implementation calls calcsatpropT(TK) to calculate the saturation
        pressure, liquid and vapor densities.    \n

        Parameters
        ----------
            P        pressure [bar]    \n
        Returns
        ----------
            Tsat     temperature [K]    \n
            rhosl    liquid density [kg/m3]    \n
            rhosv    vapor density [kg/m3]    \n
        Usage
        ----------
          [Tsat, rhosl, rhosv] = calcsatpropP( P)
        """
        btxtol = 1.0e-10
        itermx = 50
        Tc = IAPWS95_COEFFS['Tc'] # K

        # Calculate approximate saturation temperature to use as a starting estimate
        Tsat = convert_temperature( self.apxsatpropP(P), Out_Unit = 'C' )   # convert to C

        # Iterate to calculate the saturation temperature
        funct_tsat = lambda TC: self.calcsatpropT(convert_temperature( TC, Out_Unit = 'K' ))[0] - P
        Tsat = brentq(funct_tsat, 0, convert_temperature( Tc, Out_Unit = 'C' ), xtol=btxtol, maxiter = itermx) + 273.15
        #Tsat = newton(funct_tsat, Tsat, fprime=None, args=(), tol=btxtol, maxiter=itermx, fprime2=None)

        # Calculate liquid and vapor densities
        [_, rhosl, rhosv] = self.calcsatpropT(Tsat)

        return Tsat, rhosl, rhosv

    def fluidDescriptor(self, P, TK, *rho):
        """
        This function calculates the appropriate description of the H2O fluid at any given
        temperature and pressure    \n

        A problem may occur if the pressure is equal or nearly equal to the saturation pressure.
        Here comparing the pressure with the saturation pressure pressure may lead to the wrong
        description, as vapor and liquid coexist at the saturation pressure. It then becomes
        neccesary to compare the fluid density with the saturated vapor and saturated liquid densities.
        If the density is known, it will be used. If it is not known, the results obtained
        here will determine the starting density estimate, thus in essence choosing "vapor" or "liquid"
        for pressures close to the saturation pressure.       \n
        Parameters:
        ----------
            P        pressure [bar]    \n
            TK       temperature [K]    \n
            rho      density [kg/m3] (optional)    \n
        Returns:
        ----------
            phase   fluid description    \n
            rhosl    liquid density [kg/m3]    \n
            rhosv    vapor density [kg/m3]    \n
        Usage:
        ----------
          [udescr, rhosl, rhosv] = fluidDescriptor( P, TK)
        """
        # P = P*10 # MPa to bar
        Tc = IAPWS95_COEFFS['Tc'] # K
        Pc = IAPWS95_COEFFS['Pc']*10 # convert MPa to bar
        # rhoc = IAPWS95_COEFFS['rhoc']
        btxtol = 1e-10
        rhotol = 1.0e-8

        if (TK < 273.15):
            # Note that the allowed temperature range has been extended a bit on the low end to include 0C.
            phase = 'unknown'
            rhosv = 0; rhosl = 0
        elif (TK <= Tc):
            # Calculate the saturation curve properties.
            [Psat, rhosl, rhosv] = self.calcsatpropT(TK)
            if (P > Pc):
                phase = 'compressed liquid'
                if Psat == np.nan:
                    # if calcsatpropT(TK) failed, an arbitrary liquid-like density will be assigned
                    # as a starting value for compressed liquid
                    rhosl = 1.05
            else:
                # if calcsatpropT(TK) failed, the vapor and liquid states cannot be distinguished
                # from one another. Liquid is assigned arbitrarily
                if Psat == np.nan:
                    phase = 'liquid'
                    rhosl = 1.05
                else:
                    if (P >= Psat):
                        phase = 'liquid'
                    else:
                        phase = 'vapor'
                    # Use density (rho) if available and pressure is close to psat.
                    if len(rho) != 0:
                        Ptest = (P - Psat)/Psat
                        btest = 10*btxtol
                        if (abs(Ptest) <= btest):
                            # Here press is very close to psat. Use rho to determine vapor or liquid.
                            rtestl = (rho - rhosl)/rhosl
                            rtestv = (rho - rhosv)/rhosv
                            if (abs(rtestl) <= rhotol):
                                phase = 'liquid'
                            elif (abs(rtestv) <= rhotol):
                                phase = 'vapor'
                            else:
                                phase = 'unknown'
        else:
            rhosv = 0; rhosl = 0
            if (P > Pc):
                phase = 'supercritical fluid'
            else:
                phase = 'hot vapor'

        return phase, rhosl, rhosv

    def calcwaterppt(self, TC, P, *rho0, FullEOSppt = False):
        """
        This function evaluates thermodynamic properties of water at given temperature and pressure.
        The problem reduces to finding the value of density that is consistent with the desired pressure.
        The Newton-Raphson method is employed. Small negative values of calculated pressure are okay.
        Zero or negative values for calculated "pdx" (pressure derivative with respect to delta)
        imply the unstable zone and must be avoided.  \n
        Parameters:
        ----------
            T     :  temperature [°C]  \n
            P     :  pressure [bar]  \n
            rho0  :  starting estimate of density [kg/m3] (optional)
            FullEOSppt: Option to output all or essential water properties [False or True]
        Returns:
        ----------
            rho   :  density [kg/m3]  \n
            gx    :  Gibbs energy [cal/mol]  \n
            hx    :  Enthalpy [cal/mol]  \n
            sx    :  Entropy [cal/mol/K]  \n
            vx    :  Volume [m3/mol]  \n
            Pout  :  pressure [bar]  \n
            Tout  :  temperature [°C]  \n
            ux    :  Internal energy [cal/mol]  if FullEOSppt is True  \n
            ax    :  Helmholtz energy [cal/mol/K]   if FullEOSppt is True   \n
            cpx   :  Isobaric heat capacity [cal/mol/K]   if FullEOSppt is True \n
        Usage:
        ----------
            [rho, gxcu, hxcu, sxcu, vxcu, uxcu, axcu, cpxcu, Pout, Tout] = calcwaterppt(T, P),   \n
        """

        if np.ndim(TC) == 0:
            TC = np.array(TC).ravel()
        else:
            TC = TC.ravel()

        if np.ndim(P) == 0:
            P = np.array(P).ravel()
        else:
            P = P.ravel()

        rho0 = rho0[0]

        Pout = P # cases where 'T' is used as input
        Tout = TC # cases where 'P' is used as input
        TK = convert_temperature( TC, Out_Unit = 'K' )
        Ppa = P * 0.1  #Convert bars to MPa
        Tc = IAPWS95_COEFFS['Tc'] # K
        Pc = IAPWS95_COEFFS['Pc'] # MPa
        rhoc = IAPWS95_COEFFS['rhoc']
        R = IAPWS95_COEFFS['R']*1e-3  #KJ/(kg*K)
        # if len(rho0) != 0:
        #     itermx = 80
        # else:
        #     itermx = 100
        # btxtol = 1.0e-8

        # Obtain a description (udescr) of the H2O fluid.
        rho = np.zeros(len(TK)).ravel()
        for i in range(len(TK)):
            if (np.ndim(rho0) != 0):
                [phase, rhosl, rhosv] = self.fluidDescriptor(P[i], TK[i], rho0[i])
            else:
                [phase, rhosl, rhosv] = self.fluidDescriptor(P[i], TK[i])

            if (phase == 'vapor'):
                # Vapor: assume ideal gas behavior.
                rho[i] = 1000.0*Ppa[i]/(TK[i]*R)
            elif (phase == 'liquid'):
                # Liquid: use a liquid-like density. The liquid density on the saturation curve.
                rho[i] = rhosl
            elif (phase == 'compressed liquid'):
                # Estimate the density of compressed liquid. The saturated liquid density is a minimum value.
                rho[i] = 1.10*rhosl
                # Close to the upper limit for this field (T near the triple point, 1000 MPa).
                # For higher pressure, a higher value might be needed. rho = 1250.0d0
                rho[i] = np.maximum(rho[i], rhosl)
                rho[i] = np.minimum(rho[i], 1400)
            elif (phase == 'supercritical fluid'):
                # Estimate density of supercritical fluid. Twice the ideal gas correction to critical point density.
                rho[i] = 2.0*(Ppa[i]/Pc)*(Tc/TK[i])*rhoc
                # Close to the upper limit for this P, T field. (T near the critical point, 1000 MPa).
                # For higher pressure, a higher value might be needed.  rho = 1100.0d0
                rho[i] = np.minimum(rho[i], 1100.0)
            elif (phase == 'hot vapor'):
                # Estimate the density of hot vapor. Ideal gas.
                rhoidg = 1000.0*Ppa[i]/(TK[i]*R)
                # SUPCRT92 estimate, about 15% higher than ideal gas.
                rhosup = 2500.0*Ppa[i]/TK[i]
                # Ideal gas correction to critical point density.
                rhocpa = (Ppa[i]/Pc)*(Tc/TK[i])*rhoc
                # The upper limit for this field, the critical pressure (rhocr), 22.064 MPa. rho = rhoc
                if (Ppa[i] <= 1.0):
                    rho[i] = rhoidg
                elif (Ppa[i] <= 18.0):
                    rho[i] = rhosup
                else:
                    rho[i] = rhocpa
                rho[i] = np.minimum(rho[i], rhoc)
            else:
                # If the H2O fluid type could not be determined. A good starting estimate
                # of density could not be established, try three times the critical density.
                rho[i] = 4*rhoc

            funct_tsat = lambda rho: self.EOSIAPWS95(TK[i], rho, FullEOSppt = FullEOSppt)[0] - P[i]
            rho[i] = fsolve(funct_tsat, rho[i])[0]

        if FullEOSppt == True:
            [Px, ax, sx, hx, gx, vx,  _, _, _, _, _, _, ux, _, _, _, _, cpx, _, _] = self.vEOSIAPWS95(TK, rho, FullEOSppt = FullEOSppt)
        else:
            [Px, ax, sx, hx, gx, vx,  _, _, _, _, _, _] = self.vEOSIAPWS95(TK, rho, FullEOSppt = FullEOSppt)

        # The following reference state data are in kilogram units.
        ds = 3.5156150 # Entropy (kJ/kg/K)
        du = -15767.19391 # Internal energy (kJ/kg)
        dh = -15970.89538 #  Enthalpy (kJ/kg)
        da = -11906.84446 # Helmholtz energy (kJ/kg-K)
        dg = -12110.54592 # Gibbs energy (kJ/kg)
        htripl = 0.000611782 # tripple point Enthalpy (kJ/kg)
        mwH2O = 18.01528/1000    # kg/mol
        # Calculate the entropy, internal energy, enthalpy, Helmholtz energy, and Gibbs energy
        # on the standard thermochemical scale, and volume, heat capacity at constant volume.
        # Results are converted from KJ and kilogram units to cal and molar units.
        sxcu = sx + ds
        if FullEOSppt == True:
            uxcu = mwH2O*(ux + du)*1000/J_to_cal
            axcu = mwH2O*(ux - TK*sxcu + da)*1000/J_to_cal
            cpxcu = mwH2O*cpx*1000/J_to_cal
        hxcu = mwH2O*(hx - htripl + dh)*1000/J_to_cal
        gxcu = mwH2O*(hx - TK*sxcu + dg)*1000/J_to_cal
        vxcu = mwH2O*vx*1000/J_to_cal
        sxcu = mwH2O*(sx + ds)*1000/J_to_cal
        if FullEOSppt == True:
            return rho, gxcu, hxcu, sxcu, vxcu, Pout, Tout, uxcu, axcu, cpxcu
        else:
            return rho, gxcu, hxcu, sxcu, vxcu, Pout, Tout

    def calcwaterppt_Prho(self, P, rho, FullEOSppt = False):
        """
        This function evaluates thermodynamic properties of water at given density and pressure.
        The problem reduces to finding the value of temperature that is consistent with the desired pressure.  \n
        Parameters:
        ----------
            P     :  pressure [bar]  \n
            rho   :  density [kg/m3]  \n
            FullEOSppt: Option to output all or essential water properties [False or True]
        Returns:
        ----------
            rho   :  density [kg/m3]  \n
            gx    :  Gibbs energy [cal/mol]  \n
            hx    :  Enthalpy [cal/mol]  \n
            sx    :  Entropy [cal/mol/K]  \n
            vx    :  Volume [m3/mol]  \n
            Pout  :  pressure [bar]  \n
            Tout  :  temperature [°C]  \n
            ux    :  Internal energy [cal/mol]  if FullEOSppt is True  \n
            ax    :  Helmholtz energy [cal/mol/K]  if FullEOSppt is True    \n
            cpx   :  Isobaric heat capacity [cal/mol/K]  if FullEOSppt is True  \n
        Usage:
        ----------
            [rho, gxcu, hxcu, sxcu, vxcu, uxcu, axcu, cpxcu, Pout, Tout] = calcwaterppt_Prho(P, rho),   \n
        """

        if np.ndim(rho) == 0:
            rho = np.array(rho).ravel()
        else:
            rho = rho.ravel()

        if np.ndim(P) == 0:
            P = np.array(P).ravel()
        else:
            P = P.ravel()

        Tc = IAPWS95_COEFFS['Tc'] # K
        Pc = IAPWS95_COEFFS['Pc']*10 # bar

        TK = np.zeros([len(P), 1]).ravel()
        for i in range(len(P)):
            if P[i]  > Pc:
                TK[i] = Tc
            else:
                TK[i] = self.calcsatpropP(P[i])[0]
            funct_tsat = lambda TK: self.EOSIAPWS95(TK, rho[i])[0] - P[i]
            TK[i] = fsolve(funct_tsat, TK[i])
        Pout = P; Tout = convert_temperature( TK, Out_Unit = 'C' )
        if FullEOSppt == True:
            [Px, ax, sx, hx, gx, vx,  _, _, _, _, _, _, ux, _, _, _, _, cpx, _, _] = self.vEOSIAPWS95(TK, rho, FullEOSppt = FullEOSppt)
        else:
            [Px, ax, sx, hx, gx, vx,  _, _, _, _, _, _] = self.vEOSIAPWS95(TK, rho, FullEOSppt = FullEOSppt)

        # The following reference state data are in kilogram units.
        ds = 3.5156150 # Entropy (kJ/kg/K)
        du = -15767.19391 # Internal energy (kJ/kg)
        dh = -15970.89538 #  Enthalpy (kJ/kg)
        da = -11906.84446 # Helmholtz energy (kJ/kg-K)
        dg = -12110.54592 # Gibbs energy (kJ/kg)
        htripl = 0.000611782 # tripple point Enthalpy (kJ/kg)
        mwH2O = 18.01528/1000    # kg/mol
        # Calculate the entropy, internal energy, enthalpy, Helmholtz energy, and Gibbs energy
        # on the standard thermochemical scale, and volume, heat capacity at constant volume.
        # Results are converted from KJ and kilogram units to cal and molar units.
        sxcu = sx + ds
        if FullEOSppt == True:
            uxcu = mwH2O*(ux + du)*1000/J_to_cal
            axcu = mwH2O*(ux - TK*sxcu + da)*1000/J_to_cal
            cpxcu = mwH2O*cpx*1000/J_to_cal
        gxcu = mwH2O*(hx - TK*sxcu + dg)*1000/J_to_cal
        hxcu = mwH2O*(hx - htripl + dh)*1000/J_to_cal
        vxcu = mwH2O*vx*1000/J_to_cal
        sxcu = mwH2O*(sx + ds)*1000/J_to_cal

        if FullEOSppt == True:
            return rho, gxcu, hxcu, sxcu, vxcu, Pout, Tout, uxcu, axcu, cpxcu
        else:
            return rho, gxcu, hxcu, sxcu, vxcu, Pout, Tout

    def calcwaterstdppt(self, TK, hx, sx, vx, ux = None, cpx = None, Out_Unit = 'standard'):
        """
        This function converts thermodynamic properties of water from kilogram units to standard thermochemical
        scale (calorie units) and vice-versa.  \n
        Parameters:
        ----------
            TK    :  temperature [K]    \n
            hx    :  Enthalpy [kJ/kg] or [cal/mol]    \n
            sx    :  Entropy [kJ/kg/K] or [cal/mol/K]    \n
            vx    :  Volume [m3/kg]  or [m3/mol]  \n
            ux    :  Internal energy [kJ/kg] or [cal/mol]   \n
            cpx   :  Isobaric heat capacity [kJ/kg/K] or [cal/mol/K]    \n
        Returns:
        ----------
            gx    :  Gibbs energy [kJ/kg] or [cal/mol]  \n
            hx    :  Enthalpy [kJ/kg] or [cal/mol]  \n
            sx    :  Entropy [kJ/kg/K] or[cal/mol/K]  \n
            vx    :  Volume [m3/kg]  or[m3/mol]  \n
            ax    :  Helmholtz energy [kJ/kg/K] or[cal/mol/K]    \n
            ux    :  Internal energy [kJ/kg] or [cal/mol]  \n
            cpx   :  Isobaric heat capacity [kJ/kg/K] or[cal/mol/K]  \n
        Usage:
        ----------
            [gx, hx, sx, vx, ux, ax, cpx] = calcwaterstdppt(TK, hx, sx, vx, ux, cpx, Out_Unit = 'kilogram')   \n
        """
        # The following reference state data are in kilogram units.
        ds = 3.5156150 # Entropy (kJ/kg/K)
        du = -15767.19391 # Internal energy (kJ/kg)
        dh = -15970.89538 #  Enthalpy (kJ/kg)
        da = -11906.84446 # Helmholtz energy (kJ/kg-K)
        dg = -12110.54592 # Gibbs energy (kJ/kg)
        htripl = 0.000611782 # tripple point Enthalpy (kJ/kg)
        mwH2O = 18.01528/1000    # kg/mol
        #Accepted units for input and output are:
        unit_markers = ['kilogram', 'standard']
        if not (Out_Unit in unit_markers):
            return None
        elif Out_Unit == 'standard':
            # Calculate the entropy, internal energy, enthalpy, Helmholtz energy, and Gibbs energy
            # on the standard thermochemical scale, and volume, heat capacity at constant volume.
            # Results are converted from KJ and kilogram units to cal and molar units.
            sxcu = sx + ds
            uxcu = mwH2O*(ux + du)*1000/J_to_cal if ux is not None else 0
            hxcu = mwH2O*(hx - htripl + dh)*1000/J_to_cal
            axcu = mwH2O*(ux - TK*sxcu + da)*1000/J_to_cal if ux is not None else 0
            gxcu = mwH2O*(hx - TK*sxcu + dg)*1000/J_to_cal
            vxcu = mwH2O*vx*1000/J_to_cal
            cpxcu = mwH2O*cpx*1000/J_to_cal if cpx is not None else 0
            sxcu = mwH2O*(sx + ds)*1000/J_to_cal

            return gxcu, hxcu, sxcu, vxcu, axcu, uxcu, cpxcu

        elif Out_Unit == 'kilogram':
            uxcu = ux*J_to_cal/1000/mwH2O - du  if ux is not None else 0
            hxcu = hx*J_to_cal/1000/mwH2O - dh + htripl
            vxcu = vx*J_to_cal/1000/mwH2O
            cpxcu = cpx*J_to_cal/1000/mwH2O  if cpx is not None else 0
            sxcu = sx*J_to_cal/1000/mwH2O - ds
            axcu = ux*J_to_cal/1000/mwH2O - da + TK*(sxcu + ds) if ux is not None else 0
            gxcu = hx*J_to_cal/1000/mwH2O - dg + TK*(sxcu + ds)

            return gxcu, hxcu, sxcu, vxcu, axcu, uxcu, cpxcu

class iapws95:
    """
    Implementation of IAPWS Formulation 1995 for ordinary water substance, revised release of 2016

    Notes
    ------
    Temperature and Pressure input limits
        * -22 ≤ TC ≤ 1000 and 0 ≤ P ≤ 100,000

    Parameters
    ----------
        T : float, vector
            Temperature [°C]  \n
        P : float, vector
            Pressure [bar]  \n
        rho : float, vector
            Density [kg/m³]  \n
        rho0 : float, vector
            Starting estimate of density [kg/m³]  \n
        rhom : float, vector
            Molar density [kg/m³]  \n
        delta : float, vector
            Reduced density, rho/rhoc  \n
        tau : float, vector
            Reduced temperature, Tc/T  \n
        v : float, vector
            Specific volume [m³/kg]  \n
        vm : float, vector
            Specific molar volume [m³/mol]  \n
        Out_Unit : string
            Expected units ('standard' or 'kilogram')  \n
        FullEOSppt : bool
            Option to output all or essential water properties [False or True]  \n

    Returns
    ----------
        The calculated instance has the following potential properties:  \n
        rho : float, vector
            Density [kg/m3]  \n
        G  : float, vector
            Gibbs energy [cal/mol] or  [kJ/kg]  \n
        H  : float, vector
            Enthalpy [cal/mol] or [kJ/kg] \n
        S : float, vector
            Entropy [cal/mol/K] or [kJ/kg/K]   \n
        V : float, vector
            Volume [m3/mol] or [m3/kg] \n
        P : float, vector
            Pressure [bar]  \n
        TC : float, vector
            Temperature [°C]  \n
        TK : float, vector
            Temperature [K]  \n
        U : float, vector
            Internal energy [cal/mol] or [kJ/kg]  if FullEOSppt is True  \n
        F : float, vector
            Helmholtz energy [cal/mol/K] or [kJ/kg-K]  if FullEOSppt is True    \n
        Cp : float, vector
            Isobaric heat capacity [cal/mol/K]  \n
        rhosl : float, vector
            Density of liquid [kg/m3]    \n
        rhosv : float, vector
            Density of vapor [kg/m3]    \n
        pdx : float, vector
            Derivative of pressure with respect to delta in bar    \n
        adx : float, vector
            Helmholtz energy derivative with respect to delta    \n
        ztx : float, vector
            zeta value (needed to calculate viscosity)    \n
        ptx : float, vector
            Derivative of pressure with respect to tau in bar    \n
        gdx : float, vector
            Gibbs energy derivative [kJ/kg]   if FullEOSppt is True  \n
        ktx : float, vector
            Compressibility [/bar]    \n
        avx : float, vector
            Thermal expansion coefficient (thermal expansivity)    \n
        mu : float, vector
            viscosity [Pa-s] if FullEOSppt is True  \n
        bsx : float, vector
            Isentropic temperature-pressure coefficient [K-m3/kJ]  if FullEOSppt is True   \n
        dtx : float, vector
            Isothermal throttling coefficient [kJ/kg/bar]  if FullEOSppt is True   \n
        mux : float, vector
            Joule-Thomsen coefficient [K-m3/kJ]  if FullEOSppt is True   \n
        cvx : float, vector
            Isochoric heat capacity [kJ/kg/K]  if FullEOSppt is True   \n
        wx : float, vector
            Speed of sound [m/s]  if FullEOSppt is True

    Usage:
    ----------
        The general usage of iapws95 is as follows:  \n
        (1) For water properties at any Temperature and Pressure not on steam saturation curve:  \n
            water = iapws95(T = T, P = P),   \n
            where T is temperature in celsius and P is pressure in bar
        (2) For water properties at any Temperature and Pressure on steam saturation curve:  \n
            water = iapws95(T = T, P = 'T'),   \n
            where T is temperature in celsius, followed with a quoted character 'T' to reflect steam saturation pressure  \n
            water = iapws95(T = 'P', P = P),   \n
            where P is pressure in bar, followed with a quoted character 'P' to reflect steam saturation temperature
        (3) For water properties at any Temperature and density :  \n
            water = iapws95(T = T, rho = rho),   \n
            where T is temperature in celsius and rho is density in kg/m³
        (4) For water properties at any Pressure and density :  \n
            water = iapws95(P = P, rho = rho),   \n
            where P is pressure in bar and rho is density in kg/m³
        (5) For water saturation properties at any saturation Temperature :  \n
            water = iapws95(T = T),   \n
            where T is temperature in celsius
        (6) For water saturation properties at any saturation Pressure :  \n
            water = iapws95(P = P),   \n
            where P is pressure in bar

    Examples
    --------
    >>> water = iapws95(T = 200., P = 50, FullEOSppt = True)
    >>> water.rho, water.G, water.H, water.S, water.V, water.P, water.T, water.mu
        867.2595, -60368.41787, -65091.03895,  25.14869,  4.96478e-03,  50.00000,
        200.000, 0.00013546

    >>> water = iapws95(T=200, rho=996.5560, Out_Unit='kilogram', FullEOSppt=True)
    >>> water.P, water.F, water.S, water.H, water.G, water.V, water.Cp, water.pdx
        2872.063, -234.204, 2.051, 1024.747, 53.994, 1.0035e-03, 3.883, 10079.17
    >>> water.adx, water.ztx, water.ptx, water.ktx, water.avx, water.mu, water.gdx
        93.120, 2.189e-03, -7.348e+03,  3.205e-05,  6.809e-04, 1.914e-04, 1011.40

    >>> water = iapws95(T = 350)
    >>> water.P, water.rhosl, water.rhosv
        165.2942 574.7065 113.6056

    >>> water = iapws95(P = 150)
    >>> water.TC, water.rhosl, water.rhosv
        342.1553, 603.5179, 96.7271

    References
    ----------
        (1) Wagner, W., Pruß, A., 2002. The IAPWS formulation 1995 for the thermodynamic properties of
            ordinary water substance for general and scientific use. J. Phys. Chem. Ref. Data 31, 387–535.
            https://doi.org/10.1063/1.1461829

    """

    kwargs = {"T": None,
              "P": None,
              "rho": None,
              "rho0": None, 'FullEOSppt': False,
              "v": None, "Out_Unit": 'standard'}

    mwH2O = 18.015268     # g/mol

    def __init__(self, **kwargs):
        self.kwargs = iapws95.kwargs.copy()
        self.__checker__(**kwargs)
        self.__calc__(**kwargs)

    def __checker__(self, **kwargs):
        self.kwargs.update(kwargs)
        """initialization """
        self.TC = self.kwargs["T"]
        self.rho = self.kwargs["rho"]
        self.rho0 = self.kwargs["rho0"]
        self.P = self.kwargs["P"]
        self.Out_Unit = self.kwargs["Out_Unit"]
        self.FullEOSppt = self.kwargs["FullEOSppt"]
        # Alternative rho input
        if "rhom" in self.kwargs:
            self.kwargs["rho"] = self.kwargs["rhom"]*self.mwH2O
        elif "delta" in self.kwargs:
            self.kwargs["rho"] = self.kwargs["delta"]*IAPWS95_COEFFS['rhoc']
        elif self.kwargs.get("v", 0):
            self.kwargs["rho"] = 1/self.kwargs["v"]
        elif self.kwargs.get("vm", 0):
            self.kwargs["rho"] = self.mwH2O/self.kwargs["vm"]

        # Alternative T input
        if "tau" in self.kwargs:
            self.kwargs["T"] = IAPWS95_COEFFS['Tc']/self.kwargs["tau"]

        if type(self.P) == str:
            if self.P == 'T':
                self.P = Dummy().vcalcsatpropT(convert_temperature( self.TC, Out_Unit = 'K' ))[0]
                self.P[np.isnan(self.P) | (self.P < 1)] = 1.0133

        if type(self.TC) == str:
            if self.TC == 'P':
                self.TC = Dummy().vcalcsatpropP(self.P)[0]
                self.TC = convert_temperature( self.TC, Out_Unit = 'C' ) # convert from K to celcius

        if self.rho0 is not None:
            if np.size(self.rho0) < np.size(self.TC):
                self.rho0 = (self.rho0*np.ones(len(self.TC))).ravel()

        """Check if inputs are enough to define state"""
        if type(self.P) != str and type(self.TC) != str:
            if np.ravel(self.TC).any() and np.ravel(self.P).any():
                self.mode = "T_P"
                if np.size(self.P) < np.size(self.TC):
                    if np.ndim(self.P) == 0:
                        self.P = np.ravel(self.P)
                    self.P = (self.P[0]*np.ones(len(self.TC))).ravel()
                if np.size(self.TC) < np.size(self.P):
                    if np.ndim(self.TC) == 0:
                        self.TC = np.ravel(self.TC)
                    self.TC = (self.TC[0]*np.ones(len(self.P))).ravel()
            elif np.ravel(self.TC).any() and np.ravel(self.rho).any():
                self.mode = "T_rho"
                if np.size(self.rho) < np.size(self.TC):
                    if np.ndim(self.rho) == 0:
                        self.rho = np.ravel(self.rho)
                    self.rho = (self.rho[0]*np.ones(len(self.TC))).ravel()
                if np.size(self.TC) < np.size(self.rho):
                    if np.ndim(self.TC) == 0:
                        self.TC = np.ravel(self.TC)
                    self.TC = (self.TC[0]*np.ones(len(self.rho))).ravel()
            elif np.ravel(self.P).any() and np.ravel(self.rho).any():
                self.mode = "P_rho"
                if np.size(self.P) < np.size(self.rho):
                    if np.ndim(self.P) == 0:
                        self.P = np.ravel(self.P)
                    self.P = (self.P[0]*np.ones(len(self.rho))).ravel()
                if np.size(self.rho) < np.size(self.P):
                    if np.ndim(self.rho) == 0:
                        self.rho = np.ravel(self.rho)
                    self.rho = (self.rho[0]*np.ones(len(self.P))).ravel()
            elif np.ravel(self.TC).any() and np.ravel(self.P).any() is None:
                self.mode = "T_x"
            elif np.ravel(self.P).any() and np.ravel(self.TC).any() is None:
                self.mode = "P_x"
            else:
                self.mode = ""
        else:
            if self.TC and self.P:
                self.mode = "T_P"
        self.TK = convert_temperature( self.TC, Out_Unit = 'K' ) if self.TC is not None else None

    def __calc__(self, **kwargs):
        self.kwargs.update(kwargs)
        self.msg = 'Temperature and Pressure input limits: -22 ≤ TC ≤ 1000 and 0 ≤ P ≤ 100,000'
        if self.mode == "T_P":
            water = Dummy().calcwaterppt(self.TC, self.P, self.rho0, FullEOSppt = self.FullEOSppt)
            if self.FullEOSppt is True:
                [self.rho, self.G, self.H, self.S, self.V, self.P, self.TC, self.U, self.F, self.Cp] = water
                self.mu = Dummy().vwaterviscosity(self.TC, self.P, self.rho)
            else:
                [self.rho, self.G, self.H, self.S, self.V, self.P, self.TC] = water

            if self.Out_Unit.lower() == 'kilogram':
                if self.FullEOSppt is True:
                    water = Dummy().calcwaterstdppt(self.TK, self.H, self.S, self.V, ux = self.U, cpx = self.Cp, Out_Unit = 'kilogram')
                    [self.G, self.H, self.S, self.V, self.F, self.U, self.Cp] = water
                else:
                    water = Dummy().calcwaterstdppt(self.TK, self.H, self.S, self.V, Out_Unit = 'kilogram')
                    [self.G, self.H, self.S, self.V] = water[:4]

        elif self.mode == "T_rho":
            water = Dummy().vEOSIAPWS95(self.TK, self.rho, FullEOSppt = self.FullEOSppt)
            if self.FullEOSppt is True:
                [self.P, self.F, self.S, self.H, self.G, self.V, self.pdx, self.adx, self.ztx, self.ptx, self.ktx, self.avx, self.U, self.gdx, self.bsx, self.dtx, self.mux, self.Cp, self.cvx, self.wx] = water
                self.mu = Dummy().vwaterviscosity(self.TC, self.P, self.rho)
            else:
                [self.P, self.F, self.S, self.H, self.G, self.V, self.pdx, self.adx, self.ztx, self.ptx, self.ktx, self.avx] = water

            if self.Out_Unit.lower() == 'standard':
                if self.FullEOSppt is True:
                    water = Dummy().calcwaterstdppt(self.TK, self.H, self.S, self.V, ux = self.U, cpx = self.Cp, Out_Unit = 'standard')
                    [self.G, self.H, self.S, self.V, self.F, self.U, self.Cp] = water
                else:
                    water = Dummy().calcwaterstdppt(self.TK, self.H, self.S, self.V, Out_Unit = 'standard')
                    [self.G, self.H, self.S, self.V] = water[:4]

        elif self.mode == "P_rho":
            water = Dummy().calcwaterppt_Prho(self.P, self.rho, FullEOSppt = self.FullEOSppt)
            if self.FullEOSppt is True:
                [self.rho, self.G, self.H, self.S, self.V, self.P, self.TC, self.U, self.F, self.Cp] = water
                self.mu = Dummy().vwaterviscosity(self.TC, self.P, self.rho)
            else:
                [self.rho, self.G, self.H, self.S, self.V, self.P, self.TC] = water

            if self.Out_Unit.lower() == 'kilogram':
                if self.FullEOSppt is True:
                    water = Dummy().calcwaterstdppt(self.TK, self.H, self.S, self.V, ux = self.U, cpx = self.Cp, Out_Unit = 'kilogram')
                    [self.G, self.H, self.S, self.V, self.F, self.U, self.Cp] = water
                else:
                    water = Dummy().calcwaterstdppt(self.TK, self.H, self.S, self.V, Out_Unit = 'kilogram')
                    [self.G, self.H, self.S, self.V] = water[:4]

        elif self.mode == "P_x":
            water = Dummy().vcalcsatpropP(self.P)
            [self.TK, self.rhosl, self.rhosv] = water
            self.TC = convert_temperature( self.TK, Out_Unit = 'C' )
        elif self.mode == "T_x":
            water = Dummy().vcalcsatpropT(self.TK)
            [self.P, self.rhosl, self.rhosv] = water
        elif self.mode == "":
            return ('For water properties at any Temperature and Pressure \n \
                    input T = temperature (celsius) and P = pressure (bar)  \n \
                        For water properties at any Temperature and Pressure on steam saturation curve \n' + \
                        'input T = temperature (celsius) and P = "T" to reflect steam saturation pressure  \n' + \
                            'For water properties at any Temperature and density  \n' + \
                                'input T = temperature (celsius) and rho  = density (kg/m³) in kg/m³' +\
                                    'For water properties at any Pressure and density \n' + \
                                        'input P = pressure (bar) and rho  = density (kg/m³) \n' + \
                                            'For water saturation properties at any saturation Temperature  \n' + \
                                                'input T = temperature (celsius) \n' + \
                                                    'For water saturation properties at any saturation Pressure \n' + \
                                                        'P = pressure (bar)')

class ZhangDuan():
    """
    Implementation of Zhang & Duan model Formulation for water at higher Temperature and Pressure conditions, i.e, Deep Earth Water - DEW

    Notes
    ------
    Temperature and Pressure input limits
        * 0 ≤ TC ≤ 1726.85 and 1000 ≤ P ≤ 300,000

    Parameters
    ----------
        T : float, vector
            Temperature [°C]  \n
        P : float, vector
            Pressure [bar]  \n
        rho : float, vector
            Density [kg/m³]  \n
        rho0 : float, vector
            Starting estimate of density [kg/m³]  \n
        densityEquation : string
            specify either 'ZD05' to use Zhang & Duan (2005) or 'ZD09'  to use Zhang & Duan (2009)

    Returns
    ----------
        The calculated instance has the following potential properties:  \n
        rho : float, vector
            Density [kg/m3]  \n
        rhohat : float, vector
            Density [g/cm³]  \n
        G : float, vector
            Gibbs energy [cal/mol]  \n
        drhodP_T : float, vector
            Partial derivative of density with respect to pressure at constant temperature \n
        drhodT_P : float, vector
            Partial derivative of density with respect to temperature at constant pressure

    Usage:
    ----------
        The general usage of ZhangDuan is as follows:  \n
        (1) For water properties at any Temperature and Pressure:  \n
            deepearth = ZhangDuan(T = T, P = P),   \n
            where T is temperature in celsius and P is pressure in bar
        (2) For water properties at any Temperature and density :  \n
            deepearth = ZhangDuan(T = T, rho = rho),   \n
            where T is temperature in celsius and rho is density in kg/m³

    Examples
    --------
    >>> deepearth = ZhangDuan(T = 25, P = 5000)
    >>> deepearth.rho, deepearth.G, deepearth.drhodP_T, deepearth.drhodT_P
        1145.3065, -54631.5351, 2.3283e-05, -0.0004889

    >>> deepearth = ZhangDuan(T = 200, rho = 1100)
    >>> deepearth.P, deepearth.G, deepearth.drhodP_T, deepearth.drhodT_P
        7167.2231, -57319.0980, 2.3282e-05, -0.0005122

    References
    ----------
        (1) Zhang, Z., Duan, Z., 2005. Prediction of the PVT properties of water over wide range of
            temperatures and pressures from molecular dynamics simulation. Phys. Earth Planet. Inter.
            149, 335–354. https://doi.org/10.1016/j.pepi.2004.11.003.
        (2) Zhang, C. and Duan, Z., 2009. “A model for C-O-H fluid in the Earth’s mantle”, Geochimica et
            Cosmochimica Acta, vol. 73, no. 7, pp. 2089–2102, doi:10.1016/j.gca.2009.01.021.
        (3) Sverjensky, D.A., Harrison, B., Azzolini, D., 2014. Water in the deep Earth: The dielectric
            constant and the solubilities of quartz and corundum to 60kb and 1200°C. Geochim. Cosmochim.
            Acta 129, 125–145. https://doi.org/10.1016/j.gca.2013.12.019
    """

    kwargs = {"T": None, "P": None, "rho": None, "rho0": 1e-5,
              "error": 1e-2, "densityEquation": 'ZD05'}

    def __init__(self, **kwargs):
        self.kwargs = ZhangDuan.kwargs.copy()
        self.__calc__(**kwargs)

    def __calc__(self, **kwargs):
        self.kwargs.update(kwargs)
        self.msg = 'Temperature and Pressure input limits: 0 ≤ TC ≤ 1726.85 and 1000 ≤ P ≤ 300,000'
        self.TC = self.kwargs["T"]
        self.P = self.kwargs["P"]
        self.rho = self.kwargs["rho"]
        self.rho0 = self.kwargs["rho0"]
        self.method = self.kwargs["densityEquation"]
        self.error = self.kwargs["error"]

        if type(self.P) == str and np.ravel(self.TC).any():
            self.mode = "T_P"
        elif np.ravel(self.TC).any() and np.ravel(self.P).any():
            self.mode = "T_P"
            if np.size(self.P) < np.size(self.TC):
                self.P = (self.P*np.ones_like(self.TC)).ravel()
            if np.size(self.TC) < np.size(self.P):
                self.TC = (self.TC*np.ones_like(self.P)).ravel()
        elif np.ravel(self.TC).any() and np.ravel(self.rho).any():
            self.mode = "T_rho"
            if np.size(self.rho) < np.size(self.TC):
                self.rho = (self.rho*np.ones_like(self.TC)).ravel()
            if np.size(self.TC) < np.size(self.rho):
                self.TC = (self.TC*np.ones_like(self.rho)).ravel()
        else:
            self.mode = ''

        if self.mode == "T_P":
            self.rhohat  = self.ZD_Density(self.TC, self.P, method = self.method, error = self.error).ravel()
            self.rho = self.rhohat*1000
        elif self.mode == "T_rho":
            self.rhohat = self.rho/1000
            self.P = self.ZD_Pressure_drhodP(self.TC, self.rhohat, method = self.method)[0]

        self.G = self.GibbsEnergy(self.TC, self.P, method = 'VolumeIntegral').ravel()
        if type(self.P) != str:
            f_rT = lambda x: self.ZD_Density(x, self.P, method = self.method, error = 1e-4)
            self.drhodT_P = derivative(f_rT, self.TC, h = 0.0001).ravel()
            f_rP = lambda x: self.ZD_Density(self.TC, x, method = self.method, error = 1e-4)
            self.drhodP_T = derivative(f_rP, self.P, h = 0.0001).ravel()
        else:
            self.drhodT_P = 0; self.drhodP_T = 0

        if self.mode not in ["T_P", "T_rho"]:
            return ('For water properties at any Temperature and Pressure \n \
                    input T = temperature (celsius) and P = pressure (bar)  \n' + \
                        'For water properties at any Temperature and density  \n' + \
                            'input T = temperature (celsius) and rho  = density (kg/m³) in kg/m³')

    def ZD_Pressure_drhodP(self, TC, rhohat, method = None):

        if np.ndim(TC) == 0:
            TC = np.array(TC).ravel()
        if np.ndim(rhohat) == 0:
            rhohat = np.array(rhohat).ravel()

        mwH2O = 18.01528         # 'Molar mass of water molecule in units of g/mol
        TK = convert_temperature(TC, Out_Unit = 'K')   # 'Temperature must be converted to Kelvin

        P = np.zeros([len(TK), 1]); drhodP_T = np.zeros([len(TK), 1])
        for k in range(len(TK)):
            if method == 'ZD05':
                ZD05_R = 83.14467       # 'Gas Constant in units of cm^3 bar/mol/K
                ZD05_Vc = 55.9480373    # 'Critical volume in units of cm^3/mol
                ZD05_Tc = 647.25        # 'Critical temperature in units of Kelvin
                Vr = mwH2O / rhohat[k] / ZD05_Vc
                Tr = TK[k] / ZD05_Tc
                cc = ZD05_Vc / mwH2O          # 'This term appears frequently in the equation and is defined here for convenience

                B = 0.349824207 - 2.91046273 / (Tr**2) + 2.00914688 / (Tr**3)
                C = 0.112819964 + 0.748997714 / (Tr**2) - 0.87320704 / (Tr**3)
                D = 0.0170609505 - 0.0146355822 / (Tr**2) + 0.0579768283 / (Tr**3)
                E = -0.000841246372 + 0.00495186474 / (Tr**2) - 0.00916248538 / (Tr**3)
                F = -0.100358152 / Tr
                G = -0.00182674744 * Tr

                delta = 1 + B / Vr + C / (Vr**2) + D / Vr**4 + E / Vr**5 + (F / (Vr**2) + G / Vr**4) * np.exp(-0.0105999998 / Vr**2)

                P[k] = ZD05_R * TK[k] * rhohat[k] * delta / mwH2O

                kappa = B * cc + 2 * C * (cc**2) * rhohat[k] + 4 * D * cc**4 * rhohat[k]**3 + 5 * E * cc**5 * rhohat[k]**4 + \
                    (2 * F * (cc**2) * rhohat[k] + 4 * G * cc**4 * rhohat[k]**3 - (F / (Vr**2) + G / Vr**4) * (2 * 0.0105999998 * (cc**2) * rhohat[k])) * np.exp(-0.0105999998 / (Vr**2))

                drhodP_T[k] = mwH2O / (ZD05_R * TK[k] * (delta + rhohat[k] * kappa))

            elif method == 'ZD09':

                ZD09_R = 0.083145        #  'Gas constant in units of dm^3 bar/mol/K
                ZD09_epsilon = 510      #   'Lenard-Jones parameter in units of K
                ZD09_omega = 2.88       #   'Lenard-Jones parameter in units of 1E-10 m
                ZD09_c1 = ZD09_epsilon / (3.0626 * ZD09_omega**3)

                # 'Prefactor calculated from 1000 * pow(ZD09_omega / 3.691, 3)
                dm = pow(ZD09_omega / 3.691, 3)*1000*rhohat[k]
                # 'Prefactor calculated from 0.001 * pow(3.691 / ZD09_omega, 3)
                Vm = pow(3.691 / ZD09_omega, 3) * 0.001 * (mwH2O / rhohat[k])
                # 'Prefactor calculated from 154 / ZD09_epsilon
                Tm = 154 / ZD09_epsilon * TK[k]

                B = 0.029517729893 - 6337.56452413 / (Tm**2) - 275265.428882 / (Tm**3)
                C = 0.00129128089283 - 145.797416153 / (Tm**2) + 76593.8947237 / (Tm**3)
                D = 2.58661493537E-06 + 0.52126532146 / (Tm**2) - 139.839523753 / (Tm**3)
                E = -2.36335007175E-08 + 0.00535026383543 / (Tm**2) - 0.27110649951 / (Tm**3)
                F = 25038.7836486 / (Tm**3)
                G = 0.73226726041 + 0.015483335997 / (Vm**2)

                delta = 1 + B / Vm + C / (Vm**2) + D / pow(Vm, 4) + E / pow(Vm, 5) +  F / (Vm**2) * G * \
                    np.exp(-0.015483335997 / (Vm**2))

                Pm = ZD09_R * Tm * delta / Vm

                P[k] = Pm * ZD09_c1
                kappa = B / mwH2O + 2 * C * dm / (mwH2O**2) + 4 * D * pow(dm, 3) / pow(mwH2O, 4) + \
                    5 * E * pow(dm, 4) / pow(mwH2O, 5) +  (2 * F * dm / (mwH2O**2) *  G + \
                                                           F / pow(Vm, 2) * (1 - G) * \
                                                               (2 * 0.015483335997 * dm / (mwH2O**2))) * \
                        np.exp(-0.015483335997 / (Vm**2))
                drhodP_T[k] = ZD09_c1 * mwH2O / (ZD09_c1 * ZD09_R * Tm * (delta + dm * kappa))

        return P, drhodP_T

    def ZD_Density(self, TC, P, method = 'ZD05', error = None):
        if type(P) == str:
            if P == 'T':
                # 'This equation models the density of water as a function of temperature along the Psat curve.
                #'It has an R^2 value of 0.9999976885 as compared with Supcrt92 values.
                rhohat = -1.01023381581205e-104 * pow(TC, 40) + -1.1368599785953e-27 * pow(TC, 10) + \
                    -2.11689207168779e-11 * pow(TC, 4) +  1.26878850169523e-08 * pow(TC, 3) + \
                        -4.92010672693621e-06 * pow(TC, 2) +  -3.2666598612692e-05 * TC +  1.00046144613017

        else:
            if np.ndim(TC) == 0:
                TC = np.array(TC).ravel()
            if np.ndim(P) == 0:
                P = np.array(P).ravel()
            rhohat = np.zeros([len(TC), 1])
            for k in range(len(TC)):
                #'Define variables
                minGuess = 0.00001
                guess = self.rho0
                equation = 1 if method == 'ZD05' else 2
                maxGuess = 7.5 * equation - 5   #'The maxGuess is dependent on the value of "equation"
                calcP = 0

                #'Loop through and find the density
                for i in range(100):
                    #'Calculates the pressure using the specified equation
                    calcP = self.ZD_Pressure_drhodP(TC[k], guess, method = method)[0]

                    #'If the calculated pressure is not equal to input pressure, this determines a new
                    #'guess for the density based on current guess and how the calculated pressure
                    #'relates to the input pressure. In effect, this a form of a bisection method.
                    # print('count ', i, 'rhohat', guess, 'P', calcP > P)
                    if abs(calcP - P[k]) > error:
                        if calcP > P[k]:
                            maxGuess = guess
                            guess = (guess + minGuess) / 2 #
                        else:
                            minGuess = guess
                            guess = (guess + maxGuess) / 2 #
                    else:
                        rhohat[k] = guess
                        break

        return rhohat

    def GibbsEnergy(self, TC, P, method = 'VolumeIntegral'):

        if type(P) == str:
            if P == 'T':
                dGH2O = -2.72980941772081e-103 * pow(TC, 40) + 2.88918186300446e-25 * pow(TC, 10) +\
                    -2.21891314234246e-08 * pow(TC, 4) +  3.0912103873633e-05 * pow(TC, 3) +\
                        -3.20873264480928E-02 * pow(TC, 2) +  -15.169458452209 * TC +  -56289.0379433809
        else:
            if np.ndim(TC) == 0:
                TC = np.array(TC).ravel()
            if np.ndim(P) == 0:
                P = np.array(P).ravel()
            dGH2O = np.zeros([len(TC), 1])
            for k in range(len(TC)):
                if method == 'DH78':     # 'Delaney & Helgeson (1978) equation
                    coeff = [-56130.073, 0.38101798, -0.0000021167697, 2.0266445e-11, -8.3225572e-17, -15.285559,
                             0.0001375239, -1.5586868e-09, 6.6329577e-15, -0.026092451, 0.000000035988857,
                             -2.7916588e-14, 0.000017140501, -1.6860893e-11, -6.0126987e-09]

                    dGH2O_ = 0
                    Count = 0
                    for j in range(4):
                        for k in range(4 - j):
                            dGH2O_ = dGH2O_ + coeff(Count) * pow(TC[k], j) * pow(P[k], k)
                            Count = Count + 1
                    dGH2O[k] = dGH2O_

                elif method == 'VolumeIntegral':
                    mwH2O = 18.01528         # 'Molar mass of water molecule in units of g/mol
                    # 'Gibbs Free Energy of water at 1 kb. This equation is a polynomial fit to data as a function of temperature.
                    # 'It is valid in the range of 100 to 1000 C.
                    dGH2O_1Kb = 2.6880734e-09*TC[k]**4 + 6.3163061e-07*TC[k]**3 - 0.019372355*TC[k]**2 - 16.945093*TC[k] - 55769.287

                    if P[k] < 1000:             # 'Simply return zero, this method only works at P >= 1000 bars
                        integral = np.nan
                    elif P[k] == 1000:         # 'Return the value calculated above from the polynomial fit
                        integral = 0
                    elif P[k] > 1000:          # 'Integrate from 1 kb to P over the volume
                        integral = 0
                        # 'Integral is sum of rectangles with this width. This function in effect limits the spacing
                        # 'to 20 bars so that very small pressures do not have unreasonably small widths. Otherwise the width
                        # 'is chosen such that there are always 500 steps in the numerical integration. This ensures that for very
                        # 'high pressures, there are not a huge number of steps calculated which is very computationally taxing.
                        spacing = 20 if ((P[k] - 1000) / 500 < 20) else (P[k] - 1000) / 500
                        for i in np.arange(1000, P[k].item(), spacing):
                            # 'This integral determines the density only down to an error of 100 bars
                            # 'rather than the standard of 0.01. This is done to save computational
                            # 'time. Tests indicate this reduces the computation by about a half while
                            # 'introducing little error from the standard of 0.01.
                            integral = integral + (mwH2O / self.ZD_Density(TC[k], i, error = 100) / 41.84) * spacing
                    dGH2O[k] = dGH2O_1Kb + integral

        return dGH2O

class water_dielec():
    """
    Class Implementation of Water dielectric constants, the Debye-Huckel "A" and "B" parameters and their derivatives at ambient to deep-earth Temperature and Pressure conditions with three different formulations

    Parameters
    ----------
        T : float, vector
            Temperature [°C]  \n
        P : float, vector
            Pressure [bar]  \n
        rho : float, vector
            Density [kg/m³]  \n
        Dielec_method : string
            specify either 'FGL97' or 'JN91' or 'DEW' as the method to calculate dielectric constant (optional), if not specified, default - 'JN91'  \n
        Dielec_DEWoutrange : string
            specify either 'FGL97' or 'JN91' as the method to calculate dielectric constant for out of range for 'DEW' method if any

    Returns
    ----------
        The calculated instance has the following potential properties:
        E  : float, vector
            dielectric constant of water  \n
        rhohat : float, vector
            density [g/cm³] \n
        Ah : float, vector
            Debye-Huckel "A" parameters [kg^1/2 mol^-1/2] \n
        Bh : float, vector
            Debye-Huckel "B" parameters [kg^1/2 mol^-1/2 Angstrom^-1] \n
        bdot : float, vector
            bdot at any given temperature T \n
        Adhh : float, vector
            Debye-Huckel "A" parameters associated with apparent molar enthalpy \n
        Adhv : float, vector
            Debye-Huckel "A" parameters associated with apparent molar volume \n
        Bdhh : float, vector
            Debye-Huckel "B" parameters associated with apparent molar enthalpy \n
        Bdhv : float, vector
            Debye-Huckel "B" parameters associated with apparent molar volume \n
        dEdP_T : float, vector
            Partial derivative of dielectric constant with respect to pressure at constant temperature \n
        dEdT_P : float, vector
            Partial derivative of dielectric constant with respect to temperature at constant pressure

    Notes
    ------
        FGL97 Temperature and Pressure input limits:
            * -35 ≤ TC ≤ 600 and 0 ≤ P ≤ 12000
        DEW Temperature and Pressure input limits:
            * 100 ≤ TC ≤ 1200 and 1000 ≤ P ≤ 60000
        JN91 Temperature and Pressure input limits:
            * 0 ≤ TC ≤ 1000 and 0 ≤ P ≤ 5000

    Usage
    ----------
        The general usage of water_dielec is as follows:  \n
        (1) For water dielectric properties at any Temperature and Pressure:  \n
            dielect = water_dielec(T = T, P = P, Dielec_method = 'JN91'),   \n
            where T is temperature in celsius and P is pressure in bar
        (2) For water dielectric properties at any Temperature and density :  \n
            dielect = water_dielec(T = T, rho = rho, Dielec_method = 'JN91'),   \n
            where T is temperature in celsius and rho is density in kg/m³
        (3) For water dielectric properties at any Temperature and Pressure on steam saturation curve:  \n
            dielect = water_dielec(T = T, P = 'T', Dielec_method = 'JN91'),   \n
            where T is temperature in celsius and P is assigned a quoted character 'T' to reflect steam saturation pressure  \n
            dielect = water_dielec(P = P, T = 'P', Dielec_method = 'JN91'),   \n
            where P is pressure in bar and T is assigned a quoted character 'P' to reflect steam saturation temperature

    Examples
    --------
    >>> dielect = water_dielec(T = 50, P = 500, Dielec_method = 'JN91')
    >>> dielect.E, dielect.rhohat, dielect.Ah, dielect.Bh, dielect.bdot
        71.547359, 1.00868586, 0.52131899,   0.33218072,   0.04088528
    >>> dielect.Adhh, dielect.Adhv, dielect.Bdhh, dielect.Bdhv
        0.64360153,   2.13119279,  15.6936832 , -14.52571678
    >>> dielect.dEdP_T, dielect.dEdT_P
        0.03293026,   -0.32468033

    >>> dielect = water_dielec(T = 200, rho = 1100, Dielec_method = 'FGL97')
    >>> dielect.E, dielect.rhohat, dielect.Ah, dielect.Bh, dielect.bdot
        49.73131404,  1.1,  0.5302338, 0.34384714,  0.04452579
    >>> dielect.Adhh, dielect.Adhv, dielect.Bdhh, dielect.Bdhv
        1.21317825,  2.21165281, 28.0047878, -34.21216547
    >>> dielect.dEdP_T, dielect.dEdT_P
        0.01444368, -0.16864644

    >>> dielect = water_dielec(T = 250, P = 5000, Dielec_method = 'DEW')
    >>> dielect.E, dielect.rhohat, dielect.Ah, dielect.Bh, dielect.bdot, dielect.Adhh
        39.46273008,  1.0238784,  0.62248141,   0.35417088, 0.02878662, 0.80688122
    >>> dielect.Adhv, dielect.Bdhh, dielect.Bdhv, dielect.dEdP_T, dielect.dEdT_P
         3.13101408, 39.76402294, -35.29670957, 0.0129006 , -0.08837842

    References
    ----------
        (1) Release on the Static Dielectric Constant of Ordinary Water Substance for
            Temperatures from 238 K to 873 K and Pressures up to 1000 MPa" (IAPWS R8-97, 1997).
        (2) Fernandez D. P., Goodwin A. R. H., Lemmon E. W., Levelt Sengers J. M. H.,
            and Williams R. C. (1997) A Formulation for the Permittivity of Water and
            Steam at Temperatures from 238 K to 873 K at Pressures up to 1200 MPa, including
            Derivatives and Debye-Hückel Coefficients. J. Phys. Chem. Ref. Data 26, 1125-1166.
        (3) Helgeson H. C. and Kirkham D. H. (1974) Theoretical Prediction of the Thermodynamic
            Behavior of Aqueous Electrolytes at High Pressures and Temperatures: II.
            Debye-Huckel Parameters for Activity Coefficients and Relative Partial Molal Properties.
            Am. J. Sci. 274, 1199-1251.
        (4) Johnson JW, Norton D (1991) Critical phenomena in hydrothermal systems: State, thermodynamic,
            electrostatic, and transport properties of H2O in the critical region. American Journal of Science 291:541-648
        (5) D. A. Sverjensky, B. Harrison, and D. Azzolini, "Water in the deep Earth: the dielectric
            constant and the solubilities of quartz and corundum to 60 kb and 1200 °C," Geochimica et
            Cosmochimica Acta, vol. 129, pp. 125–145, 2014
    """
    kwargs = {"T": None,
              "P": None,
              "rho": None,
              "Dielec_method": None,
              "Dielec_DEWoutrange": None}

    def __init__(self, **kwargs):
        self.kwargs = water_dielec.kwargs.copy()
        self.__checker__(**kwargs)
        self.__calc__(**kwargs)


    def __checker__(self, **kwargs):
        self.kwargs.update(kwargs)
        self.TC = self.kwargs["T"]
        self.P = self.kwargs["P"]
        self.rho = self.kwargs['rho']
        self.Dielec_method = 'JN91' if self.kwargs["Dielec_method"] is None else self.kwargs["Dielec_method"]
        self.Dielec_DEWoutrange = 'JN91' if self.kwargs["Dielec_DEWoutrange"] is None else self.kwargs["Dielec_DEWoutrange"]
        if (type(self.P) == str) or (type(self.TC) == str):
            if self.P == 'T':
                self.P = np.array(iapws95(T=self.TC).P, dtype=float)  # force float array
                self.P[np.isnan(self.P) | (self.P < 1)] = 1.0133
            elif self.TC == 'P':
                self.TC = iapws95(P = self.P).TC
        if self.rho is None:
            self.rho = iapws95(T = self.TC, P = self.P).rho
        self.TK = convert_temperature( self.TC, Out_Unit = 'K' ) if self.TC is not None else 0
        if np.ndim(self.TC) == 0:
            self.TC = np.array(self.TC).ravel()
        else:
            self.TC = self.TC.ravel()
        if np.ndim(self.P) == 0:
            self.P = np.array(self.P).ravel()
        else:
            self.P = self.P.ravel()
        if np.ndim(self.rho) == 0:
            self.rho = np.array(self.rho).ravel()
        else:
            self.rho = self.rho.ravel()

    def __calc__(self, **kwargs):
        if self.Dielec_method.upper() == 'FGL97':
            self.msg = 'Temperature and Pressure input limits: -35 ≤ TC ≤ 600 and 0 ≤ P ≤ 12000 \n'
            waterdielec = self.dielec_FGL97(self.TC, self.rho)
        elif self.Dielec_method.upper() == 'JN91':
            self.msg = 'Temperature and Pressure input limits: 0 ≤ TC ≤ 1000 and 0 ≤ P ≤ 5000 \n'
            waterdielec = self.dielec_JN91(self.TC, self.rho)
        elif self.Dielec_method.upper() == 'DEW':
            self.msg = 'Temperature and Pressure input limits: 100 ≤ TC ≤ 1200 and 1000 ≤ P ≤ 60000 \n'
            waterdielec = self.dielec_DEW()

        self.E, self.rhohat, self.Ah, self.Bh, self.bdot, self.Adhh, self.Adhv, self.Bdhh, self.Bdhv, self.dEdP_T, self.dEdT_P = waterdielec

    def dielec_FGL97(self, TC, rho):
        """
        This function employs the FGL91 formulation to calculate the dielectric constant of water (E), the Debye-Huckel "A" parameters
        and Debye-Huckel "B" parameters (3)  and their derivatives as a
        function of temperature and pressure \n

        Notes
        ------
        Temperature and Pressure input limits:
            * -35 ≤ TC ≤ 600 and 0 ≤ P ≤ 12000

        Parameters
        ----------
           TC      : temperature [°C] \n
           rho     : density [kg/m3]

        Returns
        ----------
           E       : dielectric constant of water  \n
           rhohat  : density [g/cm³] \n
           Ah      : Debye-Huckel "A" parameters [kg^1/2 mol^-1/2] \n
           Bh      : Debye-Huckel "B" parameters [kg^1/2 mol^-1/2 Angstrom^-1] \n
           bdot    : bdot at any given temperature T  \n
           Adhh    : Debye-Huckel "A" parameters associated with apparent molar enthalpy  \n
           Adhv    : Debye-Huckel "A" parameters associated with apparent molar volume  \n
           Bdhh    : Debye-Huckel "B" parameters associated with apparent molar enthalpy  \n
           Bdhv    : Debye-Huckel "B" parameters associated with apparent molar volume  \n
           dEdP_T  : Partial derivative of dielectric constant with respect to pressure at constant temperature  \n
           dEdT_P  : Partial derivative of dielectric constant with respect to temperature at constant pressure

        Usage
        ----------
           [E, rhohat, Ah, Bh, bdot, Adhh, Adhv, Bdhh, Bdhv, dEdP_T, dEdT_P] = dielec_FGL97( TC, rho)

        References
        ----------
            (1) Release on the Static Dielectric Constant of Ordinary Water Substance for
                Temperatures from 238 K to 873 K and Pressures up to 1000 MPa" (IAPWS R8-97, 1997).
            (2) Fernandez D. P., Goodwin A. R. H., Lemmon E. W., Levelt Sengers J. M. H.,
                and Williams R. C. (1997) A Formulation for the Permittivity of Water and
                Steam at Temperatures from 238 K to 873 K at Pressures up to 1200 MPa, including
                Derivatives and Debye-Hückel Coefficients. J. Phys. Chem. Ref. Data 26, 1125-1166.
            (3) Helgeson H. C. and Kirkham D. H. (1974) Theoretical Prediction of the Thermodynamic
                Behavior of Aqueous Electrolytes at High Pressures and Temperatures: II.
                Debye-Huckel Parameters for Activity Coefficients and Relative Partial Molal Properties.
                Am. J. Sci. 274, 1199-1251.
        """
        if np.ndim(TC) == 0:
            TC = np.array(TC).ravel()
        else:
            TC = TC.ravel()
        if np.ndim(rho) == 0:
            rho = np.array(rho).ravel()
        else:
            rho = rho.ravel()
        TK = convert_temperature( TC, Out_Unit = 'K' )

        water = iapws95(T = TC, rho = rho)
        ptx, ktx, avx = water.ptx, water.ktx, water.avx
        ptx = ptx*0.1  # convert to MPa units
        ktx = ktx/0.1  # convert to /MPa units

        Tc = IAPWS95_COEFFS['Tc'] # K
        # Pc = IAPWS95_COEFFS['Pc'] # MPa
        rhoc = IAPWS95_COEFFS['rhoc'] # kg/m3
        mwH2O = 18.01528/1000  # kg/mol
        R = IAPWS95_COEFFS['R']/1000*mwH2O # kJ mol-1 K-1
        Nh = np.array([0.978224486826, -0.957771379375e0, 0.237511794148e0, 0.714692244396e0,
              -0.298217036956, -0.108863472196e0, 0.949327488264e-01, -0.980469816509e-02,
            0.165167634970e-04, 0.937359795772e-04, -0.123179218720e-09, 0.196096504426e-02])
        ih = np.array([1, 1, 1, 2, 3, 3, 4, 5, 6, 7, 10])
        jh = np.array([0.25, 1.0, 2.5, 1.5, 1.5, 2.5, 2.0, 2.0, 5.0, 0.5, 10.0])
        Nh = Nh.reshape(-1, 1); ih = ih.reshape(-1, 1); jh = jh.reshape(-1, 1)

        alphammp = 1.636e-40    # Mean molecular polarizability C^2 J^-1 m^2
        xmudp = 6.138e-30       # Molecular dipole moment C.m
        e = 1.6021773310e-19    # elementary charge e is 1.602176634 x 10^-19 coulomb (C)
        kB = 1.380658e-23        # Boltzmann constant k is 1.380649 x 10^-23 J K^-1
        NA = 6.0221367e23       # Avogadro constant NA is 6.02214076 x 10^23 mol^-1

        #  expression for calculating the permittivity of free space, eps0.
        c = 2997924580.0 # the speed of light in classical vacuum  m/s
        mu0 = 4.0e-07 * np.pi # the permeability of free space N Angstrom^-2

        rhom = rho/mwH2O     # molar density mol/m3
        rhocrm = rhoc/mwH2O  # critical molar density mol/m3

        # Get the permittivity of free space (eps0). eps0 = 1/(mu0*c^2)
        eps0 = 1/( mu0 * (c * 0.1)**2) # C^2 J^-1 m^-1
        delta = rhom/rhocrm
        tau = Tc/TK

        # Get the Harris and Alder g factor (g).
        g = 1 + np.sum(Nh[:-1]*(delta**ih)*(tau**jh), 0) + Nh[-1]*delta*((TK/228) - 1)**(-1.2)
        # Get A and B.
        A = ( NA*(xmudp**2)*rhom*g )/( eps0*kB*TK )
        B = ( NA*alphammp*rhom )/( 3*eps0 )
        # Get the dielectric constant (E).
        E = ( 1 + A + 5*B + np.sqrt(9 + 2*A + 18*B + A**2 + 10*A*B + 9*B**2) )/( 4 - 4*B )

        # Calculates the set of Debye-Huckel coefficients, derivatives and bdot
        # at given temperature T and pressure P
        # Debye-Huckel Agammae, Aphi and Agamma10 parameters, Units are kg^0.5 mol^-0.5
        Agammae = np.sqrt(2*np.pi*NA*rho)*((e**2/( 4*np.pi*E*eps0*kB*TK ))**1.5)
        Agamma10 = Agammae/np.log(10)
        Ah = Agamma10
        Aphi = Agammae/3

        # Debye-Huckel B(gamma) Bh parameter, Units are kg^1/2 mol^-1/2 Angstrom^-1
        kB_erg = kB * 1e7  # converts Boltzmann's constant from J K^-1 to erg K^-1.
        rho = rho/1000     # converts rho from kg m^-3 to g cm^-3
        rhohat = rho

        Bh = 1.0e-08*np.sqrt((8*np.pi*NA*rho*((c*e)**2))/(1000*E*kB_erg*TK))

        # Calculates bdot  Ref: Helgeson H.C.,1969, American Journal of Science, Vol.267, pp:729-804
        b = [0.0374e0, 1.3569e-4, 2.6411e-7, -4.6103e-9]
        bdot = np.where(TC>=300, 0, b[0] + b[1]*(TC-25.0) + b[2]*(TC-25.0)**2 + b[3]*(TC-25.0)**3)

        # Partial derivative of the g factor with respect to density at constant temperature.
        dgdr_T = np.sum((Nh[:-1]*ih/rhocrm)*(delta**(ih - 1))*(tau**jh), 0) + \
            (Nh[11]/rhocrm)*((TK/228) - 1)**(-1.2)

        # Partial derivative of the g factor with respect to temperature at constant density.
        dgdT_r = np.sum(Nh[:-1]*(delta**ih)*jh*(tau**(jh - 1))*(-tau/TK), 0) + \
            Nh[11]*delta*(-1.2*((TK/228) - 1)**(-2.2) )/228

        # Partial derivative of A with respect to density.
        A1 = (A/rhom) + (A/g)*dgdr_T
        # Partial derivative of A with respect to temperature.
        A2 = -(A/TK) + (A/g)*dgdT_r
        # Partial derivative of B with respect to density.
        B1 = B/rhom
        C = 9 + 2*A + 18*B + A**2 + 10*A*B + 9*B**2

        # Partial derivative of E with respect to density at constant temperature.
        dEdr_T = (4*B1*E/(4 - 4*B)) + (A1 + 5*B1 + 0.5*C**(-0.5)*\
                                       (2*A1 + 18*B1 + 2*A*A1 + 10*(A1*B + A*B1) + 18*B*B1))/(4 - 4*B)

        # Partial derivative of E with respect to temperature at constant density.
        dEdT_r = (A2 + 0.5*C**(-0.5)*A2*(2 + 2*A + 10*B))/(4 - 4*B)

        # Partial derivative of density with respect to Pressure at constant temperature using the compressibility (ktx)
        drdP_T = rhom*ktx

        # Partial derivative of E with respect to Pressure at constant temperature
        dEdP_T = dEdr_T*drdP_T

        # Partial derivative of Pressure with respect to temperature at constant density
        #  using "ptx" which is the partial derivative of Pressure with respect to tau
        dPdT_r = -tau*ptx/TK

        # Partial derivative of E with respect to temperature at constant Pressure
        dEdT_P = dEdT_r - dEdr_T*dPdT_r*drdP_T

        # Debye-Huckel AV constant. Units are cm^3 kg^1/2 mol^-3/2
        # Multiply RT in kJ mol^-1 by 1000 to get R in cm^3 MPa mol^-1
        Adhv = 2*Aphi*1000*R*TK*( (3*dEdP_T/E) - ktx )

        # Debye-Huckel AH constant. Units are kJ kg^1/2 mol^-3/2.
        # AH/RT are kg^1/2 mol^-1/2
        Ahrt = -6*Aphi*TK*((dEdT_P/E) + (1/TK) + (avx/3))
        Adhh = R*TK*Ahrt
        # convert Adhh from kJ kg^1/2 mol^-3/2 to kcal kg^1/2 mol^-3/2
        Adhh = Adhh/J_to_cal

        # Get the Debye-Huckel BV constant. Units are cm^3 kg^1/2 mol^-3/2 Angstrom^-1
        # Multiply RT in kJ mol^-1 by 1000 to get R in cm^3 MPa mol^-1
        Bdhv = 2*np.log(10)*1000*R*TK*(Bh/2)*( ktx - dEdP_T/E )
        # convert Bdhv from cm^3 kg^1/2 mol^-3/2 Angstrom^-1 to cm^2 kg^1/2 mol^-3/2 10^-6
        Bdhv = 100*Bdhv

        # Get the Debye-Huckel BH constant. Units are kJ kg^1/2 mol^-3/2 Angstrom^-1
        # BH/RT parameter is expressed below as kg^1/2 mol^-1/2 Angstrom^-1.
        Bhrt = -2*np.log(10)*TK*(Bh/2)*((dEdT_P/E) + (1/TK) + avx )
        Bdhh = R*TK*Bhrt   #
        # convert Bdhh from kJ kg^1/2 mol^-3/2 Angstrom^-1 to cal kg^1/2 mol^-3/2 cm^-1  10^-9
        Bdhh = Bdhh*1000/J_to_cal*0.10
        # E, rhohat, Ah, Bh, bdot, Adhh, Adhv, Bdhh, Bdhv, dEdP_T, dEdT_P, dEdT_r, dEdr_T, drdP_T

        return E, rhohat, Ah, Bh, bdot, Adhh, Adhv, Bdhh, Bdhv, dEdP_T, dEdT_P

    def dielec_JN91(self, TC, rho):
        """
        This dielec_JN91 implementation employs the JN91 formulation to calculate the
        dielectric properties of water and steam, the Debye-Huckel "A" parameters and
        Debye-Huckel "B" parameters  and their derivatives

        Notes
        ------
        Temperature and Pressure input limits:
            * 0 ≤ TC ≤ 1000 and 0 ≤ P ≤ 5000

        Parameters
        ----------
           TC      : temperature [°C] \n
           rho     : density [kg/m3]

         Returns
        ----------
           E       : dielectric constant of water \n
           rhohat  : density [g/cm³] \n
           Ah      : Debye-Huckel "A" parameters [kg^1/2 mol^-1/2] \n
           Bh      : Debye-Huckel "B" parameters [kg^1/2 mol^-1/2 Angstrom^-1] \n
           bdot    : bdot at any given temperature T \n
           Adhh    : Debye-Huckel "A" parameters associated with apparent molar enthalpy \n
           Adhv    : Debye-Huckel "A" parameters associated with apparent molar volume \n
           Bdhh    : Debye-Huckel "B" parameters associated with apparent molar enthalpy \n
           Bdhv    : Debye-Huckel "B" parameters associated with apparent molar volume \n
           dEdP_T  : Partial derivative of dielectric constant with respect to pressure at constant temperature \n
           dEdT_P  : Partial derivative of dielectric constant with respect to temperature at constant pressure

         Usage
        ----------
           [E, rhohat, Ah, Bh, bdot, Adhh, Adhv, Bdhh, Bdhv, dEdP_T, dEdT_P] = dielec_JN91( TC, rho)

        References
        ----------
            (1) Johnson JW, Norton D (1991) Critical phenomena in hydrothermal systems: State, thermodynamic,
                electrostatic, and transport properties of H2O in the critical region. American Journal of Science 291:541-648
            (2) Helgeson H. C. and Kirkham D. H. (1974) Theoretical Prediction of the Thermodynamic
                Behavior of Aqueous Electrolytes at High Pressures and Temperatures: II.
                Debye-Huckel Parameters for Activity Coefficients and Relative Partial Molal Properties.
                Am. J. Sci. 274, 1199-1251.
        """

        if np.ndim(TC) == 0:
            TC = np.array(TC).ravel()
        else:
            TC = TC.ravel()
        if np.ndim(rho) == 0:
            rho = np.array(rho).ravel()
        else:
            rho = rho.ravel()

        TK = convert_temperature( TC, Out_Unit = 'K' )

        Tr = 298.15 #K
        mwH2O = 18.01528/1000  # kg/mol
        R = IAPWS95_COEFFS['R']/1000* mwH2O # kJ mol-1 K-1

        # Convert density to dimensionless g/cm3
        rhohat = rho/1000  #g/cm^3
        #  Dielectric constant of water calculation.  Johnson et al 1992- SUPCRT92
        ae = [0.1470333593*100, 0.2128462733*1000, -0.1154445173*1000,
              0.1955210915*100, -0.8330347980*100, 0.3213240048*100,
              -0.6694098645*10, -0.3786202045*100, 0.6887359646*100,
              -0.2729401652*100]
        # Dielectric constants from UEMATSU and FRANCK
        # ae = [7.62571, 2.44003E2, -1.40569E2, 2.77841E1, -9.62805E1,
        #       4.17909E1, -1.02099E1, -4.52059E1, 8.46395E1, -3.58644]

        That = TK/Tr
        k = [0]*5
        k[0] = [1]*len(That)
        k[1] = ae[0]/That
        k[2] = ae[1]/That + ae[2] + ae[3]*That
        k[3] = ae[4]/That + ae[5]*That + ae[6]*That**2
        k[4] = ae[7]*That**(-2) + ae[8]/That + ae[9]
        # E = ((k[0]*rhohat**0)+(k[1]*rhohat**1)+(k[2]*rhohat**2)+(k[3]*rhohat**3)+(k[4]*rhohat**4))
        E = np.zeros(np.size(TK))
        for a in range(len(E)):
            for b in range(5):
                E[a] = E[a] + k[b][a]*rhohat[a]**b

        Ar, Br = 1.8248292380e6, 50.291586490
        Ah = Ar*np.sqrt(rhohat)/(E*TK*np.sqrt(E*TK))
        Bh = Br*np.sqrt(rhohat)/np.sqrt(E*TK)
        b = [0.0374e0, 1.3569e-4, 2.6411e-7, -4.6103e-9]
        bdot = np.where(TC>=300, 0, b[0] + b[1]*(TC-25.0) + b[2]*(TC-25.0)**2 + b[3]*(TC-25.0)**3)

        water = iapws95(T = TC, rho = rho)
        ptx, ktx, avx = water.ptx, water.ktx, water.avx
        ptx = ptx*0.1  # convert to MPa units
        ktx = ktx/0.1  # convert to /MPa units
        Aphi = Ah*np.log(10)/3

        dkdT = [0]*5
        dkdT[0] = [0]*len(That)
        dkdT[1] = -ae[0]*Tr/TK**2
        dkdT[2] = -ae[1]*Tr/TK**2 + ae[3]/Tr
        dkdT[3] = -ae[4]*Tr/TK**2 + ae[5]/Tr + 2*ae[6]*TK/Tr**2
        dkdT[4] = -2*ae[7]*Tr**2/TK**3 - ae[8]*Tr/TK**2

        # Partial derivative of E with respect to Pressure at constant temperature
        dEdP_T = np.zeros(np.size(TK))
        for a in range(len(E)):
            for b in range(5):
                dEdP_T[a] = dEdP_T[a] + b*k[b][a]*rhohat[a]**b
        dEdP_T = dEdP_T*ktx

        # Partial derivative of E with respect to temperature at constant Pressure
        dEdT_P = np.zeros(np.size(TK))
        for a in range(len(E)):
            for b in range(5):
                dEdT_P[a] = dEdT_P[a] + rhohat[a]**b*(dkdT[b][a] - b*avx[a]*k[b][a])

        # Debye-Huckel AV constant. Units are cm^3 kg^1/2 mol^-3/2
        # Multiply RT in kJ mol^-1 by 1000 to get R in cm^3 MPa mol^-1
        Adhv = 2*Aphi*1000*R*TK*( (3*dEdP_T/E) - ktx )

        # Debye-Huckel AH constant. Units are kJ kg^1/2 mol^-3/2.
        # AH/RT are kg^1/2 mol^-1/2
        Ahrt = -6*Aphi*TK*((dEdT_P/E) + (1/TK) + (avx/3))
        Adhh = R*TK*Ahrt
        # convert Adhh from kJ kg^1/2 mol^-3/2 to kcal kg^1/2 mol^-3/2
        Adhh = Adhh/J_to_cal

        # Get the Debye-Huckel BV constant. Units are cm^3 kg^1/2 mol^-3/2 Angstrom^-1
        # Multiply RT in kJ mol^-1 by 1000 to get R in cm^3 MPa mol^-1
        Bdhv = 2*np.log(10)*1000*R*TK*(Bh/2)*( ktx - dEdP_T/E )
        # convert Bdhv from cm^3 kg^1/2 mol^-3/2 Angstrom^-1 to cm^2 kg^1/2 mol^-3/2 10^-6
        Bdhv = 100*Bdhv

        # Get the Debye-Huckel BH constant. Units are kJ kg^1/2 mol^-3/2 Angstrom^-1
        # BH/RT parameter is expressed below as kg^1/2 mol^-1/2 Angstrom^-1.
        Bhrt = -2*np.log(10)*TK*(Bh/2)*((dEdT_P/E) + (1/TK) + avx )
        Bdhh = R*TK*Bhrt   #
        # convert Bdhh from kJ kg^1/2 mol^-3/2 Angstrom^-1 to cal kg^1/2 mol^-3/2 cm^-1  10^-9
        Bdhh = Bdhh*1000/J_to_cal*0.10


        return E, rhohat, Ah, Bh, bdot, Adhh, Adhv, Bdhh, Bdhv, dEdP_T, dEdT_P

    def dielec_DEW(self):
        """
        This watercalc implementation employs the DEW formulation embedded in Sverjensky et al. (2014)
        to calculate the dielectric properties of water and steam, the Debye-Huckel "A" parameters and
        Debye-Huckel "B" parameters  and their derivatives. This function has been set up to use
        either Johnson and Norton (1991) or Fernandez et al. (1997) formulation below 5000 bar and
        Sverjensky et al. (2014) formulation above 5000 bar.

        Notes
        ------
        Temperature and Pressure input limits:
            * 100 ≤ TC ≤ 1200 and 1000 ≤ P ≤ 60000

        Parameters
        ----------
           TC      : temperature [°C] \n
           P       : pressure [bar]

         Returns
        ----------
           E       : dielectric constant of water \n
           rhohat  : density [g/cm³] \n
           Ah      : Debye-Huckel "A" parameters [kg^1/2 mol^-1/2] \n
           Bh      : Debye-Huckel "B" parameters [kg^1/2 mol^-1/2 Angstrom^-1] \n
           bdot    : bdot at any given temperature T \n
           Adhh    : Debye-Huckel "A" parameters associated with apparent molar enthalpy \n
           Adhv    : Debye-Huckel "A" parameters associated with apparent molar volume \n
           Bdhh    : Debye-Huckel "B" parameters associated with apparent molar enthalpy \n
           Bdhv    : Debye-Huckel "B" parameters associated with apparent molar volume \n
           dEdP_T  : Partial derivative of dielectric constant with respect to pressure at constant temperature \n
           dEdT_P  : Partial derivative of dielectric constant with respect to temperature at constant pressure

         Usage
        ----------
           [E, rhohat, Ah, Bh, bdot, Adhh, Adhv, Bdhh, Bdhv, dEdP_T, dEdT_P] = dielec_DEW()

        References
        ----------
            (1) D. A. Sverjensky, B. Harrison, and D. Azzolini, "Water in the deep Earth: the dielectric
                constant and the solubilities of quartz and corundum to 60 kb and 1200 °C," Geochimica et
                Cosmochimica Acta, vol. 129, pp. 125–145, 2014
            (2) Helgeson H. C. and Kirkham D. H. (1974) Theoretical Prediction of the Thermodynamic
                Behavior of Aqueous Electrolytes at High Pressures and Temperatures: II.
                Debye-Huckel Parameters for Activity Coefficients and Relative Partial Molal Properties.
                Am. J. Sci. 274, 1199-1251.
        """


        TC = self.TC; P = self.P; Dielec_DEWoutrange = self.Dielec_DEWoutrange
        TK = self.TK
        mwH2O = 18.01528/1000  # kg/mol
        R = IAPWS95_COEFFS['R']/1000* mwH2O # kJ mol-1 K-1

        def rho_dielectric(TC, P, Dielec_method = 'JN91'):

            deepearth = ZhangDuan(T = TC, P = P)
            #[rho, dGH2O, drdP_T, drdT_P] =
            drdT_P = deepearth.drhodT_P
            drdP_T = deepearth.drhodP_T/0.1 # g cm^-3 MPa^-1

            # Convert density to dimensionless g/cm3
            # rhohat = deepearth.rho/1000    # g/cm^3
            #  Power Function - Created by Dimitri Sverjensky and Brandon Harrison
            a = [-0.00157637700752506, 0.0681028783422197, 0.754875480393944]
            b = [-8.01665106535394E-05, -0.0687161761831994, 4.74797272182151]

            A = a[0] * TC + a[1] * np.sqrt(TC) + a[2]
            B = b[0] * TC + b[1] * np.sqrt(TC) + b[2]

            # Sverjensky et al. (2014) is used for P > 1000 bars and the JN91 or FGL97 Equation for
            # P ≤ 1000 bar to calculate the Dielectric Constant.
            E = np.zeros(len(TC)); dEdP_T = np.zeros(len(TC)); dEdT_P = np.zeros(len(TC));
            for i, j in enumerate(TC):
                if (P[i] < 1000) & (j < 100):
                    # deepearth_P = DEW(T = j, rho = deepearth.rho[i]).P.ravel()
                    if Dielec_method.upper() == 'FGL97':
                        [E[i], _, _, _, _, _, _, _, _, dEdP_T[i], dEdT_P[i]] = self.dielec_FGL97(j, deepearth.rho[i])
                    elif Dielec_method.upper() ==  'JN91':
                        [E[i], _, _, _, _, _, _, _, _, dEdP_T[i], dEdT_P[i]] = self.dielec_JN91(j, deepearth.rho[i])
                else:
                    E[i] = np.exp(B[i]) * deepearth.rhohat[i] ** A[i]
                    dEdr_T = A[i] * np.exp(B[i]) * deepearth.rhohat[i] ** (A[i] - 1)
                    # Partial derivative of E with respect to Pressure at constant temperature
                    dEdP_T[i] = dEdr_T*drdP_T[i]   # unit is /MPa

            return E, deepearth.rhohat, drdP_T, drdT_P, dEdP_T #.ravel()

        E, rhohat, drdP_T, drdT_P, dEdP_T = rho_dielectric(TC, P, Dielec_method = Dielec_DEWoutrange)

        Ar, Br = 1.8248292380e6, 50.291586490
        Ah = Ar*np.sqrt(rhohat)/(E*TK*np.sqrt(E*TK))
        Bh = Br*np.sqrt(rhohat)/np.sqrt(E*TK)
        b = [0.0374e0, 1.3569e-4, 2.6411e-7, -4.6103e-9]
        bdot = np.where(TC>=300, 0, b[0] + b[1]*(TC-25.0) + b[2]*(TC-25.0)**2 + b[3]*(TC-25.0)**3)

        Aphi = Ah*np.log(10)/3

        # Partial derivative of E with respect to temperature at constant Pressure
        f_ET = lambda x : rho_dielectric(x, P)[0]
        dEdT_P = derivative(f_ET, TC, h = 0.0001)

        # Debye-Huckel AV constant. Units are cm^3 kg^1/2 mol^-3/2
        # Multiply RT in kJ mol^-1 by 1000 to get R in cm^3 MPa mol^-1
        Adhv = 2*Aphi*1000*R*TK*( (3*dEdP_T/E) - drdP_T/rhohat )

        # Debye-Huckel AH constant. Units are kJ kg^1/2 mol^-3/2.
        # AH/RT are kg^1/2 mol^-1/2
        Ahrt = -6*Aphi*TK*((dEdT_P/E) + (1/TK) - (drdT_P/rhohat/3))
        Adhh = R*TK*Ahrt
        # convert Adhh from kJ kg^1/2 mol^-3/2 to kcal kg^1/2 mol^-3/2
        Adhh = Adhh/J_to_cal

        # Get the Debye-Huckel BV constant. Units are cm^3 kg^1/2 mol^-3/2 Angstrom^-1
        # Multiply RT in kJ mol^-1 by 1000 to get R in cm^3 MPa mol^-1
        Bdhv = 2*np.log(10)*1000*R*TK*(Bh/2)*( drdP_T/rhohat  - dEdP_T/E )
        # convert Bdhv from cm^3 kg^1/2 mol^-3/2 Angstrom^-1 to cm^2 kg^1/2 mol^-3/2 10^-6
        Bdhv = 100*Bdhv

        # Get the Debye-Huckel BH constant. Units are kJ kg^1/2 mol^-3/2 Angstrom^-1
        # BH/RT parameter is expressed below as kg^1/2 mol^-1/2 Angstrom^-1.
        Bhrt = -2*np.log(10)*TK*(Bh/2)*((dEdT_P/E) + (1/TK) + (drdT_P/rhohat) )
        Bdhh = R*TK*Bhrt   #
        # convert Bdhh from kJ kg^1/2 mol^-3/2 Angstrom^-1 to cal kg^1/2 mol^-3/2 cm^-1  10^-9
        Bdhh = Bdhh*1000/J_to_cal*0.10
        # E, rhohat, Ah, Bh, bdot, Adhh, Adhv, Bdhh, Bdhv, dEdP_T, dEdT_P, dEdT_r, dEdr_T, drdP_T

        return E, rhohat, Ah, Bh, bdot, Adhh, Adhv, Bdhh, Bdhv, dEdP_T, dEdT_P


def concentration_converter(val = 1.0, In_Unit='x_wt', Out_Unit='x_wt'):
    """This function converts concentration between several units like 
    wt fraction, mole fraction, molality, mol/kg solution and volume fraction
    Values must be in fraction except it is molality

    Parameters
    ----------
    val : float
        Values to convert
    In_Unit : String
        unit of input concentration
    Out_Unit : String
        expected output concentration

    Returns
    -------
    Out : float
        Converted values
    """
    #Accepted units for input and output are:
    phase_markers = ['x_wt', 'x_mol', 'x_vol', 'x_molal', 'x_mol_kgsol']

    Mw_H2O = 18.01528   # Molar mass of water (g/mol)
    Mw_NaCl = 58.44280  # Molar mass of NaCl (g/mol)
    rho_H2O = 1         # Density of NaCl (g/cm3)
    rho_NaCl = 2.16     # Density of water (g/cm3)
    if not (In_Unit in phase_markers and Out_Unit in phase_markers):
        return None

    if In_Unit == Out_Unit or val == 0.:
        return val

    if In_Unit != 'x_molal' and In_Unit != 'x_mol_kgsol' and val > 1.:
        print('x_convert func values above 1 (>100% NaCl)')
        return None
    if In_Unit == "x_wt":
        if Out_Unit == 'x_mol':
            return (val/Mw_NaCl) / (val/Mw_NaCl + (1 - val)/Mw_H2O)
        elif Out_Unit == 'x_vol':
            return (val/rho_NaCl) / (val/rho_NaCl + (1 - val)/rho_H2O)
        elif Out_Unit == 'x_mol_kgsol':
            return (val * 1000) / Mw_NaCl
        else:
            return (val * 1000) / ((1 - val) * Mw_NaCl)
    elif In_Unit == 'x_mol':
        if Out_Unit == 'x_wt':
            return val*Mw_NaCl/(val*Mw_NaCl+(1 - val)*Mw_H2O)
        elif Out_Unit == 'x_vol':
            return Mw_NaCl*val/rho_NaCl/(Mw_NaCl*val/rho_NaCl+(1 - val)*Mw_H2O/rho_H2O)
        elif Out_Unit == 'x_mol_kgsol':
            return val/(val * Mw_NaCl + (1 - val) * Mw_H2O) * 1000
        else:
            # x_tmp = val*Mw_NaCl/(val*Mw_NaCl+(1 - val)*Mw_H2O)
            return (val * 1000) / (Mw_H2O * (1 - val))
    elif In_Unit == 'x_vol':
        if Out_Unit == 'x_wt':
            return val*rho_NaCl/(val*rho_NaCl+(1 - val)*rho_H2O)
        elif Out_Unit == 'x_mol':
            return val*rho_NaCl/Mw_NaCl/(val*rho_NaCl/Mw_NaCl + (1 - val)*(rho_H2O/Mw_H2O))
        elif Out_Unit == 'x_mol_kgsol':
            return ((val * rho_NaCl / Mw_NaCl) / (val * rho_NaCl + (1 - val) * rho_H2O)) * 1000
        else:
            # x_tmp = val*rho_NaCl/(val*rho_NaCl+(1.-val)*rho_H2O)
            return (val * rho_NaCl / Mw_NaCl / ((1 - val)*rho_H2O)) * 1000
    elif In_Unit == 'x_mol_kgsol':
        if Out_Unit == 'x_wt':
            return (val * Mw_NaCl) / 1000
        elif Out_Unit == 'x_vol':
            x_tmp = val * Mw_NaCl
            return (x_tmp / rho_NaCl) / (x_tmp / rho_NaCl + (1000 - x_tmp) / rho_H2O)
        elif Out_Unit == 'x_mol':
            # x_tmp = val*MwNaCl/(1000)
            return val/(val + (1000 - val*Mw_NaCl)/Mw_H2O)
        else:
            return val/((1000 - val * Mw_NaCl)/1000)
    else:
        if Out_Unit == 'x_wt':
            return val*Mw_NaCl/(1000 + val*Mw_NaCl)
        elif Out_Unit == 'x_mol':
            return val/(val + (1000/Mw_H2O))
        elif Out_Unit == 'x_vol':
            return val * Mw_NaCl/rho_NaCl/(val * Mw_NaCl/rho_NaCl + 1000/rho_H2O)
        else:
            return val/(1 + (val * Mw_NaCl/1000))



class Driesner_NaCl:
    """
    Implementation of Driesner and Heinrich PTx Formulation for H2O-NaCl system

    Parameters
    ----------
        T : float
            Temperature [°C]  \n
        P : float
            Pressure [bar]  \n
        xNaCl : float
            mole fraction of NaCl in H2O [-]  \n

    Returns
    ----------
        The calculated instance has the following potential properties:  \n
        PVLH : float
            Pressure of vapor + liquid + halite coexistence [bar]  \n
        Pcrit : float
            Critical pressure (of a H2O–NaCl mixture) [bar]  \n
        Xcrit : float
            Critical Composition  [-]  \n
        xL_NaCl  : float
            Composition of halite-saturated liquid (halite liquidus) Hypothetical [-]  \n
        xV_NaCl  : float
            Composition of halite-saturated vapor [-] \n
        xVL_Liq  : float
            Composition of liquid at vapor + liquid coexistence [-] \n
        xVL_Vap  : float
            Composition of vapor at vapor+liquid coexistence [-]  \n
        rho  : float
            Liquid NaCl density [kg/m3]  \n
        vm  : float
            molar volume [mol/m3]  \n
        TstarH  : float
            Scaled temperature for enthalpy correlation [°C]  \n
        H  : float
            Specific enthalpy of an H2O–NaCl solution [J/kg]  \n
        Cp  : float
            Isobaric heat capacity [J/kg/K]  \n
        mu  : float
            viscosity [Pa-s]  \n
            
    Usage:
    ----------
        The general usage of Driesner_NaCl is as follows:  \n
        (1) For water-NaCl properties at any Temperature and Pressure:  \n
            water_salt = Driesner_NaCl(T = T, P = P),   \n
            where T is temperature in celsius and P is pressure in bar
    Examples
    --------
    >>> water_salt = Driesner_NaCl(T = 400., P = 150)
    >>> water_salt.PVLH, water_salt.xL_NaCl, water_salt.xV_NaCl, water_salt.xVL_Liq, water_salt.xVL_Vap, water_salt.Xcrit
        176.12604181993797,
         0.21548565081529097,
         1.1606891909548725e-05,
         0.27785803505887324,
         1.1606891909548725e-05,
         0.006832050956381021

    >>> water_salt = Driesner_NaCl(T = 400., P = 150, xNaCl = 0.00919)
    >>> water_salt.PVLH, water_salt.xL_NaCl, water_salt.xV_NaCl, water_salt.xVL_Liq, water_salt.xVL_Vap, water_salt.rho, water_salt.vm, water_salt.H, water_salt.mu, water_salt.Cp
        (176.12604181993797,
         0.21548565081529097,
         1.1606891909548725e-05,
         0.27785803505887324,
         1.1606891909548725e-05,
         0.06932873574838519,
         265.2138005082347,
         2934.6231778877977,
         2.4596312351131325e-05,
         4394.068874696437)
        
    References
    ----------
        (1) Driesner, T, and Heinrich, C. A. (2007). The system H2O–NaCl. Part I: Correlation formulae for phase relations in 
            temperature–pressure–composition space from 0 to 1000 C, 0 to 5000 bar, and 0 to 1 XNaCl. Geochimica et Cosmochimica Acta. 71(20), 4880-4901.
            https://doi.org/10.1016/j.gca.2006.01.033
        (2) Driesner, T. (2007). "The system H2O-NaCl. II. Correlations for molar volume, enthalpy, and isobaric heat capacity from 0 to 1000 °C, 1 to 5000 bar,
        #     and 0 to 1 X-NaCl." Geochimica et Cosmochimica Acta 71(20): 4902-4919.

    """

    kwargs = {"T": None,
              "P": None,
              "xNaCl": None
              }
    def __init__(self, **kwargs):
        self.kwargs = Driesner_NaCl.kwargs.copy()
        self.__calc__(**kwargs)

    def __calc__(self, **kwargs):
        self.kwargs.update(kwargs)
        """initialization """
        self.TC = self.kwargs["T"]
        self.P = self.kwargs["P"]
        self.xNaCl = self.kwargs["xNaCl"]
        self.Pc = 220.54915  #  220.54915  # bars
        self.Tc = 373.976  # 373.946 # C

        """Check if inputs are enough to define state"""
        if self.TC and self.P is None and self.xNaCl is None:
            self.mode = "T"
        elif self.TC and self.P and self.xNaCl is None:
            self.mode = "T_P"
        else:
            self.mode = "T_P_x"
            
        if self.mode == "T":
            Driesner_calc = self.Driesner_NaCl(self.TC, self.Pc)
            self.PVLH, self.Pcrit, self.Xcrit = Driesner_calc['PVLH'], Driesner_calc['Pcrt'], Driesner_calc['Xcrt']
        elif self.mode == "T_P" or self.mode == "T_P_x":
            if self.mode == "T_P_x":
                Driesner_calc = self.Driesner_NaClII(self.TC, self.P, self.xNaCl)
                self.vm, self.rho, self.TstarH = Driesner_calc['vm'], Driesner_calc['rho'], Driesner_calc['Tref']#, Driesner_calc['q2']
                Driesner_calc = self.enthalpy_mu_heatcap(self.TC, self.P, self.xNaCl)
                self.H, self.mu, self.Cp = Driesner_calc[0], Driesner_calc[1], Driesner_calc[-1]
            Driesner_calc = self.Driesner_NaCl(self.TC, self.P)
            self.PVLH, self.xL_NaCl, self.xV_NaCl = Driesner_calc['PVLH'], Driesner_calc['xL_NaCl'], Driesner_calc['xV_NaCl']
            self.xVL_Liq, self.xVL_Vap = Driesner_calc['xVL_Liq'], Driesner_calc['xVL_Vap']
            self.Pcrit, self.Xcrit = Driesner_calc['Pcrt'], Driesner_calc['Xcrt']
    
    def Driesner_NaCl(self, T, P):
        # (Driesner and Heinrich, 2007).
        Ttriple_NaCl = 800.7 # C
        Ptriple_NaCl = 5e-4  # bar
        alpha = 2.4726e-2
        bsubl = 1.18061e4
        bboil = 0.941812e4
    
        # Eq. (1): NaCl melting curve - melting pressure
        Thm_func = lambda P: (P - Ptriple_NaCl)*alpha + Ttriple_NaCl
    
        # Eq. (2): NaCl sublimation and boiling curve - vapor pressure
        bfunc = lambda T:  np.where(T < Ttriple_NaCl, bsubl,  bboil)
        PNaCl_func = lambda T, b: 10**(log10(Ptriple_NaCl) + b*((Ttriple_NaCl + 273.15)**-1 - (T + 273.15)**-1))
    
    
        # Electronic Annex EA-2: The critical curve, Eqs. (5b,c, 7a,b).
        # NBS/NRC-84 or IAPWS-84
        Pc = 220.54915  #  220.54915  # bars
        Tc = 373.976  # 373.946 # C
        # IAPWS-95
        # Pc = 220.54915  # bars
        # Tc = 373.946 # C
        cn = np.array([-2.36, 1.28534e-1, -2.3707e-2, 3.20089e-3, -1.38917e-4, 1.02789e-7,
                       -4.8376e-11, 2.36, -1.31417e-2, 2.98491e-3, -1.30114e-4, 0, 0, -4.88336e-4])
        di = np.array([8.00000e-05, 1.00000e-05, -1.37125e-07, 9.46822e-10, -3.50549e-12,
                       6.57369e-15, -4.89423e-18, 7.77761e-2, 2.7042e-4, -4.244821e-7, 2.580872e-10])
        cnA = np.array([1, 1.5, 2, 2.5, 3, 4, 5, 1, 2, 2.5, 3, 12, 13, 14])
        Pfunc_below_Tcrt = lambda x: Pc + np.sum(cn[:7]*(Tc - x)**cnA[:7])
        Pfunc_above_Tcrt = lambda x: Pc + np.sum(cn[7:11]*(x - Tc)**cnA[7:11])
        Pfunc_above_500 = lambda x: np.sum(cn[11:]*(x - 500)**(cnA[11:] - 12))
        cn[11] = Pfunc_above_Tcrt(500)
        cn[12] = derivative(Pfunc_above_Tcrt, 500, h = 0.0001)
        #cn[12] = Pfunc_above_Tcrt(500)
        Xfunc_below_600 = lambda x: np.sum(di[:7]*(x - Tc)**np.arange(8)[1:])
        Xfunc_above_600 = lambda x: np.sum(di[7:]*(x - 600)**(np.arange(7, len(di)) - 7))
        Pcrt_func = lambda x: Pfunc_below_Tcrt(x) if (x < Tc) else Pfunc_above_500(x) if (x > 500) else Pfunc_above_Tcrt(x)
        Xcrt_func = lambda x: 0 if x < Tc else Xfunc_below_600(x) if x < 600 else Xfunc_above_600(x)
    
    
        # Electronic Annex EA-3: The halite liquidus - L + H , Eq. (8),
        # for isobars from 500 to 5000 bar in 500 bar intervals, and from 10 C to the melting temperature of NaCl.
        eifunc = lambda P: [0.0989944 + 3.30796e-6*P - 4.71759e-10*P**2,
                             0.00947257 - 8.66460e-6*P + 1.69417e-9*P**2,
                             0.610863 - 1.51716e-5*P + 1.19290e-8*P**2,
                             -1.64994 + 2.03441e-4*P - 6.46015e-8*P**2,
                             3.36474 - 1.54023e-4*P + 8.17048e-8*P**2]
        ei_func = lambda P: np.array(eifunc(P) + [1.0 - eifunc(P)[0] - eifunc(P)[1] - \
                                                  eifunc(P)[2] - eifunc(P)[3] - eifunc(P)[4]])
        
        xL_NaClSat_func = lambda T, P: np.sum(ei_func(P)*(T/Thm_func(P))**np.arange(len(ei_func(P)))) \
            if np.sum(ei_func(P)*(T/Thm_func(P))**np.arange(len(ei_func(P)))) <= 1 else 1
    
    
        # Electronic Annex EA-4: Halite saturated vapor composition - V + H coexistence, Eq. (9),
        # for isobars from 50 to 350 bar in 50 bar intervals.
        k = [-0.235694, -0.188838, 0.004, 0.0552466, 0.66918, 396.848, 45.0, -3.2719e-7, 141.699,
             -0.292631, -0.00139991, 1.95965e-6, -7.3653e-10, 0.904411, 0.000769766, -1.18658e-6]
        j_func = lambda T: np.array([k[0] + k[1]*exp(-k[2]*T),
                                     k[4] + (k[3] - k[4])/(1 + exp((T - k[5])/k[6])) + k[7]*(T + k[8])**2,
                                     k[9] + k[10]*T + k[11]*T**2 + k[12]*T**3,
                                     k[13] + k[14]*T + k[15]*T**2])
        P_bar_func = lambda T, P: (P - PNaCl_func(T, bfunc(T)))/(Pcrt_func(T) - PNaCl_func(T, bfunc(T)))
        logKbar_func = lambda T, P: (1 + j_func(T)[0]*(1 - P_bar_func(T, P))**j_func(T)[1] +  \
                                     j_func(T)[2]*(1 - P_bar_func(T, P)) + j_func(T)[3]*(1 - P_bar_func(T, P))**2 - \
                                         (1 + j_func(T)[0] + j_func(T)[2] + j_func(T)[3])*(1 - P_bar_func(T, P))**3)
        
        logKprime_func = lambda T, P: (log10(xL_NaClSat_func(T, PNaCl_func(T, bfunc(T)))) + \
                                       logKbar_func(T, P)*(log10(PNaCl_func(T, bfunc(T))/Pcrt_func(T)) - \
                                                           log10(xL_NaClSat_func(T, PNaCl_func(T, bfunc(T)))) ) )
        
        logKprime_func = lambda T, P: (log10(xL_NaClSat_func(T, PNaCl_func(T, bfunc(T)) )) + \
                                       logKbar_func(T, P)*(log10(PNaCl_func(T, bfunc(T))/Pcrt_func(T)) - \
                                                           log10(xL_NaClSat_func(T, PNaCl_func(T, bfunc(T)) )) ) )
        
        xV_NaClSat_func = lambda T, P: xL_NaClSat_func(T, P)/10**(logKprime_func(T, P) - log10(PNaCl_func(T, bfunc(T))/P ))
        
        
        # Electronic Annex EA-5: The V+L+H coexistence surface, Eq. (10) combined with Eqs. (8, 9).
        f = [4.64e-3, 5.0e-7, 1.69078e1, -2.69148e2, 7.63204e3, -4.95636e4, 2.33119e5, -5.13556e5, 5.49708e5, -2.84628e5, 0]
        f[10] = Ptriple_NaCl - (f[0] + f[1] + f[2] + f[3] + f[4] + f[5] + f[6] + f[7] + f[8] + f[9])
        PVLH_func = lambda T: np.sum(f*(T / Ttriple_NaCl)**np.arange(len(f)))
    
    
        # Electronic Annex EA-5: Isotherms of the V+L coexistence surface, Eqs. (11, 12-17).
        # the pressure limit ranges from pressure at V+L+H coexistence (Eq. (10)), and at the boiling pressure of
        # water (if the temperature is smaller than the critical temperature of water) or at the critical pressure
        # (if the temperature is higher that the critical temperature of water).
        
        h = [0, 1.68486e-3, 2.19379e-4, 4.3858e2, 1.84508e1, -5.6765e-10,
             6.73704e-6, 1.44951e-7, 3.84904e2, 7.07477e0, 6.06896e-5, 7.62859e-3]
        g0var_func = lambda T, P: [PVLH_func(T) if T < Ttriple_NaCl else PNaCl_func(T, bfunc(T)),
                                   xL_NaClSat_func(T, P) if T < Ttriple_NaCl else 1,
                                   iapws95(T = T).P if T < Tc else Pc]
        g_func = lambda T, P: np.array([0,
                                        h[2] + ((h[1] - h[2])/(1 + np.exp((T - h[3])/h[4]))) + h[5]*T**2,
                                        h[7] + ((h[6] - h[7])/(1 + np.exp((T - h[8])/h[9]))) + h[10]*np.exp(-h[11]*T)])
        
        g0_func = lambda T, P, *x: ((x[1] + g_func(T, P)[1] * (x[0] - x[2]) + \
                                     g_func(T, P)[2] * ((Pcrt_func(T) - x[2])**2 - \
                                                        (Pcrt_func(T) - x[0])**2)) / \
                                    ((Pcrt_func(T) - x[0])**0.5 - (Pcrt_func(T) - x[2])**0.5)) \
            if T <= Tc else ((x[1] - Xcrt_func(T) - g_func(T, P)[1] * (Pcrt_func(T) - x[0]) - \
                              g_func(T, P)[2] * (Pcrt_func(T) - x[0])**2) / (Pcrt_func(T) - x[0])**0.5)
        
        P_Pcrt_func =  lambda T, P:  Pcrt_func(T) if Pcrt_func(T) < P else P
        
        
        xVL_LiqNaCl_func = lambda T, P:  (g0_func(T, P, *g0var_func(T, P))*((Pcrt_func(T) - P_Pcrt_func(T, P))**0.5 - \
                                                                            (Pcrt_func(T) - g0var_func(T, P)[2])**0.5) - \
            g_func(T, P)[1]*((Pcrt_func(T) - g0var_func(T, P)[2]) - (Pcrt_func(T) - P_Pcrt_func(T, P))) - \
                g_func(T, P)[2]*((Pcrt_func(T) - g0var_func(T, P)[2])**2 - (Pcrt_func(T) - P_Pcrt_func(T, P)) ** 2) ) \
            if T <= Tc else (Xcrt_func(T) + g0_func(T, P, *g0var_func(T, P))*(Pcrt_func(T) - P_Pcrt_func(T, P))**0.5 + \
                                                             g_func(T, P)[1]*(Pcrt_func(T) - P_Pcrt_func(T, P)) + \
                                                                 g_func(T, P)[2]*(Pcrt_func(T) - P_Pcrt_func(T, P))**2 )
        
        
        xVL_VapNaCl_func = lambda T, P: (xVL_LiqNaCl_func(T, P)/10**(logKprime_func(T, P) - \
                                                                     log10(PNaCl_func(T, bfunc(T))/P ))) \
            if P > PVLH_func(T) else (xL_NaClSat_func(T, P)/10**(logKprime_func(T, P) - \
                                                                 log10(PNaCl_func(T, bfunc(T))/P )))
        
        res = {'PVLH': PVLH_func(T),
               'Pcrt': Pcrt_func(T),
               'Xcrt': Xcrt_func(T),
               'xL_NaCl': xL_NaClSat_func(T, P), 
               'xV_NaCl': xV_NaClSat_func(T, P), 
               'xVL_Liq': xVL_LiqNaCl_func(T, P), 
               'xVL_Vap': xVL_VapNaCl_func(T, P)}
        
        return res


    def Driesner_NaClII(self, T, P, xNaCl):

        calc = self.Driesner_NaCl(T, P)
        # self.PVLH, self.xL_NaCl, self.xV_NaCl = driesnier_calc['PVLH'], driesnier_calc['xL_NaCl'], driesnier_calc['xV_NaCl']
        # self.xVL_Liq, self.xVL_Vap = driesnier_calc['xVL_Liq'], driesnier_calc['xVL_Vap']
        mwH2O = 18.015268
        mwNaCl = 58.4428
        n11 = lambda P : -54.2958 - 45.7623 * exp(-9.44785e-4 * P)
        n21 = lambda P : -2.6142 - 0.000239092 * P
        n22 = lambda P : 0.0356828 + 4.37235 * 10**-6 * P + 2.0566e-9 * P**2
        n300 = lambda P : 7.60664e6 / ((P + 472.051)**2)
        n301 = lambda P : -50 - 86.1446 * exp(-6.21128e-4 * P)
        n302 = lambda P : 294.318 * exp(-5.66735e-3 * P)
        n310 = lambda P : -0.0732761 * exp(-2.3772 * 10**-3 * P) - 5.2948e-5 * P
        n311 = lambda P : -47.2747 + 24.3653 * exp(-1.25533e-3 * P)
        n312 = lambda P : -0.278529 - 0.00081381 * P
        n30 = lambda P, xNaCl : n300(P) * (exp(n301(P) * xNaCl) - 1) + n302(P) * xNaCl
        n31 = lambda P, xNaCl : n310(P) * exp(n311(P) * xNaCl) + n312(P) * xNaCl
        
        n10 = lambda P : 330.47 + 0.942876 * P**0.5 + 0.0817193 * P - 2.47556e-8 * P**2 + 3.45052e-10 * P**3
        n12 = lambda P : -n11(P) - n10(P)
        n20 = lambda P : 1 - n21(P) * n22(P)**0.5
        n23 = lambda P : -0.0370751 + 0.00237723 * P**0.5 + 5.42049e-5 * P + 5.84709e-9 * P**2 - \
            5.99373e-13 * P**3 - n20(P) - n21(P) * (1 + n22(P))**0.5
        n1 = lambda P, xNaCl : n10(P) + n11(P) * (1 - xNaCl) + n12(P) * (1 - xNaCl)**2
        n2 = lambda P, xNaCl : n20(P) + n21(P) * (xNaCl + n22(P))**0.5 + n23(P) * xNaCl
        d = lambda T, P, xNaCl : n30(P, xNaCl) * exp(n31(P, xNaCl) * T)
        Tref_vmH2ONaCl = lambda T, P, xNaCl : n1(P, xNaCl) + n2(P, xNaCl) * T + d(T, P, xNaCl)
    
        #function for low P region, eq. 17 from Driesner 2007
        #used for extrapolation of the molar volume
        def vm_extrapolation(T, P, xNaCl):
            v = calc['xL_NaCl'] 
            if T <= 373.946:
                pTmp = iapws95(T = T).P
        
            if xNaCl == 0:
                return 0
            elif T <= 200 and P < pTmp:
                t_Ref = Tref_vmH2ONaCl(T, P, xNaCl)
                vm_Sat = mwH2O / iapws95(T = T).rhosl * 1000
                vm_Wat = mwH2O / iapws95(T = T, P = P).rho * 1000
        
                if vm_Sat < vm_Wat:
                    o2 = 2.0125e-7 + 3.29977e-9 * exp(-4.31279 * log10(P)) - 1.17748e-7 * log10(P) + 7.58009e-8 * (log10(P))**2
                    vm1 = mwH2O / iapws95(T = T).rhosl * 1000
                    vm2 = mwH2O / iapws95(T = T - 0.01).rhosl * 1000
                    o1 = (vm1 - vm2) / 0.01 - 3 * o2 * t_Ref**2
                    o0 = vm1 - o1 * t_Ref - o2 * t_Ref**3
                    return o0 + o2 * t_Ref**3 + o1 * t_Ref
        
            elif T >= 600 and P <= 350:
                v = calc['xVL_Liq']
                if math.floor(xNaCl*1e6)/1e6 >= math.floor(v*1e6)/1e6:
        
                    #local function to estimate density of vapor phase neccesery for V_extrapol funtion
                    vmextreme_water = lambda T, P, x : mwH2O / iapws95(T = Tref_vmH2ONaCl(x, T, P), P = P).rho
                    rhoNaCl_Vextreme = lambda T, P, x : (mwH2O * (1 - x) + mwNaCl * x) / vmextreme_water(T, P, x)* 1000.0
        
                    vm1000 = (mwH2O * (1 - xNaCl) + mwNaCl * xNaCl) / rhoNaCl_Vextreme(T, 1000, xNaCl) * 1000
                    vm1 = (mwH2O * (1 - xNaCl) + mwNaCl * xNaCl) / rhoNaCl_Vextreme(T, 390.147, xNaCl) * 1000
                    vm2 = (mwH2O * (1 - xNaCl) + mwNaCl * xNaCl) / rhoNaCl_Vextreme(T, 390.137, xNaCl) * 1000
        
                    dVdP390 = (vm1 - vm2) * 1e-2
                    o4 = (vm1 - vm1000 + dVdP390 * 1609.853) / (log(1390.147 / 2000) - 2390.147 / 1390.147)
                    o3 = vm1 - o4 * log(1390.147) - 390.147 * dVdP390 + 390.147 / 1390.147 * o4
                    o5 = dVdP390 - o4 / (1390.147)
        
                    return o3 + o4 * log(P + 1000) + o5 * P
                else:
                    return 0
            else:
                return 0
    
        vm_H2ONaCl = lambda T, P, xNaCl : (mwH2O / (
            iapws95(T = Tref_vmH2ONaCl(T, P, xNaCl), P = P).rho*0.001)) \
            if vm_extrapolation(T, P, xNaCl) == 0 else vm_extrapolation(T, P, xNaCl)  #cm3/mol
    
        rho_H2ONaCl = lambda T, P, xNaCl : (mwH2O * (1 - xNaCl) + mwNaCl * xNaCl) / vm_H2ONaCl(T, P, xNaCl)
        
        def Tref_Enthalpy(xNaCl, T, P): #Th* for enthalpy
        
            xH2O = 1 - xNaCl
            q11 = -32.1724 + 0.0621255 * P
            q21 = -1.69513 - 4.52781e-4 * P - 6.04279e-8 * P**2
            q22 = 0.0612567 + 1.88082e-5 * P
            q10 = 47.9048 - 9.36994e-3 * P + 6.51059e-6 * P**2
            q_twoNaCl = 0.241022 + 3.45087e-5 * P - 4.28356e-9 * P**2
            q12 = -q11 - q10
            q20 = 1 - q21 * q22**0.5
            q23 = q_twoNaCl - q20 - q21 * (1 + q22)**0.5
        
            q1 = q10 + q11 * xH2O + q12 * xH2O**2
            q2 = q20 + q21 * (xNaCl + q22)**0.5 + q23 * xNaCl
        
            tStar = q1 + q2 * T + 273.15
        
            return tStar, q2
        
        res = {'vm': vm_H2ONaCl(T, P, xNaCl)[0],
               'rho': rho_H2ONaCl(T, P, xNaCl)[0],
               'Tref': Tref_Enthalpy(xNaCl, T, P)[0],
               'q2': Tref_Enthalpy(xNaCl, T, P)[-1]
               }
        return res
        
    def enthalpy_mu_heatcap(self, T, P, xNaCl):
        """ Enthalpy in J/g, viscosity in Pas and Cp in Joules per kilogram Kelvin   """
        calc = self.Driesner_NaClII(T, P, xNaCl)
        tStar, q2 = calc['Tref'], calc['q2']
        tStar = tStar - 273.15
        prop_H2O = iapws95(T = tStar, P = P, Out_Unit = 'kilogram', FullEOSppt = True)
        return prop_H2O.H[0], prop_H2O.mu[0], prop_H2O.Cp[0]*q2*1000  #/(1 + xNaCl)

