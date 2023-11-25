import boto3
from botocore.exceptions import NoCredentialsError
import csv
from io import StringIO
from datetime import datetime, timedelta, timezone

def get_timezone_offset(timezone_str):
    """
    Get the timezone offset in hours for the given timezone string.

    Parameters:
    - timezone_str (str): The timezone string (e.g., 'UTC', 'America/New_York').

    Returns:
    - int: The timezone offset in hours.
    """
    return -5
    try:
        time_diff = datetime.now() - datetime.now(timezone.utc)
        print(time_diff)

        return time_diff.seconds//3600
    except Exception as e:
        print(f"Error getting timezone offset: {e}")
        return 0  # Return 0 as a default offset if there is an error
        
def get_last_modified_date(bucket_name, object_key, local_timezone='America/New_York'):
    """
    Retrieves the last modified date for a file in an S3 bucket and formats it as a string in the local timezone.

    Parameters:
    - bucket_name (str): The name of the S3 bucket.
    - object_key (str): The key (path) of the object in the bucket.
    - local_timezone (str): The local timezone to which the last modified date should be converted.

    Returns:
    - str: The last modified date of the object formatted as a string in the local timezone.
    """

    # Initialize Boto3 S3 client
    s3 = boto3.client('s3')

    try:
        # Get the object metadata, including the last modified date
        response = s3.head_object(Bucket=bucket_name, Key=object_key)

        # Extract the last modified date in UTC
        last_modified_date_utc = response['LastModified'].replace(tzinfo=timezone.utc)

        # Convert the last modified date to the local timezone
        local_tz = timezone(timedelta(hours=get_timezone_offset(local_timezone)))
        last_modified_date_local = last_modified_date_utc.astimezone(local_tz)

        # Format the last modified date as a string
        last_modified_date_string = last_modified_date_local.strftime("%b-%d %I:%M%p")

        return last_modified_date_string
    except NoCredentialsError:
        print("Credentials not available or incorrect.")
    except Exception as e:
        print(f"Error: {e}")
        return None

def upload_csv_to_s3(csv_data, bucket_name, object_name):
    """
    Uploads a CSV file to an S3 bucket.

    Parameters:
    - csv_data (list of lists): The data to be written to the CSV file.
    - bucket_name (str): The name of the S3 bucket.
    - object_name (str): The name of the object (file) in the bucket.
    """

    # Convert the CSV data to a string
    csv_content = "\n".join([",".join(map(str, row)) for row in csv_data])

    # Initialize a Boto3 S3 client
    s3 = boto3.client('s3')

    try:
        # Upload the CSV content to the specified S3 object
        s3.put_object(Body=csv_content, Bucket=bucket_name, Key=object_name)

        print(f"CSV file uploaded to {bucket_name}/{object_name}")
    except NoCredentialsError:
        print("Credentials not available or incorrect.")
        
def read_csv_from_s3(bucket_name, object_key):
    """
    Reads CSV data from an S3 location.

    Parameters:
    - bucket_name (str): The name of the S3 bucket.
    - object_key (str): The key (path) of the object in the bucket.

    Returns:
    - list of lists: The CSV data as a list of lists.
    """

    # Initialize a Boto3 S3 client
    s3 = boto3.client('s3')

    try:
        # Get the CSV data from the specified S3 object
        response = s3.get_object(Bucket=bucket_name, Key=object_key)

        # Read the CSV data from the response
        csv_data = response['Body'].read().decode('utf-8')

        # Use StringIO to treat the string as a file-like object
        csv_file = StringIO(csv_data)

        # Use the csv.reader to read the CSV data into a list of lists
        csv_reader = csv.reader(csv_file)
        csv_data_list = [row for row in csv_reader]

        return csv_data_list[1:]

    except NoCredentialsError:
        print("Credentials not available or incorrect.")
    except Exception as e:
        print(f"Error: {e}")
        return None
        
def duplicate_file_in_s3(source_bucket, source_key, destination_bucket, destination_key):
    """
    Duplicates a file in an S3 bucket.

    Parameters:
    - source_bucket (str): The name of the source S3 bucket.
    - source_key (str): The key (path) of the source object in the source bucket.
    - destination_bucket (str): The name of the destination S3 bucket.
    - destination_key (str): The key (path) of the destination object in the destination bucket.
    """

    # Initialize Boto3 S3 clients
    s3 = boto3.client('s3')

    try:
        # Copy the object from the source to the destination
        s3.copy_object(Bucket=destination_bucket, CopySource={'Bucket': source_bucket, 'Key': source_key}, Key=destination_key)

        print(f"File duplicated: {source_bucket}/{source_key} -> {destination_bucket}/{destination_key}")
    except NoCredentialsError:
        print("Credentials not available or incorrect.")
    except Exception as e:
        print(f"Error: {e}")
        
def grant_public_read_access(bucket_name, object_key):
    # Create an S3 client
    s3 = boto3.client('s3')

    # Grant public read access to the S3 object
    s3.put_object_acl(
        Bucket=bucket_name,
        Key=object_key,
        ACL='public-read'
    )
        
def send_email(subject, etype, body, recipients, sender, aws_region='us-east-1'):
    """
    Sends an email through Amazon SES to multiple recipients.

    Parameters:
    - subject (str): The email subject.
    - body (str): The email body.
    - recipients (list): List of email recipients.
    - sender (str): The email sender.
    - aws_region (str): The AWS region (default is 'us-east-1').
    """

    # Initialize Boto3 SES client
    ses = boto3.client('ses', region_name=aws_region)

    # Create the email message
    email_message = {
        'Subject': {'Data': subject},
        'Body': {etype: {"Charset": "UTF-8", 'Data': body}},
    }

    try:
        # Send the email to multiple recipients
        response = ses.send_email(
            Source=sender,
            Destination={'ToAddresses': recipients},
            Message=email_message
        )

        print(f"Email sent! Message ID: {response['MessageId']}")

    except NoCredentialsError:
        print("Credentials not available or incorrect.")
    except Exception as e:
        print(f"Error sending email: {e}")

        