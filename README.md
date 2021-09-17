![license](https://img.shields.io/github/license/leinadred/PY-PACBuilder)	
![language](https://img.shields.io/github/languages/top/leinadred/PY-PACBuilder)

# Py-PACBuilder

Script meant to download Office 365 Endpoint List (https://docs.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-ip-web-service?view=o365-worldwide), WebEx Feed (wsa-csv format https://help.webex.com/en-us/WBX000028782/Network-Requirements-for-Webex-Services#id_134751) and/or other sources and build a PAC File i.e. to go directly or special proxy configuration...

Additionally defined "static" entries are configurable (internal Domains, IP Scopes and so on, have a look at params.json_example)


more informations and integrations to come... 

# Dependencies
Following modules are used:

uuid,
requests,
json,
argparse,
logging,
ipaddress,
os,
datetime

# Usage
- clone repository
- create a params.json (copy example/template file and edit it on your needs)

command line:
python ./pacbuilder.py -o <destinationfilename>
(if -o not given, script will generate a name with timestamp)

# Outlook
- v (to come - add verbosity of output)
- create an example/template file for own json


