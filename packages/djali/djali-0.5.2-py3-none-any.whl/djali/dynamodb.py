#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

try:
    import boto3
except ImportError:
    print(
        "no boto3 support! "
        "Use pip to install either boto3 or djali[dynamodb]"
    )

from djali import __version__
from djali.base import KVStorageMixin


class DynamoController(KVStorageMixin):
    """
    Minimal DynamoDB Controller for accessing key/value datasets.
    """

    def __init__(self, db_name, region_name=None):
        """
        DynamoDB Client

        Args:
            db_name: name of table to be used
            region_name (str, optional): AWS region override
        """
        self._db = boto3.resource("dynamodb", region_name=region_name)
        self._storage_db = db_name
        self._table = self._db.Table(self._storage_db)

    def __getitem__(self, key):
        result = self._table.get_item(Key={"key": key})

        try:
            raw_value = result["Item"]
        except KeyError:
            raise KeyError(key)

        return json.loads(raw_value["value"])

    def __setitem__(self, key, value):
        self._table.put_item(Item={"key": key, "value": json.dumps(value)})

    def __delitem__(self, key):
        self._table.delete_item(Key={"key": key})

    def __str__(self):
        return "<{klass}-{version} {db_name}>".format(
            klass=self.__class__.__name__,
            version=__version__,
            db_name=self._storage_db,
        )
