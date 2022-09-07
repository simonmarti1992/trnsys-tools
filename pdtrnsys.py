import glob
import os
import pickle

import pandas as pd
from myClass import getSched


class Trnsys():

    '''
    ===
    Une description à ajouter ici
    ===
    '''


    def __init__(self, typeBati='residentiel'):
        lesBalises = {
            'layers': '''*  L a y e r s''',
            'inputs': '''*  I n p u t s''',
            'schedules': '''*  S c h e d u l e s''',
            'construction': '''*  C O N S T R U C T I O N (Wall, Floor, Ceiling,..)''',
            'windows': '''*  W i n d o w s''',
            'gain': '''*  G a i n s''',
            'comfort': '''*  C o m f o r t''',
            'infil': '''*  I n f i l t r a t i o n''',
            'vent': '''*  V e n t i l a t i o n''',
            'cool': '''*  C o o l i n g''',
            'heat': '''*  H e a t i n g''',
            'dlight': '''*  D a y l i g h t   C o n t r o l''',
            'zones': '''*  Z o n e s'''}
        # layer dict
        xls = pd.ExcelFile('myLayers.xlsx', engine='openpyxl')
        self.layerDict = pd.read_excel(xls, 'all')
        # wall dict
        xls = pd.ExcelFile('myWalls.xlsx', engine='openpyxl')
        self.wallDict = pd.read_excel(xls, 'all')
        with open('dataLib18.pickle', 'rb') as handle:
            libTrnsys = pickle.load(handle)
        self.libTrnsys = libTrnsys
        # TODO : faire un switch avec les balises du dck
        self.balise = lesBalises
        self.typeBuilding = typeBati

    def read(self, name='simple.b18'):
        dat_txt = open('{}'.format(name), "r")
        self.myList = dat_txt.readlines()
        dat_txt.close()
        return self

    # ===================================================================================================================
    #                                      ajout des schedules - b18
    # ===================================================================================================================
    def addLayers(self):
        for k, line in enumerate(self.myList):
            if self.balise['layers'] in line:
                self.startline = k
            else:
                pass
        myStr = ''
        for layer in [x for x in self.layerDict['LAYER'] if str(x)!='nan']:
            myStr = myStr + 'LAYER {}\n'.format(layer) + \
                    ' CONDUCTIVITY = {}: CAPACITY = {}: DENSITY = {}: PERT = {}: PENRT = {}\n'.format(
                        self.layerDict['CONDUCTIVITY'].loc[(self.layerDict['LAYER']==layer)].values[0],
                        self.layerDict['CAPACITY'].loc[(self.layerDict['LAYER']==layer)].values[0],
                        self.layerDict['DENSITY'].loc[(self.layerDict['LAYER']==layer)].values[0],
                        self.layerDict['PERT'].loc[(self.layerDict['LAYER']==layer)].values[0],
                        self.layerDict['PENRT'].loc[(self.layerDict['LAYER']==layer)].values[0])
        toGo = self.myList
        toGo.insert(self.startline + 2, myStr)
        self.myList = toGo
        self.LAYERS = myStr
        return self

    def addConstruction(self):
        for k, line in enumerate(self.myList):
            if self.balise['construction'] in line:
                self.startline = k
            else:
                pass
        myStr = ''
        listWalls = list(dict.fromkeys(self.wallDict.CONSTRUCTION))
        for wall in [x for x in listWalls if str(x)!='nan']:
            dataF = self.wallDict.loc[(self.wallDict['CONSTRUCTION']==wall)]
            layers = ' '.join(list(dataF['LAYERS'].values))
            thickness = ' '.join([str(x) for x in list(dataF['THICKNESS'].values)])
            dataFirst = dataF.loc[(dataF['LAYERS']==list(dataF['LAYERS'].values)[0])]
            absfront = dataFirst['ABS-FRONT'].values[0]
            absback = dataFirst['ABS-BACK'].values[0]
            epsfront = dataFirst['EPS-FRONT'].values[0]
            epsback = dataFirst['EPS-BACK'].values[0]
            hfront = dataFirst['HFRONT'].values[0]
            hback = dataFirst['HBACK'].values[0]
            myStr = myStr + \
                    'CONSTRUCTION {}\n'.format(wall) + \
                    ' LAYERS   = {}\n THICKNESS= {}\n ABS-FRONT= {}     : ABS-BACK= {}\n EPS-FRONT= {}   : EPS-BACK= {}\n HFRONT   = {} : HBACK= {}\n'.format(
                        layers, thickness, absfront, absback, epsfront, epsback, hfront, hback)
        toGo = self.myList
        toGo.insert(self.startline + 2, myStr)
        self.myList = toGo
        self.WALLS = myStr
        return self

    def addSchedule(self):
        for k, line in enumerate(self.myList):
            if self.balise['schedules'] in line:
                self.startline = k
            else:
                pass
        myStr = ''
        for item in self.libTrnsys[self.typeBuilding]['schedule']:
            myStr = myStr + item
        toGo = self.myList
        toGo.insert(self.startline + 2, myStr)
        self.myList = toGo
        self.SCHEDULES = myStr
        self.nameSCHEDULES = [x.split(' ')[-1] for x in myStr.split('\n') if 'SCHEDULE' in x]
        self.sch_SCHEDULES = getSched({x.split(' ')[-1]:x.split(' ')[-1] for x in myStr.split('\n') if 'SCHEDULE' in x})
        return self

    def addGains(self):
        for k, line in enumerate(self.myList):
            if self.balise['gain'] in line:
                self.startline = k
            else:
                pass
        myStr = ''
        for item in self.libTrnsys[self.typeBuilding]['gain']:
            myStr = myStr + item
        toGo = self.myList
        toGo.insert(self.startline + 2, myStr)
        self.myList = toGo
        self.GAINS = myStr
        self.nameGAINS = [x.split(' ')[-1] for x in myStr.split('\n') if 'GAIN' in x]
        self.nameGAIN_occ = [x.split(' ')[-1] for x in myStr.split('\n') if 'GAIN' in x and 'Occ' in x]
        self.nameGAIN_Dev = [x.split(' ')[-1] for x in myStr.split('\n') if 'GAIN' in x and 'Dev' in x]
        self.nameGAIN_Ltg = [x.split(' ')[-1] for x in myStr.split('\n') if 'GAIN' in x and 'Ltg' in x]

        self.sch_GAIN_occ = getSched({x.split(' ')[-1]: x.split(' ')[-1] for x in myStr.split('\n') if 'GAIN' in x and 'Occ' in x})
        self.sch_GAIN_Dev = getSched({x.split(' ')[-1]: x.split(' ')[-1] for x in myStr.split('\n') if 'GAIN' in x and 'Dev' in x})
        self.sch_GAIN_Ltg = getSched({x.split(' ')[-1]: x.split(' ')[-1] for x in myStr.split('\n') if 'GAIN' in x and 'Ltg' in x})

        return self

    def addClim(self):
        for k, line in enumerate(self.myList):
            if self.balise['cool'] in line:
                self.startline = k
            else:
                pass
        myStr = ''
        for item in self.libTrnsys[self.typeBuilding]['cool']:
            myStr = myStr + item
        toGo = self.myList
        toGo.insert(self.startline + 2, myStr)
        self.myList = toGo
        self.CLIM = myStr
        self.nameCLIM = [x.split(' ')[-1] for x in myStr.split('\n') if 'COOLING' in x]
        self.sch_CLIM = getSched({x.split(' ')[-1]:x.split(' ')[-1] for x in myStr.split('\n') if 'COOLING' in x})
        return self

    def addHeat(self):
        for k, line in enumerate(self.myList):
            if self.balise['heat'] in line:
                self.startline = k
            else:
                pass
        myStr = ''
        for item in self.libTrnsys[self.typeBuilding]['heat']:
            myStr = myStr + item
        toGo = self.myList
        toGo.insert(self.startline + 2, myStr)
        self.myList = toGo
        self.HEAT = myStr
        self.nameHEAT = [x.split(' ')[-1] for x in myStr.split('\n') if 'HEATING' in x]
        self.sch_HEAT = getSched({x.split(' ')[-1]:x.split(' ')[-1] for x in myStr.split('\n') if 'HEATING' in x})
        return self

    def addDlight(self):
        for k, line in enumerate(self.myList):
            if self.balise['dlight'] in line:
                self.startline = k
            else:
                pass
        myStr = ''
        for item in self.libTrnsys[self.typeBuilding]['dlight']:
            myStr = myStr + item
        toGo = self.myList
        toGo.insert(self.startline + 2, myStr)
        self.myList = toGo
        self.DLIGHT = myStr
        self.nameDLIGHT = [x.split(' ')[-1] for x in myStr.split('\n') if 'DCONTROL' in x]
        self.sch_DLIGHT = getSched({x.split(' ')[-1]:x.split(' ')[-1] for x in myStr.split('\n') if 'DCONTROL' in x})
        return self

    def addInfiltration(self):
        for k, line in enumerate(self.myList):
            if self.balise['infil'] in line:
                self.startline = k
            else:
                pass
        myStr = ''
        for item in self.libTrnsys[self.typeBuilding]['infil']:
            myStr = myStr + item
        toGo = self.myList
        toGo.insert(self.startline + 2, myStr)
        self.myList = toGo
        self.INFILTRATION = myStr
        self.nameINFILTRATION = [x.split(' ')[-1] for x in myStr.split('\n') if 'INFILTRATION' in x]
        self.sch_INFIL = getSched({x.split(' ')[-1]:x.split(' ')[-1] for x in myStr.split('\n') if 'INFILTRATION' in x})
        return self

    def addVentil(self):
        for k, line in enumerate(self.myList):
            if self.balise['vent'] in line:
                self.startline = k
            else:
                pass
        myStr = ''
        for item in self.libTrnsys[self.typeBuilding]['vent']:
            myStr = myStr + item
        toGo = self.myList
        toGo.insert(self.startline + 2, myStr)
        self.myList = toGo
        self.VENTIL = myStr
        self.nameVENTILATION = [x.split(' ')[-1] for x in myStr.split('\n') if 'VENTILATION' in x]
        self.sch_VENTIL = getSched({x.split(' ')[-1]:x.split(' ')[-1] for x in myStr.split('\n') if 'VENTILATION' in x})

        return self

    # ===================================================================================================================
    #                                      travail sur les zones - b18
    # ===================================================================================================================
    def recupZone(self, name='simple'):
        for k, line in enumerate(self.myList):
            if '*  Z o n e  {}'.format(name) in line:
                start = k
                break
            else:
                pass
        for k, line in enumerate(self.myList[(start + 2):]):
            if '*------------------------------------' in line:
                end = k
                break
        self.myZone = self.myList[start + 2:start + end + 2]
        self.start_zone = start + 2
        self.end_zone = start + end + 2
        return self

    def addClimZone(self, clim='default'):
        if clim=='default':
            clim = self.nameCLIM[0]
        else:
            clim = clim
        for k, line in enumerate(self.myZone):
            if 'REGIME' in line:
                toInsert = ' COOLING     = {}\n'.format(clim)
                self.myList.insert(self.start_zone + k + 1, toInsert)
            else:
                pass
        return self

    def addHeatingZone(self, heat='default'):
        if heat=='default':
            heat = self.nameHEAT[0]
        else:
            heat = heat
        for k, line in enumerate(self.myZone):
            if 'REGIME' in line:
                toInsert = ' HEATING     = {}\n'.format(heat)
                self.myList.insert(self.start_zone + k + 1, toInsert)
            else:
                pass
        return self

    def addVentilationZone(self, vent='default'):
        if vent=='default':
            vent = self.nameVENTILATION[0]
        else:
            vent = vent
        for k, line in enumerate(self.myZone):
            if 'REGIME' in line:
                toInsert = ' VENTILATION = {}\n'.format(vent)
                self.myList.insert(self.start_zone + k + 1, toInsert)
            else:
                pass
        return self

    def addInfiltrationZone(self, infil='default'):
        ''''
        Un test ici !
        '''
        if infil=='default':
            infil = self.nameINFILTRATION[0]
        else:
            infil = infil
        for k, line in enumerate(self.myZone):
            if 'REGIME' in line:
                toInsert = ' INFILTRATION= {}\n'.format(infil)
                self.myList.insert(self.start_zone + k + 1, toInsert)
            else:
                pass
        return self

    def addGainsZone(self, Occ='default', Dev='default', Ltg='default'):
        # Occ
        if Occ=='default':
            Occ = self.nameGAIN_occ[0]
        else:
            Occ = Occ
        # Dev
        if Dev=='default':
            Dev = self.nameGAIN_Dev[0]
        else:
            Dev = Dev
        # Ltg
        if Ltg=='default':
            Ltg = self.nameGAIN_Ltg[0]
        else:
            Ltg = Ltg

        for k, line in enumerate(self.myZone):
            if 'REGIME' in line:
                toInsert = ''' GAIN        = {} : SCALE= 1 : GEOPOS= 0 : SCALE2= 1 : FRAC_REFAREA= 1
 GAIN        = {} : SCALE= 1 : GEOPOS= 0 : SCALE2= 1 : FRAC_REFAREA= 1
 GAIN        = {} : SCALE= 1 : GEOPOS= 0 : SCALE2= 1 : FRAC_REFAREA= 1\n'''.format(Occ, Dev, Ltg)
                self.myList.insert(self.start_zone + k + 1, toInsert)
            else:
                pass
        return self

    # ===================================================================================================================
    #                                      travail sur le dck
    # ===================================================================================================================
    def meteo(self, weatherFile='FRA_AC_La.Rochelle.073150_TMYx.2004-2018.epw'):
        for k, line in enumerate(self.myList):
            if '*$MODEL .\Weather' in line:
                modifPath_type = k
            if 'ASSIGN' in line and 'tm2' in line:
                modifEpw = k
            if '* User defined CONSTANTS' in line:
                modifCte = k
            if '! 1 File Type' in line:
                modifFileType = k
            if '! 2 Logical unit' in line:
                modifUnit = k
            else:
                pass
        self.myList[modifPath_type] = self.myList[modifPath_type].replace('Meteonorm Files (TM2)\Type15-6.tmf',
            'Energy+ Weather Files (EPW)\Type15-3.tmf')
        self.myList[modifCte + 1] = '*$USER_CONSTANTS\n' + '\n' + '*$USER_CONSTANTS_END\n'
        self.myList[modifEpw] = self.myList[modifEpw].replace(r'ASSIGN .\Weather\US-TMY2\US-WI-Madison-14837.tm2 32',
            '*** External files\n' +
            r'ASSIGN "{}\weather\{}" 30'.format(os.getcwd(), weatherFile))
        self.myList[modifFileType] = self.myList[modifFileType].replace('6', '3')
        self.myList[modifUnit] = self.myList[modifUnit].replace('32', '30')
        return self


    def addPrinter(self, infTable = 'test'):
        aColler = [

            '*------------------------------------------------------------------------------\n',
            '\n',
            '* Model "Type25c" (Type 25)\n',
            '*\n',
            '\n',
            'UNIT 51 TYPE 25 Type25c\n',
            '*$UNIT_NAME Type25c\n',
            r'*$MODEL .\Output\Printer\Unformatted\No Units\Type25c.tmf' + '\n',
            '*$POSITION 955 543\n',
            '*$LAYER Outputs  #\n',
            'PARAMETERS 10\n',
            'STEP        ! 1 Printing interval\n',
            'START        ! 2 Start time\n',
            'STOP        ! 3 Stop time\n',
            '32        ! 4 Logical unit\n',
            '0        ! 5 Units printing mode\n',
            '0        ! 6 Relative or absolute start time\n',
            '-1        ! 7 Overwrite or Append\n',
            '-1        ! 8 Print header\n',
            '0        ! 9 Delimiter\n',
            '1        ! 10 Print labels\n',
            'INPUTS {}\n'.format(len(infTable) + 1),
            '*** INITIAL INPUT VALUES\n',
            '\n',
            '*** External files\n',
            'ASSIGN "myOutput.csv" 32\n',
            '* |? Output file for printed results | 1000\n',
            '* ------------------------------------------------------------------------------\n',
        ]
        toADD = []
        myVar = ''

        for nameVar, numVar in zip(list(infTable.keys()), infTable.values()):
            toADD.append('56, {}        ! Building: {} - {} ->Input to be printed - {}\n'.format(numVar, numVar, nameVar, numVar))
            myVar = myVar+'\n'+nameVar

        toADD.append('15,1 		! Weather:Dry bulb temperature ->Input to be printed-35\n')
        myVar = myVar + ' Tamb\n'

        for k,line in enumerate(aColler):
            if 'INPUTS ' in line:
                insertInput = k+1
            if '*** INITIAL INPUT' in line:
                insertListInput = k
        aColler.insert(insertListInput+1, myVar)

        for k, item in enumerate(toADD):
            aColler.insert(insertInput+k, item)

        for k, line in enumerate(self.myList):
            if '* OUTPUTS' in line:
                goodLine = k+1
        for ii, toInsert in enumerate(aColler):
            self.myList.insert(goodLine + ii, toInsert)

        return self

    def zones(self):
        for k, line in enumerate(self.myList):
            if self.balise['zones'] in line:
                self.startline = k
            else:
                pass
        self.listZones = self.myList[self.startline + 2].replace('ZONES ', '').replace('\n', '').split(' ')[:-1]
        print(self.listZones)
        return self

    def write(self, name='monFichier.b18'):
        try:
            with open('try.txt', 'w') as f:
                for item in self.myList:
                    f.write(item)
            os.rename('try.txt', name)
        except:
            os.remove('try.txt')
            with open('try.txt', 'w') as f:
                for item in self.myList:
                    f.write(item)
            try:
                os.rename('try.txt', name)
            except:
                os.remove(name)
                os.rename('try.txt', name)
        return self


class infFile():
    def __init__(self, infFile='simple.inf'):
        dat_txt = open(infFile, "r")
        self.myList = dat_txt.readlines()
        dat_txt.close()


    def getTable(self):
        tableCorresp = {}
        for k, line in enumerate(self.myList):
            if 'OutNr  | Label' in line:
                numLine = k
        myList = self.myList[numLine:]
        for line in myList:
            if '* |    ' in line:
                num = line.split('* |    ')[1].split(' | ')[0]
                nameVar = line.split('* |    ')[1].split((' | ')[1])[1].strip()
                tableCorresp[nameVar] = num
            elif '* |   ' in line:
                num = line.split('* |   ')[1].split(' | ')[0]
                nameVar = line.split('* |   ')[1].split((' | ')[1])[1].strip()
                tableCorresp[nameVar] = num
        self.tableCorresp = tableCorresp
        return self


if __name__=="__main__":
    # 'residentiel', 'hotel', 'bureau', 'ecole', 'commerce', 'restaurant'
    # ajout des gains
    # ================
    from myClass import Scenario
    scenario = Scenario()
    typeDeBati = 'commerce'
    monB18 = Trnsys(typeBati=typeDeBati)
    monB18.read(r'./base/entree.b18') \
        .addSchedule() \
        .addLayers() \
        .addClim() \
        .addHeat() \
        .addConstruction() \
        .addDlight() \
        .addGains() \
        .addVentil() \
        .addInfiltration()

    # Gestion des zones
    # ================
    monB18.zones()
    monB18.recupZone('entree') \
        .addClimZone(clim='default') \
        .addHeatingZone(heat='default') \
        .addVentilationZone(vent='default') \
        .addInfiltrationZone(infil='default') \
        .addGainsZone(Occ='default', Dev='default', Ltg='default')

    # écriture du .b18
    # ================
    # residentiel.write('{}.b18'.format(typeDeBati))
    monB18.write('./ok-files/entree.b18')


    # écriture modification du .dck
    # ================
    monDCK = Trnsys(typeBati=typeDeBati)
    monDCK.read(r'./base/entree.dck')
    monDCK.meteo('FRA_AC_La.Rochelle.073150_TMYx.2004-2018.epw').write('./ok-files/entree.dck')

    # écriture modification du .inf
    # ================
    inf = infFile(r'./base/entree.inf').getTable()
    inf.tableCorresp
    monDCK.addPrinter(infTable = inf.tableCorresp).write('./ok-files/entree.dck')



    # CLEAN
    toDelete = glob.glob('*.bld') + glob.glob('*.inf') + glob.glob('*.trn') + glob.glob('*.log') + glob.glob('*.tpf')
    for file in toDelete:
        os.remove(file)
    print('###################\nFIN\n###################')
