:py:mod:`simplemseed.miniseed`
==============================

.. py:module:: simplemseed.miniseed

.. autodoc2-docstring:: simplemseed.miniseed
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`MiniseedHeader <simplemseed.miniseed.MiniseedHeader>`
     - .. autodoc2-docstring:: simplemseed.miniseed.MiniseedHeader
          :summary:
   * - :py:obj:`MiniseedRecord <simplemseed.miniseed.MiniseedRecord>`
     - .. autodoc2-docstring:: simplemseed.miniseed.MiniseedRecord
          :summary:

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`decompressEncodedData <simplemseed.miniseed.decompressEncodedData>`
     - .. autodoc2-docstring:: simplemseed.miniseed.decompressEncodedData
          :summary:
   * - :py:obj:`readMiniseed2Records <simplemseed.miniseed.readMiniseed2Records>`
     - .. autodoc2-docstring:: simplemseed.miniseed.readMiniseed2Records
          :summary:
   * - :py:obj:`unpackBlockette <simplemseed.miniseed.unpackBlockette>`
     - .. autodoc2-docstring:: simplemseed.miniseed.unpackBlockette
          :summary:
   * - :py:obj:`unpackBlockette100 <simplemseed.miniseed.unpackBlockette100>`
     - .. autodoc2-docstring:: simplemseed.miniseed.unpackBlockette100
          :summary:
   * - :py:obj:`unpackBlockette1000 <simplemseed.miniseed.unpackBlockette1000>`
     - .. autodoc2-docstring:: simplemseed.miniseed.unpackBlockette1000
          :summary:
   * - :py:obj:`unpackBlockette1001 <simplemseed.miniseed.unpackBlockette1001>`
     - .. autodoc2-docstring:: simplemseed.miniseed.unpackBlockette1001
          :summary:
   * - :py:obj:`unpackFixedHeaderGuessByteOrder <simplemseed.miniseed.unpackFixedHeaderGuessByteOrder>`
     - .. autodoc2-docstring:: simplemseed.miniseed.unpackFixedHeaderGuessByteOrder
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

   * - :py:obj:`B1000_SIZE <simplemseed.miniseed.B1000_SIZE>`
     - .. autodoc2-docstring:: simplemseed.miniseed.B1000_SIZE
          :summary:
   * - :py:obj:`BTime <simplemseed.miniseed.BTime>`
     - .. autodoc2-docstring:: simplemseed.miniseed.BTime
          :summary:
   * - :py:obj:`Blockette100 <simplemseed.miniseed.Blockette100>`
     - .. autodoc2-docstring:: simplemseed.miniseed.Blockette100
          :summary:
   * - :py:obj:`Blockette1000 <simplemseed.miniseed.Blockette1000>`
     - .. autodoc2-docstring:: simplemseed.miniseed.Blockette1000
          :summary:
   * - :py:obj:`Blockette1001 <simplemseed.miniseed.Blockette1001>`
     - .. autodoc2-docstring:: simplemseed.miniseed.Blockette1001
          :summary:
   * - :py:obj:`BlocketteUnknown <simplemseed.miniseed.BlocketteUnknown>`
     - .. autodoc2-docstring:: simplemseed.miniseed.BlocketteUnknown
          :summary:
   * - :py:obj:`EMPTY_SEQ <simplemseed.miniseed.EMPTY_SEQ>`
     - .. autodoc2-docstring:: simplemseed.miniseed.EMPTY_SEQ
          :summary:
   * - :py:obj:`ENC_INT <simplemseed.miniseed.ENC_INT>`
     - .. autodoc2-docstring:: simplemseed.miniseed.ENC_INT
          :summary:
   * - :py:obj:`ENC_SHORT <simplemseed.miniseed.ENC_SHORT>`
     - .. autodoc2-docstring:: simplemseed.miniseed.ENC_SHORT
          :summary:
   * - :py:obj:`HEADER_SIZE <simplemseed.miniseed.HEADER_SIZE>`
     - .. autodoc2-docstring:: simplemseed.miniseed.HEADER_SIZE
          :summary:
   * - :py:obj:`MAX_INT_PER_512 <simplemseed.miniseed.MAX_INT_PER_512>`
     - .. autodoc2-docstring:: simplemseed.miniseed.MAX_INT_PER_512
          :summary:
   * - :py:obj:`MAX_SHORT_PER_512 <simplemseed.miniseed.MAX_SHORT_PER_512>`
     - .. autodoc2-docstring:: simplemseed.miniseed.MAX_SHORT_PER_512
          :summary:
   * - :py:obj:`MICRO <simplemseed.miniseed.MICRO>`
     - .. autodoc2-docstring:: simplemseed.miniseed.MICRO
          :summary:

API
~~~

.. py:data:: B1000_SIZE
   :canonical: simplemseed.miniseed.B1000_SIZE
   :value: 8

   .. autodoc2-docstring:: simplemseed.miniseed.B1000_SIZE

.. py:data:: BTime
   :canonical: simplemseed.miniseed.BTime
   :value: 'namedtuple(...)'

   .. autodoc2-docstring:: simplemseed.miniseed.BTime

.. py:data:: Blockette100
   :canonical: simplemseed.miniseed.Blockette100
   :value: 'namedtuple(...)'

   .. autodoc2-docstring:: simplemseed.miniseed.Blockette100

.. py:data:: Blockette1000
   :canonical: simplemseed.miniseed.Blockette1000
   :value: 'namedtuple(...)'

   .. autodoc2-docstring:: simplemseed.miniseed.Blockette1000

.. py:data:: Blockette1001
   :canonical: simplemseed.miniseed.Blockette1001
   :value: 'namedtuple(...)'

   .. autodoc2-docstring:: simplemseed.miniseed.Blockette1001

.. py:data:: BlocketteUnknown
   :canonical: simplemseed.miniseed.BlocketteUnknown
   :value: 'namedtuple(...)'

   .. autodoc2-docstring:: simplemseed.miniseed.BlocketteUnknown

.. py:data:: EMPTY_SEQ
   :canonical: simplemseed.miniseed.EMPTY_SEQ
   :value: 'encode(...)'

   .. autodoc2-docstring:: simplemseed.miniseed.EMPTY_SEQ

.. py:data:: ENC_INT
   :canonical: simplemseed.miniseed.ENC_INT
   :value: 3

   .. autodoc2-docstring:: simplemseed.miniseed.ENC_INT

.. py:data:: ENC_SHORT
   :canonical: simplemseed.miniseed.ENC_SHORT
   :value: 1

   .. autodoc2-docstring:: simplemseed.miniseed.ENC_SHORT

.. py:data:: HEADER_SIZE
   :canonical: simplemseed.miniseed.HEADER_SIZE
   :value: 48

   .. autodoc2-docstring:: simplemseed.miniseed.HEADER_SIZE

.. py:data:: MAX_INT_PER_512
   :canonical: simplemseed.miniseed.MAX_INT_PER_512
   :value: None

   .. autodoc2-docstring:: simplemseed.miniseed.MAX_INT_PER_512

.. py:data:: MAX_SHORT_PER_512
   :canonical: simplemseed.miniseed.MAX_SHORT_PER_512
   :value: None

   .. autodoc2-docstring:: simplemseed.miniseed.MAX_SHORT_PER_512

.. py:data:: MICRO
   :canonical: simplemseed.miniseed.MICRO
   :value: 1000000

   .. autodoc2-docstring:: simplemseed.miniseed.MICRO

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

.. py:function:: decompressEncodedData(encoding, byteorder, numSamples, recordBytes)
   :canonical: simplemseed.miniseed.decompressEncodedData

   .. autodoc2-docstring:: simplemseed.miniseed.decompressEncodedData

.. py:function:: readMiniseed2Records(fileptr, matchsid=None)
   :canonical: simplemseed.miniseed.readMiniseed2Records

   .. autodoc2-docstring:: simplemseed.miniseed.readMiniseed2Records

.. py:function:: unpackBlockette(recordBytes, offset, endianChar, dataOffset)
   :canonical: simplemseed.miniseed.unpackBlockette

   .. autodoc2-docstring:: simplemseed.miniseed.unpackBlockette

.. py:function:: unpackBlockette100(recordBytes, offset, endianChar)
   :canonical: simplemseed.miniseed.unpackBlockette100

   .. autodoc2-docstring:: simplemseed.miniseed.unpackBlockette100

.. py:function:: unpackBlockette1000(recordBytes, offset, endianChar)
   :canonical: simplemseed.miniseed.unpackBlockette1000

   .. autodoc2-docstring:: simplemseed.miniseed.unpackBlockette1000

.. py:function:: unpackBlockette1001(recordBytes, offset, endianChar)
   :canonical: simplemseed.miniseed.unpackBlockette1001

   .. autodoc2-docstring:: simplemseed.miniseed.unpackBlockette1001

.. py:function:: unpackFixedHeaderGuessByteOrder(recordBytes)
   :canonical: simplemseed.miniseed.unpackFixedHeaderGuessByteOrder

   .. autodoc2-docstring:: simplemseed.miniseed.unpackFixedHeaderGuessByteOrder

.. py:function:: unpackMiniseedHeader(recordBytes, endianChar='>')
   :canonical: simplemseed.miniseed.unpackMiniseedHeader

   .. autodoc2-docstring:: simplemseed.miniseed.unpackMiniseedHeader

.. py:function:: unpackMiniseedRecord(recordBytes)
   :canonical: simplemseed.miniseed.unpackMiniseedRecord

   .. autodoc2-docstring:: simplemseed.miniseed.unpackMiniseedRecord
