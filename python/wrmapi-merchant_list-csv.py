#!/usr/local/bin/python3.9

import sys
import requests
from requests.structures import CaseInsensitiveDict
import json
import math
import csv

tokenUrl        = "https://api.securetrust.com/api/token"
merchantListUrl = "https://api.securetrust.com/wrm/v1/merchants"
csvOutFile      = "merchants.csv"

tokenHeaders = CaseInsensitiveDict()
tokenHeaders["Accept"] = "application/json"
tokenHeaders["Content-Type"] = "application/json"

csvHeader = [
              'Sponsor ID',
              'Unique Merchant ID',
              'MID',
              'Name',
              'DBA',
              'Address 1',
              'Address 2',
              'City',
              'State',
              'Postal Code',
              'Country',
              'Phone',
              'Email',
              'MCC',
              'MCC Segment',
              'MCC Description',
              'Status',
              'Added Via Discovery',
              'In Discovery',
              'URLs'
]

################################
##
## creds.json file format
##
## {
##  "username": "preferreduser",
##  "password": "secretpw"
## }
##
################################

try:
    with open('creds.json',"r") as credsFile:
        credsData = credsFile.read()
except (IOError, EOFError) as ex:
    print ("Can't open credentials file. {}".format(ex.args[-1]))
    raise ex

print ("Authenticating . . . ", end="")
sys.stdout.flush()
tokenResp = requests.post(tokenUrl, headers=tokenHeaders, data=credsData)
tokenResponseJson = tokenResp.json()

if tokenResp.status_code == 200:
    idToken = tokenResponseJson['idToken']
    print ("Authenticated")
    #print ("idToken: ", end="")
    #print (idToken)
else:
    print ("Failed to authenticate.")
    print ("HTTP Response: HTTP ", end="")
    print (str(tokenResp.status_code) + " - ", end="")
    print (tokenResponseJson)
    quit()

# Setup headers
bearerHeaders = CaseInsensitiveDict()
bearerHeaders["Accept"] = "application/json"
bearerHeaders["Content-Type"] = "application/json"
bearerHeaders["Authorization"] = "Bearer " + idToken
#bearerHeaders = {"Authorization": "Bearer " + idToken}

print ("Getting merchant count . . . ", end="")
merchantCountResp = requests.get(merchantListUrl, headers=bearerHeaders)
merchantCountRespJson = merchantCountResp.json()

if merchantCountResp.status_code == 200:
    print ("Done")
    merchantCount = merchantCountRespJson['totalItems']
    print ("Merchant Count: " + str(merchantCount))
else:
        print ("Initial WRM Merchant List query failed.")
        print ("HTTP Response: HTTP ", end="")
        print (str(merchantCountResp.status_code) + " - ", end="")
        print (merchantCountRespJson)
        quit()

listQueries = math.ceil(merchantCount / 100)

print ("Opening output file: " + csvOutFile)
try:
    csvOut = open(csvOutFile,"w")
    csvWriter = csv.writer(csvOut,dialect='excel')
    csvWriter.writerow(csvHeader)
except (IOError, EOFError) as ex:
    print ("Can't open CSV output file. {}".format(ex.args[-1]))
    raise ex

for queryNum in range(1,listQueries+1):
    print ("Sending merchant list request " + str(queryNum) + " of " + str(listQueries) + " . . . ", end="")
    merchantQueryUrl = merchantListUrl + "?size=100&sort-by=name&sort-dir=asc&page=" + str(queryNum)
    merchantQueryResp = requests.get(merchantQueryUrl, headers=bearerHeaders)
    merchantQueryRespJson = merchantQueryResp.json()

    if merchantQueryResp.status_code == 200:
        print ("Done")
        for merchantRecord in merchantQueryRespJson["pageItems"]:
            outputData = []
            outputData.append(merchantRecord["sponsorId"])
            outputData.append(merchantRecord["merchantId"])
            outputData.append(merchantRecord["mid"])
            outputData.append(merchantRecord["name"])
            outputData.append(merchantRecord["dba"])
            outputData.append(merchantRecord["address1"])
            outputData.append(merchantRecord["address2"])
            outputData.append(merchantRecord["city"])
            outputData.append(merchantRecord["state"])
            outputData.append(merchantRecord["postalCode"])
            outputData.append(merchantRecord["country"])
            outputData.append(merchantRecord["phone"])
            outputData.append(merchantRecord["email"])
            outputData.append(merchantRecord["mcc"])
            outputData.append(merchantRecord["mccSegment"])
            outputData.append(merchantRecord["mccDescription"])
            outputData.append(merchantRecord["status"])
            outputData.append(merchantRecord["discovery"]["addedViaDiscovery"])
            outputData.append(merchantRecord["discovery"]["inDiscovery"])
            # Grab list of URLs
            print ("Sending merchant URL list request for merchantId: " + str(merchantRecord["merchantId"]) + " . . . ", end="")
            merchantUrlQueryUrl = merchantListUrl + "/" + str(merchantRecord["merchantId"]) + "/urls"
            merchantUrlQueryResp = requests.get(merchantUrlQueryUrl, headers=bearerHeaders)
            merchantUrlQueryRespJson = merchantUrlQueryResp.json()
        
            if merchantUrlQueryResp.status_code == 200:
                print ("Done")
                merchantUrlData=""
                merchantUrls=""
                for urlRecord in merchantUrlQueryRespJson:
                    merchantUrlData += urlRecord["url"] + ":"
                if(len(merchantUrlData) > 0):
                    merchantUrls = merchantUrlData.rstrip(merchantUrlData[-1])
            else:
                print ("Merchant URL List query failed.")
                print ("HTTP Response: HTTP ", end="")
                print (str(merchantUrlQueryResp.status_code) + " - ", end="")
                print (merchantUrlQueryRespJson)
                quit()
            outputData.append(merchantUrls)
            try:
                csvWriter.writerow(outputData)
            except (IOError, EOFError) as ex:
                print ("Can't write to CSV output file. {}".format(ex.args[-1]))
                raise ex
    else:
        print ("Merchant List query failed.")
        print ("HTTP Response: HTTP ", end="")
        print (str(merchantQueryResp.status_code) + " - ", end="")
        print (merchantQueryRespJson)
        quit()

try:
    print ("Closing output file: " + csvOutFile)
    csvOut.close()
except (IOError, EOFError) as ex:
    print ("Can't close CSV output file. {}".format(ex.args[-1]))
    raise ex
