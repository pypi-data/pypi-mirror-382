#
#   Copyright (c) 2021 eGauge Systems LLC
# 	1644 Conestoga St, Suite 2
# 	Boulder, CO 80301
# 	voice: 720-545-9767
# 	email: davidm@egauge.net
#
#   All rights reserved.
#
#   This code is the property of eGauge Systems LLC and may not be
#   copied, modified, or disclosed without any prior and written
#   permission from eGauge Systems LLC.
#
from egauge.webapi import json_api


class EPICAPIClient:
    """Class to provide convenient access to the EPIC JSON API."""

    def __init__(self, url, auth=None):
        self.url = url
        self.auth = auth

    def get(self, uri):
        return json_api.get(self.url + uri, auth=self.auth)

    def post(self, uri, value):
        value = getattr(value, "__dict__", value)
        return json_api.post(self.url + uri, value, auth=self.auth)

    def put(self, uri, value):
        value = getattr(value, "__dict__", value)
        return json_api.put(self.url + uri, value, auth=self.auth)

    def patch(self, uri, value):
        value = getattr(value, "__dict__", value)
        return json_api.patch(self.url + uri, value, auth=self.auth)
