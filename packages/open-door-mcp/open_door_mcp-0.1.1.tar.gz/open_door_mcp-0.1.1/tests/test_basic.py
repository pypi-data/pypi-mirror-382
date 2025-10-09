import pytest 
from src.DoorLockController.mcp_tools import unlock_door,run


def test_unlock_door():
    result = unlock_door("123456")
    assert "已发送开门指令" in result

def test_run(monkeypatch):
    # 使用 monkeypatch 模拟 mcp_tools.run 的行为
    called = {}

    def fake_run(transport):
        called["transport"] = transport

    from src.DoorLockController import mcp_tools
    monkeypatch.setattr(mcp_tools.app,fake_run)
    mcp_tools.run()
    assert called["transport"] == "stdio"


