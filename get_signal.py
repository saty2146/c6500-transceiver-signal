#!/usr/bin/python

import os
import glob
import numpy as np
import pandas as pd

from snmp_helper import snmp_get_oid,snmp_get_oid_get,snmp_extract

COMMUNITY = 'XXX'
SNMP_PORT = 161
HOST = ('X.X.X.X', COMMUNITY, SNMP_PORT) 
my_path = '/path/'

#OID 1.3.6.1.4.1.9.9.91.1.1.1.1 look for sensor type entSensorType 14
#OID 1.3.6.1.2.1.47.1.1.1.1.7 look for iface based on sensor type

entSensorType = snmp_get_oid(HOST, oid='1.3.6.1.4.1.9.9.91.1.1.1.1',
        display_errors=True)

sensor_id = []

for i in range(len(entSensorType)):
    if entSensorType[i][0][1] == 14:
        sensor_id.append(entSensorType[i][0][0][14])
                         
#print sensor_id

sensor_iface = {}

for id in sensor_id:
    oid_iface = "1.3.6.1.2.1.47.1.1.1.1.7." + str(id)
    oid_strength = "1.3.6.1.4.1.9.9.91.1.1.1.1.4." + str(id)
                
    iface_get = snmp_get_oid_get(HOST, oid=oid_iface,
    display_errors=True)
    strength_get = snmp_get_oid_get(HOST, oid=oid_strength, display_errors=True)
    iface_description = str(iface_get[0][1])
    iface_list = iface_description.split(" ")   # e.g. ['Te2/1', 'Transmit', 'Power', 'Sensor']
    iface_raw = iface_list[0]                   # e.g. Te2/1
    strength =str(strength_get[0][1])
    direction = "Tx" if iface_list[1] == "Transmit" else "Rx"
    sensor_iface.update({id:[iface_raw,strength,direction]})

#print sensor_iface

from time import gmtime, strftime
date_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

chars_to_remove = ['\\', '/']

iface_dict = {}

def listToStringWithoutBrackets(list1):
    return str(list1).replace('[','').replace(']','')

for key, value in sensor_iface.iteritems():
    iface_dict[value[0]] = [date_time,0,0]

for key, value in sensor_iface.iteritems():
    iface_value = round(int(value[1]) * 0.1,2)          #correct dbm value
    if value[2] == "Tx":
        iface_dict[value[0]][1] = iface_value
    else:
        iface_dict[value[0]][2] = iface_value

#print iface_dict

for key in iface_dict:
    iface = key.translate(None, ''.join(chars_to_remove))   #iface e.g. Te21 for filename 
    filename = my_path + "shc32-" + iface + ".csv"                    #filename e.g. shc32-Te21.csv
    fn = open(filename,'a')
    line = listToStringWithoutBrackets(iface_dict[key])
    fn.write(line + "\n") 
    fn.close()



#for filename in glob.iglob(my_path + '.csv'):
#    
#    chart_name = os.path.basename(filename)
#    df = pd.read_csv(str(filename), names=['datetime', 'Tx', 'Rx'])
#               
#    iface = df[['Tx','Rx','datetime']]
#    print iface['Tx']
#
#for filename in glob.iglob(my_path + "*.csv"):
#    print filename
