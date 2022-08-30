import os,sys,time,datetime
import subprocess
from subprocess import Popen,PIPE


# def runViaCmdAndReturnOutputOld(commandToRun):
#     process = Popen(commandToRun.split(" "), stdout=PIPE, stderr=PIPE)
#     stdout, stderr = process.communicate()
#     return stdout

def runViaCmdAndReturnOutput(command):
    output=[]
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Poll process for new output until finished
    while True:
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() is not None:
            break
        sys.stdout.write(nextline)
        output.append(nextline+"\n")
        sys.stdout.flush()

    #output = process.communicate()[0]
    #exitCode = process.returncode
    print("returning output:",output)
    return output
    # if (exitCode == 0):
        #return output
    # else:
    #     raise ProcessException(command, exitCode, output)
