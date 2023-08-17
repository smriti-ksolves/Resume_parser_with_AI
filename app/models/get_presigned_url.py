from app.app import s3_client,logger


def get_file(object_key, bucket_name, folder_prefix):
    """
    Download a file from an S3 bucket.

    This function takes an object key, bucket name, and folder prefix as input, and downloads
    a file from the specified S3 bucket using the boto3 S3 client.

    Args:
        object_key (str): The object key (file name) to be downloaded.
        bucket_name (str): The name of the S3 bucket containing the file.
        folder_prefix (str): The prefix of the folder in the S3 bucket where the file is located.

    Returns:
        dict: A dictionary indicating the success or failure of the download operation.
    """
    try:
        # List objects in the specified S3 bucket with the given folder prefix
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)['Contents']
        all_keys = []

        # Extract all object keys from the S3 response
        for res in response:
            if not res['Key'].endswith("/"):
                all_keys.append(res['Key'])

        # Check if the specified object key exists in the S3 bucket
        if object_key in all_keys:
            with open(object_key, 'wb') as data:
                # Download the file and save it locally
                s3_client.download_fileobj(bucket_name, object_key, data)
    except Exception as err:
        logger.error(err)
