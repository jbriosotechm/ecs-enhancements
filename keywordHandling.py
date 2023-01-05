import sys,time
import string
sys.path.append("customLib")
import cxs_lib
import SystemConfig,userConfig
import customLib.Report as Report
import customUtils
from customUtils import customWriteTestStep,endProcessing,replacePlaceHolders
import time,traceback
import dynamicConfig
import json
import ast
import ApiLib
import test_data_helper
import subprocess
from pprint import pprint
from commonLib import *

listOfValidKeywords=["compareBalance"]

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


def getResponseFieldValue(expectedValue):
    #returns specific param value from response

    param=expectedValue
    if dynamicConfig.responseText is not None:
        try:
            if "xml" in str(dynamicConfig.currentResponse.headers['Content-Type']):
                #soap xml parsing

                #print "Handling xml parsing"
                preString="<"+param+">"
                postString=r"</"+param+">"

                try:
                    afterPreSplit=dynamicConfig.responseText.split(preString)[1]
                    #print "\nafterPreSplit: ",afterPreSplit
                    paramValue=afterPreSplit.split(postString)[0]
                    #print "\nafterSecondSplit: ",paramValue
                    return paramValue
                except:
                    print "Failure. Param : {0} not found in the response".format(param)

            else:
                #json parsing
                data = dynamicConfig.currentResponse.json()
                strData=str(dynamicConfig.responseText)

                if param.startswith("[") and param.endswith("]"):
                    if isObjectFound(data, param):
                        return SystemConfig.responseField
                else:
                    if param in strData:
                        #(paramFoundStatus,paramResponseValue)=parseValue(param,data)
                        parse_json_recursively(data, param)
                        return SystemConfig.responseField
                    else:
                        print "Failure. Param : {0} not found in the response".format(param)


        except Exception,e:
            traceback.print_exc()
            print "Failure. Param : {0} not found in the response".format(param)

    return None


def storeUserDefinedVariables(vars):
    if vars is None:
        return

    vars=vars.strip()

    allVars=[]

    if "\n" in vars:
        allVars=vars.split("\n")
    else:
        allVars.append(vars)

    for eachVar in allVars:
        print("Each Var is : {0}".format(eachVar))
        [key,val]=eachVar.split(userConfig.data_splitter, 1)
        val = replacePlaceHolders(val)

        #random("TR",12,"")
        if val.lower().startswith("random("):
            val=val.replace("random(","").replace(")","")
            val=val.replace("RANDOM(","").replace(")","")
            val = val.split(",")
            prefix = numberOfChars = suffix = pool = exclusions = ""
            if (5 == len(val)):
                pool = val[4]
            if (3 < len(val)):
                exclusions = val[3]
            prefix, numberOfChars, suffix =  val[0:3]
            val = test_data_helper.random_value(prefix, numberOfChars,
                                             suffix, exclusions, pool)
        elif val.startswith("genesisToken"):
            command = "node token.js " + dynamicConfig.currentUrl
            print(command)
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            val, err = process.communicate()

        elif val.startswith("generateAccessToken"):
            val = val.replace("generateAccessToken(","").replace(")","")
            authHeader=val
            val="Bearer "+cxs_lib.generateAccessToken(authHeader)

        elif val.startswith("encryptValueTraditional"):
            val = val.replace("encryptValueTraditional(","").replace(")","")
            (email,password)=val.split(",")
            val=cxs_lib.encryptValueTraditional(email,password)
            if val is None:
                customWriteTestStep("Failed to encrypt email,password with public key. Local webservice might be down",
                                    "NA","NA","Failed")
            else:
                customWriteTestStep("Encrypt login using values:\n[Email: {0}]\n[Password: {1}]".format(email,password),
                                    "Fetch encrypted login",
                                    "Encrypted Login : {0}".format(val), "Passed")

        elif val.startswith("encryptValueSocial"):
            val = val.replace("encryptValueSocial(","").replace(")","")
            socialProvider="googleplus"
            socialToken=val

            val=cxs_lib.encryptValueSocial(socialProvider,socialToken)
            if val is None:
                customWriteTestStep("Failed to encrypt email,password with public key. Local webservice might be down",
                                     "NA","NA","Failed")
            else:
                customWriteTestStep("Encrypt Request Body using RSA",
                                     "Should be able to encrypt using local webservice",
                                     "Encrypted value: {0}".format(val), "Passed")

        elif val.startswith("encryptValueSocialWithPassword"):
            socialToken="hello world todo"
            val = val.replace("encryptValueSocialWithPassword(","").replace(")","")
            #password=valsocialProvider
            (socialProvider,password)=val.split(",")
            val=cxs_lib.encryptValueSocialWithPassword(socialToken,socialProvider, password)
            if val is None:
                customWriteTestStep("Failed to encrypt email,password with public key. Local webservice might be down",
                                    "NA", "NA", "Failed")

        elif val.startswith("socialEncodedLogin"): #returns encrypted token
            (socialToken,cxsEncodedLogin)=cxs_lib.socialEncodedLogin()

            if socialToken is None:
                customWriteTestStep("Fetch Social Token", "Should be able to fetch social token",
                                    "Unable to fetch token, check execution logs for details", "Failed")
            else:
                customWriteTestStep("Fetch Social Token", "Should be able to fetch social token",
                                    "Social token fetched : {0}".format(socialToken), "Passed")

            if cxsEncodedLogin is None:
                customWriteTestStep("RSA Encrypt Social login", "Should be able to encrypt",
                                    "Encryption failed, check execution logs for details","Failed")
            else:
                customWriteTestStep("RSA Encrypt Social login", "Should be able to encrypt",
                                    "Encrypted value : {0}".format(cxsEncodedLogin), "Passed")

            val=cxsEncodedLogin

        elif val.startswith("getCookieFor1Gie"): #returns cookie via browser
            oneGieCookie=cxs_lib.getCookieFor1Gie()

            if oneGieCookie is None:
                customWriteTestStep("Fetch Cookie For Auth", "Should be able to fetch cookie",
                                    "Unable to fetch cookie, check execution logs for details", "Failed")
            else:
                customWriteTestStep("Fetch Cookie For Auth", "Should be able to fetch cookie",
                                    "Cookie fetched : {0}".format(oneGieCookie), "Passed")
            val=oneGieCookie

        elif val.startswith("RandomInt("):
            val = val.replace("RandomInt(","").replace(")","")
            [minValue, maxValue] = val.split(",")
            val = testDataHelper.random_int(minValue, maxValue)

        elif val.startswith("Split("):
            val = val.replace("Split(","").replace(")","")
            [baseString, delimiter, index] = val.split(",")
            val = testDataHelper.split(baseString, delimiter, index)

        elif val.lower().startswith("timestamp"):
            val = val.replace("timestamp(","").replace(")","")
            val = test_data_helper.generate_timestamp(val)

        elif val.lower().startswith("sleep"):
            val=int(val.replace("sleep(","").replace)(")","")
            customUtils.sleep(val)

        elif val.lower().startswith("subtract"):
            try:
                print("Inside substract operation")

                val=val.replace("subtract(","").replace(")","")
                [val1,val2]=val.split(",")
                try:
                    val1=float(val1.strip())
                    val2=float(val2.strip())
                    val="{:.2f}".format(val1-val2)

                except:
                    traceback.print_exc()
                    customWriteTestStep("Subtract functions requires only integer/float as arguments",
                                        "NA", "Arg1: {0}\nArg2:{1}".format(val,val2), "Failed")

            except:
                print("[ERROR] Subtract operation")
                traceback.print_exc()
                customWriteTestStep("Excepting handling subtract operation", "NA",
                                    "{0}".format(traceback.format_exc()), "Fail")

        elif val.lower().startswith("compareBalance"):
            try:
                #compareBalance(InitialBalance, FinalBalance, ExpectedValue)
                print("Inside compareBalance operation")

                val=val.replace("compareBalance(","").replace(")","")
                [val1,val2,expectedValue]=val.split(",")
                try:
                    val1=float(val1.strip())
                    val2=float(val2.strip())
                    val="{:.2f}".format(val1-val2)
                    expectedValue="{:.2f}".format(expectedValue)

                    if str(expectedValue)==str(val):
                        customWriteTestStep("Validate Balance", "Expected balance: {0}".format(expectedValue),
                                            "Actual balance:{0}".format(val), "Passed")
                    else:
                        customWriteTestStep("Validate Balance", "Expected balance: {0}".format(expectedValue),
                                            "Actual balance:{0}".format(val), "Failed")
                except:
                    traceback.print_exc()
                    customWriteTestStep("Subtract functions requires only integer/float as arguments", "NA",
                                        "Arg1: {0}\nArg2:{1}".format(val,val2), "Failed")

            except:
                print("[ERROR] compareBalance operation")
                traceback.print_exc()
                customWriteTestStep("Excepting handling subtract operation", "NA",
                                    "{0}".format(traceback.format_exc()), "Fail")
        SystemConfig.localRequestDict[key]=val

def keywordBasedHandling(val):
    val=val.replace("func_","")
    if val.startswith("compareBalance"):
        try:
            print("Inside compareBalance operation")

            val=val.replace("compareBalance(","").replace(")","")
            [val1,val2,actualBalance]=val.split(",")
            try:
                initialBal=replacePlaceHolders(val1)
                promoPrice=replacePlaceHolders(val2)
                initialBal=float(initialBal.strip())
                promoPrice=float(promoPrice.strip())

                expectedValue="{:.2f}".format(initialBal-promoPrice)
                actualBalanceFromServer=float(getResponseFieldValue(actualBalance))

                if actualBalanceFromServer is None:
                    customWriteTestStep("Compare balance", "[balance] field should be present in response body",
                                        "[balance] field not found in response body", "Failed")
                    return

                val="{:.2f}".format(actualBalanceFromServer) #this is actual value from server side

                if str(expectedValue)==str(val):
                    customWriteTestStep("Validate Balance", "Expected balance: {0}".format(expectedValue),
                                        "Actual balance:{0}".format(val), "Passed")
                else:
                    customWriteTestStep("Validate Balance", "Expected balance: {0}".format(expectedValue),
                                        "Actual balance:{0}".format(val),"Failed")
            except:
                traceback.print_exc()
                customWriteTestStep("Exception encountered", "NA",
                                    "{0}".format(traceback.format_exc()), "Failed")
        except:
            print("[ERROR] compareBalance operation")
            traceback.print_exc()
            customWriteTestStep("Exception encountered","NA","{0}".format(traceback.format_exc()),"Failed")

def responseParsingViaCode(val):
    val=val.replace("type_","")
    expectedFieldType=val.split(userConfig.data_splitter)[1]
    val=val.split(userConfig.data_splitter)[0]
    print("Type of responseText is : {0}".format(type(dynamicConfig.responseText)))

    #ini_string = json.dumps(dynamicConfig.responseText)
    print("Response is : {0}".format(dynamicConfig.responseText))
    try:
        res = json.loads(dynamicConfig.responseText)
        print("Final dict is : {0}".format(res))
        #res=eval(final_dictionary[])
        #print(res['error']['message'])
        try:
            responseBody=""
            exec('responseBody='+val)
            print("responseBody is : ",responseBody)
            try:
                responseBody=responseBody.encode("utf-8")
                print("After decoding responseBody is : ",responseBody)
                print("Type of responseBody is : ",type(responseBody))
                #time.sleep(10)
            except:
                print("Cant decode to unicode : {0}".format(responseBody))

            customWriteTestStep("Schema validation - field check", "{0} should be present in response body".format(val),
                                "Same as expected","Passed")

            if str(expectedFieldType).strip().lower() in str(type(responseBody)):
                customWriteTestStep("Data-Type check for field {0}".format(val),
                                    "Expected data type: {0}".format(expectedFieldType),
                                    "Actual data type: {0}".format(type(responseBody)), "Passed")
            else:
                customWriteTestStep("Data-Type check for field {0}".format(val),
                                    "Expected data type: {0}".format(expectedFieldType),
                                    "Actual data type: {0}".format(type(responseBody)),
                                    "Failed")

        except KeyError as keyerror:
            customWriteTestStep("Response validation failure", "{0} was not found in response body".format(val),
                                "{0} was expected in response body".format(val), "Failed")
            customWriteTestStep("Log Exception", "NA",
                                "{0}".format(traceback.format_exc()), "Failed")
    except Exception:
        traceback.print_exc()
        customWriteTestStep("Log Exception","NA","{0}".format(traceback.format_exc()),"Failed")
        customWriteTestStep("Response validation failure",
                            "{0} was not found in response body".format(val),
                            "{0} was expected in response body".format(val), "Failed")

def get_result_code():
    actual = None
    is_found = False
    try:
        res = json.loads(dynamicConfig.responseText)
        if 'result_code' in res.keys() and not is_found:
            print "[INF] Result Code found in Response Body"
            return str(res['result_code'])

        if 'cca' in res.keys() and not is_found:
            cca = ast.literal_eval(res['cca'])
            if 'RESULT-CODE' in cca.keys():
                print "[INF] Result Code found in 'cca' in the Response Body"
                return str(cca['RESULT-CODE'])

        print "[WARN] Result Code not found in the Response Body"
        return None
    except Exception as e:
        print "[ERR] Exception occured on getting the result_code: " + str(e)
        return None

def responseParsingViaResult(val):
    val = val.replace("result_code_check_", "")
    actual = None
    is_found = False
    actual = get_result_code()
    if actual is None:
        print ("[FAILURE] Result Code is not found in the response. "
               "Response Status Code is {0}".format(dynamicConfig.responseStatusCode))
        customWriteTestStep("Result Code Checking", "Expected value : {0}".format(val),
                            "Result Code is not found in the Response Body. " +
                            "Response status code is {0}".format(dynamicConfig.responseStatusCode), "Fail")
        return
    if val == actual:
        print ("[SUCCESS] Result Code is found in the response. "
               "{0} is same as expected : {1}".format(actual,val))
        customWriteTestStep("Result Code Checking","Expected value : {0}".format(val),
                            "Actual value : {0}".format(actual), "Pass")
    else:
        print ("[FAILURE] Result Code is found in the response but "
               "value : {0} is NOT same as expected : {1}".format(actual,val))
        customWriteTestStep("Result Code Checking","Expected value : {0}".format(val),
                            "Actual value : {0}".format(actual), "Fail")

def validate_math(expression, expectedValue):
    returnVal = customUtils.parseArithmeticExp(expression)

    if "Custom404" == str(returnVal):
        customWriteTestStep("Arithmetic exp failed to evaluate : {0}".format(expression),
                            "NA", "NA", "Fail")
    customStatus="Fail"
    if float(returnVal)==float(expectedValue):
        customStatus="Pass"
    customWriteTestStep("Evaluate Arithmetic expression ".format(expression),
                        "Expected val:{0}".format(val),
                        "Actual val: {0}".format(returnVal), str(customStatus))

def listParsing():
    myList=[
 {
  "retailer_name": "JIMTHEL",
  "retailer_subtype": "Auto Repair Shop",
  "retailer_tier": "GOLD",
  "selling_sims": "Not Selling",
  "monthly_sellout": "20000",
  "retailer_mobtel": "9156814668",
  "location": {
   "barangay": "7602025",
   "city": "7602",
   "coordinates": {
    "lat": "14.550733",
    "lon": "121.025807"
   }
  }
 },
 {
  "retailer_name": "CP",
  "retailer_subtype": "Auto Repair Shop",
  "retailer_tier": "BRONZE",
  "selling_sims": "Not Selling",
  "monthly_sellout": "4000",
  "retailer_mobtel": "9165088461",
  "location": {
   "barangay": "7602025",
   "city": "7602",
   "coordinates": {
    "lat": "14.550826",
    "lon": "121.024356"
   }
  }
 }
]


    myList=str(myList)

    print(type(myList))

