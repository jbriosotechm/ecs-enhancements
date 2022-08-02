import requests
import json
import traceback
import userConfig

import os,sys,time

import socket
from subprocess import Popen,PIPE
import subprocess
import SystemConfig


def runViaCmdAndReturnOutputAsync(commandToRun):
    try:
        p = Popen(commandToRun)
    except Exception,e:
        print("[FAILURE] RSA Webservice mighg have failed to start" )
        traceback.print_exc()



def runViaCmdAndReturnOutputOld(commandToRun):
    process = Popen(commandToRun.split(" "), stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    return stdout



def runViaCmdAndReturnOutput(command):
    output=""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Poll process for new output until finished
    while True:
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() is not None:
            break
        sys.stdout.write(nextline)
        output+=nextline
        sys.stdout.flush()

    #output = process.communicate()[0]
    #exitCode = process.returncode
    print("returning output:",output)
    return output
    # if (exitCode == 0):
        #return output
    # else:
    #     raise ProcessException(command, exitCode, output)

def encryptValueTraditional(email,password):
    try:
        url = "http://localhost:9099/rsayer/encrypt"

        payload = json.dumps({
        "payload": {
            "email": email,
            "password": password
        },
        "publicKey": "MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAq+375KSFD65rzlI8hJTpzNwZzI65ifJ3QPw0ijoi1FsZsc8GdoTxETxLUZ4+bg/i5yNjbHvUXRIuu8LQYN+tiwTGYPP8L+RMB2xB85UvBTlLhaAnl1+gvhrVTveg4xnTsPSnptTMUKqETLHjprasswue4egk0hJqw3hM4IiFFSZRD7BAciSdKgPjPlYxlXgmXXNVpyCH8r6jQOyC05TvfIuAZFiz257KvO9q3dVl99aHz/ec4fW9OwJK5saCIAbfzbyBYVphubHt3bAffz9Y+35JfkhIVIqGWKn/sOS8J4uVw2fmw98db05GYpg9b0VIrcSfvGTyCzajVpL505xZyc3GmcTsH15Hnw8ZCoMMYABwxfhtETZ8SyLMVXFlLvKYeUzXxnC+Uwn2VqF3bPTTAM+l1lPLkXjXyjQKJbJgLfs5QZbzFtmvjtoagFaalQ0thPs9ooc27VhBQJQtswsuuSmUPXurQjBj+fr9xJaP50LSY+/UDwVeFropwABgwpshzI2gMWr87R1toOlvMHHQ5meJfIjhGRvaHhXgAz5IiEYSonq8jYAzZs+6XUHsat2IFtP9K0J0o3cGpEGmrgzzLZj4M7WzDvX/Uj+bUucXerFjKhyyRHs/LQXgzgslWcHS3gxXUs1269SKa8PuwsLdDxSV8xlSySn6aATQldNhmGcCAwEAAQ=="
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        responseAsDict=json.loads(response.text)
        #print("encrypted value is : {0}".format(responseAsDict["encrypted"]))
        return responseAsDict["encrypted"]

    except Exception:
        print("***********Exception encountered*************")
        traceback.print_exc()

    return None


def encryptValueSocialWithPassword(token,socialProvider, password):
    try:
        url = "http://localhost:9099/rsayer/encrypt"
        socialToken=""
        payload = json.dumps({
        "payload": {
            "socialProvider": socialProvider,
            "socialToken": socialToken,
            "password":password
        },
        "publicKey": "MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAq+375KSFD65rzlI8hJTpzNwZzI65ifJ3QPw0ijoi1FsZsc8GdoTxETxLUZ4+bg/i5yNjbHvUXRIuu8LQYN+tiwTGYPP8L+RMB2xB85UvBTlLhaAnl1+gvhrVTveg4xnTsPSnptTMUKqETLHjprasswue4egk0hJqw3hM4IiFFSZRD7BAciSdKgPjPlYxlXgmXXNVpyCH8r6jQOyC05TvfIuAZFiz257KvO9q3dVl99aHz/ec4fW9OwJK5saCIAbfzbyBYVphubHt3bAffz9Y+35JfkhIVIqGWKn/sOS8J4uVw2fmw98db05GYpg9b0VIrcSfvGTyCzajVpL505xZyc3GmcTsH15Hnw8ZCoMMYABwxfhtETZ8SyLMVXFlLvKYeUzXxnC+Uwn2VqF3bPTTAM+l1lPLkXjXyjQKJbJgLfs5QZbzFtmvjtoagFaalQ0thPs9ooc27VhBQJQtswsuuSmUPXurQjBj+fr9xJaP50LSY+/UDwVeFropwABgwpshzI2gMWr87R1toOlvMHHQ5meJfIjhGRvaHhXgAz5IiEYSonq8jYAzZs+6XUHsat2IFtP9K0J0o3cGpEGmrgzzLZj4M7WzDvX/Uj+bUucXerFjKhyyRHs/LQXgzgslWcHS3gxXUs1269SKa8PuwsLdDxSV8xlSySn6aATQldNhmGcCAwEAAQ=="
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        responseAsDict=json.loads(response.text)
        #print("encrypted value is : {0}".format(responseAsDict["encrypted"]))
        return responseAsDict["encrypted"]

    except Exception:
        traceback.print_exc()

    return None




def encryptValueSocial(socialProvider, socialToken):
    try:
        url = "http://localhost:9099/rsayer/encrypt"

        payload = json.dumps({
        "payload": {
            "socialProvider": socialProvider,
            "socialToken": socialToken
        },
        "publicKey": "MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAq+375KSFD65rzlI8hJTpzNwZzI65ifJ3QPw0ijoi1FsZsc8GdoTxETxLUZ4+bg/i5yNjbHvUXRIuu8LQYN+tiwTGYPP8L+RMB2xB85UvBTlLhaAnl1+gvhrVTveg4xnTsPSnptTMUKqETLHjprasswue4egk0hJqw3hM4IiFFSZRD7BAciSdKgPjPlYxlXgmXXNVpyCH8r6jQOyC05TvfIuAZFiz257KvO9q3dVl99aHz/ec4fW9OwJK5saCIAbfzbyBYVphubHt3bAffz9Y+35JfkhIVIqGWKn/sOS8J4uVw2fmw98db05GYpg9b0VIrcSfvGTyCzajVpL505xZyc3GmcTsH15Hnw8ZCoMMYABwxfhtETZ8SyLMVXFlLvKYeUzXxnC+Uwn2VqF3bPTTAM+l1lPLkXjXyjQKJbJgLfs5QZbzFtmvjtoagFaalQ0thPs9ooc27VhBQJQtswsuuSmUPXurQjBj+fr9xJaP50LSY+/UDwVeFropwABgwpshzI2gMWr87R1toOlvMHHQ5meJfIjhGRvaHhXgAz5IiEYSonq8jYAzZs+6XUHsat2IFtP9K0J0o3cGpEGmrgzzLZj4M7WzDvX/Uj+bUucXerFjKhyyRHs/LQXgzgslWcHS3gxXUs1269SKa8PuwsLdDxSV8xlSySn6aATQldNhmGcCAwEAAQ=="
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        responseAsDict=json.loads(response.text)
        print(responseAsDict)
        #print("encrypted value is : {0}".format(responseAsDict["encrypted"]))
        return responseAsDict["encrypted"]

    except Exception:
        traceback.print_exc()

    return None



def generateAccessToken(authValue):

    try:
        url = "https://test-cxs.globe.com.ph/v1/channels/oauth/token"
        if "dev" in str(userConfig.excelFileName).lower():
            url = "https://dev-cxs.globe.com.ph/v1/channels/oauth/token"
        elif "prod" in str(userConfig.excelFileName).lower():
            url = "https://cxs.globe.com.ph/v1/channels/oauth/token"


        payload={}
        headers = {
        'Authorization': '{0}'.format(authValue),
        'Cookie': '__cfduid=d681d596369b7318312245d48091dc3291613380293; __cfduid=d0277fbdaa8a0f976eef8b83483acc0131616487089'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        responseAsDict=json.loads(response.text)
        print("responseAsDict:",responseAsDict)
        print("Access token with less permissions:",responseAsDict["result"]["accessToken"])
        return responseAsDict["result"]["accessToken"]

    except Exception:
        traceback.print_exc()
        print("[FAILURE]")
        return None

def getSocialToken():

    cxsSocialToken=None
    try:

        jarFileLocation="./javaLibCXS/cxs.jar"
        javaCommand="java -jar {0} ".format(jarFileLocation)
        if "prod" in str(userConfig.excelFileName).lower():
            javaCommand="java -jar {0} prod".format(jarFileLocation)

        data=runViaCmdAndReturnOutput(javaCommand)
        data=data.replace("\r","").replace("\n","")
        print("Data returned is : ",str(data))
        if "CXS token fetched : " not in str(data):
            print("Failure, wasnt able to fetch Social token")
        else:
            cxsSocialToken=(str(data).split("CXS token fetched : ")[1]).split("']")[0]
            print("[Python INFO] : Social token : {0}".format(cxsSocialToken))

    except Exception:
        traceback.print_exc()
        print("[FAILURE]")



    return cxsSocialToken




def getCookieFor1GieOld():

    cookieFor1Gie=None
    try:

        preSplit="[****CookieStarts*****]"
        postSplit="[****CookieEnds*****]"
        jarFileLocation="./javaLibCXS/oneGie.jar"
        javaCommand="java -jar {0} ".format(jarFileLocation)
        if "prod" in str(userConfig.excelFileName).lower():
            javaCommand="java -jar {0}".format(jarFileLocation)

        data=runViaCmdAndReturnOutput(javaCommand)
        #data=data.replace("\r","").replace("\n","")
        print("Data returned is : ",str(data))
        if preSplit not in str(data):
            print("[Failure-[Custom]],issue with the java program, please check logs")
        else:
            cookieFor1Gie=(str(data).split(preSplit)[1]).split(postSplit)[0]
            print("[Python INFO] : Cookie for 1Gie : {0}".format(cookieFor1Gie))

    except Exception:
        traceback.print_exc()
        print("[FAILURE] function : getCookieFor1Gie")



    return cookieFor1Gie


def getCookieFor1Gie():
    print("SystemConfig.cookieValue:",SystemConfig.cookieValue)
    return SystemConfig.cookieValue

def getCookieFor1GieViaBrowsser():

    cookieFor1Gie=None
    try:
        url = "http://localhost:5000/"

        payload = json.dumps({
        "msg": "hello Altamash"
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        print(str(response.text))
        jsonDict=json.loads(response.text)
        cookieFor1Gie=jsonDict["msg"]
        print("Cookie value: ",cookieFor1Gie)
    except:
        traceback.print_exc()
        print("Unable to get cookie for 1Gie")

    return cookieFor1Gie


def socialEncodedLogin():
    cxsEncodedLogin=None
    socialToken=None
    try:
        #parameters to return
        socialToken=getSocialToken()
        if socialToken is not None:
            cxsEncodedLogin=encryptValueSocial("googleplus",socialToken)
        # jarFileLocation="./javaLibCXS/rsa_encoder.jar {0}".format(socialToken)
        # javaCommand="java -jar {0} ".format(jarFileLocation)
        # (data,resCode)=runViaCmdAndReturnOutput(javaCommand)
        # if "Encrypted String is:" not in str(data):
        #     print("Failure, wasnt able to fetch Social token")
        # else:
        #     cxsEncodedLogin=(str(data).split("Encrypted String is:")[1]).split(']')[0]
        #     print("[Python INFO] : EncodedLogin : {0}".format(cxsEncodedLogin))

    except Exception:
        traceback.print_exc()
        print("[FAILURE]")

    return (socialToken,cxsEncodedLogin)


def doSanityForLocalWebservice():
    ctr=-1;
    try:
        while ctr<3:
            ctr+=1
            if encryptValueSocial("googleplus","c57c0fbe7cf41548e24be0780c570842d5a8941a") is not None:
                return True
            time.sleep(15)

    except Exception,e:
        traceback.print_exc()
        print("[FAILURE]")

    return False


def isPortListening(portNumber):
    status=False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1',9099))
        if result == 0:
            print "Port is open"
            status=True
        else:
            print "Port is not open"

        sock.close()

    except Exception,e:
        traceback.print_exc()

    return status



def startWebServiceForEncodingJson():
    #Logic
    #Check if port is already listening
    #If yes, do sanity
    #If no, trigger the service, wait for port to listen and then and do sanity

    try:
        if isPortListening("9099"):
            print("\nLooks like RSA Encryption Web Service is already running, doing sanity.. ")
            isServiceReady=doSanityForLocalWebservice()
            print("RSA Encryption Web Service readiness status : {0}".format(isServiceReady))
            return isServiceReady
        else:
            print("\nLooks like RSA Encryption Web Service is NOT running, triggering it.. ")
            jarFileLocation="./javaLibCXS/rsayer-0.0.1-SNAPSHOT.jar"
            javaCommand="java -jar {0}".format(jarFileLocation)
            javaFullPath=userConfig.jreBinPath+'java'
            javaCommandList=[javaFullPath,'-jar',jarFileLocation]
            runViaCmdAndReturnOutputAsync(javaCommandList)
            isServiceReady=doSanityForLocalWebservice()
            return isServiceReady

    except Exception,e:
        traceback.print_exc()

    return False
