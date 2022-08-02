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

def generateTimestamp(timestamp):
    #'2020-03-18 19:39:46.465000'

    curTimestamp=str(datetime.datetime.now())

    [dateComponent,timeComponent]=curTimestamp.split(" ")
    [year,month,day]=dateComponent.split("-")
    [hour,mins,seconds]=timeComponent.split(":")
    seconds=seconds.split(".")[0]

    if "yyyy" in timestamp:
        timestamp=timestamp.replace("yyyy",year)

    elif "yy" in timestamp:
        timestamp=timestamp.replace("yy",year[2:])

    if "mm" in timestamp:
        timestamp=timestamp.replace("mm",month)

    if "dd" in timestamp:
            timestamp=timestamp.replace("dd",day)

    if "hh" in timestamp:
            timestamp=timestamp.replace("hh",hour)

    if "mi" in timestamp:
            timestamp=timestamp.replace("mi",mins)

    if "ss" in timestamp:
            timestamp=timestamp.replace("ss",seconds)

    return timestamp

