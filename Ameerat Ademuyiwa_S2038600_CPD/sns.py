import boto3

# Initialize Boto3 client for SNS
sns_client = boto3.client('sns')

# Name of the SNS topic for vehicle notifications
sns_topic_name = 'VehiculeNotificationsS2038600'

def create_sns_topic():
    try:
        # Create the SNS topic
        response = sns_client.create_topic(Name=sns_topic_name)
        topic_arn = response['TopicArn']
        print(f"Created SNS topic: {sns_topic_name}")
        
        # Subscribe an email address to the SNS topic
        sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint='a.ademuyiwa@alustudent.com'  
        )
        print("Successfully Subscribed email address to the SNS topic.")
    except sns_client.exceptions.TopicLimitExceededException:
        print("Reached the limit for creating SNS topics")

if __name__ == "__main__":
    create_sns_topic()
