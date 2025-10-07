"""
QGC Protocol output payload definitions.

Created on 6 Oct 2025

Information sourced from public domain Quectel Interface Specifications © 2013-2021, Quectel AG

:author: semuadmin (Steve Smith)
"""

# pylint: disable=too-many-lines, line-too-long

from pyqgc.qgctypes_core import (
    PAGE53,
    U1,
    U2,
    U3,
    U4,
    U5,
    U6,
    U15,
    U16,
    U17,
    X1,
    X61,
    X250,
)

QGC_PAYLOADS_GET = {
    "RAW-PPPB2B": {
        "msgver": U1,  # 1 for this version
        "reserved1": U4,
        "prn": U1,
        "flag": (
            X1,
            {
                "reserved4": U5,
                "pppstatus": U1,  # 0 normal, 1 abnormal
            },
        ),
        "msgtype": U1,
        "reserved2": U16,
        "msgdata": X61,
    },
    "RAW-QZSSL6": {
        "msgver": U1,  # 1 for this version
        "reserved1": U4,
        "prn": U1,
        "flag": (
            X1,
            {
                "rsstatus": U2,  # 0 fail, 1, pass, 2 pass after correction
                "reserved": U5,
                "msgtype": U1,  # 0 L6E, 1 L6D
            },
        ),
        "reserved2": U17,
        "msgdata": X250,
    },
    "RAW-HASE6": {
        "msgver": U1,  # 1 for this version
        "reserved1": U3,
        "prn": U1,
        "status": (
            X1,
            {
                "hasmode": U2,  # 0 testing, 1 operational
                "reserved4": U6,
            },
        ),
        "msgtype": U1,  # 1 = MT1
        "reserved2": U1,
        "page": U1,
        "reserved3": U15,
        "msgdata": PAGE53,  # length = page*53
    },
}
