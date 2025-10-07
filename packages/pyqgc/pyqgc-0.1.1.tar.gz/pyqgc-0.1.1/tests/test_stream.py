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
    VALNONE,
    VALCKSUM,
    ERR_RAISE,
    ERR_LOG,
    ERR_IGNORE,
    NMEA_PROTOCOL,
    RTCM3_PROTOCOL,
    QGC_PROTOCOL,
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
            ubr = QGCReader(stream, parsing=True, parsebitfield=1, validate=VALCKSUM)
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
            ubr = QGCReader(stream, parsing=True, parsebitfield=0, validate=VALCKSUM)
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
            )
            for raw, parsed in ubr:
                # print(f'"{parsed}",')
                self.assertEqual(str(parsed), EXPECTED_RESULTS[i])
                i += 1
            self.assertEqual(i, len(EXPECTED_RESULTS))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
