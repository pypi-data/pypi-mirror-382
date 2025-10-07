"""
QGCReader class.

Reads and parses individual QGC messages from any viable
data stream which supports a read(n) -> bytes method.

QGC message bit format (little-endian):

+--------+---------+---------+---------+----------+---------+
|  sync  | msggrp  | msgnum  | length  | payload  | cksum   |
+========+=========+=========+=========+==========+=========+
| 0x5147 | 8 bits  | 8 bits  | 16 bits | variable | 16 bits |
+--------+---------+---------+---------+----------+---------+
|                  6 bytes             |                    |
+--------+---------+---------+---------+----------+---------+

Returns both the raw binary data (as bytes) and the parsed data
(as an QGCMessage object).

- 'quitonerror' governs how errors are handled
- 'parsing' governs whether messages are fully parsed

Created on 6 Oct 2025

:author: semuadmin (Steve Smith)
:copyright: semuadmin © 2020
:license: BSD 3-Clause
"""

# pylint: disable=too-many-positional-arguments

from logging import getLogger
from socket import socket

from pynmeagps import SocketWrapper

from pyqgc.exceptions import (
    QGCMessageError,
    QGCParseError,
    QGCStreamError,
    QGCTypeError,
)
from pyqgc.qgchelpers import bytes2val, calc_checksum, val2bytes
from pyqgc.qgcmessage import QGCMessage
from pyqgc.qgctypes_core import (
    ERR_LOG,
    ERR_RAISE,
    QGC_HDR,
    U2,
    VALCKSUM,
)


class QGCReader:
    """
    QGCReader class.
    """

    def __init__(
        self,
        datastream,
        validate: int = VALCKSUM,
        quitonerror: int = ERR_LOG,
        parsebitfield: bool = True,
        bufsize: int = 4096,
        parsing: bool = True,
        errorhandler: object = None,
    ):
        """Constructor.

        :param datastream stream: input data stream
        :param int validate: VALCKSUM (1) = Validate checksum,
            VALNONE (0) = ignore invalid checksum (1)
        :param int quitonerror: ERR_IGNORE (0) = ignore errors,  ERR_LOG (1) = log continue,
            ERR_RAISE (2) = (re)raise (1)
        :param bool parsebitfield: 1 = parse bitfields, 0 = leave as bytes (1)
        :param int bufsize: socket recv buffer size (4096)
        :param bool parsing: True = parse data, False = don't parse data (output raw only) (True)
        :param object errorhandler: error handling object or function (None)
        :raises: QGCStreamError (if mode is invalid)
        """
        # pylint: disable=too-many-arguments

        if isinstance(datastream, socket):
            self._stream = SocketWrapper(datastream, bufsize=bufsize)
        else:
            self._stream = datastream
        self._quitonerror = quitonerror
        self._errorhandler = errorhandler
        self._validate = validate
        self._parsebf = parsebitfield
        self._parsing = parsing
        self._logger = getLogger(__name__)

    def __iter__(self):
        """Iterator."""

        return self

    def __next__(self) -> tuple:
        """
        Return next item in iteration.

        :return: tuple of (raw_data as bytes, parsed_data as QGCMessage)
        :rtype: tuple
        :raises: StopIteration

        """

        (raw_data, parsed_data) = self.read()
        if raw_data is None and parsed_data is None:
            raise StopIteration
        return (raw_data, parsed_data)

    def read(self) -> tuple:
        """
        Read a single QGC message from the stream buffer
        and return both raw and parsed data.

        'quitonerror' determines whether to raise, log or ignore parsing errors.

        :return: tuple of (raw_data as bytes, parsed_data as QGCMessage)
        :rtype: tuple
        :raises: Exception (if invalid or unrecognised protocol in data stream)
        """

        parsing = True
        while parsing:  # loop until end of valid message or EOF
            try:

                raw_data = None
                parsed_data = None
                byte1 = self._read_bytes(1)  # read the first byte
                # if not QGC, NMEA or RTCM3, discard and continue
                if byte1 != b"\x51":
                    continue
                byte2 = self._read_bytes(1)
                bytehdr = byte1 + byte2
                # if it's a QGC message (b'\xb5\x62')
                if bytehdr == QGC_HDR:
                    (raw_data, parsed_data) = self._parse_qgc(bytehdr)
                    parsing = False
                # unrecognised protocol header
                else:
                    raise QGCParseError(f"Unknown protocol header {bytehdr}.")

            except EOFError:
                return (None, None)
            except (
                QGCMessageError,
                QGCTypeError,
                QGCParseError,
                QGCStreamError,
            ) as err:
                if self._quitonerror:
                    self._do_error(err)
                continue

        return (raw_data, parsed_data)

    def _parse_qgc(self, hdr: bytes) -> tuple:
        """
        Parse remainder of QGC message.

        :param bytes hdr: QGC header (b'\\x51\\x47')
        :return: tuple of (raw_data as bytes, parsed_data as QGCMessage or None)
        :rtype: tuple
        """

        # read the rest of the QGC message from the buffer
        byten = self._read_bytes(4)
        msggrp = byten[0:1]
        msgid = byten[1:2]
        lenb = byten[2:4]
        leni = int.from_bytes(lenb, "little", signed=False)
        byten = self._read_bytes(leni + 2)
        plb = byten[0:leni]
        cksum = byten[leni : leni + 2]
        raw_data = hdr + msggrp + msgid + lenb + plb + cksum
        # only parse if we need to (filter passes QGC)
        if self._parsing:
            parsed_data = self.parse(
                raw_data,
                validate=self._validate,
                parsebitfield=self._parsebf,
            )
        else:
            parsed_data = None
        return (raw_data, parsed_data)

    def _read_bytes(self, size: int) -> bytes:
        """
        Read a specified number of bytes from stream.

        :param int size: number of bytes to read
        :return: bytes
        :rtype: bytes
        :raises: QGCStreamError if stream ends prematurely
        """

        data = self._stream.read(size)
        if len(data) == 0:  # EOF
            raise EOFError()
        if 0 < len(data) < size:  # truncated stream
            raise QGCStreamError(
                "Serial stream terminated unexpectedly. "
                f"{size} bytes requested, {len(data)} bytes returned."
            )
        return data

    def _read_line(self) -> bytes:
        """
        Read bytes until LF (0x0a) terminator.

        :return: bytes
        :rtype: bytes
        :raises: QGCStreamError if stream ends prematurely
        """

        data = self._stream.readline()  # NMEA protocol is CRLF-terminated
        if len(data) == 0:
            raise EOFError()  # pragma: no cover
        if data[-1:] != b"\x0a":  # truncated stream
            raise QGCStreamError(
                "Serial stream terminated unexpectedly. "
                f"Line requested, {len(data)} bytes returned."
            )
        return data

    def _do_error(self, err: Exception):
        """
        Handle error.

        :param Exception err: error
        :raises: Exception if quitonerror = ERR_RAISE (2)
        """

        if self._quitonerror == ERR_RAISE:
            raise err from err
        if self._quitonerror == ERR_LOG:
            # pass to error handler if there is one
            # else just log
            if self._errorhandler is None:
                self._logger.error(err)
            else:
                self._errorhandler(err)

    @property
    def datastream(self) -> object:
        """
        Getter for stream.

        :return: data stream
        :rtype: object
        """

        return self._stream

    @staticmethod
    def parse(
        message: bytes,
        validate: int = VALCKSUM,
        parsebitfield: bool = True,
    ) -> object:
        """
        Parse QGC byte stream to QGCMessage object.

        :param bytes message: binary message to parse
        :param int validate: VALCKSUM (1) = Validate checksum,
            VALNONE (0) = ignore invalid checksum (1)
        :param bool parsebitfield: 1 = parse bitfields, 0 = leave as bytes (1)
        :return: QGCMessage object
        :rtype: QGCMessage
        :raises: Exception (if data stream contains invalid data or unknown message type)
        """

        lenm = len(message)
        hdr = message[0:2]
        msggrp = message[2:3]
        msgid = message[3:4]
        lenb = message[4:6]
        if lenb == b"\x00\x00":
            payload = None
            leni = 0
        else:
            payload = message[6 : lenm - 2]
            leni = len(payload)
        ckm = message[lenm - 2 : lenm]
        if payload is not None:
            ckv = calc_checksum(msggrp + msgid + lenb + payload)
        else:
            ckv = calc_checksum(msggrp + msgid + lenb)
        if validate & VALCKSUM:
            if hdr != QGC_HDR:
                raise QGCParseError(
                    (f"Invalid message header {hdr}" f" - should be {QGC_HDR}")
                )
            if leni != bytes2val(lenb, U2):
                raise QGCParseError(
                    (
                        f"Invalid payload length {lenb}"
                        f" - should be {val2bytes(leni, U2)}"
                    )
                )
            if ckm != ckv:
                raise QGCParseError(
                    (f"Message checksum {ckm}" f" invalid - should be {ckv}")
                )
        if payload is None:
            return QGCMessage(msggrp, msgid)
        return QGCMessage(
            msggrp,
            msgid,
            payload=payload,
            parsebitfield=parsebitfield,
        )
