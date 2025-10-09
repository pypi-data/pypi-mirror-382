import json
import logging
import os
from enum import Enum
from itertools import zip_longest
from pathlib import Path
from typing import Annotated, BinaryIO, Iterator, Optional, TextIO

import grpc
import numpy as np
import phonexia.grpc.common.core_pb2 as phx_common
import phonexia.grpc.technologies.speaker_identification.v1.speaker_identification_pb2 as sid
import phonexia.grpc.technologies.speaker_identification.v1.speaker_identification_pb2_grpc as sid_grpc
import typer
from google.protobuf.json_format import MessageToDict

MAX_BATCH_SIZE = 1024


def list_reader(lst: TextIO) -> Iterator[BinaryIO]:
    logging.info(f"Opening list; {lst.name}")
    for vp_path in lst.read().splitlines():
        if os.path.exists(vp_path):
            with Path(vp_path).open("rb") as file:
                yield file
        else:
            raise RuntimeError(f"Voiceprint '{vp_path}' in list '{lst.name}' does not exist")


def parse_vp(file: BinaryIO) -> phx_common.Voiceprint:
    logging.info(f"Opening voiceprint: {file.name}")
    return phx_common.Voiceprint(content=file.read())


def make_compare_request(
    list_a: Iterator[BinaryIO], list_b: Iterator[BinaryIO]
) -> Iterator[sid.CompareRequest]:
    batch_size = 0
    request = sid.CompareRequest()

    for file_a, file_b in zip_longest(list_a, list_b):
        if batch_size >= MAX_BATCH_SIZE:
            yield request
            batch_size = 0
            request = sid.CompareRequest()

        if file_a:
            vp = parse_vp(file_a)
            request.voiceprints_a.append(vp)
            batch_size += 1

        if file_b:
            vp = parse_vp(file_b)
            request.voiceprints_b.append(vp)
            batch_size += 1

    # Yield the last request if it contains any voiceprints
    if len(request.voiceprints_a) or len(request.voiceprints_b):
        yield request


def print_scores(
    response: list[sid.CompareResponse],
    rows: int,
    cols: int,
    result: list,
    output: TextIO,
    to_json: bool,
) -> None:
    mat = np.array(result).reshape(rows, cols)
    if to_json:
        for res in response:
            output.write(
                json.dumps(
                    MessageToDict(
                        res,
                        always_print_fields_with_no_presence=True,
                        preserving_proto_field_name=True,
                    ),
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n"
            )
        logging.info(f"Saved comparison to {output.name}")
    else:
        lines = ["Score:"]
        for row in mat:
            line = "".join(f"{val:7.1f} " for val in row).rstrip()
            lines.append(line)
        text = "\n".join(lines)
        output.write(text + "\n")
        logging.info(f"Saved comparison to {output.name}")


def compare_one_to_one(
    file1: BinaryIO,
    file2: BinaryIO,
    channel: grpc.Channel,
    metadata: Optional[list],
    output: TextIO,
    to_json: bool,
) -> None:
    stub = sid_grpc.VoiceprintComparisonStub(channel)
    result = stub.Compare(make_compare_request(iter([file1]), iter([file2])), metadata=metadata)
    for res in result:
        print_scores([res], 1, 1, [res.scores.values], output, to_json)


def compare_m_to_n(
    list1: Iterator[Path],
    list2: Iterator[Path],
    channel: grpc.Channel,
    metadata: Optional[list],
    output: TextIO,
    to_json: bool,
) -> None:
    stub = sid_grpc.VoiceprintComparisonStub(channel)
    n_rows = 0
    n_cols = 0
    scores = []
    results = []
    requests = make_compare_request(list1, list2)
    for result in stub.Compare(requests, metadata=metadata):
        results.append(result)
        if result.scores.rows_count:
            n_rows = result.scores.rows_count
            n_cols = result.scores.columns_count
        scores.extend(result.scores.values)

    print_scores(results, n_rows, n_cols, scores, output, to_json)


def merge_voiceprints(
    files: list[BinaryIO],
    channel: grpc.Channel,
    metadata: Optional[list],
    output: BinaryIO,
    to_json: bool,
):
    stub = sid_grpc.VoiceprintMergingStub(channel)
    request = sid.MergeRequest(voiceprints=[parse_vp(f) for f in files])
    result = stub.Merge(request, metadata=metadata)

    if to_json:
        payload = json.dumps(
            MessageToDict(
                result, always_print_fields_with_no_presence=True, preserving_proto_field_name=True
            ),
            indent=2,
            ensure_ascii=False,
        ).encode("utf-8")
        output.write(payload)
    else:
        output.write(result.voiceprint.content)
    logging.info(f"Saved merged voiceprint to {output.name}")


def make_convert_request(files: Iterator[BinaryIO]) -> Iterator[sid.ConvertRequest]:
    batch_size = 0
    request = sid.ConvertRequest()

    for file in files:
        if batch_size >= MAX_BATCH_SIZE:
            yield request
            batch_size = 0
            request = sid.ConvertRequest()

        vp = parse_vp(file)
        request.voiceprints.append(vp)
        batch_size += 1

    # Yield the last request if it contains any voiceprints
    if len(request.voiceprints):
        yield request


def convert_voiceprints(
    files: list[BinaryIO], channel: grpc.Channel, metadata: Optional[list], output: TextIO
):
    stub = sid_grpc.VoiceprintConversionStub(channel)
    for result in stub.Convert(make_convert_request(files), metadata=metadata):
        output.write(
            json.dumps(
                MessageToDict(
                    result,
                    always_print_fields_with_no_presence=True,
                    preserving_proto_field_name=True,
                ),
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        )

    logging.info(f"Saved converted voiceprints to {output.name}")


app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True)


class LogLevel(str, Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class CompareFormat(str, Enum):
    TEXT = "text"
    JSON = "json"


class MergeFormat(str, Enum):
    BINARY = "binary"
    JSON = "json"


def _parse_metadata_callback(
    ctx: typer.Context, metadata_list: Optional[list[str]]
) -> list[tuple[str, str]]:
    if ctx.resilient_parsing or metadata_list is None:
        return []

    params = []
    for item in metadata_list:
        t = tuple(item.split("=", 1))
        if len(t) != 2:
            raise typer.BadParameter(f"Metadata must be in format 'KEY=VALUE': {item}")
        params.append(t)
    return params


@app.callback()
def cli(
    ctx: typer.Context,
    host: Annotated[
        str,
        typer.Option(
            "-H",
            "--host",
            help="Server address (host:port).",
        ),
    ] = "localhost:8080",
    log_level: Annotated[
        LogLevel,
        typer.Option(
            "-l",
            "--log-level",
            help="Logging level.",
        ),
    ] = LogLevel.ERROR,
    metadata: Annotated[
        Optional[list[str]],
        typer.Option(
            "--metadata",
            metavar="KEY=VALUE",
            help="Custom client metadata.",
            show_default=False,
            callback=_parse_metadata_callback,
        ),
    ] = None,
    plaintext: Annotated[
        bool,
        typer.Option(
            "--plaintext",
            help="Use plain-text HTTP/2 when connecting to server (no TLS).",
        ),
    ] = False,
):
    """Voiceprint Comparison gRPC client. Compares voiceprints and returns scores."""
    logging.basicConfig(
        level=log_level.value.upper(),
        format="[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    ctx.obj = {
        "host": host,
        "metadata": metadata,
        "plaintext": plaintext,
    }


@app.command()
def compare(
    ctx: typer.Context,
    files: Annotated[
        Optional[tuple[typer.FileBinaryRead, typer.FileBinaryRead]],
        typer.Option(
            "--files",
            metavar="PATH PATH",
            help="Voiceprint files for 1x1 comparison, requires exactly two arguments.",
            lazy=False,
        ),
    ] = None,
    lists: Annotated[
        Optional[tuple[typer.FileText, typer.FileText]],
        typer.Option(
            "--lists",
            metavar="PATH PATH",
            help=(
                "Lists of files for MxN comparison (text file with one path to a voiceprint per line), "
                "requires exactly two arguments."
            ),
            lazy=False,
        ),
    ] = None,
    fmt: Annotated[
        CompareFormat, typer.Option("--out-format", "-f", help="Output file format.")
    ] = CompareFormat.JSON,
    output: Annotated[
        typer.FileTextWrite,
        typer.Option(
            "--output", "-o", help="Output file path. If omitted, prints to stdout.", lazy=False
        ),
    ] = "-",
):
    """Compare voiceprints"""

    host = ctx.obj["host"]
    metadata = ctx.obj["metadata"]
    plaintext = ctx.obj["plaintext"]
    to_json = fmt == CompareFormat.JSON

    # Ensure exactly one of files or lists is provided (mutually exclusive)
    if files and lists:
        raise typer.BadParameter("Cannot use both --files and --lists options together")
    if not files and not lists:
        raise typer.BadParameter("Must provide either --files or --lists option")

    try:
        logging.info(f"Connecting to {host}")
        with (
            grpc.insecure_channel(target=host)
            if plaintext
            else grpc.secure_channel(target=host, credentials=grpc.ssl_channel_credentials())
        ) as channel:
            if files:
                compare_one_to_one(
                    file1=files[0],
                    file2=files[1],
                    channel=channel,
                    metadata=metadata,
                    output=output,
                    to_json=to_json,
                )
            elif lists:
                compare_m_to_n(
                    list1=list_reader(lists[0]),
                    list2=list_reader(lists[1]),
                    channel=channel,
                    metadata=metadata,
                    output=output,
                    to_json=to_json,
                )
    except grpc.RpcError:
        logging.exception("RPC failed")
        raise typer.Exit(code=1) from None
    except typer.Exit:
        raise
    except Exception:
        logging.exception("Unknown error")
        raise typer.Exit(code=1) from None


@app.command()
def merge(
    ctx: typer.Context,
    files: Annotated[
        list[typer.FileBinaryRead],
        typer.Argument(metavar="FILES ...", help="Voiceprints to merge.", lazy=False),
    ],
    output: Annotated[
        typer.FileBinaryWrite,
        typer.Option(
            "--output", "-o", help="Output file path. If omitted, prints to stdout.", lazy=False
        ),
    ] = "-",
    fmt: Annotated[
        MergeFormat, typer.Option("--out-format", "-f", help="Output file format.")
    ] = MergeFormat.JSON,
):
    """Merge voiceprints."""
    host = ctx.obj["host"]
    metadata = ctx.obj["metadata"]
    plaintext = ctx.obj["plaintext"]
    to_json = fmt == MergeFormat.JSON

    if len(files) < 2:
        raise typer.BadParameter("Provide at least two FILE arguments.")

    try:
        logging.info(f"Connecting to {host}")
        with (
            grpc.insecure_channel(target=host)
            if plaintext
            else grpc.secure_channel(target=host, credentials=grpc.ssl_channel_credentials())
        ) as channel:
            merge_voiceprints(
                files=files, channel=channel, metadata=metadata, output=output, to_json=to_json
            )
    except grpc.RpcError:
        logging.exception("RPC failed")
        raise typer.Exit(code=1) from None
    except typer.Exit:
        raise
    except Exception:
        logging.exception("Unknown error")
        raise typer.Exit(code=1) from None


@app.command()
def convert(
    ctx: typer.Context,
    files: Annotated[
        list[typer.FileBinaryRead],
        typer.Argument(metavar="FILES ...", help="Voiceprints to convert.", lazy=False),
    ],
    output: Annotated[
        typer.FileTextWrite,
        typer.Option(
            "--output",
            "-o",
            help="Output file path. If omitted, prints to stdout. Output is in JSON format, containing the converted voiceprints.",
            lazy=False,
        ),
    ] = "-",
):
    """Convert voiceprints to vector database format."""
    host = ctx.obj["host"]
    metadata = ctx.obj["metadata"]
    plaintext = ctx.obj["plaintext"]

    if len(files) == 0:
        raise typer.BadParameter("Provide at least one FILE argument.")

    try:
        logging.info(f"Connecting to {host}")
        with (
            grpc.insecure_channel(target=host)
            if plaintext
            else grpc.secure_channel(target=host, credentials=grpc.ssl_channel_credentials())
        ) as channel:
            convert_voiceprints(files=files, channel=channel, metadata=metadata, output=output)
    except grpc.RpcError:
        logging.exception("RPC failed")
        raise typer.Exit(code=1) from None
    except typer.Exit:
        raise
    except Exception:
        logging.exception("Unknown error")
        raise typer.Exit(code=1) from None


if __name__ == "__main__":
    app()
