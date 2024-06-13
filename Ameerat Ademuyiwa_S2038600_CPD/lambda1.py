# LambdaSQS2038600 - Processes Messages received from SQS Queue
import boto3
import re

# Initialize Boto3 clients
rekognition_client = boto3.client('rekognition')
dynamodb_client = boto3.client('dynamodb')
s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')


# DynamoDB table name
dynamodb_entry_table = 'VehiculeEntryS2038600'
bucket_name = 'buckets2038600'
queue_url = 'https://sqs.us-east-1.amazonaws.com/607200637845/SqsS2038600'



def lambda_handler(event, context):
    # Get a list of object keys in the bucket
    objects = s3_client.list_objects(Bucket=bucket_name)
    image_names = [content['Key'] for content in objects.get('Contents', [])]

    for vehicule_name in image_names:
        # Detect labels using Rekognition
        rekognition_response = rekognition_client.detect_labels(
            Image={'S3Object': {'Bucket': bucket_name, 'Name': vehicule_name}}
        )

        # Extract 3 top labels and their confidence scores
        labels_with_confidence = rekognition_response['Labels'][:3]
        top_labels = [label['Name'] for label in labels_with_confidence]
        average_confidence_score = sum(label['Confidence'] for label in labels_with_confidence) / len(labels_with_confidence)

        # Detect text using Rekognition
        text_detection_response = rekognition_client.detect_text(
            Image={'S3Object': {'Bucket': bucket_name, 'Name': vehicule_name}}
        )

        # Filter out text detections below the vehicle
        plate_number = extract_plate_number(text_detection_response)

        # Save results to DynamoDB
        save_to_dynamodb(vehicule_name, top_labels, average_confidence_score, plate_number)

    # Return a response
    return {'statusCode': 200, 'body': 'Labels, Confidence Score, and Plate Numbers added are saved into the Entry Table'}




def extract_plate_number(text_detection_response):
    # Extract detected text from Rekognition response
    detected_text = [text_detection['DetectedText'] for text_detection in text_detection_response['TextDetections']]

    # Iterate through detected text and check for numbers indicative of a license plate
    for text in detected_text:
        # Assuming license plates contain a combination of letters and numbers
        # You can adjust this condition based on the specific format of license plates in your region
        if any(char.isdigit() for char in text):
            return text

    return None



def save_to_dynamodb(vehicule_name, labels, average_confidence_score, plate_number):
    # Save results to DynamoDB table
    item = {
        'VehiculeName': {'S': vehicule_name},
        'Labels': {'SS': labels},
        'Confidence Score': {'N': str(average_confidence_score)}
    }
    
    # If plate number is detected, add it to the item
    if plate_number is not None:
        item['Plate Number'] = {'S': plate_number}

    try:
        # Put the item into DynamoDB table
        dynamodb_client.put_item(TableName=dynamodb_entry_table, Item=item)
        return {'statusCode': 200, 'body': 'Labels, average confidence score, and plate number added successfully'}
    except dynamodb_client.exceptions.ClientError as e:
        # Handle DynamoDB errors
        error_message = f"Error saving item to DynamoDB: {e}"
        print(error_message)
        return {'statusCode': 500, 'body': error_message}

