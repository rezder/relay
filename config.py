import json
import os
import serial.tools.list_ports as sTools
import serial
import time


DEFAULT_BAUDRATE = 115200


class Config:
    def default() -> dict:
        conf = {
            "temps": {
                "1": {
                    "pin": 5,
                    "name": "no 1",
                    "type": "ds18b20"
                },
                "2": {
                    "pin": 5,
                    "name": "no 2",
                    "type": "ds18b20"
                },
                "3": {
                    "pin": 5,
                    "name": "no 3",
                    "type": "ds18b20"
                },
                "4": {
                    "pin": 6,
                    "name": "no 4",
                    "type": "ds18b20"
                },
                "5": {
                    "pin": 6,
                    "name": "no 5",
                    "type": "ds18b20"
                },
                "6": {
                    "pin": 7,
                    "name": "no 6",
                    "type": "resitor 8016"
                }
            },
            "relays": {
                "1": {
                    "pin": 1,
                    "name": "Relay 1",
                    "on": False,
                    "positiv-on": True
                },
                "2": {
                    "pin": 2,
                    "name": "Relay 2",
                    "on": False,
                    "positiv-on": True
                },
                "3": {
                    "pin": 3,
                    "name": "Relay 3",
                    "on": False,
                    "positiv-on": True
                },
                "4": {
                    "pin": 4,
                    "name": "Relay 4",
                    "on": False,
                    "positiv-on": True
                },
                "5": {
                    "pin": 10,
                    "name": "Relay 5",
                    "on": False,
                    "positiv-on": True
                },
                "6": {
                    "pin": 11,
                    "name": "Relay 6",
                    "on": False,
                    "positiv-on": True
                },
                "7": {
                    "pin": 12,
                    "name": "Relay 7",
                    "on": False,
                    "positiv-on": True
                },
                "8": {
                    "pin": 13,
                    "name": "Relay 8",
                    "on": False,
                    "positiv-on": True
                }
            },
            "mac": None
        }
        return conf

    def load(fileName) -> dict:
        if not os.path.isfile(fileName):
            conf = Config.default()
            with open(fileName, "w") as f:
                f.write(json.dumps(conf))
        with open(fileName, "r") as f:
            conf = json.load(f)
        return conf

    def save(self):
        with open(self.fileName, "w") as f:
            f.write(json.dumps(self.conf, indent=2))

    def __init__(self, isDefault=False):
        self.fileName = "./relayserver.json"
        if isDefault:
            self.conf = Config.default()
        else:
            self.conf = Config.load(self.fileName)

    def getRelayOns(self) -> list[bool]:
        res = list()
        for r in self.conf["relays"]:
            list.append(r["on"])
        return res

    def getMac(self) -> str | None:
        mac = self.conf["mac"]
        if mac is None:
            print("Mac address does not exist.\
            Try to get it from serial connection.")
            path = getSerialPath()
            if path is None:
                print("Serial connection: {}".format(path))
                con = serial.Serial(path,
                                    baudrate=DEFAULT_BAUDRATE,
                                    timeout=10)
                cmd = 'M'
                data = bytearray(cmd.encode(encoding="ascii"))
                con.write(data)
                con.flush()
                time.sleep(1.0)
                dataSize = 17
                bts = con.read(size=dataSize)
                con.close()
                if len(bts) == dataSize:
                    mac = bts.decode("ascii")
                    self.conf["mac"] = mac
                    self.save()
                    print("Mac address: {} was retrived".format(mac))
                else:
                    print("Serial data was not complete after 10 seconds")

        return mac


def getSerialPath() -> str:
    ports = sTools.comports()
    path = None
    for p in ports:
        if p.product == "Nano ESP32" or p.manufacturer == "Espressif":
            path = p.device
    return path
