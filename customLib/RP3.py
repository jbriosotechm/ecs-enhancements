"""

Main args are : 2, 3, 6, 7
arg2 = excelFileName, example : excelFileName=r"C:\Results\ActualData27062020_1406377\ActualData\ActualData.xlsx"
arg3 = excelFilePath, example : excelFilePath=r"C:\Results\ActualData27062020_1406377\ActualData"
arg6 = PC if image resolution should be of PC screen
arg7 = yes if bugs need to be logged in JIRA

Sample Command:
python 
RP3.py 
dummy 
"C:\\Results\\ActualData27062020_1406377\\ActualData\\ActualData.xlsx" 
"C:\\Results\\ActualData27062020_1406377\\ActualData" 
dummy 
dummy 
PC 
yes

"""


import sys,RP3Lib

arg1=""
arg2=sys.argv[2]
arg3=sys.argv[3]
arg4=""
arg5=""
arg6=sys.argv[6]
arg7="no"

print "Arg Len : ",len(sys.argv)

if len(sys.argv)>7:
	arg7=sys.argv[7]



RP3Lib.main(arg1,arg2,arg3,arg4,arg5,arg6,arg7)