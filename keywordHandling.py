import sys,time
import string
sys.path.append("customLib")
import cxs_lib
import SystemConfig,userConfig
import customLib.Report as Report
import customUtils
from customUtils import customWriteTestStep,endProcessing,replacePlaceHolders,getVariableValue
import time,traceback
import dynamicConfig
import json

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

    #random number
    #timestamps of different formats
    #Assignments tab
    print("storeUserDefinedVariables")

    if vars is not None:
            vars=vars.strip()

            allVars=[]

            if "\n" in vars:
                allVars=vars.split("\n")
            else:
                allVars.append(vars)


            for eachVar in allVars:
                print("Each Var is : {0}".format(eachVar))
                [key,val]=eachVar.split(":", 1)
                if "#{" in val and "}#" in val:
                    val = replacePlaceHolders(val)

                #random("TR",12,"")
                if val.lower().startswith("random("):
                    val=val.replace("random(","").replace(")","")
                    val=val.replace("RANDOM(","").replace(")","")
                    #random("TR", 12, "", [number alpha special], "abc123")
                    if 2 == val.count(','):
                        [prefix, numberOfChars, suffix]=val.split(",")
                        randomPool = string.digits
                    elif 3 <= val.count(','):
                        randomPool = ""
                        exclusions = ""
                        if 3 == val.count(','):
                            [prefix, numberOfChars,suffix, pool] = val.split(",")
                        elif 4 == val.count(','):
                            [prefix, numberOfChars,suffix, pool, exclusions] = val.split(",")

                        if "numbers" in pool:
                            randomPool += string.digits
                        if "alpha" in pool:
                            randomPool += string.ascii_letters
                        if "special" in pool:
                            randomPool += string.punctuation

                        for char in SystemConfig.fixedExclusions:
                            randomPool = randomPool.replace(char, "")
                        for char in exclusions:
                            randomPool = randomPool.replace(char, "")

                    noOfChars=int(numberOfChars)-len(prefix)-len(suffix)

                    if noOfChars>0:
                        filler=""
                        itr=0
                        while itr<noOfChars:
                            filler+=random.choice(randomPool)
                            itr+=1

                        val=prefix+filler+suffix
                    else:
                        val=prefix+suffix
                # RandomInt(1,10)

                elif val.startswith("generateAccessToken"):
                    val = val.replace("generateAccessToken(","").replace(")","")
                    authHeader=val
                    val="Bearer "+cxs_lib.generateAccessToken(authHeader)


                elif val.startswith("encryptValueTraditional"):
                    val = val.replace("encryptValueTraditional(","").replace(")","")
                    (email,password)=val.split(",")
                    val=cxs_lib.encryptValueTraditional(email,password)
                    if val is None:
                        Report.WriteTestStep("Failed to encrypt email,password with public key. Local webservice might be down","NA","NA","Failed")
                    else:
                        Report.WriteTestStep("Encrypt login using values:\n[Email: {0}]\n[Password: {1}]".format(email,password),"Fetch encrypted login","Encrypted Login : {0}".format(val),"Passed")

                elif val.startswith("encryptValueSocial"):

                    val = val.replace("encryptValueSocial(","").replace(")","")
                    socialProvider="googleplus"
                    socialToken=val

                    val=cxs_lib.encryptValueSocial(socialProvider,socialToken)
                    if val is None:
                        Report.WriteTestStep("Failed to encrypt email,password with public key. Local webservice might be down","NA","NA","Failed")
                    else:
                        Report.WriteTestStep("Encrypt Request Body using RSA","Should be able to encrypt using local webservice","Encrypted value: {0}".format(val),"Passed")

                elif val.startswith("encryptValueSocialWithPassword"):
                    socialToken="hello world todo"
                    val = val.replace("encryptValueSocialWithPassword(","").replace(")","")
                    #password=valsocialProvider
                    (socialProvider,password)=val.split(",")
                    val=cxs_lib.encryptValueSocialWithPassword(socialToken,socialProvider, password)
                    if val is None:
                        Report.WriteTestStep("Failed to encrypt email,password with public key. Local webservice might be down","NA","NA","Failed")

                elif val.startswith("socialEncodedLogin"): #returns encrypted token
                    (socialToken,cxsEncodedLogin)=cxs_lib.socialEncodedLogin()

                    if socialToken is None:
                        Report.WriteTestStep("Fetch Social Token","Should be able to fetch social token","Unable to fetch token, check execution logs for details","Failed")
                    else:
                        Report.WriteTestStep("Fetch Social Token","Should be able to fetch social token","Social token fetched : {0}".format(socialToken),"Passed")


                    if cxsEncodedLogin is None:
                        Report.WriteTestStep("RSA Encrypt Social login","Should be able to encrypt","Encryption failed, check execution logs for details","Failed")
                    else:
                        Report.WriteTestStep("RSA Encrypt Social login","Should be able to encrypt","Encrypted value : {0}".format(cxsEncodedLogin),"Passed")

                    val=cxsEncodedLogin


                elif val.startswith("getCookieFor1Gie"): #returns cookie via browser
                    oneGieCookie=cxs_lib.getCookieFor1Gie()

                    if oneGieCookie is None:
                        Report.WriteTestStep("Fetch Cookie For Auth","Should be able to fetch cookie","Unable to fetch cookie, check execution logs for details","Failed")
                    else:
                        Report.WriteTestStep("Fetch Cookie For Auth","Should be able to fetch cookie","Cookie fetched : {0}".format(oneGieCookie),"Passed")

                    val=oneGieCookie


                elif val.startswith("RandomInt("):
                    val = val.replace("RandomInt(","").replace(")","")
                    [minValue, maxValue] = val.split(",")

                    val = random.randint(int(minValue), int(maxValue))
                # Split(hello.123, ., 1)
                elif val.startswith("Split("):
                    val = val.replace("Split(","").replace(")","")
                    [baseString, delimiter, index] = val.split(",")

                    baseString = baseString.split(delimiter)
                    val = baseString[int(index)]
                # timestamp(yyyy-mm-dd)
                elif val.lower().startswith("timestamp"):
                    #timestamp(DDMMYYYY)
                    val = val.replace("timestamp(","").replace(")","")
                    if "epoch" in val:
                        val=int(time.time())
                    else:
                        val=generateTimestamp(val)

                    #timestamp(DDMMYYYY)
                    # val=val.replace("theiaDoubleEncode(","").replace(")","")
                    # val=theiaDoubleEncode(val)



                elif val.lower().startswith("sleep"):
                    try:
                        val=int(val.replace("sleep(","").replace)(")","")
                        time.sleep(val)
                        customWriteTestStep("Wait before proceeding to next step for {0} seconds".format(val), "Should wait","Waited for: {0} seconds".format(val),"Passed")
                    except:
                        print("[ERROR] Invalid argument for Sleep command : {0}".format(val))
                        customWriteTestStep("Wait before proceeding to next step for {0} seconds".format(val), "The argument passed should be an Integer","The argument passed is Invalid : {0}".format(val),"Pass")

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
                            customWriteTestStep("Subtract functions requires only integer/float as arguments","NA","Arg1: {0}\nArg2:{1}".format(val,val2),"Failed")

                    except:
                        print("[ERROR] Subtract operation")
                        traceback.print_exc()
                        customWriteTestStep("Excepting handling subtract operation", "NA","{0}".format(traceback.format_exc()),"Fail")

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
                                customWriteTestStep("Validate Balance","Expected balance: {0}".format(expectedValue),"Actual balance:{0}".format(val),"Passed")
                            else:
                                customWriteTestStep("Validate Balance","Expected balance: {0}".format(expectedValue),"Actual balance:{0}".format(val),"Failed")
                        except:
                            traceback.print_exc()
                            customWriteTestStep("Subtract functions requires only integer/float as arguments","NA","Arg1: {0}\nArg2:{1}".format(val,val2),"Failed")

                    except:
                        print("[ERROR] Subtract operation")
                        traceback.print_exc()
                        customWriteTestStep("Excepting handling subtract operation", "NA","{0}".format(traceback.format_exc()),"Fail")


                SystemConfig.localRequestDict[key]=val

def keywordBasedHandling(val):

    #func_compareBalance(#{initialBal}#,#{price}#,balance)
    #compareBalance(#{initialBal}#,#{price}#,balance)

    val=val.replace("func_","")


    if val.startswith("compareBalance"):
        try:
            print("Inside compareBalance operation")

            val=val.replace("compareBalance(","").replace(")","")
            [val1,val2,actualBalance]=val.split(",")
            try:
                initialBal=getVariableValue(val1)
                promoPrice=getVariableValue(val2)
                initialBal=float(initialBal.strip())
                promoPrice=float(promoPrice.strip())

                expectedValue="{:.2f}".format(initialBal-promoPrice)
                actualBalanceFromServer=float(getResponseFieldValue(actualBalance))

                if actualBalanceFromServer is None:
                    customWriteTestStep("Compare balance","[balance] field should be present in response body","[balance] field not found in response body","Failed")
                    return

                val="{:.2f}".format(actualBalanceFromServer) #this is actual value from server side

                if str(expectedValue)==str(val):
                    customWriteTestStep("Validate Balance","Expected balance: {0}".format(expectedValue),"Actual balance:{0}".format(val),"Passed")
                else:
                    customWriteTestStep("Validate Balance","Expected balance: {0}".format(expectedValue),"Actual balance:{0}".format(val),"Failed")
            except:
                traceback.print_exc()
                customWriteTestStep("Exception encountered","NA","{0}".format(traceback.format_exc()),"Failed")


        except:
            print("[ERROR] compareBalance operation")
            traceback.print_exc()
            customWriteTestStep("Exception encountered","NA","{0}".format(traceback.format_exc()),"Failed")

def responseParsingViaCode(val):

    val=val.replace("type_","")
    expectedFieldType=val.split(":")[1]
    val=val.split(":")[0]
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

            customWriteTestStep("Schema validation - field check","{0} should be present in response body".format(val),"Same as expected","Passed")

            if str(expectedFieldType).strip().lower() in str(type(responseBody)):
                customWriteTestStep("Data-Type check for field {0}".format(val),"Expected data type: {0}".format(expectedFieldType),"Actual data type: {0}".format(type(responseBody)),"Passed")
            else:
                customWriteTestStep("Data-Type check for field {0}".format(val),"Expected data type: {0}".format(expectedFieldType),"Actual data type: {0}".format(type(responseBody)),"Failed")

        except KeyError as keyerror:
            customWriteTestStep("Response validation failure","{0} was not found in response body".format(val),"{0} was expected in response body".format(val),"Failed")
            customWriteTestStep("Log Exception","NA","{0}".format(traceback.format_exc()),"Failed")



    except Exception:
        traceback.print_exc()
        customWriteTestStep("Log Exception","NA","{0}".format(traceback.format_exc()),"Failed")
        customWriteTestStep("Response validation failure","{0} was not found in response body".format(val),"{0} was expected in response body".format(val),"Failed")


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

