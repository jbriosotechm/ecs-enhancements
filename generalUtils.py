import os,sys,time

def runViaCmdAndReturnOutput(activityDescription,commandToRun):

	print "{0}".format(activityDescription)

	time.sleep(1)
	tmpFileName="tmpOutput"+str(time.time());
	resCode=os.system(commandToRun+">"+tmpFileName)
	data = [line.rstrip('\n') for line in open(tmpFileName)]
	try:
		os.remove(tmpFileName)
	except:
		pass

	print "{0}".format(data)

	return (data,resCode)