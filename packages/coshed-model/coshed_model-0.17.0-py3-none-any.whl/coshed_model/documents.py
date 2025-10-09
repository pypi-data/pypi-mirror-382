#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
from io import BytesIO

import boto3
import botocore.exceptions
import orjson


class JSONDocumentOnS3Controller(object):
    """
    Controller class for reading and writing JSON encoded documents.
    """

    # TODO: change variable name
    env_bucket_key = "TANGIBLE_BUCKET"

    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(__name__)

        if kwargs.get("bucket_name") is None:
            self.bucket_name = os.environ.get(self.env_bucket_key)
        else:
            self.bucket_name = kwargs.get("bucket_name")

        self.region_name = kwargs.get("region_name")

        if self.bucket_name is None:
            mfg = (
                "No bucket name?! Please set either environment variable "
                "{!r} or provide "
                "*bucket_name* parameter".format(self.env_bucket_key)
            )
            self.log.error(mfg)

            raise ValueError(mfg)

    def s3_upload(self, key, value):
        """
        Upload JSON content to S3.

        Args:
            key: key
            value: value

        """
        s3 = boto3.client("s3", region_name=self.region_name)
        filelike = BytesIO()
        filelike.write(orjson.dumps(value))
        filelike.seek(0)

        s3.upload_fileobj(filelike, self.bucket_name, key)

    def s3_delete(self, key):
        s3 = boto3.client("s3", region_name=self.region_name)
        s3.delete_object(Key=key, Bucket=self.bucket_name)

    def s3_download(self, key):
        """
        Download JSON content from S3.

        Args:
            key:

        Returns:
            object: contents
        """
        s3 = boto3.client("s3", region_name=self.region_name)
        filelike = BytesIO()

        s3.download_fileobj(self.bucket_name, key, filelike)

        return orjson.loads(filelike.getvalue())

    def __delitem__(self, key):
        self.s3_delete(key)

    def __getitem__(self, key):
        try:
            return self.s3_download(key)
        except botocore.exceptions.ClientError as bexc:
            if bexc.response["Error"]["Code"] == "404":
                raise KeyError(key)
            response_id = bexc.response["ResponseMetadata"]["RequestId"]
            self.log.error(
                "Unexpected S3 error: {!s} Request ID: {!s}".format(
                    bexc, response_id
                )
            )

    def __setitem__(self, key, value):
        self.s3_upload(key, value)
