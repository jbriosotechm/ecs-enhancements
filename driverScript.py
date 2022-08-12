#pending development :

#Timestamp keyword check
#JS Fetch

import os, sys
sys.path.append(".")
sys.path.append("customLib")
import keywordHandling
from keywordHandling import storeUserDefinedVariables
import openpyxl
import logging, traceback
import SystemConfig,userConfig
import time
import customLib.Report as Report
import customLib.Config as Config
import ApiLib
import excel_helper as eh
import dynamicConfig
import re
import random
import datetime
import json
import urllib
import string
import ast
import customUtils
from customUtils import customWriteTestStep,endProcessing, replacePlaceHolders, getIndexNumber, find_element_using_path,parseArithmeticExp, convert_text_to_dict
from commonLib import *

def setColumnNumbersForFileValidations():
    eh.read_sheet("Structures", SystemConfig.lastColumnInSheetStructures)
    SystemConfig.col_ApiName = eh.get_column_number_of_string(SystemConfig.field_apiName)
    SystemConfig.col_API_Structure = eh.get_column_number_of_string(SystemConfig.field_API_Structure)
    SystemConfig.col_EndPoint = eh.get_column_number_of_string(SystemConfig.field_EndPoint)
    SystemConfig.col_Method = eh.get_column_number_of_string(SystemConfig.field_Method)
    SystemConfig.col_Headers = eh.get_column_number_of_string(SystemConfig.field_Headers)
    SystemConfig.col_Authentication = eh.get_column_number_of_string(SystemConfig.field_Authentication)

    eh.read_sheet("TCs", SystemConfig.lastColumnInSheetTCs)
    SystemConfig.col_API_to_trigger = eh.get_column_number_of_string(SystemConfig.field_API_to_trigger)
    SystemConfig.col_Automation_Reference = eh.get_column_number_of_string(SystemConfig.field_Automation_Reference)
    SystemConfig.col_Status_Code = eh.get_column_number_of_string(SystemConfig.field_Status_Code)
    SystemConfig.col_HeadersToValidate = eh.get_column_number_of_string(SystemConfig.field_HeadersToValidate)
    SystemConfig.col_Assignments = eh.get_column_number_of_string(SystemConfig.field_Assignments)
    SystemConfig.col_TestCaseNo = eh.get_column_number_of_string(SystemConfig.field_TestCaseNo)
    SystemConfig.col_TestCaseName = eh.get_column_number_of_string(SystemConfig.field_TestCaseName)
    SystemConfig.col_ResponseParametersToCapture = eh.get_column_number_of_string(SystemConfig.field_ResponseParametersToCapture)
    SystemConfig.col_Parameters = eh.get_column_number_of_string(SystemConfig.field_Parameters)
    SystemConfig.col_GlobalParametersToStore = eh.get_column_number_of_string(SystemConfig.field_GlobalParametersToStore)
    SystemConfig.col_ClearGlobalParameters = eh.get_column_number_of_string(SystemConfig.field_ClearGlobalParameters)
    SystemConfig.col_isJsonAbsolutePath = eh.get_column_number_of_string(SystemConfig.field_isJsonAbsolutePath)
    SystemConfig.col_preCommands = eh.get_column_number_of_string(SystemConfig.field_preCommands)
    SystemConfig.col_postCommands = eh.get_column_number_of_string(SystemConfig.field_postCommands)

def customWriteTestCase(TestScenarioSrNo,TestCaseDesc):
    dynamicConfig.testCaseHasFailed=False
    Report.WriteTestCase(TestScenarioSrNo, TestCaseDesc)

def customEvaluateTestCase():
    dynamicConfig.testCaseHasFailed=False
    Report.evaluateIfTestCaseIsPassOrFail()

def parseHeader(requestParameters):
    if requestParameters is None:
        return None

    dictHeader = {}
    allParams  = []

    requestParameters = replacePlaceHolders(requestParameters)
    requestParameters = requestParameters.strip()

    if "\n" in requestParameters:
        allParams = requestParameters.split("\n")
    else:
        allParams.append(requestParameters)

    for eachParamValuePair in allParams:
        [paramName, paramValue] = eachParamValuePair.split(userConfig.data_splitter, 1)
        dictHeader[paramName]   = paramValue
    return dictHeader

def logResponseTime():
    if dynamicConfig.responseTime is not None:
        customWriteTestStep("Log Response Time","Response Time : {:.2f} seconds".format(dynamicConfig.responseTime),"Computed response time : {:.2f} seconds".format(dynamicConfig.responseTime),"Pass")
        return

    customWriteTestStep("Log Response Time","Should compute Response time","Unable to compute Response time","Fail")

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
                    print("[PK] stringToReplace" + stringToReplace)
                    print("[PK] oldString" + oldString)
                    print("[PK] paramName" + paramName)
                    if stringToReplace in paramName :
                        string=userConfig.data_splitter+'"'+stringToReplace+'"'
                        print("[PK] string" + string)
                        pmv=userConfig.data_splitter+'"'+paramValue+'"'
                        print("[PK] pmv" + pmv)
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

def parseValue(fieldToFind,responseChunk):
    #if response chunk is a dict, {"result":{"accessToken":"eyJraWQiOiJabkc5"}}
    #takes in a dictionary and tries to match the keys to the desired key
    valueParsed=None
    valueFound=False

    if type(responseChunk) is dict:
        for key in responseChunk.keys():
            if str(key).lower()==str(fieldToFind).lower():
                valueParsed=responseChunk[key]
                valueFound=True
                return (valueFound,valueParsed)
            if type(responseChunk[key]) is dict:
                return parseValue(fieldToFind,responseChunk[key])
            elif type(responseChunk[key]) is list:
                for eachValue in responseChunk[key]:
                    return parseValue(fieldToFind,eachValue)
    return (valueParsed,valueFound)

def parse_json_recursively(json_object, target_key):
    #global retval
    if type(json_object) is dict and json_object:
        for key in json_object:
            if key.lower() == str(target_key.lower()):
                if type(json_object[key]) is float:
                    SystemConfig.responseField=str(format(json_object[key], SystemConfig.floatLimit))
                else:
                    SystemConfig.responseField=str(json_object[key])
                print("{}: {}".format(target_key, json_object[key]))
                return;
            parse_json_recursively(json_object[key], target_key)

    elif type(json_object) is list and json_object:
        for item in json_object:
            parse_json_recursively(item, target_key)

def isObjectFound(json_object, targetKey):
    jsonPath = "json_object" + targetKey
    print("jsonPath : " + jsonPath)
    try:
        if type(eval(jsonPath)) is float:
            SystemConfig.responseField=str(format(eval(jsonPath), SystemConfig.floatLimit))
        else:
            SystemConfig.responseField=str(format(eval(jsonPath)))
        return True
    except Exception as e:
        print "Failure. Param : {0} not found in the response".format(targetKey)
        return False

def extractParamValueFromResponse(param): #passed key eg id:12 (then key will be id)
    #returns specific param value from response

    #always set response to None initially
    SystemConfig.responseField=None
    if dynamicConfig.responseText is None:
        return None

    if "xml" in str(dynamicConfig.currentResponse.headers['Content-Type']):
        try:
            if param.startswith("[") and param.endswith("]"):
                if isObjectFound(dynamicConfig.currentResponseInJson, param):
                    return SystemConfig.responseField

            preString="<"+param+">"
            postString=r"</"+param+">"

            afterPreSplit=dynamicConfig.responseText.split(preString)[1]
            paramValue=afterPreSplit.split(postString)[0]
            return paramValue
        except Exception as e:
            print "[ERR] Exception found while Extracting '{0}' in response: {1}".format(param, e)
    else:
        try:
            data = dynamicConfig.currentResponse.json()
            strData=str(dynamicConfig.responseText)

            if param.startswith("[") and param.endswith("]"):
                if isObjectFound(data, param):
                    return SystemConfig.responseField
            else:
                if param in strData:
                    parse_json_recursively(data, param)
                    return SystemConfig.responseField
        except Exception as e:
            print "[ERR] Exception found while Extracting '{0}' in response: {1}".format(param, e)

    return None

def extractParamValueFromHeaders(param):
    if dynamicConfig.responseHeaders is None:
        return None

    try:
        data = dict(dynamicConfig.responseHeaders)
        print("Type of data is : {0}".format(type(data)))
        strData=str(data)

        if param in strData:
            (paramFoundStatus,paramResponseValue)=parseValue(param,data)
            if paramFoundStatus:
                return paramResponseValue
            else:
                return None
        else:
            print "Failure. Param : {0} not found in the response".format(param)
    except Exception as e:
        print "[ERR] Exception found while Extracting '{0}' in headers: {1}".format(param, e)
    return None

def storeGlobalParameters(globalParams):
    #parse response and find the global parameter
    val=None
    if globalParams is None:
        return

    try:
        globalParams=globalParams.strip()
    except:
        pass

    allGlobalParams=[]
    if "\n" in globalParams:
        allGlobalParams=globalParams.split("\n")
    else:
        allGlobalParams.append(globalParams)

    for eachParam in allGlobalParams:
        val=None
        if userConfig.data_splitter in eachParam:
            key = eachParam.partition(userConfig.data_splitter)[0]
            val = eachParam.partition(userConfig.data_splitter)[2]

            val = replacePlaceHolders(val)
            if "[" and "]" in val:
                val = extractParamValueFromResponse(val)
            SystemConfig.globalDict[key]=val
        else:
            if eachParam.startswith("HEADER_"):
                eachParam = eachParam.replace("HEADER_", "")
                val = extractParamValueFromHeaders(eachParam)
            else:
                val = extractParamValueFromResponse(eachParam)
            SystemConfig.globalDict[eachParam]=val

def add_time(initial_time, time_to_add, timeformat='%Y-%m-%dT%H:%M:%S'):
    from dateutil.relativedelta import relativedelta
    from datetime import datetime

    try:
        initial_time = datetime.strptime(initial_time, timeformat)
    except Exception as e:
        print ("[ERR] Encountered converting '{0}' to timeformat: {1}").format(initial_time, e)
        return None

    time_to_add = time_to_add.split(' ')
    years = 0
    for time in time_to_add:
        years = int(time.replace("years", "")) if "years" in time.lower() else 0
        months = int(time.replace("months", "")) if "months" in time.lower() else 0
        days = int(time.replace("days", "")) if "days" in time.lower() else 0
        hours = int(time.replace("hours", "")) if "hours" in time.lower() else 0
        minutes = int(time.replace("minutes", "")) if "minutes" in time.lower() else 0
        seconds = int(time.replace("seconds", "")) if "seconds" in time.lower() else 0

    time_to_add = relativedelta(years=years, months=months, days=days,
                                hours=hours, minutes=minutes, seconds=seconds)
    return (initial_time + time_to_add).strftime(timeformat)

def findElement(key, val):
    jsonPath = "dynamicConfig.currentResponseInJson" + key
    currentDict = eval(jsonPath)
    item_list = []

    if type(currentDict) is not list:
        item_list.append(currentDict)
    else:
        item_list = currentDict
    items = val.split(";")

    for index, item in enumerate(item_list):
        structureFound = False
        jsonPath = "item_list"
        for var in items:
            k = var.partition(userConfig.data_splitter)[0]
            v = var.partition(userConfig.data_splitter)[2]
            t = jsonPath + "[" + str(index)+ "]" + k

            try:
                if v == "" or v is None:
                    eval(t)
                    print("[INF] {0} is in {1}".format(k, key))
                else:
                    if eval(t) != str(v):
                        structureFound = False
                        break
            except Exception as e:
                print (e)
                structureFound = False
                break
            structureFound = True

        if structureFound:
            print ("[INF] "+ val + " is found in " + jsonPath + "[" + str(index)+ "]")
            return index

    print ("[ERR] "+ val + " is not found in " + jsonPath + "[" + str(index)+ "]")
    return -1

def parseAndValidateResponse(userParams):
    if userParams is None:
        return

    userParams=userParams.strip()
    allUserParams=[]
    if "\n" in userParams:
        allUserParams=userParams.split("\n")
    else:
        allUserParams.append(userParams)

    for eachUserParam in allUserParams:
        shouldContain = False

        if str(eachUserParam).startswith("func_"):
            keywordHandling.keywordBasedHandling(eachUserParam)

        elif str(eachUserParam).startswith("type_"):
            keywordHandling.responseParsingViaCode(eachUserParam)

        elif eachUserParam.startswith("result_code_check_"):
            val = eachUserParam.replace("result_code_check_", "")
            actual = keywordHandling.responseParsingViaResult(val)

            if actual is None:
                print ("[FAILURE] Result Code is not found in the response. "
                      "Response Status Code is {0}".format(dynamicConfig.responseStatusCode))
                customWriteTestStep("Result Code Checking", "Expected value : {0}".format(val),
                                    "Result Code is not found in the Response Body. " +
                                    "Response status code is {0}".format(dynamicConfig.responseStatusCode), "Fail")
                continue

            if val == actual:
                print ("[SUCCESS] Result Code is found in the response. "
                       "{0} is same as expected : {1}".format(actual,val))
                customWriteTestStep("Result Code Checking","Expected value : {0}".format(val),
                                    "Actual value : {0}".format(actual), "Pass")
            else:
                print(val + "::" + actual)
                print ("[FAILURE] Result Code is found in the response but "
                       "value : {0} is NOT same as expected : {1}".format(actual,val))
                customWriteTestStep("Result Code Checking","Expected value : {0}".format(val),
                                    "Actual value : {0}".format(actual), "Fail")

        elif eachUserParam.startswith("textMatch_"):
            val=eachUserParam
            val=val.replace("textMatch_","")
            if val.lower() in str(dynamicConfig.responseText).lower():
                customWriteTestStep("Check text match in Response body: {0}".format(val),"Expected Text : {0} should appear in response body".format(val),"Expected text appeared","Pass")
            else:
                customWriteTestStep("Check text match in Response body: {0}".format(val),"Expected Text : {0} should appear in response body".format(val),"Expected text did not appear in response body","Fail")

        elif eachUserParam.startswith("math_"):
            #math_var1+var2-var3:val_var4
            val=eachUserParam
            val=val.replace("math_","")
            (arithmeticExpression,expectedValue)=val.split(userConfig.data_splitter + "val_")

            returnVal=parseArithmeticExp(arithmeticExpression)
            if "Custom404"==str(returnVal):
                customWriteTestStep("Arithmetic exp failed to evaluate : {0}".format(arithmeticExpression),"NA","NA","Fail")

            customStatus="Fail"
            if float(returnVal)==float(expectedValue):
                customStatus="Pass"

            customWriteTestStep("Evaluate Arithmetic expression ".format(arithmeticExpression),"Expected val:{0}".format(val),"Actual val: {0}".format(returnVal),str(customStatus))

        elif eachUserParam.startswith("xml_"):
            #xml_<field_name>:val_<value>
            #value will be a path like root[0].
            key=None
            val=None
            if userConfig.data_splitter + "val_" in eachUserParam:
                (key,val)=eachUserParam.split(userConfig.data_splitter + "val_")
                key=key.replace("xml_","")
                try:
                    val=val.strip()
                except:
                    val=None
            else:
                key=eachUserParam.replace("xml_","")


            elementValue=find_element_using_path(dynamicConfig.responseText, key)

            if elementValue != "FieldNotFound":
                    # print "Failure: Expected field : {0} not".format(key)
                    customWriteTestStep("Find field : {0}".format(key),
                                        "Field should exist in Response Body",
                                        "Field exist in response body having value: {0}".format(elementValue), "Pass")

            else:
                    print "Failure: Expected field : {0} not found".format(key);customWriteTestStep("Unable to find field : {0}".format(key),"Field should exist in Response Body","Field does not exist in response body","Fail")

            if val is not None:
                fieldStatus="fail"
                if str(val)==str(elementValue):
                    fieldStatus="pass"

                customWriteTestStep("Expected field value should be same as actual. Field: {0}".format(key),
                                    "Expected value : {0}".format(val),
                                    "Actual Value : {0}".format(elementValue), fieldStatus)

            SystemConfig.localRequestDict[key]=elementValue

        elif eachUserParam.startswith("xmlWallet_"):
            #xmlWallet_<Wallet Name>
            origKeyword=eachUserParam
            key=None
            val=None

            #key is wallet name
            key=eachUserParam.replace("xmlWallet_","")


            returnValue=customUtils.getVolumeByWalletName(dynamicConfig.responseText, key)
            SystemConfig.localRequestDict[key]=returnValue

        elif "find(" in eachUserParam:
            key=eachUserParam.partition("find(")[0][:-1]
            val=eachUserParam.partition("find(")[2][:-1]
            index = findElement(key, val)
            if index != -1:
                Report.WriteTestStep("Response Parameter Validation by Finding Structure", "{0} Should be located in {1}".format(val, key), "Structure is Located in index: {0}".format(index),"Pass")
            else:
                Report.WriteTestStep("Response Parameter Validation by Finding Structure", "{0} Should be located in {1}".format(val, key), "Structure is not Located","Fail")
            continue

        elif userConfig.data_splitter in eachUserParam:
            val=eachUserParam.split(userConfig.data_splitter)[-1]
            key=eachUserParam.replace(userConfig.data_splitter + val, "")
            expectedValue = str(val).strip()
            expectedValue = replacePlaceHolders(expectedValue)

            if expectedValue.startswith("addTime("):
                tmp = expectedValue.partition("(")[2][:-1]
                [initial_time, time_to_add] = tmp.split(",")
                expectedValue = add_time(initial_time, time_to_add)

            elif expectedValue.startswith("contains("):
                expectedValue = expectedValue.replace("contains(", "").replace(")", "")
                shouldContain = True

            paramValue = extractParamValueFromResponse(key)
            val=expectedValue
            #val is the expectedValue
            #paramValue is the actualValue
            if paramValue is not None:
                if shouldContain:
                    if val.lower() in paramValue.lower():  #Earlier - if expectedValue.lower() in val.lower():
                        print "Success : param : {0} found in response and Value : {1} is  contained in value : {2}".format(key,paramValue,val)
                        customWriteTestStep("Response Parameter Validation : [{0}]".format(key),"Expected value : {0}".format(val),"Actual value : {0}".format(paramValue),"Pass")
                    else:
                        print "Failure : param : {0} found in response BUT Value : {1} is NOT contained in value : {2}".format(key,paramValue,val)
                        customWriteTestStep("Response Parameter Validation : [{0}]".format(key),"Expected value : {0}".format(val),"Actual value : {0}".format(paramValue),"Fail")
                else:
                    if str(val.lower())==str(paramValue.lower()):
                        print "Success : param : {0} found in response and Value : {1} is same as expected : {2}".format(key,paramValue,val)
                        customWriteTestStep("Response Parameter Validation : [{0}]".format(key),"Expected value : {0}".format(val),"Actual value : {0}".format(paramValue),"Pass")
                    else:
                        print "Failure : param : {0} found in response BUT Value : {1} is NOT same as expected : {2}".format(key,paramValue,val)
                        customWriteTestStep("Response Parameter Validation : [{0}]".format(key),"Expected value : {0}".format(val),"Actual value : {0}".format(paramValue),"Fail")
            else:
                print "Falure : param : {0} not found in response".format(key)
                customWriteTestStep("Response Parameter Validation : [{0}]".format(key),"Expected value : {0}".format(val),"Parameter was not found in the response structure","Fail")


        else:
            #just make sure fields are available
            key=eachUserParam
            paramValue=extractParamValueFromResponse(eachUserParam)
            if paramValue is not None:
                print "Success : param : {0} found in response. Value : {1}".format(eachUserParam,paramValue)
                customWriteTestStep("Capture Response Parameter : [{0}]".format(key),"Parameter should be present in the Response","Parameter : [{0}] having value : [{1}] was found in the Response".format(key,paramValue),"Pass")

            else:
                print "Failure : param : {0} not found in response".format(eachUserParam)
                customWriteTestStep("Capture Response Parameter : [{0}]".format(key),"Parameter should be present in the Response","Parameter : [{0}] was not found in Response".format(key),"Fail")

def parseAndValidateHeaders(userParams):
    if userParams is None:
        return

    userParams=replacePlaceHolders(userParams.strip())
    allUserParams=[]

    if "\n" in userParams:
        allUserParams=userParams.split("\n")
    else:
        allUserParams.append(userParams)

    for eachUserParam in allUserParams:
        shouldContain = False

        if eachUserParam.startswith("textMatch_"):
            eachUserParam=eachUserParam.replace("textMatch_","")
            val=eachUserParam
            if val.lower() in str(dynamicConfig.responseHeaders).lower():
                customWriteTestStep("Check text match in Response Headers: {0}".format(val),"Expected Text : {0} should appear in Response Headers".format(val),"Expected text appeared","Pass")
            else:
                customWriteTestStep("Check text match in Response Headers: {0}".format(val),"Expected Text : {0} should appear in Response Headers".format(val),"Expected text did not appear in Response Headers","Fail")

        elif userConfig.data_splitter in eachUserParam:
            key=eachUserParam.split(userConfig.data_splitter)[0]
            val=eachUserParam.replace(key+userConfig.data_splitter,"")
            expectedValue=str(val).strip()

            if expectedValue.startswith("contains("):
                expectedValue = expectedValue.replace("contains(", "").replace(")", "")
                shouldContain = True

            paramValue = extractParamValueFromHeaders(key)
            val        = expectedValue

            if paramValue is not None:
                if shouldContain:
                    if val.lower() in paramValue.lower():
                        print "Success : param : {0} found in response and Value : {1} is  contained in value : {2}".format(key,paramValue,val)
                        customWriteTestStep("Response Parameter Validation : [{0}]".format(key),"Expected value : {0}".format(val),"Actual value : {0}".format(paramValue),"Pass")
                    else:
                        print "Failure : param : {0} found in response BUT Value : {1} is NOT contained in value : {2}".format(key,paramValue,val)
                        customWriteTestStep("Response Parameter Validation : [{0}]".format(key),"Expected value : {0}".format(val),"Actual value : {0}".format(paramValue),"Fail")
                else:
                    if str(val.lower())==str(paramValue.lower()):
                        print "Success : param : {0} found in response and Value : {1} is same as expected : {2}".format(key,paramValue,val)
                        customWriteTestStep("Response Parameter Validation : [{0}]".format(key),"Expected value : {0}".format(val),"Actual value : {0}".format(paramValue),"Pass")
                    else:
                        print "Failure : param : {0} found in response BUT Value : {1} is NOT same as expected : {2}".format(key,paramValue,val)
                        customWriteTestStep("Response Parameter Validation : [{0}]".format(key),"Expected value : {0}".format(val),"Actual value : {0}".format(paramValue),"Fail")
            else:
                print "Falure : param : {0} not found in response".format(key)
                customWriteTestStep("Response Parameter Validation : [{0}]".format(key),"Expected value : {0}".format(val),"Parameter was not found in the response structure","Fail")
        else:
            key=eachUserParam
            paramValue=extractParamValueFromHeaders(eachUserParam)
            if paramValue is not None:
                print "Success : param : {0} found in response. Value : {1}".format(eachUserParam,paramValue)
                customWriteTestStep("Capture Response Parameter : [{0}]".format(key),"Parameter should be present in the Response","Parameter : [{0}] having value : [{1}] was found in the Response".format(key,paramValue),"Pass")
            else:
                print "Failure : param : {0} not found in response".format(eachUserParam)
                customWriteTestStep("Capture Response Parameter : [{0}]".format(key),"Parameter should be present in the Response","Parameter : [{0}] was not found in Response".format(key),"Fail")

def markInBetweenTestCasesBlocked(startTC,endTC):
    for tc in range(startTC,endTC):
        testCaseName = eh.get_cell_value(tc+1, SystemConfig.col_TestCaseName)
        nextTestCaseName = eh.get_cell_value(tc+2, SystemConfig.col_TestCaseName)

        if testCaseName is not None:
            dynamicConfig.testStepNo = 1
            customWriteTestCase("TC_{0}".format(dynamicConfig.testCaseNo), testCaseName)
            dynamicConfig.testCaseNo += 1
            customWriteTestStep("This TC is blocked since Row {0} had failed".format(startTC-1),"NA","NA","Failed")
        else:
            dynamicConfig.testStepNo += 1
            customWriteTestStep("Test Step in row {0} is blocked since Row {1} had failed".format(tc, startTC-1),"NA","NA","Failed")

        if nextTestCaseName is not None or tc == endTC:
            Report.evaluateIfTestCaseIsPassOrFail()

def executeCommand(vars):
    if vars is None:
        return

    vars = vars.strip()
    if not vars:
        return

    allVars=[]
    if "\n" in vars:
        allVars=vars.split("\n")
    else:
        allVars.append(vars)

    for val in allVars:
        if val.lower().startswith("sleep"):
            try:
                val=int(str(val.replace("sleep(","").replace(")","")).strip())
                print("[User-Command] Will sleep for {0} seconds".format(val))
                time.sleep(val)
                customWriteTestStep("Wait before proceeding to next step for {0} seconds".format(val), "Should wait","Waited for: {0} seconds".format(val),"Passed")
            except:
                print("[ERROR] Invalid argument for Sleep command : {0}".format(val))
                customWriteTestStep("Wait before proceeding to next step for {0} seconds".format(val), "The argument passed should be an Integer","The argument passed is Invalid : {0}".format(val),"Passed")

        elif val.lower().startswith("terminateonfailure"):
            try:
                if dynamicConfig.testCaseHasFailed:
                    print("[User-Command] Terminate on failure")
                    val=str(val.replace("terminateonfailure(","").replace(")","")).strip()
                    if val.lower()=="true":
                        customWriteTestStep("Terminating flow since failure is encountered","NA","NA","Failed")
                        Report.evaluateIfTestCaseIsPassOrFail()
                        endProcessing()
            except:
                print("[ERROR] Invalid argument for TerminateOnFailure command : {0}".format(val))
                customWriteTestStep("Invalid argument for TerminateOnFailure command : {0}".format(val), "The argument passed should be either yes or no","Invalid argument","Failed")

        elif val.startswith("math_"):
            val=val.replace("math_","")
            (arithmeticExpression,expectedValue)=val.split(":val_")

            returnVal=parseArithmeticExp(arithmeticExpression)
            if "Custom404"==str(returnVal):
                customWriteTestStep("Arithmetic exp failed to evaluate : {0}".format(arithmeticExpression),"NA","NA","Fail")

            customStatus="Fail"
            if float(returnVal)==float(expectedValue):
                customStatus="Pass"

            customWriteTestStep("Evaluate Arithmetic expression ".format(arithmeticExpression),"Expected val:{0}".format(val),"Actual val: {0}".format(returnVal),str(customStatus))

        elif val.lower().startswith("skiponfailure"):
            try:
                if dynamicConfig.testCaseHasFailed:
                    print("[User-Command] SkipOnFailure")
                    val=int(str(val.replace("skiponfailure(","").replace(")","")).strip())
                    testCaseNumberToSkipTo=val

                    if(testCaseNumberToSkipTo<=SystemConfig.endRow):
                        rowNumberWhichFailed=SystemConfig.currentRow
                        SystemConfig.currentRow=testCaseNumberToSkipTo
                        customWriteTestStep("Skip to TC #{0} since failure is encountered".format(testCaseNumberToSkipTo),"NA","NA".format(SystemConfig.endRow),"Failed")
                        testCaseNumberToSkipTo=val
                        markInBetweenTestCasesBlocked(rowNumberWhichFailed, testCaseNumberToSkipTo)
                    else:
                        customWriteTestStep("TC#:{0} to skip to does not exist.".format(testCaseNumberToSkipTo),"The TC# to skip to should be within the range of total # of TCs","Max TCs {0}: ".format(SystemConfig.endRow),"Failed")
            except:
                traceback.print_exc()
                print("[ERROR] Invalid argument for SkipOnFailure command : {0}".format(val))
                customWriteTestStep("Invalid argument for SkipOnFailure command : {0}".format(val), "The argument passed should be an Integer","Invalid argument","Failed")

        elif val.lower().startswith("skipalways"):
            try:
                print("[User-Command] Skip-Always")
                val=int(str(val.replace("skipalways(","").replace(")","")).strip())
                testCaseNumberToSkipTo=val

                if(testCaseNumberToSkipTo<=SystemConfig.endRow):
                    rowNumberWhichFailed=SystemConfig.currentRow
                    SystemConfig.currentRow=testCaseNumberToSkipTo
                    testCaseNumberToSkipTo=val
                    Report.evaluateIfTestCaseIsPassOrFail()
                else:
                    customWriteTestStep("TC#:{0} to skip to does not exist.".format(testCaseNumberToSkipTo),"The TC# to skip to should be within the range of total # of TCs","Max TCs {0}: ".format(SystemConfig.endRow),"Failed")
            except:
                traceback.print_exc()
                print("[ERROR] Invalid argument for SkipOnFailure command : {0}".format(val))
                customWriteTestStep("Invalid argument for SkipOnFailure command : {0}".format(val), "The argument passed should be an Integer","Invalid argument","Failed")
        else:
            print("No handling defined for : ",val)

def theiaDoubleEncode(val):
    os.system("getEncodedVal.pys")

    urllib.quote_plus('W7Bv+KOF0xQIgf2T2V/LJQ==')

def setAuthentication(authentication):
    if authentication is None:
        dynamicConfig.currentAuthentication = None
        return
    authentication = authentication.encode('ascii', 'ignore')
    allVars=[]
    authentication = replacePlaceHolders(authentication)

    if "\n" in authentication:
        allVars=authentication.split("\n")
    else:
        allVars.append(authentication)

    for eachVar in allVars:
        [key,val] = eachVar.split(userConfig.data_splitter, 1)
        key       = key.lower()

        SystemConfig.authenticationDict[key] = val

    if "BASIC" == SystemConfig.authenticationDict["type"].upper():
        dynamicConfig.currentAuthentication = (SystemConfig.authenticationDict["username"],
                                               SystemConfig.authenticationDict["password"])

    if "NO AUTH" == SystemConfig.authenticationDict["type"].upper():
        dynamicConfig.currentAuthentication =None

def getEndRow(currentRow):
    while SystemConfig.maxRows >= currentRow:
        testCaseNumber = eh.get_cell_value(currentRow, SystemConfig.col_TestCaseNo)
        if "(end)" in str(testCaseNumber).lower():
            return currentRow
        currentRow += 1

def main():
    startingPointisFound=False
    eh.read_sheet("TCs", SystemConfig.lastColumnInSheetTCs)
    setColumnNumbersForFileValidations()
    #Report.InitializeReporting()

    #loop over all records one by one
    SystemConfig.currentRow = eh.get_row_number_of_string("ResponseParametersToCapture")
    SystemConfig.currentRow += 1
    SystemConfig.startingRowNumberForRecordProcessing=SystemConfig.currentRow
    SystemConfig.endRow = getEndRow(SystemConfig.currentRow)
    #print "Max Rows : {0}\n".format(SystemConfig.maxRows)

    while SystemConfig.currentRow <= SystemConfig.endRow:
        currentRow = SystemConfig.currentRow
        #print("Row #: {0}\n".format(currentRow))
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

        eh.read_sheet("TCs",SystemConfig.lastColumnInSheetTCs)
        automation_reference = str(eh.get_cell_value(currentRow, SystemConfig.col_Automation_Reference))
        testCaseNumber = str(eh.get_cell_value(currentRow, SystemConfig.col_TestCaseNo))

        if automation_reference is None or str(automation_reference).strip()=="":
            break

        if not startingPointisFound:
            if "(start)" not in str(testCaseNumber).lower():
                SystemConfig.currentRow+=1
                continue
            else:
                startingPointisFound=True

        testCaseName                = eh.get_cell_value(currentRow, SystemConfig.col_TestCaseName)
        statusCode                  = eh.get_cell_value(currentRow, SystemConfig.col_Status_Code)
        headerFieldsToValidate      = eh.get_cell_value(currentRow, SystemConfig.col_HeadersToValidate)
        responseParametersToCapture = eh.get_cell_value(currentRow, SystemConfig.col_ResponseParametersToCapture)
        headerParametersToCapture   = eh.get_cell_value(currentRow, SystemConfig.col_HeadersToValidate)
        requestParameters           = eh.get_cell_value(currentRow, SystemConfig.col_Parameters)
        apiToTrigger                = eh.get_cell_value(currentRow, SystemConfig.col_API_to_trigger)
        globalParams                = eh.get_cell_value(currentRow, SystemConfig.col_GlobalParametersToStore)
        clearGlobalParams           = eh.get_cell_value(currentRow, SystemConfig.col_ClearGlobalParameters)
        userDefinedVars             = eh.get_cell_value(currentRow, SystemConfig.col_Assignments)
        isJsonAbsolutePath          = eh.get_cell_value(currentRow, SystemConfig.col_isJsonAbsolutePath)
        preCommands                 = eh.get_cell_value(currentRow, SystemConfig.col_preCommands)
        postCommands                = eh.get_cell_value(currentRow, SystemConfig.col_postCommands)

        eh.read_sheet("Structures", SystemConfig.lastColumnInSheetStructures)
        matchedRow = eh.get_row_number_of_string(apiToTrigger)
        endPoint             = eh.get_cell_value(matchedRow, SystemConfig.col_EndPoint)
        requestStructure     = eh.get_cell_value(matchedRow, SystemConfig.col_API_Structure)
        rawHeaderText        = eh.get_cell_value(matchedRow, SystemConfig.col_Headers)
        typeOfRequest        = eh.get_cell_value(matchedRow, SystemConfig.col_Method)
        authenticationParams = eh.get_cell_value(matchedRow, SystemConfig.col_Authentication)

        eh.read_sheet("TCs", SystemConfig.lastColumnInSheetTCs)

        executeCommand(preCommands)

        if typeOfRequest is not None:
            if requestStructure and "<soap" in requestStructure:
                typeOfRequest+="(soap)" #POST(soap)
            else:
                typeOfRequest+="(rest)" #POST(rest)
            print "type of request is : ",typeOfRequest

        testCaseNumber = testCaseNumber.upper().replace("(START)", "")
        testCaseNumber = testCaseNumber.upper().replace("(END)", "")

        if testCaseName is not None:
            dynamicConfig.testStepNo = 1
            customWriteTestCase("TC_{0}".format(dynamicConfig.testCaseNo), testCaseName)
            dynamicConfig.testCaseNo += 1

        SystemConfig.currentTestCaseNumber=testCaseNumber
        SystemConfig.currentAPI=apiToTrigger

        if isJsonAbsolutePath is not None:
            SystemConfig.currentisJsonAbsolutePath = isJsonAbsolutePath.upper()

        storeUserDefinedVariables(userDefinedVars)
        #parse header
        setAuthentication(authenticationParams)
        endPoint = replacePlaceHolders(endPoint)
        headers = parseHeader(rawHeaderText)

        if headers is not None:
            dynamicConfig.currentHeader=headers
            if "Content-Type" in headers.keys():
                dynamicConfig.currentContentType = headers["Content-Type"].encode('ascii', 'ignore')
        else:
            if "rest" in typeOfRequest.lower():
                dynamicConfig.currentHeader={}
            else:
                dynamicConfig.currentHeader=""

        #parse parameters
        requestStructure = parametrizeRequest(requestStructure, requestParameters)

        if requestStructure is not None:
            dynamicConfig.currentRequest=requestStructure
        else:
            if "rest" in typeOfRequest.lower():
                dynamicConfig.currentRequest={}
            else:
                dynamicConfig.currentRequest=""


        dynamicConfig.currentUrl=endPoint
        dynamicConfig.restRequestType=typeOfRequest.strip().lower()

        print "\nTC# : {0}".format(testCaseNumber)

        if requestStructure is not None and str(requestStructure).startswith("<soap"):
            print "\n[ Executing SOAP Request ]"
            print "\nWebservice : {0}".format(apiToTrigger)
            dynamicConfig.apiToTrigger=apiToTrigger
            print "\nEndPoint : {0}".format(endPoint)
            print "\nRequest : {0}".format(requestStructure)

            customWriteTestStep("SOAP Request details","Log request details","EndPoint : {0}\nHeader: {1}\nBody : {2}".format(endPoint,headers,requestStructure),"Pass")

            ApiLib.triggerSoapRequest()
            dynamicConfig.currentResponseInJson = convert_text_to_dict(dynamicConfig.responseText)

            customWriteTestStep("Log Response","Log Response","{0}".format(dynamicConfig.currentResponse),"Pass")


        else:
            print "\n[ Executing Rest Request ]"

            print "\nAPI : {0}".format(apiToTrigger)
            dynamicConfig.apiToTrigger=apiToTrigger
            print "\nEndPoint : {0}".format(endPoint)
            print "\nHeader : {0}".format(headers)
            print "\nRequest : {0}".format(requestStructure)

            customWriteTestStep("Rest Request details","Log request details","Request Type : {0}\n\nEndPoint : {1}\n\nHeader: {2}\n\nBody : {3}".format(typeOfRequest,endPoint,headers,requestStructure),"Pass")
            ApiLib.triggerRestRequest()
        logResponseTime()

        if dynamicConfig.currentResponse is None:
            customWriteTestStep("Log Response","Log Response","No Response received from server within user-configured timeout : {0} seconds".format(userConfig.timeoutInSeconds),"Fail")

        else:
            if "application/pdf" not in str(dynamicConfig.responseHeaders):
                customWriteTestStep("Log Response","Log Response","Status Code : {0}\n\nHeaders: {1}\n\nBody: {2}".format(dynamicConfig.responseStatusCode,dynamicConfig.responseHeaders,dynamicConfig.responseText),"Pass")
            else:
                customWriteTestStep("Log Response","Log Response","Status Code : {0}\n\nHeaders: {1}".format(dynamicConfig.responseStatusCode,dynamicConfig.responseHeaders),"Pass")

        if statusCode is not None:
            SystemConfig.successfulResponseCode=str(statusCode)
            dynamicConfig.responseStatusCode = str(dynamicConfig.responseStatusCode)
            if dynamicConfig.responseStatusCode in str(statusCode):
                customWriteTestStep("Validate Response Code","Expected Response Code(s) : {0}".format(SystemConfig.successfulResponseCode),"Actual Response Code : {0}".format(dynamicConfig.responseStatusCode),"Pass")
                print "[INFO] Valid Status Code: " + dynamicConfig.responseStatusCode + " is received"
            else:
                customWriteTestStep("Validate Response Code","Expected Response Code(s) : {0}".format(SystemConfig.successfulResponseCode),"Actual Response Code : {0}".format(dynamicConfig.responseStatusCode),"Fail")
                print "[ERR] " + dynamicConfig.responseStatusCode + " not in Expected Status Codes : " + SystemConfig.successfulResponseCode
        else:
            customWriteTestStep("Skipping Response Validation since no Response Code is specified in Datasheet","NA","NA","Pass")

        storeGlobalParameters(globalParams)
        parseAndValidateResponse(responseParametersToCapture)
        parseAndValidateHeaders(headerParametersToCapture)
        executeCommand(postCommands)

        if str(clearGlobalParams).upper().startswith("Y"):
            SystemConfig.globalDict={}

        SystemConfig.localRequestDict={}

        nextTestCaseName = eh.get_cell_value(SystemConfig.currentRow + 1, SystemConfig.col_TestCaseName)

        if nextTestCaseName is not None or SystemConfig.currentRow == SystemConfig.endRow:
            Report.evaluateIfTestCaseIsPassOrFail()
        else:
            dynamicConfig.testStepNo += 1
        SystemConfig.currentRow += 1

def initiateLogging(resultFolder):
    if dynamicConfig.isLoggingEnabled:
        return

    dynamicConfig.isLoggingEnabled=True
    Config.logsFolder=str(resultFolder)+"\\logs"
    print "Logs will be created at : {0}".format(Config.logsFolder)
    os.mkdir(Config.logsFolder)

def superMain(cookieValue):
    try:
        SystemConfig.startTime=datetime.datetime.now()
        resultFolder=Report.InitializeReporting()
        initiateLogging(resultFolder)

        SystemConfig.cookieValue=cookieValue
        main()
    except Exception:
        traceback.print_exc()
    finally:
        executionTime = datetime.datetime.now() - SystemConfig.startTime
        os.environ["EXECTIME"] = str(executionTime)

    try:
        Report.GeneratePDFReport()
    except:
        traceback.print_exc()
        print "[ERR] Failure in Generating Pdf."

if __name__ == '__main__':
    resultFolder=Report.InitializeReporting()
    initiateLogging(resultFolder)

    try:
        cookieValue='''GCP_IAP_UID=securetoken.google.com/globe-isg-onegie-staging:N0bENMd9Gyc5UiWMq6QqBUAVA3y2; sessionid=6rv44hvpai181kopktbtwuyr2sg9k4rc; GCP_IAP_XSRF_NONCE_7pNhEx7Xdxh-Y4nxfXQePQ=1; GCP_IAAP_AUTH_TOKEN_7978BFF0652DFB0=AFtMideN_SR0LqiA0WTUMOQkOjGNUAg2bdpCw5RCbziMTJ6JvcwofZipRPBSIl9DdbZiW-W9vmNMwPnUH3Xn7yleh8PJZPnkEaWxGp7AS9j06lZ1heZn4lRKycY2Onn36rwa9Ch0bQ39eaCpVRWzV9oWR9YwTiwO91sPqHL1T-UKThAxY8oARJJpsLGV7-9G_T8llrhhuTFLK6Z1utXqgEFBkLR7yxLW0jwAhQxa53p-nm4KTRNDjY0WphcowkOWWN1-zxEP7QHEbRW6xzObYj4u2LM9DstZc1VRCYCREAOTMUivoC3a3BN8VJinkZmxtqHmn8_i3MTaitHZdknK34wxV_bwN5gaRaSvHO9sSF5rvZfew8a7Dvw4jeEv3a0cRqhwsqM9O8VErl2SajpfJcUrsJFPEmSEDiRnqlAZuHw6vE5GJzDKlL-8Jvu_kCVFsPuw4OLRfQz2RBYYgdleVsdU2IegBzAhBq-f4EPQrAb82cbf686tLMf0Nqs4E-fXkLqJ49RywXylAFvLrs12lOJ-8XD_llZFEQ1VwokGOo2xPnLLzkC0D5H6wtA-3SgPH_4DXI-RFkIY-tmMOmaJLFh9vdKelvGqAGPDWEGEgsKREZ_dTfGx3zxVg2n3tlp_Q4fm8n7v7agp0dUaso6vibsS2PlRSKeqYBoZOmC3zabj-bl7WzXfD7li1waSvVYJab-Tbei-2tvuDcO8FUYPM1OJBOLI1IlbfGubVjPl3jLE1c1X6_7fMkZ8Ht-AGvCC-5AtkkRnhdP_e9UwUjDiXpC4wyfgV3DAhzkVo_5MaRRouhNgvay6_9XHW6UxQG9SDekmAojY8N_K8hdC1DEKiGjdXAj27L6XPYlSt9ziDIm_guFp6Bnyz97wj-3z1yI66dA7lLMNAWWwgciH48c-TonFbIorLwwXW1fNknWrpKoT-KiPdO0nOoXEq84KXAJ3BpX_UUZp8_F7rZdyE7B5t7sRRwz5BXwV3_G4_U9qCm7WZeiU0dN9HR52O65XYVxpSJ4s3mXDPr94EefgDbu6aqNvrQ_Rds_Ontixm6YZBVFxMtNdqig6Ferou2xpAviccFB1NmWgHs_I7FPICCfI65_ZUX3oxfQBAigXt3uwwrmfb6E1d4V5JF1runahd0AfbpcQZ8NIFDwvUAxwCa-ZSJJbKbdYjs7XM8Ftwy0I77O2Ei-qB8E-zwNXok9-8fYMkOUIvRdv-wV0nnCjLGIRrfri5FOdX_IZ-Wj2NZGbhOfo074YMl0-EpObE1ZYRYS3ryZ_bfoSEj1jDb8-DUFiaNkAKVfsIqHicOnA4VusPEnO_YNZKkv_hq24Jo76CX59b5CCbuk_jQoQWagqqIwtu_eLdhF2KhAfDOTMztXTJW10mUhJECz1Pddo3p9In4MgjNN_Hgy_U61ZHLlutBGO0L0XbDSWVuiPRRdUAK0EYslyOq_nggjrmDZUgK6nPO6mx1xlvZbd69QAXoim9VO8mlOJw27o9vakZhCbFl2aNiJIL8wv1sH6LvzqHewJ3n0IRg4ButEoGkF1wboVUUFozX5lwbMuOd7QZa8m9Pt5GXeZhYYLG-70S4DyuIZw6eqhtAv7Mts; csrftoken=atAeuO5B365maolhimoYCfUfoB4m69F84DcTAf9BNMJameJ6oMIw5o5PHBhFB2CJ'''
        superMain(cookieValue)
    except Exception,e:
        traceback.print_exc()
