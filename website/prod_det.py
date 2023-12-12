#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 16:35:10 2023

@author: ricardo
"""

import pandas as pd
import json

dic_prod={'ID':{'':''},'Molecule':"",'Smile':""}
d_prod={'':{'Molecule':"",'Smile':"","Detectables":''}}
d_prod
producibles = dict(pd.read_csv('Producible.csv', delimiter=';'))
p=dict(producibles['ID'])
m=list(producibles['Molecule'])
s=list(producibles['Smile'])
dic_prod['Molecule']=m
dic_prod['Smile']=s
dic_prod['ID']=p

print(producibles['ID'][2])

res = dict((v,k) for k,v in dic_prod['ID'].items())
dic_prod['ID']=res
detectables = (pd.read_csv('Detectable.csv', delimiter=';'))
pathways =  pd.read_csv('Pathways.csv', delimiter=';')
P1=pathways['Pair'].str.endswith("P1")
test=pathways['Pair']
prod1="P13"
d={}
dic={'id':{'P13':''}}
result1=pathways.loc[pathways['Producible'] == prod1]
detectables1=list(result1['Detectable'])
detectables1 = list( dict.fromkeys(detectables1))
detectables1=list( dict.fromkeys(detectables1))
first_key = list(dic_prod['ID'].keys())[0]
prod = list(dic_prod['ID'].keys())
print(prod)
print (first_key)

for i in prod:
    print(i)
    result=pathways.loc[pathways['Producible'] == i]
    detectables=list(result['Detectable'])
    detectables = list( dict.fromkeys(detectables))
    detectables=list( dict.fromkeys(detectables))
    print(detectables)
    dic_prod['ID'][i]=detectables

prod_det=json.dumps(dic_prod, indent = 3)
with open("prod_det.json", "w") as outfile: 
    json.dump(dic_prod, outfile)
    