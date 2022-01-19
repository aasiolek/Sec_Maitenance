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
#securities_col_names = ['Code', 'ISIN', 'Security long name', 'Currency',
#                        'Security type code', 'CUSIP', 'SEDOL', 'BBG_CODE']
#
#securities = pd.DataFrame(columns=securities_col_names)
#
#
#securities['Code'] = df_clean['Primary Identifier'].values
#securities['ISIN'] = df_clean['Primary Identifier'].values
#securities['Security long name'] = df_clean['Security Name'].values
#securities['Currency'] = df_clean['Ccy'].values
#securities['Security type code'] = df_clean['Asset Type'].values
#securities['CUSIP'] = df_clean['CUSIP'].values
#
#
#securities_filename = "SECURITIES_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
#securities.to_csv(outpath + "\\" + securities_filename, sep=',', encoding = 'utf-8', index=False)

#Creating SECCLASS dataframe

secclass_col_names = ['Unique Security Identifier','ISIN','Security Name','CUSIP',
                      'SEDOL','Security Currency Code','Classifier Code',
                      'Classification Code','Date From',
                      'Date End']

secclass = pd.DataFrame(columns=secclass_col_names)

secclass['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass['ISIN'] = df_clean['Primary Identifier'].values
secclass['Security Name'] =  df_clean['Security Name'].values
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



secclass_issuer = pd.DataFrame(columns=secclass_col_names)

secclass_issuer['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_issuer['ISIN'] = df_clean['Primary Identifier'].values
secclass_issuer['Security Name'] =  df_clean['Security Name'].values
secclass_issuer['Classifier Code'] = "Everest Issuer"
secclass_issuer['Classification Code'] = df_clean['Issuer'].values

secclass_issuer.dropna(subset=['Classification Code'], inplace = True)

#Saving  both files



secclass_filename = "SECCLASS_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_filename_issuer = "SECCLASS_ISSUER" +(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_filename_street = "SECCLASS_STREET"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass.to_csv(outpath + "\\" + secclass_filename, sep=',', encoding = 'utf-8', index=False)
secclass_issuer.to_csv(outpath +"\\" + secclass_filename_issuer, sep=',', encoding = 'utf-8', index=False)
secclass_street.to_csv(outpath +"\\" + secclass_filename_street, sep=',', encoding = 'utf-8', index=False)


#creating gics group secclass file 

secclass_gics_group = pd.DataFrame(columns=secclass_col_names)

secclass_gics_group['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_gics_group['ISIN'] = df_clean['Primary Identifier'].values
secclass_gics_group['Security Name'] =  df_clean['Security Name'].values
secclass_gics_group['Classifier Code'] = "GICS Group"
secclass_gics_group['Classification Code'] = df_clean['GICS Industry Group'].str[0:4]
secclass_gics_group.dropna(subset=['Classification Code'], inplace = True)

secclass_filename_gics_group = "SECCLASS_GICS_Group_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_gics_group.to_csv(outpath + "\\" + secclass_filename_gics_group, sep=',', encoding = 'utf-8', index=False)

#creating GICS Industry  secclass file 

secclass_gics_industry = pd.DataFrame(columns=secclass_col_names)

secclass_gics_industry['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_gics_industry['ISIN'] = df_clean['Primary Identifier'].values
secclass_gics_industry['Security Name'] =  df_clean['Security Name'].values
secclass_gics_industry['Classifier Code'] = "GICS Industry"
secclass_gics_industry['Classification Code'] = df_clean['GICS Industry'].str[0:6]
secclass_gics_industry.dropna(subset=['Classification Code'], inplace = True)

secclass_filename_gics_industry = "SECCLASS_GICS_Industry_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_gics_industry.to_csv(outpath + "\\" + secclass_filename_gics_industry, sep=',', encoding = 'utf-8', index=False)

#creating GICS Sector secclass file 

secclass_gics_sector = pd.DataFrame(columns=secclass_col_names)
secclass_gics_sector['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_gics_sector['ISIN'] = df_clean['Primary Identifier'].values
secclass_gics_sector['Security Name'] =  df_clean['Security Name'].values
secclass_gics_sector['Classifier Code'] = "GICS Sector"
secclass_gics_sector['Classification Code'] = df_clean['GICS Sector'].str[0:2]
secclass_gics_sector.dropna(subset=['Classification Code'], inplace = True)

secclass_filename_gics_sector = "SECCLASS_GICS_Sector_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_gics_sector.to_csv(outpath + "\\" + secclass_filename_gics_sector, sep=',', encoding = 'utf-8', index=False)

#creating GICS Sub- Industry secclass file 

secclass_gics_sub_ind = pd.DataFrame(columns=secclass_col_names)

secclass_gics_sub_ind['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_gics_sub_ind['ISIN'] = df_clean['Primary Identifier'].values
secclass_gics_sub_ind['Security Name'] =  df_clean['Security Name'].values
secclass_gics_sub_ind['Classifier Code'] = "GICSSub-Industry"
secclass_gics_sub_ind['Classification Code'] = df_clean['GICS Sub Industry'].str[0:8]
secclass_gics_sub_ind.dropna(subset=['Classification Code'], inplace = True)

secclass_filename_gics_sub_ind = "SECCLASS_GICS_Sub_Ind_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_gics_sub_ind.to_csv(outpath + "\\" + secclass_filename_gics_sub_ind, sep=',', encoding = 'utf-8', index=False)

#creating Everest Country of Issue Holding view file 

#secclass_country = pd.DataFrame(columns=secclass_col_names)
#
#secclass_country['Unique Security Identifier'] = df_clean['Primary Identifier'].values
#secclass_country['ISIN'] = df_clean['Primary Identifier'].values
#secclass_country['Security Name'] =  df_clean['Security Name'].values
#secclass_country['Classifier Code'] = "Ev_Country_Of_Issue(Holding)"
#secclass_country['Classification Code'] = df_clean['Country Of Issue'].values
#secclass_country.dropna(subset=['Classification Code'], inplace = True)
#
#secclass_filename_country = "SECCLASS_Country_Holding_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
#secclass_country.to_csv(outpath + "\\" + secclass_filename_country, sep=',', encoding = 'utf-8', index=False)

#creating GICS code classifier 

secclass_gics_code = pd.DataFrame(columns=secclass_col_names)

secclass_gics_code['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_gics_code['ISIN'] = df_clean['Primary Identifier'].values
secclass_gics_code['Security Name'] =  df_clean['Security Name'].values
secclass_gics_code['Classifier Code'] = "GICS_code"
secclass_gics_code['Classification Code'] = df_clean['GICS Sub Industry'].str[0:8]
secclass_gics_code.dropna(subset=['Classification Code'], inplace = True)

secclass_filename_gics_code = "SECCLASS_gics_code_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_gics_code.to_csv(outpath + "\\" + secclass_filename_gics_code, sep=',', encoding = 'utf-8', index=False)

#creating Bloomberg ID & Bloomberg FIGI classifier 

secclass_ev_bbg_id = pd.DataFrame(columns=secclass_col_names)

secclass_ev_bbg_id['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_ev_bbg_id['ISIN'] = df_clean['Primary Identifier'].values
secclass_ev_bbg_id['Security Name'] =  df_clean['Security Name'].values
secclass_ev_bbg_id['Classifier Code'] = "BBG_ID"
secclass_ev_bbg_id['Classification Code'] = df_clean['Bloomberg ID'].values
secclass_ev_bbg_id.dropna(subset=['Classification Code'], inplace = True)

secclass_ev_bbg_id_filename = "SECCLASS_Ev_bbg_id_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_ev_bbg_id.to_csv(outpath + "\\" + secclass_ev_bbg_id_filename, sep=',', encoding = 'utf-8', index=False)

secclass_ev_bbg_figi = pd.DataFrame(columns=secclass_col_names)

secclass_ev_bbg_figi['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_ev_bbg_figi['ISIN'] = df_clean['Primary Identifier'].values
secclass_ev_bbg_figi['Security Name'] =  df_clean['Security Name'].values
secclass_ev_bbg_figi['Classifier Code'] = "BBG_FIGI"
secclass_ev_bbg_figi['Classification Code'] = df_clean['Bloomberg FIGI'].values
secclass_ev_bbg_figi.dropna(subset=['Classification Code'], inplace = True)

secclass_ev_bbg_figi_filename = "SECCLASS_Ev_bbg_figi_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_ev_bbg_figi.to_csv(outpath + "\\" + secclass_ev_bbg_figi_filename, sep=',', encoding = 'utf-8', index=False)

secclass_ev_lien_type = pd.DataFrame(columns=secclass_col_names)

secclass_ev_lien_type['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_ev_lien_type['ISIN'] = df_clean['Primary Identifier'].values
secclass_ev_lien_type['Security Name'] =  df_clean['Security Name'].values
secclass_ev_lien_type['Classifier Code'] = "Everest_Lien_Type"
secclass_ev_lien_type['Classification Code'] = df_clean['Lien Type'].values
secclass_ev_lien_type.dropna(subset=['Classification Code'], inplace = True)

secclass_ev_lien_type_filename = "SECCLASS_Ev_lien_type_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_ev_lien_type.to_csv(outpath + "\\" + secclass_ev_lien_type_filename, sep=',', encoding = 'utf-8', index=False)


#creating Everest seniority classifier 

secclass_ev_seniority = pd.DataFrame(columns=secclass_col_names)

secclass_ev_seniority['Unique Security Identifier'] = df_clean['Primary Identifier'].values
secclass_ev_seniority['ISIN'] = df_clean['Primary Identifier'].values
secclass_ev_seniority['Security Name'] =  df_clean['Security Name'].values
secclass_ev_seniority['Classifier Code'] = "Everest_Seniority"
secclass_ev_seniority['Classification Code'] = df_clean['Seniority'].values
secclass_ev_seniority.dropna(subset=['Classification Code'], inplace = True)

secclass_ev_seniority_filename = "SECCLASS_Ev_Seniority_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
secclass_ev_seniority.to_csv(outpath + "\\" + secclass_ev_seniority_filename, sep=',', encoding = 'utf-8', index=False)


name = "df_Clean"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
df_clean.to_csv(outpath + "\\" + name, sep=',', encoding = 'utf-8', index=False)


##creating Category classifier 
##deleting cells where Country is blank
#df_loans = df_loans[~df_loans['Country Of Issue'].isnull()]
#df_loans['Category'] = np.where(df_loans['Country Of Issue'].isin(USFilter),
#        "Loan United States","Loan Europe")
#df_bonds = df_bonds[~df_bonds['Country Of Issue'].isnull()]
#df_bonds['Category'] = np.where(df_bonds['Country Of Issue'].isin(USFilter),
#        "Bond United States","Bond Europe")
#df_abs['Category'] = np.where(df_abs['Primary Identifier'].str[0:2]=='US',
#        "CLO United States","CLO Europe")
#
##Merging two dataframes
#df_abs_bonds = df_abs.append(df_bonds, sort = False)
#df_clean = df_loans.append(df_abs_bonds, sort = False)
##df_clean.set_index(['Primary Identifier'], inplace = True)
#df_clean.reset_index(inplace = True)
##len(df_clean)
#
#secclass_category = pd.DataFrame(columns=secclass_col_names)
#
#secclass_category['Unique Security Identifier'] = df_clean['Primary Identifier'].values
#secclass_category['ISIN'] = df_clean['Primary Identifier'].values
#secclass_category['Security Name'] =  df_clean['Security Name'].values
#secclass_category['Classifier Code'] = "Category"
#secclass_category['Classification Code'] = df_clean["Category"]
#secclass_category.dropna(subset=['Classification Code'], inplace = True)
#
#secclass_filename_category = "SECCLASS_category_"+(time.strftime("%Y%m%d_%H%M%S")+".csv")
#secclass_category.to_csv(outpath + "\\" + secclass_filename_category, sep=',', encoding = 'utf-8', index=False)

#Exit Message

window = Tk()
window.geometry("500x100+700+400")

def close_window (): 

    window.destroy()

button = Button ( text = ".CSV files are Saved! Please Click to Exit :)", command = close_window)
button.pack()

window.mainloop()
