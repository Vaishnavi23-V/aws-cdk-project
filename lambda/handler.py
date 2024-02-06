import json
import boto3
import uuid

# Create the DynamoDB resource and table
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('HelloWorldTable')

def hello(event, context):
    cognito_identity_token = event['headers'].get('Authorization')
    print('checking auth token')
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',  
        'Access-Control-Allow-Methods': 'OPTIONS, POST',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    }

    if event['httpMethod'] == 'OPTIONS':
        # Return CORS headers for preflight requests
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps('Preflight request received'),
        }

    if cognito_identity_token:
        # User is authenticated, proceed with business logic
        try:
            unique_id = str(uuid.uuid4())
            response = table.put_item(
                Item={
                    'id': unique_id,
                    'message': 'Hello World!'
                }
            )
            print('Storing hello world')
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps('Hello World stored in DynamoDB!')
            }
        except Exception as e:
            print(f"Error storing Hello World in DynamoDB: {e}")
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps('Internal Server Error')
            }
    else:
        # User is not authenticated
        return {
            'statusCode': 401,
            'headers': headers,
            'body': json.dumps('Unauthorized')
        }
