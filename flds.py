import sys
import time

#sys.path.append('/home/rho/Python/arduino/havsmolf/disp/')
sys.path.append('../disp/')
from guiflds import Fld
import guiflds as gf
from guiflddefs import FldDef


def tsf(ts: float) -> str:
    return time.strftime("%a %H:%M:%S", time.localtime(ts))


class flds:
    no = Fld("no", "No", "No", str)
    pin = Fld("pin", "Pin", "Pin", int)
    name = Fld("name", "Name", "Name", str)
    temp = Fld("temp", "Temperature", "Temp", int)
    ts = Fld("ts", "Timestamp", "Time", float, toStr=tsf)
    tempType = Fld("temptype", "Type", "Type", str)
    on = Fld("on", "On", "On", bool)
    onPos = Fld("positiv-on", "On Positive", "On Pos", bool)


class temps:
    no = FldDef(flds.no, 2, 2, gf.FldLabel, isKey=True)
    pin = FldDef(flds.pin, 2, 2, gf.FldLabel)
    name = FldDef(flds.name, 15, 15, gf.FldLabel)
    temp = FldDef(flds.temp, 4, 4, gf.FldLabel, isJson=False)
    ts = FldDef(flds.ts, 13, 13, gf.FldLabel, isJson=False)


class relays:
    no = FldDef(flds.no, 2, 2, gf.FldLabel, isKey=True)
    pin = FldDef(flds.pin, 2, 2, gf.FldLabel)
    name = FldDef(flds.name, 15, 15, gf.FldEntry)
    on = FldDef(flds.on, 1, 1, gf.FldBool)
    onPos = FldDef(flds.onPos, 1, 1, gf.FldBool, isDisable=True)
