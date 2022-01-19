
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
#dropping unused columns
#sec.columns.tolist()

      
#special sits
SpecialSitsFilter = ['LX142678','LX142679','LX127528','LX127537','LX900000']
sec=sec[(~sec["Primary Identifier"].isin(SpecialSitsFilter))]
sec = sec[~sec['Par (EUR)'].isnull()]
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

outpath= os.path.dirname(fname)

#Creating SECURITIES dataframe###################################
#
securities_col_names = ['Code', 'ISIN', 'Security long name', 'Currency',
                        'Security type code', 'CUSIP', 'SEDOL', 'BBG_CODE']

securities = pd.DataFrame(columns=securities_col_names)


securities['Code'] = df_clean['Primary Identifier'].values
securities['ISIN'] = df_clean['Primary Identifier'].values
securities['Security long name'] = df_clean['Security Name'].values
securities['Currency'] = df_clean['Ccy'].values
securities['Security type code'] = df_clean['Asset Type'].values
securities['CUSIP'] = df_clean['CUSIP'].values




securities_filename = "SECURITIES_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
securities.to_csv(outpath + "\\" + securities_filename, sep=',', encoding = 'utf-8', index=False)