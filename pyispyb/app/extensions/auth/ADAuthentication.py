# Project: py-ispyb
# https://github.com/ispyb/py-ispyb

# This file is part of py-ispyb software.

# py-ispyb is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# py-ispyb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with py-ispyb. If not, see <http://www.gnu.org/licenses/>.


import logging
from typing import Any, Optional
import ldap

from ispyb import models

from .AbstractAuthentication import AbstractAuthentication


__license__ = "LGPLv3+"


log = logging.getLogger(__name__)


class ADAuthentication(AbstractAuthentication):

    def __init__(self):
        super().__init__(self)  # TODO not entirely sure we need this since there is no __init__

        # Configuration settings
        self.ad_base_dn = ""  # base DN
        self.ad_domain = ""
        self.ad_uri = ""

    def configure(self, config: dict[str, Any]):
        """Configure auth plugin.

        Args:
            config (dict): plugin configuration from file
        """
        self.ad_base_dn = config["AD_BASE_DN"]
        self.ad_domain = config["AD_DOMAIN"]
        self.ad_uri = config["AD_URI"]

    def authenticate_by_login(self, login: str, password: str) -> Optional[models.Person]:

        log.debug("AD login: try to authenticate user `%s`" % login)
        login = login.strip()

        if not login:
            log.debug("AD login: can not authenticate without login")
            return None

        who = f"{login}@{self.ad_domain}"
        log.debug("AD login: try to authenticate user `%s`" % who)

        try:
            ad_conn = ldap.initialize(self.ad_uri)
        except Exception as exc:  # TODO Check actual exception type
            log.exception("AD login: can not initialize connection")
            return None

        ad_conn.protocol_version = ldap.VERSION3
        ad_conn.set_option(ldap.OPT_REFERRALS, 0)

        try:
            ad_conn.simple_bind_s(who, password)
        except ldap.INVALID_CREDENTIALS:
            log.exception("AD login: unable to authenticate user `%s`" % login)
            return None

        log.debug("AD login: user authenticated... waiting to have all the attributes")

        try:
            res = ad_conn.search_s(
                self.ad_base_dn,
                ldap.SCOPE_SUBTREE,
                f"(SAMAccountname={login})", 
                ['mail', 'uidNumber', 'sn', 'givenName', 'telephoneNumber', 'memberOf'],
            )[0][1]
        except ldap.INVALID_CREDENTIALS:
            log.exception("AD login: unable to authenticate user `%s`" % login)
            return None

        log.debug("AD login: search result: %s" % res)

        def get_value(v: str):
            if v in res:
                return res[v][0]
            return None
        
        return models.Person(
            login=login,
            emailAddress=get_value("mail"),
            siteId=get_value("uidNumber"),
            familyName=get_value("sn"),
            givenName=get_value("givenName"),
            phoneNumber=get_value("telephoneNumber"),
        )


    # TODO Do we need this?
    def get_user_and_groups(
        self, username: str | None, password: str | None, _token: str | None
    ) -> tuple[str | None, list[str] | None]:
        """Return username and groups associated to the user.

        Args:
            username (string): auth username
            password (string): auth password
            _token (string): auth token (unused)
        Returns:
            username, groups
        """

        username = username.strip()

        msg = "AD login: try to authenticate user `%s`" % username
        log.debug(msg)

        if not username:
            log.debug("AD login: can not authenticate without username")
            return None, None

        groups = None
        group_list = None
        who = f"{username}@{self.ad_domain}"
        search_filter = f"(samAccountName={username})"
        attrs = ["*"]

        msg = "AD login: try to authenticate user `%s`" % who
        log.debug(msg)

        try:
            ad_conn = ldap.initialize(self.ad_uri)
        except Exception as exc:  # TODO Check actual exception type
            log.exception("AD login: can not initialize connection")
            return None, None

        try:
            ad_conn.simple_bind_s(search_str, password)
            result = ad_conn.search_s(
                self.ad_base_dn,
                ldap.SCOPE_SUBTREE,
                search_filter,
                attrs,
            )
        except ldap.INVALID_CREDENTIALS as ex:
            msg = "AD login: unable to authenticate user `%s`" % who
            log.exception(msg)
            return None, None
        
        group_list = result[0][1]["memberOf"]
        for group in group_list:
            groups.append(group)

        if user is None or groups is None:
            return None, None

        return user, groups
