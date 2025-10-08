from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Tuple, BinaryIO, List, AsyncIterable
import heapq
from p2p_copy.security import ChainedChecksum

CHUNK_SIZE = 1 << 20  # 1 MiB


async def read_in_chunks(fp: BinaryIO, *, chunk_size: int = CHUNK_SIZE) -> AsyncIterable[bytes]:
    """
    Asynchronously read bytes from a file in chunks.

    Parameters
    ----------
    fp : BinaryIO
        The file pointer to read from.
    chunk_size : int, optional
        Size of each chunk in bytes. Default is 1 MiB.

    Yields
    ------
    bytes
        The next chunk of data.
    """

    while True:
        # Read from disk without blocking the event-loop
        chunk = await asyncio.to_thread(fp.read, chunk_size)
        if not chunk:
            break
        yield chunk


async def compute_chain_up_to(path: Path, limit: int | None = None) -> Tuple[int, bytes]:
    """
    Compute chained checksum over the raw bytes of a file up to a limit.

    Parameters
    ----------
    path : Path
        Path to the file.
    limit : int, optional
        Maximum bytes to hash. If None, hash the entire file.

    Returns
    -------
    tuple[int, bytes]
        (bytes_hashed, final_chain_bytes)
    """

    c = ChainedChecksum()
    hashed = 0
    with path.open("rb") as fp:
        if limit is None:
            while True:
                chunk = await asyncio.to_thread(fp.read, CHUNK_SIZE)
                if not chunk:
                    break
                hashed += len(chunk)
                c.next_hash(chunk)
        else:
            remaining = int(limit)
            while remaining > 0:
                to_read = min(remaining, CHUNK_SIZE)
                chunk = await asyncio.to_thread(fp.read, to_read)
                if not chunk:
                    break
                hashed += len(chunk)
                remaining -= len(chunk)
                c.next_hash(chunk)
    return hashed, c.prev_chain




def iter_manifest_entries(paths: List[str], n: int = 1) -> List[List[Tuple[Path, Path, int]]]:
    """
    Collect manifest entries for files in the given paths (files or directories) and partition into n groups
    with approximately equal total sizes.

    Parameters
    ----------
    paths : List[str]
        List of file or directory paths.
    n : int, optional
        Number of groups to partition into (default 1).

    Returns
    -------
    List[List[Tuple[Path, Path, int]]]
        n lists, each containing (absolute_path, relative_path, size) tuples with roughly equal total size.
        If n=1, returns [[all_entries]].

    Notes
    -----
    - Entries are sorted by size descending for partitioning.
    - Skips non-existent or invalid paths.
    - Uses greedy heuristic for partitioning.
    """

    if not isinstance(paths, list):
        print("[p2p_copy] send(): files or dirs must be passed as list")
        return [[] for _ in range(n)]
    elif not paths:
        return [[] for _ in range(n)]
    if n <= 0:
        raise ValueError("n must be positive")

    # Collect all entries
    entries = []
    for raw in paths:
        if len(raw) == 1:
            print("[p2p_copy] send(): probably not a file:", raw)
            continue
        p = Path(raw).expanduser()
        if not p.exists():
            print("[p2p_copy] send(): file does not exist:", p)
            continue
        if p.is_file():
            entries.append((p.resolve(), Path(p.name), p.stat().st_size))
        else:
            root = p.resolve()
            for sub in sorted(root.rglob("*")):
                if sub.is_file():
                    rel = Path(p.name) / sub.relative_to(root)
                    entries.append((sub.resolve(), rel, sub.stat().st_size))

    # Deduplicate by absolute path (keep first occurrence)
    seen = set()
    unique_entries = []
    for entry in entries:
        abs_p = entry[0]
        if abs_p not in seen:
            seen.add(abs_p)
            unique_entries.append(entry)
    entries = unique_entries

    if not entries:
        return [[] for _ in range(n)]

    # Sort by size descending
    entries.sort(key=lambda x: x[2], reverse=True)

    # Use a min-heap to track current group sums and indices
    groups = [[] for _ in range(n)]
    heap = [(0, i) for i in range(n)]  # (current_sum, group_index)
    heapq.heapify(heap)

    for tup in entries:
        size = tup[2]
        current_sum, group_idx = heapq.heappop(heap)
        groups[group_idx].append(tup)
        new_sum = current_sum + size
        heapq.heappush(heap, (new_sum, group_idx))
    return groups


def ensure_dir(p: Path) -> None:
    """
    Ensure the directory exists, creating parents if needed.

    Parameters
    ----------
    p : Path
        The path to ensure is a directory.
    """
    p.mkdir(parents=True, exist_ok=True)
