"""
Helper, Property and Static method tests for pyqgc.UBXMessage

Created on 6 Oct 2025

*** NB: must be saved in UTF-8 format ***

@author: semuadmin
"""

# pylint: disable=line-too-long, invalid-name, missing-docstring, no-member

import os
import unittest

import pyqgc.qgctypes_core as qgt
import pyqgc.exceptions as qge
from pyqgc.qgctypes_core import SET, GET, VALCKSUM, CV, POLL, QGC_MSGIDS
from pyqgc import QGCReader, QGCMessage
from pyqgc.qgchelpers import (
    attsiz,
    att2idx,
    att2name,
    bytes2val,
    nomval,
    calc_checksum,
    escapeall,
    get_bits,
    getpaylen,
    getinputmode,
    hextable,
    isvalid_checksum,
    key_from_val,
    val2bytes,
)


class StaticTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        dirname = os.path.dirname(__file__)
        self.streamQGC = open(os.path.join(dirname, "pygpsdata_lg580p_qgc.log"), "rb")
        self.qgcmsg = QGCMessage(
            b"\x0a",
            b"\xb2",
            msgmode=GET,
            parsebitfield=1,
            msgver=1,
            prn=60,
            pppstatus=1,
            msgtype=1,
            msgdata=b"\x10\x35\xfc\x49\x04\x40\x01\x3f\x77\x04\x00\x11\x00\x04\x40\x01\x10\x00\x44\x00\x11\x00\x05\x80\x00\x5f\x6b\x84\x00\x11\x00\x07\x7d\x63\x10\x00\x78\x17\x0f\xfd\xd1\x02\x57\x10\x00\x44\x00\x11\x00\x04\x40\x01\x10\x00\x58\x7f\x00\x01\x81\x36\xb0",
        )

    def tearDown(self):
        self.streamQGC.close()

    # def testDefinitions(self):  # DEBUG test for possible missing payload definitions
    #     for msg in ubt.UBX_MSGIDS.values():
    #         if (
    #             msg not in (ubp.UBX_PAYLOADS_POLL)
    #             and msg not in (ubg.UBX_PAYLOADS_GET)
    #             and msg not in (ubs.UBX_PAYLOADS_SET)
    #         ):
    #             print(f"Possible missing payload definition {msg}")
    #     for msg in ubg.UBX_PAYLOADS_GET:
    #         if msg not in ubt.UBX_MSGIDS.values():
    #             print(f"Possible missing core definition {msg} GET")
    #     for msg in ubs.UBX_PAYLOADS_SET:
    #         if msg not in ubt.UBX_MSGIDS.values():
    #             print(f"Possible missing core definition {msg} SET")
    #     for msg in ubp.UBX_PAYLOADS_POLL:
    #         if msg not in ubt.UBX_MSGIDS.values():
    #             print(f"Possible missing core definition {msg} POLL")

    def testConstructor(self):
        EXPECTED_RESULT = "<QGC(RAW-PPPB2B, msgver=1, reserved1=0, prn=60, pppstatus=1, msgtype=1, reserved2=0, msgdata=b'\\x10\\x35\\xfc\\x49\\x04\\x40\\x01\\x3f\\x77\\x04\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x44\\x00\\x11\\x00\\x05\\x80\\x00\\x5f\\x6b\\x84\\x00\\x11\\x00\\x07\\x7d\\x63\\x10\\x00\\x78\\x17\\x0f\\xfd\\xd1\\x02\\x57\\x10\\x00\\x44\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x58\\x7f\\x00\\x01\\x81\\x36\\xb0')>"
        msg = QGCMessage(
            b"\x0a",
            b"\xb2",
            msgmode=GET,
            parsebitfield=1,
            msgver=1,
            prn=60,
            pppstatus=1,
            msgtype=1,
            msgdata=b"\x10\x35\xfc\x49\x04\x40\x01\x3f\x77\x04\x00\x11\x00\x04\x40\x01\x10\x00\x44\x00\x11\x00\x05\x80\x00\x5f\x6b\x84\x00\x11\x00\x07\x7d\x63\x10\x00\x78\x17\x0f\xfd\xd1\x02\x57\x10\x00\x44\x00\x11\x00\x04\x40\x01\x10\x00\x58\x7f\x00\x01\x81\x36\xb0",
        )
        self.assertEqual(str(msg), EXPECTED_RESULT)

    def testParse(self):
        EXPECTED_RESULT = "<QGC(RAW-PPPB2B, msgver=1, reserved1=0, prn=60, pppstatus=1, msgtype=1, reserved2=0, msgdata=b'\\x10\\x35\\xfc\\x49\\x04\\x40\\x01\\x3f\\x77\\x04\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x44\\x00\\x11\\x00\\x05\\x80\\x00\\x5f\\x6b\\x84\\x00\\x11\\x00\\x07\\x7d\\x63\\x10\\x00\\x78\\x17\\x0f\\xfd\\xd1\\x02\\x57\\x10\\x00\\x44\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x58\\x7f\\x00\\x01\\x81\\x36\\xb0')>"
        msg = QGCMessage(
            b"\x0a",
            b"\xb2",
            msgmode=GET,
            parsebitfield=1,
            msgver=1,
            prn=60,
            pppstatus=1,
            msgtype=1,
            msgdata=b"\x10\x35\xfc\x49\x04\x40\x01\x3f\x77\x04\x00\x11\x00\x04\x40\x01\x10\x00\x44\x00\x11\x00\x05\x80\x00\x5f\x6b\x84\x00\x11\x00\x07\x7d\x63\x10\x00\x78\x17\x0f\xfd\xd1\x02\x57\x10\x00\x44\x00\x11\x00\x04\x40\x01\x10\x00\x58\x7f\x00\x01\x81\x36\xb0",
        )
        self.assertEqual(
            msg.serialize(),
            b"QG\n\xb2U\x00\x01\x00\x00\x00\x00< \x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x105\xfcI\x04@\x01?w\x04\x00\x11\x00\x04@\x01\x10\x00D\x00\x11\x00\x05\x80\x00_k\x84\x00\x11\x00\x07}c\x10\x00x\x17\x0f\xfd\xd1\x02W\x10\x00D\x00\x11\x00\x04@\x01\x10\x00X\x7f\x00\x01\x816\xb0L\xf4",
        )
        self.assertEqual(str(QGCReader.parse(msg.serialize())), EXPECTED_RESULT)

    def testRepr(self):
        EXPECTED_REPR = "QGCMessage(b'\\n', b'\\xb2', 0, payload=b'\\x01\\x00\\x00\\x00\\x00< \\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x105\\xfcI\\x04@\\x01?w\\x04\\x00\\x11\\x00\\x04@\\x01\\x10\\x00D\\x00\\x11\\x00\\x05\\x80\\x00_k\\x84\\x00\\x11\\x00\\x07}c\\x10\\x00x\\x17\\x0f\\xfd\\xd1\\x02W\\x10\\x00D\\x00\\x11\\x00\\x04@\\x01\\x10\\x00X\\x7f\\x00\\x01\\x816\\xb0')"
        msg = QGCMessage(
            b"\x0a",
            b"\xb2",
            msgmode=GET,
            parsebitfield=1,
            msgver=1,
            prn=60,
            pppstatus=1,
            msgtype=1,
            msgdata=b"\x10\x35\xfc\x49\x04\x40\x01\x3f\x77\x04\x00\x11\x00\x04\x40\x01\x10\x00\x44\x00\x11\x00\x05\x80\x00\x5f\x6b\x84\x00\x11\x00\x07\x7d\x63\x10\x00\x78\x17\x0f\xfd\xd1\x02\x57\x10\x00\x44\x00\x11\x00\x04\x40\x01\x10\x00\x58\x7f\x00\x01\x81\x36\xb0",
        )
        self.assertEqual(repr(msg), EXPECTED_REPR)
        self.assertEqual(str(eval(repr(msg))), str(msg))

    def testProperties(self):
        msg = QGCMessage(
            b"\x0a",
            b"\xb2",
            msgmode=GET,
            parsebitfield=1,
            msgver=1,
            prn=60,
            pppstatus=1,
            msgtype=1,
            msgdata=b"\x10\x35\xfc\x49\x04\x40\x01\x3f\x77\x04\x00\x11\x00\x04\x40\x01\x10\x00\x44\x00\x11\x00\x05\x80\x00\x5f\x6b\x84\x00\x11\x00\x07\x7d\x63\x10\x00\x78\x17\x0f\xfd\xd1\x02\x57\x10\x00\x44\x00\x11\x00\x04\x40\x01\x10\x00\x58\x7f\x00\x01\x81\x36\xb0",
        )
        self.assertEqual(msg.msg_grp, b"\x0a")
        self.assertEqual(msg.msg_id, b"\xb2")
        self.assertEqual(msg.length, 85)
        self.assertEqual(msg.msgmode, GET)
        self.assertEqual(
            msg.payload,
            b"\x01\x00\x00\x00\x00< \x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x105\xfcI\x04@\x01?w\x04\x00\x11\x00\x04@\x01\x10\x00D\x00\x11\x00\x05\x80\x00_k\x84\x00\x11\x00\x07}c\x10\x00x\x17\x0f\xfd\xd1\x02W\x10\x00D\x00\x11\x00\x04@\x01\x10\x00X\x7f\x00\x01\x816\xb0",
        )

    def testVal2Bytes(self):  # test conversion of value to bytes
        INPUTS = [
            (2345, qgt.U2),
            (b"\x44\x55", qgt.X2),
            (23.12345678, qgt.R4),
            (-23.12345678912345, qgt.R8),
            ("test1234", qgt.C8),
        ]
        EXPECTED_RESULTS = [
            b"\x29\x09",
            b"\x44\x55",
            b"\xd7\xfc\xb8\x41",
            b"\x1f\xc1\x37\xdd\x9a\x1f\x37\xc0",
            "test1234",
        ]
        for i, inp in enumerate(INPUTS):
            (val, att) = inp
            res = val2bytes(val, att)
            self.assertEqual(res, EXPECTED_RESULTS[i])

    def testVal2BytesInvalid(self):
        with self.assertRaisesRegex(qge.QGCTypeError, "Unknown attribute type Y002"):
            res = val2bytes(1234, "Y002")

    def testBytes2Val(self):  # test conversion of bytes to value
        INPUTS = [
            (b"\x29\x09", qgt.U2),
            (b"\x44\x55", qgt.X2),
            (b"\xd7\xfc\xb8\x41", qgt.R4),
            (b"\x1f\xc1\x37\xdd\x9a\x1f\x37\xc0", qgt.R8),
            (b"test1234", qgt.C8),
        ]
        EXPECTED_RESULTS = [
            2345,
            b"\x44\x55",
            23.12345678,
            -23.12345678912345,
            "test1234",
        ]
        for i, inp in enumerate(INPUTS):
            (valb, att) = inp
            res = bytes2val(valb, att)
            if att == qgt.R4:
                self.assertAlmostEqual(res, EXPECTED_RESULTS[i], 6)
            elif att == qgt.R8:
                self.assertAlmostEqual(res, EXPECTED_RESULTS[i], 14)
            else:
                self.assertEqual(res, EXPECTED_RESULTS[i])

    def testBytes2ValInvalid(self):
        with self.assertRaisesRegex(qge.QGCTypeError, "Unknown attribute type Y002"):
            res = bytes2val(b"\x12\x34", "Y002")

    def testNomval(self):  # test conversion of value to bytes
        INPUTS = [
            qgt.U2,
            qgt.X2,
            qgt.R4,
            qgt.R8,
            qgt.C8,
        ]
        EXPECTED_RESULTS = [
            0,
            b"\x00\x00",
            0.0,
            0.0,
            "        ",
        ]
        for i, att in enumerate(INPUTS):
            res = nomval(att)
            self.assertEqual(res, EXPECTED_RESULTS[i])

    def testNomValInvalid(self):
        with self.assertRaisesRegex(qge.QGCTypeError, "Unknown attribute type Y002"):
            res = nomval("Y002")

    def testCalcChecksum(self):
        res = calc_checksum(b"\x06\x01\x02\x00\xf0\x05")
        self.assertEqual(res, b"\xfe\x16")

    def testGoodChecksum(self):
        res = isvalid_checksum(b"\xb5b\x06\x01\x02\x00\xf0\x05\xfe\x16")
        self.assertTrue(res)

    def testBadChecksum(self):
        res = isvalid_checksum(b"\xb5b\x06\x01\x02\x00\xf0\x05\xfe\x15")
        self.assertFalse(res)

    def testgetbits(self):
        INPUTS = [
            (b"\x89", 192),
            (b"\xc9", 3),
            (b"\x89", 9),
            (b"\xc9", 9),
            (b"\x18\x18", 8),
            (b"\x18\x20", 8),
        ]
        EXPECTED_RESULTS = [2, 1, 9, 9, 1, 0]
        for i, (vb, mask) in enumerate(INPUTS):
            vi = get_bits(vb, mask)
            self.assertEqual(vi, EXPECTED_RESULTS[i])

    def testdatastream(self):  # test datastream getter
        EXPECTED_RESULT = "<class '_io.BufferedReader'>"
        res = str(type(QGCReader(self.streamQGC).datastream))
        self.assertEqual(res, EXPECTED_RESULT)

    def testhextable(self):  # test hextable*( method)
        EXPECTED_RESULT = "000: 2447 4e47 4c4c 2c35 3332 372e 3034 3331  | b'$GNGLL,5327.0431'                                                 |\n016: 392c 532c 3030 3231 342e 3431 3339 362c  | b'9,S,00214.41396,'                                                 |\n032: 452c 3232 3332 3332 2e30 302c 412c 412a  | b'E,223232.00,A,A*'                                                 |\n048: 3638 0d0a                                | b'68\\r\\n'                                                           |\n"
        res = hextable(b"$GNGLL,5327.04319,S,00214.41396,E,223232.00,A,A*68\r\n", 8)
        self.assertEqual(res, EXPECTED_RESULT)

    def testgetinputmode(self):
        res = getinputmode(b"\x02", b"\x04", b"\x01\x00")
        self.assertEqual(res, POLL)
        res = getinputmode(b"\x02", b"\x04", b"\x0c\x00")
        self.assertEqual(res, SET)
        res = getinputmode(b"\x02", b"\x01", b"\x01\x00")
        self.assertEqual(res, POLL)
        res = getinputmode(b"\x02", b"\x01", b"\x0c\x00")
        self.assertEqual(res, SET)
        res = getinputmode(b"\x99", b"\x99", b"\x0c\x00")
        self.assertEqual(res, SET)

    def testattsiz(self):  # test attsiz
        self.assertEqual(attsiz(CV), -1)
        self.assertEqual(attsiz("C032"), 32)

    def testatt2idx(self):  # test att2idx
        EXPECTED_RESULT = [4, 16, 101, 0, (3, 6), 0]
        atts = ["svid_04", "gnssId_16", "cno_101", "gmsLon", "gnod_03_06", "dodgy_xx"]
        for i, att in enumerate(atts):
            res = att2idx(att)
            # print(res)
            self.assertEqual(res, EXPECTED_RESULT[i])

    def testatt2name(self):  # test att2name
        EXPECTED_RESULT = ["svid", "gnssId", "cno", "gmsLon"]
        atts = ["svid_04", "gnssId_16", "cno_101", "gmsLon"]
        for i, att in enumerate(atts):
            res = att2name(att)
            # print(res)
            self.assertEqual(res, EXPECTED_RESULT[i])

    def testescapeall(self):
        EXPECTED_RESULT = "b'\\x68\\x65\\x72\\x65\\x61\\x72\\x65\\x73\\x6f\\x6d\\x65\\x63\\x68\\x61\\x72\\x73'"
        val = b"herearesomechars"
        res = escapeall(val)
        print(res)
        self.assertEqual(res, EXPECTED_RESULT)

    def testInvMode(self):  # test invalid mode
        EXPECTED_ERROR = "Invalid msgmode 4 - must be 0, 1 or 2"
        with self.assertRaisesRegex(qge.QGCMessageError, EXPECTED_ERROR):
            QGCMessage(
                b"\x0a",
                b"\xb2",
                msgmode=4,
                parsebitfield=1,
                msgdata=b"\x10\x35\xfc\x49\x04\x40\x01\x3f\x77\x04\x00\x11\x00\x04\x40\x01\x10\x00\x44\x00\x11\x00\x05\x80\x00\x5f\x6b\x84\x00\x11\x00\x07\x7d\x63\x10\x00\x78\x17\x0f\xfd\xd1\x02\x57\x10\x00\x44\x00\x11\x00\x04\x40\x01\x10\x00\x58\x7f\x00\x01\x81\x36\xb0",
            )

    def testBadCksum(self):  # bad checksum
        EXPECTED_ERROR = "Message checksum (.*) invalid - should be (.*)"
        badck = b"QG\n\xb2U\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x105\xfcI\x04@\x01?w\x04\x00\x11\x00\x04@\x01\x10\x00D\x00\x11\x00\x05\x80\x00_k\x84\x00\x11\x00\x07}c\x10\x00x\x17\x0f\xfd\xd1\x02W\x10\x00D\x00\x11\x00\x04@\x01\x10\x00X\x7f\x00\x01\x816\xb0\xee\xb2"
        with self.assertRaisesRegex(qge.QGCParseError, EXPECTED_ERROR):
            QGCReader.parse(badck, validate=VALCKSUM)

    def testbadType(self):  # incorrect type (integer not binary)
        EXPECTED_ERROR = (
            "Incorrect type for attribute 'prn' in GET message class RAW-PPPB2B"
        )
        with self.assertRaisesRegex(qge.QGCTypeError, EXPECTED_ERROR):
            QGCMessage(
                b"\x0a",
                b"\xb2",
                msgmode=GET,
                parsebitfield=1,
                msgver=1,
                prn="60",
                pppstatus=1,
                msgtype=1,
                msgdata=b"\x10\x35\xfc\x49\x04\x40\x01\x3f\x77\x04\x00\x11\x00\x04\x40\x01\x10\x00\x44\x00\x11\x00\x05\x80\x00\x5f\x6b\x84\x00\x11\x00\x07\x7d\x63\x10\x00\x78\x17\x0f\xfd\xd1\x02\x57\x10\x00\x44\x00\x11\x00\x04\x40\x01\x10\x00\x58\x7f\x00\x01\x81\x36\xb0",
            )

    def testgetpayloadlen(self):
        res = getpaylen("CFG-MSG-INTF", SET)
        self.assertEqual(res, 7)
        res = getpaylen("CFG-MSG", SET)
        self.assertEqual(res, 5)
        res = getpaylen("SEN-IMU", GET)
        self.assertEqual(res, 37)
        res = getpaylen("INF-VER", GET)
        self.assertEqual(res, -1)
        res = getpaylen("INF-VER", 7)
        self.assertEqual(res, -1)

    def testkeyfromval(self):
        res = key_from_val(QGC_MSGIDS, "CFG-UART")
        self.assertEqual(res, b"\x02\x01")

    def testkeyfromvalinvalid(self):
        with self.assertRaisesRegex(KeyError, "No key found for value CFG-XXXX"):
            res = key_from_val(QGC_MSGIDS, "CFG-XXXX")

    def testOverflow(self):
        with self.assertRaisesRegex(
            qge.QGCTypeError,
            "Overflow error for attribute 'prn' in GET message class RAW-PPPB2B",
        ):
            msg = QGCMessage(
                b"\x0a",
                b"\xb2",
                msgmode=GET,
                parsebitfield=1,
                msgver=1,
                prn=99999999,
                pppstatus=1,
                msgtype=1,
                msgdata=b"\x10\x35\xfc\x49\x04\x40\x01\x3f\x77\x04\x00\x11\x00\x04\x40\x01\x10\x00\x44\x00\x11\x00\x05\x80\x00\x5f\x6b\x84\x00\x11\x00\x07\x7d\x63\x10\x00\x78\x17\x0f\xfd\xd1\x02\x57\x10\x00\x44\x00\x11\x00\x04\x40\x01\x10\x00\x58\x7f\x00\x01\x81\x36\xb0",
            )

    def testImmutable(self):
        with self.assertRaisesRegex(
            qge.QGCMessageError,
            "Object is immutable. Updates to prn not permitted after initialisation.",
        ):
            msg = QGCMessage(
                b"\x0a",
                b"\xb2",
                msgmode=GET,
                parsebitfield=1,
                msgver=1,
                prn=60,
                pppstatus=1,
                msgtype=1,
                msgdata=b"\x10\x35\xfc\x49\x04\x40\x01\x3f\x77\x04\x00\x11\x00\x04\x40\x01\x10\x00\x44\x00\x11\x00\x05\x80\x00\x5f\x6b\x84\x00\x11\x00\x07\x7d\x63\x10\x00\x78\x17\x0f\xfd\xd1\x02\x57\x10\x00\x44\x00\x11\x00\x04\x40\x01\x10\x00\x58\x7f\x00\x01\x81\x36\xb0",
            )
            msg.prn = 33


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
