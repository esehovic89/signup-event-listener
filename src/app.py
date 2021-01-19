import urllib.request
import json
import logging
import boto3
import time
import os
from boto3.dynamodb.conditions import Attr


SENDER_EMAIL = "mensur@mandzuka@gmail.com"
MESSAGE_TEMPLATE_INTRO = "Hi {}, welcome to komoot. "
MESSAGE_TEMPLATE_SUFFIX = " also joined recently"
TTL_IN_SECONDS = 300


table_name = os.environ['TABLE_NAME']
region_name = os.environ['REGION_NAME']
notification_endpoint = os.environ['NOTIFICATION_ENDPOINT']


client = boto3.resource('dynamodb', region_name=region_name)
table = client.Table(table_name)


def lambda_handler(event, context):
    sns_message_payload = json.loads(event['Records'][0]['Sns']['Message'])
    logging.info("Received message: {}", sns_message_payload)

    user_name = sns_message_payload['name']
    user_id = sns_message_payload['id']

    request_body = create_notification_service_payload(user_name, user_id)
    post_notification(request_body)
    add_recent_signup(user_id, user_name)


def get_recent_signups():
    current_epoch_in_seconds = int(time.time())
    search_filter = Attr('expire_on').gt(current_epoch_in_seconds)
    return table.scan(
        FilterExpression=search_filter,
        Limit=3
    )['Items']

def add_recent_signup(user_id, user_name):
    expire_on = int(time.time() + TTL_IN_SECONDS)
    table.put_item(Item={
        'user_id': user_id,
        'user_name': user_name,
        'expire_on': expire_on
    })
    logging.info("User with ID: {} added".format(user_id))


def create_notification_service_payload(user_name, user_id):
    recent_signups = get_recent_signups()
    recent_ids = [int(item['user_id']) for item in recent_signups]
    recent_names = [item['user_name'] for item in recent_signups]

    logging.info(recent_signups)
    notification_message = {
        "sender": SENDER_EMAIL,
        "receiver": user_id,
        "message": create_user_message(user_name, recent_names),
        "recent_user_ids": recent_ids
    }

    return notification_message

def post_notification(body):
    notification_request = urllib.request.Request(notification_endpoint)
    notification_request.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondata = json.dumps(body)
    jsondataasbytes = jsondata.encode('utf-8')
    notification_request.add_header('Content-Length', len(jsondataasbytes))
    return urllib.request.urlopen(notification_request, jsondataasbytes)


def create_user_message(user_name, recent_names):
    first_sentence = MESSAGE_TEMPLATE_INTRO.format(user_name)

    if len(recent_names) == 1:
        return first_sentence + recent_names[0] + MESSAGE_TEMPLATE_SUFFIX

    elif len(recent_names) == 2:
        return first_sentence + recent_names[0] + " and " + recent_names[1] + MESSAGE_TEMPLATE_SUFFIX

    elif len(recent_names) == 3:
        return first_sentence + recent_names[0] + ", " + recent_names[1] + " and " + recent_names[2] + MESSAGE_TEMPLATE_SUFFIX

    else:
        return first_sentence
