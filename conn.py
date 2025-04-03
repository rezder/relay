import asyncio as ass
import bleak
from msgboard import MsgBoard
import constate


def convData(data: list[bool]) -> bytearray:
    v = bytearray()
    for i in range(len(data)):
        if i % 8 == 0:
            v.append(0)
        if data[i]:
            vno = len(v)-1
            print(vno)
            v[vno] = v[vno] + pow(2, i % 8)
    return v


class Conn:

    def __init__(self, mac: str, initRelays: list[bool], msgBoard: MsgBoard):
        self.macAddr = mac
        self.intRelays = initRelays
        self.msgBoard = msgBoard
        self.client = bleak.BleakClient(self.macAddr, timeout=10.0)
        self.notifyIsOn = False
        self.isInitSend = False
        self.dataCharId = bleak.uuids.normalize_uuid_32(201)
        self.tempCharId = bleak.uuids.normalize_uuid_32(202)
        self.cmdCharId = bleak.uuids.normalize_uuid_32(203)
        self.connTask = None

    def start(self):
        txt = "Connecting to {}".format(self.macAddr)
        self.msgBoard.conSetState(constate.connecting, txt)
        self.connTask = ass.create_task(self.connect(),
                                        name="Ble client conn")

    async def connect(self):
        isTimeError = True
        while isTimeError:
            try:
                await self.client.connect()
                isTimeError = False
            except ass.TimeoutError:
                txt = "Ble connect did not finish within 10 seconds.\
                Trying again"
                self.msgBoard.setTxt(txt)

        self.client.start_notify(self.tempCharId, self.tempCb)
        self.notifyIsOn = True

        buff = convData(self.intRelays)
        await self.client.write_gatt_char(self.dataCharId,
                                          buff,
                                          response=True)
        self.isInitSend = True
        txt = "Connected to {}".format(self.macAddr)
        self.msgBoard.conSetState(constate.connected, txt)

    def tempCb(self,
               sender: bleak.BleakGATTCharacteristic,
               data: bytearray):
        if len(data) == 6:
            temps = list()
            for i in range(6):
                temp = int.from_bytes([data[i]])
                temps.append(temp)
            self.msgBoard.conSetTemp(temps)
        else:
            txt = "Characteristic: {} send wrong byte numbers {} on temp"
            self.msgBoard.setTxt(txt.format(sender, len(data)))

    def checkConnTask(self):
        """
        Check the connection task if a task exist and is done.
        If the task have errors the state of connection is change
        to broken. Done task is removed.
        When connection is down and no task exit a new task is created.
        """
        if self.connTask is not None:
            if self.connTask.done():
                ex = self.connTask.exception()
                if ex is not None:
                    txt = "Connection task failed with: {}"
                    self.msgBoard.conSetState(constate.broke, txt)

                self.connTask = None
        # Task completted(may have been with errors) or not started
        if self.connTask is None:
            if not self.client.is_connected:
                self.notifyIsOn = False
                self.isInitSend = False
                self.start()

    async def send(self, relays: list[bool]):
        self.intRelays = relays
        self.checkConnTask()
        if self.isInitSend:
            buff = convData(relays)
            await self.client.write_gatt_char(self.dataCharId,
                                              buff,
                                              response=True)
        else:
            self.intRelays = relays

    async def turnOff(self):
        """
        **Async** Turns the connection off
        """
        if self.connTask is not None:
            if not self.connTask.done():
                self.connTask.cancel()
                try:
                    await self.connTask
                except ass.CancelledError:
                    pass

            self.connTask = None

        if self.client.is_connected:
            cmdOff = bytearray('E', "ascii")
            await self.client.write_gatt_char(self.cmdCharId,
                                              cmdOff,
                                              response=True)
            await self.client.disconnect()

        self.notifyIsOn = False
        self.isInitSend = False
        txt = "Disconnected {}".format(self.macAddr)
        self.msgBoard.conSetState(constate.off, txt)
