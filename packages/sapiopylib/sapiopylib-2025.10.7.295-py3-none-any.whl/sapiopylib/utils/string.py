# PEP 0616
def removeprefix(src: str, prefix: str) -> str:
    """
    Remove the prefix of a string.
    Using PEP-0616 implementation reference code.
    """
    if src.startswith(prefix):
        return src[len(prefix):]
    else:
        return src[:]


def removesuffix(src: str, suffix: str) -> str:
    """
    Remove the prefix of a string.
    Using PEP-0616 implementation reference code.
    """
    # suffix='' should not call self[:-0].
    if suffix and src.endswith(suffix):
        return src[:-len(suffix)]
    else:
        return src[:]


def to_base64(data: bytes) -> str:
    """
    Convert the data bytes array into base 64 that can be read by Sapio.
    """
    import base64
    # In older Sapio platform systems the '\n' and '\r' causes the decoder to crash, which is part of the output coming from decode() operation in python.
    return base64.encodebytes(data).decode("utf-8").replace('\n', '').replace('\r', '')
