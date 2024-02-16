import json
import boto3
from datetime import datetime

def admin(event, context):
    operation = event.get("operation")

    if not operation:
        return {
            'statusCode': 400,
            'body': json.dumps('Operation not specified')
        }

    user_pool_id = event.get("userPoolId")
    if not user_pool_id:
        return {
            'statusCode': 400,
            'body': json.dumps('User Pool ID not specified')
        }

    client = boto3.client('cognito-idp')

    if operation == "add_user":
        username = event.get("username")
        email = event.get("email")

        if not username or not email:
            return {
                'statusCode': 400,
                'body': json.dumps('Username or Email not specified')
            }

        try:
            response = client.admin_create_user(
                UserPoolId=user_pool_id,
                Username=username,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                ],
                TemporaryPassword='Temp1234!',
                MessageAction='SUPPRESS',  # Do not send a confirmation email
            )

            return {
                'statusCode': 200,
                'body': json.dumps(response, default=str)  # Convert datetime objects to strings
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Error: {str(e)}')
            }

    elif operation == "delete_user":
        username = event.get("username")

        if not username:
            return {
                'statusCode': 400,
                'body': json.dumps('Username not specified')
            }

        try:
            response = client.admin_delete_user(
                UserPoolId=user_pool_id,
                Username=username
            )

            return {
                'statusCode': 200,
                'body': json.dumps(response, default=str)  # Convert datetime objects to strings
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Error: {str(e)}')
            }

    else:
        return {
            'statusCode': 400,
            'body': json.dumps(f'Invalid operation: {operation}')
        }
