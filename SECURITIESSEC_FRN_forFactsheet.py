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
    Button(root, text='Please Click to Choose Trade blotter File to Import', command = openFile).pack(fill=X)
    mainloop()

sec= pd.read_excel(fname)
#dropping unused columns
sec['Asset Type'].replace(['ABS'], 'CLO', inplace=True)
sec.drop(["Trade Date", 'Trade ID', 'Issuer ID',  'Asset ID'], inplace=True, axis=1)

#replacing asset types 

sec['lenght']=sec['Primary Identifier'].map(str).apply(len)


#special sits
sec = sec[sec['Primary Identifier'] != 'LX142678']
sec = sec[sec['Primary Identifier'] !='LX142679']
sec = sec[sec['Primary Identifier'] !='LX127528']
sec = sec[sec['Primary Identifier'] !='LX127537']
sec = sec[sec['Primary Identifier'] !='LX900000']

sec = sec[sec["Asset"].str.contains("SWAP") == False]
sec = sec[sec["Asset"].str.contains("Swap") == False]
sec = sec[sec["Asset"].str.contains("swap") == False]


#Slicing df to df_bond and df_loan
#########################LOANS#################################################

df_loans = sec[sec['Asset Type'] == 'Loan']
#deleting empty cells
df_loans = df_loans[~df_loans['Primary Identifier'].isnull()]
#leaving cell containing only LX
df_loans = df_loans[df_loans['Primary Identifier'].str.contains('LX')]
#Adding new column

df_loans['Security Name'] = df_loans['Issuer'] + " " + df_loans['Asset']
df_loans.drop(['Asset', 'ISIN','lenght'], inplace=True, axis=1)
#remove duplicates
df_loans = df_loans.drop_duplicates(subset=['Primary Identifier'],keep='first')


df_abs = sec[sec['Asset Type'] == 'CLO']
df_abs = df_abs[~df_abs['Primary Identifier'].isnull()]
#Adding new column

df_abs['Security Name'] = df_abs['Issuer'] + " " + df_abs['Asset']
df_abs['Issuer Alias'] = np.where(df_abs['Issuer Alias'].isnull(), df_abs['Issuer'] + " "+ df_abs['Asset'], df_abs['Issuer Alias'])
df_abs['Primary Identifier'] = np.where(df_abs['Primary Identifier'].map(str).apply(len)<12,df_abs['ISIN'], df_abs['Primary Identifier'] )
df_abs['Security Name'] = df_abs['Issuer'] + " " + df_abs['Asset']


df_abs = df_abs.drop_duplicates(subset=['Primary Identifier'],keep='first')



df_bonds = sec[sec['Asset Type'] == 'Bond']
df_bonds['Asset Type'] = np.where(df_bonds['Coupon Type'] =='Float','Floating Rate Note', 'Bond')   
df_bonds['Primary Identifier'] = np.where(df_bonds['Primary Identifier'].map(str).apply(len)<12, df_bonds['ISIN'],  df_bonds['Primary Identifier'])
df_bonds = df_bonds[~df_bonds['ISIN'].isnull()]
df_bonds['Security Name'] = df_bonds['Asset']

df_bonds.drop(['Asset', 'ISIN','lenght'], inplace=True, axis=1)
df_bonds = df_bonds.drop_duplicates(subset=['Primary Identifier'],keep='first')


###############################################################################

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

#Creating SECCLASS dataframe

secclass_col_names = ['Unique Security Identifier','ISIN','Security Name','CUSIP',
                      'SEDOL','Security Currency Code','Classifier Code',
                      'Classification Code','Date From',
                      'Date End']

secclass = pd.DataFrame(columns=secclass_col_names)

secclass['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass['ISIN'] = df_clean['Primary Identifier'].values
secclass['Security Name'] =  df_clean['Security Name'].values
secclass['CUSIP'] = df_clean['CUSIP'].values
secclass['SEDOL'] = ""
secclass['Classifier Code'] = "Asset_Class_(Factsheet)"
secclass['Classification Code'] = df_clean['Asset Type'].values
secclass['Date From'] = ""
secclass['Date End'] = ""


#Saving  both files

outpath= os.path.dirname(fname)
secclass_filename = "SECCLASS_Asset_Factsheet"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass.to_csv(outpath + "\\" + secclass_filename, sep=',', encoding = 'utf-8', index=False)

#HOLDING DATA
#importing file by asking a user

fname = "unassigned"

def openFile():
    global fname
    fname = askopenfilename()
    root.destroy()

if __name__ == '__main__':

    root = Tk()
    root.geometry("500x100+700+400")  #added
    Button(root, text='Please Click to Choose Holding all Liquid File to Import', command = openFile).pack(fill=X)
    mainloop()

sec= pd.read_excel(fname)
#dropping unused columns
sec['Asset Type'].replace(['ABS'], 'CLO', inplace=True)


#replacing asset types 

sec['lenght']=sec['Primary Identifier'].map(str).apply(len)

#special sits
sec = sec[sec['Primary Identifier'] != 'LX142678']
sec = sec[sec['Primary Identifier'] !='LX142679']
sec = sec[sec['Primary Identifier'] !='LX127528']
sec = sec[sec['Primary Identifier'] !='LX127537']
sec = sec[sec['Primary Identifier'] !='LX900000']

sec = sec[sec["Asset"].str.contains("SWAP") == False]
sec = sec[sec["Asset"].str.contains("Swap") == False]
sec = sec[sec["Asset"].str.contains("swap") == False]


#Slicing df to df_bond and df_loan
#########################LOANS#################################################

df_loans = sec[sec['Asset Type'] == 'Loan']
#deleting empty cells
df_loans = df_loans[~df_loans['Primary Identifier'].isnull()]
#leaving cell containing only LX
df_loans = df_loans[df_loans['Primary Identifier'].str.contains('LX')]
#Adding new column

df_loans['Security Name'] = df_loans['Issuer'] + " " + df_loans['Asset']
df_loans.drop(['Asset', 'ISIN','lenght'], inplace=True, axis=1)
#remove duplicates
df_loans = df_loans.drop_duplicates(subset=['Primary Identifier'],keep='first')


df_abs = sec[sec['Asset Type'] == 'CLO']
df_abs = df_abs[~df_abs['Primary Identifier'].isnull()]
#Adding new column

df_abs['Security Name'] = df_abs['Issuer'] + " " + df_abs['Asset']
df_abs['Issuer Alias'] = np.where(df_abs['Issuer Alias'].isnull(), df_abs['Issuer'] + " "+ df_abs['Asset'], df_abs['Issuer Alias'])
df_abs['Primary Identifier'] = np.where(df_abs['Primary Identifier'].map(str).apply(len)<12,df_abs['ISIN'], df_abs['Primary Identifier'] )
df_abs['Security Name'] = df_abs['Issuer'] + " " + df_abs['Asset']


df_abs = df_abs.drop_duplicates(subset=['Primary Identifier'],keep='first')

###############################################################################

#Equity df
df_equity = sec[sec['Asset Type'] == 'Equity']
df_equity = df_equity[~df_equity['Primary Identifier'].isnull()]
df_equity['Security Name'] = df_equity['Issuer']
df_equity = df_equity.drop_duplicates(subset=['Primary Identifier'],keep='first')


#Merging two dataframes
df_abs_eq = df_abs.append(df_equity, sort = False)
df_clean = df_loans.append(df_abs_eq, sort = False)

#df_clean.set_index(['Primary Identifier'], inplace = True)
df_clean.reset_index(inplace = True)

#Creating SECCLASS dataframe

secclass_col_names = ['Unique Security Identifier','ISIN','Security Name','CUSIP',
                      'SEDOL','Security Currency Code','Classifier Code',
                      'Classification Code','Date From',
                      'Date End']

secclass = pd.DataFrame(columns=secclass_col_names)

secclass['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass['ISIN'] = df_clean['Primary Identifier'].values
secclass['Security Name'] =  df_clean['Security Name'].values
secclass['CUSIP'] = df_clean['CUSIP'].values
secclass['SEDOL'] = ""
secclass['Classifier Code'] = "Asset_Class_(Factsheet)"
secclass['Classification Code'] = df_clean['Asset Type'].values
secclass['Date From'] = ""
secclass['Date End'] = ""


#Saving  both files

outpath= os.path.dirname(fname)
secclass_filename = "SECCLASS_Asset_Factsheet"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass.to_csv(outpath + "\\" + secclass_filename, sep=',', encoding = 'utf-8', index=False)




#Exit Message

window = Tk()
window.geometry("500x100+700+400")

def close_window (): 

    window.destroy()

button = Button ( text = ".CSV files are Saved! Please Click to Exit :)", command = close_window)
button.pack()

window.mainloop()
