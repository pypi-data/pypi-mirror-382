from mcp.server.fastmcp import FastMCP
import os
import sys
import logging

# 日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DoorLockMCP")


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# 引入模块
from DoorLockController import mqtt_client
from JC_packet.JC_packet_action import set_payload_action
from JC_packet.JC_packet import set_packet


app = FastMCP("DoorLockController")


@app.tool()
def unlock_door(gateway_id: str) -> str:
    """
    通过 MQTT 发布开门指令
    参数:
        gateway_id: 门锁网关编号
    """
    try:
        #生成payload数据
        payload = set_payload_action()

        #封装完整通信帧
        frame = set_packet(0x0108, payload)

        #转换为十六进制字符串
        data_str = ''.join(format(x, '02X') for x in frame)

        #发布MQTT消息
        mqtt_client.publish_command(gateway_id, f"value:{data_str}")

        logger.info(f"开门指令已发送到网关 {gateway_id}，数据帧: {data_str}")
        return f"已发送开门指令到网关 {gateway_id}\n帧内容: {data_str}"

    except Exception as e:
        logger.error(f"发送开门指令失败: {e}", exc_info=True)
        return f"发送失败: {str(e)}"


def run():
    """启动 MQTT 客户端与 MCP 工具"""
    mqtt_client.start()
    app.run(transport="stdio")




