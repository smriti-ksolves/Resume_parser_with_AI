from app.app import s3_client
import botocore


def generate_presigned_url(bucket_name, object_key, expiration=3600):
    try:
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration,
            HttpMethod='PUT'
        )
    except botocore.exceptions.ClientError as e:

        return None

    return presigned_url


