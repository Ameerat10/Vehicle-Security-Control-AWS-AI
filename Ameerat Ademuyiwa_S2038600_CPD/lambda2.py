#LambdaUpdateTableS2038600 - Database Update Lambda Function
import boto3
import re

# Initialize Boto3 clients
dynamodb_client = boto3.client('dynamodb')
sns_client = boto3.client('sns')

# DynamoDB table names
entry_table_name = 'VehiculeEntryS2038600'
update_table_name = 'VehiculeUpdateS2038600'

# SNS topic ARN for email notifications
sns_topic_arn = 'arn:aws:sns:us-east-1:607200637845:VehiculeNotificationsS2038600'


def lambda_handler(event, context):
    # Retrieve all items from the DynamoDB entry table
    response = dynamodb_client.scan(TableName=entry_table_name)
    items = response.get('Items', [])

    for item in items:
        # Extract relevant data from the DynamoDB item
        vehicule_name = item.get('VehiculeName', {}).get('S')
        labels = item.get('Labels', {'SS': []})['SS']
        plate_number = item.get('Plate Number', {'S': ''})['S']

        # Determine if vehicle is blacklisted based on detected labels and plate number
        is_blacklisted = blacklisted_vehicle(labels, plate_number)

        # Save results to Vehicle DynamoDB table
        save_to_update_table(vehicule_name, plate_number, is_blacklisted)

        # Send email notification if vehicle is blacklisted
        if is_blacklisted:
            send_blacklisted_email(vehicule_name, plate_number, is_blacklisted)

    # Return a response
    return {'statusCode': 200, 'body': 'Successfully sent emails for blacklisted vehicules and saved statuses into the update table'}


def blacklisted_vehicle(labels, plate_number):
    # Check if plate number is less than 8 characters long or doesnt exist
    if not plate_number or len(plate_number) < 8:
        return True  # Vehicle is blacklisted if plate number format is invalid

    return False  # Vehicle is not blacklisted (whitelisted)


def save_to_update_table(vehicule_name, plate_number, is_blacklisted):
    # Determine the status based on whether the vehicule is blacklisted
    status = 'Blacklisted' if is_blacklisted else 'Whitelisted'

    # Save results to Vehicle DynamoDB table
    item = {
        'VehiculeName': {'S': vehicule_name},
        'Plate Number': {'S': plate_number},
        'Vehicule Status': {'S': status}  # Add the 'Vehicule Status' attribute
    }

    try:
        # Put the item into Vehicle DynamoDB table
        dynamodb_client.put_item(TableName=update_table_name, Item=item)
        print(f"Results saved into the update table for the vehicule image: {vehicule_name}")
    except dynamodb_client.exceptions.ClientError as e:
        # Handle DynamoDB errors
        error_message = f"Error saving item to Update Table: {e}"
        print(error_message)


def send_blacklisted_email(vehicule_name, plate_number, is_blacklisted):
    # Get the S3 bucket URL
    bucket_url = f"https://s3.amazonaws.com/buckets2038600/{vehicule_name}"

    # Send email notification to email address for blacklisted vehicles detected
    subject = 'Security Entrance Alert: Detection of Blacklisted Vehicle'
    body = f'A blacklisted Vehicle has been detected upon its arrival at the security entrance. This notification serves as an alert regarding the presence of a vehicle deemed unsuitable for access according to our security protocols. The vehicule details can be found below:\n\n'
    body += f'Vehicle Name: {vehicule_name}\n'
    body += f'Plate Number: {plate_number}\n'
    body += f'Download Vehicule Image here: {bucket_url}' 

    try:
        # Publish message to SNS topic only if vehicle is blacklisted
        if is_blacklisted:
            response = sns_client.publish(
                TopicArn=sns_topic_arn,
                Message=body,
                Subject=subject
            )
            print(f"Email notification sent for the blacklisted vehicle: {vehicule_name}")
        else:
            print(f"No email notification sent for the vehicle: {vehicule_name}. Vehicle is not blacklisted, thus whitelisted.")
    except Exception as e:
        # Handle SNS errors
        print(f"Error sending email notification for vehicle: {vehicule_name}, Error: {str(e)}")

