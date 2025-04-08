import threading
import time

import constate


class MsgBoard:
    def __init__(self):
        self.txt = ""
        self.lock = threading.Lock()
        self.conTemp: list[int] = list()
        self.conTempTs = None
        self.conState = constate.off
        self.guiIsStop = False
        self.guiRelay: list[bool] = list()

    def reset(self):
        self.txt = ""
        self.conTemp.clear()
        self.conState = constate.off
        self.guiIsStop = False
        self.guiRelay.clear()

    def conSetState(self, st: int, txt: str):
        isMine = self.lock.acquire()
        if isMine:
            self.conState = st
            self.txt = self.txt + "\n" + txt
            self.lock.release()

    def conSetTemp(self, temps: list[int]):
        isMine = self.lock.acquire()
        if isMine:
            self.conTemp = temps
            self.conTempTs = time.time()
            self.lock.release()

    def conGetGui(self) -> tuple[bool, list[bool]]:
        relays = list(self.guiRelay)
        self.guiRelay.clear()
        return self.guiIsStop, relays

    def guiGetConInfo(self) -> tuple[str,
                                     list[int],
                                     float,
                                     int] | None:
        isMine = self.lock.acquire(timeout=2.0)
        res = None
        if isMine:
            txt = ""
            if self.txt:
                txt = self.txt
                self.txt = ""
            temp = list(self.conTemp)
            res = txt, temp, self.conTempTs, self.conState
            self.lock.release()
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
                self.lock.release()
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
        if isMine:
            if not self.guiIsStop and self.conState in [constate.connected,
                                                        constate.connecting,
                                                        constate.broke]:
                if len(self.guiRelay) == 0:
                    isInform = True
                self.guiRelay = relays
            self.lock.release()
        return isInform

    def setTxt(self, txt):
        isMine = self.lock.acquire()
        if isMine:
            self.txt = self.txt + "\n" + txt
            self.lock.release()
        else:
            print("Failed to get status this should not happen")
