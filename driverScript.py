#pending development :

#Timestamp keyword check
#JS Fetch

import os, sys
sys.path.append(".")
sys.path.append("customLib")
import keywordHandling
import openpyxl
import logging, traceback
import SystemConfig,userConfig
import time
import customLib.Report as Report
import customLib.Config as Config
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
import test_data_helper
import execute_commands_helper
from customUtils import customWriteTestStep, endProcessing, replacePlaceHolders, getIndexNumber, find_element_using_path
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
    SystemConfig.col_Main_Test_Step = eh.get_column_number_of_string(SystemConfig.field_Main_Test_Step)
    SystemConfig.col_Main_Test_Step_Description = eh.get_column_number_of_string(SystemConfig.field_Main_Test_Step_Description)
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

def extractParamValueFromResponse(param): #passed key eg id:12 (then key will be id)
    #returns specific param value from response

    #always set response to None initially
    SystemConfig.responseField=None
    if dynamicConfig.responseText is None:
        return None

    if "xml" in str(dynamicConfig.currentResponse.headers['Content-Type']):
        try:
            if param.startswith("[") and param.endswith("]"):
                if keywordHandling.isObjectFound(dynamicConfig.currentResponseInJson, param):
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
                if keywordHandling.isObjectFound(data, param):
                    return SystemConfig.responseField
            else:
                if param in strData:
                    keywordHandling.parse_json_recursively(data, param)
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
            keywordHandling.responseParsingViaResult(eachUserParam)

        elif eachUserParam.startswith("textMatch_"):
            val=eachUserParam
            val=val.replace("textMatch_","")
            if val.lower() in str(dynamicConfig.responseText).lower():
                customWriteTestStep("Check text match in Response body: {0}".format(val),
                                    "Expected Text : {0} should appear in response body".format(val),
                                    "Expected text appeared", "Pass")
            else:
                customWriteTestStep("Check text match in Response body: {0}".format(val),
                                    "Expected Text : {0} should appear in response body".format(val),
                                    "Expected text did not appear in response body", "Fail")

        elif eachUserParam.startswith("math_"):
            #math_var1+var2-var3:val_var4
            val=eachUserParam
            val=val.replace("math_","")
            (arithmeticExpression,expectedValue)=val.split(userConfig.data_splitter + "val_")
            keywordHandling.validate_math(arithmeticExpression, expectedValue)

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
                    print "Failure: Expected field : {0} not found".format(key)
                    customWriteTestStep("Unable to find field : {0}".format(key),
                                        "Field should exist in Response Body",
                                        "Field does not exist in response body", "Fail")

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
            index = test_data_helper.findElement(key, val)
            if index == -1:
                customWriteTestStep("Response Parameter Validation by Finding Structure",
                                    "{0} Should be located in {1}".format(val, key),
                                    "{0} is not Located".format(val), "Fail")
            elif index == -2:
                customWriteTestStep("Response Parameter Validation by Finding Structure",
                    "{0} Should be located in {1}".format(val, key),
                    "{0} is not located in the response".format(key),"Fail")
            continue

        elif "get_value(" in eachUserParam:
            key=eachUserParam.partition("get_value(")[0][:-1]
            val=eachUserParam.partition("get_value(")[2][:-1]
            output = test_data_helper.get_element(key, val)
            if output == 0:
                customWriteTestStep("Response Parameter Validation by Finding Structure",
                                    "Get value for paramaeters {0}".format(val),
                                    "Value for {0} is {1}".format(val, SystemConfig.globalDict[key]), "Pass")
            continue

        elif userConfig.data_splitter in eachUserParam:
            val=eachUserParam.split(userConfig.data_splitter)[-1]
            key=eachUserParam.replace(userConfig.data_splitter + val, "")
            expectedValue = str(val).strip()
            expectedValue = replacePlaceHolders(expectedValue)

            if expectedValue.startswith("addTime("):
                tmp = expectedValue.partition("(")[2][:-1]
                [initial_time, time_to_add] = tmp.split(",")
                expectedValue = test_data_helper.add_time(initial_time, time_to_add)

            elif expectedValue.startswith("contains("):
                expectedValue = expectedValue.replace("contains(", "").replace(")", "")
                shouldContain = True

            paramValue = extractParamValueFromResponse(key)
            val = expectedValue
            #val is the expectedValue
            #paramValue is the actualValue
            if paramValue is not None:
                if shouldContain:
                    if val.lower() in paramValue.lower():  #Earlier - if expectedValue.lower() in val.lower():
                        print "Success : param : {0} found in response and Value : {1} is  contained in value : {2}".format(key,paramValue,val)
                        customWriteTestStep("Response Parameter Validation : [{0}]".format(key),
                                            "Expected value : {0}".format(val),
                                            "Actual value : {0}".format(paramValue), "Pass")
                    else:
                        print "Failure : param : {0} found in response BUT Value : {1} is NOT contained in value : {2}".format(key,paramValue,val)
                        customWriteTestStep("Response Parameter Validation : [{0}]".format(key),
                                            "Expected value : {0}".format(val),
                                            "Actual value : {0}".format(paramValue), "Fail")
                else:
                    if str(val.lower())==str(paramValue.lower()):
                        print "Success : param : {0} found in response and Value : {1} is same as expected : {2}".format(key,paramValue,val)
                        customWriteTestStep("Response Parameter Validation : [{0}]".format(key),
                                            "Expected value : {0}".format(val),
                                            "Actual value : {0}".format(paramValue), "Pass")
                    else:
                        print "Failure : param : {0} found in response BUT Value : {1} is NOT same as expected : {2}".format(key,paramValue,val)
                        customWriteTestStep("Response Parameter Validation : [{0}]".format(key),
                                            "Expected value : {0}".format(val),
                                            "Actual value : {0}".format(paramValue), "Fail")
            else:
                print "Falure : param : {0} not found in response".format(key)
                customWriteTestStep("Response Parameter Validation : [{0}]".format(key),
                                    "Expected value : {0}".format(val),
                                    "Parameter was not found in the response structure", "Fail")


        else:
            #just make sure fields are available
            key = eachUserParam
            paramValue = extractParamValueFromResponse(eachUserParam)
            if paramValue is not None:
                print "Success : param : {0} found in response. Value : {1}".format(eachUserParam,paramValue)
                customWriteTestStep("Capture Response Parameter : [{0}]".format(key),
                                    "Parameter should be present in the Response",
                                    "Parameter : [{0}] having value : [{1}] was found in the Response".format(key,paramValue), "Pass")

            else:
                print "Failure : param : {0} not found in response".format(eachUserParam)
                customWriteTestStep("Capture Response Parameter : [{0}]".format(key),
                                    "Parameter should be present in the Response",
                                    "Parameter : [{0}] was not found in Response".format(key), "Fail")

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
                customWriteTestStep("Check text match in Response Headers: {0}".format(val),
                                    "Expected Text : {0} should appear in Response Headers".format(val),
                                    "Expected text appeared", "Pass")
            else:
                customWriteTestStep("Check text match in Response Headers: {0}".format(val),
                                    "Expected Text : {0} should appear in Response Headers".format(val),
                                    "Expected text did not appear in Response Headers", "Fail")

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
                        print "Success : param : {0} found in response header and Value : {1} is  contained in value : {2}".format(key,paramValue,val)
                        customWriteTestStep("Response Header Parameter Validation : [{0}]".format(key),
                                            "Expected value : {0}".format(val),
                                            "Actual value : {0}".format(paramValue), "Pass")
                    else:
                        print "Failure : param : {0} found in response header BUT Value : {1} is NOT contained in value : {2}".format(key,paramValue,val)
                        customWriteTestStep("Response Header Parameter Validation : [{0}]".format(key),
                                            "Expected value : {0}".format(val),
                                            "Actual value : {0}".format(paramValue), "Fail")
                else:
                    if str(val.lower())==str(paramValue.lower()):
                        print "Success : param : {0} found in response header and Value : {1} is same as expected : {2}".format(key,paramValue,val)
                        customWriteTestStep("Response Header Parameter Validation : [{0}]".format(key),
                                            "Expected value : {0}".format(val),
                                            "Actual value : {0}".format(paramValue), "Pass")
                    else:
                        print "Failure : param : {0} found in response header BUT Value : {1} is NOT same as expected : {2}".format(key,paramValue,val)
                        customWriteTestStep("Response Header Parameter Validation : [{0}]".format(key),
                                            "Expected value : {0}".format(val),
                                            "Actual value : {0}".format(paramValue), "Fail")
            else:
                print "Falure : param : {0} not found in response header".format(key)
                customWriteTestStep("Response Header Parameter Validation : [{0}]".format(key),
                                    "Expected value : {0}".format(val),
                                    "Parameter was not found in the response structure", "Fail")
        else:
            key=eachUserParam
            paramValue=extractParamValueFromHeaders(eachUserParam)
            if paramValue is not None:
                print "Success : param : {0} found in response. Value : {1}".format(eachUserParam,paramValue)
                customWriteTestStep("Capture Response Header Parameter : [{0}]".format(key),
                                    "Parameter should be present in the Response Header",
                                    "Parameter : [{0}] having value : [{1}] was found in the Response".format(key,paramValue), "Pass")
            else:
                print "Failure : param : {0} not found in response".format(eachUserParam)
                customWriteTestStep("Capture Response Header Parameter : [{0}]".format(key),
                                    "Parameter should be present in the Response Header",
                                    "Parameter : [{0}] was not found in Response".format(key), "Fail")

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
        dynamicConfig.currentAuthentication = None

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

        eh.read_sheet("TCs",SystemConfig.lastColumnInSheetTCs)
        automation_reference = str(eh.get_cell_value(currentRow, SystemConfig.col_Automation_Reference))
        testCaseNumber = str(eh.get_cell_value(currentRow, SystemConfig.col_TestCaseNo))

        dynamicConfig.will_execute_api = True
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
        responseParametersToCapture = eh.get_cell_value(currentRow, SystemConfig.col_ResponseParametersToCapture)
        headerParametersToCapture   = eh.get_cell_value(currentRow, SystemConfig.col_HeadersToValidate)
        requestParameters           = eh.get_cell_value(currentRow, SystemConfig.col_Parameters)
        apiToTrigger                = eh.get_cell_value(currentRow, SystemConfig.col_API_to_trigger)
        main_test_step              = eh.get_cell_value(currentRow, SystemConfig.col_Main_Test_Step)
        main_test_step_description  = eh.get_cell_value(currentRow, SystemConfig.col_Main_Test_Step_Description)
        globalParams                = eh.get_cell_value(currentRow, SystemConfig.col_GlobalParametersToStore)
        clearGlobalParams           = eh.get_cell_value(currentRow, SystemConfig.col_ClearGlobalParameters)
        userDefinedVars             = eh.get_cell_value(currentRow, SystemConfig.col_Assignments)
        isJsonAbsolutePath          = eh.get_cell_value(currentRow, SystemConfig.col_isJsonAbsolutePath)
        preCommands                 = eh.get_cell_value(currentRow, SystemConfig.col_preCommands)
        postCommands                = eh.get_cell_value(currentRow, SystemConfig.col_postCommands)

        eh.read_sheet("Structures", SystemConfig.lastColumnInSheetStructures)
        dynamicConfig.requestParameters = requestParameters
        testCaseNumber = testCaseNumber.upper().replace("(START)", "")
        testCaseNumber = testCaseNumber.upper().replace("(END)", "")
        SystemConfig.currentTestCaseNumber = testCaseNumber

        if isJsonAbsolutePath is not None:
            SystemConfig.currentisJsonAbsolutePath = isJsonAbsolutePath.upper()

        if testCaseName is not None:
            dynamicConfig.current_test_step_no = 0
            dynamicConfig.testStepNo = 1
            customWriteTestCase("TC_{0}".format(dynamicConfig.testCaseNo), testCaseName)
            dynamicConfig.testCaseNo += 1

        if main_test_step is not None:
            dynamicConfig.has_actual_test_step = True
            print("[INF] Running Test Steps for {0}".format(main_test_step))
            customUtils.customWriteActualTestCase(main_test_step, main_test_step_description)

        if apiToTrigger is None:
            keywordHandling.storeUserDefinedVariables(userDefinedVars)
            execute_commands_helper.parse(preCommands)
            eh.read_sheet("TCs", SystemConfig.lastColumnInSheetTCs)
        else:
            customUtils.reset_config()
            matchedRow = eh.get_row_number_of_string(apiToTrigger)
            endPoint             = eh.get_cell_value(matchedRow, SystemConfig.col_EndPoint)
            requestStructure     = eh.get_cell_value(matchedRow, SystemConfig.col_API_Structure)
            rawHeaderText        = eh.get_cell_value(matchedRow, SystemConfig.col_Headers)
            typeOfRequest        = eh.get_cell_value(matchedRow, SystemConfig.col_Method)
            authenticationParams = eh.get_cell_value(matchedRow, SystemConfig.col_Authentication)
            eh.read_sheet("TCs", SystemConfig.lastColumnInSheetTCs)

            execute_commands_helper.parse(preCommands)

            if typeOfRequest is not None:
                if requestStructure and "<soap" in requestStructure:
                    typeOfRequest+="(soap)" #POST(soap)
                else:
                    typeOfRequest+="(rest)" #POST(rest)
                print "type of request is : ",typeOfRequest

            SystemConfig.currentAPI = apiToTrigger
            dynamicConfig.apiToTrigger = apiToTrigger

            keywordHandling.storeUserDefinedVariables(userDefinedVars)
            #parse header
            setAuthentication(authenticationParams)
            endPoint = replacePlaceHolders(endPoint)
            headers = customUtils.parseHeader(rawHeaderText)
            dynamicConfig.currentUrl=endPoint
            dynamicConfig.restRequestType=typeOfRequest.strip().lower()

            #parse parameters
            requestStructure = customUtils.parametrizeRequest(requestStructure, requestParameters)
            customUtils.set_dynamic_request(requestStructure)

            print "\nTC# : {0}".format(testCaseNumber)

            if requestStructure is not None and str(requestStructure).startswith("<soap"):
                customUtils.triggerSoapRequest()
            else:
                customUtils.triggerRestRequest()

        skip_validation = False
        if statusCode is not None and dynamicConfig.will_execute_api:
            SystemConfig.expectedStatusCode=str(statusCode)
            dynamicConfig.responseStatusCode = str(dynamicConfig.responseStatusCode)

            if dynamicConfig.responseStatusCode in str(statusCode):
                customUtils.print_request_details(False)
                customUtils.print_response_details(False)
                customWriteTestStep("Validate Response Code",
                                    "Expected Response Code(s) : {0}".format(SystemConfig.expectedStatusCode),
                                    "Actual Response Code : {0}".format(dynamicConfig.responseStatusCode), "Pass")
                print "[INFO] Valid Status Code: " + dynamicConfig.responseStatusCode + " is received"
            else:
                customUtils.print_request_details(True)
                customUtils.print_response_details(True)
                customWriteTestStep("Validate Response Code",
                                    "Expected Response Code(s) : {0}".format(SystemConfig.expectedStatusCode),
                                    "Actual Response Code : {0}".format(dynamicConfig.responseStatusCode), "Fail")
                print "[ERR] " + dynamicConfig.responseStatusCode + " not in Expected Status Codes : " + SystemConfig.expectedStatusCode
                skip_validation = True

        if not skip_validation and dynamicConfig.will_execute_api:
            storeGlobalParameters(globalParams)
            parseAndValidateResponse(responseParametersToCapture)
            parseAndValidateHeaders(headerParametersToCapture)
            execute_commands_helper.parse(postCommands)

        customUtils.clear_dict(clearGlobalParams)

        nextTestCaseName = eh.get_cell_value(SystemConfig.currentRow + 1, SystemConfig.col_TestCaseName)
        nextActualTestCaseName = eh.get_cell_value(SystemConfig.currentRow + 1, SystemConfig.col_Main_Test_Step)
        if nextTestCaseName is not None or SystemConfig.currentRow == SystemConfig.endRow:
            Report.evaluateIfTestCaseIsPassOrFail()
        else:
            dynamicConfig.testStepNo += 1

        if dynamicConfig.has_actual_test_step:
            has_next_values = nextTestCaseName is not None or nextActualTestCaseName is not None
            if has_next_values or SystemConfig.currentRow == SystemConfig.endRow:
                dynamicConfig.has_actual_test_step = False
                Report.end_manual_test_case()
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
