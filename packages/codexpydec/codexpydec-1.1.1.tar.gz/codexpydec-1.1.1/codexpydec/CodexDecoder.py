from functools import lru_cache
from pathlib import Path
import zlib
from .CodexSchema import get_compatible_schema

try:
    import liblzfse

    LIBLZFSE_AVAILABLE = True
except ImportError:
    LIBLZFSE_AVAILABLE = False


def _decompress_zlib(block: bytes) -> bytes:
    return zlib.decompress(block[:-4], wbits=-15)


def _decompress_lzfse(block: bytes) -> bytes:
    return liblzfse.decompress(block[:-4])


class CodexDecoder:
    """
    Decoder for the Codex archive format. Initialize with a path to the Codex
    archive without the shard number or file extension.
    """

    def __init__(self, archive_path: Path | str):

        archive_path = Path(archive_path)
        file_handle = open(
            archive_path.with_suffix(archive_path.suffix + ".000.codex"), "rb"
        )
        assert file_handle.read(4).decode("utf-8") == "CODX"

        major = int.from_bytes(file_handle.read(1), byteorder="little", signed=False)
        minor = int.from_bytes(file_handle.read(1), byteorder="little", signed=False)
        self.schema = get_compatible_schema(major, minor)
        assert self.schema is not None

        self.pointer_length = self.schema["pointerLength"]
        self.shard_pointer_length = self.schema["shardPointerLength"]

        self.compression_algorithm = self._read_string_field(
            self.schema["compressionAlgorithm"], file_handle
        )
        if self.compression_algorithm == "ZLIB":
            self._decompress = _decompress_zlib
        elif self.compression_algorithm == "LZFS":
            if not LIBLZFSE_AVAILABLE:
                raise ImportError(
                    "This archive is compressed with LZFSE but pyliblzfse is not installed. Install with: pip install codexpydec[lzfse]"
                )
            self._decompress = _decompress_lzfse
        else:
            raise ValueError(
                f"Unrecognized compression algorithm: {self.compression_algorithm}"
            )

        self.library_id = self._read_string_field(self.schema["libraryID"], file_handle)
        self.library_name = self._read_string_field(
            self.schema["libraryName"], file_handle
        )
        self.library_license = self._read_string_field(
            self.schema["libraryLicense"], file_handle
        )
        self.library_version = self._read_integer_field(
            self.schema["libraryVersion"], file_handle
        )
        self.patched_version = self._read_integer_field(
            self.schema["patchedVersion"], file_handle
        )
        self.n_catalog_entries = self._read_integer_field(
            self.schema["nCatalogEntries"], file_handle
        )
        self.n_library_entries = self._read_integer_field(
            self.schema["nLibraryEntries"], file_handle
        )
        self.n_catalog_blocks = self._read_integer_field(
            self.schema["nCatalogBlocks"], file_handle
        )
        self.n_library_blocks = self._read_integer_field(
            self.schema["nLibraryBlocks"], file_handle
        )
        self.n_catalog_shards = self._read_integer_field(
            self.schema["nCatalogShards"], file_handle
        )
        self.n_library_shards = self._read_integer_field(
            self.schema["nLibraryShards"], file_handle
        )
        self.inventory_pointer = self._read_integer_field(
            self.schema["inventoryPointer"], file_handle
        )
        self.catalog_index_pointer = self._read_integer_field(
            self.schema["catalogIndexPointer"], file_handle
        )
        self.library_index_pointer = self._read_integer_field(
            self.schema["libraryIndexPointer"], file_handle
        )

        self.n_shards = self.n_catalog_shards + self.n_library_shards + 1
        self.shard_paths = []
        for shard_number in range(self.n_shards):
            zero_padded_shard_number = str(shard_number).zfill(3)
            shard_extension = f".{zero_padded_shard_number}.codex"
            shard_path = archive_path.with_suffix(archive_path.suffix + shard_extension)
            self.shard_paths.append(Path(shard_path))

        self.library_block_sizes = self._determine_block_sizes(
            self.n_library_entries, self.n_library_blocks
        )

        self.catalog_index = self._load_index(
            file_handle, self.catalog_index_pointer, self.n_catalog_blocks
        )
        assert len(self.catalog_index) == (self.n_catalog_blocks + 1)

        self.library_index = self._load_index(
            file_handle, self.library_index_pointer, self.n_library_blocks
        )
        assert len(self.library_index) == (self.n_library_blocks + 1)

        file_handle.close()

        self.footer_text = self._load_footer_text()

    def __iter__(self):
        for block_number in range(self.n_catalog_blocks):
            catalog_block = self._get_catalog_block(block_number)
            entry_count = int.from_bytes(
                catalog_block[: self.pointer_length], byteorder="little", signed=False
            )
            for entry_index in range(entry_count):
                entry_bytes = self._extract_from_data(entry_index, catalog_block)
                entry_title = entry_bytes[self.pointer_length :].decode("utf-8")
                if "\x00" in entry_title:
                    continue
                entry_number = int.from_bytes(
                    entry_bytes[: self.pointer_length], byteorder="little", signed=False
                )
                article = self.get_article(entry_title, entry_number)
                if article is None:
                    continue
                yield entry_number, article

    def _open_file(self, shard_number: int):
        assert shard_number < len(self.shard_paths)
        return open(self.shard_paths[shard_number], "rb")

    def _read_integer_field(self, field_schema: dict, file_handle) -> int:
        file_handle.seek(field_schema["offset"])
        field_bytes = file_handle.read(field_schema["length"])
        return int.from_bytes(field_bytes, byteorder="little", signed=False)

    def _read_string_field(self, field_schema: dict, file_handle) -> str:
        file_handle.seek(field_schema["offset"])
        field_bytes = file_handle.read(field_schema["length"])
        return field_bytes.rstrip(b"\x00").decode("utf-8")

    def _determine_block_sizes(self, n_entries: int, n_blocks: int) -> list[int]:
        assert n_entries >= n_blocks
        block_sizes = [n_entries // n_blocks] * n_blocks
        remainder = n_entries % n_blocks
        if remainder == 0:
            return block_sizes
        for i in range(remainder):
            block_sizes[i] += 1
        return block_sizes

    def _load_index(self, file_handle, index_offset: int, n_blocks: int):
        index_item_length = self.shard_pointer_length + self.pointer_length
        file_handle.seek(index_offset)
        index_length = (n_blocks + 1) * index_item_length
        index_bytes = file_handle.read(index_length)
        assert len(index_bytes) == index_length
        index = []
        for start_index in range(0, index_length, index_item_length):
            end_index = start_index + index_item_length
            shard_number = int.from_bytes(
                index_bytes[start_index : start_index + 1],
                byteorder="little",
                signed=False,
            )
            shard_pointer = int.from_bytes(
                index_bytes[start_index + 1 : end_index],
                byteorder="little",
                signed=False,
            )
            index.append((shard_number, shard_pointer))
        return index

    def _load_footer_text(self):
        footer_text = self.get_article_by_entry_number(0)
        if footer_text is None:
            return ""
        version_string = str(self.library_version)
        if len(version_string) == 8:
            snapshot_date = (
                f"{version_string[0:4]}-{version_string[4:6]}-{version_string[6:8]}"
            )
        else:
            snapshot_date = "unknown"
        footer_text = footer_text.replace("«SNAPSHOT_DATE»", snapshot_date)
        horizontal_rule = "_" * 70
        return f"\n{horizontal_rule}\n\n{footer_text}"

    def _locate_article(self, entry_number: int) -> tuple[int, int]:
        sum_of_previous_block_sizes = 0
        for block_number, block_size in enumerate(self.library_block_sizes):
            if entry_number < (block_size + sum_of_previous_block_sizes):
                return block_number, entry_number - sum_of_previous_block_sizes
            sum_of_previous_block_sizes += block_size
        raise ValueError("Invalid entry number")

    def _retrieve_article(self, entry_number: int) -> bytes:
        assert entry_number >= 0 and entry_number < self.n_library_entries
        block_number, article_number = self._locate_article(entry_number)
        block = self._get_library_block(block_number)
        article_bytes = self._extract_from_data(article_number, block)
        return article_bytes

    @lru_cache(maxsize=16)
    def _get_catalog_block(self, block_number: int) -> bytes:
        shard_number, shard_pointer = self.catalog_index[block_number]
        next_shard_number, next_shard_pointer = self.catalog_index[block_number + 1]
        file_handle = self._open_file(shard_number)
        file_handle.seek(shard_pointer)
        if shard_number == next_shard_number:
            block_length = next_shard_pointer - shard_pointer
            catalog_block = file_handle.read(block_length)
        else:
            catalog_block = file_handle.read()
        return self._decompress(catalog_block)

    @lru_cache(maxsize=16)
    def _get_library_block(self, block_number: int) -> bytes:
        shard_number, shard_pointer = self.library_index[block_number]
        next_shard_number, next_shard_pointer = self.library_index[block_number + 1]
        file_handle = self._open_file(shard_number)
        file_handle.seek(shard_pointer)
        if shard_number == next_shard_number:
            block_length = next_shard_pointer - shard_pointer
            library_block = file_handle.read(block_length)
        else:
            library_block = file_handle.read()
        return self._decompress(library_block)

    def _recursive_catalog_search(
        self, search_query: str, low_index: int, high_index: int, prefix_match: bool
    ) -> int | None:
        if low_index > high_index:
            return None
        middle_catalog_block_index = (low_index + high_index) // 2
        catalog_block = self._get_catalog_block(middle_catalog_block_index)
        first_entry_bytes = self._extract_from_data(0, catalog_block)
        first_entry_title = first_entry_bytes[self.pointer_length :].decode("utf-8")
        first_entry_title_lower = first_entry_title.lower()
        if prefix_match and first_entry_title_lower.startswith(search_query):
            return middle_catalog_block_index
        if search_query < first_entry_title_lower:
            if middle_catalog_block_index < 1:
                return None
            return self._recursive_catalog_search(
                search_query, low_index, middle_catalog_block_index - 1, prefix_match
            )
        entry_count = int.from_bytes(
            catalog_block[: self.pointer_length], byteorder="little", signed=False
        )
        last_entry_bytes = self._extract_from_data(entry_count - 1, catalog_block)
        last_entry_title = last_entry_bytes[self.pointer_length :].decode("utf-8")
        last_entry_title_lower = last_entry_title.lower()
        if prefix_match and last_entry_title_lower.startswith(search_query):
            return middle_catalog_block_index
        if search_query > last_entry_title_lower:
            return self._recursive_catalog_search(
                search_query, middle_catalog_block_index + 1, high_index, prefix_match
            )
        return middle_catalog_block_index

    def _extract_from_data(self, chunk_number: int, data: bytes) -> bytes:
        chunk_count = int.from_bytes(
            data[: self.pointer_length], byteorder="little", signed=False
        )
        if chunk_number >= chunk_count:
            raise ValueError("Invalid chunk number")
        header_length = chunk_count * self.pointer_length
        chunk_start_position = header_length
        chunk_end_position = header_length
        if chunk_number > 0:
            chunk_index_start_position = chunk_number * self.pointer_length
            chunk_start_position += int.from_bytes(
                data[
                    chunk_index_start_position : chunk_index_start_position
                    + self.pointer_length
                ],
                byteorder="little",
                signed=False,
            )
        if chunk_number < chunk_count - 1:
            chunk_index_end_position = (chunk_number + 1) * self.pointer_length
            chunk_end_position += int.from_bytes(
                data[
                    chunk_index_end_position : chunk_index_end_position
                    + self.pointer_length
                ],
                byteorder="little",
                signed=False,
            )
        else:
            chunk_end_position = None
        return data[chunk_start_position:chunk_end_position]

    def _find_article(self, target_title: str) -> int | None:
        if len(target_title) == 0:
            return None
        if self.n_catalog_blocks == 1:
            block_number = 0
        else:
            block_number = self._recursive_catalog_search(
                target_title.lower(), 0, self.n_catalog_blocks - 1, prefix_match=False
            )
        if block_number is None:
            return None
        catalog_block = self._get_catalog_block(block_number)
        entry_count = int.from_bytes(
            catalog_block[: self.pointer_length], byteorder="little", signed=False
        )
        for entry_index in range(entry_count):
            entry_bytes = self._extract_from_data(entry_index, catalog_block)
            entry_title = entry_bytes[self.pointer_length :].decode("utf-8")
            if target_title == entry_title.split("\x00", maxsplit=1)[0]:
                entry_number = int.from_bytes(
                    entry_bytes[: self.pointer_length], byteorder="little", signed=False
                )
                return entry_number
        return None

    def search_catalog(
        self, search_query: str, max_results: int = 64, include_redirects: bool = True
    ) -> list[tuple[str, int]]:
        if len(search_query) == 0:
            return []
        search_query_lower = search_query.lower()
        if self.n_catalog_blocks == 1:
            block_number = 0
        else:
            block_number = self._recursive_catalog_search(
                search_query_lower, 0, self.n_catalog_blocks - 1, prefix_match=True
            )
        if block_number is None:
            return []
        block_numbers = [block_number]
        if block_number > 0:
            block_numbers.append(block_number - 1)
        if block_number < self.n_catalog_blocks - 1:
            block_numbers.append(block_number + 1)
        exact_matches = []
        prefix_matches = []
        for block_number in block_numbers:
            catalog_block = self._get_catalog_block(block_number)
            entry_count = int.from_bytes(
                catalog_block[: self.pointer_length], byteorder="little", signed=False
            )
            for entry_index in range(entry_count):
                entry_bytes = self._extract_from_data(entry_index, catalog_block)
                entry_title = entry_bytes[self.pointer_length :].decode("utf-8")
                if not include_redirects and "\x00" in entry_title:
                    continue
                entry_title_lower = entry_title.split("\x00", maxsplit=1)[0].lower()
                if entry_title_lower == search_query_lower:
                    entry_number = int.from_bytes(
                        entry_bytes[: self.pointer_length],
                        byteorder="little",
                        signed=False,
                    )
                    exact_matches.append((entry_title, entry_number))
                elif entry_title_lower.startswith(search_query_lower):
                    entry_number = int.from_bytes(
                        entry_bytes[: self.pointer_length],
                        byteorder="little",
                        signed=False,
                    )
                    prefix_matches.append((entry_title, entry_number))
        search_results = exact_matches + prefix_matches
        return search_results[:max_results]

    def get_article_by_entry_number(self, entry_number: int) -> str | None:
        article_bytes = self._retrieve_article(entry_number)
        if article_bytes is None:
            return None
        if len(article_bytes) == 0:
            return None
        return article_bytes.decode("utf-8")

    def get_article_by_title(self, article_title: str) -> str | None:
        entry_number = self._find_article(article_title)
        if entry_number is None:
            return None
        return self.get_article(article_title, entry_number)

    def get_article(self, article_title: str, entry_number: int) -> str | None:
        main_text = self.get_article_by_entry_number(entry_number)
        if main_text is None:
            return None
        header = f"# {article_title}\n\n"
        footer = self.footer_text.replace(
            "«ARTICLE_TITLE»", article_title.replace(" ", "_")
        )
        return header + main_text + footer
