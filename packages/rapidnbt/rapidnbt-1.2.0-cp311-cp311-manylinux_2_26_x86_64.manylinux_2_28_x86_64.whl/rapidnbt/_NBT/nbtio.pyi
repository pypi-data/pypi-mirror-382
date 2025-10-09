# Copyright © 2025 GlacieTeam.All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy
# of the MPL was not distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# SPDX-License-Identifier: MPL-2.0

import os
from typing import Union, Optional
from rapidnbt._NBT.compound_tag import CompoundTag
from rapidnbt._NBT.snbt_format import SnbtFormat
from rapidnbt._NBT.nbt_file_format import NbtFileFormat
from rapidnbt._NBT.nbt_compression_level import NbtCompressionLevel
from rapidnbt._NBT.nbt_compression_type import NbtCompressionType
from rapidnbt._NBT.nbt_file import NbtFile

def detect_content_format(
    content: Union[bytes, bytearray], strict_match_size: bool = True
) -> Optional[NbtFileFormat]:
    """
    Detect NBT format from binary content

    Args:
        content (bytes): Binary content to analyze
        strict_match_size (bool): Strictly match nbt content size (default: True)

    Returns:
        NbtFileFormat or None if format cannot be determined

    """

def detect_file_format(
    path: os.PathLike, file_memory_map: bool = False, strict_match_size: bool = True
) -> Optional[NbtFileFormat]:
    """
    Detect NBT format from a file

    Args:
        path (os.PathLike): Path to the file
        file_memory_map (bool): Use memory mapping for large files (default: False)
        strict_match_size (bool): Strictly match nbt content size (default: True)

    Returns:
        NbtFileFormat or None if format cannot be determined

    """

def detect_content_compression_type(
    content: Union[bytes, bytearray],
) -> NbtCompressionType:
    """
    Detect NBT format from binary content

    Args:
        content (bytes): Binary content to analyze

    Returns:
        NbtCompressionType

    """

def detect_file_compression_type(
    path: os.PathLike, file_memory_map: bool = False
) -> NbtCompressionType:
    """
    Detect NBT format from a file

    Args:
        path (os.PathLike): Path to the file
        file_memory_map (bool): Use memory mapping for large files (default: False)

    Returns:
        NbtCompressionType

    """

def dump(
    nbt: CompoundTag,
    path: os.PathLike,
    format: NbtFileFormat = NbtFileFormat.LITTLE_ENDIAN,
    compression_type: NbtCompressionType = NbtCompressionType.GZIP,
    compression_level: NbtCompressionLevel = NbtCompressionLevel.DEFAULT,
) -> bool:
    """
    Save CompoundTag to a file

    Args:
        nbt (CompoundTag): Tag to save
        path (os.PathLike): Output file path
        format (NbtFileFormat): Output format (default: LITTLE_ENDIAN)
        compression_type (CompressionType): Compression method (default: Gzip)
        compression_level (CompressionLevel): Compression level (default: Default)

    Returns:
        bool: True if successful, False otherwise

    """

def dump_snbt(
    nbt: CompoundTag,
    path: os.PathLike,
    format: SnbtFormat = SnbtFormat.Default,
    indent: int = 4,
) -> bool:
    """
    Save CompoundTag to SNBT (String NBT) file

    Args:
        nbt (CompoundTag): Tag to save
        path (os.PathLike): Output file path
        format (SnbtFormat): Output formatting style (default: Default)
        indent (int): Indentation level (default: 4)

    Returns:
        bool: True if successful, False otherwise

    """

def dumps(
    nbt: CompoundTag,
    format: NbtFileFormat = NbtFileFormat.LITTLE_ENDIAN,
    compression_type: NbtCompressionType = NbtCompressionType.GZIP,
    compression_level: NbtCompressionLevel = NbtCompressionLevel.DEFAULT,
) -> bytes:
    """
    Serialize CompoundTag to binary data

    Args:
        nbt (CompoundTag): Tag to serialize
        format (NbtFileFormat): Output format (default: LITTLE_ENDIAN)
        compression_type (CompressionType): Compression method (default: Gzip)
        compression_level (CompressionLevel): Compression level (default: Default)

    Returns:
        bytes: Serialized binary data

    """

def dumps_snbt(
    nbt: CompoundTag,
    format: SnbtFormat = SnbtFormat.Default,
    indent: int = 4,
) -> str:
    """
    Save CompoundTag to SNBT (String NBT) file

    Args:
        nbt (CompoundTag): Tag to save
        format (SnbtFormat): Output formatting style (default: Default)
        indent (int): Indentation level (default: 4)

    Returns:
        bool: SNBT string

    """

def dumps_base64(
    nbt: CompoundTag,
    format: NbtFileFormat = NbtFileFormat.LITTLE_ENDIAN,
    compression_type: NbtCompressionType = NbtCompressionType.GZIP,
    compression_level: NbtCompressionLevel = NbtCompressionLevel.DEFAULT,
) -> str:
    """
    Serialize CompoundTag to Base64 string

    Args:
        nbt (CompoundTag): Tag to serialize
        format (NbtFileFormat): Output format (default: LITTLE_ENDIAN)
        compression_type (CompressionType): Compression method (default: Gzip)
        compression_level (CompressionLevel): Compression level (default: Default)

    Returns:
        str: Base64-encoded NBT data

    """

def load(
    path: os.PathLike,
    format: Optional[NbtFileFormat] = None,
    file_memory_map: bool = False,
    strict_match_size: bool = True,
) -> Optional[CompoundTag]:
    """
    Parse CompoundTag from a file

    Args:
        path (os.PathLike): Path to NBT file
        format (NbtFileFormat, optional): Force specific format (autodetect if None)
        file_memory_map (bool): Use memory mapping for large files (default: False)
        strict_match_size (bool): Strictly match nbt content size (default: True)

    Returns:
        CompoundTag or None if parsing fails
    """

def load_snbt(path: os.PathLike) -> Optional[CompoundTag]:
    """
    Parse CompoundTag from SNBT (String NBT) file

    Args:
        path (os.PathLike): Path to SNBT file

    Returns:
        CompoundTag or None if parsing fails
    """

def loads(
    content: Union[bytes, bytearray],
    format: Optional[NbtFileFormat] = None,
    strict_match_size: bool = True,
) -> Optional[CompoundTag]:
    """
    Parse CompoundTag from binary data

    Args:
        content (bytes): Binary NBT data
        format (NbtFileFormat, optional): Force specific format (autodetect if None)
        strict_match_size (bool): Strictly match nbt content size (default: True)

    Returns:
        CompoundTag or None if parsing fails
    """

def loads_base64(
    content: str,
    format: Optional[NbtFileFormat] = None,
    strict_match_size: bool = True,
) -> Optional[CompoundTag]:
    """
    Parse CompoundTag from Base64-encoded NBT

    Args:
        content (str): Base64-encoded NBT data
        format (NbtFileFormat, optional): Force specific format (autodetect if None)
        strict_match_size (bool): Strictly match nbt content size (default: True)

    Returns:
        CompoundTag or None if parsing fails
    """

def loads_snbt(
    content: str, parsed_length: Optional[int] = None
) -> Optional[CompoundTag]:
    """
    Parse CompoundTag from SNBT (String NBT) file

    Args:
        content (str): SNBT content

    Returns:
        CompoundTag or None if parsing fails
    """

def open(path: os.PathLike) -> Optional[NbtFile]:
    """
    Open a NBT file (auto detect)

    Args:
        path (os.PathLike): NBT file path

    Returns:
        Optional[NbtFile]: NbtFile or None if open failed
    """

def validate_content(
    content: Union[bytes, bytearray],
    format: NbtFileFormat = NbtFileFormat.LITTLE_ENDIAN,
    strict_match_size: bool = True,
) -> bool:
    """
    Validate NBT binary content

    Args:
        content (bytes): Binary data to validate
        format (NbtFileFormat): Expected format (default: LITTLE_ENDIAN)
        strict_match_size (bool): Strictly match nbt content size (default: True)

    Returns:
        bool: True if valid NBT, False otherwise
    """

def validate_file(
    path: os.PathLike,
    format: NbtFileFormat = NbtFileFormat.LITTLE_ENDIAN,
    file_memory_map: bool = False,
    strict_match_size: bool = True,
) -> bool:
    """
    Validate NBT file

    Args:
        path (os.PathLike): File path to validate
        format (NbtFileFormat): Expected format (default: LITTLE_ENDIAN)
        file_memory_map (bool): Use memory mapping (default: False)
        strict_match_size (bool): Strictly match nbt content size (default: True)

    Returns:
        bool: True if valid NBT file, False otherwise
    """
