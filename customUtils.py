import sys,os
sys.path.append("customLib")
import customLib.Report as Report
import SystemConfig,userConfig
import traceback
import dynamicConfig
from bs4 import BeautifulSoup
import xmltodict

debugFlag=True

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
        customWriteTestStep("User-Input error","Undefined variable used","Only variables which are defined can be used","Fail")
        endProcessing()
    return var

def endProcessing():
    Report.GeneratePDFReport()
    os._exit(-1)

def customWriteTestStep(TestStepDesc,ExpectedResult, ActualResult,StepStatus):
    if "fail" in StepStatus.lower():
        dynamicConfig.testCaseHasFailed=True
        StepStatus="Failed"
    elif "pass" in StepStatus.lower():
        StepStatus="Passed"

    TestStepDesc = "[Test Step #{0}] ".format(dynamicConfig.testStepNo) + TestStepDesc
    Report.WriteTestStep(TestStepDesc,ExpectedResult, ActualResult,StepStatus)

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
            customWriteTestStep('Capture VolumeRemaining for Wallet : {0}'.format(walletName),"Capture Volume Remaining","Volume Remaining : {0}".format(volume),"Pass")
            return volume

        customWriteTestStep('Capture VolumeRemaining for Wallet : {0}'.format(walletName),"Capture Volume Remaining","Unable to capture Volume Remaining","Fail")
        return "-1"
    except Exception as e:
        print("Exception:",e)
    return "FieldNotFound"

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
