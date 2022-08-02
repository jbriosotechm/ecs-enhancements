import os,sys,userConfig,time
from commonLib import runViaCmdAndReturnOutput
import traceback


def checkForWordFileGenerationWithTimeout(filename,timeoutInSeconds):
    startTime=time.time()
    while(time.time()-startTime<timeoutInSeconds):
        if os.path.exists(filename):
            return True
        print("Waiting for word file to be generated")
        time.sleep(1)

    return False



def main(excelAbsName):
    #arg1 is the abs file name
    print("excelAbsName:",excelAbsName)
    userConfig.excelFileName=excelAbsName
    userConfig.excelFilePath=(excelAbsName.split("\\")[:-1]) #['C:', 'Users', 'ALTAMASH', 'Desktop', 'TCoE', 'API', '1Gie', 'Results', 'Result_2021_11_07_01_32_43715000']
    userConfig.excelFilePath=os.path.join(*userConfig.excelFilePath).replace(":",":/")
    wordFileName=excelAbsName.replace(".xlsx",".docx")
    print("wordFileName:",wordFileName)
    

    if checkForWordFileGenerationWithTimeout(wordFileName,45):
        #convert here to pdf
        try:
            command=userConfig.sofficePath+ " --headless --convert-to pdf:writer_pdf_Export --outdir {0} {1}".format(userConfig.excelFilePath,wordFileName)
            print("Command is : {0}".format(command))
            resultCodeForPDF=runViaCmdAndReturnOutput(command)
            checkForWordFileGenerationWithTimeout(os.path.join(userConfig.excelFilePath,wordFileName.replace(".docx",".pdf")),60)
        except:
            traceback.print_exc()
            print("[ERR ]Conversion to PDF failed")
            

        try:
            command=userConfig.sofficePath+" --headless --convert-to doc --outdir {0} {1}".format(userConfig.excelFilePath,wordFileName)
            print("Command is : {0}".format(command))
            resultCodeForDoc=runViaCmdAndReturnOutput(command)
            checkForWordFileGenerationWithTimeout(os.path.join(userConfig.excelFilePath,wordFileName.replace(".docx",".doc")),60)
        except:
            traceback.print_exc()
            print("[ERR ]Conversion to DOC failed")

    else:
        print("[ERR] Can't generate PDF since Docx was not found at path : {0}".format(wordFileName))