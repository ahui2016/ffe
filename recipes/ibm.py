"""ibm: 上传文件到 IBM COS
dependencies = ["ibm-cos-sdk"]

https://github.com/ahui2016/ffe/raw/main/recipes/ibm.py
"""

# 每个插件都应如上所示在文件开头写简单介绍，以便 "ffe install --peek" 功能窥视插件概要。

"""
- 参考1 (重要) https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-python
- 参考2 https://github.com/IBM/ibm-cos-sdk-python
- 参考3 https://cloud.ibm.com/apidocs/cos/cos-compatibility?code=python

- 注册一个 cloud.ibm.com 账号
- 启用 IBM Cloud Object Storage 并且创建一个 bucket
- pip install ibm-cos-sdk
- Gather required information (收集必要参数) https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-python#python-prereqs
- 把相关信息填写到 ffe-config.toml (参考 https://github.com/ahui2016/ffe/blob/main/examples/ffe-config.toml)
"""

from typing import cast
import ibm_boto3
from ibm_botocore.client import Config, ClientError
import tomli
import requests
from ffe.model import Recipe, ErrMsg, must_exist, get_bool, names_limit
from ffe.util import app_config_file, get_proxies


# 每个插件都必须继承 model.py 里的 Recipe
class IBM(Recipe):
    @property  # 必须设为 @property
    def name(self) -> str:
        return "ibm"

    @property  # 必须设为 @property
    def help(self) -> str:
        return """upload to IBM COS"""

    @property  # 必须设为 @property
    def default_options(self) -> dict:
        return dict()

    def validate(self, names: list[str], options: dict) -> ErrMsg:
        """初步检查参数（比如文件数量与是否存在），并初始化以下项目：
        """
        # 要在 dry_run, exec 中确认 is_validated
        self.is_validated = True
        return ""

    def dry_run(self) -> ErrMsg:
        assert self.is_validated, "在执行 dry_run 之前必须先执行 validate"
        print("There is no dry run for this recipe.")
        print("本插件涉及第三方服务，因此无法提供 dry run.")
        return ""

    def exec(self) -> ErrMsg:
        assert self.is_validated, "在执行 exec 之前必须先执行 validate"
        cfg_ibm = get_config()
        cos = get_ibm_resource(cfg_ibm)
        # get_buckets(cos)
        get_bucket_files(cos, cfg_ibm["bucket_name"])
        return ""


__recipe__ = IBM


def get_config() -> dict:
    with open(app_config_file, "rb") as f:
        config = tomli.load(f)
        return config["ibm"]


def get_ibm_resource(cfg_ibm: dict):
    return ibm_boto3.resource(
        "s3",
        ibm_api_key_id=cfg_ibm["ibm_api_key_id"],
        ibm_service_instance_id=cfg_ibm["ibm_service_instance_id"],
        config=Config(signature_version="oauth"),
        endpoint_url=cfg_ibm["endpoint_url"]
    )


def get_buckets(cos):
    print("Retrieving list of buckets")
    try:
        buckets = cos.buckets.all()
        for bucket in buckets:
            print("Bucket Name: {0}".format(bucket.name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve list buckets: {0}".format(e))


def get_bucket_files(cos, bucket_name):
    print("Retrieving bucket contents from: {0}".format(bucket_name))
    try:
        files = cos.Bucket(bucket_name).objects.all()
        for file in files:
            print(f"Item: {file.key} ({file.size} bytes) ctime:{file.last_modified}")
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve bucket contents: {0}".format(e))
