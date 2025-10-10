#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import requests
from six.moves.urllib.parse import urljoin
from six.moves.urllib.parse import urlparse, ParseResult
from cloudant.replicator import Replicator
from cloudant.client import CouchDB

from djali.couchdb import CloudiControl

WARNING_FMT = "GOT {status_code!r} while trying {method:s} {url!r}"


class DjaliDatabaseManager(object):
    """
    Controller implementing simple database and user management for a CouchDB
    instance. Basically it allows you to create a database and grant access
    for one specific user to it.

    Args:
        instance_url (str): CouchDB instance URL \
            (with administrative credentials, if needed!)
    """

    def __init__(self, instance_url, *args, **kwargs):
        self.log = kwargs.get("use_log", logging.getLogger(__name__))
        p_url = urlparse(instance_url)
        self._scheme = p_url.scheme
        self._netloc = p_url.netloc
        if "@" in p_url.netloc:
            self._netloc = p_url.netloc.split("@")[1]
        username = ""
        password = ""

        if p_url.username is not None:
            username = p_url.username

        if p_url.password is not None:
            password = p_url.password

        self._root_auth = (username, password)

        couch_db_pr = ParseResult(self._scheme, self._netloc, "", "", "", "")
        self.instance_url = couch_db_pr.geturl()

    def urls_for(self, db_name, username):
        """
        Generate URLs for given CouchDB database and username.

        Args:
            db_name (str): Database
            username (str): User for authentication

        Returns:
            dict: URLs
        """
        return {
            "db": urljoin(self.instance_url, "/" + db_name),
            "permissions": urljoin(
                self.instance_url, "/{:s}/_security".format(db_name)
            ),
            "create_admin": urljoin(
                self.instance_url, "/_node/_local/_config/admins/" + username
            ),
            "create_user": urljoin(
                self.instance_url, "/_users/org.couchdb.user:" + username
            ),
        }

    def djali_create_database(
        self, db_name, username, session=None, use_log=None, auth=None
    ):
        """
        Create CouchDB database accessible by given user.

        .. warning::

            User will be granted administrative privileges for database

        Args:
            db_name (str): Database
            username (str): User for authentication
            session (requests.Session, optional): Override HTTP Session
            use_log (logging.Logger): Override logger instance
            auth (tuple, optional): Override used authentication credentials

        Raises:
            ValueError: If anything went wrong
            requests.exceptions.HTTPError: If HTTP connection went south
        """
        if use_log is None:
            use_log = self.log

        urls = self.urls_for(db_name, username)

        db_permissions = {
            "admins": {"names": [username], "roles": ["admins"]},
            "members": {"names": [username], "roles": ["developers"]},
        }

        if session is None:
            session = requests.session()
            if auth is None:
                session.auth = self._root_auth
            else:
                session.auth = auth

        req1 = session.put(urls["db"])
        req2 = session.put(urls["permissions"], json=db_permissions)

        for req in (req1, req2):
            if req.status_code // 100 != 2:
                mfg = WARNING_FMT.format(
                    status_code=req.status_code,
                    method=req.request.method,
                    url=req.request.url,
                )
                use_log.error(mfg)

                raise ValueError(mfg)

    def create_meta_databases(self, use_log=None, session=None):
        """
        Create CouchDB meta databases

        Args:
            session (requests.Session, optional): Override HTTP Session
            use_log (logging.Logger): Override logger instance

        Raises:
            ValueError: If anything went wrong
            requests.exceptions.HTTPError: If HTTP connection went south
        """
        if use_log is None:
            use_log = self.log

        if session is None:
            session = requests.session()
            session.auth = self._root_auth

        meta_dbs = ("_users", "_replicator", "_global_changes")

        for meta_db in meta_dbs:
            meta_db_url = urljoin(self.instance_url, "/" + meta_db)
            use_log.debug("Checking {:s} ..".format(meta_db_url))
            req_m_preflight = session.get(meta_db_url)

            if req_m_preflight.status_code == 200:
                continue

            if req_m_preflight.status_code // 100 == 4:
                mfg = WARNING_FMT.format(
                    status_code=req_m_preflight.status_code,
                    method=req_m_preflight.request.method,
                    url=meta_db_url,
                )
                use_log.warning(mfg)

            req_m = session.put(meta_db_url)
            if req_m.status_code // 100 != 2:
                mfg = WARNING_FMT.format(
                    status_code=req_m_preflight.status_code,
                    method=req_m_preflight.request.method,
                    url=meta_db_url,
                )
                use_log.warning(mfg)

                raise ValueError(mfg)

    def djali_init_db(
        self, db_name, username, password, use_log=None, **kwargs
    ):
        """
        Initialise a CouchDB database for given credentials.

        .. versionchanged:: 0.1.9

            One needs to use the ``may_raise`` parameter to explicitely request
            raising of an exception on error.

        Args:
            db_name (str): Database name
            username (str): Database user
            password (str): Database password
            use_log (logging.Logger): Override logger instance

        Keyword Args:
            create_admin_user (bool, optional): True if user shall be created \
                as an administrative account for current CouchDB instance
            may_raise (bool): if exception shall be raised on error \
                defaults to ``False``

        Raises:
            ValueError: If anything went wrong
            requests.exceptions.HTTPError: If HTTP connection went south

        Returns:
            str: Database URL
        """
        if use_log is None:
            use_log = self.log

        create_admin_user = kwargs.get("create_admin_user", False)

        urls = self.urls_for(db_name, username)

        session = requests.session()
        session.auth = self._root_auth

        self.create_meta_databases(use_log=use_log, session=session)

        if create_admin_user:
            req0 = session.put(urls["create_admin"], json=password)
        else:
            create_args = {
                "name": username,
                "password": password,
                "roles": [],
                "type": "user",
            }
            req0 = session.put(urls["create_user"], json=create_args)

        if req0.status_code // 100 != 2:
            use_log.warning("Create user {!r}: {!r}".format(username, req0))
            if kwargs.get("may_raise", False):
                raise ValueError("Create user failed")

        self.djali_create_database(
            db_name, username, session=session, use_log=use_log
        )

        db_url = "{scheme}://{username}:{password}@{netloc}/{db_name}".format(
            username=username,
            password=password,
            db_name=db_name,
            netloc=self._netloc,
            scheme=self._scheme,
        )

        return db_url

    def djali_setup(
        self,
        db_name,
        username,
        password,
        use_log=None,
        fastlane=True,
        **kwargs,
    ):
        """
        Set up a CouchDB database for given credentials. If user is not
        existing it will created.

        .. warning::

            When using ``fastlane = True`` it is only checked if the user is
            already existing and granted access to CouchDB instance. The
            database itself may or may not exist!

        Args:
            db_name (str): Database name
            username (str): Database user
            password (str): Database password
            use_log (logging.Logger): Override logger instance
            fastlane (bool, optional):

        Keyword Args:
            create_admin_user (bool, optional): True if user shall be created \
                as an administrative account for current CouchDB instance

        Raises:
            ValueError: If anything went wrong
            requests.exceptions.HTTPError: If HTTP connection went south

        Returns:
            tuple: Database URL and :py:class:`djali.couchdb.CloudiControl` \
                instance

        """
        db_url = "{scheme}://{username}:{password}@{netloc}/{db_name}".format(
            username=username,
            password=password,
            db_name=db_name,
            scheme=self._scheme,
            netloc=self._netloc,
        )

        if use_log is None:
            use_log = self.log

        try:
            if fastlane:
                use_log.warning(
                    "Using fast lane! {!r} may or may not exist!".format(
                        db_name
                    )
                )
            else:
                req = requests.get(db_url)

                if req.status_code == 404:
                    self.djali_init_db(
                        db_name, username=username, password=password, **kwargs
                    )

            return db_url, CloudiControl(db_url, use_log=use_log)
        except requests.exceptions.HTTPError as herror:
            if herror.response.status_code == 401:
                self.djali_init_db(
                    db_name, username=username, password=password, **kwargs
                )
                return db_url, CloudiControl(db_url, use_log=use_log)

            raise ValueError(herror.response.status_code)

    def setup_replication(
        self, source_db_name, target, repl_id=None, use_log=None, **kwargs
    ):
        """
        Set up replication of a database.

        Args:
            source_db_name: Source database
            target: Target database URL or :py:class:`djali.couchdb.CloudiControl` instance
            repl_id (str, optional): replication document ID
            use_log (logging.Logger): Override logger instance

        Keyword Args:
            continuous(bool): Continuous replication (defaults to ``False``)

        Returns:
            cloudant.document.Document: replication document
        """
        if use_log is None:
            use_log = self.log

        client = CouchDB(
            self._root_auth[0],
            self._root_auth[1],
            url=self.instance_url,
            connect=True,
            auto_renew=True,
        )
        replicator_obj = Replicator(client)

        try:
            target_database = target.database
        except Exception:
            target = CloudiControl(target, create=True)
            target_database = target.database

        source_database = client[source_db_name]
        use_log.info(
            "Setting up replication: {!s} -> {!s}".format(
                source_database, target_database
            )
        )

        return replicator_obj.create_replication(
            source_database,
            target_database,
            repl_id=repl_id,
            create_target=True,
            continuous=kwargs.get("continuous", False),
        )
