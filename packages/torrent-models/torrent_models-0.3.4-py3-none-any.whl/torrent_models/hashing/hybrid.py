"""
Hybrid v1/v2 torrent creation

This is not a straightforward combination of v1 and v2 hashing
since each version of torrent has different optimization requirements.

Since v1 is just a linear set of hashes, and the pieces are much larger units,
we can read a larger buffer and feed the whole thing into a hashing process at once.
v2 works on 16KiB chunks always, so the tradeoff of reading and processing time is a bit different.

Hybrid torrents require us to do both, as well as generate padfiles,
so we use routines from the v1 and v2 but build on top of them.
"""

from functools import cached_property
from itertools import count
from multiprocessing.pool import AsyncResult
from multiprocessing.pool import Pool as PoolType
from pathlib import Path
from typing import cast, overload

from pydantic import PrivateAttr, field_validator

from torrent_models.const import BLOCK_SIZE
from torrent_models.hashing.base import Chunk, Hash
from torrent_models.hashing.v1 import V1Hasher
from torrent_models.hashing.v2 import V2Hasher, sort_v2
from torrent_models.types.v1 import FileItem
from torrent_models.types.v2 import PieceLayers, V2PieceLength


def add_padfiles(files: list[FileItem], piece_length: int) -> list[FileItem]:
    """
    Modify a v1 file list to intersperse .pad files
    """
    padded = []
    for f in files:
        padded.append(f)
        if f.attr in (b"p", "p"):
            continue
        if (remainder := f.length % piece_length) != 0:
            pad_length = piece_length - remainder
            pad = FileItem(length=pad_length, path=[".pad", str(pad_length)], attr=b"p")
            padded.append(pad)
    return padded


class HybridHasher(V1Hasher, V2Hasher):
    piece_length: V2PieceLength
    read_size: V2PieceLength | None = None

    _v1_chunks: list[Chunk] = PrivateAttr(default_factory=list)
    _last_path: Path | None = None
    _v1_counter: count = PrivateAttr(default_factory=count)

    @field_validator("paths", mode="after")
    def sort_paths(cls, value: list[Path]) -> list[Path]:
        """
        v1 torrents have arbitrary file sorting,
        but we mimick libtorrent/qbittorrent's sort order for consistency's sake
        """
        value = sort_v2(value)
        return value

    @cached_property
    def blocks_per_piece(self) -> int:
        return int(self.piece_length / BLOCK_SIZE)

    @cached_property
    def total_hashes(self) -> int:
        return self._v2_total_hashes() + self._v1_total_hashes_hybrid()

    @overload
    def update(self, chunk: Chunk, pool: PoolType) -> list[AsyncResult]: ...

    @overload
    def update(self, chunk: Chunk, pool: None) -> list[Hash]: ...

    def update(self, chunk: Chunk, pool: PoolType | None = None) -> list[AsyncResult] | list[Hash]:
        res = self._update_v2(chunk, pool)
        res.extend(self._update_v1(chunk, pool))  # type: ignore
        return res

    @overload
    def _on_file_end(self, pool: PoolType) -> list[AsyncResult]: ...

    @overload
    def _on_file_end(self, pool: None) -> list[Hash]: ...

    def _on_file_end(self, pool: PoolType | None) -> list[AsyncResult] | list[Hash]:
        """Pad and submit buffer"""
        if len(self._buffer) == 0:
            return []
        self._buffer.extend(bytes(self.piece_length - len(self._buffer)))
        self._last_path = cast(Path, self._last_path)
        chunk = Chunk.model_construct(
            idx=next(self._v1_counter), path=self._last_path, chunk=bytes(self._buffer)
        )
        self._buffer = bytearray()
        if pool:
            return [pool.apply_async(self._hash_v1, args=(chunk, self.path_root))]
        else:
            return [self._hash_v1(chunk, self.path_root)]

    @overload
    def _after_read(self, pool: PoolType) -> list[AsyncResult]: ...

    @overload
    def _after_read(self, pool: None) -> list[Hash]: ...

    def _after_read(self, pool: PoolType | None) -> list[AsyncResult] | list[Hash]:
        """Submit any remaining v1 pieces from the last file"""
        res = self._on_file_end(pool)
        return res

    def split_v1_v2(
        self,
        hashes: list[Hash],
    ) -> tuple[PieceLayers, list[bytes]]:
        """Split v1 and v2 hashes, returning sorted v1 pieces and v2 piece layers"""
        v1_pieces = [h for h in hashes if h.type == "v1_piece"]
        v1_pieces = sorted(v1_pieces, key=lambda h: h.idx)
        v1_pieces = [h.hash for h in v1_pieces]

        v2_leaf_hashes = [h for h in hashes if h.type == "block"]
        trees = self.finish_trees(v2_leaf_hashes)
        layers = PieceLayers.from_trees(trees, self.path_root)
        return layers, v1_pieces
