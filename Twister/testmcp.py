from RPiMCP23S17.MCP23S17 import MCP23S17
import time

mcp1 = MCP23S17(bus=0x00, pin_cs=0, device_id=0x00)
mcp2 = MCP23S17(bus=0x00, pin_cs=1, device_id=0x01)
mcp1.open()
mcp2.open()
mcp1._spi.max_speed_hz=1000000
mcp2._spi.max_speed_hz=1000000

for x in range(0, 16):
    mcp1.setDirection(x, mcp1.DIR_OUTPUT)
    mcp2.setDirection(x, mcp2.DIR_OUTPUT)

for x in range(0, 16):
    mcp1.digitalWrite(x, MCP23S17.LEVEL_LOW)
    mcp2.digitalWrite(x, MCP23S17.LEVEL_LOW)
time.sleep(1)

print("Starting blinky on all pins (CTRL+C to quit)")
while (True):
    for x in range(0, 16):
        mcp1.digitalWrite(x, MCP23S17.LEVEL_HIGH)
        mcp2.digitalWrite(x, MCP23S17.LEVEL_HIGH)
    time.sleep(1)

    for x in range(0, 16):
        mcp1.digitalWrite(x, MCP23S17.LEVEL_LOW)
        mcp2.digitalWrite(x, MCP23S17.LEVEL_LOW)
    time.sleep(1)