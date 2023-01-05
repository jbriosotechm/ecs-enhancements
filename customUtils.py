import sys,os
sys.path.append("customLib")
import customLib.Report as Report
import SystemConfig,userConfig
import traceback
import dynamicConfig
from bs4 import BeautifulSoup
import xmltodict
import re
import ApiLib
import json
import time
import ast

from pprint import pprint
debugFlag=True

def reset_config():
    dynamicConfig.responseHeaders    = None
    dynamicConfig.responseStatusCode = None
    dynamicConfig.responseText       = None
    dynamicConfig.restRequestType    = None
    dynamicConfig.currentRequest     = None
    dynamicConfig.currentResponse    = None
    dynamicConfig.currentUrl         = None
    dynamicConfig.currentException   = None
    dynamicConfig.currentHeader      = None
    dynamicConfig.currentContentType = None
    dynamicConfig.requestParameters  = None

def clear_dict(flag):
    if str(flag).upper().startswith("Y"):
        SystemConfig.globalDict={}

    SystemConfig.localRequestDict={}

def getIndexNumber(element):
    # if element is root[0], return index only which is 0 here
    try:
        return str((element.split("[")[1]).split("]")[0]).strip()
    except Exception as e:
        if debugFlag:
            print("Exception:", e)

    return None

def find_element_using_path(root, path):
    # path can be root[0].country.rank
    try:
        root = BeautifulSoup(root, 'xml')
        indexNumber=0
        pathList = path
        if "." in path:
            pathList = path.split(".")

        data = root

        if 'list' not in type(pathList).__name__:
            element=path
            if "[" in element:
                indexNumber = getIndexNumber(element)
                element = element.split("[")[0]
            if indexNumber is None:
                print("Todo : log error and return")
                return
            try:

                data = data.findAll(str(element).encode('ascii','ignore'))
                data = data[int(indexNumber)]
            except Exception as e:
                print("Exception:",e)

        if 'list' in type(pathList).__name__ :
            if len(pathList) == 0:
                return "FieldNotFound"

            for element in pathList:
                indexNumber = 0
                if "[" in element:

                    indexNumber = getIndexNumber(element)
                    element = element.split("[")[0]
                if indexNumber is None:
                    print("Todo : log error and return")
                    return
                data = data.findAll(element)
                data = data[int(indexNumber)]

        return data.text
    except Exception as e:
        print("Exception:",e)

    return "FieldNotFound"

def parseArithmeticExp(arithmericExpression):
    errorCode="Custom404"
    try:
        #{var1}#+#{var2}#+var3-var4
        origExp=arithmericExpression
        arithmericExpression=str(arithmericExpression)
        ctr=0
        maxLimit=10
        arithmericExpression = replacePlaceHolders(arithmericExpression)
        import numexpr
        arithValue=numexpr.evaluate(arithmericExpression).item()
        print("Arith value:",arithValue)
        return arithValue
    except Exception as e:
        print('Exception:',e)
    return errorCode

def replacePlaceHolders(var):
    prefix = SystemConfig.splitterPrefix
    postfix = SystemConfig.splitterPostfix

    if var is None:
        return var

    if prefix not in var and postfix not in var:
        return var

    for key in SystemConfig.globalDict.keys():
        stringToMatch = prefix + key + postfix
        if stringToMatch in var:
            var = var.replace(stringToMatch,str(SystemConfig.globalDict[key]))

    for key in SystemConfig.localRequestDict.keys():
        stringToMatch = prefix + key + postfix
        if stringToMatch in var:
            var = var.replace(stringToMatch,str(SystemConfig.localRequestDict[key]))

    if prefix in var and postfix in var:
        print "Failure: Undefined variable usage in {0}".format(var)
        customWriteTestStep("User-Input error", "Undefined variable used",
                            "Only variables which are defined can be used", "Fail")
        endProcessing()
    return var

def parseHeader(headers):
    if headers is None:
        return None

    dictHeader = {}
    allParams  = []

    headers = replacePlaceHolders(headers)
    headers = headers.strip()

    if "\n" in headers:
        allParams = headers.split("\n")
    else:
        allParams.append(headers)

    for eachParamValuePair in allParams:
        [paramName, paramValue] = eachParamValuePair.split(userConfig.data_splitter, 1)
        dictHeader[paramName]   = paramValue

    if dictHeader is not None:
        dynamicConfig.currentHeader = dictHeader
        if "Content-Type" in dictHeader.keys():
            dynamicConfig.currentContentType = dictHeader["Content-Type"].encode('ascii', 'ignore')
    else:
        if "rest" in dynamicConfig.restRequestType.lower():
            dynamicConfig.currentHeader={}
        else:
            dynamicConfig.currentHeader=""

    return dictHeader

def parametrizeRequest(requestStructure, requestParameters):
    #returns new request with actual parameters

    #parse parameters and replace in the structure(to replace variables(#{}#) in request structures if used)
    requestStructure = replacePlaceHolders(requestStructure)

    if requestParameters is None:
        return requestStructure

    allParams=[]
    requestStructure = requestStructure.encode('ascii', 'ignore')

    if "\n" in requestParameters.strip():
        allParams=requestParameters.split("\n")
    else:
        allParams.append(requestParameters)

    for eachParamValuePair in allParams:
        [paramName, paramValue] = eachParamValuePair.split(userConfig.data_splitter, 1)
        SystemConfig.localRequestDict[paramName]=paramValue
        print(paramValue)
        paramValue = replacePlaceHolders(paramValue)
        if "Y" == SystemConfig.currentisJsonAbsolutePath:
            data = ast.literal_eval(requestStructure)
            tempString = paramName
            if paramValue.startswith("ADD("):
                paramValue = paramValue.replace("ADD(", "").replace(")", "")
                exec(tempString + ".append(" + paramValue + ")")

            elif paramValue.startswith("DEL("):
                paramValue = paramValue.replace("DEL(", "").replace(")", "")
                exec(tempString + ".pop(" + paramValue +" )")

            else:
                print("\n\n\n")
                print("*"*50)
                print("Following is the statement evaluated by python")
                print(tempString + " = " + paramValue)
                exec(tempString + " = " + paramValue)
            requestStructure = str(data).replace("'", '"')
            print("Data is ",data)
            print("Request structure is : ",requestStructure)
        else:
            if requestStructure is not None and "<"+paramName.strip()+">" in requestStructure:
                #handle xml replacement
                regexString="<"+paramName+">"+".*"+r'</'+paramName+">"
                newString="<"+paramName+">"+paramValue+r'</'+paramName+">"
            else:
                regexString='"'+paramName+'" *:.*"(.*)"'
                result = re.search(regexString, requestStructure)

                if result is not None:
                    stringToReplace=result.group(1)
                    oldString='"'+paramName+'"'+":"+'"'+stringToReplace+'"'
                    if stringToReplace in paramName :
                        string=userConfig.data_splitter+'"'+stringToReplace+'"'
                        pmv=userConfig.data_splitter+'"'+paramValue+'"'
                        if stringToReplace=='':
                            newString=oldString.replace(oldString,'"'+paramName+'":'+'"'+paramValue+'"',1)
                        else:
                            newString=oldString.replace(string,pmv,1)
                    else:
                        if stringToReplace=='':
                            newString=oldString.replace(oldString,'"'+paramName+'":'+'"'+paramValue+'"',1)
                        else:
                            newString=oldString.replace(stringToReplace,paramValue,1)
                else: #result is None
                    regexString='"'+paramName+'" *:(.*)'
                    result = re.search(regexString, requestStructure)

                    if result is not None:
                        stringToReplace=result.group(1)
                        oldString='"'+paramName+'"'+userConfig.data_splitter+stringToReplace
                        if stringToReplace in paramName :
                           string=userConfig.data_splitter+'"'+stringToReplace+'"'
                           pmv=userConfig.data_splitter+'"'+paramValue+'"'
                           if stringToReplace=='':
                              newString=oldString.replace(oldString,'"'+paramName+'":'+'"'+paramValue+'"',1)
                           else:
                              newString=oldString.replace(string,pmv,1)
                        else:
                            if stringToReplace=='':
                               newString=oldString.replace(oldString,'"'+paramName+'":'+'"'+paramValue+'"',1)
                            else:
                               newString=oldString.replace(stringToReplace,paramValue,1)
                    else: #if result is None
                        print "No matching substitution for param : {0}".format(paramName)
                        customWriteTestStep("Excel Error: No matching substitution for param : {0}".format(paramName),"NA","NA","Failed")
                        return
            if regexString.endswith(","):
                newString=newString+","
            requestStructure=re.sub(regexString,newString,requestStructure)
    return requestStructure

def set_dynamic_request(requestStructure):
    if requestStructure is not None:
        dynamicConfig.currentRequest = requestStructure
    else:
        if "rest" in dynamicConfig.restRequestType.lower():
            dynamicConfig.currentRequest={}
        else:
            dynamicConfig.currentRequest=""

def get_request_parameter(requestStructure, key):
    requestStructure = json.loads(requestStructure)
    return requestStructure[key]

def add_request_parameters(value):
    if dynamicConfig.requestParameters is None:
        dynamicConfig.requestParameters = value
    else:
        dynamicConfig.requestParameters += "\n" + value

def endProcessing():
    Report.GeneratePDFReport()
    os._exit(-1)

def customWriteTestStep(TestStepDesc,ExpectedResult, ActualResult,StepStatus,screenshot_path=None):
    if "fail" in StepStatus.lower():
        dynamicConfig.testCaseHasFailed=True
        StepStatus="Failed"
    elif "pass" in StepStatus.lower():
        StepStatus="Passed"

    if str(dynamicConfig.testStepNo) != str(dynamicConfig.current_test_step_no):
        dynamicConfig.current_test_step_no = dynamicConfig.testStepNo
        TestStepDesc = "[Test Step #{0}] ".format(dynamicConfig.testStepNo) + TestStepDesc

    Report.WriteTestStep(TestStepDesc, ExpectedResult, ActualResult, StepStatus,screenshot_path)

def getVolumeByWalletName(root, walletName):
    #xmlWallet_WalletName
    volume=None
    # path can be root[0].country.rank
    try:
        root = BeautifulSoup(root, 'xml')
        walletList = root.findAll('WalletList')

        for eachWallet in walletList:
            wallet = eachWallet.find('Wallet')
            if wallet.text==walletName:
                volume = eachWallet.find('VolumeRemaining')
                break
        if volume is not None:
            volume=volume.text
            customWriteTestStep('Capture VolumeRemaining for Wallet : {0}'.format(walletName),
                                "Capture Volume Remaining",
                                "Volume Remaining : {0}".format(volume), "Pass")
            return volume

        customWriteTestStep('Capture VolumeRemaining for Wallet : {0}'.format(walletName),
                            "Capture Volume Remaining",
                            "Unable to capture Volume Remaining", "Fail")
        return "-1"
    except Exception as e:
        print("Exception:",e)
    return "FieldNotFound"

def print_request_details(is_failing):
    if 'test_case_prefix' in SystemConfig.localRequestDict.keys():
        prefix = SystemConfig.localRequestDict['test_case_prefix']
    else:
        prefix = ""

    if 'test_case_postfix' in SystemConfig.localRequestDict.keys():
        postfix = SystemConfig.localRequestDict['test_case_postfix']
    else:
        postfix = ""

    if is_failing:
        customWriteTestStep("{0} Request via {1} {2}".format(prefix, dynamicConfig.apiToTrigger, postfix),
                            "Log request details",
                            "EndPoint : {0}\n\nHeader: {1}\n\nBody : {2}".format(dynamicConfig.currentUrl,
                            dynamicConfig.currentHeader, dynamicConfig.currentRequest),"Pass")
    else:
        customWriteTestStep("{0} Request via {1} {2}".format(prefix, dynamicConfig.apiToTrigger, postfix),
                            "Log request details",
                            "Request sent successfully.\n\nDetails of Request: {0}".format(dynamicConfig.request_file_name),
                            "Pass")

def logResponseTime():
    if dynamicConfig.responseTime is not None:
        customWriteTestStep("Log Response Time", "Response Time : {:.2f} seconds".format(dynamicConfig.responseTime),
                            "Computed response time : {:.2f} seconds".format(dynamicConfig.responseTime), "Pass")
        return
    customWriteTestStep("Log Response Time","Should compute Response time","Unable to compute Response time","Fail")

def print_response_details(is_failing, custom_message=None):
    if custom_message == None:
        custom_message = "Response received for {0}".format(dynamicConfig.apiToTrigger)

    if not is_failing:
        customWriteTestStep(custom_message, "Log Response",
                            "Status Code : {0}\nResponse received with expected Status Code.\n\nDetails of Response: {1}".format(dynamicConfig.responseStatusCode,
                            dynamicConfig.response_file_name),"Pass")
    else:
        if dynamicConfig.currentResponse is None:
            customWriteTestStep(custom_message, "Log Response",
                                "No Response received from server within user-configured timeout : {0} seconds".format(userConfig.timeoutInSeconds),"Fail")
        else:
            customWriteTestStep(custom_message, "Log Response",
                                "Expected Status Code : {0}\nActual Status Code : {1}\n\nHeaders: {2}\n\nBody: {3}".format(SystemConfig.expectedStatusCode,
                                dynamicConfig.responseStatusCode, dynamicConfig.responseHeaders,
                                dynamicConfig.responseText),"Fail")

def triggerSoapRequest(will_create_file=True):
    ApiLib.triggerSoapRequest(will_create_file)
    dynamicConfig.currentResponseInJson = convert_text_to_dict(dynamicConfig.responseText)

def triggerRestRequest(will_create_file=True):
    ApiLib.triggerRestRequest(will_create_file)

def convert_text_to_dict(text):
    try:
        text = str(text)
        text = text.replace("soapenv:", "").replace("soap:", "")
        body = xmltodict.parse(text)
        body = body["Envelope"]["Body"]
        next_child = str(body.keys()[0])
        return body[next_child]
    except Exception as e:
        print ("[ERR] Response cannot be converted to dictionary")
    return None

def sleep(duration):
    try:
        print("[User-Command] Will sleep for {0} seconds".format(duration))
        time.sleep(duration)
        customWriteTestStep("Wait before proceeding to next step for {0} seconds".format(duration),
                            "Should wait", "Waited for: {0} seconds".format(duration), "Passed")
    except:
        print("[ERROR] Invalid argument for Sleep command : {0}".format(duration))
        customWriteTestStep("Wait before proceeding to next step for {0} seconds".format(duration),
                            "The argument passed should be an Integer",
                            "The argument passed is Invalid : {0}".format(duration),
                            "Pass")
