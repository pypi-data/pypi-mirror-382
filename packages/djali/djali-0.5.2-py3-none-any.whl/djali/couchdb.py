#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import uuid
import logging

import six
from cloudant.client import CouchDB
from cloudant.query import Query
from six.moves.urllib.parse import urlparse, ParseResult

from djali import __version__
from djali.base import KVStorageMixin

#: fallback username
COUCHDB_USERNAME = ""

#: fallback password
COUCHDB_PASSWORD = ""

#: fallback CouchDB instance URL
COUCHDB_URL = "http://127.0.0.1:5984"

#: fallback database name
COUCHDB_DB_NAME = "djali"


class CloudiControl(KVStorageMixin):
    """
    Controller for accessing CouchDB instances
    """

    def __init__(self, *args, **kwargs):
        self.client = None
        username = COUCHDB_USERNAME
        password = COUCHDB_PASSWORD
        db_name = COUCHDB_DB_NAME
        couch_db_url = None

        if kwargs.get("use_log"):
            self.log = kwargs["use_log"]
        else:
            self.log = logging.getLogger(__name__)

        if args:
            p_url = urlparse(args[0])
            if p_url.username is not None:
                username = p_url.username

            if p_url.password is not None:
                password = p_url.password

            if p_url.path:
                split_path = p_url.path.split("/", 2)
                try:
                    db_name = split_path[1]
                except IndexError:
                    db_name = split_path[0]

            if p_url.scheme:
                couch_db_pr = ParseResult(
                    p_url.scheme, p_url.netloc, "", "", "", ""
                )
                couch_db_url = couch_db_pr.geturl()

        if couch_db_url is None:
            default_p = urlparse(COUCHDB_URL)
            auth_prefix_parts = list()
            username = kwargs.get("username", COUCHDB_USERNAME)
            password = kwargs.get("password", COUCHDB_PASSWORD)
            scheme = kwargs.get("scheme", default_p.scheme)
            port = kwargs.get("port", default_p.port)
            host = kwargs.get("host", default_p.hostname)

            if not port:
                port = 5984

                if scheme == "https":
                    port = 6984

            if username:
                auth_prefix_parts.append(username)

                if password:
                    auth_prefix_parts.append(":")
                    auth_prefix_parts.append(password)

            if len(auth_prefix_parts) > 0:
                auth_prefix_parts.append("@")

            netloc = "{auth_prefix}{host:s}:{port:d}".format(
                auth_prefix="".join(auth_prefix_parts),
                host=host,
                port=int(port),
            )

            couch_db_url = ParseResult(scheme, netloc, "", "", "", "").geturl()

        if couch_db_url is None:
            couch_db_url = COUCHDB_URL

        self._auth = (username, password)
        self._couch_db_url = couch_db_url
        self._storage_db = db_name
        self._connect()

        if kwargs.get("create"):
            try:
                self.database
            except KeyError:
                self.client.create_database(self._storage_db)

    def __str__(self):
        return "<{klass}-{version} {url} {db_name}>".format(
            klass=self.__class__.__name__,
            version=__version__,
            url=self._couch_db_url,
            db_name=self._storage_db,
        )

    def _connect(self):
        self.log.debug("{!s} CONNECTING".format(self))
        self.client = CouchDB(
            self._auth[0],
            self._auth[1],
            url=self._couch_db_url,
            connect=True,
            auto_renew=True,
        )

    @property
    def database(self):
        return self.client[self._storage_db]

    def create(self, *args, **kwargs):
        """
        Create a new document.

        Raises:
            ValueError: If neither *args nor **kwargs is given

        Returns:
            cloudant.document.Document: Created document
        """
        if args:
            data = dict(args[0])
        elif kwargs:
            data = dict(**kwargs)
        else:
            raise ValueError("WTF?!")

        if "_id" not in data:
            data["_id"] = uuid.uuid4().hex

        return self.database.create_document(data)

    def __getitem__(self, key):
        return self.database[key]

    def __setitem__(self, key, value):
        del self[key]
        value["_id"] = key
        self.create(value)

    def __delitem__(self, key):
        try:
            doc = self.database[key]
            doc.delete()
        except KeyError:
            pass

    def lookup(self, key, value):
        """
        Lookup document matching given key/value pair.

        Args:
            key: lookup field
            value: lookup value

        Returns:
            cloudant.document.Document: Matched document

        Raises:
            KeyError: If not matching document could be found
        """
        if not isinstance(value, six.string_types):
            value = value.decode("utf-8")
        query = Query(self.database, selector={key: {"$eq": value}})

        for doc in query(limit=1)["docs"]:
            return self.database[doc["_id"]]

        raise KeyError(
            "No result for {key}={value}".format(key=key, value=value)
        )

    def _get_user(self, user_id):
        if isinstance(user_id, six.string_types):
            user_id = int(user_id, 10)
        doc_id = "{:032x}".format(user_id)

        return self.database[doc_id]

    def _get_user_by_username(self, username):
        self.log.info(
            "Looking up user by name {!r} in {!r}".format(
                username, self._storage_db
            )
        )
        return self.lookup("username", username)

    def _get_user_by_credential_id(self, credential_id):
        self.log.info(
            "Looking up user by credential_id {!r} in {!r}".format(
                credential_id, self._storage_db
            )
        )
        return self.lookup("credential_id", credential_id)


class CouchControl(CloudiControl):
    """
    Attic interface controller class
    """

    def __init__(self, db_name, *args, **kwargs):
        mangled_kwargs = dict()
        copy_keys = ("host", "port", "username", "password", "create")

        for cc in copy_keys:
            val = kwargs.get(cc)
            if val is None:
                continue
            mangled_kwargs[cc] = val

        CloudiControl.__init__(self, db_name, **mangled_kwargs)

    @property
    def db(self):
        return self.client[self._storage_db]
