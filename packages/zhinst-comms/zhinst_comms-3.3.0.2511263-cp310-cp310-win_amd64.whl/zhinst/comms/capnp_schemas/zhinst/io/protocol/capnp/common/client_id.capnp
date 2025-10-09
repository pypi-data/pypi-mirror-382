@0xe03f860570f1a51f;

using Cxx = import "/capnp/c++.capnp";
$Cxx.namespace("zhinst_capnp");

using import "/zhinst/io/protocol/capnp/common/uuid.capnp".Uuid;

# A unique identifier for a client. Typically, there is a 1:1 relation between
# clients and socket connections, but this is not mandated, nor should it be
# relied upon.
using ClientId = Uuid;
const defaultClientId :ClientId = "";
