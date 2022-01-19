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
    Button(root, text='Choose the Holdings View all liquid to Import', command = openFile).pack(fill=X)
    mainloop()

sec= pd.read_excel(fname)    

#excluding swaps
sec = sec[sec["Asset"].str.contains("(?i)swap") == False]

#replacing asset types 
sec['Asset Type'].replace(['Loan'], 'LOANS', inplace=True) 
sec['lenght']=sec['Primary Identifier'].map(str).apply(len)

#Slicing df to df_bond and df_loan
#########################LOANS#################################################
df_loans = sec[sec['Asset Type'] == 'LOANS']
#deleting empty cells
df_loans = df_loans[~df_loans['Primary Identifier'].isnull()]
#leaving cell containing only LX
df_loans = df_loans[df_loans['Primary Identifier'].str.contains('LX')]


#Slicing df to df_bond and df_loan
#########################ABS#################################################
df_abs = sec[sec['Asset Type'] == 'ABS']
df_abs['Primary Identifier'] = np.where(df_abs['Primary Identifier'].map(str).apply(len)<12,
      df_abs['ISIN'], df_abs['Primary Identifier'] )


###################################Bond############################################

df_bonds = sec[sec['Asset Type'] == 'Bond']
df_bonds['Primary Identifier'] = np.where(df_bonds['Primary Identifier'].map(str).apply(len)<12, 
        df_bonds['ISIN'],  df_bonds['Primary Identifier'])

#Equity df
df_equity = sec[sec['Asset Type'] == 'Equity']
df_equity = df_equity[~df_equity['Primary Identifier'].isnull()]
df_equity['Security Name'] = df_equity['Issuer']
df_equity = df_equity.drop_duplicates(subset=['Primary Identifier'],keep='first')


#Merging two dataframes
df_abs_bonds = df_abs.append(df_bonds, sort = False)
df_abs_bonds_eq = df_abs_bonds.append(df_equity, sort = False)
df_clean = df_loans.append(df_abs_bonds_eq, sort = False)

#df_clean.set_index(['Primary Identifier'], inplace = True)
df_clean.reset_index(inplace = True)




#outpath
outpath= os.path.dirname(fname)

import time  
df_clean['Today'] = time.strftime("%d/%m/%Y")


# BDay is business day, not birthday...
from pandas.tseries.offsets import BDay
from pandas.tseries.offsets import BusinessMonthEnd

#****************DO ZMIANY**********************

from pandas.tseries.offsets import BMonthBegin
df_clean['Beg_Date'] =(pd.to_datetime(df_clean['Today'], format="%d/%m/%Y")+BMonthBegin(-2)).dt.strftime("%d/%m/%Y")

df_clean["Moody's Facility Rating"].replace(['No Rating'], 'NR', inplace=True) 
df_clean['S&P Facility Rating'].replace(['No Rating'], 'NR', inplace=True) 

#creating a multiindex
df_clean['multi_rating'] = df_clean["Moody's Facility Rating"] + df_clean['S&P Facility Rating']
#secclass Moodys facility rating

secclass_col_names = ['CustomSecurityCode','ISIN','Security Name','CUSIP',
                      'SEDOL','Security Currency Code','Classifier Code',
                      'Classification Code','Date From',
                      'Date End']

secclass_moodys_rating = pd.DataFrame(columns=secclass_col_names)


secclass_moodys_rating['CustomSecurityCode'] = df_clean['Primary Identifier'].values
secclass_moodys_rating['ISIN'] = df_clean['Primary Identifier'].values
secclass_moodys_rating['Classifier Code'] = "SF_Moodys"
secclass_moodys_rating['Classification Code'] = df_clean["Moody's Facility Rating"].values
secclass_moodys_rating['Date From'] = df_clean['Beg_Date'].values

#drop duplicates for the same ratings and the same ISIN
secclass_moodys_rating = secclass_moodys_rating.drop_duplicates(subset=['CustomSecurityCode','Classification Code'],keep='last')
secclass_moodys_rating = secclass_moodys_rating[~secclass_moodys_rating['Classification Code'].isnull()]


#secclass SP facility rating

secclass_SP_rating = pd.DataFrame(columns=secclass_col_names)


secclass_SP_rating['CustomSecurityCode'] = df_clean['Primary Identifier'].values
secclass_SP_rating['ISIN'] = df_clean['Primary Identifier'].values
secclass_SP_rating['Classifier Code'] = "SF_SP_Rating"
secclass_SP_rating['Classification Code'] = df_clean["S&P Facility Rating"].values
secclass_SP_rating['Date From'] = df_clean['Beg_Date'].values

#drop duplicates for the same ratings and the same ISIN
secclass_SP_rating = secclass_SP_rating.drop_duplicates(subset=['CustomSecurityCode','Classification Code'],keep='last')
secclass_SP_rating = secclass_SP_rating[~secclass_SP_rating['Classification Code'].isnull()]

#Saving files
secclass_filename_sf_moodys = "SECCLASS_SF_Moodys_Everest"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_moodys_rating.to_csv(outpath + "\\" + secclass_filename_sf_moodys, sep=',', encoding = 'utf-8', index=False)

secclass_filename_sf_SP = "SECCLASS_SF_SP_Rating_Everest"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_SP_rating.to_csv(outpath + "\\" + secclass_filename_sf_SP, sep=',', encoding = 'utf-8', index=False)


#warf classfier
warf_mapping = pd.read_excel(r"C:\Users\StaniszewskaJ\Downloads\moodys_rating_factor_mapping.xlsx")

#merging df_clean with warf moodys mapping
df_clean=df_clean.merge(warf_mapping, how= 'left', left_on=["Moody's Facility Rating"], right_on=["Moody's Rating"])
df_clean.reset_index(inplace = True)
#
#secclass WARF

secclass_warf = pd.DataFrame(columns=secclass_col_names)

secclass_warf['CustomSecurityCode'] = df_clean['Primary Identifier'].values
secclass_warf['ISIN'] = df_clean['Primary Identifier'].values
secclass_warf['Classifier Code'] = "WARF Rating"
secclass_warf['Classification Code'] = df_clean["Moody's Rating Factor"].values
secclass_warf['Date From'] = df_clean['Beg_Date'].values

#drop duplicates for the same ratings and the same ISIN
secclass_warf = secclass_warf.drop_duplicates(subset=['CustomSecurityCode','Classification Code'],keep='last')
secclass_warf = secclass_warf[~secclass_warf['Classification Code'].isnull()]

#Saving files

secclass_filename_sf_warf = "SECCLASS_WARF"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_warf.to_csv(outpath + "\\" + secclass_filename_sf_warf, sep=',', encoding = 'utf-8', index=False)

#creating Everest Moody's rating type classifier 

secclass_ev_mood_type = pd.DataFrame(columns=secclass_col_names)

secclass_ev_mood_type['CustomSecurityCode'] = df_clean['Primary Identifier'].values
secclass_ev_mood_type['ISIN'] = df_clean['Primary Identifier'].values
secclass_ev_mood_type['Classifier Code'] = "Moodys_Rating_Type"
secclass_ev_mood_type['Classification Code'] = df_clean["Moody's Rating Type "].values
secclass_ev_mood_type['Date From'] = df_clean['Beg_Date'].values

#drop duplicates for the same ratings and the same ISIN
secclass_ev_mood_type = secclass_ev_mood_type.drop_duplicates(subset=['CustomSecurityCode','Classification Code'],keep='last')
secclass_ev_mood_type = secclass_ev_mood_type[~secclass_ev_mood_type['Classification Code'].isnull()]


secclass_ev_mood_type_filename = "SECCLASS_Moodys_Rating_Type_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_ev_mood_type.to_csv(outpath + "\\" + secclass_ev_mood_type_filename, sep=',', encoding = 'utf-8', index=False)

#creating Everest SP rating type classifier 

secclass_ev_sp_type = pd.DataFrame(columns=secclass_col_names)

secclass_ev_sp_type['CustomSecurityCode'] = df_clean['Primary Identifier'].values
secclass_ev_sp_type['ISIN'] = df_clean['Primary Identifier'].values
secclass_ev_sp_type['Classifier Code'] = "SP_Rating_Type"
secclass_ev_sp_type['Classification Code'] = df_clean['S&P Rating Type'].values
secclass_ev_sp_type['Date From'] = df_clean['Beg_Date'].values

#drop duplicates for the same ratings and the same ISIN
secclass_ev_sp_type = secclass_ev_sp_type.drop_duplicates(subset=['CustomSecurityCode','Classification Code'],keep='last')
secclass_ev_sp_type = secclass_ev_sp_type[~secclass_ev_sp_type['Classification Code'].isnull()]



secclass_ev_sp_type_filename = "SECCLASS_SP_Rating_Type_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_ev_sp_type.to_csv(outpath + "\\" + secclass_ev_sp_type_filename, sep=',', encoding = 'utf-8', index=False)

#CS_Rating classfier
cs_rating_mapping = pd.read_excel(r"C:\Users\StaniszewskaJ\Downloads\CS_Rating_mapping.xlsx")

#merging df_clean with warf moodys mapping
df_clean=df_clean.merge(cs_rating_mapping, how= 'left', left_on=["multi_rating"], right_on=["multiindex"])
#df_clean.reset_index(inplace = True)
#
#secclass cs_rating

secclass_cs_rating = pd.DataFrame(columns=secclass_col_names)

secclass_cs_rating['CustomSecurityCode'] = df_clean['Primary Identifier'].values
secclass_cs_rating['ISIN'] = df_clean['Primary Identifier'].values
secclass_cs_rating['Classifier Code'] = "CS_Rating DATE_STAMPED"
secclass_cs_rating['Classification Code'] = df_clean["CreditSuisse"].values
secclass_cs_rating['Date From'] = df_clean['Beg_Date'].values

#drop duplicates for the same ratings and the same ISIN
secclass_cs_rating = secclass_cs_rating.drop_duplicates(subset=['CustomSecurityCode','Classification Code'],keep='last')
secclass_cs_rating = secclass_cs_rating[~secclass_cs_rating['Classification Code'].isnull()]

#Saving files

secclass_filename_sf_cs_rating = "SECCLASS_CS_rating"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_cs_rating.to_csv(outpath + "\\" + secclass_filename_sf_cs_rating, sep=',', encoding = 'utf-8', index=False)


#Exit Message

window = Tk()
window.geometry("500x100+700+400")

def close_window (): 

    window.destroy()

button = Button ( text = ".CSV files are Saved! Please Click to Exit :)", command = close_window)
button.pack()

window.mainloop()

