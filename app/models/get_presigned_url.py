from app.app import s3_client


def get_file(object_key, bucket_name, folder_prefix):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)['Contents']
        all_keys = []
        for res in response:
            if not res['Key'].endswith("/"):
                all_keys.append(res['Key'])
        if object_key in all_keys:
            with open(object_key, 'wb') as data:
                s3_client.download_fileobj(bucket_name, object_key, data)
        return {"success": "File Downloaded Successfully"}
    except Exception as err:
        return {"error": "Something went wrong while downloading the pdf"}
