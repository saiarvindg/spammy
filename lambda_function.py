"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
from boto3.dynamodb.conditions import Key, Attr
import boto3
import datetime


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': '<speak>' + output + '</speak>'
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
    
# --------------- Interacting with other AWS services ------------------

def email_user(subject,body,from_addr,to_addr):
    currdatetime = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    sesclient = boto3.client('ses')
    response = sesclient.send_email(
        Source=from_addr,
        Destination={
            'ToAddresses':[to_addr]
        },
        Message={
            'Subject': {
                'Data':subject + ' @ ' + currdatetime,
                'Charset': 'utf8'
            },
            'Body': {
                'Text': {
                    'Data': body,
                    'Charset':'utf8'
                }
            }
        },
        ReplyToAddresses=[from_addr])
    print("Line 67: send_email: " + str(response))

# only method that directly returns a build_response
def get_spam_nums():
    nums = ''
    txtmsg = 'AWS Spam report @ ' + datetime.datetime.now().strftime("%I:%M%p) + ':\nNumber: Count\n'
    emailmsg = 'AWS Spam Report\n'
    dd = boto3.resource('dynamodb', region_name = 'us-east-1')
    table = dd.Table('User1Spam')
    response = table.scan()
    numCount = int(response['Count'])
        
    for idx, item in enumerate(response['Items']):
        #spamnum = '<say-as interpret-as="digits">' + str(item['SpamNumber']) + '</say-as>'
        #spamnum_count = '<say-as interpret-as="digits">' +  str(item['Count']) + '</say-as>'
        spamnum = str(item['SpamNumber']) 
        spamcount = str(item['Count'])
        txtmsg += spamnum + ': ' + spamcount + '\n'
        emailmsg += spamnum + ' called you ' + spamcount + ' times\n' 
        #nums += spamnum + ' called you ' + spamnum_count + ' times, '
    #return nums
    
    # Send a text if there are less than 6 spam numbers using SNS
    if numCount < 6:
        # call SNS text message method here
        sns = boto3.client('sns')
        number = '+14848688957' #this number should be gotten from the User's Alexa/Amazon account using OAuth
        sns.publish(PhoneNumber = number, Message = txtmsg)
        return build_response({}, build_speechlet_response("Get Spam Numbers", "I've sent a text message to you", None, True))
    else:
        # if there are more than 6 spam numbers send them an email using SES
        #emailmsg += '</ul></body></html>'
        email_user("Spam Number Report from AWS",emailmsg, "sai.arvindg@gmail.com", "saiarvindg@yahoo.com")
        return build_response({}, build_speechlet_response("Get Spam Numbers", "I've sent an email to you.", None, True))
        
    return build_response({}, build_speechlet_response("Get Spam Numbers", 
    "I did't catch that. Please try again.", None, True))
    
def get_spam_num_count(num):
    dd = boto3.resource('dynamodb', region_name = 'us-east-1')
    table = dd.Table('User1Spam')
    num = int(float(num))
    try:
        response = table.get_item(
            Key={
                'SpamNumber':num
            }
        )
    except Exception, e:
        print(e.response)
        return "Error"
        
    
    if 'Item' not in response:
        return 0
        
    return response['Item']['Count']

# returns what to say directly
def add_num(num):
    dd = boto3.resource('dynamodb', region_name = 'us-east-1')
    table = dd.Table('User1Spam')
    num = int(float(num))
    try:
        # check if the number already exists
        response = get_spam_num_count(num)
        
        # if num already exists - update the count
        if response > 0:
            #old_count = response['Item']['Count']
            new_count = response + 1
            table.put_item(
                Item={
                    'SpamNumber': num,
                    'Count': new_count
                })
            return '<say-as interpret-as="digits">' + str(num) + '</say-as> has now called you ' + str(new_count) + ' times.'
        else:
            # add the new spam number
            table.put_item(
                Item={
                    'SpamNumber': num,
                    'Count': 1
                })
            return 'I have added <say-as interpret-as="digits">' + str(num) + '</say-as> to the list of spam numbers.'
    except Exception, e:
        print(e)
        return "Error" 
    
    # if not
    if len(response['Item']) == 0:
        # call the Table's put_item function here with count = 1
        return 'I have added <say-as interpret-as="digits">' + str(num) + '</say-as> to your address book'
    else:
        # get the count and call the Table's upate_item here and update the count
        return "I have updated the count of the spam number"
        
def delete_num(num):
    dd = boto3.resource('dynamodb', region_name = 'us-east-1')
    table = dd.Table('User1Spam')
    num = int(float(num))
    try:
        if get_spam_num_count(num) > 0:
            response = table.delete_item(
                Key={
                    'SpamNumber':num
                })
        else:
            return "That number is not in the list of spam numbers."
    except Exception, e:
        print(e)
        return "Error"
    
    return 'Deleted <say-as interpret-as="digits">' + str(num) + '</say-as> from the list of spam numbers.'

# --------------- Functions that control the skill's behavior ------------------
    
def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    #speech_output = "The spam numbers and counts are " + get_spam_nums()
    speech_output = "What spam issues can I help you with today?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "What would you like me to do?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_spam_num_count_request(intent, session):
    card_title = "Get the Spam Count of a Number"
    session_attributes = {}
    speech_output = ''
    reprompt_text = "Sorry, I didn't catch that. Please try again. Make sure the number is 10 digits."
    
    if 'num' in intent['slots'] and (len(intent['slots']['num']['value']) == 10):
        num = intent['slots']['num']['value']
        response = get_spam_num_count(num)
        if response == "Error":
            speech_output = "Sorry, I didn't catch that. Please try again. Make sure the number is only 10 digits"
            should_end_session = False
        elif response == 0:
            speech_output = "That number has not called you yet."
            should_end_session = True
        else:
            speech_output = "That number has called you " + str(response) + " times"
            should_end_session = True
    else:
        speech_output = "Sorry, I didn't understand. Please try again. Make sure the number is only 10 digits"
        should_end_session = False
    
    return build_response({},build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def add_spam_num_request(intent, session):
    card_title = "Add a Spam Number"
    session_attributes = {}
    speech_output = ''
    reprompt_text = "Sorry, I didn't catch that. Please try again. Make sure the number is 10 digits."
    
    if 'num' in intent['slots'] and (len(intent['slots']['num']['value']) == 10):
        num = intent['slots']['num']['value']
        response = add_num(num)
        if response == "Error":
            speech_output = "Sorry, I didn't catch that. Please try again. Make sure the number is 10 digits."
            should_end_session = False
        else:
            speech_output = response
            should_end_session = True
    else:
        speech_output = "Sorry, I didn't understand. Please try again. Make sure the number is 10 digits."
        should_end_session = False
    
    return build_response({},build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
    
def delete_spam_num_request(intent,session):
    card_title = "Delete a Spam Number"
    session_attributes = {}
    speech_output = ''
    reprompt_text = "Sorry, I didn't catch that. Please try again. Make sure the number is 10 digits."
    
    if 'num' in intent['slots'] and (len(intent['slots']['num']['value']) == 10):
        num = intent['slots']['num']['value']
        response = delete_num(num)
        if response == "Error":
            speech_output = "Sorry, I didn't catch that. Please try again. Make sure the number is 10 digits."
            should_end_session = False
        else:
            speech_output = response
            should_end_session = True
    else:
        speech_output = "Sorry, I didn't understand. Please try again. Make sure the number is 10 digits."
        should_end_session = False
    
    return build_response({},build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
    

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'], ", intent_name=" + intent_request['intent']['name'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "SendSpamNumReport":
        return get_spam_nums()
    elif intent_name == "GetSpamNumberCount":
        return get_spam_num_count_request(intent, session)
    elif intent_name == "AddSpamNum":
        return add_spam_num_request(intent,session)
    elif intent_name == "DeleteSpamNum":
        return delete_spam_num_request(intent,session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    #if (event['session']['application']['applicationId'] != " amzn1.ask.skill.d7affff1-133b-41b1-a6ac-ab429f02d4b9"):
     #   raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
