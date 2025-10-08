:py:mod:`simplemseed.steimframeblock`
=====================================

.. py:module:: simplemseed.steimframeblock

.. autodoc2-docstring:: simplemseed.steimframeblock
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`SteimFrame <simplemseed.steimframeblock.SteimFrame>`
     - .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrame
          :summary:
   * - :py:obj:`SteimFrameBlock <simplemseed.steimframeblock.SteimFrameBlock>`
     - .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrameBlock
          :summary:

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`getFloat32 <simplemseed.steimframeblock.getFloat32>`
     - .. autodoc2-docstring:: simplemseed.steimframeblock.getFloat32
          :summary:
   * - :py:obj:`getInt16 <simplemseed.steimframeblock.getInt16>`
     - .. autodoc2-docstring:: simplemseed.steimframeblock.getInt16
          :summary:
   * - :py:obj:`getInt32 <simplemseed.steimframeblock.getInt32>`
     - .. autodoc2-docstring:: simplemseed.steimframeblock.getInt32
          :summary:
   * - :py:obj:`getUint32 <simplemseed.steimframeblock.getUint32>`
     - .. autodoc2-docstring:: simplemseed.steimframeblock.getUint32
          :summary:

API
~~~

.. py:class:: SteimFrame()
   :canonical: simplemseed.steimframeblock.SteimFrame

   .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrame

   .. rubric:: Initialization

   .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrame.__init__

   .. py:method:: isEmpty()
      :canonical: simplemseed.steimframeblock.SteimFrame.isEmpty

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrame.isEmpty

   .. py:method:: pack()
      :canonical: simplemseed.steimframeblock.SteimFrame.pack

      .. autodoc2-docstring:: simplemseed.steimframeblock.SteimFrame.pack

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

.. py:function:: getFloat32(dataBytes, offset, littleEndian)
   :canonical: simplemseed.steimframeblock.getFloat32

   .. autodoc2-docstring:: simplemseed.steimframeblock.getFloat32

.. py:function:: getInt16(dataBytes, offset, littleEndian)
   :canonical: simplemseed.steimframeblock.getInt16

   .. autodoc2-docstring:: simplemseed.steimframeblock.getInt16

.. py:function:: getInt32(dataBytes, offset, littleEndian)
   :canonical: simplemseed.steimframeblock.getInt32

   .. autodoc2-docstring:: simplemseed.steimframeblock.getInt32

.. py:function:: getUint32(dataBytes, offset, littleEndian)
   :canonical: simplemseed.steimframeblock.getUint32

   .. autodoc2-docstring:: simplemseed.steimframeblock.getUint32
