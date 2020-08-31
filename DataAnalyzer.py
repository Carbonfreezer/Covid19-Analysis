# -*- coding: utf-8 -*-
"""
Created on Sun Aug 30 13:45:36 2020

@author: chris
"""

import pandas as pd
import DataLoader 
import matplotlib.pyplot as plt
import numpy as np

class DataAnalyzer:
    def __init__(self):
        loader = DataLoader.DataLoader()
        loader.LoadTables()
        self.loader = loader
        
    def generatePopulationList(self, listOfCountries):
        result = []
        pt = self.loader.populationTable
        for country in listOfCountries:
            inhabitants = pt.loc[ pt["Country (or dependency)"] == country].iat[0,2]
            result.append(inhabitants)
            
        return result
    
    def generateListOfCountries(self):
        listA = self.loader.caseTable["Country/Region"].unique()
        listB = self.loader.populationTable["Country (or dependency)"]
        result = [x for x in listB if x in listA]
        result.sort()
        return result
    
    
    def generateCoordinates(self, listOfCountries):
        resultLatitude = []
        resultLongitude = []
        ct = self.loader.caseTable
        for country in listOfCountries:
            subTable = ct.loc[ct["Country/Region"] == country]
            singularRow = subTable.loc[subTable["Province/State"].isnull()]
            if not singularRow.empty:
                subTable = singularRow
                
            resultLatitude.append(subTable["Lat"].median())
            resultLongitude.append(subTable["Long"].median())
        return (resultLatitude, resultLongitude)
    
    
    
    def getStatisticsFromTable(self, table, listOfCountries, listOfInhabitants):
        result = []
        for i in range(len(listOfCountries)):
            country = listOfCountries[i]
            inhabitants = listOfInhabitants[i]
            subTable = table.loc[table["Country/Region"] == country]
            dataField = subTable.iloc[:, 5:]
            # Build sum over all sub regions
            sumValue = dataField.sum()
            # Build differences           
            baseCopy = sumValue.to_numpy()
            numArray = np.empty_like(baseCopy)
            numArray[0] = baseCopy[0]
            for i in range(1, len(numArray)):
                numArray[i] = baseCopy[i] - baseCopy[i - 1]
            # Normalize    
            numArray = numArray / inhabitants
            result.append(numArray)
        return result
    
    
           
        
    def PrepareData(self):
        listOfCountrys = self.generateListOfCountries()   
        listOfInhabitants = self.generatePopulationList(listOfCountrys)
        latitude, longitude = self.generateCoordinates(listOfCountrys)
        infections = self.getStatisticsFromTable(self.loader.caseTable, listOfCountrys, listOfInhabitants)
        deaths = self.getStatisticsFromTable(self.loader.deathTable, listOfCountrys, listOfInhabitants)
        prefiltered = pd.DataFrame( index = listOfCountrys, \
            data = {"Inhabitants" : listOfInhabitants, "Latitude" : latitude, "Longitude": longitude, "Infections" : infections, "Deaths" : deaths})
        
        deathSequence = prefiltered["Deaths"].to_numpy()
        isValid = [element.sum() > 0.0 for element in deathSequence]
        filtered = prefiltered.loc[isValid, :]
        filtered = filtered.loc[filtered["Inhabitants"] > 30000000]
        filtered = filtered.drop("Peru")
        self.finalResult = filtered
            
            
            
    def PlotGeoInformation(self, arrayOfInformation, title):       
        fig, ax = plt.subplots(figsize=(20, 10))
        earth   = plt.imread('WorldMap.png')
        rang = [-170.0, 192.0, -85, 95.0]
        ax.imshow(earth, extent=rang)
        
        xValues = self.finalResult["Longitude"].to_numpy()
        yValues = self.finalResult["Latitude"].to_numpy()
        yValues = np.arctanh(np.sin(np.deg2rad(yValues))) * 133 / np.pi
        
        sizeScale = self.finalResult["Inhabitants"].to_numpy()
        sizeScale = 1500.0 * sizeScale / sizeScale.max()
        
        start = arrayOfInformation.min()
        end = arrayOfInformation.max()
        scatter = ax.scatter(xValues, yValues, s=sizeScale, c=arrayOfInformation, vmin = start, vmax = end,  cmap='viridis', alpha=1.0)
        ax.set_title(title)
        ax.axis('off')
        ax.set_xlim(rang[0],rang[1])
        ax.set_ylim(rang[2],rang[3])
        fig.colorbar(scatter)
        fig.tight_layout()
        fig.savefig("WorldImages/" + title.replace(" ","")+".png")
        plt.show()
        
   
        
    def GetFirstDayAboveThreshold(self, array):
        result = np.zeros(len(array))
        for i in range(len(array)):
            sequence = array[i]
            for day in range(len(sequence)):
                if sequence[day] > 0.0:
                    result[i] = day
                    break
                
        return result
    
    def GetSum(self, array):
        result = np.zeros(len(array))
        for i in range(len(array)):
            result[i] = array[i].sum()
        return result
    
    
    def PlotFirstInfection(self):
        baseArray = self.finalResult["Infections"].to_numpy()
        infectionDelay = self.GetFirstDayAboveThreshold(baseArray)
        self.PlotGeoInformation(infectionDelay, "First Infection After Start")

    def PlotFirstDeath(self):
        baseArray = self.finalResult["Deaths"].to_numpy()
        deaths = self.GetFirstDayAboveThreshold(baseArray)
        self.PlotGeoInformation(deaths, "First Death After Start")
        
    def PlotFirstInfectionToDeath(self):
        baseArray = self.finalResult["Deaths"].to_numpy()
        deaths = self.GetFirstDayAboveThreshold(baseArray)
        baseArray = self.finalResult["Infections"].to_numpy()
        infectionDelay = self.GetFirstDayAboveThreshold(baseArray)
        timeLag = deaths - infectionDelay
        self.PlotGeoInformation(timeLag, "Time First Infection to First Death")


    def PlotInfection(self):
        baseArray = self.finalResult["Infections"].to_numpy()
        sumArray = self.GetSum(baseArray)
        self.PlotGeoInformation(sumArray, "Infections per Inhabitant")
        
    def PlotDeaths(self):
        baseArray = self.finalResult["Deaths"].to_numpy()
        sumArray = self.GetSum(baseArray)
        self.PlotGeoInformation(sumArray, "Deaths per Inhabitant")
        
    def PlotDeathsPerInfection(self):
        baseArray = self.finalResult["Infections"].to_numpy()
        infections = self.GetSum(baseArray)
        baseArray = self.finalResult["Deaths"].to_numpy()
        deaths = self.GetSum(baseArray)
        deathPerInfection = deaths / infections
        self.PlotGeoInformation(deathPerInfection, "Deaths per Infection")        
        
    def PlotGraphs(self, country):
        deathArray = self.finalResult["Deaths"][country]
        infectionArray = self.finalResult["Infections"][country]
        dayArray = np.arange(0,  len(deathArray))
        fig, axs = plt.subplots(2, 1)
        axs[0].plot(dayArray, infectionArray)
        axs[0].set_xlabel('day')
        axs[0].set_ylabel('infections')
        
        axs[1].plot(dayArray, deathArray)
        axs[1].set_xlabel('day')
        axs[1].set_ylabel('deaths')
      

        fig.tight_layout()
        fig.suptitle(country)
        fig.savefig('Figures/'+country + '.png')
        plt.show()
       
        
    def PlotWorldMaps(self):
        self.PlotInfection()
        self.PlotDeaths()
        self.PlotDeathsPerInfection()
        self.PlotFirstInfection()
        self.PlotFirstDeath()
        self.PlotFirstInfectionToDeath()    
        
    def PlotCountryCurves(self):
        for country in self.finalResult.index:
            self.PlotGraphs(country)
        
  
        
if __name__ == "__main__":
    analyzer = DataAnalyzer()
    analyzer.PrepareData()
    analyzer.PlotWorldMaps()
    # analyzer.PlotCountryCurves()
    
   