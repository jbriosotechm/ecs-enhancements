"""
Parts of the problem - holistic view

1. Read API name from Excel, and fetch the corresponding endpoint from json doc
2. Grab the whole info about that endpoint from the json document, it can be across multiple places
3. Once schema is prepared, do a nested comparison - Done

"""

import json, traceback, sys
import SystemConfig
import utils
import customUtils

jsonFileParsed='./1gie.json'
rootJsonObject=None

def parse_json_recursively(json_object, target_key):
    if type(json_object) is dict and json_object:
        for key in json_object:
            if key == target_key:
                print("{}: {}".format(target_key, json_object[key]))
                SystemConfig.schemaValue=json_object[key]
            parse_json_recursively(json_object[key], target_key)

    elif type(json_object) is list and json_object:
        for item in json_object:
            parse_json_recursively(item, target_key)


def getSchemaFromPath(apiPath):
    key="schema"
    apiJsonObject=rootJsonObject['paths'][apiPath]

    SystemConfig.schemaValue=None
    parse_json_recursively(apiJsonObject, key)
    return SystemConfig.schemaValue


def getExampleFromPath(apiPath):
    key="examples"
    apiJsonObject=rootJsonObject['paths'][apiPath]

    SystemConfig.schemaValue=None
    parse_json_recursively(apiJsonObject, key)
    dict=SystemConfig.schemaValue

    if dict is not None:
            key="value"

            SystemConfig.schemaValue=None
            parse_json_recursively(dict, key)
            dict=SystemConfig.schemaValue


    return dict

def loadJsonFileAndReturnRootJsonObject():
    jsonFilePath="./1gie.json"

    file=open(jsonFilePath)
    rootJsonObject=json.load(file)
    return rootJsonObject


def prettyPrintDict(dictObj):
    print(json.dumps(dictObj, indent = 3))


def getExampleResponse(path):
    return getExampleFromPath(path)

def main(path,actualResponse):
    global rootJsonObject
    rootJsonObject=loadJsonFileAndReturnRootJsonObject()

    schemaJson=getSchemaFromPath(path)
    actualResponse=json.loads(actualResponse)

    print("Schema Json is : ")
    prettyPrintDict(schemaJson)

    customUtils.customWriteTestStep("Log Expected Schema","Expected Schema is : \n{0}".format(schemaJson),"NA","Passed")

    print("Actual Response is : ")
    prettyPrintDict(actualResponse)
    utils.main(schemaJson, actualResponse)
    #Todo : Handle if schemaJson is None which means key schema was not found in api json object
    #prettyPrintDict(schemaJson)

if __name__=="__main__":
    main()