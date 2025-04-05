import sys
import time

sys.path.append('/home/rho/Python/arduino/havsmolf/disp/')
from guiflds import Fld
import guiflds as gf
from guiflddefs import FldDef


def tsf(ts: float) -> str:
    return time.strftime("%a %H:%M:%S", time.localtime(ts))


class flds:
    no = Fld("no", "No", "No",
             str, str,
             "w",
             isKey=True
             )
    pin = Fld("pin", "Pin", "Pin",
              str, int,
              "e")
    name = Fld("name", "Name", "Name",
               str, str,
               "w"
               )
    temp = Fld("temp", "Temperature", "Temp",
               str, int,
               "e")
    ts = Fld("ts", "Timestamp", "Time",
             tsf, None)
    tempType = Fld("temptype", "Type", "Type",
                   str, str,
                   "w"
                   )
    on = Fld("on", "On", "On",
             None, None,
             "e"
             )
    onPos = Fld("positiv-on", "On Positive", "On Pos",
                None, None,
                "e"
                )


class temps:
    no = FldDef(flds.no, 2, 2, gf.FldLabel)
    pin = FldDef(flds.pin, 2, 2, gf.FldLabel)
    name = FldDef(flds.name, 15, 15, gf.FldLabel)
    temp = FldDef(flds.temp, 4, 4, gf.FldLabel, isJson=False)
    ts = FldDef(flds.ts, 13, 13, gf.FldLabel, isJson=False)


class relays:
    no = FldDef(flds.no, 2, 2, gf.FldLabel)
    pin = FldDef(flds.pin, 2, 2, gf.FldLabel)
    name = FldDef(flds.name, 15, 15, gf.FldEntry)
    on = FldDef(flds.on, 1, 1, gf.FldBool)
    onPos = FldDef(flds.onPos, 1, 1, gf.FldBool)
