from mcp.server.fastmcp import FastMCP
import os
import sys

# 动态添加项目根目录到 sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.DoorLockController import mqtt_client
from JC_packet.JC_packet_action import set_payload_action
from JC_packet.JC_packet import set_packet


app = FastMCP("DoorLockController")

# 工具：开门
@app.tool()
def unlock_door(gatewayID: str) -> str:
    """通过 MQTT 发布开门指令"""
    
    payload = set_payload_action()  # 调用包内函数生成数据
    frame = set_packet(0x0108, payload)
    data_str = bytes(frame).hex()
    mqtt_client.publish_command(gatewayID, f"value:{data_str.upper()}")
    
    return f"已发送开门指令(payload={data_str.upper()})到网关 {gatewayID}"



# @app.tool()
# def get_lock_status() -> str:
#     """返回门锁的最新状态"""
#     status = mqtt_client.get_last_status()
#     if status:
#         return f"最新门锁状态: {status}"
#     else:
#         return "还没有收到门锁状态消息"

def run():
    mqtt_client.start()
    app.run(transport="stdio")

