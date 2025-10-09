"""
Stream method tests using actual receiver binary outputs for pyqcg.QCGReader

Created on 6 Oct 2025

*** NB: must be saved in UTF-8 format ***

@author: semuadmin
"""

# pylint: disable=line-too-long, invalid-name, missing-docstring, no-member

import sys
import os
import unittest
from io import StringIO
from logging import ERROR

from pyqgc import (
    QGCReader,
    QGCMessage,
    SET,
    GET,
    POLL,
    SETPOLL,
    QGC_HDR,
    VALCKSUM,
    VALNONE,
    ERR_RAISE,
    NMEA_PROTOCOL,
    RTCM3_PROTOCOL,
    QGC_PROTOCOL,
    QGCMessageError,
    QGCParseError,
    QGCStreamError,
)
import pyqgc.qgctypes_core as qgt

DIRNAME = os.path.dirname(__file__)


class StreamTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        pass

    def catchio(self):
        """
        Capture stdout as string.
        """

        self._saved_stdout = sys.stdout
        self._strout = StringIO()
        sys.stdout = self._strout

    def restoreio(self) -> str:
        """
        Return captured output and restore stdout.
        """

        sys.stdout = self._saved_stdout
        return self._strout.getvalue().strip()

    def testQGCLOG(self):  # test stream of QGC messages with parsebitfield = True
        EXPECTED_RESULTS = (
            "<QGC(RAW-PPPB2B, msgver=1, reserved1=0, prn=60, pppstatus=0, msgtype=0, reserved2=0, msgdata=b'\\x10\\x35\\xfc\\x49\\x04\\x40\\x01\\x3f\\x77\\x04\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x44\\x00\\x11\\x00\\x05\\x80\\x00\\x5f\\x6b\\x84\\x00\\x11\\x00\\x07\\x7d\\x63\\x10\\x00\\x78\\x17\\x0f\\xfd\\xd1\\x02\\x57\\x10\\x00\\x44\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x58\\x7f\\x00\\x01\\x81\\x36\\xb0')>",
            "<QGC(RAW-QZSSL6, msgver=1, reserved1=0, prn=195, rsstatus=1, msgtype=1, reserved2=0, msgdata=b'\\x1a\\xcf\\xfc\\x1d\\xc3\\xa9\\x7f\\x48\\xab\\x08\\x92\\x88\\xc0\\x3a\\xa8\\x40\\x30\\x02\\x02\\x93\\xdf\\xdf\\xf5\\xd5\\xde\\x43\\x1c\\x00\\x00\\x02\\x04\\x80\\x04\\x70\\x00\\x00\\x00\\x00\\x82\\x40\\x7f\\x49\\xe8\\x11\\x08\\x04\\x7f\\xed\\x40\\x0e\\x9f\\xe2\\x01\\x8b\\x02\\xb1\\x02\\x5c\\x00\\x5c\\x06\\x2f\\xb1\\x9f\\xea\\xbf\\xea\\xbf\\xf6\\x00\\x5d\\x07\\x7b\\xf1\\x03\\xe8\\xa7\\xf5\\x10\\x6e\\xdf\\xd2\\x5a\\x04\\xa2\\x3b\\xfd\\x0d\\xfc\\x40\\x30\\x0e\\xfc\\x5c\\x02\\x20\\x0b\\xc8\\xbf\\x0b\\x03\\x98\\x0d\\x60\\x5f\\x0a\\x80\\xd4\\x03\\x98\\xbf\\x68\\xff\\xdf\\x03\\x82\\x87\\xd5\\x4f\\xba\\x01\\x8c\\xd7\\xf0\\x88\\x4b\\xfe\\xd4\\x31\\xf4\\x34\\x08\\xa0\\x3a\\x19\\xfc\\xe7\\xf0\\x10\\x01\\x17\\x7c\\x3a\\xfd\\xb8\\x23\\x04\\xbf\\xb5\\x1f\\xf2\\xff\\xe8\\x93\\xf7\\x4c\\x01\\xc0\\x04\\x13\\xbe\\xd9\\x00\\x2b\\xfe\\xa2\\x77\\xde\\xd0\\x08\\x7f\\xd8\\x4e\\xfa\\xbd\\xff\\x70\\x03\\x09\\xdf\\x89\\xbf\\xfa\\x00\\xca\\x5f\\xcd\\x1f\\xb5\\xfd\\xcd\\x2f\\xd1\\xb0\\x0d\\xff\\x8e\\x97\\xbf\\x17\\xf6\\x80\\x55\\xfd\\x29\\xa0\\x4a\\x20\\x01\\xfe\\x80\\x28\\x00\\x05\\xc0\\xa7\\xf3\\x00\\x15\\x9c\\xcd\\xe1\\x8b\\xc4\\xee\\x2d\\xe8\\x5c\\xd1\\xf1\\x28\\xf9\\xa2\\x81\\x83\\xdf\\xeb\\x8e\\x1b\\x5f\\xfe\\x18\\xf7\\xd9\\x21\\x54\\x33\\x1c\\x5c\\x10')>",
            "<QGC(RAW-HASE6, msgver=1, reserved1=0, prn=34, hasmode=1, msgtype=1, reserved2=0, page=2, reserved3=0, msgdata=b'\\x38\\xb2\\x00\\xe8\\x50\\xe9\\xa0\\x5e\\x7f\\xc6\\x0d\\x00\\x31\\xff\\x2e\\x00\\x00\\x5b\\xfe\\x50\\x2c\\xc0\\xe1\\x00\\x00\\x2f\\x77\\xe0\\x0b\\x20\\xc6\\xe5\\x3f\\x49\\x79\\xf0\\x10\\x50\\x11\\xf8\\xcb\\xeb\\x7f\\x31\\x04\\x67\\xd0\\x80\\xf2\\x05\\xc0\\x0e\\x81\\xb2\\x00\\xe8\\x50\\xe9\\xa0\\x5e\\x7f\\xc6\\x0d\\x00\\x31\\xff\\x2e\\x00\\x00\\x5b\\xfe\\x50\\x2c\\xc0\\xe1\\x00\\x00\\x2f\\x77\\xe0\\x0b\\x20\\xc6\\xe5\\x3f\\x49\\x79\\xf0\\x10\\x50\\x11\\xf8\\xcb\\xeb\\x7f\\x31\\x04\\x67\\xd0\\x80\\xf2\\x05\\xc0\\x0e\\x81\\xc8')>",
        )

        i = 0
        with open(os.path.join(DIRNAME, "pygpsdata_lg580p_qgc.log"), "rb") as stream:
            ubr = QGCReader(
                stream,
                parsing=True,
                parsebitfield=1,
                validate=VALCKSUM,
                quitonerror=ERR_RAISE,
            )
            for raw, parsed in ubr:
                # print(f'"{parsed}",')
                self.assertEqual(str(parsed), EXPECTED_RESULTS[i])
                i += 1
            self.assertEqual(i, len(EXPECTED_RESULTS))

    def testQGCLOG_NOBITFIELD(
        self,
    ):  # test stream of QGC messages with parsebitfield = False
        EXPECTED_RESULTS = (
            "<QGC(RAW-PPPB2B, msgver=1, reserved1=0, prn=60, flag=b'\\x00', msgtype=0, reserved2=0, msgdata=b'\\x10\\x35\\xfc\\x49\\x04\\x40\\x01\\x3f\\x77\\x04\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x44\\x00\\x11\\x00\\x05\\x80\\x00\\x5f\\x6b\\x84\\x00\\x11\\x00\\x07\\x7d\\x63\\x10\\x00\\x78\\x17\\x0f\\xfd\\xd1\\x02\\x57\\x10\\x00\\x44\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x58\\x7f\\x00\\x01\\x81\\x36\\xb0')>",
            "<QGC(RAW-QZSSL6, msgver=1, reserved1=0, prn=195, flag=b'\\x81', reserved2=0, msgdata=b'\\x1a\\xcf\\xfc\\x1d\\xc3\\xa9\\x7f\\x48\\xab\\x08\\x92\\x88\\xc0\\x3a\\xa8\\x40\\x30\\x02\\x02\\x93\\xdf\\xdf\\xf5\\xd5\\xde\\x43\\x1c\\x00\\x00\\x02\\x04\\x80\\x04\\x70\\x00\\x00\\x00\\x00\\x82\\x40\\x7f\\x49\\xe8\\x11\\x08\\x04\\x7f\\xed\\x40\\x0e\\x9f\\xe2\\x01\\x8b\\x02\\xb1\\x02\\x5c\\x00\\x5c\\x06\\x2f\\xb1\\x9f\\xea\\xbf\\xea\\xbf\\xf6\\x00\\x5d\\x07\\x7b\\xf1\\x03\\xe8\\xa7\\xf5\\x10\\x6e\\xdf\\xd2\\x5a\\x04\\xa2\\x3b\\xfd\\x0d\\xfc\\x40\\x30\\x0e\\xfc\\x5c\\x02\\x20\\x0b\\xc8\\xbf\\x0b\\x03\\x98\\x0d\\x60\\x5f\\x0a\\x80\\xd4\\x03\\x98\\xbf\\x68\\xff\\xdf\\x03\\x82\\x87\\xd5\\x4f\\xba\\x01\\x8c\\xd7\\xf0\\x88\\x4b\\xfe\\xd4\\x31\\xf4\\x34\\x08\\xa0\\x3a\\x19\\xfc\\xe7\\xf0\\x10\\x01\\x17\\x7c\\x3a\\xfd\\xb8\\x23\\x04\\xbf\\xb5\\x1f\\xf2\\xff\\xe8\\x93\\xf7\\x4c\\x01\\xc0\\x04\\x13\\xbe\\xd9\\x00\\x2b\\xfe\\xa2\\x77\\xde\\xd0\\x08\\x7f\\xd8\\x4e\\xfa\\xbd\\xff\\x70\\x03\\x09\\xdf\\x89\\xbf\\xfa\\x00\\xca\\x5f\\xcd\\x1f\\xb5\\xfd\\xcd\\x2f\\xd1\\xb0\\x0d\\xff\\x8e\\x97\\xbf\\x17\\xf6\\x80\\x55\\xfd\\x29\\xa0\\x4a\\x20\\x01\\xfe\\x80\\x28\\x00\\x05\\xc0\\xa7\\xf3\\x00\\x15\\x9c\\xcd\\xe1\\x8b\\xc4\\xee\\x2d\\xe8\\x5c\\xd1\\xf1\\x28\\xf9\\xa2\\x81\\x83\\xdf\\xeb\\x8e\\x1b\\x5f\\xfe\\x18\\xf7\\xd9\\x21\\x54\\x33\\x1c\\x5c\\x10')>",
            "<QGC(RAW-HASE6, msgver=1, reserved1=0, prn=34, status=b'\\x01', msgtype=1, reserved2=0, page=2, reserved3=0, msgdata=b'\\x38\\xb2\\x00\\xe8\\x50\\xe9\\xa0\\x5e\\x7f\\xc6\\x0d\\x00\\x31\\xff\\x2e\\x00\\x00\\x5b\\xfe\\x50\\x2c\\xc0\\xe1\\x00\\x00\\x2f\\x77\\xe0\\x0b\\x20\\xc6\\xe5\\x3f\\x49\\x79\\xf0\\x10\\x50\\x11\\xf8\\xcb\\xeb\\x7f\\x31\\x04\\x67\\xd0\\x80\\xf2\\x05\\xc0\\x0e\\x81\\xb2\\x00\\xe8\\x50\\xe9\\xa0\\x5e\\x7f\\xc6\\x0d\\x00\\x31\\xff\\x2e\\x00\\x00\\x5b\\xfe\\x50\\x2c\\xc0\\xe1\\x00\\x00\\x2f\\x77\\xe0\\x0b\\x20\\xc6\\xe5\\x3f\\x49\\x79\\xf0\\x10\\x50\\x11\\xf8\\xcb\\xeb\\x7f\\x31\\x04\\x67\\xd0\\x80\\xf2\\x05\\xc0\\x0e\\x81\\xc8')>",
        )

        i = 0
        with open(os.path.join(DIRNAME, "pygpsdata_lg580p_qgc.log"), "rb") as stream:
            ubr = QGCReader(
                stream,
                parsing=True,
                parsebitfield=0,
                validate=VALCKSUM,
                quitonerror=ERR_RAISE,
            )
            for raw, parsed in ubr:
                # print(f'"{parsed}",')
                self.assertEqual(str(parsed), EXPECTED_RESULTS[i])
                i += 1
            self.assertEqual(i, len(EXPECTED_RESULTS))

    def testMixed(
        self,
    ):  # test mixed stream of QGC, NMEA and RTCM3 - show NMEA and RTCM only
        EXPECTED_RESULTS = (
            "<NMEA(GNDTM, datum=W84, subDatum=, latOfset=0.0, NS=N, lonOfset=0.0, EW=E, alt=0.0, refDatum=W84)>",
            "<NMEA(GNRMC, time=10:36:07, status=A, lat=53.450657, NS=N, lon=-102.2404103333, EW=W, spd=0.046, cog=, date=2021-03-06, mv=, mvEW=, posMode=A, navStatus=V)>",
            "<NMEA(GPRTE, numMsg=2, msgNum=1, status=c, routeid=0, wpt_01=PBRCPK, wpt_02=PBRTO, wpt_03=PTELGR, wpt_04=PPLAND, wpt_05=PYAMBU, wpt_06=PPFAIR, wpt_07=PWARRN, wpt_08=PMORTL, wpt_09=PLISMR)>",
            "<NMEA(GNRLM, beacon=00000078A9FBAD5, time=08:35:59, code=3, body=C45B)>",
            "<NMEA(GNVTG, cogt=, cogtUnit=T, cogm=, cogmUnit=M, sogn=0.046, sognUnit=N, sogk=0.085, sogkUnit=K, posMode=A)>",
            "<NMEA(GNGNS, time=10:36:07, lat=53.450657, NS=N, lon=-2.2404103333, EW=W, posMode=AANN, numSV=6, HDOP=5.88, alt=56.0, sep=48.5, diffAge=, diffStation=, navStatus=V)>",
            "<NMEA(GNGGA, time=10:36:07, lat=53.450657, NS=N, lon=-2.2404103333, EW=W, quality=1, numSV=6, HDOP=5.88, alt=56.0, altUnit=M, sep=48.5, sepUnit=M, diffAge=, diffStation=)>",
            "<NMEA(GNGSA, opMode=A, navMode=3, svid_01=23, svid_02=24, svid_03=20, svid_04=12, svid_05=, svid_06=, svid_07=, svid_08=, svid_09=, svid_10=, svid_11=, svid_12=, PDOP=9.62, HDOP=5.88, VDOP=7.62, systemId=1)>",
            "<NMEA(GNGSA, opMode=A, navMode=3, svid_01=66, svid_02=76, svid_03=, svid_04=, svid_05=, svid_06=, svid_07=, svid_08=, svid_09=, svid_10=, svid_11=, svid_12=, PDOP=9.62, HDOP=5.88, VDOP=7.62, systemId=2)>",
            "<NMEA(GNGSA, opMode=A, navMode=3, svid_01=, svid_02=, svid_03=, svid_04=, svid_05=, svid_06=, svid_07=, svid_08=, svid_09=, svid_10=, svid_11=, svid_12=, PDOP=9.62, HDOP=5.88, VDOP=7.62, systemId=3)>",
            "<NMEA(GNGSA, opMode=A, navMode=3, svid_01=, svid_02=, svid_03=, svid_04=, svid_05=, svid_06=, svid_07=, svid_08=, svid_09=, svid_10=, svid_11=, svid_12=, PDOP=9.62, HDOP=5.88, VDOP=7.62, systemId=4)>",
            "<NMEA(GPGSV, numMsg=3, msgNum=1, numSV=11, svid_01=1, elv_01=6.0, az_01=14, cno_01=8, svid_02=12, elv_02=43.0, az_02=207, cno_02=28, svid_03=14, elv_03=6.0, az_03=49, cno_03=, svid_04=15, elv_04=44.0, az_04=171, cno_04=23, signalID=1)>",
            "<NMEA(GPGSV, numMsg=3, msgNum=2, numSV=11, svid_01=17, elv_01=32.0, az_01=64, cno_01=16, svid_02=19, elv_02=33.0, az_02=94, cno_02=, svid_03=20, elv_03=20.0, az_03=251, cno_03=31, svid_04=21, elv_04=4.0, az_04=354, cno_04=, signalID=1)>",
        )

        i = 0
        with open(os.path.join(DIRNAME, "pygpsdata_mixed.log"), "rb") as stream:
            ubr = QGCReader(
                stream,
                protfilter=NMEA_PROTOCOL | RTCM3_PROTOCOL,
                parsing=True,
                parsebitfield=1,
                validate=VALCKSUM,
                quitonerror=ERR_RAISE,
            )
            for raw, parsed in ubr:
                # print(f'"{parsed}",')
                self.assertEqual(str(parsed), EXPECTED_RESULTS[i])
                i += 1
            self.assertEqual(i, len(EXPECTED_RESULTS))

    def testMixed2(self):  # test mixed stream of QGC, NMEA - show QGC and NMEA only
        EXPECTED_RESULTS = (
            "<QGC(RAW-PPPB2B, msgver=1, reserved1=0, prn=60, pppstatus=0, msgtype=0, reserved2=0, msgdata=b'\\x10\\x35\\xfc\\x49\\x04\\x40\\x01\\x3f\\x77\\x04\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x44\\x00\\x11\\x00\\x05\\x80\\x00\\x5f\\x6b\\x84\\x00\\x11\\x00\\x07\\x7d\\x63\\x10\\x00\\x78\\x17\\x0f\\xfd\\xd1\\x02\\x57\\x10\\x00\\x44\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x58\\x7f\\x00\\x01\\x81\\x36\\xb0')>",
            "<QGC(RAW-QZSSL6, msgver=1, reserved1=0, prn=195, rsstatus=1, msgtype=1, reserved2=0, msgdata=b'\\x1a\\xcf\\xfc\\x1d\\xc3\\xa9\\x7f\\x48\\xab\\x08\\x92\\x88\\xc0\\x3a\\xa8\\x40\\x30\\x02\\x02\\x93\\xdf\\xdf\\xf5\\xd5\\xde\\x43\\x1c\\x00\\x00\\x02\\x04\\x80\\x04\\x70\\x00\\x00\\x00\\x00\\x82\\x40\\x7f\\x49\\xe8\\x11\\x08\\x04\\x7f\\xed\\x40\\x0e\\x9f\\xe2\\x01\\x8b\\x02\\xb1\\x02\\x5c\\x00\\x5c\\x06\\x2f\\xb1\\x9f\\xea\\xbf\\xea\\xbf\\xf6\\x00\\x5d\\x07\\x7b\\xf1\\x03\\xe8\\xa7\\xf5\\x10\\x6e\\xdf\\xd2\\x5a\\x04\\xa2\\x3b\\xfd\\x0d\\xfc\\x40\\x30\\x0e\\xfc\\x5c\\x02\\x20\\x0b\\xc8\\xbf\\x0b\\x03\\x98\\x0d\\x60\\x5f\\x0a\\x80\\xd4\\x03\\x98\\xbf\\x68\\xff\\xdf\\x03\\x82\\x87\\xd5\\x4f\\xba\\x01\\x8c\\xd7\\xf0\\x88\\x4b\\xfe\\xd4\\x31\\xf4\\x34\\x08\\xa0\\x3a\\x19\\xfc\\xe7\\xf0\\x10\\x01\\x17\\x7c\\x3a\\xfd\\xb8\\x23\\x04\\xbf\\xb5\\x1f\\xf2\\xff\\xe8\\x93\\xf7\\x4c\\x01\\xc0\\x04\\x13\\xbe\\xd9\\x00\\x2b\\xfe\\xa2\\x77\\xde\\xd0\\x08\\x7f\\xd8\\x4e\\xfa\\xbd\\xff\\x70\\x03\\x09\\xdf\\x89\\xbf\\xfa\\x00\\xca\\x5f\\xcd\\x1f\\xb5\\xfd\\xcd\\x2f\\xd1\\xb0\\x0d\\xff\\x8e\\x97\\xbf\\x17\\xf6\\x80\\x55\\xfd\\x29\\xa0\\x4a\\x20\\x01\\xfe\\x80\\x28\\x00\\x05\\xc0\\xa7\\xf3\\x00\\x15\\x9c\\xcd\\xe1\\x8b\\xc4\\xee\\x2d\\xe8\\x5c\\xd1\\xf1\\x28\\xf9\\xa2\\x81\\x83\\xdf\\xeb\\x8e\\x1b\\x5f\\xfe\\x18\\xf7\\xd9\\x21\\x54\\x33\\x1c\\x5c\\x10')>",
            "<QGC(RAW-HASE6, msgver=1, reserved1=0, prn=34, hasmode=1, msgtype=1, reserved2=0, page=2, reserved3=0, msgdata=b'\\x38\\xb2\\x00\\xe8\\x50\\xe9\\xa0\\x5e\\x7f\\xc6\\x0d\\x00\\x31\\xff\\x2e\\x00\\x00\\x5b\\xfe\\x50\\x2c\\xc0\\xe1\\x00\\x00\\x2f\\x77\\xe0\\x0b\\x20\\xc6\\xe5\\x3f\\x49\\x79\\xf0\\x10\\x50\\x11\\xf8\\xcb\\xeb\\x7f\\x31\\x04\\x67\\xd0\\x80\\xf2\\x05\\xc0\\x0e\\x81\\xb2\\x00\\xe8\\x50\\xe9\\xa0\\x5e\\x7f\\xc6\\x0d\\x00\\x31\\xff\\x2e\\x00\\x00\\x5b\\xfe\\x50\\x2c\\xc0\\xe1\\x00\\x00\\x2f\\x77\\xe0\\x0b\\x20\\xc6\\xe5\\x3f\\x49\\x79\\xf0\\x10\\x50\\x11\\xf8\\xcb\\xeb\\x7f\\x31\\x04\\x67\\xd0\\x80\\xf2\\x05\\xc0\\x0e\\x81\\xc8')>",
            "<QGC(RAW-PPPB2B, msgver=1, reserved1=0, prn=60, pppstatus=0, msgtype=0, reserved2=0, msgdata=b'\\x10\\x35\\xfc\\x49\\x04\\x40\\x01\\x3f\\x77\\x04\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x44\\x00\\x11\\x00\\x05\\x80\\x00\\x5f\\x6b\\x84\\x00\\x11\\x00\\x07\\x7d\\x63\\x10\\x00\\x78\\x17\\x0f\\xfd\\xd1\\x02\\x57\\x10\\x00\\x44\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x58\\x7f\\x00\\x01\\x81\\x36\\xb0')>",
            "<QGC(RAW-QZSSL6, msgver=1, reserved1=0, prn=195, rsstatus=1, msgtype=1, reserved2=0, msgdata=b'\\x1a\\xcf\\xfc\\x1d\\xc3\\xa9\\x7f\\x48\\xab\\x08\\x92\\x88\\xc0\\x3a\\xa8\\x40\\x30\\x02\\x02\\x93\\xdf\\xdf\\xf5\\xd5\\xde\\x43\\x1c\\x00\\x00\\x02\\x04\\x80\\x04\\x70\\x00\\x00\\x00\\x00\\x82\\x40\\x7f\\x49\\xe8\\x11\\x08\\x04\\x7f\\xed\\x40\\x0e\\x9f\\xe2\\x01\\x8b\\x02\\xb1\\x02\\x5c\\x00\\x5c\\x06\\x2f\\xb1\\x9f\\xea\\xbf\\xea\\xbf\\xf6\\x00\\x5d\\x07\\x7b\\xf1\\x03\\xe8\\xa7\\xf5\\x10\\x6e\\xdf\\xd2\\x5a\\x04\\xa2\\x3b\\xfd\\x0d\\xfc\\x40\\x30\\x0e\\xfc\\x5c\\x02\\x20\\x0b\\xc8\\xbf\\x0b\\x03\\x98\\x0d\\x60\\x5f\\x0a\\x80\\xd4\\x03\\x98\\xbf\\x68\\xff\\xdf\\x03\\x82\\x87\\xd5\\x4f\\xba\\x01\\x8c\\xd7\\xf0\\x88\\x4b\\xfe\\xd4\\x31\\xf4\\x34\\x08\\xa0\\x3a\\x19\\xfc\\xe7\\xf0\\x10\\x01\\x17\\x7c\\x3a\\xfd\\xb8\\x23\\x04\\xbf\\xb5\\x1f\\xf2\\xff\\xe8\\x93\\xf7\\x4c\\x01\\xc0\\x04\\x13\\xbe\\xd9\\x00\\x2b\\xfe\\xa2\\x77\\xde\\xd0\\x08\\x7f\\xd8\\x4e\\xfa\\xbd\\xff\\x70\\x03\\x09\\xdf\\x89\\xbf\\xfa\\x00\\xca\\x5f\\xcd\\x1f\\xb5\\xfd\\xcd\\x2f\\xd1\\xb0\\x0d\\xff\\x8e\\x97\\xbf\\x17\\xf6\\x80\\x55\\xfd\\x29\\xa0\\x4a\\x20\\x01\\xfe\\x80\\x28\\x00\\x05\\xc0\\xa7\\xf3\\x00\\x15\\x9c\\xcd\\xe1\\x8b\\xc4\\xee\\x2d\\xe8\\x5c\\xd1\\xf1\\x28\\xf9\\xa2\\x81\\x83\\xdf\\xeb\\x8e\\x1b\\x5f\\xfe\\x18\\xf7\\xd9\\x21\\x54\\x33\\x1c\\x5c\\x10')>",
            "<QGC(RAW-HASE6, msgver=1, reserved1=0, prn=34, hasmode=1, msgtype=1, reserved2=0, page=2, reserved3=0, msgdata=b'\\x38\\xb2\\x00\\xe8\\x50\\xe9\\xa0\\x5e\\x7f\\xc6\\x0d\\x00\\x31\\xff\\x2e\\x00\\x00\\x5b\\xfe\\x50\\x2c\\xc0\\xe1\\x00\\x00\\x2f\\x77\\xe0\\x0b\\x20\\xc6\\xe5\\x3f\\x49\\x79\\xf0\\x10\\x50\\x11\\xf8\\xcb\\xeb\\x7f\\x31\\x04\\x67\\xd0\\x80\\xf2\\x05\\xc0\\x0e\\x81\\xb2\\x00\\xe8\\x50\\xe9\\xa0\\x5e\\x7f\\xc6\\x0d\\x00\\x31\\xff\\x2e\\x00\\x00\\x5b\\xfe\\x50\\x2c\\xc0\\xe1\\x00\\x00\\x2f\\x77\\xe0\\x0b\\x20\\xc6\\xe5\\x3f\\x49\\x79\\xf0\\x10\\x50\\x11\\xf8\\xcb\\xeb\\x7f\\x31\\x04\\x67\\xd0\\x80\\xf2\\x05\\xc0\\x0e\\x81\\xc8')>",
            "<NMEA(GNDTM, datum=W84, subDatum=, latOfset=0.0, NS=N, lonOfset=0.0, EW=E, alt=0.0, refDatum=W84)>",
            "<NMEA(GNRMC, time=10:36:07, status=A, lat=53.450657, NS=N, lon=-102.2404103333, EW=W, spd=0.046, cog=, date=2021-03-06, mv=, mvEW=, posMode=A, navStatus=V)>",
            "<NMEA(GPRTE, numMsg=2, msgNum=1, status=c, routeid=0, wpt_01=PBRCPK, wpt_02=PBRTO, wpt_03=PTELGR, wpt_04=PPLAND, wpt_05=PYAMBU, wpt_06=PPFAIR, wpt_07=PWARRN, wpt_08=PMORTL, wpt_09=PLISMR)>",
            "<NMEA(GNRLM, beacon=00000078A9FBAD5, time=08:35:59, code=3, body=C45B)>",
            "<NMEA(GNVTG, cogt=, cogtUnit=T, cogm=, cogmUnit=M, sogn=0.046, sognUnit=N, sogk=0.085, sogkUnit=K, posMode=A)>",
            "<NMEA(GNGNS, time=10:36:07, lat=53.450657, NS=N, lon=-2.2404103333, EW=W, posMode=AANN, numSV=6, HDOP=5.88, alt=56.0, sep=48.5, diffAge=, diffStation=, navStatus=V)>",
            "<NMEA(GNGGA, time=10:36:07, lat=53.450657, NS=N, lon=-2.2404103333, EW=W, quality=1, numSV=6, HDOP=5.88, alt=56.0, altUnit=M, sep=48.5, sepUnit=M, diffAge=, diffStation=)>",
            "<NMEA(GNGSA, opMode=A, navMode=3, svid_01=23, svid_02=24, svid_03=20, svid_04=12, svid_05=, svid_06=, svid_07=, svid_08=, svid_09=, svid_10=, svid_11=, svid_12=, PDOP=9.62, HDOP=5.88, VDOP=7.62, systemId=1)>",
            "<NMEA(GNGSA, opMode=A, navMode=3, svid_01=66, svid_02=76, svid_03=, svid_04=, svid_05=, svid_06=, svid_07=, svid_08=, svid_09=, svid_10=, svid_11=, svid_12=, PDOP=9.62, HDOP=5.88, VDOP=7.62, systemId=2)>",
            "<NMEA(GNGSA, opMode=A, navMode=3, svid_01=, svid_02=, svid_03=, svid_04=, svid_05=, svid_06=, svid_07=, svid_08=, svid_09=, svid_10=, svid_11=, svid_12=, PDOP=9.62, HDOP=5.88, VDOP=7.62, systemId=3)>",
            "<NMEA(GNGSA, opMode=A, navMode=3, svid_01=, svid_02=, svid_03=, svid_04=, svid_05=, svid_06=, svid_07=, svid_08=, svid_09=, svid_10=, svid_11=, svid_12=, PDOP=9.62, HDOP=5.88, VDOP=7.62, systemId=4)>",
            "<NMEA(GPGSV, numMsg=3, msgNum=1, numSV=11, svid_01=1, elv_01=6.0, az_01=14, cno_01=8, svid_02=12, elv_02=43.0, az_02=207, cno_02=28, svid_03=14, elv_03=6.0, az_03=49, cno_03=, svid_04=15, elv_04=44.0, az_04=171, cno_04=23, signalID=1)>",
            "<NMEA(GPGSV, numMsg=3, msgNum=2, numSV=11, svid_01=17, elv_01=32.0, az_01=64, cno_01=16, svid_02=19, elv_02=33.0, az_02=94, cno_02=, svid_03=20, elv_03=20.0, az_03=251, cno_03=31, svid_04=21, elv_04=4.0, az_04=354, cno_04=, signalID=1)>",
        )

        i = 0
        with open(os.path.join(DIRNAME, "pygpsdata_mixed.log"), "rb") as stream:
            ubr = QGCReader(
                stream,
                protfilter=NMEA_PROTOCOL | QGC_PROTOCOL,
                parsing=True,
                parsebitfield=1,
                validate=VALCKSUM,
                quitonerror=ERR_RAISE,
            )
            for raw, parsed in ubr:
                # print(f'"{parsed}",')
                self.assertEqual(str(parsed), EXPECTED_RESULTS[i])
                i += 1
            self.assertEqual(i, len(EXPECTED_RESULTS))

    def testlu600set(self):  # test LU600 SET messages
        EXPECTED_RESULTS = (
            "<QGC(CTL-PAR, mode=1, reserved1=0)>",
            "<QGC(CFG-UART, intfid=1, intfstatus=1, reserved1=0, baudrate=921600, databit=8, parity=0, stopbit=1, reserved2=0)>",
            "<QGC(CFG-UART, intfid=1, intfstatus=0)>",
            "<QGC(CFG-CAN, intfid=0, intfstatus=1, frameprotocol=0, frameformat=0, baudrate=500000, databaudrate=2000000)>",
            "<QGC(CFG-CAN, intfid=0, intfstatus=0, frameprotocol=0, frameformat=0, baudrate=0, databaudrate=0)>",
            "<QGC(CFG-MSG, setmsggrp=16, setmsgid=1, rate=0, msgver=3)>",
            "<QGC(CFG-MSG, setmsggrp=241, setmsgid=10, rate=400, msgver=3)>",
            "<QGC(CFG-MSG, setmsggrp=202, setmsgid=2, rate=400, msgver=3)>",
            "<QGC(CFG-MSG, intftype=1, intfid=1, setmsggrp=241, setmsgid=10, rate=50, msgver=3)>",
            "<QGC(CFG-MSG, intftype=4, intfid=0, setmsggrp=202, setmsgid=2, rate=10, msgver=3)>",
            "<QGC(CFG-IMULPF, gyofilter=46, accfilter=46)>",
            "<QGC(CTL-RST, rstmask=0, rstmode=1, reserved1=0)>",
            "<QGC(CTL-PAR, mode=1, reserved1=0)>",
            "<QGC(CTL-PAR, mode=2, reserved1=0)>",
        )

        i = 0
        with open(os.path.join(DIRNAME, "pygpsdata_lu600_qgc_set.log"), "rb") as stream:
            ubr = QGCReader(
                stream,
                protfilter=QGC_PROTOCOL,
                parsing=True,
                parsebitfield=1,
                validate=VALCKSUM,
                msgmode=SET,
                quitonerror=ERR_RAISE,
            )
            for raw, parsed in ubr:
                # print(f'"{parsed}",')
                self.assertEqual(str(parsed), EXPECTED_RESULTS[i])
                i += 1
            self.assertEqual(i, len(EXPECTED_RESULTS))

    def testlu600get(self):  # test LU600 GET messages
        EXPECTED_RESULTS = (
            "<QGC(ACK-ACK, ackmsggrp=3, ackmsgid=2, errcode=0, reserved1=0)>",
            "<QGC(ACK-ACK, ackmsggrp=2, ackmsgid=1, errcode=0, reserved1=0)>",
            "<QGC(ACK-ACK, ackmsggrp=2, ackmsgid=1, errcode=0, reserved1=0)>",
            "<QGC(CFG-UART, intfid=1, intfstatus=1, reserved1=0, baudrate=460800, databit=8, parity=0, stopbit=1, reserved2=0)>",
            "<QGC(ACK-ACK, ackmsggrp=2, ackmsgid=1, errcode=0, reserved1=0)>",
            "<QGC(ACK-ACK, ackmsggrp=2, ackmsgid=4, errcode=0, reserved1=0)>",
            "<QGC(ACK-ACK, ackmsggrp=2, ackmsgid=4, errcode=0, reserved1=0)>",
            "<QGC(CFG-CAN, intfid=0, intfstatus=1, frameprotocol=0, frameformat=0, baudrate=1000000, databaudrate=2000000)>",
            "<QGC(ACK-ACK, ackmsggrp=2, ackmsgid=4, errcode=0, reserved1=0)>",
            "<QGC(ACK-ACK, ackmsggrp=2, ackmsgid=16, errcode=0, reserved1=0)>",
            "<QGC(ACK-ACK, ackmsggrp=2, ackmsgid=16, errcode=0, reserved1=0)>",
            "<QGC(ACK-ACK, ackmsggrp=2, ackmsgid=16, errcode=0, reserved1=0)>",
            "<QGC(CFG-MSG, setmsggrp=241, setmsgid=10, rate=0, msgver=3)>",
            "<QGC(ACK-ACK, ackmsggrp=2, ackmsgid=16, errcode=0, reserved1=0)>",
            "<QGC(CFG-MSG, setmsggrp=202, setmsgid=1, rate=100, msgver=3)>",
            "<QGC(ACK-ACK, ackmsggrp=2, ackmsgid=16, errcode=0, reserved1=0)>",
            "<QGC(ACK-ACK, ackmsggrp=2, ackmsgid=16, errcode=0, reserved1=0)>",
            "<QGC(ACK-ACK, ackmsggrp=2, ackmsgid=16, errcode=0, reserved1=0)>",
            "<QGC(CFG-MSG, intftype=4, intfid=0, setmsggrp=202, setmsgid=2, rate=400, msgver=3)>",
            "<QGC(ACK-ACK, ackmsggrp=2, ackmsgid=16, errcode=0, reserved1=0)>",
            "<QGC(ACK-ACK, ackmsggrp=2, ackmsgid=32, errcode=0, reserved1=0)>",
            "<QGC(CFG-IMULPF, gyofilter=46, accfilter=46)>",
            "<QGC(ACK-ACK, ackmsggrp=2, ackmsgid=32, errcode=0, reserved1=0)>",
            "<QGC(ACK-ACK, ackmsggrp=3, ackmsgid=1, errcode=0, reserved1=0)>",
            "<QGC(ACK-ACK, ackmsggrp=3, ackmsgid=2, errcode=0, reserved1=0)>",
            "<QGC(ACK-ACK, ackmsggrp=3, ackmsgid=2, errcode=0, reserved1=0)>",
            "<QGC(INF-VER, verstr=LUA600A00AANR01A02, builddate=2023/04/17, buildtime=16:28:06)>",
            "<QGC(ACK-ACK, ackmsggrp=6, ackmsgid=1, errcode=0, reserved1=0)>",
            "<QGC(INF-SN, snid=1, snstr=Q29G0F222200666)>",
            "<QGC(ACK-ACK, ackmsggrp=6, ackmsgid=2, errcode=0, reserved1=0)>",
            "<QGC(SEN-IMU, msgver=3, timestamp=15490, imutemp=27.549999237060547, gyox=-0.08710326999425888, gyoy=-0.1629486083984375, gyoz=0.00035095211933366954, accx=0.006952259223908186, accy=0.0011053276248276234, accz=-0.9955214858055115)>",
        )

        i = 0
        with open(os.path.join(DIRNAME, "pygpsdata_lu600_qgc_get.log"), "rb") as stream:
            ubr = QGCReader(
                stream,
                protfilter=QGC_PROTOCOL,
                parsing=True,
                parsebitfield=1,
                validate=VALCKSUM,
                msgmode=GET,
                quitonerror=ERR_RAISE,
            )
            for raw, parsed in ubr:
                # print(f'"{parsed}",')
                self.assertEqual(str(parsed), EXPECTED_RESULTS[i])
                i += 1
            self.assertEqual(i, len(EXPECTED_RESULTS))

    def testlu600poll(self):  # test LU600 POLL messages
        EXPECTED_RESULTS = (
            "<QGC(CFG-UART, intfid=1)>",
            "<QGC(CFG-CAN, intfid=0)>",
            "<QGC(CFG-MSG, setmsggrp=241, setmsgid=10, msgver=3)>",
            "<QGC(CFG-MSG, setmsggrp=202, setmsgid=1, msgver=3)>",
            "<QGC(CFG-MSG, intftype=4, intfid=0, setmsggrp=202, setmsgid=2, rate=3, msgver=0)>",
            "<QGC(CFG-IMULPF)>",
            "<QGC(INF-VER)>",
            "<QGC(INF-SN, snid=1)>",
        )

        i = 0
        with open(
            os.path.join(DIRNAME, "pygpsdata_lu600_qgc_poll.log"), "rb"
        ) as stream:
            ubr = QGCReader(
                stream,
                protfilter=QGC_PROTOCOL,
                parsing=True,
                parsebitfield=1,
                validate=VALCKSUM,
                msgmode=POLL,
                quitonerror=ERR_RAISE,
            )
            for raw, parsed in ubr:
                # print(f'"{parsed}",')
                self.assertEqual(str(parsed), EXPECTED_RESULTS[i])
                i += 1
            self.assertEqual(i, len(EXPECTED_RESULTS))

    def testunknown(self):  # test unknown message type
        EXPECTED_RESULT = "<QGC(UNKNOWN-0177-NOMINAL, payload=b'\\x03\\x02\\x00\\x00')>"
        BYTES = b"QG\x01\x77\x04\x00\x03\x02\x00\x00\x81s"
        msg = QGCReader.parse(BYTES)
        self.assertEqual(str(msg), EXPECTED_RESULT)

    def testunknownmode(self):  # test unknown message type
        BYTES = b"QG\x10\x01%\x00\x03\x82<\x00\x00\x00\x00\x00\x00ff\xdcA3c\xb2\xbd\x00\xdc&\xbe\xff\xff\xb79\xc7\xcf\xe3;\xa4\xe0\x90:\x7f\xda~\xbf+\xf2"
        with self.assertRaisesRegex(
            QGCMessageError,
            "Unknown message type b'\\\\x10\\\\x01', mode SET. Check 'msgmode' setting is appropriate for data stream",
        ):
            msg = QGCReader.parse(BYTES, msgmode=SET)

    def testrtcm(self):  # test RTCM parsing
        EXPECTED_RESULTS = (
            "<NMEA(GNGLL, field_01=3203.94995, field_02=N, field_03=03446.42914, field_04=E, field_05=084158.00, field_06=A, field_07=D)>",
            "<RTCM(1005, DF002=1005, DF003=0, DF021=0, DF022=1, DF023=1, DF024=1, DF141=0, DF025=4444030.802800001, DF142=1, DF001_1=0, DF026=3085671.2349, DF364=0, DF027=3366658.256)>",
            "<RTCM(4072, DF002=4072, Not_Yet_Implemented)>",
            "<RTCM(1077, DF002=1077, DF003=0, DF004=204137001, DF393=1, DF409=0, DF001_7=0, DF411=0, DF412=0, DF417=0, DF418=0, DF394=760738918298550272, NSat=10, DF395=1073807360, NSig=2, DF396=1044459, NCell=17, PRN_01=005, PRN_02=007, PRN_03=009, PRN_04=013, PRN_05=014, PRN_06=015, PRN_07=017, PRN_08=019, PRN_09=020, PRN_10=030, DF397_01=75, DF397_02=75, DF397_03=81, DF397_04=72, DF397_05=67, DF397_06=80, DF397_07=75, DF397_08=82, DF397_09=75, DF397_10=71, ExtSatInfo_01=0, ExtSatInfo_02=0, ExtSatInfo_03=0, ExtSatInfo_04=0, ExtSatInfo_05=0, ExtSatInfo_06=0, ExtSatInfo_07=0, ExtSatInfo_08=0, ExtSatInfo_09=0, ExtSatInfo_10=0, DF398_01=0.005859375, DF398_02=0.5341796875, DF398_03=0.7626953125, DF398_04=0.138671875, DF398_05=0.5498046875, DF398_06=0.11328125, DF398_07=0.8037109375, DF398_08=0.1025390625, DF398_09=0.521484375, DF398_10=0.345703125, DF399_01=-178, DF399_02=-304, DF399_03=-643, DF399_04=477, DF399_05=-52, DF399_06=645, DF399_07=529, DF399_08=643, DF399_09=-428, DF399_10=-181, CELLPRN_01=005, CELLSIG_01=1C, CELLPRN_02=005, CELLSIG_02=2L, CELLPRN_03=007, CELLSIG_03=1C, CELLPRN_04=007, CELLSIG_04=2L, CELLPRN_05=009, CELLSIG_05=1C, CELLPRN_06=009, CELLSIG_06=2L, CELLPRN_07=013, CELLSIG_07=1C, CELLPRN_08=014, CELLSIG_08=1C, CELLPRN_09=014, CELLSIG_09=2L, CELLPRN_10=015, CELLSIG_10=1C, CELLPRN_11=015, CELLSIG_11=2L, CELLPRN_12=017, CELLSIG_12=1C, CELLPRN_13=017, CELLSIG_13=2L, CELLPRN_14=019, CELLSIG_14=1C, CELLPRN_15=020, CELLSIG_15=1C, CELLPRN_16=030, CELLSIG_16=1C, CELLPRN_17=030, CELLSIG_17=2L, DF405_01=0.00014309026300907135, DF405_02=0.00014183297753334045, DF405_03=0.0003883279860019684, DF405_04=0.00038741156458854675, DF405_05=-0.0004838351160287857, DF405_06=-0.00046883709728717804, DF405_07=0.0003478657454252243, DF405_08=0.0002196934074163437, DF405_09=0.00021521002054214478, DF405_10=-0.00018852390348911285, DF405_11=-0.00018319115042686462, DF405_12=-0.00010087713599205017, DF405_13=-9.844452142715454e-05, DF405_14=0.00047875382006168365, DF405_15=0.00043664872646331787, DF405_16=-0.0003105681389570236, DF405_17=-0.00030865520238876343, DF406_01=0.00014193402603268623, DF406_02=0.00014339853078126907, DF406_03=0.00039040297269821167, DF406_04=0.00038743019104003906, DF406_05=-0.0004843934439122677, DF406_06=-0.00046825408935546875, DF406_07=0.0003473707474768162, DF406_08=0.00021758908405900002, DF406_09=0.00021597417071461678, DF406_10=-0.00018658116459846497, DF406_11=-0.00018350128084421158, DF406_12=-9.993184357881546e-05, DF406_13=-9.724870324134827e-05, DF406_14=0.0004128236323595047, DF406_15=0.0004355977289378643, DF406_16=-0.0003112703561782837, DF406_17=-0.00030898721888661385, DF407_01=341, DF407_02=341, DF407_03=341, DF407_04=341, DF407_05=341, DF407_06=341, DF407_07=341, DF407_08=341, DF407_09=341, DF407_10=341, DF407_11=341, DF407_12=341, DF407_13=341, DF407_14=295, DF407_15=341, DF407_16=341, DF407_17=341, DF420_01=0, DF420_02=0, DF420_03=0, DF420_04=0, DF420_05=0, DF420_06=0, DF420_07=0, DF420_08=0, DF420_09=0, DF420_10=0, DF420_11=0, DF420_12=0, DF420_13=0, DF420_14=0, DF420_15=0, DF420_16=0, DF420_17=0, DF408_01=45.0, DF408_02=38.0, DF408_03=43.0, DF408_04=39.0, DF408_05=39.0, DF408_06=37.0, DF408_07=45.0, DF408_08=46.0, DF408_09=46.0, DF408_10=39.0, DF408_11=34.0, DF408_12=45.0, DF408_13=38.0, DF408_14=31.0, DF408_15=45.0, DF408_16=46.0, DF408_17=41.0, DF404_01=-0.9231, DF404_02=-0.9194, DF404_03=-0.8321000000000001, DF404_04=-0.8326, DF404_05=-0.4107, DF404_06=-0.4072, DF404_07=0.2451, DF404_08=-0.0693, DF404_09=-0.0684, DF404_10=0.9390000000000001, DF404_11=0.9417000000000001, DF404_12=0.2384, DF404_13=0.2416, DF404_14=0.6636000000000001, DF404_15=-0.9556, DF404_16=-0.21480000000000002, DF404_17=-0.2174)>",
            "<RTCM(1087, DF002=1087, DF003=0, DF416=2, DF034=42119001, DF393=1, DF409=0, DF001_7=0, DF411=0, DF412=0, DF417=0, DF418=0, DF394=4039168114821169152, NSat=7, DF395=1090519040, NSig=2, DF396=16382, NCell=13, PRN_01=003, PRN_02=004, PRN_03=005, PRN_04=013, PRN_05=014, PRN_06=015, PRN_07=023, DF397_01=69, DF397_02=64, DF397_03=73, DF397_04=76, DF397_05=66, DF397_06=70, DF397_07=78, DF419_01=12, DF419_02=13, DF419_03=8, DF419_04=5, DF419_05=0, DF419_06=7, DF419_07=10, DF398_01=0.6337890625, DF398_02=0.3427734375, DF398_03=0.25390625, DF398_04=0.310546875, DF398_05=0.5126953125, DF398_06=0.8271484375, DF398_07=0.8837890625, DF399_01=-665, DF399_02=29, DF399_03=672, DF399_04=-573, DF399_05=-211, DF399_06=312, DF399_07=317, CELLPRN_01=003, CELLSIG_01=1C, CELLPRN_02=003, CELLSIG_02=2C, CELLPRN_03=004, CELLSIG_03=1C, CELLPRN_04=004, CELLSIG_04=2C, CELLPRN_05=005, CELLSIG_05=1C, CELLPRN_06=005, CELLSIG_06=2C, CELLPRN_07=013, CELLSIG_07=1C, CELLPRN_08=013, CELLSIG_08=2C, CELLPRN_09=014, CELLSIG_09=1C, CELLPRN_10=014, CELLSIG_10=2C, CELLPRN_11=015, CELLSIG_11=1C, CELLPRN_12=015, CELLSIG_12=2C, CELLPRN_13=023, CELLSIG_13=1C, DF405_01=0.00024936161935329437, DF405_02=0.0002511627972126007, DF405_03=-4.678964614868164e-05, DF405_04=-5.141831934452057e-05, DF405_05=1.1144205927848816e-05, DF405_06=2.15042382478714e-05, DF405_07=0.00047079287469387054, DF405_08=0.0004794951528310776, DF405_09=-0.0003879182040691376, DF405_10=-0.00037603825330734253, DF405_11=0.0002771839499473572, DF405_12=0.0002871435135602951, DF405_13=-0.00023611821234226227, DF406_01=0.00024937279522418976, DF406_02=0.00025077443569898605, DF406_03=-4.834495484828949e-05, DF406_04=-5.1246024668216705e-05, DF406_05=1.1149328202009201e-05, DF406_06=2.1803192794322968e-05, DF406_07=0.00047026341781020164, DF406_08=0.0004848274402320385, DF406_09=-0.0003876127302646637, DF406_10=-0.0003757951781153679, DF406_11=0.0002778824418783188, DF406_12=0.0002880701795220375, DF406_13=-0.00023698341101408005, DF407_01=341, DF407_02=341, DF407_03=340, DF407_04=340, DF407_05=341, DF407_06=341, DF407_07=340, DF407_08=341, DF407_09=341, DF407_10=341, DF407_11=341, DF407_12=341, DF407_13=340, DF420_01=0, DF420_02=0, DF420_03=0, DF420_04=0, DF420_05=0, DF420_06=0, DF420_07=0, DF420_08=0, DF420_09=0, DF420_10=0, DF420_11=0, DF420_12=0, DF420_13=0, DF408_01=47.0, DF408_02=40.0, DF408_03=47.0, DF408_04=42.0, DF408_05=47.0, DF408_06=39.0, DF408_07=36.0, DF408_08=33.0, DF408_09=48.0, DF408_10=43.0, DF408_11=48.0, DF408_12=40.0, DF408_13=41.0, DF404_01=-0.8193, DF404_02=-0.8173, DF404_03=0.8539, DF404_04=0.8501000000000001, DF404_05=0.7333000000000001, DF404_06=0.7311000000000001, DF404_07=-0.24930000000000002, DF404_08=-0.2543, DF404_09=-0.21580000000000002, DF404_10=-0.21780000000000002, DF404_11=0.3924, DF404_12=0.3947, DF404_13=0.6146)>",
            "<RTCM(1097, DF002=1097, DF003=0, DF248=204137001, DF393=1, DF409=0, DF001_7=0, DF411=0, DF412=0, DF417=0, DF418=0, DF394=216181732825628672, NSat=5, DF395=1073872896, NSig=2, DF396=1023, NCell=10, PRN_01=007, PRN_02=008, PRN_03=021, PRN_04=027, PRN_05=030, DF397_01=79, DF397_02=84, DF397_03=89, DF397_04=78, DF397_05=83, ExtSatInfo_01=0, ExtSatInfo_02=0, ExtSatInfo_03=0, ExtSatInfo_04=0, ExtSatInfo_05=0, DF398_01=0.15625, DF398_02=0.2509765625, DF398_03=0.3544921875, DF398_04=0.37109375, DF398_05=0.259765625, DF399_01=-198, DF399_02=-516, DF399_03=423, DF399_04=63, DF399_05=-384, CELLPRN_01=007, CELLSIG_01=1C, CELLPRN_02=007, CELLSIG_02=7Q, CELLPRN_03=008, CELLSIG_03=1C, CELLPRN_04=008, CELLSIG_04=7Q, CELLPRN_05=021, CELLSIG_05=1C, CELLPRN_06=021, CELLSIG_06=7Q, CELLPRN_07=027, CELLSIG_07=1C, CELLPRN_08=027, CELLSIG_08=7Q, CELLPRN_09=030, CELLSIG_09=1C, CELLPRN_10=030, CELLSIG_10=7Q, DF405_01=-4.5398250222206116e-05, DF405_02=-2.8252601623535156e-05, DF405_03=-0.00034597329795360565, DF405_04=-0.0003268253058195114, DF405_05=0.0004809703677892685, DF405_06=0.0005012489855289459, DF405_07=-0.00013696029782295227, DF405_08=-0.0001260414719581604, DF405_09=-1.8440186977386475e-05, DF405_10=-3.041699528694153e-06, DF406_01=-4.44464385509491e-05, DF406_02=-2.835458144545555e-05, DF406_03=-0.0003525479696691036, DF406_04=-0.0003263736143708229, DF406_05=0.00048203859478235245, DF406_06=0.0005008447915315628, DF406_07=-0.0001375703141093254, DF406_08=-0.00012635625898838043, DF406_09=-1.8037855625152588e-05, DF406_10=-3.2926909625530243e-06, DF407_01=341, DF407_02=341, DF407_03=341, DF407_04=341, DF407_05=341, DF407_06=341, DF407_07=341, DF407_08=341, DF407_09=341, DF407_10=341, DF420_01=0, DF420_02=0, DF420_03=0, DF420_04=0, DF420_05=0, DF420_06=0, DF420_07=0, DF420_08=0, DF420_09=0, DF420_10=0, DF408_01=46.0, DF408_02=49.0, DF408_03=41.0, DF408_04=43.0, DF408_05=43.0, DF408_06=43.0, DF408_07=45.0, DF408_08=49.0, DF408_09=43.0, DF408_10=47.0, DF404_01=-0.5806, DF404_02=-0.5831000000000001, DF404_03=-0.7947000000000001, DF404_04=-0.7943, DF404_05=0.7243, DF404_06=0.7174, DF404_07=0.5534, DF404_08=0.5545, DF404_09=-0.7726000000000001, DF404_10=-0.7733)>",
            "<RTCM(1127, DF002=1127, DF003=0, DF427=204123001, DF393=0, DF409=0, DF001_7=0, DF411=0, DF412=0, DF417=0, DF418=0, DF394=198178247981137920, NSat=10, DF395=1074003968, NSig=2, DF396=387754, NCell=11, PRN_01=007, PRN_02=009, PRN_03=010, PRN_04=020, PRN_05=023, PRN_06=028, PRN_07=032, PRN_08=037, PRN_09=040, PRN_10=043, DF397_01=129, DF397_02=132, DF397_03=126, DF397_04=75, DF397_05=81, DF397_06=84, DF397_07=78, DF397_08=74, DF397_09=130, DF397_10=86, ExtSatInfo_01=0, ExtSatInfo_02=0, ExtSatInfo_03=0, ExtSatInfo_04=0, ExtSatInfo_05=0, ExtSatInfo_06=0, ExtSatInfo_07=0, ExtSatInfo_08=0, ExtSatInfo_09=0, ExtSatInfo_10=0, DF398_01=0.1171875, DF398_02=0.4814453125, DF398_03=0.3095703125, DF398_04=0.7255859375, DF398_05=0.41015625, DF398_06=0.5703125, DF398_07=0.5595703125, DF398_08=0.322265625, DF398_09=0.578125, DF398_10=0.673828125, DF399_01=-130, DF399_02=-58, DF399_03=-81, DF399_04=32, DF399_05=-398, DF399_06=436, DF399_07=-523, DF399_08=-65, DF399_09=-182, DF399_10=79, CELLPRN_01=007, CELLSIG_01=7I, CELLPRN_02=009, CELLSIG_02=7I, CELLPRN_03=010, CELLSIG_03=2I, CELLPRN_04=010, CELLSIG_04=7I, CELLPRN_05=020, CELLSIG_05=2I, CELLPRN_06=023, CELLSIG_06=2I, CELLPRN_07=028, CELLSIG_07=2I, CELLPRN_08=032, CELLSIG_08=2I, CELLPRN_09=037, CELLSIG_09=2I, CELLPRN_10=040, CELLSIG_10=2I, CELLPRN_11=043, CELLSIG_11=2I, DF405_01=-0.0003885403275489807, DF405_02=0.00022730417549610138, DF405_03=0.0004036612808704376, DF405_04=0.00039606913924217224, DF405_05=-0.00016684085130691528, DF405_06=-4.75514680147171e-05, DF405_07=0.0003674682229757309, DF405_08=0.00026629865169525146, DF405_09=-0.0002502594143152237, DF405_10=-0.00011803768575191498, DF405_11=-0.0002937670797109604, DF406_01=-0.0003882073797285557, DF406_02=0.0002264929935336113, DF406_03=0.0004031979478895664, DF406_04=0.0003964221104979515, DF406_05=-0.00016694329679012299, DF406_06=-4.848744720220566e-05, DF406_07=0.00036971503868699074, DF406_08=0.0002654106356203556, DF406_09=-0.00025115441530942917, DF406_10=-0.00011868216097354889, DF406_11=-0.00029495684430003166, DF407_01=341, DF407_02=341, DF407_03=341, DF407_04=341, DF407_05=341, DF407_06=341, DF407_07=341, DF407_08=341, DF407_09=341, DF407_10=341, DF407_11=341, DF420_01=0, DF420_02=0, DF420_03=0, DF420_04=0, DF420_05=0, DF420_06=0, DF420_07=0, DF420_08=0, DF420_09=0, DF420_10=0, DF420_11=0, DF408_01=45.0, DF408_02=41.0, DF408_03=42.0, DF408_04=45.0, DF408_05=48.0, DF408_06=46.0, DF408_07=42.0, DF408_08=47.0, DF408_09=48.0, DF408_10=44.0, DF408_11=43.0, DF404_01=-0.5674, DF404_02=-0.612, DF404_03=-0.1384, DF404_04=-0.1332, DF404_05=0.5992000000000001, DF404_06=-0.7312000000000001, DF404_07=0.17320000000000002, DF404_08=-0.4308, DF404_09=-0.5975, DF404_10=-0.6733, DF404_11=0.6122000000000001)>",
            "<RTCM(1230, DF002=1230, DF003=0, DF421=1, DF001_3=0, DF422_1=0, DF422_2=0, DF422_3=0, DF422_4=0)>",
            "<NMEA(GNRMC, field_01=084159.00, field_02=A, field_03=3203.94995, field_04=N, field_05=03446.42914, field_06=E, field_07=0.000, field_08=, field_09=080222, field_10=, field_11=, field_12=D, field_13=V)>",
        )

        i = 0
        with open(os.path.join(DIRNAME, "pygpsdata_mixed_rtcm3.log"), "rb") as stream:
            ubr = QGCReader(
                stream,
                protfilter=QGC_PROTOCOL | RTCM3_PROTOCOL | NMEA_PROTOCOL,
                parsing=True,
                parsebitfield=1,
                validate=VALCKSUM,
                msgmode=POLL,
                quitonerror=ERR_RAISE,
            )
            for raw, parsed in ubr:
                # print(f'"{parsed}",')
                self.assertEqual(str(parsed), EXPECTED_RESULTS[i])
                i += 1
            self.assertEqual(i, len(EXPECTED_RESULTS))

    def testparse(self):
        EXPECTED_RESULT = "<QGC(RAW-PPPB2B, msgver=1, reserved1=0, prn=60, pppstatus=1, msgtype=1, reserved2=0, msgdata=b'\\x10\\x35\\xfc\\x49\\x04\\x40\\x01\\x3f\\x77\\x04\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x44\\x00\\x11\\x00\\x05\\x80\\x00\\x5f\\x6b\\x84\\x00\\x11\\x00\\x07\\x7d\\x63\\x10\\x00\\x78\\x17\\x0f\\xfd\\xd1\\x02\\x57\\x10\\x00\\x44\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x58\\x7f\\x00\\x01\\x81\\x36\\xb0')>"
        stream = b"QG\n\xb2U\x00\x01\x00\x00\x00\x00< \x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x105\xfcI\x04@\x01?w\x04\x00\x11\x00\x04@\x01\x10\x00D\x00\x11\x00\x05\x80\x00_k\x84\x00\x11\x00\x07}c\x10\x00x\x17\x0f\xfd\xd1\x02W\x10\x00D\x00\x11\x00\x04@\x01\x10\x00X\x7f\x00\x01\x816\xb0L\xf4"
        msg = QGCReader.parse(stream, msgmode=GET)
        self.assertEqual(str(msg), EXPECTED_RESULT)

    def testparse_badmode(self):
        stream = b"QG\n\xb2U\x00\x01\x00\x00\x00\x00< \x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x105\xfcI\x04@\x01?w\x04\x00\x11\x00\x04@\x01\x10\x00D\x00\x11\x00\x05\x80\x00_k\x84\x00\x11\x00\x07}c\x10\x00x\x17\x0f\xfd\xd1\x02W\x10\x00D\x00\x11\x00\x04@\x01\x10\x00X\x7f\x00\x01\x816\xb0L\xf4"
        with self.assertRaisesRegex(
            QGCParseError, "Invalid message mode 7 - must be 0, 1, 2 or 3"
        ):
            msg = QGCReader.parse(stream, msgmode=7)

    def testparse_badhdr(self):
        stream = b"QX\n\xb2U\x00\x01\x00\x00\x00\x00< \x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x105\xfcI\x04@\x01?w\x04\x00\x11\x00\x04@\x01\x10\x00D\x00\x11\x00\x05\x80\x00_k\x84\x00\x11\x00\x07}c\x10\x00x\x17\x0f\xfd\xd1\x02W\x10\x00D\x00\x11\x00\x04@\x01\x10\x00X\x7f\x00\x01\x816\xb0L\xf4"
        with self.assertRaisesRegex(
            QGCParseError, f"Invalid message header b'QX' - should be {QGC_HDR}"
        ):
            msg = QGCReader.parse(stream, msgmode=GET)

    def testparse_badlen(self):
        stream = b"QG\n\xb2V\x00\x01\x00\x00\x00\x00< \x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x105\xfcI\x04@\x01?w\x04\x00\x11\x00\x04@\x01\x10\x00D\x00\x11\x00\x05\x80\x00_k\x84\x00\x11\x00\x07}c\x10\x00x\x17\x0f\xfd\xd1\x02W\x10\x00D\x00\x11\x00\x04@\x01\x10\x00X\x7f\x00\x01\x816\xb0L\xf4"
        with self.assertRaisesRegex(
            QGCParseError, "Invalid payload length b'V\\\\x00' - should be b'U\\\\x00'"
        ):
            msg = QGCReader.parse(stream, msgmode=GET)

    def testparse_badcks(self):
        stream = b"QG\n\xb2U\x00\x01\x00\x00\x00\x00< \x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x105\xfcI\x04@\x01?w\x04\x00\x11\x00\x04@\x01\x10\x00D\x00\x11\x00\x05\x80\x00_k\x84\x00\x11\x00\x07}c\x10\x00x\x17\x0f\xfd\xd1\x02W\x10\x00D\x00\x11\x00\x04@\x01\x10\x00X\x7f\x00\x01\x816\xb0L\xf5"
        with self.assertRaisesRegex(
            QGCParseError,
            "Message checksum b'L\\\\xf5' invalid - should be b'L\\\\xf4'",
        ):
            msg = QGCReader.parse(stream, msgmode=GET)

    def testparse_badcks_permitted(self):
        EXPECTED_RESULT = "<QGC(RAW-PPPB2B, msgver=1, reserved1=0, prn=60, pppstatus=1, msgtype=1, reserved2=0, msgdata=b'\\x10\\x35\\xfc\\x49\\x04\\x40\\x01\\x3f\\x77\\x04\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x44\\x00\\x11\\x00\\x05\\x80\\x00\\x5f\\x6b\\x84\\x00\\x11\\x00\\x07\\x7d\\x63\\x10\\x00\\x78\\x17\\x0f\\xfd\\xd1\\x02\\x57\\x10\\x00\\x44\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x58\\x7f\\x00\\x01\\x81\\x36\\xb0')>"
        stream = b"QG\n\xb2U\x00\x01\x00\x00\x00\x00< \x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x105\xfcI\x04@\x01?w\x04\x00\x11\x00\x04@\x01\x10\x00D\x00\x11\x00\x05\x80\x00_k\x84\x00\x11\x00\x07}c\x10\x00x\x17\x0f\xfd\xd1\x02W\x10\x00D\x00\x11\x00\x04@\x01\x10\x00X\x7f\x00\x01\x816\xb0L\xf5"
        msg = QGCReader.parse(stream, msgmode=GET, validate=VALNONE)
        self.assertEqual(str(msg), EXPECTED_RESULT)

    def testparse_setpoll(self):
        msg1 = QGCMessage(
            b"\x02",
            b"\x04",
            msgmode=POLL,
            intfid=3,
        )
        msg2 = QGCReader.parse(msg1.serialize(), msgmode=SETPOLL)
        self.assertEqual(str(msg1), str(msg2))
        msg1 = QGCMessage(
            b"\x02",
            b"\x04",
            msgmode=SET,
            intfid=3,
            intfstatus=0,
            frameprotocol=0,
            frameformat=1,
            baudrate=100000,
            databaudrate=200000,
        )
        msg2 = QGCReader.parse(msg1.serialize(), msgmode=SETPOLL)
        self.assertEqual(str(msg1), str(msg2))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
