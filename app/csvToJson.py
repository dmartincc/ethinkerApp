# -*- coding: utf8 -*-
import csv, itertools, json
 
def cluster(rows):
    result = []
    data = sorted(rows, key=lambda r: r[1])
    for k, g in itertools.groupby(rows, lambda r: r[0]):
        group_rows = [row[1:] for row in g]
 
        if len(row[1:]) == 1:
               result.append({"name": row[0],"size": int(row[1])*100})
        else:
               result.append({"name": k,"children":cluster(group_rows)})
 
    return result

def clusterJson(rows):
    result = []
    data = sorted(rows, key=lambda r: r[1])
    for k, g in itertools.groupby(rows, lambda r: r[0]):
        group_rows = [row[1:] for row in g]
 
        if len(row[1:]) == 1:
               result.append({"name": row[0],"size": int(row[1])*100})
        else:
               result.append({"name": k,"children":cluster(group_rows)})
 
    return result
 
if __name__ == '__main__':
    s = '''\
sys,WCNV,Converter,1
sys,WCNV,Grid,2
sys,WGEN,Gen, inverter,3
sys,WGEN,Generator,4
sys,WGEN,Grid,5
sys,WNAC,Environment,6
sys,WROT,Hub,7
sys,WROT,Rotor,8
sys,WTRF,Grid,9
sys,WTRM,Brake,10
sys,WTRM,Gear,11
sys,WTRM,Hydraulics,12
sys,WTUR,xxx,13
sys,WTUR,Controller,14
sys,WTUR,Environment,15
sys,WTUR,Grid,16
sys,WTUR,Miscellaneous,17
sys,WTUR,Pitch,18
sys,WTUR,System,19
sys,WTUR,Turbine,20
sys,WTUR,Yaw,21
sys,WYAW,Yaw,22
'''
rows = list(csv.reader(s.splitlines()))
print json.dumps(cluster(rows)[0],indent=2)