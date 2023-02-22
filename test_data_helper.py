import random
import string
from dateutil.relativedelta import relativedelta
from datetime import datetime
import dynamicConfig
import userConfig
import SystemConfig
import customUtils as cu
import time

def random_int(min_value, max_value):
    return random.randint(int(min_value), int(max_value))

def random_value(prefix, number_of_chars, suffix, exclusions, pool):
    random_pool = ""
    if pool == "":
        random_pool = string.ascii_letters

    if "numbers" in pool:
        random_pool += string.digits
    if "alpha" in pool:
        random_pool += string.ascii_letters
    if "special" in pool:
        random_pool += string.punctuation

    for char in SystemConfig.fixedExclusions:
        random_pool = random_pool.replace(char, "")
    for char in exclusions:
        random_pool = random_pool.replace(char, "")

    number_of_chars = int(number_of_chars) - len(prefix) - len(suffix)

    filler = ""

    if number_of_chars > 0:
        itr = 0
        while itr < number_of_chars:
            filler += random.choice(random_pool)
            itr += 1
    return prefix + filler + suffix

def generate_timestamp(timeformat):
    cur_timestamp = datetime.now()

    if "epoch" in timeformat:
        return int(time.time())

    timeformat = timeformat.replace("YYYY", "%Y")
    timeformat = timeformat.replace("yy", "%y")
    timeformat = timeformat.replace("yy", "%#y")

    timeformat = timeformat.replace("MONTH", "%B")
    timeformat = timeformat.replace("MM", "%m")
    timeformat = timeformat.replace("mm", "%#m")

    timeformat = timeformat.replace("DD", "%d")
    timeformat = timeformat.replace("dd", "%#d")

    timeformat = timeformat.replace("HH", "%H")
    timeformat = timeformat.replace("HM", "%I")

    timeformat = timeformat.replace("MI", "%M")
    timeformat = timeformat.replace("mi", "%#M")

    timeformat = timeformat.replace("SS", "%S")
    timeformat = timeformat.replace("ss", "%#S")

    return cur_timestamp.strftime(timeformat)

def random_int(min_value, max_value):
    return random.randint(int(min_value), int(max_value))

def split(text, delimiter, index):
    text = text.split(delimiter)
    return text[int(index)]

def theiaDoubleEncode(val):
    os.system("getEncodedVal.pys")

    urllib.quote_plus('W7Bv+KOF0xQIgf2T2V/LJQ==')

def add_time(initial_time, time_to_add, timeformat='%Y-%m-%dT%H:%M:%S'):
    try:
        initial_time = datetime.strptime(initial_time, timeformat)
    except Exception as e:
        print ("[ERR] Encountered converting '{0}' to timeformat: {1}").format(initial_time, e)
        return None

    time_to_add = time_to_add.split(' ')
    years = 0
    for time in time_to_add:
        years = int(time.replace("years", "")) if "years" in time.lower() else 0
        months = int(time.replace("months", "")) if "months" in time.lower() else 0
        days = int(time.replace("days", "")) if "days" in time.lower() else 0
        hours = int(time.replace("hours", "")) if "hours" in time.lower() else 0
        minutes = int(time.replace("minutes", "")) if "minutes" in time.lower() else 0
        seconds = int(time.replace("seconds", "")) if "seconds" in time.lower() else 0

    time_to_add = relativedelta(years=years, months=months, days=days,
                                hours=hours, minutes=minutes, seconds=seconds)
    return (initial_time + time_to_add).strftime(timeformat)

def check_item_is_list(path):
    if type(path) is list:
        return True
    return False

def findElement(key, val):
    jsonPath = "dynamicConfig.currentResponseInJson" + key
    try:
        currentDict = eval(jsonPath)
    except Exception as e:
        print ("[ERR] " + key + " is not found in the response")
        return -2
    item_list = []

    if type(currentDict) is not list:
        item_list.append(currentDict)
    else:
        item_list = currentDict
    items = val.split(";")

    storeIndex = None
    if (items[-1].partition(userConfig.data_splitter)[0] == "storeIndexTo"):
        storeIndex = items[-1].partition(userConfig.data_splitter)[2]
        items = items[:-1]

    for index, item in enumerate(item_list):
        structureFound = False
        jsonPath = "item_list"

        item_value = []
        for var in items:
            k = var.partition(userConfig.data_splitter)[0]
            v = var.partition(userConfig.data_splitter)[2]
            t = jsonPath + "[" + str(index)+ "]" + k

            try:
                if v == "" or v is None:
                    eval(t)
                    print("[INF] {0} is in {1} with value {2}".format(k, key, eval(t)))
                    item_value.append(k + "=" + eval(t))
                else:
                    if eval(t) != str(v):
                        structureFound = False
                        break
                    else:
                        item_value.append(k + "=" + eval(t))
            except Exception as e:
                print (e)
                structureFound = False
                break
            structureFound = True

        if structureFound:
            print ("[INF] "+ val + " is found in " + jsonPath + "[" + str(index)+ "]")
            if storeIndex is not None:
                SystemConfig.localRequestDict[storeIndex] = index

            actual = ",".join(item_value)
            cu.customWriteTestStep("Response Parameter Validation by Finding Structure",
                                "{0} Should be located in {1}".format(val, key),
                                "Parameters found: {0}".format(actual), "Pass")
            return 0

    print ("[ERR] "+ val + " is not found in " + key)
    return -1

def get_element(key, val):
    try:
        container, item, index = val.split(";")
    except Exception as e:
        length = len(val.split(";"))
        print("[ERR] Expected length of get_element arguments is 3. Received {0} arguments".format(length))
        cu.customWriteTestStep("Response Parameter Validation by Finding Structure",
                               "Get Value for {0}".format(val),
                               "Received invalid length of {0} should be 3".format(length), "Fail")
        return -1
    jsonPath = "dynamicConfig.currentResponseInJson" + container

    try:
        if check_item_is_list(eval(jsonPath)):
            jsonPath += "[{0}]{1}".format(index, item)
            value = str(eval(jsonPath))
            print(value)
        else:
            jsonPath += item
            value = str(eval(jsonPath))
    except Exception as e:
        jsonPath = jsonPath.replace("dynamicConfig.currentResponseInJson", "")
        print("[ERR] Error occured on getting the values in {0} for item {1} in index {2}".format(container, item, index))
        cu.customWriteTestStep("Response Parameter Validation by Finding Structure",
                               "Get Value for {0}".format(jsonPath),
                               "Error Encountered on locating the value: {0}".format(str(e)), "Fail")
    print("[INF] Value for {0} in {1} is {2}".format(item, container, value))
    SystemConfig.globalDict[key] = value
    return 0