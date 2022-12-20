from bleak import BleakScanner, BleakClient, backends, exc
from atmon_lang import *
from atmon_conf import *
import asyncio
import struct
import subprocess
import os

DATALEN = 36
DATADLMBYTE = 255

class AtorchInfo:
    def __init__(self) -> None:
        pass
    def __str__(self) -> str:
        p = ""
        for index, item in self.__dict__.items():
            p += f'{LANGVAR[LANGUAGE].get(index, index)}: {item}\n'
        return p


scanner = BleakScanner()
atinfo = AtorchInfo()


async def main():
    os.system('clear')
    subprocess.run('bluetoothctl power off; bluetoothctl power on', shell=True)
    while True:
        devices = await scanner.discover()
        os.system('clear')
        print(f'''{LANGVAR[LANGUAGE].get('SCANFOR', 'SCANFOR')} {TARGET_NAME}...\n''')
        for d in devices:
            print(f'[{d.address}] {d.name}')
        for dev in devices:
            if TARGET_NAME == dev.name:
                print(LANGVAR[LANGUAGE].get('TGTFOUND', 'TGTFOUND'))
                await connect(dev)
        print('')


async def connect(dev: backends.device.BLEDevice):
    async with BleakClient(dev) as client:
        print(f"{LANGVAR[LANGUAGE].get('CONNECTED', 'CONNECTED')}: {client.is_connected}")
        try:
            await client.pair()
            print(f'''{LANGVAR[LANGUAGE].get('DEVPAIR', 'DEVPAIR')}''')
            await client.start_notify(CHAR2, handleNotify)
        except exc.BleakError as ex:
            print(ex.with_traceback())
        while await client.is_connected():
            await asyncio.sleep(1)
        else:
            print(f'''{LANGVAR[LANGUAGE].get('CONLOST', 'CONLOST')}''')


async def handleNotify(_, data: bytearray):
    
    dlist = list(data)
    pktStart = dlist.index(DATADLMBYTE)
    dlist = [*dlist[pktStart:], *dlist[:pktStart]]

    if len(dlist) == DATALEN:

        atinfo.volts = float(struct.unpack('>H', bytes(dlist[5:7]))[0])/10
        atinfo.amperes = float(struct.unpack('>H', bytes(dlist[8:10]))[0])/1000
        atinfo.powerdraw = float(struct.unpack('>H', bytes(dlist[11:13]))[0])/10
        atinfo.kwhs = float(struct.unpack('>I', bytes(dlist[13:17]))[0])/100
        atinfo.frequency = float(struct.unpack('>H', bytes(dlist[20:22]))[0])/10
        atinfo.temp = dlist[25]
        atinfo.price = float(dlist[19])/100
        atinfo.timehour = struct.unpack('>H', bytes(dlist[26:28]))[0] #USELESS
        atinfo.timeminute = dlist[28] #USELESS
        atinfo.timesecond  = dlist[29] #USELESS
        atinfo.standbytime = dlist[30] #USELESS
        #print(dlist)
        print(atinfo)


if __name__ == '__main__':
    asyncio.run(main())

