
import asyncio

from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, MemoryStorage, UserState
from botbuilder.schema import Activity, ActionTypes
from flask import Flask, request, Response, render_template

from luis.luisApp import LuisConnect
from covid import weolcomebot

app = Flask(__name__, template_folder=".")
loop = asyncio.get_event_loop()


bot_settings = BotFrameworkAdapterSettings("", "")
bot_adapter = BotFrameworkAdapter(bot_settings)

#CON_MEMORY = ConversationState(MemoryStorage())
Mm = MemoryStorage()
user_state = UserState(Mm)
luis_bot_dialog = LuisConnect()
print(luis_bot_dialog.luis_endpoint)
wbot = weolcomebot.WelcomeUserBot(user_state)



@app.route("/helloworld", methods=["GET"])
def helloWorld():
    return "Hello World"

@app.route("/")
def render_html_file():
    return render_template("index.html")


@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["content-type"]:
        #log=Log()
        #luis_bot_dialog.on
        request_body = request.json
        user_says = Activity().deserialize(request_body)

        # msg ="user says " + str(user_says)
        # print("user says ",+ msg)
        sessionid = str(request_body['recipient']['id'])
        print("session id is ",sessionid)
        authorization_header = (request.headers["Authorization"] if "Authorization" in request.headers else "")

        async def messages(truecontext):
            # Main bot message handler.

            response = await bot_adapter.process_activity(user_says, authorization_header, wbot.on_turn)
            return response
        task = loop.create_task(
        bot_adapter.process_activity(user_says, authorization_header, messages)
       )
        task

        async def call_user_fun(turncontext):
            await luis_bot_dialog.on_turn(turncontext)

        task = loop.create_task(
            bot_adapter.process_activity(user_says, authorization_header, call_user_fun)
        )
        loop.run_until_complete(task)
        return ""
    else:
        return Response(status=406)  # status for Not Acceptable




if __name__ == '__main__':
    app.run(port= 8000)
    #app.run()