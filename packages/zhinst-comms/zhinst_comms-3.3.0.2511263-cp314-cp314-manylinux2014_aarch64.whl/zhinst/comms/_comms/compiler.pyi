"""
Compiler module to interact with the capnp compiler.
"""

from __future__ import annotations

__all__ = ["capnp_id", "compile"]

def capnp_id() -> str:
    """Generates a new 64-bit unique ID for use in a Cap'n Proto schema.

    Returns:
        A string containing a 64-bit unique ID in hexadecimal form.
    """

def compile(
    src: list[str], src_prefix: str, output_folder: str, import_paths: list[str]
) -> None:
    """Compile a .capnp file into a _schema.py file.

    This function can be used to generate _schema.py file starting
    from a .capnp file. It works like the 'capnp compile'
    command of CapnProto.

    Args:
        src: a list of .capnp files to be compiled. At the moment,
            only one file can be passed.
        src_prefix: if a file specified for compilation starts with
            <prefix>, remove the prefix for the purpose of deciding
            the names of output files.
        output_folder: the folder in which the _schema.py file will
            be written.
        import_paths: directories to add for the search of imports.
    """
