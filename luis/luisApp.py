from botbuilder.core import TurnContext, ActivityHandler, MessageFactory
from botbuilder.ai.luis import LuisApplication, LuisPredictionOptions, LuisRecognizer
import json
from covid.weatherApp import WeatherInformation
from covid.covidApp import covidDetails
from config.config_reader import ConfigReader
from logger.logger import Log
import re


class LuisConnect(ActivityHandler):
    def __init__(self):
        self.config_reader = ConfigReader()
        self.configuration = self.config_reader.read_config()
        self.luis_app_id = self.configuration['LUIS_APP_ID']
        self.luis_endpoint_key = self.configuration['LUIS_ENDPOINT_KEY']
        self.luis_endpoint = self.configuration['LUIS_ENDPOINT']
        print(self.luis_app_id,self.luis_endpoint, self.luis_endpoint_key)
        self.luis_app = LuisApplication(self.luis_app_id, self.luis_endpoint_key, self.luis_endpoint)
        self.luis_options = LuisPredictionOptions(include_all_intents=True, include_instance_data=True)
        self.luis_recognizer = LuisRecognizer(application=self.luis_app, prediction_options=self.luis_options,
                                              include_api_results=True)
        self.log = Log()



    async def on_message_activity(self, turn_context: TurnContext):

        weather_info = WeatherInformation()
        covid_info = covidDetails()
        print("Before luis hit")
        #luisCon = LuisConnect()
        luis_result = await self.luis_recognizer.recognize(turn_context)
        result = luis_result.properties["luisResult"]
        print((str(result)))
        intent_str = json.loads((str(result.top_scoring_intent)).replace("'", "\""))
        print(intent_str)
        intent, entity, entity_type = weather_info.getIntentAndEntity(result)
        user_msg = str(turn_context.activity.text)
        response = covid_info.createRules(intent,entity, entity_type)
        if (len(response.split("$$$")) > 1):
            responseValue = response.split("$$$")
            response = responseValue[0]
            image_url=responseValue[1]
            await turn_context.send_activity(
                MessageFactory.content_url(text=response, url=image_url, content_type="image/png"))
        else:
            await turn_context.send_activity(
                MessageFactory.text(text=response))

        sessionid = str(turn_context.activity.recipient.id)

        self.log.write_log_to_db(sessionID=sessionid, log_message="user Says: " + str(user_msg))
        self.log.write_log_to_db(sessionID=sessionid, log_message="Bot Says: " + str(response))
        #response = intent_str
