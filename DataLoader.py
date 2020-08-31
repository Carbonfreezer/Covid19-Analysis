# -*- coding: utf-8 -*-
"""
Created on Sun Aug 30 12:11:35 2020

@author: chris
"""


import pandas as pd
import requests

class DataLoader:
    def __init__(self):
        pass
    
    @staticmethod
    def getPandasTable(url):
        header = {
          "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
          "X-Requested-With": "XMLHttpRequest"
        }

        r = requests.get(url, headers=header)
        dfs = pd.read_html(r.text)
        return dfs[0]
    
    def LoadBaseData(self):
        self.populationTable = DataLoader.getPandasTable("https://www.worldometers.info/world-population/population-by-country/") 
        self.caseTable = DataLoader.getPandasTable("https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
        self.deathTable = DataLoader.getPandasTable("https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
        
    def SaveTables(self):
        self.populationTable.to_excel("Population.xlsx", index = False)
        self.caseTable.to_excel("Cases.xlsx", index = False)
        self.deathTable.to_excel("Death.xlsx", index = False)
        
    def LoadTables(self):
        self.populationTable = pd.read_excel("Population.xlsx")
        self.caseTable = pd.read_excel("Cases.xlsx")
        self.deathTable = pd.read_excel("Death.xlsx")
        # In population table US is named United States
        self.populationTable["Country (or dependency)"] = self.populationTable["Country (or dependency)"].replace({ "United States" : "US"})


if __name__ == "__main__":
    data = DataLoader()
    data.LoadBaseData()
    data.SaveTables()
    # data.LoadTables()