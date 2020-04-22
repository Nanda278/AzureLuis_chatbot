#import pyowm
from config.config_reader import ConfigReader
import json


class WeatherInformation():
    def __init__(self):
        self.config_reader = ConfigReader()
        self.configuration = self.config_reader.read_config()
        #self.owmapikey = self.configuration['WEATHER_API_KEY']
        #self.owm = pyowm.OWM(self.owmapikey)

    def get_weather_info(self,city):

        self.bot_says = "Today the weather in"
        return self.bot_says

    def getIntentAndEntity(self,result):
        intent_str = json.loads((str(result.top_scoring_intent)).replace("'", "\""))
        if("intent" in intent_str):
            intent = intent_str.get('intent')
        else:
            intent=""
        if(len(result.entities)) > 0:
            entity = result.entities[0].entity
            entity_type=result.entities[0].type
        else:
            entity = ""
            entity_type = ""
        return intent,entity, entity_type