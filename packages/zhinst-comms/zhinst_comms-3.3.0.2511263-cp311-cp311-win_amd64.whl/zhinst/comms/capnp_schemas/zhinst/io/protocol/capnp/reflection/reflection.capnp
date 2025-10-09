@0x8461c2916c39ad0e;

using Cxx = import "/capnp/c++.capnp";
$Cxx.namespace("zhinst_capnp");

using import "/capnp/schema.capnp".Node;
using import "/zhinst/io/protocol/capnp/common/version.capnp".Version;

struct CapSchema @0xcb31ef7a76eb85cf {
  typeId @0 :UInt64;
  theSchema @1 :List(Node);
}

interface Reflection @0xf9a52e68104bc776 {
  # 1.0.0: initial version.
  const capabilityVersion :Version = "1.0.0";
  getReflectionVersion @1 () -> (version :Version);

  getTheSchema @0 () -> (theSchema :CapSchema);
}
