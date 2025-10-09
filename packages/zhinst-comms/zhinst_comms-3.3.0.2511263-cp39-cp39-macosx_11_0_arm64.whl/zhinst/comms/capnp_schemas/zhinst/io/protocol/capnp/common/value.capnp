@0xfca5cbb23425bcc7;

using Cxx = import "/capnp/c++.capnp";
$Cxx.namespace("zhinst_capnp");

using import "/zhinst/io/protocol/capnp/common/complex.capnp".Complex;
using import "/zhinst/io/protocol/capnp/common/path.capnp".Path;
using import "/zhinst/io/protocol/capnp/common/error.capnp".Error;
using import "/zhinst/io/protocol/capnp/common/shf_vectors.capnp".ShfDemodulatorVectorData;
using import "/zhinst/io/protocol/capnp/common/shf_vectors.capnp".ShfResultLoggerVectorData;
using import "/zhinst/io/protocol/capnp/common/shf_vectors.capnp".ShfScopeVectorData;
using import "/zhinst/io/protocol/capnp/common/shf_vectors.capnp".ShfGeneratorWaveformVectorData;
using import "/zhinst/io/protocol/capnp/common/shf_vectors.capnp".ShfPidVectorData;

# StreamingErrors are used to signal errors within a continuous stream of data.
# Outside of the streaming context, the must not occur but rather be signaled
# using the result error mechanism.
using StreamingError = Error;

# A empty struct that can be used when no data needs to be sent. Note that there
# is also the built-in capnp Void type. However, this struct has an advantage
# over the built-in one: it can be used with generic types such as Result.
struct VoidStruct @0xdf7fe8e981437816 { }

struct VectorData @0x994c65b80df38978 {
  # "valueType" specifies the type of the vector. It uses (a subset) of values
  # from `ZIValueType_enum`.
  # The most commonly used type is "ZI_VALUE_TYPE_VECTOR_DATA". Some vectors use
  # a different format, e.g., for SHF devices.
  valueType @0 :UInt16;
  # "vectorElementType" uses the values from `ZIVectorElementType_enum` to
  # specify the data type of each element in the vector.
  vectorElementType @1 :UInt8;
  # ExtraHeader: [31:16] type and version information, [15:0] length in 32-bit
  # words
  extraHeaderInfo @2 :UInt32;
  # "data" maps to the `VectorData` struct.
  data @3 :Data;
}

# Important: a single "Data" field can't store more than 2^29-1 bytes. Thus,
# when sending very large vectors, the data should be split into multiple
# segments.
struct LargeVectorData @0xd948f7b09959b00a {
  valueType @0 :UInt16;
  vectorElementType @1 :UInt8;
  extraHeaderInfo @2 :UInt32;
  dataSegments @3 :List(Data);
}

# The CntSample data type is application specific. We generally avoid
# application specific data types, but these are needed to support the HDAWG in
# the HPK.
struct CntSample @0xe9370bd8287d6065 {
  timestamp @0 :UInt64;
  counter   @1 :Int32;
  trigger   @2 :UInt32;
}

# The TriggerSample data type is application specific. We generally avoid
# application specific data types, but these are needed to support the HDAWG in
# the HPK.
struct TriggerSample @0xdeb72097c27d0d95 {
  timestamp      @0 :UInt64;
  sampleTick     @1 :UInt64;
  trigger        @2 :UInt32;
  missedTriggers @3 :UInt32;
  awgTrigger     @4 :UInt32;
  dio            @5 :UInt32;
  sequenceIndex  @6 :UInt32;
}

struct Value @0xb1838b4771be75ac {
  union {
    int64                    @0  :Int64;
    double                   @1  :Float64;
    complex                  @2  :Complex;
    string                   @3  :Text;
    vectorData               @4  :VectorData;
    cntSample                @5  :CntSample;
    triggerSample            @6  :TriggerSample;
    none                     @7  :VoidStruct;
    streamingError           @8  :StreamingError;
    shfDemodData             @9  :ShfDemodulatorVectorData;
    shfResultLoggerData      @10 :ShfResultLoggerVectorData;
    vectorCntSamples         @11 :List(CntSample);
    vectorTriggerSamples     @12 :List(TriggerSample);
    largeVectorData          @13 :LargeVectorData;
    bool                     @14 :Bool;
    shfScopeData             @15 :ShfScopeVectorData;
    shfGeneratorWaveformData @16 :ShfGeneratorWaveformVectorData;
    shfPidData               @17 :ShfPidVectorData;
  }
}

struct AnnotatedValue @0xf408ee376e837cdc {
  struct Metadata @0xad53d8ca57af3018 {
    timestamp @0 :UInt64;
    path @1 :Path;
  }

  metadata @0 :Metadata;
  value @1 :Value;
}
