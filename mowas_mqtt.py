#!/usr/bin/env python3
# -*- coding: utf-8 -*
import os
import requests
import json
from requests.exceptions import ConnectionError
/*
 * Version 0.1.0
 * By Thomas Binder
 * openHAB Community: https://community.openhab.org/u/binderth
*/


# API information
# AGS from a "Landkreis" coming from https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/_inhalt.html

landkreis_ags = '097720000000'
landkreis_status = 'https://warnung.bund.de/bbk.status/status_{}.json'.format(landkreis_ags)
json_URLs = {
    'mowas':    'https://warnung.bund.de/bbk.mowas/gefahrendurchsagen.json',
    'biwapp':   'https://warnung.bund.de/bbk.biwapp/warnmeldungen.json',
    'katwarn':  'https://warnung.bund.de/bbk.katwarn/warnmeldungen.json',
    'lhp':      'https://warnung.bund.de/bbk.lhp/hochwassermeldungen.json',
    'dwd':      'https://warnung.bund.de/bbk.dwd/unwetter.json',
    'mowas':    'https://warnung.bund.de/bbk.mowas/gefahrendurchsagen.json'
}
mqtt_ipaddress= "192.168.xx.yy"
mqtt_user= "user"
mqtt_pass= "pass"
mqtt_roottopic= "openHAB/master/mowasJSON/"

buckets_live = {}
JSONreturn = {}

def get_json_as_dict(url):
    headers = {'Accept': '*/*',
             'Content-Type': 'application/json; charset=utf-8',
             'User-Agent': 'mowas_mqtt'}
    # make request, gracefully with error
    try:
        r = requests.get(url, headers=headers)
    except ConnectionError as e:
        print("Connection Error")
        print(e)
        return json.loads('{"data": {"Connection Error": 1, "URL": "'+url+'", "error": "'+e+'"}}')
    # wenn HTTP-StatusCode nicht 200
    if r.status_code != 200:
        return json.loads('{"data": {"HTTP Error": 1, "URL": "'+url+'", "error": "'+str(r.status_code)+'"}}')
    # JSON to dict, gracefully with error
    try:
        data = json.loads(r.content.decode())
    except ValueError as e:
        print ("JSON Error")
        print (e)
        return json.loads('{"data": {"JSON Error": 1, "URL": "'+url+'", "error": "'+e+'"}}')
    return data




if __name__ == "__main__":
    # get JSON from Landkreis as dict
    landkreis_meldungen = get_json_as_dict(landkreis_status)
    
    # check, if there's announcements for the Landkreis
    i = 0
    for bucket in landkreis_meldungen:
        # MOWAS JSON has multiple buckets, currently:
        # 0: bkk.mowas
        # 1: bbk.biwapp
        # 3: bkk.katwarn
        # 4: bkk.lhp
        # 5: bkk.dwd
        keys = bucket['bucketname'].split(".")
        buckets_live[keys[1]] = {}
        for ref in bucket['ref']:
            # call the URL and find message
            buckets_live[keys[1]]['ref'+str(i)] = ref
            i = i + 1

    # get the announcements information
    i = 0
    #print (buckets_live)    
    for buckets in buckets_live:
        if (len(buckets_live[buckets]) > 0):
            # There's announcements for that bucket!
            announcementJSON = get_json_as_dict(json_URLs[buckets])
            for meldung, meldewert in (buckets_live[buckets].items()):
                j = 0
                while (j < len(announcementJSON)):
                    if (announcementJSON[j]["identifier"] == meldewert):
                        JSONreturn[i] = announcementJSON[j]
                        JSONreturn[i]["info"][0]["area"][0].pop("polygon")
                    j = j+1
                i = i + 1
    
    print ("mosquitto_pub -h " + mqtt_ipaddress + " -u '" + mqtt_user + "' -P '" + mqtt_pass + "' -t '" + mqtt_roottopic + "' -m '" + json.dumps(JSONreturn) + "'")
    os.system("mosquitto_pub -h " + mqtt_ipaddress + " -u '" + mqtt_user + "' -P '" + mqtt_pass + "' -t '" + mqtt_roottopic + "' -m '" + json.dumps(JSONreturn) + "'")
