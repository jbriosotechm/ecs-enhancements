
import json, traceback
from os import access

from customUtils import customWriteTestStep

"""

As long as expected schema and actual are well defined, the script will work, main function can be called

"""


def parsePath(path):
    fieldsInPath=[]
    if "." in path:
        fieldsInPath=path.split('.')
    else:
        fieldsInPath.append(path)

    return fieldsInPath


def compareDataTypeOfActualResponseVsExpectedSchema(key, path, expectedTypeFromSchema, actualTypeFromServer):
    #Todo - might be some mappings needed, if same data types are not reported as same due to spellings
    #Todo - have this verified with Bong
   returnValue=False

   if 'unicode' in str(actualTypeFromServer) and 'string' in expectedTypeFromSchema:
      #print('Validation passed')
      returnValue=True

   if 'dict' in actualTypeFromServer and 'object' in expectedTypeFromSchema:
      #print('Validation passed')
      returnValue=True

   if 'NoneType' in actualTypeFromServer and 'None' in expectedTypeFromSchema:
      #print('Validation passed')
      returnValue=True

   if 'list' in actualTypeFromServer and 'array' in expectedTypeFromSchema:
      #print('Validation passed')
      returnValue=True

   if 'float' in actualTypeFromServer and 'number' in expectedTypeFromSchema:
      #print('Validation passed')
      returnValue=True

   if 'int' in actualTypeFromServer and 'number' in expectedTypeFromSchema:
      #print('Validation passed')
      returnValue=True

   if str(actualTypeFromServer) in str(expectedTypeFromSchema):
        #print('Validation passed')
        returnValue=True

   if not returnValue:
      print('************* [ Validation failed ] ***************')
      #print("Validating field : {0}", key)
      print("Path (Schema): {0} ".format(path))
      print('actualTypeFromServer',actualTypeFromServer)
      print('expectedTypeFromSchema',expectedTypeFromSchema)

   status="Failed"
   if returnValue:
      status="Passed"

   customWriteTestStep("Data type validation for path : {0}".format(path),"Expected Data type : {0}".format(expectedTypeFromSchema),"Actual data type : {0}".format(actualTypeFromServer),status)

   return returnValue


def getValueAndDataTypeFromActualResponse(path,actualResponse):

    fieldsInPath=parsePath(path)
    exceptionMsg=""
    dic=actualResponse

   #  if type(dic).__name__=='list':
   #     dic=dic[0]
    #print("path is : ",path)
    try:
        for field in fieldsInPath:



            # print('fieldsInPath: ',fieldsInPath)
            # print("Field is : ",field)
            if field in ['items']:
               if type(dic).__name__=='list':
                  dic=dic[0]


            else:
               if field not in ['properties']:
                  dic=dic[field]

        #print("Path exists : ",path)
        return (True,dic, type(dic).__name__)

    except Exception as e:
            traceback.print_exc()
            exceptionMsg=e

    print("Path is : ",path)
    return (False,exceptionMsg,None)



def validateSchemaAndDataType(actualResponse,key,path,valueFromSchema):

    #array has items, object has properties
    if key=='type':

        path='.'.join(path.split('.')[:-1])

        if path != '':

            (valuesFetched, valueFromActualResponse, dataType)=getValueAndDataTypeFromActualResponse(path,actualResponse)

            if valuesFetched:
                  #print("Value : [{0}] has data type [{1}]".format(valueFromSchema, dataType))
                  compareDataTypeOfActualResponseVsExpectedSchema(key, path, valueFromSchema, dataType)
            else:
                  #this means path does not exist on the actual response
                  exceptionMsg=valueFromActualResponse
                  print("Exception in validateSchemaAndDataType : {0}".format(exceptionMsg))
                  customWriteTestStep("Path : {0} does not exist on the actual response".format(path),"Path should exist as per Schema definition","Path does not exist in Actual Response","Failed")



def iterateJsonAndPrintPath(actualResponse, expectedSchema,path=''):

    for key in expectedSchema:

        validateSchemaAndDataType(actualResponse, key, path+key,expectedSchema[key])
        if isinstance(expectedSchema[key], dict):
            iterateJsonAndPrintPath(actualResponse, expectedSchema[key],path+key + '.')

        print("\n\n")


def getSchemaDataType(jsonObjectExpected):
   try:
      return jsonObjectExpected["items"]["type"]
   except:
      pass
   return jsonObjectExpected["type"]


def compareRootObjects(jsonObjectExpected, actualResponse):
   expectedTypeFromSchema=getSchemaDataType(jsonObjectExpected)
   actualTypeFromServer=type(actualResponse).__name__
   returnValue=False

   if 'unicode' in str(actualTypeFromServer) and 'string' in expectedTypeFromSchema:
      #print('Validation passed')
      returnValue=True

   if 'dict' in actualTypeFromServer and 'object' in expectedTypeFromSchema:
      #print('Validation passed')
      returnValue=True



   if 'list' in actualTypeFromServer and 'array' in expectedTypeFromSchema:
      #print('Validation passed')
      returnValue=True
   if str(actualTypeFromServer) in str(expectedTypeFromSchema):
        #print('Validation passed')
        returnValue=True

   if not returnValue:
      print('********** [ Validation failed ] ************')

      print("Root dataTypeExpected:",expectedTypeFromSchema)
      print("Root dataTypeOfResponse:",actualTypeFromServer)

   status="Failed"
   if returnValue:
      status="Passed"

   customWriteTestStep("Compare schema of root","Expected Data type: {0}".format(expectedTypeFromSchema),"Actual Data type : {0}".format(actualTypeFromServer),status)

   return returnValue


def getContentFromExpectedSchema(expectedSchema):
   return expectedSchema['items']['properties']

def main(expectedSchema, actualResponse):


   #now derive the actual content from the expected schema
   #expectedSchema=getContentFromExpectedSchema(expectedSchema)
   compareRootObjects(expectedSchema,actualResponse)
   iterateJsonAndPrintPath(actualResponse, expectedSchema)


if __name__=="__main__":
    main()