import time
from paho.mqtt import client as mqtt

BROKER = "emqx.logfun.xyz"   
PORT = 1883
TOPIC_CMD = "door/lock/cmd"
TOPIC_STATUS = "door/lock/status"
CLIENT_ID = "door_lock_client"
USERNAME = "admin"
PASSWORD = "$edh2VZ$EX}>!jb"


# 全局变量：保存最新门锁状态
last_status = None
connected_once = False

# MQTT 客户端实例
client = mqtt.Client(
    client_id=CLIENT_ID,
    clean_session=True,
    protocol=mqtt.MQTTv311,  # 指定协议版本
    userdata=None,
    transport="tcp"
)

# 设置用户名密码
client.username_pw_set(USERNAME, PASSWORD)


# 连接回调
connected_once = False
def on_connect(client, userdata, flags, rc):
    global connected_once
    if rc == 0:
        print("成功连接到 EMQX")
        client.subscribe(TOPIC_STATUS)
        print(f"已订阅主题: {TOPIC_STATUS}")

        # 仅首次连接时发送一次初始化指令
        if not connected_once:
            payload = '{"gatewayID": "123456", "value": "testok"}'
            client.publish(TOPIC_CMD, payload)
            connected_once = True
            print(f"首次连接: {payload}")
    else:
        print(f"连接失败，错误码 {rc}")

# 消息回调
def on_message(client, userdata, msg):
    print(f"收到消息: Topic={msg.topic}, Payload={msg.payload.decode()}")


# 绑定回调
client.on_connect = on_connect
client.on_message = on_message


def start():
    """启动 MQTT 客户端"""
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()
    print("MQTT 客户端已启动")


def publish_command(gateway_id: str, value: str):
    """发布开关门指令"""
    payload = f'{{"gatewayID": "{gateway_id}","value": "{value}" }}'
    client.publish(TOPIC_CMD, payload)
    print(f"已发布指令到 {TOPIC_CMD}: {payload}")
    return payload 


def get_last_status():
    """返回最新的门锁状态"""
    return last_status

if __name__ == "__main__":
    start()
    # 等待一会儿，保持客户端在线，可以手动从 EMQX Dashboard 往 door/lock/status 发消息测试
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("客户端已退出")
        client.loop_stop()