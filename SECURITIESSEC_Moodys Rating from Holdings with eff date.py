# -*- coding: utf-8 -*-
"""
Created on Mon May 13 16:14:08 2019

@author: StaniszewskaJ"""

import os
import fnmatch
import pandas as pd
import time as time
import numpy as np
from pandas.tseries.offsets import MonthEnd
from datetime import date
from datetime import datetime
from tkinter import *
from tkinter.filedialog import askopenfilename 

fname = "unassigned"

def openFile():
    global fname
    fname = askopenfilename()
    root.destroy()

if __name__ == '__main__':

    root = Tk()
    root.geometry("500x100+700+400")
    Button(root, text='Choose the Holdings View - all Liquids to Import', command = openFile).pack(fill=X)
    mainloop()

dtmp= pd.read_excel(fname, sheet_name=0)  

#outpath
outpath= os.path.dirname(fname)
dtmp.columns.tolist()

#dtmp = dtmp[~dtmp["Moody's Facility Rating"].isnull()]

import time  
dtmp['Today'] = time.strftime("%d/%m/%Y")


# BDay is business day, not birthday...
from pandas.tseries.offsets import BDay
from pandas.tseries.offsets import BusinessMonthEnd

dtmp['PrMonthEnd']= (pd.to_datetime(dtmp['Today'], format="%d/%m/%Y")+ BusinessMonthEnd(-2)).dt.strftime("%d/%m/%Y")

dtmp["Moody's Facility Rating"].replace(['No Rating'], 'NR', inplace=True) 


#secclass Moodys facility rating

secclass_col_names = ['CustomSecurityCode','ISIN','Security Name','CUSIP',
                      'SEDOL','Security Currency Code','Classifier Code',
                      'Classification Code','Date From',
                      'Date End']

secclass_moodys_rating = pd.DataFrame(columns=secclass_col_names)

secclass_moodys_rating['CustomSecurityCode'] = dtmp['Primary Identifier'].values
secclass_moodys_rating['ISIN'] = dtmp['Primary Identifier'].values
secclass_moodys_rating['Classifier Code'] = "SF_Moodys"
secclass_moodys_rating['Classification Code'] = dtmp["Moody's Facility Rating"].values
secclass_moodys_rating['Date From'] = dtmp["Moody's Facility Rating Effective Date"].values

#drop duplicates for the same ratings and the same ISIN
secclass_moodys_rating = secclass_moodys_rating.drop_duplicates(subset=['CustomSecurityCode','Classification Code'],keep='last')
secclass_moodys_rating = secclass_moodys_rating[~secclass_moodys_rating['Classification Code'].isnull()]
#secclass SP facility rating

secclass_SP_rating = pd.DataFrame(columns=secclass_col_names)

secclass_SP_rating['CustomSecurityCode'] = dtmp['Primary Identifier'].values
secclass_SP_rating['ISIN'] = dtmp['Primary Identifier'].values
secclass_SP_rating['Classifier Code'] = "SF_SP_Rating"
secclass_SP_rating['Classification Code'] = dtmp["S&P Facility Rating"].values
secclass_SP_rating['Date From'] = dtmp['S&P Issuer Rating Effective Date'].values

#drop duplicates for the same ratings and the same ISIN
secclass_SP_rating = secclass_SP_rating.drop_duplicates(subset=['CustomSecurityCode','Classification Code'],keep='last')
secclass_SP_rating = secclass_SP_rating[~secclass_SP_rating['Classification Code'].isnull()]


#Saving files

secclass_filename_sf_moodys = "SECCLASS_SF_Moodys_Everest"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_moodys_rating.to_csv(outpath + "\\" + secclass_filename_sf_moodys, sep=',', encoding = 'utf-8', index=False)

secclass_filename_sf_SP = "SECCLASS_SF_SP_Rating_Everest"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_SP_rating.to_csv(outpath + "\\" + secclass_filename_sf_SP, sep=',', encoding = 'utf-8', index=False)

#Exit Message

window = Tk()
window.geometry("500x100+700+400")

def close_window (): 

    window.destroy()

button = Button ( text = ".CSV files are Saved! Please Click to Exit :)", command = close_window)
button.pack()

window.mainloop()
