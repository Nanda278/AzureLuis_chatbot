import requests
import re
from requests.utils import requote_uri
import json

class covidRest:

    def __init__(self):
        self.baseUrl = "https://endapicovid.azurewebsites.net" #"http://localhost:8001"
        self.countryUrl = "/totalcasesbycountry?country=#country&type=#type"
        self.pincodeUrl = "/getCovidDetailsByPincode?pincode=#pincode"
        self.topCountyDetailsUrl = "/gettopcountrydetails?entity=#entity&sortType=#sortType&type=#type"
        self.mailURL = "/sendMail"
        self.errMsg = "Sorry..!! I could not reach my internal api to get the details by country"

    def getTotalCountByCountry(self, entity='All', type="All"):
        url = self.baseUrl + self.countryUrl
        url = url.replace("#country", entity)
        url = url.replace("#type", type)
        url = requote_uri(url)
        response = requests.get(url)
        if (response.status_code == 200):
            return response.text
        else:
            return "Sorry..!! I could not reach my internal api to get the details by country"

    def formCasesString(self, data, type, entity):
        ccases = 0
        rcases = 0
        dcases = 0
        responeMsg = ""
        if (type == "All"):
            ccases = data['cases']
            rcases = data['recovered']
            dcases = data['deaths']
            accases = data['active']
            responeMsg = "Hey, the latest covid-19 cases of " + f"{entity}" + " with \n \n" + "Confirmed cases as " + f"{ccases}" + "\n \n" \
                                                                                                                                    "and the Recovered Cases counts to " + f"{rcases}" + "\n \n" + "and finally the Death Cases are " + f"{dcases}"
        elif (type == "confirmed"):
            ccases = data['cases']
            responeMsg = "The total confirmed covid-19 cases of " + f"{entity}" + " is " + f"{ccases}"
        elif (type == "deaths"):
            dcases = data['deaths']
            responeMsg = "The total death cases of covid-19 in " + f"{entity}" + " is " + f"{dcases}"
        elif (type == "recovered"):
            rcases = data['recovered']
            responeMsg = "The recovered cases for covid-19 in " + f"{entity}" + " is Recovered Cases " + f"{rcases}"

        # responeMsg += "$$$" + data['countryInfo']['flag']

        return responeMsg, ccases, rcases, dcases

    def checkMobileValid(self, value):

        regex = "(\w{3})\w{3}\w{4}"
        if re.search(regex, value):
            responseMsg = "Thanks for the mobile.. You can enquire about the convid-19 details.."
        else:
            responseMsg = "Your mobile number is not valid.. Please enter a valid mobile number.."

        return responseMsg

    def getCountryNameFromPincode(self, pincode):
        if (re.fullmatch("\w{2}\d{2}|\d{5,6}", pincode)):
            url = self.baseUrl + self.pincodeUrl
            url = url.replace("#pincode", pincode)
            url = requote_uri(url)
            print(url)
            response = requests.get(url)
            if (response.status_code == 200):
                print(response.text)
                return response.text
            else:
                return "Sorry..!! I could not reach my internal api to get the details by country"
        else:
            return "Pincode is not on the appropriate format..!! Please give the picode as 110001 "

    def getTopCountyCases(self, entity=1, sortType="DESC", type=""):
        if (entity == "" or entity == None):
            entity = 1

        url = self.baseUrl + self.topCountyDetailsUrl
        url = url.replace("#entity", str(entity))
        url = url.replace("#sortType", sortType)
        url = url.replace("#type", type)
        url = requote_uri(url)
        print(url)
        response = requests.get(url)
        if (response.status_code == 200):
            responseMsg = response.text
        else:
            responseMsg = self.errMsg

        return responseMsg

    def sendEmailToRest(self, entity):
        data ={}
        data['name'] = ""
        data['mailid'] = entity
        data['mobile'] = ""

        url = self.baseUrl+self.mailURL
        url = requote_uri(url)
        data = json.dumps(data)
        response = requests.post(url,json=data)
        if(response.status_code==200):
            return response.text
        else:
            return response.text
