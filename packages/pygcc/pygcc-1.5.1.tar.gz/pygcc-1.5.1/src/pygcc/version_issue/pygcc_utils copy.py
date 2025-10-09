#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 16:02:22 2021

@author: Adedapo Awolayo and Ben Tutolo, University of Calgary

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

"""
from .read_db import db_reader, dbaccess_modify
from .water_eos import iapws95, ZhangDuan, water_dielec, readIAPWS95data, convert_temperature
from .water_eos import  Driesner_NaCl, concentration_converter
from .species_eos import heatcap, supcrtaq
from .solid_solution import solidsolution_thermo
from .clay_thermocalc import calclogKclays
import warnings
import re
import os
import json
import numpy as np
import pandas as pd
import time
from scipy.optimize import fsolve, curve_fit
from scipy.linalg import lu_factor, lu_solve
from scipy.interpolate import splev, splrep, Rbf
import inspect, itertools
import math
from fractions import Fraction
from collections import OrderedDict
np.random.seed(4321)
warnings.filterwarnings("ignore", message="divide by zero encountered")
warnings.filterwarnings("ignore", message="invalid value encountered")

eps = 2.220446049250313e-16
J_to_cal = 4.184
IAPWS95_COEFFS = readIAPWS95data()

def calc_elem_count_molewt(formula, **kwargs):
    """
    This function calculates the molecular mass and the elemental composition of a substance given
    by its chemical formula. This is modified from https://github.com/cgohlke/molmass/blob/master/molmass/molmass.py

    Parameters
    ----------
        formula : string
            chemical formula
        Elementdic : dict
            dictionary, containing the atomic mass of element database

    Returns
    ----------
        elements : dict
            dictionary of elemental composition and their respective number of atoms
        molewt : float
            Calculated Molecular Weights [g/mol]

    Usage:
    ----------
    [elements, molewt] = calc_elem_count_molewt(formula)
        Examples of valid formulas are "H2O", "[2H]2O", "CH3COOH", "EtOH", "CuSO4:5H2O", "(COOH)2",
        "AgCuRu4(H)2[CO]12{PPh3}2", "CGCGAATTCGCG", and, "MDRGEQGLLK" .

    Examples
    --------
    >>> elements, molewt = calc_elem_count_molewt("CuSO4:5H2O")
    >>> elements, molewt
        {'O': 9.0, 'H': 10.0, 'S': 1, 'Cu': 1}, 249.6773
    """
    kwargs = dict({"Elementdic": None   }, **kwargs)
    Elementdic = kwargs['Elementdic']

    if Elementdic is None:
        periodic_table = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           'PeriodicTableJSON.json'), encoding='utf8')
        data = json.load(periodic_table)
        Elementdic = {data['elements'][x]['symbol'] : pd.DataFrame([data['elements'][x]['name'],
                                                                    data['elements'][x]['atomic_mass']],
                                                                   index = ['name', 'mass']).T
                   for x in range(len(data['elements']))}
        periodic_table.close()

    validchars = set('([{<123456789ABCDEFGHIKLMNOPRSTUVWXYZ')
    validchars |= set(']})>0abcdefghiklmnoprstuy')

    elements = {}
    ele = ''  # parsed element
    num = 0  # number
    level = 0  # parenthesis level
    counts = [1]  # parenthesis level multiplication
    i = len(formula)
    while i:
        i -= 1
        char = formula[i]

        if char in '([{<':
            level -= 1
        elif char in ')]}>':
            if num == 0:
                num = 1
            level += 1
            if level > len(counts) - 1:
                counts.append(0)
            counts[level] = num * counts[level - 1]
            num = 0
        elif char.isdigit():
            j = i
            while i and (formula[i - 1].isdigit() or formula[i - 1] == '.'):
                i -= 1
            num = float(formula[i : j + 1])
        elif char.islower():
            ele = char
        elif char.isupper():
            ele = char + ele
            if num == 0:
                num = 1
            j = i
            number = num * counts[level]
            if ele in elements.keys():
                elements[ele] = number + elements[ele]
            else:
                elements[ele] = number
            ele = ''
            num = 0
        elif char == ':':
            if num == 0:
                num = 1
            for k in elements.keys():
                elements[k] = elements[k]*num

    molewt = 0
    for symbol in elements:
        molewt += Elementdic[symbol].mass[0] * elements[symbol]

    return elements, molewt


def importconfile(filename, *Rows):
    """
    This function imports numeric data from a text file as column vectors.
       [Var1, Var2] = importconfile(filename) Reads data from text file
       filename for the default selection.

       [Var1, Var2] = importconfile(filename, StartRow, EndRow) Reads data
       from rows StartRow through EndRow of text file filename.

     Example:
       [Var1, Var2] = importconfile('100bar.con', 6, 13);
    """

    # %% Initialize variables.
    if (len(Rows) == 0):
        startRow = 5
        endRow = np.inf
    else:
        startRow, endRow = Rows

    # %% Open the text file.
    fileID = open(filename,'r');

    df=fileID.readlines()
    Var1 = []
    Var2 = []
    for block in range(startRow,len(df)):
        if not df[block].startswith('\n'):
            dataArray = df[block].split()
            Var1.append(float(dataArray[0]))
            Var2.append(float(dataArray[1]))

    Var1 = np.asarray(Var1)
    Var2 = np.asarray(Var2)
    # %% Close the text file.
    fileID.close()
    # %%

    return Var1, Var2

def var_name(var):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    print(str([k for k, v in callers_local_vars if v is var][0])+': '+str(var))

def feval(funcName, *args):
    return eval(funcName)(*args)

def roundup_tenth(x):
    return int(math.ceil(x / 10.0)) * 10

def roundup_hundredth(x):
    return int(math.ceil(x / 100)) * 100

def read_specific_lines(file, lines_to_read):
   lines = set(lines_to_read)
   last = max(lines)
   for n, line in enumerate(file):
      if n + 1 in lines:
          yield line
      if n + 1 > last:
          return
      if not line:
          continue

def denormalize_phreeqc_species_charge(j):
    """
    Helper function to reverse the normalization of PHREEQC species charge notation.
    - Convert expanded charges back into compact notation (e.g., 'Ca++' -> 'Ca+2').
    - Remove '(aq)' from neutral species.
    - Keep integers or floats unchanged.
    
    Examples:
    'Ca++'     -> 'Ca+2'
    'Fe---'    -> 'Fe-3'
    'H2O(aq)'  -> 'H2O'
    'CH4(aq)'  -> 'CH4'
    '-1'       -> '-1'
    '3.5'      -> '3.5'
    """
    # If it's just an integer or float, return as is
    try:
        float(j)
        return j
    except ValueError:
        pass

    # Remove (aq) if present
    if j.endswith("(aq)"):
        j = j[:-4]

    # Collapse repeated charges back into +n / -n
    def repl(match):
        sign = match.group(1)[0]  # '+' or '-'
        num = len(match.group(1)) # number of signs
        return f"{sign}{num}"

    out = re.sub(r'([+-]{2,})', repl, j)  # match ++, ---, etc.

    return out

def normalize_species_charges(species):

    # 'Ca++' -> 'Ca+2', 'Fe---' -> 'Fe-3'
    species = re.sub(r'^([A-Za-z0-9()]+)([+-]+)$',
                    lambda m: m.group(1) + m.group(2)[0] + str(len(m.group(2))),
                    species)
    
    # 'Ca(+2)' -> 'Ca+2', 'Fe(-3)' -> 'Fe-3'
    species = re.sub(r'\(([\+\-]\d+)\)$', r'\1', species)

    # 'SrCl(+)' -> 'SrCl+', 'HNiO2(-)' -> 'HNiO2-'
    species = re.sub(r'\(([\+\-])\)$', r'\1', species)

    # 'NaCl(0)' -> 'NaCl'
    species = re.sub(r'\(0\)$', '', species)

    # 'CdOH+1' -> 'CdOH+'
    species = re.sub(r'\+1$', '+', species)
    species = re.sub(r'-1$', '-', species)

    return species


def normalize_phreeqc_species_charge(j):
    """
    Helper function to normalize PHREEQC species charge notation.
    - Replace charge notation like +2, -3, +4 etc. with expanded '+' or '-' symbols.
    - Skip cases where the entire string is just an integer (e.g., '1', '-1', '+2').
    - If the species has no explicit charge, append '(aq)'.
    
    Examples:
    'Ca+2'  -> 'Ca++'
    'Fe-3'  -> 'Fe---'
    '-1'    -> '-1'
    'H2O'   -> 'H2O(aq)'
    'CH4'   -> 'CH4(aq)'
    """
    def repl(match):
        sign, num = match.groups()
        return sign * int(num)

    # If it's just an integer or float, return as is
    try:
        float(j)
        return j
    except ValueError:
        pass

    # Expand charges like +2 -> ++, -3 -> ---
    out = re.sub(r'([+-])(\d+)', repl, j)

    # Append (aq) if no charge, except for "" and "H2O"
    if out not in ("", "H2O") and not re.search(r'[+-]', out):
        out += "(aq)"

    return out


def contains_missing_species(line, missing_spx):
    # Helper function to check if a line contains missing species
    parts = line.replace("=", " ").replace("+", " ").split()
    for p in parts:
        if p.strip() in missing_spx:
            return True
    return False


def build_side_regex(side):
    """
    Build a regex to match one side of a chemical reaction.
    - Optional numeric coefficients (integer, decimal, scientific notation)
    - Flexible spacing around '+' signs
    - Species with charges, e.g., CO3-2, Eu+3, H+, e-
    """
    species = [x.strip() for x in side.split('+')]
    species_regex = []

    for sp in species:
        # Optional numeric coefficient in front of species
        coeff_pattern = r'(?:\d*\.?\d+(?:[eE][+-]?\d+)?)?'

        # Escape the species exactly (keep +, -, numbers for charges)
        species_regex.append(rf'{coeff_pattern}\s*{re.escape(sp)}')

    # Join species with optional spaces around '+'
    return r'\s*\+\s*'.join(species_regex)


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


def info(name, dic):
    """
    This function checks for naming convention of the species in the direct-access or source database

    Parameters
    ----------
       name : string
           species name
       dic : dict
           dictionary of species from direct-access or source database
    Returns
    ----------
       lst : list
           resulting search of all species with the input name

    Examples
    --------
    >>> from pygcc.pygcc_utils import db_reader
    >>> ps = db_reader() # utilizes the default direct-access database, speq21
    >>> info('ss_', ps.dbaccessdic)
        ['ss_Anorthite',  'ss_Albite_high', 'ss_K-feldspar', 'ss_Ferrosilite',
         'ss_Enstatite', 'ss_Clinoenstatite', 'ss_Hedenbergite', 'ss_Diopside',
         'ss_Forsterite', 'ss_Fayalite', 'ss_Annite',  'ss_Phlogopite',
         'ss_Anorthite',  'ss_Albite_high', 'ss_K-feldspar', 'ss_Ferrosilite',
         'ss_Enstatite', 'ss_Clinoenstatite', 'ss_Hedenbergite', 'ss_Diopside',
         'ss_Forsterite',  'ss_Fayalite', 'ss_Annite', 'ss_Phlogopite']
    """
    lst = [i for i in list(dic.keys()) if i.startswith(name)==True] # starts with name
    lst = lst + [i for i in list(dic.keys()) if i.__contains__(name)] # contains name
    return lst

#%%------------------------------------------------------------------------------------

def drummondgamma(TK, I):
    """
    This function models solubility of CO2 gas in brine using Drummond equation

    Parameters
    ----------
       TK : float, vector
           Temperature [K]
       I : float, vector
           Ionic strength

     Returns
    ----------
       log10_gamma : float, vector
           co2 aqueous activity coefficients in log10

    Examples
    --------
    >>> log10_gamma = drummondgamma( 500, 0.5)
    >>> log10_gamma
        0.0781512920184902
    """

    # A=20.244
    # B=-0.016323
    C=-1.0312
    # D=-3629.7
    E=0.4445
    F=0.0012806
    G=255.9
    H=-0.001606

    #gamma=(((C + F*TK + (G/TK))*I - (E + H*TK)*(I / (I + 1)))/np.log(10))
    log10_gamma = np.log10(np.exp((C + F*TK + (G/TK))*I - (E + H*TK)*(I / (I + 1))))

    return log10_gamma

def Henry_duan_sun(TK, P, I):
    """
    This function evaluates the solubility of CO2 gase in brine using Duan_Sun Formulation

    Parameters
    ----------
       TK : float, vector
           Temperature [K]
       P : float, vector
           Pressure [bar]
       I : float
           Ionic strength

    Returns
    ----------
       log10_co2_gamma : float, vector
           co2 aqueous activity coefficients in log10
       mco2 : float, vector
           co2 aqueous molalities

    Usage
    ----------
       log10_co2_gamma, mco2 = Henry_duan_sun( TK, P, I)

    Examples
    --------
    >>> log10_co2_gamma, mco2 = Henry_duan_sun( 500, 250, 0.5)
    >>> log10_co2_gamma, mco2
        0.06202532, 1.6062557

    References
    ----------
        (1) Duan, Z. and Sun, R., 2003. An improved model calculating CO2 solubility in
            pure water and aqueous NaCl solutions from 273 to 533 K and from 0 to 2000 bar.
            Chemical geology, 193(3-4), pp.257-271.
    """
    if (np.ndim(TK) == 0):
        TK = np.array(TK).ravel()
    if (np.ndim(P) == 0):
        P = np.array(P).ravel()
    if (np.ndim(I) == 0):
        I = np.array(I).ravel()
    if np.size(TK) < np.size(P):
        TK = TK*np.ones_like(P)
    if np.size(P) < np.size(TK):
        P = P*np.ones_like(TK)

    # calculate CO2 fugacity and partial pressure
    # vco2fugacity = np.vectorize(co2fugacity)
    [fCO2, denCO2, SI, pCO2] = co2fugacity(TK, P)

    # Equation B1 of Duan & Sun model to calculate vapor pressure of water
    c1 = -38.640844
    c2 = 5.894842
    c3 = 59.876516
    c4 = 26.654627
    c5 = 10.637097
    Pc = 220.85     ## bar
    Tc = 647.29     ## K
    t = (TK - Tc) / Tc
    PH2O = Pc * TK/Tc*(1 + c1*(-t)**1.9 + c2*t + c3*t**2 + c4*t**3 + c5*t**4)
    yCO2 = (P - PH2O) / P ## gas phase molar fraction of CO2

    mNaCl = 2 * I/ ((1)**2 + (-1)**2)
    par_mu = np.array([28.9447706, -0.0354581768, -4770.67077, 0.0000102782768,
                       33.8126098, 0.0090403714, -0.00114934031, -0.307405726,
                        -0.0907301486, 0.000932713393, 0])

    par_lambda = np.array([-0.411370585, 0.000607632013, 97.5347708, 0, 0, 0, 0,
                           -0.0237622469, 0.0170656236, 0, 0.0000141335834])

    par_xi = np.array([0.000336389723, -0.000019829898, 0, 0, 0, 0, 0,
                       0.0021222083, -0.00524873303, 0, 0])

    fTP = [1*np.ones([1, len(TK)]), TK, 1/TK, TK**2, 1/(630-TK), P, P*np.log(TK),
           P/TK, P/(630-TK), (P/(630-TK))**2, TK*np.log(P)]
    fTP = np.vstack(fTP)

    muCO2 = np.sum(par_mu.reshape(-1,1) * fTP, 0)      # mu0/RT
    lambdaCO2Na = np.sum(par_lambda.reshape(-1,1) * fTP, 0)    # lambda_CO2-Na Pitzer 2nd order int. param.
    xiCO2NaCl = np.sum(par_xi.reshape(-1,1) * fTP, 0)  # zeta_CO2-Na-Cl Pitzer 3rd order int. param.

    # activity coef. aqueous co2
    # Honoring limits for Duan and Sun - P-T-X range (0– 2000 bar, 0–260°C, 0–4.3 m NaCl)
    lngamco2 = np.zeros([len(I), len(TK)]); mco2 = np.zeros([len(I), len(TK)])
    for j in range(len(I)):
        for i in range(len(TK)):
            if (TK[i] <= convert_temperature( 260, Out_Unit = 'K' ) ) and (I[j] <= 4.3) and (P[i] <= 2000):
                lngamco2[j, i] = 2*lambdaCO2Na[i]*mNaCl[j] +  xiCO2NaCl[i]*mNaCl[j]**2
                mco2[j, i] = P[i] * yCO2[i]/np.exp(muCO2[i] - np.log(fCO2[i]/P[i]) + \
                                                   2*lambdaCO2Na[i]*mNaCl[j] +  xiCO2NaCl[i]*mNaCl[j]**2)
            else:
                lngamco2[j, i] = 0
                mco2[j, i] = 0

    log10_co2_gamma =  np.log10(np.exp(lngamco2))  #  ((lngamco2)/np.log(10))  #

    return log10_co2_gamma, mco2

def co2fugacity(TK, P, poy = True):
    """
    This function computes the fugacity and density of CO2 by Duan and Sun 2003
    Also Calculate the Saturation Index SI and partial pressure of CO2(g) at any given T, P
    using the Duan equation of state. A Poynting correction factor is also applied.
    Parameters
    ----------
       TK : float, vector
           Temperature [K]
       P : float, vector
           pressure [bar]
       poy : bool
           Option to apply a Poynting correction factor [True is the default]

    Returns
    ----------
       fCO2 : float, vector
           co2 fugacity [bar]
       denCO2 : float, vector
           co2 density [g/cm3]
       SI : float, vector
           co2 saturation index
       pCO2 : float, vector
           co2 partial pressure [bar]

    Usage
    ----------
       [fCO2, denCO2, SI, pCO2] = co2fugacity( TK, P)

    Examples
    --------
    >>> fCO2, denCO2, SI, pCO2 = co2fugacity( np.array([400,420]), np.array([150, 200]))
    >>> fCO2
        array([114.50387423, 150.87672517])
    >>> denCO2
        array([2.6741242 , 3.33134397])
    >>> SI
        array([1.73291553, 1.84597591])
    >>> pCO2
        array([54.78127571, 71.0710152])
    """
    if np.ndim(TK) == 0 :
        TK = np.array(TK).ravel()
    else:
        TK = np.ravel(TK)
    if np.ndim(P) == 0 :
        P = np.array(P).ravel()
    else:
        P = np.ravel(P)

    Rgas = 0.0831446261815324  #bar*L/mol/K
    PcCO2 = 73.825    ## bar
    TcCO2 = 31.05 + 273.15  ## K
    VcCO2 = Rgas * TcCO2 / PcCO2  # L/mol

    Pr = P / PcCO2 # unitless
    Tr = TK / TcCO2 # unitless
    xmwc = 44.0098  # g/mol

    a1  =  0.0899288497
    a2  = -0.494783127
    a3  =  0.0477922245
    a4  =  0.0103808883
    a5  = -0.0282516861
    a6  =  0.0949887563
    a7  =  0.00052060088
    a8  = -0.000293540971
    a9  = -0.00177265112
    a10 = -0.0000251101973
    a11 =  0.0000893353441
    a12 =  0.0000788998563
    a13 = -0.0166727022
    a14 =  1.398
    a15 =  0.0296

    # Equation A1
    Z = np.zeros([len(TK), 1]).ravel()

    for k in range(len(TK)):
        zfun = lambda Z : -Z + (1 + (a1 + a2 / Tr[k]**2 + a3 / Tr[k]**3) / (Z * Tr[k]) * Pr[k] +
                                (a4 + a5 / Tr[k]**2 + a6 / Tr[k]**3) / (Z * Tr[k])**2 * Pr[k]**2 +
                                (a7 + a8 / Tr[k]**2 + a9 / Tr[k]**3) / (Z * Tr[k])**4 * Pr[k]**4 +
                                (a10 + a11 / Tr[k]**2 + a12 / Tr[k] ** 3) / (Z * Tr[k])**5 * Pr[k]**5 +
                                a13 / Tr[k]**3 / (Z * Tr[k])**2 * Pr[k]**2 * (a14 + a15 / (Z * Tr[k])**2 * Pr[k]**2)*
                                np.exp(-a15 / (Z * Tr[k])**2 * Pr[k]**2))
        # set initial guess from ideal gas law
        Videal = Rgas*TK[k]/P[k]
        Zguess = Videal/VcCO2*Pr[k]/Tr[k]

        Z[k] = fsolve(zfun, Zguess, xtol=1.0e-10)[0]

    Vr = Z * Tr / Pr
    V = Vr * VcCO2  ## L / mol

    phi = np.exp(Z - 1 - np.log(Z) + (a1 + a2 / (Tr ** 2) + a3 / (Tr ** 3)) / Vr + \
                 (a4 + a5 / (Tr ** 2) + a6 / (Tr ** 3)) / (2 * Vr ** 2) + \
                     ((a7 + a8 / (Tr ** 2) + a9 / (Tr ** 3)) / (4 * Vr ** 4) + \
                      (a10 + a11 / (Tr ** 2) + a12 / (Tr ** 3)) / (5 * Vr ** 5) + \
                          a13 / (2 * Tr ** 3 * a15) * (a14 + 1 - (a14 + 1 + a15 / Vr ** 2) * \
                                                           np.exp(-a15 / Vr ** 2))))
    # print(phi)
    #-----fugacity
    fCO2 = phi * P  #bar

    #-----density
    denCO2 = xmwc*1e-3 / V # g/cm^3
    Poy = 1
    Patm = P / 1.01325

    if (poy):
        R =   0.082057366080960 ## L atm /K/mol
        Vm = np.where(V < 0, 32.0e-3, V)   ## L / mol
        Poy = np.exp(-(Patm - 1)*Vm/R/TK)
    pCO2 = phi*Patm*Poy  # atm
    SI = np.log10(pCO2)
    pCO2 = pCO2 * 1.01325  # bar

    return fCO2, denCO2, SI, pCO2

def gamma_correlation(TC, P, method = None):
    """
    This function calculates the CO2 activity correlation coefficients at
    given temperature T and pressure P

    Parameters
    ----------
       TC : float, vector
           Temperature [°C]
       P : float, vector
           Pressure [bar]
       method : string
           specify the activity model [``'Duan_Sun'`` or ``'Drummond'``]

     Returns
    ----------
       cco2 : float, vector
           co2 correlation coefficients

     Usage
    ----------
       cco2 = gamma_correlation( TC, P)

    Examples
    --------
    >>> log10_co2_gamma, mco2 = Henry_duan_sun( 500, 250, 0.5)
    >>> log10_co2_gamma, mco2
        0.06202532, 1.6062557

    References
    ----------
        (1) Segal Edward Drummond, 1981, Boiling and Mixing of Hydrothermal
            Fluids: Chemical Effects on Mineral Precipitation, page 19
        (2) Wolery, T. J., Lawrence Livermore National Laboratory, United States Dept.
            of Energy, 1992. EQ3/6: A software package for geochemical modeling of
            aqueous systems: package overview and  installation guide (version 7.0)
    """

    if np.ndim(TC) == 0:
        TC = np.array(TC).ravel()
    if np.ndim(P) == 0:
        P = np.array(P).ravel()

    TK = convert_temperature( TC, Out_Unit = 'K' )
    #   assign ionic strength from 0 to 3
    N = 100
    I = np.zeros([N, 1])
    for i in range(N):
        I[i] = 3 * i /(N - 1)


    A = np.zeros([3, 3])
    B = np.zeros([3, 1])
    cco2 = np.zeros([4, len(TK)])
    if method is not None:
        if method.lower() == 'duan_sun':
            ccoef = Henry_duan_sun(TK, P, I)[0]
        elif method.lower() == 'drummond':
            ccoef = drummondgamma(TK, I)
    else:
        ccoef = drummondgamma(TK, I)

    for i in range(len(TK)):
        for ii in range(3):
            for jj in range(3):
                A[ii, jj] = np.sum(I**((ii+1) + (jj+1)))
                B[ii] = np.sum(ccoef[:, i]*I.ravel()**(ii+1))
        Coef = lu_solve(lu_factor(A), B)
        cco2[:, i] = np.concatenate([Coef.ravel(),np.array([0])])

    return cco2


def Helgeson_activity(TC, P, I, Dielec_method = None, **rhoEDB):
    """
    This function calculates the solute activity coefficient, solvent osmotic coefficient,
    and solvent  activity at given temperature and pressure using equations 298, 190 and 106 in
    Helgeson, Kirkham and Flowers, 1981, A.J.S. p.1249-1516
    Parameters:
    ----------
       TC       :   Temperature [°C]
       P        :   pressure [bar]
       I        :   ionic strength
       Dielec_method :   specify either 'FGL97' or 'JN91' or 'DEW' as the method to calculate dielectric
                       constant (optional), if not specified default - 'JN91'
       rhoEDB   :   dictionary of water properties like density (rho), dielectric factor (E) and
                       Debye–Hückel coefficients (optional)
    Returns:
    ----------
       aw       :   solvent activity
       phi      :   solvent osmotic coefficient
       mean_act :   solute activity coefficient
    Usage
    -------
       [aw, phi, mean_act] = Helgeson_activity( TC, P, I)
    """

    if np.ndim(TC) == 0:
        TC = np.array(TC).ravel()
    if np.ndim(P) == 0:
        P = np.array(P).ravel()
    if np.ndim(I) == 0 :
        I = np.array(I).ravel()
    if np.size(TC) < np.size(P):
        TC = TC*np.ones_like(P)
    if np.size(P) < np.size(TC):
        P = P*np.ones_like(TC)
    I = I.reshape(-1,1)

    Dielec_method = 'JN91' if Dielec_method is None else Dielec_method
    if rhoEDB.__len__() != 0:
        Ah = rhoEDB['Ah'].ravel()
        Bh = rhoEDB['Bh'].ravel()
    else:
        water = water_dielec(T = TC, P = P, Dielec_method = Dielec_method)
        Ah, Bh = water.Ah, water.Bh

    z = [-1.0, 1.0]
    mwH2O = 18.01528/1000  # kg/mol
    R = 1.9872041  # cal/mol/K

    mstar = 2*I         # total solute in solution
    mtj = I             # total concentration of ion j
    mchr= 2*I           # total solute excluding neutral species
    loggamma = [0]*2; summt = [0]*2
    rej = [1.810, 1.910]    # Rej of Cl- and Na+

    bijl = np.zeros(np.size(TC)); bi = np.zeros(np.size(TC))
    # bil and bihat correlation
    for k in range(len(TC)):
        if TC[k] < 350:
            Psat = iapws95(T = TC[k], P = 'T').P
        else:
            Psat = [0]
        if P[k] == Psat:  #%% P = Psat Region
            x = np.array([ 25.,  50.,  75., 100., 125., 150., 175., 200., 225.,
                          250., 275., 300., 325.])
            y = np.array([ 2.47,  2.15,  1.79,  1.39,  0.93,  0.41, -0.18, -0.85, -1.64,
                          -2.57, -3.71, -5.21, -7.32])
            fun = splrep(x, y)
            bhat = splev(TC[k], fun)
            y = np.array([-9.77, -5.59, -2.43,  0.23,  2.44,  4.51,  6.38,  8.11,  9.73, 11.29,
                          11.71, 14.15, 15.49])
            fun = Rbf(x, y)
            bil = fun(TC[k])
        elif P[k] != Psat and P[k] < 1000:
            isoline = P[k]
            x = np.array([ 25.,  50.,  75., 100., 125., 150., 175., 200., 225., 250., 275., 300., 325.])
            y = np.array([ 2.47,  2.15,  1.79,  1.39,  0.93,  0.41, -0.18,
                          -0.85, -1.64, -2.57, -3.71, -5.21, -7.32])
            fun = splrep(x, y)
            xpred = np.linspace(0, 500, 100)
            ypred1 = splev(xpred, fun)
            #ypred1 = np.where(ypred1 < -17.12, -17.12, ypred1)
            x = np.arange(25,525,25)
            y = np.array([  2.58,   2.28,   1.95,   1.58,   1.18,   0.73,   0.25,   0.28,
                          -0.86,  -1.5 ,  -2.2 ,  -2.99,  -3.88,  -4.91,  -6.11,  -7.56,
                          -9.31, -11.43, -14.01, -17.12])
            mask = np.arange(len(x)) !=np.where(x == 200)[0][0]
            fun = splrep(x[mask], y[mask])
            ypred2 = splev(xpred, fun)
            newy = (1000-isoline)/1000*ypred1 + (isoline/1000)*ypred2
            fun = splrep(xpred, newy)
            bhat = splev(TC[k], fun)
            x = np.array([ 25.,  50.,  75., 100., 125., 150., 175., 200., 225., 250., 275., 300., 325.])
            y = np.array([-9.77, -5.59, -2.43,  0.23,  2.44,  4.51,  6.38,  8.11,  9.73, 11.29,
                          11.71, 14.15, 15.49])
            fun = Rbf(x, y)
            xpred = np.linspace(0, 500, 100)
            ypred1 = fun(xpred)
            ypred1 = np.where(ypred1 > 24.03, 24.03, ypred1)
            x = np.arange(25,525,25)
            y = np.array([ -9.19, -5.07, -2.63, -0.07,  1.71,  4.13,  5.91,  7.48,  9.27,
                          10.8 , 12.24, 13.68, 15.16, 16.48, 17.8 , 19.12, 20.33, 21.55,
                          22.86, 24.03])
            fun = splrep(x, y)
            ypred2 = splev(xpred, fun)
            newy = (1000-isoline)/1000*ypred1 + (isoline/1000)*ypred2
            fun = splrep(xpred, newy)
            bil = splev(TC[k], fun)
        elif P[k] >= 1000 and P[k] <= 2000:
            isoline = P[k] - 1000
            x = np.arange(25,525,25)
            y = np.array([  2.58,   2.28,   1.95,   1.58,   1.18,   0.73,   0.25,   0.28,
                          -0.86,  -1.5 ,  -2.2 ,  -2.99,  -3.88,  -4.91,  -6.11,  -7.56,
                          -9.31, -11.43, -14.01, -17.12])
            mask = np.arange(len(x)) !=np.where(x == 200)[0][0]
            fun = splrep(x[mask], y[mask])
            xpred = np.linspace(0, 500, 100)
            ypred1 = splev(xpred, fun)
            y = np.array([  2.66,  2.37,  2.06,  1.72,  1.35,  0.95,  0.51,  0.04, -0.46,
                          -1.  , -1.57, -2.19, -2.85, -3.58, -4.38, -5.26, -6.24, -7.34,
                          -8.56, -9.88])
            fun = splrep(x, y)
            ypred2 = splev(xpred, fun)
            newy = (1000-isoline)/1000*ypred1 + (isoline/1000)*ypred2
            fun = splrep(xpred, newy)
            bhat = splev(TC[k], fun)
            y = np.array([ -9.19, -5.07, -2.63, -0.07,  1.71,  4.13,  5.91,  7.48,  9.27,
                          10.80, 12.24, 13.68, 15.16, 16.48, 17.8 , 19.12, 20.33, 21.55,
                          22.86, 24.03])
            fun = splrep(x, y)
            xpred = np.linspace(0, 500, 100)
            ypred1 = splev(xpred, fun)
            y = np.array([ -9.12, -5.52, -2.65, -0.1 ,  1.83,  4.12,  5.88,  7.66,  9.2 ,
                          10.73, 12.19, 13.66, 15.1 , 16.42, 17.79, 19.11, 20.35, 21.61,
                          22.84, 23.95])
            fun = splrep(x, y)
            ypred2 = splev(xpred, fun)
            newy = (1000-isoline)/1000*ypred1 + (isoline/1000)*ypred2
            fun = splrep(xpred, newy)
            bil = splev(TC[k], fun)
        elif P[k] > 2000 and P[k] <= 3000: #%% P = 3000 Region
            isoline = P[k] - 2000
            x = np.arange(25,525,25)
            y = np.array([  2.66,  2.37,  2.06,  1.72,  1.35,  0.95,  0.51,  0.04, -0.46,
                          -1.  , -1.57, -2.19, -2.85, -3.58, -4.38, -5.26, -6.24, -7.34,
                          -8.56, -9.88])
            fun = splrep(x, y)
            xpred = np.linspace(0, 500, 100)
            ypred1 = splev(xpred, fun)
            y = np.array([  2.72,  2.45,  2.15,  1.83,  1.48,  1.11,  0.72,  0.29, -0.15,
                          -0.63, -1.13, -1.67, -2.24, -2.86, -3.52, -4.24, -5.03, -5.87,
                          -6.78, -7.73])
            fun = splrep(x, y)
            ypred2 = splev(xpred, fun)
            newy = (1000-isoline)/1000*ypred1 + (isoline/1000)*ypred2
            fun = splrep(xpred, newy)
            bhat = splev(TC[k], fun)
            y = np.array([ -9.19, -5.07, -2.63, -0.07,  1.71,  4.13,  5.91,  7.48,  9.27,
                          10.80, 12.24, 13.68, 15.16, 16.48, 17.8 , 19.12, 20.33, 21.55,
                          22.86, 24.03])
            fun = splrep(x, y)
            xpred = np.linspace(0, 500, 100)
            ypred1 = splev(xpred, fun)
            y = np.array([ -9.51, -5.6 , -2.46,  0.13,  2.14,  4.28,  6.16,  8.18,  9.59,
                          11.15, 12.62, 13.99, 15.41, 16.76, 18.1 , 19.4 , 20.66, 21.85,
                          23.09, 24.32])
            fun = splrep(x, y)
            ypred2 = splev(xpred, fun)
            newy = (1000-isoline)/1000*ypred1 + (isoline/1000)*ypred2
            fun = splrep(xpred, newy)
            bil = splev(TC[k], fun)
        elif P[k] > 3000 and P[k] <= 4000: #%% P = 4000 Region
            isoline = P[k] - 3000
            x = np.arange(25,525,25)
            y = np.array([  2.72,  2.45,  2.15,  1.83,  1.48,  1.11,  0.72,  0.29, -0.15,
                          -0.63, -1.13, -1.67, -2.24, -2.86, -3.52, -4.24, -5.03, -5.87,
                          -6.78, -7.73])
            fun = splrep(x, y)
            xpred = np.linspace(0, 500, 100)
            ypred1 = splev(xpred, fun)
            y = np.array([  2.77,  2.51,  2.22,  1.91,  1.58,  1.23,  0.86,  0.47,  0.05,
                          -0.38, -0.84, -1.33, -1.85, -2.4 , -2.99, -3.63, -4.32, -5.06,
                          -5.84, -6.63])
            fun = splrep(x, y)
            ypred2 = splev(xpred, fun)
            newy = (1000-isoline)/1000*ypred1 + (isoline/1000)*ypred2
            fun = splrep(xpred, newy)
            bhat = splev(TC[k], fun)

            y = np.array([ -9.51, -5.6 , -2.46,  0.13,  2.14,  4.28,  6.16,  8.18,  9.59,
                          11.15, 12.62, 13.99, 15.41, 16.76, 18.1 , 19.4 , 20.66, 21.85,
                          23.09, 24.32])
            fun = splrep(x, y)
            xpred = np.linspace(0, 500, 100)
            ypred1 = splev(xpred, fun)
            y = np.array([-10.44,  -5.68,  -2.15,   0.71,   3.05,   5.13,   7.05,   9.05,
                          10.4 ,  11.92,  13.39,  14.83,  16.23,  17.52,  18.81,  20.13,
                          21.38,  22.56,  23.74,  24.94])
            fun = splrep(x, y)
            ypred2 = splev(xpred, fun)
            newy = (1000-isoline)/1000*ypred1 + (isoline/1000)*ypred2
            fun = splrep(xpred, newy)
            bil = splev(TC[k], fun)
        elif P[k] > 4000 and P[k] <= 5000: #%% P = 4000 Region
            isoline = P[k] - 4000
            x = np.arange(25,525,25)
            y = np.array([  2.77,  2.51,  2.22,  1.91,  1.58,  1.23,  0.86,  0.47,  0.05,
                          -0.38, -0.84, -1.33, -1.85, -2.4 , -2.99, -3.63, -4.32, -5.06,
                          -5.84, -6.63])
            fun = splrep(x, y)
            xpred = np.linspace(0, 500, 100)
            ypred1 = splev(xpred, fun)
            y = np.array([  2.82,  2.56,  2.28,  1.99,  1.67,  1.33,  0.98,  0.6 ,  0.21,
                          -0.2 , -0.63, -1.09, -1.58, -2.1 , -2.65, -3.25, -3.89, -4.57,
                          -5.28, -6. ])
            fun = splrep(x, y)
            ypred2 = splev(xpred, fun)
            newy = (1000-isoline)/1000*ypred1 + (isoline/1000)*ypred2
            fun = splrep(xpred, newy)
            bhat = splev(TC[k], fun)

            y = np.array([-10.44,  -5.68,  -2.15,   0.71,   3.05,   5.13,   7.05,   9.05,
                          10.4 ,  11.92,  13.39,  14.83,  16.23,  17.52,  18.81,  20.13,
                          21.38,  22.56,  23.74,  24.94])
            fun = splrep(x, y)
            xpred = np.linspace(0, 500, 100)
            ypred1 = splev(xpred, fun)
            y = np.array([-11.76,  -5.87,  -1.68,   1.39,   4.21,   6.26,   8.13,  10.3,
                          11.58,  13.15,  14.54,  16.01,  17.36,  18.65,  19.83,  21.23,
                          22.38,  23.64,  24.78,  25.95])
            fun = splrep(x, y)
            ypred2 = splev(xpred, fun)
            newy = (1000-isoline)/1000*ypred1 + (isoline/1000)*ypred2
            fun = splrep(xpred, newy)
            bil = splev(TC[k], fun)
        elif P[k] >= 5000: #%% P = 5000 Region and beyond
            x = np.arange(25,525,25)
            y = np.array([  2.82,  2.56,  2.28,  1.99,  1.67,  1.33,  0.98,  0.6 ,  0.21,
                          -0.2 , -0.63, -1.09, -1.58, -2.1 , -2.65, -3.25, -3.89, -4.57,
                          -5.28, -6. ])
            fun = splrep(x, y)
            bhat = splev(TC[k], fun)
            y = np.array([-11.76,  -5.87,  -1.68,   1.39,   4.21,   6.26,   8.13,  10.3,
                          11.58,  13.15,  14.54,  16.01,  17.36,  18.65,  19.83,  21.23,
                          22.38,  23.64,  24.78,  25.95])
            fun = splrep(x, y)
            bil = splev(TC[k], fun)

        # bihat NaCl (b NaCl = bhat/(2.303RT)) from Table 29 (bi here) in kg/mol * 1e+3
        # b Na+Cl- from Table 30 (bil here) in kg/mol * 1e+2
        bihat = bhat*1e-3    # [kg/mol]
        bi[k] = bihat/(np.log(10)*R*convert_temperature( TC[k], Out_Unit = 'K' ))  #[kg/cal]
        bijl[k] = bil*1e-2

    # activity and osmotic coefficients
    # for j in range(len(I)):
    for i in range(2):
        zabsi = np.abs(z[i])
        if i < 1: rex = 1.81
        else: rex = 1.91
        azero = 2*(rej[i] + zabsi*rex)/(zabsi + 1)
        omega = 1.66027e5*z[i]**2/rej[i]
        lambdaa = 1 + Bh*azero*I**0.5
        loggamma[i] = - Ah * z[i]**2 * I**0.5 / lambdaa - np.log10(1 + mwH2O * mstar) + \
            (omega*bi + bijl - 0.19*(np.abs(z[i]) - 1))*I

        summt[i] = mtj * ( (Ah*z[i]**2/((azero*Bh)**3*I)) *\
                          (lambdaa - 1/lambdaa - 2*np.log(lambdaa)) + \
                              (-np.log10(1 + mwH2O * mstar)/(mwH2O*mstar)) - \
                                  0.5*(omega*bi*I + (bijl - 0.19 *(np.abs(z[i]) - 1)) * \
                                       mchr*0.5) )

    mean_act = 10**((loggamma[0]+loggamma[1])/2)
    phi = -np.log(10)*(summt[0]+summt[1])/mstar
    phi = np.where(np.isnan(phi), 0, phi)

    aw = np.exp(-phi*mstar*mwH2O)
    return aw, phi, mean_act

def aw_correlation(TC, P, Dielec_method = None, **rhoEDB):
    """
    Calculates the water activity correlation coefficients at given temperature and pressure
    Parameters:
    ----------
       TC       :       Temperature [°C]
       P        :       pressure [bar]
       Dielec_method :  specify either 'FGL97' or 'JN91' or 'DEW' as the method to calculate dielectric
                           constant (optional), if not specified default - 'JN91'
       rhoEDB   :       dictionary of water properties like density (rho), dielectric factor (E) and
                           Debye-Hückel coefficients (optional)
    Returns:
    ----------
       ch20     :       water activity correlation coefficients
    Usage
    -------
       [ch20] = aw_correlation( TC, P)
    """

    Dielec_method = 'JN91' if Dielec_method is None else Dielec_method

    if rhoEDB.__len__() != 0:
        rho = rhoEDB['rho'].ravel()
        E = rhoEDB['E'].ravel()
        Ah = rhoEDB['Ah'].ravel()
        Bh = rhoEDB['Bh'].ravel()
    else:
        if Dielec_method.upper() == 'DEW':
            rho = ZhangDuan(T = TC, P = P).rho
        else:
            rho = iapws95(T = TC, P = P).rho
        water = water_dielec(T = TC, P = P, Dielec_method = Dielec_method)
        E, Ah, Bh = water.E, water.Ah, water.Bh

        rhoEDB = {'rho': rho, 'E': E,  'Ah': Ah, 'Bh': Bh}

    if np.ndim(TC) == 0 | np.ndim(P) == 0:
        TC = np.array(TC).ravel()
        P = np.array(P).ravel()

    #   assign ionic strength from 0 to 3
    N = 100
    Is = np.linspace(0, 6, N).reshape(-1,1)
    mwH2O = 18.01528/1000  # kg/mol

    #  Water Activity
    aw = Helgeson_activity(TC, P, Is, Dielec_method = Dielec_method, **rhoEDB)[0]
    ch20 = np.zeros([4, len(TC)])
    x0 = [1.454, 0.02236, 9.380e-3, -5.362e-4]
    for i in range(len(TC)):
        if np.sum(np.isnan(aw[:, i])) == 0:
            Is_0 = Is [1:]  # avoid zero values
            Ahi = Ah[i]
            ch20func = lambda Is_0, *x: (-2*Is_0*mwH2O * \
                                         (1 - (np.log(10)*Ahi/(x[0]**3*Is_0)) * \
                                          ((1 + x[0]*np.sqrt(Is_0)) - 2*np.log(1 + x[0]*np.sqrt(Is_0)) - \
                                           ( 1/(1 + x[0]*np.sqrt(Is_0)) ) ) + \
                    (x[1]*Is_0/2) + (2/3*x[2]*Is_0**2) + (3/4*x[3]*Is_0**3) ))

            ch20[:, i], pcov = curve_fit(ch20func, Is_0.ravel(), np.log(aw[1:, i]).ravel(),
                                         p0=x0,  maxfev = 1000000)
        else:
            ch20[:, i] = [500]*4
    return ch20



#%%------------------------------------------------------------------------------------

class calcRxnlogK():
    """
    This class implemetation calculates logK values for any reaction with the option for extrapolation where rho < 350kg/m3  \n

    Parameters
    ----------
        T : float, vector
            Temperature [°C]
        P : float, vector
            Pressure [bar]
        Specie : string
            specify the species for logK calculation, either the Product species of any reaction or solid solutions or clay like 'AnAb' or 'AbOr' or 'FoFa' or 'EnFe' or 'DiHedEnFe' or 'clay'  \n
        Specie_class : string, optional
            specify the class of species  like 'aqueous', 'minerals', 'liquids', or 'gases'
        elem : list
            list containing nine or ten parameters with clay names and elements compositions with the following format ['Montmorillonite_Lc_MgK', 'Si', 'Al', 'FeIII', 'FeII', 'Mg', 'K', 'Na', 'Ca', 'Li', 'H3O'] \n
        dbaccessdic : dict
            direct-acess database dictionary
        rhoEGextrap : dict
            dictionary of water properties like  density (rho), dielectric factor (E) and Gibbs Energy for density region 350-550kg/m3
        group : string
            specify the structural layering of the phyllosilicate, for layers composed of  ``1 tetrahedral + 1 octahedral sheet (1:1 layer)`` - specify ``'7A'``, ``2 tetrahedral + 1 octahedral sheet (2:1 layer)`` - specify ``'10A'``, or  the latter with ``a brucitic sheet in the interlayer (2:1:1 layer)``  - specify ``'14A'``  (optional), if not specified, default is '10A' for smectites, micas, et cetera \n
        ClayMintype : string
            specify either 'Smectite' or 'Chlorite' or 'Mica' as the clay type, if not specified default - 'Smectites'
        X : float
            volume fractions of any (Anorthite, Albite, Forsterite, Enstatite) or mole fraction of Mg
        cpx_Ca : float
            number of moles of Ca in formula unit (=1 for Di, Hed), must be greater than zero
        sourcedic : dict
            source database reactions dictionary
        specielist : list of list, optional
            source database species grouped into categories [element, basis, redox, aqueous, minerals, gases, oxides]
        Dielec_method : string
            specify either 'FGL97' or 'JN91' or 'DEW' as the method to calculate dielectric constant, default is 'JN91' \n
        heatcap_method : string
            specify either 'SUPCRT' or 'Berman88' or 'HP11' or 'HF76' as the method to calculate thermodynamic properties of any mineral or gas, default is 'SUPCRT' \n
        ThermoInUnit : string
            specify either 'cal' or 'KJ' as the input units for species properties (optional), particularly used to covert KJ data to cal by supcrtaq function if not specified default - 'cal'
        Al_Si : string
            specify either 'pygcc' or 'Arnórsson_Stefánsson' as the input to express Al and Si species in solid solution (optional), 'Arnórsson_Stefánsson' expresses them as 'Al(OH)4-' and 'H4SiO4(aq)', respectively while pygcc uses 'Al3+' and 'SiO2(aq)', respectively if not specified default - 'pygcc'
        Int_Mg_fract : string
            specify the fraction of Mg to partition into Interlayer sheet and the remainder will be partitioned into Octahedral sheet, if not specified, default is 1
        Int_Li_fract : string
            specify the fraction of Li to partition into Interlayer sheet and the remainder will be partitioned into Octahedral sheet, if not specified, default is 1
        heatcap_approx : string
            specify either 'Maier-Kelley' or 'constant' as the approximation method for clay minerals' specific heat capacity calculation, default is 'constant', based on ClayTherm's definition for specific cations (Octahedral sites: Li+, Mn2+, Cr3+, Ni2+, Co2+, Zn2+; Interlayer sites: Cs+, Rb+, Li+, Ba2+, Sr2+, Mg2+, Cu2+, Co2+, Zn2+, H3O+) \n
        sourceformat : string
            specify the source database format, either 'GWB', 'EQ36' or 'PHREEQC'
        densityextrap : float, vector
            specify the extrapolation option for density-logK, 'Yes'/True or 'No'/False

    Returns
    -------
        log_K : float, vector
            logarithmic K value(s)  \n
        dGrxn : float, vector
            Total reaction Gibbs energy [cal/mol] \n

    Usage
    ----------
        The general usage of water_dielec is as follows:  \n
        (1) For water dielectric properties at any Temperature and Pressure:  \n
            calclogK = calcRxnlogK(T = T, P = P, Dielec_method = 'JN91', **kwargs),   \n
            where T is temperature in celsius and P is pressure in bar
        (2) For water dielectric properties at any Temperature and density :  \n
            calclogK = calcRxnlogK(T = T, rho = rho, Dielec_method = 'JN91', **kwargs),   \n
            where T is temperature in celsius and rho is density in kg/m³
        (3) For water dielectric properties at any Temperature and Pressure on steam saturation curve:  \n
            calclogK = calcRxnlogK(T = T, P = 'T', Dielec_method = 'JN91', **kwargs),   \n
            where T is temperature in celsius, followed with a quoted character 'T' to reflect steam saturation pressure  \n
            calclogK = calcRxnlogK(P = P, T = 'P', Dielec_method = 'JN91', **kwargs),   \n
            where P is pressure in bar, followed with a quoted character 'P' to reflect steam saturation temperature

    Examples
    --------
    >>> ps = db_reader(sourcedb = './default_db/thermo.com.dat',
                       sourceformat = 'gwb', dbaccess = './default_db/speq21.dat')
    >>> calclogK = calcRxnlogK(T = 100, P = 50, Specie = 'H2S(aq)',
                               Specie_class = 'aqueous',
                               dbaccessdic = ps.dbaccessdic,
                               sourcedic = ps.sourcedic, specielist = ps.specielist)
    >>> calclogK.logK, calclogK.dGrxn
         -6.4713,       11049.3168
    """
    kwargs = {"T": None, "Specie": None, "Specie_class": None, "ThermoInUnit": 'cal',
              "P": None, "group": None,  "X": None,  "cpx_Ca": None,  "elem": None,
              'rhoEGextrap': None, "sourcedic": None, "specielist": None,
              'dbaccessdic': None, "Dielec_method": None, "sourceformat": None,
              'heatcap_method': None, "densityextrap": None, 'rhoEG': None, 
              'Int_Mg_fract': None, 'Int_Li_fract': None, 'heatcap_approx': None, 
              'ClayMintype': 'Smectite', "Al_Si": 'pygcc'}

    def __init__(self, **kwargs):
        self.kwargs = calcRxnlogK.kwargs.copy()
        self.__calc__(**kwargs)

    def __calc__(self, **kwargs):
        self.kwargs.update(kwargs)
        """initialization """
        self.TC = self.kwargs["T"];                        self.P = self.kwargs["P"]
        self.sourceformat = self.kwargs['sourceformat'];   self.specielist = self.kwargs['specielist'];
        self.sourcedic = self.kwargs['sourcedic'];         self.Dielec_method = self.kwargs['Dielec_method'];
        self.rhoEG = self.kwargs['rhoEG'];                 self.ThermoInUnit = self.kwargs['ThermoInUnit']
        self.rhoEGextrap = self.kwargs['rhoEGextrap'];     self.Specie = self.kwargs['Specie']
        self.Specie_class = self.kwargs['Specie_class'];   self.elem = self.kwargs['elem']
        self.cpx_Ca = self.kwargs['cpx_Ca'];               self.group = self.kwargs['group']
        self.X = self.kwargs['X'];                         self.heatcap_method = self.kwargs['heatcap_method']
        self.ClayMintype = self.kwargs['ClayMintype'];     self.Al_Si = self.kwargs["Al_Si"]
        self.Int_Mg_fract = self.kwargs['Int_Mg_fract'];     self.Int_Li_fract = self.kwargs["Int_Li_fract"]
        self.heatcap_approx = self.kwargs["heatcap_approx"]
        self.densityextrap = 'No' if (self.kwargs['densityextrap'] is None or self.kwargs['densityextrap'] is False) else 'Yes' if self.kwargs['densityextrap'] is True else self.kwargs['densityextrap']

        self.Dielec_method = 'JN91' if self.Dielec_method is None else self.Dielec_method
        self.heatcap_method = 'SUPCRT' if self.heatcap_method is None else self.heatcap_method
        self.sourceformat = 'GWB' if self.sourceformat is None else self.sourceformat

        if self.kwargs['dbaccessdic'] == None:
            self.dbaccess_dir = './default_db/speq21.dat'
            self.dbaccess_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.dbaccess_dir)
            self.dbaccessdic = db_reader(dbaccess = self.dbaccess_dir).dbaccessdic
        else:
            self.dbaccessdic = self.kwargs['dbaccessdic']

        if (type(self.P) == str) or (type(self.TC) == str):
            if self.P == 'T':
                self.P = iapws95(T = self.TC).P
                self.P[np.isnan(self.P) | (self.P < 1)] = 1.0133
            elif self.TC == 'P':
                self.TC = iapws95(P = self.P).TC

        if np.ndim(self.TC) == 0 :
            self.TC = np.array(self.TC).ravel()
        elif np.size(self.TC) == 2:
            self.TC = np.array([roundup_tenth(j) if j != 0 else 0.01
                                for j in np.linspace(self.TC[0], self.TC[-1], 8)])
        if np.size(self.P) <= 2:
            self.P = np.ravel(self.P)
            self.P = self.P[0]*np.ones(np.size(self.TC))


        if self.rhoEG is None:
            if self.Dielec_method.upper() == 'DEW':
                water = ZhangDuan(T = self.TC, P = self.P)
            else:
                water = iapws95(T = self.TC, P = self.P)
            rho, dGH2O = water.rho, water.G
            E = water_dielec(T = self.TC, P = self.P, Dielec_method = self.Dielec_method).E
            self.rhoEG = {'rho': rho, 'E': E,  'dGH2O': dGH2O}

        if self.densityextrap.lower() == 'yes':
            subBornptrs = self.rhoEG['rho'] < 350
            self.nonsubBornptrs = self.rhoEG['rho'] >= 350
            rhoEG_nonsubBornptrs = {'rho': self.rhoEG['rho'][self.nonsubBornptrs], 'E': self.rhoEG['E'][self.nonsubBornptrs],
                                   'dGH2O': self.rhoEG['dGH2O'][self.nonsubBornptrs]}

            if self.rhoEGextrap is None:
                # Calculate the rho E G for density extrapolation method here so we have it below
                self.rhoEGextrap = {}
                if any(subBornptrs):
                    for i, j in enumerate(zip(self.TC[subBornptrs], self.P[subBornptrs])):
                        rhoextrap = np.linspace(350, 550, 3)
                        Pextrap = iapws95(T = j[0], rho = rhoextrap).P if self.Dielec_method.upper() != 'DEW' else ZhangDuan(T = j[0], rho = rhoextrap).P
                        Textrap = j[0]*np.ones(np.size(Pextrap))

                        dGH2O = iapws95(T = Textrap, P = Pextrap).G if self.Dielec_method.upper() != 'DEW' else ZhangDuan(T = Textrap, P = Pextrap).G
                        E = water_dielec(T = Textrap, P = Pextrap, Dielec_method = self.Dielec_method).E
                        rhoextrap = np.around(rhoextrap, 3)
                        self.rhoEGextrap['%d_%d' % (j[0], j[1])]= {'rho': rhoextrap,'E': E, 'dGH2O': dGH2O,
                                                                   'Textrap': Textrap, 'Pextrap': Pextrap}

        if self.densityextrap.lower() == 'no':
            if self.Specie.lower().startswith(('plagio', 'oliv', 'pyroxe', 'alk-')) or self.Specie.lower() in ['cpx', 'clay']:
                self.logK, self.Rxn = self.AllRxnslogK( self.TC, self.P, self.rhoEG)
            else:
                self.logK, self.dGrxn, dGP, dGRs = self.AllRxnslogK( self.TC, self.P, self.rhoEG)
            self.nonsubBornptrs = [False]*len(self.TC) # Required to shut off density extrapolation prompt
        elif self.densityextrap.lower() == 'yes':
            self.logK = np.nan*np.zeros(len(self.TC))
            self.dGrxn = np.nan*np.zeros(len(self.TC))
            if any(subBornptrs):
                self.logK[subBornptrs] =  self.densitylogKextrap( self.TC[subBornptrs], self.P[subBornptrs],
                                                                 self.rhoEGextrap)
            if any(self.nonsubBornptrs):
                if self.Specie.lower().startswith(('plagio', 'oliv', 'pyroxe', 'alk-')) or self.Specie.lower() in ['cpx', 'clay']:
                    self.logK[self.nonsubBornptrs], self.Rxn = self.AllRxnslogK( self.TC[self.nonsubBornptrs], self.P[self.nonsubBornptrs], rhoEG_nonsubBornptrs)
                else:
                    self.logK[self.nonsubBornptrs], self.dGrxn[self.nonsubBornptrs], dGP, dGRs = self.AllRxnslogK( self.TC[self.nonsubBornptrs], self.P[self.nonsubBornptrs], rhoEG_nonsubBornptrs)

    def AllRxnslogK( self, TC, P, rhoEG):
        """
        This function calculates logK values of all reactions including solid-solution and clay minerals \n
        Parameters
        ----------
            TC          : temperature [°C] \n
            P           : pressure [bar] \n
            rhoEG       : dictionary of water properties like  density (rho),
                            dielectric factor (E) and Gibbs Energy  (optional) \n
        Returns
        -------
            logK        : logarithmic K value(s)  \n
            dGrxn       : Total reaction Gibbs energy [cal/mol] \n
            dGP         : Product specie Gibbs energy [cal/mol] \n
            dGRs        : Reactant species Gibbs energy [cal/mol] \n
            Rxn         : dict
            The calculated dictionary of reaction thermodynamic properties has the following properties:

                * type: solid-solution mineral type, [-]
                * name: solid-solution name, [K]
                * formula: solid-solution mineral formula, [-]
                * MW: Molecular weight, [g/mol]
                * min: solid-solution mineral properties, ['formula', 'source date', dG[cal/ml], dH[cal/mol], S[cal/mol-K], V[cm3/mol], a[cal/mol-K], b[10^3 cal/mol/K^2], c[10^-5 cal/mol/K]]
                * spec: list of species, [-]
                * coeff: list of corresponding coefficients of species above, [-]
                * nSpec: Total number of species, [-]
                * V: Molar volume, [cm3/mol]
                * source: Source of thermo data, [kJ/kg·K]
                * elements: list of elements and their total numbers, [-]
        Usage
        -------
            The general usage of calcRxnlogK without the optional argument is as follows:  \n
            (1) Not on steam saturation curve:  \n
                [logK, dGrxn, dGP, dGRs] = AllRxnslogK(TC, P, Prod, dbaccessdic, sourcedic, specielist),  \n
                where TC is temperature in celsius and P is pressure in bar;
            (2) On steam saturation curve:  \n
                [logK, dGrxn, dGP, dGRs] = AllRxnslogK(TC, 'T', Prod, dbaccessdic, sourcedic, specielist),   \n
                where TC is temperature in celsius, followed with a quoted char 'T'  \n
                [logK, dGrxn, dGP, dGRs] = AllRxnslogK(P, 'P', Prod, dbaccessdic, sourcedic, specielist), \n
                where P is pressure in bar, followed with a quoted char 'P'.
            (3) Meanwhile, usage with any specific dielectric constant method ('FGL97') for
                condition not on steam saturation curve is as follows. Default method is 'JN91' \n
                [logK, dGrxn, dGP, dGRs] = AllRxnslogK( TC, P, Prod, dbaccessdic, sourcedic, specielist, Dielec_method = 'FGL97')
        """
        if self.Specie.lower().startswith(('plagio', 'oliv', 'pyroxe', 'alk-')):
            ss = solidsolution_thermo(X = self.X, T = TC, P = P, Dielec_method = self.Dielec_method,
                                      dbaccessdic = self.dbaccessdic, solidsolution_type = self.Specie,
                                      ThermoInUnit = self.ThermoInUnit, rhoEG = rhoEG, Al_Si = self.Al_Si)
            return ss.logK, ss.Rxn
        elif self.Specie.lower() == 'cpx':
            ss = solidsolution_thermo(cpx_Ca = self.cpx_Ca, X = self.X, T = TC, P = P,
                                      dbaccessdic = self.dbaccessdic, Dielec_method = self.Dielec_method,
                                      solidsolution_type = 'cpx', ThermoInUnit = self.ThermoInUnit,
                                      rhoEG = rhoEG, Al_Si = self.Al_Si)
            return ss.logK, ss.Rxn
        elif self.Specie.lower() == 'clay':
            logK, Rxn = calclogKclays(TC, P, *self.elem, dbaccessdic = self.dbaccessdic,
                                      group = self.group, Dielec_method = self.Dielec_method, 
                                      Int_Mg_fract = self.Int_Mg_fract, Int_Li_fract = self.Int_Li_fract,
                                      ThermoInUnit = self.ThermoInUnit, ClayMintype = self.ClayMintype,
                                      heatcap_approx = self.heatcap_approx, **self.rhoEG)
            return logK, Rxn
        else:
            logK, dGrxn, dGP, dGRs = self.RxnlogK( TC, P, self.Specie, rhoEG)
            return logK, dGrxn, dGP, dGRs

    def RxnlogK( self, TC, P, Prod, rhoEG):
        """
        This function calculates logK values of any reaction \n
        Parameters
        ----------
            TC          : temperature [°C] \n
            P           : pressure [bar] \n
            Prod        : Product species of the reaction \n
            dbaccessdic  : direct-acess database dictionary \n
            sourcedic   : source database reactions dictionary \n
            specielist  : source database species grouped into
                            [element, basis, redox, aqueous, minerals, gases, oxides] \n
            Dielec_method    : specify either 'FGL97' or 'JN91' or 'DEW' as the method
                            to calculate dielectric constant, default is 'JN91' \n
            sourceformat: source database format, either 'GWB' or 'EQ36', default is 'GWB'
            heatcap_method : specify either 'SUPCRT' or 'Berman88' or 'HP11' or 'HF76' as the method to calculate thermodynamic properties
                            of any mineral, default is 'SUPCRT' \n
            rhoEG       : dictionary of water properties like  density (rho),
                            dielectric factor (E) and Gibbs Energy  (optional) \n
        Returns
        -------
            logK        : logarithmic K value(s)  \n
            dGrxn       : Total reaction Gibbs energy [cal/mol] \n
            dGP         : Product specie Gibbs energy [cal/mol] \n
            dGRs        : Reactant species Gibbs energy [cal/mol] \n
        Usage
        -------
            The general usage of calcRxnlogK without the optional argument is as follows:  \n
            (1) Not on steam saturation curve:  \n
                [logK, dGrxn, dGP, dGRs] = RxnlogK(TC, P, Prod, dbaccessdic, sourcedic, specielist),  \n
                where TC is temperature in celsius and P is pressure in bar;
            (2) On steam saturation curve:  \n
                [logK, dGrxn, dGP, dGRs] = RxnlogK(TC, 'T', Prod, dbaccessdic, sourcedic, specielist),   \n
                where TC is temperature in celsius, followed with a quoted char 'T'  \n
                [logK, dGrxn, dGP, dGRs] = RxnlogK(P, 'P', Prod, dbaccessdic, sourcedic, specielist), \n
                where P is pressure in bar, followed with a quoted char 'P'.
            (3) Meanwhile, usage with any specific dielectric constant method ('FGL97') for
                condition not on steam saturation curve is as follows. Default method is 'JN91' \n
                [logK, dGrxn, dGP, dGRs] = RxnlogK( TC, P, Prod, dbaccessdic, sourcedic, specielist, Dielec_method = 'FGL97')
        """

        R = 1.9872041 # cal/mol/K
        dGH2O = rhoEG['dGH2O'].ravel()

        TK = convert_temperature( TC, Out_Unit = 'K' )

        if self.sourceformat.upper() == 'EQ36':
            rxnspecies = [j for k,j in enumerate(self.sourcedic[Prod]) if k not in [2,3]]
        elif self.sourceformat.upper() == 'GWB' or self.sourceformat.upper() == 'PHREEQC':
            rxnspecies = self.sourcedic[Prod]

        method = 'SUPCRT' if (self.heatcap_method != 'HP11' and (Prod.endswith(('(g)', ',g')) or
                              self.Specie_class == 'gases')) else self.heatcap_method
        # print(self.heatcap_method, Prod, method)
        if Prod == 'e-' or Prod == 'eh':
            dGP = 0
        elif Prod == 'H2O':
            dGP = dGH2O
        elif Prod in ['Hydroxyapatite', 'Fluorapatite', 'Ankerite', 'Acmite', 'Molybdenite', 'Molybdite'] or Prod.startswith('ss_'):
            if self.heatcap_method != 'HP11': #and self.dbaccessdic[Prod][1].split()[0] in ['H&P2011', 'R&H95']
                dGP = heatcap( T = TC, P = P, Species_ppt = self.dbaccessdic[Prod], method = 'HF76').dG
            else:
                dGP = heatcap( T = TC, P = P, Species_ppt = self.dbaccessdic[Prod], Species = Prod, method = 'HP11').dG
        elif self.specielist is None:
            if (Prod.endswith(('(aq)','+','-')) or Prod[-1].isdigit()):
                dGP  = supcrtaq(TC, P, self.dbaccessdic[Prod.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)').replace('CH4(aq)', 'Methane(aq)')],
                                Dielec_method = self.Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
            else:
                dGP = heatcap( T = TC, P = P, Species_ppt = self.dbaccessdic[Prod], Species = Prod,
                              method = method).dG
        elif (Prod in self.specielist[4] + self.specielist[5] + self.specielist[6]) or (self.Specie_class in ['minerals', 'liquids', 'gases']): #
            dGP = heatcap( T = TC, P = P, Species_ppt = self.dbaccessdic[Prod], Species = Prod,
                          method = method).dG
        else:
            dGP  = supcrtaq(TC, P, self.dbaccessdic[Prod.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)').replace('CH4(aq)', 'Methane(aq)')],
                            Dielec_method = self.Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)

        total_reactants = int(len(rxnspecies[2:])/2)
        dGRs = 0
        for i in range(total_reactants):
            R_coeff = float(rxnspecies[2 + 2*i])
            R_specie = rxnspecies[4 + 2*i - 1]

            method = 'SUPCRT' if (self.heatcap_method != 'HP11' and R_specie.endswith(('(g)', ',g')) ) else self.heatcap_method
            # print(self.heatcap_method, R_specie, method)
            if R_specie == 'e-' or R_specie == 'eh':
                dGR = 0
            elif R_specie == 'H2O':
                dGR = dGH2O
            elif R_specie in ['Hydroxyapatite', 'Fluorapatite', 'Ankerite', 'Acmite', 'Molybdenite', 'Molybdite'] or R_specie.startswith('ss_'):
                if self.heatcap_method != 'HP11':
                    dGR = heatcap( T = TC, P = P, Species_ppt = self.dbaccessdic[R_specie], method = 'HF76').delG
                else:
                    dGP = heatcap( T = TC, P = P, Species_ppt = self.dbaccessdic[R_specie], Species = R_specie, method = 'HP11').dG
            elif self.specielist is None:
                if (R_specie.endswith(('(aq)','+','-')) or R_specie[-1].isdigit()):
                    dGR  = supcrtaq(TC, P, self.dbaccessdic[R_specie.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)').replace('CH4(aq)', 'Methane(aq)')],
                                    Dielec_method = self.Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
                else:
                    dGR = heatcap( T = TC, P = P, Species_ppt = self.dbaccessdic[R_specie], Species = R_specie,
                                  method = method).dG
            elif (R_specie in self.specielist[4] + self.specielist[5] + self.specielist[6]) or R_specie.endswith(('(g)', ',g')):
                dGR = heatcap( T = TC, P = P, Species_ppt = self.dbaccessdic[R_specie], Species = R_specie,
                              method = method).dG
            else:
                dGR  = supcrtaq(TC, P, self.dbaccessdic[R_specie.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)').replace('CH4(aq)', 'Methane(aq)')],
                                Dielec_method = self.Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
            dGRs = dGRs + R_coeff*dGR

        dGrxn = - dGP + dGRs
        logK = (-dGrxn/R/(TK)/np.log(10))

        return logK, dGrxn, dGP, dGRs

    def densitylogKextrap(self, TC, P, rhoEGextrap ):
        """
        This function calculates logK values extrapolation for conditions where rho < 350kg/m3  \n
        Parameters
        ----------
            TC          : temperature [°C] \n
            P           : pressure [bar] \n
            rhoEGextrap : dictionary of water properties like  density (rho), dielectric factor (E) and
                            Gibbs Energy for density region 350-550kg/m3 \n
        Returns
        -------
            logK        : extrapolated logarithmic K value(s)  \n
        Usage
        -------
            [logK] = densitylogKextrap(TC, P, 'H2S(aq)', dbaccessdic = dbaccessdic, sourcedic = sourcedic, specielist = specielist),  \n
        """

        length = len(TC)
        logK = np.nan*np.ones(np.size(TC))
        for i in range(length): #need a for loop because calculation is T-specific
            rhotarget =  iapws95(T = TC[i], P = P[i]).rho
            rhotarget = rhotarget/1000     # kg/m3 => g/cm^3
            Pextrap = rhoEGextrap['%d_%d' % (TC[i], P[i])]['Pextrap']
            Textrap = rhoEGextrap['%d_%d' % (TC[i], P[i])]['Textrap']
            rhoextrap = rhoEGextrap['%d_%d' % (TC[i], P[i])]['rho']
            rhoextrap = rhoextrap/1000     # kg/m3 => g/cm^3
            rhoextrap = np.around(rhoextrap, 3)
            rhoEGextrap_only = rhoEGextrap['%d_%d' % (TC[i], P[i])]
            logrho = np.log10(rhoextrap)
            logKextrap = self.AllRxnslogK( Textrap, Pextrap, rhoEGextrap_only)[0]
            p = np.polyfit(logrho, logKextrap, 1)
            logK[i] = np.polyval(p, np.log10(rhotarget))

        return logK

def outputfmt(fid, logK, Rxn, *T, dataset = None, logK_form = None):
    """
    This function writes logK and Rxn data to any file using GWB, EQ36, PHREEQC, Pflotran and ToughReact format

    Parameters
    ----------
        fid : string
            file ID
        logK : float, vector
            logarithmic K value(s)
        Rxn : dict
            dictionary of reaction thermodynamic properties
        T : float, vector
            Temperature value(s), optional, required when 'polycoeffs' is specified for logK_form
        dataset : string
            specify the dataset format, either 'GWB', 'EQ36', 'PHREEQC', 'Pflotran' or 'ToughReact'
        logK_form : string
            specify the format of logK either as a set of eight values one for each of the dataset's principal temperatures, or blocks of polynomial coefficients,  [values, polycoeffs], default is 'a set of eight values' (optional)

    Returns
    -------
        Output data to the file with filename described in fid with any format mentioned above.

    Examples
    --------
    >>> fid = open('./logK_details.txt', 'w')
    >>> logKRxn = calcRxnlogK(T = 100, P = 'T', X = 0.634,
                              Specie = 'Plagioclase', densityextrap = True)
    >>> # output in EQ36 format
    >>> outputfmt(fid, logKRxn.logK, logKRxn.Rxn, dataset = 'EQ36')
    >>> fid.close()

    """

    if len(T) == 0:
        TK = 25*np.ones(np.size(logK))
    else:
        TK = np.asarray(T).ravel()
    logK_form = 'values' if logK_form is None else logK_form.lower()

    # Open the text file.
    if dataset.lower() == 'gwb':
        fid.writelines("%s                       " % Rxn['name'])
        fid.writelines( "%s= " %  list(Rxn.keys())[0])
        if Rxn['type'].find('plag') == 0:
            fid.writelines( "plagioclase\n")
        else:
            fid.writelines( "%s\n" %  Rxn['type'])
        fid.writelines( "     %s= " %  list(Rxn.keys())[2])
        fid.writelines( "%s\n" %  Rxn['formula'])
        fid.writelines( "     mole vol.=   %1.3f cc" %  Rxn['V'])
        fid.writelines( "      mole wt.=  %1.4f g\n" %  Rxn['MW'])
        fid.writelines( "     %s species in reaction\n" %  Rxn['nSpec'])
        for i in range(len(Rxn['spec'])):
            i = i + 1
            fid.writelines( "%9.4f " %  Rxn['coeff'][i-1])
            fid.writelines( "%-9s          " %  Rxn['spec'][i-1])
            if (i % 3 == 0) | (i % 6 == 0) | (i == len(Rxn['spec'])):
                fid.writelines( "\n")

        if logK_form.lower() == 'polycoeffs':
            Tr = 298.15
            logKfunc = lambda TK, *x: x[0] + x[1]*(TK - Tr) + x[2]*(TK**2 - Tr**2) +  x[3]*((1/TK) - (1/Tr)) + \
                x[4]*((1/TK**2) - (1/Tr**2)) + x[5]*np.log(TK/Tr)
            x0 = [-31.9605, 20.6576, 3.73497e-2, -9.01862, 6.0111, 2.5]
            logKcorr = curve_fit(logKfunc, TK[logK!=500].ravel(), logK[logK!=500].ravel(), p0 = x0,  maxfev = 1000000)[0]
            fid.writelines('     a= %15.9f   ' % logKcorr[0] + 'b= %15.9f   ' % logKcorr[1] + \
                            'c= %15.6e\n' % logKcorr[2])
            fid.writelines('     d= %15.6f   ' % logKcorr[3] + 'e= %15.5f   ' % logKcorr[4] + \
                            'f= %15.8f \n' % logKcorr[5])
            fid.writelines('     TminK= %-15.2f ' % np.min(TK) + 'TmaxK= %-7.2f\n' % np.max(TK))
        else:
            for i in range(len(logK)):
                i = i + 1
                if (i == 1) | (i == 5) | (i == 9) | (i == 13) | (i == 17):
                    fid.writelines("       %9.4f" %  logK[i-1])
                else:
                    fid.writelines("  %9.4f" %  logK[i-1])
                if (i % 4 == 0) | (i == 8) | (i == len(logK)):
                    fid.writelines( "\n")

        fid.writelines( "*    gflag = 1 [reported delG0f used]\n" )
        if Rxn['type'].find('plag') == 0:
            fid.writelines( "*    extrapolation algorithm: supcrt92 [92joh/oel]\n" )
        else:
            fid.writelines( "*    extrapolation algorithm: supcrt92/water95\n" )
        if Rxn['type'].find('serp') == 0:
            fid.writelines( "*    reference-state data source = Blanc et al 2015\n" )
        elif 'source' in Rxn:
            fid.writelines( "*    reference-state data source = %s\n" % Rxn['source'])
        else:
            fid.writelines( "*    reference-state data source = supcrt92?\n" )

        fid.write( "*         delG0f =   %8.3f  kcal/mol\n" % (Rxn['min'][2]/1000) )
        if Rxn['type'] == 'Smectites':
            fid.writelines( "*         delH0f =   %8.3f  kcal/mol\n" % (Rxn['min'][3]/1000) )
        else:
            fid.writelines( "*         delH0f =   NaN  kcal/mol\n")
        fid.writelines( "*         S0PrTr =   %8.3f  cal/mol\n" % Rxn['min'][4])
        fid.writelines( "\n")
    elif dataset.lower() == 'eq36':
        fid.writelines('%-25s %s \n' % (Rxn['name'], Rxn['formula']))
        fid.writelines('     sp.type =  solid\n')
        fid.writelines('*    EQ3/6   =  com, alt, sup\n')
        fid.writelines('     revised =  01-Jan-2020\n')
        fid.writelines('*    mol.wt. =%8.3f g/mol\n' % Rxn['MW'])
        fid.writelines('     V0PrTr  = %8.3f cm**3/mol [source: %s ]\n' % (Rxn['V'], Rxn['source']))
        fid.writelines('****\n')
        fid.writelines( "     %s element(s):\n" % int(len(Rxn['elements'])/2))
        for i in range(len(Rxn['elements'])):
            i = i + 1
            if (i == 1) | (i == 7) | (i == 13):
                fid.writelines( "    %9.4f " %  float(Rxn['elements'][i - 1]))
            elif i % 2 != 0:
                fid.writelines( "%9.4f " %  float(Rxn['elements'][i - 1]))
            else:
                fid.writelines( "%-9s     " %  (Rxn['elements'][i - 1]))
            if (i % 6 == 0) | (i == len(Rxn['elements'])):
                fid.writelines( "\n")
        fid.writelines('****\n')
        fid.writelines( "     %s species in reaction:\n" % (Rxn['nSpec'] + 1))
        fid.writelines( "  %9.4f " %  (-1))
        fid.writelines( " %-21s     " %  Rxn['name'])
        for i in range(len(Rxn['spec'])):
            i = i + 1
            fid.writelines( "  %9.4f " %  Rxn['coeff'][i-1])
            fid.writelines( " %-21s     " %  Rxn['spec'][i-1])
            if (i % 2 != 0) | (i == len(Rxn['spec'])):
                fid.writelines( "\n")
        fid.writelines('*\n')
        fid.writelines('**** logK grid [T, P @ Miscellaneous parameters]\n')
        for i in range(len(logK)):
            i = i + 1
            if (i == 1) | (i == 5) | (i == 9) | (i == 13) | (i == 17):
                fid.writelines( "      %9.4f" %  logK[i-1])
            else:
                fid.writelines( "  %9.4f" %  logK[i-1])
            if (i % 4 == 0) | (i == len(logK)):
                fid.writelines( "\n")
        fid.writelines( "*    gflag = 1 [reported delG0f used]\n" )
        if Rxn['type'].find('plag') == 0:
            fid.writelines( "*    extrapolation algorithm: supcrt92 [92joh/oel]\n" )
        else:
            fid.writelines( "*    extrapolation algorithm: supcrt92/water95\n" )
        if Rxn['type'].find('serp') == 0:
            fid.writelines( "*    ref-state data  [source:   Blanc et al 2015 ]\n" )
        elif 'source' in Rxn:
            fid.writelines( "*    ref-state data  [source:   %s ]\n" % Rxn['source'])
        else:
            fid.writelines( "*    ref-state data  [source:   supcrt92? ]\n" )
        fid.writelines( "*         delG0f =   %8.3f  kcal/mol\n" % (Rxn['min'][2]/1000) )
        if Rxn['type'] == 'Smectites':
            fid.writelines( "*         delH0f =   %8.3f  kcal/mol\n" % (Rxn['min'][3]/1000) )
        else:
            fid.writelines( "*         delH0f =   NaN  kcal/mol\n")
        fid.writelines( "*         S0PrTr =   %8.3f  cal/(mol*K)\n" % Rxn['min'][4])
        fid.writelines( "*    Cp coefficients [source:   %s  ]\n" % Rxn['source'])
        fid.writelines( "*         T**0   =   %11.8e  \n" % (Rxn['min'][6]) )
        fid.writelines( "*         T**1   =   %11.8e  \n" % (Rxn['min'][7]))
        if Rxn['min'][8] < 1:
            fid.writelines( "*         T**-2  =  %12.8e  \n" % (Rxn['min'][8]))
        else:
            fid.writelines( "*         T**-2  =   %11.8e  \n" % (Rxn['min'][8]))
        if len(Rxn['min']) > 10:
            fid.writelines( "*         T**-0.5 =   %11.8e  \n" % (Rxn['min'][9]))
            fid.writelines( "*         T**2   =   %11.8e  \n" % (Rxn['min'][10]))
        fid.writelines( "+" + "-"*68 + "\n")
    elif dataset.lower() == 'phreeqc':
        fid.writelines("%s                       " % Rxn['name'] + "\n")

        lhs_terms = [Rxn['formula'].replace('FeIII', 'Fe')]  # start with the mineral formula
        rhs_terms = []

        for n in range(len(Rxn['coeff'])):
            coeff = Rxn['coeff'][n]
            specie = denormalize_phreeqc_species_charge(Rxn['spec'][n])

            # Absolute value of coefficient for display
            abs_coeff = abs(coeff)

            # Format term (skip coefficient if it's 1)
            if abs_coeff == 1.0:
                term = f"{specie}"
            else:
                term = f"{abs_coeff:.4f}{specie}"

            # Negative coeffs go to LHS, positive coeffs go to RHS
            if coeff < 0:
                lhs_terms.append(term)
            else:
                rhs_terms.append(term)

        # Join LHS and RHS with " + "
        to_write = " + ".join(lhs_terms) + " = " + " + ".join(rhs_terms)
        
        fid.writelines(to_write + "\n")

        logKfunc = lambda TK, *x: x[0] + x[1]*TK + x[2]*TK**(-1) + x[3]*np.log10(TK) + x[4]*TK**(-2) #+ x[5]*TK**(2) 
        x0 = [2.06576e2, 3.73497e-2, -9.01862e3, -3.19605e1, 6.0111e5]
        logKcorr = curve_fit(logKfunc, TK[logK != 500].ravel(), logK[logK != 500].ravel(), p0 = x0,  maxfev = 1000000)[0]
        
        info = "  " + " ".join("%9.5f" % e for e in logKcorr)
        logK25 = logKfunc(convert_temperature( 25, Out_Unit = 'K' ), *logKcorr)

        fid.writelines(f"     -log_k  {logK25:.3f}\n")
        fid.writelines(f"     -analytic  {info}\n")

        fid.writelines(f"     -log_k  {Rxn['V']:.3f}\n")
        if Rxn['type'].find('plag') == 0:
            fid.writelines( "     #    extrapolation algorithm: supcrt92 [92joh/oel]\n" )
        else:
            fid.writelines( "     #    extrapolation algorithm: supcrt92/water95\n" )
        if Rxn['type'].find('serp') == 0:
            fid.writelines( "     #    reference-state data source = Blanc et al 2015\n" )
        elif 'source' in Rxn:
            fid.writelines( "     #    reference-state data source = %s\n" % Rxn['source'])
        else:
            fid.writelines( "     #    reference-state data source = supcrt92?\n" )
        fid.writelines( "\n")
    elif dataset.lower() == 'pflotran':
        list_logk = ' '.join(str("%9.4f" % e) for e in list(logK))
        Rxns_lst = ' '.join([ "%8.4f" % Rxn['coeff'][i]+' ' + "'%s'" % Rxn['spec'][i]
                             for i in range(len(Rxn['spec']))])
        info = "'%s'" % Rxn['name'] + ' ' + "%7.3f" % Rxn['V'] + ' ' + str(Rxn['nSpec']) + ' ' + \
            Rxns_lst + ' ' + list_logk + ' ' + "%8.4f" % Rxn['MW']
        fid.writelines('%s\n' % info)
    elif dataset.lower() == 'toughreact':
        logKfunc = lambda TK, *x: x[0]*np.log(TK) + x[1] + x[2]*TK + x[3]*TK**(-1) + x[4]*TK**(-2)
        x0 = [-3.19605e1, 2.06576e2, 3.73497e-2, -9.01862e3, 6.0111e5]
        logKcorr = curve_fit(logKfunc, TK[logK!=500].ravel(), logK[logK!=500].ravel(), p0 = x0,  maxfev = 1000000)[0]
        list_logk = '  '.join(str("%9.4f" % e) for e in list(logK))
        list_logKcorr = ' '.join(str("%.5e" % e) for e in list(logKcorr))
        Rxns_spec = [j.replace('++++', '+4') if j.endswith('++++',0)
                      else j.replace('+++', '+3') if j.endswith('+++',0)
                      else j.replace('++', '+2') if j.endswith('++',0)
                      else j.replace('----', '-4') if j.endswith('----',0)
                      else j.replace('---', '-3') if j.endswith('---',0)
                      else j.replace('--', '-2') if j.endswith('--',0) else j for j in Rxn['spec']]
        Rxn_lst = '  '.join([ "%8.4f" % Rxn['coeff'][i]+' ' + "'%s'" % Rxns_spec[i] for i in range(len(Rxn['spec']))])

        info = "%-32s" % Rxn['name'] + "%8.3f" % Rxn['MW'] + " %7.3f" % Rxn['V'] +\
            ' ' + str(Rxn['nSpec']) + ' ' + Rxn_lst
        info = "'%s'" % info[:len(info.split()[0])] + info[len(info.split()[0]) + 2:]
        fid.writelines('%s\n' % info)
        info = '%-35s' % Rxn['name'] + ' ' + list_logk
        info = "'%s'" % info[:len(info.split()[0])] + info[len(info.split()[0]) + 2:]
        fid.writelines('%s\n' % info)
        info = '%-35s' % Rxn['name'] + '  ' + list_logKcorr.replace('e','E')
        info = "'%s'" % info[:len(info.split()[0])] + info[len(info.split()[0]) + 2:]
        fid.writelines('%s\n' % info)

    return

class write_database():
    """
    Class to write the new database for either GWB, EQ3/6, ToughReact, Pflotran or PHREEQC into
    a new folder called "output"   \n
    Parameters
    ----------
        T : float, vector
            Temperature [°C]   \n
        P : float, vector
            Pressure [bar]   \n
        cpx_Ca : string
            number of moles of Ca in solid solution of clinopyroxene (optional) if it is ommitted solid solution of clinopyroxene will not be included, 0 < nCa >=1   \n
        solid_solution : string, bool
            specify the inclusion of solid-solution [Yes/True or No/False], default is 'No'   \n
        clay_thermo : float, vector
            specify the inclusion of clay thermodynamic properties [Yes/True or No/False], default is 'No'   \n
        logK_form : float, vector
            specify the format of logK either as a set of eight values one for each of the dataset’s principal temperatures, or blocks of polynomial coefficients, [values, polycoeffs] default is 'a set of eight values'   \n
        densityextrap : float, vector
            specify the utilization of density extrapolation [Yes/True or No/False], default is 'Yes'   \n
        dbaccess : string
            direct-access database filename and location  (optional)  \n
        dbBerman_dir : string
            filename and location of the Berman mineral database (optional)     \n
        dbHP_dir : string
            filename and location of the supcrtbl mineral and gas database, optional
        dbaccessformat : string, optional
            specify the direct-access/sequential-access database format, either 'speq' or 'supcrtbl', default is 'speq'
        sourcedb : string
            source database filename and location  (optional)  \n
        sourceformat : string
            source database format, either 'GWB', 'EQ36' or 'PHREEQC', default is 'GWB'
        sourcedb_codecs : string
            specify the name of the encoding used to decode or encode the sourcedb file, optional
        objdb : string
            new database filename and location    (optional) \n
        co2actmodel : string
            co2 activity model equation [Duan_Sun or Drummond]  (optional), if not specified, default is 'Drummond'   \n
        Dielec_method : string
            specify either 'FGL97' or 'JN91' or 'DEW' as the method to calculate dielectric constant, default is 'JN91'   (optional) \n
        heatcap_method : string
            specify either 'SUPCRT' or 'Berman88'  or 'HP11' or 'HF76' the method to calculate thermodynamic properties of any mineral, default is 'SUPCRT' \n
        ThermoInUnit : string
            specify either 'cal' or 'KJ' as the input units for species properties (optional), particularly used to covert KJ data to cal by supcrtaq function if not specified default - 'cal'
        dataset : string
            specify the dataset format, either 'GWB', 'EQ36', 'PHREEQC', 'Pflotran' or 'ToughReact', default is old GWB database ['GWB'] (optional) \n
        print_msg : string, bool
            print debug message [True or False], default is False   \n

    Returns
    -------
        Output the new database to an ASCII file with filename described in 'objdb' if specified.

    Usage
    -------
      With any Temperature and Pressure:
        (1) General format with default dielectric constant and CO2 activity model and exclusions
            of solid solutions for GWB   \n
            write_database(T = T, P = P, cpx_Ca = nCa, dataset = 'GWB', sourceformat = 'GWB')   \n
        (2) Inclusion of solid solutions and exclusion of solid solution of clinopyroxene and clay thermo  \n
            write_database(T = T, P = P, solid_solution = 'Yes', clay_thermo = 'Yes', dataset = 'GWB', sourceformat = 'GWB')   \n
        (3) Inclusion of all solid solutions and clay thermo with \emph{'Duan_Sun'} CO2 activity model and
            'FGL97' dielectric constant calculation \n
            write_database(T = T, P = P, cpx_Ca = nCa, solid_solution = 'Yes', clay_thermo = 'Yes', co2actmodel = 'Duan_Sun', Dielec_method = 'FGL97', dataset = 'GWB', sourceformat = 'GWB')   \n
      With any Temperature or Pressure on the steam saturation curve:
        (4) General format with default dielectric constant and CO2 activity model  \n
            write_database(T = T, P = 'T', cpx_Ca = nCa, dataset = 'GWB', sourceformat = 'GWB'),   \n
            where T is temperature in celsius and P is assigned a quoted character 'T' to reflect steam saturation pressure  \n
            write_database(P = P, T = 'P', cpx_Ca = nCa, dataset = 'GWB', sourceformat = 'GWB'),   \n
            where P is pressure in bar and T is assigned a quoted character 'P' to reflect steam saturation temperature

    Examples
    --------
    >>> write_database(T=np.array([ 0.010, 25., 60., 100., 150.,  200.,
                                   250.,  300.]), P=200, cpx_Ca = 0.5,
                       sourceformat = 'GWB', solid_solution = True,
                       clay_thermo = True, dataset = 'GWB')  \n
    >>> write_database(T=np.array([ 0.010, 25., 60., 100., 150.,  200.,  250.,
                                   300.]), P=200, cpx_Ca = 0.5,
                       sourceformat = 'GWB', solid_solution = True,
                       clay_thermo = True, dataset = 'Pflotran',
                       sourcedb = './pygcc/default_db/thermo.2021.dat')  \n
    """

    kwargs = {
            "T": None,                  # float/array - temperature
            "P": None,                  # float/array - pressure
            "cpx_Ca": None,             # float - number of moles of Ca in formula unit
            "solid_solution": None,     # bool - is solid solution
            "clay_thermo": None,        # bool/vector? - include clay thermodynamic properties
            "logK_form": None,          # float, vector - format of logK 
            'dbBerman_dir': None,       # string opt - filename and location of berman mineral database
            'dbHP_dir': None,           # string opt - filename and location of the supcrtbl mineral and gas database
            "dbaccess": None,           # string - direct-access database filename and location
            "sourcedb": None,           # string opt - source database filename and location
            "objdb": None,              # string opt - new database filename and location
            "ThermoInUnit": 'cal',      
            "co2actmodel": None,        # string opt - co2 activity model equation (Duan-Sun or Drummond), defaults to Drummond
            "Dielec_method": None,      # string opt - way to calculate dielectric constant
            "heatcap_method": None,     # string opt - specifiy method to calculate thermo properties of any mineral (‘SUPCRT’ or ‘Berman88’ or ‘HP11’ or ‘HF76’)
            "dataset": None,            # string opt - dataset format (‘GWB’, ‘EQ36’, ‘PHREEQC‘, ‘Pflotran’ or ‘ToughReact’)
            "sourceformat": None,       # string opt - (‘GWB’ or ‘EQ36’ or ‘PHREEQC‘)
            'densityextrap': None,      # bool opt - utilization of density extrapolation, default is 'Yes'
            "sourcedb_codecs": None,    # string opt - name of encoding used to decode/encode sourcedb file
            "dbaccessformat": 'speq',   
            "print_msg": False          # string, bool - print debugging message 
        }

    def __init__(self, **kwargs):
        self.kwargs = write_database.kwargs.copy()
        self.kwargs.update(kwargs)

        # Required args
        self.T = self.kwargs["T"]
        self.P = self.kwargs["P"]
        self.dbaccessformat = self.kwargs.get("dbaccessformat")
        self.dbBerman_dir   = self.kwargs.get("dbBerman_dir")
        self.dbHP_dir       = self.kwargs.get("dbHP_dir")
        self.dataset        = self.kwargs.get("dataset", "") #.upper()
        self.objdb          = self.kwargs.get("objdb")
        self.co2actmodel    = self.kwargs.get("co2actmodel")
        self.ThermoInUnit   = self.kwargs.get("ThermoInUnit")
        self.sourcedb_codecs = self.kwargs.get("sourcedb_codecs")
        self.Dielec_method  = self.kwargs.get("Dielec_method")      
        self.cpx_Ca         = self.kwargs.get("cpx_Ca")
        self.logK_form      = self.kwargs.get("logK_form")
        self.heatcap_method = self.kwargs.get("heatcap_method")
        self.dbaccess       = self.kwargs.get("dbaccess")
        self.sourceformat   = self.kwargs.get("sourceformat")

        self.__calc__(**kwargs)

    def __calc__(self, **kwargs):

        # Direct-access database
        if self.dbaccess is None:
            self.dbaccess = os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_db/speq21.dat")


        # Source format
        if self.sourceformat is None:
            if self.dataset == "GWB":
                self.sourceformat = "GWB"
            elif self.dataset == "EQ36":
                self.sourceformat = "EQ36"
            elif self.dataset == "PHREEQC":
                self.sourceformat = "PHREEQC"
            else:
                self.sourceformat = ""


        # Source DB selection
        self.sourcedb = self._resolve_sourcedb(self.sourceformat, self.kwargs.get("sourcedb") )


        # Options
        self.solid_solution = self._flag_to_yesno(self.kwargs.get("solid_solution"), default="No")
        self.clay_thermo    = self._flag_to_yesno(self.kwargs.get("clay_thermo"), default="No")
        self.densityextrap  = self._flag_to_yesno(self.kwargs.get("densityextrap"), default="Yes")

        self.Dielec_method = 'JN91' if self.Dielec_method is None else self.Dielec_method

        self.heatcap_method = 'HP11' if self.dbHP_dir is not None else 'Berman88' if self.dbBerman_dir is not None else 'SUPCRT' if self.heatcap_method is None else self.heatcap_method
        self.logK_form      = 'values' if self.logK_form is None else self.logK_form
        self.cpx_Ca         = 0 if self.cpx_Ca is None else self.cpx_Ca
        
        # Read DB        
        self.dbr = db_reader(dbaccess = self.dbaccess, dbBerman_dir = self.dbBerman_dir,
                             dbHP_dir = self.dbHP_dir, dbaccessformat = self.dbaccessformat,
                             sourcedb = self.sourcedb, sourceformat = self.sourceformat,
                             sourcedb_codecs = self.sourcedb_codecs)
        # condition to add Dimer from Sverjensky et al. 2014 to SPEQ database
        # if self.dbHP_dir is None or self.dbBerman_dir is None:
        # print("print database name", self.dbHP_dir)
        # Check for Sverjensky Si2O4 requirement
        # if self.dbr.header_ref[self.dbr.dbaccessdic['SiO2(aq)'][1].strip(' ref:').split('   ')[0]].startswith('Sverjensky, D. A., Harrison, B., & Azzolini, D., 2014'):
        #     if 'Si2O4(aq)' not in self.dbr.dbaccessdic.keys() or 'Si2O4(aq)' not in self.dbr.sourcedic.keys():
        #         warnings.warn('Warning: you are using SiO2(aq) data from Sverjensky et al. (2014) GCA. This thermodynamic model requires that you also add data for Si2O4(aq) to achieve accurate solubility calculations. Please ensure thermodynamic data for Si2O4(aq) are added to both your source GWB or EQ3/6 database AND your source direct-access database.')
        
        si_entry = self.dbr.dbaccessdic.get("SiO2(aq)")
        if si_entry:
            ref_key = si_entry[1].strip(" ref:").split("   ")[0]
            if self.dbr.header_ref[ref_key].startswith("Sverjensky, D. A., Harrison, B., & Azzolini, D., 2014"):
                if "Si2O4(aq)" not in self.dbr.dbaccessdic.keys() and "Si2O4(aq)" not in self.dbr.sourcedic.keys():
                    warnings.warn(
                        "Warning: Using SiO2(aq) data from Sverjensky et al. (2014) GCA. "
                        "This thermodynamic model requires that you also add data for Si2O4(aq) to achieve accurate solubility calculations."
                        "Please ensure thermodynamic data for Si2O4(aq) are added to both your source GWB or EQ3/6 database AND your source direct-access database."
                    )

        # Handle P/T arrays
        self._process_PT()

        # Write dataset-specific DB
        if self.dataset.upper() == 'GWB':
            self.write_GWBdb(self.T, self.P)
        elif self.dataset.upper() == 'EQ36':
            self.write_EQ36db(self.T, self.P )
        elif self.dataset.upper() == 'PHREEQC':
            self.write_PHREEQCdb(self.T, self.P )
        elif self.dataset.lower() == 'pflotran':
            self.write_pflotrandb(self.T, self.P )
        elif self.dataset.lower() == 'toughreact':
            self.write_ToughReactdb(self.T, self.P )

        # Build message
        self._build_message()

    # --------------------------------------------------- Helpers --------------------------------------------------- #
    def _resolve_sourcedb(self, sourceformat, sourcedb):
        """
            Resolve default source database based on format and user input.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if sourceformat.lower() == "gwb":
            mapping = {
                "thermo.com": "thermo.com.dat",
                "thermo.2021": "thermo.2021.dat",
                "thermo_latest": "thermo_latest.tdat",
                "thermo_cemdata_mar": "thermo_cemdata_mar.tdat",
                None: "thermo.com.tdat",   # fallback 
            }
            fname = mapping.get(sourcedb, sourcedb)
        elif sourceformat.lower() == "eq36":
            fname = "data0.dat" if sourcedb in (None, "data0") else sourcedb
        elif sourceformat.lower() == "phreeqc":
            fname = "phreeqc.dat" if sourcedb in (None, "phreeqc") else sourcedb
        else:
            fname = sourcedb
        return os.path.join(base_dir, "default_db", fname)

    def _flag_to_yesno(self, value, default="No"):
        """
            Convert boolean/None/custom flag to Yes/No string.
        """
        if value is True:
            return "Yes"
        elif value is False or value is None:
            return default
        return value

    def _process_PT(self):
        """Process temperature and pressure arrays safely."""
        # Handle cases where P or T given as 'T' or 'P'
        if isinstance(self.P, str) or isinstance(self.T, str):
            if self.P == "T":
                self.T = self._expand_temperature(self.T)
                self.P = iapws95(T = self.T).P
                self.P[np.isnan(self.P) | (self.P < 1)] = 1.0133
            elif self.T == "P":
                self.T = iapws95(P = self.P).TC

        # Expand temp range if needed
        self.T = self._expand_temperature(self.T)

        # Expand P to match T
        if np.size(self.P) <= 2:
            self.P = np.ravel(self.P)
            self.P = self.P[0] * np.ones(np.size(self.T))

    def _expand_temperature(self, T):
        """
            Expand temperature input into proper array.
        """
        if np.ndim(T) == 0:
            T = np.ravel(T)
        elif np.size(T) == 2:
            if T[-1] > 400:
                # for critical region of water (350 - 400C)
                return np.array([0.01 if (x == 0)&(T[0] == 0)
                              else T[0] if (x == 0)&(T[0] != 0)
                              else roundup_hundredth(T[0] + x*(T[-1] - T[0])/(8 - 1)) if 350 <= (T[0] + x*(T[-1] - T[0])/(8 - 1)) <= 400
                              else round(T[-1]) if x == 7
                              else roundup_tenth(T[0] + x*(T[-1] - T[0])/(8 - 1))
                              for x in range(8)])
            elif T[-1] > 350:
                return np.array([0.01 if (x == 0)&(T[0] == 0)
                              else T[0] if (x == 0)&(T[0] != 0)
                              else roundup_hundredth(T[0] + x*(T[-1] - T[0])/(8 - 1)) if 350 <= (T[0] + x*(T[-1] - T[0])/(8 - 1)) <= 400
                              else roundup_tenth(T[0] + x*(T[-1] - T[0])/(8 - 1))
                              for x in range(8)])
            else:
                return np.array([roundup_tenth(j) if j != 0 else 0.01 for j in np.linspace(T[0], T[-1], 8)])


    def _build_message(self):
        """Construct final success message."""
        # Use basename instead of regex splitting
        fname = os.path.basename(self.sourcedb)

        self.msg = (
            "Database for %s generated successfully using %s dielectric constant, "
            "%s %s source database"
            % (
                self.dataset.upper(),
                self.Dielec_method,
                fname,
                self.sourceformat,
            )
        )

        if self.cpx_Ca != 0:
            self.msg += ", full solid solution included"
        elif self.solid_solution == "Yes":
            self.msg += ", solid solution included with cpx excluded"
        if self.clay_thermo == "Yes":
            self.msg += ", clay thermodynamics included"

        if self.kwargs.get("print_msg", False):
            print(self.msg)

    def write_GWBdb(self, T, P ):
        """
        This function writes the new GWB database into a new folder called "output"   \n
        Parameters
        ----------
            T               :    temperature [°C]   \n
            P               :    pressure [bar]   \n

        Returns
        -------
            Outputs the new database to an ASCII file with filename described in 'objdb'.   \n
        Usage
        -------
         Example:
             (1) General format with default dielectric constant and CO2 activity model and exclusions
                 of solid solutions   \n
                 write_GWBdb(T, P)   \n
             (2) Inclusion of solid solutions and clay thermo and exclusion of solid solution of clinopyroxene  \n
                 write_GWBdb(T, P)   \n
             (3) Inclusion of all solid solutions and clay thermo with \emph{'Duan_Sun'} CO2 activity model and 'JN91'
                 dielectric constant calculation \n
                 write_GWBdb(T, P)   \n
        """

        nCa_cpx = self.cpx_Ca;                     logK_form = self.logK_form
        solid_solution = self.solid_solution;      clay_thermo = self.clay_thermo
        sourcedb = self.sourcedb
        objdb = self.objdb;                        Dielec_method = self.Dielec_method
        co2actmodel = self.co2actmodel;            sourceformat = self.sourceformat
        heatcap_method = self.heatcap_method;
        densityextrap = self.densityextrap

        dbaccessdic, dbname, sourcedic, specielist = self.dbr.dbaccessdic, self.dbr.dbaccess, self.dbr.sourcedic, self.dbr.specielist
        MWdic, act_param, chargedic = self.dbr.MWdic, self.dbr.act_param, self.dbr.chargedic
        sourcedb_codecs = self.dbr.sourcedb_codecs if self.sourcedb_codecs is None else self.sourcedb_codecs
        activity_model = act_param['activity_model']

        if sourceformat.upper() == 'GWB':
            Mineraltype, fugacity_info = self.dbr.Mineraltype, self.dbr.fugacity_info
            # fugacity_model = fugacity_info['fugacity_model']
        elif sourceformat.upper() == 'EQ36':
            block_info, Elemlist = self.dbr.block_info, self.dbr.Elemlist

        if sourceformat.upper() == 'EQ36':
            dataset = 'tdat'
            dataset_format =  'apr20'
        else:
            dataset = sourcedb.split('.')[-1]
            dataset_format =  act_param['dataset_format']

        logK_form = 'values' if (logK_form is None) | (dataset_format in ['oct94', 'jul17']) else logK_form.lower()

        if Dielec_method.upper() == 'DEW':
            water = ZhangDuan(T = T, P = P)
            rho, dGH2O, dHH2O, SH2O = water.rho, water.G, np.nan*np.ones(len(T)), np.nan*np.ones(len(T))
        else:
            water = iapws95(T = T, P = P)
            rho, dGH2O, dHH2O, SH2O = water.rho, water.G, water.H, water.S

        TK = convert_temperature( T, Out_Unit = 'K' )

        if dataset_format in ['jan19', 'apr20', 'mar21'] and logK_form.lower() == 'polycoeffs':
            Tr = 298.15
            logKfunc = lambda TK, *x: x[0] + x[1]*(TK - Tr) + x[2]*(TK**2 - Tr**2) +  x[3]*((1/TK) - (1/Tr)) + \
                x[4]*((1/TK**2) - (1/Tr**2)) + x[5]*np.log(TK/Tr)
            x0 = [-31.9605, 20.6576, 3.73497e-2, -9.01862, 6.0111, 2.5]

        if os.path.exists(os.path.join(os.getcwd(), 'output/GWB')) == False:
            os.makedirs(os.path.join(os.getcwd(), 'output/GWB'))

        periodic_table = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           'PeriodicTableJSON.json'), encoding='utf8')
        data = json.load(periodic_table)
        Element = {data['elements'][x]['symbol'] : pd.DataFrame([data['elements'][x]['name'],
                                                                 data['elements'][x]['atomic_mass']],
                                                                index = ['name', 'mass']).T
                   for x in range(len(data['elements']))}
        periodic_table.close()

        fid = open(sourcedb, 'r', encoding = sourcedb_codecs)

        missing_species = []
        elemspeclist = [ symbol for x in specielist[0] for symbol, item in Element.items()
                        if item.name[0][:5] == x[:5] ] if sourceformat.upper() == 'GWB' else specielist[0]

        form_del = [1] if sourceformat.upper() == 'GWB' else [1, 3, 4]
        all_species_source = [[i]+k for i, k in sourcedic.items()
                              if i not in (['eh', 'e-', 'H2O']) or (dataset_format == 'mar21' and i not in specielist[6])]

        # all_species_source = [x.split()[0] if (dataset_format == 'mar21' and k in specielist[6])
        #                       else [i]+k
        #                       for i, k in sourcedic.items() for x in k if i not in (['eh', 'e-', 'H2O']) or (dataset_format == 'mar21' and k in specielist[6] and x.strip('\n') and x.split()[0] not in ['a0', '*'] ) ]
        all_species_source = [[k for j, k in enumerate(all_species_source[i])
                               if (j not in form_del and k not in elemspeclist and str(k).strip('0123456789.- ') != '') ]
                              if  (i <= len(specielist[0]))
                              else [k for j, k in enumerate(all_species_source[i])
                                    if (j not in form_del and str(k).strip('0123456789.- ') != '') ]
                              for i in range(len(all_species_source)) ]
        for num in range(len(all_species_source)): #
            if num < len(all_species_source):
                if dataset_format == 'mar21':
                    lst = [v for v in all_species_source[num] if v not in (specielist[6] + ['eh', 'e-', 'H2O']) ]
                else:
                    lst = [v for v in all_species_source[num] if v not in (['eh', 'e-', 'H2O']) ]

                bool_miss = [x.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
                             not in dbaccessdic.keys() for x in lst  ]
                if any(bool_miss):
                    sublist = [i for (i, v) in zip(lst, bool_miss) if v ]
                    if lst[0] not in sublist:
                        missing_species.append([lst[0]] + sublist)
                    else:
                        missing_species.append(sublist)

        missingfile = open(os.path.join(os.path.abspath("."), 'output', 'GWB', 'spxNotFound.txt'), 'w+')
        #missing_species = [i for i in missing_species if len(i)<1]
        for line in missing_species:
            if len(line) > 0:
                missingfile.writelines(line[0])
                missingfile.writelines('\n')
                for i in range(len(line)):
                    missingfile.writelines('   %s' % line[i])
                    missingfile.writelines('\n')
        missingfile.close()
        missing_species = [item for sublist in missing_species for item in sublist]
        missing_species = [i for n, i in enumerate(missing_species) if i not in missing_species[:n]]
        elem_avail = list(np.unique([k for i, j in enumerate([[i] + k for i, k in sourcedic.items()
                                                              if i not in missing_species])
                                     for l, k in enumerate(j) if i < len(specielist[1])
                                     and str(k).strip('0123456789.- ') != ''
                                     and not str(k).endswith(("+", "-", '(aq)', '(g)'))
                                     and k not in ['O2', 'H2O'] and len(k) < 3]))

        if objdb == None:
            objdb = 'thermo.%sbars' % int(P[0])
        logKnan_alert = False
        # timestr = '.' + time.strftime("%d%b%y_%H%M")

        fout = open(os.path.join(os.path.abspath("."),'output', 'GWB',  objdb + '.' + dataset), 'w+') # + timestr
        dbname2 = 'and supcrtbl.dat' if self.dbHP_dir is not None else 'and berman.dat' if self.dbBerman_dir is not None else  ''

        if sourceformat.upper() != 'EQ36':
            s = fid.readline()
            fout.writelines(s)
            s = fid.readline()
            fout.writelines(s[:16] + dataset_format + '\n')

            if dataset_format in ['jul17', 'jan19', 'apr20', 'mar21']:
                s = fid.readline()
                fout.writelines(s)

            s = fid.readline()
            fout.writelines(s)
            s = fid.readline()
            if s.strip(' \n*') != '':
                if s[:27].strip(' \n*:') == 'THERMODYNAMIC DATABASE':
                    fout.writelines(s[:27] + dbname + '\n')
                else:
                    fout.writelines('*  THERMODYNAMIC DATABASE: ' + dbname + '\n')
            else:
                fout.writelines('*  THERMODYNAMIC DATABASE: ' + dbname + '\n')
            s = fid.readline()
            if s[:15].strip(' \n*:') == 'generated by':
                fout.writelines(s[:15] + ': pyGeochemCalc, ' + time.ctime() + '\n')
            else:
                fout.writelines('*  generated by' + ': pyGeochemCalc, ' + time.ctime() + '\n')
            s = fid.readline()
            fout.writelines(s)
            s = fid.readline()
            fout.writelines(s)
        else:
            fout.writelines('dataset of thermodynamic data for gwb programs \n' + \
                            'dataset format: ' + dataset_format + '\n' + \
                                'activity model: %s \n' % activity_model + \
                                    'fugacity model: tsonopoulos \n'  + \
                                        '*  THERMODYNAMIC DATABASE: ' + dbname + ' ' + dbname2 + '\n' +\
                                            '*  generated by: pyGeochemCalc, ' + time.ctime() + '\n' +\
                                                '*  Output package:  gwb \n' + \
                                                    '*  Data set:        com \n')

        if dataset_format in ['oct94', 'jul17']:
            fout.writelines('*  Note: coefficients for calculating the activity coefficients \n' + \
                            '*    for CO2 are based on Ref:\n' + \
                                '*    S.E.Drummond,1981. Boiling and Mixing of Hydrothermal\n' + \
                                    '*    Fluids: Chemical Effects on Mineral Precipitation.\n')
        elif dataset_format in ['jan19', 'apr20', 'mar21'] and logK_form.lower() == 'polycoeffs':
            fout.writelines('*   \n' + \
                            '* This thermo data file uses the polynomial expression of the logK values: \n' + \
                                '*  \n' + \
                                    '* log10 K(TK) = a + b*(TK-Tr) + c*(TK^2-Tr^2) + d*(1/TK-1/Tr) + e*(1/TK^2-1/Tr^2) + f*ln(TK/Tr) \n' + \
                                            '* TK is the Temperature in Kelvin, Tr is the relative temperature (T = 298.15 K). \n')


        #skip lines till temperature rows
        for i in range(1000) :
            s = fid.readline()
            if s.strip('\n').strip('* ') in ['temperatures', 'temperatures (degC)', 'Temperature grid (degC)']:
                break
        fout.writelines( "\n")
        if s.strip('\n').strip('* ') == 'temperatures':
            if sourceformat.upper() != 'EQ36':
                fout.writelines(s[:-1] + '(degC)\n')
            else:
                fout.writelines('* ' + s[:-1] + '(degC)\n')
        elif s.strip('\n').strip('* ') == 'Temperature grid (degC)':
            fout.writelines('* temperatures (degC)\n')
        else:
            fout.writelines(s)

        for i in range(len(T)):
            i = i + 1
            if (i == 1) | (i == 5):
                fout.writelines( "       %9.4f" %  T[i-1])
            else:
                fout.writelines( "   %9.4f" %  T[i-1])
            if (i % 4 == 0) | (i == len(T)):
                fout.writelines( "\n")

        #skip lines till pressure rows
        for i in range(1000) :
            s = fid.readline()
            if s.strip('\n').strip('* ') in ['pressures', 'pressures (bar)', 'Pressure grid (bars)']:
                break
        if s.strip('\n').strip('* ') == 'pressures':
            if sourceformat.upper() != 'EQ36':
                fout.writelines(s[:-1] + '(bar)\n')
            else:
                fout.writelines('* ' + s[:-1] + '(bar)\n')
        elif s.strip('\n').strip('* ') == 'Pressure grid (bars)':
            fout.writelines('* pressures (bar)\n')
        else:
            fout.writelines(s)
        for i in range(len(P)):
            i = i + 1
            if (i == 1) | (i == 5):
                fout.writelines( "       %9.4f" %  P[i-1])
            else:
                fout.writelines( "   %9.4f" %  P[i-1])
            if (i % 4 == 0) | (i == len(P)):
                fout.writelines( "\n")

        #% Calculation for debye huckel and bdot and water properties
        waterdielc = water_dielec(T = T, P = P, Dielec_method = Dielec_method)
        E, Adh, Bdh, bdot = waterdielc.E, waterdielc.Ah, waterdielc.Bh, waterdielc.bdot

        rhoEG = {'rho': rho, 'E': E,  'dGH2O': dGH2O}
        rhoEDB = {'rho': rho, 'E': E,  'Ah': Adh, 'Bh': Bdh}

        # Calculate the rho E G for density extrapolation method here so we have it below
        rhoEGextrap = {}
        if any(rhoEG['rho'] < 350):
            subBornptrs = rhoEG['rho'] < 350
            for i, j in enumerate(zip(T[subBornptrs], P[subBornptrs])):
                rhoextrap = np.linspace(350, 550, 3)
                Pextrap = iapws95(T = j[0], rho = rhoextrap).P if Dielec_method.upper() != 'DEW' else ZhangDuan(T = j[0], rho = rhoextrap).P
                Textrap = j[0]*np.ones(np.size(Pextrap))

                dGH2O = iapws95(T = Textrap, P = Pextrap).G if Dielec_method.upper() != 'DEW' else ZhangDuan(T = Textrap, P = Pextrap).G
                E = water_dielec(T = Textrap, P = Pextrap, Dielec_method = Dielec_method).E
                rhoextrap = np.around(rhoextrap, 3)
                rhoEGextrap['%d_%d' % (j[0], j[1])]= {'rho': rhoextrap,'E': E, 'dGH2O': dGH2O,
                                                       'Textrap': Textrap, 'Pextrap': Pextrap}


        #skip lines till adh rows
        #  'cco2' in s.strip('\n') 'log k for eh reaction' or 'Eh reaction: logKr' in s.strip('\n')
        for i in range(100) :
            s = fid.readline()
            if any(re.findall(r'|'.join(('(adh)', 'Debye-Huckel A_gamma')), s.strip('\n'), re.IGNORECASE)):
                break
        if sourceformat.upper() != 'EQ36':
            fout.writelines(s)
        else:
            fout.writelines('* debye huckel a (adh)\n')
        if (dataset_format in ['jan19', 'apr20', 'mar21']) & (logK_form.lower() == 'polycoeffs'):
            Adhcorr = curve_fit(logKfunc, TK[Adh!=500].ravel(), Adh[Adh!=500].ravel(), p0 = x0,  maxfev = 1000000)[0]
            fout.writelines('     a= %15.9f   ' % Adhcorr[0] + 'b= %15.9f   ' % Adhcorr[1] + \
                            'c= %15.6e\n' % Adhcorr[2])
            fout.writelines('     d= %15.6f   ' % Adhcorr[3] + 'e= %15.5f   ' % Adhcorr[4] + \
                            'f= %15.8f \n' % Adhcorr[5])
        else:
            for i in range(len(Adh)):
                i = i + 1
                if (i == 1) | (i == 5):
                    fout.writelines( "       %9.4f" %  Adh[i-1])
                else:
                    fout.writelines( "   %9.4f" %  Adh[i-1])
                if (i % 4 == 0) | (i == len(Adh)):
                    fout.writelines( "\n")
        #skip lines till bdh rows
        for i in range(100):
            s = fid.readline()
            if any(re.findall(r'|'.join(('(bdh)', 'Debye-Huckel B_gamma')), s.strip('\n'), re.IGNORECASE)):
                break
        if sourceformat.upper() != 'EQ36':
            fout.writelines(s)
        else:
            fout.writelines('* debye huckel b (bdh)\n')
        if (dataset_format in ['jan19', 'apr20', 'mar21']) & (logK_form.lower() == 'polycoeffs'):
            Bdhcorr = curve_fit(logKfunc, TK[Bdh!=500].ravel(), Bdh[Bdh!=500].ravel(), p0 = x0,  maxfev = 1000000)[0]
            fout.writelines('     a= %15.9f   ' % Bdhcorr[0] + 'b= %15.9f   ' % Bdhcorr[1] + \
                            'c= %15.6e\n' % Bdhcorr[2])
            fout.writelines('     d= %15.6f   ' % Bdhcorr[3] + 'e= %15.5f   ' % Bdhcorr[4] + \
                            'f= %15.8f \n' % Bdhcorr[5])
        else:
            for i in range(len(Bdh)):
                i = i + 1
                if (i == 1) | (i == 5):
                    fout.writelines( "       %9.4f" %  Bdh[i-1])
                else:
                    fout.writelines( "   %9.4f" %  Bdh[i-1])
                if (i % 4 == 0) | (i == len(Bdh)):
                    fout.writelines( "\n")
        #skip lines till bdot rows
        if activity_model in ['debye-huckel', 'b-dot']:
            for i in range(100) :
                s = fid.readline()
                if any(re.findall(r'|'.join(('bdot', 'B-dot')), s.strip('\n'), re.IGNORECASE)):
                    break
        if sourceformat.upper() != 'EQ36':
            fout.writelines(s)
        else:
            if activity_model in ['debye-huckel', 'b-dot']:
                fout.writelines('* bdot\n')

        if activity_model in ['debye-huckel', 'b-dot']:
            for i in range(len(bdot)):
                i = i + 1
                if (i == 1) | (i == 5):
                    fout.writelines( "       %9.4f" %  bdot[i-1])
                else:
                    fout.writelines( "   %9.4f" %  bdot[i-1])
                if (i % 4 == 0) | (i == len(bdot)):
                    fout.writelines( "\n")

            #% Calculation for co2 fitting coefs
            cco2 = gamma_correlation(T, P, co2actmodel)
            cco2 = cco2.T #.ravel()
            for j in range(4):
                fout.writelines('* c co2 %s\n' % (j+1))
                for i in range(len(cco2)):
                    i = i + 1
                    if (i == 1) | (i == 5):
                        fout.writelines( "       %9.4f" %  cco2[i-1, j])
                    else:
                        fout.writelines( "   %9.4f" %  cco2[i-1, j])
                    if (i % 4 == 0) | (i == len(cco2)):
                        fout.writelines( "\n")

            #skip lines till c h2o rows
            if sourceformat.upper() != 'EQ36':
                for i in range(100) :
                    s = fid.readline()
                    # print(s)
                    if s[:7] == '* c h2o':
                        break

            #% Calculation for h2o fitting coefs
            ch2o = aw_correlation(T, P, Dielec_method = Dielec_method, **rhoEDB)
            ch2o = ch2o.T #.ravel()
            for j in range(4):
                fout.writelines('* c h2o %s\n' % (j+1))
                for i in range(len(cco2)):
                    i = i + 1
                    if (i == 1) | (i == 5):
                        fout.writelines( "       %9.4f" %  ch2o[i-1, j])
                    else:
                        fout.writelines( "   %9.4f" %  ch2o[i-1, j])
                    if (i % 4 == 0) | (i == len(ch2o)):
                        fout.writelines( "\n")

        if dataset_format == 'oct94':
        # #Copy and replace c h2o values
            for i in range(100) :
                s = fid.readline()
                if s[:7] == '* log k':
                    break
                # fout.writelines(s)
            #% Calculations for "log k for eh" rows
            fout.writelines(s)
            logK = calcRxnlogK( T = T, P = P, Specie = 'eh', dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                               specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                               sourceformat = sourceformat, densityextrap = densityextrap,
                               rhoEGextrap = rhoEGextrap).logK
            logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
            for i in range(len(logK)):
                i = i + 1
                if (i == 1) | (i == 5):
                    fout.writelines( "       %9.4f" %  logK[i-1])
                else:
                    fout.writelines( "   %9.4f" %  logK[i-1])
                if (i % 4 == 0) | (i == len(logK)):
                    fout.writelines( "\n")

            #% Calculations for "log k for o2"
            #skip lines till "log k for o2" rows
            for i in range(50) :
                s = fid.readline()
                # print(s)
                if s[:14] == '* log k for o2':
                    break
            fout.writelines(s)
            logK = calcRxnlogK( T = T, P = P, Specie = 'O2(g)', dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                               specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                               sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'gases',
                               heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap).logK
            logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
            for i in range(len(logK)):
                i = i + 1
                if (i == 1) | (i == 5):
                    fout.writelines( "       %9.4f" %  logK[i-1])
                else:
                    fout.writelines( "   %9.4f" %  logK[i-1])
                if (i % 4 == 0) | (i == len(logK)):
                    fout.writelines( "\n")

            #% Calculations for "log k for h2"
            #skip lines till "log k for h2" rows
            for i in range(50) :
                s = fid.readline()
                # print(s)
                if s[:14] == '* log k for h2':
                    break
            fout.writelines(s)
            logK = calcRxnlogK( T = T, P = P, Specie = 'H2(g)', dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                               Specie_class = 'gases', specielist = specielist, Dielec_method = Dielec_method,
                               sourceformat = sourceformat, densityextrap = densityextrap, rhoEG = rhoEG,
                               heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap).logK
            logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
            for i in range(len(logK)):
                i = i + 1
                if (i == 1) | (i == 5):
                    fout.writelines( "       %9.4f" %  logK[i-1])
                else:
                    fout.writelines( "   %9.4f" %  logK[i-1])
                if (i % 4 == 0) | (i == len(logK)):
                    fout.writelines( "\n")

            #% Calculations for "log k for n2"
            #skip lines till "log k for n2" rows
            for i in range(50) :
                s = fid.readline()
                # print(s)
                if s[:14] == '* log k for n2':
                    break
            fout.writelines(s)
            logK = calcRxnlogK( T = T, P = P, Specie = 'N2(g)', dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                               specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                               sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'gases',
                               heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap).logK
            logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
            for i in range(len(logK)):
                i = i + 1
                if (i == 1) | (i == 5):
                    fout.writelines( "       %9.4f" %  logK[i-1])
                else:
                    fout.writelines( "   %9.4f" %  logK[i-1])
                if (i % 4 == 0) | (i == len(logK)):
                    fout.writelines( "\n")
            fout.writelines( "\n")
        else:
            fout.writelines('\n')

        if sourceformat.upper() == 'EQ36':
            fout.writelines( "\n")

            f_ionsize = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ion_size.txt'), 'r')
            Rd = f_ionsize.readlines()
            Rd = Rd[1:]
            ion_sizedic = {Rd[x].split()[0] : Rd[x].split()[1] for x in range(len(Rd))}
            f_ionsize.close()
            # Needed for rebalancing aqueous and mineral reactions in terms of O2(aq) instead of O2(g)
            dic = {'O2(g)' : ['', 1, '1.0000', 'O2(aq)']}
            logK_rebal = calcRxnlogK( T = T, P = P, Specie = 'O2(g)', dbaccessdic = dbaccessdic, sourcedic = dic,
                                     specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                     sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'gases',
                                     heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap).logK
            logK_rebal = np.where(np.isnan(logK_rebal), 500, logK_rebal) # set abitrary 500 to nan values

        #% Elements
        #skip lines till "elements" rows
        for i in range(5000) :
            s = fid.readline()
            if s.rstrip('\n').lstrip('0123456789.- ') == 'elements':
                break
        fout.writelines( "   %s elements" % len(elem_avail))
        fout.writelines( "\n\n")

        #copy and paste lines till "basis" rows
        for i in range(1000) :
            s = fid.readline()
            s_mod = s.split()[0] if s.strip('\n') != '' else s
            if s.rstrip('\n').lstrip('0123456789.- ') == 'basis species':
                break
            if sourceformat.upper() != 'EQ36':
                if s_mod[:5] in [Element[j].name[0][:5] for j in elem_avail]:
                    fout.writelines(s)
            else:
                if s_mod in elem_avail and not s.startswith('+---'):
                    fout.writelines('%-15s (%-2s)          mole wt.=  %8.4f g\n'
                                    % (Element[s_mod].name[0], s_mod, float(s.split()[1])))
                else:
                    continue
        fout.writelines( "\n-end-\n\n")

        #only used for counter
        counter = 0
        for j in specielist[1]:
            if (j not in missing_species):
                counter +=1
        fout.writelines( "   %s basis species\n\n" % counter)

        #% Basis reactions
        #skip lines till "redox couples" rows
        for i in range(2000):
            s = fid.readline()
            if s.rstrip('\n').lstrip('0123456789.- ') in ['redox couples', 'auxiliary basis species']:
                break

        for j in specielist[1]:
            if (j not in missing_species):
                k = j.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
                if sourceformat.upper() != 'EQ36':
                    fout.writelines('%s\n' % j)
                else:
                    fout.writelines('%s\n' % j.replace('O2(g)', 'O2(aq)'))
                if sourceformat.upper() != 'EQ36':
                    fout.writelines('%s\n' % chargedic[j])
                else:
                    if j == 'O2(g)':
                        ionsize = [float(re.sub('[^0123456789\.]', '', x)) for x in block_info['O2(g)_b'] if x.strip('*    ').startswith('DHazero')]
                    else:
                        ionsize = [float(re.sub('[^0123456789\.]', '', x)) for x in block_info[j] if x.strip('*    ').startswith('DHazero')]
                    if any(ionsize) and any([MWdic[j]]):
                        fout.writelines('     charge=  %d      ion size=  %.1f A      mole wt.=   %8.4f g\n'
                                        % (float(chargedic[j].split()[-1]), ionsize[0], MWdic[j]))
                    else:
                        formula = j if sourcedic[j][0] == '' else sourcedic[j][0]
                        formula = formula.rstrip('(aq)(g)')
                        ionsize = 3 if j.endswith('(aq)') else float(ion_sizedic[j]) if j in ion_sizedic.keys() else 500
                        fout.writelines('     charge=  %d      ion size=  %.1f A      mole wt.=   %8.4f g\n'
                                        % (float(chargedic[j].split()[-1]), ionsize,
                                           calc_elem_count_molewt(formula, Elementdic = Element)[-1]) )

                if sourceformat.upper() != 'EQ36':
                    fout.writelines( "     %s elements in species\n" % sourcedic[j][1])
                    Rxn = sourcedic[j][2:]
                else:
                    fout.writelines( "     %s elements in species\n" % int(len(Elemlist[j])/2) )
                    Rxn = Elemlist[j]

                for i in range(len(Rxn)):
                    i = i + 1
                    if (i == 1) | (i == 7):
                        fout.writelines( "    %9.4f " %  float(Rxn[i - 1]))
                    elif i % 2 != 0:
                        fout.writelines( "%9.4f " %  float(Rxn[i - 1]))
                    else:
                        if sourceformat.upper() != 'EQ36':
                            fout.writelines( "%-9s     " %  (Rxn[i - 1]))
                        else:
                            fout.writelines( "%-9s     " %  (Rxn[i - 1]).replace('O2(g)', 'O2(aq)'))
                    if (i % 6 == 0) | (i == len(Rxn)):
                        fout.writelines( "\n")
                fout.writelines( "*    gflag = 1 [reported delG0f used]\n" )
                fout.writelines( "*    extrapolation algorithm:      [92joh/oel]\n" )
                if j != 'H2O':
                    ref = dbaccessdic[k][1].split('  ')[0]
                    ref = ref.split(':')[1] if ('ref' in ref) or ('REF' in ref) else ref
                    dG, dH, S = dbaccessdic[k][2], dbaccessdic[k][3], dbaccessdic[k][4]
                else:
                    dG, dH, S, ref = dGH2O[0], dHH2O[0], SH2O[0], 'iapws95/' + Dielec_method if Dielec_method in ['FGL97', 'JN91'] else 'DEW'
                fout.writelines( "*    reference-state data source = %s\n" % ref)
                fout.writelines( "*         delG0f =   %8.3f  kcal/mol\n" % (dG/1000) )
                fout.writelines( "*         delH0f =   %8.3f  kcal/mol\n" % (dH/1000))
                fout.writelines( "*         S0PrTr =   %8.3f  cal/(mol*K)\n" % S)
                fout.writelines( "\n")
            else:
                continue
        fout.writelines( "-end-\n\n")

        #only used for counter
        counter = 0
        for j in specielist[2]:
            rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]] # remove formula and specie number
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ] # remove all coefficients
            if (j not in missing_species) and (len([k for k in rxnlst if k not in missing_species]) == len(rxnlst)):
                counter +=1
        fout.writelines( "   %s redox couples\n\n" % counter)

        #% Redox reactions
        #skip lines till "aqueous species" rows
        for i in range(2000):
            s = fid.readline()
            # print(s)
            if s.rstrip('\n').lstrip('0123456789.- ') == 'aqueous species':
                break

        if sourceformat.upper() != 'EQ36':
            speclst = specielist[2]
        else:
            speclst = [ x for x in specielist[2] if x != 'O2(aq)']
        for j in speclst:
            rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]] # remove formula and specie number
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ] # remove all coefficients
            if (j not in missing_species) and (len([i for i in rxnlst if i not in missing_species]) == len(rxnlst)):
                k = j.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
                if dataset_format == 'oct94':
                    fout.writelines('%s\n' % j)
                    if sourcedic[j][0] != '':
                        fout.writelines('*    formula= %s\n' % sourcedic[j][0])
                    else:
                        fout.writelines('*    formula= %s\n' % dbaccessdic[k][0])
                elif dataset_format in ['jul17', 'jan19', 'apr20', 'mar21']:
                    if sourcedic[j][0] != '':
                        fout.writelines('%-30s %s %s\n' % (j, 'formula=', sourcedic[j][0]))
                    else:
                        fout.writelines('%-30s %s %s\n' % (j, 'formula=', dbaccessdic[k][0]))
                if sourceformat.upper() != 'EQ36':
                    fout.writelines('%s\n' % chargedic[j])
                else:
                    ionsize = [float(re.sub('[^0123456789\.]', '', x)) for x in block_info[j] if x.strip('*    ').startswith('DHazero')]
                    if any(ionsize) and any([MWdic[j]]):
                        fout.writelines('     charge=  %d      ion size=  %.1f A      mole wt.=   %8.4f g\n'
                                        % (float(chargedic[j].split()[-1]), ionsize[0], MWdic[j]))
                    else:
                        formula = j if sourcedic[j][0] == '' else sourcedic[j][0]
                        formula = formula.rstrip('(aq)')
                        ionsize = 3 if j.endswith('(aq)') else float(ion_sizedic[j]) if j in ion_sizedic.keys() else 500
                        fout.writelines('     charge=  %d      ion size=  %.1f A      mole wt.=   %8.4f g\n'
                                        % (float(chargedic[j].split()[-1]), ionsize,
                                           calc_elem_count_molewt(formula, Elementdic = Element)[-1]) )
                if sourceformat.upper() != 'EQ36':
                    fout.writelines( "     %s species in reaction\n" % sourcedic[j][1])
                else:
                    fout.writelines( "     %s species in reaction\n" % (sourcedic[j][1] - 1) )
                Rxn = sourcedic[j][2:] if sourceformat.upper() != 'EQ36' else sourcedic[j][4:]

                for i in range(len(Rxn)):
                    i = i + 1
                    if (i == 1) | (i == 7):
                        fout.writelines( "    %9.4f " %  float(Rxn[i - 1]))
                    elif i % 2 != 0:
                        fout.writelines( "%9.4f " %  float(Rxn[i - 1]))
                    else:
                        fout.writelines( "%-9s     " %  (Rxn[i - 1]))
                    if (i % 6 == 0) | (i == len(Rxn)):
                        fout.writelines( "\n")
                logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                                   specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                   sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'aqueous',
                                   rhoEGextrap = rhoEGextrap, ThermoInUnit = self.ThermoInUnit)

                if densityextrap.lower() == 'yes': #any(np.isnan(logK)):
                    if all(logK.nonsubBornptrs) == True: # if all densities are >= 350
                        logKnan_alert = False            # turn off the prompts for using Density extrapolation
                    else:
                        logKnan_alert = True
                else:
                    logKnan_alert = False                # turn off the prompts for using Density extrapolation
                logK = logK.logK
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values

                if (dataset_format in ['jan19', 'apr20', 'mar21']) & (logK_form.lower() == 'polycoeffs'):
                    logKcorr = curve_fit(logKfunc, TK[logK!=500].ravel(), logK[logK!=500].ravel(), p0 = x0,  maxfev = 1000000)[0]
                    fout.writelines('     a= %15.9f   ' % logKcorr[0] + 'b= %15.9f   ' % logKcorr[1] + \
                                    'c= %15.6e\n' % logKcorr[2])
                    fout.writelines('     d= %15.6f   ' % logKcorr[3] + 'e= %15.5f   ' % logKcorr[4] + \
                                    'f= %15.8f \n' % logKcorr[5])
                    fout.writelines('     TminK= %-15.2f ' % np.min(TK) + 'TmaxK= %-7.2f\n' % np.max(TK))
                else:
                    for i in range(len(logK)):
                        i = i + 1
                        if (i == 1) | (i == 5):
                            fout.writelines( "     %9.4f" %  logK[i-1])
                        else:
                            fout.writelines( "  %9.4f" %  logK[i-1])
                        if (i % 4 == 0) | (i == len(logK)):
                            fout.writelines( "\n")
                fout.writelines( "*    gflag = 1 [reported delG0f used]\n" )
                fout.writelines( "*    extrapolation algorithm: supcrt92 [92joh/oel]\n" )
                if j != 'H2O':
                    ref = dbaccessdic[k][1].split('  ')[0]
                    ref = ref.split(':')[1] if ('ref' in ref) or ('REF' in ref) else ref
                    dG, dH, S = dbaccessdic[k][2], dbaccessdic[k][3], dbaccessdic[k][4]
                else:
                    dG, dH, S, ref = dGH2O[0], dHH2O[0], SH2O[0], 'iapws95/' + Dielec_method if Dielec_method in ['FGL97', 'JN91'] else 'DEW'
                fout.writelines( "*    reference-state data source = %s\n" % ref)
                fout.writelines( "*         delG0f =   %8.3f  kcal/mol\n" % (dG/1000) )
                fout.writelines( "*         delH0f =   %8.3f  kcal/mol\n" % (dH/1000))
                fout.writelines( "*         S0PrTr =   %8.3f  cal/(mol*K)\n" % S)
                fout.writelines( "\n")
            else:
                continue
        fout.writelines( "-end-\n\n")
        if logKnan_alert == True:
            warnings.warn('Some temperature and pressure points are out of aqueous species HKF eqns regions of applicability, hence, density extrapolation has been applied')

        #only used for counter
        counter = 0
        for j in specielist[3]:
            rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]] # remove formula and specie number
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ] # remove all coefficients
            if (j not in missing_species) and (len([k for k in rxnlst if k not in missing_species])==len(rxnlst)):
                counter +=1
        fout.writelines( "   %s aqueous species\n\n" % counter)

        #% Aqueous reactions
        # skip lines till "minerals" rows
        for i in range(20000):
            s = fid.readline()
            if s.rstrip('\n').lstrip('0123456789.- ') in ['minerals', 'solids']:
                break

        for j in specielist[3]:
            rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]] # remove formula and specie number
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ] # remove all coefficients
            if (j not in missing_species) and (len([i for i in rxnlst if i not in missing_species]) == len(rxnlst)):
                k = j.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
                # print(k)
                if dataset_format == 'oct94':
                    fout.writelines('%s\n' % j)
                    if sourcedic[j][0] != '':
                        fout.writelines('*    formula= %s\n' % sourcedic[j][0])
                    else:
                        fout.writelines('*    formula= %s\n' % dbaccessdic[k][0])
                elif dataset_format in ['jul17', 'jan19', 'apr20', 'mar21']:
                    if sourcedic[j][0] != '':
                        fout.writelines('%-30s %s %s\n' % (j, 'formula=', sourcedic[j][0]))
                    else:
                        fout.writelines('%-30s %s %s\n' % (j, 'formula=', dbaccessdic[k][0]))

                if sourceformat.upper() != 'EQ36':
                    fout.writelines('%s\n' % chargedic[j])
                else:
                    ionsize = [float(re.sub('[^0123456789\.]', '', x)) for x in block_info[j] if x.strip('*    ').startswith('DHazero')]
                    if any(ionsize) and any([MWdic[j]]):
                        fout.writelines('     charge=  %d      ion size=  %.1f A      mole wt.=   %8.4f g\n'
                                        % (float(chargedic[j].split()[-1]), ionsize[0], MWdic[j]))
                    else:
                        formula = j if sourcedic[j][0] == '' else sourcedic[j][0]
                        formula = formula.rstrip('(aq)')
                        ionsize = 3 if j.endswith('(aq)') else float(ion_sizedic[j]) if j in ion_sizedic.keys() else 500
                        fout.writelines('     charge=  %d      ion size=  %.1f A      mole wt.=   %8.4f g\n'
                                        % (float(chargedic[j].split()[-1]), ionsize,
                                           calc_elem_count_molewt(formula, Elementdic = Element)[-1] ) )

                if sourceformat.upper() != 'EQ36':
                    fout.writelines( "     %s species in reaction\n" % sourcedic[j][1])
                else:
                    fout.writelines( "     %s species in reaction\n" % (sourcedic[j][1] - 1) )
                Rxn = sourcedic[j][2:]  if sourceformat.upper() != 'EQ36' else sourcedic[j][4:]
                for i in range(len(Rxn)):
                    i = i + 1
                    if (i == 1) | (i == 7) | (i == 13):
                        fout.writelines( "    %9.4f " %  float(Rxn[i - 1]))
                    elif i % 2 != 0:
                        fout.writelines( "%9.4f " %  float(Rxn[i - 1]))
                    else:
                        if sourceformat.upper() != 'EQ36':
                            fout.writelines( "%-9s     " %  (Rxn[i - 1]))
                        else:
                            fout.writelines( "%-9s     " %  (Rxn[i - 1]).replace('O2(g)', 'O2(aq)'))
                    if (i % 6 == 0) | (i % 12 == 0) | (i == len(Rxn)):
                        fout.writelines( "\n")
                logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                                   specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                   sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'aqueous',
                                   rhoEGextrap = rhoEGextrap, ThermoInUnit = self.ThermoInUnit).logK
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                if sourceformat.upper() == 'EQ36' and 'O2(g)' in Rxn:
                    coeff_O2 = float(Rxn[Rxn.index('O2(g)') - 1])
                    logK = np.where(logK != 500, logK + coeff_O2*logK_rebal, logK)

                if (dataset_format in ['jan19', 'apr20', 'mar21']) & (logK_form.lower() == 'polycoeffs'):
                    logKcorr = curve_fit(logKfunc, TK[logK!=500].ravel(), logK[logK!=500].ravel(), p0 = x0,  maxfev = 1000000)[0]
                    fout.writelines('     a= %15.9f   ' % logKcorr[0] + 'b= %15.9f   ' % logKcorr[1] + \
                                    'c= %15.6e\n' % logKcorr[2])
                    fout.writelines('     d= %15.6f   ' % logKcorr[3] + 'e= %15.5f   ' % logKcorr[4] + \
                                    'f= %15.8f \n' % logKcorr[5])
                    fout.writelines('     TminK= %-15.2f ' % np.min(TK) + 'TmaxK= %-7.2f\n' % np.max(TK))
                else:
                    for i in range(len(logK)):
                        i = i + 1
                        if (i == 1) | (i == 5):
                            fout.writelines( "     %9.4f" %  logK[i-1])
                        else:
                            fout.writelines( "  %9.4f" %  logK[i-1])
                        if (i % 4 == 0) | (i == len(logK)):
                            fout.writelines( "\n")
                fout.writelines( "*    gflag = 1 [reported delG0f used]\n" )
                fout.writelines( "*    extrapolation algorithm: supcrt92 [92joh/oel]\n" )
                if j != 'H2O':
                    ref = dbaccessdic[k][1].split('  ')[0]
                    ref = ref.split(':')[1] if ('ref' in ref) or ('REF' in ref) else ref
                    dG, dH, S = dbaccessdic[k][2], dbaccessdic[k][3], dbaccessdic[k][4]
                else:
                    dG, dH, S, ref = dGH2O[0], dHH2O[0], SH2O[0], 'iapws95/' + Dielec_method if Dielec_method in ['FGL97', 'JN91'] else 'DEW'
                fout.writelines( "*    reference-state data source = %s\n" % ref)
                fout.writelines( "*         delG0f =   %8.3f  kcal/mol\n" % (dG/1000) )
                fout.writelines( "*         delH0f =   %8.3f  kcal/mol\n" % (dH/1000))
                fout.writelines( "*         S0PrTr =   %8.3f  cal/(mol*K)\n" % S)
                fout.writelines( "\n")
            else:
                continue

        fout.writelines( "-end-\n\n")

        #% free electron for tdat dataset format
        if dataset_format in ['jul17', 'jan19', 'apr20', 'mar21']:
            if sourceformat.upper() != 'EQ36':
                speclst = specielist[4]
            else:
                speclst = ['e-']
            fout.writelines( "   %s free electron\n\n" % len(speclst))
            for j in speclst:
                fout.writelines('%s\n' % j)
                if sourceformat.upper() != 'EQ36':
                    fout.writelines('%s\n' % chargedic[j])
                    fout.writelines( "     %s species in reaction\n" % sourcedic[j][1])
                else:
                    fout.writelines('     charge=  %d      ion size=  %.1f A      mole wt.=   %8.4f g\n'
                                    % (-1, 0, 0) )
                    fout.writelines( "     %s species in reaction\n" % (sourcedic[j][1] - 1) )

                Rxn = sourcedic[j][2:]  if sourceformat.upper() != 'EQ36' else sourcedic[j][4:]
                for i in range(len(Rxn)):
                    i = i + 1
                    if (i == 1) | (i == 7) | (i == 13):
                        fout.writelines( "    %9.4f " %  float(Rxn[i - 1]))
                    elif i % 2 != 0:
                        fout.writelines( "%9.4f " %  float(Rxn[i - 1]))
                    else:
                        fout.writelines( "%-9s     " %  (Rxn[i - 1]))
                    if (i % 6 == 0) | (i % 12 == 0) | (i == len(Rxn)):
                        fout.writelines( "\n")
                speclist = specielist #None if dataset_format == 'mar21' else specielist
                logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                                   specielist = speclist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                   sourceformat = sourceformat, densityextrap = densityextrap,
                                   heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap).logK
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values

                if (dataset_format in ['jan19', 'apr20', 'mar21']) & (logK_form.lower() == 'polycoeffs'):
                    logKcorr = curve_fit(logKfunc, TK[logK!=500].ravel(), logK[logK!=500].ravel(), p0 = x0,  maxfev = 1000000)[0]
                    fout.writelines('     a= %15.9f   ' % logKcorr[0] + 'b= %15.9f   ' % logKcorr[1] + \
                                    'c= %15.6e\n' % logKcorr[2])
                    fout.writelines('     d= %15.6f   ' % logKcorr[3] + 'e= %15.5f   ' % logKcorr[4] + \
                                    'f= %15.8f \n' % logKcorr[5])
                    fout.writelines('     TminK= %-15.2f ' % np.min(TK) + 'TmaxK= %-7.2f\n' % np.max(TK))
                else:
                    for i in range(len(logK)):
                        i = i + 1
                        if (i == 1) | (i == 5):
                            fout.writelines( "     %9.4f" %  logK[i-1])
                        else:
                            fout.writelines( "  %9.4f" %  logK[i-1])
                        if (i % 4 == 0) | (i == len(logK)):
                            fout.writelines( "\n")

            fout.writelines( "-end-\n\n")

        #only used for counter
        if clay_thermo is not None:
            if clay_thermo.lower() == 'yes':
                fclay = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clay_elements.dat'), 'r')
                Rd = fclay.readlines()
                Rd = [j.replace('-','_').strip('\n') for j in Rd]
                counter = len(Rd)
            else:
                counter = 0
        else: # default no clay thermo calculation
            clay_thermo = 'no'
            counter = 0

        solidsolution_no = 11
        if solid_solution is not None:
            if solid_solution.lower() == 'yes':
                if nCa_cpx is None:
                    nCa = 0
                    counter = counter + 3*solidsolution_no # no cpx
                else:
                    nCa = nCa_cpx
                    if nCa > 0:
                        counter = counter + 4*solidsolution_no
                    else:
                        counter = counter + 3*solidsolution_no  # no cpx
            else:
                counter = counter + 0
        else: # default no solid solution
            counter = counter + 0
            solid_solution = 'no'

        if sourceformat.upper() != 'EQ36':
            speclst = specielist[5]
        else:
            speclst = specielist[4] + specielist[5]
        for j in speclst:
            rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]] # remove formula and specie number
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ] # remove all coefficients
            if (j not in missing_species) and (len([k for k in rxnlst if k not in missing_species]) == len(rxnlst)):
                if (solid_solution.lower() == 'no') & (clay_thermo.lower() == 'no'):
                    counter += 1
                elif  (solid_solution.lower() == 'yes') & (clay_thermo.lower() == 'no'):
                    if j not in ['Anorthite', 'Albite', 'Forsterite', 'Fayalite', 'Enstatite', 'Ferrosilite']:
                        counter += 1
                    else:
                        continue
                elif  (solid_solution.lower() == 'no') & (clay_thermo.lower() == 'yes'):
                    if j not in [ Rd[h].split(',')[0] for h in range(len(Rd))]:
                        counter += 1
                    else:
                        continue
                else:
                    if j not in ['Anorthite', 'Albite', 'Forsterite', 'Fayalite', 'Enstatite', 'Ferrosilite'] + [ Rd[h].split(',')[0] for h in range(len(Rd))]:
                        counter += 1
                    else:
                        continue

        if (solid_solution.lower() == 'yes') and (nCa == 1):
            fout.writelines( "   %s minerals\n\n" % (counter - 2))
        else:
            fout.writelines( "   %s minerals\n\n" % (counter))

        # print('-> Processing mineral output')
        #% Mineral reactions
        #skip lines till "gases" rows
        for i in range(20000):
            s = fid.readline()
            if (dataset_format == 'mar21') and (s.rstrip('\n').lstrip('0123456789.- ') == 'solid solutions'):
                break
            elif dataset_format != 'mar21' and s.rstrip('\n').lstrip('0123456789.- ') == 'gases':
                break
        if solid_solution.lower() == 'yes':
            mineralcount = 0
            fnlist = ['plagio', 'olivine', 'pyroxene', 'cpx'] if nCa > 0 else ['plagio', 'olivine', 'pyroxene']
            for fn in fnlist:
                for nX in np.round(np.linspace(1, 0, solidsolution_no), 1):
                    if fn != 'cpx':
                        ss = calcRxnlogK(X = nX, T = T, P = P, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                         dbaccessdic = dbaccessdic, Specie = fn, densityextrap = densityextrap,
                                         ThermoInUnit = self.ThermoInUnit, rhoEGextrap = rhoEGextrap)
                    else:
                        ss = calcRxnlogK(cpx_Ca = nCa, X = nX, T = T, P = P, Dielec_method = Dielec_method,
                                         rhoEG = rhoEG, dbaccessdic = dbaccessdic, Specie = fn,
                                         densityextrap = densityextrap, ThermoInUnit = self.ThermoInUnit,
                                         rhoEGextrap = rhoEGextrap)
                    logK, Rxn = ss.logK, ss.Rxn

                    logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                    outputfmt(fout, logK, Rxn, TK, dataset = 'GWB', logK_form = logK_form)
                    mineralcount += 1

        # clay minerals
        if clay_thermo.lower() == 'yes':
            for i in range(len(Rd)):
                ss = calcRxnlogK(T = T, P = P, Specie = 'Clay', elem = Rd[i].split(','),
                                 dbaccessdic = dbaccessdic, ThermoInUnit = self.ThermoInUnit, rhoEG = rhoEG,
                                 rhoEGextrap = rhoEGextrap, densityextrap = densityextrap)
                logK, Rxn = ss.logK, ss.Rxn
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                outputfmt(fout, logK, Rxn, TK, dataset = 'GWB', logK_form = logK_form)

        for j in speclst:
            rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]] # remove formula and specie number
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ] # remove all coefficients
            if (j not in missing_species) and (len([k for k in rxnlst if k not in missing_species])==len(rxnlst)):
                if solid_solution.lower() == 'yes' and j in ['Anorthite', 'Albite', 'Forsterite', 'Fayalite', 'Enstatite', 'Ferrosilite']:
                    continue
                elif solid_solution.lower() == 'yes' and (nCa == 1) and j in ['Diopside', 'Hedenbergite']:
                    continue
                elif clay_thermo.lower() == 'yes' and j in [ Rd[h].split(',')[0] for h in range(len(Rd))]:
                    continue
                else:
                    k = j.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
                    fout.writelines("%s                       " % j)
                    if sourceformat.upper() != 'EQ36':
                        fout.writelines( "type= %s\n" %  Mineraltype[j])
                    else:
                        fout.writelines( "\n" )
                    if sourcedic[j][0] != '':
                        fout.writelines('     formula= %s\n' % sourcedic[j][0])
                    else:
                        fout.writelines('     formula= %s\n' % dbaccessdic[k][0])
                    fout.writelines("     mole vol.=   %1.3f cc" %  dbaccessdic[k][5])
                    if MWdic[j] != []:
                        fout.writelines("      mole wt.=  %1.4f g\n" %  MWdic[j])
                    else:
                        formula = k if sourcedic[j][0] == '' else sourcedic[j][0]
                        formula = formula.rstrip('(aq)(am)')#.rstrip('+2').rstrip('+3').rstrip('+4')
                        fout.writelines("      mole wt.=  %1.4f g\n" %  calc_elem_count_molewt(formula, Elementdic = Element)[-1] )
                    if sourceformat.upper() != 'EQ36':
                        fout.writelines( "     %s species in reaction\n" % sourcedic[j][1])
                    else:
                        fout.writelines( "     %s species in reaction\n" % (sourcedic[j][1] - 1) )

                    Rxn = sourcedic[j][2:] if sourceformat.upper() != 'EQ36' else sourcedic[j][4:]
                    for i in range(len(Rxn)):
                        i = i + 1
                        if (i == 1) | (i == 7) | (i == 13):
                            fout.writelines("%9.4f " %  float(Rxn[i - 1]))
                        elif i % 2 != 0:
                            fout.writelines("%9.4f " %  float(Rxn[i - 1]))
                        else:
                            if sourceformat.upper() != 'EQ36':
                                fout.writelines( "%-9s     " %  (Rxn[i - 1]))
                            else:
                                fout.writelines( "%-9s     " %  (Rxn[i - 1]).replace('O2(g)', 'O2(aq)'))
                        if (i % 6 == 0) | (i % 12 == 0) | (i == len(Rxn)):
                            fout.writelines( "\n")
                    logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                                       specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                       sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'minerals',
                                       heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap).logK
                    logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                    if sourceformat.upper() == 'EQ36' and 'O2(g)' in Rxn:
                        coeff_O2 = float(Rxn[Rxn.index('O2(g)') - 1])
                        logK = np.where(logK != 500, logK + coeff_O2*logK_rebal, logK)

                    if (dataset_format in ['jan19', 'apr20', 'mar21']) & (logK_form.lower() == 'polycoeffs'):
                        logKcorr = curve_fit(logKfunc, TK[logK!=500].ravel(), logK[logK!=500].ravel(), p0 = x0,  maxfev = 1000000)[0]
                        fout.writelines('     a= %15.9f   ' % logKcorr[0] + 'b= %15.9f   ' % logKcorr[1] + \
                                        'c= %15.6e\n' % logKcorr[2])
                        fout.writelines('     d= %15.6f   ' % logKcorr[3] + 'e= %15.5f   ' % logKcorr[4] + \
                                        'f= %15.8f \n' % logKcorr[5])
                        fout.writelines('     TminK= %-15.2f ' % np.min(TK) + 'TmaxK= %-7.2f\n' % np.max(TK))
                    else:
                        for i in range(len(logK)):
                            i = i + 1
                            if (i == 1) | (i == 5) | (i == 9):
                                fout.writelines("       %9.4f" %  logK[i-1])
                            else:
                                fout.writelines("  %9.4f" %  logK[i-1])
                            if (i % 4 == 0) | (i == len(logK)):
                                fout.writelines( "\n")

                    fout.writelines( "*    gflag = 1 [reported delG0f used]\n" )
                    if dbaccessdic[k][0] == 'nan':
                        fout.writelines( "*    extrapolation algorithm: supcrt92/water95\n" )
                    else:
                        fout.writelines( "*    extrapolation algorithm: supcrt92 [92joh/oel]\n" )
                    ref = dbaccessdic[k][1].split('  ')[0]
                    ref = ref.split(':')[1] if ('ref' in ref) or ('REF' in ref) else ref
                    fout.writelines( "*    reference-state data source = %s\n" % ref )
                    fout.writelines( "*         delG0f =   %8.3f  kcal/mol\n" % (dbaccessdic[k][2]/1000/J_to_cal if heatcap_method.lower() == 'berman88' else dbaccessdic[k][2]/1000) )
                    fout.writelines( "*         delH0f =   %8.3f  kcal/mol\n" % (dbaccessdic[k][3]/1000/J_to_cal if heatcap_method.lower() == 'berman88' else dbaccessdic[k][3]/1000))
                    fout.writelines( "*         S0PrTr =   %8.3f  cal/(mol*K)\n" % (dbaccessdic[k][4]/J_to_cal if heatcap_method.lower() == 'berman88' else dbaccessdic[k][4]))
                    fout.writelines( "\n")
            else:
                continue

        fout.writelines( "-end-\n\n")

        #% Solid solutions for GWB internal calculation
        #only used for counter
        counter = 0; ss_list = []
        if dataset_format == 'mar21':
            for j in specielist[6]:
                # print(j)
                lst = [x for x in sourcedic[j] if x.strip('\n')]
                minlst = [x.split()[0] for x in lst if x.split()[0] not in ['a0', '*']]
                # print(minlst)
                if all(x not in missing_species for x in minlst):
                    counter +=1
                    ss_list.append(j)
            fout.writelines( "   %s solid solutions\n\n" % counter )

            for i in range(20000):
                s = fid.readline()
                if s.rstrip('\n').lstrip('0123456789.- ') == 'gases':
                    break

            for j in ss_list:
                for k in range(len(sourcedic[j])):
                    fout.writelines( sourcedic[j][k] )
                if sourcedic[j][-1] != '\n':
                    fout.writelines( "\n")
            fout.writelines( "-end-\n\n")

        #only used for counter
        counter = 0
        spec = specielist[6]  if dataset_format != 'mar21' else specielist[7]
        for j in spec:
            rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]] # remove formula and specie number
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ] # remove all coefficients
            if (j not in missing_species) and (len([k for k in rxnlst if k not in missing_species])==len(rxnlst)):
                counter +=1
        fout.writelines( "   %s gases\n\n" % counter )

        #% Gas reactions
        #skip lines till "oxides" rows
        for i in range(20000):
            s = fid.readline()
            # print(s)
            if s.rstrip('\n').lstrip('0123456789.- ') in ['oxides', 'solid solutions']:
                break

        for j in spec:
            rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]] # remove formula and specie number
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ] # remove all coefficients
            if (j not in missing_species) and (len([k for k in rxnlst if k not in missing_species])==len(rxnlst)):
                k = j.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
                fout.writelines("%s\n" % j)
                if MWdic[j] != []:
                    fout.writelines( "     mole wt.=   %1.4f g\n" %  MWdic[j])
                else:
                    formula = j.rstrip('(g)')
                    fout.writelines("      mole wt.=  %1.4f g\n" %  calc_elem_count_molewt(formula, Elementdic = Element)[-1] )

                if sourceformat.upper() == 'EQ36':
                    fugacity_info = {'fugacity_chi': {'CH4(g)': '     chi=       -537.779     1.54946 -.000927827     1.20861  -.00370814  3.33804e-6\n',
                                                      'CO2(g)': '     chi=       -1430.87       3.598  -.00227376     3.47644   -.0104247  8.46271e-6\n',
                                                      'H2(g)': '     chi=       -12.5908     .259789  -7.2473e-5   .00471947 -2.69962e-5  2.15622e-8\n',
                                                      'H2O(g)': '     chi=       -6191.41     14.8528  -.00914267    -66.3326      .18277  -.00013274\n'},
                                     'fugacity_Pcrit': {'Ar(g)': '     Pcrit=     48.7 bar      Tcrit=     150.8 K      omega=        .001\n',
                                                        'CH4(g)': '     Pcrit=     46.0 bar      Tcrit=     190.4 K      omega=        .011\n',
                                                        'CO2(g)': '     Pcrit=     73.8 bar      Tcrit=     304.1 K      omega=        .239\n',
                                                        'H2(g)': '     Pcrit=     13.0 bar      Tcrit=      33.2 K      omega=       -.218\n',
                                                        'H2O(g)': '     Pcrit=    221.2 bar      Tcrit=     647.3 K      omega=        .344    a=-.0109    b=   0.0\n',
                                                        'H2S(g)': '     Pcrit=     89.4 bar      Tcrit=     373.2 K      omega=        .097\n',
                                                        'He(g)': '     Pcrit=     2.27 bar      Tcrit=      5.19 K      omega=       -.365\n',
                                                        'N2(g)': '     Pcrit=     33.9 bar      Tcrit=     126.2 K      omega=        .039\n',
                                                        'NH3(g)': '     Pcrit=    113.5 bar      Tcrit=     405.5 K      omega=        .250\n',
                                                        'O2(g)': '     Pcrit=     50.4 bar      Tcrit=     154.6 K      omega=        .025\n',
                                                        'SO2(g)': '     Pcrit=     78.8 bar      Tcrit=     430.8 K      omega=        .256\n'}}
                if dataset_format in ['jul17', 'jan19', 'apr20', 'mar21']:
                    if j in fugacity_info['fugacity_chi'].keys():
                        fout.writelines("%s" % fugacity_info['fugacity_chi'][j])
                    if j in fugacity_info['fugacity_Pcrit'].keys():
                        fout.writelines("%s" % fugacity_info['fugacity_Pcrit'][j])

                if sourceformat.upper() != 'EQ36':
                    fout.writelines( "     %s species in reaction\n" % sourcedic[j][1])
                else:
                    fout.writelines( "     %s species in reaction\n" % (sourcedic[j][1] - 1) )
                Rxn = sourcedic[j][2:] if sourceformat.upper() != 'EQ36' else sourcedic[j][4:]
                for i in range(len(Rxn)):
                    i = i + 1
                    if (i == 1) | (i == 7) | (i == 13):
                        fout.writelines( "    %9.4f " %  float(Rxn[i - 1]))
                    elif i % 2 != 0:
                        fout.writelines( "%9.4f " %  float(Rxn[i - 1]))
                    else:
                        if sourceformat.upper() != 'EQ36':
                            fout.writelines( "%-9s     " %  (Rxn[i - 1]))
                        else:
                            fout.writelines( "%-9s     " %  (Rxn[i - 1]).replace('O2(g)', 'O2(aq)'))
                    if (i % 6 == 0) | (i % 12 == 0) | (i == len(Rxn)):
                        fout.writelines( "\n")
                logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                                   specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                   sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'gases',
                                   heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap).logK
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                if sourceformat.upper() == 'EQ36' and 'O2(g)' in Rxn:
                    coeff_O2 = float(Rxn[Rxn.index('O2(g)') - 1])
                    logK = np.where(logK != 500, logK + coeff_O2*logK_rebal, logK)
                if (dataset_format in ['jan19', 'apr20', 'mar21']) & (logK_form.lower() == 'polycoeffs'):
                    TK = convert_temperature( T, Out_Unit = 'K' )
                    logKcorr = curve_fit(logKfunc, TK[logK!=500].ravel(), logK[logK!=500].ravel(), p0 = x0,  maxfev = 1000000)[0]
                    fout.writelines('     a= %15.9f   ' % logKcorr[0] + 'b= %15.9f   ' % logKcorr[1] + \
                                    'c= %15.6e\n' % logKcorr[2])
                    fout.writelines('     d= %15.6f   ' % logKcorr[3] + 'e= %15.5f   ' % logKcorr[4] + \
                                    'f= %15.8f \n' % logKcorr[5])
                    fout.writelines('     TminK= %-15.2f ' % np.min(TK) + 'TmaxK= %-7.2f\n' % np.max(TK))
                else:
                    for i in range(len(logK)):
                        i = i + 1
                        fout.writelines( "      %9.4f" %  logK[i-1])
                        if (i % 4 == 0) | (i == len(logK)):
                            fout.writelines( "\n")

                ref = dbaccessdic[k][1].split('  ')[0]
                ref = ref.split(':')[1] if ('ref' in ref) or ('REF' in ref) else ref
                fout.writelines( "*    gflag = 1 [reported delG0f used]\n" )
                fout.writelines( "*    extrapolation algorithm: supcrt92 [92joh/oel]\n" )
                fout.writelines( "*    reference-state data source = %s\n" % ref )
                fout.writelines( "*         delG0f =   %8.3f  kcal/mol\n" % (dbaccessdic[k][2]/1000) )
                fout.writelines( "*         delH0f =   %8.3f  kcal/mol\n" % (dbaccessdic[k][3]/1000))
                fout.writelines( "*         S0PrTr =   %8.3f  cal/(mol*K)\n" % dbaccessdic[k][4])
                fout.writelines( "\n")
            else:
                continue

        fout.writelines( "-end-\n\n")

        if sourceformat.upper() != 'EQ36':
            #only used for counter
            counter = 0
            spec = specielist[7]  if dataset_format != 'mar21' else specielist[8]
            for j in spec:
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]] # remove formula and specie number
                rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ] # remove all coefficients
                if (len([k for k in rxnlst if k not in missing_species])==len(rxnlst)):
                    counter +=1
            fout.writelines( "   %s oxides\n\n" % counter )

            #% Oxides reactions
            #skip lines till "references" rows
            for i in range(20000):
                s = fid.readline()
                # print(s)
                if s.strip(' \n*').lstrip('0123456789.- ').startswith(("references", 'virial coefficients', 'Virial coefficients', 'SIT epsilon coefficients', 'Pitzer parameters')):
                    break

            for j in spec:
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]] # remove formula and specie number
                rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ] # remove all coefficients
                if (len([k for k in rxnlst if k not in missing_species]) == len(rxnlst)):
                    fout.writelines("%s\n" % j)
                    fout.writelines( "      mole wt.=   %1.4f g\n" %  MWdic[j])
                    fout.writelines( "     %s species in reaction\n" % sourcedic[j][1])
                    Rxn = sourcedic[j][2:]
                    for i in range(len(Rxn)):
                        i = i + 1
                        if (i == 1) | (i == 7) | (i == 13):
                            fout.writelines( "    %9.4f " %  float(Rxn[i - 1]))
                        elif i % 2 != 0:
                            fout.writelines( "%9.4f " %  float(Rxn[i - 1]))
                        else:
                            fout.writelines( "%-9s     " %  (Rxn[i - 1]))
                        if (i % 6 == 0) | (i % 12 == 0) | (i == len(Rxn)):
                            fout.writelines( "\n")
                    fout.writelines( "\n")
                else:
                    continue

        else:
            fout.writelines( "   0 oxides\n\n" )

        #% Pitzer parameters
        if activity_model != 'h-m-w':
            fout.writelines( "-end-\n\n")
        elif activity_model == 'h-m-w':
            fout.writelines( "-end-\n*\n")
            if sourceformat.upper() == 'GWB':
                fout.writelines(s)
                for i in range(15000):
                    s = fid.readline()
                    fout.writelines(s)
                    if not s.strip(' \n').startswith("*"):
                        break

                for i in range(15000):
                    s = fid.readline()
                    if any(s.lstrip().rstrip('\n').startswith(x) for x in act_param['act_list']):
                        rowlst = []; rowlst.append(s)
                        for i in range(150):
                            s = fid.readline()
                            if s.lstrip().rstrip('\n').startswith(""):
                                break
                            rowlst.append(s)
                        if all([x not in missing_species for x in rowlst[0].rstrip('\n').split()]):
                            fout.writelines(rowlst)
                            fout.writelines( "\n")
                    else:
                        fout.writelines(s)
            elif sourceformat.upper() == 'EQ36':
                fout.writelines("* Pitzer parameters are represented by the 25C-centric four-term temperature \n" + \
                                "* function given by: \n" +  "* \n" + \
                                "* x(T) = a1 + a2*(1/T - 1/298.15) + a3*ln(T/298.15) + a4*(T - 298.15) \n" + "*  \n" + \
                                "* where T is temperature in Kelvin and a1 through a4 denote the temperature  \n" + \
                                "* function fitting coefficients for the temperature-dependent Pitzer  \n" + \
                                "* parameters. The conversion of non-standard or expanded forms of Pitzer  \n" + \
                                "* interaction parameters recently adopted by several workers for highly  \n" + \
                                "* soluble salts to the standard form currently embedded in EQ3/6 Version 8.0  \n" + \
                                "* was conducted using the approach described in 02Rard/Wij.  This conversion  \n" + \
                                "* imposes usage limits on these parameters within a valid range of temperature  \n" + \
                                "* and ionic strength. \n" + "*  \n" + \
                                "* In GWB (Version 9.0.1 or lower) Pitzer parameters are represented by the  \n" + \
                                "* 25C-centric five-term temperature function given by: \n" + "*  \n" + \
                                "* val = val25 + c1*(Tk-Tr) + c2*(1/Tk-1/Tr) + c3*ln(Tk/Tr) + c4(Tk^2-Tr^2) \n" + "*  \n" + \
                                "* So the last temperature term (c4(Tk^2-Tr^2)) will be set to zero \n" + \
                                "* since no such term is available in the data0.ypf.R0. \n" + "*  \n" + \
                                "* In GWB (Version 9.0.2 or higher) Pitzer parameters are represented by the  \n" + \
                                "* 25C-centric six-term temperature function given by: \n" + \
                                "* val = val25 + c1*(Tk-Tr) + c2*(1/Tk-1/Tr) + c3*ln(Tk/Tr) + c4(Tk^2-Tr^2) + c5(1/Tk^2-1/Tr^2) \n" + \
                                "* So the last two temperature terms (c4(Tk^2-Tr^2) and c5(1/Tk^2-1/Tr^2))   \n" + \
                                "* will be set to zero (or left blank) since no such term is available.  \n\n")
                for k in act_param['alpha_beta'].keys():
                    if all([x not in missing_species for x in k.rstrip('\n').split()]):
                        ks = k.rstrip('\n').split()
                        fout.writelines('%-8s\n' % ks[0]) if len(ks) == 1 else fout.writelines('%-8s  %-8s\n' % (ks[0], ks[1]))  if len(ks) == 2 else fout.writelines('%-8s  %-8s  %-8s\n' % (ks[0], ks[1], ks[2]))
                        lst = ['beta0', 'beta1', 'beta2', 'cphi', 'alpha1', 'alpha2']
                        for order in lst:
                            fout.writelines('     %-6s  = %s \n' % (order, act_param[order][k]))
                        fout.writelines('\n')
                fout.writelines('-end- end of beta set, begin with theta set of 2nd virial coefficients  \n\n')
                for k in act_param['theta'].keys():
                    if all([x not in missing_species for x in k.rstrip('\n').split()]):
                        ks = k.rstrip('\n').split()
                        fout.writelines('%-8s\n' % ks[0]) if len(ks) == 1 else fout.writelines('%-8s  %-8s\n' % (ks[0], ks[1]))  if len(ks) == 2 else fout.writelines('%-8s  %-8s  %-8s\n' % (ks[0], ks[1], ks[2]))
                        fout.writelines('     %-6s  = %s \n' % ('theta', act_param['theta'][k]))
                        fout.writelines('\n')
                fout.writelines('-end-  end of theta set, begin with lambda set  \n\n')
                for k in act_param['lambda'].keys():
                    if all([x not in missing_species for x in k.rstrip('\n').split()]):
                        ks = k.rstrip('\n').split()
                        fout.writelines('%-8s\n' % ks[0]) if len(ks) == 1 else fout.writelines('%-8s  %-8s\n' % (ks[0], ks[1]))  if len(ks) == 2 else fout.writelines('%-8s  %-8s  %-8s\n' % (ks[0], ks[1], ks[2]))
                        fout.writelines('     %-6s  = %s \n' % ('lambda', act_param['lambda'][k]))
                        fout.writelines('\n')
                fout.writelines('-end- end of lambda set, begin with psi set  \n\n')
                for k in act_param['psi'].keys():
                    if all([x not in missing_species for x in k.rstrip('\n').split()]):
                        ks = k.rstrip('\n').split()
                        fout.writelines('%-8s\n' % ks[0]) if len(ks) == 1 else fout.writelines('%-8s  %-8s\n' % (ks[0], ks[1]))  if len(ks) == 2 else fout.writelines('%-8s  %-8s  %-8s\n' % (ks[0], ks[1], ks[2]))
                        fout.writelines('     %-6s  = %s \n' % ('psi', act_param['psi'][k]))
                        fout.writelines('\n')
                fout.writelines('-end- end of psi set \n')

        fout.writelines('* references\n')
        fout.writelines('** Please copy references to here from the corresponding\n')
        fout.writelines('** sequential-access version of the direct-access SUPCRT database.\n* stop.\n\n')

        #% close all files
        fid.close()
        fout.close()

        if clay_thermo.lower() == 'yes':
            fclay.close()

        return print('Success, your new GWB database is ready for download')

    def write_EQ36db(self, T, P ):
        """
        This function writes the new EQ3/6 database into a new folder called "output"   \n
        Parameters
        ----------
            T               :    temperature [°C]   \n
            P               :    pressure [bar]   \n

        Returns
        -------
            Outputs the new database to an ASCII file with filename described in 'objdb'.   \n
        Usage
        -------
         Example:
             (1) General format with default dielectric constant and CO2 activity model and exclusions
                 of solid solutions   \n
                 write_EQ36db(T, P )   \n
             (2) Inclusion of solid solutions and clay thermo and exclusion of solid solution of clinopyroxene  \n
                 write_EQ36db(T, P )   \n
             (3) Inclusion of all solid solutions and clay thermo with \emph{'Duan_Sun'} CO2 activity model and 'FGL97'
                 dielectric constant calculation \n
                 write_EQ36db(T, P )   \n

        """

        nCa_cpx = self.cpx_Ca;
        solid_solution = self.solid_solution;      clay_thermo = self.clay_thermo
        sourcedb = self.sourcedb
        objdb = self.objdb;                        Dielec_method = self.Dielec_method
        heatcap_method = self.heatcap_method;      sourceformat = self.sourceformat
        densityextrap = self.densityextrap

        dbaccessdic, dbname, sourcedic, specielist = self.dbr.dbaccessdic, self.dbr.dbaccess, self.dbr.sourcedic, self.dbr.specielist

        if sourceformat.upper() == 'GWB':
            MWdic, act_param, chargedic = self.dbr.MWdic, self.dbr.act_param, self.dbr.chargedic
            dataset = '1kbu'

            periodic_table = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                               'PeriodicTableJSON.json'), encoding='utf8')
            data = json.load(periodic_table)
            Element = {data['elements'][x]['symbol'] : pd.DataFrame([data['elements'][x]['name'],
                                                                     data['elements'][x]['atomic_mass']],
                                                                    index = ['name', 'mass']).T
                       for x in range(len(data['elements']))}
            periodic_table.close()
            specielist[0] = [ symbol for x in specielist[0] for symbol, item in Element.items() 
                             if item.name[0][:4] == x[:4] ]
            
        elif sourceformat.upper() == 'EQ36':
            block_info, Elemlist, act_param = self.dbr.block_info, self.dbr.Elemlist, self.dbr.act_param
            dataset = sourcedb.split('.')[-1]

        if os.path.exists(os.path.join(os.getcwd(), 'output/EQ36')) == False:
                os.makedirs(os.path.join(os.getcwd(), 'output/EQ36'))

        logKnan_alert = False
        missing_species = []
        all_species_source = [[i]+k for i, k in sourcedic.items() if i not in (['eh', 'e-', 'H2O']) ]
        all_species_source = [[k for j, k in enumerate(all_species_source[i])
                               if (j not in [1, 3] and k not in all_species_source[i][:j]
                                   and k not in specielist[0] and str(k).strip('0123456789.- ') != '') ]
                              if  (i <= len(specielist[0]))
                              else [k for j, k in enumerate(all_species_source[i])
                                    if (j not in [1, 3] and k not in all_species_source[i][:j] and str(k).strip('0123456789.- ') != '') ]
                              for i in range(len(all_species_source)) ]
        for num in range(len(all_species_source)): #
            if num < len(all_species_source):
                lst = [v for v in all_species_source[num] if v not in (specielist[7] + ['eh', 'e-', 'H2O']) ]

                bool_miss = [x.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
                             not in dbaccessdic.keys() for x in lst  ]
                if any(bool_miss):
                    sublist = [i for (i, v) in zip(lst, bool_miss) if v ]
                    if lst[0] not in sublist:
                        missing_species.append([lst[0]] + sublist)
                    else:
                        missing_species.append(sublist)

        missingfile = open(os.path.join(os.path.abspath("."),'output', 'EQ36', 'spxNotFound.txt'), 'w')
        #missing_species = [i for i in missing_species if len(i)<1]
        for line in missing_species:
            if len(line) > 0:
                missingfile.writelines(line[0])
                missingfile.writelines('\n')
                for i in range(len(line)):
                    missingfile.writelines('   %s' % line[i])
                    missingfile.writelines('\n')
        missingfile.close()
        missing_species = [item for sublist in missing_species for item in sublist]
        elem_avail = list(set([k for i, j in enumerate([[i] + k for i, k in sourcedic.items()
                                                        if i not in missing_species])
                               for l, k in enumerate(j) if i < len(specielist[1]) and str(k).strip('0123456789.- ') != '' and
                               not str(k).endswith(("+", "-", '(aq)', '(g)')) and k not in ['O2', 'H2O'] and len(k) < 3]))
        all_species_source = [k for j in all_species_source for i, k in enumerate(j) ]
        all_species_source = list(set(all_species_source))
        all_species_avail = [j for j in all_species_source if j not in missing_species]

        if objdb == None:
            objdb = 'data0.%s' % (int(P[0]))

        fout = open(os.path.join(os.path.abspath("."),'output', 'EQ36', objdb + '.%s' % dataset), 'w+')  # + timestr

        fid = open(sourcedb, 'r')

        dbname2 = 'and supcrtbl.dat' if self.dbHP_dir is not None else 'and berman.dat' if self.dbBerman_dir is not None else ''
        if sourceformat.upper() != 'GWB':
            s = fid.readline()
            fout.writelines(s)
            for i in range(500) :
                s = fid.readline()
                if s.startswith('Generated', 0) | s.startswith('Data', 0) | (s.rstrip('\n') == ""):
                    break
            fout.writelines('CII: ' + ' pyGeochemCalc.2021' + '\n')
            fout.writelines('Generated by: ' + ' pyGeochemCalc, ' + time.ctime() + '\n')
            fout.writelines('Output package:  eq3\n' + 'Data set:        ' + dbname + ' ' + dbname2 + '\n')
        else:
            fout.writelines('data0.com.RX ! dataset converted from gwb database \n' + \
                            'CII: ' + ' pyGeochemCalc.2021' + '\n' + \
                                'Generated by: ' + ' pyGeochemCalc, ' + time.ctime() + '\n' + \
                                    'Output package:  eq3\n' + 'Data set:        ' + dbname + ' ' + dbname2 + '\n')

        if Dielec_method.upper() == 'DEW':
            water = ZhangDuan(T = T, P = P)
            rho, dGH2O, dHH2O, SH2O = water.rho, water.G, np.nan*np.ones(len(T)), np.nan*np.ones(len(T))
        else:
            water = iapws95(T = T, P = P)
            rho, dGH2O, dHH2O, SH2O = water.rho, water.G, water.H, water.S
        #copy and paste lines till temperature rows
        for i in range(2500):
            s = fid.readline()
            if sourceformat.upper() != 'GWB':
                fout.writelines(s) 
                if s.startswith('+', 0):
                    break
            else:
                if s.strip('\n').strip('* ') in ['temperatures', 'temperatures (degC)', 'Temperature grid (degC)']:
                    break
        if sourceformat.upper() != 'GWB':
            s = fid.readline()
            fout.writelines(s)
            s = fid.readline()
            fout.writelines(s)
            s = fid.readline()
            fout.writelines(s)
        else:
            fout.write( "+" + "-"*68 + "\n")
            fout.write("Miscellaneous parameters\n")
            fout.write( "+" + "-"*68 + "\n")
            fout.write("Temperature limits (degC)\n")
        fout.writelines('      %9.4f %9.4f\n' % (T[0], T[-1]))


        if sourceformat.upper() != 'GWB':
            for i in range(50) :
                s = fid.readline()
                if s.strip('\n').strip('* ') in ['temperatures', 'temperatures (degC)', 'Temperature grid (degC)']:
                    break
        fout.writelines(s) if sourceformat.upper() != 'GWB' else fout.writelines(s.strip('* ').split('(')[0] + '\n')
        for i in range(len(T)):
            i = i + 1
            if (i == 1) | (i == 5):
                fout.writelines( "      %9.4f" %  T[i-1])
            else:
                fout.writelines( " %9.4f" %  T[i-1])
            if (i % 4 == 0) | (i == len(T)):
                fout.writelines( "\n")

        for i in range(50) :
            s = fid.readline()
            if s.strip('\n').strip('* ') in ['pressures', 'Pressure grid (bars)', 'pressures (bar)']:
                break
        fout.writelines(s) if sourceformat.upper() != 'GWB' else fout.writelines(s.strip('* ').split('(')[0] + '\n')
        for i in range(len(P)):
            i = i + 1
            if (i == 1) | (i == 5):
                fout.writelines( "      %9.4f" %  P[i-1])
            else:
                fout.writelines( " %9.4f" %  P[i-1])
            if (i % 4 == 0) | (i == len(P)):
                fout.writelines( "\n")

        #% Calculation for debye huckel and bdot and water properties
        waterdielc = water_dielec(T = T, P = P, Dielec_method = Dielec_method)
        E, Adh, Bdh, bdot = waterdielc.E, waterdielc.Ah, waterdielc.Bh, waterdielc.bdot

        rhoEG = {'rho': rho, 'E': E,  'dGH2O': dGH2O}

        # Calculate the rho E G for density extrapolation method here so we have it below
        rhoEGextrap = {}
        if any(rhoEG['rho'] < 350):
            subBornptrs = rhoEG['rho'] < 350
            for i, j in enumerate(zip(T[subBornptrs], P[subBornptrs])):
                rhoextrap = np.linspace(350, 550, 3)
                Pextrap = iapws95(T = j[0], rho = rhoextrap).P if Dielec_method.upper() != 'DEW' else ZhangDuan(T = j[0], rho = rhoextrap).P
                Textrap = j[0]*np.ones(np.size(Pextrap))

                dGH2O = iapws95(T = Textrap, P = Pextrap).G if Dielec_method.upper() != 'DEW' else ZhangDuan(T = Textrap, P = Pextrap).G
                E = water_dielec(T = Textrap, P = Pextrap, Dielec_method = Dielec_method).E
                rhoextrap = np.around(rhoextrap, 3)
                rhoEGextrap['%d_%d' % (j[0], j[1])]= {'rho': rhoextrap,'E': E, 'dGH2O': dGH2O,
                                                       'Textrap': Textrap, 'Pextrap': Pextrap}

        #skip lines till adh rows
        if act_param['activity_model'] == 'debye-huckel':
            for i in range(50) :
                s = fid.readline()
                if '(adh)' in s.strip('\n') or 'Debye-Huckel A_gamma' in s.strip('\n'):
                    break
            fout.writelines(s) if sourceformat.upper() != 'GWB' else fout.writelines(s.strip('* '))
            for i in range(len(Adh)):
                i = i + 1
                if (i == 1) | (i == 5):
                    fout.writelines( "      %9.4f" %  Adh[i-1])
                else:
                    fout.writelines( " %9.4f" %  Adh[i-1])
                if (i % 4 == 0) | (i == len(Adh)):
                    fout.writelines( "\n")
            #skip lines till bdh rows
            for i in range(50) :
                s = fid.readline()
                if '(bdh)' in s.strip('\n') or 'Debye-Huckel B_gamma' in s.strip('\n'):
                    break
            fout.writelines(s) if sourceformat.upper() != 'GWB' else fout.writelines(s.strip('* '))
            for i in range(len(Bdh)):
                i = i + 1
                if (i == 1) | (i == 5):
                    fout.writelines( "      %9.4f" %  Bdh[i-1])
                else:
                    fout.writelines( " %9.4f" %  Bdh[i-1])
                if (i % 4 == 0) | (i == len(Bdh)):
                    fout.writelines( "\n")
            #skip lines till bdot rows
            for i in range(50) :
                s = fid.readline()
                if 'bdot' in s.strip('\n') or 'B-dot' in s.strip('\n'):
                    break
            fout.writelines(s) if sourceformat.upper() != 'GWB' else fout.writelines(s.strip('* '))
            for i in range(len(bdot)):
                i = i + 1
                if (i == 1) | (i == 5):
                    fout.writelines( "      %9.4f" %  bdot[i-1])
                else:
                    fout.writelines( " %9.4f" %  bdot[i-1])
                if (i % 4 == 0) | (i == len(bdot)):
                    fout.writelines( "\n")

            #skip lines till cco2 rows
            for i in range(50) :
                s = fid.readline()
                if 'cco2' in s.strip('\n') or 'c co2' in s.strip('\n'):
                    break
            if sourceformat.upper() != 'GWB':
                fout.writelines(s)
                s = fid.readline()
                fout.writelines(s)
                s = fid.readline()
                fout.writelines(s)
                s = fid.readline()
                fout.writelines(s)
            else:
                fout.writelines('cco2   (coefficients for the Drummond (1981) polynomial) \n' + \
                                '         -1.0312              0.0012806 \n' + \
                                    '          255.9                 0.4445 \n' + \
                                        '      -0.001606 \n')
                
        elif act_param['activity_model'] == 'h-m-w':
            for i in range(50) :
                s = fid.readline()
                if any(re.findall(r'|'.join(('aphi', 'debye huckel')), s.strip('\n'), re.IGNORECASE)):
                    break
            fout.writelines(s)
            Aphi = Adh*np.log(10)/3
            for i in range(len(Aphi)):
                i = i + 1
                if (i == 1) | (i == 5):
                    fout.writelines( "      %9.4f" %  Aphi[i-1])
                else:
                    fout.writelines( " %9.4f" %  Aphi[i-1])
                if (i % 4 == 0) | (i == len(Aphi)):
                    fout.writelines( "\n")

        for i in range(50) :
            s = fid.readline()
            if any(re.findall(r'|'.join(('log k for eh reaction', 'Eh reaction: logKr')), s.strip('\n').strip('*'), re.IGNORECASE)):
                break
        fout.writelines(s) if sourceformat.upper() != 'GWB' else fout.writelines(s.strip('* '))
        
        #% Calculations for "log k for eh" rows
        logK = calcRxnlogK( T = T, P = P, Specie = 'eh', dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                           specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                           sourceformat = sourceformat, densityextrap = densityextrap,
                           heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap).logK
        logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
        for i in range(len(logK)):
            i = i + 1
            if (i == 1) | (i == 5):
                fout.writelines( "      %9.4f" %  logK[i-1])
            else:
                fout.writelines( " %9.4f" %  logK[i-1])
            if (i % 4 == 0) | (i == len(logK)):
                fout.writelines( "\n")

        if sourceformat.upper() != 'GWB':
            for i in range(50) :
                s = fid.readline()
                if s.startswith('+', 0):
                    break
        if act_param['activity_model'] == 'debye-huckel':
            if sourceformat.upper() != 'GWB':
                fout.writelines(s)
                s = fid.readline()
                fout.writelines(s)
                s = fid.readline()
                fout.writelines(s)
                s = fid.readline()
                fout.writelines(s)

                # copy and paste bdot parameters
                for i in range(3000) :
                    s = fid.readline()
                    s = s.replace(' acid','_acid').replace(' high','_high').replace(' low','_low') if 'acid' in s else s
                    s_mod = s.split()[0]
                    if s.startswith('+--', 0):
                        break
                    if s_mod in all_species_avail:
                        fout.writelines(s)
                    else:
                        missing_species.append(s_mod)
                fout.writelines(s)
                s = fid.readline()
                fout.writelines(s)
                s = fid.readline()
                fout.writelines(s)
            else:
                fout.write( "+" + "-"*68 + "\n")
                fout.write("bdot parameters \n")
                fout.write( "+" + "-"*68 + "\n")
                fout.write("*  species name                 azer0  neutral ion type \n")

                f_ionsize = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ion_size.txt'), 'r')
                Rd = f_ionsize.readlines()
                Rd = Rd[1:]
                Rd = list(OrderedDict.fromkeys(Rd))
                Rd_dup = [x for n, x in enumerate(Rd) if x.split()[0] in [l.split()[0] for l in Rd[:n]]]
                Rd = [x for x in Rd if x not in Rd_dup]
                Rd = [x if x.split()[0] != 'O2(aq)' else x.replace('O2(aq)', 'O2(g) ') for x in Rd if x.split()[0] in chargedic.keys() ]
                f_ionsize.close() #
                for i in range(len(Rd)):
                    fout.writelines(Rd[i])
                fout.write( "+" + "-"*68 + "\n")
        elif act_param['activity_model'] == 'h-m-w':
            fout.writelines(s)
            s = fid.readline()
            fout.writelines(s)
            s = fid.readline()
            fout.writelines(s)
            for i in range(2000):
                s = fid.readline()
                if (s.rstrip('\n') == "elements"):
                    break
                if any(s.lstrip().rstrip('\n').startswith(x) for x in act_param['act_list']):
                    rowlst = []; rowlst.append(s)
                    for i in range(50):
                        s = fid.readline()
                        if s.lstrip().rstrip('\n').startswith("+" + "-"*30):
                            break
                        rowlst.append(s)
                    if all([x in all_species_avail for x in rowlst[0].rstrip('\n').split()]):
                        fout.writelines(rowlst)
                        fout.writelines( "+" + "-"*64 + "\n")
                else:
                    #break
                    fout.writelines(s)
            fout.writelines(s)
            s = fid.readline()
            fout.writelines(s)


        # copy and paste elements
        if sourceformat.upper() != 'GWB':
            counter = 0
            for i in range(2000) :
                s = fid.readline()
                s_mod = s.split()[0]
                if s_mod in elem_avail:
                    fout.writelines(s)
                    counter = counter + 1
                if s.startswith('+', 0):
                    break
            fout.writelines(s)
            s = fid.readline()
            fout.writelines(s)
            s = fid.readline()
            fout.writelines(s)
        else:
            #skip lines till "elements" rows
            for i in range(5000) :
                s = fid.readline()
                if s.rstrip('\n').lstrip('0123456789.- ') == 'elements':
                    break
            fout.writelines( "%s \n" % s.rstrip('\n').lstrip('0123456789.- '))
            fout.writelines( "+" + "-"*68 + "\n")
    
            #copy and paste lines till "basis" rows
            for i in range(1000) :
                s = fid.readline()
                s_mod = s.split() if s.strip('\n') != '' else s.strip('\n')
                if s.rstrip('\n').lstrip('0123456789.- ') == 'basis species':
                    break
                if len(s_mod) > 1:
                    if s_mod[1].strip('()') in elem_avail:
                        fout.writelines('%-2s %14s \n' % (s_mod[1].strip('()'), s_mod[-1]))
            fout.writelines( "+" + "-"*68 + "\n")
            fout.writelines( "%s \n" % s.rstrip('\n').lstrip('0123456789.- '))
            fout.writelines( "+" + "-"*68 + "\n")

        #% Basis reactions
        counter = 0
        for j in specielist[1]:
            k = j.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
            if j not in missing_species:
                fout.writelines('%s\n' % j.replace('O2(aq)', 'O2(g)')) if j == 'O2(aq)' else fout.writelines('%s\n' % j) 

                if sourceformat.upper() != 'GWB':
                    if j == 'O2(g)':
                        fout.writelines(block_info['O2(g)_b'])
                    else:
                        fout.writelines(block_info[j])
                else:
                    filler = re.sub('[^-0123456789\.]', ' ', chargedic[j]).split()
                    fout.writelines('     sp.type =  basis \n') if j != 'O2(aq)' else fout.writelines('     sp.type =  gas     refstate \n')
                    fout.writelines('*    EQ3/6   =  com, alt, sup, pit\n' +\
                                    '     revised =  - \n' +\
                                    '*    mol.wt. =  %s g/mol\n' % filler[-1] +\
                                    '*    DHazero =   %s \n' % filler[1] +\
                                    '     charge  =   %s \n' % filler[0])

                fout.writelines('****\n')
                if sourceformat.upper() != 'GWB':
                    fout.writelines( "     %s element(s):\n" % int(len(Elemlist[j])/2))
                    Rxn = Elemlist[j]
                else:                    
                    Rxn = [[v,k] for k,v in dict( sorted(calc_elem_count_molewt(j.rstrip('(aq)(g)') )[0].items(), 
                                                         key=lambda x: x[0].lower()) ).items()]
                    Rxn = [item for sublist in Rxn for item in sublist]
                    fout.writelines( "     %s element(s):\n" % int(len(Rxn)/2))
                for i in range(len(Rxn)):
                    i = i + 1
                    if (i == 1) | (i == 7):
                        fout.writelines( "    %9.4f " %  float(Rxn[i - 1]))
                    elif i % 2 != 0:
                        fout.writelines( "%9.4f " %  float(Rxn[i - 1]))
                    else:
                        fout.writelines( "%-9s     " %  (Rxn[i - 1]))
                    if (i % 6 == 0) | (i == len(Rxn)):
                        fout.writelines( "\n")
                fout.writelines('****\n')
                fout.writelines( "*    gflag = 1 [reported delG0f used]\n" )
                fout.writelines( "*    extrapolation algorithm: supcrt92 [92joh/oel]\n" )
                if j != 'H2O':
                    ref = dbaccessdic[k][1].split('  ')[0]
                    ref = ref.split(':')[1] if ('ref' in ref) or ('REF' in ref) else ref
                    dG, dH, S = dbaccessdic[k][2], dbaccessdic[k][3], dbaccessdic[k][4]
                else:
                    dG, dH, S, ref = dGH2O[0], dHH2O[0], SH2O[0], 'iapws95/' + Dielec_method
                fout.writelines( "*    ref-state data  [source:   %s  ]\n" % ref)
                fout.writelines( "*         delG0f =   %8.3f  kcal/mol\n" % (dG/1000) )
                fout.writelines( "*         delH0f =   %8.3f  kcal/mol\n" % (dH/1000))
                fout.writelines( "*         S0PrTr =   %8.3f  cal/(mol*K)\n" % S)
                fout.writelines( "+" + "-"*68 + "\n")
                counter = counter + 1
            else:
                continue
        fout.writelines( "auxiliary basis species\n")
        fout.writelines( "+" + "-"*68 + "\n")

        #% Auxiliary Basis reactions
        specielist[2] = specielist[2] + ['O2(aq)'] if sourceformat.upper() == 'GWB' else specielist[2]
        for j in specielist[2]:
            k = j.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
            rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1, 2, 3]]
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ] # remove all coefficients
            if (j not in missing_species) and (len([i for i in rxnlst if i not in missing_species]) == len(rxnlst)):
                if sourcedic[j][0] != '':
                    fout.writelines('%-25s %s \n' % (j, sourcedic[j][0]))
                else:
                    fout.writelines('%-25s %s \n' % (j, dbaccessdic[k][0]))
                
                if sourceformat.upper() != 'GWB':
                    fout.writelines(block_info[j])
                else:
                    filler = re.sub('[^-0123456789\.]', ' ', chargedic[j]).split()
                    fout.writelines('     sp.type =  aux\n' +\
                                    '*    EQ3/6   =  com, alt, sup \n' +\
                                    '     revised = - \n' +\
                                    '*    mol.wt. =  %s g/mol\n' % filler[-1] +\
                                    '*    DHazero =   %s \n' % filler[1] +\
                                    '     charge  =   %s \n' % filler[0])

                fout.writelines('****\n')
                if sourceformat.upper() != 'GWB':
                    fout.writelines( "     %s element(s):\n" % int(len(Elemlist[j])/2))
                    Elem = Elemlist[j]
                else:                    
                    # print(j)
                    formula = j.rstrip('(aq)(g)') if sourcedic[j][0] == '' else j if not j.endswith('(aq)') else dbaccessdic[k][0].rstrip('(aq)(g)') #.rstrip('(+0123456789)')
                    Elem = [[v,k] for k,v in dict( sorted(calc_elem_count_molewt(formula)[0].items(), 
                                                         key=lambda x: x[0].lower()) ).items()]
                    Elem = [item for sublist in Elem for item in sublist]
                    fout.writelines( "     %s element(s):\n" % int(len(Elem)/2))

                for i in range(len(Elem)):
                    i = i + 1
                    if (i == 1) | (i == 7):
                        fout.writelines( "    %9.4f " %  float(Elem[i - 1]))
                    elif i % 2 != 0:
                        fout.writelines( "%9.4f " %  float(Elem[i - 1]))
                    else:
                        fout.writelines( "%-9s     " %  (Elem[i - 1]))
                    if (i % 6 == 0) | (i == len(Elem)):
                        fout.writelines( "\n")
                fout.writelines('****\n')
                if sourceformat.upper() != 'GWB':
                    fout.writelines( "     %s species in aqueous dissociation reaction:\n" % sourcedic[j][1])
                    Rxn = sourcedic[j][2:]
                else:
                    fout.writelines( "     %s species in aqueous dissociation reaction:\n" % (sourcedic[j][1] + 1))
                    sourcedic[j] = [k if k != 'O2(aq)' else k.replace('O2(aq)', 'O2(g)') for k in sourcedic[j]]
                    Rxn = ['-1.0000', 'O2(aq)', '1.0000', 'O2(g)'] if sourceformat.upper() == 'GWB' and j == 'O2(aq)' else ['-1.0000', '%s' % j] + sourcedic[j][2:]
                for i in range(len(Rxn)):
                    i = i + 1
                    if (i == 1) | (i == 5) | (i == 9):
                        fout.writelines( "  %9.4f " %  float(Rxn[i - 1]))
                    elif i % 2 != 0:
                        fout.writelines( "%9.4f " %  float(Rxn[i - 1]))
                    else:
                        fout.writelines( " %-21s     " %  (Rxn[i - 1]))
                    if (i % 4 == 0) | (i == len(Rxn)):
                        fout.writelines( "\n")
                fout.writelines('*\n')
                fout.writelines('**** logK grid [T, P @ Miscellaneous parameters]\n')
                sourcedic[j] = ['', 1, '1.0000', 'O2(g)'] if sourceformat.upper() == 'GWB' and j == 'O2(aq)' else sourcedic[j]
                logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                                   specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                   sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'aqueous',
                                   heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap, ThermoInUnit = self.ThermoInUnit)
                if densityextrap.lower() == 'yes': 
                    if all(logK.nonsubBornptrs) == True: # if all densities are >= 350
                        logKnan_alert = False            # turn off the prompts for using Density extrapolation
                    else:
                        logKnan_alert = True
                else:
                    logKnan_alert = False                # turn off the prompts for using Density extrapolation
                logK = logK.logK
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values

                for i in range(len(logK)):
                    i = i + 1
                    if (i == 1) | (i == 5):
                        fout.writelines( "      %9.4f" %  logK[i-1])
                    else:
                        fout.writelines( "  %9.4f" %  logK[i-1])
                    if (i % 4 == 0) | (i == len(logK)):
                        fout.writelines( "\n")
                fout.writelines( "*    gflag = 1 [reported delG0f used]\n" )
                fout.writelines( "*    extrapolation algorithm: supcrt92 [92joh/oel]\n" )
                if j != 'H2O':
                    ref = dbaccessdic[k][1].split('  ')[0]
                    ref = ref.split(':')[1] if ('ref' in ref) or ('REF' in ref) else ref
                    dG, dH, S = dbaccessdic[k][2], dbaccessdic[k][3], dbaccessdic[k][4]
                else:
                    dG, dH, S, ref = dGH2O[0], dHH2O[0], SH2O[0], 'iapws95/' + Dielec_method
                fout.writelines( "*    ref-state data  [source:   %s  ]\n" % ref)
                fout.writelines( "*         delG0f =   %8.3f  kcal/mol\n" % (dG/1000) )
                fout.writelines( "*         delH0f =   %8.3f  kcal/mol\n" % (dH/1000))
                fout.writelines( "*         S0PrTr =   %8.3f  cal/(mol*K)\n" % S)
                fout.writelines( "+" + "-"*68 + "\n")
            else:
                continue
        fout.writelines( "aqueous species\n")
        fout.writelines( "+" + "-"*68 + "\n")
        if logKnan_alert == True:
            warnings.warn('Some temperature and pressure points are out of aqueous species HKF eqns regions of applicability, hence, density extrapolation has been applied')

        #% Aqueous reactions
        for j in specielist[3]:
            k = j.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
            rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1, 2, 3]]
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ]
            if (j not in missing_species) and (len([i for i in rxnlst if i not in missing_species]) == len(rxnlst)):
                if sourcedic[j][0] != '':
                    fout.writelines('%-25s %s \n' % (j, sourcedic[j][0]))
                else:
                    fout.writelines('%-25s %s \n' % (j, dbaccessdic[k][0]))

                if sourceformat.upper() != 'GWB':
                    fout.writelines(block_info[j])
                else:
                    filler = re.sub('[^-0123456789\.]', ' ', chargedic[j]).split()
                    fout.writelines('     sp.type =  aqueous\n' +\
                                    '*    EQ3/6   =  com, alt, sup \n' +\
                                    '     revised =  - \n' +\
                                    '*    mol.wt. =  %s g/mol\n' % filler[-1] +\
                                    '*    DHazero =   %s \n' % filler[1] +\
                                    '     charge  =   %s \n' % filler[0])

                fout.writelines('****\n')
                if sourceformat.upper() != 'GWB':
                    fout.writelines( "     %s element(s):\n" % int(len(Elemlist[j])/2))
                    Elem = Elemlist[j]
                else: 
                    # print(j)
                    filler = ('(aq)', '(But)', '(Prop)', '(Pent)', '(For)', '(Gly)', '(Glyc)', '(Lac)', 'Acetate')
                    formula = j.rstrip('(aq)(g)') if sourcedic[j][0] == '' else j if not any([l in j for l in filler]) else re.sub('(aq)', '', dbaccessdic[k][0]) #.rstrip('(+0123456789)')
                    Elem = [[v,k] for k,v in dict( sorted(calc_elem_count_molewt(formula)[0].items(), 
                                                         key=lambda x: x[0].lower()) ).items()]
                    Elem = [item for sublist in Elem for item in sublist]
                    fout.writelines( "     %s element(s):\n" % int(len(Elem)/2))

                for i in range(len(Elem)):
                    i = i + 1
                    if (i == 1) | (i == 7):
                        fout.writelines( "    %9.4f " %  float(Elem[i - 1]))
                    elif i % 2 != 0:
                        fout.writelines( "%9.4f " %  float(Elem[i - 1]))
                    else:
                        fout.writelines( "%-9s     " %  (Elem[i - 1]))
                    if (i % 6 == 0) | (i == len(Elem)):
                        fout.writelines( "\n")
                fout.writelines('****\n')

                if sourceformat.upper() != 'GWB':
                    fout.writelines( "     %s species in aqueous dissociation reaction:\n" % sourcedic[j][1])
                    Rxn = sourcedic[j][2:]
                else:
                    fout.writelines( "     %s species in aqueous dissociation reaction:\n" % (sourcedic[j][1] + 1))
                    sourcedic[j] = [k if k != 'O2(aq)' else k.replace('O2(aq)', 'O2(g)') for k in sourcedic[j]]
                    Rxn = ['-1.0000', '%s' % j] + sourcedic[j][2:]
                
                for i in range(len(Rxn)):
                    i = i + 1
                    if (i == 1) | (i == 5) | (i == 9):
                        fout.writelines( "  %9.4f " %  float(Rxn[i - 1]))
                    elif i % 2 != 0:
                        fout.writelines( "%9.4f " %  float(Rxn[i - 1]))
                    else:
                        fout.writelines( " %-21s     " %  (Rxn[i - 1]))
                    if (i % 4 == 0) | (i == len(Rxn)):
                        fout.writelines( "\n")
                fout.writelines('*\n')
                fout.writelines('**** logK grid [T, P @ Miscellaneous parameters]\n')
                logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                                   specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                   sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'aqueous',
                                   heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap, ThermoInUnit = self.ThermoInUnit).logK
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                for i in range(len(logK)):
                    i = i + 1
                    if (i == 1) | (i == 5):
                        fout.writelines( "      %9.4f" %  logK[i-1])
                    else:
                        fout.writelines( "  %9.4f" %  logK[i-1])
                    if (i % 4 == 0) | (i == len(logK)):
                        fout.writelines( "\n")
                fout.writelines( "*    gflag = 1 [reported delG0f used]\n" )
                fout.writelines( "*    extrapolation algorithm: supcrt92 [92joh/oel]\n" )
                if j != 'H2O':
                    ref = dbaccessdic[k][1].split('  ')[0]
                    ref = ref.split(':')[1] if ('ref' in ref) or ('REF' in ref) else ref
                    dG, dH, S = dbaccessdic[k][2], dbaccessdic[k][3], dbaccessdic[k][4]
                else:
                    dG, dH, S, ref = dGH2O[0], dHH2O[0], SH2O[0], 'iapws95/' + Dielec_method
                fout.writelines( "*    ref-state data  [source:   %s  ]\n" % ref)
                fout.writelines( "*         delG0f =   %8.3f  kcal/mol\n" % (dG/1000) )
                fout.writelines( "*         delH0f =   %8.3f  kcal/mol\n" % (dH/1000))
                fout.writelines( "*         S0PrTr =   %8.3f  cal/(mol*K)\n" % S)
                fout.writelines( "+" + "-"*68 + "\n")
            else:
                continue
        fout.writelines( "solids\n")
        fout.writelines( "+" + "-"*68 + "\n")

        #% Mineral reactions
        solid_solution = 'no' if solid_solution is None else solid_solution
        clay_thermo = 'no' if clay_thermo is None else clay_thermo
        if solid_solution.lower() == 'yes':
            if nCa_cpx is None:
                nCa = 0
            else:
                nCa = nCa_cpx
            solidsolution_no = 11
            fnlist = ['plagio', 'olivine', 'pyroxene', 'cpx'] if nCa > 0 else ['plagio', 'olivine', 'pyroxene']
            for fn in fnlist:
                for nX in np.round(np.linspace(1, 0, solidsolution_no), 1):
                    if fn != 'cpx':
                        ss = calcRxnlogK(X = nX, T = T, P = P, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                         dbaccessdic = dbaccessdic, Specie = fn, densityextrap = densityextrap,
                                         ThermoInUnit = self.ThermoInUnit, rhoEGextrap = rhoEGextrap)
                    else:
                        ss = calcRxnlogK(cpx_Ca = nCa, X = nX, T = T, P = P, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                         dbaccessdic = dbaccessdic, Specie = fn, densityextrap = densityextrap,
                                         ThermoInUnit = self.ThermoInUnit, rhoEGextrap = rhoEGextrap)
                    logK, Rxn = ss.logK, ss.Rxn

                    logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                    outputfmt(fout, logK, Rxn, dataset = 'EQ36')

        # clay minerals
        if clay_thermo.lower() == 'yes':
            fclay = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clay_elements.dat'), 'r')
            Rd = fclay.readlines()
            Rd = [j.replace('-','_').strip('\n') for j in Rd]
            for i in range(len(Rd)):
                ss = calcRxnlogK(T = T, P = P, Specie = 'Clay', elem = Rd[i].split(','),
                                 dbaccessdic = dbaccessdic, ThermoInUnit = self.ThermoInUnit, rhoEG = rhoEG,
                                 rhoEGextrap = rhoEGextrap, densityextrap = densityextrap)
                logK, Rxn = ss.logK, ss.Rxn
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                outputfmt(fout, logK, Rxn, dataset = 'EQ36')

        # other minerals in the source database
        minlst = specielist[4] if sourceformat.upper() != 'GWB' else specielist[5]
        for j in minlst:
            k = j.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
            rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1, 2, 3]]
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ]
            if (j not in missing_species) and (len([k for k in rxnlst if k not in missing_species]) == len(rxnlst)):
                if solid_solution.lower() == 'yes' and j in ['Anorthite', 'Albite', 'Forsterite',
                                                              'Fayalite', 'Enstatite', 'Ferrosilite']:
                    continue
                elif solid_solution.lower() == 'yes' and (nCa == 1) and j in ['Diopside', 'Hedenbergite']:
                    continue
                elif clay_thermo.lower() == 'yes' and j in [ Rd[h].split(',')[0] for h in range(len(Rd))]:
                    continue
                else:
                    if sourcedic[j][0] != '':
                        fout.writelines('%-25s %s \n' % (j, sourcedic[j][0]))
                    else:
                        fout.writelines('%-25s %s \n' % (j, dbaccessdic[k][0]))
                    
                    if sourceformat.upper() != 'GWB':
                        fout.writelines(block_info[j])
                    else:
                        fout.writelines('     sp.type =  solid \n' +\
                                        '*    EQ3/6   =  com, alt, sup \n' +\
                                        '     revised =   - \n' +\
                                        '*    mol.wt. =  %s g/mol\n' % MWdic[j] +\
                                        '     V0PrTr  =   %s cm**3/mol \n' % dbaccessdic[j][5] )

                    fout.writelines('****\n')

                    if sourceformat.upper() != 'GWB':
                        fout.writelines( "     %s element(s):\n" % int(len(Elemlist[j])/2))
                        Elem = Elemlist[j]
                    else:                    
                        formula = re.sub('(s)', '', j) if sourcedic[j][0] == '' else re.sub('(s)', '', dbaccessdic[k][0])
                        Elem = [[v,k] for k,v in dict( sorted(calc_elem_count_molewt(formula)[0].items(), 
                                                             key=lambda x: x[0].lower()) ).items()]
                        Elem = [item for sublist in Elem for item in sublist]
                        fout.writelines( "     %s element(s):\n" % int(len(Elem)/2))

                    for i in range(len(Elem)):
                        i = i + 1
                        if (i == 1) | (i == 7) | (i == 13):
                            fout.writelines( "    %9.4f " %  float(Elem[i - 1]))
                        elif i % 2 != 0:
                            fout.writelines( "%9.4f " %  float(Elem[i - 1]))
                        else:
                            fout.writelines( "%-9s     " %  (Elem[i - 1]))
                        if (i % 6 == 0) | (i == len(Elem)):
                            fout.writelines( "\n")
                    fout.writelines('****\n')

                    if sourceformat.upper() != 'GWB':
                        fout.writelines( "     %s species in reaction:\n" % sourcedic[j][1])
                        Rxn = sourcedic[j][2:]
                    else:
                        fout.writelines( "     %s species in reaction:\n" % (sourcedic[j][1] + 1))
                        sourcedic[j] = [k if k != 'O2(aq)' else k.replace('O2(aq)', 'O2(g)') for k in sourcedic[j]]
                        Rxn = ['-1.0000', '%s' % j] + sourcedic[j][2:]

                    for i in range(len(Rxn)):
                        i = i + 1
                        if (i == 1) | (i == 5) | (i == 9) | (i == 13) | (i == 17) | (i == 21):
                            fout.writelines( "  %9.4f " %  float(Rxn[i - 1]))
                        elif i % 2 != 0:
                            fout.writelines( "%9.4f " %  float(Rxn[i - 1]))
                        else:
                            fout.writelines( " %-21s     " %  (Rxn[i - 1]))
                        if (i % 4 == 0) | (i == len(Rxn)):
                            fout.writelines( "\n")
                    fout.writelines('*\n')
                    fout.writelines('**** logK grid [T, P @ Miscellaneous parameters]\n')
                    logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                                       specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                       sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'minerals',
                                       heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap).logK
                    logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                    for i in range(len(logK)):
                        i = i + 1
                        if (i == 1) | (i == 5):
                            fout.writelines( "      %9.4f" %  logK[i-1])
                        else:
                            fout.writelines( "  %9.4f" %  logK[i-1])
                        if (i % 4 == 0) | (i == len(logK)):
                            fout.writelines( "\n")
                    fout.writelines( "*    gflag = 1 [reported delG0f used]\n" )
                    fout.writelines( "*    extrapolation algorithm: supcrt92 [92joh/oel]\n" )
                    if j != 'H2O':
                        dG, dH, S = dbaccessdic[k][2], dbaccessdic[k][3], dbaccessdic[k][4]
                    else:
                        dG, dH, S, ref = dGH2O[0], dHH2O[0], SH2O[0], 'iapws95/' + Dielec_method
                    fout.writelines( "*    ref-state data  [source:   %s  ]\n" % ref)
                    fout.writelines( "*         delG0f =   %8.3f  kcal/mol\n" % (dG/1000) )
                    fout.writelines( "*         delH0f =   %8.3f  kcal/mol\n" % (dH/1000))
                    fout.writelines( "*         S0PrTr =   %8.3f  cal/(mol*K)\n" % S)
                    fout.writelines( "*    Cp coefficients [source:   %s  ]\n" % ref)
                    fout.writelines( "*         T**0   =   %11.8e  \n" % (dbaccessdic[k][6]) )
                    fout.writelines( "*         T**1   =   %11.8e  \n" % (dbaccessdic[k][7]*10**-3))
                    if dbaccessdic[j][8] < 1:
                        fout.writelines( "*         T**-2  =  %12.8e  \n" % (dbaccessdic[k][8]*10**5))
                    else:
                        fout.writelines( "*         T**-2  =   %11.8e  \n" % (dbaccessdic[k][8]*10**5))
                    fout.writelines( "*         Tlimit =   %7.2fC  \n" % (dbaccessdic[k][9]))


                    fout.writelines( "+" + "-"*68 + "\n")
            else:
                continue
        fout.writelines( "liquids\n")
        fout.writelines( "+" + "-"*68 + "\n")


        #% Liquids reactions
        if sourceformat.upper() != 'GWB':
            for j in specielist[5]:
                k = j.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1, 2, 3]]
                rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ]
                if (j not in missing_species) and (len([k for k in rxnlst if k not in missing_species])==len(rxnlst)):
                    if sourcedic[j][0] != '':
                        fout.writelines('%-25s %s \n' % (j, sourcedic[j][0]))
                    else:
                        fout.writelines('%-25s %s \n' % (j, dbaccessdic[k][0]))
                    fout.writelines(block_info[j])
    
                    fout.writelines('****\n')
                    fout.writelines( "     %s element(s):\n" % int(len(Elemlist[j])/2))
                    Elem = Elemlist[j]
                    for i in range(len(Elem)):
                        i = i + 1
                        if (i == 1) | (i == 7) | (i == 13):
                            fout.writelines( "    %9.4f " %  float(Elem[i - 1]))
                        elif i % 2 != 0:
                            fout.writelines( "%9.4f " %  float(Elem[i - 1]))
                        else:
                            fout.writelines( "%-9s     " %  (Elem[i - 1]))
                        if (i % 6 == 0) | (i == len(Elem)):
                            fout.writelines( "\n")
                    fout.writelines('****\n')
                    fout.writelines( "     %s species in reaction:\n" % sourcedic[j][1])
                    Rxn = sourcedic[j][2:]
                    for i in range(len(Rxn)):
                        i = i + 1
                        if (i == 1) | (i == 5) | (i == 9) | (i == 13):
                            fout.writelines( "  %9.4f " %  float(Rxn[i - 1]))
                        elif i % 2 != 0:
                            fout.writelines( "%9.4f " %  float(Rxn[i - 1]))
                        else:
                            fout.writelines( " %-21s     " %  (Rxn[i - 1]))
                        if (i % 4 == 0) | (i == len(Rxn)):
                            fout.writelines( "\n")
                    fout.writelines('*\n')
                    fout.writelines('**** logK grid [T, P @ Miscellaneous parameters]\n')
                    logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                                       specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                       sourceformat = 'EQ36', densityextrap = densityextrap, Specie_class = 'liquids',
                                       rhoEGextrap = rhoEGextrap).logK
                    logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                    for i in range(len(logK)):
                        i = i + 1
                        if (i == 1) | (i == 5):
                            fout.writelines( "      %9.4f" %  logK[i-1])
                        else:
                            fout.writelines( "  %9.4f" %  logK[i-1])
                        if (i % 4 == 0) | (i == len(logK)):
                            fout.writelines( "\n")
                    fout.writelines( "*    gflag = 1 [reported delG0f used]\n" )
                    fout.writelines( "*    extrapolation algorithm: supcrt92 [92joh/oel]\n" )
                    if j == 'Quicksilver':
                        fout.writelines( "*    alternate name = Quicksilver\n" )
                    if j != 'H2O':
                        dG, dH, S = dbaccessdic[k][2], dbaccessdic[k][3], dbaccessdic[k][4]
                    else:
                        dG, dH, S, ref = dGH2O[0], dHH2O[0], SH2O[0], 'iapws95/' + Dielec_method
                    fout.writelines( "*    ref-state data  [source:   %s  ]\n" % ref)
                    fout.writelines( "*         delG0f =   %8.3f  kcal/mol\n" % (dG/1000) )
                    fout.writelines( "*         delH0f =   %8.3f  kcal/mol\n" % (dH/1000))
                    fout.writelines( "*         S0PrTr =   %8.3f  cal/(mol*K)\n" % S)
                    fout.writelines( "*    Cp coefficients [source:   %s  ]\n" % ref)
                    fout.writelines( "*         T**0   =   %11.8e  \n" % (dbaccessdic[k][6]) )
                    fout.writelines( "*         T**1   =   %11.8e  \n" % (dbaccessdic[k][7]*10**-3))
                    if dbaccessdic[k][8] < 1:
                        fout.writelines( "*         T**-2  =  %12.8e  \n" % (dbaccessdic[k][8]*10**5))
                    else:
                        fout.writelines( "*         T**-2  =   %11.8e  \n" % (dbaccessdic[k][8]*10**5))
                    fout.writelines( "*         Tlimit =   %7.2fC  \n" % (dbaccessdic[k][9]))
                    fout.writelines( "+" + "-"*68 + "\n")
                else:
                    continue
        fout.writelines( "gases\n")
        fout.writelines( "+" + "-"*68 + "\n")

        #% Gases reactions
        for j in specielist[6]:
            k = j.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
            rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1, 2, 3]]
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ]
            if (j not in missing_species) and (len([k for k in rxnlst if k not in missing_species])==len(rxnlst)):
                if sourcedic[j][0] != '':
                    fout.writelines('%-25s %s \n' % (j, sourcedic[j][0]))
                else:
                    fout.writelines('%-25s %s \n' % (j, dbaccessdic[k][0]))

                if sourceformat.upper() != 'GWB':
                    fout.writelines(block_info[j])
                else:
                    fout.writelines('     sp.type =  gas \n' +\
                                    '*    EQ3/6   =  com, alt, sup \n' +\
                                    '     revised =   - \n' +\
                                    '*    mol.wt. =  %s g/mol\n' % MWdic[j] +\
                                    '     V0PrTr  =   %s cm**3/mol \n' % dbaccessdic[j][5] )


                fout.writelines('****\n')

                if sourceformat.upper() != 'GWB':
                    fout.writelines( "     %s element(s):\n" % int(len(Elemlist[j])/2))
                    Elem = Elemlist[j]
                else:                    
                    formula = j.rstrip('(g)') if sourcedic[j][0] == '' else sourcedic[j][0].rstrip('(g)')
                    Elem = [[v,k] for k,v in dict( sorted(calc_elem_count_molewt(formula)[0].items(), 
                                                         key=lambda x: x[0].lower()) ).items()]
                    Elem = [item for sublist in Elem for item in sublist]
                    fout.writelines( "     %s element(s):\n" % int(len(Elem)/2))

                for i in range(len(Elem)):
                    i = i + 1
                    if (i == 1) | (i == 7) | (i == 13):
                        fout.writelines( "    %9.4f " %  float(Elem[i - 1]))
                    elif i % 2 != 0:
                        fout.writelines( "%9.4f " %  float(Elem[i - 1]))
                    else:
                        fout.writelines( "%-9s     " %  (Elem[i - 1]))
                    if (i % 6 == 0) | (i == len(Elem)):
                        fout.writelines( "\n")
                fout.writelines('****\n')
                if sourceformat.upper() != 'GWB':
                    fout.writelines( "     %s species in reaction:\n" % sourcedic[j][1])
                    Rxn = sourcedic[j][2:]
                else:
                    fout.writelines( "     %s species in reaction:\n" % (sourcedic[j][1] + 1))
                    sourcedic[j] = [k if k != 'O2(aq)' else k.replace('O2(aq)', 'O2(g)') for k in sourcedic[j]]
                    Rxn = ['-1.0000', '%s' % j] + sourcedic[j][2:]

                for i in range(len(Rxn)):
                    i = i + 1
                    if (i == 1) | (i == 5) | (i == 9) | (i == 13):
                        fout.writelines( "  %9.4f " %  float(Rxn[i - 1]))
                    elif i % 2 != 0:
                        fout.writelines( "%9.4f " %  float(Rxn[i - 1]))
                    else:
                        fout.writelines( " %-21s     " %  (Rxn[i - 1]))
                    if (i % 4 == 0) | (i == len(Rxn)):
                        fout.writelines( "\n")
                fout.writelines('*\n')
                fout.writelines('**** logK grid [T, P @ Miscellaneous parameters]\n')
                logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                                   specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                   sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'gases',
                                   heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap).logK
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                for i in range(len(logK)):
                    i = i + 1
                    if (i == 1) | (i == 5):
                        fout.writelines( "      %9.4f" %  logK[i-1])
                    else:
                        fout.writelines( "  %9.4f" %  logK[i-1])
                    if (i % 4 == 0) | (i == len(logK)):
                        fout.writelines( "\n")
                fout.writelines( "*    gflag = 1 [reported delG0f used]\n" )
                fout.writelines( "*    extrapolation algorithm: supcrt92 [92joh/oel]\n" )
                if j != 'H2O':
                    dG, dH, S = dbaccessdic[k][2], dbaccessdic[k][3], dbaccessdic[k][4]
                else:
                    dG, dH, S, ref = dGH2O[0], dHH2O[0], SH2O[0], 'iapws95/' + Dielec_method
                fout.writelines( "*    ref-state data  [source:   %s  ]\n" % ref)
                fout.writelines( "*         delG0f =   %8.3f  kcal/mol\n" % (dG/1000) )
                fout.writelines( "*         delH0f =   %8.3f  kcal/mol\n" % (dH/1000))
                fout.writelines( "*         S0PrTr =   %8.3f  cal/(mol*K)\n" % S)
                fout.writelines( "*    Cp coefficients [source:   %s  ]\n" % ref)
                fout.writelines( "*         T**0   =   %11.8e  \n" % (dbaccessdic[k][6]) )
                fout.writelines( "*         T**1   =   %11.8e  \n" % (dbaccessdic[k][7]*10**-3))
                if dbaccessdic[j][8] < 1:
                    fout.writelines( "*         T**-2  =  %12.8e  \n" % (dbaccessdic[k][8]*10**5))
                else:
                    fout.writelines( "*         T**-2  =   %11.8e  \n" % (dbaccessdic[k][8]*10**5))
                fout.writelines( "*         Tlimit =   %7.2fC  \n" % (dbaccessdic[k][9]))
                fout.writelines( "+" + "-"*68 + "\n")
            else:
                continue
        fout.writelines( "solid solutions\n")
        fout.writelines( "+" + "-"*68 + "\n")

        #% Solid solution reactions
        if sourceformat.upper() != 'GWB':
            for j in specielist[7]:
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]]
                rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ]
                if (len([k for k in rxnlst if k not in missing_species]) == len(rxnlst)):
                    if sourcedic[j][0] != '':
                        fout.writelines('%-25s %s \n' % (j, sourcedic[j][0]))
                    else:
                        fout.writelines('%-25s %s \n' % (j, dbaccessdic[j][0]))
                    fout.writelines(block_info[j][0])
    
                    fout.writelines( "  %s components\n" % sourcedic[j][1])
                    Rxn = sourcedic[j][2:]
                    for i in range(len(Rxn)):
                        i = i + 1
                        if (i == 1) | (i == 5) | (i == 9) | (i == 13):
                            fout.writelines( "  %9.4f " %  float(Rxn[i - 1]))
                        elif i % 2 != 0:
                            fout.writelines( "%9.4f " %  float(Rxn[i - 1]))
                        else:
                            fout.writelines( " %-21s     " %  (Rxn[i - 1]))
                        if (i % 4 == 0) | (i == len(Rxn)):
                            fout.writelines( "\n")
                    fout.writelines(block_info[j][1])
                    fout.writelines( "+" + "-"*68 + "\n")
                else:
                    continue

        fout.writelines( "references\n")
        fout.writelines( "+" + "-"*68 + "\n")
        fout.writelines('** Please copy references to here from the corresponding\n')
        fout.writelines('** sequential-access version of the direct-access SUPCRT database.\n stop.\n\n')

        #% close all files
        fid.close()
        fout.close()
        if clay_thermo.lower() == 'yes':
            fclay.close()

        return print('Success, your new EQ3/6 database is ready for download')

    def write_PHREEQCdb(self, T, P):
        """
        This function writes the new PHREEQC database into a new folder called "output"   \n
        Parameters
        ----------
            T               :    temperature [°C]   \n
            P               :    pressure [bar]   \n

        Returns
        -------
            Outputs the new database to an ASCII file with filename described in 'objdb'.   \n

        Usage
        -------
         Example:
             (1) General format with default dielectric constant and CO2 activity model and exclusions
                 of solid solutions   \n
                 write_PHREEQCdb(T, P )   \n
             (2) Inclusion of solid solutions and clay thermo and exclusion of solid solution of clinopyroxene  \n
                 write_PHREEQCdb(T, P )   \n
             (3) Inclusion of all solid solutions and clay thermo with \emph{'Duan_Sun'} CO2 activity model and 'FGL97'
                 dielectric constant calculation \n
                 write_PHREEQCdb(T, P )   \n
        """

        nCa_cpx = self.cpx_Ca
        solid_solution = self.solid_solution
        clay_thermo = self.clay_thermo
        # sourcedb = self.sourcedb
        objdb = self.objdb                 # new database file path
        Dielec_method = self.Dielec_method
        heatcap_method = self.heatcap_method  
        sourceformat = self.sourceformat    # source database format 
        densityextrap = self.densityextrap

        dbaccessdic, sourcedic, specielist, Rd, d = self.dbr.dbaccessdic, self.dbr.sourcedic, self.dbr.specielist, self.dbr.Rd, self.dbr.d
        act_param = self.dbr.act_param
        dataset_format = act_param['dataset_format']
        # sourcedb_codecs = getattr(self, "sourcedb_codecs", None) or getattr(self.dbr, "sourcedb_codecs", {})
        logK_form = self.logK_form

        sourcedic_logK = {(normalize_phreeqc_species_charge(k) if k in specielist[1] + specielist[3] else k):
                          [normalize_phreeqc_species_charge(x) if isinstance(x, str) else x for x in v]
                          for k, v in sourcedic.items()
                            }
        specielist_logK = [[normalize_phreeqc_species_charge(x) for x in k] if idx in (1, 3) else k for idx, k in enumerate(specielist)]


        # make dir and file to write data to
        phreeqc_path = os.path.join(os.getcwd(), 'output', 'PHREEQC')
        os.makedirs(phreeqc_path, exist_ok=True)

        # extract periodic table symbols into a set safely 
        try:
            periodic_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PeriodicTableJSON.json")
        except NameError: 
            periodic_file = os.path.join(os.getcwd(), "PeriodicTableJSON.json")

        with open(periodic_file, encoding="utf8") as f:
            periodic_data = json.load(f)
            element_symbols = {element["symbol"] for element in periodic_data["elements"]}


        # missing species list
        missing_species = []    # list of all species in sourcedb that are not in dbaccessdic

        # missing species - start 
        for key, values in sourcedic.items():
            normalized_key = normalize_phreeqc_species_charge(key) if key in specielist[1] + specielist[3] else key
            normalized_key = normalized_key + "(s)" if not normalized_key.endswith('(aq)') and key in specielist[3] and key in specielist[4] else normalized_key
         
            key_found = True
            normalized_key = normalized_key.replace('CH4(aq)', 'Methane(aq)')

            if normalized_key not in dbaccessdic.keys() and normalized_key not in (['eh', 'e-', 'H2O']):
                key_found = False
            
            # go through keys reactants
            temp_missing = []
            for i in range(3, len(values), 2):
                curr = values[i]
                curr_norm = normalize_phreeqc_species_charge(curr).replace('CH4(aq)', 'Methane(aq)')
                
                # check for each reaction if all the species in that reaction exist in dbaccess
                if curr_norm not in dbaccessdic.keys() and curr_norm not in (['eh', 'e-', 'H2O']) and curr_norm not in element_symbols: 
                    temp_missing.append(curr)

            if temp_missing != [] or not key_found:
                missing_species.append([key] + temp_missing)
            
        missingfile = open(os.path.join(os.path.abspath("."), 'output', 'PHREEQC', 'spxNotFound.txt'), 'w+')

        for line in missing_species:
            if len(line) > 0:
                missingfile.writelines(line[0])
                missingfile.writelines('\n')
                for i in range(len(line)):
                    missingfile.writelines('   %s' % line[i])
                    missingfile.writelines('\n')
        missingfile.close()

        # write all info from source unless bases species was not found in direct-access db ?
        flattened_missing_spx = list(itertools.chain(*missing_species))

        missing_species = [item for sublist in missing_species for item in sublist]
        missing_species = [i for n, i in enumerate(missing_species) if i not in missing_species[:n]]


        # make new file
        if objdb == None:
            objdb = 'phreeqc_%sbars' % int(P[0])

        fout = open(os.path.join(os.path.abspath("."),'output', 'PHREEQC',  objdb + '.dat'), 'w+')

        # write header - TODO - add comments from sourcedb?
        fout.writelines(["# Dataset for thermodynamic data for PHREEQC programs \n", 
                        "# Dataset format: " + dataset_format + "\n",
                        "# Generated by: pyGeochemCalc" + time.ctime() + '\n', 
                        "# Output Package: PHREEQC \n", 
                        "\n"])

        # moved this block outside of debye huckel if statement because of errors when we needed rho later
        if Dielec_method.upper() == 'DEW':
            water = ZhangDuan(T = T, P = P)
            rho, dGH2O, dHH2O, SH2O = water.rho, water.G, np.nan*np.ones(len(T)), np.nan*np.ones(len(T))
        else:
            water = iapws95(T = T, P = P)
            rho, dGH2O, dHH2O, SH2O = water.rho, water.G, water.H, water.S

        
        waterdielc = water_dielec(T = T, P = P, Dielec_method = Dielec_method)
        E, Adh, Bdh, bdot = waterdielc.E, waterdielc.Ah, waterdielc.Bh, waterdielc.bdot

        rhoEG = {'rho': rho, 'E': E,  'dGH2O': dGH2O}
        rhoEDB = {'rho': rho, 'E': E,  'Ah': Adh, 'Bh': Bdh}

        rhoEGextrap = {}
        if any(rhoEG['rho'] < 350):
            subBornptrs = rhoEG['rho'] < 350
            for i, j in enumerate(zip(T[subBornptrs], P[subBornptrs])):
                rhoextrap = np.linspace(350, 550, 3)
                Pextrap = iapws95(T = j[0], rho = rhoextrap).P if Dielec_method.upper() != 'DEW' else ZhangDuan(T = j[0], rho = rhoextrap).P
                Textrap = j[0]*np.ones(np.size(Pextrap))

                dGH2O = iapws95(T = Textrap, P = Pextrap).G if Dielec_method.upper() != 'DEW' else ZhangDuan(T = Textrap, P = Pextrap).G
                E = water_dielec(T = Textrap, P = Pextrap, Dielec_method = Dielec_method).E
                rhoextrap = np.around(rhoextrap, 3)
                rhoEGextrap['%d_%d' % (j[0], j[1])]= {'rho': rhoextrap,'E': E, 'dGH2O': dGH2O,
                                                    'Textrap': Textrap, 'Pextrap': Pextrap}

        TK = convert_temperature( T, Out_Unit = 'K' )
        logKfunc = lambda TK, *x: x[0] + x[1]*TK + x[2]*TK**(-1) + x[3]*np.log10(TK) + x[4]*TK**(-2) #+ x[5]*TK**(2) 
        x0 = [2.06576e2, 3.73497e-2, -9.01862e3, -3.19605e1, 6.0111e5]

        if act_param['activity_model'].lower() == 'debye huckel':
            if any("-llnl_gamma" in k for k in Rd[d['SOLUTION_SPECIES']:d['PHASES']]):
                fout.writelines(["LLNL_AQUEOUS_MODEL_PARAMETERS \n", "-temperatures\n"])  
                # write temperatures
                for i in range(len(T)):
                    i = i + 1
                    if (i == 1) | (i == 5):
                        fout.writelines( "       %9.4f" %  T[i-1])
                    else:
                        fout.writelines( "   %9.4f" %  T[i-1])
                    if (i % 4 == 0) | (i == len(T)):
                        fout.writelines( "\n")
                
                # Calculation for debye huckel and bdot and water properties
                fout.writelines(["#debye huckel a (adh) \n", " -dh_a \n"])
                for i in range(len(Adh)):
                    i = i + 1
                    if (i == 1) | (i == 5):
                        fout.writelines( "       %9.4f" %  Adh[i-1])
                    else:
                        fout.writelines( "   %9.4f" %  Adh[i-1])
                    if (i % 4 == 0) | (i == len(Adh)):
                        fout.writelines( "\n")

                fout.writelines(["#debye huckel b (bdh) \n", " -dh_b \n"])
                for i in range(len(Bdh)):
                    i = i + 1
                    if (i == 1) | (i == 5):
                        fout.writelines( "       %9.4f" %  Bdh[i-1])
                    else:
                        fout.writelines( "   %9.4f" %  Bdh[i-1])
                    if (i % 4 == 0) | (i == len(Bdh)):
                        fout.writelines("\n")

                fout.writelines(["#bdot (bdot) \n", " -bdot \n"])
                for i in range(len(bdot)):
                    i = i + 1
                    if (i == 1) | (i == 5):
                        fout.writelines( "       %9.4f" %  bdot[i-1])
                    else:
                        fout.writelines( "   %9.4f" %  bdot[i-1])
                    if (i % 4 == 0) | (i == len(bdot)):
                        fout.writelines( "\n")

                fout.writelines(["#cco2 (coefficients for the Drummond (1981) polynomial)  \n", " -co2_coefs \n"])
                # Define Drummond equation coefficients
                C = -1.0312
                F = 0.0012806
                G = 255.9
                E = 0.4445
                H = -0.001606
                # First row: C and F
                fout.writelines(f"       {C:9.4f}   {F:12.7f}\n")
                # Second row: G and E
                fout.writelines(f"       {G:9.4f}   {E:12.4f}\n")
                # Third row: H alone
                fout.writelines(f"       {H:9.5f}\n")

                fout.writelines([" \n NAMED_EXPRESSIONS\n\n #\n # formation of O2 from H2O\n # 2H2O =  O2 + 4H+ + 4e-\n #\n      Log_K_O2\n "])
                # print(sourcedic_logK['O2(aq)'])
                logK = calcRxnlogK( T = T, P = P, Specie = 'O2(aq)', dbaccessdic = dbaccessdic, sourcedic = sourcedic_logK,
                            specielist = specielist_logK, Dielec_method = Dielec_method, rhoEG = rhoEG,
                            sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'aqueous',
                            rhoEGextrap = rhoEGextrap, ThermoInUnit = self.ThermoInUnit)
                

                logK = - logK.logK
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                logKcorr = curve_fit(logKfunc, TK[logK != 500].ravel(), logK[logK != 500].ravel(), p0 = x0,  maxfev = 1000000)[0]
                
                info = "  " + " ".join("%9.5f" % e for e in logKcorr)
                logK25 = logKfunc(convert_temperature( 25, Out_Unit = 'K' ), *logKcorr)

                fout.writelines(f"     -log_k  {logK25:.3f}\n")
                fout.writelines(f"     -analytic  {info}\n")

            else:
                fout.writelines(["\n"])

        else:
            fout.writelines(["\n"])

        fout.writelines(["\n",
                           "SOLUTION_MASTER_SPECIES",
                             "\n\n",
                                 "#"
                                + "element".ljust(14)
                                + "species".ljust(14)
                                + "alk".ljust(14)
                                + "gfw_formula".ljust(14)
                                + "element_gfw".ljust(14)
                                + "\n"
                            ])


        solid_solution = 'no' if solid_solution is None else solid_solution
        clay_thermo = 'no' if clay_thermo is None else clay_thermo
        master_sp = []
        # Elements
        # print(flattened_missing_spx)
        for i in range(d['SOLUTION_MASTER_SPECIES'], d['SOLUTION_SPECIES']):
            s = Rd[i]
            if (not s.startswith('#')) and (len(s.split()) > 2 and s.split()[1] not in flattened_missing_spx):
                fout.writelines(s)
                master_sp.append(s.split()[1])

        if solid_solution.lower() == 'yes' or clay_thermo.lower() == 'yes':
            if 'Al+3' not in master_sp:
                fout.writelines('Al            Al+3           0            Al            26.982\n')
            if 'Fe+3' not in master_sp:
                fout.writelines('Fe(2)         Fe+2           0            Fe            55.847\n')
                fout.writelines('Fe(3)         Fe+3          -2            Fe            55.847\n')
            if 'O2' not in master_sp:
                fout.writelines('O(0)          O2             0            O             15.999\n')
            if 'H4SiO4' not in master_sp:
                fout.writelines('Si            H4SiO4         0            Si            28.086\n')
                # print(master_sp)
        
        # SOLUTION_SPECIES
        fout.writelines(["\nSOLUTION_SPECIES\n\n"])
        last_num = 0

        if solid_solution.lower() == 'yes' or clay_thermo.lower() == 'yes':
            if 'Al+3' not in master_sp:
                fout.writelines(['Al+3     = Al+3\n', '     -log_k     0.000     \n\n'])
            if 'Fe+3' not in master_sp:
                fout.writelines(['Fe+3     = Fe+3\n', '     -log_k     0.000     \n\n'])
                sourcedic['Fe+3'] = ['', 4, '0.250', 'O2', '1.000', 'Fe+2', '1.000', 'H+', '-0.500', 'H2O']
                sourcedic['O2'] = ['', 3, '2.000', 'H2O', '-4.000', 'e-', '-4.000', 'H+']
                specielist[3] += ['Fe+3', 'O2']

                sourcedic_logK['Fe+++'] = ['', 4, '0.250', 'O2(aq)', '1.000', 'Fe++', '1.000', 'H+', '-0.500', 'H2O']
                sourcedic_logK['O2(aq)'] = ['', 3, '2.000', 'H2O', '-4.000', 'e-', '-4.000', 'H+']
                specielist_logK[3] += ['Fe+++', 'O2(aq)']
                
            if 'H4SiO4' not in master_sp:
                fout.writelines(['H4SiO4     = H4SiO4\n', '     -log_k     0.000     \n\n'])

            sourcedic['Al(OH)4-'] = ['', 3, '4.000', 'H2O', '1.000', 'Al+3', '-4.000', 'H+']
            sourcedic['SiO2'] = ['', 3, '1.000', 'H4SiO4', '-2.000', 'H2O']
            specielist[3] += ['Al(OH)4-', 'SiO2']

            sourcedic_logK['Al(OH)4-'] = ['', 3, '4.000', 'H2O', '1.000', 'Al+++', '-4.000', 'H+']
            sourcedic_logK['SiO2(aq)'] = ['', 3, '1.000', 'H4SiO4(aq)', '-2.000', 'H2O']
            specielist_logK[3] += ['Al(OH)4-', 'SiO2(aq)']


        for j in specielist[1] + specielist[3]: # 
            rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1, 2]]
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 == 0 ]

            if (j not in flattened_missing_spx) and all(sp not in flattened_missing_spx for sp in rxnlst):
                lhs_terms = []
                rhs_terms = [j]

                for n in range(2, len(sourcedic[j]), 2):
                    coeff = sourcedic[j][n]
                    specie = sourcedic[j][n+1]

                    # Absolute value of coefficient for display
                    abs_coeff = abs(float(coeff))

                    # Try to detect if it's a rational with small denominator
                    frac = Fraction(abs_coeff).limit_denominator(1000)

                    if abs(abs_coeff - float(frac)) < 1e-12:  # effectively rational
                        coeff_str = f"{abs_coeff:.15f}".rstrip("0").rstrip(".")
                    else:
                        coeff_str = f"{abs_coeff:.4f}".rstrip("0").rstrip(".")

                    # Format term (skip coefficient if it's 1)
                    if coeff_str == "1":
                        term = f"{specie}"
                    else:
                        term = f"{coeff_str}{specie}"

                    # Sort into LHS (positive coeffs) or RHS (negative coeffs)
                    if float(coeff) >= 0:
                        lhs_terms.append(term)
                    else:
                        rhs_terms.append(term)

                # Join LHS and RHS with " + "
                to_write = " + ".join(lhs_terms) + " = " + " + ".join(rhs_terms)

                fout.writelines(to_write + "\n")

                lhs_species, rhs_species = [x.strip() for x in to_write.split('=')]
                pattern = re.compile(rf'^\s*{build_side_regex(lhs_species)}\s*=\s*{build_side_regex(rhs_species)}\s*$')
                # pattern = re.compile(rf'{build_side_regex(lhs_species)}\s*=\s*{build_side_regex(rhs_species)}')
                
                species_line = re.compile(r'^\s*[\w\+\-\(\)]+.*=\s*[\w\+\-\(\)]+.*$')
                block = []
                capture = False

                for line in Rd[d['SOLUTION_SPECIES']:d['PHASES']]:
                    stripped = line
                    if stripped.startswith('#'):
                        continue  # skip comments

                    # Start capturing when we find the species of interest
                    if pattern.match(stripped):
                        capture = True
                        block.append(line)
                        continue

                    # Stop if a new species starts
                    if capture and species_line.match(stripped):
                        break

                    if capture:
                        block.append(line)
                    

                fout.writelines([k for k in block if ("llnl_gamma" in k or "gamma" in k) and not k.lstrip().startswith('#')])

                # if this is 1 : 1 - no need to calculate logk
                if len(sourcedic[j]) > 4:

                    curr_species_w_normalized_charge = normalize_phreeqc_species_charge(j)

                    logK = calcRxnlogK( T = T, P = P, Specie = curr_species_w_normalized_charge, dbaccessdic = dbaccessdic, sourcedic = sourcedic_logK,
                                specielist = specielist_logK, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'aqueous',
                                rhoEGextrap = rhoEGextrap, ThermoInUnit = self.ThermoInUnit)
                    
                    if densityextrap.lower() == 'yes': 
                        if all(logK.nonsubBornptrs) == True: # if all densities are >= 350
                            logKnan_alert = False            # turn off the prompts for using Density extrapolation
                        else:
                            logKnan_alert = True
                    else:
                        logKnan_alert = False                # turn off the prompts for using Density extrapolation
                    logK = - logK.logK
                    logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                    logKcorr = curve_fit(logKfunc, TK[logK != 500].ravel(), logK[logK != 500].ravel(), p0 = x0,  maxfev = 1000000)[0]
                    
                    info = "  " + " ".join("%9.5f" % e for e in logKcorr)
                    logK25 = logKfunc(convert_temperature( 25, Out_Unit = 'K' ), *logKcorr)

                    fout.writelines(f"     -log_k  {logK25:.3f}\n")
                    fout.writelines(f"     -analytic  {info}\n")
                else:
                    fout.writelines(f"     -log_k  {0.000}\n")

                # fout.writelines([k for _, k in block if ("llnl_gamma" in k or "gamma" in k) and not k.lstrip().startswith('#')])

                fout.writelines([k for k in block if "dw" in k and not k.lstrip().startswith('#')])
                fout.writelines([k for k in block if "millero" in k and not k.lstrip().startswith('#')])
                fout.writelines([k for k in block if "Vm" in k and not k.lstrip().startswith('#')])
                fout.writelines(f"\n")
            
        if logKnan_alert == True:
            warnings.warn('Some temperature and pressure points are out of aqueous species HKF eqns regions of applicability, hence, density extrapolation has been applied')

        # PHASES
        if d['PHASES'] != -1:
            fout.writelines(["PHASES\n\n"])

        if nCa_cpx is None:
            nCa = 0
        else:
            nCa = nCa_cpx
        if solid_solution.lower() == 'yes':
            solidsolution_no = 11
            fnlist = ['plagio', 'olivine', 'pyroxene', 'cpx'] if nCa_cpx > 0 else ['plagio', 'olivine', 'pyroxene']
            for fn in fnlist:
                for nX in np.round(np.linspace(1, 0, solidsolution_no), 1):
                    if fn != 'cpx':
                        ss = calcRxnlogK(X = nX, T = T, P = P, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                         dbaccessdic = dbaccessdic, Specie = fn, densityextrap = densityextrap,
                                         ThermoInUnit = self.ThermoInUnit, rhoEGextrap = rhoEGextrap, Al_Si = 'Arnórsson_Stefánsson')
                    else:
                        ss = calcRxnlogK(cpx_Ca = nCa, X = nX, T = T, P = P, Dielec_method = Dielec_method,
                                         rhoEG = rhoEG, dbaccessdic = dbaccessdic, Specie = fn,
                                         densityextrap = densityextrap, ThermoInUnit = self.ThermoInUnit,
                                         rhoEGextrap = rhoEGextrap, Al_Si = 'Arnórsson_Stefánsson')
                    logK, Rxn = ss.logK, ss.Rxn

                    logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                    outputfmt(fout, logK, Rxn, TK, dataset = 'PHREEQC', logK_form = logK_form)

        # clay minerals
        if clay_thermo.lower() == 'yes':
            # fclay = open(os.path.join(folder, 'clay_elements.dat'), 'r')
            fclay = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clay_elements.dat'), 'r')
            Rd_clay = fclay.readlines()
            Rd_clay = [j.replace('-','_').strip('\n') for j in Rd_clay]
            
            for i in range(len(Rd_clay)):
                ss = calcRxnlogK(T = T, P = P, Specie = 'Clay', elem = Rd_clay[i].split(','),
                                 dbaccessdic = dbaccessdic, ThermoInUnit = self.ThermoInUnit, rhoEG = rhoEG,
                                 rhoEGextrap = rhoEGextrap, densityextrap = densityextrap)
                logK, Rxn = ss.logK, ss.Rxn
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                outputfmt(fout, logK, Rxn, TK, dataset = 'PHREEQC', logK_form = logK_form)

        for j in specielist[4] + specielist[5]: # 
            rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1, 2]]
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 == 0 ]

            if (j not in flattened_missing_spx) and all(sp not in flattened_missing_spx for sp in rxnlst):
                lhs_terms = []
                rhs_terms = [sourcedic[j][0]]

                for n in range(2, len(sourcedic[j]), 2):
                    coeff = sourcedic[j][n]
                    specie = sourcedic[j][n+1]

                    # Absolute value of coefficient for display
                    abs_coeff = abs(float(coeff))

                    # Format term (skip coefficient if it's 1)
                    if abs_coeff == 1.0:
                        term = f"{specie}"
                    else:
                        term = f"{abs_coeff:.3f}{specie}"

                    # Sort into LHS (positive coeffs) or RHS (negative coeffs)
                    if float(coeff) >= 0:
                        lhs_terms.append(term)
                    else:
                        rhs_terms.append(term)

                # Join LHS and RHS with " + "
                to_write = " + ".join(rhs_terms)  + " = " + " + ".join(lhs_terms)

                fout.writelines(j + "\n" + "     " + to_write + "\n")


                logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic_logK,
                            specielist = specielist_logK, Dielec_method = Dielec_method, rhoEG = rhoEG,
                            sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'minerals',
                            heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap)
                
                logK = logK.logK
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                logKcorr = curve_fit(logKfunc, TK[logK != 500].ravel(), logK[logK != 500].ravel(), p0 = x0,  maxfev = 1000000)[0]
                
                info = "  " + " ".join("%9.5f" % e for e in logKcorr)
                logK25 = logKfunc(convert_temperature( 25, Out_Unit = 'K' ), *logKcorr)

                fout.writelines(f"     -log_k  {logK25:.3f}\n")
                fout.writelines(f"     -analytic  {info}\n")

                block = []
                capture = False
                
                for line in Rd[d['PHASES']:]:
                    stripped = line.strip()
                    if stripped.startswith('#'):
                        continue  # skip comments
                    if stripped == j:
                        capture = True
                    elif capture and stripped and not stripped.startswith('-') and ' ' not in stripped:
                        # Stop if a new species name appears
                        break
                    if capture:
                        block.append(line)

                fout.writelines([k for k in block if "Vm" in k and not k.lstrip().startswith('#')])
                fout.writelines([k for k in block if "T_c" in k and not k.lstrip().startswith('#')])
                fout.writelines([k for k in block if "P_c" in k and "T_c" not in k and not k.lstrip().startswith('#')])
                fout.writelines([k for k in block if "Omega" in k and "T_c" not in k and not k.lstrip().startswith('#')])
                fout.writelines(f"\n")


        # PITZER
        if act_param['activity_model'].lower() == 'h-m-w':
            # fout.writelines(["PITZER\n\n"])
            for i in range(d['PITZER'], d['length']):
                s = Rd[i]
                if s.startswith(('EXCHANGE_MASTER_SPECIES', 'SURFACE_MASTER_SPECIES', 'RATES')) or i == d['length']:
                    break
                else:
                    if s.startswith(('-B0', '-B1', '-B2', '-C0', '-THETA', '-LAMDA', '-ZETA', '-PSI')):
                        fout.writelines(s)
                    else:
                        s_out = [p for p in s.split() if not re.match(r'^[0-9.eE+-]+$', p)]
                        
                        if all(item not in flattened_missing_spx for item in s_out):
                            fout.writelines(s)

        # EXCHANGE_SPECIES
        if d['EXCHANGE_MASTER_SPECIES'] != -1:
            # fout.writelines(["EXCHANGE_MASTER_SPECIES\n\n"])
            # Collect filtered block
            filtered_block = []
            skip_block = False
            for i in range(d['EXCHANGE_MASTER_SPECIES'], d['length']):
                line = Rd[i]
                if line.startswith(('SURFACE_MASTER_SPECIES', 'RATES')) or i == d['length']:
                    break
                if line.strip().startswith("#"):  # reset skip check per block header
                    skip_block = False
                if contains_missing_species(line, flattened_missing_spx):
                    skip_block = True
                if not skip_block:
                    filtered_block.append(line)   
            fout.writelines(filtered_block)

            # for i in range(d['EXCHANGE_MASTER_SPECIES'], d['length']):
            #     s = Rd[i]
            #     if s.startswith(('SURFACE_MASTER_SPECIES', 'RATES')) or i == d['length']:
            #         break
            #     else:
            #         fout.writelines(s)

        # SURFACE_SPECIES
        if d['SURFACE_MASTER_SPECIES'] != -1:
            filtered_block = []
            skip_block = False
            for i in range(d['SURFACE_MASTER_SPECIES'], d['length']):
                line = Rd[i]
                if line.startswith('RATES') or i == d['length']:
                    break
                if line.strip().startswith("#"):  # reset skip check per block header
                    skip_block = False
                if contains_missing_species(line, flattened_missing_spx):
                    skip_block = True
                if not skip_block:
                    filtered_block.append(line)   
            fout.writelines(filtered_block)
            # for i in range(d['SURFACE_MASTER_SPECIES'], d['length']):
            #     s = Rd[i]
            #     if s.startswith('RATES') or i == d['length']:
            #         break
            #     else:
            #         fout.writelines(s)

        # RATES
        if d['RATES'] != -1:
            fout.writelines(["RATES\n\n"])
        for j in specielist[6]: # 
            if (j in specielist[4] + specielist[5]):
                block = []
                capture = False

                for k in Rd[d['RATES']:]:
                    line = k.strip()
                    if line.startswith('#'):
                        continue  # skip comments
                    if line.startswith(j):
                        capture = True
                    if capture:
                        block.append(k)
                    if capture and line == "-end":
                        break
                # block now contains all lines from "-start" to "-end" inclusive
                fout.writelines(block)
                fout.writelines("\n")               

        fout.close()
        if clay_thermo.lower() == 'yes':
            fclay.close()

        return print('Success, your new PHREEQC database is ready for download')

    def write_pflotrandb(self, T, P ):
        """
        This function writes the new pflotran database into a new folder called "output"   \n
        Parameters
        ----------
            T               :    temperature [°C]   \n
            P               :    pressure [bar]   \n

        Returns
        -------
            Outputs the new database to an ASCII file with filename described in 'objdb'.   \n

        Usage
        -------
          Example:
              (1) General format with default dielectric constant and CO2 activity model and exclusions
                  of solid solutions   \n
                  write_pflotrandb(T, P )   \n
              (2) Inclusion of solid solutions and clay thermo and exclusion of solid solution of clinopyroxene  \n
                  write_pflotrandb(T, P )   \n
              (3) Inclusion of all solid solutions and clay thermo with \emph{'Duan_Sun'} CO2 activity model and 'FGL97'
                  dielectric constant calculation \n
                  write_pflotrandb(T, P )   \n
        """
        nCa_cpx = self.cpx_Ca;                     sourcedb = self.sourcedb;
        solid_solution = self.solid_solution;      clay_thermo = self.clay_thermo
        objdb = self.objdb;                        Dielec_method = self.Dielec_method
        sourceformat = self.sourceformat;          heatcap_method = self.heatcap_method;
        densityextrap = self.densityextrap

        dbaccessdic, sourcedic, specielist = self.dbr.dbaccessdic, self.dbr.sourcedic, self.dbr.specielist
        MWdic, chargedic = self.dbr.MWdic, self.dbr.chargedic

        if sourceformat.upper() == 'EQ36':
            block_info = self.dbr.block_info

        if sourceformat.upper() == 'EQ36':
            dataset = 'tdat'
            dataset_format =  'apr20'
        else:
            dataset = sourcedb.split('.')[-1]
            dataset_format =  self.dbr.act_param['dataset_format']

        if os.path.exists(os.path.join(os.getcwd(), 'output/Pflotran')) == False:
                os.makedirs(os.path.join(os.getcwd(), 'output/Pflotran'))

        periodic_table = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           'PeriodicTableJSON.json'), encoding='utf8')
        data = json.load(periodic_table)
        Element = {data['elements'][x]['symbol'] : pd.DataFrame([data['elements'][x]['name'],
                                                                 data['elements'][x]['atomic_mass']],
                                                                index = ['name', 'mass']).T
                   for x in range(len(data['elements']))}
        periodic_table.close()

        missing_species = []
        elemspeclist = [ symbol for x in specielist[0] for symbol, item in Element.items()
                        if item.name[0][:5] == x[:5] ] if sourceformat.upper() == 'GWB' else specielist[0]

        form_del = [1] if sourceformat.upper() == 'GWB' else [1, 3, 4]
        all_species_source = [[i]+k for i, k in sourcedic.items() if i not in (['eh', 'e-', 'H2O']) ]
        all_species_source = [[k for j, k in enumerate(all_species_source[i])
                               if (j not in form_del and k not in elemspeclist and str(k).strip('0123456789.- ') != '') ]
                              if  (i <= len(specielist[0]))
                              else [k for j, k in enumerate(all_species_source[i])
                                    if (j not in form_del and str(k).strip('0123456789.- ') != '') ]
                              for i in range(len(all_species_source)) ]
        for num in range(len(all_species_source)): #
            if num < len(all_species_source):
                lst = [v for v in all_species_source[num] if v not in (['eh', 'e-', 'H2O']) ]

                bool_miss = [x.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
                             not in dbaccessdic.keys() for x in lst  ]
                if any(bool_miss):
                    sublist = [i for (i, v) in zip(lst, bool_miss) if v ]
                    if lst[0] not in sublist:
                        missing_species.append([lst[0]] + sublist)
                    else:
                        missing_species.append(sublist)

        missingfile = open(os.path.join(os.path.abspath("."),'output', 'Pflotran', 'spxNotFound.txt'), 'w')
        for line in missing_species:
            if len(line) > 0:
                missingfile.writelines(line[0])
                missingfile.writelines('\n')
                for i in range(len(line)):
                    missingfile.writelines('   %s' % line[i])
                    missingfile.writelines('\n')
        missingfile.close()
        missing_species = [item for sublist in missing_species for item in sublist]
        missing_species = [i for n, i in enumerate(missing_species) if i not in missing_species[:n]]
        logKnan_alert = False
        if objdb == None:
            objdb = 'thermo_%sbars' % int(P[0])
        # timestr = '.' + time.strftime("%d%b%y_%H%M")

        fout = open(os.path.join(os.path.abspath("."),'output', 'Pflotran', objdb + '.dat'), 'w+') # + timestr

        if np.ndim(T) == 0 | np.ndim(P) == 0:
            T = np.ravel(T)
            P = np.ravel(P)

        if Dielec_method.upper() == 'DEW':
            water = ZhangDuan(T = T, P = P)
        else:
            water = iapws95(T = T, P = P)
        rho, dGH2O = water.rho, water.G

        #% Calculation for debye huckel and bdot and water properties
        E = water_dielec(T = T, P = P, Dielec_method = Dielec_method).E

        rhoEG = {'rho': rho, 'E': E,  'dGH2O': dGH2O}

        # Calculate the rho E G for density extrapolation method here so we have it below
        rhoEGextrap = {}
        if any(rhoEG['rho'] < 350):
            subBornptrs = rhoEG['rho'] < 350
            for i, j in enumerate(zip(T[subBornptrs], P[subBornptrs])):
                rhoextrap = np.linspace(350, 550, 3)
                Pextrap = iapws95(T = j[0], rho = rhoextrap).P if Dielec_method.upper() != 'DEW' else ZhangDuan(T = j[0], rho = rhoextrap).P
                Textrap = j[0]*np.ones(np.size(Pextrap))

                dGH2O = iapws95(T = Textrap, P = Pextrap).G if Dielec_method.upper() != 'DEW' else ZhangDuan(T = Textrap, P = Pextrap).G
                E = water_dielec(T = Textrap, P = Pextrap, Dielec_method = Dielec_method).E
                rhoextrap = np.around(rhoextrap, 3)
                rhoEGextrap['%d_%d' % (j[0], j[1])]= {'rho': rhoextrap,'E': E, 'dGH2O': dGH2O,
                                                       'Textrap': Textrap, 'Pextrap': Pextrap}


        fout.writelines("'temperatures(degC) points' %s" % len(T))
        for i in range(len(T)):
            fout.writelines( " %6.1f" %  T[i])
        fout.writelines( "\n")
        fout.write('!:database is isobaric, at %d bars\n' % P[0])
        fout.write('!:basis_species  a0  valence  formula weight [g]\n')

        if sourceformat.upper() == 'EQ36':
            f_ionsize = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ion_size.txt'), 'r')
            Rd = f_ionsize.readlines()
            Rd = Rd[1:]
            ion_sizedic = {Rd[x].split()[0] : Rd[x].split()[1] for x in range(len(Rd))}
            f_ionsize.close()

        #% Basis reactions
        for j in specielist[1]:
            if j not in missing_species:
                if sourceformat.upper() == 'GWB':
                    charge = chargedic[j].lstrip().split()[1]
                    ionsize = chargedic[j].lstrip().split()[4]
                    MW = MWdic[j]
                elif sourceformat.upper() == 'EQ36':
                    charge = chargedic[j].split()[-1]
                    if j == 'O2(g)':
                        ionsize = [float(re.sub('[^0123456789\.]', '', x)) for x in block_info['O2(g)_b'] if x.strip('*    ').startswith('DHazero')]
                    else:
                        ionsize = [float(re.sub('[^0123456789\.]', '', x)) for x in block_info[j] if x.strip('*    ').startswith('DHazero')]
                    if any(ionsize) and any([MWdic[j]]):
                        ionsize, MW = ionsize[0], MWdic[j]
                    else:
                        formula = j if sourcedic[j][0] == '' else sourcedic[j][0]
                        formula = formula.rstrip('(aq)(g)')
                        ionsize = 3 if j.endswith('(aq)') else float(ion_sizedic[j]) if j in ion_sizedic.keys() else 500 #
                        MW =  calc_elem_count_molewt(formula, Elementdic = Element)[-1]
                info = "'%s'" % j + ' ' + str(ionsize) + ' ' + charge +' ' + str(MW)
                fout.writelines('%s\n' % info)
            else:
                continue
        fout.write("'null' 0 0 0\n")

        fout.write("!:species_name  num (n_i A_i, i=1,num)  log K (1:8)  a0  valence  formula weight [g]\n")
        #% Redox and Aqueous reactions
        for j in specielist[2] + specielist[3]:
            if sourceformat.upper() == 'GWB':
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]]
                charge = chargedic[j].lstrip().split()[1]
                ionsize = chargedic[j].lstrip().split()[4]
                MW, source_rxns = MWdic[j], sourcedic[j][2:]
            elif sourceformat.upper() == 'EQ36':
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1, 2, 3]]
                charge = chargedic[j].split()[-1]
                source_rxns = sourcedic[j][4:]
                ionsize = [float(re.sub('[^0123456789\.]', '', x)) for x in block_info[j] if x.strip('*    ').startswith('DHazero')]
                if any(ionsize) and any([MWdic[j]]):
                    ionsize, MW = ionsize[0], MWdic[j]
                else:
                    formula = j if sourcedic[j][0] == '' else sourcedic[j][0]
                    formula = formula.rstrip('(aq)')
                    ionsize = 3 if j.endswith('(aq)') else float(ion_sizedic[j]) if j in ion_sizedic.keys() else 500
                    MW =  calc_elem_count_molewt(formula, Elementdic = Element)[-1]

            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ]
            if (j not in missing_species) and (len([i for i in rxnlst if i not in missing_species])==len(rxnlst)):
                name, species = j, sourcedic[j][1]
                Rxn = [row if i%2==0 else "'%s'" %row for i,row in enumerate(source_rxns)]
                Rxn = ' '.join(Rxn)
                logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                                   specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                   sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'aqueous',
                                   rhoEGextrap = rhoEGextrap, ThermoInUnit = self.ThermoInUnit)
                if densityextrap.lower() == 'yes': 
                    if all(logK.nonsubBornptrs) == True: # if all densities are >= 350
                        logKnan_alert = False            # turn off the prompts for using Density extrapolation
                    else:
                        logKnan_alert = True
                else:
                    logKnan_alert = False                # turn off the prompts for using Density extrapolation
                logK = logK.logK
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                list_logk = ' '.join(str("%9.4f" % e) for e in list(logK))
                info = "'%s'" % name + ' ' + str(species) + ' ' + Rxn + ' ' + list_logk + ' ' + str(ionsize) +\
                    ' ' + charge +' ' + str(MW)
                fout.writelines('%s\n' % info)

            else:
                continue
        fout.writelines("'null' 1 0. '0' 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.\n")
        if logKnan_alert == True:
            warnings.warn('Some temperature and pressure points are out of aqueous species HKF eqns regions of applicability, hence, density extrapolation has been applied')

        fout.write("!:gas_name molar_vol  num (n_i A_i, i=1,num) log K (1:8)  formula weight [g]\n")
        #% Gas reactions
        if dataset_format != 'mar21':
            speclst = specielist[6]
        else:
            speclst = specielist[7]
        #print(speclst)
        for j in speclst:
            if sourceformat.upper() == 'GWB':
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]]
                source_rxns = sourcedic[j][2:]
            elif sourceformat.upper() == 'EQ36':
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1, 2, 3]]
                source_rxns = sourcedic[j][4:]
            #print(j)
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ] # remove all coefficients
            if (j not in missing_species) and (len([k for k in rxnlst if k not in missing_species]) == len(rxnlst)):
                name, species = j, sourcedic[j][1]
                if MWdic[j] != [] or MWdic[j] != '':
                    MW = MWdic[j]
                else:
                    formula = j.rstrip('(g)')
                    MW =  calc_elem_count_molewt(formula, Elementdic = Element)[-1]
                Rxn = [row if i%2 == 0 else "'%s'" %row for i,row in enumerate(source_rxns)]
                Rxn = ' '.join(Rxn)
                logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                                   specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                   sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'gases',
                                   heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap).logK
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                list_logk = ' '.join(str("%9.4f" % e) for e in list(logK))
                info = "'%s'" % name + ' ' + '0.000' + ' ' + str(species) + ' ' + Rxn +\
                    ' ' + list_logk + ' ' + str(MW)
                fout.writelines('%s\n' % info)
            else:
                continue

        fout.write("'null' 0. 1 1. '0' 0. 0. 0. 0. 0. 0. 0. 0. 0.\n")

        fout.write("!:mineral_name molar_vol  num (n_i A_i, i=1,num) log K (1:8)  formula weight [g]\n")
        #% Mineral reactions
        solid_solution = 'no' if solid_solution is None else solid_solution
        clay_thermo = 'no' if clay_thermo is None else clay_thermo
        if nCa_cpx is None:
            nCa = 0
        else:
            nCa = nCa_cpx
        if solid_solution.lower() == 'yes':
            solidsolution_no = 11
            fnlist = ['plagio', 'olivine', 'pyroxene', 'cpx'] if nCa > 0 else ['plagio', 'olivine', 'pyroxene']
            for fn in fnlist:
                for nX in np.round(np.linspace(1, 0, solidsolution_no), 1):
                    if fn != 'cpx':
                        ss = calcRxnlogK(X = nX, T = T, P = P, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                         dbaccessdic = dbaccessdic, Specie = fn, densityextrap = densityextrap,
                                         ThermoInUnit = self.ThermoInUnit, rhoEGextrap = rhoEGextrap)
                    else:
                        ss = calcRxnlogK(cpx_Ca = nCa, X = nX, T = T, P = P, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                         dbaccessdic = dbaccessdic, Specie = fn, densityextrap = densityextrap,
                                         ThermoInUnit = self.ThermoInUnit, rhoEGextrap = rhoEGextrap)
                    logK, Rxn = ss.logK, ss.Rxn

                    logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                    outputfmt(fout, logK, Rxn, dataset = 'Pflotran')

        # clay minerals
        if clay_thermo.lower() == 'yes':
            fclay = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clay_elements.dat'), 'r')
            Rd = fclay.readlines()
            Rd = [j.replace('-','_').strip('\n') for j in Rd]
            for i in range(len(Rd)):
                ss = calcRxnlogK(T = T, P = P, Specie = 'Clay', elem = Rd[i].split(','),
                                 dbaccessdic = dbaccessdic, ThermoInUnit = self.ThermoInUnit, rhoEG = rhoEG,
                                 rhoEGextrap = rhoEGextrap, densityextrap = densityextrap)
                logK, Rxn = ss.logK, ss.Rxn

                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                outputfmt(fout, logK, Rxn, dataset = 'Pflotran')

        if sourceformat.upper() == 'GWB':
            speclst = specielist[5]
        elif sourceformat.upper() == 'EQ36':
            speclst = specielist[4]+specielist[5]
        for j in speclst:
            if sourceformat.upper() == 'GWB':
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]]
                source_rxns = sourcedic[j][2:]
            elif sourceformat.upper() == 'EQ36':
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1, 2, 3]]
                source_rxns = sourcedic[j][4:]
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ] # remove all coefficients
            if (j not in missing_species) and (len([k for k in rxnlst if k not in missing_species])==len(rxnlst)):
                if solid_solution.lower() == 'yes' and j in ['Anorthite', 'Albite', 'Forsterite',
                                                    'Fayalite', 'Enstatite', 'Ferrosilite']:
                    continue
                elif solid_solution.lower() == 'yes' and (nCa == 1) and j in ['Diopside', 'Hedenbergite']:
                    continue
                elif clay_thermo.lower() == 'yes' and j in [ Rd[h].split(',')[0] for h in range(len(Rd))]:
                    continue
                else:
                    k = j.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
                    MW, MV, species = MWdic[j], dbaccessdic[k][5], sourcedic[j][1]
                    Rxn = [row if i%2 == 0 else "'%s'" %row for i, row in enumerate(source_rxns)]
                    Rxn = ' '.join(Rxn)

                    logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                                       specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                       sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'minerals',
                                       heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap).logK
                    logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                    list_logk = ' '.join(str("%9.4f" % e) for e in list(logK))
                    info = "'%s'" % j + ' ' + "%7.3f" % (MV) + ' ' + str(species) + ' ' + \
                        Rxn + ' ' + list_logk + ' ' + "%8.4f" % (MW)
                    fout.writelines('%s\n' % info)

            else:
                continue

        fout.write("'null' 1 0. '0' 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.\n")

        fout.write("!:oxide_name molar_vol  num (n_i A_i, i=1,num) log K (1:8)  formula weight [g]\n")
        #% Oxides reactions
        if sourceformat.upper() == 'GWB':
            if dataset_format != 'mar21':
                speclst = specielist[7]
            else:
                speclst = specielist[8]
            for j in speclst:
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]] # remove formula and specie number
                rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ] # remove all coefficients
                if (len([k for k in rxnlst if k not in missing_species])==len(rxnlst)):
                    MW, species = MWdic[j], sourcedic[j][1]
                    Rxn = [row if i%2 == 0 else "'%s'" %row for i,row in enumerate(sourcedic[j][2:])]
                    Rxn = ' '.join(Rxn)
                    list_logk = ' '.join(['500.00']*len(T))
                    info = "'%s'" % j + ' ' + '0.000' + ' ' + str(species) + ' ' + Rxn +\
                        ' ' + list_logk + ' ' + str(MW)
                    fout.writelines('%s\n' % info)
                else:
                    continue

            fout.write("'null' 0. 1 1. '0' 0. 0. 0. 0. 0. 0. 0. 0. 0.\n")

        #% close all files
        fout.close()
        if clay_thermo.lower() == 'yes':
            fclay.close()
        return print('Success, your new Pflotran database is ready for download')

    def write_ToughReactdb(self, T, P ):
        """
        This function writes the new ToughReact database into a new folder called "output"   \n
        Parameters
        ----------
            T               :    temperature [°C]   \n
            P               :    pressure [bar]   \n

        Returns
        -------
            Outputs the new database to an ASCII file with filename described in 'objdb'.   \n

        Usage
        -------
          Example:
              (1) General format with default dielectric constant and CO2 activity model and exclusions
                  of solid solutions   \n
                  write_ToughReactdb(T, P, dbaccess = 'location', sourcedb = 'location',
                                    objdb = 'location', sourceformat = 'GWB')   \n
              (2) Inclusion of solid solutions and clay thermo and exclusion of solid solution of clinopyroxene  \n
                  write_ToughReactdb(T, P, solid_solution = 'Yes', clay_thermo = 'Yes', dbaccess = 'location',
                                    sourcedb = 'location', objdb = 'location', sourceformat = 'GWB')   \n
              (3) Inclusion of all solid solutions and clay thermo with \emph{'Duan_Sun'} CO2 activity model and 'FGL97'
                  dielectric constant calculation \n
                  write_ToughReactdb(T, P, nCa, solid_solution = 'Yes', clay_thermo = 'Yes', dbaccess = 'location',
                                    sourcedb = 'location', objdb = 'location', co2actmodel = 'Duan_Sun',
                                    Dielec_method = 'FGL97', sourceformat = 'GWB')   \n

        """

        nCa_cpx = self.cpx_Ca;
        solid_solution = self.solid_solution;      clay_thermo = self.clay_thermo
        objdb = self.objdb;                        Dielec_method = self.Dielec_method
        sourceformat = self.sourceformat;          heatcap_method = self.heatcap_method;
        densityextrap = self.densityextrap

        dbaccessdic, sourcedic, specielist = self.dbr.dbaccessdic, self.dbr.sourcedic, self.dbr.specielist
        act_param, MWdic, chargedic = self.dbr.act_param, self.dbr.MWdic, self.dbr.chargedic

        # from Table 3 of Helgeson, H.C., Kirkham, D.H., Flowers, G.C., 1981. Theoretical prediction of the
        # thermodynamic behavior of aqueous electrolytes at high pressures and temperatures: IV.
        # Calculation of activity coefficients, osmotic coefficients, and apparent molal and standard and relative partial molal properties to 600oC. Am. J. Sci
        rej = {'H+' : 3.08, 'Li+' : 1.64, 'Na+': 1.910, 'K+' : 2.27, 'Rb+' : 2.41, 'Cs+' : 2.61,
                'NH4+' : 2.31, 'Ag+' : 2.20, 'Au+' : 2.31, 'Cu+' : 1.90, 'Mg++' : 2.54, 'Sr++' : 3.0,
                'Ca++' : 2.87, 'Ba++' : 3.22, 'Pb++' : 3.08, 'Zn++' : 2.62, 'Cu++': 2.60, 'Cd++' : 2.85,
                'Hg++' : 2.98, 'Fe++' : 2.62, 'Mn++' : 2.68, 'Fe+++' : 3.46, 'Al+++' : 3.33, 'Au+++' : 3.72,
                'La+++' : 3.96, 'Gd+++' : 3.79, 'In+++' : 3.63, 'Ga+++' : 3.44, 'Tl+++' : 3.77, 'F-' : 1.33,
                'Cl-' : 1.810, 'Br-' : 1.96, 'I-' : 2.20, 'OH-' : 1.40, 'HS-' : 1.84, 'NO3-' : 2.81,
                'HCO3-' : 2.10, 'HSO4-' : 2.37, 'ClO4-' : 3.59, 'ReO4--' : 4.230, 'SO4--' : 3.15,
                'CO3--' : 2.810}

        if os.path.exists(os.path.join(os.getcwd(), 'output/ToughReact')) == False:
                os.makedirs(os.path.join(os.getcwd(), 'output/ToughReact'))

        periodic_table = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           'PeriodicTableJSON.json'), encoding='utf8')
        data = json.load(periodic_table)
        Element = {data['elements'][x]['symbol'] : pd.DataFrame([data['elements'][x]['name'],
                                                                 data['elements'][x]['atomic_mass']],
                                                                index = ['name', 'mass']).T
                   for x in range(len(data['elements']))}
        periodic_table.close()

        missing_species = []
        elemspeclist = [ symbol for x in specielist[0] for symbol, item in Element.items()
                        if item.name[0][:5] == x[:5] ] if sourceformat.upper() == 'GWB' else specielist[0]

        form_del = [1] if sourceformat.upper() == 'GWB' else [1, 3, 4]
        all_species_source = [[i]+k for i, k in sourcedic.items() if i not in (['eh', 'e-', 'H2O']) ]
        all_species_source = [[k for j, k in enumerate(all_species_source[i])
                               if (j not in form_del and k not in elemspeclist and str(k).strip('0123456789.- ') != '') ]
                              if  (i <= len(specielist[0]))
                              else [k for j, k in enumerate(all_species_source[i])
                                    if (j not in form_del and str(k).strip('0123456789.- ') != '') ]
                              for i in range(len(all_species_source)) ]
        for num in range(len(all_species_source)): #
            if num < len(all_species_source):
                lst = [v for v in all_species_source[num] if v not in (['eh', 'e-', 'H2O']) ]

                bool_miss = [x.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
                             not in dbaccessdic.keys() for x in lst  ]
                if any(bool_miss):
                    sublist = [i for (i, v) in zip(lst, bool_miss) if v ]
                    if lst[0] not in sublist:
                        missing_species.append([lst[0]] + sublist)
                    else:
                        missing_species.append(sublist)

        missingfile = open(os.path.join(os.path.abspath("."),'output', 'ToughReact', 'spxNotFound.txt'), 'w')
        for line in missing_species:
            if len(line) > 0:
                missingfile.writelines(line[0])
                missingfile.writelines('\n')
                for i in range(len(line)):
                    missingfile.writelines('   %s' % line[i])
                    missingfile.writelines('\n')
        missingfile.close()
        missing_species = [item for sublist in missing_species for item in sublist]
        missing_species = [i for n, i in enumerate(missing_species) if i not in missing_species[:n]]

        if objdb == None:
            objdb = './thermo%sbars' % int(P[0])
        else:
            objdb = objdb
        # timestr = '.' + time.strftime("%d%b%Y_%H%M")

        fout = open(os.path.join(os.path.abspath("."),'output', 'ToughReact', objdb + '.dat'), 'w+') # + timestr

        Dielec_method = 'JN91' if Dielec_method is None else Dielec_method
        heatcap_method = 'SUPCRT' if heatcap_method is None else heatcap_method

        if Dielec_method.upper() == 'DEW':
            water = ZhangDuan(T = T, P = P)
        else:
            water = iapws95(T = T, P = P)
        rho, dGH2O = water.rho, water.G

        #% Calculation for debye huckel and bdot and water properties
        waterdielc = water_dielec(T = T, P = P, Dielec_method = Dielec_method)
        E, Adh = waterdielc.E, waterdielc.Ah

        rhoEG = {'rho': rho, 'E': E,  'dGH2O': dGH2O}

        # Calculate the rho E G for density extrapolation method here so we have it below
        rhoEGextrap = {}
        if any(rhoEG['rho'] < 350):
            subBornptrs = rhoEG['rho'] < 350
            for i, j in enumerate(zip(T[subBornptrs], P[subBornptrs])):
                rhoextrap = np.linspace(350, 550, 3)
                Pextrap = iapws95(T = j[0], rho = rhoextrap).P if Dielec_method.upper() != 'DEW' else ZhangDuan(T = j[0], rho = rhoextrap).P
                Textrap = j[0]*np.ones(np.size(Pextrap))

                dGH2O = iapws95(T = Textrap, P = Pextrap).G if Dielec_method.upper() != 'DEW' else ZhangDuan(T = Textrap, P = Pextrap).G
                E = water_dielec(T = Textrap, P = Pextrap, Dielec_method = Dielec_method).E

                rhoextrap = np.around(rhoextrap, 3)
                rhoEGextrap['%d_%d' % (j[0], j[1])]= {'rho': rhoextrap,'E': E, 'dGH2O': dGH2O,
                                                       'Textrap': Textrap, 'Pextrap': Pextrap}

        fout.writelines('The file format of this thermodynamic database is suitable for TOUGHREACT\n')
        fout.writelines('Generated by pyGeochemCalc.2021, '  + time.ctime() + '\n')
        fout.writelines('\n!end-of-header     Do not remove this record!\n')

        fout.writelines("'temperature points'  %6s" % len(T))
        for i in range(len(T)):
            fout.writelines( " %6.1f" %  T[i])
        fout.writelines( "\n")

        logKfunc = lambda TK, *x: x[0]*np.log(TK) + x[1] + x[2]*TK + x[3]*TK**(-1) + x[4]*TK**(-2)
        TK = convert_temperature( T, Out_Unit = 'K' )
        x0 = [-3.19605e1, 2.06576e2, 3.73497e-2, -9.01862e3, 6.0111e5]

        #% Basis reactions
        for j in specielist[1]:
            if j not in missing_species:
                if any([MWdic[j]]):
                    MW = MWdic[j]
                else:
                    formula = j if sourcedic[j][0] == '' else sourcedic[j][0]
                    formula = formula.rstrip('(aq)(g)')
                    MW =  calc_elem_count_molewt(formula, Elementdic = Element)[-1]
                name = j.replace('++++', '+4') if j.endswith('++++',0) else j.replace('+++', '+3') if j.endswith('+++',0) else j.replace('++', '+2') if j.endswith('++',0) else j.replace('----', '-4') if j.endswith('----',0) else j.replace('---', '-3') if j.endswith('---',0) else j.replace('--', '-2') if j.endswith('--',0) else j
                if sourceformat.upper() == 'GWB':
                    charge = float(chargedic[j].lstrip().split()[1])
                elif sourceformat.upper() == 'EQ36':
                    charge = float(chargedic[j].split()[-1])
                # ToughReact implementation
                if j in rej.keys():
                    ionrad = rej[j]
                elif charge == -1 :
                    ionrad = rej['Cl-']
                elif charge == -2 :
                    ionrad = round(np.mean([rej['SO4--'], rej['CO3--']]))
                elif charge <= -3 :
                    ionrad = charge*4.2/3
                elif charge == 1 :
                    ionrad = rej['NH4+']
                elif charge == 2 :
                    ionrad = np.mean([rej[j] for j in rej.keys()
                                      if j.endswith('++',0) and not j.endswith('+++',0)])
                elif charge == 3 :
                    ionrad = np.mean([ rej[j] for j in rej.keys() if j.endswith('+++',0)])
                elif charge == 4 :
                    ionrad = 4.5
                elif charge > 3 :
                    ionrad = charge*4.5/4
                else:
                    ionrad = 0

                info = "%-34s" % name + '%5.2f' % ionrad + ' %5.2f' % charge + '   %8.3f' % MW
                info = "'%s'" % info[:len(info.split()[0])] + info[len(info.split()[0]) + 2:]
                fout.writelines('%s\n' % info)
            else:
                continue
        fout.write("'null'   0.  0.  0.\n\n")
        fout.write("#****************************** \n")
        fout.write("#* Aqueous Species \n")
        fout.write("#****************************** \n\n")

        #% Redox and Aqueous reactions
        for j in specielist[2] + specielist[3]:
            if sourceformat.upper() == 'GWB':
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]]
                charge = float(chargedic[j].lstrip().split()[1])
                source_rxns = sourcedic[j][2:]
            elif sourceformat.upper() == 'EQ36':
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1, 2, 3]]
                charge = float(chargedic[j].split()[-1])
                source_rxns = sourcedic[j][4:]
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ]
            if (j not in missing_species) and (len([i for i in rxnlst if i not in missing_species])==len(rxnlst)):
                name = j.replace('++++', '+4') if j.endswith('++++',0) else j.replace('+++', '+3') if j.endswith('+++',0) else j.replace('++', '+2') if j.endswith('++',0) else j.replace('----', '-4') if j.endswith('----',0) else j.replace('---', '-3') if j.endswith('---',0) else j.replace('--', '-2') if j.endswith('--',0) else j
                species = sourcedic[j][1]
                if any([MWdic[j]]):
                    MW = MWdic[j]
                else:
                    formula = j if sourcedic[j][0] == '' else sourcedic[j][0]
                    formula = formula.rstrip('(aq)(g)')
                    MW =  calc_elem_count_molewt(formula, Elementdic = Element)[-1]
                # ToughReact implementation
                if j in rej.keys():
                    ionrad = rej[j]
                elif charge == -1 :
                    ionrad = rej['Cl-']
                elif charge == -2 :
                    ionrad = round(np.mean([rej['SO4--'], rej['CO3--']]))
                elif charge <= -3 :
                    ionrad = charge*4.2/3
                elif charge == 1 :
                    ionrad = rej['NH4+']
                elif charge == 2 :
                    ionrad = np.mean([rej[j] for j in rej.keys()
                                      if j.endswith('++',0) and not j.endswith('+++',0)])
                elif charge == 3 :
                    ionrad = np.mean([ rej[j] for j in rej.keys() if j.endswith('+++',0)])
                elif charge == 4 :
                    ionrad = 4.5
                elif charge > 3 :
                    ionrad = charge*4.5/4
                else:
                    ionrad = 0
                Rxn = [row if i%2==0 else "'%s'" % (row.replace('++++', '+4') if row.endswith('++++',0)
                                                    else row.replace('+++', '+3') if row.endswith('+++',0)
                                                    else row.replace('++', '+2') if row.endswith('++',0)
                                                    else row.replace('----', '-4') if row.endswith('----',0)
                                                    else row.replace('---', '-3') if row.endswith('---',0)
                                                    else row.replace('--', '-2') if row.endswith('--',0)
                                                    else row) for i,row in enumerate(source_rxns)]
                Rxn = '  '.join(Rxn)
                logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                                   specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                   sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'aqueous',
                                   rhoEGextrap = rhoEGextrap, ThermoInUnit = self.ThermoInUnit)
                if densityextrap.lower() == 'yes': 
                    if all(logK.nonsubBornptrs) == True: # if all densities are >= 350
                        logKnan_alert = False            # turn off the prompts for using Density extrapolation
                    else:
                        logKnan_alert = True
                else:
                    logKnan_alert = False                # turn off the prompts for using Density extrapolation
                logK = logK.logK
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                logKcorr = curve_fit(logKfunc, TK[logK != 500].ravel(), logK[logK != 500].ravel(), p0 = x0,  maxfev = 1000000)[0]
                list_logk = '  '.join(str("%9.4f" % e) for e in list(logK))
                list_logKcorr = ' '.join(str("%.5e" % e) for e in list(logKcorr))

                info = "%-32s" % name + '  %7.3f' % MW + '  %3.1f' % ionrad + ' %5.2f' % charge +\
                    '  ' + str(species) + ' ' + Rxn
                info = "'%s'" % info[:len(info.split()[0])] + info[len(info.split()[0]) + 2:]
                fout.writelines('%s\n' % info)

                info = '%-35s' % name + ' ' + list_logk
                info = "'%s'" % info[:len(info.split()[0])] + info[len(info.split()[0]) + 2:]
                fout.writelines('%s\n' % info)

                info = '%-35s' % name + '  ' + list_logKcorr.replace('e','E')
                info = "'%s'" % info[:len(info.split()[0])] + info[len(info.split()[0]) + 2:]
                fout.writelines('%s\n' % info)

            else:
                continue
        fout.writelines("'null'   0. 0. 0. 0 \n\n")
        fout.write("#****************************** \n")
        fout.write("#* Minerals \n")
        fout.write("#****************************** \n\n")
        if logKnan_alert == True:
            warnings.warn('Some temperature and pressure points are out of aqueous species HKF eqns regions of applicability, hence, density extrapolation has been applied')

        #% Mineral reactions
        solid_solution = 'no' if solid_solution is None else solid_solution
        clay_thermo = 'no' if clay_thermo is None else clay_thermo

        if nCa_cpx == 0:
            nCa = 0
        else:
            nCa = nCa_cpx
        if solid_solution.lower() == 'yes':
            solidsolution_no = 11
            fnlist = ['plagio', 'olivine', 'pyroxene', 'cpx'] if nCa > 0 else ['plagio', 'olivine', 'pyroxene']
            for fn in fnlist:
                for nX in np.round(np.linspace(1, 0, solidsolution_no), 1):
                    if fn != 'cpx':
                        ss = calcRxnlogK(X = nX, T = T, P = P, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                         dbaccessdic = dbaccessdic, Specie = fn, densityextrap = densityextrap,
                                         ThermoInUnit = self.ThermoInUnit, rhoEGextrap = rhoEGextrap)
                    else:
                        ss = calcRxnlogK(cpx_Ca = nCa, X = nX, T = T, P = P, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                         dbaccessdic = dbaccessdic, Specie = fn, densityextrap = densityextrap,
                                         ThermoInUnit = self.ThermoInUnit, rhoEGextrap = rhoEGextrap)
                    logK, Rxn = ss.logK, ss.Rxn

                    logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                    outputfmt(fout, logK, Rxn, dataset = 'ToughReact')

        # clay minerals
        if clay_thermo.lower() == 'yes':
            fclay = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clay_elements.dat'), 'r')
            Rd = fclay.readlines()
            Rd = [j.replace('-','_').strip('\n') for j in Rd]
            for i in range(len(Rd)):
                ss = calcRxnlogK(T = T, P = P, Specie = 'Clay', elem = Rd[i].split(','),
                                 dbaccessdic = dbaccessdic, ThermoInUnit = self.ThermoInUnit, rhoEG = rhoEG, #group = layering,
                                 rhoEGextrap = rhoEGextrap, densityextrap = densityextrap)
                logK, Rxn = ss.logK, ss.Rxn
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                outputfmt(fout, logK, Rxn, TK, dataset = 'ToughReact')

        if sourceformat.upper() == 'GWB':
            speclst = specielist[5]
        elif sourceformat.upper() == 'EQ36':
            speclst = specielist[4]+specielist[5]
        for j in speclst:
            if sourceformat.upper() == 'GWB':
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]]
                source_rxns = sourcedic[j][2:]
            elif sourceformat.upper() == 'EQ36':
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1, 2, 3]]
                source_rxns = sourcedic[j][4:]
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ]
            if (j not in missing_species) and (len([k for k in rxnlst if k not in missing_species])==len(rxnlst)):
                if solid_solution.lower() == 'yes' and j in ['Anorthite', 'Albite', 'Forsterite',
                                                    'Fayalite', 'Enstatite', 'Ferrosilite']:
                    continue
                elif solid_solution.lower() == 'yes' and (nCa == 1) and j in ['Diopside', 'Hedenbergite']:
                    continue
                elif clay_thermo.lower() == 'yes' and j in [ Rd[h].split(',')[0] for h in range(len(Rd))]:
                    continue
                else:
                    name = j
                    k = j.replace('(CH3COO)', '(Ac)').replace('CH3COO', '(Ac)')
                    MV, species = dbaccessdic[k][5], sourcedic[j][1]
                    if any([MWdic[j]]):
                        MW = MWdic[j]
                    else:
                        formula = j if sourcedic[j][0] == '' else sourcedic[j][0]
                        formula = formula.rstrip('(aq)(g)(am)')
                        MW =  calc_elem_count_molewt(formula, Elementdic = Element)[-1]
                    Rxn = [row if i%2 == 0 else "'%s'" % (row.replace('++++', '+4') if row.endswith('++++',0)
                                                    else row.replace('+++', '+3') if row.endswith('+++',0)
                                                    else row.replace('++', '+2') if row.endswith('++',0)
                                                    else row.replace('----', '-4') if row.endswith('----',0)
                                                    else row.replace('---', '-3') if row.endswith('---',0)
                                                    else row.replace('--', '-2') if row.endswith('--',0)
                                                    else row) for i, row in enumerate(source_rxns)]
                    Rxn = ' '.join(Rxn)
                    logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                                       specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                       sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'minerals',
                                       heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap).logK
                    logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                    logKcorr = curve_fit(logKfunc, TK[logK!=500].ravel(), logK[logK!=500].ravel(), p0 = x0,  maxfev = 1000000)[0]
                    list_logk = '  '.join(str("%9.4f" % e) for e in list(logK))
                    list_logKcorr = ' '.join(str("%.5e" % e) for e in list(logKcorr))

                    info = "%-32s" % name + "%8.3f" % MW + " %7.2f" % MV +\
                        ' ' + str(species) + ' ' + Rxn
                    info = "'%s'" % info[:len(info.split()[0])] + info[len(info.split()[0]) + 2:]
                    fout.writelines('%s\n' % info)

                    info = '%-35s' % name + ' ' + list_logk
                    info = "'%s'" % info[:len(info.split()[0])] + info[len(info.split()[0]) + 2:]
                    fout.writelines('%s\n' % info)

                    info = '%-35s' % name + '  ' + list_logKcorr.replace('e','E')
                    info = "'%s'" % info[:len(info.split()[0])] + info[len(info.split()[0]) + 2:]
                    fout.writelines('%s\n' % info)
            else:
                continue
        fout.write("'null'   0.  0. 0            ! end of mineral\n\n")
        fout.write("#****************************** \n")
        fout.write("#* Gases \n")
        fout.write("#****************************** \n\n")

        #% Gas reactions
        for j in specielist[6]:
            if sourceformat.upper() == 'GWB':
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1]]
                source_rxns = sourcedic[j][2:]
            elif sourceformat.upper() == 'EQ36':
                rxnlst = [b for a, b in enumerate(sourcedic[j]) if a not in [0, 1, 2, 3]]
                source_rxns = sourcedic[j][4:]
            rxnlst = [v for x, v in enumerate(rxnlst) if x % 2 != 0 ]
            if (j not in missing_species) and (len([k for k in rxnlst if k not in missing_species])==len(rxnlst)):
                name, species = j, sourcedic[j][1]
                if any([MWdic[j]]):
                    MW = MWdic[j]
                else:
                    formula = j if sourcedic[j][0] == '' else sourcedic[j][0]
                    formula = formula.rstrip('(aq)(g)')
                    MW =  calc_elem_count_molewt(formula, Elementdic = Element)[-1]
                Rxn = [row if i%2 == 0 else "'%s'" %(row.replace('++++', '+4') if row.endswith('++++',0)
                                                    else row.replace('+++', '+3') if row.endswith('+++',0)
                                                    else row.replace('++', '+2') if row.endswith('++',0)
                                                    else row.replace('----', '-4') if row.endswith('----',0)
                                                    else row.replace('---', '-3') if row.endswith('---',0)
                                                    else row.replace('--', '-2') if row.endswith('--',0)
                                                    else row) for i,row in enumerate(source_rxns)]
                Rxn = ' '.join(Rxn)
                logK = calcRxnlogK( T = T, P = P, Specie = j, dbaccessdic = dbaccessdic, sourcedic = sourcedic,
                                   specielist = specielist, Dielec_method = Dielec_method, rhoEG = rhoEG,
                                   sourceformat = sourceformat, densityextrap = densityextrap, Specie_class = 'gases',
                                   heatcap_method = heatcap_method, rhoEGextrap = rhoEGextrap).logK
                logK = np.where(np.isnan(logK), 500, logK) # set abitrary 500 to nan values
                logKcorr = curve_fit(logKfunc, TK[logK!=500].ravel(), logK[logK!=500].ravel(), p0 = x0,  maxfev = 1000000)[0]
                list_logk = '  '.join(str("%9.4f" % e) for e in list(logK))
                list_logKcorr = ' '.join(str("%.5e" % e) for e in list(logKcorr))

                info = "%-32s" % name + "%8.3f" % MW + ' ' + '0.100E-09' +\
                    ' ' + str(species) + ' ' + Rxn
                info = "'%s'" % info[:len(info.split()[0])] + info[len(info.split()[0]) + 2:]
                fout.writelines('%s\n' % info)

                info = '%-35s' % name + ' ' + list_logk
                info = "'%s'" % info[:len(info.split()[0])] + info[len(info.split()[0]) + 2:]
                fout.writelines('%s\n' % info)

                info = '%-35s' % name + '  ' + list_logKcorr.replace('e','E')
                info = "'%s'" % info[:len(info.split()[0])] + info[len(info.split()[0]) + 2:]
                fout.writelines('%s\n' % info)
            else:
                continue

        fout.write("'null'   0.  0. 0            ! end of gas\n\n")
        fout.write("#****************************** \n")
        fout.write("#* Surface complexes \n")
        fout.write("#****************************** \n\n")
        fout.write("'null'  0.  0             ! surface complex\n\n")
        
        #% Pitzer database
        if act_param['activity_model'] == 'h-m-w' and sourceformat.lower() == 'eq36':
            fout.write("StartPitzerParams     !this is a needed keyword!!!\n\n")
            fout.write("#************************************************************\n")
            delimiters = "/", "\\"
            patterns = '|'.join('(?<={})'.format(re.escape(delim)) for delim in delimiters)
            fout.write("#* Pitzer ion interaction parameters from EQ3/6 %s\n" % re.split(patterns, self.sourcedb)[-1])
            fout.write("#************************************************************\n")
            fout.write("#!!! Note: 'Miscellaneous' below is a needed flag !!!!\n\n")

            fout.write("+--------------------------------------------------------------------\n")
            fout.write("Miscellaneous parameters\n")
            fout.write("+--------------------------------------------------------------------\n")
            fout.write("Temperature limits (degC)\n")
            fout.writelines('      %9.4f %9.4f\n' % (T[0], T[-1]))
            fout.write("temperatures\n")
            for i in range(len(T)):
                i = i + 1
                if (i == 1) | (i == 5):
                    fout.writelines( "      %9.4f" %  T[i-1])
                else:
                    fout.writelines( " %9.4f" %  T[i-1])
                if (i % 4 == 0) | (i == len(T)):
                    fout.writelines( "\n")
            fout.write("debye huckel aphi \n")
            Aphi = Adh*np.log(10)/3
            for i in range(len(Aphi)):
                i = i + 1
                if (i == 1) | (i == 5):
                    fout.writelines( "      %9.4f" %  Aphi[i-1])
                else:
                    fout.writelines( " %9.4f" %  Aphi[i-1])
                if (i % 4 == 0) | (i == len(Aphi)):
                    fout.writelines( "\n")

            fout.write("\n+--------------------------------------------------------------------\n")
            fout.write("ca combinations: beta(n)(ca) and Cphi(ca) [optional: alpha(n)(ca)]\n")
            fout.write("+--------------------------------------------------------------------\n")
            for k in act_param['alpha_beta'].keys():
                if all([x not in missing_species for x in k.rstrip('\n').split()]):
                    ks = k.rstrip('\n').split()
                    fout.writelines('%-8s\n' % ks[0]) if len(ks) == 1 else fout.writelines('%-24s  %-24s\n' % (ks[0], ks[1]))  if len(ks) == 2 else fout.writelines('%-8s  %-8s  %-8s\n' % (ks[0], ks[1], ks[2]))
                    lst = ['alpha1', 'alpha2', 'beta0', 'beta1', 'beta2', 'cphi']
                    app_lst = ['alpha(1)', 'alpha(2)', 'beta(0)', 'beta(1)', 'beta(2)', 'Cphi']
                    for l, order in enumerate(lst):
                        if l < 2:
                            fout.writelines('  %-6s = %s \n' % (app_lst[l], act_param[order][k]))
                        else:
                            fout.writelines('  %-6s: \n' % app_lst[l])
                            if type(act_param[order][k]) == float:
                                fout.writelines('    a1 = %s \n' % act_param[order][k])
                                fout.writelines('    a2 = 0. \n    a3 = 0. \n    a4 = 0. \n    a5 = 0. \n    a6 = 0. \n' )
                            else:
                                fout.writelines('    a1 = %s \n' % act_param[order][k][0])
                                fout.writelines('    a2 = %s \n'  % act_param[order][k][1])
                                fout.writelines('    a3 = %s \n'  % act_param[order][k][2])
                                fout.writelines('    a4 = %s \n'  % act_param[order][k][3])
                                fout.writelines('    a5 = 0. \n    a6 = 0. \n' )
                    fout.writelines('+---------------------------------------------------------------\n')
            fout.write("cc' and aa' combinations: theta(cc') and theta(aa')\n")
            fout.write("+--------------------------------------------------------------------\n")
            for k in act_param['theta'].keys():
                if all([x not in missing_species for x in k.rstrip('\n').split()]):
                    ks = k.rstrip('\n').split()
                    fout.writelines('%-8s\n' % ks[0]) if len(ks) == 1 else fout.writelines('%-24s  %-24s\n' % (ks[0], ks[1]))  if len(ks) == 2 else fout.writelines('%-8s  %-8s  %-8s\n' % (ks[0], ks[1], ks[2]))
                    fout.writelines('  %-6s: \n' % 'theta')
                    if type(act_param['theta'][k]) == float:
                        fout.writelines('    a1 = %s \n' % act_param['theta'][k])
                        fout.writelines('    a2 = 0. \n    a3 = 0. \n    a4 = 0. \n    a5 = 0. \n    a6 = 0. \n' )
                    else:
                        fout.writelines('    a1 = %s \n' % act_param['theta'][k][0])
                        fout.writelines('    a2 = %s \n'  % act_param['theta'][k][1])
                        fout.writelines('    a3 = %s \n'  % act_param['theta'][k][2])
                        fout.writelines('    a4 = %s \n'  % act_param['theta'][k][3])
                        fout.writelines('    a5 = 0. \n    a6 = 0. \n' )
                    fout.writelines('+---------------------------------------------------------------\n')
            fout.write("nc and na combinations: lambda(nc) and lambda(na)\n")
            fout.write("+--------------------------------------------------------------------\n")
            if act_param['lambda'].keys():  # checks if dictionary is not empty
                ions_exmpt = [j for j, k in enumerate(act_param['lambda'].keys()) if len(k.rstrip('\n').split()) <= 1][0]
                ions_exmpt = list(act_param['lambda'].keys())[ions_exmpt:]
                for k in act_param['lambda'].keys():
                    if all([x not in missing_species for x in k.rstrip('\n').split()]) and k not in ions_exmpt:
                        ks = k.rstrip('\n').split()
                        fout.writelines('%-8s\n' % ks[0]) if len(ks) == 1 else fout.writelines('%-24s  %-24s\n' % (ks[0], ks[1]))  if len(ks) == 2 else fout.writelines('%-8s  %-8s  %-8s\n' % (ks[0], ks[1], ks[2]))
                        fout.writelines('  %-6s: \n' % 'lambda')
                        if type(act_param['lambda'][k]) == float:
                            fout.writelines('    a1 = %s \n' % act_param['lambda'][k])
                            fout.writelines('    a2 = 0. \n    a3 = 0. \n    a4 = 0. \n    a5 = 0. \n    a6 = 0. \n' )
                        else:
                            fout.writelines('    a1 = %s \n' % act_param['lambda'][k][0])
                            fout.writelines('    a2 = %s \n'  % act_param['lambda'][k][1])
                            fout.writelines('    a3 = %s \n'  % act_param['lambda'][k][2])
                            fout.writelines('    a4 = %s \n'  % act_param['lambda'][k][3])
                            fout.writelines('    a5 = 0. \n    a6 = 0. \n' )
                        fout.writelines('+---------------------------------------------------------------\n')
            fout.write("nn combinations: lambda(nn) and mu(nnn) \n")
            fout.write("+--------------------------------------------------------------------\n")
            if act_param['mu'].keys():  # checks if dictionary is empty
                ions_exmpt = [j for j, k in enumerate(act_param['mu'].keys()) if len(k.rstrip('\n').split()) <= 1][0]
                ions_exmpt = list(act_param['mu'].keys())[ions_exmpt:]
                for k in act_param['mu'].keys():
                    if all([x not in missing_species for x in k.rstrip('\n').split()]):
                        ks = k.rstrip('\n').split()
                        if len(ks) <= 1:
                            fout.writelines('%-8s\n' % ks[0]) if len(ks) == 1 else fout.writelines('%-24s  %-24s\n' % (ks[0], ks[1]))  if len(ks) == 2 else fout.writelines('%-8s  %-8s  %-8s\n' % (ks[0], ks[1], ks[2]))
                            fout.writelines('  %-6s: \n' % 'lambda')
                            if type(act_param['lambda'][k]) == float:
                                fout.writelines('    a1 = %s \n' % act_param['lambda'][k])
                                fout.writelines('    a2 = 0. \n    a3 = 0. \n    a4 = 0. \n    a5 = 0. \n    a6 = 0. \n' )
                            else:
                                fout.writelines('    a1 = %s \n' % act_param['lambda'][k][0])
                                fout.writelines('    a2 = %s \n'  % act_param['lambda'][k][1])
                                fout.writelines('    a3 = %s \n'  % act_param['lambda'][k][2])
                                fout.writelines('    a4 = %s \n'  % act_param['lambda'][k][3])
                                fout.writelines('    a5 = 0. \n    a6 = 0. \n' )
                            fout.writelines('  %-6s: \n' % 'mu')
                            if type(act_param['mu'][k]) == float:
                                fout.writelines('    a1 = %s \n' % act_param['mu'][k])
                                fout.writelines('    a2 = 0. \n    a3 = 0. \n    a4 = 0. \n    a5 = 0. \n    a6 = 0. \n' )
                            else:
                                fout.writelines('    a1 = %s \n' % act_param['mu'][k][0])
                                fout.writelines('    a2 = %s \n'  % act_param['mu'][k][1])
                                fout.writelines('    a3 = %s \n'  % act_param['mu'][k][2])
                                fout.writelines('    a4 = %s \n'  % act_param['mu'][k][3])
                                fout.writelines('    a5 = 0. \n    a6 = 0. \n' )
                            fout.writelines('+---------------------------------------------------------------\n')
                fout.write("nn' combinations: lambda(nn') \n")
                fout.write("+--------------------------------------------------------------------\n")
                for k in [j for j in ions_exmpt if j not in act_param['mu'].keys()]:
                    if all([x not in missing_species for x in k.rstrip('\n').split()]):
                        ks = k.rstrip('\n').split()
                        fout.writelines('%-8s\n' % ks[0]) if len(ks) == 1 else fout.writelines('%-24s  %-24s\n' % (ks[0], ks[1]))  if len(ks) == 2 else fout.writelines('%-8s  %-8s  %-8s\n' % (ks[0], ks[1], ks[2]))
                        fout.writelines('  %-6s: \n' % 'lambda')
                        if type(act_param['lambda'][k]) == float:
                            fout.writelines('    a1 = %s \n' % act_param['lambda'][k])
                            fout.writelines('    a2 = 0. \n    a3 = 0. \n    a4 = 0. \n    a5 = 0. \n    a6 = 0. \n' )
                        else:
                            fout.writelines('    a1 = %s \n' % act_param['lambda'][k][0])
                            fout.writelines('    a2 = %s \n'  % act_param['lambda'][k][1])
                            fout.writelines('    a3 = %s \n'  % act_param['lambda'][k][2])
                            fout.writelines('    a4 = %s \n'  % act_param['lambda'][k][3])
                            fout.writelines('    a5 = 0. \n    a6 = 0. \n' )
                        fout.writelines('+---------------------------------------------------------------\n')
            fout.write("cc'a and aa'c combinations: psi(cc'a) and psi(aa'c) \n")
            fout.write("+--------------------------------------------------------------------\n")
            for k in act_param['psi'].keys():
                if all([x not in missing_species for x in k.rstrip('\n').split()]):
                    ks = k.rstrip('\n').split()
                    fout.writelines('%-8s\n' % ks[0]) if len(ks) == 1 else fout.writelines('%-24s  %-24s\n' % (ks[0], ks[1]))  if len(ks) == 2 else fout.writelines('%-8s  %-8s  %-8s\n' % (ks[0], ks[1], ks[2]))
                    fout.writelines('  %-6s: \n' % 'psi')
                    if type(act_param['psi'][k]) == float:
                        fout.writelines('    a1 = %s \n' % act_param['psi'][k])
                        fout.writelines('    a2 = 0. \n    a3 = 0. \n    a4 = 0. \n    a5 = 0. \n    a6 = 0. \n' )
                    else:
                        fout.writelines('    a1 = %s \n' % act_param['psi'][k][0])
                        fout.writelines('    a2 = %s \n'  % act_param['psi'][k][1])
                        fout.writelines('    a3 = %s \n'  % act_param['psi'][k][2])
                        fout.writelines('    a4 = %s \n'  % act_param['psi'][k][3])
                        fout.writelines('    a5 = 0. \n    a6 = 0. \n' )
                    fout.writelines('+---------------------------------------------------------------\n')
            fout.write("nca combinations: zeta(nca) \n")
            fout.write("+--------------------------------------------------------------------\n")
            for k in act_param['zeta'].keys():
                if all([x not in missing_species for x in k.rstrip('\n').split()]):
                    ks = k.rstrip('\n').split()
                    fout.writelines('%-8s\n' % ks[0]) if len(ks) == 1 else fout.writelines('%-24s  %-24s\n' % (ks[0], ks[1]))  if len(ks) == 2 else fout.writelines('%-8s  %-8s  %-8s\n' % (ks[0], ks[1], ks[2]))
                    fout.writelines('  %-6s: \n' % 'zeta')
                    if type(act_param['zeta'][k]) == float:
                        fout.writelines('    a1 = %s \n' % act_param['zeta'][k])
                        fout.writelines('    a2 = 0. \n    a3 = 0. \n    a4 = 0. \n    a5 = 0. \n    a6 = 0. \n' )
                    else:
                        fout.writelines('    a1 = %s \n' % act_param['zeta'][k][0])
                        fout.writelines('    a2 = %s \n'  % act_param['zeta'][k][1])
                        fout.writelines('    a3 = %s \n'  % act_param['zeta'][k][2])
                        fout.writelines('    a4 = %s \n'  % act_param['zeta'][k][3])
                        fout.writelines('    a5 = 0. \n    a6 = 0. \n' )
                    fout.writelines('+---------------------------------------------------------------\n')
            fout.write("nnn' combinations: mu(nnn') \n")
            fout.write("+--------------------------------------------------------------------\n")
            for k in act_param['mu'].keys():
                if all([x not in missing_species for x in k.rstrip('\n').split()]):
                    ks = k.rstrip('\n').split()
                    if len(ks) > 1:
                        fout.writelines('%-8s\n' % ks[0]) if len(ks) == 1 else fout.writelines('%-24s  %-24s\n' % (ks[0], ks[1]))  if len(ks) == 2 else fout.writelines('%-8s  %-8s  %-8s\n' % (ks[0], ks[1], ks[2]))
                        fout.writelines('  %-6s: \n' % 'mu')
                        if type(act_param['mu'][k]) == float:
                            fout.writelines('    a1 = %s \n' % act_param['mu'][k])
                            fout.writelines('    a2 = 0. \n    a3 = 0. \n    a4 = 0. \n    a5 = 0. \n    a6 = 0. \n' )
                        else:
                            fout.writelines('    a1 = %s \n' % act_param['mu'][k][0])
                            fout.writelines('    a2 = %s \n'  % act_param['mu'][k][1])
                            fout.writelines('    a3 = %s \n'  % act_param['mu'][k][2])
                            fout.writelines('    a4 = %s \n'  % act_param['mu'][k][3])
                            fout.writelines('    a5 = 0. \n    a6 = 0. \n' )
                        fout.writelines('+---------------------------------------------------------------\n')

            fout.write("'null'  0.  0 !this is needed here to end the DB\n")


        #% close all files
        fout.close()
        if clay_thermo.lower() == 'yes':
            fclay.close()

        return print('Success, your new ToughReact database is ready for download')

def main_function_name(module):
    """
     print main_function name
    """
    functname = []
    for i in dir(module):
        if not i.startswith(('Delta', 'Psi', 'phir', 'phi0', '__')):
            if i not in ['IAPWS95_COEFFS', 'var_name', 'J_to_cal', 'splev', 'splrep',
                         'MW', 'curve_fit', 'eps', 'feval', 'warnings', 'inspect',
                         'lu_factor', 'lu_solve', 'math', 'Rbf', 'json', 'pd','newton',
                         'np', 'os', 'textwrap', 'theta', 'time', 'read_specific_lines',
                         'fsolve', 'main_function_name', 'warnings', 'calcRxnlogKonly',
                         're', 'timer', 'root_scalar', 'functools']:
                functname.append(i)
    return functname

# pipreqs --encoding=utf8 --debug . # creates requirements.txt
