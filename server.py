import threading
import asyncio as ass

from msgboard import MsgBoard
from config import Config
from conn import Conn
import constate


class Server:
    def __init__(self):
        self.msgBoard = MsgBoard()
        self.conf = Config()
        self.mac = self.conf.getMac()
        if self.mac is None:
            raise Exception("Error no mac address")
        self.guiEvent = None
        self.loop = None

    def exist(self) -> bool:
        """
        Returns if the asyncio server thread
        is started.
        """
        return self.loop is not None

    def start(self) -> bool:
        isOk = False
        if not self.exist():
            if isOk:
                self.serverThread = threading.Thread(
                    target=self._startAsync)
                self.serverThread.start()
        return isOk

    def stopSend(self) -> bool:
        """
        Send the stop signal to the async server
        return false if server does not exist and
        does not send it again if allready send
        """
        # self.queue.shutdown() methods comes in python 3.13
        ok = False
        if self.exist():
            ok = True
            inform = self.msgBoard.guiSetStop()
            if inform:
                self.loop.call_soon_threadsafe(guiSetEvent,
                                               self.guiEvent)
        return ok

    def stopCheck(self) -> bool:
        """
        Check if the async server is stopped and
        if it is stopped do some cleanup.
        Cleanup removed the thread.
        """
        done = False
        if not self.exist():
            done = True
            self.conf.save()
        else:
            if not self.serverThread.is_alive():
                self.msgBoard.guiSetDone()
                self.loop = None
                self.guiEvent = None
                self.serverThread = None
                done = True
                self.conf.save()
        return done

    def relaysUpd(self, relayJson: dict):
        """
        Saves the relay in config and sends it to
        the connection if needed.
        :param relays: The relay settings on or off
         """
        self.conf.relaysSet(relayJson)
        relaySett = self.conf.relaysGetSett()
        if self.exist():
            if self.msgBoard.guiSetRelay(relaySett):
                self.loop.call_soon_threadsafe(guiSetEvent,
                                               self.guiEvent)

    def getStatus(self) -> tuple[str, list[int], int] | None:
        """
        Returns the connection state txt
        and temperatues. If lock is not possible
        within 2 seconds it returns None
        :returns:
        - Text
        - Temperature a list 6
        - Temerature last read timestamp
        - Connection state
        """
        return self.msgBoard.guiGetConInfo()

    def _startAsync(self):
        """
        Setup the async loop
        """
        self.loop = ass.new_event_loop()
        ass.set_event_loop(self.loop)
        self.guiEvent = ass.Event()
        self.loop.run_until_complete(self._serve())

    async def _serve(self):
        """
        The primary async function.
        Listens for signalk data and gui signals.
        """
        await serve(self.msgBoard,
                    self.guiEvent,
                    self.conf.getMac(),
                    self.conf.getRelayOns())


async def serve(msgBoard: MsgBoard,
                guiEvent: ass.Event,
                mac: str,
                initRelays: list[bool]):
    conn = Conn(mac, initRelays, msgBoard)
    conn.start()
    while True:
        await guiEvent.wait()
        stop, relays = msgBoard.conGetGui()
        guiEvent.clear()
        if stop:
            txt = "Stopping connection after gui event mesagges"
            msgBoard.conSetState(constate.stopping, txt)
            await conn.turnOff()
            break
        else:
            await conn.send(relays)


def guiSetEvent(ev: ass.Event):
    """
    Sends a signal to the asyncio server
    gui have changed stop or relays
    should run in the asyncio thread
    to make it thread safe.
    """
    print("setting gui event")
    ev.set()
