import os
from slack import RTMClient
from rlg_util import *

# file containing list of restaurants
rest_file='restaurant_list'

# random seed for restaurant selection
random.seed()

@RTMClient.run_on(event="message")
def respond(**payload):

  # save last event for debugging in case of crash
  with open("log",'w') as log:
    log.write(str(payload)+'\n')

  data = payload['data']
  web_client = payload['web_client']

  # check for direct message
  if 'text' in data:
    user_id, message = parse_direct_mention(data['text'])

    # special case: bitmoji "what's for lunch?"
    if "/bitmoji" in data['text'] and "for lunch" in data['text']:
      user_id = rlgbot_id
      message = "where"

    if user_id == rlgbot_id:
      channel_id = data['channel']
#     thread_ts = data['ts']
      user = data['user']

      response=handle_command(message, user, rest_file)

      web_client.chat_postMessage(
        channel=channel_id,
        text=response #,
#       thread_ts=thread_ts
      )

  # if bot's suggestion, save data
  if 'username' in data:
    if data['username']=='Random Lunch Generator':
#      print("received bot message event")
#      print(data["text"])
      if "random restaurant" in data["text"] or "formula" in data["text"] or "VETOED" in data["text"]:
        with open("last_suggestions", 'w') as log:
          log.write(data["event_ts"]+'\n')

@RTMClient.run_on(event="reaction_added")
def react(**payload):

  # save last event for debugging in case of crash
  with open("log",'w') as log:
    log.write(str(payload)+'\n')

  data = payload['data']
  web_client = payload['web_client']
  channel_id=data['item']['channel']

  # check that reaction is to the lunch bot's last suggestion
  with open("last_suggestions", 'r') as log:
    suggested_time=log.readline().strip()
#    print(suggested_time)
 
  if data['item']['ts']==suggested_time:
    response=handle_reaction(data["reaction"], data["user"], rest_file)

    if response!=None:
      web_client.chat_postMessage(
        channel=channel_id,
        text=response #,
#       thread_ts=thread_ts
      )
  

with open('slack_token','r') as pwd:
    slack_token=pwd.readline().strip()
with open('bot_id', 'r') as uid:
    rlgbot_id=uid.readline().strip()
rtm_client = RTMClient(token=slack_token)
#rlgbot_id = rtm_client.api_call("auth.test")["user_id"]
rtm_client.start()
