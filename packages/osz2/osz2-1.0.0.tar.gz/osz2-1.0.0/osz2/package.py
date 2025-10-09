
from osz2.xxtea_reader import XXTEAReader
from osz2.xxtea import XXTEA
from typing import Dict, List

from .types import MetadataType
from .file import File
from .utils import *

import datetime
import hashlib
import struct
import io

class Osz2Package:
    def __init__(self, reader: io.BufferedReader, metadata_only: bool = False) -> None:
        self.metadata: Dict[MetadataType, str] = {}
        self.filenames: Dict[str, int] = {}
        self.files: List[File] = []
        self.key: bytes = b""

        self.metadata_hash: bytes = b""
        self.file_info_hash: bytes = b""
        self.full_body_hash: bytes = b""

        # Always read the header when initializing
        self.read_header(reader)

        if not metadata_only:
            # Read the files if requested
            self.read_files(reader)

    @classmethod
    def from_file(cls, path: str, metadata_only: bool = False) -> "Osz2Package":
        with open(path, "rb") as f:
            return cls(f, metadata_only)

    @classmethod
    def from_bytes(cls, data: bytes, metadata_only: bool = False) -> "Osz2Package":
        with io.BytesIO(data) as f:
            return cls(f, metadata_only)

    def read_header(self, reader: io.BufferedReader) -> None:
        magic = reader.read(3)
        assert magic == b"\xECHO", "Not a valid osz2 package" # nice one echo

        # Seek 17 bytes from the current position
        # to skip unused version byte & IV data
        reader.seek(17, 1)

        self.metadata_hash = reader.read(16)
        self.file_info_hash = reader.read(16)
        self.full_body_hash = reader.read(16)

        self.read_metadata(reader)
        self.read_file_names(reader)

        assert MetadataType.Creator in self.metadata, "Metadata is missing creator"
        assert MetadataType.BeatmapSetID in self.metadata, "Metadata is missing beatmapset ID"

        creator = self.metadata[MetadataType.Creator]
        beatmapset_id = self.metadata[MetadataType.BeatmapSetID]

        seed = f"{creator}yhxyfjo5{beatmapset_id}"
        self.key = hashlib.md5(seed.encode()).digest()

    def read_metadata(self, reader: io.BufferedReader) -> None:
        buffer = reader.read(4)
        count = struct.unpack("<I", buffer)[0]

        for _ in range(count):
            buf = reader.read(2)
            meta_type = struct.unpack("<H", buf)[0]
            meta_value = read_string(reader)

            self.metadata[MetadataType(meta_type)] = meta_value

            buffer += buf
            buffer += write_string(meta_value)

        hash = compute_osz_hash(buffer, count*3, 0xA7)
        assert hash == self.metadata_hash, f"Hash mismatch, expected: {hash}, got: {self.metadata_hash}"

    def read_file_names(self, reader: io.BufferedReader) -> None:
        buffer = reader.read(4)
        count = struct.unpack("<I", buffer)[0]

        for _ in range(count):
            filename = read_string(reader)
            beatmap_id = struct.unpack("<I", reader.read(4))[0]
            self.filenames[filename] = beatmap_id

        for name, id in self.filenames.items():
            print(f"{name}: {id}")

    def read_files(self, reader: io.BufferedReader) -> None:
        reader.seek(64, 1)

        # Read encrypted i32 length
        length = struct.unpack("<I", reader.read(4))[0]

        # Decode length by encrypted length
        for i in range(0, 16, 2):
            length -= self.file_info_hash[i] | (self.file_info_hash[i+1] << 17)

        file_info = reader.read()
        file_offset = reader.seek(0, 1)
        total_size = reader.seek(0, 2)
        reader.seek(file_offset, 0)

        key = bytes_to_uint32_array(self.key)
        xxtea_reader = XXTEAReader(io.BytesIO(file_info), key)

        # Parse file info using xxtea stream and proceed to read file contents
        self.parse_files(xxtea_reader, file_offset, total_size)

    def parse_files(self, reader: XXTEAReader, file_offset: int, total_size: int) -> None:
        count = struct.unpack("<I", reader.read(4))[0]
        curr_offset = struct.unpack("<I", reader.read(4))[0]

        for i in range(count):
            filename = read_string(reader)
            file_hash = reader.read(16)

            date_created_binary = struct.unpack("<Q", reader.read(8))[0]
            date_modified_binary = struct.unpack("<Q", reader.read(8))[0]

            # Convert from .NET DateTime.ToBinary() format
            date_created = datetime_from_binary(date_created_binary)
            date_modified = datetime_from_binary(date_modified_binary)

            next_offset = 0
            if count > i + 1:
                next_offset = struct.unpack("<I", reader.read(4))[0]
            else:
                # This is the last file, so we calculate size differently
                # using total file size minus file offset
                next_offset = total_size - file_offset

            file_length = next_offset - curr_offset

            file = File(
                filename,
                curr_offset,
                file_length,
                file_hash,
                date_created,
                date_modified,
                content=bytes(),
            )
            self.files.append(file)
            curr_offset = next_offset

        # After reading the file info, read the actual file contents
        for i in range(len(self.files)):
            length = struct.unpack("<I", reader.read(4))[0]
            self.files[i].content = reader.read(length)
