:py:mod:`simplemseed`
=====================

.. py:module:: simplemseed

.. autodoc2-docstring:: simplemseed
   :allowtitles:

Package Contents
----------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`FDSNSourceId <simplemseed.fdsnsourceid.FDSNSourceId>`
     - .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId
          :summary:
   * - :py:obj:`LocationSourceId <simplemseed.fdsnsourceid.LocationSourceId>`
     - .. autodoc2-docstring:: simplemseed.fdsnsourceid.LocationSourceId
          :summary:
   * - :py:obj:`MSeed3Header <simplemseed.mseed3.MSeed3Header>`
     - .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header
          :summary:
   * - :py:obj:`MSeed3Record <simplemseed.mseed3.MSeed3Record>`
     - .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record
          :summary:
   * - :py:obj:`MiniseedHeader <simplemseed.miniseed.MiniseedHeader>`
     - .. autodoc2-docstring:: simplemseed.miniseed.MiniseedHeader
          :summary:
   * - :py:obj:`MiniseedRecord <simplemseed.miniseed.MiniseedRecord>`
     - .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord
          :summary:
   * - :py:obj:`NetworkSourceId <simplemseed.fdsnsourceid.NetworkSourceId>`
     - .. autodoc2-docstring:: simplemseed.fdsnsourceid.NetworkSourceId
          :summary:
   * - :py:obj:`NslcId <simplemseed.fdsnsourceid.NslcId>`
     - .. autodoc2-docstring:: simplemseed.fdsnsourceid.NslcId
          :summary:
   * - :py:obj:`StationSourceId <simplemseed.fdsnsourceid.StationSourceId>`
     - .. autodoc2-docstring:: simplemseed.fdsnsourceid.StationSourceId
          :summary:
   * - :py:obj:`SteimFrameBlock <simplemseed.steimframeblock.SteimFrameBlock>`
     - .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock
          :summary:

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`bandCodeDescribe <simplemseed.fdsnsourceid.bandCodeDescribe>`
     - .. autodoc2-docstring:: simplemseed.fdsnsourceid.bandCodeDescribe
          :summary:
   * - :py:obj:`bandCodeForRate <simplemseed.fdsnsourceid.bandCodeForRate>`
     - .. autodoc2-docstring:: simplemseed.fdsnsourceid.bandCodeForRate
          :summary:
   * - :py:obj:`canDecompress <simplemseed.seedcodec.canDecompress>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.canDecompress
          :summary:
   * - :py:obj:`crcAsHex <simplemseed.mseed3.crcAsHex>`
     - .. autodoc2-docstring:: simplemseed.mseed3.crcAsHex
          :summary:
   * - :py:obj:`decodeSteim1 <simplemseed.steim1.decodeSteim1>`
     - .. autodoc2-docstring:: simplemseed.steim1.decodeSteim1
          :summary:
   * - :py:obj:`decodeSteim2 <simplemseed.steim2.decodeSteim2>`
     - .. autodoc2-docstring:: simplemseed.steim2.decodeSteim2
          :summary:
   * - :py:obj:`decompress <simplemseed.seedcodec.decompress>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.decompress
          :summary:
   * - :py:obj:`encode <simplemseed.seedcodec.encode>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.encode
          :summary:
   * - :py:obj:`encodeSteim1 <simplemseed.steim1.encodeSteim1>`
     - .. autodoc2-docstring:: simplemseed.steim1.encodeSteim1
          :summary:
   * - :py:obj:`encodeSteim1FrameBlock <simplemseed.steim1.encodeSteim1FrameBlock>`
     - .. autodoc2-docstring:: simplemseed.steim1.encodeSteim1FrameBlock
          :summary:
   * - :py:obj:`encodeSteim2 <simplemseed.steim2.encodeSteim2>`
     - .. autodoc2-docstring:: simplemseed.steim2.encodeSteim2
          :summary:
   * - :py:obj:`encodeSteim2FrameBlock <simplemseed.steim2.encodeSteim2FrameBlock>`
     - .. autodoc2-docstring:: simplemseed.steim2.encodeSteim2FrameBlock
          :summary:
   * - :py:obj:`encodingName <simplemseed.seedcodec.encodingName>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.encodingName
          :summary:
   * - :py:obj:`isPrimitiveCompression <simplemseed.seedcodec.isPrimitiveCompression>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.isPrimitiveCompression
          :summary:
   * - :py:obj:`isoWZ <simplemseed.util.isoWZ>`
     - .. autodoc2-docstring:: simplemseed.util.isoWZ
          :summary:
   * - :py:obj:`readMSeed3Records <simplemseed.mseed3.readMSeed3Records>`
     - .. autodoc2-docstring:: simplemseed.mseed3.readMSeed3Records
          :summary:
   * - :py:obj:`readMiniseed2Records <simplemseed.miniseed.readMiniseed2Records>`
     - .. autodoc2-docstring:: simplemseed.miniseed.readMiniseed2Records
          :summary:
   * - :py:obj:`sourceCodeDescribe <simplemseed.fdsnsourceid.sourceCodeDescribe>`
     - .. autodoc2-docstring:: simplemseed.fdsnsourceid.sourceCodeDescribe
          :summary:
   * - :py:obj:`unpackBlockette <simplemseed.miniseed.unpackBlockette>`
     - .. autodoc2-docstring:: simplemseed.miniseed.unpackBlockette
          :summary:
   * - :py:obj:`unpackMSeed3FixedHeader <simplemseed.mseed3.unpackMSeed3FixedHeader>`
     - .. autodoc2-docstring:: simplemseed.mseed3.unpackMSeed3FixedHeader
          :summary:
   * - :py:obj:`unpackMSeed3Record <simplemseed.mseed3.unpackMSeed3Record>`
     - .. autodoc2-docstring:: simplemseed.mseed3.unpackMSeed3Record
          :summary:
   * - :py:obj:`unpackMiniseedHeader <simplemseed.miniseed.unpackMiniseedHeader>`
     - .. autodoc2-docstring:: simplemseed.miniseed.unpackMiniseedHeader
          :summary:
   * - :py:obj:`unpackMiniseedRecord <simplemseed.miniseed.unpackMiniseedRecord>`
     - .. autodoc2-docstring:: simplemseed.miniseed.unpackMiniseedRecord
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`BIG_ENDIAN <simplemseed.seedcodec.BIG_ENDIAN>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.BIG_ENDIAN
          :summary:
   * - :py:obj:`CRC_OFFSET <simplemseed.mseed3.CRC_OFFSET>`
     - .. autodoc2-docstring:: simplemseed.mseed3.CRC_OFFSET
          :summary:
   * - :py:obj:`FDSN_PREFIX <simplemseed.fdsnsourceid.FDSN_PREFIX>`
     - .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSN_PREFIX
          :summary:
   * - :py:obj:`FIXED_HEADER_SIZE <simplemseed.mseed3.FIXED_HEADER_SIZE>`
     - .. autodoc2-docstring:: simplemseed.mseed3.FIXED_HEADER_SIZE
          :summary:
   * - :py:obj:`LITTLE_ENDIAN <simplemseed.seedcodec.LITTLE_ENDIAN>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.LITTLE_ENDIAN
          :summary:
   * - :py:obj:`SINGLE_STATION_NETCODE <simplemseed.fdsnsourceid.SINGLE_STATION_NETCODE>`
     - .. autodoc2-docstring:: simplemseed.fdsnsourceid.SINGLE_STATION_NETCODE
          :summary:
   * - :py:obj:`STEIM1 <simplemseed.seedcodec.STEIM1>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.STEIM1
          :summary:
   * - :py:obj:`STEIM2 <simplemseed.seedcodec.STEIM2>`
     - .. autodoc2-docstring:: simplemseed.seedcodec.STEIM2
          :summary:
   * - :py:obj:`TESTDATA_NETCODE <simplemseed.fdsnsourceid.TESTDATA_NETCODE>`
     - .. autodoc2-docstring:: simplemseed.fdsnsourceid.TESTDATA_NETCODE
          :summary:
   * - :py:obj:`VERSION <simplemseed.version.VERSION>`
     - .. autodoc2-docstring:: simplemseed.version.VERSION
          :summary:

API
~~~

.. py:data:: BIG_ENDIAN
   :canonical: simplemseed.seedcodec.BIG_ENDIAN
   :value: 1

   .. autodoc2-docstring:: simplemseed.seedcodec.BIG_ENDIAN

.. py:data:: CRC_OFFSET
   :canonical: simplemseed.mseed3.CRC_OFFSET
   :value: 28

   .. autodoc2-docstring:: simplemseed.mseed3.CRC_OFFSET

.. py:exception:: CodecException(message)
   :canonical: simplemseed.exceptions.CodecException

   Bases: :py:obj:`Exception`

.. py:class:: FDSNSourceId(networkCode: typing.Union[str, simplemseed.fdsnsourceid.NetworkSourceId], stationCode: str, locationCode: str, bandCode: str, sourceCode: str, subsourceCode: str)
   :canonical: simplemseed.fdsnsourceid.FDSNSourceId

   .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId

   .. rubric:: Initialization

   .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.__init__

   .. py:attribute:: SPECIFICATION_URL
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.SPECIFICATION_URL
      :value: 'http://docs.fdsn.org/projects/source-identifiers/en/v1.0'

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.SPECIFICATION_URL

   .. py:attribute:: SPECIFICATION_VERSION
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.SPECIFICATION_VERSION
      :value: '1.0'

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.SPECIFICATION_VERSION

   .. py:method:: asNslc() -> simplemseed.fdsnsourceid.NslcId
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.asNslc

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.asNslc

   .. py:attribute:: bandCode
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.bandCode
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.bandCode

   .. py:method:: createUnknown(sampRate: typing.Optional[typing.Union[float, int]] = None, sourceCode: str = 'H', response_lb: typing.Optional[typing.Union[float, int]] = None, networkCode: str = TESTDATA_NETCODE, stationCode: str = 'ABC', locationCode: str = '', subsourceCode: str = 'U') -> simplemseed.fdsnsourceid.FDSNSourceId
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.createUnknown
      :staticmethod:

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.createUnknown

   .. py:method:: fromNslc(net: str, sta: str, loc: str, channelCode: str, startYear: str | int | None = None) -> simplemseed.fdsnsourceid.FDSNSourceId
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.fromNslc
      :staticmethod:

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.fromNslc

   .. py:attribute:: locationCode
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.locationCode
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.locationCode

   .. py:method:: locationSourceId() -> simplemseed.fdsnsourceid.LocationSourceId
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.locationSourceId

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.locationSourceId

   .. py:attribute:: networkCode
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.networkCode
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.networkCode

   .. py:method:: networkSourceId() -> simplemseed.fdsnsourceid.NetworkSourceId
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.networkSourceId

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.networkSourceId

   .. py:method:: parse(sid: str) -> typing.Union[simplemseed.fdsnsourceid.FDSNSourceId, simplemseed.fdsnsourceid.NetworkSourceId, simplemseed.fdsnsourceid.StationSourceId, simplemseed.fdsnsourceid.LocationSourceId]
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.parse
      :staticmethod:

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.parse

   .. py:method:: parseNslc(nslc: str, sep='.', startYear: str | int | None = None) -> simplemseed.fdsnsourceid.FDSNSourceId
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.parseNslc
      :staticmethod:

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.parseNslc

   .. py:method:: shortChannelCode() -> str
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.shortChannelCode

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.shortChannelCode

   .. py:attribute:: sourceCode
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.sourceCode
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.sourceCode

   .. py:attribute:: stationCode
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.stationCode
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.stationCode

   .. py:method:: stationSourceId() -> simplemseed.fdsnsourceid.StationSourceId
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.stationSourceId

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.stationSourceId

   .. py:attribute:: subsourceCode
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.subsourceCode
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.subsourceCode

   .. py:method:: validate() -> (bool, typing.Union[str, None])
      :canonical: simplemseed.fdsnsourceid.FDSNSourceId.validate

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSNSourceId.validate

.. py:data:: FDSN_PREFIX
   :canonical: simplemseed.fdsnsourceid.FDSN_PREFIX
   :value: 'FDSN:'

   .. autodoc2-docstring:: simplemseed.fdsnsourceid.FDSN_PREFIX

.. py:data:: FIXED_HEADER_SIZE
   :canonical: simplemseed.mseed3.FIXED_HEADER_SIZE
   :value: 40

   .. autodoc2-docstring:: simplemseed.mseed3.FIXED_HEADER_SIZE

.. py:data:: LITTLE_ENDIAN
   :canonical: simplemseed.seedcodec.LITTLE_ENDIAN
   :value: 0

   .. autodoc2-docstring:: simplemseed.seedcodec.LITTLE_ENDIAN

.. py:class:: LocationSourceId(networkCode: typing.Union[str, simplemseed.fdsnsourceid.NetworkSourceId], stationCode: str, locationCode: str)
   :canonical: simplemseed.fdsnsourceid.LocationSourceId

   .. autodoc2-docstring:: simplemseed.fdsnsourceid.LocationSourceId

   .. rubric:: Initialization

   .. autodoc2-docstring:: simplemseed.fdsnsourceid.LocationSourceId.__init__

   .. py:method:: createFDSNSourceId(bandCode: str, sourceCode: str, subsourceCode: str) -> simplemseed.fdsnsourceid.FDSNSourceId
      :canonical: simplemseed.fdsnsourceid.LocationSourceId.createFDSNSourceId

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.LocationSourceId.createFDSNSourceId

   .. py:attribute:: locationCode
      :canonical: simplemseed.fdsnsourceid.LocationSourceId.locationCode
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.LocationSourceId.locationCode

   .. py:attribute:: networkCode
      :canonical: simplemseed.fdsnsourceid.LocationSourceId.networkCode
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.LocationSourceId.networkCode

   .. py:method:: networkSourceId() -> simplemseed.fdsnsourceid.NetworkSourceId
      :canonical: simplemseed.fdsnsourceid.LocationSourceId.networkSourceId

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.LocationSourceId.networkSourceId

   .. py:attribute:: stationCode
      :canonical: simplemseed.fdsnsourceid.LocationSourceId.stationCode
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.LocationSourceId.stationCode

   .. py:method:: stationSourceId() -> simplemseed.fdsnsourceid.StationSourceId
      :canonical: simplemseed.fdsnsourceid.LocationSourceId.stationSourceId

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.LocationSourceId.stationSourceId

   .. py:method:: validate() -> (bool, typing.Union[str, None])
      :canonical: simplemseed.fdsnsourceid.LocationSourceId.validate

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.LocationSourceId.validate

.. py:class:: MSeed3Header()
   :canonical: simplemseed.mseed3.MSeed3Header

   .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header

   .. rubric:: Initialization

   .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.__init__

   .. py:method:: clone()
      :canonical: simplemseed.mseed3.MSeed3Header.clone

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.clone

   .. py:attribute:: crc
      :canonical: simplemseed.mseed3.MSeed3Header.crc
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.crc

   .. py:method:: crcAsHex()
      :canonical: simplemseed.mseed3.MSeed3Header.crcAsHex

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.crcAsHex

   .. py:attribute:: dataLength
      :canonical: simplemseed.mseed3.MSeed3Header.dataLength
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.dataLength

   .. py:attribute:: dayOfYear
      :canonical: simplemseed.mseed3.MSeed3Header.dayOfYear
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.dayOfYear

   .. py:attribute:: encoding
      :canonical: simplemseed.mseed3.MSeed3Header.encoding
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.encoding

   .. py:property:: endtime
      :canonical: simplemseed.mseed3.MSeed3Header.endtime

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.endtime

   .. py:attribute:: extraHeadersLength
      :canonical: simplemseed.mseed3.MSeed3Header.extraHeadersLength
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.extraHeadersLength

   .. py:attribute:: flags
      :canonical: simplemseed.mseed3.MSeed3Header.flags
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.flags

   .. py:attribute:: formatVersion
      :canonical: simplemseed.mseed3.MSeed3Header.formatVersion
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.formatVersion

   .. py:attribute:: hour
      :canonical: simplemseed.mseed3.MSeed3Header.hour
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.hour

   .. py:attribute:: identifierLength
      :canonical: simplemseed.mseed3.MSeed3Header.identifierLength
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.identifierLength

   .. py:attribute:: minute
      :canonical: simplemseed.mseed3.MSeed3Header.minute
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.minute

   .. py:attribute:: nanosecond
      :canonical: simplemseed.mseed3.MSeed3Header.nanosecond
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.nanosecond

   .. py:attribute:: numSamples
      :canonical: simplemseed.mseed3.MSeed3Header.numSamples
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.numSamples

   .. py:method:: pack()
      :canonical: simplemseed.mseed3.MSeed3Header.pack

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.pack

   .. py:attribute:: publicationVersion
      :canonical: simplemseed.mseed3.MSeed3Header.publicationVersion
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.publicationVersion

   .. py:attribute:: recordIndicator
      :canonical: simplemseed.mseed3.MSeed3Header.recordIndicator
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.recordIndicator

   .. py:method:: recordSize()
      :canonical: simplemseed.mseed3.MSeed3Header.recordSize

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.recordSize

   .. py:property:: samplePeriod
      :canonical: simplemseed.mseed3.MSeed3Header.samplePeriod

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.samplePeriod

   .. py:property:: sampleRate
      :canonical: simplemseed.mseed3.MSeed3Header.sampleRate

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.sampleRate

   .. py:attribute:: sampleRatePeriod
      :canonical: simplemseed.mseed3.MSeed3Header.sampleRatePeriod
      :type: float
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.sampleRatePeriod

   .. py:method:: sanityCheck()
      :canonical: simplemseed.mseed3.MSeed3Header.sanityCheck

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.sanityCheck

   .. py:attribute:: second
      :canonical: simplemseed.mseed3.MSeed3Header.second
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.second

   .. py:property:: starttime
      :canonical: simplemseed.mseed3.MSeed3Header.starttime

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.starttime

   .. py:attribute:: year
      :canonical: simplemseed.mseed3.MSeed3Header.year
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header.year

.. py:class:: MSeed3Record(header: simplemseed.mseed3.MSeed3Header, identifier: typing.Union[simplemseed.fdsnsourceid.FDSNSourceId, str], data: typing.Union[numpy.ndarray, bytes, bytearray, array.array, list[int], list[float]], extraHeaders: typing.Union[str, dict, None] = None)
   :canonical: simplemseed.mseed3.MSeed3Record

   .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record

   .. rubric:: Initialization

   .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.__init__

   .. py:method:: clone()
      :canonical: simplemseed.mseed3.MSeed3Record.clone

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.clone

   .. py:method:: decompress() -> numpy.ndarray
      :canonical: simplemseed.mseed3.MSeed3Record.decompress

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.decompress

   .. py:method:: decompressedRecord()
      :canonical: simplemseed.mseed3.MSeed3Record.decompressedRecord

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.decompressedRecord

   .. py:method:: details(showExtraHeaders=True, showData=False)
      :canonical: simplemseed.mseed3.MSeed3Record.details

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.details

   .. py:property:: eh
      :canonical: simplemseed.mseed3.MSeed3Record.eh

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.eh

   .. py:method:: encodedDataBytes()
      :canonical: simplemseed.mseed3.MSeed3Record.encodedDataBytes

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.encodedDataBytes

   .. py:method:: encodingName()
      :canonical: simplemseed.mseed3.MSeed3Record.encodingName

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.encodingName

   .. py:property:: endtime
      :canonical: simplemseed.mseed3.MSeed3Record.endtime

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.endtime

   .. py:method:: getSize()
      :canonical: simplemseed.mseed3.MSeed3Record.getSize

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.getSize

   .. py:method:: hasExtraHeaders()
      :canonical: simplemseed.mseed3.MSeed3Record.hasExtraHeaders

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.hasExtraHeaders

   .. py:attribute:: header
      :canonical: simplemseed.mseed3.MSeed3Record.header
      :type: simplemseed.mseed3.MSeed3Header
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.header

   .. py:attribute:: identifier
      :canonical: simplemseed.mseed3.MSeed3Record.identifier
      :type: typing.Union[simplemseed.fdsnsourceid.FDSNSourceId, str]
      :value: None

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.identifier

   .. py:method:: pack()
      :canonical: simplemseed.mseed3.MSeed3Record.pack

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.pack

   .. py:method:: parseIdentifier() -> simplemseed.fdsnsourceid.FDSNSourceId
      :canonical: simplemseed.mseed3.MSeed3Record.parseIdentifier

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.parseIdentifier

   .. py:property:: starttime
      :canonical: simplemseed.mseed3.MSeed3Record.starttime

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.starttime

   .. py:method:: summary()
      :canonical: simplemseed.mseed3.MSeed3Record.summary

      .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record.summary

.. py:exception:: Miniseed3Exception()
   :canonical: simplemseed.mseed3.Miniseed3Exception

   Bases: :py:obj:`Exception`

   .. autodoc2-docstring:: simplemseed.mseed3.Miniseed3Exception

   .. rubric:: Initialization

   .. autodoc2-docstring:: simplemseed.mseed3.Miniseed3Exception.__init__

.. py:exception:: MiniseedException()
   :canonical: simplemseed.miniseed.MiniseedException

   Bases: :py:obj:`Exception`

.. py:class:: MiniseedHeader(network, station, location, channel, starttime, numSamples, sampleRate, encoding=-1, byteorder=BIG_ENDIAN, sampRateFactor=0, sampRateMult=0, actFlag=0, ioFlag=0, qualFlag=0, numBlockettes=0, timeCorr=0, dataOffset=0, blocketteOffset=0, sequence_number=0, dataquality='D')
   :canonical: simplemseed.miniseed.MiniseedHeader

   .. autodoc2-docstring:: simplemseed.miniseed.MiniseedHeader

   .. rubric:: Initialization

   .. autodoc2-docstring:: simplemseed.miniseed.MiniseedHeader.__init__

   .. py:method:: calcSeedMultipilerFactor()
      :canonical: simplemseed.miniseed.MiniseedHeader.calcSeedMultipilerFactor

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedHeader.calcSeedMultipilerFactor

   .. py:method:: codes(sep='.')
      :canonical: simplemseed.miniseed.MiniseedHeader.codes

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedHeader.codes

   .. py:method:: fdsnSourceId()
      :canonical: simplemseed.miniseed.MiniseedHeader.fdsnSourceId

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedHeader.fdsnSourceId

   .. py:method:: pack()
      :canonical: simplemseed.miniseed.MiniseedHeader.pack

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedHeader.pack

   .. py:method:: packBTime(header, time)
      :canonical: simplemseed.miniseed.MiniseedHeader.packBTime

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedHeader.packBTime

   .. py:method:: setSampleRate(sampleRate)
      :canonical: simplemseed.miniseed.MiniseedHeader.setSampleRate

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedHeader.setSampleRate

   .. py:method:: setStartTime(starttime)
      :canonical: simplemseed.miniseed.MiniseedHeader.setStartTime

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedHeader.setStartTime

.. py:class:: MiniseedRecord(header: simplemseed.miniseed.MiniseedHeader, data, encodedDataBytes=None, blockettes=None)
   :canonical: simplemseed.miniseed.MiniseedRecord

   .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord

   .. rubric:: Initialization

   .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.__init__

   .. py:method:: clone()
      :canonical: simplemseed.miniseed.MiniseedRecord.clone

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.clone

   .. py:method:: codes(sep='.')
      :canonical: simplemseed.miniseed.MiniseedRecord.codes

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.codes

   .. py:method:: createB100()
      :canonical: simplemseed.miniseed.MiniseedRecord.createB100

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.createB100

   .. py:method:: createB1000()
      :canonical: simplemseed.miniseed.MiniseedRecord.createB1000

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.createB1000

   .. py:method:: createB1001()
      :canonical: simplemseed.miniseed.MiniseedRecord.createB1001

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.createB1001

   .. py:method:: decompress()
      :canonical: simplemseed.miniseed.MiniseedRecord.decompress

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.decompress

   .. py:method:: decompressed()
      :canonical: simplemseed.miniseed.MiniseedRecord.decompressed

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.decompressed

   .. py:method:: details(showData=False)
      :canonical: simplemseed.miniseed.MiniseedRecord.details

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.details

   .. py:method:: endtime()
      :canonical: simplemseed.miniseed.MiniseedRecord.endtime

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.endtime

   .. py:property:: identifier
      :canonical: simplemseed.miniseed.MiniseedRecord.identifier

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.identifier

   .. py:method:: next_starttime()
      :canonical: simplemseed.miniseed.MiniseedRecord.next_starttime

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.next_starttime

   .. py:method:: pack()
      :canonical: simplemseed.miniseed.MiniseedRecord.pack

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.pack

   .. py:method:: packB100(recordBytes, offset, b)
      :canonical: simplemseed.miniseed.MiniseedRecord.packB100

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.packB100

   .. py:method:: packB1000(recordBytes, offset, b)
      :canonical: simplemseed.miniseed.MiniseedRecord.packB1000

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.packB1000

   .. py:method:: packB1001(recordBytes, offset, b)
      :canonical: simplemseed.miniseed.MiniseedRecord.packB1001

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.packB1001

   .. py:method:: packBlockette(recordBytes, offset, b)
      :canonical: simplemseed.miniseed.MiniseedRecord.packBlockette

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.packBlockette

   .. py:method:: packBlocketteUnknown(recordBytes, offset, bUnk)
      :canonical: simplemseed.miniseed.MiniseedRecord.packBlocketteUnknown

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.packBlocketteUnknown

   .. py:method:: packData(recordBytes, offset, data)
      :canonical: simplemseed.miniseed.MiniseedRecord.packData

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.packData

   .. py:method:: starttime()
      :canonical: simplemseed.miniseed.MiniseedRecord.starttime

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.starttime

   .. py:method:: summary()
      :canonical: simplemseed.miniseed.MiniseedRecord.summary

      .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord.summary

.. py:class:: NetworkSourceId(networkCode: str, startYear: str | int | None = None)
   :canonical: simplemseed.fdsnsourceid.NetworkSourceId

   .. autodoc2-docstring:: simplemseed.fdsnsourceid.NetworkSourceId

   .. rubric:: Initialization

   .. autodoc2-docstring:: simplemseed.fdsnsourceid.NetworkSourceId.__init__

   .. py:method:: createStationSourceId(stationCode) -> simplemseed.fdsnsourceid.StationSourceId
      :canonical: simplemseed.fdsnsourceid.NetworkSourceId.createStationSourceId

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.NetworkSourceId.createStationSourceId

   .. py:method:: isSeedTempNet() -> bool
      :canonical: simplemseed.fdsnsourceid.NetworkSourceId.isSeedTempNet

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.NetworkSourceId.isSeedTempNet

   .. py:method:: isTempNetConvention() -> bool
      :canonical: simplemseed.fdsnsourceid.NetworkSourceId.isTempNetConvention

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.NetworkSourceId.isTempNetConvention

   .. py:method:: isTempNetHistorical() -> bool
      :canonical: simplemseed.fdsnsourceid.NetworkSourceId.isTempNetHistorical

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.NetworkSourceId.isTempNetHistorical

   .. py:method:: isTemporary() -> bool
      :canonical: simplemseed.fdsnsourceid.NetworkSourceId.isTemporary

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.NetworkSourceId.isTemporary

   .. py:attribute:: networkCode
      :canonical: simplemseed.fdsnsourceid.NetworkSourceId.networkCode
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.NetworkSourceId.networkCode

   .. py:method:: validate() -> (bool, typing.Union[str, None])
      :canonical: simplemseed.fdsnsourceid.NetworkSourceId.validate

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.NetworkSourceId.validate

.. py:class:: NslcId(net: str, sta: str, loc: str, chan: str)
   :canonical: simplemseed.fdsnsourceid.NslcId

   .. autodoc2-docstring:: simplemseed.fdsnsourceid.NslcId

   .. rubric:: Initialization

   .. autodoc2-docstring:: simplemseed.fdsnsourceid.NslcId.__init__

   .. py:attribute:: channelCode
      :canonical: simplemseed.fdsnsourceid.NslcId.channelCode
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.NslcId.channelCode

   .. py:attribute:: locationCode
      :canonical: simplemseed.fdsnsourceid.NslcId.locationCode
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.NslcId.locationCode

   .. py:attribute:: networkCode
      :canonical: simplemseed.fdsnsourceid.NslcId.networkCode
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.NslcId.networkCode

   .. py:attribute:: stationCode
      :canonical: simplemseed.fdsnsourceid.NslcId.stationCode
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.NslcId.stationCode

.. py:data:: SINGLE_STATION_NETCODE
   :canonical: simplemseed.fdsnsourceid.SINGLE_STATION_NETCODE
   :value: 'SS'

   .. autodoc2-docstring:: simplemseed.fdsnsourceid.SINGLE_STATION_NETCODE

.. py:data:: STEIM1
   :canonical: simplemseed.seedcodec.STEIM1
   :type: int
   :value: 10

   .. autodoc2-docstring:: simplemseed.seedcodec.STEIM1

.. py:data:: STEIM2
   :canonical: simplemseed.seedcodec.STEIM2
   :type: int
   :value: 11

   .. autodoc2-docstring:: simplemseed.seedcodec.STEIM2

.. py:class:: StationSourceId(networkCode: typing.Union[str, simplemseed.fdsnsourceid.NetworkSourceId], stationCode: str)
   :canonical: simplemseed.fdsnsourceid.StationSourceId

   .. autodoc2-docstring:: simplemseed.fdsnsourceid.StationSourceId

   .. rubric:: Initialization

   .. autodoc2-docstring:: simplemseed.fdsnsourceid.StationSourceId.__init__

   .. py:method:: createLocationSourceId(locationCode) -> simplemseed.fdsnsourceid.LocationSourceId
      :canonical: simplemseed.fdsnsourceid.StationSourceId.createLocationSourceId

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.StationSourceId.createLocationSourceId

   .. py:attribute:: networkCode
      :canonical: simplemseed.fdsnsourceid.StationSourceId.networkCode
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.StationSourceId.networkCode

   .. py:method:: networkSourceId() -> simplemseed.fdsnsourceid.NetworkSourceId
      :canonical: simplemseed.fdsnsourceid.StationSourceId.networkSourceId

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.StationSourceId.networkSourceId

   .. py:attribute:: stationCode
      :canonical: simplemseed.fdsnsourceid.StationSourceId.stationCode
      :type: str
      :value: None

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.StationSourceId.stationCode

   .. py:method:: validate() -> (bool, typing.Union[str, None])
      :canonical: simplemseed.fdsnsourceid.StationSourceId.validate

      .. autodoc2-docstring:: simplemseed.fdsnsourceid.StationSourceId.validate

.. py:class:: SteimFrameBlock(maxNumFrames: int = 0, steimVersion: int = 2)
   :canonical: simplemseed.steimframeblock.SteimFrameBlock

   .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock

   .. rubric:: Initialization

   .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock.__init__

   .. py:method:: addEncodedWord(word: numpy.int32, samples: int, nibble: int)
      :canonical: simplemseed.steimframeblock.SteimFrameBlock.addEncodedWord

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock.addEncodedWord

   .. py:method:: addEncodingNibble(bitFlag: numpy.int32)
      :canonical: simplemseed.steimframeblock.SteimFrameBlock.addEncodingNibble

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock.addEncodingNibble

   .. py:attribute:: currentFrame
      :canonical: simplemseed.steimframeblock.SteimFrameBlock.currentFrame
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock.currentFrame

   .. py:attribute:: currentSteimFrame
      :canonical: simplemseed.steimframeblock.SteimFrameBlock.currentSteimFrame
      :type: simplemseed.steimframeblock.SteimFrame
      :value: None

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock.currentSteimFrame

   .. py:method:: getEncodedData()
      :canonical: simplemseed.steimframeblock.SteimFrameBlock.getEncodedData

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock.getEncodedData

   .. py:method:: getNumFrames()
      :canonical: simplemseed.steimframeblock.SteimFrameBlock.getNumFrames

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock.getNumFrames

   .. py:method:: getNumSamples()
      :canonical: simplemseed.steimframeblock.SteimFrameBlock.getNumSamples

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock.getNumSamples

   .. py:method:: getSteimFrames()
      :canonical: simplemseed.steimframeblock.SteimFrameBlock.getSteimFrames

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock.getSteimFrames

   .. py:method:: getSteimVersion()
      :canonical: simplemseed.steimframeblock.SteimFrameBlock.getSteimVersion

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock.getSteimVersion

   .. py:attribute:: maxNumFrames
      :canonical: simplemseed.steimframeblock.SteimFrameBlock.maxNumFrames
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock.maxNumFrames

   .. py:attribute:: numSamples
      :canonical: simplemseed.steimframeblock.SteimFrameBlock.numSamples
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock.numSamples

   .. py:method:: pack()
      :canonical: simplemseed.steimframeblock.SteimFrameBlock.pack

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock.pack

   .. py:method:: setXsubN(word: numpy.int32)
      :canonical: simplemseed.steimframeblock.SteimFrameBlock.setXsubN

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock.setXsubN

   .. py:attribute:: steimFrameList
      :canonical: simplemseed.steimframeblock.SteimFrameBlock.steimFrameList
      :type: list[simplemseed.steimframeblock.SteimFrame]
      :value: None

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock.steimFrameList

   .. py:attribute:: steimVersion
      :canonical: simplemseed.steimframeblock.SteimFrameBlock.steimVersion
      :type: int
      :value: None

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock.steimVersion

.. py:data:: TESTDATA_NETCODE
   :canonical: simplemseed.fdsnsourceid.TESTDATA_NETCODE
   :value: 'XX'

   .. autodoc2-docstring:: simplemseed.fdsnsourceid.TESTDATA_NETCODE

.. py:exception:: UnsupportedCompressionType(message)
   :canonical: simplemseed.exceptions.UnsupportedCompressionType

   Bases: :py:obj:`simplemseed.exceptions.CodecException`

.. py:data:: VERSION
   :canonical: simplemseed.version.VERSION
   :value: None

   .. autodoc2-docstring:: simplemseed.version.VERSION

.. py:function:: bandCodeDescribe(bandCode: str) -> str
   :canonical: simplemseed.fdsnsourceid.bandCodeDescribe

   .. autodoc2-docstring:: simplemseed.fdsnsourceid.bandCodeDescribe

.. py:function:: bandCodeForRate(sampRatePeriod: typing.Optional[typing.Union[float, int]] = None, response_lb: typing.Optional[typing.Union[float, int]] = None) -> str
   :canonical: simplemseed.fdsnsourceid.bandCodeForRate

   .. autodoc2-docstring:: simplemseed.fdsnsourceid.bandCodeForRate

.. py:function:: canDecompress(encoding: int) -> bool
   :canonical: simplemseed.seedcodec.canDecompress

   .. autodoc2-docstring:: simplemseed.seedcodec.canDecompress

.. py:function:: crcAsHex(crc)
   :canonical: simplemseed.mseed3.crcAsHex

   .. autodoc2-docstring:: simplemseed.mseed3.crcAsHex

.. py:function:: decodeSteim1(dataBytes: bytearray, numSamples, bias=np.int32(0))
   :canonical: simplemseed.steim1.decodeSteim1

   .. autodoc2-docstring:: simplemseed.steim1.decodeSteim1

.. py:function:: decodeSteim2(dataBytes: bytearray, numSamples: int, bias: int = 0)
   :canonical: simplemseed.steim2.decodeSteim2

   .. autodoc2-docstring:: simplemseed.steim2.decodeSteim2

.. py:function:: decompress(compressionType: int, dataBytes: bytearray, numSamples: int, littleEndian: bool) -> numpy.ndarray
   :canonical: simplemseed.seedcodec.decompress

   .. autodoc2-docstring:: simplemseed.seedcodec.decompress

.. py:function:: encode(data, encoding=None, littleEndian=True)
   :canonical: simplemseed.seedcodec.encode

   .. autodoc2-docstring:: simplemseed.seedcodec.encode

.. py:function:: encodeSteim1(samples: typing.Union[numpy.ndarray, list[int]], frames: int = 0, bias: numpy.int32 = 0, offset: int = 0) -> bytearray
   :canonical: simplemseed.steim1.encodeSteim1

   .. autodoc2-docstring:: simplemseed.steim1.encodeSteim1

.. py:function:: encodeSteim1FrameBlock(samples: typing.Union[numpy.ndarray, list[int]], frames: int = 0, bias: numpy.int32 = 0, offset: int = 0) -> simplemseed.steimframeblock.SteimFrameBlock
   :canonical: simplemseed.steim1.encodeSteim1FrameBlock

   .. autodoc2-docstring:: simplemseed.steim1.encodeSteim1FrameBlock

.. py:function:: encodeSteim2(samples: typing.Union[numpy.ndarray, list[int]], frames: int = 0, bias: numpy.int32 = 0)
   :canonical: simplemseed.steim2.encodeSteim2

   .. autodoc2-docstring:: simplemseed.steim2.encodeSteim2

.. py:function:: encodeSteim2FrameBlock(samples: typing.Union[numpy.ndarray, list[int]], frames: int = 0, bias: numpy.int32 = 0) -> simplemseed.steimframeblock.SteimFrameBlock
   :canonical: simplemseed.steim2.encodeSteim2FrameBlock

   .. autodoc2-docstring:: simplemseed.steim2.encodeSteim2FrameBlock

.. py:function:: encodingName(encoding)
   :canonical: simplemseed.seedcodec.encodingName

   .. autodoc2-docstring:: simplemseed.seedcodec.encodingName

.. py:function:: isPrimitiveCompression(compressionType: int) -> bool
   :canonical: simplemseed.seedcodec.isPrimitiveCompression

   .. autodoc2-docstring:: simplemseed.seedcodec.isPrimitiveCompression

.. py:function:: isoWZ(time) -> str
   :canonical: simplemseed.util.isoWZ

   .. autodoc2-docstring:: simplemseed.util.isoWZ

.. py:function:: readMSeed3Records(fileptr, check_crc=True, matchsid=None, merge=False, verbose=False)
   :canonical: simplemseed.mseed3.readMSeed3Records

   .. autodoc2-docstring:: simplemseed.mseed3.readMSeed3Records

.. py:function:: readMiniseed2Records(fileptr, matchsid=None)
   :canonical: simplemseed.miniseed.readMiniseed2Records

   .. autodoc2-docstring:: simplemseed.miniseed.readMiniseed2Records

.. py:function:: sourceCodeDescribe(sourceCode: str) -> str
   :canonical: simplemseed.fdsnsourceid.sourceCodeDescribe

   .. autodoc2-docstring:: simplemseed.fdsnsourceid.sourceCodeDescribe

.. py:function:: unpackBlockette(recordBytes, offset, endianChar, dataOffset)
   :canonical: simplemseed.miniseed.unpackBlockette

   .. autodoc2-docstring:: simplemseed.miniseed.unpackBlockette

.. py:function:: unpackMSeed3FixedHeader(recordBytes)
   :canonical: simplemseed.mseed3.unpackMSeed3FixedHeader

   .. autodoc2-docstring:: simplemseed.mseed3.unpackMSeed3FixedHeader

.. py:function:: unpackMSeed3Record(recordBytes, check_crc=True)
   :canonical: simplemseed.mseed3.unpackMSeed3Record

   .. autodoc2-docstring:: simplemseed.mseed3.unpackMSeed3Record

.. py:function:: unpackMiniseedHeader(recordBytes, endianChar='>')
   :canonical: simplemseed.miniseed.unpackMiniseedHeader

   .. autodoc2-docstring:: simplemseed.miniseed.unpackMiniseedHeader

.. py:function:: unpackMiniseedRecord(recordBytes)
   :canonical: simplemseed.miniseed.unpackMiniseedRecord

   .. autodoc2-docstring:: simplemseed.miniseed.unpackMiniseedRecord
