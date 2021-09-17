# 202101 - Daniel Meier
import uuid
import requests
import json
import argparse
import logging
import ipaddress
import os
from datetime import datetime

#################################################################################################
# set args                                                                                      #
#################################################################################################
parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outfile', help='Target file name (ie. proxy.pac')
args = parser.parse_args()
#################################################################################################
params={}
pacdata={}
if not args.outfile:
    filename=str(datetime.now()).replace(' ','-').replace('.','_')+'.pac'
else:
    filename=args.outfile

def fun_setup():
    try:
        with open('params.json', 'r') as paramsfile:
            json.load(paramsfile)
    except:
        print("parameter file not found or invalid, please define! Downloading template, please adjust!")
        with open("params.json", "w") as paramsfile:
            tmpl_url = 'https://cloudfs.ackme.tech/index.php/s/TxyExbDQzsTeCTm/download/params.json_tmpl'
            r = requests.get(tmpl_url, verify=False)
            with open("params.json_tmpl","w") as file:
                file.write(r.content)
            raise ValueError("Downloaded file 'params.json_tmpl' - now you can set your preferencecs.")
    else:
        print("file found, using it!")
        with open("params.json","r") as paramsjson:
            params = json.load(paramsjson)
    #print(dir(params))
    #print(params)
    if params["general"]["v_debug"]=='True':
        logging.basicConfig(level=logging.DEBUG)
    logging.debug("################## Starting - With extended Logging ##################")
    logging.debug("################## Setup Done, downloading Feeds ##################")
    return params

def fun_downloadfeeds():    
    params = fun_setup()
    n=1
    for feeds in params["feeds"]:
        print("Feed to work on: "+str(params["feeds"][feeds]["feed_name"])+"...")
        logging.debug("################## Downloading from "+str(params["feeds"][feeds]["feed_url"])+" ##################")
        #feedcontent = str("feedcontent_"+str(n))
        if params["feeds"][feeds]["feed_uuid"]=="True":
            feedcontent = requests.get(params["feeds"][feeds]["feed_url"]+params["feeds"][feeds]["feed_guid"], verify=False)
        else:
            feedcontent = requests.get(params["feeds"][feeds]["feed_url"], verify=False)
        feedname=str(params["feeds"][feeds]["feed_name"])
        pacdata[feedname]={}
        try:
            feedcontent.status_code==200
        except:
            print("Download failed or file could not be parsed! (is it json formatted?)")
            raise(SystemExit)
        else:
            #pacdata[feedname]['ServiceArea']={}
            n+=1
            fun_extractfromfeed(feedname,feedcontent,params,feeds)
    fun_pacbuilding(pacdata,params,filename)
    with open (filename,'a+') as file:
        file.write('else return "{0}";\n'.format(params['actions'][params['default']['act_todo']]))
        file.write("    }")

def fun_extractfromfeed(feedname,feedcontent,params,feeds):
    cnt_url=1
    cnt_ip4=1
    cnt_ip6=1
    if params['feeds'][feeds]['feed_format']=='json':
        for feedcont_entry in feedcontent.json():
            pacdata[feedname]['action']={}
            pacdata[feedname]['action']=params["feeds"][feeds]["pac_action"]["act_todo"]
            pacdata[feedname][feedcont_entry['serviceArea']]={}
            pacdata[feedname][feedcont_entry['serviceArea']]['urls']={}
            pacdata[feedname][feedcont_entry['serviceArea']]['ips']={}
            pacdata[feedname][feedcont_entry['serviceArea']]['ips']['v4']={}
            pacdata[feedname][feedcont_entry['serviceArea']]['ips']['v6']={}
        for feedcont_entry in feedcontent.json():
            if feedcont_entry['required']==False and not params["feeds"][feeds]['feed_option'] == 'all':
                print("Not Required: "+str(pacdata[feedname][feedcont_entry['serviceArea']]))
            else:   
                for fe_key in feedcont_entry.keys():
                    if fe_key == 'urls':
                        pacdata[feedname][feedcont_entry['serviceArea']]['urls'][cnt_url]={}
                        for entry in feedcont_entry['urls']:
                            pacdata[feedname][feedcont_entry['serviceArea']]['urls'][cnt_url]=entry
                            cnt_url=cnt_url+1
                    if fe_key == 'ips':
                        #pacdata[feedname]['ips'][cnt_ip]={}
                        for entry in feedcont_entry['ips']:
                            try:
                                ipaddress.IPv4Network(entry)
                            except:
                                try:
                                    ipaddress.IPv6Network(entry)
                                except:
                                    print("something weird with address "+entry)
                                else:
                                    pacdata[feedname][feedcont_entry['serviceArea']]['ips']['v6'][cnt_ip6]=entry
                                    cnt_ip6=cnt_ip6+1
                            else:
                                pacdata[feedname][feedcont_entry['serviceArea']]['ips']['v4'][cnt_ip4]=entry
                                cnt_ip4=cnt_ip4+1
    elif params['feeds'][feeds]['feed_format']=='wsa-csv':
        cnt_site=1
        cnt_ip4=1
        cnt_ip6=1        
        feedcont_entry='from-wsa-csv'
        pacdata[feedname]['action']={}
        pacdata[feedname]['action']=params["feeds"][feeds]["pac_action"]["act_todo"]
        pacdata[feedname][feedcont_entry]={}
        pacdata[feedname][feedcont_entry]['ips']={}
        pacdata[feedname][feedcont_entry]['urls']={}
        pacdata[feedname][feedcont_entry]['ips']['v4']={}
        pacdata[feedname][feedcont_entry]['ips']['v6']={}
        pacdata[feedname][feedcont_entry]['action']=params['feeds'][feeds]['pac_action']['act_todo']
        for destination in feedcontent.text.splitlines():
            if destination.split(',')[0][0]=='.':
                pacdata[feedname][feedcont_entry]['urls'][cnt_site]=destination.split(',')[0].replace('.','*.',1)
            else:
                pacdata[feedname][feedcont_entry]['urls'][cnt_site]=destination.split(',')[0]
            cnt_site+=1
        pass
    elif params['feeds'][feeds]['feed_format']=='csv':
        cnt_site=1
        cnt_ip4=1
        cnt_ip6=1
        feedcont_entry='csv'
        pacdata[feedname]['action']={}
        pacdata[feedname]['action']=params["feeds"][feeds]["pac_action"]["act_todo"]
        pacdata[feedname][feedcont_entry]={}
        pacdata[feedname][feedcont_entry]['urls']={}
        pacdata[feedname][feedcont_entry]['ips']={}
        pacdata[feedname][feedcont_entry]['ips']['v4']={}
        pacdata[feedname][feedcont_entry]['ips']['v6']={}
        pacdata[feedname][feedcont_entry]['action']=params['feeds'][feeds]['pac_action']['act_todo']
        for destination in feedcontent.text.split(','):
            if destination=='':print('found empty value, ignoring')
            else:
                try:
                    ipaddress.ip_network(destination)
                except:
                    #domainname
                    if destination[0]=='.':
                        pacdata[feedname][feedcont_entry]['urls'][cnt_site]=destination.replace('.','*.',1)
                    else:
                        pacdata[feedname][feedcont_entry]['urls'][cnt_site]=destination
                    cnt_site+=1
                else:
                    try:
                        ipaddress.IPv4Network(destination)
                    except:
                        try:
                            ipaddress.IPv6Network(destination)
                        except:
                            print("something is wrong with {0}".format(destination))
                        else:
                            pacdata[feedname][feedcont_entry['serviceArea']]['ips']['v6'][cnt_ip6]=destination
                    else:
                        if destination[0]=='.':
                            pacdata[feedname][feedcont_entry]['urls'][cnt_site]=destination.replace('.','*.',1)
                        else:
                            pacdata[feedname][feedcont_entry]['urls'][cnt_site]=destination
                        cnt_site+=1
    elif params['feeds'][feedname]['feed_format']=='plain':
        pass # FUTURE Build, Plain text or other formats
    return pacdata

def fun_pacbuilding(pacdata,params,filename):
    #filename=str(datetime.now()).replace(' ','-').replace('.','_')+'.pac'    
    try:
        with open (filename,'r'):
            print('file exists')
    except:
        with open(filename, 'w') as file:
            file.write
    else:
        filename=str(datetime.now()).replace(' ','-').replace('.','_')+'_1.pac'
        print('generating new file')
        with open (filename,'w') as file:
            file.write
    print('pacfile all is written to: '+filename)
    with open (filename,'a+') as file:
        file.write("function FindProxyForURL(url, host) {\n")
    #DEBUG
    #print(pacdata)
    line=''
    pacline={}
    isfirst=True
    for feedname in list(pacdata.keys()): #Feeds
        if line =='' and isfirst==True:
            line+='if ('
            isfirst=False
        else:
            line+='else if('
        for feedservice in list(pacdata[feedname].keys()): #Parts of Feeds, like "Skype","Exchange" 
            if not feedservice == 'action':
                for feeditemtype in pacdata[feedname][feedservice]: # type - URLs/IP
                    if feeditemtype=='urls':
                        for feeditem in pacdata[feedname][feedservice][feeditemtype]:
                            if line =='' and isfirst==True:
                                line+='if ('
                                isfirst=False
                                pacline={}
                                pacline['targetline']={}
                            elif line =='':
                                line+='else if('
                                pacline['targetline']={}
                                if pacdata[feedname][feedservice][feeditemtype][feeditem].startswith('*.'):
                                    line='if (shExpMatch(host, "{0}") ||\n'.format(pacdata[feedname][feedservice][feeditemtype][feeditem])
                                else:
                                    line='if (dnsDomainIs(host, "{0}") ||\n'.format(pacdata[feedname][feedservice][feeditemtype][feeditem])
                            else:
                                if pacdata[feedname][feedservice][feeditemtype][feeditem].startswith('*.'):
                                    if feeditem==1:
                                        line+='shExpMatch(host, "{0}") ||\n'.format(pacdata[feedname][feedservice][feeditemtype][feeditem])
                                    else:
                                        line+='\tshExpMatch(host, "{0}") ||\n'.format(pacdata[feedname][feedservice][feeditemtype][feeditem])
                                else:
                                    line+='\tdnsDomainIs(host, "{0}") ||\n'.format(pacdata[feedname][feedservice][feeditemtype][feeditem])
                    if feeditemtype=='ips':
                        for ipver in pacdata[feedname][feedservice][feeditemtype]:
                            for feeditem in pacdata[feedname][feedservice][feeditemtype][ipver]:
                                if line =='' and isfirst==True:
                                    line+='if ('
                                    pacline={}
                                    pacline['targetline']={}
                                elif line =='':    
                                    line+='else if (isInNet(host, "{0}", "{1}") || isInNet(dnsResolve(host), "{0}", "{1}") ||\n'.format(str(ipaddress.ip_network(pacdata[feedname][feedservice][feeditemtype][ipver][feeditem]).network_address), str(ipaddress.ip_network(pacdata[feedname][feedservice][feeditemtype][ipver][feeditem]).netmask))
                                else:
                                    line+='\tisInNet(host, "{0}", "{1}") || isInNet(dnsResolve(host), "{0}", "{1}") ||\n'.format(str(ipaddress.ip_network(pacdata[feedname][feedservice][feeditemtype][ipver][feeditem]).network_address), str(ipaddress.ip_network(pacdata[feedname][feedservice][feeditemtype][ipver][feeditem]).netmask))
        line=line[:-3]+')\n\t\t\treturn "{0}";\n'.format(params['actions'][pacdata[feedname]['action']])
        pacline['targetline']=line
        with open (filename,'a+') as file:
            file.write(pacline['targetline'])
        line=''
        pacline.clear()   
    for content in list(params['static'].keys()):
        if content.startswith('domains_'):
            for domainitem in params['static'][content]['destdomains']['names'].split(','):
                if line =='' and isfirst==True:
                    line+='if ('
                    isfirst=False
                elif line =='':
                    line+='else if('
                    if domainitem.startswith('*.'):
                        line+='shExpMatch(host, "{0}") ||\n'.format(domainitem).replace(' ','')
                    else:
                        line+='dnsDomainIs(host, "{0}") ||\n'.format(domainitem).replace(' ','')
                else:
                    if domainitem.startswith('*.'):
                        line+='\tshExpMatch(host, "{0}") ||\n'.format(domainitem).replace(' ','')
                    else:
                        line+='\tdnsDomainIs(host, "{0}") ||\n'.format(domainitem).replace(' ','')
            line=line[:-3]+')\n\t\t\treturn "{0}";\n'.format(params['actions'][params['static'][content]['pac_action']['act_todo']])
            pacline['targetline']=line
            with open (filename,'a+') as file:
                file.write(pacline['targetline'])
                pacline.clear()
                line=''
        elif content.startswith('ipscopes_'):
            for ipver in params['static'][content]:
                if not ipver =='pac_action':
                    for ipitem in params['static'][content][ipver]['networks'].split(','):
                        if not ipitem=="":
                            if line =='' and isfirst==True:
                                line+='if ('
                                isfirst=False
                            elif line =='':
                                line+='else if('
                                try:
                                    str(ipaddress.ip_network(str([ipitem]).replace('[','').replace(']','').replace('\'','')))
                                except:
                                    print("ERROR with network "+ipitem)
                                    raise(SystemExit)
                                line+='isInNet(host, "{0}", "{1}") || isInNet(dnsResolve(host), "{0}", "{1}") ||\n'.format(str(ipaddress.ip_network(str([ipitem]).replace('[','').replace(']','').replace('\'','')).network_address), str(ipaddress.ip_network(str([ipitem]).replace('[','').replace(']','').replace('\'','')).netmask))
                            else:
                                line+='\tisInNet(host, "{0}", "{1}") || isInNet(dnsResolve(host), "{0}", "{1}") ||\n'.format(str(ipaddress.ip_network(str([ipitem]).replace('[','').replace(']','').replace('\'','')).network_address), str(ipaddress.ip_network(str([ipitem]).replace('[','').replace(']','').replace('\'','')).netmask))
            line=line[:-3]+')\n\t\t\treturn "{0}";\n'.format(params['actions'][params['static'][content]['pac_action']['act_todo']])
            pacline['targetline']=line
            with open (filename,'a+') as file:
                file.write(pacline['targetline'])
                pacline.clear()
                line=''
if __name__ == "__main__":
    fun_downloadfeeds()
