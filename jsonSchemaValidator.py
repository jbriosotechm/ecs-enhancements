obj1={
 "retailer_tier": [
  "BRONZE",
  "DIAMOND",
  "GOLD",
  "REGULAR",
  "SILVER"
 ]
}

obj2={
 "retailer_tier": [
  "BRONZE",
  "DIAMOND",
  "GOLD",
  "REGULAR",
  "SILVER"
 ]
}


obj3={
 "retailer_tier2": [
  "BRONZE",
  "DIAMOND",
  "GOLD",
  "REGULAR",
  "SILVER"
 ]
}

#check if obj1 is list/json
#for each value encountered, check if the key exists in another json object
#if atomic data types, then stop, else repeat


print(obj1)


#if parent is list, return the 1st json objet
def compareJsonObjects(obj1,obj2):

    if(type(obj1)!=type(obj2)):
        returnMsg="Type of Obj1 is not equal to Obj2"
        return False

    for key in obj1.keys()
