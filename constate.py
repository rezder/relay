"""
A domain value for connection state.
None is used when there is no asyncio server thread
"""
off = 0
connecting = 1
connected = 2
broke = 3
stopping = 4

shorts = {0: "Off",
          1: "Connecting",
          2: "Connected",
          3: "Broken",
          4: "Stopping"
          }


def all() -> set[int]:
    return set(shorts.keys())


def shortTxt(no) -> str:
    return shorts[no]
