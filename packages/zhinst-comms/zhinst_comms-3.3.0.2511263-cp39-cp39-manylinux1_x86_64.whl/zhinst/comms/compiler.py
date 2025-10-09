from zhinst.comms._comms.compiler import *
import importlib.resources

__all__ = ["compile", "capnp_id"]


def standard_imports() -> str:
    """Return a path to a folder with useful, stable schema files.

    The folder contains .capnp files that are shipped with zhinst.comms itself
    and that are of general use. For example, error.capnp and reflection.capnp.

    The returned folder can be added to the "import_path" folders of the "compile"
    command.
    """
    return str(importlib.resources.files("zhinst.comms").joinpath("capnp_schemas"))
