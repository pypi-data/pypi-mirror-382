
from DoorLockController.mcp_tools import unlock_door

def test():
    result = unlock_door("123456")
    print(result)

if __name__ == "__main__":
    test()
    # run()  # Uncomment this line to start the MCP service if needed