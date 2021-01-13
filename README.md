# mowas_mqtt
Converter for reading JSON from MOWAS and sending the data via MQTT

# Prerequisites
* living in Germany ;)
* knowing your "Amtlicher Gemeindeschlüssel (AGS)" for your Landkreis (not city!), available from https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/Administrativ/04-kreise.html
* mosquitto_pub (see ToDo)

# Variables in script
* landkreis_ags: insert your AGS for your Landkreis, there's only JSONs available for Landkreise, not cities or other smaller entities.
* mqtt_ipaddress: IP-Address of your MQTT Broker
* mqtt_user: MQTT User
* mqtt_pass: MQTT password
* mqtt_roottopic: MQTT topic for the JSON 

# what the script does
The script searches for Identifiers of your AGS in all of warnings from the german Bundesamt für Bevölkerungsschutz und Katastrophenschutz for your regions.
It subsumizes the findings in a complete JSON in the nodes
* bkk.mowas: Modulares Warnsystem
* bbk.biwapp: Bürgerinfo und Warn-App
* bkk.katwarn: KATWARN
* bkk.lhp: Länderübergreifendes Hochwasserportal
* bkk.dwd: Deutscher Wetterdienst

So the JSON of this script only has the warnings for your regions in it.

# ToDo
* Integration of MQTT-publisher in python
