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

import math, os
import numpy as np
from .water_eos import iapws95, ZhangDuan, water_dielec, convert_temperature
from .species_eos import heatcap, supcrtaq
from .read_db import db_reader

def roundup_tenth(x):
    return int(math.ceil(x / 10.0)) * 10


def Molecularweight():
    """
    This function stores the Molecular weight of all elements
    """
    MW = {'O': 15.9994,
         'Ag': 107.8682,
         'Al': 26.98154,
         'Am': 243.0,
         'Ar': 39.948,
         'Au': 196.96654,
         'B': 10.811,
         'Ba': 137.327,
         'Be': 9.01218,
         'Br': 79.904,
         'Ca': 40.078,
         'Cd': 112.411,
         'Ce': 140.115,
         'Cl': 35.4527,
         'Co': 58.9332,
         'Cr': 51.9961,
         'Cs': 132.90543,
         'Cu': 63.546,
         'Dy': 162.5,
         'Er': 167.26,
         'Eu': 151.965,
         'F': 18.9984,
         'Fe': 55.847,
         'Ga': 69.723,
         'Gd': 157.25,
         'H': 1.00794,
         'As': 74.92159,
         'C': 12.011,
         'P': 30.97376,
         'He': 4.0026,
         'Hg': 200.59,
         'Ho': 164.93032,
         'I': 126.90447,
         'In': 114.82,
         'K': 39.0983,
         'Kr': 83.8,
         'La': 138.9055,
         'Li': 6.941,
         'Lu': 174.967,
         'Mg': 24.305,
         'Mn': 54.93805,
         'Mo': 95.94,
         'N': 14.00674,
         'Na': 22.98977,
         'Nd': 144.24,
         'Ne': 20.1797,
         'Ni': 58.69,
         'Np': 237.048,
         'Pb': 207.2,
         'Pd': 106.42,
         'Pr': 140.90765,
         'Pu': 244.0,
         'Ra': 226.025,
         'Rb': 85.4678,
         'Re': 186.207,
         'Rn': 222.0,
         'Ru': 101.07,
         'S': 32.066,
         'Sb': 121.75,
         'Sc': 44.95591,
         'Se': 78.96,
         'Si': 28.0855,
         'Sm': 150.36,
         'Sn': 118.71,
         'Sr': 87.62,
         'Tb': 158.92534,
         'Tc': 98.0,
         'Th': 232.0381,
         'Ti': 47.88,
         'Tl': 204.3833,
         'Tm': 168.93421,
         'U': 238.0289,
         'V': 50.9415,
         'W': 183.85,
         'Xe': 131.29,
         'Y': 88.90585,
         'Yb': 173.04,
         'Zn': 65.39,
         'Zr': 91.224}

    return MW

MW = Molecularweight()
J_to_cal = 4.184

def generate_structural_formula(Rxn, Interlayer, Octahedral, Tetrahedral, Oxy, OH, MW, charge):
    # Extract cation counts
    nCs = Interlayer['Tot']['Cs+']
    nRb = Interlayer['Tot']['Rb+']
    nK = Interlayer['Tot']['K+']
    nNa = Interlayer['Tot']['Na+']
    nCa = Interlayer['Tot']['Ca2+']
    nH3O = Interlayer['Tot']['H3O+']
    nNi = Octahedral['Tot']['Ni2+']
    nTi = Octahedral['Tot']['Ti4+']; nCr = Octahedral['Tot']['Cr3+']
    nV = Octahedral['Tot']['V3+']; nVO = Octahedral['Tot']['VO2+']
    nLi = Interlayer['Tot']['Li+'] + Octahedral['Tot']['Li+']
    nMg = Interlayer['Tot']['Mg2+'] + Octahedral['Tot']['Mg2+']
    nFe = Interlayer['Tot']['Fe2+'] + Octahedral['Tot']['Fe2+']
    nZn = Interlayer['Tot']['Zn2+'] + Octahedral['Tot']['Zn2+']
    nMn = Interlayer['Tot']['Mn2+'] + Octahedral['Tot']['Mn2+']
    nCo = Interlayer['Tot']['Co2+'] + Octahedral['Tot']['Co2+']
    nCd = Interlayer['Tot']['Cd2+'] + Octahedral['Tot']['Cd2+']
    nAl = Tetrahedral['Tot']['Al3+'] + Octahedral['Tot']['Al3+']
    nFe3 = Tetrahedral['Tot']['Fe3+'] + Octahedral['Tot']['Fe3+']
    nSi = Tetrahedral['Tot']['Si4+']

    # Calculate hydrogen content
    nH = np.sum([Interlayer['Tot'][j]*charge[j]
                for j in list(Interlayer['Tot'].keys())[:7] + \
                    list(Interlayer['Tot'].keys())[-5:]]) + \
        np.sum([Octahedral['Tot'][j]*charge[j]
               for j in list(Octahedral['Tot'].keys())[:-1] if j != 'Cd2+']) + \
           np.sum([Tetrahedral['Tot'][j]*charge[j] for j in list(Tetrahedral['Tot'].keys())[1:]])
    nH = round(nH, 3)

    # Helper function to format numbers
    def format_num(value):
        return f"{value:.3f}".rstrip('0').rstrip('.') if not value.is_integer() else f"{int(value)}"

    # Build interlayer formula (first bracket)
    interlayer_parts = []
    if nCs != 0: interlayer_parts.append(f"Cs{format_num(nCs)}")
    if nRb != 0: interlayer_parts.append(f"Rb{format_num(nRb)}")
    if nK != 0: interlayer_parts.append(f"K{format_num(nK)}")
    if nNa != 0: interlayer_parts.append(f"Na{format_num(nNa)}")
    if nH3O != 0: interlayer_parts.append(f"H{format_num(nH3O)}")
    if nCa != 0: interlayer_parts.append(f"Ca{format_num(nCa)}")
    if Interlayer['Tot']['Li+'] != 0: interlayer_parts.append(f"Li{format_num(Interlayer['Tot']['Li+'])}")
    if Interlayer['Tot']['Mg2+'] != 0: interlayer_parts.append(f"Mg{format_num(Interlayer['Tot']['Mg2+'])}")
    if Interlayer['Tot']['Fe2+'] != 0: interlayer_parts.append(f"Fe{format_num(Interlayer['Tot']['Fe2+'])}")
    if Interlayer['Tot']['Zn2+'] != 0: interlayer_parts.append(f"Fe{format_num(Interlayer['Tot']['Zn2+'])}")
    if Interlayer['Tot']['Mn2+'] != 0: interlayer_parts.append(f"Fe{format_num(Interlayer['Tot']['Mn2+'])}")
    if Interlayer['Tot']['Co2+'] != 0: interlayer_parts.append(f"Fe{format_num(Interlayer['Tot']['Co2+'])}")
    if Interlayer['Tot']['Cd2+'] != 0: interlayer_parts.append(f"Fe{format_num(Interlayer['Tot']['Cd2+'])}")
    interlayer_formula = "".join(interlayer_parts)

    # Build octahedral formula (second bracket)
    octahedral_parts = []
    if Octahedral['Tot']['Mg2+'] > 0: octahedral_parts.append(f"Mg{format_num(Octahedral['Tot']['Mg2+'])}")
    if Octahedral['Tot']['Li+'] > 0: octahedral_parts.append(f"Li{format_num(Octahedral['Tot']['Li+'])}")
    if Octahedral['Tot']['Fe2+'] > 0: octahedral_parts.append(f"Fe{format_num(Octahedral['Tot']['Fe2+'])}")
    if nNi > 0: octahedral_parts.append(f"Ni{format_num(nNi)}")
    if nTi > 0: octahedral_parts.append(f"Ti{format_num(nTi)}")
    if nCr > 0: octahedral_parts.append(f"Cr{format_num(nCr)}")
    if nV > 0: octahedral_parts.append(f"V{format_num(nV)}")
    if nVO > 0: octahedral_parts.append(f"VO{format_num(nVO)}")
    if Octahedral['Tot']['Mn2+'] > 0: octahedral_parts.append(f"Mn{format_num(Octahedral['Tot']['Mn2+'])}")
    if Octahedral['Tot']['Co2+'] > 0: octahedral_parts.append(f"Co{format_num(Octahedral['Tot']['Co2+'])}")
    if Octahedral['Tot']['Zn2+'] > 0: octahedral_parts.append(f"Zn{format_num(Octahedral['Tot']['Zn2+'])}")
    if Octahedral['Tot']['Cd2+'] > 0: octahedral_parts.append(f"Cd{format_num(Octahedral['Tot']['Cd2+'])}")
    if Octahedral['Tot']['Al3+'] > 0: octahedral_parts.append(f"Al{format_num(Octahedral['Tot']['Al3+'])}")
    if Octahedral['Tot']['Fe3+'] > 0: octahedral_parts.append(f"FeIII{format_num(Octahedral['Tot']['Fe3+'])}")
    octahedral_formula = "".join(octahedral_parts)

    # Build tetrahedral formula (third bracket)
    tetrahedral_parts = []
    if nSi > 0: tetrahedral_parts.append(f"Si{format_num(nSi)}")
    if Tetrahedral['Tot']['Al3+'] > 0: tetrahedral_parts.append(f"Al{format_num(Tetrahedral['Tot']['Al3+'])}")
    if Tetrahedral['Tot']['Fe3+'] > 0: tetrahedral_parts.append(f"FeIII{format_num(Tetrahedral['Tot']['Fe3+'])}")
    tetrahedral_formula = "".join(tetrahedral_parts)

    # Construct the structural formula
    Rxn['struct_formula'] = f"({interlayer_formula})({octahedral_formula})({tetrahedral_formula})O{int(Oxy - OH)}(OH){int(OH)}"

    return Rxn



def calclogKclays(TC, P, *elem, dbaccessdic = None, group = None, cation_order = None, export_struct_formula = None,
                  Dielec_method = None, ClayMintype = None, Int_Mg_fract = None, Int_Li_fract = None,
                  heatcap_approx = None, ThermoInUnit = 'cal', **rhoEG):
    """
    This function calculates logK values and reaction parameters of clay reactions using below references:

    Parameters
    ----------
        TC : float, vector
            Temperature [°C]  \n
        P : float, vector
            Pressure [bar]  \n
        elem : list
            list containing nine or ten parameters with clay names and elements compositions with the following format ['Montmorillonite_Lc_MgK', 'Si', 'Al', 'FeIII', 'FeII', 'Mg', 'K', 'Na', 'Ca', 'Li', 'H3O'] \n
        dbacessdic : dict
            dictionary of species from direct-access database, optional, default is speq23  \n
        group : string
            specify the structural layering of the phyllosilicate, for layers composed of ``1 tetrahedral + 1 octahedral sheet (1:1 layer)`` - specify '7A', ``2 tetrahedral + 1 octahedral sheet (2:1 layer)`` - specify '10A', or the latter with a ``brucitic sheet in the interlayer (2:1:1 layer)``  - specify '14A' (optional), if not specified, default is based on charge balance on the cations and anions \n
        cation_order : string
            specify ordering of Si and Al ions either 'Eastonite', 'Ordered', 'Random', or 'HDC'  (optional), if not specified, default is based on guidelines by Vinograd (1995) \n
        Dielec_method : string
            specify either 'FGL97' or 'JN91' or 'DEW' as the method to calculate dielectric constant (optional), if not specified, default - 'JN91'
        ClayMintype : string
            specify either 'Smectite' or 'Chlorite' or 'Mica' as the clay type, if not specified default - 'Smectites'
        Int_Mg_fract : string
            specify the fraction of Mg to partition into Interlayer sheet and the remainder will be partitioned into Octahedral sheet, if not specified, default is 1
        Int_Li_fract : string
            specify the fraction of Li to partition into Interlayer sheet and the remainder will be partitioned into Octahedral sheet, if not specified, default is 1
        heatcap_approx : string
            specify either 'Maier-Kelley' or 'constant' as the approximation method for clay minerals' specific heat capacity calculation, default is 'constant', based on ClayTherm's definition for specific cations (Octahedral sites: Li+, Mn2+, Cr3+, Ni2+, Co2+, Zn2+; Interlayer sites: Cs+, Rb+, Li+, Ba2+, Sr2+, Mg2+, Cu2+, Co2+, Zn2+, H3O+) \n
        ThermoInUnit : string
            specify either 'cal' or 'KJ' as the input units for species properties (optional), particularly used to covert KJ data to cal by supcrtaq function if not specified default - 'cal'
        rhoEG : dict
            dictionary of water properties like  density (rho), dielectric factor (E) and Gibbs Energy  (optional)

    Returns
    -------
        logK_clay : float, vector
            logarithmic K values
        Rxn : dict
            dictionary of reaction thermodynamic properties

    Usage
    -------
        The general usage of calclogKclays is as follows:  \n
        (1) Without the optional arguments, not on steam saturation curve:  \n
            [logK, Rxn] = calclogKclays(TC, P, *elem),  \n
            where T is temperature in celsius and P is pressure in bar;
        (2) Without the optional arguments, on steam saturation curve:  \n
            [logK, Rxn] = calclogKclays(TC, 'T', *elem),   \n
            where T is temperature in celsius, followed with a quoted char 'T'  \n
            [logK, Rxn] = calclogKclays(P, 'P', *elem), \n
            where P is pressure in bar, followed with a quoted char 'P'.
        (3) Meanwhile, usage with any specific dielectric constant method ('FGL97') for
            condition not on steam saturation curve is as follows. Default method is 'JN91' \n
            [logK, Rxn] = calclogKclays(TC, P, *elem, dbacessdic = dbacessdic, group = '10A', cation_order = 'HDC', Dielec_method = 'FGL97')

    Examples
    --------
    >>> logK, Rxn = calclogKclays(50, 'T', *['Clinochlore', '3', '2', '0', '0',
                                             '5', '0', '0', '0', '0'],
                                  group = '14A')
    >>> logK
        57.56820225

    References
    ----------
        (1) Blanc, P., Vieillard, P., Gailhanou, H., Gaboreau, S., Gaucher, É., Fialips, C. I.,
            Madé, B & Giffaut, E. (2015). A generalized model for predicting the thermodynamic properties
            of clay minerals. American journal of science, 315(8), 734-780. \n
        (2) Blanc, P., Gherardi, F., Vieillard, P., Marty, N. C. M., Gailhanou, H., Gaboreau, S.,
            Letat, B., Geloni, C., Gaucher, E.C. and Madé, B. (2021). Thermodynamics for clay minerals:
            calculation tools and application to the case of illite/smectite interstratified minerals.
            Applied Geochemistry, 104986.  \n
        (3) Vinograd, V.L., 1995. Substitution of [4]Al in layer silicates: Calculation of the Al-Si
            configurational entropy according to 29Si NMR Spectra. Physics and Chemistry of Minerals
            22, 87-98. (
            saponite-H-Li  Li0.165H0.165)(Mg3)(Si3.67Al0.33)O10(OH)2
            saponite-Mg-Li(VI)	(Mg0.17)(Li0.33Mg2.835)(Si3.66Al0.34)O10(OH)2	
            ['Name', 'Si', 'Al', 'FeIII', 'FeII', 'Mg', 'K', 'Na', 'Ca', 'Li', 'H3O']			
    """

    if type(P) == str:
        if P == 'T':
            P = np.array(iapws95(T = TC).P, dtype=float)  # force float array
            P[(np.isnan(P)) | (P < 1)] = 1.0133
        elif P == 'P':
            P = TC   # Assign first input T to pressure in bar
            TC = iapws95(P = P).TC

    if np.ndim(TC) == 0 :
        TC = np.array(TC).ravel()
    elif np.size(TC) == 2:
        TC = np.array([roundup_tenth(j) if j != 0 else 0.01 for j in np.linspace(TC[0], TC[-1], 8)])

    if np.size(P) <= 2:
        P = np.ravel(P)
        P = P[0]*np.ones(np.size(TC))

    if dbaccessdic is None:
        dbaccess_dir = './default_db/speq23.dat'
        dbaccess_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), dbaccess_dir)
        dbaccessdic = db_reader(dbaccess = dbaccess_dir).dbaccessdic

    export_struct_formula = True if export_struct_formula is None else False
    Int_Li_fract = 1 if Int_Li_fract is None else Int_Li_fract
    Dielec_method = 'JN91' if Dielec_method is None else Dielec_method
    heatcap_approx = 'constant' if heatcap_approx is None else heatcap_approx

    mass_bal = round(np.sum([j*float(k) for j,k in zip([4, 3, 3, 2, 2, 1, 1, 2, 1, 1], elem[1:])]), 0) if len(elem) > 10 else round(np.sum([j*float(k) for j,k in zip([4, 3, 3, 2, 2, 1, 1, 2, 1], elem[1:])]), 2) 
    if mass_bal not in [14, 22, 28]:
        raise Exception("Mass/Charge balance error: the summation of the product of charge and mass of each element must equal 14 for '7A' group, 22 for '10A' group and 28 for  '14A' group")
    if group is None:
        group = '10A' if mass_bal == 22 else '7A' if mass_bal == 14 else '14A' if mass_bal == 28 else None

    ClayMintype = 'Smectites' if ClayMintype is None else ClayMintype

    if rhoEG.__len__() != 0:
        rho = rhoEG['rho'].ravel()
        E = rhoEG['E'].ravel()
        dGH2O = rhoEG['dGH2O'].ravel()
    else:
        if Dielec_method.upper() == 'DEW':
            water = ZhangDuan(T = TC, P = P)
        else:
            water = iapws95(T = TC, P = P)
        rho, dGH2O = water.rho, water.G
        E = water_dielec(T = TC, P = P, Dielec_method = Dielec_method).E

        rhoEG = {'rho': rho, 'E': E,  'dGH2O': dGH2O}

    name = '' if len(elem) == 0 else elem[0]
    T_Si = 0 if len(elem) == 0 else float(elem[1]);
    if len(elem) == 0:
        T_Al = 0
    else:
        if group == '7A':
            T_Al = 2 - float(elem[1]) if float(elem[2]) != 0 else 0
            T_Al = T_Al if float(elem[2]) >= T_Al else float(elem[2])
        else:
            T_Al = 4 - float(elem[1]) if float(elem[2]) != 0 else 0
            T_Al = T_Al if float(elem[2]) >= T_Al else float(elem[2])
    if len(elem) == 0:
        O_Al = 0
    elif (float(elem[2]) > T_Al + 1e-3):
        O_Al = float(elem[2]) - T_Al
    else:
        T_Al = float(elem[2])
        O_Al = 0

    if len(elem) == 0:
        O_FeIII = 0
        T_FeIII = 0
    elif float(elem[3]) >= 2:
        O_FeIII = float(elem[3])*0.5
        T_FeIII = float(elem[3]) - O_FeIII
    else:
        O_FeIII = float(elem[3])
        T_FeIII = float(elem[3]) - O_FeIII
    O_FeII = 0 if len(elem) == 0 else float(elem[4])

    I_K = 0 if len(elem) == 0 else float(elem[6])
    I_Na = 0 if len(elem) == 0 else float(elem[7])
    I_Ca = 0 if len(elem) == 0 else float(elem[8])
    I_H3O = float(elem[10]) if len(elem) > 10 else  0 
    if len(elem) == 0:
        I_Mg = 0; I_Li = 0
        O_Mg = 0; O_Li = 0
    else:
        if ('montmorillonite_lc' in name.lower()) or ('saponite' in name.lower()) or ('nontronite' in name.lower()) or ('beidellite' in name.lower()):
            Tot_Oxy = 0.17
        elif 'montmorillonite_hc' in name.lower():
            Tot_Oxy = 0.3
        elif ('illite' in name.lower()) or ('vermiculite' in name.lower()):
            Tot_Oxy = 0.43
        else:
            Tot_Oxy = 0.0
        Calc_Oxy = (I_K + I_Na + float(elem[9]))*0.5 + I_Ca
        if Calc_Oxy == 0:
            I_Mg = Tot_Oxy if float(elem[5]) != 0 else 0
            I_Li = Tot_Oxy if float(elem[9]) != 0 else 0
        else:
            I_Mg = 0; I_Li = 0
        I_Mg = Int_Mg_fract*float(elem[5]) if Int_Mg_fract is not None else I_Mg
        I_Li = Int_Li_fract*float(elem[9]) if Int_Li_fract is not None else I_Li
        O_Mg = float(elem[5]) - I_Mg
        O_Li = float(elem[9]) - I_Li
    TK = convert_temperature( TC, Out_Unit = 'K' )


    Interlayer = {'Tot' : {'Cs+' : 0, 'Rb+' : 0, 'K+' : I_K, 'Na+' : I_Na, 'Li+' : I_Li,
                           'H3O+' : I_H3O, 'NH4+' : 0, 'Mn2+' : 0.0, 'Fe2+' : 0, 'Co2+' : 0,
                           'Cu2+' : 0, 'Cd2+' : 0, 'Zn2+' : 0, 'Ba2+' : 0, 'Sr2+' : 0,
                           'Ca2+' : I_Ca, 'Mg2+' : I_Mg}}
    Octahedral = {'Tot' : {'Li+' : O_Li, 'Mg2+': O_Mg, 'Fe2+' : O_FeII, 'Mn2+' : 0,
                           'Ni2+' : 0, 'Co2+' : 0, 'Zn2+' : 0, 'Cd2+' : 0,
                           'VO2+' : 0, 'Al3+' : O_Al, 'Fe3+' : O_FeIII, 'V3+' : 0,
                           'Cr3+' : 0, 'Mn3+' : 0, 'Ti4+' : 0.}}
    Tetrahedral = {'Tot' : {'Si4+' : T_Si, 'Al3+': T_Al, 'Fe3+' : T_FeIII}}
    # initialize site occupancy
    for k  in ['M1','M2']:
        Octahedral[k] = {j : 0 for j in Octahedral['Tot']}
    for k in ['T1','T2']:
        Tetrahedral[k] = {j : 0 for j in Tetrahedral['Tot']}
    Brucitic = {}
    for k in ['M3','M4']:
        Brucitic[k] = {j : 0 for j in Octahedral['Tot']}
    # Mixing constants:
    K = { 'Inter' : -0.856571, 'M2' : -0.579046, 'M3' : -0.107956}
    # Entropy of the elements (CODATA)
    S_elem = {'Si' : 18.81, 'O2' : 205.152, 'H2' : 130.68, 'Al' : 28.3, 'Mg' : 32.67, 'K' : 64.68,
              'Na' : 51.3, 'Ca' : 41.59, 'Fe' : 27.32, 'Li' : 29.12, 'Mn' : 32.01, 'Ni' : 29.87,
              'Co' : 30.04, 'Cs' : 85.23, 'Rb' : 76.78, 'Ba' : 62.48, 'Sr' : 55.69, 'Cu' : 33.15,
              'Cd' : 51.8, 'Zn' : 41.72, 'N2' : 191.6, 'V' : 28.94, 'Cr' : 23.62, 'Ti' : 30.72,
              'B' : 5.9, 'Be' : 9.5}
    # Entropy Configuration for Magnetic spin
    R = 8.31451 #J K​−1 mol−1
    S_spin = {'Sc3+' : 0.00, 'Ti3+' : 1/2, 'Ti4+' : 0.00, 'V3+' : 1, 'Cr3+' : 3/2, 'Mn2+' : 5/2,
              'Mn3+' : 2, 'Fe2+' : 2, 'Fe3+' : 5/2, 'Ni2+' : 1, 'Co2+' : 3/2} # spin quantum number
    S_spin = {i: R*np.log(2*x + 1) for i,x in S_spin.items()} # R*ln(2S+1)    (J/K/mole)
    # Slat, V, Cp, a, b, c for oxides in specific sites
    Tetrahedral['Slat'] = {'SiO2' : 35.94, 'Al2O3': 29.42, 'Fe2O3' : 66.62}
    Tetrahedral['V'] = {'SiO2' : 25.7, 'Al2O3': 46.72, 'Fe2O3' : 27.29}
    Tetrahedral['Cp'] = {'SiO2' : 47.61, 'Al2O3': 80.91, 'Fe2O3' : 101.33}
    Tetrahedral['a'] = {'SiO2' : 14.99, 'Al2O3': -93.35, 'Fe2O3' : 0}
    Tetrahedral['b'] = {'SiO2' : 44, 'Al2O3': 177.61, 'Fe2O3' : 0}
    Tetrahedral['c'] = {'SiO2' : 17.33, 'Al2O3': 107.83, 'Fe2O3' : 0}

    Octahedral['Slat'] = {'Li2O' : 40.8, 'LiOH' : 45.04, 'MgO' : 27.89, 'Mg(OH)2' : 61.12,
                          'FeO' : 55.74, 'Fe(OH)2' : 61.9, 'Al2O3' : 55.02, 'Al(OH)3' : 79.37,
                          'Fe2O3' : 0, 'Fe(OH)3' : 178.75, 'MnO' : 57.15, 'Mn(OH)2' : 81.74,
                          'Cr2O3' : 56.3, 'Cr(OH)3' : 85.95, 'NiO' : 33.03, 'Ni(OH)2' : 42.59,
                          'CoO' : 48.6, 'Co(OH)2' : 91.10, 'ZnO' : 39.79, 'Zn(OH)2' : 79.65,
                          'CdO' : 52.23, 'TiO2' : 44.36}
    Octahedral['V'] = {'Li2O' : 4.26, 'LiOH' : 9.51, 'MgO' : 4.57, 'Mg(OH)2' : 25.91, 'FeO' : 10.59,
                       'Fe(OH)2' : 21.61, 'Al2O3' : 4.91, 'Al(OH)3' : 34.96, 'Fe2O3' : 14.23,
                       'Fe(OH)3' : 24.98, 'MnO' : 10.72, 'Mn(OH)2' : 21.29, 'Cr2O3' : 29.55,
                       'Cr(OH)3' : 27.96, 'NiO' : 7.01, 'Ni(OH)2' : 15, 'CoO' : 9.95,
                       'Co(OH)2' : 19.65, 'ZnO' : 8.65, 'Zn(OH)2' : 23.5, 'CdO' : 13.11, 'TiO2' : 15.24}
    Octahedral['Cp'] = {'Li2O' : 47.48, 'LiOH' : 45.38, 'MgO' : 30.84, 'Mg(OH)2' : 72.19, 'FeO' : 42.35,
                        'Fe(OH)2' : 80.39, 'Al2O3' : 74.89, 'Al(OH)3' : 89.63, 'Fe2O3' : 104.41,
                        'Fe(OH)3' : 103.01, 'MnO' : 42.52, 'Mn(OH)2' : 83.87, 'Cr2O3' : 120.76,
                        'Cr(OH)3' : 111.185, 'NiO' : 45.7, 'Ni(OH)2' : 116.19, 'CoO' : 42.35,
                        'Co(OH)2' : 83.7, 'ZnO' : 36.72, 'Zn(OH)2' : 65.76, 'CdO' : 41.95, 'TiO2' : 51.75}
    Octahedral['a'] = {'Li2O' : 0, 'LiOH' : 0, 'MgO' : 131.03, 'Mg(OH)2' : 71.47, 'FeO' : 141.77,
                       'Fe(OH)2' : 59.74, 'Al2O3' : 299.02, 'Al(OH)3' : 111.51, 'Fe2O3' : 221.92,
                       'Fe(OH)3' : 127.36, 'MnO' : 0, 'Mn(OH)2' : 0, 'Cr2O3' : 0, 'Cr(OH)3' : 0,
                       'NiO' : 0, 'Ni(OH)2' : 0, 'CoO' : 0, 'Co(OH)2' : 0, 'ZnO' : 0, 'Zn(OH)2' : 0,
                       'CdO' : 0, 'TiO2' : 0}
    Octahedral['b'] =  {'Li2O' : 0, 'LiOH' : 0, 'MgO' : -66.740, 'Mg(OH)2' : 66.540, 'FeO' : -64.550,
                         'Fe(OH)2' : 89.87, 'Al2O3' : -100.59, 'Al(OH)3' : 77.25, 'Fe2O3' : -515.68,
                         'Fe(OH)3' : 671.46, 'MnO' : 0, 'Mn(OH)2' : 0, 'Cr2O3' : 0, 'Cr(OH)3' : 0,
                         'NiO' : 0, 'Ni(OH)2' : 0, 'CoO' : 0, 'Co(OH)2' : 0, 'ZnO' : 0, 'Zn(OH)2' : 0,
                         'CdO' : 0, 'TiO2' : 0}
    Octahedral['c'] =  { 'Li2O' : 0, 'LiOH' : 0, 'MgO' : -71.38, 'Mg(OH)2' : -16.99, 'FeO' : -71.27,
                       'Fe(OH)2' : -5.46, 'Al2O3' : -172.58, 'Al(OH)3' : -39.92, 'Fe2O3' : 32.22,
                       'Fe(OH)3' : -199.61, 'MnO' : 0, 'Mn(OH)2' : 0, 'Cr2O3' : 0, 'Cr(OH)3' : 0,
                       'NiO' : 0, 'Ni(OH)2' : 0, 'CoO' : 0, 'Co(OH)2' : 0, 'ZnO' : 0, 'Zn(OH)2' : 0,
                       'CdO' : 0, 'TiO2' : 0}

    Interlayer['Slat'] = {'Cs2O' : 226.01, 'Rb2O' : 204.83,	'K2O' : 157.70,	'Na2O' : 186.15, 'Li2O' : 131.43,
                          'BaO' : 171.12, 'SrO' : 157.1, 'CaO' : 133.08, 'MgO' : 136.99, 'CuO' : 150.06,
                          'CoO' : 162.43, 'NiO' : 148.05, 'ZnO' : 152.54, 'H2O' : 169.65, '(NH4)2O' : 364.5,
                          'CdO' : 160.85}
    Interlayer['V'] = {'Cs2O' : 62.25, 'Rb2O' : 46.40, 'K2O' : 27.26, 'Na2O' : 22.97, 'Li2O' : 4.26,
                       'BaO' : 25.92, 'SrO' : 20.19, 'CaO' : 32.47,	'MgO' : 8.97, 'CuO' : 5.19,	'CoO' : 9.95,
                       'NiO' : 7.01, 'ZnO' : 8.65, 'H2O' : 14.85, '(NH4)2O' : 38.16, 'CdO' : 13.11}
    Interlayer['Cp'] = {'Cs2O' : 77.12,	'Rb2O' : 73.99,	'K2O' : 74.50,	'Na2O' : 70.20,	'Li2O' : 47.48,
                        'BaO' : 47.38,	'SrO' : 44.9,	'CaO' : 42.43,	'MgO' : 35.59,	'CuO' : 37.67,
                        'CoO' : 42.35,	'NiO' : 45.7,	'ZnO' : 36.72,	'H2O' : 74.23,	'(NH4)2O' : 247.63,
                        'CdO' : 41.95}
    Interlayer['a'] = {'Cs2O' : 0,	'Rb2O' : 0,	'K2O' : 148.56,	'Na2O': 43.27,	'Li2O' : 0,	'BaO' : 0,
                       'SrO' : 0,	'CaO' : 63.88,	'MgO' : 0,	'CuO' : 0,	'CoO' : 0,	'NiO' : 0,
                       'ZnO' : 0,	'H2O' : 0,	'(NH4)2O' : 0,	'CdO' : 0}
    Interlayer['b'] = {'Cs2O' : 0,	'Rb2O' : 0,	'K2O' : 24.73,	'Na2O': 395.84,	'Li2O' : 0,	'BaO' : 0,
                       'SrO' : 0,	'CaO' : 315.36,	'MgO' : 0,	'CuO' : 0,	'CoO' : 0,	'NiO' : 0,
                       'ZnO' : 0,	'H2O' : 0,	'(NH4)2O' : 0,	'CdO' : 0}
    Interlayer['c'] = {'Cs2O' : 0,	'Rb2O' : 0,	'K2O' : -72.39,	'Na2O': -80.98,	'Li2O' : 0,	'BaO' : 0,
                       'SrO' : 0,	'CaO' : -102.65,	'MgO' : 0,	'CuO' : 0,	'CoO' : 0,	'NiO' : 0,
                       'ZnO' : 0,	'H2O' : 0,	'(NH4)2O' : 0,	'CdO' : 0}
    # Enthalpy of formation of Oxides
    dH = {'Li2O' : -597.90, 'Na2O' : -414.80, 'K2O' : -363.17, 'Rb2O' : -339,
          'Cs2O' : -345.73, '(NH4)2O' : -234.30,  '(H3O)2O' : -857.49, 'BeO' : -609.40,
          'MgO' : -601.60, 'CaO' : -634.92, 'SrO' : -591.3, 'BaO' : -548.1, 'FeO' : -272.04,
          'MnO' : -385.2, 'CuO' : -156.1, 'CoO' : -237.9, 'NiO' : -239.3, 'CdO' : -258.4,
          'ZnO' : -350.5, 'Fe2O3' : -826.23, 'Al2O3' : -1675.70, 'B2O3' : -1273.5,
          'V2O3' : -1218.8, 'Cr2O3' : -1053.1, 'Mn2O3' : -959, 'SiO2' : -910.70,
          'TiO2' : -944, '(VO2)2O' : -1550.59, 'H2O' : -285.83}
    # Enthalpy of formation for elements in specific sites:
    Interlayer['dH'] = {'Cs+' : 544.22, 'Rb+' : 522.89, 'K+' : 453.0, 'Na+' : 260.0,
                        'Li+' : 14.2, 'H3O+' : -312.730, 'NH4+' : 171.84857190,
                        'Mn2+' : -189.180, 'Fe2+' : -211.8386339, 'Co2+' : -208.9244064,
                        'Cu2+' : -256.2185226, 'Cd2+' : -212.38346050, 'Zn2+' : -222.8680592,
                        'Ba2+' : 70.57, 'Sr2+' : 15.350, 'Ca2+' : -71.23, 'Mg2+' : -147.250,
                        'H2O' : -249.576624132357}
    Octahedral['dH'] = {'Li+' : -110.00, 'Mg2+': -191.72, 'Fe2+' : -230.790, 'Mn2+' : -218.940,
                        'Ni2+' : -237.50, 'Co2+' : -232.590, 'Zn2+' : -242.780,
                        'Cd2+' : -235.07550080,  'VO2+' : -296.25, 'Al3+' : -251.750,
                        'Fe3+' : -290.79, 'V3+' : -280.45, 'Cr3+' : -243.610,
                        'Mn3+' : -281.08, 'Ti4+' : -291.05}
    Brucitic['dH'] = {'Li+' : 66.34, 'Mg2+': -88.98, 'Fe2+' : -216.99, 'Mn2+' : -159.60,
                      'Ni2+' : -197.67, 'Co2+' : -187.60, 'Zn2+' : -208.49,
                      'Cd2+' : -192.6891279,  'VO2+' : -318.16, 'Al3+' : -229.05,
                      'Fe3+' : -288.99, 'V3+' : -285.76,  'Cr3+' : -210.19, 'Mn3+' : -287.05,
                      'Ti4+' : -307.49, 'H2O' : -311.976483069821 }
    Tetrahedral['dH'] = {'Si4+' : -285.33, 'Al3+': -260.450, 'Fe3+' : -310.0}

    charge = {'Mn2+' : 2, 'Fe2+' : 2, 'Co2+' : 2, 'Cu2+' : 2, 'Cd2+' : 2, 'V3+' : 3,
              'Zn2+' : 2, 'Ba2+' : 2, 'Sr2+' : 2, 'Ca2+' : 2, 'Mg2+' : 2, 'Fe3+' : 3,
              'Na+' : 1, 'Li+' : 1, 'Cs+' : 1, 'Rb+' : 1, 'K+' : 1, 'Cr3+' : 3,
              'Mn3+' : 3, 'Ti4+' : 4, 'VO2+' : 1, 'Al3+': 3, 'Si4+' : 4,
              'H3O+' : 1, 'NH4+' : 1, 'Ni2+' : 2}

    nCs = Interlayer['Tot']['Cs+']
    nRb = Interlayer['Tot']['Rb+']
    nK = Interlayer['Tot']['K+']
    nNa = Interlayer['Tot']['Na+']
    nCa = Interlayer['Tot']['Ca2+']
    nH3O = Interlayer['Tot']['H3O+']
    nNi = Octahedral['Tot']['Ni2+']
    nTi = Octahedral['Tot']['Ti4+']; nCr = Octahedral['Tot']['Cr3+']
    nV = Octahedral['Tot']['V3+']; nVO = Octahedral['Tot']['VO2+']
    nLi = Interlayer['Tot']['Li+'] + Octahedral['Tot']['Li+']
    nMg = Interlayer['Tot']['Mg2+'] + Octahedral['Tot']['Mg2+']
    nFe = Interlayer['Tot']['Fe2+'] + Octahedral['Tot']['Fe2+']
    nZn = Interlayer['Tot']['Zn2+'] + Octahedral['Tot']['Zn2+']
    nMn = Interlayer['Tot']['Mn2+'] + Octahedral['Tot']['Mn2+']
    nCo = Interlayer['Tot']['Co2+'] + Octahedral['Tot']['Co2+']
    nCd = Interlayer['Tot']['Cd2+'] + Octahedral['Tot']['Cd2+']
    nAl = Tetrahedral['Tot']['Al3+'] + Octahedral['Tot']['Al3+']
    nFe3 = Tetrahedral['Tot']['Fe3+'] + Octahedral['Tot']['Fe3+']
    nSi = Tetrahedral['Tot']['Si4+']

    nFeII = Octahedral['Tot']['Fe2+']
    if group == '10A':
        nAlIV = 4 - nSi
        if nAl > (4 - nSi):
            nAlVI = nAl - nAlIV
        else:
            nAlVI = 0
        nFeIII = nFe3 - np.sum([Tetrahedral[j]['Fe3+']
                               for j in Tetrahedral if j in ['T1', 'T2']])
    elif group == '7A':
        nAlIV = 2 - nSi - np.sum([Tetrahedral[j]['Fe3+']
                                  for j in Tetrahedral if j in ['T1', 'T2']])
        if nAl > (2 - nSi):
            nAlVI = nAl - nAlIV
        else:
            nAlVI = 0
        nFeIII = nFe3 - np.sum([Tetrahedral[j]['Fe3+']
                               for j in Tetrahedral if j in ['T1', 'T2']])
    else:
        nAlIV = 4 - nSi
        if nAl > (4 - nSi):
            nAlVI = nAl - nAlIV
        else:
            nAlVI = 0
        nFeIII = nFe3 - np.sum([Tetrahedral[j]['Fe3+']
                               for j in Tetrahedral if j in ['T1', 'T2']])
    # followed the guidelines after ref (3)
    if cation_order is None:
        if group == '10A' and nAlIV < 0.4:
            cation_order = 'Random'
        elif nAlIV > 1.3:
            cation_order = 'Ordered'
        else:
            cation_order = 'HDC'
    else:
        cation_order = cation_order

    NbO = np.sum( [Octahedral['Tot'][j] for j in Octahedral['Tot']])
    NbO_tri = np.sum([ Octahedral['Tot'][j]
                      for j in list(Octahedral['Tot'].keys())[:9]])
    nbDI = 2/NbO if NbO >= 2 else 1
    if group in ['7A', '10A']:
        if NbO < 2.33:
            TRI = 0
        else:
            TRI = 1
    else:
        TRI = (6 - NbO)/6
    Test_east = 1 if cation_order.title() == 'Eastonite' else 0
    Interlayer['Tot_Remainder'] = 1 - np.sum([Interlayer['Tot'][k]
                                              for k in Interlayer['Tot']])
    # Tetrahedral T1 and T2 site configuration
    for k in list(Tetrahedral['Tot'].keys()):
        if cation_order.title() not in ['Ordered', 'Eastonite']:
            if group == '7A':
                Tetrahedral['T1'][k] = Tetrahedral['Tot'][k]*0.5
                Tetrahedral['T2'][k] = Tetrahedral['Tot'][k] - Tetrahedral['T1'][k]
            else:
                Tetrahedral['T1'][k] = Tetrahedral['Tot'][k]*0.5
                Tetrahedral['T2'][k] = Tetrahedral['Tot'][k] - Tetrahedral['T1'][k]
        else:
            if group == '7A':
                if k == 'Si4+':
                    if Tetrahedral['Tot'][k] < 1:
                        Tetrahedral['T1'][k] = Tetrahedral['Tot'][k]
                    else:
                        Tetrahedral['T1'][k] = 1
                    Tetrahedral['T2'][k] = Tetrahedral['Tot'][k] - Tetrahedral['T1'][k]
                else:
                    if Tetrahedral['Tot'][k] < 1:
                        Tetrahedral['T2'][k] = Tetrahedral['Tot'][k]
                    else:
                        Tetrahedral['T2'][k] = 1
                    Tetrahedral['T1'][k] = Tetrahedral['Tot'][k] - Tetrahedral['T2'][k]
            else:
                if k == 'Si4+':
                    if Tetrahedral['Tot'][k] < 2:
                        Tetrahedral['T1'][k] = Tetrahedral['Tot'][k]
                    else:
                        Tetrahedral['T1'][k] = 2
                    Tetrahedral['T2'][k] = Tetrahedral['Tot'][k] - Tetrahedral['T1'][k]
                else:
                    if Tetrahedral['Tot'][k] < 2:
                        Tetrahedral['T2'][k] = Tetrahedral['Tot'][k]
                    else:
                        Tetrahedral['T2'][k] = 2
                    Tetrahedral['T1'][k] = Tetrahedral['Tot'][k] - Tetrahedral['T2'][k]

    if ClayMintype.title() == 'Smectite' or ClayMintype.title() not in ['Chlorite', 'Mica']:
        # Brucitic M4 site configuration
        for k in np.sort(list(Octahedral['Tot'].keys())):
            if group in ['7A', '10A']:
                Brucitic['M4'][k] = 0
            else:
                if Octahedral['Tot']['Al3+'] < 1:
                    if k != 'Al3+':
                        Brucitic['M4'][k] = Octahedral['Tot'][k]*\
                            (1 - Octahedral['Tot']['Al3+'])/(NbO - Brucitic['M4']['Al3+'])
                    else:
                        Brucitic['M4'][k] = Octahedral['Tot']['Al3+']
                else:
                    if k != 'Al3+':
                        Brucitic['M4'][k] = 0
                    else:
                        Brucitic['M4'][k] = 1

        NbO_tri1 = NbO_tri - np.sum([Brucitic['M4'][j] for j in Brucitic['M4'] if j != 'Al3+'])
        # Brucitic M3 site configuration for first 9 ions
        for k in list(Octahedral['Tot'].keys())[:9]:
            if group in ['7A', '10A']:
                Brucitic['M3'][k] = 0
            else:
                if NbO_tri1 >= 4:
                    Brucitic['M3'][k] = Octahedral['Tot'][k]*2/NbO_tri
                else:
                    Brucitic['M3'][k] = Octahedral['Tot'][k]*NbO_tri1/2/NbO_tri

        # Octahedral M2 site configuration for first 8 ions
        for k in list(Octahedral['Tot'].keys())[:8]:
            if group in ['7A', '10A']:
                if TRI == 0:
                    Octahedral['M2'][k] = Octahedral['Tot'][k]*nbDI
                else:
                    if Test_east == 1:
                        if Octahedral['Tot']['Al3+'] > 1:
                            Octahedral['M1']['Al3+'] = 1
                        else:
                            Octahedral['M1']['Al3+'] = Octahedral['Tot']['Al3+']
                        Octahedral['M2'][k] = Octahedral['Tot'][k]*2/(2 + (1 - Octahedral['M1']['Al3+']))
                    else:
                        Octahedral['M2'][k] = Octahedral['Tot'][k]*2/NbO
            else:
                if NbO_tri1 >= 4:
                    Octahedral['M2'][k] = Octahedral['Tot'][k]*2/NbO_tri
                else:
                    Octahedral['M2'][k] = Octahedral['Tot'][k]*NbO_tri1/2/NbO_tri

        NbOdi_M2M3 = 4 - np.sum([Brucitic['M3'][j] for j in list(Octahedral['Tot'].keys())[:9]
                                 if j != 'Cd2+'] +  [Octahedral['M2'][j]
                                                     for j in list(Octahedral['Tot'].keys())[:7]])

        # Brucitic M3 configuration for last ions
        for k in list(Octahedral['Tot'].keys())[9:]:
            if group in ['7A', '10A']:
                Brucitic['M3'][k] = 0
            else:
                if NbOdi_M2M3 >= 0:
                    Brucitic['M3'][k] = (Octahedral['Tot'][k] - Brucitic['M4'][k])* \
                        NbOdi_M2M3/(NbO - 1)
                else:
                    Brucitic['M3'][k] = 0

        # Octahedral M2 configuration for last ions
        for k in list(Octahedral['Tot'].keys())[8:]:
            if group in ['7A', '10A']:
                if TRI == 0:
                    Octahedral['M2'][k] = Octahedral['Tot'][k]*nbDI
                else:
                    if Test_east == 1:
                        if k != 'Al3+':
                            Octahedral['M2'][k] = Octahedral['Tot'][k]*2/(2 + (1 - Octahedral['M1']['Al3+']))
                        else:
                            if Octahedral['Tot'][k] > 1:
                                Octahedral['M1'][k] = Octahedral['Tot'][k] - Octahedral['M1']['Al3+']
                            else:
                                Octahedral['M1'][k] = 0
                    else:
                        Octahedral['M2'][k] = Octahedral['Tot'][k]*2/NbO
            else:
                if NbOdi_M2M3 >= 0:
                    Octahedral['M2'][k] = (Octahedral['Tot'][k] - Brucitic['M4'][k])* \
                        NbOdi_M2M3/(NbO - 1)
                else:
                    Octahedral['M2'][k] = 0

        # Octahedral M1 site configuration
        for k in list(Octahedral['Tot'].keys()):
            if k != 'Al3+':
                if group in ['7A', '10A']:
                    Octahedral['M1'][k] = Octahedral['Tot'][k] - Octahedral['M2'][k]
                else:
                    Octahedral['M1'][k] = Octahedral['Tot'][k] - Octahedral['M2'][k] - \
                        Brucitic['M3'][k] - Brucitic['M4'][k]
            else:
                if group in ['7A', '10A']:
                    if TRI == 0:
                        Octahedral['M1'][k] = Octahedral['Tot'][k] - Octahedral['M2'][k]
                    else:
                        if Test_east == 1:
                            if Octahedral['Tot'][k] > 1:
                                Octahedral['M1'][k] = 1
                            else:
                                Octahedral['M1'][k] = Octahedral['Tot'][k]
                        else:
                            Octahedral['M1'][k] = Octahedral['Tot'][k] - Octahedral['M2'][k]
                else:
                    Octahedral['M1'][k] = Octahedral['Tot'][k] - Octahedral['M2'][k] - \
                        Brucitic['M3'][k] - Brucitic['M4'][k]

    elif ClayMintype.title() in ['Chlorite', 'Mica']:
        for k in list(Octahedral['Tot'].keys()):
            if group == '14A':
                if k == 'Al3+':
                    Octahedral['M1'][k] = (Octahedral['Tot'][k] + Tetrahedral['Tot'][k])/5
                    Octahedral['M2'][k] = (Octahedral['Tot'][k] + Tetrahedral['Tot'][k])*2/5
                    Brucitic['M3'][k] = (Octahedral['Tot'][k] + Tetrahedral['Tot'][k])*2/5
                    Brucitic['M4'][k] = 1
                elif k == 'Fe3+':
                    Octahedral['M1'][k] = (Octahedral['Tot'][k] + Tetrahedral['Tot'][k])/5
                    Octahedral['M2'][k] = (Octahedral['Tot'][k] + Tetrahedral['Tot'][k])*2/5
                    Brucitic['M3'][k] = (Octahedral['Tot'][k] + Tetrahedral['Tot'][k])*2/5
                    Brucitic['M4'][k] = 0
                else:
                    Octahedral['M1'][k] = Octahedral['Tot'][k]/5
                    Octahedral['M2'][k] = Octahedral['Tot'][k]*2/5
                    Brucitic['M3'][k] = Octahedral['Tot'][k]*2/5
                    Brucitic['M4'][k] = 0
            else:
                if k in ['Al3+', 'Fe3+']:
                    Octahedral['M1'][k] = (Octahedral['Tot'][k] + Tetrahedral['Tot'][k])/3
                    Octahedral['M2'][k] = (Octahedral['Tot'][k] + Tetrahedral['Tot'][k])*2/3
                    Brucitic['M3'][k] = 0
                    Brucitic['M4'][k] = 0
                else:
                    Octahedral['M1'][k] = Octahedral['Tot'][k]/3
                    Octahedral['M2'][k] = Octahedral['Tot'][k]*2/3
                    Brucitic['M3'][k] = 0
                    Brucitic['M4'][k] = 0

    Octahedral['M1_Remainder'] = 1 - np.sum([Octahedral['M1'][k] for k in Octahedral['M1']])


    Calc = {'Total_sites' : {}, 'XlnX' : {}, 'Nb_Oxy' : {}, 'DO_moy' : {}}
    Calc['DO_moy']['H_i'] =  Interlayer['dH']['H2O']
    Calc['DO_moy']['H_b'] =  Brucitic['dH']['H2O']
    Calc['DO_moy']['H_ext'] =  -287.20
    if group == '7A':
        Oxy = 9
        OH = 4
        Calc['Nb_Oxy']['H_i'] = 0.5
        Calc['Nb_Oxy']['H_b'] = 0
        Calc['Nb_Oxy']['H_ext'] = 1.5
    elif group == '10A':
        Oxy = 12
        OH = 2
        Calc['Nb_Oxy']['H_i'] = 1
        Calc['Nb_Oxy']['H_b'] = 0
        Calc['Nb_Oxy']['H_ext'] = 0
    else:
        Oxy = 18
        OH = 8
        Calc['Nb_Oxy']['H_i'] = 1
        Calc['Nb_Oxy']['H_b'] = 3
        Calc['Nb_Oxy']['H_ext'] = 0

    Calc['Nb_Oxy']['Inter'] = np.sum([0.5*Interlayer['Tot'][j]*charge[j]
                                      for j in Interlayer['Tot'] if j != 'NH4+'])
    for j, k in zip(['T1', 'T2', 'M1', 'M2', 'M3', 'M4'],
                    [Tetrahedral['T1'], Tetrahedral['T2'], Octahedral['M1'],
                     Octahedral['M2'], Brucitic['M3'], Brucitic['M4']]):
        i = '%s' % j
        Calc['Total_sites'][i] = np.sum([k[j] for j in k])
        Calc['Nb_Oxy'][i] = np.sum([0.5*k[j]*charge[j] for j in k ])

    for i, k  in zip(['Inter', 'M1', 'M2', 'M3', 'M4', 'T1', 'T2'],
                  [Interlayer, Octahedral, Octahedral, Brucitic, Brucitic,
                   Tetrahedral, Tetrahedral]):
        if i == 'Inter':
            a = 'Tot'
            summInt = np.sum([k[a][j] if k[a][j] != 0 else 1e-11 for j in k[a]]) + k['Tot_Remainder']
            X = [k[a][j]/summInt if k[a][j] != 0 else 1e-11/summInt for j in k[a]]
            X.extend([k['Tot_Remainder']/summInt, (summInt - k['Tot_Remainder'])/summInt])

        else:
            a = '%s' % i
            summ = np.sum([k[a][j] if k[a][j] != 0 else 1e-11 for j in k[a]])
            X = [k[a][j]/summ if k[a][j] != 0 else 1e-11/summ for j in k[a]]
            if i == 'M1':
                X = [k[a][j] if k[a][j] != 0 else 1e-11 for j in k[a]] 
                X.append(k['M1_Remainder'])

        lnX = [np.log(j) if j > 0 else 0 for j in X]
        if (group != '14A')&(i in ['M3', 'M4']):
            Calc['XlnX'][i] = 0
        elif (Octahedral['M1_Remainder'] == 0)&(i == 'M1'):
            Calc['XlnX'][i] = 0
        elif i == 'Inter':
            condition1 = (group == '10A')
            condition2 = ((summInt - Interlayer['Tot_Remainder']) < 0.66)
            condition3 = (np.sum([Interlayer['Tot'][j]*charge[j] 
                                  for j in Interlayer['Tot'] if j in ['K+', 'Na+', 'Ca2+']])>0.5*(summInt - Interlayer['Tot_Remainder']))
            condition4 = (np.sum([Interlayer['Tot'][j]*charge[j] 
                                  for j in Interlayer['Tot'] if j in ['Mg2+', 'Ca2+']])>0.5*(summInt - Interlayer['Tot_Remainder']))
            if condition1 & condition2 & condition3:
                Calc['XlnX'][i] = lnX[-1]*X[-1] + lnX[-2]*X[-2]
            else:
                Calc['XlnX'][i] = np.sum([lnX[j]*X[j] if X[j]*summInt != summInt else 0 for j in range(len(X)-1)])
        elif i in ['M1', 'M2', 'M3', 'M4']:
            Calc['XlnX'][i] = np.sum([lnX[j]*X[j] if X[j]*summ != summ else 0 for j in range(len(X))])
        else:
            Calc['XlnX'][i] = np.sum([lnX[j]*X[j] for j in range(len(X))])


    for i, k  in zip(['Inter', 'M1', 'M2', 'M3', 'M4', 'T1', 'T2'],
                  [Interlayer, Octahedral, Octahedral, Brucitic, Brucitic,
                   Tetrahedral, Tetrahedral]):
        if i == 'Inter':
            a = 'Tot'
        else:
            a = '%s' % i
        k['dH_%s' % i] = {j : 0 for j in ['moy'] + list(k[a]) }
        if Calc['Nb_Oxy'][i] == 0:
            k['dH_%s' % i]['moy'] = 0
        else:
            k['dH_%s' % i]['moy'] = np.sum([0.5*k[a][j]*charge[j]*k['dH'][j]
                                            for j in k[a]])/Calc['Nb_Oxy'][i]
        c = []
        for b in list(k['dH_%s' % i].keys())[1:]:
            c = c + [b]
            k['dH_%s' % i][b] = np.sum([0.5*k[a][j]*charge[j]*0.5*k[a][b]*charge[b]*\
                                        np.abs(k['dH'][j] - k['dH'][b]) for j in k[a] if j not in c])

    for j, k in zip(['Inter', 'T1', 'T2', 'M1', 'M2', 'M3', 'M4'],
                    [Interlayer, Tetrahedral, Tetrahedral, Octahedral,
                     Octahedral, Brucitic, Brucitic]):
        i = '%s' % j
        if j in ['M1', 'M4', 'T1', 'T2']:
            Calc['DO_moy'][i] = k['dH_%s' % j]['moy']
        else:
            if Calc['Nb_Oxy'][i] == 0:
                Calc['DO_moy'][i] = 0
            else:
                Calc['DO_moy'][i] = k['dH_%s' % j]['moy'] + K[j]*\
                    np.sum(list(k['dH_%s' % j].values())[1:])/Calc['Nb_Oxy'][i]**2

    dHoxphtl = -(np.sum([Calc['Nb_Oxy'][k]*Calc['Nb_Oxy'][j]*abs(Calc['DO_moy'][k]-Calc['DO_moy'][j])
                        for j in ['T1', 'T2'] for k in ['Inter', 'M1', 'M2']] + \
                       [Calc['Nb_Oxy'][k]*Calc['Nb_Oxy'][j]*abs(Calc['DO_moy'][k]-Calc['DO_moy'][j])
                        for j in ['H_i'] for k in ['M1', 'M2']] + \
                           [Calc['Nb_Oxy'][k]*Calc['Nb_Oxy'][j]*abs(Calc['DO_moy'][k]-Calc['DO_moy'][j])
                            for j in ['M1'] for k in ['M2']] + \
                               [Calc['Nb_Oxy'][k]*Calc['Nb_Oxy'][j]*abs(Calc['DO_moy'][k]-Calc['DO_moy'][j])
                                for j in ['T1'] for k in ['T2']] + \
                                   [Calc['Nb_Oxy'][k]*Calc['Nb_Oxy'][j]*abs(Calc['DO_moy'][k]-Calc['DO_moy'][j])
                                    for j in ['H_b'] for k in ['M3', 'M4']] +\
                                       [Calc['Nb_Oxy'][k]*Calc['Nb_Oxy'][j]*abs(Calc['DO_moy'][k]-Calc['DO_moy'][j])
                                        for j in ['M4'] for k in ['M3']] +\
                                           [Calc['Nb_Oxy'][k]*Calc['Nb_Oxy'][j]*abs(Calc['DO_moy'][k]-Calc['DO_moy'][j])
                                            for j in ['H_b'] for k in ['T1', 'T2']]) +\
                 np.sum([Calc['Nb_Oxy'][k]*Calc['Nb_Oxy'][j]*abs(Calc['DO_moy'][k]-Calc['DO_moy'][j])
                         for j in ['H_ext'] for k in ['M1', 'M2']] +\
                        [Calc['Nb_Oxy'][k]*Calc['Nb_Oxy'][j]*abs(Calc['DO_moy'][k]-Calc['DO_moy'][j])
                         for j in ['H_ext'] for k in ['T1', 'T2']]))/Oxy

    dHox = dHoxphtl - Calc['Nb_Oxy']['H_i']*(dH['H2O'] - Interlayer['dH']['H2O']) -\
        Calc['Nb_Oxy']['H_b']*(dH['H2O'] - Brucitic['dH']['H2O']) - \
            Calc['Nb_Oxy']['H_ext']*(dH['H2O'] - Calc['DO_moy']['H_ext'])

    dHf = dHox + np.sum([Calc['Nb_Oxy'][j] for j in list(Calc['Nb_Oxy'].keys())[:3]])*dH['H2O']
    for i, k in zip(['Tot', 'T1', 'T2', 'M1', 'M2', 'M3', 'M4'],
                    [Interlayer, Tetrahedral, Tetrahedral, Octahedral,
                     Octahedral, Brucitic, Brucitic]):
        dHf = dHf + np.sum([0.5*k[i][j]*dH['%s2O' % (j.rstrip('+'))]
                            if (charge[j] == 1 and j not in ['NH4+', 'H3O+', 'VO2+'])
                            else k[i][j]*dH['%sO' % (j.rstrip('0123456789.+ '))] if charge[j] == 2
                            else 0.5*k[i][j]*dH['(%s)2O' % j.rstrip('+')] if j in ['NH4+', 'H3O+', 'VO2+']
                            else k[i][j]*dH['%sO2' % j.rstrip('0123456789.+ ')] if j in ['Si4+', 'Ti4+']
                            else 0.5*k[i][j]*dH['%s2O%d' % (j.rstrip('0123456789.+ '), charge[j])]
                            for j in k[i] ])

    if group in ['7A', '10A']:
        R1 = ((O_Li + nVO + 2*(O_Mg + nFeII + Octahedral['Tot']['Mn2+'] + nNi + 
                               Octahedral['Tot']['Co2+'] + Octahedral['Tot']['Zn2+']) + 3*(nFeIII + nAlVI + nV))/OH - 1)

    else:
        R1 = (2*nMg/(8 - 3*nAlVI) + 2*nFeII/(8 - 3*nAlVI) + 3*nFeIII/(8 - 3*nAlVI) - 1)
        R2 = 2*nMg/(8 - 3 - 3*(nAlVI - 1)) + 2*nFeII/(8 - 3 - 3*(nAlVI - 1)) + \
            3*nFeIII/(8 - 3 - 3*(nAlVI - 1)) - 1
        R3 = 2*nMg/(8 - 3 - 2/3) + 2*nFeII/(8 - 3 - 2/3) + 3*nFeIII/(8 - 3 - 2/3) + \
            3*(nAlVI - 2)/(8 - 3 - 2/3) - 1
        Etape = {'M4':{}, 'M1':{}, 'M2_M3':{}, 'Mixed':{}}
        Etape['M4'] = {'Na2O' : 0.5*nNa, 'K2O' : 0.5*nK, 'CaO' : nCa, 'Fe(OH)3' : nFeIII/(R1 + 1),
                       'Mg(OH)2' : nMg/(R1 + 1), 'Fe(OH)2' : nFeII/(R1 + 1),
                       'Al(OH)3' : [nAlVI if nAlVI <= 1 else 0][0], 'LiOH' : nLi/(R1 + 1),
                       'Mn(OH)2' : nMn/(R1 + 1), 'Cr(OH)3' : nCr/(R1 + 1), 'Ni(OH)2' : nNi/(R1 + 1),
                       'Co(OH)2' : nCo/(R1 + 1), 'Zn(OH)2' : nZn/(R1 + 1),
                       'Al2O3_VI' : 0.5*(nAlVI - [nAlVI if nAlVI <= 1 else 0][0]),
                       'FeO_VI' : (nFeII - nFeII/(R1 + 1)), 'MgO_VI' : (nMg - nMg/(R1 + 1)),
                       'Fe2O3_VI' : 0.5*(nFeIII - nFeIII/(R1 + 1)), 'Li2O' : 0.5*(nLi - nLi/(R1 + 1)),
                       'MnO' : (nMn - nMn/(R1 + 1)), 'Cr2O3' : 0.5*(nCr - nCr/(R1 + 1)),
                       'NiO' : (nNi - nNi/(R1 + 1)), 'CoO' : (nCo - nCo/(R1 + 1)), 'ZnO' : (nZn - nZn/(R1 + 1)),
                       'TiO2' : 0, 'Al2O3_IV' : 0.5*nAlIV, 'SiO2_IV' : nSi}
        Etape['M1'] = {'Na2O' : 0.5*nNa, 'K2O' : 0.5*nK, 'CaO' : nCa, 'Fe(OH)3' : nFeIII/(R2 + 1),
                       'Mg(OH)2' : nMg/(R2 + 1), 'Fe(OH)2' : nFeII/(R2 + 1),
                       'Al(OH)3' : [nAlVI if nAlVI <= 2 else 0][0], 'LiOH' : nLi/(R2 + 1),
                       'Mn(OH)2' : nMn/(R2 + 1), 'Cr(OH)3' : nCr/(R2 + 1), 'Ni(OH)2' : nNi/(R2 + 1),
                       'Co(OH)2' : nCo/(R2 + 1), 'Zn(OH)2' : nZn/(R2 + 1),
                       'Al2O3_VI' : 0.5*(nAlVI - [nAlVI if nAlVI <= 2 else 0][0]),
                       'FeO_VI' : (nFeII - nFeII/(R2 + 1)), 'MgO_VI' : (nMg - nMg/(R2 + 1)),
                       'Fe2O3_VI' : 0.5*(nFeIII - nFeIII/(R2 + 1)), 'Li2O' : 0.5*(nLi - nLi/(R2 + 1)),
                       'MnO' : (nMn - nMn/(R2 + 1)), 'Cr2O3' : 0.5*(nCr - nCr/(R2 + 1)),
                       'NiO' : (nNi - nNi/(R2 + 1)), 'CoO' : (nCo - nCo/(R2 + 1)), 'ZnO' : (nZn - nZn/(R2 + 1)),
                       'TiO2' : 0, 'Al2O3_IV' : 0.5*nAlIV, 'SiO2_IV' : nSi}
        Etape['M2_M3'] = {'Na2O' : 0.5*nNa, 'K2O' : 0.5*nK, 'CaO' : nCa, 'Fe(OH)3' : nFeIII/(R3 + 1),
                       'Mg(OH)2' : nMg/(R3 + 1), 'Fe(OH)2' : nFeII/(R3 + 1),
                       'Al(OH)3' : ((8-3-2/3)-(3*nFeIII/(R3 + 1)+2*nMg/(R3 + 1)+2*nFeII/(R3 + 1)))/3+1+2/3/3,
                       'LiOH' : nLi/(R3 + 1), 'Mn(OH)2' : nMn/(R3 + 1), 'Cr(OH)3' : nCr/(R3 + 1),
                       'Ni(OH)2' : nNi/(R3 + 1), 'Co(OH)2' : nCo/(R3 + 1), 'Zn(OH)2' : nZn/(R3 + 1),
                       'Al2O3_VI' : 0.5*(nAlVI - (((8-3-2/3)-(3*nFeIII/(R3 + 1) +\
                                                              2*nMg/(R3 + 1)+2*nFeII/(R3 + 1)))/3+1+2/3/3)),
                       'FeO_VI' : (nFeII - nFeII/(R3 + 1)), 'MgO_VI' : (nMg - nMg/(R3 + 1)),
                       'Fe2O3_VI' : 0.5*(nFeIII - nFeIII/(R3 + 1)), 'Li2O' : 0.5*(nLi - nLi/(R3 + 1)),
                       'MnO' : (nMn - nMn/(R3 + 1)), 'Cr2O3' : 0.5*(nCr - nCr/(R3 + 1)),
                       'NiO' : (nNi - nNi/(R3 + 1)), 'CoO' : (nCo - nCo/(R3 + 1)), 'ZnO' : (nZn - nZn/(R3 + 1)),
                       'TiO2' : 0, 'Al2O3_IV' : 0.5*nAlIV, 'SiO2_IV' : nSi}
        for k in list(Etape['M1'].keys()):
            if k in ['Na2O', 'K2O', 'CaO', 'Al2O3_IV', 'SiO2_IV']:
                Etape['Mixed'][k] = np.sum([Etape[j][k] for j in Etape if j != 'Mixed'])/3
            else:
                if nAlVI > 1+1/3:
                    Etape['Mixed'][k] = Etape['M2_M3'][k]
                else:
                    if nAlVI > 1:
                        Etape['Mixed'][k] = Etape['M1'][k]
                    else:
                        Etape['Mixed'][k] = Etape['M4'][k]


    Tetrahedral['moles'] = {}; Octahedral['moles'] = {}; Interlayer['moles'] = {}
    Tetrahedral['moles']['Fe2O3'] = 0.5*np.sum([Tetrahedral[j]['Fe3+']
                                                for j in Tetrahedral if j in ['T1', 'T2']])
    for j, k in zip(['CdO', 'TiO2'],['Cd2+', 'Ti4+']):
        Octahedral['moles'][j] = Octahedral['M1'][k] + Octahedral['M2'][k] + Brucitic['M3'][k] +\
             Brucitic['M4'][k]

    if group in ['7A', '10A']:
        Tetrahedral['moles']['Al2O3'] = 0.5*np.sum([Tetrahedral[j]['Al3+']
                                                    for j in Tetrahedral if j in ['T1', 'T2']])
        Tetrahedral['moles']['SiO2'] = np.sum([Tetrahedral[j]['Si4+']
                                               for j in Tetrahedral if j in ['T1', 'T2']])
        for j, k in zip(['LiOH', 'Li2O', 'Mg(OH)2', 'MgO', 'Fe(OH)2', 'FeO',
                         'Fe(OH)3', 'Fe2O3', 'Mn(OH)2', 'MnO', 'Cr(OH)3', 'Cr2O3',
                         'Ni(OH)2', 'NiO', 'Co(OH)2', 'CoO', 'Zn(OH)2', 'ZnO', 'Al(OH)3', 'Al2O3'],
                        ['Li+', 'Li+', 'Mg2+', 'Mg2+', 'Fe2+', 'Fe2+', 'Fe3+', 'Fe3+',
                         'Mn2+', 'Mn2+', 'Cr3+', 'Cr3+', 'Ni2+', 'Ni2+',
                         'Co2+', 'Co2+', 'Zn2+', 'Zn2+', 'Al3+', 'Al3+']):
            if 'OH' not in j:
                if charge[k] == 1:
                    hydroxide = '%sOH' % (k.rstrip('0123456789.+ '))
                else:
                    hydroxide = '%s(OH)%d' % (k.rstrip('0123456789.+ '), charge[k])

                if charge[k] in (1, 3):
                    Octahedral['moles'][j] = (Octahedral['M1'][k] + Octahedral['M2'][k] + \
                        Brucitic['M3'][k] + Brucitic['M4'][k] - Octahedral['moles'][hydroxide])/2
                else:
                    Octahedral['moles'][j] = Octahedral['M1'][k] + Octahedral['M2'][k] + \
                        Brucitic['M3'][k] + Brucitic['M4'][k] - Octahedral['moles'][hydroxide]
            elif j == 'Al(OH)3':
                Octahedral['moles'][j] = (OH - np.sum([Octahedral['moles'][a]*2 if a.endswith('2')
                                                     else Octahedral['moles'][a]*3
                                                     for a in Octahedral['moles'].keys()
                                                     if 'OH' in a and 'Li' not in a and 'Al' not in a]))/3
            else:
                Octahedral['moles'][j] = (Octahedral['M1'][k] + Octahedral['M2'][k] + \
                    Brucitic['M3'][k] + Brucitic['M4'][k])/(R1 + 1)
    else:
        Tetrahedral['moles']['Al2O3'] = 0.5*(4 - nSi)
        Tetrahedral['moles']['SiO2'] = nSi
        for j in ['LiOH', 'Li2O', 'Mg(OH)2', 'MgO', 'Fe(OH)2', 'FeO', 'Fe(OH)3', 'Fe2O3',
                  'Mn(OH)2', 'MnO', 'Cr(OH)3', 'Cr2O3', 'Ni(OH)2', 'NiO', 'Co(OH)2', 'CoO',
                  'Zn(OH)2', 'ZnO', 'Al(OH)3', 'Al2O3']:
            if j in ['Al2O3', 'FeO', 'MgO', 'Fe2O3']:
                Octahedral['moles'][j] = Etape['Mixed']['%s_VI' % j]
            else:
                Octahedral['moles'][j] = Etape['Mixed'][j]
    for k in Interlayer['Tot'].keys():
        if charge[k] == 1 and k not in ['H3O+', 'NH4+']:
            j = '%s2O' % (k.rstrip('0123456789.+ '))
            div = 0.5
        elif k == 'H3O+':
            j = 'H2O'
            div = 1
        elif k == 'NH4+':
            j = '(NH4)2O'
            div = 1
        else:
            j = '%sO' % (k.rstrip('0123456789.+ '))
            div = 1
        if j in Interlayer['Slat'].keys():
            Interlayer['moles'][j] = div*Interlayer['Tot'][k]
    Interlayer['moles']['NiO'] = 0
    Slat = np.sum([Octahedral['moles'][j]*Octahedral['Slat'][j]
                   for j in Octahedral['Slat'].keys()] + \
                  [Tetrahedral['moles'][j]*Tetrahedral['Slat'][j]
                   for j in Tetrahedral['Slat'].keys()] + \
                      [Interlayer['moles'][j]*Interlayer['Slat'][j]
                       for j in Interlayer['Slat'].keys()])

    V = np.sum([Octahedral['moles'][j]*Octahedral['V'][j]
                for j in Octahedral['V'].keys()] + \
               [Tetrahedral['moles'][j]*Tetrahedral['V'][j]
                for j in Tetrahedral['V'].keys()] + \
                   [Interlayer['moles'][j]*Interlayer['V'][j]
                    for j in Interlayer['V'].keys()]) # cm3/mol
    
    Cp = np.where(np.sum([Octahedral['moles'][j] for j in Octahedral['moles'].keys()
                          if j in ['Mn(OH)2', 'Cr(OH)3', 'Co(OH)2']]) == 0,
                  np.sum([Octahedral['moles'][j]*Octahedral['Cp'][j]
                          for j in Octahedral['Cp'].keys()] + \
                          [Tetrahedral['moles'][j]*Tetrahedral['Cp'][j]
                          for j in Tetrahedral['Cp'].keys()] + \
                              [Interlayer['moles'][j]*Interlayer['Cp'][j]
                              for j in Interlayer['Cp'].keys()]),
                          0)
    
    if heatcap_approx.lower() == 'maier-kelley':
        a = np.sum([Octahedral['moles'][j]*Octahedral['a'][j] for j in Octahedral['a'].keys()] + \
                [Tetrahedral['moles'][j]*Tetrahedral['a'][j] for j in Tetrahedral['a'].keys()] + \
                    [Interlayer['moles'][j]*Interlayer['a'][j] for j in Interlayer['a'].keys()])
        b = np.sum([Octahedral['moles'][j]*Octahedral['b'][j] for j in Octahedral['b'].keys()] + \
                   [Tetrahedral['moles'][j]*Tetrahedral['b'][j] for j in Tetrahedral['b'].keys()] + \
                      [Interlayer['moles'][j]*Interlayer['b'][j] for j in Interlayer['b'].keys()])
        c = np.sum([Octahedral['moles'][j]*Octahedral['c'][j] for j in Octahedral['c'].keys()] + \
                [Tetrahedral['moles'][j]*Tetrahedral['c'][j] for j in Tetrahedral['c'].keys()] + \
                    [Interlayer['moles'][j]*Interlayer['c'][j] for j in Interlayer['c'].keys()])

    else:    
        a = np.where(np.sum([Octahedral['moles'][j] for j in Octahedral['moles'].keys()
                            if j in ['Li2O', 'MnO', 'Cr2O3', 'NiO', 'CoO', 'ZnO']] + \
                            [Interlayer['moles'][j] for j in Interlayer['moles'].keys()
                            if j in ['Cs2O', 'Rb2O', 'Li2O', 'ZnO', 'BaO', 'SrO', 'CoO',
                                    'MgO', 'CuO', 'H2O']]) == 0,
                    np.sum([Octahedral['moles'][j]*Octahedral['a'][j]
                            for j in Octahedral['a'].keys()] + \
                            [Tetrahedral['moles'][j]*Tetrahedral['a'][j]
                            for j in Tetrahedral['a'].keys()] + \
                                [Interlayer['moles'][j]*Interlayer['a'][j]
                                for j in Interlayer['a'].keys()]),
                            0)
        b = np.where(np.sum([Octahedral['moles'][j] for j in Octahedral['moles'].keys()
                            if j in ['Li2O', 'MnO', 'Cr2O3', 'NiO', 'CoO', 'ZnO']] + \
                            [Interlayer['moles'][j] for j in Interlayer['moles'].keys()
                            if j in ['Cs2O', 'Rb2O', 'Li2O', 'ZnO', 'BaO', 'SrO', 'CoO',
                                    'MgO', 'CuO', 'H2O']]) == 0,
                    np.sum([Octahedral['moles'][j]*Octahedral['b'][j]
                            for j in Octahedral['b'].keys()] + \
                            [Tetrahedral['moles'][j]*Tetrahedral['b'][j]
                            for j in Tetrahedral['b'].keys()] + \
                                [Interlayer['moles'][j]*Interlayer['b'][j]
                                for j in Interlayer['b'].keys()]),
                            0)
        c = np.where(np.sum([Octahedral['moles'][j] for j in Octahedral['moles'].keys()
                            if j in ['Li2O', 'MnO', 'Cr2O3', 'NiO', 'CoO', 'ZnO']] + \
                            [Interlayer['moles'][j] for j in Interlayer['moles'].keys()
                            if j in ['Cs2O', 'Rb2O', 'Li2O', 'ZnO', 'BaO', 'SrO', 'CoO',
                                    'MgO', 'CuO', 'H2O']]) == 0,
                    np.sum([Octahedral['moles'][j]*Octahedral['c'][j]
                            for j in Octahedral['c'].keys()] + \
                            [Tetrahedral['moles'][j]*Tetrahedral['c'][j]
                            for j in Tetrahedral['c'].keys()] + \
                                [Interlayer['moles'][j]*Interlayer['c'][j]
                                for j in Interlayer['c'].keys()]),
                            0)
    S_spin_mag = np.sum([S_spin[j]*Octahedral['M2'][j]
                         for j in set(S_spin.keys())&set(Octahedral['M2'].keys())] +\
                        [S_spin[j]*Octahedral['M1'][j]
                         for j in set(S_spin.keys())&set(Octahedral['M1'].keys())] +\
                            [S_spin[j]*Brucitic['M3'][j]
                             for j in set(S_spin.keys())&set(Brucitic['M3'].keys())] +\
                                [S_spin[j]*Brucitic['M4'][j]
                                 for j in set(S_spin.keys())&set(Brucitic['M4'].keys())] +\
                                    [S_spin[j]*Tetrahedral['T1'][j]
                                     for j in set(S_spin.keys())&set(Tetrahedral['T1'].keys())] +\
                                        [S_spin[j]*Tetrahedral['T2'][j]
                                         for j in set(S_spin.keys())&set(Tetrahedral['T2'].keys())])
    Al_Tet_ratio = np.sum([Tetrahedral[j]['Al3+']
                           for j in ['T1', 'T2'] ])/np.sum([Tetrahedral[j][k]
                                                            for j in ['T1', 'T2']
                                                            for k in Tetrahedral['T1'].keys()])
    R = 8.31451 #J K​−1 mol−1
    if Al_Tet_ratio < 0.2:
        Sconf_site = 1270*Al_Tet_ratio**3 + (-903.7)*Al_Tet_ratio**2 + 166.2*Al_Tet_ratio
        Sconf_site = -Sconf_site/R/2
    elif Al_Tet_ratio < 0.31:
        Sconf_site = 4610*Al_Tet_ratio**3 + (-4271.3)*Al_Tet_ratio**2 + 1280*Al_Tet_ratio + (-114.79)
        Sconf_site = -Sconf_site/R/2
    else:
        Sconf_site = Calc['XlnX']['T2']
    if cation_order.title() == 'Ordered':
        Sconf_T = 0
    elif cation_order.title() == 'Random':
        Sconf_T = Calc['XlnX']['T1'] + Calc['XlnX']['T2']
    else:
        Sconf_T = Sconf_site
    if group == '10A':
        Scf = -R*(Calc['XlnX']['Inter'] + 2*Calc['XlnX']['M2'] + Calc['XlnX']['M1'] + 2*Sconf_T)
    elif group == '14A':
        Scf = -R*(2*Calc['XlnX']['M2'] + 2*Calc['XlnX']['M3'] + Calc['XlnX']['M1'] + \
                  Calc['XlnX']['M4'] + 2*Sconf_T)
    else:
        Scf = -R*(2*Calc['XlnX']['M2'] + Calc['XlnX']['M1'] + Sconf_T)
    S_allelem = 0
    for x in list(S_elem.keys()):
        ele =  x.rstrip('0123456789.+ ')
        if x == 'O2':
            ele_lst = [Octahedral[k][j] for k in ['M1', 'M2']
                       for j in Octahedral[k].keys() if ele in j] + \
                [Brucitic[k][j] for k in ['M3', 'M4']
                 for j in Brucitic[k].keys() if ele in j] + \
                    [Tetrahedral[k][j] for k in ['T1', 'T2']
                     for j in Tetrahedral[k].keys() if ele in j] + \
                        [Interlayer['Tot'][j]*0.5 if j == 'H3O+'
                         else Interlayer['Tot'][j] for j in Interlayer['Tot'].keys() if ele in j]
            ele_lst.append(Oxy/2)
        elif x == 'H2':
            ele_lst = [Octahedral[k][j] for k in ['M1', 'M2']
                       for j in Octahedral[k].keys() if ele in j] + \
                [Brucitic[k][j] for k in ['M3', 'M4']
                 for j in Brucitic[k].keys() if ele in j] + \
                    [Tetrahedral[k][j] for k in ['T1', 'T2']
                     for j in Tetrahedral[k].keys() if ele in j] + \
                        [Interlayer['Tot'][j]*1.5 if j == 'H3O+'
                         else Interlayer['Tot'][j]*2 if j == 'NH4+'
                         else Interlayer['Tot'][j] for j in Interlayer['Tot'].keys() if ele in j]
            ele_lst = ele_lst + [Calc['Nb_Oxy']['H_i'], Calc['Nb_Oxy']['H_b'], Calc['Nb_Oxy']['H_ext']]
        elif x == 'N2':
            ele_lst = [Octahedral[k][j] for k in ['M1', 'M2']
                       for j in Octahedral[k].keys() if ele in j and j not in ['Ni2+', 'Na+']] + \
                [Brucitic[k][j] for k in ['M3', 'M4']
                 for j in Brucitic[k].keys() if ele in j and j not in ['Ni2+', 'Na+']] + \
                    [Tetrahedral[k][j] for k in ['T1', 'T2']
                     for j in Tetrahedral[k].keys() if ele in j and j not in ['Ni2+', 'Na+']] + \
                        [Interlayer['Tot'][j]*0.5 if j == 'NH4+' else Interlayer['Tot'][j]
                         for j in Interlayer['Tot'].keys()
                         if ele in j and j not in ['Ni2+', 'Na+']]
        else:
            ele_lst = [Octahedral[k][j] for k in ['M1', 'M2']
                       for j in Octahedral[k].keys() if ele in j] + \
                [Brucitic[k][j] for k in ['M3', 'M4']
                 for j in Brucitic[k].keys() if ele in j] + \
                    [Tetrahedral[k][j] for k in ['T1', 'T2']
                     for j in Tetrahedral[k].keys() if ele in j] + \
                        [Interlayer['Tot'][j] for j in Interlayer['Tot'].keys() if ele in j]
        S_allelem = S_allelem + np.sum(ele_lst)*S_elem[x]

    S = Slat + Scf + S_spin_mag if group == '10A' else Slat + S_spin_mag
    dG = (dHf*1e3 - 298.15*(S - S_allelem))*1e-3
 
    Rxn = {}
    Rxn['type'] = ClayMintype
    Rxn['name'] = name
    Rxn['formula'] = ''
    Rxn['MW'] = 0
    if nCs != 0:
        Rxn['formula'] = Rxn['formula'] + 'Cs%1.2f' % nCs
        Rxn['MW'] = Rxn['MW'] + nCs*MW['Cs']
    if nRb != 0:
        Rxn['formula'] = Rxn['formula'] + 'Rb%1.2f' % nRb
        Rxn['MW'] = Rxn['MW'] + nRb*MW['Rb']
    if nK != 0:
        Rxn['formula'] = Rxn['formula'] + 'K%1.2f' % nK
        Rxn['MW'] = Rxn['MW'] + nK*MW['K']
    if nNa != 0:
        Rxn['formula'] = Rxn['formula'] + 'Na%1.2f' % nNa
        Rxn['MW'] = Rxn['MW'] + nNa*MW['Na']
    if nLi != 0:
        Rxn['formula'] = Rxn['formula'] + 'Li%1.2f' % nLi
        Rxn['MW'] = Rxn['MW'] + nLi*MW['Li']
    if nH3O != 0:
        Rxn['formula'] = Rxn['formula'] + 'H%1.2f' % nH3O
        Rxn['MW'] = Rxn['MW'] + nH3O*MW['H']  #(3*MW['H'] + MW['O'])
    if nFe != 0:
        Rxn['formula'] = Rxn['formula'] + 'Fe%1.2f' % nFe
        Rxn['MW'] = Rxn['MW'] + nFe*MW['Fe']
    if nMn != 0:
        Rxn['formula'] = Rxn['formula'] + 'Mn%1.2f' % nMn
        Rxn['MW'] = Rxn['MW'] + nMn*MW['Mn']
    if nNi != 0:
        Rxn['formula'] = Rxn['formula'] + 'Ni%1.2f' % nNi
        Rxn['MW'] = Rxn['MW'] + nNi*MW['Ni']
    if nCo != 0:
        Rxn['formula'] = Rxn['formula'] + 'Co%1.2f' % nCo
        Rxn['MW'] = Rxn['MW'] + nCo*MW['Co']
    if nCd != 0:
        Rxn['formula'] = Rxn['formula'] + 'Cd%1.2f' % nCd
        Rxn['MW'] = Rxn['MW'] + nCd*MW['Cd']
    if nZn != 0:
        Rxn['formula'] = Rxn['formula'] + 'Zn%1.2f' % nZn
        Rxn['MW'] = Rxn['MW'] + nZn*MW['Zn']
    if nCa != 0:
        Rxn['formula'] = Rxn['formula'] + 'Ca%1.2f' % nCa
        Rxn['MW'] = Rxn['MW'] + nCa*MW['Ca']
    if nMg != 0:
        Rxn['formula'] = Rxn['formula'] + 'Mg%1.2f' % nMg
        Rxn['MW'] = Rxn['MW'] + nMg*MW['Mg']
    if nAl != 0:
        Rxn['formula'] = Rxn['formula'] + 'Al%1.2f' % nAl
        Rxn['MW'] = Rxn['MW'] + nAl*MW['Al']
    if nFe3 != 0:
        Rxn['formula'] = Rxn['formula'] + 'FeIII%1.2f' % nFe3
        Rxn['MW'] = Rxn['MW'] + (nFe3)*MW['Fe']
    if nV != 0:
        Rxn['formula'] = Rxn['formula'] + 'V%1.2f' % nV
        Rxn['MW'] = Rxn['MW'] + nV*MW['V']
    if nCr != 0:
        Rxn['formula'] = Rxn['formula'] + 'Cr%1.2f' % nCr
        Rxn['MW'] = Rxn['MW'] + nCr*MW['Cr']
    if nTi != 0:
        Rxn['formula'] = Rxn['formula'] + 'Ti%1.2f' % nTi
        Rxn['MW'] = Rxn['MW'] + nTi*MW['Ti']
    if nVO != 0:
        Rxn['formula'] = Rxn['formula'] + 'VO%1.2f' % nVO
        Rxn['MW'] = Rxn['MW'] + nVO*(MW['V'] + 2*MW['O'])

    nH = np.sum([Interlayer['Tot'][j]*charge[j]
                 for j in list(Interlayer['Tot'].keys())[:7] + \
                     list(Interlayer['Tot'].keys())[-5:]]) + \
        np.sum([Octahedral['Tot'][j]*charge[j]
                for j in list(Octahedral['Tot'].keys())[:-1] if j != 'Cd2+']) + \
            np.sum([Tetrahedral['Tot'][j]*charge[j] for j in list(Tetrahedral['Tot'].keys())[1:]])
    nH = round(nH, 3) - nH3O
    nH2O = (Oxy - nH3O  + nH3O - 2*nSi - 2*nTi)
    # nH = (nH2O*2 - OH) if (nH2O*2 - OH) != nH else nH
    Rxn['formula'] = Rxn['formula'] + 'Si%s' % nSi + 'O%d(OH)%d' % (Oxy - OH, OH)
    Rxn['MW'] = Rxn['MW'] + nSi*MW['Si'] + Oxy*MW['O'] + OH*MW['H']
    Rxn['min']=[dG*1000/J_to_cal, dHf*1000/J_to_cal, S/J_to_cal,
                V, a/J_to_cal, b/J_to_cal, c/J_to_cal]
    Rxn['min'].insert(0, Rxn['formula'])
    Rxn['min'].insert(1, 'B2015, B2021')

    # In your main code where you want to generate the formula:
    if export_struct_formula is True:
        Rxn = generate_structural_formula(Rxn, Interlayer, Octahedral, Tetrahedral, Oxy, OH, MW, charge)

    coeff = [-nH, nCs, nRb, nK, nNa, nLi, nFe, nMn, nNi, nCo, nCd, nZn, nCa, nMg,
             nAl, nFe3, nV, nCr, nTi, nVO, nSi, nH2O]
    spec = ['H+', 'Cs+', 'Rb+', 'K+', 'Na+', 'Li+', 'Fe++', 'Mn++', 'Ni++', 'Co++', 'Cd++',
            'Zn++', 'Ca++', 'Mg++', 'Al+++', 'Fe+++', 'V+++', 'Cr+++',
            'Ti(OH)4', 'VO++', 'SiO2(aq)', 'H2O']
    Rxn['spec'] = [x for x, y in zip(spec, coeff) if y!=0]
    Rxn['coeff'] = [y for y in coeff if y!=0]
    Rxn['nSpec'] = len(Rxn['coeff'])
    Rxn['V'] = V
    Rxn['dG'] = dG
    Rxn['dHf'] = dHf
    Rxn['S'] = S
    Rxn['Cp'] = float(Cp)
    Rxn['source'] = 'B2015, B2021'

    elements  = ['%.4f' % nCa, 'Ca', '%.4f' % nK, 'K', '%.4f' % nNa, 'Na', '%.4f' % nLi, 'Li',
                 '%.4f' % (nFe + nFe3), 'Fe', '%.4f' % nMg, 'Mg', '%.4f' % nNi, 'Ni', 
                 '%.4f' % nAl, 'Al', '%.4f' % nSi, 'Si', '%.4f' % (OH + 3 * nH3O), 'H', 
                 '%.4f' % (Oxy + nH3O), 'O']
    filters = [y for x, y in enumerate(elements) if x%2 == 0 and float(y) == 0]
    filters = [[x, x+1] for x, y in enumerate(elements) if y in filters]
    filters = [num for elem in filters for num in elem]
    Rxn['elements'] = [y for x, y in enumerate(elements) if x not in filters]

    clay = Rxn['min']
    dGTP = heatcap( T = TC, P = P, method = 'SUPCRT', Species_ppt = clay, Species = name).dG
    R = 1.9872041 # cal/mol/K
    dGRs = 0
    for i in range(Rxn['nSpec']):
        R_coeff = float(Rxn['coeff'][i])
        R_specie = Rxn['spec'][i]

        if R_specie == 'H2O':
            dGR = dGH2O
        else:
            dGR  = supcrtaq(TC, P, dbaccessdic[R_specie], Dielec_method = Dielec_method, ThermoInUnit = ThermoInUnit, **rhoEG)
        dGRs = dGRs + R_coeff*dGR

    dGrxn = -dGTP + dGRs
    logK_clay = (-dGrxn/R/(TK)/np.log(10))

    return logK_clay, Rxn#, rhoEG

