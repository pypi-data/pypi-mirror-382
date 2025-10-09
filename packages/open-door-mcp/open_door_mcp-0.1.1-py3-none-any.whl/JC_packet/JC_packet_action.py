# echo-client.py
import time
import os

import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad

from hexdump2 import hexdump
from JC_packet.JC_packet import set_packet, set_data_crc, AEScoder


# device_id 0A0EFE99AEC2130E
# 9C01 070A 0000003C002A0000002162D8B5F601010001A2DB010102001F0006313437323538FFFFFFFFFFFFFFFFFFFFFFFFFF0A404A7B

device_id_name ="0C6E82A6CA021F83"
device_ID = bytes.fromhex(device_id_name)
#aes_key = bytes.fromhex("C8F636EEF4751A51C1D9EACE89BBDB07")
aes_key = None


# 蓝牙开门命令
def set_payload_action(
        _key,                   # 加密密钥
        _count,                 # uint32_t 自增计数值
        _timestamp,             # uint32_t 服务器时间戳
        _account,               # uint32_t 用户账户信息
        _level,                 # uint8_t  钥匙等级
        _chanal,                # uint8_t  执行通道
        _action,                # uint8_t  执行动作
    ):
    payload = []

    # uint32_t 自增计数值
    bb = int(_count).to_bytes(length=4, byteorder="big", signed=False)
    payload.append(bb[0])
    payload.append(bb[1])
    payload.append(bb[2])
    payload.append(bb[3])

    # uint32_t 服务器时间戳
    bb = int(_timestamp).to_bytes(length=4, byteorder="big", signed=False)
    payload.append(bb[0])
    payload.append(bb[1])
    payload.append(bb[2])
    payload.append(bb[3])

    # uint32_t 用户账户信息
    bb = int(_account).to_bytes(length=4, byteorder="big", signed=False)
    payload.append(bb[0])
    payload.append(bb[1])
    payload.append(bb[2])
    payload.append(bb[3])

    # uint8_t  钥匙等级
    payload.append(_level)

    # uint8_t  执行通道
    payload.append(_chanal)

    # uint8_t  执行动作
    payload.append(_action)

    data_crc = 0x0000
    data_crc = set_data_crc(payload)
    print("data_crc = 0x%04X" % data_crc)

    # uint16_t 数据校验
    bb = int(data_crc).to_bytes(length=2, byteorder="big", signed=False)
    payload.append(bb[0])
    payload.append(bb[1])

    if _key != None:
        print("aes_key =", aes_key)
        aes_test = AEScoder(_key, _key)
        cipher_text = aes_test.encrypt(bytearray(payload))
        payload = cipher_text
        init_text = aes_test.decrypt(bytearray(cipher_text))
        print("init_text", "(", len(init_text), ") = ", bytes(init_text).hex())

    return payload

if __name__ == '__main__':

    print('-' * 32)
    # print("key_value", "(", len(key_value), ") = ", key_value)
    time_Stamp = (int)(time.time())
    payload = []
    payload = set_payload_action(
        aes_key,        # 加密密钥
        1,              # uint32_t 自增计数值
        time_Stamp,     # uint32_t 服务器时间戳
        666     ,       # uint32_t 用户账户信息
        1     ,         # uint8_t  钥匙等级
        1,              # uint8_t  执行通道
        1,              # uint8_t  执行动作
    )

    frame = set_packet(0x0108, payload)
    data_str = bytes(frame).hex()

    print("payload(", len(payload), ") = ", bytes(payload).hex().upper())
    print('-' * 32)
    print(f"frame({len(frame)}) = {data_str.upper()}")
    print('-' * 32)

   