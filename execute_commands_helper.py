import os, sys
sys.path.append(".")
sys.path.append("customLib")
import subprocess
import logging, traceback

import SystemConfig
import userConfig
import dynamicConfig
import customLib.Report as Report
import excel_helper as eh
import parserMain
import customUtils as cu
import test_data_helper
import math
import keywordHandling
import json

sys.path.append("customLib")
import customLib.customLogging as customLogging

def append_consumption_request(type, data):
    current_request = "*************** [ Request for {0} ] ***************".format(type)
    current_request += "\nURL : {0}\n\nHeaders : {1}\n\nBody: {2}".format(dynamicConfig.currentUrl,
                       dynamicConfig.currentHeader, dynamicConfig.currentRequest)
    current_request += "\n"
    SystemConfig.current_consumption_content += current_request

def append_consumption_response(type, data):
    current_response = "*************** [ Response for {0} ] ***************".format(type)
    current_response += "\nStatus Code : {0}\n\nHeaders : {1}\n\nBody : {2}".format(dynamicConfig.responseStatusCode,
                        dynamicConfig.responseHeaders, dynamicConfig.responseText)
    current_response += "\nResponse time : {0} seconds\nNote : Response time = Server Response time + Network Latency".format(dynamicConfig.responseTime)
    current_response += "\n\n\n"

    SystemConfig.current_consumption_content += current_response

def trigger_consume_data(type, data=None):
    matchedRow           = eh.get_row_number_of_string(type)
    endPoint             = eh.get_cell_value(matchedRow, SystemConfig.col_EndPoint)
    requestStructure     = eh.get_cell_value(matchedRow, SystemConfig.col_API_Structure)
    rawHeaderText        = eh.get_cell_value(matchedRow, SystemConfig.col_Headers)
    typeOfRequest        = eh.get_cell_value(matchedRow, SystemConfig.col_Method)
    authenticationParams = eh.get_cell_value(matchedRow, SystemConfig.col_Authentication)
    dynamicConfig.restRequestType=typeOfRequest.strip().lower()
    typeOfRequest+="(rest)"

    cc_request_type = cu.get_request_parameter(requestStructure, "cc_request_type")
    cu.add_request_parameters("cc_request_number={0}".format(str(SystemConfig.cc_request_number)))
    SystemConfig.cc_request_number += 1

    if type == "initData" and cc_request_type == "1":
        SystemConfig.session_id = "tb_ugwgy01;3757027;380;"
        time_epoch = test_data_helper.generate_timestamp("epoch")
        SystemConfig.session_id += str(time_epoch)

    if SystemConfig.session_id is None:
        print("[WARN] Session ID was not generated")
    else:
        cu.add_request_parameters("session_id={0}".format(SystemConfig.session_id))

    headers = cu.parseHeader(rawHeaderText)
    if data is None:
        data = 0
        cu.add_request_parameters("cc_total_octets=0")
    else:
        data = data * 1000000
        if '.' in str(data):
            tmp = str(data).split('.')[0]
        else:
            tmp = str(data)
        cu.add_request_parameters("cc_total_octets={0}".format(tmp))
    requestStructure = cu.parametrizeRequest(requestStructure, dynamicConfig.requestParameters)
    cu.set_dynamic_request(requestStructure)

    dynamicConfig.currentUrl = endPoint

    data = data / 1000000
    append_consumption_request(type, data)
    will_create_file = False
    cu.triggerRestRequest(will_create_file)
    append_consumption_response(type, data)
    validate_result_code(type, data)

def validate_result_code(type, data):
    dynamicConfig.failed_consumption = False
    current_result_code = keywordHandling.get_result_code()
    if current_result_code == "2001":
        return True
    print("[ERR] Result code {0} is different from expected 2001 in {1}".format(current_result_code, type))
    dynamicConfig.failed_consumption = True
    req = json.loads(dynamicConfig.currentRequest)
    msisdn = req['subscription_id_data']
    session_id = req['session_id']
    rating_group = req['rating_group']
    apn = req['called_station_id']
    resp = json.loads(dynamicConfig.responseText)
    cca = None
    if 'cca' in resp.keys():
        cca = str(resp['cca'])
    filename = "DataConsumption_TC_{0}".format(dynamicConfig.testCaseNo - 1)
    cu.customWriteTestStep(SystemConfig.consume_data_test_case, "Log details of Data Consumption",
                           "Failed during {0} while consuming {1}mb for {2} using:\n\nSession ID: {3}\nRating group: {4}\nAPN: {5}\n\nCCA: {6}\n\nFull logs here: logs\\{7}.log".format(type, data,
                            msisdn, session_id, rating_group, apn, cca, filename), "Failed")
    customLogging.writeToLog(filename, SystemConfig.current_consumption_content)
    return False

def consume_data(data):
    SystemConfig.cc_request_number = 0
    SystemConfig.consume_data_test_case = "Triggering Consumption of {0}".format(data)
    print("[INF] {0}").format(SystemConfig.consume_data_test_case)
    data = data
    data = data.replace("mb", "")

    if '.' in data:
        data = float(data)
    else:
        data = int(data)

    SystemConfig.current_consumption_content = ""
    trigger_consume_data("initData")
    req = json.loads(dynamicConfig.currentRequest)
    msisdn = req['subscription_id_data']
    session_id = req['session_id']
    rating_group = req['rating_group']
    apn = req['called_station_id']

    while not dynamicConfig.failed_consumption and data > 900 :
        data -= 900
        trigger_consume_data("updateData", 900)

    if not dynamicConfig.failed_consumption:
        trigger_consume_data("terminateData", data)

    if not dynamicConfig.failed_consumption:
        filename = "DataConsumption_TC_{0}".format(dynamicConfig.testCaseNo - 1)
        cu.customWriteTestStep(SystemConfig.consume_data_test_case, "Log details of Data Consumption",
                               "Consumed {0}mb for {1} using:\n\nSession ID: {2}\nRating group: {3}\nAPN: {4}\n\nFull logs here: logs\\{5}.log".format(data,
                                msisdn, session_id, rating_group, apn, filename), "Passed")
        customLogging.writeToLog(filename, SystemConfig.current_consumption_content)

    import time

def check_excel_file(filename):
    filename = "{0}/target/Results/{1}/NFWebtool/NFWebtool.xlsx".format(userConfig.web_validation_location, filename)
    print(filename)
    test_steps = eh.read_results(filename)
    if test_steps == -1:
        print("[ERR] {0} cannot be found").format(filename)
        cu.customWriteTestStep("Checking Excel Report in {0}".format(filename),
                               "Excel Report should be present",
                               "Excel Report '{0}' is not located".format(filename), "Failed")
        return

    if test_steps == -2:
        cu.customWriteTestStep("Checking Excel Report in {0}".format(filename),
                               "Excel Report should have values",
                               "Excel Report '{0}' has no steps with status".format(filename), "Failed")
        return

    fail_count = 0
    if len(test_steps) > 0:
        for steps in test_steps:
            cu.customWriteTestStep(steps['Step Description'], steps['Expected'],
                                   steps['Actual'], steps['Status'], steps['Screenshot'])
            if "fail" in steps['Status'].lower():
                fail_count += 1

    if fail_count != 0:
        print("[ERR] {0} failing test steps are found in {1}").format(len(test_steps), filename)

def print_invalid_length(api, expected, actual):
    invalid_length = "[ERR] Invalid length of argument encountered in '{0}'. " \
                     "Encountered {1}, expected size is {2}".format(api, expected, actual)
    print (invalid_length)
    cu.customWriteTestStep("Validate User Input for {0}".format(api),
                           "Arguments should have {0} arguments".format(expected),
                           "Arguments only has {0} arguments".format(actual), "Failed")

def validate_user_input_for_excel(val):
    api = val[0]
    invalid_length = "[ERR] Invalid length of argument encountered in '{0}'. ".format(api)
    is_invalid_length = None
    api = api.lower()
    if api == "cpspromo" or api == "cpsnopromo" or api == "nfnopromo":
        expected_length = 4
        if len(val) != expected_length:
            print_invalid_length(api, len(val), expected_length)
            return -1

        print "[INF] Running {0} with Arguments: MSISDN={1}, Type={2} Excel={3}" \
              .format(api, val[1], val[2], val[3])
        command_line = 'mvn test -DAPI="{0}" -DMSISDN="{1}" -DType="{2}" -DFolder="{3}"' \
              .format(api, val[1], val[2], val[3])
        print("[DEBUG] Running:: " + command_line)
        return command_line

    elif api == "curlverify":
        expected_length = 4
        if len(val) != expected_length:
            print_invalid_length(api, len(val), expected_length)
            return -1

        print "[INF] Running {0} with Arguments: Type={1}, MSISDN={2} Excel={3}" \
              .format(api, val[1], val[2], val[3])
        command_line = 'mvn test -DAPI="{0}" -DType="{1}" -DMSISDN="{2}" -DFolder="{3}"' \
              .format(api, val[1], val[2], val[3])
        print("[DEBUG] Running:: " + command_line)
        return command_line

    elif api == "nfpromo":
        expected_length = 6
        if len(val) != expected_length:
            invalid_length += "Encountered {0}, expected size is {1}".format(len(val), expected_length)
            print_invalid_length(api, len(val), expected_length)
            return -1

        print "[INF] Running {0} with Arguments: MSISDN={1}, Status={2}, Value={3}, Type={4}, Excel={5}" \
              .format(api, val[1], val[2], val[3], val[4], val[5])
        command_line = 'mvn test -DAPI="{0}" -DMSISDN="{1}" -DStatus="{2}" -DValue="{3}" -DType="{4}" -DFolder="{5}"' \
              .format(api, val[1], val[2], val[3], val[4], val[5])
        print("[DEBUG] Running:: " + command_line)
        return command_line

    elif api == "curlprovision":
        expected_length = 5
        if len(val) != expected_length:
            invalid_length += "Encountered {0}, expected size is {1}".format(len(val), expected_length)
            print_invalid_length(api, len(val), expected_length)
            return -1

        print "[INF] Running {0} with Arguments: Brand={1}, Type={2}, MSISDN={3}, Excel={3}" \
              .format(api, val[1], val[2], val[3])
        command_line = 'mvn test -DAPI="{0}" -DBrand="{1}" -DType="{2}" -DMSISDN="{3}" -DFolder="{4}"' \
              .format(api, val[1], val[2], val[3], val[4])
        print("[DEBUG] Running:: " + command_line)
        return command_line

    elif api == "curlsms":
        expected_length = 4
        if len(val) != expected_length:
            invalid_length += "Encountered {0}, expected size is {1}".format(len(val), expected_length)
            print_invalid_length(api, len(val), expected_length)
            return -1
        print "[INF] Running {0} with Arguments: Offer={1}, MSISDN={2} Excel={3}" \
              .format(api, val[1], val[2], val[3])
        command_line = 'mvn test -DAPI="{0}" -DOffer="{1}" -DMSISDN="{2}" -DFolder="{3}"' \
              .format(api, val[1], val[2], val[3])
        print("[DEBUG] Running:: " + command_line)
        return command_line
    else:
        print ("[ERR] {0} is not supported".format(api))
        cu.customWriteTestStep("Validate User Input for {0}".format(api),
                               "API should be supported",
                               "{0} is not supported".format(api), "Failed")
        return -1

def trigger_java_web_validation(val):
    val = val.split("_")
    command = validate_user_input_for_excel(val)
    if command == -1:
        return

    p = subprocess.Popen(command, shell=True, cwd=userConfig.web_validation_location)
    p.wait()
    returnCode = p.poll()
    if returnCode != 0:
        print("[ERR] Encountered Return code {0} on triggering java script".format(str(returnCode)))
        cu.customWriteTestStep("Triggering Web Scripts from: {0}".format(userConfig.web_validation_location),
                               "Web Scripts should be triggered",
                               "Web Scripts was triggered but encountered Return Code {0}".format(returnCode), "Failed")
    check_excel_file(val[-1])

def parse(vars):
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
            val=int(str(val.replace("sleep(","").replace(")","")).strip())
            cu.sleep(val)

        elif val.lower().startswith("terminateonfailure"):
            try:
                if dynamicConfig.testCaseHasFailed:
                    print("[User-Command] Terminate on failure")
                    val = str(val.replace("terminateonfailure(","").replace(")","")).strip()
                    if val.lower() == "true":
                        cu.customWriteTestStep("Terminating flow since failure is encountered","NA","NA","Failed")
                        Report.evaluateIfTestCaseIsPassOrFail()
                        endProcessing()
            except:
                print("[ERROR] Invalid argument for TerminateOnFailure command : {0}".format(val))
                cu.customWriteTestStep("Invalid argument for TerminateOnFailure command : {0}".format(val),
                                       "The argument passed should be either yes or no",
                                       "Invalid argument", "Failed")

        elif val.lower().startswith("validatefor1gie"):
            # endpoint validation for 1gie
            print("[User-Command] validateFor1Gie")
            pathForValidation =val.replace("validateFor1Gie_" ,"")
            try:
                if dynamicConfig.responseHeaders and 'json' in str \
                        (dynamicConfig.responseHeaders['Content-Type']).lower():
                    parserMain.main(pathForValidation, dynamicConfig.responseText)

                else:
                    cu.customWriteTestStep("Skipping schema valdiation since reponse body is not in JSON format",
                                           "Response Body should be in JSON",
                                           "Response Body not in JSON", "Failed")
            except Exception as e:
                cu.customWriteTestStep("Exception", "NA", str(e), "Failed")

        elif val.startswith("math_"):
            val=val.replace("math_","")
            (arithmeticExpression,expectedValue) = val.split(":val_")
            keywordHandling.validate_math(arithmeticExpression, expectedValue)

        elif val.startswith("consume_data_"):
            val=val.replace("consume_data_","")
            consume_data(val)
        elif val.startswith("webvalidation_"):
            val=val.replace("webvalidation_","")
            trigger_java_web_validation(val)

        elif val.lower().startswith("skiponfailure"):
            try:
                if dynamicConfig.testCaseHasFailed:
                    print("[User-Command] SkipOnFailure")
                    val=int(str(val.replace("skiponfailure(","").replace(")","")).strip())
                    testCaseNumberToSkipTo=val

                    if(testCaseNumberToSkipTo<=SystemConfig.endRow):
                        rowNumberWhichFailed=SystemConfig.currentRow
                        SystemConfig.currentRow=testCaseNumberToSkipTo
                        cu.customWriteTestStep("Skip to TC #{0} since failure is encountered".format(testCaseNumberToSkipTo),
                                               "NA", "NA", "Failed")
                        testCaseNumberToSkipTo=val
                        markInBetweenTestCasesBlocked(rowNumberWhichFailed, testCaseNumberToSkipTo)
                    else:
                        cu.customWriteTestStep("TC#:{0} to skip to does not exist.".format(testCaseNumberToSkipTo),
                                               "The TC# to skip to should be within the range of total # of TCs",
                                               "Max TCs {0}: ".format(SystemConfig.endRow), "Failed")
            except:
                traceback.print_exc()
                print("[ERROR] Invalid argument for SkipOnFailure command : {0}".format(val))
                cu.customWriteTestStep("Invalid argument for SkipOnFailure command : {0}".format(val),
                                       "The argument passed should be an Integer",
                                       "Invalid argument", "Failed")

        elif val.lower().startswith("skipalways"):
            try:
                print("[User-Command] Skip-Always")
                val=int(str(val.replace("skipalways(","").replace(")","")).strip())
                testCaseNumberToSkipTo=val

                if(testCaseNumberToSkipTo<=SystemConfig.endRow):
                    SystemConfig.currentRow=testCaseNumberToSkipTo
                    testCaseNumberToSkipTo=val
                    Report.evaluateIfTestCaseIsPassOrFail()
                else:
                    cu.customWriteTestStep("TC#:{0} to skip to does not exist.".format(testCaseNumberToSkipTo),
                                           "The TC# to skip to should be within the range of total # of TCs",
                                           "Max TCs {0}: ".format(SystemConfig.endRow), "Failed")
            except:
                traceback.print_exc()
                print("[ERROR] Invalid argument for SkipOnFailure command : {0}".format(val))
                cu.customWriteTestStep("Invalid argument for SkipOnFailure command : {0}".format(val),
                                       "The argument passed should be an Integer",
                                       "Invalid argument", "Failed")
        else:
            print("No handling defined for : ",val)