#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import boto3
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)


s3_client = None
s3_resource = None


def handler(event, context):
    """Lambda handler"""
    return


def get_s3_client():
    global s3_client
    if s3_client is None:
        s3_client = boto3.client('s3')
    return s3_client


def get_s3_resource():
    global s3_resource
    if s3_resource is None:
        s3_resource = boto3.resource('s3')
    return s3_resource


def get_region_name(bucket_name):
    """Returns AWS region name, given a bucket name.

    :param bucket_name: Name of a S3 bucket.
    :type bucket_name: str

    :return: AWS region name. Example: 'us-east-1'.
    :rtype: str

    """
    response = get_s3_client().get_bucket_location(Bucket=bucket_name)
    # For default region, US Standard, LocationConstraint is empty.
    # Return 'us-east-1' when no data is available.
    return response['LocationConstraint'] or 'us-east-1'


def bucket_generator():
    """Returns a s3.Bucket object generator."""
    bucket_collection = get_s3_resource().buckets.all()
    for bucket in bucket_collection:
        yield bucket


def enable_versioning(bucket_name):
    """Enables versioning in a given bucket name.

    :param bucket_name: Name of a S3 bucket.
    :type bucket_name: str

    """
    get_s3_resource().BucketVersioning(bucket_name).enable()


def enable_logging(source_bucket_name, target_bucket_name):
    """Enable logging for a source bucket in a target bucket with prefix
    as the name of source bucket.

    :param source_bucket_name: Bucket in which logging has to be enabled.
    :type source_bucket_name: str

    :param target_bucket_name: Bucket where the logs would be stored.
    :type target_bucket_name: str

    """
    get_s3_client().put_bucket_logging(
        Bucket=source_bucket_name,
        BucketLoggingStatus={
            'LoggingEnabled': {
                'TargetBucket': target_bucket_name,
                'TargetPrefix': source_bucket_name + '/'
            }
        }
    )


def buckets_in_same_region(x_bucket_name, y_bucket_name):
    """Checks if x and y buckets are in the same region.
    This would be used if no region-wise log buckets are specified, to validate
    if x can have y as the target logging bucket.

    :param x_bucket_name: Name of bucket x.
    :type x_bucket_name: str

    :param y_bucket_name: Name of bucket y.
    :type y_bucket_name: str

    :return: True if both the buckets are in the same region. False otherwise.
    :rtype: bool

    """
    if get_region_name(x_bucket_name) == get_region_name(y_bucket_name):
        return True
    return False


def get_log_bucket_for_region(region):
    """Returns log bucket assigned for a particular region.
    This is required to add logging target bucket in the same region bucket.

    :param region: AWS region name.
    :type region: str

    :return: Name of bucket assigned for logs in the given region.
    :rtype: str or NoneType

    """
    env_var_name = "BUCKET_" + region
    return os.getenv(env_var_name)
