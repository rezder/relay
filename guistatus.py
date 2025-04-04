import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import constate


class Status:
    def __init__(self, parent: tk.Frame, statusCb):
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.bottomFrame = tk.Frame(self.mainFrame)
        self.statusCb = statusCb
        self.subTempList = list()
        self.textBox = scrolledtext.ScrolledText(self.mainFrame, undo=True)
        self.textBox['font'] = ('consolas', '12')
        self.textBox.pack(fill=tk.X, expand=True)
        heading = "Relay server"
        self.textBox.insert(tk.END, heading)
        self.bottomFrame.pack(fill=tk.BOTH, expand=True)
        self.stateVar = tk.StringVar()
        self.stateVar.set(constate.shortTxt(constate.off))
        self.stateLabel = tk.Label(self.bottomFrame,
                                   textvariable=self.stateVar)
        self.stateLabel.pack(side=tk.RIGHT)

    def write(self, txt):
        self.textBox.insert(tk.END, "\n"+txt)

    def subscribeTemps(self, fn):
        self.subTempList.append(fn)

    def executeTemps(self, temps: list):
        for f in self.subTempList:
            f(temps)

    def updateStatus(self):
        t = self.statusCb()
        if t is not None:
            txt, temps, state = t
            if txt != "":
                self.textBox.insert(tk.END, txt)
            self.stateVar.set(constate.shortTxt(state))
            self.executeTemps(temps)
        else:
            self.write("Failed to get log")
