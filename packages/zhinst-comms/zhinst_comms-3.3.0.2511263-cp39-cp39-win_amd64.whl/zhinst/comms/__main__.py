import click
from zhinst.comms import init_logs, LogSeverity
from zhinst.comms.compiler import compile, capnp_id, standard_imports


@click.group()
def main():
    pass


# The command line "compile" command is almost identical to the "capnp" executable of CapnProto.
# The only substantial difference is that capnp has a "--no-standard-import" flag, while we use
# a "--standard-import" flag, which if set will add a folder packaged with zhinst.comms itself
# to the import paths.
@main.command(
    name="compile",
    help="Compiles Cap'n Proto schema files and generates corresponding _schema.py files.",
)
@click.argument(
    "source",
    required=True,
)
@click.option(
    "--src-prefix",
    default="",
    help="If a file specified for compilation starts with <prefix>, remove the prefix for the purpose of deciding the names of output files.",
)
@click.option(
    "--output-folder",
    "-o",
    required=True,
    help="The folder in which the _schema.py file will be written.",
)
@click.option(
    "--import-path",
    "-I",
    multiple=True,
    help="Directories to add for the search of imports.",
)
@click.option(
    "--standard-import",
    is_flag=True,
    help="Add basic schemas that ship with the zhinst.comms library to the import path.",
)
def compile_cli(source, src_prefix, output_folder, import_path, standard_import):
    init_logs(LogSeverity.STATUS)
    import_path = list(import_path)
    if standard_import:
        import_path.append(standard_imports())
    compile(
        src=[source],
        src_prefix=src_prefix,
        output_folder=output_folder,
        import_paths=import_path,
    )


@main.command(
    name="id",
    help="Generates a new 64-bit unique ID for use in a Cap'n Proto schema.",
)
def id_cli():
    id = capnp_id()
    print(id)


if __name__ == "__main__":
    main()
