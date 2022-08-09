#performs api calls


import requests,os,sys
import dynamicConfig
import traceback
import json
import userConfig, SystemConfig
import time
sys.path.append("customLib")
import customLib.customLogging as customLogging

def formatRequestBody():
    body = dynamicConfig.currentRequest
    return body

def triggerSoapRequest():
    headers = dynamicConfig.currentHeader
    url     = dynamicConfig.currentUrl
    body    = dynamicConfig.currentRequest
    requestType    = dynamicConfig.restRequestType

    dynamicConfig.responseTime=None
    dynamicConfig.responseStatusCode = None
    dynamicConfig.responseHeaders    = None
    dynamicConfig.responseText       = None

    response = None

    try:
        startTime=time.time()
        if str(requestType).startswith("get"):
            response = requests.get(url,data=body,headers=headers,timeout=userConfig.timeoutInSeconds,verify=False)
        else:
            response = requests.post(url,data=body,headers=headers,timeout=userConfig.timeoutInSeconds,verify=False)

        requestContent="URL : {0}\nHeaders : {1}\nBody: {2}".format(url,headers,body)
        customLogging.writeToLog("Req_SOAP_"+str(time.time()),requestContent)

    except Exception,e:
        traceback.print_exc()
        dynamicConfig.currentException=traceback.format_exc()

    dynamicConfig.responseTime=time.time()-startTime
    dynamicConfig.currentResponse=response

    if response is not None:
        dynamicConfig.responseHeaders=response.headers
        dynamicConfig.responseStatusCode=response.status_code
        dynamicConfig.responseText=response.text

    print "\n*************** [ Response ] ***************"
    print "\n\n Headers : {0}".format(dynamicConfig.responseHeaders)
    print "\nStatus Code : {0}".format(dynamicConfig.responseStatusCode)
    print "\nBody : {0}".format(dynamicConfig.responseText)



    responseContent="Status Code : {0}\n\nHeaders : {1}\n\nBody : {2}".format(dynamicConfig.responseStatusCode,dynamicConfig.responseHeaders,dynamicConfig.responseText)
    customLogging.writeToLog("Res_SOAP_"+str(time.time()),responseContent)

def triggerRestRequest():
    headers        = dynamicConfig.currentHeader
    url            = dynamicConfig.currentUrl
    body           = formatRequestBody()
    requestType    = dynamicConfig.restRequestType
    authentication = dynamicConfig.currentAuthentication

    try:
        body=body.encode('utf-8')
        if body.encode('utf-8') == '{}':
            body={}
    except:
        print("Exception converting to unicode")

    print "Request type is : ",requestType
    print "Request headers is : ",headers
    response=None

    files=[

]

    if dynamicConfig.currentRequest is None:
        dynamicConfig.currentRequest = ""

    requestContent = "\nRequest type : {3}\n\nURL : {0}\n\nHeaders : {1}\n\nBody: {2}".format(url,headers,body,requestType)
    customLogging.writeToLog("Req_Rest_"+str(time.time()),requestContent)
    runTimes = 1
    if "RERUN_TIMES" in SystemConfig.localRequestDict.keys():
        runTimes = int(SystemConfig.localRequestDict["RERUN_TIMES"])

    dynamicConfig.responseTime=None
    for i in range(0, runTimes):
        dynamicConfig.responseTime=None
        startTime=time.time()
        try:
            if str(requestType).startswith("post"):
                if str(dynamicConfig.apiToTrigger).lower() in ["createcsvmaplayer"]:
                    data={'options': '{"areas":[{"selection":{"type":"pin","lat":14.554729,"lon":121.0244452,"distance":500}}],"fields":{"accounts":[],"households":[],"facilities-wireline":["Cabinet Name, Serving Cabinet Name","Cabinet Capacity","Distribution Point","Cabinet Latitude, Cabinet Lat","Cabinet Longitude, Cabinet Long","Cabinet Distance in Meters","Distribution Point Latitude, DP Lat","Distribution Point Longitude, DP Long","Cabinet Distribution Point Type, DP Type","Physical location address id","Cabinet Type","Area Name","Region Name","Region 2 Name","Cluster Name","FO Head Name","FO Assigned Name","Approximate Location Address","Building Name","Floor Number","Digital Subscriber Line Access Multiplexer","Technology Type","Plan Based on DP Distance","Port Utilization, DP Utilization and Cabinet Utilization","Network Utilization","Plan based on Network Util","Multi Dwelling Unit","Unutilized Ports","Reserved Ports","Sellable Ports","Barangay Code","Barangay","AB","C1","C2","D","E","Commercial","Retail Micro","Total"],"facilities-wireless":[],"facilities-goldmine":[],"facilities-eg":[],"facilities-wireline - upcoming":[],"facilities-wireless - upcoming":[],"opportunities":[],"globe-stores":[],"subscribers":[],"non-serviceables":[],"predicted-utilization":[],"retailer-mapping":[]},"filters":{"accounts":{},"households":{},"facilities-wireline":{},"facilities-wireless":{},"facilities-goldmine":{},"facilities-eg":{},"facilities-wireline - upcoming":{},"facilities-wireless - upcoming":{},"opportunities":{},"globe-stores":{},"subscribers":{},"non-serviceables":{},"predicted-utilization":{},"retailer-mapping":{}}}',
'file': 'csv'}
                    response = requests.post(url,data=data,headers=headers,timeout=userConfig.timeoutInSeconds,verify=False, auth=authentication,files=files)

                elif str(dynamicConfig.apiToTrigger).lower() in ["createkmzmaplayer"]:
                    data={'options': '{"areas":[{"selection":{"type":"pin","lat":14.554729,"lon":121.0244452,"distance":500}}],"fields":{"accounts":[],"households":[],"facilities-wireline":["Cabinet Name, Serving Cabinet Name","Cabinet Capacity","Distribution Point","Cabinet Latitude, Cabinet Lat","Cabinet Longitude, Cabinet Long","Cabinet Distance in Meters","Distribution Point Latitude, DP Lat","Distribution Point Longitude, DP Long","Cabinet Distribution Point Type, DP Type","Physical location address id","Cabinet Type","Area Name","Region Name","Region 2 Name","Cluster Name","FO Head Name","FO Assigned Name","Approximate Location Address","Building Name","Floor Number","Digital Subscriber Line Access Multiplexer","Technology Type","Plan Based on DP Distance","Port Utilization, DP Utilization and Cabinet Utilization","Network Utilization","Plan based on Network Util","Multi Dwelling Unit","Unutilized Ports","Reserved Ports","Sellable Ports","Barangay Code","Barangay","AB","C1","C2","D","E","Commercial","Retail Micro","Total"],"facilities-wireless":[],"facilities-goldmine":[],"facilities-eg":[],"facilities-wireline - upcoming":[],"facilities-wireless - upcoming":[],"opportunities":[],"globe-stores":[],"subscribers":[],"non-serviceables":[],"predicted-utilization":[],"retailer-mapping":[]},"filters":{"accounts":{},"households":{},"facilities-wireline":{},"facilities-wireless":{},"facilities-goldmine":{},"facilities-eg":{},"facilities-wireline - upcoming":{},"facilities-wireless - upcoming":{},"opportunities":{},"globe-stores":{},"subscribers":{},"non-serviceables":{},"predicted-utilization":{},"retailer-mapping":{}}}',
'file': 'kmz'}
                    response = requests.post(url,data=data,headers=headers,timeout=userConfig.timeoutInSeconds,verify=False, auth=authentication,files=files)

                else:
                    response = requests.post(url,data=body,headers=headers,timeout=userConfig.timeoutInSeconds,verify=False, auth=authentication)

            elif str(requestType).startswith("put"):
                response = requests.put(url,data=body,headers=headers,timeout=userConfig.timeoutInSeconds,verify=False, auth=authentication)
            elif str(requestType).startswith("get"):
                #time.sleep(10)
                response = requests.get(url,data=body,headers=headers,timeout=userConfig.timeoutInSeconds,verify=False, auth=authentication)
            elif str(requestType).startswith("patch"):
                response = requests.patch(url,data=body,headers=headers,timeout=userConfig.timeoutInSeconds,verify=False, auth=authentication)
            elif str(requestType).startswith("delete"):
                response = requests.delete(url,data=body,headers=headers,timeout=userConfig.timeoutInSeconds,verify=False, auth=authentication)
            else:
                response = requests.post(url,data=body,headers=headers,timeout=userConfig.timeoutInSeconds,verify=False, auth=authentication)


        except Exception,e:
            traceback.print_exc()
            dynamicConfig.currentException = traceback.format_exc()

        dynamicConfig.responseTime=time.time()-startTime

    #response=response.decode("utf-8")
    dynamicConfig.currentResponse = response
    responseContent=""
    if response is not None:
        dynamicConfig.responseHeaders    = response.headers
        dynamicConfig.responseStatusCode = response.status_code
        dynamicConfig.responseText       = response.text.encode('ascii', 'ignore')

    print "\n*************** [ Response ] ***************"
    print "\n\n Headers : {0}".format(dynamicConfig.responseHeaders)
    print "\nStatus Code : {0}".format(dynamicConfig.responseStatusCode)

    if dynamicConfig.responseHeaders is not None:
        if "application/pdf" not in str(dynamicConfig.responseHeaders):
            print "\nBody : {0}".format(dynamicConfig.responseText)
            responseContent="Status Code : {0}\n\nHeaders : {1}\n\nBody : {2}".format(dynamicConfig.responseStatusCode,dynamicConfig.responseHeaders,dynamicConfig.responseText)
        else:
            print "\nBody : {0}".format(dynamicConfig.responseText)
            responseContent="Status Code : {0}\n\nHeaders : {1}".format(dynamicConfig.responseStatusCode,dynamicConfig.responseHeaders)

            pdfLocation = "response.pdf"
            if "PDF_LOCATION" in SystemConfig.localRequestDict.keys():
                pdfLocation = SystemConfig.localRequestDict["PDF_LOCATION"]
            with open(pdfLocation, 'wb') as f:
                f.write(dynamicConfig.currentResponse.content)
    responseContent+="\n\nResponse time : {0} seconds\nNote : Response time = Server Response time + Network Latency".format(dynamicConfig.responseTime)
    customLogging.writeToLog("Res_Rest" + str(time.time()),responseContent)
