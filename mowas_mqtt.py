#!/usr/bin/env python3
# -*- coding: utf-8 -*
import os                                           # using the OS
import requests                                     # requesting information
import json                                         # working with JSON 
import configparser                                 # working with INI
from requests.exceptions import ConnectionError     # errors in requests


# read settings from mowas_mqtt.ini
ApplicationDir = os.path.dirname(os.path.abspath(__file__))
ReadSettings = os.path.join(ApplicationDir, 'mowas_mqtt.ini')
Settings = configparser.ConfigParser()
Settings.read(ReadSettings)

# Log-Level
loglevel = Settings.get("General", "loglevel")
# MQTT-Settings
mqtt_paho = eval(Settings.get("MQTT", "Paho"))
mqtt_ipaddress = Settings.get("MQTT", "Broker")
mqtt_user = Settings.get("MQTT", "User")
mqtt_pass = Settings.get("MQTT", "Password")
mqtt_topic = Settings.get("MQTT", "Topic")
mqtt_port = int(Settings.get("MQTT", "Port"))
mqtt_qos = int(Settings.get("MQTT", "QOS"))
mqtt_retain = eval(Settings.get("MQTT", "Retain"))
mqtt_clientid = Settings.get("MQTT", "ClientID")

# Landkreis AGS
landkreis_ags=Settings.get("AGS", "AGScode")

# setting API information sort of from https://warnung.bund.de/bbk.config/config_rel.json 
landkreis_status = 'https://warnung.bund.de/bbk.status/status_{}.json'.format(landkreis_ags)
json_URLs = {
    'mowas':    'https://warnung.bund.de/bbk.mowas/gefahrendurchsagen.json',
    'biwapp':   'https://warnung.bund.de/bbk.biwapp/warnmeldungen.json',
    'katwarn':  'https://warnung.bund.de/bbk.katwarn/warnmeldungen.json',
    'lhp':      'https://warnung.bund.de/bbk.lhp/hochwassermeldungen.json',
    'dwd':      'https://warnung.bund.de/bbk.dwd/unwetter.json'
}

# start variables
buckets_live = {}
JSONreturn = {}

def on_connect(client, userdata, flags, rc):
    # Connect to MQTT-Broker
    if rc==0:
        print("Connected to broker using Paho with result code " + str(rc))
    else:
        print("Connection Error to broker using Paho with result code "+ str(rc))

def send_mqtt_paho(message, topic):
    # send MQTT message
    print ("Sending JSON using Paho-Client with Broker '{}' to Topic '{}'".format(mqtt_ipaddress,topic))
    if (loglevel == "DEBUG"):
        print ("Broker with Client-ID '{}', Port '{}', User '{}', Passwort '{}' and QOS '{}', Retain '{}'".format(mqtt_clientid, mqtt_port, mqtt_user, mqtt_pass, mqtt_qos, mqtt_retain))         
        print ("Sending message: " + message)
    mqttclient = mqtt.Client(mqtt_clientid)
    mqttclient.on_connect = on_connect
    if mqtt_user != "":
        mqttclient.username_pw_set(mqtt_user, mqtt_pass)
    mqttclient.connect(mqtt_ipaddress, mqtt_port, 60)
    mqttclient.loop_start()
    mqttpub = mqttclient.publish(topic, payload=message, qos=mqtt_qos, retain=mqtt_retain)
    mqttclient.loop_stop()
    mqttclient.disconnect()

def send_mqtt_os(message, topic):
    # send MQTT message
    print ("Sending JSON using os.system and mosquitto_pub and Broker '{}' to Topic '{}'".format(mqtt_ipaddress,topic))
    os.system("mosquitto_pub -h " + mqtt_ipaddress + " -u '" + mqtt_user + "' -P '" + mqtt_pass + "' -t '" + topic + "' -m '" + message + "'")     

def get_json_as_dict(url):
    # GET JSON from URL
    global requestError
    headers = {'Accept': '*/*',
             'Content-Type': 'application/json; charset=utf-8',
             'User-Agent': 'MOWAS-MQTT'}
    # make request, gracefully with error
    try:
        if (loglevel == "DEBUG"):
            print("request URL: {} - {}".format(str(url),str(headers)))
        r = requests.get(url, headers=headers)
    except ConnectionError as e:
        requestError = True
        print("Connection Error")
        print(e)
        return json.loads('{"data": {"Connection Error": 1, "URL": "'+url+'", "error": "'+e+'"}}')
    # wenn HTTP-StatusCode not 200
    if r.status_code != 200:
        requestError = True
        print("HTTP Error")
        print(str(r.status_code))
        return json.loads('{"data": {"HTTP Error": 1, "URL": "'+url+'", "error": "'+str(r.status_code)+'"}}')
    # JSON to dict, gracefully with error
    try:
        data = json.loads(r.content.decode())
    except ValueError as e:
        requestError = True
        print("JSON Error")
        print(e)
        return json.loads('{"data": {"JSON Error": 1, "URL": "'+url+'", "error": "'+e+'"}}')
    requestError = False
    return data

def search_in_dict (values, searchterm):
    # find a term in a dict
    for k in values:
        print (values)
        print (k)
        for v in values[k]:
            if searchterm in v:
                return True
    return False


if __name__ == "__main__":
    # get JSON from Landkreis as dict
    landkreis_meldungen = get_json_as_dict(landkreis_status)
   
    # check, if there's an error with the JSON
    if (requestError == True):
        send_mqtt(json.dumps(landkreis_meldungen), mqtt_topic)
        if loglevel == "DEBUG":
            print(landkreis_meldungen)
        quit('Error in URL: ' + landkreis_status)
    
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
        if (loglevel == "DEBUG"):
            print("Find Buckets #" + str(i))
        for ref in bucket['ref']:
            # call the URL and find message
            if (loglevel == "DEBUG"):
                print("Add Bucket to JSON: " + ref)
            buckets_live[keys[1]]['ref'+str(i)] = ref
            i = i + 1

    # get the announcements information
    if (loglevel == "DEBUG"):
        print("Add Bucket to JSON: " + ref)
    i = 0

    for buckets in buckets_live:
        if (len(buckets_live[buckets]) > 0):
            # There's announcements for that bucket!
            if (loglevel == "DEBUG"):
                print("open JSON for Bucket: " + json_URLs[buckets])

            announcementJSON = get_json_as_dict(json_URLs[buckets])
            if (loglevel == "DEBUG"):
                print("Found Announcements in: " + json_URLs[buckets])
            for meldung, meldewert in (buckets_live[buckets].items()):
                j = 0
                while (j < len(announcementJSON)):
                    if (loglevel == "DEBUG"):
                        print("search Announcement for: " + meldewert)
                    if (announcementJSON[j]["identifier"] == meldewert):
                        if (loglevel == "DEBUG"):
                            print("Added Announcement for: " + meldewert)
                        JSONreturn[i] = announcementJSON[j]
                        JSONreturn[i]["info"][0]["area"][0].pop("polygon")
                    j = j+1
                i = i + 1
    
    # Sending final JSON with MQTT
    if loglevel == "DEBUG":
        print ("Sending MQTT")

    # if Paho is active use this, else use mosquitto_pub with .os
    if mqtt_paho == True:
        import paho.mqtt.client as mqtt				        # using MQTT-client
        send_mqtt_paho(json.dumps(JSONreturn), mqtt_topic)
    else:
        send_mqtt_os(json.dumps(JSONreturn), mqtt_topic)
