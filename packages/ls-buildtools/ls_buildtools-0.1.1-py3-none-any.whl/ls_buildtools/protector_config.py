from typing import TypedDict,NotRequired
class GlobalFilterConfig(TypedDict):remove_regexes:NotRequired[list[str]]
class EncryptionConfig(TypedDict):enabled:NotRequired[bool];encryption_keys_file:NotRequired[str];exclude_regexes:NotRequired[list[str]]
class ObfuscationConfig(TypedDict):exclude_regexes:NotRequired[list[str]];custom_patches:bool;remove_literal_statements:bool;remove_annotations:bool
class ProtectorConfig(TypedDict):global_filter:NotRequired[GlobalFilterConfig];encryption:NotRequired[EncryptionConfig];obfuscation:NotRequired[ObfuscationConfig]