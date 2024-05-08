import logging, asyncio

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.exc import BleakError

abb07_chars = [
    '0000ffe1-0000-1000-8000-00805f9b34fb'
]


class ABB07Device:

    def __init__(self, addr_str: str, timeout: float, keep_connected: bool):
        self._command = bytes([0xCA, 0xFD, 0x00, 0x06, 0x09, 0xD6]) # default command to request all sensor data from charger
        self._rawdata = bytearray()
        self._sensordata = {}
        self._is_connected = False
        self._addr_str = addr_str
        self._timeout = timeout
        self._keep_connected = keep_connected

    @property
    def addr_str(self):
        return str(self._addr_str)

    @property
    def timeout(self):
        return float(self._timeout)

    @property
    def sensordata(self):
        return self._sensordata

    @property
    def is_connected(self):
        return self._is_connected

    @property
    def keep_connected(self):
        return self._keep_connected

    async def connect(self) -> bool:
        device = await BleakScanner().find_device_by_address(device_identifier=self.addr_str, timeout=self.timeout)
        if not device:
            logging.eror(f'No matching device found!')
            return False

        self.dev = BleakClient(device, disconnected_callback=self.handle_disconnect, timeout=self.timeout)

        logging.debug(f'Trying to connect with {device}')
        await self.dev.connect()
        if self.dev.is_connected:
            self._is_connected = True
            logging.debug(f'Device {self.dev.address} connected')
        else:
            logging.error(f'Could not connect to {self.dev.address}')
            return False

        logging.debug(f'Setting up chars')
        self.write_char = self.find_char(['write', 'write-without-response'])
        self.read_char = self.find_char(['notify', 'indicate'])
        if not self.write_char or not self.read_char:
            logging.error(f'Could not setup chars')
            return False

        await self.dev.start_notify(self.read_char, self.handle_notify)
        return True

    def find_char(self, req_props: [str]) -> BleakGATTCharacteristic:
        name = req_props[0]

        uuid_candidates = abb07_chars
        results = []
        for srv in self.dev.services:
            for c in srv.characteristics:
                if c.uuid in uuid_candidates:
                    results.append(c)

        res_str = '\n'.join(f'\t{c} {c.properties}' for c in results)
        logging.debug(f'Characteristic candidates for {name}: \n{res_str}')

        # Check if there is a intersection of permission flags
        results[:] = [c for c in results if set(c.properties) & set(req_props)]

        assert len(results) > 0, \
            f"No characteristic with {req_props} property found!"

        assert len(results) == 1, \
            f'Multiple matching {name} characteristics found, please specify one'

        # must be valid here
        found = results[0]
        logging.debug(f'Found {name} characteristic {found.uuid} (H. {found.handle})')
        return found

    async def disconnect(self):
        if hasattr(self, 'dev') and self.dev.is_connected:
            if hasattr(self, 'read_char'):
                await self.dev.stop_notify(self.read_char)
            await self.dev.disconnect()
            self._is_connected = False
            logging.debug('Device disconnected')

    def handle_notify(self, handle: int, data: bytes):
        logging.debug(f'Received notify from {handle}: {data}')
        self._rawdata.extend(data)


    def handle_disconnect(self, client: BleakClient):
        self._is_connected = False
        logging.debug(f'Device {client.address} disconnect handled')

    async def get_sensor_data(self):
        logging.debug(f'Downloading sensor data')
        self._rawdata.clear()
        if self._is_connected:
            await self.dev.write_gatt_char(self.write_char, self._command)
            await asyncio.sleep(1)
            await self.process_respons()
        else:
            logging.warning(f'Device not connected')

        if not self._keep_connected:
            await self.disconnect()

    async def process_respons(self):
        if len(self._rawdata) > 0:
            # Check if first two bytes are magic header: 0xCA, 0xFD
            if int.from_bytes(self._rawdata[0:2]) == 51965:
                # Check if the respons is complete
                if len(self._rawdata) == int.from_bytes(self._rawdata[3:4]):
                    # Check checksum of the respons
                    checksum = int(0)
                    for i in self._rawdata[:-1]:
                        checksum = checksum + i
                    checksum = checksum & 0xFF
                    if checksum == int.from_bytes(self._rawdata[46:47]):
                        # data is ok, proceed with extracting values
                        logging.debug(f'Received: {self._rawdata.hex()}')
                        liv = float(int.from_bytes(self._rawdata[5:7], byteorder='big') * 0.0354838709677419)
                        riv = float(int.from_bytes(self._rawdata[7:9], byteorder='big') * 0.0354838709677419)
                        lov = float(int.from_bytes(self._rawdata[9:11], byteorder='big') * 0.0354838709677419)
                        rov = float(int.from_bytes(self._rawdata[11:13], byteorder='big') * 0.0354838709677419)
                        li = float(int.from_bytes(self._rawdata[13:15], byteorder='big') * 0.0358)
                        mt = int.from_bytes(self._rawdata[15:17], byteorder='big') - 273
                        ft = int.from_bytes(self._rawdata[17:19], byteorder='big') - 273
                        rt = int.from_bytes(self._rawdata[19:21], byteorder='big') - 273
                        vtrgt = float(int.from_bytes(self._rawdata[21:23], byteorder='big') * 0.0354838709677419)
                        vfloat = float(int.from_bytes(self._rawdata[23:25], byteorder='big') * 0.0354838709677419)
                        vboost = float(int.from_bytes(self._rawdata[25:27], byteorder='big') * 0.0354838709677419)
                        rund = int.from_bytes(self._rawdata[27:29], byteorder='big')
                        runh = int.from_bytes(self._rawdata[29:30], byteorder='big')
                        runm = int.from_bytes(self._rawdata[30:31], byteorder='big')
                        runs = int.from_bytes(self._rawdata[31:32], byteorder='big')
                        runms = int.from_bytes(self._rawdata[32:34], byteorder='big')
                        devh = int.from_bytes(self._rawdata[34:35], byteorder='big')
                        devm = int.from_bytes(self._rawdata[35:36], byteorder='big')
                        devs = int.from_bytes(self._rawdata[36:37], byteorder='big')
                        devms = int.from_bytes(self._rawdata[37:39], byteorder='big')
                        devicerunning = (rund * 86400) + (runh * 3600) + (runm * 60) + runs
                        deviceuptime = (devh * 3600) + (devm * 60) + devs
                        dataobject = {
                            "liv":liv,
                            "riv":riv,
                            "lov":lov,
                            "rov":rov,
                            "li":li,
                            "mt":mt,
                            "ft":ft,
                            "rt":rt,
                            "vtrgt":vtrgt,
                            "vfloat":vfloat,
                            "vboost":vboost,
                            "devicerunning":devicerunning,
                            "deviceuptime":deviceuptime
                         }
                        self._sensordata = dataobject
                        logging.debug(self.sensordata)
                    else:
                        logging.error(f'Incorrect checksum')
                else:
                    logging.error(f'Incorrect message length')
            else:
                logging.error(f'Respons doesn\'t contain magic header')
        else:
            logging.error(f'No data received')
