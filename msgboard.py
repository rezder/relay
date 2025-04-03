import constate
import threading
import time


class MsgBoard:
    def __init__(self):
        self.conTxt = ""
        self.lock = threading.Lock()
        self.conTemp: list[int] = list()
        self.conTempTs = None
        self.conState = constate.off
        self.guiIsStop = False
        self.guiRelay: list[bool] = list()

    def reset(self):
        self.conTxt = ""
        self.conTemp.clear()
        self.conState = constate.off
        self.guiIsStop = False
        self.guiRelay.clear()

    def conSetState(self, st: int, txt: str):
        isMine = self.lock.acquire()
        if isMine:
            self.conState = st
            self.conTxt = self.conTxt + "\n" + txt
            self.lock.release()

    def conSetTemp(self, temps: list[int]):
        isMine = self.lock.acquire()
        if isMine:
            self.conTemp = temps
            self.conTempTs = time.monotonic()

    def conGetGui(self) -> tuple[bool, list[bool]]:
        return self.guiStop, list(self.guiRelay)

    def guiGetConInfo(self) -> tuple[str,
                                     list[int],
                                     int] | None:
        isMine = self.lock.acquire(timeout=2.0)
        res = None
        if isMine:
            txt = ""
            if self.txt:
                txt = self.txt
                self.txt = ""
            temp = list(self.conTemp)
            res = txt, temp, self.conState
        return res

    def guiSetStop(self) -> bool:
        """
        Sets stop. Return true if assync connection need
        to be informed.
        """
        isInform = False
        isMine = self.lock.acquire()
        if isMine:
            if not self.guiIsStop:
                isInform = True
                self.guiIsStop = True
                self.txt = self.txt+"\n"+"Sending stop signal"
        return isInform

    def guiSetDone(self):
        isMine = self.lock.acquire()
        if isMine:
            self.guiIsStop = False
            self.guiRelay.clear()
            self.txt = self.txt + "\n" + "Server is stopped"
            self.lock.release()

    def guiSetRelay(self, relays: list[bool]) -> tuple[bool, bool]:
        """
        Sets the relays
        :return: true if relay was empty and assync need to be
        informed
        """
        isInform = False
        isMine = self.lock.acquire()
        if isMine and not self.guiIsStop:
            if self.conState in [constate.connected,
                                 constate.connecting,
                                 constate.broke]:
                if len(self.guiRelay) == 0:
                    isInform = True
                self.guiRelay = relays
        return isInform

    def setTxt(self, txt):
        isMine = self.lock.acquire()
        if isMine:
            self.txt = self.txt + "\n" + txt
            self.lock.release()
        else:
            print("Failed to get status this should not happen")
