# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 08:00:51 2020

@author: chris
"""

import DataAnalyzer
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class TimeAnalyzer:
    def __init__(self):
        self.dataAnalyzer = DataAnalyzer.DataAnalyzer()
        self.dataAnalyzer.PrepareData()
        
        
    def LowPassFilterSeris(self, array, window):
        mT = len(array)
        result = np.zeros(len(array))
        for i in range(mT):
            count = 0
            vals = 0
            for j in range(-window, window + 1):
                k = i + j
                if (k < 0) or (k >= mT):
                    continue
                count += 1
                vals += array[k]
            result[i] = vals / count
        return result
    
    def GetLocalMaximum(self, array, window):
        threshold = 0.3 * array.max()
        for scan in range(window, len(array) - window):
            testValue = array[scan]
            if testValue < threshold:
                continue
            testFailed = False
            for compare in range(-window, window + 1):
                if compare == 0:
                    continue
                if array[scan + compare] > testValue:
                    testFailed = True
            if not testFailed:
                return  scan
        return  -1
                
    def GenerateMaximumInformation(self, window):
        resultTable = self.dataAnalyzer.finalResult
        rawInfections = resultTable["Infections"].to_numpy()
        infectionMaximum = [self.GetLocalMaximum(series, window) for series in rawInfections] 
        rawDeaths = resultTable["Deaths"].to_numpy()
        deathMaximum = [self.GetLocalMaximum(series, window) for series in rawDeaths]
        resultTable["InfectMax"] = infectionMaximum
        resultTable["DeathMax"] = deathMaximum
        
        
    def LowPassFilterAllData(self, window):
        rawInfections = self.dataAnalyzer.finalResult["Infections"].to_numpy()
        transformedInfections = [self.LowPassFilterSeris(series, window) for series in rawInfections]
        self.dataAnalyzer.finalResult["Infections"] = transformedInfections
        rawDeaths = self.dataAnalyzer.finalResult["Deaths"].to_numpy()
        transformedDeaths = [self.LowPassFilterSeris(series, window) for series in rawDeaths]
        self.dataAnalyzer.finalResult["Deaths"] = transformedDeaths
        
    def PlotGraphs(self, country):
        resultTable = self.dataAnalyzer.finalResult
        deathArray = resultTable["Deaths"][country]
        infectionArray = resultTable["Infections"][country]
        deathMax =  resultTable["DeathMax"][country] 
        infectMax = resultTable["InfectMax"][country]
        
        dayArray = np.arange(0,  len(deathArray))
        fig, axs = plt.subplots(2, 1)
        axs[0].plot(dayArray, infectionArray)
        if infectMax != -1:
            axs[0].scatter([infectMax],[infectionArray[infectMax]] , c='Red')
        axs[0].set_xlabel('day')
        axs[0].set_ylabel('infections')
        
        axs[1].plot(dayArray, deathArray)
        if deathMax != -1:
            axs[1].scatter([deathMax],[deathArray[deathMax]] , c='Red')
        axs[1].set_xlabel('day')
        axs[1].set_ylabel('deaths')
      

        fig.tight_layout()
        fig.suptitle(country)
        fig.savefig('Figures/'+country + '.png')
        plt.show()
        
    def PlotCountryCurves(self):
        for country in self.dataAnalyzer.finalResult.index:
            self.PlotGraphs(country) 
            
            
    def PlotCountryWaveCompleted(self):
        resultTable = self.dataAnalyzer.finalResult
        deathMax = resultTable["DeathMax"].to_numpy()
        infectMax = resultTable["InfectMax"].to_numpy()
        minimum = np.minimum(deathMax, infectMax)
        valueArray = [1.0 if test > 0 else 0.0 for test in minimum]
        valueArray = np.asarray(valueArray)
        self.dataAnalyzer.PlotGeoInformation(valueArray, "Maxima Detected")
        
    def FilterForFirstWave(self):
        resultTable = self.dataAnalyzer.finalResult
        deathMax = resultTable["DeathMax"].to_numpy()
        infectMax = resultTable["InfectMax"].to_numpy()
        minimum = np.minimum(deathMax, infectMax)
        filterT = [test > 0  for test in minimum]
        self.dataAnalyzer.finalResult = resultTable.loc[filterT]
        
    def PlotDeathAfterInfection(self):
        resultTable = self.dataAnalyzer.finalResult
        difference = resultTable["DeathMax"].to_numpy() - resultTable["InfectMax"].to_numpy()
        self.dataAnalyzer.PlotGeoInformation(difference, "Maxima Death after Infect")
        difference = [1.0 if test > 0.0 else 0.0 for test in difference]
        difference = np.asarray(difference)
        self.dataAnalyzer.PlotGeoInformation(difference, "Maxima Death after Infect Occured")
        
        
    def PlotDaysTillInfectionMax(self):
        resultTable = self.dataAnalyzer.finalResult
        infectMax = resultTable["InfectMax"].to_numpy()
        infections = resultTable["Infections"].to_numpy()
        infectStarted = self.dataAnalyzer.GetFirstDayAboveThreshold(infections)
        delta = infectMax - infectStarted
        self.dataAnalyzer.PlotGeoInformation(delta, "Time till maximum infaction")
     
    def PlotDaysTillDeathsMax(self):
        resultTable = self.dataAnalyzer.finalResult
        deathMax = resultTable["DeathMax"].to_numpy()
        deaths = resultTable["Deaths"].to_numpy()
        dyingStarted = self.dataAnalyzer.GetFirstDayAboveThreshold(deaths)
        delta = deathMax - dyingStarted
        self.dataAnalyzer.PlotGeoInformation(delta, "Time till maximum deaths")
        
        
    def PlotDeathsAtFirstMaximum(self):
        resultTable = self.dataAnalyzer.finalResult
        deathMax = resultTable["DeathMax"].to_numpy()
        deaths = resultTable["Deaths"].to_numpy()
        maxValues = np.zeros(len(deaths))
        for i in range(len(deaths)):
            maxValues[i] = deaths[i][deathMax[i]]
        self.dataAnalyzer.PlotGeoInformation(maxValues, "Deaths at first maximum")
        
    def PlotDeathsSlope(self):
        resultTable = self.dataAnalyzer.finalResult
        deathMax = resultTable["DeathMax"].to_numpy()
        deaths = resultTable["Deaths"].to_numpy()
        maxValues = np.zeros(len(deaths))
        for i in range(len(deaths)):
            maxValues[i] = deaths[i][deathMax[i]]
        maxValues /= deathMax    
        self.dataAnalyzer.PlotGeoInformation(maxValues, "Death slope till first maximum")
    
        
    def GenerateGeoImages(self):
        self.PlotCountryWaveCompleted()
        self.FilterForFirstWave()
        self.PlotDeathAfterInfection()
        self.PlotDaysTillInfectionMax()
        self.PlotDaysTillDeathsMax()
        self.PlotDeathsAtFirstMaximum()
        self.PlotDeathsSlope()
        
if __name__ == "__main__":
    time = TimeAnalyzer()
    time.LowPassFilterAllData(7)
    # time.dataAnalyzer.PlotCountryCurves()
    time.GenerateMaximumInformation(20)
    # time.PlotCountryCurves()
    time.GenerateGeoImages()
    