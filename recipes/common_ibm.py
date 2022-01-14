"""文件名以 'common_' 开头的文件不视为插件。

本文件提供 ibm-upload 与 ibm-delete 的通用常量、函数。
"""

from typing import TypedDict
import json
import tomli
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from ffe.model import MB
from ffe.util import app_config_file


"""
- 参考1 (重要) https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-python
- 参考2 https://github.com/IBM/ibm-cos-sdk-python
- 参考3 https://cloud.ibm.com/apidocs/cos/cos-compatibility?code=python
"""


# set 5 MB chunks
part_size = 5 * MB

# set default threadhold to 15 MB
default_limit = 15

files_summary_name = "files-summary.json"


class FilesSummary(TypedDict):
    date_count: dict[str, int]  # 日期与文件数量 '20220104': 3


def get_config() -> dict:
    with open(app_config_file, "rb") as f:
        config = tomli.load(f)
        return config["ibm"]


def get_ibm_resource(cfg_ibm: dict, proxies: dict | None):
    return ibm_boto3.resource(
        "s3",
        ibm_api_key_id=cfg_ibm["ibm_api_key_id"],
        ibm_service_instance_id=cfg_ibm["ibm_service_instance_id"],
        config=Config(signature_version="oauth", proxies=proxies),
        endpoint_url=cfg_ibm["endpoint_url"],
    )


# https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-python#python-examples-multipart
def upload(cos, bucket_name: str, item_name: str, size_limit: int, file_path: str):
    try:
        # set the transfer threshold and chunk size
        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold=size_limit, multipart_chunksize=part_size
        )

        # the upload_fileobj method will automatically execute a multi-part upload
        # in 5 MB chunks for all files over 15 MB
        with open(file_path, "rb") as file_data:
            cos.Object(bucket_name, item_name).upload_fileobj(
                Fileobj=file_data, Config=transfer_config
            )

        print("Transfer complete.")
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to complete multi-part upload: {0}".format(e))


# https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-python#python-examples-get-file-contents
def get_item(cos, bucket_name: str, item_name: str):
    try:
        return cos.Object(bucket_name, item_name).get()
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve file contents: {0}".format(e))


# https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-python#python-examples-get-file-contents
def get_files_summary(cos, bucket_name: str, item_name: str) -> FilesSummary:
    try:
        f = cos.Object(bucket_name, item_name).get()
        summary = json.loads(f["Body"].read())
        return FilesSummary(date_count=summary.get("date_count", {}))
    except ClientError as be:
        if be.__str__().find("NoSuchKey") < 0:
            raise
    except Exception as e:
        print("Unable to retrieve file contents: {0}".format(e))
    return FilesSummary(date_count={})


# https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-python#python-examples-new-file
def put_text_file(cos, bucket_name: str, item_name: str, file_text: str):
    try:
        cos.Object(bucket_name, item_name).put(Body=file_text)
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to create text file: {0}".format(e))
