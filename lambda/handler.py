import json
import boto3
import uuid

# Create the DynamoDB resource and table
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('HelloWorldTable')

def hello(event, context):
    try:
        # Generate a unique identifier for 'id'
        unique_id = str(uuid.uuid4())

        # Put item into DynamoDB
        response = table.put_item(
            Item={
                'id': unique_id,
                'message': 'Hello World!'
            }
        )

        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps('Hello World stored in DynamoDB!')
        }
    except Exception as e:
        # Log error and return error response
        print(f"Error storing Hello World in DynamoDB: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Internal Server Error')
        }
