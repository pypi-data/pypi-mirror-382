#
#   Copyright (c) 2014-2015, 2017-2019 eGauge Systems LLC
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
"""Read footprint info from KiCad footprints directory."""

import os
import re

from django.conf import settings as cfg


class Footprints:
    @classmethod
    def get(cls):
        ret = []
        pattern = re.compile(r"([.]pretty(/|$))")
        for root, _, files in os.walk(cfg.EPIC_KICAD_FOOTPRINTS_DIR):
            libname = pattern.sub(
                ":", root[len(cfg.EPIC_KICAD_FOOTPRINTS_DIR) :]
            )
            for f in files:
                m = re.match(r"(.*)[.]kicad_mod$", f)
                if m:
                    ret.append(libname + m.group(1))
        return ret
