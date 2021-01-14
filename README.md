# mowas_mqtt
Converter for reading JSON from MOWAS and sending the data via MQTT

# Prerequisites
* living in Germany ;)
* knowing your "Amtlicher Gemeindeschlüssel (AGS)" for your Landkreis (not city!), available from https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/Administrativ/04-kreise.html
* Paho MQTT Client (https://pypi.org/project/paho-mqtt/) e.g. `pip install paho-mqtt`

# Variables in mowas_mqtt.ini settings file
[General]
* loglevel: INFO, DEBUG
* *INFO: shows only when ready
* *DEBUG: shows more debug information to track down errors

[AGS]
* Landkreis: name of your Landkreis (not yet used in script)
* AGScode: insert your AGS (Amtlicher Gemeindeschlüssel) for your Landkreis, there's only JSONs available for Landkreise, not cities or other smaller entities. The AGScode must be 12 digits long, if yours is shorter, please add enough "0" for 12 digits.

[MQTT]
* Broker: IP-Address (or FQN) of your MQTT Broker
* Port: Port for your Broker (1883 or 8883 for SSL)
* QOS: QOS-level for the messge
* Topic: MQTT topic for the JSON 
* User: Username for the broker (leave empty for anonymous call)
* Password: Password for the broker (leave empty for anonymous call)
* ClientID: ClientID for the broker to avoid parallel connections

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
* ...
