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
    Button(root, text='Please Click to Choose Holdings File Inka to Import', command = openFile).pack(fill=X)
    mainloop()

sec= pd.read_excel(fname)    
#dropping unused columns

      
#special sits
SpecialSitsFilter = ['LX142678','LX142679','LX127528','LX127537','LX900000']
sec=sec[(~sec["Primary Identifier"].isin(SpecialSitsFilter))]

#excluding swaps
sec = sec[sec["Asset"].str.contains("(?i)swap") == False]

#replacing asset types 
sec['Asset Type'].replace(['Loan'], 'LOANS', inplace=True) 
#sec['Asset Type'].replace(['ABS'], 'ABS', inplace=True)
sec['lenght']=sec['Primary Identifier'].map(str).apply(len)

USFilter = ['United States','Canada']

#Slicing df to df_bond and df_loan
#########################LOANS#################################################
df_loans = sec[sec['Asset Type'] == 'LOANS']
#deleting empty cells
df_loans = df_loans[~df_loans['Primary Identifier'].isnull()]
#leaving cell containing only LX
df_loans = df_loans[df_loans['Primary Identifier'].str.contains('LX')]

#Adding new column
df_loans['Security Name'] = df_loans['Issuer'] + " " + df_loans['Asset']
df_loans.drop(['Asset', 'lenght'], inplace=True, axis=1)
df_loans.drop(['ISIN'], inplace=True, axis=1)

#remove duplicates
df_loans = df_loans.drop_duplicates(subset=['Primary Identifier'],keep='first')
#Slicing df to df_bond and df_loan
#########################ABS#################################################
df_abs = sec[sec['Asset Type'] == 'ABS']
df_abs = df_abs[~df_abs['Primary Identifier'].isnull()]
#Adding new column

df_abs['Security Name'] = df_abs['Issuer'] + " " + df_abs['Asset']
df_abs['Issuer Alias'] = np.where(df_abs['Issuer Alias'].isnull(), df_abs['Issuer'], df_abs['Issuer Alias'])
df_abs['Primary Identifier'] = np.where(df_abs['Primary Identifier'].map(str).apply(len)<12,
      df_abs['ISIN'], df_abs['Primary Identifier'] )
df_abs['Security Name'] = df_abs['Issuer'] + " " + df_abs['Asset']
df_abs['GICS Industry Group'] = "Structured Finance"
df_abs = df_abs.drop_duplicates(subset=['Primary Identifier'],keep='first')

###################################Bond############################################

df_bonds = sec[sec['Asset Type'] == 'Bond']
df_bonds['Primary Identifier'] = np.where(df_bonds['Primary Identifier'].map(str).apply(len)<12, 
        df_bonds['ISIN'],  df_bonds['Primary Identifier'])
df_bonds = df_bonds[~df_bonds['ISIN'].isnull()]
df_bonds['Security Name'] = df_bonds['Asset']
#df_bonds['Primary Identifier'] = df_bonds['ISIN'].values

df_bonds.drop(['Asset', 'ISIN','lenght'], inplace=True, axis=1)
df_bonds = df_bonds.drop_duplicates(subset=['Primary Identifier'],keep='first')

#Merging two dataframes
df_abs_bonds = df_abs.append(df_bonds, sort = False)
df_clean = df_loans.append(df_abs_bonds, sort = False)
#df_clean.set_index(['Primary Identifier'], inplace = True)
df_clean.reset_index(inplace = True)


secclass_col_names = ['Unique Security Identifier','ISIN','Security Name','CUSIP',
                      'SEDOL','Security Currency Code','Classifier Code',
                      'Classification Code','Date From',
                      'Date End']

#Saving  both files

outpath= os.path.dirname(fname)

#creating Everest Country of Issue Holding view file 

secclass_country = pd.DataFrame(columns=secclass_col_names)

secclass_country['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_country['ISIN'] = df_clean['Primary Identifier'].values
secclass_country['Security Name'] =  df_clean['Security Name'].values
secclass_country['Classifier Code'] = "Ev_Country_Tecta(Holding)"
secclass_country['Classification Code'] = df_clean['Country Of Issue'].values
secclass_country.dropna(subset=['Classification Code'], inplace = True)

secclass_filename_country = "SECCLASS_Country_Holding_Tecta_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_country.to_csv(outpath + "\\" + secclass_filename_country, sep=',', encoding = 'utf-8', index=False)

secclass_country_risk = pd.DataFrame(columns=secclass_col_names)

secclass_country_risk['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_country_risk['ISIN'] = df_clean['Primary Identifier'].values
secclass_country_risk['Security Name'] =  df_clean['Security Name'].values
secclass_country_risk['Classifier Code'] = "Ev_Country_of_Risk_Tecta"
secclass_country_risk['Classification Code'] = df_clean['Country Of Risk'].values
secclass_country_risk.dropna(subset=['Classification Code'], inplace = True)

secclass_filename_country_risk = "SECCLASS_Country_Risk_Tecta_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_country_risk.to_csv(outpath + "\\" + secclass_filename_country_risk, sep=',', encoding = 'utf-8', index=False)



#Country for CS comparison

secclass_country_cs = pd.DataFrame(columns=secclass_col_names)

secclass_country_cs['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_country_cs['ISIN'] = df_clean['Primary Identifier'].values
secclass_country_cs['Security Name'] =  df_clean['Security Name'].values
secclass_country_cs['Classifier Code'] = "Country_Ev_Tecta_CS"
secclass_country_cs['Classification Code'] = df_clean['Country Of Issue'].values
secclass_country_cs.dropna(subset=['Classification Code'], inplace = True)

secclass_filename_country_cs = "SECCLASS_Country_CS_Tecta_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_country_cs.to_csv(outpath + "\\" + secclass_filename_country_cs, sep=',', encoding = 'utf-8', index=False)



#Exit Message

window = Tk()
window.geometry("500x100+700+400")

def close_window (): 

    window.destroy()

button = Button ( text = ".CSV files are Saved! Please Click to Exit :)", command = close_window)
button.pack()

window.mainloop()
