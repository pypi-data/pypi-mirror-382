pyqgc
=======

[Current Status](#currentstatus) |
[Installation](#installation) |
[Message Categories](#msgcat) |
[Reading](#reading) |
[Parsing](#parsing) |
[Generating](#generating) |
[Serializing](#serializing) |
[Examples](#examples) |
[Extensibility](#extensibility) |
[Troubleshooting](#troubleshoot) |
[Author & License](#author)

`pyqgc` is an original Python 3 parser for the QGC &copy; protocol. QGC is a proprietary binary protocol implemented on Quectel &trade; GNSS receiver modules. `pyqgc` can also parse NMEA 0183 &copy; and RTCM3 &copy; protocols via the underlying [`pynmeagps`](https://github.com/semuconsulting/pynmeagps) and [`pyrtcm`](https://github.com/semuconsulting/pyrtcm) packages from the same author - hence it covers all the protocols that Quectel QGC GNSS receivers are capable of outputting.

The `pyqgc` homepage is located at [https://github.com/semuconsulting/pyqgc](https://github.com/semuconsulting/pyqgc).

This is an independent project and we have no affiliation whatsoever with Quectel.

## <a name="currentstatus">Current Status</a>

![Status](https://img.shields.io/pypi/status/pyqgc)
![Release](https://img.shields.io/github/v/release/semuconsulting/pyqgc?include_prereleases)
![Build](https://img.shields.io/github/actions/workflow/status/semuconsulting/pyqgc/main.yml?branch=main)
![Codecov](https://img.shields.io/codecov/c/github/semuconsulting/pyqgc)
![Release Date](https://img.shields.io/github/release-date-pre/semuconsulting/pyqgc)
![Last Commit](https://img.shields.io/github/last-commit/semuconsulting/pyqgc)
![Contributors](https://img.shields.io/github/contributors/semuconsulting/pyqgc.svg)
![Open Issues](https://img.shields.io/github/issues-raw/semuconsulting/pyqgc)

The current alpha release implements 3 QGC RAW message types defined for the LG580P receiver, but is readily [extensible](#extensibility). Refer to `QGC_MSGIDS` in [qgctypes_core.py](https://github.com/semuconsulting/pyqgc/blob/main/src/pyqgc/qgctypes_core.py#L64) for the complete dictionary of messages currently supported. QGC protocol information sourced from public domain Quectel [LG580P GNSS Protocol Specification](https://www.quectel.com/download/quectel_lg290p03lgx80p03_gnss_protocol_specification_v1-1/) © 2025, Quectel.

Sphinx API Documentation in HTML format is available at [https://www.semuconsulting.com/pyqgc/](https://www.semuconsulting.com/pyqgc/).

Contributions welcome - please refer to [CONTRIBUTING.MD](https://github.com/semuconsulting/pyqgc/blob/master/CONTRIBUTING.md). Feel free to discuss any proposed changes beforehand in the [Discussion Channel](https://github.com/semuconsulting/pyqgc/discussions/categories/ideas).

[Bug reports](https://github.com/semuconsulting/pyqgc/blob/master/.github/ISSUE_TEMPLATE/bug_report.md) and [Feature requests](https://github.com/semuconsulting/pyqgc/blob/master/.github/ISSUE_TEMPLATE/feature_request.md) - please use the templates provided. For general queries and advice, post a message to one of the [pyqgc Discussions](https://github.com/semuconsulting/pyqgc/discussions) channels.

![No Copilot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/nocopilot100.png?raw=true)

---
## <a name="installation">Installation</a>

![Python version](https://img.shields.io/pypi/pyversions/pyqgc.svg?style=flat)
[![PyPI version](https://img.shields.io/pypi/v/pyqgc.svg?style=flat)](https://pypi.org/project/pyqgc/)
[![PyPI downloads](https://github.com/semuconsulting/pygpsclient/blob/master/images/clickpy_icon.svg?raw=true)](https://clickpy.clickhouse.com/dashboard/pyqgc)

`pyqgc` is compatible with Python>=3.10. In the following, `python3` & `pip` refer to the Python 3 executables. You may need to substitute `python` for `python3`, depending on your particular environment (*on Windows it's generally `python`*).

The recommended way to install the latest version of `pyqgc` is with [pip](http://pypi.python.org/pypi/pip/):

```shell
python3 -m pip install --upgrade pyqgc
```

If required, `pyqgc` can also be installed into a virtual environment, e.g.:

```shell
python3 -m venv env
source env/bin/activate # (or env\Scripts\activate on Windows)
python3 -m pip install --upgrade pyqgc
```

For [Conda](https://docs.conda.io/en/latest/) users, `pyqgc` is also available from [conda forge](https://github.com/conda-forge/pyqgc-feedstock):

[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyqgc/badges/version.svg)](https://anaconda.org/conda-forge/pyqgc)
[![Anaconda-Server Badge](https://img.shields.io/conda/dn/conda-forge/pyqgc)](https://anaconda.org/conda-forge/pyqgc)

```shell
conda install -c conda-forge pyqgc
```
---
## <a name="msgcat">QGC Message Categories - GET, SET, POLL</a>

`pyqgc` divides QGC messages into three categories, signified by the `mode` or `msgmode` parameter.

| mode        | description                              | defined in         |
|-------------|------------------------------------------|--------------------|
| GET (0x00)  | output *from* the receiver (the default) | `qgctypes_get.py`  |
| SET (0x01)  | command input *to* the receiver          | `qgctypes_set.py`  |
| POLL (0x02) | query input *to* the receiver            | `qgctypes_poll.py` |

If you're simply streaming and/or parsing the *output* of a QGC receiver, the mode is implicitly GET. If you want to create
or parse an *input* (command or query) message, you must set the mode parameter to SET or POLL. If the parser mode is set to
0x03 (SETPOLL), `pyqgc` will automatically determine the applicable input mode (SET or POLL) based on the message payload.

---
## <a name="reading">Reading (Streaming)</a>

```
class pyqgc.qgcreader.QGCReader(stream, *args, **kwargs)
```

You can create a `QGCReader` object by calling the constructor with an active stream object. 
The stream object can be any viable data stream which supports a `read(n) -> bytes` method (e.g. File or Serial, with 
or without a buffer wrapper). `pyqgc` implements an internal `SocketWrapper` class to allow sockets to be read in the same way as other streams (see example below).

Individual QGC messages can then be read using the `QGCReader.read()` function, which returns both the raw binary data (as bytes) and the parsed data (as a `QGCMessage` object, via the `parse()` method). The function is thread-safe in so far as the incoming data stream object is thread-safe. `QGCReader` also implements an iterator.

The constructor accepts the following optional keyword arguments:

* `protfilter`: `NMEA_PROTOCOL` (1), `QGC_PROTOCOL` (2), `RTCM3_PROTOCOL` (4). Can be OR'd; default is `NMEA_PROTOCOL | QGC_PROTOCOL | RTCM3_PROTOCOL` (7)
* `quitonerror`: `ERR_IGNORE` (0) = ignore errors, `ERR_LOG` (1) = log errors and continue (default), `ERR_RAISE` (2) = (re)raise errors and terminate
* `validate`: `VALCKSUM` (0x01) = validate checksum (default), `VALNONE` (0x00) = ignore invalid checksum or length
* `parsebitfield`: 1 = parse bitfields ('X' type properties) as individual bit flags, where defined (default), 0 = leave bitfields as byte sequences
* `msgmode`: `GET` (0) (default), `SET` (1), `POLL` (2), `SETPOLL` (3) = automatically determine SET or POLL input mode

Example -  Serial input. This example will output both QGC and NMEA messages but not RTCM3:
```python
from serial import Serial
from pyqgc import QGCReader, VALCKSUM, ERR_LOG, NMEA_PROTOCOL, QGC_PROTOCOL
with Serial('/dev/ttyACM0', 115200, timeout=3) as stream:
  qgr = QGCReader(stream, protfilter=QGC_PROTOCOL | NMEA_PROTOCOL, quitonerror=ERR_LOG, validate=VALCKSUM, parsebitfield=1)
  raw_data, parsed_data = qgr.read()
  if parsed_data is not None:
    print(parsed_data)
```
```
<QGC(RAW-PPPB2B, msgver=1, reserved1=0, prn=60, pppstatus=0, msgtype=0, reserved2=0, msgdata=b'\x10\x35\xfc\x49\x04\x40\x01\x3f\x77\x04\x00\x11\x00\x04\x40\x01\x10\x00\x44\x00\x11\x00\x05\x80\x00\x5f\x6b\x84\x00\x11\x00\x07\x7d\x63\x10\x00\x78\x17\x0f\xfd\xd1\x02\x57\x10\x00\x44\x00\x11\x00\x04\x40\x01\x10\x00\x58\x7f\x00\x01\x81\x36\xb0')>
```

Example - File input (using iterator). This will only output QGC data:
```python
from pyqgc import QGCReader, QGC_PROTOCOL
with open('QGCdata.bin', 'rb') as stream:
  qgr = QGCReader(stream, protfilter=QGC_PROTOCOL)
  for raw_data, parsed_data in qg:
    print(parsed_data)
```
```
<QGC(RAW-QZSSL6, msgver=1, reserved1=0, prn=195, rsstatus=1, msgtype=1, reserved2=0, msgdata=b'\x1a\xcf\xfc\x1d\xc3\xa9\x7f\x48\xab\x08\x92\x88\xc0\x3a\xa8\x40\x30\x02\x02\x93\xdf\xdf\xf5\xd5\xde\x43\x1c\x00\x00\x02\x04\x80\x04\x70\x00\x00\x00\x00\x82\x40\x7f\x49\xe8\x11\x08\x04\x7f\xed\x40\x0e\x9f\xe2\x01\x8b\x02\xb1\x02\x5c\x00\x5c\x06\x2f\xb1\x9f\xea\xbf\xea\xbf\xf6\x00\x5d\x07\x7b\xf1\x03\xe8\xa7\xf5\x10\x6e\xdf\xd2\x5a\x04\xa2\x3b\xfd\x0d\xfc\x40\x30\x0e\xfc\x5c\x02\x20\x0b\xc8\xbf\x0b\x03\x98\x0d\x60\x5f\x0a\x80\xd4\x03\x98\xbf\x68\xff\xdf\x03\x82\x87\xd5\x4f\xba\x01\x8c\xd7\xf0\x88\x4b\xfe\xd4\x31\xf4\x34\x08\xa0\x3a\x19\xfc\xe7\xf0\x10\x01\x17\x7c\x3a\xfd\xb8\x23\x04\xbf\xb5\x1f\xf2\xff\xe8\x93\xf7\x4c\x01\xc0\x04\x13\xbe\xd9\x00\x2b\xfe\xa2\x77\xde\xd0\x08\x7f\xd8\x4e\xfa\xbd\xff\x70\x03\x09\xdf\x89\xbf\xfa\x00\xca\x5f\xcd\x1f\xb5\xfd\xcd\x2f\xd1\xb0\x0d\xff\x8e\x97\xbf\x17\xf6\x80\x55\xfd\x29\xa0\x4a\x20\x01\xfe\x80\x28\x00\x05\xc0\xa7\xf3\x00\x15\x9c\xcd\xe1\x8b\xc4\xee\x2d\xe8\x5c\xd1\xf1\x28\xf9\xa2\x81\x83\xdf\xeb\x8e\x1b\x5f\xfe\x18\xf7\xd9\x21\x54\x33\x1c\x5c\x10')>
            
```

Example - Socket input (using iterator). This will output QGC, NMEA and RTCM3 data:
```python
import socket
from pyqgc import QGCReader, NMEA_PROTOCOL, QGC_PROTOCOL, RTCM3_PROTOCOL
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as stream:
  stream.connect(("localhost", 50007))
  qgr = QGCReader(stream, protfilter=NMEA_PROTOCOL | QGC_PROTOCOL | RTCM3_PROTOCOL)
  for raw_data, parsed_data in qgr:
    print(parsed_data)
```
```
<QGC(RAW-HASE6, msgver=1, reserved1=0, prn=34, hasmode=1, msgtype=1, reserved2=0, page=2, reserved3=0, msgdata=b'\x38\xb2\x00\xe8\x50\xe9\xa0\x5e\x7f\xc6\x0d\x00\x31\xff\x2e\x00\x00\x5b\xfe\x50\x2c\xc0\xe1\x00\x00\x2f\x77\xe0\x0b\x20\xc6\xe5\x3f\x49\x79\xf0\x10\x50\x11\xf8\xcb\xeb\x7f\x31\x04\x67\xd0\x80\xf2\x05\xc0\x0e\x81\xb2\x00\xe8\x50\xe9\xa0\x5e\x7f\xc6\x0d\x00\x31\xff\x2e\x00\x00\x5b\xfe\x50\x2c\xc0\xe1\x00\x00\x2f\x77\xe0\x0b\x20\xc6\xe5\x3f\x49\x79\xf0\x10\x50\x11\xf8\xcb\xeb\x7f\x31\x04\x67\xd0\x80\xf2\x05\xc0\x0e\x81\xc8')>
```

---
## <a name="parsing">Parsing</a>

You can parse individual QGC messages using the static `QGCReader.parse(data)` function, which takes a bytes array containing a binary QGC message and returns a `QGCMessage` object.

**NB:** Once instantiated, a `QGCMessage` object is immutable.

The `parse()` method accepts the following optional keyword arguments:

* `validate`: VALCKSUM (0x01) = validate checksum (default), VALNONE (0x00) = ignore invalid checksum or length
* `parsebitfield`: 1 = parse bitfields ('X' type properties) as individual bit flags, where defined (default), 0 = leave bitfields as byte sequences

Example - output message:
```python
from pyqgc import QGCReader
msg = QGCReader.parse(b'QG\n\xb2U\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x105\xfcI\x04@\x01?w\x04\x00\x11\x00\x04@\x01\x10\x00D\x00\x11\x00\x05\x80\x00_k\x84\x00\x11\x00\x07}c\x10\x00x\x17\x0f\xfd\xd1\x02W\x10\x00D\x00\x11\x00\x04@\x01\x10\x00X\x7f\x00\x01\x816\xb0\xee\xb1')
print(msg)
```
```
<QGC(RAW-PPPB2B, msgver=0, reserved1=0, prn=0, pppstatus=0, msgtype=0, reserved2=0, msgdata=b'\x10\x35\xfc\x49\x04\x40\x01\x3f\x77\x04\x00\x11\x00\x04\x40\x01\x10\x00\x44\x00\x11\x00\x05\x80\x00\x5f\x6b\x84\x00\x11\x00\x07\x7d\x63\x10\x00\x78\x17\x0f\xfd\xd1\x02\x57\x10\x00\x44\x00\x11\x00\x04\x40\x01\x10\x00\x58\x7f\x00\x01\x81\x36\xb0')>
```

The `QGCMessage` object exposes different public attributes depending on its message type or 'identity',
e.g. the `RAW-PPPB2B` message has the following attributes:

```python
print(msg)
print(msg.identity)
print(msg.pppstatus)
```
```
<QGC(RAW-PPPB2B, msgver=1, reserved1=0, prn=60, pppstatus=0, msgtype=0, reserved2=0, msgdata=b'\x10\x35\xfc\x49\x04\x40\x01\x3f\x77\x04\x00\x11\x00\x04\x40\x01\x10\x00\x44\x00\x11\x00\x05\x80\x00\x5f\x6b\x84\x00\x11\x00\x07\x7d\x63\x10\x00\x78\x17\x0f\xfd\xd1\x02\x57\x10\x00\x44\x00\x11\x00\x04\x40\x01\x10\x00\x58\x7f\x00\x01\x81\x36\xb0')>
RAW-PPPB2B
0
```

The `payload` attribute always contains the raw payload as bytes. Attributes within repeating groups are parsed with a two-digit suffix (svid_01, svid_02, etc.).

---
## <a name="generating">Generating</a>

```
class pyqgc.qgcmessage.QGCMessage(msggrp, msgid, **kwargs)
```

You can create a `QGCMessage` object by calling the constructor with the following parameters:
1. message group (must be a valid group from `pyqgc.QGC_MSGIDS`)
2. message id (must be a valid id from `pqgc.QGC_MSGIDS`)
3. (optional) a series of keyword parameters representing the message payload
4. (optional) `parsebitfield` keyword - 1 = define bitfields as individual bits (default), 0 = define bitfields as byte sequences

The 'message group' and 'message id' parameters must be passed as bytes.

The message payload can be defined via keyword arguments in one of three ways:
1. A single keyword argument of `payload` containing the full payload as a sequence of bytes (any other keyword arguments will be ignored). **NB** the `payload` keyword argument *must* be used for message types which have a 'variable by size' repeating group.
2. One or more keyword arguments corresponding to individual message attributes. Any attributes not explicitly provided as keyword arguments will be set to a nominal value according to their type.
3. If no keyword arguments are passed, the payload is assumed to be null.

Example - to generate a RAW-PPPB2B command (*msggrp 0x0a, msgid 0xb2*) from individual keyword arguments:

```python
from pyqgc import QGCMessage
msg = QGCMessage(
    b"\x0a",
    b"\xb2",
    parsebitfield=1,
    msgver=1,
    prn=60,
    pppstatus=0,
    msgtype=0,
    msgdata=b"\x10\x35\xfc\x49\x04\x40\x01\x3f\x77\x04\x00\x11\x00\x04\x40\x01\x10\x00\x44\x00\x11\x00\x05\x80\x00\x5f\x6b\x84\x00\x11\x00\x07\x7d\x63\x10\x00\x78\x17\x0f\xfd\xd1\x02\x57\x10\x00\x44\x00\x11\x00\x04\x40\x01\x10\x00\x58\x7f\x00\x01\x81\x36\xb0",
)
print(msg)
```
```
<QGC(RAW-PPPB2B, msgver=1, reserved1=0, prn=60, pppstatus=0, msgtype=0, reserved2=0, msgdata=b'\\x10\\x35\\xfc\\x49\\x04\\x40\\x01\\x3f\\x77\\x04\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x44\\x00\\x11\\x00\\x05\\x80\\x00\\x5f\\x6b\\x84\\x00\\x11\\x00\\x07\\x7d\\x63\\x10\\x00\\x78\\x17\\x0f\\xfd\\xd1\\x02\\x57\\x10\\x00\\x44\\x00\\x11\\x00\\x04\\x40\\x01\\x10\\x00\\x58\\x7f\\x00\\x01\\x81\\x36\\xb0')>
        
```

---
## <a name="serializing">Serializing</a>

The `QGCMessage` class implements a `serialize()` method to convert a `QGCMessage` object to a bytes array suitable for writing to an output stream.

e.g. to create and send a `RAW-PPPB2B` message:

```python
from serial import Serial
from pyqgc import QGCMessage
serialOut = Serial('COM7', 115200, timeout=5)
print(msg)
output = msg.serialize()
print(output)
serialOut.write(output)
```
```
<QGC(RAW-PPPB2B, msgver=0, reserved1=0, prn=0, pppstatus=0, msgtype=0, reserved2=0, msgdata=b'\x10\x35\xfc\x49\x04\x40\x01\x3f\x77\x04\x00\x11\x00\x04\x40\x01\x10\x00\x44\x00\x11\x00\x05\x80\x00\x5f\x6b\x84\x00\x11\x00\x07\x7d\x63\x10\x00\x78\x17\x0f\xfd\xd1\x02\x57\x10\x00\x44\x00\x11\x00\x04\x40\x01\x10\x00\x58\x7f\x00\x01\x81\x36\xb0')>
b'QG\n\xb2U\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x105\xfcI\x04@\x01?w\x04\x00\x11\x00\x04@\x01\x10\x00D\x00\x11\x00\x05\x80\x00_k\x84\x00\x11\x00\x07}c\x10\x00x\x17\x0f\xfd\xd1\x02W\x10\x00D\x00\x11\x00\x04@\x01\x10\x00X\x7f\x00\x01\x816\xb0\xee\xb1'
```

---
## <a name="examples">Examples</a>

The following command line examples can be found in the `\examples` folder:

1. `qgcusage.py` illustrates basic usage of the `QGCMessage` and `QGCReader` classes.

---
## <a name="extensibility">Extensibility</a>

The QGC protocol is principally defined in the modules `QGCtypes_*.py` as a series of dictionaries. Message payload definitions must conform to the following rules:

```
1. attribute names must be unique within each message class
2. attribute types must be one of the valid types (S1, U2, X4, etc.)
3. if the attribute is scaled, attribute type is list of [attribute type as string (S1, U2, etc.), scaling factor as float] e.g. {"lat": [I4, 1e-7]}
4. repeating or bitfield groups must be defined as a tuple ('numr', {dict}), where:
   'numr' is either:
     a. an integer representing a fixed number of repeats e.g. 32
     b. a string representing the name of a preceding attribute containing the number of repeats e.g. 'numCh'
     c. an 'X' attribute type ('X1', 'X2', 'X4', etc) representing a group of individual bit flags
     d. 'None' for a 'variable by size' repeating group. Only one such group is permitted per payload and it must be at the end.
   {dict} is the nested dictionary of repeating items or bitfield group
```

Repeating attribute names are parsed with a two-digit suffix (svid_01, svid_02, etc.). Nested repeating groups are supported.

---
## <a name="troubleshoot">Troubleshooting</a>

#### 1. `UnicodeDecode` errors.
- If reading QGC data from a log file, check that the file.open() procedure is using the `rb` (read binary) setting e.g.
`stream = open('QGCdata.log', 'rb')`.

---
## <a name="author">Author & License Information</a>

semuadmin@semuconsulting.com

![License](https://img.shields.io/github/license/semuconsulting/pyqgc.svg)

`pyqgc` is maintained entirely by unpaid volunteers. It receives no funding from advertising or corporate sponsorship. If you find the utility useful, please consider sponsoring the project with the price of a coffee...

[![Sponsor](https://github.com/semuconsulting/pyubx2/blob/master/images/sponsor.png?raw=true)](https://buymeacoffee.com/semuconsulting)

[![Freedom for Ukraine](https://github.com/semuadmin/sandpit/blob/main/src/semuadmin_sandpit/resources/ukraine200.jpg?raw=true)](https://u24.gov.ua/)
