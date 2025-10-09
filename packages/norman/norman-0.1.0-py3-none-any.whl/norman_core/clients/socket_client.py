import asyncio
import base64
import contextlib
from typing import AsyncGenerator

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from norman_objects.services.file_push.pairing.socket_pairing_response import SocketPairingResponse
from norman_utils_external.streaming_utils import StreamingUtils, AsyncBufferedReader
from xxhash import xxh3_64

from norman_core._app_config import AppConfig


class SocketClient:
    @staticmethod
    async def write_and_digest(socket_info: SocketPairingResponse, asset_stream: AsyncBufferedReader):
        hash_stream = xxh3_64()
        body_stream = StreamingUtils.process_read_stream(asset_stream, hash_stream.update, AppConfig.io.chunk_size, False)

        async for _ in SocketClient.write(socket_info, body_stream):
            ...

        return hash_stream.hexdigest()

    @staticmethod
    async def write(socket_info: SocketPairingResponse, file_stream: AsyncGenerator[bytes, None]):
        authentication_header = base64.b64decode(socket_info.authentication_header)
        encryptor = SocketClient._create_encryptor(socket_info)

        body_stream = StreamingUtils.chain_streams([authentication_header], file_stream)

        stream_reader, stream_writer = await asyncio.open_connection(socket_info.host, socket_info.port)
        try:
            async for chunk in body_stream:
                encrypted = encryptor.update(chunk)
                stream_writer.write(encrypted)
                if stream_writer.transport.get_write_buffer_size() >= AppConfig.io.flush_size:
                    await stream_writer.drain()
                await stream_writer.drain()
                yield chunk
        finally:
            stream_writer.close()
            with contextlib.suppress(ConnectionResetError):
                await stream_writer.wait_closed()

    @staticmethod
    def _create_encryptor(pairing_response: SocketPairingResponse):
        key_bytes = base64.b64decode(pairing_response.encryption_key)
        base_nonce12 = base64.b64decode(pairing_response.nonce)

        counter_nonce4 = (0).to_bytes(4, "little")
        full_nonce16 = counter_nonce4 + base_nonce12

        cipher = Cipher(algorithms.ChaCha20(key_bytes, full_nonce16), mode=None)
        encryptor = cipher.encryptor()

        return encryptor
