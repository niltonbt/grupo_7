# handler.py

import boto3
import json

def process_order(event, context):
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        status = object_key.split('/')[0]  # Obtendo o status do pedido do prefixo do objeto
        order_data = {
            'bucket': bucket_name,
            'object_key': object_key,
            'status': status
        }
        # Decida para qual fila SQS enviar o pedido
        if status == 'em-preparacao':
            send_to_preparation_queue(order_data)
        elif status == 'pronto':
            send_to_ready_queue(order_data)

def send_to_preparation_queue(order_data):
    sqs_client = boto3.client('sqs')
    sqs_queue_url = 'URL_DA_FILA_PREPARACAO'
    sqs_client.send_message(
        QueueUrl=sqs_queue_url,
        MessageBody=json.dumps(order_data)
    )

def send_to_ready_queue(order_data):
    sqs_client = boto3.client('sqs')
    sqs_queue_url = 'URL_DA_FILA_PRONTO'
    sqs_client.send_message(
        QueueUrl=sqs_queue_url,
        MessageBody=json.dumps(order_data)
    )

def insert_into_dynamodb_preparation(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('pedidos-preparacao')
    for record in event['Records']:
        order_data = json.loads(record['body'])
        table.put_item(Item=order_data)

def insert_into_dynamodb_ready(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('pedidos-pronto')
    for record in event['Records']:
        order_data = json.loads(record['body'])
        table.put_item(Item=order_data)
