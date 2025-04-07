import tkinter as tk
import sys
import time

from server import Server
from guistatus import Status
from flds import temps as TempFlds
from flds import relays as RelayFlds
from flds import flds


sys.path.append('/home/rho/Python/arduino/havsmolf/disp/')
#sys.path.insert(0, '/home/rho/Python/arduino/havsmolf/disp/')
import guiflds as gf
from guijsontable import Table
from gui import BORDER_COLOR, BORDER_WIDTH


class GuiServer:
    """
    The gui of the display server.
    """
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Relay Server")
        self.server = Server()
        self.server.start()

        # Main Frames

        # Left Frame
        self.leftFrame = tk.Frame(self.window,
                                  highlightthickness=BORDER_WIDTH,
                                  highlightbackground=BORDER_COLOR)
        self.leftFrame.pack(side=tk.LEFT,
                            fill=tk.Y,
                            expand=True,
                            padx=(0, 10))
        tempflds = [TempFlds.no, TempFlds.pin, TempFlds.name,
                    TempFlds.temp, TempFlds.ts]
        self.tempTable = Table(self.window, self.leftFrame,
                               TempFlds.no, None, tempflds)
        self.tempTable.mainFrame.pack()
        self.tempTable.show(self.server.conf.tempsGet())

        relayflds = [RelayFlds.no, RelayFlds.pin, RelayFlds.onPos,
                     RelayFlds.name, RelayFlds.on]
        self.relayTable = Table(self.window, self.leftFrame,
                                RelayFlds.no, None, relayflds)

        self.relayTable.mainFrame.pack()

        self.relayTable.show(self.server.conf.relaysGet())
        #  Quick and dirty a general solution for all input flds in table
        # is need option and check mark have command but entry do not
        # commend cant be removed but i do not think it matter just
        # replace
        # Entry properly need to bind on FocusOut
        # cb need key and fld added like current bind
        for row in self.relayTable.rowsFlds.values():
            row[flds.on.jId].postChgAdd(self.relayUpdCb)

        # Righ frame
        self.rightFrame = self.rightFrame = tk.Frame(self.window,)
        self.rightFrame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.statusGui = Status(self.rightFrame, self.server.getStatus)
        self.statusGui.mainFrame.pack()

        # Gui inter connections
        self.statusGui.subscribeTemps(self.tempUpdCb)


        # window callbacks
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def relayUpdCb(self):
        relayJson, _, _, _ = self.relayTable.get()
        self.server.relaysUpd(relayJson)

    def tempUpdCb(self, temps, ts):
        for i in range(len(temps)):
            key = str(i+1)
            self.tempTable.setFld(TempFlds.temp, key, temps[i])
            self.tempTable.setFld(TempFlds.ts, key, ts)

    def logger(self, txt):
        self.statusGui.write(txt)

    def on_closing(self):
        tabJson, _, _, _ = self.relayTable.get()
        self.server.conf.relaysSet(tabJson)  # Save names
        self.logger("Clossing server")
        self.window.update_idletasks()
        self.statusGui.updateStatus()
        send = self.server.stopSend()
        if send:
            self.window.after(1000, self.on_closingStopCheck)
        else:
            self.server.stopCheck()
            self.window.destroy()

    def on_closingStopCheck(self):
        self.statusGui.updateStatus()
        if self.server.stopCheck():
            self.window.update_idletasks()
            time.sleep(2)
            self.window.destroy()
        else:
            self.window.after(2000, self.on_closingStopCheck)

    def start(self):
        self.window.after(1000, self.statusLoop())

        self.window.mainloop()

    def statusLoop(self):
        self.statusGui.updateStatus()
        self.window.after(3000, self.statusLoop)


dp = GuiServer()
dp.start()
