"""
Convenience class used when creating a new torrent.

The :class:`.TorrentCreate` class provides some convenience fields
that allows some common fields to be declared in a version-agnostic way
at the top level, rather than nested within the infodict.
"""

import multiprocessing as mp
from pathlib import Path
from typing import Any, Self, cast

from pydantic import Field, model_validator

from torrent_models import Torrent, TorrentVersion
from torrent_models.compat import get_size
from torrent_models.const import DEFAULT_TORRENT_CREATOR, EXCLUDE_FILES
from torrent_models.hashing import HybridHasher, V1Hasher, add_padfiles
from torrent_models.hashing.v1 import sort_v1
from torrent_models.info import InfoDictHybrid, InfoDictHybridCreate, InfoDictV1, InfoDictV2
from torrent_models.torrent import TorrentBase
from torrent_models.types import (
    AbsPath,
    ByteStr,
    FileItem,
    TrackerFields,
    V1PieceLength,
    V2PieceLength,
)
from torrent_models.types.v2 import FileTree, PieceLayers


class TorrentCreate(TorrentBase):
    """
    A programmatically created torrent that may not have its hashes computed yet.

    Torrents may be created *either* by passing an info dict with all details,
    (with or without piece hashes), *or* by using a handful of convenience fields.
    E.g. rather than needing to pass a fully instantiated file tree,
    one can just pass a list of files to ``files``
    """

    _EXCLUDE = {
        "paths": True,
        "path_root": True,
        "trackers": True,
        "piece_length": True,
        "info": {"meta_version", "files", "file_tree", "piece_length"},
        "piece_layers": True,
    }
    """
    Exclude from model dumps when creating internal model dumps when generating.
    ie. because they are transformed by creation
    """

    # make parent types optional
    announce: ByteStr | None = None
    created_by: ByteStr | None = Field(DEFAULT_TORRENT_CREATOR, alias="created by")

    # convenience fields
    info: InfoDictHybridCreate = Field(default_factory=InfoDictHybridCreate)  # type: ignore
    paths: list[Path] | None = Field(
        None,
        description="""
        Convenience field for creating torrents from lists of files.
        Can be either relative or absolute.
        Paths must be located beneath the path root, passed either explicitly or using
        cwd (default).
        If absolute, paths are made relative to the path root.
        """,
    )
    path_root: AbsPath = Field(
        default_factory=Path, description="Path to interpret paths relative to"
    )

    trackers: list[ByteStr] | list[list[ByteStr]] | None = Field(
        None,
        description="Convenience method for declaring tracker lists."
        "If a flat list, put each tracker in a separate tier."
        "Otherwise, sublists indicate tiers.",
    )
    piece_length: V1PieceLength | V2PieceLength | None = Field(
        None, description="Convenience method for passing piece length"
    )
    similar: list[bytes] | None = Field(
        None, description="Infohashes of other torrents that might contain overlapping files"
    )

    @model_validator(mode="after")
    def no_duplicated_params(self) -> Self:
        """
        Ensure that values that can be set from the top level convenience fields aren't doubly set,

        We don't set the accompanying values in the infodict on instantiation because
        this object is intended to be a programmatic constructor object,
        so we expect these values to change and don't want to have to worry about
        state consistency in it -
        all values are gathered and validated when the torrent is generated.
        """
        if self.paths:
            assert not self.info.files, "Can't pass both paths and info.files"
            assert not self.info.file_tree, "Can't pass both paths and info.file_tree"
        if self.trackers:
            assert not self.announce, "Can't pass both trackers and announce"
            assert not self.announce_list, "Can't pass both trackers and announce_list"
        if self.piece_length:
            assert not self.info.piece_length, "Can't pass both piece_length and info.piece_length"
        return self

    @model_validator(mode="after")
    def name_from_path_root(self) -> Self:
        """If `name` is not provided, infer it from the path root"""
        if not self.info.name:
            self.info.name = self.path_root.name
        return self

    def generate(
        self, version: TorrentVersion | str, n_processes: int | None = 1, progress: bool = False
    ) -> Torrent:
        """
        Generate a torrent file, hashing its pieces and transforming convenience values
        to valid torrent values.
        """
        if isinstance(version, str):
            version = TorrentVersion.__members__[version]

        if n_processes is None:
            n_processes = mp.cpu_count()

        if version == TorrentVersion.v1:
            return self._generate_v1(n_processes, progress)
        elif version == TorrentVersion.v2:
            return self._generate_v2(n_processes, progress)
        elif version == TorrentVersion.hybrid:
            return self._generate_hybrid(n_processes, progress)
        else:
            raise ValueError(f"Unknown torrent version: {version}")

    def generate_libtorrent(
        self,
        version: TorrentVersion | str,
        output: Path | None = None,
        bencode: bool = False,
        progress: bool = False,
    ) -> dict | bytes:
        from torrent_models.libtorrent import create_from_model

        return create_from_model(
            self, version=version, progress=progress, output=output, bencode=bencode
        )

    def _generate_common(self) -> dict:
        # dump just the fields we want to have in the final torrent,
        # excluding top-level convenience fields (set in the generate methods),
        # and hash values which are created during generation
        dumped = self.model_dump(
            exclude_none=True,
            exclude=self._EXCLUDE,  # type: ignore
            by_alias=False,
        )

        dumped["info"]["piece_length"] = self._get_piece_length()
        if "similar" in dumped:
            dumped["info"]["similar"] = dumped["similar"]
            del dumped["similar"]
        dumped.update(self.get_trackers())
        return dumped

    def _generate_v1(self, n_processes: int, progress: bool = False, **kwargs: Any) -> Torrent:
        dumped = self._generate_common()

        paths = self.get_paths(clean=True, v1_order=True)
        file_items = self._get_v1_file_items(paths)

        if not self.info.files:
            if len(file_items) == 1:
                dumped["info"]["name"] = file_items[0].path[-1]
                dumped["info"]["length"] = file_items[0].length
            else:
                dumped["info"]["files"] = file_items

        if "pieces" not in dumped["info"]:
            hasher = V1Hasher(
                paths=paths,
                piece_length=self._get_piece_length(),
                read_size=self._get_piece_length(),
                path_root=self.path_root,
                n_processes=n_processes,
                progress=progress,
                **kwargs,
            )
            hashes = hasher.process()
            hashes = [hash.hash for hash in sorted(hashes, key=lambda x: x.idx)]
            dumped["info"]["pieces"] = hashes
        info = InfoDictV1(**dumped["info"])
        del dumped["info"]
        return Torrent(info=info, **dumped)

    def _generate_v2(self, n_processes: int, progress: bool = False) -> Torrent:
        dumped = self._generate_common()
        paths = self.get_paths(clean=True, v1_order=False)

        if "piece_layers" not in dumped or "file_tree" not in dumped["info"]:
            piece_layers = PieceLayers.from_paths(
                paths=paths,
                piece_length=dumped["info"]["piece_length"],
                path_root=self.path_root,
                n_processes=n_processes,
                progress=progress,
            )
            dumped["piece_layers"] = piece_layers.piece_layers
            dumped["info"]["file_tree"] = piece_layers.file_tree.tree

        info = InfoDictV2(**dumped["info"])
        del dumped["info"]
        return Torrent(info=info, **dumped)

    def _generate_hybrid(self, n_processes: int, progress: bool = False) -> Torrent:
        dumped = self._generate_common()

        # Gather paths

        if (self.info.files or self.info.length) and self.info.file_tree:
            # check for inconsistent paths in v1 and v2 if both are present
            v1_paths = self._get_v1_paths()
            v1_items = self._get_v1_file_items(v1_paths)
            v2_paths = [Path(path) for path in FileTree.flatten_tree(self.info.file_tree)]
            if not len(v1_paths) == len(v2_paths) and not all(
                [v1p == v2p for v1p, v2p in zip(v1_paths, v2_paths)]
            ):
                raise ValueError(
                    "Both v1 files and v2 file tree present, but have inconsistent paths!"
                )
            paths = v2_paths
        else:
            paths = self.get_paths(clean=True, v1_order=False)
            # v1 files
            v1_items = self._get_v1_file_items(paths)

        # add padding to the v1 files
        v1_items = add_padfiles(v1_items, dumped["info"]["piece_length"])

        hasher = HybridHasher(
            paths=paths,
            path_root=self.path_root,
            piece_length=self.piece_length,
            read_size=self.piece_length,
            n_processes=n_processes,
            progress=progress,
        )
        hashes = hasher.process()
        piece_layers, v1_pieces = hasher.split_v1_v2(hashes)
        dumped["piece layers"] = piece_layers.piece_layers
        dumped["info"]["file tree"] = piece_layers.file_tree.tree
        dumped["info"]["pieces"] = v1_pieces
        if len(v1_items) == 1:
            dumped["info"]["name"] = v1_items[0].path[-1]
            dumped["info"]["length"] = v1_items[0].length
        else:
            dumped["info"]["files"] = v1_items

        info = InfoDictHybrid(**dumped["info"])
        del dumped["info"]
        return Torrent(info=info, **dumped)

    def get_paths(self, clean: bool = True, v1_order: bool = False) -> list[Path]:
        """
        Get paths specified in one of potentially several ways

        In order (first match is returned):
        - paths set in top level `paths` field
        - v2 file tree, if present
        - v1 `files`, if present
        - v1 `name`, if present with `length` set
        - iterate the files beneath the :attr:`.path_root`

        Args:
            clean (bool): clean and sort the files
            v1_order (bool): sort files in v1 order -
                first top-level files, then files in directories
                in case-sensitive alphanumeric order within those categories.
        """
        if self.paths:
            paths = self.paths.copy()
        elif self.info.file_tree is not None:
            tree = self.flat_files
            assert tree is not None
            paths = [Path(t) for t in tree]
        else:
            try:
                paths = self._get_v1_paths()
            except ValueError:
                # no V1 paths, get files beneath base-path
                paths = list(self.path_root.rglob("*"))

        if not paths:
            raise ValueError("No paths provided, and nothing found within path root!")

        if clean:
            paths = clean_files(paths, relative_to=self.path_root, v1=v1_order)
        return paths

    def _get_v1_paths(self, paths: list[Path] | None = None, v1_only: bool = False) -> list[Path]:
        if paths:
            files = paths
        elif self.paths:
            files = self.paths
        elif self.info.files:
            files = [Path(*f.path) for f in self.info.files]
        elif self.info.length and self.info.name is not None:
            files = [Path(self.info.name)]
        else:
            raise ValueError("paths not provided, and info.files and info.length are unset!")

        files = clean_files(files, relative_to=self.path_root, v1=v1_only)
        return files

    def _get_v1_file_items(self, paths: list[Path]) -> list[FileItem]:
        items = [FileItem(path=list(f.parts), length=get_size(self.path_root / f)) for f in paths]
        return items

    def get_trackers(
        self,
    ) -> TrackerFields:
        # FIXME: hideous
        if self.trackers:
            if isinstance(self.trackers[0], list):

                self.trackers = cast(list[list[str]], self.trackers)
                if len(self.trackers[0]) == 1 and len(self.trackers[0][0]) == 1:
                    return {"announce": self.trackers[0][0]}
                else:
                    return {"announce": self.trackers[0][0], "announce-list": self.trackers}
            else:
                self.trackers = cast(list[str], self.trackers)
                if len(self.trackers) == 1:
                    return {"announce": self.trackers[0]}
                else:
                    return {
                        "announce": self.trackers[0],
                        "announce-list": [[t] for t in self.trackers],
                    }
        else:
            trackers_: TrackerFields = {}
            if self.announce is not None:
                trackers_["announce"] = self.announce

            if self.announce_list is not None:
                trackers_["announce-list"] = self.announce_list

            return trackers_

    def _get_piece_length(self) -> int:
        piece_length = self.piece_length if self.piece_length else self.info.piece_length
        if piece_length is None:
            raise ValueError("No piece length provided!")
        return piece_length


def list_files(path: Path | str) -> list[Path]:
    """
    Recursively list files relative to path, sorting, excluding known system files
    """
    path = Path(path)
    if path.is_file():
        return [path]

    paths = list(path.rglob("*"))

    return clean_files(paths, path)


def clean_files(paths: list[Path], relative_to: Path, v1: bool = False) -> list[Path]:
    """
    Remove system files, and make paths relative to some directory root
    """
    cleaned = []
    for f in paths:
        if f.is_absolute():
            abs_f = f
            # no absolute paths in the torrent plz
            rel_f = f.relative_to(relative_to)
        else:
            abs_f = relative_to / f
            rel_f = f
        if not abs_f.exists():
            raise FileNotFoundError(
                f"File {abs_f} does not exist for path {f} relative to {relative_to}"
            )
        if abs_f.is_file() and f.name not in EXCLUDE_FILES:
            cleaned.append(rel_f)
    cleaned = sort_v1(cleaned) if v1 else sorted(cleaned, key=lambda f: f.as_posix())
    return cleaned
