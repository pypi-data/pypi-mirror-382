from base64 import b32encode
from binascii import crc32


def short_hash(text: str) -> str:
    hash_int = crc32(text.encode('utf8'))
    hash_bytes = b32encode(hash_int.to_bytes((hash_int.bit_length() + 8) // 8, 'big', signed=True))
    return str(hash_bytes, 'utf8').replace('=', '')
