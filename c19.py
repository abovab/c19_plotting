'''Andrew Burton. 9.29.2020'''

'''Plots daily/total death data due to covid and/or daily hospitalization               
   rates/morbidity for input jurisdiction .'''
################################################################################

import os
import csv
import logging
import argparse
import numpy as np
from datetime import datetime
from matplotlib import gridspec
import matplotlib.pyplot as plt
import matplotlib.ticker as tick

################################################################################

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler('c19.log', 'w')
fileHandler.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)

streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.INFO)
logger.addHandler(streamHandler)

fileName = 'Reference_hospitalization_all_locs.csv'

################################################################################

def readCSV(aFile,locID,i=False):
    '''Reads input csv file (aFile) and returns numpy array of data from input
       jurisdiction locID.'''
    logger.debug(f'Initiating readCSV_H(), reading: {aFile}, locID: {locID}')
    cData, dates = [], []
    with open(aFile,'r') as f:
        r = csv.reader(f)
        for l in r:
            if l[3] == locID:
                dates.append(datetime.strptime(l[2],"%Y-%m-%d"))
                if type(i) == int:
                    if l[38] == '':
                        cData.append([l[i],l[i+1],l[i+2],0])
                    else:
                        cData.append([l[i],l[i+1],l[i+2],float(l[38])])
                else:
                    if l[41] == '':
                        cData.append([h for h in l[42:45]] +
                                     [j for j in l[ 4:13]] +
                                     [k for k in l[46:49]] + [np.NaN])
                    else:
                        cData.append([h for h in l[42:45]] +
                                     [j for j in l[ 4:13]] +
                                     [k for k in l[46:49]] + [float(l[41])])
    return dates, np.array(cData, dtype=float)

################################################################################

def getLocations(aFile):
    '''Reads input csv file (aFile) and returns set of jurisdictions in file.'''
    logger.debug(f'Initiating getLocations(), reading: {aFile}')
    with open(aFile,'r') as f:
        r = csv.reader(f)
        next(r)
        return {l[1].lower().replace(' ','_'):l[3] for l in r}

################################################################################

def getProjDate(list1,list2 = False):
    '''Takes input list(s) and returns index of when data projections start.'''
    logger.debug('Initiating getProjDate()')

    if type(list2) == bool:
        for i in range(len(list1)-1,0,-1):
            if np.isnan(list1[i]) == False:
                return i
    for i in range(len(list1)):
        if list1[i] != list2[i]:
            return i

################################################################################

def formatYticks(n,pos):
  '''Formats input float and returns truncated number as a string.'''
  logger.debug(f'Initiating formatYticks() on {n}')
  if int(n) > 999999:
    n = str(int(n/1000000)) + 'M'
  elif int(n) > 999:
    n = str(int(n/1000)) + 'K'
  return n

################################################################################

def plotIntervals(ax,dates,avg,min,max,legend,alpha=0.2):
    '''Creates plots with confidence intervals of input data.
        Inputs:
            ax (matplot AxesSublot object): subplot to which plot will be added.
            dates (list of datetime objects): list of dates.
            avg, min, max (numpy arrays): data to be plotted.
            legend (list of strings): Defines plot colors and labels.
    '''
    logger.debug(f'Initiating plotIntervals()')
    if legend == False:
        legend = ['','','orange','gray','Average']
        ax.plot(dates,max,color='red',alpha=0.8,label='Worst Case')
        ax.plot(dates,min,color='yellow',alpha=0.8,label='Best Case')
    else:
        ax.plot(dates,max,color=legend[0],alpha=0.8)
        ax.plot(dates,min,color=legend[1],alpha=0.8)
    ax.plot(dates,avg,color=legend[2],label=legend[4])
    ax.fill_between(dates,max,avg,color=legend[3],interpolate=True,alpha=alpha)
    ax.fill_between(dates,min,avg,color=legend[3],interpolate=True,alpha=alpha)
    ax.fill_between(dates,max,0,color=legend[3],interpolate=True,alpha=alpha-.1)
    return ax

################################################################################
def plotData_D(dates,cArray,location,tLabel,proj,log):
    '''Plots daily or total covid death counts for given jurisdiction.
        Inputs:
          dates (list of datetime objects): list of dates.
          cArray (numpy array): data to plotted.
          location (string): jurisdiction being plotted.
          tLabel (boolean): used for plot title (daily vs. total).
          proj (boolean): if True, future projections plotted.
          log (boolean): if True, changes y-axis to log scale.
        Returns: None
    '''
    logger.debug(f'Initiating plotData_D(), loc:{location}, plotting:{tLabel}')
    title = location.replace('_',' ').title()

    if tLabel:
        tLabel = 'Total'
    else:
        tLabel = 'Daily'

    projIndex = getProjDate(cArray[:,0],cArray[:,2])
    if proj == False:
        dates = dates[:projIndex]
        cArray = cArray[:projIndex,:]

    plt.style.use('dark_background')
    fig,axs = plt.subplots(figsize=(20,10))
    gs = gridspec.GridSpec(2, 1, height_ratios=[2,1])

    ax0 = plt.subplot(gs[0])
    if proj:
        ax0.vlines(dates[projIndex],0,max(cArray[:,2]),color='white',
                   linestyles='dashed',alpha=0.5)
        plotIntervals(ax0,dates,cArray[:,0],cArray[:,1],cArray[:,2],False)
        ax0.legend(loc="upper left")

    ax0.plot(dates[:projIndex+1],cArray[:projIndex+1,0],
             color='white',label='Observed')
    if log:
        ax0.set_yscale('log')
        log_string = ' (log)'
    else:
        log_string = ''
    ax0.set_ylabel(f'Deaths {log_string}')
    ax0.yaxis.set_major_formatter(tick.FuncFormatter(formatYticks))

    plt.title(f'{tLabel} Covid Deaths and Mobility Data: {title}',loc="left")

    ax1 = plt.subplot(gs[1], sharex=ax0)
    ax1.plot(dates,cArray[:,3],color='white')
    ax1.hlines(0,dates[0],dates[-1],
               color='cyan',linestyles='dashed',alpha=0.5)
    if proj:
        ax1.vlines(dates[projIndex],min(cArray[:,3]),max(cArray[:,3]),
                   color='white',linestyles='dashed',alpha=0.5)
    ax1.set_ylabel('Change in Mobility')
    plt.setp(ax0.get_xticklabels(), visible=False)
    plt.subplots_adjust(hspace=0)

    #plt.savefig(f'{location}_{tLabel}Deaths.png')
    plt.show()

################################################################################

def plotData_H(dates,cArray,location,proj,log):
    '''Plots covid cases and hospitalization data for given jurisdiction.
        Inputs:
            dates (list of datetime objects): list of dates.
            cArray (numpy array): data to plotted.
            location (string): jurisdiction being plotted.
            proj (boolean): if True, future projections plotted.
            log (boolean): if True, changes y-axis to log scale.
        Returns: None
    '''
    logger.debug(f'Initiating plotData_H(), loc: {location}')

    title = location.replace('_',' ').title()
    legend = [['orange']*4+['Estimated Infected'], ['blue']*4+['Hospitalized'],
              ['purple']*4+['Hospitalized in ICU'],['red']*4+['Ventilated']]
    alpha = [0.2,0.3,0.5,0.2]

    projIndex = getProjDate(cArray[:,-1])
    if proj == False:
        dates = dates[:projIndex]
        cArray = cArray[:projIndex,:]

    plt.style.use('dark_background')
    fig,axs = plt.subplots(figsize=(20,10))
    gs = gridspec.GridSpec(2,1,height_ratios=[2,1])

    ax0 = plt.subplot(gs[0])
    if proj:
        ax0.vlines(dates[projIndex], 0, max(cArray[:,2]),
                   color='cyan', linestyles='dashed', alpha=0.5)
    for i in range(0,11,3):
        plotIntervals(ax0,dates,cArray[:,i],cArray[:,i+1],
                     cArray[:,i+2],legend[int((i)/3)],alpha[int((i)/3)])
    ax0.plot(dates, cArray[:,-1], color='white', label='Confirmed Cases')
    ax0.fill_between(dates,cArray[:,-1],cArray[:,6],color='white',alpha=0.2,
                     interpolate=True,where=(cArray[:,-1]>cArray[:,6]))
    ax0.legend(loc="upper left")
    if log:
        ax0.set_yscale('log')
        log_string = ' (log)'
    else:
        log_string = ''
    ax0.yaxis.set_major_formatter(tick.FuncFormatter(formatYticks))
    ax0.set_ylabel(f'Cases{log_string}')

    plt.title(f'Covid Hospitalization and Mortality Rates: {title}',loc="left")

    ax1 = plt.subplot(gs[1],sharex=ax0)
    plotIntervals(ax1,dates,cArray[:,12],cArray[:,13],cArray[:,14],
                  ['white']*4+['Confirmed Cases'])
    if proj:
        ax1.vlines(dates[projIndex],0,max(cArray[:,14]),color='cyan',
                   linestyles='dashed',alpha=0.5)
    ax1.set_ylabel('Death (per 100K)')
    plt.setp(ax0.get_xticklabels(), visible=False)
    plt.subplots_adjust(hspace=0)

    #plt.savefig(f'{location}_Hosp.png')
    plt.show()

################################################################################

def main(fName):
    '''Parses command line arguments to plot data from input file.'''
    logger.debug('Initiating main()')

    locDict = getLocations(fName)

    USAGE ='c19.py [-l <location>] [-t] [-hosp] [-d] [-p] [-log] <command>'
    parser = argparse.ArgumentParser(description= 'Plots Covid daily and total\
            death data for specified jurisdiction.')
    parser.add_argument('-l', '--loc', action = 'store', dest = 'loc',
            choices = locDict.keys(), default = 'global',
               help = 'Choose jurisdiction to plot.')
    parser.add_argument('-t', '--tot', action = 'store_true', dest = 'tot',
                default = False, help = 'Plot total deaths (use with -d).')
    parser.add_argument('-hosp', '--hosp', action = 'store_true',dest = 'hosp',
                default = False, help = 'Choose to plot hospitalization data.')
    parser.add_argument('-d', '--death', action = 'store_true',dest = 'death',
                default = False, help = 'Choose to plot covid death data.')
    parser.add_argument('-p', '--proj', action = 'store_true',dest = 'proj',
                default = False, help = 'Choose to plot projection data.')
    parser.add_argument('-log', '--log', action = 'store_true',dest = 'log',
                default = False, help = 'Choose to plot projection data.')
    args = parser.parse_args()

    if args.hosp:
        dates, data = readCSV(fName, locDict[args.loc])
        plotData_H(dates, data, args.loc, args.proj, args.log)
    if args.death or args.tot:
        dates, data = readCSV(fName, locDict[args.loc], 25+(args.tot*3))
        plotData_D(dates, data, args.loc, args.tot, args.proj, args.log)

################################################################################

if __name__ == '__main__':
    main(fileName)
