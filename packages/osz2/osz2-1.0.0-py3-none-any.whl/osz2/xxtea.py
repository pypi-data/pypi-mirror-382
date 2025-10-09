
from .simple_cryptor import SimpleCryptor
import struct

MAX_WORDS = 16
MAX_BYTES = MAX_WORDS * 4
TEA_DELTA = 0x9E3779B9

class XXTEA:
    def __init__(self, key: bytes) -> None:
        self.cryptor = SimpleCryptor(key)
        self.key = key
        self.n = 0

    def decrypt(self, buffer: bytearray, start: int, count: int) -> None:
        self.encrypt_decrypt(buffer, start, count, False)

    def encrypt(self, buffer: bytearray, start: int, count: int) -> None:
        self.encrypt_decrypt(buffer, start, count, True)

    def encrypt_decrypt(self, buffer: bytearray, buf_start: int, count: int, encrypt: bool) -> None:
        full_word_count = count // MAX_BYTES
        left_over = count % MAX_BYTES

        for i in range(full_word_count):
            offset = buf_start + i * MAX_BYTES
            if encrypt:
                self.encrypt_fixed_word_array(buffer, offset)
            else:
                self.decrypt_fixed_word_array(buffer, offset)

        if left_over == 0:
            return

        leftover_start = buf_start + full_word_count * MAX_BYTES
        self.n = left_over // 4

        if self.n > 1:
            if encrypt:
                self.encrypt_words(buffer, leftover_start)
            else:
                self.decrypt_words(buffer, leftover_start)

            left_over -= self.n * 4
            if left_over == 0:
                return

            leftover_start += self.n * 4

        remaining = buffer[leftover_start:leftover_start + left_over]

        if encrypt:
            self.cryptor.encrypt_bytes(remaining)
        else:
            self.cryptor.decrypt_bytes(remaining)

        buffer[leftover_start:leftover_start + left_over] = remaining

    def encrypt_words(self, data: bytearray, offset: int) -> None:
        if len(data) - offset < self.n * 4:
            return

        v = [struct.unpack_from('<I', data, offset + i * 4)[0] for i in range(self.n)]

        rounds = 6 + 52 // self.n
        sum_val = 0
        z = v[self.n - 1]

        while rounds > 0:
            sum_val = (sum_val + TEA_DELTA) & 0xFFFFFFFF
            e = (sum_val >> 2) & 3

            for p in range(self.n - 1):
                y = v[p + 1]
                v[p] = (v[p] + ((((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))) ^ ((sum_val ^ y) + (self.key[(p & 3) ^ e] ^ z)))) & 0xFFFFFFFF
                z = v[p]

            y = v[0]
            p = self.n - 1
            v[self.n - 1] = (v[self.n - 1] + ((((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))) ^ ((sum_val ^ y) + (self.key[(p & 3) ^ e] ^ z)))) & 0xFFFFFFFF
            z = v[self.n - 1]
            rounds -= 1

        for i in range(self.n):
            struct.pack_into('<I', data, offset + i * 4, v[i])

    def decrypt_words(self, data: bytearray, offset: int) -> None:
        if len(data) - offset < self.n * 4:
            return

        v = [struct.unpack_from('<I', data, offset + i * 4)[0] for i in range(self.n)]

        rounds = 6 + 52 // self.n
        sum_val = (rounds * TEA_DELTA) & 0xFFFFFFFF
        y = v[0]

        while True:
            e = (sum_val >> 2) & 3

            for p in range(self.n - 1, 0, -1):
                z = v[p - 1]
                v[p] = (v[p] - ((((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))) ^ ((sum_val ^ y) + (self.key[(p & 3) ^ e] ^ z)))) & 0xFFFFFFFF
                y = v[p]

            z = v[self.n - 1]
            p = 0
            v[0] = (v[0] - ((((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))) ^ ((sum_val ^ y) + (self.key[(p & 3) ^ e] ^ z)))) & 0xFFFFFFFF
            y = v[0]

            sum_val = (sum_val - TEA_DELTA) & 0xFFFFFFFF
            if sum_val == 0:
                break

        for i in range(self.n):
            struct.pack_into('<I', data, offset + i * 4, v[i])

    def encrypt_fixed_word_array(self, data: bytearray, offset: int) -> None:
        if len(data) - offset < MAX_BYTES:
            return

        v = [struct.unpack_from('<I', data, offset + i * 4)[0] for i in range(MAX_WORDS)]

        rounds = 6 + 52 // MAX_WORDS
        sum_val = 0
        z = v[MAX_WORDS - 1]

        while rounds > 0:
            sum_val = (sum_val + TEA_DELTA) & 0xFFFFFFFF
            e = (sum_val >> 2) & 3

            for p in range(MAX_WORDS - 1):
                y = v[p + 1]
                v[p] = (v[p] + ((((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))) ^ ((sum_val ^ y) + (self.key[(p & 3) ^ e] ^ z)))) & 0xFFFFFFFF
                z = v[p]

            y = v[0]
            p = MAX_WORDS - 1
            v[MAX_WORDS - 1] = (v[MAX_WORDS - 1] + ((((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))) ^ ((sum_val ^ y) + (self.key[(p & 3) ^ e] ^ z)))) & 0xFFFFFFFF
            z = v[MAX_WORDS - 1]
            rounds -= 1

        for i in range(MAX_WORDS):
            struct.pack_into('<I', data, offset + i * 4, v[i])

    def decrypt_fixed_word_array(self, data: bytearray, offset: int) -> None:
        if len(data) - offset < MAX_BYTES:
            return

        v = [struct.unpack_from('<I', data, offset + i * 4)[0] for i in range(MAX_WORDS)]

        rounds = 6 + 52 // MAX_WORDS
        sum_val = (rounds * TEA_DELTA) & 0xFFFFFFFF
        y = v[0]

        while True:
            e = (sum_val >> 2) & 3

            for p in range(MAX_WORDS - 1, 0, -1):
                z = v[p - 1]
                v[p] = (v[p] - ((((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))) ^ ((sum_val ^ y) + (self.key[(p & 3) ^ e] ^ z)))) & 0xFFFFFFFF
                y = v[p]

            z = v[MAX_WORDS - 1]
            p = 0
            v[0] = (v[0] - ((((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))) ^ ((sum_val ^ y) + (self.key[(p & 3) ^ e] ^ z)))) & 0xFFFFFFFF
            y = v[0]

            sum_val = (sum_val - TEA_DELTA) & 0xFFFFFFFF
            if sum_val == 0:
                break

        for i in range(MAX_WORDS):
            struct.pack_into('<I', data, offset + i * 4, v[i])
