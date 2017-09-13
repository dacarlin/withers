import os
import time
from slackclient import SlackClient

def get_bot_id(bot_name):
    slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == bot_name:
                return user['id']

BOT_ID = get_bot_id('trotsky')
TOKEN = os.environ.get('SLACK_TOKEN')

# constants
AT_BOT = "<@" + BOT_ID + ">"

# instantiate Slack & Twilio clients
slack_client = SlackClient(TOKEN)

def handle_command(command, channel):
    response = command or "Generic response" 
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            print(output) 
            if output and 'text' in output and AT_BOT in output['text']:
                flat_response = output['text'].split(AT_BOT)[1].strip() 
                return flat_response, output['channel']
    return None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Bot connected and running")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid token or bot ID?")
