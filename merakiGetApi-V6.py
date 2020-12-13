#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
import json
import pandas
import sqlite3
import time


import sys
# to display the completion
def printProgressBar(i,max):
    n_bar =10 #size of progress bar
    j= i/max
    sys.stdout.write('\r')
    sys.stdout.write(f"[{'=' * int(n_bar * j):{n_bar}s}] {int(100 * j)}% Completion")
    sys.stdout.flush()
    return i




global api_key
organizationIds = []
networkIds = []
global conn #var for databse

#gets the api response
def grabData(path):
    
    payload = None
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": api_key
    }

    url = 'https://api.meraki.com/api/v0' + path
    response = {'path':None,'info':None}
    try:
        response['info'] = requests.get(url , headers=headers, data = payload)
    
    except:# if response time error wait for a few secs
        time.sleep(2)
        response['info'] = requests.get(url , headers=headers, data = payload)
    
    response['path'] = path
    
    return response



#gets the json data from the response sent by grabData func
def grabVar(data):
    
    response = data['info']
    
    if( str(response) != '<Response [200]>'  #if response none other then 200 break
        if(checkApiValidity):
            print('error:possible invalid input key')
        return []
    
    response = response.text.encode('utf8')
    response = json.loads(response)
    
    return response




#gets the data response grabData and stores to databse
def toDatabase(data):
        
        path = data['path']
        response = data['info']
        
        if( str(response) != '<Response [200]>' ):
            return
        
        response = response.text.encode('utf8')
        #if null data returned
        if(response == b'[]'): #if empty data from the response break
            return
        
        try:#standard methode to convert the json to table
            df = pandas.read_json(response)
            
        except:#if methode 1 fails
            response = json.loads(response)
            
            try:
                df = pandas.DataFrame.from_dict(response, orient='index')
                
            except:#if methode 2 fails
                col = []
                for key in response.keys():
                    col.append(key)
                df = pandas.DataFrame(list(response.items()),col)
                del df[0]
            
            df = df.transpose() #rearranges the table
            #df.reset_index(level=0, inplace=True)
            
        df = df.astype('str') #casts the df to string for ease of db
        top =  df.columns.tolist()
        if(len(top) == 0 ): return  
        #generates the cmnnd to create the table
        cmd = 'CREATE TABLE IF NOT EXISTS {NAME} ('
        for i in range(1,(len(top)+1)):
            cmd += 'COL' + str(i) + ' LONGTEXT,'

        cmd = cmd[:-1] + ')'
        tableName = path[1:].replace('/','_').replace('-','_')
        cmd = cmd.format(NAME = tableName)
        
        c = conn.cursor()
        
        c.execute(cmd)
        
            
            
        
        conn.commit()
        df.to_sql(tableName, conn, if_exists='replace', index = False)
        


def getPreReqVar():
    
    
    print('status: fetching pre requisite variables...' )
    
    getorganizationIds = grabVar(grabData('/organizations'))
    for getorganizationId in getorganizationIds:
        organizationIds.append(getorganizationId['id'])
        
        getnetworkIds = grabVar(grabData('/organizations/{organizationId}/networks'.format(organizationId  = organizationIds[-1])))
        for getnetworkId in getnetworkIds:
                networkIds.append(getnetworkId['id'])
                

    print('status: operation completed')

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

class  ORG:
    
    total = 0 #for status bar
    i = 0
    
    
    
    
    
    def __init__(self):
            print('status: In operation ORG commands\nfetching variables...\nfetching data...\nstoring in Datbase...\n')
            self.total = len(networkIds) + len(organizationIds) 
            self.i = printProgressBar(self.i,self.total) # to display the status
            
    def organizationCmds(self):
        
    
        urls = [ '/organizations/{organizationId}',
        '/organizations/{organizationId}/deviceStatuses',
        '/organizations/{organizationId}/inventory',
        '/organizations/{organizationId}/licenseState',
        '/organizations/{organizationId}/thirdPartyVPNPeers',
        '/organizations/{organizationId}/uplinksLossAndLatency',
        '/organizations/{organizationId}/apiRequests',
        '/organizations/{organizationId}/apiRequests/overview',
        '/organizations/{organizationId}/admins',
        '/organizations/{organizationId}/configurationChanges',
        '/organizations/{organizationId}/configTemplates',
        '/organizations/{organizationId}/webhookLogs',
        '/organizations/{organizationId}/openapiSpec',
        '/organizations/{organizationId}/snmp',
        #added from here
        '/organizations/{organizationId}/actionBatches',
        '/organizations/{organizationId}/brandingPolicies',
        '/organizations/{organizationId}/samlRoles',
        '/organizations/{organizationId}/brandingPolicies/priorities',
        '/organizations/{organizationId}/devices',
        '/organizations/{organizationId}/securityEvents',
        '/organizations/{organizationId}/licenses',
        '/organizations/{organizationId}/insight/monitoredMediaServers'] 

        for organizationId in organizationIds:
            for url in urls:
                toDatabase(grabData(url.format(organizationId = organizationId)))#for each url and for each org id
                
            self.i = printProgressBar(self.i+1,self.total)
        
        

        
    
    
    
    
    def networkCmds(self):
        
        
        urls = [ '/networks/{networkId}/alertSettings',
        '/networks/{networkId}/connectivityMonitoringDestinations',
        '/networks/{networkId}/contentFiltering/categories',
        '/networks/{networkId}/contentFiltering',
        '/networks/{networkId}/events',
        '/networks/{networkId}/events/eventTypes',
        '/networks/{networkId}/netflowSettings',
        '/networks/{networkId}/snmpSettings',
        '/networks/{networkId}/splashLoginAttempts',
        '/networks/{networkId}/syslogServers',
        '/networks/{networkId}/trafficAnalysisSettings',
        '/networks/{networkId}/uplinkSettings', 
        '/networks/{networkId}/pii/piiKeys', #added from here
        '/networks/{networkId}/pii/requests',
        '/networks/{networkId}/pii/smDevicesForKey',
        '/networks/{networkId}/pii/smOwnersForKey',
        '/networks/{networkId}/securityEvents',
        '/networks/{networkId}/groupPolicies',
        '/networks/{networkId}/merakiAuthUsers',
        '/networks/{networkId}/sm/targetGroups',
        '/networks/{networkId}/trafficShaping',
        '/networks/{networkId}/trafficShaping/applicationCategories',
        '/networks/{networkId}/trafficShaping/dscpTaggingOptions',
        '/networks/{networkId}/vlans',
        '/networks/{networkId}/vlansEnabledState',
        '/networks/{networkId}/sm/targetGroups',
        '/networks/{networkId}/sm/devices', # sm commands here
        '/networks/{networkId}/sm/profiles',
        '/networks/{networkId}/sm/users']


        for networkId in networkIds:
            
            for url in urls:
                toDatabase(grabData(url.format(networkId = networkId))) #for each url and for each net id


            data = grabData('/networks/{networkId}/devices'.format(networkId = networkId))
            toDatabase(data)
            serials = grabVar(data)
            for serial in serials: #loopong through for all serials
                toDatabase(grabData('/networks/{networkId}/devices/{serial}/lldp_cdp'.format(networkId = networkId,serial = serial['serial'])))
                toDatabase(grabData('/networks/{networkId}/devices/{serial}/lossAndLatencyHistory'.format(networkId = networkId,serial = serial['serial'])))
                toDatabase(grabData('/networks/{networkId}/devices/{serial}/performance'.format(networkId = networkId,serial = serial['serial'])))
                toDatabase(grabData('/networks/{networkId}/devices/{serial}/uplink'.format(networkId = networkId,serial = serial['serial'])))
        #Management interface settings
                toDatabase(grabData('/networks/{networkId}/devices/{serial}/managementInterfaceSettings '.format(networkId = networkId,serial = serial['serial'])))

                toDatabase(grabData('/devices/{serial}/clients'.format(serial = serial['serial'])))



            data = grabData('/networks/{networkId}/clients'.format(networkId = networkId))
            toDatabase(data)
            clientIds = grabVar(data)
            for clientId in clientIds: #looping through for all client ids
                toDatabase(grabData('/networks/{networkId}/clients/{clientId}/events'.format(networkId = networkId,clientId = clientId['id'])))
                toDatabase(grabData('/networks/{networkId}/clients/{clientId}/latencyHistory'.format(networkId = networkId,clientId = clientId['id'])))
                toDatabase(grabData('/networks/{networkId}/clients/{clientId}/latencyHistory'.format(networkId = networkId,clientId = clientId['id'])))
                toDatabase(grabData('/networks/{networkId}/clients/{clientId}/splashAuthorizationStatus'.format(networkId = networkId,clientId = clientId['id'])))
                toDatabase(grabData('/networks/{networkId}/clients/{clientId}/trafficHistory'.format(networkId = networkId,clientId = clientId['id'])))
                toDatabase(grabData('/networks/{networkId}/clients/{clientId}/usageHistory'.format(networkId = networkId,clientId = clientId['id'])))

        #Security events Get
                toDatabase(grabData('/networks/{networkId}/clients/{clientId}/securityEvents'.format(networkId = networkId,clientId = clientId['id'])))


            data = grabData('/networks/{networkId}/httpServers'.format(networkId = networkId)) 
            toDatabase(data)
            ids = grabVar(data)
            for id in ids: #loopong through for all ids
                toDatabase(grabData('/networks/{networkId}/httpServers/webhookTests/{id}'.format(networkId = networkId,id = id['id'])))

                  

            serials = grabVar(grabData('/networks/{networkId}/devices'.format(networkId = networkId)))
            for serial in serials:
                numbers = grabVar(grabData('/devices/{serial}/switchPorts'.format(serial = serial['serial'])))
                for number in numbers:
                    toDatabase(grabData('/networks/{networkId}/ssids/{number}/trafficShaping'.format(networkId = networkId,number = number['number'])))
            
            
            
        

            #Sm Get
            #/networks/{networkId}/sm/bypassActivationLockAttempts/{attemptId}
            #/networks/{networkId}/sm/devices
            #/networks/{networkId}/sm/profiles
            #/networks/{networkId}/sm/user/{userId}/deviceProfiles
            #/networks/{networkId}/sm/user/{userId}/softwares
            #/networks/{networkId}/sm/users
            #/networks/{networkId}/sm/{deviceId}/cellularUsageHistory
            #/networks/{networkId}/sm/{deviceId}/certs
            #/networks/{networkId}/sm/{deviceId}/deviceProfiles
            #/networks/{networkId}/sm/{deviceId}/networkAdapters
            #/networks/{networkId}/sm/{deviceId}/restrictions
            #/networks/{networkId}/sm/{deviceId}/securityCenters
            #/networks/{networkId}/sm/{deviceId}/softwares
            #/networks/{networkId}/sm/{deviceId}/wlanLists
            #/networks/{network_id}/sm/{id}/connectivity
            #/networks/{network_id}/sm/{id}/desktopLogs
            #/networks/{network_id}/sm/{id}/deviceCommandLogs
            #/networks/{network_id}/sm/{id}/performanceHistory


            self.i = printProgressBar(self.i+1,self.total)
                               
        
    def __del__(self): 
        print('\nstatus: operation completed')
        
        
        
        
        
        
        
        
        

class MG:
    
    
    total = 0
    i = 0
    
    
    def __init__(self):
            print('status: In operation MG commands\nfetching variables...\nfetching data...\nstoring in Datbase...\n')
            self.total = len(networkIds) # to display the status
            self.i = printProgressBar(self.i,self.total)
                
    def organizationCmds(self):
        #none
        return
    
    
    def networkCmds(self):

        urls = [' /networks/{networkId}/cellularGateway/settings/dhcp',
        '/networks/{networkId}/cellularGateway/settings/connectivityMonitoringDestinations',
        '/networks/{networkId}/cellularGateway/settings/subnetPool',
        '/networks/{networkId}/cellularGateway/settings/uplink',
        '/networks/{networkId}/uplinkSettings',
        #start from here
        '/networks/{networkId}/vlans',
        '/networks/{networkId}/vlansEnabledState']
        
        
        for networkId in networkIds:
            
            for url in urls:
                toDatabase(grabData(url.format(networkId = networkId)))
                
            serials = grabVar(grabData('/networks/{networkId}/devices'.format(networkId = networkId)))
            for serial in serials: #loopong through for all serials
        #MG LAN settings Get
                toDatabase(grabData('/devices/{serial}/cellularGateway/settings'.format(serial = serial['serial'])))
        #MG port forwarding rules Get
                toDatabase(grabData('/devices/{serial}/cellularGateway/settings/portForwardingRules'.format(serial = serial['serial'])))
                
        
        
            self.i = printProgressBar(self.i+1,self.total)
        
        
                
    def __del__(self): 
        print('\nstatus: operation completed')
        
        
        
        
                
            
            
            


class MS:
    
    
    total = 0 #for status bar
    i = 0
    
    
    def __init__(self):
            print('status: In operation MS commands\nfetching variables...\nfetching data...\nstoring in Datbase...\n')
            self.total = len(networkIds) + len(organizationIds)
            self.i = printProgressBar(self.i,self.total) # to display the status
    
    def networkCmds(self):

        urls = ['/networks/{networkId}/switch/settings',
        '/networks/{networkId}/switch/settings/dhcpServerPolicy',
        '/networks/{networkId}/switch/settings/dscpToCosMappings',
        '/networks/{networkId}/switch/settings/mtu',
        '/networks/{networkId}/switch/settings/multicast',
        '/networks/{networkId}/switch/settings/qosRules/order',
        '/networks/{networkId}/switch/settings/qosRules',
        '/networks/{networkId}/switch/settings/stormControl',
        '/networks/{networkId}/switch/settings/stp',
        '/networks/{networkId}/switchStacks',
        '/networks/{networkId}/uplinkSettings',
        '/networks/{networkId}/vlans',
        '/networks/{networkId}/vlansEnabledState',
        '/networks/{networkId}',
        '/networks/{networkId}/accessPolicies',
        '/networks/{networkId}/airMarshal',
        '/networks/{networkId}/siteToSiteVpn',
        '/networks/{networkId}/traffic',
        '/networks/{networkId}/switch/linkAggregations',
        '/networks/{networkId}/switch/accessControlLists',
        '/networks/{networkId}/switch/portSchedules']
    
    
        for networkId in networkIds:
            for url in urls:
                toDatabase(grabData(url.format(networkId = networkId)))
            
                
            serials = grabVar(grabData('/networks/{networkId}/devices'.format(networkId = networkId)))
            
            for serial in serials: #loopong through for all serials
                toDatabase(grabData('/devices/{serial}/switchPortStatuses'.format(serial = serial['serial'])))
                toDatabase(grabData('/devices/{serial}/switchPortStatuses/packets'.format(serial = serial['serial'])))
                toDatabase(grabData('/devices/{serial}/switchPorts'.format(serial = serial['serial'])))
     

            self.i = printProgressBar(self.i+1,self.total)




    def organizationCmds(self):
        
        for organizationId in organizationIds:
            toDatabase(grabData('/organizations/{organizationId}/networks'.format(organizationId = organizationId)))

        
            configTemplateIds = grabVar(grabData('/organizations/{organizationId}/configTemplates'.format(organizationId = organizationId)))
            
            for configTemplateId in configTemplateIds:
                toDatabase(grabData('/organizations/{organizationId}/configTemplates/{configTemplateId}/switchProfiles'.format(organizationId = organizationId,configTemplateId = configTemplateId['id'])))


            self.i = printProgressBar(self.i+1,self.total)

    
    def __del__(self): 
        print('\nstatus: operation completed')
        
        
        
        
        
        
        

class MR:
    
    total = 0
    i = 0
    
    
    
    def __init__(self):
            
            print('status: In operation MR commands\nfetching variables...\nfetching data...\nstoring in Datbase...\n')
            self.total = len(networkIds)
            self.i = printProgressBar(self.i,self.total) # to display the status
            
    def networkCmds(self):
        
        
        #Floorplans Get
        for networkId in networkIds:
            
            data = grabData('/networks/{networkId}/floorPlans'.format(networkId = networkId))
            toDatabase(data)
            floorPlanIds = grabVar(data)
            for floorPlanId in floorPlanIds: #looping for each floorplan id
                toDatabase(grabData('/networks/{networkId}/floorPlans/{floorPlanId}'.format(networkId = networkId,floorPlanId = floorPlanId['floorPlanId'])))
        
        
            serials = grabVar(grabData('/networks/{networkId}/devices'.format(networkId = networkId)))
            for serial in serials: #looping through for all serials
                numbers = grabVar(grabData('/devices/{serial}/switchPorts'.format(serial = serial['serial'])))
                for number in numbers:
                    toDatabase(grabData('/networks/{networkId}/ssids/{number}/l3FirewallRules'.format(networkId = networkId,number = number['number'])))
            
            
            self.i = printProgressBar(self.i+1,self.total)
            
        

    
    
    def organizationCmds(self):
        #none
        return

        
        
    def __del__(self): 
        print('\nstatus: operation completed')
        
        
        
        
        
        

class MV:
    
    
    total = 0
    i = 0
    
    
    def __init__(self):
            print('status: In operation MV commands\nfetching variables...\nfetching data...\nstoring in Datbase...\n')
            self.total = len(networkIds)
            self.i = printProgressBar(self.i,self.total) # to display the status
    
    def networkCmds(self):
        
        urls = ['/networks/{networkId}/camera/schedule',
                '/networks/{networkId}/camera/qualityRetentionProfiles']
        
        for networkId in networkIds: #for each url and for each net id
            
            for url in urls:
                toDatabase(grabData(url.format(networkId = networkId)))
                
                serials = grabVar(grabData('/networks/{networkId}/devices'.format(networkId = networkId)))
                for serial in serials: #loopong through for all serials
                    
            #Cameras Get
                    toDatabase(grabData('/networks/{networkId}/cameras/{serial}/videoLink'.format(networkId = networkId,serial = serial['serial'])))
                    toDatabase(grabData('/devices/{serial}/camera/qualityAndRetentionSettings'.format(serial = serial['serial'])))
                    toDatabase(grabData('/devices/{serial}/camera/video/settings'.format(serial = serial['serial'])))
            #MV Sense Get
                    toDatabase(grabData('/devices/{serial}/camera/analytics/live'.format(serial = serial['serial'])))
                    toDatabase(grabData('/devices/{serial}/camera/analytics/overview'.format(serial = serial['serial'])))
                    toDatabase(grabData('/devices/{serial}/camera/analytics/recent'.format(serial = serial['serial'])))

                    data= grabData('/devices/{serial}/camera/analytics/zones'.format(serial = serial['serial']))
                    toDatabase(data)
                    zones = grabVar(data)
                    for zone in zones: #looping for each zone id
                        toDatabase(grabData('/devices/{serial}/camera/analytics/zones/{zoneId}/history'.format(serial = serial['serial'], zoneId = zone['zoneId'])))

            self.i = printProgressBar(self.i+1,self.total)
            
    
    def organizationCmds(self):
        #none
        return
    
   

    def __del__(self): 
        print('\nstatus: operation completed')    
        
        
        
        
        
    

class MX:
    
    i = 0
    total = 0
    
    
    def __init__(self):
        print('status: In operation MX commands\nfetching variables...\nfetching data...\nstoring in Datbase...\n')
        self.total = len(networkIds) + len(organizationIds)
        self.i = printProgressBar(self.i,self.total) # to display the status
    
    
    
    def organizationCmds(self):
        
        for organizationId in organizationIds: #for each url and for each org id
            toDatabase(grabData('/organizations/{organizationId}/security/intrusionSettings'.format(organizationId = organizationId)))
            toDatabase(grabData('/organizations/{organizationId}/vpnFirewallRules'.format(organizationId = organizationId)))
    
            self.i = printProgressBar(self.i+1,self.total)
        
    def networkCmds(self):
        
        
        
        urls = ['networks/{networkId}/security/intrusionSettings',
        '/networks/{networkId}/oneToOneNatRules',
        '/networks/{networkId}/oneToManyNatRules',
        '/networks/{networkId}/l3FirewallRules',
        '/networks/{networkId}/l7FirewallRules/applicationCategories',
        '/networks/{networkId}/l7FirewallRules',
        '/networks/{networkId}/cellularFirewallRules'
        '/networks/{networkId}/appliance/firewall/inboundFirewallRules',
        '/networks/{networkId}/portForwardingRules',
        '/networks/{networkId}/warmSpareSettings',
        '/networks/{networkId}/security/malwareSettings',
        '/networks/{networkId}/uplinkSettings' 
        #strat from here
        '/networks/{networkId}/firewalledServices',
        '/networks/{networkId}/vlans',
        '/networks/{networkId}/vlansEnabledState', 
        '/networks/{networkId}/appliancePorts',
        '/networks/{networkId}/staticRoutes']


        for networkId in networkIds:
            for url in urls: #for each url and for each net id
                toDatabase(grabData(url.format(networkId = networkId)))
            
            self.i = printProgressBar(self.i+1,self.total)

    



    def __del__(self): 
        print('\nstatus: operation completed')
        
        
        
        
     
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

if __name__ == "__main__":
    
    checkApiValidity = True #variable to check the validity of api key
    api_key = input('input the API key: ')
    getPreReqVar()
    checkApiValidity = False
    
    filename =  input('input the file name for the Database file to create or overwrite: ')
    
    conn = sqlite3.connect(filename + '.db') # build a connection to the database
    
    while(True):
        
        print('\n\n1.MG\n2.MR\n3.MS\n4.MV\n5.MX\n6.ORG\n7.Exit\n\n')
        while(True):
            x = input('select a number ')
            try:
                x = int(x)
                break
            except:
                print('invalid output!')
                continue
        
        if(x==1):
            obj = MG()
        elif(x==2):
            obj = MR()
        elif(x==3):
            obj = MS()
        elif(x==4):
            obj = MV()
        elif(x==5):
            obj = MX()
        elif(x==6):
            obj = ORG()
        elif(x==7):
            break
        else:
            continue
        
        obj.networkCmds() #for all network commands store the data to db
        obj.organizationCmds() #for all organization commands store the data to db
        
        
        del obj #del all dynamically allocated data before strarting a new one
        
    conn.close()

