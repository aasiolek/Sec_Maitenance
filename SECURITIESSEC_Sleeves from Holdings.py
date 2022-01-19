# -*- coding: utf-8 -*-
"""
Created on Mon May 13 16:14:08 2019

@author: StaniszewskaJ"""

import pandas as pd
import numpy as np
import time as time
import sys
from tkinter import *
from tkinter.filedialog import askopenfilename   
import os

#importing file by asking a user

fname = "unassigned"

def openFile():
    global fname
    fname = askopenfilename()
    root.destroy()

if __name__ == '__main__':

    root = Tk()
    root.geometry("500x100+700+400")  #added
    Button(root, text='Please Click to Choose Holdings - All Liquid File to Import', command = openFile).pack(fill=X)
    mainloop()

sec= pd.read_excel(fname)    
outpath= os.path.dirname(fname)
      
#special sits
SpecialSitsFilter = ['LX142678','LX142679','LX127528','LX127537','LX900000']
sec=sec[(~sec["Primary Identifier"].isin(SpecialSitsFilter))]

#excluding swaps
sec = sec[sec["Asset"].str.contains("(?i)swap") == False]

#replacing asset types 
sec['Asset Type'].replace(['Loan'], 'LOANS', inplace=True) 
#sec['Asset Type'].replace(['ABS'], 'ABS', inplace=True)
sec['lenght']=sec['Primary Identifier'].map(str).apply(len)


def func_GTC(row):
    if row['Portfolio Name']== 'GTC New York':
        return 'GTC NY'
    elif row['Portfolio Name'] =='ICG GTC London':
        return 'GTC LON'
    else:
        return 'SYSOTHERS'
    
def func_GLF(row):
    if row['Portfolio Name'] == 'GLF New York':
        return 'GLF NY'
    elif row['Portfolio Name'] =='ICG GLF London':
        return 'GLF LON'
    else:
        return 'SYSOTHERS'

sec['sleeve_gtc'] = sec.apply(func_GTC, axis = 1)
sec['sleeve_glf'] = sec.apply(func_GLF, axis = 1)
#if you are running this on the month after last BD from previous month
import time  
sec['Today'] = time.strftime("%d/%m/%Y")

# BDay is business day, not birthday...
from pandas.tseries.offsets import BDay
from pandas.tseries.offsets import BusinessMonthEnd

sec['PrMonthEnd']= (pd.to_datetime(sec['Today'], format="%d/%m/%Y")+ BusinessMonthEnd(-2)).dt.strftime("%d/%m/%Y")



#Creating SECCLASS dataframe

secclass_col_names = ['Unique Security Identifier','ISIN','Security Name','CUSIP',
                      'SEDOL','Security Currency Code','Classifier Code',
                      'Classification Code','Date From',
                      'Date End']

#creating sleeves classifiers 

secclass_sleeve_gtc = pd.DataFrame(columns=secclass_col_names)

secclass_sleeve_gtc['Unique Security Identifier'] = sec['Primary Identifier'].values
secclass_sleeve_gtc['ISIN'] = np.where(sec['Primary Identifier'].map(str).apply(len)<12, 
        sec['ISIN'],  sec['Primary Identifier'])
secclass_sleeve_gtc['Classifier Code'] = "GTC_SLEEVE"
secclass_sleeve_gtc['Classification Code'] = sec['sleeve_gtc'].values
secclass_sleeve_gtc.dropna(subset=['Classification Code'], inplace = True)
secclass_sleeve_gtc['Date From'] = sec['PrMonthEnd'].values
secclass_sleeve_gtc = secclass_sleeve_gtc[~secclass_sleeve_gtc['Classification Code'].str.contains('SYSOTHERS')]


secclass_sleeve_gtc_filename = "SECCLASS_sleeve_gtc_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_sleeve_gtc.to_csv(outpath + "\\" + secclass_sleeve_gtc_filename, sep=',', encoding = 'utf-8', index=False)

secclass_sleeve_glf = pd.DataFrame(columns=secclass_col_names)

secclass_sleeve_glf['Unique Security Identifier'] = sec['Primary Identifier'].values
secclass_sleeve_glf['ISIN'] = np.where(sec['Primary Identifier'].map(str).apply(len)<12, 
        sec['ISIN'],  sec['Primary Identifier'])
secclass_sleeve_glf['Classifier Code'] = "GLF_SLEEVE"
secclass_sleeve_glf['Classification Code'] = sec['sleeve_glf'].values
secclass_sleeve_glf.dropna(subset=['Classification Code'], inplace = True)
secclass_sleeve_glf['Date From'] = sec['PrMonthEnd'].values
secclass_sleeve_glf = secclass_sleeve_glf[~secclass_sleeve_glf['Classification Code'].str.contains('SYSOTHERS')]

secclass_sleeve_glf_filename = "SECCLASS_sleeve_glf_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_sleeve_glf.to_csv(outpath + "\\" + secclass_sleeve_glf_filename, sep=',', encoding = 'utf-8', index=False)

#Exit Message

window = Tk()
window.geometry("500x100+700+400")

def close_window (): 

    window.destroy()

button = Button ( text = ".CSV files are Saved! Please Click to Exit :)", command = close_window)
button.pack()

window.mainloop()
