import pandas as pd
import re
import smtplib
from geopy.geocoders import Bing
import requests
from covid.covidRest import covidRest

def getconfirmedCases(name=None):
    print(name)
    url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    print(url)
    df = pd.read_csv(url)
    return df

def getrecovredCases(name=None):
    print(name)
    url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
    print(url)
    df = pd.read_csv(url)
    return df


def gettotalDeathCases(name=None):
    print(name)
    url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
    print(url)
    df = pd.read_csv(url)
    return df


def get_dates(df):
    dt_cols = df.columns[~df.columns.isin(['Province/State', 'Country/Region', 'Lat', 'Long','pincode'])]
    LAST_DATE_I = -1
    # sometimes last column may be empty, then go backwards
    for i in range(-1, -len(dt_cols), -1):
        if not df[dt_cols[i]].fillna(0).eq(0).all():
            LAST_DATE_I = i
            break
    return LAST_DATE_I, dt_cols


def getCountNameWithCode():
    url = "https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes/raw/master/all/all.csv"
    countryWithName = {}

    countryNameWithCode = pd.read_csv(url)
    #listVal = []
    for index, row in countryNameWithCode.iterrows():
        countryWithName[str(row['alpha-2']).lower()] = str(row['name']).lower()
        countryWithName[str(row['alpha-3']).lower()] = str(row['name']).lower()
    countryWithName['us'] = 'us'
    countryWithName['usa'] = 'us'
    countryWithName['united states'] = 'us'
    countryWithName['uk'] = 'united kingdom'
    return countryWithName


class covidDetails:

    def __init__(self):
        self.CCCases = pd.DataFrame() #getconfirmedCases("confirmed_global")
        self.CRCases = pd.DataFrame() #getrecovredCases()
        self.CDCases = pd.DataFrame() #gettotalDeathCases()
        self.lastDate, self.Columns = get_dates(self.CCCases)
        self.countWithCodes = getCountNameWithCode()
        self.userName = ""
        self.mobieNumber = ""
        self.covRest = covidRest()
        #print(self.CCCases.head())

    def getTotalConfirmedCasesInWorld(self,county=None,df=None,type=None):
        returnBool = True
        county = str(county).lower()
        if (len(county) == 2):
            if(str(county).lower() in self.countWithCodes.keys()):
                county = self.countWithCodes[county]
        elif (len(county) == 3):
            if(str(county).lower() in self.countWithCodes.keys()):
                county = self.countWithCodes[county]
        print(county)
        if(county == None or county == "" or county == "world"):
            responseValue = df[df.columns[-1]].sum()
            county = "World"
            county = "**"+ str(county).title() + "**"
            responseValueMsg = "Hey, the total number of "+type +" in " + county + " is " + f"{responseValue}"
        else:
            if(str(county).lower() =="united states"):
                county ="us"
            groupedDF= df.groupby("Country/Region")[df.columns[-1]].sum()
            groupedDF = groupedDF.reset_index()
            groupedDF.columns = ['country','total']
            groupedDF = groupedDF[groupedDF['country'].str.lower() == str(county).lower()]
            county = "**"+ str(county).title() + "**"
            print(groupedDF)
            try :
                responseValue = groupedDF['total'].values[0]
                responseValueMsg = "Hey, the total number of "+f"{type}" +" in " + f"{county}" + " is " + f"{responseValue}"
            except Exception as e:
                print(e)
                returnBool = False
                responseValue=0
                responseValueMsg = "Hey Sorry, I could not find any cases for "+county

        return responseValueMsg,responseValue,returnBool, county


    def createRules(self, intent, entity, entity_type=None):
        if(intent == "welcome"):
            return self.performWelcomeActivity(entity)
        elif (intent == "user_name" or entity_type == "personName"):
            return self.performUserWelcome(entity)
        elif (intent == "mobile_number"):
            return self.extractMobileNumber(entity)
        elif (intent == "zipcode_intent" or entity_type=="zipcode_entity" or entity_type=="zipcode_entity1" ):
            return self.covRest.getCountryNameFromPincode(entity)
            #return self.extractZipCodeInfo(entity)
        elif (intent=="total_cases"):
            countryName = self.getCountryName(entity)
            return self.covRest.getTotalCountByCountry(countryName,"All")
            # responsemsg , _ , _ , _ = self.getTotalCasesInfo(countryName,"All")
            # return responsemsg
        elif(intent=="confirmed_cases"):
            countryName = self.getCountryName(entity)
            return self.covRest.getTotalCountByCountry(countryName, "confirmed")
            # responsemsg, _, _, _ = self.getTotalCasesInfo(countryName, "confirmed")
            # return responsemsg
        elif(intent=="recovered_cases"):
            countryName = self.getCountryName(entity)
            return self.covRest.getTotalCountByCountry(countryName, "recovered")
            # responsemsg, _, _, _ = self.getTotalCasesInfo(countryName, "recovered")
            # return responsemsg
        elif(intent=="death_cases"):
            countryName = self.getCountryName(entity)
            return self.covRest.getTotalCountByCountry(countryName, "deaths")
            # responsemsg, _, _, _ = self.getTotalCasesInfo(countryName, "deaths")
            # return responsemsg
        elif(intent=="active_cases"):
            responsemsg = self.getTotalActiveCases(entity)
            return responsemsg
        elif (intent == "highest_confirmed_count"):
            # self.CCCases = getconfirmedCases()
            # self.lastDate, self.Columns = get_dates(self.CCCases)
            # responsemsg = self.getHighestCount(entity, self.CCCases, sortType="DESC", type="most confirmed cases")
            # return responsemsg
            return self.covRest.getTopCountyCases(entity, "DESC", "most_confirmed_cases")
        elif (intent == "lowest_confirmed_count"):
            # self.CCCases = getconfirmedCases()
            # self.lastDate, self.Columns = get_dates(self.CCCases)
            # responsemsg = self.getHighestCount(entity, self.CCCases, sortType="ASC", type="less confirmed cases")
            # return responsemsg
            return self.covRest.getTopCountyCases(entity, "ASC", "less_confirmed_cases")
        elif (intent == "highest_recovered_count"):
            # self.CRCases = getrecovredCases()
            # self.lastDate, self.Columns = get_dates(self.CRCases)
            # responsemsg = self.getHighestCount(entity, self.CRCases, sortType="DESC",type="most recovered cases")
            # return responsemsg
            return self.covRest.getTopCountyCases(entity, "DESC", "most_recovered_cases")
        elif (intent == "lowest_recovered_count"):
            # self.CRCases = getrecovredCases()
            # self.lastDate, self.Columns = get_dates(self.CRCases)
            # responsemsg = self.getHighestCount(entity, self.CRCases, sortType="ASC", type="less recovered cases")
            # return responsemsg
            return self.covRest.getTopCountyCases(entity, "ASC", "less_recovered_cases")

        elif (intent == "highest_death_count"):
            # self.CDCases  = gettotalDeathCases()
            # self.lastDate, self.Columns = get_dates(self.CDCases)
            # responsemsg = self.getHighestCount(entity, self.CDCases, sortType="DESC", type="most death cases")
            # return responsemsg
            return self.covRest.getTopCountyCases(entity, "DESC", "most_death_cases")
        elif (intent == "lowest_death_count"):
            # self.CDCases = gettotalDeathCases()
            # self.lastDate, self.Columns = get_dates(self.CDCases)
            # responsemsg = self.getHighestCount(entity, self.CDCases, sortType="ASC", type="less death cases")
            # return responsemsg
            return self.covRest.getTopCountyCases(entity, "ASC", "less_death_cases")
        elif(intent=="good_bye"):
            responseMsg = self.peformGoodBye()
            return responseMsg
        elif (intent=="user_email"):
            return self.covRest.sendEmailToRest(entity)
            #return self.sentEmailToUser(entity)
        elif(intent == "stupid"):
            return "Hey..! Pleae ask me about covid-19 cases.. \n \n I have been taught only about that."
        elif(intent =="preventive_measures"):
            return "Hey, The Preventive Measures are  : \n \n" \
                                             "1. STAY Home \n " \
                                             "2. KEEP a safe distance \n " \
                                             "3. WASH your hands often \n " \
                                             "4. COVER your cough \n " \
                                             "5. SICK ? Please call the helpline"
        else:
            return "Sorry I cannot recognize your msg. Please provide a correct message. For Eg., total cases in India"

    def performWelcomeActivity(self, entity):
        response = "Welcome, I am a covid bot. \n Can you please provide your name ?"
        return response

    def getTotalActiveCases(self, entity, type="active cases"):
        _, totalccases, resp1, country = self.getTotalConfirmedCasesInWorld(entity, self.CCCases)
        _, totalrcases, resp2, country = self.getTotalConfirmedCasesInWorld(entity, self.CRCases)
        _, totaldcases, resp3, country = self.getTotalConfirmedCasesInWorld(entity, self.CDCases)
        active_count = totalccases - totalrcases - totaldcases
        if(not resp1 and resp2 and resp3):
            response = "Sorry I cannot recognize your msg. Please provide a ccorrect message. For Eg., total cases in India"
        else:
            county = "**"+ str(country).title() + "**"
            response = "Hey, the total number of "+type +" in " + county + " is " + f"{active_count}"

        return response

    def getHighestCount(self, entity=1, df=None, sortType="DESC", type="cases"):
        try:
            if(entity=="" or entity==None):
                entity=1
            groupedDF = df.groupby("Country/Region")[self.Columns[self.lastDate]].sum()
            groupedDF = groupedDF.reset_index()
            groupedDF.columns = ['country','total']
            if(sortType=="DESC"):
                groupedDF = groupedDF.sort_values(['total'], ascending=False)
            else:
                groupedDF = groupedDF.sort_values(['total'], ascending=True)

            results = groupedDF.head(int(entity)).values
            if(len(results) > 0):
                type = str(type).title()
                responseMsg = "Top Countreis with "+f"{type} "+ " \n \n"
                for xx in results:
                    #print(i)

                    responseMsg += "***"+str(xx[0]).title()+"*** has \t  " +f"{xx[1]}  cases \n \n"

            else:
                responseMsg = "Hey sorry, I couldn't recognise your message. Please give an appropriate message. \n " \
                              "For Eg., total number of confirmed cases"
        except Exception as e:
            responseMsg = "Hey sorry, I couldn't recognise your message. Please give an appropriate message. \n " \
                              "For Eg., total number of confirmed cases"
            print(e)
        return responseMsg

    def getCountryName(self, country):
        if (len(country) == 2):
            if (str(country).lower() in self.countWithCodes.keys()):
                country = self.countWithCodes[country]
        elif (len(country) == 3):
            if (str(country).lower() in self.countWithCodes.keys()):
                country = self.countWithCodes[country]
        elif (str(country).lower() == "uk"):
            country = "united kingdom"
        country = str(country).lower()
        return country

    def peformGoodBye(self):
        responseMSg = "Thank you "+ self.userName + " it was good interacting wtih you.. Could you please confirm your email please ?"
        return responseMSg

    def performUserWelcome(self, entity):
        self.userName = str(f'{entity}').title()
        responseMSg = "Hey " + self.userName + " thanks for mentioning your name.. \n Can you please confirm your mobile number ?"
        return responseMSg

    def extractMobileNumber(self, entity):

        self.mobieNumber = str(entity)
        regex = "(\w{3})\w{3}\w{4}"
        if re.search(regex,self.mobieNumber):
            responseMSg = "Thanks "+ self.userName+" for your mobile number. \n Now you can your enquire about the covid-19 cases. \n \n " \
                                                   "At any point if you want to conclude the chat. Say Good bye"
        else:
            responseMSg = "Mobile number is not in appropriate format. \n can you please re-enter."

        return responseMSg

    def sentEmailToUser(self, entity):
        # creates SMTP session
        if(str(entity)==""):
            responseMsg = "Please provide a valid email"
        else:
            try:
                fromMy = 'covid19.luisbot@yahoo.com'  # fun-fact: from is a keyword in python, you can't use it as variable, did abyone check if this code even works?
                to = str(entity).lower()
                subj = 'Covid-19 Details And Preventive Measures'
                from datetime import date
                today = date.today()
                #print("Today's date:", today)
                date = str(today)
                _,totalccases, totalrcases, totaldcases = self.getTotalCasesInfo(type="All")
                message_text = "Hi "+ self.userName +" \n \n As on #date total number of covid-19 cases in the World is #totalccases, \n total number of recovered" \
                                                     "cases is #totalrcases and \n total number of death cases is #totaldcases. \n \n \n " \
                                                     "Preventive Measures are  : \n \n" \
                                                     "1. STAY Home \n " \
                                                     "2. KEEP a safe distance \n " \
                                                     "3. WASH your hands often \n " \
                                                     "4. COVER your cough \n " \
                                                     "5. SICK ? Please call the helpline"

                message_text = message_text.replace("#date", date)
                message_text = message_text.replace("#totalccases", str(totalccases))
                message_text = message_text.replace("#totalrcases", str(totalrcases))
                message_text = message_text.replace("#totaldcases", str(totaldcases))

                msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % (fromMy, to, subj, date, message_text)

                username = str('covid19.luisbot@yahoo.com')
                password = str('wznd bqky ojoy cnpf')


                server = smtplib.SMTP("smtp.mail.yahoo.com", 587)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(username, password)
                server.sendmail(fromMy, to, msg)
                server.quit()
                return "Thank you..!! Details about covid-19 and the preventive measure is send to your email "+f"{entity}"
            except Exception as ex:
                print(ex)
                responseMsg = "Thank you..!! Error in sending Email"

        return responseMsg

    def extractZipCodeInfo(self, entity):
        geolocator = Bing(api_key="Ar-aTc8AF9MnqnsJAbSHorGLYZUugT5Rd2gmD6Aq6Cd-z-kMzJ71u3Ku7h_s0MNh")
        zipcode =str(entity)
        location = geolocator.geocode(zipcode, include_country_code=True, include_neighborhood=True)
        resonseMSg = ""
        try :

            countryValues = location.raw
            country = countryValues['address']['countryRegionIso2']
            print("Country is ", country)
            try:
                state = countryValues['address']['adminDistrict']
                print("state is ",state)
                inputValues = str(state)+", "+str(country)
                compleleteList = geolocator.geocode(inputValues, include_country_code=True, include_neighborhood=True)
                correctStateName = str(compleleteList.raw['address']['formattedAddress'])
                #_, count, _ , country= self.getTotalConfirmedCasesInWorld(country,self.CCCases)
                resonseMSg, _, _, _ = self.getTotalCasesInfo(correctStateName,"All")

                return resonseMSg
            except Exception as ex:
                print(ex)
                resonseMSg1, _, _, _ = self.getTotalCasesInfo(country, "All")
                resonseMSg = "Sorry..!! I could not find the details for "+ zipcode.upper() +" \n Instead I am giving the below details " \
                               " as the "+zipcode.upper()+" belongs to "+country+"\n \n" \
                              ""+ resonseMSg1
                return resonseMSg

        except Exception as e:
            print(e)
            return "Sorry I am not able to recognize the zipcode "+ zipcode

    def getTotalCasesInfo(self, entity='All', type="All"):
        ccases= 0
        rcases = 0
        dcases = 0
        indiaFlag = True
        entity =str(entity).lower()
        try:
            if((entity == None) | (entity== "") | (entity == 'globe') | (entity=="world") |
                    (entity=="All")):
                url = "https://corona.lmao.ninja/v2/all"
                entity = "World"

            else:
                url1 = "https://api.rootnet.in/covid19-in/stats/latest"
                responseValue = requests.get(url1)
                ind_data = responseValue.json()
                regionalData= ind_data['data']['regional']
                statesList= []
                data = {}
                for x in regionalData:
                    states = str(x['loc']).lower()
                    statesList.append(states)
                entity = str(entity).lower()
                try:
                    indexMatch = statesList.index(entity)
                    if(indexMatch >= 0):
                        entity = str(entity).title()
                        entity = "**" + entity + "**"
                        data['cases'] =regionalData[indexMatch]['confirmedCasesIndian']
                        data['recovered'] =regionalData[indexMatch]['discharged']
                        data['deaths'] =regionalData[indexMatch]['deaths']
                        data['active'] = 0
                        #data['countryInfo']['flag'] = "https://raw.githubusercontent.com/NovelCOVID/API/master/assets/flags/in.png"
                        responeMsg,ccases,rcases,dcases = self.formCasesString(data, type, entity)
                        indiaFlag= False
                except Exception as ex :
                    geolocator = Bing(api_key="Ar-aTc8AF9MnqnsJAbSHorGLYZUugT5Rd2gmD6Aq6Cd-z-kMzJ71u3Ku7h_s0MNh")
                    zipcode = str(entity)
                    location = geolocator.geocode(zipcode, include_country_code=True, include_neighborhood=True)
                    try:
                        entity = location.raw['address']['countryRegion']
                        url = "https://corona.lmao.ninja/v2/countries/" + entity
                    except Exception as exp:
                        print(exp)
                    print(ex)


            if(indiaFlag):
                response = requests.get(url)
                if (response.status_code == 200):
                    data = response.json()
                    entity = entity if (entity == "World") else data['country']
                    entity = str(entity).title()
                    entity = "**" + entity + "**"
                    if(type=="All"):
                        ccases = data['cases']
                        rcases = data['recovered']
                        dcases = data['deaths']
                        accases = data['active']
                        responeMsg = "Hey, the latest covid-19 cases of " + f"{entity}" + " with \n \n" + "Confirmed cases as " + f"{ccases}" + "\n \n" \
                                        "and the Recovered Cases counts to " + f"{rcases}" + "\n \n" + "and finally the Death Cases are " + f"{dcases}"
                    elif(type=="confirmed"):
                        ccases = data['cases']
                        responeMsg = "The total confirmed covid-19 cases of " + f"{entity}" + " is " + f"{ccases}"
                    elif (type == "deaths"):
                        dcases = data['deaths']
                        responeMsg = "The total death cases of covid-19 in " + f"{entity}" + " is " + f"{dcases}"
                    elif (type == "recovered"):
                        rcases = data['recovered']
                        responeMsg = "The recovered cases for covid-19 in " + f"{entity}" + " is Recovered Cases " + f"{rcases}"
                    if( 'countryInfo' in data):
                        responeMsg+="$$$"+data['countryInfo']['flag']

                else:
                    responeMsg = "Sorry!! I could not reach the api.."
        except Exception as ex:
            print(ex)
            responeMsg = "Sorry!! I could not recognized you.."


        return responeMsg, ccases,rcases,dcases

    def formCasesString(self, data, type, entity):
        ccases = 0
        rcases = 0
        dcases = 0
        responeMsg=""
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

        #responeMsg += "$$$" + data['countryInfo']['flag']


        return  responeMsg, ccases,rcases,dcases


