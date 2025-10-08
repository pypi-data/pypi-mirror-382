:py:mod:`simplemseed.mseed3`
============================

.. py:module:: simplemseed.mseed3

.. autodoc2-docstring:: simplemseed.mseed3
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`MSeed3Header <simplemseed.mseed3.MSeed3Header>`
     - .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Header
          :summary:
   * - :py:obj:`MSeed3Record <simplemseed.mseed3.MSeed3Record>`
     - .. autodoc2-docstring:: simplemseed.mseed3.MSeed3Record
          :summary:

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`areCompatible <simplemseed.mseed3.areCompatible>`
     - .. autodoc2-docstring:: simplemseed.mseed3.areCompatible
          :summary:
   * - :py:obj:`crcAsHex <simplemseed.mseed3.crcAsHex>`
     - .. autodoc2-docstring:: simplemseed.mseed3.crcAsHex
          :summary:
   * - :py:obj:`mseed3merge <simplemseed.mseed3.mseed3merge>`
     - .. autodoc2-docstring:: simplemseed.mseed3.mseed3merge
          :summary:
   * - :py:obj:`readMSeed3Records <simplemseed.mseed3.readMSeed3Records>`
     - .. autodoc2-docstring:: simplemseed.mseed3.readMSeed3Records
          :summary:
   * - :py:obj:`unpackMSeed3FixedHeader <simplemseed.mseed3.unpackMSeed3FixedHeader>`
     - .. autodoc2-docstring:: simplemseed.mseed3.unpackMSeed3FixedHeader
          :summary:
   * - :py:obj:`unpackMSeed3Record <simplemseed.mseed3.unpackMSeed3Record>`
     - .. autodoc2-docstring:: simplemseed.mseed3.unpackMSeed3Record
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`CRC_OFFSET <simplemseed.mseed3.CRC_OFFSET>`
     - .. autodoc2-docstring:: simplemseed.mseed3.CRC_OFFSET
          :summary:
   * - :py:obj:`FIXED_HEADER_SIZE <simplemseed.mseed3.FIXED_HEADER_SIZE>`
     - .. autodoc2-docstring:: simplemseed.mseed3.FIXED_HEADER_SIZE
          :summary:
   * - :py:obj:`HEADER_PACK_FORMAT <simplemseed.mseed3.HEADER_PACK_FORMAT>`
     - .. autodoc2-docstring:: simplemseed.mseed3.HEADER_PACK_FORMAT
          :summary:
   * - :py:obj:`MINISEED_THREE_MIME <simplemseed.mseed3.MINISEED_THREE_MIME>`
     - .. autodoc2-docstring:: simplemseed.mseed3.MINISEED_THREE_MIME
          :summary:
   * - :py:obj:`MS_FORMAT_VERSION_3 <simplemseed.mseed3.MS_FORMAT_VERSION_3>`
     - .. autodoc2-docstring:: simplemseed.mseed3.MS_FORMAT_VERSION_3
          :summary:
   * - :py:obj:`MS_RECORD_INDICATOR <simplemseed.mseed3.MS_RECORD_INDICATOR>`
     - .. autodoc2-docstring:: simplemseed.mseed3.MS_RECORD_INDICATOR
          :summary:
   * - :py:obj:`UNKNOWN_PUBLICATION_VERSION <simplemseed.mseed3.UNKNOWN_PUBLICATION_VERSION>`
     - .. autodoc2-docstring:: simplemseed.mseed3.UNKNOWN_PUBLICATION_VERSION
          :summary:

API
~~~

.. py:data:: CRC_OFFSET
   :canonical: simplemseed.mseed3.CRC_OFFSET
   :value: 28

   .. autodoc2-docstring:: simplemseed.mseed3.CRC_OFFSET

.. py:data:: FIXED_HEADER_SIZE
   :canonical: simplemseed.mseed3.FIXED_HEADER_SIZE
   :value: 40

   .. autodoc2-docstring:: simplemseed.mseed3.FIXED_HEADER_SIZE

.. py:data:: HEADER_PACK_FORMAT
   :canonical: simplemseed.mseed3.HEADER_PACK_FORMAT
   :value: '<ccBBIHHBBBBdIIBBHI'

   .. autodoc2-docstring:: simplemseed.mseed3.HEADER_PACK_FORMAT

.. py:data:: MINISEED_THREE_MIME
   :canonical: simplemseed.mseed3.MINISEED_THREE_MIME
   :value: 'application/vnd.fdsn.mseed3'

   .. autodoc2-docstring:: simplemseed.mseed3.MINISEED_THREE_MIME

.. py:data:: MS_FORMAT_VERSION_3
   :canonical: simplemseed.mseed3.MS_FORMAT_VERSION_3
   :value: 3

   .. autodoc2-docstring:: simplemseed.mseed3.MS_FORMAT_VERSION_3

.. py:data:: MS_RECORD_INDICATOR
   :canonical: simplemseed.mseed3.MS_RECORD_INDICATOR
   :value: 'MS'

   .. autodoc2-docstring:: simplemseed.mseed3.MS_RECORD_INDICATOR

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

.. py:data:: UNKNOWN_PUBLICATION_VERSION
   :canonical: simplemseed.mseed3.UNKNOWN_PUBLICATION_VERSION
   :value: 0

   .. autodoc2-docstring:: simplemseed.mseed3.UNKNOWN_PUBLICATION_VERSION

.. py:function:: areCompatible(ms3a: simplemseed.mseed3.MSeed3Record, ms3b: simplemseed.mseed3.MSeed3Record, timeTolFactor=0.5) -> bool
   :canonical: simplemseed.mseed3.areCompatible

   .. autodoc2-docstring:: simplemseed.mseed3.areCompatible

.. py:function:: crcAsHex(crc)
   :canonical: simplemseed.mseed3.crcAsHex

   .. autodoc2-docstring:: simplemseed.mseed3.crcAsHex

.. py:function:: mseed3merge(ms3a: simplemseed.mseed3.MSeed3Record, ms3b: simplemseed.mseed3.MSeed3Record) -> list[simplemseed.mseed3.MSeed3Record]
   :canonical: simplemseed.mseed3.mseed3merge

   .. autodoc2-docstring:: simplemseed.mseed3.mseed3merge

.. py:function:: readMSeed3Records(fileptr, check_crc=True, matchsid=None, merge=False, verbose=False)
   :canonical: simplemseed.mseed3.readMSeed3Records

   .. autodoc2-docstring:: simplemseed.mseed3.readMSeed3Records

.. py:function:: unpackMSeed3FixedHeader(recordBytes)
   :canonical: simplemseed.mseed3.unpackMSeed3FixedHeader

   .. autodoc2-docstring:: simplemseed.mseed3.unpackMSeed3FixedHeader

.. py:function:: unpackMSeed3Record(recordBytes, check_crc=True)
   :canonical: simplemseed.mseed3.unpackMSeed3Record

   .. autodoc2-docstring:: simplemseed.mseed3.unpackMSeed3Record
