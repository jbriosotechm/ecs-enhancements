import os,sys,driverScript
import shutil, glob
import traceback,socket

from scripts import *

def getLatestFile():
	listOfFiles = glob.glob(os.path.join("Results\\*", '*.xlsx'))
	latest = max(listOfFiles, key=os.path.getctime)
	print("latest: {0}".format(latest))
	return latest


def main():
		try:
			#cookieValue="GCP_IAP_UID=securetoken.google.com/globe-isg-onegie-staging:N0bENMd9Gyc5UiWMq6QqBUAVA3y2; sessionid=613nsrrf8mo19g2y5p89wji76ye4tl0b; GCP_IAP_XSRF_NONCE_5pxecz_R0vpA9VbTtZEsOA=1; GCP_IAAP_AUTH_TOKEN_7978BFF0652DFB0=AFtMidcuBEITc7Ztg8VmlkB32ztxbu-A5Xq5iXXmQKur87ucPLV61TwozqKrqC7aSVoSoJIzgh2qiiNoVzXzsIc7yWCGVC6ZORScEKNv1SrbfKaES7Wd9ES4VQU2vXgUr7W5NHdPJgX2uqWkdyskaLxKqhVCO3hlKorpa1JYhST84uzazSY6_XnYUByJRIT28XWMlZIPHZnBbHrMrkrRiph5VsFypIuQAjzjKFo1DSd3Dini5BSGgmzKkEcraYyh2NKMJ6DrLqo643H5aMKlFtZ4ojecPm_KcWOFrPx5XsJNxT4pbGP2H3NFJpAso7PIhzk4u7BWPAry0GsW-bCM5kpxdFrtR7Smb2CANYQu9MmQ_e5n34cwwax9WPoRxv2y0Xb-2Enirr57qXGUtWFnm5rL-SDSweHLPca-HS-JNG91TFNqoAGNRlW4c2SvbuY_HGC4z-IQ3xH4_BNJGE9ZTAXIOw8VSWNAj_37Ta5a_XXYBfZ2lLmbbSgpeIxuXycZLPXxIZo8qInbDbkshw94sG5zR5GNIeAVBShOyug-RqT7RhIxsr3MJ-CeA6ordieof2IP_jgCGw8fKK7Zfgz7Qjz2ui-g1j9Oh88okSq7HpjEWdC9FSKIqB4sIPfaQ-rBLNhwrE7oljuxMgyoKPPtsg97SO7VAyjFC8Grv0rylM-rsJQI4-D_AZeCm95zCMrpUnZeTQHRyZlaaP8vPh3MC0LHPHrG3MH50nvCLJo-slBwZEjJrX1SOYIm8DMm9S_IS5j_zazly5fy8uFIOyjm4Z6WFIcjaPd3wPsnA1WPfzqgx0IR-NiFBGD3dtZTPi7RxaGsmDy3iA746aBTFo4biokvanwN6uYhGPEKrlcMxHRiHBqdii9zFH6AAFk-V8eUsCpjxEokCiV7silEQuv_L01_I_gQC-POW-p5F7hn9dmhOFZWB5BGFsKBemok8w8uIfwvvfZ4QfBqYKCEnltcJMNGCcjif3YK-noTuswu8xQKBSxb9RFsv4Id5H4EYcaR2kLDdl-t57kzmHDITVQvtJrBGCWgMtYF4APtGCQuMirvKdHEkBfYJoUo4h6YXrtaBBPmezGDHy26V2ngCisvPm12Oy5E37ybZQ-j1qeSTHhfih1oG_y2RchPtmiBNtf0UA8IG3J3SUl72n5qEYbCZaUykXAF0cCLRcPi9T7GYurUc0PmDreyxKFi5plnMVuq4c4ggdn4T5kvT7S9TsHLUDCTfzE20QoiI9zL3zM4EsFB3OtxoJyASztM829BDvxWTUN8bWHnzj71Y8K-R68MTKVNje3M1IUe0cDlCh799dbJ3PxzQXKQTHTZjrakJHDdVhZ4x1blSHSuq0SmGjNa-O73myFTljEpeG2ly8ZdCp4QzFmmAMckJUOxDKTCeCd3xS9M3A0_iBv0ezb2M6Xb_RzXk25xbVIZhXCixhWOaoHfG2xR_KGJ7OeTxmUkB31XZXTyzdev9Wj2ISVMh__KAzHsVQiXgYxafXmtJ98A09RhvA1dTSKUzIptLdt7S6E31g1VCTrUgTGjqeyYMd2w74WHDMooPrgW1xyi9SWvuRiNdfrkwIHUic4HIfFjw-GC9Om4rjc; csrftoken=01o8J76CdJsrKoiKHZ7zWj4jCsCHK9GsuuxTQAsOGW1N7j1YNUcetE0FSeljxViq"
			cookieValue=sys.argv[1]
			#print("Cookie value is : ",cookieValue)

			try:
				if socket.gethostname() != "LAPTOP-FINEIFN5":
					shutil.rmtree('Results')
					os.mkdir('Results')
					
			except:
				print('Error while deletion/creation of Results Directory')
				traceback.print_exc()



			try:
				print("Triggering main function")
				driverScript.superMain(cookieValue)
			except:
				print "[ERR - run.py] Encountered issue when Running the Test Data"
				traceback.print_exc()


			if socket.gethostname() != "LAPTOP-FINEIFN5":

				JUnitReport = createJUnitReport("API_Automation_Framework", "API_Automation_Framework", getLatestFile(), "Results\\JunitReport.xml")
				JUnitReport.create()

				htmlReport = createHTMLreport(getLatestFile(), "Results\\Results.html")
				htmlReport.create()
		except:
			traceback.print_exc()
			print("[ERR-run.py]")


main()