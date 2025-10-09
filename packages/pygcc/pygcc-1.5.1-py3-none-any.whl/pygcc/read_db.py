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

import re, os, pandas as pd
import textwrap
J_to_cal = 4.184

# from sys import platform

def findcodecs(filename):
    """Function to find the name of the encoding used to decode or encode any file    """
    data = open(filename, "rb").read()
    # data = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), 'rb').read()
    all_codecs = ['ascii', 'latin_1', 'utf_8']
    f = [0]*len(all_codecs)
    for j, i in enumerate(all_codecs):
        try:
            decoded = data.decode(i)
        except UnicodeDecodeError:
            f[j] = False
        else:
            for ch in decoded:
                if i == 'utf_8' and 0xD800 <= ord(ch) <= 0xDFFF:
                    f[j] = False
            f[j] = True
    if all(f) == True:
        return None
    else:
        return all_codecs[1]
        # if platform == "darwin": # OS X
        #     return all_codecs[1]
        # elif platform in ["linux", "linux2", "win32"]:   # linux and # Windows...
        #     return None


class db_reader:
    """Class to read direct-access and source thermodynamic database

    Parameters
    ----------
        dbaccess : string
            path of the direct-access/sequential-access database, optional, default is speq21
        dbBerman_dir : string
            path of the Berman mineral database, optional
        dbHP_dir : string
            path of the supcrtbl mineral and gas database, optional
        sourcedb : string
            path of the source database, optional
        sourceformat : string
            specify the source database format, either 'GWB', 'EQ36' or 'PHREEQC', optional
        dbaccessformat : string, optional
            specify the direct-access/sequential-access database format, either 'speq' or 'supcrtbl', default is 'speq'
        sourcedb_codecs : string
            specify the name of the encoding used to decode or encode the sourcedb file, optional
        dbaccess_codecs : string
            specify the name of the encoding used to decode or encode the dbaccess file, optional

    Returns
    -------
        dbaccessdic : dict
            dictionary of minerals, gases, redox and aqueous species     \n
        dbaccess : string
            direct-access database file name     \n
        sourcedic : dict
            dictionary of reaction coefficients and species   \n
        specielist : list
            list of species segmented into the different categories [element, basis, redox, aqueous, minerals, gases, oxides]   \n
        speciecat : list
            list of species categories listed in 'specielist'   \n
        chargedic : dict
            dictionary of charges of species   \n
        MWdic : dict
            dictionary of MW of species   \n
        Mineraltype : dict
            mineral type for minerals   \n
        fugacity_info : dict
            fugacity information as stored in new tdat database for chi and critical ppts   \n
        Sptype : dict
            specie types and eq3/6 and revised date info   \n
        Elemlist : dict
            dictionary of elements and coefficients   \n
        Rd : list
            each line of sourcedb in an array   \n
        d : dict
            dictionary of database headers and corresponding line numbers in Rd  \n

    Examples
    --------
    >>> ps = db_reader(sourcedb = './default_db/thermo.com.dat',
                       sourceformat = 'gwb',
                       dbaccess = './default_db/speq23.dat')
    >>> ps.sourcedic, ps.dbaccessdic, ps.specielist


    """
    kwargs = {"dbaccess": None,
              "dbBerman_dir": None,
              "dbHP_dir": None,
              "sourcedb": None,
              "sourceformat": None,
              "dbaccessformat": 'speq',
              "sourcedb_codecs": None,
              "dbaccess_codecs": None}

    def __init__(self, **kwargs):
        self.kwargs = db_reader.kwargs.copy()
        self.Rd = {}
        self.d = {}
        self.__calc__(**kwargs)

    def __calc__(self, **kwargs):
        self.kwargs.update(kwargs) 
        if self.kwargs["dbaccess"] == 'speq23':
            self.dbaccess_dir = './default_db/speq23.dat'
            self.dbaccess_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.dbaccess_dir)
        elif self.kwargs["dbaccess"] == 'speq23_dimer':
            self.dbaccess_dir = './default_db/speq23_dimer.dat'
            self.dbaccess_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.dbaccess_dir)
        elif self.kwargs["dbaccess"] == 'speq21_dimer':
            self.dbaccess_dir = './default_db/speq21_dimer.dat'
            self.dbaccess_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.dbaccess_dir)
        elif self.kwargs['dbaccess'] is None:
            self.dbaccess_dir = './default_db/speq21.dat'
            self.dbaccess_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.dbaccess_dir)
        else:
            self.dbaccess_dir = self.kwargs["dbaccess"]
        self.dbaccessformat = self.kwargs["dbaccessformat"]
        self.dbBerman_dir = self.kwargs["dbBerman_dir"]
        self.dbHP_dir = self.kwargs["dbHP_dir"]
        self.sourcedb_dir = None if self.kwargs["sourcedb"] is None else self.kwargs["sourcedb"]

        if self.kwargs["sourceformat"] is not None:
            # GWB
            if self.kwargs["sourceformat"].lower() == 'gwb': # options for all default database included with PyGCC
                if self.kwargs["sourcedb"] == 'thermo.com':
                    self.sourcedb = './default_db/thermo.com.dat'
                    self.sourcedb_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.sourcedb)
                elif self.kwargs["sourcedb"] == 'thermo.2021':
                    self.sourcedb = './default_db/thermo.2021.dat'
                    self.sourcedb_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.sourcedb)
                elif self.kwargs["sourcedb"] == 'thermo_latest':
                    self.sourcedb = './default_db/thermo_latest.tdat'
                    self.sourcedb_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.sourcedb)
                elif self.kwargs["sourcedb"] == 'thermo_cemdata_mar':
                    self.sourcedb = './default_db/thermo_cemdata_mar.tdat'
                    self.sourcedb_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.sourcedb)
                elif self.kwargs["sourcedb"] is None:
                    self.sourcedb = './default_db/thermo.com.tdat'
                    self.sourcedb_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.sourcedb)
                else:
                    self.sourcedb_dir = self.kwargs["sourcedb"]
            # EQ36
            elif self.kwargs["sourceformat"].lower() == 'eq36':
                if self.kwargs["sourcedb"] == 'data0' or self.kwargs["sourcedb"] is None:
                    self.sourcedb = './default_db/data0.dat'
                    self.sourcedb_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.sourcedb)
                else:
                    self.sourcedb_dir = self.kwargs["sourcedb"]
            # PHREEQC
            elif self.kwargs["sourceformat"].lower() == 'phreeqc':
                # TODO - add more source databases that are phreeqc formats to default_db folder
                if self.kwargs["sourcedb"] is None:
                    self.sourcedb = "./default_db/phreeqc.dat"
                    self.sourcedb_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.sourcedb)

        # get codecs for dbaccess and sourcedb
        if self.kwargs['dbaccess_codecs'] is None:
            self.dbaccess_codecs = findcodecs(self.dbaccess_dir)
        else:
            self.dbaccess_codecs = self.kwargs['dbaccess_codecs']

        if self.kwargs["sourcedb"] is not None and self.kwargs['sourcedb_codecs'] is None:
            self.sourcedb_codecs = findcodecs(self.sourcedb_dir)
        else:
            self.sourcedb_codecs = self.kwargs['sourcedb_codecs']

        if self.dbaccess_dir is not None:
            self.dbaccess = self.dbaccess_dir.split('/')[-1]
        if self.dbaccess_dir is not None:
            self.readAqspecdb() #
        if self.sourcedb_dir is not None:
            if self.kwargs["sourceformat"].lower() == 'gwb':
                self.readSourceGWBdb()
            elif self.kwargs["sourceformat"].lower() == 'eq36':
                self.readSourceEQ36db()
            elif self.kwargs["sourceformat"].lower() == 'phreeqc':
                self.readSourcePHREEQCdb()

    def readAqspecdb(self):
        """
        This function reads direct access thermodynamic database and can add other database sources
        at the bottom returns all constants of Maier-Kelley power function  for minerals and gases
        (dG [cal/mol], dH [cal/mol], S [cal/mol-K], V [cm3/mol] a [cal/mol-K], b [*10**3 cal/mol/K^2],
         c [*10^-5 cal/mol/K], Ttrans [K], Htr [cal/mol], Vtr [cm³/mol], dPdTtr [bar/K] ) and
        aqueous species (dG [cal/mol], dH [cal/mol], S [cal/mol-K], V [cm3/mol], a1 [*10 cal/mol/bar],
        a2 [*10**-2 cal/mol], a3 [cal-K/mol/bar], a4 [*10**-4 cal-K/mol], c1 [cal/mol/K], c2 [*10**-4 cal-K/mol],
        ω [*10**-5 cal/mol] ) packed into a dbacess dictionary. In addition, the function can read Berman's
        mineral properties such as (dG [J/mol], dH [J/mol], S [J/mol-K], V [cm³/mol], k0, k1, k2, k3,
        v1 [*10^5 K^-1], v2 [*10^5 K^-2], v3 [*10^5 bar^-1], v4 [*10^8 bar^-2], dTdP [K/bar], Tlambda [K],
        Tref [K], l1 [(J/mol)^0.5/K], l2 [(J/mol)^0.5/K^2], DtH, d0 [J/mol], d1 [J/mol], d2 [J/mol],
        d3 [J/mol], d4 [J/mol], d5 [J/mol], Tmin [K], Tmax [K]). In addition, the function can read supcrtbl's
        mineral and gas properties such as (dG [kJ/mol], dH [kJ/mol], S [J/mol-K], V [J/bar], a [kJ/mol-K],
        b [*10^5 kJ/mol/K^2], c [kJ-mol-K], d [kJ/mol/K^0.5], alpha [*10^5 K^-1], kappa0 [kbar],
        kappa0_d [kbar], kappa0_dd [kbar], n_atom [-], Tc0 [K], Smax [J/mol-K], Vmax [J/bar], dH [KJ/mol],
        dV [J/bar], W [kJ/mol], Wv [J/bar], n [-], SF [-]) \n
        Parameters
        ----------
            dbaccess        filename and location of the direct-access database     \n
            dbBerman_dir    filename and location of the Berman mineral database     \n
            dbHP_dir        filename and location of the supcrtbl (Holland and Powell) mineral and gas database     \n
        Returns
        ----------
            dbaccessdic      dictionary of minerals, gases, redox and aqueous species     \n
            dbaccess        dat file name     \n
        Usage:
        ----------
        [dbaccessdic, dbname] = readAqspecdb(dbaccess)
        """
        # check if its a single liner data
        codecs = self.dbaccess_codecs
        with open(self.dbaccess_dir, encoding = codecs) as g:
            Rd = g.readlines()
        header_counter = [p for p, k in enumerate(Rd) if k.startswith('*************')]

        def multiline_reader(Rd, counter, dbaccess_dir):
            db_dic = {}; last_gas = ''
            for i in range(len(Rd)): #
                s1 = Rd[i].rstrip('\n').strip()
                if (not s1.lstrip().startswith(('*', '!'))) and (s1.lstrip('0123456789.- \t') != ""):
                    if (s1[:3] != 'ref') and (s1[:3] != 'REF') and (s1.split()[0] not in ['minerals', 'gases', 'gas', 'aqueous', 'abandoned']):
                        name = s1.strip().split()[0]
                        name = name.replace('+4', '++++') if name.endswith('+4') else name.replace('+3', '+++') if name.endswith('+3') else name.replace('+2', '++') if name.endswith('+2') else name.replace('-4', '----') if name.endswith('-4') else name.replace('-3', '---') if name.endswith('-3') else name.replace('-2', '--') if name.endswith('-2') else name
                        if self.dbaccessformat.lower() == 'supcrtbl':
                            name = name.title() if not name.endswith(('+', '-', ",aq", "(S)", "(am)",
                                                                      'dis', 'ord')) else name.capitalize() if 'ACID' in name else name
                            name = name.replace(",aq", "(aq)").replace(",G", "(g)").replace("(S)", "(s)").replace("(Am)", "(am)").replace("(Alpha)", "(alpha)").replace("(Beta)", "(beta)")
                            name = name.replace("-acid", "_acid").replace("(High)", "_high").replace("(Low)", "_low").replace(" anhyd", "_anhyd").replace(" hydr", "_hydr")
                            name = name.replace("-Lo", "_low").replace("(-Hi)", "_high").replace("(oh)", "(OH)").replace("(Oh)", "(OH)").replace("(G)", "(g)").replace("(Ordered)", "-ord")

                        if len(s1.split()) > 1:
                            formula = s1.split()[1]
                        else:
                            formula = ''
                        s2 = Rd[i + 1].strip()
                        dates = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
                        if (s2[:3] != 'ref') and (s2[:3] != 'REF') and (s2[0].lstrip('0123456789.,- ') != '') and any(k in s2.split()[-1].lower() for k in dates) == False:
                            s3 = Rd[i+2]; s4 = Rd[i+3]; s5 = Rd[i+4];
                            if i >= len(Rd) - 5:
                                s6 = 'Null'; s7 = 'Null'; s8 = 'Null';
                                s9 = 'Null'; s10 = 'Null'; s11 = 'Null';
                            elif i >= len(Rd) - 6:
                                s6  = Rd[i + 5]; s7 = 'Null'; s8 = 'Null';
                                s9 = 'Null'; s10 = 'Null'; s11 = 'Null';
                            else:
                                s6  = Rd[i + 5]; s7 = Rd[i + 6]; s8 = Rd[i + 7];
                                s9 = Rd[i + 8]; s10 = Rd[i + 9]; s11 = Rd[i + 10];

                            if s3.strip()[:3] == 'ref':
                                ref = s3#.split()[0][4:]
                            else:
                                ref = s3#.split()[0]
                            if (s6.lower().islower() == True) | s6.startswith('*', 0):
                                params = s4.split() + s5.split()
                            elif (s7.lower().islower() == True) | s7.startswith('*', 0):
                                params = s4.split() + s5.split() + s6.split()
                            elif (s8.lower().islower() == True) | s8.startswith('*', 0):
                                params = s4.split() + s5.split() + s6.split() + s7.split()
                            elif (s9.lower().islower() == True) | s9.startswith('*', 0):
                                params = s4.split() + s5.split() + s6.split() + s7.split() + s8.split()
                            elif (s10.lower().islower() == True) | s10.startswith('*', 0):
                                params = s4.split() + s5.split() + s6.split() + s7.split() + s8.split() + \
                                    s9.split()
                            elif (s11.lower().islower() == True) | s11.startswith('*', 0):
                                params = s4.split() + s5.split() + s6.split() + s7.split() + s8.split() + \
                                    s9.split() + s10.split()
                            else:
                                params = s4.split() + s5.split() + s6.split() + s7.split() + s8.split() + \
                                    s9.split() + s10.split() + s11.split()
                            params = [float(i) if float(i) != 999999 else 0 for i in params]
                            counter += 1
                            if name in db_dic.keys():
                                print('Duplicate found for species "%s" in %s' % (name, dbaccess_dir.split('/')[-1]))
                                continue
                            else:
                                db_dic[name] = [formula, ref] + params

                            if len(s5.split()) != 0 and len(s6.split()) and (s5.strip() == '' and s6.strip() == ''):
                                break
                            elif len(s7.split()) != 0 and len(s6.split()) and (s6.strip() == '' and s7.strip() == ''):
                                break
                            elif len(s7.split()) != 0 and len(s8.split()) and (s7.strip() == '' and s8.strip() == ''):
                                break
                            elif len(s8.split()) != 0 and len(s9.split()) and (s8.strip() == '' and s9.strip() == ''):
                                break
                            elif len(s9.split()) != 0 and len(s10.split()) and (s9.strip() == '' and s10.strip() == ''):
                                break
                            elif len(s6.split()) != 0 and (s6.split()[-1] in ['(nmin1)', '(nmin2)', '(nmin3)', '(nmin4)', '(ngas)', '(naqs)']):
                                break
                            elif len(s7.split()) != 0 and (s7.split()[-1] in ['(nmin1)', '(nmin2)', '(nmin3)', '(nmin4)', '(ngas)', '(naqs)']):
                                break
                            elif len(s8.split()) != 0 and (s8.split()[-1] in ['(nmin1)', '(nmin2)', '(nmin3)', '(nmin4)', '(ngas)', '(naqs)']) :
                                break
                            elif len(s9.split()) != 0 and (s9.split()[-1] in ['(nmin1)', '(nmin2)', '(nmin3)', '(nmin4)', '(ngas)', '(naqs)']) :
                                break
                            elif len(s10.split()) != 0 and (s10.split()[-1] in ['(nmin1)', '(nmin2)', '(nmin3)', '(nmin4)', '(ngas)', '(naqs)']):
                                break
                            elif s9.strip('*').strip() == '' and s10.strip('*').strip() == '' and s11.strip('*').strip() == '':
                                break
                if s1.split()[0] in ['gases', 'gas']:
                    last_mineral = list(db_dic.keys())[-1] # aqueous
                if s1.lstrip().split()[0] in ['aqueous']:
                    last_gas = list(db_dic.keys())[-1]

            # last_gas = '' if last_gas is None else last_gas
            return db_dic, last_mineral, last_gas


        self.dbaccessdic = {}; counter = 0
        # if it is single line data like for dpeq20
        if len(Rd) <= 1:
            width = re.search('                     3 ', Rd[0]).start()
            Rd = textwrap.wrap(Rd[0], width=width)

            for i in range(len(Rd)): #
                s1 = Rd[i]
                if not s1.startswith(('*', ' '),0) | (s1.rstrip('\n').lstrip('0123456789.- ') == "") | (s1[0] == "-") :
                    if (s1.strip()[:3] != 'ref') and (s1.strip()[:3] != 'REF'):
                        name = s1.strip().split()[0]
                        if len(s1.strip().split()) > 1:
                            formula = s1.strip().split()[1]
                        else:
                            formula = ''
                        s2 = Rd[i + 1]
                        if (s2.strip()[:3] != 'ref') and (s2.strip()[:3] != 'REF') and (s2.split()[0].lstrip('0123456789.,- ') != ''):
                            s3 = Rd[i+2]; s4 = Rd[i+3]; s5 = Rd[i+4];
                            if s3.split()[0].lstrip('0123456789.,- ') != '':
                                if i >= len(Rd) - 5:
                                    s6 = 'Null'; s7 = 'Null'; s8 = 'Null';
                                    s9 = 'Null'; s10 = 'Null'; s11 = 'Null';
                                elif i >= len(Rd) - 6:
                                    s6  = Rd[i + 5]; s7 = 'Null'; s8 = 'Null';
                                    s9 = 'Null'; s10 = 'Null'; s11 = 'Null';
                                else:
                                    s6  = Rd[i + 5]; s7 = Rd[i + 6]; s8 = Rd[i + 7];
                                    s9 = Rd[i + 8]; s10 = Rd[i + 9]; s11 = Rd[i + 10];

                                if s3.strip()[:3] == 'ref':
                                    ref = s3#.split()[0][4:]
                                else:
                                    ref = s3#.split()[0]
                                if (s6.lower().islower() == True) | (s6.strip().split()[0] == name):
                                    params = s4.split() + s5.split()
                                elif (s7.lower().islower() == True) | (s7.strip().split()[0] == name):
                                    params = s4.split() + s5.split() + s6.split()
                                elif (s8.lower().islower() == True) | (s8.strip().split()[0] == name):
                                    params = s4.split() + s5.split() + s6.split() + s7.split()
                                elif (s9.lower().islower() == True) | (s9.strip().split()[0] == name):
                                    params = s4.split() + s5.split() + s6.split() + s7.split() + s8.split()
                                elif (s10.lower().islower() == True) | (s10.strip().split()[0] == name):
                                    params = s4.split() + s5.split() + s6.split() + s7.split() + s8.split() + \
                                        s9.split()
                                elif (s11.lower().islower() == True) | (s11.strip().split()[0] == name):
                                    params = s4.split() + s5.split() + s6.split() + s7.split() + s8.split() + \
                                        s9.split() + s10.split()
                                else:
                                    params = s4.split() + s5.split() + s6.split() + s7.split() + s8.split() + \
                                        s9.split() + s10.split() + s11.split()
                                params = [float(i) if float(i) != 999999 else 0 for i in params]
                                counter += 1
                                if name in self.dbaccessdic.keys():
                                    print('Duplicate found for species "%s" in %s' % (name, self.dbaccess_dir.split('/')[-1]))
                                    continue
                                else:
                                    self.dbaccessdic[name] = [formula, ref] + params
        else:
            # for multi line data like for speq21
            self.dbaccessdic, last_mineral, last_gas = multiline_reader(Rd, counter, self.dbaccess_dir)

        if self.dbBerman_dir is not None:
            codecs = findcodecs(self.dbBerman_dir)
            mineral_list = list(self.dbaccessdic.keys())[:list(self.dbaccessdic.keys()).index(last_mineral)+1]
            self.dbaccessdic = {k: v for k, v in self.dbaccessdic.items() if k not in mineral_list}
            specie_name = []
            with open(self.dbBerman_dir, encoding = codecs) as g:
                for i, line in enumerate(g, 1):
                    if line.strip('*').startswith('COMMENTS'):
                        break
                    if (not line.lstrip().startswith(('!', 'ST', 'C1', 'C2', 'C3', 'D1', 'D2',
                                                      'T1', 'T2', 'V1', '*'))) and (line.lstrip('0123456789.- \t\n') != ""):
                        specie_name.append(line.strip().split()[0])

            gid = open(self.dbBerman_dir, 'r', encoding = codecs)
            for i in range(5000):
                s1 = gid.readline()
                if s1.strip('*').startswith('MINERAL DATA'):
                    break

            s4 = '0'; s5 = '0'; s6 = '0'
            for i in range(5000):
                s1 = s4 if s4.strip().split()[0] in specie_name else s5 if s5.strip().split()[0] in specie_name else s6 if s6.strip().split()[0] in specie_name else gid.readline()
                if s1.strip('*').startswith('COMMENTS')|s6.strip('*').startswith('COMMENTS')|s5.strip('*').startswith('COMMENTS'):
                    break
                if (not s1.lstrip().startswith(('!', 'ST', 'C1', 'C2', 'C3', 'D1', 'D2', 'T1', 'T2', 'V1'))) and (s1.lstrip('0123456789.- \t\n') != ""):
                    name = s1.strip().split()[0]
                    if len(s1.split()) > 1:
                        formula = s1.split()[1]
                    else:
                        formula = ''
                    s2 = gid.readline(); s2 = gid.readline() if s2.lstrip().startswith('!') else s2;
                    s3 = gid.readline()
                    s4 = gid.readline() if (s3.strip().split()[0] not in specie_name) else '0'
                    s4 = s4 + '0' if s4.strip() == '' else s4
                    s5 = gid.readline() if s4.strip().split()[0] not in specie_name else '0'
                    s5 = s5 + '0' if s5.strip() == '' else s5
                    s6 = gid.readline() if s5.strip().split()[0] not in specie_name else '0'
                    s6 = s6 + '0' if s6.strip() == '' else s6
                    params = s2.split()[1:-1] if s2.lstrip().startswith('ST') else s3.split()[1:-1] if s3.lstrip().startswith('ST') else s4.split()[1:-1] if s4.lstrip().startswith('ST') else s5.split()[1:-1] if s5.lstrip().startswith('ST') else [0]*4
                    params += s3.split()[1:-1] if s3.lstrip().startswith('C1') else s4.split()[1:-1] if s4.lstrip().startswith('C1') else s5.split()[1:-1] if s5.lstrip().startswith('C1') else s6.split()[1:-1] if s6.lstrip().startswith('C1') else [0]*4
                    # params += s3.split()[1:-2] if s3.lstrip().startswith('C2') else s4.split()[1:-2] if s4.lstrip().startswith('C2') else s5.split()[1:-2] if s5.lstrip().startswith('C2') else s6.split()[1:-2] if s6.lstrip().startswith('C2') else [0]*3
                    params += s3.split()[1:-1] if s3.lstrip().startswith('V1') else s4.split()[1:-1] if s4.lstrip().startswith('V1') else s5.split()[1:-1] if s5.lstrip().startswith('V1') else s6.split()[1:-1] if s6.lstrip().startswith('V1') else [0]*4
                    params += s3.split()[1:2] if s3.lstrip().startswith('T2') else s4.split()[1:2] if s4.lstrip().startswith('T2') else s5.split()[1:2] if s5.lstrip().startswith('T2') else s6.split()[1:2] if s6.lstrip().startswith('T2') else [0]
                    params += s3.split()[1:] if s3.lstrip().startswith('T1') else s4.split()[1:] if s4.lstrip().startswith('T1') else s5.split()[1:] if s5.lstrip().startswith('T1') else s6.split()[1:] if s6.lstrip().startswith('T1') else [0]*5
                    params += s3.split()[1:-1] if s3.lstrip().startswith('D1') else s4.split()[1:-1] if s4.lstrip().startswith('D1') else s5.split()[1:-1] if s5.lstrip().startswith('D1') else s6.split()[1:-1] if s6.lstrip().startswith('D1') else []
                    params += s3.split()[1:-1] if s3.lstrip().startswith('D2') else s4.split()[1:-1] if s4.lstrip().startswith('D2') else s5.split()[1:-1] if s5.lstrip().startswith('D2') else s6.split()[1:-1] if s6.lstrip().startswith('D2') else []
                    ref = 'Berman_1988'
                    params = [float(i) if float(i) != 999999 else 0 for i in params]
                    # print(name, params)
                    if name in self.dbaccessdic.keys():
                        print('Duplicate found for species "%s" in %s' % (name, self.dbBerman_dir.split('/')[-1]))
                        continue
                    else:
                        self.dbaccessdic[name] = [formula, ref] + params
            gid.close()

        elif self.dbHP_dir is not None:
            codecs = findcodecs(self.dbHP_dir)
            mineralgas_list = list(self.dbaccessdic.keys())[:list(self.dbaccessdic.keys()).index(last_gas)+1]
            self.dbaccessdic = {k: v for k, v in self.dbaccessdic.items() if k not in mineralgas_list}
            with open(self.dbHP_dir, encoding = codecs) as g:
                Rd_HP = g.readlines()
            self.dbaccessdic.update(multiline_reader(Rd_HP, 0, self.dbHP_dir)[0])

        # read in the header reference list
        if len(header_counter) != 0:
            header_lines = Rd[header_counter[0]+1:header_counter[1]]
            if len(header_lines) > 1:
                checker = [i for i, x in enumerate(header_lines) if ' ... ' in x.lstrip()]; ref_list = []
                for i in range(len(checker)-1):
                    p = ''
                    for k in range(checker[i],checker[i+1]):
                        p = p + header_lines[k].lstrip('*').lstrip().strip('\n')
                    ref_list.append(p)
                self.header_ref = dict(zip(*[iter([item.strip() for sublist in [k.split(' ... ') for k in ref_list] for item in sublist])]*2))

        #%% other sources aside speq20 for solid solution calculation
        #dG dH S V a1 a2 a3 a4 a5
        # dG, dH, S from Arnorsson 1999, V and Cp from Robie and Hemingway #1995
        _Anorthite_ = ['Ca(Al2Si2)O8', 'R&H95, Stef2001',-4002095, -4227830, 199.30, 100.790*J_to_cal,
                       5.168e2, -9.249e-2, -1.408e6, -4.589e3, 4.188e-5]
        self.dbaccessdic['ss_Anorthite'] = [x/J_to_cal if type(x)!=str else x for x in _Anorthite_ ]

        self.dbaccessdic['ss_Albite_high'] = ['NaAlSi3O8', 'R&H95, Stef2001', -887368.32+8413/J_to_cal,
                                        -940769.52, 224.14/J_to_cal, 100.07, 139.56, -0.0221916826,
                                        401051.6, -1535.37, 5.430210e-06]

        _K_feldspar_ = ['KAlSi3O8', 'R&H95, A&S99', -3745958, -3965730, 232.90, 108.960*J_to_cal,
                        6.934e2, -1.717e-1, 3.462e6, -8.305e3, 4.919e-5]
        self.dbaccessdic['ss_K-feldspar'] = [x/J_to_cal if type(x)!=str else x for x in _K_feldspar_ ]

        _Ferrosilite_ = ['FeSiO3', 'R&H95, Stef2001', -1118000, -1195200, 94.6, 33.0*J_to_cal,
                       1.243e2, 1.454e-2, -3.378e6, 0, 0]
        self.dbaccessdic['ss_Ferrosilite'] = [x/J_to_cal if type(x)!=str else x for x in _Ferrosilite_]

        _Enstatite_=['MgSiO3', 'R&H95, Stef2001', -1458300, -1545600,  66.3, 31.31*J_to_cal,
                     3.507e2, -1.472e-1, 1.769e6, -4.296e3, 5.826e-5]
        self.dbaccessdic['ss_Enstatite'] = [x/J_to_cal if type(x)!=str else x for x in _Enstatite_]

        _Clinoenstatite_=['MgSiO3', 'R&H95, Stef2001', -1458100, -1545000,  67.9, 31.28*J_to_cal,
                     2.056e2, -1.280e-2, 1.193e6, -2.298e3, 0]
        self.dbaccessdic['ss_Clinoenstatite'] = [x/J_to_cal if type(x)!=str else x for x in _Clinoenstatite_]

        _Hedenbergite_=['CaFeSi2O6', 'R&H95, Stef2001', -2676300, -2839900,  174.2, 67.950*J_to_cal,
                     3.1046e2, 1.257e-2, -1.846e6, -2.040e3, 0]
        self.dbaccessdic['ss_Hedenbergite'] = [x/J_to_cal if type(x)!=str else x for x in _Hedenbergite_]

        _Diopside_=['CaMgSi2O6', 'R&H95, Stef2001', -3026800, -3201500,  142.7 , 66.090*J_to_cal,
                     4.7025e2, -9.864e-2, 0.2454e6, -4.823e3, 2.813e-5]
        self.dbaccessdic['ss_Diopside'] = [x/J_to_cal if type(x)!=str else x for x in _Diopside_]

        #dG dH S V a1 a2 a3 a4 a5
        _Forsterite_ = ['Mg2SiO4', 'R&H95, Stef2001', -2053600, -2171850, 94.1, 43.65*J_to_cal,
                      8.736e1, 8.717e-2, -3.699e6, 8.436e2, -2.237e-5]
        self.dbaccessdic['ss_Forsterite'] = [x/J_to_cal if type(x)!=str else x for x in _Forsterite_]

        _Fayalite_ = ['Fe2SiO4', 'R&H95, Stef2001', -1379100, -1478200, 151, 46.31*J_to_cal, 1.7602e2,
                    -8.808e-3, -3.889e6, 0, 2.471e-5]
        self.dbaccessdic['ss_Fayalite'] = [x/J_to_cal if type(x)!=str else x for x in _Fayalite_]

        _Fluorapatite_ = ['Ca5(PO4)3F', 'R&H95', -6489700, -6872000, 387.9, 157.56*J_to_cal,
                      7.543e2, -3.026e-2, -0.9084e6, -6.201e3, 0]
        if 'Fluorapatite' not in self.dbaccessdic.keys():
            self.dbaccessdic['Fluorapatite'] = [x/J_to_cal if type(x)!=str else x for x in _Fluorapatite_]

        _Hydroxyapatite_ = ['Ca5(OH)(PO4)3', 'R&H95', -6337100, -6738500, 390.4, 159.6*J_to_cal,
                            3.878e2, 11.186e-2, -12.70e6, 1.811e3, 0]
        if 'Hydroxyapatite' not in self.dbaccessdic.keys():
            self.dbaccessdic['Hydroxyapatite'] = [x/J_to_cal if type(x)!=str else x for x in _Hydroxyapatite_]

        if 'Ankerite' not in self.dbaccessdic.keys():
            self.dbaccessdic['Ankerite'] = ['CaFe(CO3)2', 'H&P2011               31.DEC.11\n', -434945.7,
                                            -471178.3, 45.043, 66.060,  81.500956, -0.277486, 0, -730.114720, 0]

        if 'Acmite' not in self.dbaccessdic.keys():
            self.dbaccessdic['Acmite'] = ['NaFeSi2O6', 'H&P2011               31.DEC.11\n', -577476.5,
                                          -617454.6, 40.774, 64.590,  1.994e2, 6.197e-2, -4.267e6, 0, 0]

        _Annite_ = ['KFe3AlSi3O10(OH)2', 'R&H95', -4798300, -5149300, 415.0, 154.3*J_to_cal,
                    6.366e2, 8.208e-2, -4.860e6, -3.731e3, 0]
        self.dbaccessdic['ss_Annite'] = [x/J_to_cal if type(x)!=str else x for x in _Annite_]

        _Phlogopite_ = ['KMg3AlSi3O10(OH)2', 'R&H95', -5860500, -6246000, 315.9, 149.65*J_to_cal,
                        8.639e2, -7.6076e-2, 3.5206e5, -8.470e3, 0]
        self.dbaccessdic['ss_Phlogopite'] = [x/J_to_cal if type(x)!=str else x for x in _Phlogopite_]
                                        #dG dH S V a1 a2 a3 a4 a5
        _Molybdenite_ = ['MoS2', 'R&H95', -262800, -271800, 62.6, 32.02*J_to_cal,
                        1.045e2, -4.812e-3, -6.291e3, -6.817e2, 0]
        if 'Molybdenite' not in self.dbaccessdic.keys():
            self.dbaccessdic['Molybdenite'] = [x/J_to_cal if type(x)!=str else x for x in _Molybdenite_]

        _Molybdite_ = ['MoO3', 'R&H95', -668100, -745200, 77.7, 30.56*J_to_cal,
                        6.433e0, 6.278e-2, -2.46e6, 1.337e3, 0]
        if 'Molybdite' not in self.dbaccessdic.keys():
            self.dbaccessdic['Molybdite'] = [x/J_to_cal if type(x)!=str else x for x in _Molybdite_]

        return

    def readSourceGWBdb(self):
        """
        This function reads source GWB thermodynamic database and reaction coefficients of 'eh'
        and 'e-' has been added at the bottom returns all reaction coefficients and species,
        group species into redox, minerals, gases, oxides and aqueous species
        Parameters
        ----------
            sourcedb      :     filename of the source database
        Returns
        ----------
            sourcedic     :     dictionary of reaction coefficients and species
            specielist    :     list of species segmented into the different categories
                                [element, basis, redox, aqueous, minerals, gases, oxides]
            speciecat     :     list of species categories listed in 'specielist'
            chargedic     :     dictionary of charges of species
            MWdic         :     dictionary of MW of species
            Mineraltype   :     mineral type for minerals
            fugacity_info :     fugacity information as stored in new tdat database for chi and critical ppts
        Usage:
        ----------
        [sourcedic, specielist, chargedic, MWdic, Mineraltype, fugacity_info, activity_model] = readSourceGWBdb()
        """
        codecs = self.sourcedb_codecs
        with open(self.sourcedb_dir, encoding = codecs) as g:
            for line in g:
                if line.startswith('activity model'):
                    break

        with open(self.sourcedb_dir, encoding = codecs) as g:
            Rd = g.readlines()
        activity_model = line.strip('\n').split()[-1]
        data_fmt = [x for x in Rd if 'dataset format' in x][0].strip('\n').split(':')[-1].strip()
        fugacity_model = [x for x in Rd if 'fugacity model' in x][0].strip('\n').split(': ')[-1] if data_fmt != 'oct94' else ''

        unwanted = ['elements', 'basis species', 'redox couples', 'aqueous species',
                    'free electron', 'minerals', 'solid solutions', 'gases', 'oxides', 'stop.' ]
        #capture line numbers with line break
        d=[]; previousline = ''
        with open(self.sourcedb_dir, encoding = codecs) as fid:
            for idx, line in enumerate(fid, 1):
                if line.strip().rstrip('\n').lstrip('0123456789.- ') in unwanted:
                    x=idx
                    d.append(x-1)
                #elif line.strip(' \n*').startswith(('virial coefficients', 'Virial coefficients', 'SIT epsilon coefficients', 'Pitzer parameters')):
                elif previousline.startswith('-end-') and line.startswith('*'):
                    x=idx; #print(x)
                    d.append(x+1)
                    break
                previousline = line

        if activity_model == 'h-m-w':
            if all([i.startswith('*') for i in Rd[d[-1]:d[-1]+30]]) == False:
                d_act = [i for i, x in enumerate(Rd[d[-1]:]) if x.strip('\n') ==''][0]
            else:
                d_act = [i for i, x in enumerate(Rd[d[-2]:]) if x.strip('\n') ==''][0]
        f = open(self.sourcedb_dir, 'r', encoding = codecs)
        #skip first 11 lines of database  .lstrip('0123456789.- ')
        for i in range(d[1]+2):
          s1 = f.readline()

        self.sourcedic = {} # initialize dictionary
        for i in range(d[-1]-d[1]):   #
            s1 = f.readline()
            if s1.strip(' \n*').startswith(("references", 'virial coefficients', 'Virial coefficients', 'SIT epsilon coefficients', 'Pitzer parameters')) :
                break
            if not s1.startswith((' ', '*'), 0) | (s1.rstrip('\n') == "") | (len(s1) !=0 and s1[0] == "-") :
                if s1.rstrip('\n').lstrip('0123456789.- ') in unwanted:
                    continue
                elif s1.rstrip('\n').lstrip('0123456789.- ') == '':
                    continue
                else:
                    specie_name = s1.strip().split()[0]
                    s2 = f.readline(); s3 = f.readline() if s2.rstrip('\n') != '' else ''
                    s4 = f.readline() if s3.rstrip('\n') != '' else ''
                    s5 = f.readline() if s4.rstrip('\n') != '' else ''
                    if data_fmt == 'mar21' and not s3.split()[0].isdigit() and'mole' not in [s3.split()[0], s2.split()[0]] :
                        if (s2.rstrip('\n') != "" and s3.rstrip('\n') == ""):
                            ss_details = [s1, s2, s3]
                        elif (s3.rstrip('\n') != "" and s4.rstrip('\n') == ""):
                            ss_details = [s1, s2, s3, s4]
                        elif (s4.rstrip('\n') != "" and s5.rstrip('\n') == ""):
                            ss_details = [s1, s2, s3, s4, s5]
                        elif (s5.rstrip('\n') != ""):
                            s6 = f.readline()
                            ss_details = [s1, s2, s3, s4, s5, s6]
                            if (s6.rstrip('\n') != ""):
                                s7 = f.readline()
                                ss_details = [s1, s2, s3, s4, s5, s6, s7]
                                if (s7.rstrip('\n') != ""):
                                    s8 = f.readline()
                                    ss_details = [s1, s2, s3, s4, s5, s6, s7, s8]
                                    if (s8.rstrip('\n') != ""):
                                        s9 = f.readline()
                                        ss_details = [s1, s2, s3, s4, s5, s6, s7, s8, s9]
                        specie_formula = []; species_num = []; reactant = []
                    else:
                        if (s5.rstrip('\n') != ""):
                            s6 = f.readline()
                            if (s6.rstrip('\n') != ""):
                                s7 = f.readline()
                                if not s2.startswith('*',0):
                                    if (len(s2.split()) > 1) and (s2.split()[0] != 'formula='):
                                        if len(s1.split('formula=')) <= 1:
                                            specie_formula = ""
                                        else:
                                            specie_formula = s1.rstrip('\n').split('formula=')[1]
                                        if not s3.lstrip().startswith(('chi', 'Pcrit'), 0):
                                            species_num = int(s3.split()[0])
                                            if species_num <= 3:
                                                reactant = s4.split()
                                            elif species_num <= 6:
                                                reactant = s4.split() + s5.split()
                                            else:
                                                reactant = s4.split() + s5.split() + s6.split()
                                        else:
                                            if not s4.lstrip().startswith(('chi','Pcrit'),0):
                                                species_num = int(s4.split()[0])
                                                if species_num <= 3:
                                                    reactant = s5.split()
                                                elif species_num <= 6:
                                                    reactant = s5.split() + s6.split()
                                                else:
                                                    reactant = s5.split() + s6.split() + s7.split()
                                            else:
                                                species_num = int(s5.split()[0])
                                                if species_num <= 3:
                                                    reactant = s6.split()
                                                else:
                                                    reactant = s6.split() + s7.split()
                                    else:
                                        if len(s2.split('formula=')) <= 1:
                                            specie_formula = ""
                                        else:
                                            specie_formula = s2.rstrip('\n').split('formula=')[1]
                                        species_num = int(s4.split()[0])
                                        if species_num <= 3:
                                            reactant = s5.split()
                                        elif species_num <= 6:
                                            reactant = s5.split() + s6.split()
                                        else:
                                            reactant = s5.split() + s6.split() + s7.split()
                                else:
                                    specie_formula = s2.split()[2]
                                    species_num = int(s4.split()[0])
                                    if species_num <= 3:
                                        reactant = s5.split()
                                    elif species_num <= 6:
                                        reactant = s5.split() + s6.split()
                                    else:
                                        reactant = s5.split() + s6.split() + s7.split()
                            else:
                                specie_formula = ""
                                species_num = int(s3.split()[0])
                                if species_num <= 3:
                                    reactant = s4.split()
                                elif species_num <= 6:
                                    reactant = s4.split() + s5.split()
                                else:
                                    reactant = s4.split() + s5.split() + s6.split()
                        else:
                            specie_formula = ""
                            species_num = int(s3.split()[0])
                            if species_num <= 3:
                                reactant = s4.split()
                            elif species_num <= 6:
                                reactant = s4.split() + s5.split()
                            else:
                                reactant = s4.split() + s5.split() + s6.split()
                        ss_details = []

            dt = [specie_formula, species_num] + reactant + ss_details
            self.sourcedic[specie_name] = dt[2:] if any(isinstance(el, list) for el in dt) else dt
        self.sourcedic['eh'] = ['eh', 3, '-2.0000', 'H2O', '1.0000', 'O2(g)', '4.0000', 'H+']
        self.sourcedic['e-'] = ['e-', 3, '0.50000', 'H2O', '-0.2500', 'O2(g)', '-1.0000', 'H+']

        f.close()

        element = []; basis = []; redox = []; aqueous = []; minerals = []; gases = []; oxides = [];
        solidsolutions = []
        charge = []; MW = []; electron = []; self.Mineraltype = {}; fugacity_chi = {}; fugacity_Pcrit = {}
        with open(self.sourcedb_dir, encoding = codecs) as fid:
            for i, line in enumerate(fid, 1):
                previousline = line
                if (line.strip(' \n*').startswith(("references", 'Pitzer parameters', 'virial coefficients', 'Virial coefficients', 'SIT epsilon coefficients'))):
                    break
                # elif previousline.startswith('-end-') and line.startswith('*'):
                #     break
                if not line.startswith((' ','*'),0) | (line.rstrip('\n') == "") | (line[0] == "-") :
                    if not line.split()[0].replace('.','',1).isnumeric():
                        if not line.startswith(('charge', 'mole', 'formula'), 0):
                            if d[0] < i < d[1]:
                                element.append(line.split()[0])
                            elif d[1] < i < d[2]:
                                basis.append(line.split()[0])
                            elif d[2] < i < d[3]:
                                redox.append(line.split()[0])
                            elif d[3] < i < d[4]:
                                aqueous.append(line.split()[0])
                            elif d[4] < i < d[5]:
                                if data_fmt == 'oct94':
                                    minerals.append(line.split()[0])
                                elif data_fmt in ['jul17', 'jan19', 'apr20', 'mar21'] :
                                    electron.append(line.split()[0])
                            elif d[5] < i < d[6]:
                                if data_fmt == 'oct94':
                                    gases.append(line.split()[0])
                                elif data_fmt in ['jul17', 'jan19', 'apr20', 'mar21'] :
                                    minerals.append(line.split()[0])
                            elif i > d[6]:
                                if data_fmt == 'oct94':
                                    oxides.append(line.split()[0])
                                elif d[6] < i < d[7]:
                                    if data_fmt in ['jul17', 'jan19', 'apr20'] :
                                        gases.append(line.split()[0])
                                    elif data_fmt == 'mar21':
                                        solidsolutions.append(line.split()[0])
                                elif i > d[7]:
                                    if data_fmt in ['jul17', 'jan19', 'apr20'] :
                                        oxides.append(line.split()[0])
                                    elif data_fmt == 'mar21':
                                        if d[7] < i < d[8]:
                                            gases.append(line.split()[0])
                                        elif i > d[8]:
                                            oxides.append(line.split()[0])

                if (re.compile(r"charge").search(line) != None) and not line.startswith('*'):
                    charge.append(line)
                if (re.compile(r"mole wt.=").search(line) != None) and not line.startswith('*'):
                    MW.append(re.sub('[^0123456789\.]', '', line.strip('\n').split('wt.=')[1]))
                if (re.compile(r"type=").search(line) != None) and not line.startswith('*'):
                    if len(line.split()) <= 2:
                        self.Mineraltype[line.split()[0]] = ''
                    else:
                        self.Mineraltype[line.split()[0]] = line.split()[2]
                if (re.compile(r"chi=").search(line) != None) and not line.startswith('*'):
                    fugacity_chi[gases[-1]] = line
                if (re.compile(r"Pcrit=").search(line) != None) and not line.startswith('*'):
                    fugacity_Pcrit[gases[-1]] = line

        act_list = []; #previousline = ''
        if activity_model == 'h-m-w':
            with open(self.sourcedb_dir, encoding = codecs) as fid:
                for i, line in enumerate(fid, 1):
                    num = d[-1] + d_act if all([i.startswith('*') for i in Rd[d[-1]:d[-1]+30]]) == False else d[-2] + d_act
                    if i > num: #d[-1] + d_act:
                        if not line.startswith(('  ', '\n', '-end-', '*')):
                            act_list.append(line)

        self.act_param = {'activity_model': activity_model, 'act_list': act_list, 'dataset_format' : data_fmt}
        self.fugacity_info = {'fugacity_model': fugacity_model, 'fugacity_chi': fugacity_chi,'fugacity_Pcrit': fugacity_Pcrit}
        res = basis + redox + aqueous + electron
        self.chargedic = {res[i]: charge[i].rstrip('\n') for i in range(len(charge))}
        res = element + basis + redox + aqueous + electron + minerals + gases + oxides
        self.MWdic = {res[i]: float(MW[i]) for i in range(len(MW))}
        if data_fmt != 'mar21':
            self.specielist = [element, basis, redox, aqueous, electron, minerals, gases, oxides]
            self.speciecat = ['element', 'basis', 'redox', 'aqueous', 'electron', 'minerals', 'gases', 'oxides']
        else:
            self.specielist = [element, basis, redox, aqueous, electron, minerals, solidsolutions, gases, oxides]
            self.speciecat = ['element', 'basis', 'redox', 'aqueous', 'electron', 'minerals', 'solidsolutions', 'gases', 'oxides']

        return

    def readSourceEQ36db(self):
        """
        This function reads source EQ3/6 thermodynamic database and reaction coefficients of 'eh'
        and 'e-' has been added at the bottom returns all reaction coefficients and species,
        group species into basis, auxiliary basis, minerals, gases, liquids and aqueous species
        Parameters
        ----------
            sourcedb      :     filename of the source database
        Returns
        ----------
            sourcedic     :     dictionary of reaction coefficients and species
            specielist    :     list of species segmented into the different categories
                                [element, basis, redox, aqueous, minerals, gases, oxides]
            speciecat     :     list of species categories listed in 'specielist'
            chargedic     :     dictionary of charges of species and DHazero info
            MWdic         :     dictionary of MW of species
            Sptype        :     specie types and eq3/6 and revised date info
            Elemlist      :     dictionary of elements and coefficients
        Usage:
        ----------
        [sourcedic, specielist, chargedic, MWdic, block_info, Elemlist, act_param] = readSourceEQ36db(sourcedb)
        """
        codecs = self.sourcedb_codecs
        with open(self.sourcedb_dir, encoding = codecs) as g:
            for line in g:
                if line.startswith(('bdot parameters', 'single-salt parameters', 'ca combinations')):
                    break

        if line.startswith('bdot parameters'):
            activity_model = 'debye-huckel'
        elif line.startswith(('single-salt parameters', 'ca combinations')):
            activity_model = 'h-m-w'

        subheading = ['elements', 'basis species', 'auxiliary basis species', 'aqueous species',
                    'solids', 'liquids', 'gases', 'solid solutions', 'references', 'stop.']
        d = []
        with open(self.sourcedb_dir, encoding = codecs) as f:
            for idx, line in enumerate(f, 1):
                if line.strip().rstrip('\n').lstrip('0123456789.- ') in subheading:
                    x=idx
                    d.append(x-1)
                if line.startswith(('bdot parameters', 'single-salt parameters', 'ca combinations')):
                    x=idx
                    d.append(x-1)

        element = []; basis = []; auxiliary = []; aqueous = []; minerals = []; MW = []; #DH = []
        gases = []; liquids = []; charge = []; solid_solutions = []; act_params = []

        with open(self.sourcedb_dir, encoding = codecs) as f:
            for i, line in enumerate(f, 1):
                if (line.rstrip('\n') == "references"):
                    break
                if not line.startswith('*',0) | line.startswith(' ',0) | (line.rstrip('\n') == "") | (line[0] == "-") :
                    if not line.split()[0].replace('.','',1).isnumeric() and not line.startswith('+',0):
                        if line.strip().rstrip('\n').lstrip('0123456789.- ') not in subheading:
                            line = line.strip().rstrip('\n')
                            if d[1] < i < d[2]:
                                element.append(line.split()[0])
                                MW.append(float(line.split()[1]))
                            elif d[2] < i < d[3]:
                                basis.append(line.split('  ')[0])
                            elif d[3] < i < d[4]:
                                if any(re.findall(r'|'.join(('acid', 'high', 'low')), line.split('  ')[0], re.IGNORECASE)):
                                    auxiliary.append(line.split('  ')[0].replace(' ', '_'))
                                else:
                                    auxiliary.append(line.split('  ')[0])
                            elif d[4] < i < d[5]:
                                if any(re.findall(r'|'.join(('acid', 'high', 'low')), line.split('  ')[0], re.IGNORECASE)):
                                    aqueous.append(line.split('  ')[0].replace(' ', '_'))
                                else:
                                    aqueous.append(line.split('  ')[0])
                            elif d[5] < i < d[6]:
                                if any(re.findall(r'|'.join(('acid', 'high', 'low', 'anhyd', 'hydr')), line.split('  ')[0], re.IGNORECASE)):
                                    minerals.append(line.split('  ')[0].replace(' ', '_'))
                                else:
                                    minerals.append(line.split('  ')[0])
                            elif d[6] < i < d[7]:
                                liquids.append(line.split('  ')[0])
                            elif d[7] < i < d[8]:
                                gases.append(line.split('  ')[0])
                            elif i > d[8]:
                                solid_solutions.append(line.split('  ')[0])
                if re.compile(r"charge").search(line) != None:
                    charge.append(line)
                if d[0] < i < d[1]:
                    act_params.append(line)

        self.MWdic = {element[i]: float(MW[i]) for i in range(len(MW))}
        res = basis + auxiliary + aqueous + minerals + liquids + gases + solid_solutions
        lstname = []; self.block_info = {}; self.Elemlist = {}; self.sourcedic = {}
        self.act_param = {'activity_model': activity_model, 'act_list': None, 'alpha_beta' : {},
                          'theta':{}, 'lambda':{}, 'psi':{},'zeta':{},'mu':{}, 'beta0' : {},
                          'beta1' : {}, 'beta2' : {}, 'alpha1' : {}, 'alpha2' : {}, 'cphi' : {}}
        keywords = [["+" + "-"*30,   "+" + "-"*30]  ]
        for num, k in enumerate(keywords):
            lst = []; counter = 0
            f = open(self.sourcedb_dir, 'r', encoding = codecs)

            for i in range(d[1] + len(element)):#
                s1 = f.readline()
                if (s1.rstrip('\n') == "elements") :
                    break
                act_list = [act_params[i +1] for i,x in enumerate(act_params) if x.rstrip('\n').startswith(k[0])]
                act_list = [x for x in act_list if not x.startswith(('*', 'nn', 'nc', 'cc', 'mixture'))]
                if (activity_model == 'h-m-w') and any(s1.lstrip().rstrip('\n').startswith(x) for x in act_list):
                    lst = []; lst.append(s1)
                    for j in range(50):
                        s = f.readline()
                        if s.lstrip().rstrip('\n').startswith(k[1]):
                            break
                        elif not s.lstrip().startswith(('****', '*',  'single-salt parameters', 'ca combinations')) | (s.rstrip('\n').strip('0123456789.- ') in ["", 'Miscellaneous parameters']+subheading):
                            lst.append(s)
                    if len(lst) > 2:
                        if any(['mu' in x for x in lst]):
                            checker = [x.strip(' \n').split()[-1] for i, x in enumerate(lst) if x.lstrip().startswith('mu')]
                            if re.sub('[^0123456789\.]', '', checker[0]) == '':
                                first_a = [i for i, x in enumerate(lst) if x.lstrip().startswith('a')][0]
                                mu = float(lst[first_a].split()[-1])
                            else:
                                mu = float(re.sub('[^0123456789\.]', '', checker[0]))
                            self.act_param['mu'][lst[0].rstrip('\n')] = mu
                        if any(['zeta' in x for x in lst]):
                            checker = [x.strip(' \n').split()[-1] for i, x in enumerate(lst) if x.lstrip().startswith('zeta')]
                            if re.sub('[^0123456789\.]', '', checker[0]) == '':
                                first_a = [i for i, x in enumerate(lst) if x.lstrip().startswith('a')][0]
                                zeta = float(lst[first_a].split()[-1])
                            else:
                                zeta = float(re.sub('[^0123456789\.]', '', checker[0]))
                            self.act_param['zeta'][lst[0].rstrip('\n')] = zeta
                        if any([('alpha' or 'beta') in x for x in lst]):
                            self.act_param['alpha_beta'][lst[0].rstrip('\n')] = lst
                            lster = ['beta0', 'beta1', 'beta2', 'alpha1', 'alpha2', 'cphi']
                            for pos in lster:
                                checker = [x.strip(' \n') for i, x in enumerate(lst) if pos in re.sub('[()]', '', x).lstrip().lower()]
                                if all([x in checker[0] for x in lster[:3]]):
                                    checker = checker[0].replace("=", "").split()
                                    par = float(checker[checker.index(pos) + 1])
                                elif all([x in checker[0] for x in lster[3:5]]):
                                    checker = checker[0].replace("=", "").split()
                                    par = float(checker[checker.index(pos) + 1])
                                else:
                                    # checker = checker.split()[-1]
                                    if re.sub('[^0123456789\.]', '', re.sub('[(012)]', '', checker[0])) == '':
                                        first_a = [i for i, x in enumerate(lst) if pos in re.sub('[()]', '', x).lstrip().lower() ][0] + 1
                                        par = float(lst[first_a].split()[-1])
                                    else:
                                        par = float(re.sub('[^0123456789\.]', '', re.sub('[()]', '', checker[0])))
                                self.act_param[pos][lst[0].rstrip('\n')] = par
                        if any(['psi' in x for x in lst]):
                            checker = [x.strip(' \n') for i, x in enumerate(lst) if 'psi' in x.lstrip() ]
                            if all([x in checker[0] for x in [' psi', 'theta']]):
                                checker = checker[0].replace("=", "").split()
                                psi = float(checker[checker.index('psi') + 1])
                            else:
                                if re.sub('[^0123456789\.]', '', checker[0]) == '':
                                    first_a = [i for i, x in enumerate(lst) if x.lstrip().startswith('a')][0]
                                    psi = float(lst[first_a].split()[-1])
                                else:
                                    psi = float(re.sub('[^0123456789\.]', '', checker[0]))
                            self.act_param['psi'][lst[0].rstrip('\n')] = psi
                        if any(['theta' in x for x in lst]):
                            checker = [x.strip(' \n') for i, x in enumerate(lst) if 'theta' in x.lstrip() ]
                            if all([x in checker[0] for x in ['theta', ' psi']]):
                                checker = checker[0].replace("=", "").split()
                                theta = float(checker[checker.index('theta') + 1])
                            else:
                                if re.sub('[^0123456789\.]', '', checker[0]) == '':
                                    first_a = [i for i, x in enumerate(lst) if x.lstrip().startswith('a')][0]
                                    theta = float(lst[first_a].split()[-1])
                                else:
                                    theta = float(re.sub('[^0123456789\.]', '', checker[0]))
                            self.act_param['theta'][lst[0].rstrip('\n')] = theta
                        if any(['lambda' in x for x in lst]):
                            checker = [x.strip(' \n').split()[-1] for i, x in enumerate(lst) if 'lambda' in x.lstrip()]
                            if re.sub('[^0123456789\.]', '', checker[0]) == '':
                                first_a = [i for i, x in enumerate(lst) if x.lstrip().startswith('a')][0]
                                lambdaa = float(lst[first_a].split()[-1])
                            else:
                                lambdaa = float(re.sub('[^0123456789\.]', '', checker[0]))
                            self.act_param['lambda'][lst[0].rstrip('\n')] = lambdaa

            for i in range(d[-1]) :  #
                s = f.readline()
                if (s.rstrip('\n') == "references") :
                    break
                s = s.replace(" acid", "_acid").replace(" high", "_high").replace(" low", "_low").replace(" anhyd", "_anhyd").replace(" hydr", "_hydr")

                if any(s.lstrip().rstrip('\n').startswith(x) for x in res):
                    lst = []; lst.append(s); counter += 1
                    for j in range(50):
                        s = f.readline()
                        if s.lstrip().rstrip('\n').startswith(k[1]):
                            break
                        elif not s.lstrip().startswith('****'):
                            lst.append(s)
                    lst[0] = lst[0].rstrip('\n')
                    if lst[0] not in subheading:
                        if lst[0].split('  ')[0] in res or lst[0].split()[0].replace(' ', '_') in res:
                            if any(re.findall(r'|'.join(('acid', 'high', 'low', 'anhyd', 'hydr')), lst[0].split('  ')[0], re.IGNORECASE)):
                                specie_name = lst[0].split('  ')[0].replace(' ', '_')
                            else:
                                specie_name = lst[0].split('  ')[0]
                            lstname.append(specie_name)
                            if specie_name not in solid_solutions:
                                indx, elem_numb =[(i,int(re.sub('[^0123456789\.]', '', x))) for i,x in enumerate(lst)
                                                  if x.strip('0123456789.,-: ').startswith('element(s)')][0]
                                elem_rows = list(range(indx + 1, indx + 2)) if elem_numb <= 3 else list(range(indx + 1, indx + 3)) if elem_numb <= 6 else list(range(indx + 1, indx + 4)) if elem_numb <= 9 else list(range(indx + 1, indx + 5))
                                reactant = [lst[x].rstrip('\n').split('  ') for x in elem_rows]
                                reactant = [item for sublist in reactant for item in sublist] # convert list of list to list
                                reactant = [y for x in reactant for y in x.split() if x != '' and x != '****']
                                self.Elemlist[specie_name] = reactant
                            else:
                                elem_rows = [20]
                            if specie_name not in basis[:-1] + solid_solutions and counter > len(basis):
                                indx, species_num =[(i,int(re.sub('[^0123456789\.]', '', x))) for i,x in enumerate(lst)
                                                    if x.strip('0123456789.,-: ').startswith('species in')][0]
                                spec_rows = list(range(indx + 1, indx + 2)) if species_num < 3 else list(range(indx + 1, indx + 3)) if species_num < 5 else list(range(indx + 1, indx + 4)) if species_num < 7 else list(range(indx + 1, indx + 5)) if species_num < 9 else  list(range(indx + 1, indx + 6))
                                reactants = [lst[x].rstrip('\n').split('  ') for x in spec_rows]
                                reactants = [item for sublist in reactants for item in sublist] # convert list of list to list
                                reactants = [y for x in reactants for y in x.split() if x != '' and x != '****']
                                reactants = [j.replace(' ', '_') if any(re.findall(r'|'.join(('acid', 'high', 'low', 'anhyd', 'hydr')),
                                                                                    j, re.IGNORECASE)) else j for j in reactants]
                            else:
                                spec_rows = [20]
                            if specie_name in solid_solutions:
                                indx, species_num =[(i,int(re.sub('[^0123456789\.]', '', x))) for i,x in enumerate(lst)
                                                    if x.strip('0123456789.,-: ').startswith(('components', 'end members'))][0]
                                spec_rows = list(range(indx + 1, indx + 2)) if species_num < 3 else list(range(indx + 1, indx + 3)) if species_num < 5 else list(range(indx + 1, indx + 4)) if species_num < 7 else list(range(indx + 1, indx + 5)) if species_num < 9 else  list(range(indx + 1, indx + 6))
                                reactants = [lst[x].rstrip('\n').split('  ') for x in spec_rows]
                                reactants = [item for sublist in reactants for item in sublist] # convert list of list to list
                                reactants = [y for x in reactants for y in x.split() if x != '' and x != '****']
                            mw = [x for x in lst if x.strip('*    ').startswith('mol.wt.')]
                            mw = float(re.sub('[^0123456789\.]', '', mw[0].split()[-2])) if len(mw) != 0 else []
                            if len(lst[0].split()) <= 1:
                                specie_formula = ""
                            elif len(lst[0].split()) > 2:
                                specie_formula = lst[0].split()[2]
                            else:
                                specie_formula = lst[0].split()[1]
                            if (specie_name == 'O2(g)') and counter <= len(basis):
                                self.block_info['%s_b' % specie_name] = lst[1:min(elem_rows,spec_rows)[0] - 1]
                            elif specie_name in basis[:-1] + auxiliary + aqueous + minerals + liquids + gases:
                                self.block_info[specie_name] = lst[1:min(elem_rows,spec_rows)[0] - 1]
                            elif specie_name in solid_solutions:
                                self.block_info[specie_name] = [lst[1:min(spec_rows) - 1], lst[(max(spec_rows) + 1):]]
                            if specie_name in basis and counter <= len(basis):
                                self.sourcedic[specie_name] = [specie_formula, elem_numb] + reactant
                            elif specie_name == 'O2(g)':
                                self.sourcedic[specie_name] = [specie_formula, species_num] + reactants
                            else:
                                self.sourcedic[specie_name] = [specie_formula, species_num] + reactants
                            self.MWdic[specie_name] = mw

        self.sourcedic['eh'] = ['eh', 4, '-1.0000', 'eh', '-2.0000', 'H2O', '1.0000', 'O2(g)', '4.0000', 'H+']
        self.sourcedic['e-'] = ['e-', 4, '-1.0000', 'e-', '0.50000', 'H2O', '-0.2500', 'O2(g)', '-1.0000', 'H+']
        self.specielist = [element, basis, auxiliary, aqueous, minerals, liquids, gases, solid_solutions]
        self.speciecat = ['element', 'basis', 'redox', 'aqueous', 'minerals', 'liquids', 'gases', 'solid_solutions']
        res = basis + auxiliary + aqueous
        self.chargedic = {res[i]: charge[i].rstrip('\n') for i in range(len(charge))}
        self.act_param['act_list'] = act_list if activity_model == 'h-m-w' else ''
        self.act_param['activity_model'] = activity_model

        f.close()
        return

    def readSourcePHREEQCdb(self):
        """
        This function reads source PHREEQC thermodynamic database and
        group species into solution, phases, exchange and surface species
        Parameters
        ----------
            sourcedb      :     filename of the source database
        Returns
        ----------
            sourcedic     :     dictionary of reaction coefficients and species
            specielist    :     list of species segmented into the different categories
                                [element, basis, redox, aqueous, minerals, gases, oxides]
            speciecat     :     list of species categories listed in 'specielist'
            chargedic     :     dictionary of charges of species
        Usage:
        ----------
        [sourcedic, specielist, chargedic, act_param] = readSourcePHREEQCdb()
        """

        # SOLUTION_MASTER_SPECIES - SOLUTION_SPECIES
        def get_solution_master_species(Rd, d, elements):
            i = d['SOLUTION_MASTER_SPECIES'] + 1

            while i < d["SOLUTION_SPECIES"]:
                curr = Rd[i].split()

                if len(curr) != 0 and len(re.findall(r'[A-Za-z]', curr[0])) <= 2 and curr[0] != '#':
                    elements.append(curr[0])
                    i += 1
                else:
                    i += 1

            return elements
    
        # SOLUTION_SPECIES - PHASES
        # helper for get_stoich_coeff_of_basis_species() when compound has no brackets 
        def helper_no_brackets(compound, elements_in_copy, stoich_coeff_dic, i):
            # i = len(compound) - 1 - removed to make work on compounds with and without brackets
            
            while i >= 0:
                if compound[i].isdigit():
                    # ensure number represents subscript and not a charge ex. +2, -2
                    if compound[i-1] not in '+-':
                        coeff = compound[i]

                        if i >= 2 and compound[i-2:i] in elements_in_copy:
                            stoich_coeff_dic[compound[i-2:i]] = coeff + ".000"
                            i-=3
                        elif compound[i-1] in elements_in_copy:
                            stoich_coeff_dic[compound[i-1]] = coeff  + ".000" 
                            i-=2
                        else:
                            print("could not find associated element for subscript - smtg went wrong for compound: ", compound)
                            break
                    else:
                        i-=2
                        continue

                else:
                    # compound[i] is second char of element with length=2 and no subscript
                    if i >= 1 and compound[i-1:i+1] in elements_in_copy:
                        stoich_coeff_dic[compound[i-1:i+1]] = '1.000'
                        i-=2
                    # compound[i] is an element with length=1 and no subscript
                    elif compound[i] in elements_in_copy:
                        stoich_coeff_dic[compound[i]] = '1.000'
                        i-=1

                    # TODO - delete later
                    else:
                        #print("found nothing")
                        i-=1

            return stoich_coeff_dic

        def get_stoich_coeff_of_basis_species(compound, elements_in_copy):
            """
            Parameters
            ----------
                compound            :       string - chemical formula of a compound listed in SOLUTION_SPECIES, lines (261, 687) in PHREEQC database
                elements_in_copy    :       list[string] - elements in compound
            Returns
            ----------
                stoich_coeff_dic    :       dict - {elem : coeff}

            Ex. 
            get_stoich_coeff_of_basis_species('HPO4-2', ['H', 'P', 'O']) -> {'O': '4.000', 'P': '1.000', 'H': '1.000'}
            """
            stoich_coeff_dic = {}
            
            if '(' not in compound and ')' not in compound:
                stoich_coeff_dic = helper_no_brackets(compound, elements_in_copy, stoich_coeff_dic, len(compound) - 1)
            else:
                compound_copy = re.split(r'[()]', compound)

                i = len(compound_copy) - 1

                coeff = compound_copy[i]
                stoich_coeff_dic[compound_copy[i-1][0]] = coeff
                stoich_coeff_dic[compound_copy[i-1][1]] = coeff

                helper_no_brackets(compound, elements_in_copy, stoich_coeff_dic, len(compound)-6)

            return stoich_coeff_dic

        def get_stoich_coeff_of_sol_species(formula, sourcedic, sol_species):
            """
            Parameters
            ----------
                formula             :       list[string] - solution_species that has been split by ' + ' (not stripped)
                sourcedic           :       dict
                sol_species         :       list[string] - running list of solution species found in database being read 
            Returns
            ----------
                sourcedic           :       dict
                species_of_interest :       string - species after '=' tnat we are trying to add to sourcedic 
                sol_species         :       list

            Ex. get_stoich_coeff_of_sol_species(['2 H2O', 'Fe+2 = Fe(OH)2', '2 H+'], {}, [])  -> ({'Fe(OH)2': ['', 3, '2', 'H2O', '1', 'Fe+2', '2', 'H+']}, 'Fe(OH)2')
            Test cases: get_stoich_coeff_of_sol_species('['2 H2O', 'Fe+2 = Fe(OH)2', '2 H+']', {}, []) 
                        get_stoich_coeff_of_sol_species('2.000HS- + 1.000Zn+2 + 1.000H2O  = Zn(HS)2OH- + 1.000H+', {}, [])
            """
            # the compound after the '=' is the species_of_interest in solution species

            idx_of_equals = -1
            # This for-loop:
            # ['Fe+3', '3 H2O = Fe(OH)3', '3 H+'] -> ['Fe+3', '3 H2O', '=', 'Fe(OH)3', '3 H+']
            for i in range(len(formula)):
                formula[i] = formula[i].strip()
                if '=' in formula[i]:
                    temp = re.split(r'=', formula[i])
                    formula = formula[:i] + [temp[0].strip()] + ['='] + [temp[1].strip()] + formula[i+1:]
                    idx_of_equals = i + 1
                    break

            i = 0 
            temp = {}

            while i < idx_of_equals:
                item = formula[i]

                # find start of compound formula
                first_char_of_species = re.findall("[a-zA-Z]+", item)[0]
                start_of_species_idx = item.index(first_char_of_species)

                species = item[start_of_species_idx:]
                coeff = item[:start_of_species_idx].strip()
                temp[species] = '1' if coeff == '' else coeff

                i += 1

            # skip '=', compound after '=' is species we are wanting to add to sourcedic
            i += 1

            species_of_interest = formula[i]

            i += 1

            while i < len(formula):
                item = formula[i]

                first_char_of_species = re.findall("[a-zA-Z]+", item)[0]
                start_of_species_idx = item.index(first_char_of_species)

                species = item[start_of_species_idx:]
                coeff = item[:start_of_species_idx].strip()
                temp[species] = '-' + '1' if coeff == '' else '-' + coeff

                i += 1

            sourcedic[species_of_interest] = ['', len(temp)]

            sol_species.append(species_of_interest)
                
            for key in temp.keys():
                sourcedic[species_of_interest].append(temp.get(key))
                sourcedic[species_of_interest].append(key)
                
            return sourcedic, species_of_interest, sol_species

        def get_solution_species(Rd, sourcedic, d, basis_species, sol_species, chargedic):

            i = d["SOLUTION_SPECIES"] + 1

            while i < d["PHASES"]:
                curr = Rd[i].strip()

                if curr == "":
                    i += 1
                    continue 
                
                is_formula = not curr.startswith("-") and not curr.startswith("#") and (curr[0].isupper() or curr[0].isdigit() or curr[0] == '.' or curr.startswith("e-"))
                # print(Rd[i], is_formula)
                
                if is_formula:
                    curr = curr.split(' + ')
                    
                    # this is a basis species - added second condition because 2CO2 = (CO2)2 was being read as a basis species when its not in phreeqc.dat
                    if len(curr) == 1 and not curr[0].isdigit():
                        basis_spec = curr[0].split('=')[-1].strip()
                        basis_spec = basis_spec if '#' not in basis_spec else basis_spec.split('#')[0].strip()  # some names have comments inline with the name 
                        basis_species.append(basis_spec)

                        sourcedic[basis_spec] = ['', 1]
                        sourcedic[basis_spec].append('1.0000')
                        sourcedic[basis_spec].append(basis_spec)
                    
                    # this is a solution species
                    else:
                        sourcedic, species_of_interest, sol_species = get_stoich_coeff_of_sol_species(curr, sourcedic, sol_species)

                        if Rd[i + 1].strip().startswith("-llnl_gamma"):
                            x = re.search(r"[-+]?\d*\.?\d+", Rd[i + 1].strip())
                            if x: chargedic[species_of_interest] = float(x.group())
                
                i += 1
            
            return sourcedic, basis_species, sol_species, chargedic

        # PHASES - next header found
        def get_phases(Rd, d, j, sourcedic, minerals, gases):
            i = d["PHASES"] + 1
            dj = d[j] - 1 if d[j] > i else len(Rd)

            while i < dj:
                curr = Rd[i].strip()
                # print("curr before if:", curr)
                # if not (curr.startswith("-") or curr.startswith("#") or curr.startswith("log_k") or curr.startswith("delta_h") or curr == "\n"):
                if curr == "":
                    i += 1
                    continue

                if curr.lower() == "references" or curr.upper() == "END":
                    # print("We found references at the end so we will skip them")
                    break

                if not (curr[0] == '-' or curr[0] == '#' or curr.startswith("log_k") or curr.startswith("delta_h") or curr.startswith("Vm") or curr.startswith("T_c")):
                    # since database is formatted as name \n formula, take both at once
                    name = Rd[i].strip()

                    name = name if '#' not in name else name.split('#')[0]
                    name = name if '\t' not in name else name.split('\t')[0]
                    name = name if '    ' not in name else name.split('    ')[0]


                    formula = Rd[i+1].strip()

                    # print("curr name:", name)
                    # print("curr formula:", formula)

                    sourcedic = get_stoich_coeff_of_phases(name, formula, sourcedic)

                    # TODO ? - phreeqc.dat has just a g instead of (g)
                    # name ex. 'Ar(g)', 'Hdg', 'CO2(g)'
                    gases.append(name) if '(g)' in name else minerals.append(name)
                        

                    i += 1

                i += 1


            return sourcedic, minerals, gases

        # RATES - len(Rd)
        def get_rates(Rd, d, rates):
            i = d['PHASES'] + 1
            
            while i < d['length'] - 1:
                curr = Rd[i].strip()
                
                if curr == '-start':
                    rates.append(Rd[i-1].strip())


                i += 1
                
            return rates

        def get_stoich_coeff_of_phases(name, formula, sourcedic):
            # species of interest is always the first compound on loftmost side

            # preprocessing formula line
            formula = formula.split(' + ')
            idx_of_equals = -1
            # This for-loop:
            # ['Fe+3', '3 H2O = Fe(OH)3', '3 H+'] -> ['Fe+3', '3 H2O', '=', 'Fe(OH)3', '3 H+']
            for i in range(len(formula)):
                formula[i] = formula[i].strip()
                if '=' in formula[i]:
                    # print("Found = ")
                    temp = re.split(r'=', formula[i])
                    formula = formula[:i] + [temp[0].strip()] + ['='] + [temp[1].strip()] + formula[i+1:]
                    idx_of_equals = i + 1
                    break

            species_of_interest = formula[0]
            # print(formula)
            # print(species_of_interest)

            i = 1 
            temp = {}

            while i < idx_of_equals:
                item = formula[i]
                # print(item)

                # find start of compound formula
                first_char_of_species = re.findall("[a-zA-Z]+", item)[0]
                start_of_species_idx = item.index(first_char_of_species)

                species = item[start_of_species_idx:]
                coeff = item[:start_of_species_idx].strip()
                temp[species] = '-1' if coeff == '' else '-' + coeff

                #print("temp sourcedic", temp)

                i += 1

            # print("temp sourcedic before = ", temp)

            i += 1


            while i < len(formula):
                item = formula[i]

                first_char_of_species = re.findall("[a-zA-Z]+", item)[0]
                start_of_species_idx = item.index(first_char_of_species)

                species = item[start_of_species_idx:]
                coeff = item[:start_of_species_idx].strip()
                temp[species] = '1' if coeff == '' else coeff
                

                # print("temp sourcedic", temp)

                i += 1

            sourcedic[name] = [species_of_interest, len(temp)]

            for key in temp.keys():
                sourcedic[name].append(temp.get(key))
                sourcedic[name].append(key)
                
            return sourcedic
        
        # MAIN 
        sourcedb_dir = self.sourcedb_dir

        codecs = findcodecs(sourcedb_dir)
        with open(sourcedb_dir, encoding=codecs) as g:
            Rd = g.readlines()          # Rd is list st each element is a line of text - includes \n 

        labels = ["SOLUTION_MASTER_SPECIES", "SOLUTION_SPECIES", "PHASES", "PITZER", "EXCHANGE_MASTER_SPECIES", "EXCHANGE_SPECIES", "SURFACE_MASTER_SPECIES", "SURFACE_SPECIES", "RATES", "length"]

        d = {}
        for x in labels:
            d[x] = -1


        act_param = {'activity_model' : '', 'act_list' : [], 'dataset_format' : ''}

        # set-up d list
        for i in range(len(Rd)):
            current_line = Rd[i].strip()

            if current_line == 'SOLUTION_MASTER_SPECIES':
                d['SOLUTION_MASTER_SPECIES'] = i
            elif current_line == 'SOLUTION_SPECIES':
                d['SOLUTION_SPECIES'] = i
            elif current_line == 'PHASES':
                d['PHASES'] = i
            elif current_line == 'PITZER':
                d['PITZER'] = i
                # act_param['activity_model'] = 'pitzer'
            elif current_line == 'EXCHANGE_MASTER_SPECIES':
                d['EXCHANGE_MASTER_SPECIES'] = i
            elif current_line == 'EXCHANGE_SPECIES':
                d['EXCHANGE_SPECIES'] = i
            elif current_line == 'SURFACE_MASTER_SPECIES':
                d['SURFACE_MASTER_SPECIES'] = i
            elif current_line == 'SURFACE_SPECIES':
                d['SURFACE_SPECIES'] = i
            elif current_line == 'RATES':
                d['RATES'] = i

            if d['PITZER'] != -1:
                act_param['activity_model'] = 'h-m-w' # specific-ion-interaction parameters for the Pitzer aqueous model.
            else:
                act_param['activity_model'] = 'debye huckel'

        d["length"] = len(Rd)

        unwanted_data = ['log_k', 'delta_h', '#', '-']     # lines to skip when parsing Rd
        sourcedic = {}
        elements, basis_species, sol_species, minerals, gases, rates = [], [], [], [], [], []
        chargedic = {}


        # if 'SOLUTION_MASTER_SPECIES' and 'SOLUTION_SPECIES' labels exist get elements between those labels
        if d['SOLUTION_MASTER_SPECIES'] != -1 and d['SOLUTION_SPECIES'] != -1:
            elements = get_solution_master_species(Rd, d, elements)

        # if 'SOLUTION_SPECIES' and 'PHASES' labels exist get basis and solution species between those labels
        if d['SOLUTION_SPECIES'] != -1 and d['PHASES'] != -1:
            sourcedic, basis_species, sol_species, chargedic = get_solution_species(Rd, sourcedic, d, basis_species, sol_species, chargedic)

        # find next header written in database 
        
        if d['PHASES'] != -1:
            j = 3
            while j < 8:
                if d[labels[j]] != -1:
                    break
                j += 1

        # 'PHASES' until the next header 
        sourcedic, minerals, gases = get_phases(Rd, d, labels[j], sourcedic, minerals, gases)

        if d['PHASES'] != -1:
            rates = get_rates(Rd, d, rates)

        # [element, basis, redox, aqueous, minerals, gases, oxides] TODO --- REDOX??? --- this was working incorrectly 
        specielist = [elements, basis_species, [], sol_species, minerals, gases, rates]

        self.sourcedic = sourcedic
        self.specielist = specielist
        self.speciecat = ['elements', 'basis', 'redox', 'aqueous', 'minerals', 'gases', 'rates']
        self.chargedic = chargedic
        self.act_param = act_param
        
        self.Rd = Rd
        self.d = d
         
        return




def dbaccess_modify(in_filename = None, dbaccess = None, out_filename = None):
    """
    This function loads thermodynamic data from a csv files and appends/replace the corresponding species thermo data and writes out a modified direct-access database
    Parameters
    ----------
        in_filename : string
            CSV filename and location   \n
        dbaccess : string
            direct-access database filename and location  (optional)  \n
        out_filename : string
            newly modified direct-access database filename and location    (optional) \n

    Returns
    -------
        Output the newly modified direct-access with filename described in 'out_filename' if specified.

    Examples
    --------
    >>> dbaccess_modify(in_filename = 'geotpd_data_block_cr.csv')

    """
    
    if dbaccess is None:
        dbaccess = './default_db/speq21.dat'
        dbaccess = os.path.join(os.path.dirname(os.path.abspath(__file__)), dbaccess)

    with open(dbaccess, "r") as file:
        lines = file.readlines()
        
    df = pd.read_csv(in_filename)
    
    for i in df.index:
        name = df.loc[i, "name"]
        abbrv = df.loc[i, "abbrv"]
        name = name.replace("*", ":")
        if pd.isnull(abbrv) is True:
            abbrv = name
        formula = df.loc[i, "formula"]
        formula = formula.replace("*", ":")
        ref1 = df.loc[i, "ref1"]
        ref2 = df.loc[i, "ref2"]
        if pd.isnull(ref2) is False:
            ref = "ref:" + ref1 + "," + ref2
        else:
            ref = "ref:" + ref1
    
        units = df.loc[i, "E_units"]
        state = df.loc[i, "state"]
    
        pattern = r"([A-Z][a-z]*)(\d*)|(\()|(\))(\d*)|(\:)(\d*)"
        elements = re.findall(pattern, formula)
    
        stack = []
        current_element = ""
        count_after_colon = None
        for element, count1, open_paren, close_paren, count2, colon, count3 in elements:
            if element and pd.isnull(count_after_colon):
                current_element = element
                stack.append((element, int(count1) if count1 else 1))
            elif open_paren and pd.isnull(count_after_colon):
                stack.append("(")
            elif close_paren and pd.isnull(count_after_colon):
                count_outside_paren = int(count2) if count2 else 1
                elements_inside_paren = []
                while stack[-1] != "(":
                    popped_element, popped_count = stack.pop()
                    if popped_element == "(":
                        continue
                    elements_inside_paren.insert(0, (popped_element, popped_count))
                stack.pop()
                for e, c in elements_inside_paren:
                    stack.append((e, c * count_outside_paren))
            elif colon:
                count_after_colon = int(count3) if count3 else 1
            elif element and count_after_colon >= 1:
                current_element = element
                c = int(count1) if count1 else 1
                stack.append((element, c * count_after_colon))
            else:
                stack.append((current_element, int(count1) if count1 else 1))
    
        formula_parsed = ""
    
        element_counts = {}
        for element, count in stack:
            if element in element_counts:
                element_counts[element] += count
            else:
                element_counts[element] = count
    
        for element, count in element_counts.items():
            formula_parsed += element + ("(%d)" % count if count > 1 else "(1)")
    
        if state == "aq":
            charge = df.loc[i, "z.T"]
            if charge >= 0:
                formula_parsed += "+" + f"({charge})"
            elif charge <= 0:
                formula_parsed += "-" + f"({abs(charge)})"
        else:
            formula_parsed += "+" + "(0)"
    
        if units == "J":
            coeff = 1 / 4.184
        else:
            coeff = 1
    
        col = ["H"]
        df[col] = df[col].fillna(999999)
        col = ["V"]
        df[col] = df[col].fillna(0)
        dG = df.loc[i, "G"] * coeff
        dH = df.loc[i, "H"] * coeff
        S = df.loc[i, "S"] * coeff
        V = df.loc[i, "V"]
    
        if df.loc[i, "model"] == "CGL":
            a = df.loc[i, "a1.a"] * coeff
            b = df.loc[i, "a2.b"] * coeff
            c = df.loc[i, "a3.c"] * coeff
        elif df.loc[i, "model"] == "HKF":
            a1 = df.loc[i, "a1.a"] * coeff
            a2 = df.loc[i, "a2.b"] * coeff
            a3 = df.loc[i, "a3.c"] * coeff
            a4 = df.loc[i, "a4.d"] * coeff
            c1 = df.loc[i, "c1.e"] * coeff
            c2 = df.loc[i, "c2.f"] * coeff
            w = df.loc[i, "omega.lambda"] * coeff
    
        if state == "cr":
    
            location = [
                j
                for j, x in enumerate(lines)
                if "minerals that do not undergo phase transitions" in x
            ]
            location2 = [j for j, x in enumerate(lines) if name in x]
    
            name_pad = "{: <20}".format(name)
            abbrv_pad = "{: <20}".format(abbrv)
            ref_pad = "{: <20}".format(ref)
            dG_pad = "{: >18.1f}".format(dG)
            dH_pad = "{: >14.1f}".format(dH)
            S_pad = "{: >10.3f}".format(S)
            V_pad = "{: >10.3f}".format(V)
            a_pad = "{: >18.6f}".format(a)
            b_pad = "{: >14.6f}".format(b)
            c_pad = "{: >14.6f}".format(c)
            Ttrans = df.loc[i, "z.T"]
            Trans_pad = "{: >18.4f}".format(Ttrans)
    
            if not location2:
    
                lines.insert(location[0] + 2, (" " + name_pad + formula + "\n"))
                lines.insert(location[0] + 3, (" " + abbrv_pad + formula_parsed + "\n"))
                lines.insert(location[0] + 4, (" " + ref_pad + "\n"))
                lines.insert(location[0] + 5, (dG_pad + dH_pad + S_pad + V_pad + "\n"))
                lines.insert(location[0] + 6, (a_pad + b_pad + c_pad + "\n"))
                lines.insert(location[0] + 7, (Trans_pad + "\n"))
            else:
                lines[location2[0]] = " " + name_pad + formula + "\n"
                lines[location2[0] + 1] = " " + abbrv_pad + formula_parsed + "\n"
                lines[location2[0] + 2] = " " + ref_pad + "\n"
                lines[location2[0] + 3] = dG_pad + dH_pad + S_pad + V_pad + "\n"
                lines[location2[0] + 4] = a_pad + b_pad + c_pad + "\n"
                lines[location2[0] + 5] = Trans_pad + "\n"
    
        elif state == "aq":
    
            name_pad = "{: <20}".format(name)
            abbrv_pad = "{: <20}".format(abbrv)
            ref_pad = "{: <20}".format(ref)
            dG_pad = "{: >18.1f}".format(dG)
            dH_pad = "{: >14.1f}".format(dH)
            S_pad = "{: >10.3f}".format(S)
            V_pad = "{: >14.4f}".format(V)
            a1_pad = "{: >14.4f}".format(a1)
            a2_pad = "{: >12.4f}".format(a2)
            a3_pad = "{: >12.4f}".format(a3)
            c1_pad = "{: >14.4f}".format(c1)
            c2_pad = "{: >12.4f}".format(c2)
            w_pad = "{: >12.4f}".format(w)
            charge_pad = "{: >15.0f}".format(charge)
    
            location = [j for j, x in enumerate(lines) if "    aqueous species" in x]
            location2 = [j for j, x in enumerate(lines) if name in x]
    
            if not location2:
    
                lines.insert(location[0] + 2, (" " + name_pad + formula + "\n"))
                lines.insert(location[0] + 3, (" " + abbrv_pad + formula_parsed + "\n"))
                lines.insert(location[0] + 4, (" " + ref_pad + "\n"))
                lines.insert(location[0] + 5, (dG_pad + dH_pad + S_pad + "\n"))
                lines.insert(location[0] + 6, (V_pad + a1_pad + a2_pad + a3_pad + "\n"))
                lines.insert(
                    location[0] + 7, (c1_pad + c2_pad + w_pad + charge_pad + "\n")
                )
            else:
                lines[location2[0]] = " " + name_pad + formula + "\n"
                lines[location2[0] + 1] = " " + abbrv_pad + formula_parsed + "\n"
                lines[location2[0] + 2] = " " + ref_pad + "\n"
                lines[location2[0] + 3] = dG_pad + dH_pad + S_pad + "\n"
                lines[location2[0] + 4] = V_pad + a1_pad + a2_pad + a3_pad + "\n"
                lines[location2[0] + 5] = c1_pad + c2_pad + w_pad + charge_pad + "\n"
    
    if out_filename is None:
        out_filename = os.path.basename(dbaccess).split('.')[0]
        fout = open(os.path.join(os.path.dirname(in_filename), out_filename + '_mod.dat'), 'w+') 
    else:
        fout = open(os.path.join(os.path.dirname(in_filename), out_filename + '.dat'), 'w+') 
    
    fout.writelines(lines)
    fout.close()
    
    return
