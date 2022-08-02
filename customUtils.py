import sys,os
sys.path.append("customLib")
import customLib.Report as Report
import SystemConfig,userConfig
import traceback
import dynamicConfig
from bs4 import BeautifulSoup



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
        while "#{" in arithmericExpression:
            ctr+=1
            if ctr>=maxLimit:
                return errorCode
            varToReplace=str(arithmericExpression).split("#{")[1].split("}#")[0]
            varValue=float(resolveVars(varToReplace))
            strToReplace="#{"+str(varToReplace)+"}#"
            arithmericExpression=arithmericExpression.replace(strToReplace,str(varValue))
        import numexpr
        arithValue=numexpr.evaluate(arithmericExpression).item()
        print("Arith value:",arithValue)
        return arithValue
    except Exception as e:
        print('Exception:',e)
    return errorCode


def resolveVars(var):
    #local vars get priority over Global vars
    #{}#
    var=str(var)
    if str(var).startswith("#{"):
        var=var.replace("#{","").replace("}#","")

    for key in SystemConfig.localRequestDict.keys():
        #stringToMatch = "#{" + key + "}#"
        if str(key)==str(var):
            return str(SystemConfig.localRequestDict[key])

    for key in SystemConfig.globalDict.keys():
        if str(key)==str(var):
            return str(SystemConfig.globalDict[key])



    if "#{" in var and "}#" in var:
            print "Failure: Undefined variable usage"
            customWriteTestStep("User-Input error","Undefined variable used","Only variables which are defined can be used","Fail")
            endProcessing()

    return var


def replacePlaceHolders(var):
    #local vars get priority over Global vars
    for key in SystemConfig.localRequestDict.keys():
        stringToMatch = "#{" + key + "}#"
        if stringToMatch in var:
            var = var.replace(stringToMatch,str(SystemConfig.localRequestDict[key]))

    for key in SystemConfig.globalDict.keys():
        stringToMatch = "#{" + key + "}#"
        if stringToMatch in var:
            var = var.replace(stringToMatch,str(SystemConfig.globalDict[key]))



    if "#{" in var and "}#" in var:
            print "Failure: Undefined variable usage"
            customWriteTestStep("User-Input error","Undefined variable used","Only variables which are defined can be used","Fail")
            endProcessing()

    return var


def endProcessing():
    Report.GeneratePDFReport()
    os._exit(-1)
    #sys.exit(-1)

def getVariableValue(varName):

    try:
        if "#{" in varName and "}#" in varName:

            varName=varName.replace("#{","").replace("}#","")

            if varName in SystemConfig.localRequestDict.keys():
                return SystemConfig.localRequestDict[varName]

            if varName in SystemConfig.globalDict.keys():
                return SystemConfig.globalDict[varName]


    except:
        traceback.print_exc()

    return None



def customWriteTestStep(TestStepDesc,ExpectedResult, ActualResult,StepStatus):

    if "fail" in StepStatus.lower():
        dynamicConfig.testCaseHasFailed=True
        StepStatus="Failed"

    if "pass" in StepStatus.lower():
        StepStatus="Passed"

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

