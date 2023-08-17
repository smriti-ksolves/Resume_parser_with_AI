from app.app import s3_client, logger
import botocore


def generate_presigned_url(bucket_name, object_key, expiration=3600):
    """
        Generate a presigned URL for uploading an object to an S3 bucket.

        This function generates a presigned URL that allows temporary access to upload an object
        to the specified S3 bucket with the provided object key. The generated URL has a limited
        expiration time.

        Args:
            bucket_name (str): The name of the S3 bucket.
            object_key (str): The object key (file name) within the bucket.
            expiration (int, optional): Expiration time for the presigned URL in seconds. Default is 3600 seconds (1 hour).

        Returns:
            str: A presigned URL that can be used to upload an object to the S3 bucket.
                Returns None if an error occurs during URL generation.
    """
    try:
        # Generate a presigned URL using the 'put_object' action
        presigned_post = s3_client.generate_presigned_post(
            Bucket=bucket_name,
            Key=object_key,
            ExpiresIn=expiration,
        )
        return presigned_post

    except botocore.exceptions.ClientError as e:
        logger.error(e)
        return None



