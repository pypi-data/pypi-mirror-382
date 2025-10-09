# echo-client.py

import time
import os

import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad


# device_id 0A0EFE99AEC2130E
# 9C01 070A 0000003C002A0000002162D8B5F601010001A2DB010102001F0006313437323538FFFFFFFFFFFFFFFFFFFFFFFFFF0A404A7B

device_ID = bytes.fromhex("0A522438E6021CA6")
#aes_key   = bytes.fromhex("E9D956C1495B17F57445DBAC00330F5B")
aes_key = None
keyCode = 7


class AEScoder():
    def __init__(self, key, iv):
        self.key = key
        self.iv  = iv

    # AES加密
    def encrypt(self,data):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        encrData = cipher.encrypt(pad(data, 16, 'pkcs7'))
        # encrData = base64.b64encode(encrData)
        return encrData

    # AES解密
    def decrypt(self,encrData):
        # encrData = base64.b64decode(encrData)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        decrData = unpad(cipher.decrypt(encrData), 16, 'pkcs7')
        return decrData

# 获取python脚本文件所在路径
def get_py_path():
    return os.path.split(os.path.realpath(__file__))[0]

# 导入图片
def load_image(img_path):
    binFile = open(img_path, 'rb')
    size = os.path.getsize(img_path)
    if (size):
        bb = binFile.read(size)
    else:
        bb = False
    binFile.close()
    return bb

# CRC校验
def set_data_crc(data):
    # print("data", "(", len(data), ") = ", data)
    crc = 0x0000
    for pos in data:
        crc ^= ((pos&0x00FF)<<8)
        crc &= 0xFFFF
        for i in range(8):
            if (crc & 0x8000):
                crc = ((crc<<1)^0x1021)
                crc &= 0xFFFF
            else:
                crc <<= 1
                crc &= 0xFFFF
        # print("0x%04X" % (crc))
    # print("crc = 0x%04X" % (crc))
    return crc & 0xFFFF
    # return ((crc & 0xff) << 8) + (crc >> 8)

# 钥匙信息组包
def set_key_value(kt_bin_path):
    bb = load_image(kt_bin_path)
    print("kt_len =", len(bb))
    key_value = []

    bbe = base64.b64encode(bb)
    for i in bbe:
        key_value.append(i)

    key_crc = 0x0000
    key_crc = set_data_crc(key_value)
    print("key_crc = 0x%04X" % key_crc)

    # uint16_t 数据校验
    bbc = int(key_crc).to_bytes(length=2, byteorder="big", signed=False)
    # 转成字符串
    bbs = bbc.hex()
    # 字符串转字节
    bbb = bytes(bbs, encoding = "utf8")
    for i in bbb:
        # print(i)
        key_value.append(i)

    return key_value

# 数据域组包
def set_payload_fea(
        _key,                   # 加密密钥
        _count,                 # uint32_t 自增计数值
        _device_id,             # uint64_t 设备ID
        _timestamp,             # uint32_t 服务器时间戳
        _packet_sum,            # uint8_t  包总数
        _packet_seq,            # uint8_t  包序号(从1开始)
        _account,               # uint32_t 用户账户信息
        _level,                 # uint8_t  钥匙等级
        _reg_type,              # uint8_t  用户属性：0管理员，1普通用户，2限时钥匙，3循环钥匙
        _key_type,              # uint8_t  钥匙类型；指纹/密码/IC卡
        _key_code,              # uint16_t 钥匙编号
        _start_timestamp,       # uint32_t 起始时间戳
        _end_timestamp,         # uint32_t 结束时间戳
        _effective_day,         # uint8_t  有效工作日
        _start_hour,            # uint8_t  起始小时
        _start_min,             # uint8_t  起始分钟
        _continue_duration,     # uint16_t 持续时长(分钟)
        _start_stop_flag,       # uint8_t  启停标志
        _alarm_flag,            # uint8_t  报警标志
        _start_stop_timestamp,  # uint32_t 启停生效时间
        _alarm_timestamp,       # uint32_t 报警生效时间
        _key_len,               # uint16_t 钥匙长度
        _key_value              # uint8_t  钥匙信息
    ):
    payload = []

    # uint32_t 自增计数值
    bb = int(_count).to_bytes(length=4, byteorder="big", signed=False)
    payload.append(bb[0])
    payload.append(bb[1])
    payload.append(bb[2])
    payload.append(bb[3])

    # uint64_t 设备ID
    for i in _device_id:
        payload.append(i)

    # uint32_t 服务器时间戳
    bb = int(_timestamp).to_bytes(length=4, byteorder="big", signed=False)
    payload.append(bb[0])
    payload.append(bb[1])
    payload.append(bb[2])
    payload.append(bb[3])

    # uint8_t  包总数
    payload.append(_packet_sum)

    # uint8_t  包序号(从1开始)
    payload.append(_packet_seq)

    # uint32_t 用户账户信息
    bb = int(_account).to_bytes(length=4, byteorder="big", signed=False)
    payload.append(bb[0])
    payload.append(bb[1])
    payload.append(bb[2])
    payload.append(bb[3])

    # uint8_t  钥匙等级
    payload.append(_level)

    # uint8_t  用户属性：0管理员，1普通用户，2限时钥匙，3循环钥匙
    payload.append(_reg_type)

    # uint8_t  钥匙类型；指纹/密码/IC卡
    payload.append(_key_type)

    # uint16_t 钥匙编号
    bb = int(_key_code).to_bytes(length=2, byteorder="big", signed=False)
    payload.append(bb[0])
    payload.append(bb[1])

    # uint32_t 起始时间戳
    bb = int(_start_timestamp).to_bytes(length=4, byteorder="big", signed=False)
    payload.append(bb[0])
    payload.append(bb[1])
    payload.append(bb[2])
    payload.append(bb[3])

    # uint32_t 结束时间戳
    bb = int(_end_timestamp).to_bytes(length=4, byteorder="big", signed=False)
    payload.append(bb[0])
    payload.append(bb[1])
    payload.append(bb[2])
    payload.append(bb[3])

    # uint8_t  有效工作日
    payload.append(_effective_day)

    # uint8_t  起始小时
    payload.append(_start_hour)

    # uint8_t  起始分钟
    payload.append(_start_min)

    # uint16_t 持续时长(分钟)
    bb = int(_continue_duration).to_bytes(length=2, byteorder="big", signed=False)
    payload.append(bb[0])
    payload.append(bb[1])

    # uint8_t  启停标志
    payload.append(_start_stop_flag)

    # uint8_t  报警标志
    payload.append(_alarm_flag)

    # uint32_t 启停生效时间
    bb = int(_start_stop_timestamp).to_bytes(length=4, byteorder="big", signed=False)
    payload.append(bb[0])
    payload.append(bb[1])
    payload.append(bb[2])
    payload.append(bb[3])

    # uint32_t 报警生效时间
    bb = int(_alarm_timestamp).to_bytes(length=4, byteorder="big", signed=False)
    payload.append(bb[0])
    payload.append(bb[1])
    payload.append(bb[2])
    payload.append(bb[3])

    # uint16_t 钥匙长度
    bb = int(_key_len).to_bytes(length=2, byteorder="big", signed=False)
    payload.append(bb[0])
    payload.append(bb[1])

    # uint8_t[]  钥匙信息
    for i in _key_value:
        payload.append(i)

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

    return payload

# 发送组包
def set_packet(
        cmd,
        payload
    ):
    frame = []
    frame.append(0x9C)  # header
    frame.append(0x01)  # ver
    # frame.append(0x09)  # cmd_h
    # frame.append(0x10)  # cmd_l
    bb = int(cmd).to_bytes(length=2, byteorder="big", signed=False)
    frame.append(bb[0])
    frame.append(bb[1])
    frame.append(0x00)  # msg_id
    frame.append(0x00)  # msg_id
    frame.append(0x00)  # msg_id
    frame.append(0x00)  # msg_id

    ll = len(payload)   # size

    len_bytes = int(ll).to_bytes(length=2, byteorder="big", signed=False)
    frame.append(len_bytes[0])
    frame.append(len_bytes[1])
    for i in payload:
        frame.append(i)

    frame_crc = 0x0000
    frame_crc = set_data_crc(frame)
    # print("frame_crc = 0x%04X" % frame_crc)

    bb = int(frame_crc).to_bytes(length=2, byteorder="big", signed=False)
    frame.append(bb[0])
    frame.append(bb[1])
    # return bytes(frame)
    return frame

if __name__ == '__main__':
    # psw = "667788"
    # key_value = psw.encode('utf-8')
    # bb = load_image(r"data\111.kt")
    # kt_path = ""
    # key_value = []
    # key_value = base64.b64encode(bb)
    kt_path = get_py_path() + r"\data\111.kt"
    print("kt_path =", kt_path)
    key_value = []
    key_value = set_key_value(kt_path)

    print("key_value(", len(key_value), ") = ", bytes(key_value).hex())

    print('-' * 32)
    # print("key_value", "(", len(key_value), ") = ", key_value)
    time_Stamp = (int)(time.time())
    payload = []
    payload = set_payload_fea(
        aes_key,
        1,              # uint32_t 自增计数值
        device_ID,      # uint64_t 设备ID
        time_Stamp,     # uint32_t 服务器时间戳
        1,              # uint8_t  包总数
        1,              # uint8_t  包序号(从1开始)
        666,            # uint32_t 用户账户信息
        1,              # uint8_t  钥匙等级
        1,              # uint8_t  用户属性：0管理员，1普通用户，2限时钥匙，3循环钥匙
        27,             # uint8_t  钥匙类型；指纹/密码/IC卡 27人脸
        keyCode,        # uint16_t 钥匙编号
        0xFFFFFFFF,     # uint32_t 起始时间戳
        0xFFFFFFFF,     # uint32_t 结束时间戳
        0xFF,           # uint8_t  有效工作日
        0xFF,           # uint8_t  起始小时
        0xFF,           # uint8_t  起始分钟
        0xFFFF,         # uint16_t 持续时长(分钟)
        0x00,           # uint8_t  启停标志
        0x00,           # uint8_t  报警标志
        0xFFFFFFFF,     # uint32_t 启停生效时间
        0xFFFFFFFF,     # uint32_t 报警生效时间
        len(key_value), # uint16_t 钥匙长度
        key_value       # uint8_t  钥匙信息
    )

    frame = set_packet(0x0910, payload)

    print("frame all =", len(frame) )

    gate = 1000

    if len(frame) <= gate:
        print("payload(", len(payload), ") = ", bytes(payload).hex())
        print('-' * 32)
        print("frame(", len(frame), ") = ", bytes(frame).hex())
    else:
        print("="*64)

    print('-' * 32)

def value_to_payload(value, len, order='big'):
    bb = int(value).to_bytes(length=len, byteorder=order, signed=False)
    payload = []
    for i in bb:
        payload.append(i)

    return payload
