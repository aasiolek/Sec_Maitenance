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
    Button(root, text='Please Click to Choose Trade Blotter to Import', command = openFile).pack(fill=X)
    mainloop()

sec= pd.read_excel(fname)
#dropping unused columns

sec.drop(["Trade Date", 'Trade ID', 'Issuer ID',  'Asset ID'], inplace=True, axis=1)

#special sits
sec = sec[sec['Primary Identifier'] != 'LX142678']
sec = sec[sec['Primary Identifier'] !='LX142679']
sec = sec[sec['Primary Identifier'] !='LX127528']
sec = sec[sec['Primary Identifier'] !='LX127537']
sec = sec[sec['Primary Identifier'] !='LX900000']

#replace asset type

sec['Asset Type'].replace(['Loan'], 'LOANS', inplace=True) 
sec['Asset Type'].replace(['ABS'], 'ABS', inplace=True)
sec['lenght']=sec['Primary Identifier'].map(str).apply(len)

sec = sec[~sec['Asset'].str.contains("SWAP")]
sec = sec[~sec['Asset'].str.contains("swap")]
sec = sec[~sec['Asset'].str.contains("Swap")]


sec.dtypes
list(sec)
#Slicing df to df_bond and df_loan
#########################LOANS#################################################

df_loans = sec[sec['Asset Type'] == 'LOANS']
#deleting empty cells
df_loans = df_loans[~df_loans['Primary Identifier'].isnull()]
#leaving cell containing only LX
df_loans = df_loans[df_loans['Primary Identifier'].str.contains('LX')]
#Adding new column

df_loans['Security Name'] = df_loans['Issuer'] + " " + df_loans['Asset']
df_loans.drop(['Asset', 'ISIN','lenght'], inplace=True, axis=1)
#remove duplicates
df_loans = df_loans.drop_duplicates(subset=['Primary Identifier'],keep='first')

#########################Bond##################################################



df_abs = sec[sec['Asset Type'] == 'ABS']
df_abs = df_abs[~df_abs['Primary Identifier'].isnull()]
#Adding new column

df_abs['Security Name'] = df_abs['Issuer'] + " " + df_abs['Asset']
df_abs['Issuer Alias'] = np.where(df_abs['Issuer Alias'].isnull(), df_abs['Issuer'], df_abs['Issuer Alias'])
df_abs['Primary Identifier'] = np.where(df_abs['Primary Identifier'].map(str).apply(len)<12,df_abs['ISIN'], df_abs['Primary Identifier'] )
df_abs['Security Name'] = df_abs['Issuer'] + " " + df_abs['Asset']


df_abs = df_abs.drop_duplicates(subset=['Primary Identifier'],keep='first')

   
df_bonds = sec[sec['Asset Type'] == 'Bond']
df_bonds['Primary Identifier'] = np.where(df_bonds['Primary Identifier'].map(str).apply(len)<12, df_bonds['ISIN'],  df_bonds['Primary Identifier'])
df_bonds = df_bonds[~df_bonds['ISIN'].isnull()]
df_bonds['Security Name'] = df_bonds['Asset']
#df_bonds['Primary Identifier'] = df_bonds['ISIN'].values

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
secclass['Classifier Code'] = "Asset class"
secclass['Classification Code'] = df_clean['Asset Type'].values
secclass['Date From'] = "31/12/2011"


secclass.dropna(subset=['Classification Code'], inplace = True)

#Creating SECCLASS dataframe for Street Name

secclass_col_names_street = ['Unique Security Identifier','ISIN','Security Name','CUSIP',
                      'SEDOL','Security Currency Code','Classifier Code',
                      'Classification Code','Date From',
                      'Date End']

secclass_street = pd.DataFrame(columns=secclass_col_names_street)

secclass_street['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_street['ISIN'] = df_clean['Primary Identifier'].values
secclass_street['Security Name'] =  df_clean['Security Name'].values
secclass_street['CUSIP'] = df_clean['CUSIP'].values
secclass_street['Classifier Code'] = "street_name"
secclass_street['Classification Code'] = np.where(df_clean['Issuer Alias'].isnull(), df_clean['Issuer'].values,df_clean['Issuer Alias'].values )


secclass_street.dropna(subset=['Classification Code'], inplace = True)

#Creating SECCLASS dataframe for Issuer

secclass_col_names_issuer = ['Unique Security Identifier','ISIN','Security Name','CUSIP',
                      'SEDOL','Security Currency Code','Classifier Code',
                      'Classification Code','Date From',
                      'Date End']

secclass_issuer = pd.DataFrame(columns=secclass_col_names_issuer)

secclass_issuer['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_issuer['ISIN'] = df_clean['Primary Identifier'].values
secclass_issuer['Security Name'] =  df_clean['Security Name'].values
secclass_issuer['CUSIP'] = df_clean['CUSIP'].values
secclass_issuer['Classifier Code'] = "Everest Issuer"
secclass_issuer['Classification Code'] = df_clean['Issuer'].values


secclass_issuer.dropna(subset=['Classification Code'], inplace = True)

#Creating SECCLASS dataframe for Market Type

secclass_market_type = pd.DataFrame(columns=secclass_col_names)

secclass_market_type['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_market_type['ISIN'] = df_clean['Primary Identifier'].values
secclass_market_type['Security Name'] =  df_clean['Security Name'].values
secclass_market_type['CUSIP'] = df_clean['CUSIP'].values
secclass_market_type['Classifier Code'] = "Everest_Market_Type"
secclass_market_type['Classification Code'] = df_clean['Market Type'].values

secclass_market_type.dropna(subset=['Classification Code'], inplace = True)

#Creating SECCLASS dataframe for Coupon Type

secclass_coupon_type = pd.DataFrame(columns=secclass_col_names)

secclass_coupon_type['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_coupon_type['ISIN'] = df_clean['Primary Identifier'].values
secclass_coupon_type['Security Name'] =  df_clean['Security Name'].values
secclass_coupon_type['CUSIP'] = df_clean['CUSIP'].values
secclass_coupon_type['Classifier Code'] = "Everest_Coupon_Type"
secclass_coupon_type['Classification Code'] = df_clean['Coupon Type'].values

secclass_coupon_type.dropna(subset=['Classification Code'], inplace = True)
#Creating SECCLASS dataframe for Coupon Rate

secclass_coupon_rate = pd.DataFrame(columns=secclass_col_names)

secclass_coupon_rate['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_coupon_rate['ISIN'] = df_clean['Primary Identifier'].values
secclass_coupon_rate['Security Name'] =  df_clean['Security Name'].values
secclass_coupon_rate['CUSIP'] = df_clean['CUSIP'].values
secclass_coupon_rate['Classifier Code'] = "Everest_Coupon_Rate"
secclass_coupon_rate['Classification Code'] = df_clean['Coupon Rate'].values

secclass_coupon_rate.dropna(subset=['Classification Code'], inplace = True)
#Creating SECCLASS dataframe for Maturity Date

secclass_maturity_date = pd.DataFrame(columns=secclass_col_names)

secclass_maturity_date['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_maturity_date['ISIN'] = df_clean['Primary Identifier'].values
secclass_maturity_date['Security Name'] =  df_clean['Security Name'].values
secclass_maturity_date['CUSIP'] = df_clean['CUSIP'].values
secclass_maturity_date['Classifier Code'] = "Everest_Maturity_Date"
secclass_maturity_date['Classification Code'] = df_clean['Maturity Date'].values


secclass_maturity_date.dropna(subset=['Classification Code'], inplace = True)

secclass_payment_freq = pd.DataFrame(columns=secclass_col_names)

secclass_payment_freq['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_payment_freq['ISIN'] = df_clean['Primary Identifier'].values
secclass_payment_freq['Security Name'] =  df_clean['Security Name'].values
secclass_payment_freq['CUSIP'] = df_clean['CUSIP'].values
secclass_payment_freq['Classifier Code'] = "Ev_Payment_Frq"
secclass_payment_freq['Classification Code'] = df_clean['Payment Frequency Name'].values


secclass_payment_freq.dropna(subset=['Classification Code'], inplace = True)

#Creating SECURITIES dataframe

securities_col_names = ['Code', 'ISIN', 'Security long name', 'Currency',
                        'Security type code', 'CUSIP', 'SEDOL', 'BBG_CODE']

securities = pd.DataFrame(columns=securities_col_names)


securities['Code'] = df_clean['Primary Identifier'].values
securities['ISIN'] = df_clean['Primary Identifier'].values
securities['Security long name'] = df_clean['Security Name'].values
securities['Currency'] = df_clean['Ccy'].values
securities['Security type code'] = df_clean['Asset Type'].values
securities['CUSIP'] = df_clean['CUSIP'].values



#Saving  both files

outpath= os.path.dirname(fname)
secclass_filename = "SECCLASS_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
securities_filename = "SECURITIES_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_filename_street = "SECCLASS_STREET"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_filename_issuer = "SECCLASS_ISSUER" +(time.strftime("%Y%m%d_%H%M%S")+".csv")
#secclass_filename_CCY = "SECCLASS_CCY" +(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_filename_market_type = "SECCLASS_Market_Type" +(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_filename_coupon_type = "SECCLASS_Coupon_Type" +(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_filename_coupon_rate = "SECCLASS_Coupon_Rate" +(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_filename_maturity_date = "SECCLASS_Maturity_Date" +(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_filename_pay_frq = "SECCLASS_Payment_frq" +(time.strftime("%Y%m%d_%H%M%S")+".csv")

secclass.to_csv(outpath + "\\" + secclass_filename, sep=',', encoding = 'utf-8', index=False)
securities.to_csv(outpath + "\\" + securities_filename, sep=',', encoding = 'utf-8', index=False)
secclass_street.to_csv(outpath +"\\" + secclass_filename_street, sep=',', encoding = 'utf-8', index=False)
secclass_issuer.to_csv(outpath +"\\" + secclass_filename_issuer, sep=',', encoding = 'utf-8', index=False)
#secclass_CCY.to_csv(outpath +"\\" + secclass_filename_CCY, sep=',', encoding = 'utf-8', index=False)
secclass_market_type.to_csv(outpath +"\\" + secclass_filename_market_type, sep=',', encoding = 'utf-8', index=False)
secclass_coupon_type.to_csv(outpath +"\\" + secclass_filename_coupon_type, sep=',', encoding = 'utf-8', index=False)
secclass_coupon_rate.to_csv(outpath +"\\" + secclass_filename_coupon_rate, sep=',', encoding = 'utf-8', index=False)
secclass_maturity_date.to_csv(outpath +"\\" + secclass_filename_maturity_date, sep=',', encoding = 'utf-8', index=False)
secclass_payment_freq.to_csv(outpath +"\\" + secclass_filename_pay_frq, sep=',', encoding = 'utf-8', index=False)


#Exit Message

window = Tk()
window.geometry("500x100+700+400")

def close_window (): 

    window.destroy()

button = Button ( text = ".CSV files are Saved! Please Click to Exit :)", command = close_window)
button.pack()

window.mainloop()
