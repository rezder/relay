import tkinter as tk
import sys
import time

from server import Server
from guistatus import Status


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

        # Main Frames
        self.leftFrame = tk.Frame(self.window,
                                  highlightthickness=BORDER_WIDTH,
                                  highlightbackground=BORDER_COLOR)
        self.leftFrame.pack(side=tk.LEFT,
                            fill=tk.Y,
                            expand=True,
                            padx=(0, 10))
        self.rightFrame = self.rightFrame = tk.Frame(self.window,)
        self.rightFrame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.statusGui = Status(self.rightFrame, self.server.getStatus)
        self.statusGui.mainFrame.pack()
        # window callbacks
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def logger(self, txt):
        self.statusGui.write(txt)

    def on_closing(self):
        self.logger("Clossing server")
        self.window.update_idletasks()
        self.statusGui.updateStatus()
        send = self.server.stopSend()
        if send:
            self.window.after(1000, self.on_closingStopCheck)
        else:
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
