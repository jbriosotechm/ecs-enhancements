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
import dynamicConfig
import re
import random
import datetime
import json
import urllib
import string
import ast
import parserMain
import cxs_lib
from customUtils import customWriteTestStep,endProcessing,replacePlaceHolders, getIndexNumber, find_element_using_path,parseArithmeticExp
from commonLib import *


def executeCommand(vars):

    # random number
    # timestamps of different formats
    # Assignments tab

    if vars is not None:
        vars =vars.strip()
        if not vars:
            return

        allVars =[]

        if "\n" in vars:
            allVars =vars.split("\n")
        else:
            allVars.append(vars)


        for val in allVars:

            if val.lower().startswith("sleep"):
                try:
                    val =int(str(val.replace("sleep(" ,"").replace(")" ,"")).strip())
                    print("[User-Command] Will sleep for {0} seconds".format(val))
                    time.sleep(val)
                    customWriteTestStep("Wait before proceeding to next step for {0} seconds".format(val), "Should wait" ,"Waited for: {0} seconds".format(val) ,"Passed")
                except:
                    print("[ERROR] Invalid argument for Sleep command : {0}".format(val))
                    customWriteTestStep("Wait before proceeding to next step for {0} seconds".format(val), "The argument passed should be an Integer"
                                        ,"The argument passed is Invalid : {0}".format(val) ,"Passed")

            elif val.lower().startswith("terminateonfailure"):
                try:
                    if dynamicConfig.testCaseHasFailed:
                        print("[User-Command] Terminate on failure")
                        val =str(val.replace("terminateonfailure(" ,"").replace(")" ,"")).strip()
                        if val.lower( )=="true":
                            customWriteTestStep("Terminating flow since failure is encountered" ,"NA" ,"NA" ,"Failed")
                            Report.evaluateIfTestCaseIsPassOrFail()
                            endProcessing()
                except:
                    print("[ERROR] Invalid argument for TerminateOnFailure command : {0}".format(val))
                    customWriteTestStep("Invalid argument for TerminateOnFailure command : {0}".format(val), "The argument passed should be either yes or no" ,"Invalid argument" ,"Failed")


            elif val.lower().startswith("validatefor1gie"):
                # endpoint validation for 1gie
                print("[User-Command] validateFor1Gie")
                pathForValidation =val.replace("validateFor1Gie_" ,"")
                try:
                    if dynamicConfig.responseHeaders and 'json' in str \
                            (dynamicConfig.responseHeaders['Content-Type']).lower():
                        parserMain.main(pathForValidation, dynamicConfig.responseText)

                    else:
                        customWriteTestStep("Skipping schema valdiation since reponse body is not in JSON format"
                                            ,"Response Body should be in JSON" ,"Response Body not in JSON" ,"Failed")

                except Exception as e:
                    customWriteTestStep("Exception" ,"NA" ,str(e) ,"Failed")


            elif val.lower().startswith("skiponfailure"):
                try:
                    if dynamicConfig.testCaseHasFailed:
                        print("[User-Command] SkipOnFailure")
                        val =int(str(val.replace("skiponfailure(" ,"").replace(")" ,"")).strip())
                        # if val=="True":
                        # customWriteTestStep("Skipping to Test Case [{0}] since failure is encountered".format(val),"NA","NA","Failed")
                        testCaseNumberToSkipT o =val

                        i f(testCaseNumberToSkipT o< =SystemConfig.endRow):
                            rowNumberWhichFaile d =SystemConfig.currentRow
                            SystemConfig.currentRo w =testCaseNumberToSkipTo
                            customWriteTestStep \
                                ("Skip to TC #{0} since failure is encountered".format(testCaseNumberToSkipTo) ,"NA"
                                ,"NA".format(SystemConfig.endRow) ,"Failed")
                            testCaseNumberToSkipT o =val
                            Report.evaluateIfTestCaseIsPassOrFail()
                            # print "Row# which failed : ",rowNumberWhichFailed

                            markInBetweenTestCasesBlocked(rowNumberWhichFailed ,testCaseNumberToSkipTo)
                        else:
                            customWriteTestStep("TC#:{0} to skip to does not exist.".format(testCaseNumberToSkipTo)
                                                ,"The TC# to skip to should be within the range of total # of TCs"
                                                ,"Max TCs {0}: ".format(SystemConfig.endRow) ,"Failed")


                except:
                    traceback.print_exc()
                    print("[ERROR] Invalid argument for SkipOnFailure command : {0}".format(val))
                    customWriteTestStep("Invalid argument for SkipOnFailure command : {0}".format(val), "The argument passed should be an Integer" ,"Invalid argument" ,"Failed")

            elif val.lower().startswith("skipalways"):
                try:
                    if True:
                        print("[User-Command] Skip-Always")
                        va l =int(str(val.replace("skipalways(" ,"").replace(")" ,"")).strip())
                        # if val=="True":
                        # customWriteTestStep("Skipping to Test Case [{0}] since failure is encountered".format(val),"NA","NA","Failed")
                        testCaseNumberToSkipT o =val

                        i f(testCaseNumberToSkipT o< =SystemConfig.endRow):
                            rowNumberWhichFaile d =SystemConfig.currentRow
                            SystemConfig.currentRo w =testCaseNumberToSkipTo
                            # customWriteTestStep("Skip to TC #{0} since failure is encountered".format(testCaseNumberToSkipTo),"NA","NA".format(SystemConfig.endRow),"Failed")
                            testCaseNumberToSkipT o =val
                            Report.evaluateIfTestCaseIsPassOrFail()
                            # print "Row# which failed : ",rowNumberWhichFailed

                            # markInBetweenTestCasesBlocked(rowNumberWhichFailed,testCaseNumberToSkipTo)
                        else:
                            customWriteTestStep("TC#:{0} to skip to does not exist.".format(testCaseNumberToSkipTo)
                                                ,"The TC# to skip to should be within the range of total # of TCs"
                                                ,"Max TCs {0}: ".format(SystemConfig.endRow) ,"Failed")


                except:
                    traceback.print_exc()
                    print("[ERROR] Invalid argument for SkipOnFailure command : {0}".format(val))
                    customWriteTestStep("Invalid argument for SkipOnFailure command : {0}".format(val), "The argument passed should be an Integer" ,"Invalid argument" ,"Failed")

            else:
                parseAndValidateResponse(val)

