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


class solidsolution_thermo():
    """Class to calculate Ideal mixing model for solid-solutions, supporting multisite ideal formalism

    Parameters
    ----------
        X : float
            End member mineral volume fraction or mole fraction of Mg in clinopyroxene
        cpx_Ca : float
            number of moles of Ca in clinopyroxene formula unit (=1 for Di, Hed)  \n
        T : float, vector
            Temperature [°C]  \n
        P : float, vector
            Pressure [bar]  \n
        dbaccessdic : dict
            dictionary of species from direct-access database, optional, default is speq23  \n
        solidsolution_type : string
            specify either 'All' or 'plagioclase' or 'olivine' or 'pyroxene' or 'cpx' or 'alk-feldspar' or 'biotite' to carry-out all or any solid-solution calculations, default is 'All'
        Dielec_method   : string
            specify either 'FGL97' or 'JN91' or 'DEW' as the method to calculate dielectric constant (optional), if not specified default - 'JN91'
       ThermoInUnit : string
           specify either 'cal' or 'KJ' as the input units for species properties (optional), particularly used to covert KJ data to cal by supcrtaq function if not specified default - 'cal'
       Al_Si : string
           specify either 'pygcc' or 'Arnórsson_Stefánsson' as the input to express Al and Si species in solid solution (optional), 'Arnórsson_Stefánsson' expresses them as 'Al(OH)4-' and 'H4SiO4(aq)', respectively while pygcc uses 'Al3+' and 'SiO2(aq)', respectively if not specified default - 'pygcc'
        rhoEG      : dict
            dictionary of water properties like  density (rho), dielectric factor (E) and Gibbs Energy  (optional)

    Returns
    -------
        if 'All' is specified for solidsolution_type, each case has the follwowing prefix - AnAb_, FoFa_, EnFe_, cpx_, AlkFed_, Biotite_   \n
        logK : float, vector
            logarithmic K values \n
        Rxn : dict
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
    ----------
        The general usage of water_dielec is as follows:  \n
        (1) For water dielectric properties at any Temperature and Pressure:  \n
            ss = solidsolution_thermo(T = T, P = P, X = X, solidsolution_type = 'All', Dielec_method = 'JN91'),   \n
            where T is temperature in celsius and P is pressure in bar
        (2) For water dielectric properties at any Temperature and density :  \n
            ss = solidsolution_thermo(T = T, rho = rho, X = X, solidsolution_type = 'All', Dielec_method = 'JN91'),   \n
            where T is temperature in celsius and rho is density in kg/m³
        (3) For water dielectric properties at any Temperature and Pressure on steam saturation curve:  \n
            ss = solidsolution_thermo(T = T, P = 'T', X = X, solidsolution_type = 'All', Dielec_method = 'JN91'),   \n
            where T is temperature in celsius and P is assigned a quoted character 'T' to reflect steam saturation pressure  \n
            ss = solidsolution_thermo(P = P, T = 'P', X = X, solidsolution_type = 'All', Dielec_method = 'JN91'),   \n
            where P is pressure in bar and T is assigned a quoted character 'P' to reflect steam saturation temperature

    Examples
    --------
    >>> ss = solidsolution_thermo(cpx_Ca = 0.5, X = 0.85, T = 30, P = 50,
                                  solidsolution_type = 'All')
    >>> ss.AnAb_logK, ss.FoFa_logK, ss.EnFe_logK, ss.cpx_logK, ss.AlkFed_logK,
        ss.Biotite_logK
        21.750590, 26.570902, 10.793372, 20.577152,  3.756792, 32.96363

    >>> ss = solidsolution_thermo(cpx_Ca = 1, X = 0.85, T = 50, P = 100,
                                  solidsolution_type = 'cpx')
    >>> ss.logK
        18.81769186
    >>> ss.Rxn
        {'type': 'cpx', 'name': 'Di85Hed15',
         'formula': 'Ca1.00Mg0.85Fe0.15Si2O6', 'MW': 221.2817,
         'min': ['Ca1.00Mg0.85Fe0.15Si2O6', ' R&H95, Stef2001',
                 -711392.7391800061, nan, 37.032850185405415, 66.369,
                 106.66383843212236, -0.019588551625239002, -16326.4818355,
                 -1052.9517208413004, 5.714746653919693e-06],
         'spec': ['H+', 'Ca++', 'Mg++', 'Fe++', 'SiO2(aq)', 'H2O'],
         'coeff': [-4, 1.0, 0.85, 0.15, 2, 2], 'nSpec': 6, 'V': 66.369,
         'source': ' R&H95, Stef2001', 'elements': ['1.0000', 'Ca', '0.8500',
                                                    'Mg', '0.1500', 'Fe', '2.0000',
                                                    'Si', '6.0000', 'O']}

    >>> ss = solidsolution_thermo(X = 0.5, T = 50, P = 100,
                                  solidsolution_type = 'plagioclase')
    >>> ss.logK
        12.62488394
    >>> ss.Rxn
        {'type': 'plag', 'name': 'An50', 'formula': 'Ca0.50Na0.50Al1.50Si2.50O8',
         'MW': 270.215145, 'min': ['Ca0.50Na0.50Al1.50Si2.50O8', ' R&H95,
                                   Stef2001', -919965.222804649, nan,
                                   47.33081919017781, 100.43, 131.53908221797,
                                   -0.022148661567686426, 32265.761759082205,
                                   -1316.0836615678777, 7.719885114722753e-06],
         'spec': ['H+', 'Al+++', 'Na+', 'Ca++', 'SiO2(aq)', 'H2O'],
         'coeff': [-6.0, 1.5, 0.5, 0.5, 2.5, 3.0], 'nSpec': 6, 'V': 100.43,
         'source': ' R&H95, Stef2001', 'elements': ['0.5000', 'Ca', '0.5000',
                                                    'Na', '1.5000', 'Al', '2.5000',
                                                    'Si', '8.0000', 'O']}
    """
    kwargs = {"X": None,
              "cpx_Ca": 0.5,
              "T": None,
              "P": None, "ThermoInUnit": 'cal',
              "Dielec_method": None, "solidsolution_type": 'All',
              "rhoEG": None, "dbaccessdic": None, "Al_Si": 'pygcc'}

    def __init__(self, **kwargs):
        self.kwargs = solidsolution_thermo.kwargs.copy()
        self.__calc__(**kwargs)

    def __calc__(self, **kwargs): #
        self.kwargs.update(kwargs)
        self.X = self.kwargs["X"]
        self.cpx_Ca = self.kwargs["cpx_Ca"]
        self.ThermoInUnit = self.kwargs["ThermoInUnit"]
        self.Al_Si = self.kwargs["Al_Si"]
        self.__checker__(**kwargs)
        if self.kwargs["solidsolution_type"].lower() == 'all':
            self.AnAb_logK, self.AnAb_Rxn = self.calclogKAnAb(self.X, self.T, self.P, self.dbaccessdic,
                                                              self.rhoEG, Dielec_method = self.Dielec_method)
            self.FoFa_logK, self.FoFa_Rxn = self.calclogKFoFa(self.X, self.T, self.P, self.dbaccessdic,
                                                              self.rhoEG, Dielec_method = self.Dielec_method)
            self.EnFe_logK, self.EnFe_Rxn = self.calclogKEnFe(self.X, self.T, self.P, self.dbaccessdic,
                                                              self.rhoEG, Dielec_method = self.Dielec_method)
            self.cpx_logK, self.cpx_Rxn = self.calclogKDiHedEnFe(self.cpx_Ca, self.X, self.T, self.P,
                                                                 self.dbaccessdic, self.rhoEG, Dielec_method = self.Dielec_method)
            self.AlkFed_logK, self.AlkFed_Rxn = self.calclogKAbOr(self.X, self.T, self.P, self.dbaccessdic,
                                                                  self.rhoEG, Dielec_method = self.Dielec_method)
            self.Biotite_logK, self.Biotite_Rxn = self.calclogKBiotite(self.X, self.T, self.P, self.dbaccessdic,
                                                                       self.rhoEG, Dielec_method = self.Dielec_method)
        elif self.kwargs["solidsolution_type"].lower().startswith('plag'):
            self.logK, self.Rxn = self.calclogKAnAb(self.X, self.T, self.P, self.dbaccessdic,
                                                    self.rhoEG, Dielec_method = self.Dielec_method)
        elif self.kwargs["solidsolution_type"].lower().startswith('ol'):
            self.logK, self.Rxn = self.calclogKFoFa(self.X, self.T, self.P, self.dbaccessdic,
                                                    self.rhoEG, Dielec_method = self.Dielec_method)
        elif self.kwargs["solidsolution_type"].lower().startswith('py'):
            self.logK, self.Rxn = self.calclogKEnFe(self.X, self.T, self.P, self.dbaccessdic,
                                                    self.rhoEG, Dielec_method = self.Dielec_method)
        elif self.kwargs["solidsolution_type"].lower().startswith('cpx'):
            if self.cpx_Ca > 0:
                self.logK, self.Rxn = self.calclogKDiHedEnFe(self.cpx_Ca, self.X, self.T, self.P,
                                                             self.dbaccessdic, self.rhoEG,
                                                             Dielec_method = self.Dielec_method)
            else:
                self.logK, self.Rxn = self.calclogKEnFe(self.X, self.T, self.P, self.dbaccessdic,
                                                        self.rhoEG, Dielec_method = self.Dielec_method)
        elif self.kwargs["solidsolution_type"].lower().startswith('alk'):
            self.logK, self.Rxn = self.calclogKAbOr(self.X, self.T, self.P, self.dbaccessdic,
                                                    self.rhoEG, Dielec_method = self.Dielec_method)
        elif self.kwargs["solidsolution_type"].lower().startswith('bio'):
            self.logK, self.Rxn = self.calclogKBiotite(self.X, self.T, self.P, self.dbaccessdic,
                                                       self.rhoEG, Dielec_method = self.Dielec_method)

    def __checker__(self, **kwargs):
        self.T = self.kwargs["T"]
        self.P = self.kwargs["P"]
        self.rhoEG = self.kwargs['rhoEG']
        self.Dielec_method = 'JN91' if self.kwargs["Dielec_method"] is None else self.kwargs["Dielec_method"]
        if (type(self.P) == str) or (type(self.T) == str):
            if self.P == 'T':
                self.P = iapws95(T = self.TC).P
                self.P[np.isnan(self.P) | (self.P < 1)] = 1.0133
            elif self.TC == 'P':
                self.TC = iapws95(P = self.P).TC

        if np.ndim(self.T) == 0 :
            self.T = np.array(self.T).ravel()
        # elif np.size(self.T) == 2:
        #     self.T = np.array([roundup_tenth(j) if j != 0 else 0.01 for j in np.linspace(self.T[0], self.T[-1], 8)])

        if np.size(self.P) <= 2:
            self.P = np.ravel(self.P)
            self.P = self.P[0]*np.ones(np.size(self.T))

        if self.rhoEG is None:
            if self.Dielec_method.upper() == 'DEW':
                water = ZhangDuan(T = self.T, P = self.P)
            else:
                water = iapws95(T = self.T, P = self.P)
            rho, dGH2O = water.rho, water.G
            E = water_dielec(T = self.T, P = self.P, Dielec_method = self.Dielec_method).E
            self.rhoEG = {'rho': rho, 'E': E,  'dGH2O': dGH2O}

        if self.kwargs['dbaccessdic'] == None:
            dbaccess_dir = './default_db/speq23.dat'
            dbaccess_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), dbaccess_dir)
            self.dbaccessdic = db_reader(dbaccess = dbaccess_dir).dbaccessdic
        else:
            self.dbaccessdic = self.kwargs['dbaccessdic']

    def calclogKAnAb(self, XAn, TC, P, dbaccessdic, rhoEG, Dielec_method = None):
        """
        This function calculates thermodynamic properties of solid solution of Plagioclase minerals

        Parameters
        ----------
            XAn        : volume fraction of Anorthite  \n
            TC         : temperature [°C]  \n
            P          : pressure [bar]  \n
            dbaccessdic : dictionary of species from direct-access database  \n
            Dielec_method   : specify either 'FGL97' or 'JN91' or 'DEW' as the method to calculate
                            dielectric constant (optional), if not specified default - 'JN91'
            rhoEG      : dictionary of water properties like  density (rho),
                           dielectric factor (E) and Gibbs Energy  (optional)
        Returns
        -------
            logKplag   : logarithmic K values   \n
            Rxn        : dictionary of reaction thermodynamic properties
        Usage
        -------
            The general usage of calclogKAnAb without the optional argument is as follows:  \n
            (1) Not on steam saturation curve:  \n
                [logK, Rxn] = calclogKAnAb(XAn, TC, P, dbaccessdic),  \n
                where T is temperature in celsius and P is pressure in bar;
            (2) On steam saturation curve:  \n
                [logK, Rxn] = calclogKAnAb(XAn, TC, 'T', dbaccessdic),   \n
                where T is temperature in celsius, followed with a quoted char 'T'  \n
                [logK, Rxn] = calclogKAnAb(XAn, P, 'P', dbaccessdic), \n
                where P is pressure in bar, followed with a quoted char 'P'.
            (3) Meanwhile, usage with any specific dielectric constant method ('FGL97') for
                condition not on steam saturation curve is as follows. Default method is 'JN91' \n
                [logK, Rxn] = calclogKAnAb(XAn, TC, P, dbaccessdic, Dielec_method = 'FGL97')
        """

        dGH2O = rhoEG['dGH2O'].ravel()

        TK = convert_temperature( TC, Out_Unit = 'K' )
        Rxn = {}
        Rxn['type'] = 'plag'
        XAb = 1 - XAn
        nH = (8 - 4*XAb)
        nAl = (2 - XAb)
        nH2O = (4 - 2*XAb)
        nNa = XAb
        nCa = (1 - XAb)
        nSi = (2 + XAb)
        if XAn == 1:
            Rxn['name'] ='Anorthite'
            Rxn['formula'] ='CaAl2(SiO4)2'
        elif XAn == 0:
            Rxn['name'] ='Albite'
            Rxn['formula'] ='NaAlSi3O8'
        else:
            Rxn['name'] = 'An%d' % (XAn*100)
            Rxn['formula'] = 'Ca%1.2f' % nCa + 'Na%1.2f' % nNa + 'Al%1.2f' % nAl + 'Si%1.2f' % nSi + 'O8'

        Rxn['MW'] = nCa*MW['Ca'] + nNa* MW['Na'] + nAl*MW['Al'] + nSi*MW['Si'] + 8*MW['O']
        R = 1.9872041

        if self.Al_Si == 'pygcc':
            dGAl = supcrtaq(TC, P, dbaccessdic['Al+++'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
            dGSiO2aq  = supcrtaq(TC, P, dbaccessdic['SiO2(aq)'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
            dGH = supcrtaq(TC, P, dbaccessdic['H+'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        elif self.Al_Si == 'Arnórsson_Stefánsson':
            dGAl = supcrtaq(TC, P, dbaccessdic['Al(OH)4-'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
            dGSiO2aq  = supcrtaq(TC, P, dbaccessdic['H4SiO4(aq)'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
            nH2O = nH2O + 2*nSi

        dGNa = supcrtaq(TC, P, dbaccessdic['Na+'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        dGCa = supcrtaq(TC, P, dbaccessdic['Ca++'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)


        if (XAn < 1) & (XAn != 0):
            Smix=-R*(XAb*np.log((XAb*(4-XAb**2)*(2+XAb)**2)/27) + \
                     XAn*np.log((XAn*(1+XAn)**2*(3-XAn)**2)/16))
        else:
            Smix=0

        dGplag = XAb*dbaccessdic['ss_Albite_high'][2] + XAn*dbaccessdic['ss_Anorthite'][2] + R*298.15*Smix
        Splag = XAb*dbaccessdic['ss_Albite_high'][4] + XAn*dbaccessdic['ss_Anorthite'][4] - R*Smix
        Vplag = XAb*dbaccessdic['ss_Albite_high'][5] + XAn*dbaccessdic['ss_Anorthite'][5]
        Cpplag = [a + b for a, b in zip([XAb*x for x in dbaccessdic['ss_Albite_high'][6:11] ],
                                        [XAn*y for y in dbaccessdic['ss_Anorthite'][6:11] ])]
        Rxn['min'] = [dGplag, np.nan, Splag, Vplag] + Cpplag
        Rxn['min'].insert(0, Rxn['formula'])
        Rxn['min'].insert(1,' R&H95, Stef2001')
        plag = Rxn['min']
        dGplagTP = heatcap( T = TC, P = P, method = 'HF76', Species_ppt = plag).dG
        if self.Al_Si == 'pygcc':
            coeff = [-nH, nAl, nNa, nCa, nSi, nH2O]
            spec = ['H+', 'Al+++', 'Na+', 'Ca++', 'SiO2(aq)', 'H2O']
        elif self.Al_Si == 'Arnórsson_Stefánsson':
            coeff = [nAl, nNa, nCa, nSi, -nH2O]
            spec = ['Al(OH)4-', 'Na+', 'Ca++', 'H4SiO4(aq)', 'H2O']
        Rxn['spec'] = [x for x, y in zip(spec, coeff) if y!=0]
        Rxn['coeff'] = [y for y in coeff if y!=0]
        Rxn['nSpec'] = len(Rxn['coeff'])

        if self.Al_Si == 'pygcc':
            dGrxn = -dGplagTP - nH*dGH + nAl*dGAl + nH2O*dGH2O + nNa*dGNa+ nCa*dGCa + nSi*dGSiO2aq
        elif self.Al_Si == 'Arnórsson_Stefánsson':
            dGrxn = -dGplagTP + nAl*dGAl - nH2O*dGH2O + nNa*dGNa+ nCa*dGCa + nSi*dGSiO2aq
        logKplag = (-dGrxn/R/(TK)/np.log(10))   #np.log10(np.exp(-dGrxn/R/(TK)))

        Rxn['V'] = Rxn['min'][5]  #,'%8.3f')
        Rxn['source'] = ' R&H95, Stef2001'
        elements  = ['%.4f' % nCa, 'Ca', '%.4f' % nNa, 'Na', '%.4f' % nAl, 'Al', '%.4f' % nSi, 'Si', '8.0000', 'O']
        filters = [y for x, y in enumerate(elements) if x%2 == 0 and float(y) == 0]
        filters = [[x, x+1] for x, y in enumerate(elements) if y in filters]
        filters = [num for elem in filters for num in elem]
        Rxn['elements'] = [y for x, y in enumerate(elements) if x not in filters]

        return logKplag, Rxn

    def calclogKFoFa( self, XFo, TC, P, dbaccessdic, rhoEG, Dielec_method = None ):
        """
        This function calculates thermodynamic properties of solid solution of olivine minerals  \n
        Parameters
        ----------
            XFo        : volume fraction of Forsterite  \n
            TC         : temperature [°C]  \n
            P          : pressure [bar]  \n
            dbaccessdic : dictionary of species from direct-access database  \n
            Dielec_method   : specify either 'FGL97' or 'JN91' or 'DEW' as the method to calculate
                            dielectric constant (optional), if not specified default - 'JN91'
            rhoEG      : dictionary of water properties like  density (rho),
                           dielectric factor (E) and Gibbs Energy  (optional)
        Returns
        -------
            logK_ol    : logarithmic K values   \n
            Rxn        : dictionary of reaction thermodynamic properties
        Usage
        -------
            The general usage of calclogKFoFa without the optional argument is as follows:  \n
            (1) Not on steam saturation curve:  \n
                [logK, Rxn] = calclogKFoFa(XFo, TC, P, dbaccessdic),  \n
                where T is temperature in celsius and P is pressure in bar;
            (2) On steam saturation curve:  \n
                [logK, Rxn] = calclogKFoFa(XFo, TC, 'T', dbaccessdic),   \n
                where T is temperature in celsius, followed with a quoted char 'T'  \n
                [logK, Rxn] = calclogKFoFa(XFo, P, 'P', dbaccessdic), \n
                where P is pressure in bar, followed with a quoted char 'P'.
            (3) Meanwhile, usage with any specific dielectric constant method ('FGL97') for
                condition not on steam saturation curve is as follows. Default method is 'JN91' \n
                [logK, Rxn] = calclogKFoFa(XFo, TC, P, dbaccessdic, Dielec_method = 'FGL97')
        """
        Tref = 25; Pref = 1
        rho = rhoEG['rho'].ravel();   E = rhoEG['E'].ravel()
        dGH2O = rhoEG['dGH2O'].ravel()
        # if no reference Temperature and Pressure is found, append to the bottom
        if any((TC == Tref) & (P == Pref)) == False:
            water = iapws95(T = Tref, P = Pref)
            rhoref, dGH2Oref = water.rho, water.G
            Eref = water_dielec(T = Tref, P = Pref, Dielec_method = Dielec_method).E

            TC = np.concatenate([TC, np.ravel(Tref)])
            P = np.concatenate([P, np.ravel(Pref)])
            rho = np.concatenate([rho, np.ravel(rhoref)])
            E = np.concatenate([E, np.ravel(Eref)])
            dGH2O = np.concatenate([dGH2O, np.ravel(dGH2Oref)])
            rhoEG = {'rho': rho, 'E': E,  'dGH2O': dGH2O}

        TK = convert_temperature( TC, Out_Unit = 'K' )
        Rxn = {}
        Rxn['type']='ol'
        XFa = 1-XFo
        nH = 4
        nMg = 2*XFo
        nFe = 2*XFa
        nSi = 1
        nH2O = 2
        if XFo == 1:
            Rxn['name']='Forsterite'
            Rxn['formula']='Mg2SiO4'
        elif XFo == 0:
            Rxn['name']='Fayalite'
            Rxn['formula']='Fe2SiO4'
        else:
            Rxn['name'] = 'Fo%d' % (XFo*100)
            Rxn['formula']= 'Mg%1.2f' % nMg + 'Fe%1.2f' % nFe + 'Si%s' % nSi + 'O4'

        Rxn['MW'] = nMg*MW['Mg'] + nFe*MW['Fe'] + nSi*MW['Si'] + 4*MW['O']
        R = 1.9872041
        WH = 10366.2/J_to_cal
        WS = 4/J_to_cal

        if self.Al_Si == 'pygcc':
            dGSiO2aq  = supcrtaq(TC, P, dbaccessdic['SiO2(aq)'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        elif self.Al_Si == 'Arnórsson_Stefánsson':
            dGSiO2aq  = supcrtaq(TC, P, dbaccessdic['H4SiO4(aq)'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
            nH2O = nH2O - 2*nSi

        dGH = supcrtaq(TC, P, dbaccessdic['H+'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        dGFe = supcrtaq(TC, P, dbaccessdic['Fe++'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        dGMg = supcrtaq(TC, P, dbaccessdic['Mg++'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)

        if (XFo == 1) | (XFo == 0):
            Sconf = 0
        else:
            Sconf = -2*R*(XFo*np.log(XFo) + XFa*np.log(XFa))

        dG_ol = XFa*dbaccessdic['ss_Fayalite'][2] + XFo*dbaccessdic['ss_Forsterite'][2]
        S_ol = XFa*dbaccessdic['ss_Fayalite'][4] + XFo*dbaccessdic['ss_Forsterite'][4] + Sconf
        V_ol = XFa*dbaccessdic['ss_Fayalite'][5] + XFo*dbaccessdic['ss_Forsterite'][5]
        Cp_ol = [a + b for a, b in zip([XFa*x for x in dbaccessdic['ss_Fayalite'][6:11] ],
                                        [XFo*y for y in dbaccessdic['ss_Forsterite'][6:11] ])]
        WG = WH - TK*WS
        Gex = WG*XFo*XFa
        dG_ol = dG_ol + Gex - 298.15*Sconf
        Rxn['min'] = [dG_ol, np.nan, S_ol, V_ol] + Cp_ol
        Rxn['min'].insert(0, Rxn['formula'])
        Rxn['min'].insert(1,' R&H95, Stef2001')
        if self.Al_Si == 'pygcc':
            coeff = [-nH, nMg, nFe, nSi, nH2O]
            spec = ['H+', 'Mg++', 'Fe++', 'SiO2(aq)', 'H2O']
        elif self.Al_Si == 'Arnórsson_Stefánsson':
            coeff = [-nH, nMg, nFe, nSi]
            spec = ['H+', 'Mg++', 'Fe++', 'H4SiO4(aq)']
        Rxn['spec'] = [x for x, y in zip(spec, coeff) if y!=0]
        Rxn['coeff'] = [y for y in coeff if y!=0]
        Rxn['nSpec'] = len(Rxn['coeff'])

        logK_ol = np.zeros([len(TK), 1])
        ol = Rxn['min']
        dGolTP = heatcap( T = TC, P = P, method = 'HF76', Species_ppt = ol).dG
        dGrxn = -dGolTP - nH*dGH + nMg*dGMg + nFe*dGFe + nH2O*dGH2O + nSi*dGSiO2aq
        logK_ol = (-dGrxn/R/(TK)/np.log(10))   #np.log10(np.exp(-dGrxn/R/(TK)))

        Rxn['min'][2] = dG_ol[(TC == Tref) & (P == Pref)][0]
        Rxn['V'] = Rxn['min'][5]  #,'%8.3f')
        Rxn['source'] = ' R&H95, Stef2001'
        elements  = ['%.4f' % nMg, 'Mg', '%.4f' % nFe, 'Fe', '%.4f' % nSi, 'Si', '4.0000', 'O']
        filters = [y for x, y in enumerate(elements) if x%2 == 0 and float(y) == 0]
        filters = [[x, x+1] for x, y in enumerate(elements) if y in filters]
        filters = [num for elem in filters for num in elem]
        Rxn['elements'] = [y for x, y in enumerate(elements) if x not in filters]

        if (TC[-1] == Tref) & (P[-1] == Pref):
            logK_ol = logK_ol[:-1]

        return logK_ol, Rxn

    def calclogKEnFe( self, XEn, TC, P, dbaccessdic, rhoEG, Dielec_method = None ):
        """
        This function calculates thermodynamic properties of solid solution of pyroxene minerals  \n
        Parameters
        ----------
            XEn        : volume fraction of Enstatite  \n
            TC         : temperature [°C]  \n
            P          : pressure [bar]  \n
            dbaccessdic : dictionary of species from direct-access database  \n
            Dielec_method   : specify either 'FGL97' or 'JN91' or 'DEW' as the method to calculate
                            dielectric constant (optional), if not specified default - 'JN91'
            rhoEG      : dictionary of water properties like  density (rho),
                           dielectric factor (E) and Gibbs Energy  (optional)
        Returns
        -------
            logK_opx   : logarithmic K values   \n
            Rxn        : dictionary of reaction thermodynamic properties
        Usage
        -------
            The general usage of calclogKEnFe without the optional argument is as follows:  \n
            (1) Not on steam saturation curve:  \n
                [logK, Rxn] = calclogKEnFe(XEn, TC, P, dbaccessdic),  \n
                where T is temperature in celsius and P is pressure in bar;
            (2) On steam saturation curve:  \n
                [logK, Rxn] = calclogKEnFe(XEn, TC, 'T', dbaccessdic),   \n
                where T is temperature in celsius, followed with a quoted char 'T'  \n
                [logK, Rxn] = calclogKEnFe(XEn, P, 'P', dbaccessdic), \n
                where P is pressure in bar, followed with a quoted char 'P'.
            (3) Meanwhile, usage with any specific dielectric constant method ('FGL97') for
                condition not on steam saturation curve is as follows. Default method is 'JN91' \n
                [logK, Rxn] = calclogKEnFe(XEn, TC, P, dbaccessdic, Dielec_method = 'FGL97')
        """
        rho = rhoEG['rho'].ravel()
        E = rhoEG['E'].ravel()
        dGH2O = rhoEG['dGH2O'].ravel()
        Tref = 25; Pref = 1
        # if no reference Temperature and Pressure is found, append to the bottom
        if any((TC == Tref) & (P == Pref)) == False:
            water = iapws95(T = Tref, P = Pref)
            rhoref, dGH2Oref = water.rho, water.G
            Eref = water_dielec(T = Tref, P = Pref, Dielec_method = Dielec_method).E
            TC = np.concatenate([TC, np.ravel(Tref)])
            P = np.concatenate([P, np.ravel(Pref)])
            rho = np.concatenate([rho, np.ravel(rhoref)])
            E = np.concatenate([E, np.ravel(Eref)])
            dGH2O = np.concatenate([dGH2O, np.ravel(dGH2Oref)])
            rhoEG = {'rho': rho, 'E': E,  'dGH2O': dGH2O}

        TK = convert_temperature( TC, Out_Unit = 'K' )
        Rxn = {}
        Rxn['type'] = 'opx'
        XFe = 1 - XEn
        nH = 2
        nMg = XEn
        nFe = XFe
        nSi = 1
        nH2O = 1
        if XEn == 1:
            Rxn['name'] = 'Enstatite'
            Rxn['formula'] = 'MgSiO3'
        elif XEn == 0:
            Rxn['name'] = 'Ferrosilite'
            Rxn['formula'] = 'FeSiO3'
        else:
            Rxn['name'] = 'En%d' % (XEn*100)
            Rxn['formula'] = 'Mg%1.2f' % nMg + 'Fe%1.2f' % nFe + 'Si%s' % nSi + 'O3'

        Rxn['MW'] = nMg*MW['Mg'] + nFe*MW['Fe'] + nSi*MW['Si'] + 3*MW['O']
        R = 1.9872041
        WH = -2600.4/J_to_cal
        WS = -1.34/J_to_cal

        if self.Al_Si == 'pygcc':
            dGSiO2aq  = supcrtaq(TC, P, dbaccessdic['SiO2(aq)'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        elif self.Al_Si == 'Arnórsson_Stefánsson':
            dGSiO2aq  = supcrtaq(TC, P, dbaccessdic['H4SiO4(aq)'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
            nH2O = nH2O - 2*nSi

        dGH = supcrtaq(TC, P, dbaccessdic['H+'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        dGFe = supcrtaq(TC, P, dbaccessdic['Fe++'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        dGMg = supcrtaq(TC, P, dbaccessdic['Mg++'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)

        if (XEn == 1) | (XEn == 0):
            Sconf = 0
        else:
            Sconf = -1*R*(XEn*np.log(XEn) + XFe*np.log(XFe))

        dG_opx = XEn*dbaccessdic['ss_Enstatite'][2] + XFe*dbaccessdic['ss_Ferrosilite'][2]
        S_opx = XEn*dbaccessdic['ss_Enstatite'][4] + XFe*dbaccessdic['ss_Ferrosilite'][4] + Sconf
        V_opx = XEn*dbaccessdic['ss_Enstatite'][5] + XFe*dbaccessdic['ss_Ferrosilite'][5]
        Cp_opx = [a + b for a, b in zip([XEn*x for x in dbaccessdic['ss_Enstatite'][6:11] ],
                                        [XFe*y for y in dbaccessdic['ss_Ferrosilite'][6:11] ])]
        WG = WH-TK*WS
        Gex = WG*XEn*XFe
        dG_opx = dG_opx + Gex - 298.15*Sconf
        Rxn['min'] = [dG_opx, np.nan, S_opx, V_opx] + Cp_opx
        Rxn['min'].insert(0, Rxn['formula'])
        Rxn['min'].insert(1, ' R&H95, Stef2001')
        if self.Al_Si == 'pygcc':
            coeff = [-nH, nMg, nFe, nSi, nH2O]
            spec = ['H+', 'Mg++', 'Fe++', 'SiO2(aq)', 'H2O']
        elif self.Al_Si == 'Arnórsson_Stefánsson':
            coeff = [-nH, nMg, nFe, nSi, nH2O]
            spec = ['H+', 'Mg++', 'Fe++', 'H4SiO4(aq)', 'H2O']
        Rxn['spec'] = [x for x, y in zip(spec, coeff) if y != 0]
        Rxn['coeff'] = [y for y in coeff if y != 0]
        Rxn['nSpec'] = len(Rxn['coeff'])

        opx = Rxn['min']
        dGopxTP = heatcap( T = TC, P = P, method = 'HF76', Species_ppt = opx).dG
        dGrxn = -dGopxTP - nH*dGH + nMg*dGMg + nFe*dGFe + nH2O*dGH2O + nSi*dGSiO2aq
        logK_opx = (-dGrxn/R/(TK)/np.log(10))   # np.log10(np.exp(-dGrxn/R/(TK)))

        Rxn['min'][2] = dG_opx[(TC == Tref) & (P == Pref)][0]
        Rxn['V'] = Rxn['min'][5]  #,'%8.3f')
        Rxn['source'] = ' R&H95, Stef2001'
        elements  = ['%.4f' % nMg, 'Mg', '%.4f' % nFe, 'Fe', '%.4f' % nSi, 'Si', '3.0000', 'O']
        filters = [y for x, y in enumerate(elements) if x%2 == 0 and float(y) == 0]
        filters = [[x, x+1] for x, y in enumerate(elements) if y in filters]
        filters = [num for elem in filters for num in elem]
        Rxn['elements'] = [y for x, y in enumerate(elements) if x not in filters]

        if (TC[-1] == Tref) & (P[-1] == Pref):
            logK_opx = logK_opx[:-1]

        return logK_opx, Rxn

    def calclogKDiHedEnFe( self, nCa, XMg, TC, P, dbaccessdic, rhoEG, Dielec_method = None ):
        """
        This function calculates thermodynamic properties of solid solution of clinopyroxene
        minerals (Di, Hed, En and Fe) \n
        Parameters
        ----------
            nCa        : number of moles of Ca in formula unit (=1 for Di, Hed)
                           and must be greater than zero  \n
            XMg        : mole fraction of Mg
                            XMg = (nMg/(nFe + nMg))  \n
            TC         : temperature [°C]  \n
            P          : pressure [bar]  \n
            dbaccessdic : dictionary of species from direct-access database  \n
            Dielec_method   : specify either 'FGL97' or 'JN91' or 'DEW' as the method to calculate
                            dielectric constant (optional), if not specified default - 'JN91'
            rhoEG      : dictionary of water properties like  density (rho),
                            dielectric factor (E) and Gibbs Energy  (optional)
        Returns
        -------
            logK_cpx   : logarithmic K values   \n
            Rxn        : dictionary of reaction thermodynamic properties
        Usage
        -------
            The general usage of calclogKDiHedEnFe without the optional argument is as follows:  \n
            (1) Not on steam saturation curve:  \n
                [logK, Rxn] = calclogKDiHedEnFe(nCa, XMg, TC, P, dbaccessdic),  \n
                where T is temperature in celsius and P is pressure in bar;
            (2) On steam saturation curve:  \n
                [logK, Rxn] = calclogKDiHedEnFe(nCa, XMg, TC, 'T', dbaccessdic),   \n
                where T is temperature in celsius, followed with a quoted char 'T'  \n
                [logK, Rxn] = calclogKDiHedEnFe(nCa, XMg, P, 'P', dbaccessdic), \n
                where P is pressure in bar, followed with a quoted char 'P'.
            (3) Meanwhile, usage with any specific dielectric constant method ('FGL97') for
                condition not on steam saturation curve is as follows. Default method is 'JN91' \n
                [logK, Rxn] = calclogKDiHedEnFe(nCa, XMg, TC, P, dbaccessdic, Dielec_method = 'FGL97')
        """
        rho = rhoEG['rho'].ravel()
        E = rhoEG['E'].ravel()
        dGH2O = rhoEG['dGH2O'].ravel()
        Tref = 25; Pref = 1
        # if no reference Temperature and Pressure is found, append to the bottom
        if any((TC == Tref) & (P == Pref)) == False:
            water = iapws95(T = Tref, P = Pref)
            rhoref, dGH2Oref = water.rho, water.G
            Eref = water_dielec(T = Tref, P = Pref, Dielec_method = Dielec_method).E
            TC = np.concatenate([TC, np.ravel(Tref)])
            P = np.concatenate([P, np.ravel(Pref)])
            rho = np.concatenate([rho, np.ravel(rhoref)])
            E = np.concatenate([E, np.ravel(Eref)])
            dGH2O = np.concatenate([dGH2O, np.ravel(dGH2Oref)])
            rhoEG = {'rho': rho, 'E': E,  'dGH2O': dGH2O}

        TK = convert_temperature( TC, Out_Unit = 'K' )
        R = 1.9872041

        if nCa >= 1:
            XDi = XMg
            XHed = 1-XDi
            XEn = 0
            XFs = 0
        else:
            XDi = XMg*nCa
            XHed = (1 - XMg)*nCa
            Xopx = 1 -nCa
            XEn = XMg*Xopx
            XFs = (1 - XMg)*Xopx

        #start on M1 parms
        WH_M1 = -1910/J_to_cal
        WS_M1 = -1.05/J_to_cal
        if nCa < 1:
            # for the M1 (i.e., opx) component of cpx
            Mg_M1 = XEn*2 #  %multiplying by 2 b/c thermo props multiplied by 2
            Fe_M1 = XFs*2 #  %multiplying by 2 b/c thermo props multiplied by 2

            XFe_M1 = Fe_M1/(Fe_M1 + Mg_M1)
            XMg_M1 = Mg_M1/(Fe_M1 + Mg_M1)
            if (XEn == 0) | (XFs == 0):
                Sconf_M1 = 0 # if you don't do this, you take log of 0
            else:
                Sconf_M1 = -1*R*(XFe_M1*np.log(XFe_M1) + XMg_M1*np.log(XMg_M1))
        else: #No M1 if nCa >=1
            XMg_M1 = 0; Mg_M1 = 0
            XFe_M1 = 0; Fe_M1 = 0
            Sconf_M1 = 0

        WG_M1 = WH_M1 - TK*WS_M1
        Gex_M1 = WG_M1*XFe_M1*XMg_M1
        WG_M1_25 = WH_M1 - 298.15*WS_M1
        Gex_M1_25 = WG_M1_25*XFe_M1*XMg_M1

        # now start on the M2 part
        WH_M2 = 0./J_to_cal
        WS_M2 = 0./J_to_cal
        Fe_M2 = (XHed)
        Mg_M2 = (XDi)
        Ca_M2 = (XHed + XDi)
        Tot_M2 = Fe_M2 + Mg_M2 + Ca_M2

        XFe_M2 = Fe_M2/Tot_M2
        XMg_M2 = Mg_M2/Tot_M2
        XCa_M2 = Ca_M2/Tot_M2
        if (XHed == 0) | (XDi == 0):
            Sconf_M2 = 0
        else:
            #because of the entropy term in WG, Gex and dGol are T-dependent, thus must
            #do the logK calculation on a piecewise basis.
            Sconf_M2 = -1*R*( XFe_M2*np.log(XFe_M2) + XMg_M2*np.log(XMg_M2) + \
                             XCa_M2*np.log(XCa_M2))
        WG_M2 = WH_M2 - TK*WS_M2
        Gex_M2 = WG_M2*XDi*XHed
        WG_M2_25 = WH_M2 - 298.15*WS_M2
        Gex_M2_25 = WG_M2_25*XFe_M2*XMg_M2

        Rxn = {}
        Rxn['type']='cpx'
        nH = 4
        nMg = round(Mg_M1 + Mg_M2, 2)
        nFe = round(Fe_M1 + Fe_M2, 2)
        nCa = round(Ca_M2, 2)
        nSi = 2
        nH2O = 2
        if (XEn == 0):
            if (XFs == 0):
                if XDi == 1:
                    Rxn['name'] = 'Diopside'
                elif XHed == 1:
                    Rxn['name'] = 'Hedenbergite'
                else:
                    Rxn['name'] = 'Di%d' % round(XDi*100) + 'Hed%d' % round(XHed*100)
            elif (XHed == 0):
                Rxn['name'] = 'Di%d' % round(XDi*100) + 'Fe%d' % round(XFs*100)
            elif (XDi == 0):
                Rxn['name'] = 'Hed%d' % round(XHed*100) + 'Fe%d' % round(XFs*100)
            else:
                Rxn['name'] = 'Di%d' % round(XDi*100) + 'Hed%d' % round(XHed*100) + 'Fe%d' % round(XFs*100)
        elif (XFs == 0):
            if (XHed == 0):
                Rxn['name'] = 'Di%d' % round(XDi*100) + 'En%d' % round(XEn*100)
            elif (XDi == 0):
                Rxn['name'] = 'Hed%d' % round(XHed*100) + 'En%d' % round(XEn*100)
            else:
                Rxn['name'] = 'Di%d' % round(XDi*100) + 'Hed%d' % round(XHed*100) + 'En%d' % round(XEn*100)
        elif (XHed == 0):
            Rxn['name'] = 'Di%d' % round(XDi*100) + 'En%d' % round(XEn*100) + 'Fe%d' % round(XFs*100)
        elif (XDi == 0):
            Rxn['name'] = 'Hed%d' % round(XHed*100) + 'En%d' % round(XEn*100) + 'Fe%d' % round(XFs*100)
        else:
            Rxn['name'] = 'Di%d' % round(XDi*100) + 'Hed%d' % round(XHed*100) + 'En%d' % round(XEn*100) + 'Fe%d' % round(XFs*100)

        if (nCa == 0):
            Rxn['formula'] = 'Mg%1.2f' % nMg + 'Fe%1.2f' % nFe + 'Si%s' % nSi + 'O6'
        elif (nMg == 0):
            if (nCa == 1) and (nFe == 1):
                Rxn['formula'] = 'CaFe' + 'Si%s' % nSi + 'O6'
            else:
                Rxn['formula'] = 'Ca%1.2f' % nCa + 'Fe%1.2f' % nFe + 'Si%s' % nSi + 'O6'
        elif (nFe == 0):
            if (nCa == 1) and (nMg == 1):
                Rxn['formula'] = 'CaMg' + 'Si%s' % nSi + 'O6'
            else:
                Rxn['formula'] = 'Ca%1.2f' % nCa + 'Mg%1.2f' % nMg + 'Si%s' % nSi + 'O6'
        else:
            Rxn['formula'] = 'Ca%1.2f' % nCa + 'Mg%1.2f' % nMg + 'Fe%1.2f' % nFe + 'Si%s' % nSi + 'O6'
        Rxn['MW'] = nCa*MW['Ca'] + nMg*MW['Mg'] + nFe*MW['Fe'] + nSi*MW['Si'] + 6*MW['O']
        R = 1.9872041

        if self.Al_Si == 'pygcc':
            dGSiO2aq  = supcrtaq(TC, P, dbaccessdic['SiO2(aq)'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        elif self.Al_Si == 'Arnórsson_Stefánsson':
            dGSiO2aq  = supcrtaq(TC, P, dbaccessdic['H4SiO4(aq)'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
            nH2O = nH2O - 2*nSi

        dGH = supcrtaq(TC, P, dbaccessdic['H+'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        dGFe = supcrtaq(TC, P, dbaccessdic['Fe++'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        dGMg = supcrtaq(TC, P, dbaccessdic['Mg++'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        dGCa = supcrtaq(TC, P, dbaccessdic['Ca++'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)

        # Addition of M1 and M2 sites
        Sconf = Sconf_M1 + Sconf_M2
        dG_cpx_noGex = 2*XFs*dbaccessdic['ss_Ferrosilite'][2] + 2*XEn*dbaccessdic['ss_Clinoenstatite'][2] + \
            XHed*dbaccessdic['ss_Hedenbergite'][2] + XDi*dbaccessdic['ss_Diopside'][2]
        dG_cpx_25 = dG_cpx_noGex + Gex_M1_25 + Gex_M2_25

        S_cpx = 2*XFs*dbaccessdic['ss_Ferrosilite'][4] + 2*XEn*dbaccessdic['ss_Clinoenstatite'][4] + \
            XHed*dbaccessdic['ss_Hedenbergite'][4] + XDi*dbaccessdic['ss_Diopside'][4] + Sconf
        V_cpx = 2*XFs*dbaccessdic['ss_Ferrosilite'][5] + 2*XEn*dbaccessdic['ss_Clinoenstatite'][5] + \
            XHed*dbaccessdic['ss_Hedenbergite'][5] + XDi*dbaccessdic['ss_Diopside'][5]
        Cp_cpx = [i + j + k + l for i, j, k, l in zip([2*XFs*a for a in dbaccessdic['ss_Ferrosilite'][6:11] ],
                                                      [2*XEn*b for b in dbaccessdic['ss_Clinoenstatite'][6:11] ],
                                                      [XHed*c for c in dbaccessdic['ss_Hedenbergite'][6:11] ],
                                                      [XDi*d for d in dbaccessdic['ss_Diopside'][6:11] ] ) ]
        # because of the entropy term in WG, Gex and dGol are T-dependent, thus must do the logK calculation on a piecewise basis.
        dG_cpx = dG_cpx_25 + Gex_M1 + Gex_M2 - TK*Sconf
        Rxn['min'] = [dG_cpx, np.nan, S_cpx, V_cpx] + Cp_cpx
        Rxn['min'].insert(0, Rxn['formula'])
        Rxn['min'].insert(1,' R&H95, Stef2001')
        if self.Al_Si == 'pygcc':
            coeff = [-nH, nCa, nMg, nFe, nSi, nH2O]
            spec = ['H+', 'Ca++', 'Mg++', 'Fe++', 'SiO2(aq)', 'H2O']
        elif self.Al_Si == 'Arnórsson_Stefánsson':
            coeff = [-nH, nCa, nMg, nFe, nSi, nH2O]
            spec = ['H+', 'Ca++', 'Mg++', 'Fe++', 'H4SiO4(aq)', 'H2O']

        Rxn['spec'] = [x for x, y in zip(spec, coeff) if y != 0]
        Rxn['coeff'] = [y for y in coeff if y != 0]
        Rxn['nSpec'] = len(Rxn['coeff'])

        cpx = Rxn['min']
        dGcpxTP = heatcap( T = TC, P = P, method = 'HF76', Species_ppt = cpx).dG
        dGrxn = - dGcpxTP - nH*dGH + nCa*dGCa + nMg*dGMg + nFe*dGFe + nH2O*dGH2O + nSi*dGSiO2aq
        logK_cpx = (-dGrxn/R/(TK)/np.log(10))   # np.log10(np.exp(-dGrxn/R/(TK)))

        Rxn['min'][2] = dG_cpx[(TC == Tref) & (P == Pref)][0]
        Rxn['V'] = Rxn['min'][5]
        Rxn['source'] = ' R&H95, Stef2001'
        elements  = ['%.4f' % nCa, 'Ca', '%.4f' % nMg, 'Mg', '%.4f' % nFe, 'Fe', '%.4f' % nSi, 'Si', '6.0000', 'O']
        filters = [y for x, y in enumerate(elements) if x%2 == 0 and float(y) == 0]
        filters = [[x, x+1] for x, y in enumerate(elements) if y in filters]
        filters = [num for elem in filters for num in elem]
        Rxn['elements'] = [y for x, y in enumerate(elements) if x not in filters]

        if (TC[-1] == Tref) & (P[-1] == Pref):
            logK_cpx = logK_cpx[:-1]

        return logK_cpx, Rxn

    def calclogKAbOr( self, XAb, TC, P, dbaccessdic, rhoEG, Dielec_method = None):
        """
        This function calculates thermodynamic properties of solid solution of Alkaline-Feldspar minerals

        Parameters
        ----------
            XAb        : volume fraction of Albite  \n
            TC         : temperature [°C]  \n
            P          : pressure [bar]  \n
            dbaccessdic : dictionary of species from direct-access database  \n
            Dielec_method   : specify either 'FGL97' or 'JN91' or 'DEW' as the method to calculate
                            dielectric constant (optional), if not specified default - 'JN91'
            rhoEG      : dictionary of water properties like  density (rho),
                           dielectric factor (E) and Gibbs Energy  (optional)
        Returns
        -------
            logKalkfeld: logarithmic K values   \n
            Rxn        : dictionary of reaction thermodynamic properties
        Usage
        -------
            The general usage of calclogKAnAb without the optional argument is as follows:  \n
            (1) Not on steam saturation curve:  \n
                [logK, Rxn] = calclogKAbOr(XAb, TC, P, dbaccessdic),  \n
                where T is temperature in celsius and P is pressure in bar;
            (2) On steam saturation curve:  \n
                [logK, Rxn] = calclogKAbOr(XAb, TC, 'T', dbaccessdic),   \n
                where T is temperature in celsius, followed with a quoted char 'T'  \n
                [logK, Rxn] = calclogKAbOr(XAb, P, 'P', dbaccessdic), \n
                where P is pressure in bar, followed with a quoted char 'P'.
            (3) Meanwhile, usage with any specific dielectric constant method ('FGL97') for
                condition not on steam saturation curve is as follows. Default method is 'JN91' \n
                [logK, Rxn] = calclogKAbOr(XAb, TC, P, dbaccessdic, Dielec_method = 'FGL97')
        """
        rho = rhoEG['rho'].ravel()
        E = rhoEG['E'].ravel()
        dGH2O = rhoEG['dGH2O'].ravel()
        Tref = 25; Pref = 1
        # if no reference Temperature and Pressure is found, append to the bottom
        if any((TC == Tref) & (P == Pref)) == False:
            water = iapws95(T = Tref, P = Pref)
            rhoref, dGH2Oref = water.rho, water.G
            Eref = water_dielec(T = Tref, P = Pref, Dielec_method = Dielec_method).E
            TC = np.concatenate([TC, np.ravel(Tref)])
            P = np.concatenate([P, np.ravel(Pref)])
            rho = np.concatenate([rho, np.ravel(rhoref)])
            E = np.concatenate([E, np.ravel(Eref)])
            dGH2O = np.concatenate([dGH2O, np.ravel(dGH2Oref)])
            rhoEG = {'rho': rho, 'E': E,  'dGH2O': dGH2O}

        TK = convert_temperature( TC, Out_Unit = 'K' )
        Rxn = {}
        Rxn['type'] = 'Alk feldspar'
        XOr = 1 - XAb
        nNa = XAb
        nK = (1 - XAb)
        nH = 4
        nAl = 1
        nH2O = 2
        nSi = 3
        if XAb == 1:
            Rxn['name'] ='Albite'
            Rxn['formula'] ='NaAlSi3O8'
        elif XAb == 0:
            Rxn['name'] ='K-Feldspar'
            Rxn['formula'] ='KAlSi3O8'
        else:
            Rxn['name'] = 'Alkfeld%d' % (XAb*100)
            Rxn['formula'] = 'Na%1.2f' % nNa + 'K%1.2f' % nK + 'Al%1.2f' % nAl + 'Si%1.2f' % nSi + 'O8'

        Rxn['MW'] = nNa* MW['Na'] + nK*MW['K'] + nAl*MW['Al'] + nSi*MW['Si'] + 8*MW['O']
        R = 1.9872041
        WH = 23800/J_to_cal
        WS = 0/J_to_cal

        if self.Al_Si == 'pygcc':
            dGAl = supcrtaq(TC, P, dbaccessdic['Al+++'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
            dGSiO2aq  = supcrtaq(TC, P, dbaccessdic['SiO2(aq)'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
            dGH = supcrtaq(TC, P, dbaccessdic['H+'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        elif self.Al_Si == 'Arnórsson_Stefánsson':
            dGAl = supcrtaq(TC, P, dbaccessdic['Al(OH)4-'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
            dGSiO2aq  = supcrtaq(TC, P, dbaccessdic['H4SiO4(aq)'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
            nH2O = nH2O + 2*nSi

        dGNa = supcrtaq(TC, P, dbaccessdic['Na+'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        dGK = supcrtaq(TC, P, dbaccessdic['K+'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)

        if (XAb < 1) & (XAb != 0):
            Sconf = -R*(XOr*np.log(XOr) + XAb*np.log(XAb))
        else:
            Sconf = 0

        dGalk = XOr*dbaccessdic['ss_K-feldspar'][2] + XAb*dbaccessdic['ss_Albite_high'][2]
        Salk = XOr*dbaccessdic['ss_K-feldspar'][4] + XAb*dbaccessdic['ss_Albite_high'][4] + Sconf
        Valk = (XOr*dbaccessdic['ss_K-feldspar'][5] + XAb*dbaccessdic['ss_Albite_high'][5]) #*(P - 1)
        Cpalk = [a + b for a, b in zip([XOr*x for x in dbaccessdic['ss_K-feldspar'][6:11] ],
                                       [XAb*y for y in dbaccessdic['ss_Albite_high'][6:11] ])]
        WG = WH - TK*WS
        Gex = WG*XAb*XOr
        dGalk = dGalk + Gex - 298.15*Sconf
        Rxn['min'] = [dGalk, np.nan, Salk, Valk] + Cpalk
        Rxn['min'].insert(0, Rxn['formula'])
        Rxn['min'].insert(1,' R&H95, A&S99')
        alk = Rxn['min']
        dGalkTP = heatcap( T = TC, P = P, method = 'HF76', Species_ppt = alk).dG
        if self.Al_Si == 'pygcc':
            coeff = [-nH, nAl, nNa, nK, nSi, nH2O]
            spec = ['H+', 'Al+++', 'Na+', 'K+', 'SiO2(aq)', 'H2O']
        elif self.Al_Si == 'Arnórsson_Stefánsson':
            coeff = [nAl, nNa, nK, nSi, -nH2O]
            spec = ['Al(OH)4-', 'Na+', 'K+', 'H4SiO4(aq)', 'H2O']
        Rxn['spec'] = [x for x, y in zip(spec, coeff) if y!=0]
        Rxn['coeff'] = [y for y in coeff if y!=0]
        Rxn['nSpec'] = len(Rxn['coeff'])

        if self.Al_Si == 'pygcc':
            dGrxn = - dGalkTP - nH*dGH + nAl*dGAl + nH2O*dGH2O + nNa*dGNa+ nK*dGK + nSi*dGSiO2aq
        elif self.Al_Si == 'Arnórsson_Stefánsson':
            dGrxn = -dGalkTP + nAl*dGAl - nH2O*dGH2O + nNa*dGNa+ nK*dGK + nSi*dGSiO2aq
        logKalkfeld = (-dGrxn/R/(TK)/np.log(10))   # np.log10(np.exp(-dGrxn/R/(TK)))

        Rxn['min'][2] = dGalk[(TC == Tref) & (P == Pref)][0]
        Rxn['V'] = Rxn['min'][5]  #,'%8.3f')
        Rxn['source'] = ' R&H95, A&S99'
        elements  = ['%.4f' % nNa, 'Na', '%.4f' % nK, 'K', '%.4f' % nAl, 'Al', '%.4f' % nSi, 'Si', '8.0000', 'O']
        filters = [y for x, y in enumerate(elements) if x%2 == 0 and float(y) == 0]
        filters = [[x, x+1] for x, y in enumerate(elements) if y in filters]
        filters = [num for elem in filters for num in elem]
        Rxn['elements'] = [y for x, y in enumerate(elements) if x not in filters]

        if (TC[-1] == Tref) & (P[-1] == Pref):
            logKalkfeld = logKalkfeld[:-1]

        return logKalkfeld, Rxn

    def calclogKBiotite( self, XPh, TC, P, dbaccessdic, rhoEG, Dielec_method = None):
        """
        This function calculates thermodynamic properties of solid solution of Biotite minerals

        Parameters
        ----------
            XAb        : volume fraction of Albite  \n
            TC         : temperature [°C]  \n
            P          : pressure [bar]  \n
            dbaccessdic : dictionary of species from direct-access database  \n
            Dielec_method   : specify either 'FGL97' or 'JN91' or 'DEW' as the method to calculate
                            dielectric constant (optional), if not specified default - 'JN91'
            rhoEG      : dictionary of water properties like  density (rho),
                           dielectric factor (E) and Gibbs Energy  (optional)
        Returns
        -------
            logKalkfeld: logarithmic K values   \n
            Rxn        : dictionary of reaction thermodynamic properties
        Usage
        -------
            The general usage of calclogKAnAb without the optional argument is as follows:  \n
            (1) Not on steam saturation curve:  \n
                [logK, Rxn] = calclogKAbOr(XAb, TC, P, dbaccessdic),  \n
                where T is temperature in celsius and P is pressure in bar;
            (2) On steam saturation curve:  \n
                [logK, Rxn] = calclogKAbOr(XAb, TC, 'T', dbaccessdic),   \n
                where T is temperature in celsius, followed with a quoted char 'T'  \n
                [logK, Rxn] = calclogKAbOr(XAb, P, 'P', dbaccessdic), \n
                where P is pressure in bar, followed with a quoted char 'P'.
            (3) Meanwhile, usage with any specific dielectric constant method ('FGL97') for
                condition not on steam saturation curve is as follows. Default method is 'JN91' \n
                [logK, Rxn] = calclogKAbOr(XAb, TC, P, dbaccessdic, Dielec_method = 'FGL97')
        """
        rho = rhoEG['rho'].ravel()
        E = rhoEG['E'].ravel()
        dGH2O = rhoEG['dGH2O'].ravel()
        Tref = 25; Pref = 1
        # if no reference Temperature and Pressure is found, append to the bottom
        if any((TC == Tref) & (P == Pref)) == False:
            water = iapws95(T = Tref, P = Pref)
            rhoref, dGH2Oref = water.rho, water.G
            Eref = water_dielec(T = Tref, P = Pref, Dielec_method = Dielec_method).E
            TC = np.concatenate([TC, np.ravel(Tref)])
            P = np.concatenate([P, np.ravel(Pref)])
            rho = np.concatenate([rho, np.ravel(rhoref)])
            E = np.concatenate([E, np.ravel(Eref)])
            dGH2O = np.concatenate([dGH2O, np.ravel(dGH2Oref)])
            rhoEG = {'rho': rho, 'E': E,  'dGH2O': dGH2O}

        TK = convert_temperature( TC, Out_Unit = 'K' )
        Rxn = {}
        Rxn['type'] = 'Biotite'
        XAn = 1 - XPh
        nFe = 3*XAn
        nMg = 3*XPh
        nK = 1
        nH = 10
        nAl = 1
        nH2O = 6
        nSi = 3
        if XPh == 0:
            Rxn['name'] ='Annite'
            Rxn['formula'] ='KFe3AlSi3O10(OH)2'
        elif XPh == 1:
            Rxn['name'] ='Phlogopite'
            Rxn['formula'] ='KMg3AlSi3O10(OH)2'
        else:
            Rxn['name'] = 'Biotite_Mg_Fe_ratio%s' % np.round(nMg/nFe, 2)
            Rxn['formula'] = 'K%1.2f' % nK + 'Mg%1.2f' % nMg + 'Fe%1.2f' % nFe + 'Al%1.2f' % nAl + 'Si%1.2f' % nSi + 'O10(OH)2'

        Rxn['MW'] = nK*MW['K'] + nMg* MW['Mg'] + nFe* MW['Fe'] + nAl*MW['Al'] + nSi*MW['Si'] + 12*MW['O'] + 2*MW['H']
        R = 1.9872041
        WH = 9000/J_to_cal
        WS = 0/J_to_cal

        dGAl = supcrtaq(TC, P, dbaccessdic['Al+++'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        dGSiO2aq  = supcrtaq(TC, P, dbaccessdic['SiO2(aq)'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)

        dGH = supcrtaq(TC, P, dbaccessdic['H+'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        dGMg = supcrtaq(TC, P, dbaccessdic['Mg++'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        dGFe = supcrtaq(TC, P, dbaccessdic['Fe++'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)
        dGK = supcrtaq(TC, P, dbaccessdic['K+'], Dielec_method = Dielec_method, ThermoInUnit = self.ThermoInUnit, **rhoEG)

        if (XAn < 1) & (XAn != 0):
            Sconf = -3*R*(XAn*np.log(XAn) + XPh*np.log(XPh))
        else:
            Sconf = 0

        dGbiot = XAn*dbaccessdic['ss_Annite'][2] + XPh*dbaccessdic['ss_Phlogopite'][2]
        Sbiot = XAn*dbaccessdic['ss_Annite'][4] + XPh*dbaccessdic['ss_Phlogopite'][4] + Sconf
        Vbiot = (XAn*dbaccessdic['ss_Annite'][5] + XPh*dbaccessdic['ss_Phlogopite'][5])
        Cpbiot = [a + b for a, b in zip([XAn*x for x in dbaccessdic['ss_Annite'][6:11] ],
                                       [XPh*y for y in dbaccessdic['ss_Phlogopite'][6:11] ])]
        WG = WH - TK*WS
        Gex = WG*XAn*XPh
        dGbiot = dGbiot + Gex - 298.15*Sconf
        Rxn['min'] = [dGbiot, np.nan, Sbiot, Vbiot] + Cpbiot
        Rxn['min'].insert(0, Rxn['formula'])
        Rxn['min'].insert(1,' R&H95, P&H99')
        biot = Rxn['min']
        dGbiotTP = heatcap( T = TC, P = P, method = 'HF76', Species_ppt = biot).dG
        coeff = [-nH, nAl, nK, nMg, nFe, nSi, nH2O]
        spec = ['H+', 'Al+++', 'K+', 'Mg++', 'Fe++', 'SiO2(aq)', 'H2O']
        Rxn['spec'] = [x for x, y in zip(spec, coeff) if y!=0]
        Rxn['coeff'] = [y for y in coeff if y!=0]
        Rxn['nSpec'] = len(Rxn['coeff'])

        dGrxn = - dGbiotTP - nH*dGH + nAl*dGAl + nMg*dGMg + nFe*dGFe + nK*dGK + nSi*dGSiO2aq + nH2O*dGH2O
        logKbiot = (-dGrxn/R/(TK)/np.log(10))   # np.log10(np.exp(-dGrxn/R/(TK)))

        Rxn['min'][2] = dGbiot[(TC == Tref) & (P == Pref)][0]
        Rxn['V'] = Rxn['min'][5]
        Rxn['source'] = ' R&H95, P&H99'
        elements  = ['%.4f' % nK, 'K', '%.4f' % nMg, 'Mg', '%.4f' % nFe, 'Fe', '%.4f' % nAl, 'Al', '%.4f' % nSi, 'Si', '12.0000', 'O', '2.0000', 'H']
        filters = [y for x, y in enumerate(elements) if x%2 == 0 and float(y) == 0]
        filters = [[x, x+1] for x, y in enumerate(elements) if y in filters]
        filters = [num for elem in filters for num in elem]
        Rxn['elements'] = [y for x, y in enumerate(elements) if x not in filters]

        if (TC[-1] == Tref) & (P[-1] == Pref):
            logKbiot = logKbiot[:-1]

        return logKbiot, Rxn

