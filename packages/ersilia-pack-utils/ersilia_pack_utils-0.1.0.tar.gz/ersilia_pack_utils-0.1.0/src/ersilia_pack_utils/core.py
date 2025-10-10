import csv
import json
import struct
import numpy as np

Smiles = list[str]
Header = list[str]

_ALLOWED_DATA_TYPES = {
    "int32": np.int32,
    "float32": np.float32,
}

def read_smiles_csv(in_file: str) -> tuple[Header, Smiles]:
    """Read SMILES strings from a CSV file."""
    with open(in_file, "r", newline="") as f:
        reader = csv.reader(f)
        cols = next(reader)
        data = [r[0] for r in reader]
    return cols, data


def read_smiles_bin(in_file: str) -> tuple[Header, Smiles]:
    """Read SMILES strings from a custom binary file (length-prefixed strings)."""
    with open(in_file, "rb") as f:
        data = f.read()

    mv = memoryview(data)
    nl = mv.tobytes().find(b"\n")
    meta = json.loads(mv[:nl].tobytes().decode("utf-8"))
    cols = meta.get("columns", [])
    count = meta.get("count", 0)

    smiles_list = [None] * count
    offset = nl + 1
    for i in range(count):
        (length,) = struct.unpack_from(">I", mv, offset)
        offset += 4
        smiles_list[i] = mv[offset: offset + length].tobytes().decode("utf-8")
        offset += length

    return cols, smiles_list


def read_smiles(in_file: str) -> tuple[Header, Smiles]:
    """Dispatch to the appropriate SMILES reader based on file suffix."""
    if in_file.endswith(".bin"):
        return read_smiles_bin(in_file)
    return read_smiles_csv(in_file)


def write_out_csv(results, header, file: str) -> None:
    """Write rows to a CSV file."""
    with open(file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(results)


def write_out_bin(results, header, file: str, dtype: np.dtype | None = None) -> None:
    """
    Write a 2D array to a custom binary file.

    Strict mode: dtype must be exactly np.int32 or np.float32.
    """
    if dtype is None:
        raise ValueError("dtype must be specified (np.int32 or np.float32).")
    if dtype not in (np.int32, np.float32):
        raise ValueError("Only np.int32 and np.float32 are supported for binary endpoints.")

    arr = np.asarray(results, dtype=dtype)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)

    if len(header) != arr.shape[1]:
        raise ValueError(f"Header length ({len(header)}) != number of columns ({arr.shape[1]}).")

    dtype_name = "int32" if dtype is np.int32 else "float32"
    meta = {"columns": list(header), "shape": list(arr.shape), "dtype": dtype_name}
    meta_bytes = (json.dumps(meta) + "\n").encode("utf-8")

    with open(file, "wb") as f:
        f.write(meta_bytes)
        f.truncate(len(meta_bytes) + arr.nbytes)

    m = np.memmap(file, dtype=dtype, mode="r+", offset=len(meta_bytes), shape=arr.shape)
    m[:] = arr
    m.flush()


def write_out(results, header, file: str, dtype: np.dtype | None = None) -> None:
    """
    Dispatch to CSV or binary writer based on file suffix.
    """
    if file.endswith(".bin"):
        write_out_bin(results, header, file, dtype)
    elif file.endswith(".csv"):
        write_out_csv(results, header, file)
    else:
        raise ValueError(f"Unsupported extension for {file!r}")
