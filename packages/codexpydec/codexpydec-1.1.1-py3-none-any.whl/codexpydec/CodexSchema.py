def get_compatible_schema(major: int, minor: int) -> dict | None:
    while minor >= 0:
        version = f"{major}.{minor}"
        if version in CODEX_SCHEMATA:
            return CODEX_SCHEMATA[version]
        minor -= 1
    return None


CODEX_SCHEMATA = {
    "1.0": {
        "pointerLength": 4,
        "shardPointerLength": 1,
        "fileSignature": {
            "type": "string",
            "offset": 0,
            "length": 4,
            "value": "CODX",
        },
        "schemaVersionMajor": {
            "type": "int",
            "offset": 4,
            "length": 1,
            "value": 1,
        },
        "schemaVersionMinor": {
            "type": "int",
            "offset": 5,
            "length": 1,
            "value": 0,
        },
        "compressionAlgorithm": {
            "type": "string",
            "offset": 6,
            "length": 4,
            "value": None,
        },
        "libraryID": {
            "type": "string",
            "offset": 10,
            "length": 8,
            "value": None,
        },
        "libraryName": {
            "type": "string",
            "offset": 18,
            "length": 64,
            "value": None,
        },
        "libraryLicense": {
            "type": "string",
            "offset": 82,
            "length": 128,
            "value": None,
        },
        "libraryVersion": {
            "type": "int",
            "offset": 210,
            "length": 4,
            "value": None,
        },
        "patchedVersion": {
            "type": "int",
            "offset": 214,
            "length": 4,
            "value": None,
        },
        "nCatalogEntries": {
            "type": "int",
            "offset": 218,
            "length": 4,
            "value": None,
        },
        "nLibraryEntries": {
            "type": "int",
            "offset": 222,
            "length": 4,
            "value": None,
        },
        "nCatalogBlocks": {
            "type": "int",
            "offset": 226,
            "length": 2,
            "value": None,
        },
        "nLibraryBlocks": {
            "type": "int",
            "offset": 228,
            "length": 2,
            "value": None,
        },
        "nCatalogShards": {
            "type": "int",
            "offset": 230,
            "length": 1,
            "value": None,
        },
        "nLibraryShards": {
            "type": "int",
            "offset": 231,
            "length": 1,
            "value": None,
        },
        "inventoryPointer": {
            "type": "int",
            "offset": 232,
            "length": 8,
            "value": None,
        },
        "catalogIndexPointer": {
            "type": "int",
            "offset": 240,
            "length": 8,
            "value": None,
        },
        "libraryIndexPointer": {
            "type": "int",
            "offset": 248,
            "length": 8,
            "value": None,
        },
    },
}
