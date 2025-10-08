import base64
import gzip
import re
from operator import itemgetter
from typing import Optional, Pattern

from sapiopylib.utils.string import to_base64


class CompressionUtil:
    """
    This class adds methods to compress a string then split the data to multiple parts. This is helpful to store
    larger preference settings or protocol/step specific context data.
    """
    OPTION_VALUE_LIMIT = 4000
    ENTRY_OPTION_VALUE_LIMIT = 40000

    @staticmethod
    def compress_to_option_value(string: Optional[str]) -> Optional[str]:
        """
        Compress the string being passed in and then encode using base64 so the value can be read by dev-tools
        :param string: The value to be compressed
        :return: A version of the string that has been passed in that has been gzip compressed and base64 encoded.
        """
        if not string:
            return None

        compressed_bytes: bytes = CompressionUtil.compress(string)
        return to_base64(compressed_bytes)

    @staticmethod
    def uncompress_from_option_value(base_64_compressed: Optional[str]) -> Optional[str]:
        """
        Decompress the string being passed in and decode it from base64
        :param base_64_compressed: The string which has been compressed to gzip and encoded with base64
        :return: The decoded version of the string
        """
        if not base_64_compressed:
            return None

        compressed_bytes: bytes = base64.decodebytes(base_64_compressed.encode('utf-8'))
        return CompressionUtil.decompress(compressed_bytes)

    @staticmethod
    def set_task_option_value(option_key: str, original_option_value: str, option_map: dict[str, str]) -> None:
        """
        For workflow tasks. Compress and split into chunks that are acceptable by DB.
        :param option_key: The original option key, the prefix of all chunks.
        :param original_option_value: The original uncompressed option value to store.
        :param option_map: The map that the new compressed value will be stored in
        """
        CompressionUtil.set_option_value(option_key, original_option_value, option_map,
                                         CompressionUtil.OPTION_VALUE_LIMIT)

    @staticmethod
    def set_workflow_option_value(option_key: str, original_option_value: str, option_map: dict[str, str]) -> None:
        """
        For workflow tasks. Compress and split into chunks that are acceptable by DB.
        :param option_key: The original option key, the prefix of all chunks.
        :param original_option_value: The original uncompressed option value to store.
        :param option_map: The map that the new compressed value will be stored in
        :return:
        """
        CompressionUtil.set_option_value(option_key, original_option_value, option_map,
                                         CompressionUtil.OPTION_VALUE_LIMIT)

    @staticmethod
    def set_notebook_experiment_option_value(option_key: str, original_option_value: str,
                                             option_map: dict[str, str]) -> None:
        """
        For notebook experiment. Compress and split into chunks that are acceptable by DB.
        :param option_key: The original option key, the prefix of all chunks.
        :param original_option_value: The original uncompressed option value to store.
        :param option_map: The map that the new compressed value will be stored in
        :return:
        """
        CompressionUtil.set_option_value(option_key, original_option_value, option_map,
                                         CompressionUtil.OPTION_VALUE_LIMIT)

    @staticmethod
    def set_entry_option_value(option_key: str, original_option_value: str, option_map: dict[str, str]):
        """
        For notebook experiment entry. Compress and split into chunks that are acceptable by DB.
        :param option_key: The original option key, the prefix of all chunks.
        :param original_option_value: The original uncompressed option value to store.
        :param option_map: The map that the new compressed value will be stored in
        :return:
        """
        CompressionUtil.set_option_value(option_key, original_option_value, option_map,
                                         CompressionUtil.ENTRY_OPTION_VALUE_LIMIT)

    @staticmethod
    def set_option_value(option_key: str, original_option_value: str, option_map: dict[str, str],
                         limit: int) -> None:
        """
        Set the option key and option value to option map.
        If the length exceeds the maximum, then this is split into multiple chunks with _.
        This method is usually an internal method in this util.
        Algorithm: first we compress into zip, then take base64. Then we split base64 into chunks.
        :param option_key: The original option key, the prefix of all chunks.
        :param original_option_value: The original uncompressed option value to store.
        :param option_map: The map the new compressed value will be stored in
        :param limit: the limit of the option value in DB.
        :return:
        """
        CompressionUtil.clear_option_value(option_key, option_map)

        encoded_option_value: str = CompressionUtil.compress_to_option_value(original_option_value)
        encoded_split: list = [encoded_option_value[i:i + limit] for i in range(0, len(encoded_option_value), limit)]

        val_counter = 0
        for split in encoded_split:
            val_counter += 1
            key: str = option_key + "_" + str(val_counter)
            option_map[key] = split

    @staticmethod
    def get_option_value(option_key: str, option_map: dict[str, str]) -> str:
        """
        This is the opposite of setOptionValue. In this operation, we retrieve the value originally stored in compressed chunks.
        Retrieve entry option key across all chunks. This will be the base 64.
        Then it will decompress the union of strings.
        :param option_key: The key to retrieve the option value.
        :param option_map: The preference map to retrieve value from.
        :return: None if the value is not present, the original value if the key is present.
        """
        key_index_pairs: list[tuple[int, str]] = []
        pattern: Pattern = CompressionUtil.get_option_key_pattern(option_key)

        for key in option_map:
            if key:
                if re.match(pattern, key):
                    matcher = re.search(pattern, key)
                    index: int = matcher.group(1)
                    pair_to_add = (index, key)
                    key_index_pairs.append(pair_to_add)
        key_index_pairs.sort(key=itemgetter(0))
        key_list: list[str] = []

        for key in key_index_pairs:
            if option_map[key[1]]:
                key_list.append(option_map[key[1]])

        keys: str = "".join(key_list)
        return CompressionUtil.uncompress_from_option_value(keys)

    @staticmethod
    def clear_option_value(option_key: str, option_map: dict[str, str]) -> set[str]:
        """
        Clear option from a preference map.
        :param option_key: The option key to be cleared.
        :param option_map: The map the key will be removed from
        :return: The set of keys removed from the map
        """
        pattern: Pattern = CompressionUtil.get_option_key_pattern(option_key)
        matching_keys: set[str] = set()
        for key in option_map:
            if re.match(pattern, key) and option_key:
                matching_keys.add(key)

        for matched_key in matching_keys:
            del option_map[matched_key]

        return matching_keys

    @staticmethod
    def compress(string: Optional[str]) -> Optional[bytes]:
        """
        Compress a string via GZIP
        :param string: The string to be compressed
        :return: A version of the string that was passed in that has been compressed with gzip
        """
        if not string:
            return None

        return gzip.compress(string.encode('utf-8'))

    @staticmethod
    def decompress(compressed: Optional[bytes]) -> Optional[str]:
        """
        Compress a string via GZIP
        :param compressed: A bytes object that will be decompressed with gzip
        :return: A string version of the gzip decompressed bytes object that was passed in
        """
        if not compressed:
            return None
        return gzip.decompress(compressed).decode("utf-8")

    @staticmethod
    def get_option_key_pattern(option_key: str) -> Pattern:
        """
        Get the regex to obtain all option keys for a given option key name.
        :param option_key: The option key name.
        :return: The regex to match all option keys in a preference map.
        """
        return re.compile(re.escape(option_key + "_") + "([0-9]+)")