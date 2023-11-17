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

from pyispyb.app.extensions.auth.AbstractAuthentication import AbstractAuthentication


__license__ = "LGPLv3+"


log = logging.getLogger(__name__)


class ADAuthentication(AbstractAuthentication):
    def __init__(self):
        AbstractAuthentication.__init__(self)

        self.ad_conn = None
        self.ad_dn = None
        self.ad_base_internal = None
        self.ad_uri = None
        self.ad_domain = None

    def configure(self, config: dict[str, Any]):
        """Configure auth plugin.

        Args:
            config (dict): plugin configuration from file
        """
        self.ad_uri = config["AD_URI"]
        self.ad_dn = config["AD_DN"]
        self.ad_base_internal = "cn=Users,dc=maxlab,dc=lu,dc=se"
        self.ad_domain = config["AD_DOMAIN"]

    def authenticate_by_login(
        self, login: str, password: str
    ) -> Optional[models.Person]:
        groups = None
        group_list = None
        try:
            log.debug(
                f"AD login: try to authenticate user `{login}` "
            )
            self.ad_conn = ldap.initialize(self.ad_uri)
            search_str = login + "@" + self.ad_domain 
            self.ad_conn.protocol_version = ldap.VERSION3
            self.ad_conn.set_option(ldap.OPT_REFERRALS, 0)
            self.ad_conn.simple_bind_s(search_str, password)
            log.debug("user authenticated... waiting to have all the attributes")
            print("user authenticated... waiting to have all the attributes")
            # self.ad_conn.simple_bind_s(
            #     f"cn={login},{self.ad_dn}", password
            # )
            res = self.ad_conn.search_s(
                self.ad_dn,
                ldap.SCOPE_SUBTREE,
                f"(SAMAccountname={login})", 
                ['mail', 'uidNumber', 'sn', 'givenName', 'telephoneNumber', 'memberOf'])[0][1]
            log.debug(res)
            print(res)

            def get_value(v: str):
                if v in res:
                    return res[v][0]
                return None
            
            group_list = res["memberOf"]
            for group in group_list:
                print(group)
                groups += [group]

            return models.Person(
                login=login,
                emailAddress=get_value("mail"),
                siteId=get_value("uidNumber"),
                familyName=get_value("sn"),
                givenName=get_value("givenName"),
                phoneNumber=get_value("telephoneNumber"),
            )
        except ldap.INVALID_CREDENTIALS:
            log.exception(f"AD login: unable to authenticate user {login}")

    def get_user_and_groups(
        self, username: str | None, password: str | None, token: str | None
    ) -> tuple[str | None, list[str] | None]:
        """Return username and groups associated to the user.

        Args:
            username (string): auth username
            password (string): auth password
            token (string): auth token
        Returns:
            username, groups
        """
        user = None
        groups = None
        group_list = None
        try:
            msg = "AD login: try to authenticate user %s " % username
            log.debug(msg)
            search_filter = "(samAccountName=%s)" % username
            attrs = ["*"]
            #search_str = self.ldap_id + "=" + username + "," + self.ldap_base_internal
            search_str = username + "@" + self.ad_domain 
            self.ad_conn.simple_bind_s(search_str, password)
            result = self.ad_conn.search_s(
                self.ad_dn,
                ldap.SCOPE_SUBTREE,
                search_filter,
                attrs,
            )
            #print(result)
            user = username
            group_list = result[0][1]["memberOf"]
            for group in group_list:
                groups.append(group)
        except ldap.INVALID_CREDENTIALS as ex:
            msg = "AD login: unable to authenticate user %s (%s)" % (
                username,
                str(ex),
            )
            log.exception(msg)
            return None, None
        
        if user is None or groups is None:
            return None, None, None
        return user, groups
