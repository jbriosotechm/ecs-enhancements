import os,sys,time,datetime
from subprocess import Popen,PIPE


def runViaCmdAndReturnOutput(commandToRun):
        process = Popen(commandToRun.split(" "), stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        return stdout

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

