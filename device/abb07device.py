from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.exc import BleakError
import logging, asyncio, json
from device.constants import abb07_chars

class abb07_device():

    def __init__(self):
        self._command = bytes([0xCA, 0xFD, 0x00, 0x06, 0x09, 0xD6]) # default command to request all sensor data from charger
        self._rawdata = bytearray()
        self._sensordata = {} # json object of the sensor data
        self.refreshrate = int(10) # default refresh sensor data every 10 seconds
 

    @property
    def sensordata(self):
        return self._sensordata


    async def connect(self, adapter: str, addr_str: str, addr_type: str, timeout: float):
        device = await BleakScanner.find_device_by_address(addr_str, timeout=timeout, adapter=adapter)
        assert device, f'No matching device found!'

        self.dev = BleakClient(device, address_type=addr_type,timeout=timeout, disconnected_callback=self.handle_disconnect)

        logging.info(f'Trying to connect with {device}')
        await self.dev.connect()
        logging.info(f'Device {self.dev.address} connected')

        logging.info(f'Setting up chars')
        self.write_char = self.find_char(['write', 'write-without-response'])
        self.read_char = self.find_char(['notify', 'indicate'])
        await self.dev.start_notify(self.read_char, self.handle_notify)

        logging.info(f'Setting up sensor data')
        await self.setup_sensor_data()

        logging.info(f'Starting refresh loop')
        self._task = asyncio.create_task(self.refresh_sensor_data())


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
        logging.info(f'Found {name} characteristic {found.uuid} (H. {found.handle})')
        return found


    async def disconnect(self):
        if hasattr(self, 'dev') and self.dev.is_connected:
            if hasattr(self, 'read_char'):
                await self.dev.stop_notify(self.read_char)
            await self.dev.disconnect()
            logging.info('Bluetooth disconnected')


    def handle_notify(self, handle: int, data: bytes):
        logging.debug(f'Received notify from {handle}: {data}')
        self._rawdata.extend(data)


    def handle_disconnect(self, client: BleakClient):
        logging.warning(f'Device {client.address} disconnected')


    async def setup_sensor_data(self):
        dataobject = {
            "sensors": [
                {"name":"liv", "value":0},
                {"name":"riv", "value":0},
                {"name":"lov", "value":0},
                {"name":"rov", "value":0},
                {"name":"li", "value":0},
                {"name":"mt", "value":0},
                {"name":"ft", "value":0},
                {"name":"rt", "value":0},
                {"name":"vtrgt", "value":0},
                {"name":"vfloat", "value":0},
                {"name":"vboost", "value":0}
            ] }
        self._sensordata = json.dumps(dataobject)


    async def refresh_sensor_data(self):
        while True:
            logging.debug(f'Refreshing sensor data')
            self._rawdata.clear()
            await self.dev.write_gatt_char(self.write_char, self._command)
            await asyncio.sleep(1)
            await self.process_respons()
            await asyncio.sleep(self.refreshrate)


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
                        dataobject = {
                            "sensors": [
                                {"name":"liv", "value":liv},
                                {"name":"riv", "value":riv},
                                {"name":"lov", "value":lov},
                                {"name":"rov", "value":rov},
                                {"name":"li", "value":li},
                                {"name":"mt", "value":mt},
                                {"name":"ft", "value":ft},
                                {"name":"rt", "value":rt},
                                {"name":"vtrgt", "value":vtrgt},
                                {"name":"vfloat", "value":vfloat},
                                {"name":"vboost", "value":vboost}
                            ] }
                        self._sensordata = json.dumps(dataobject)
                        logging.debug(self.sensordata)
                    else:
                        logging.error(f'Incorrect checksum')
                else:
                    logging.error(f'Incorrect message length')
            else:
                logging.error(f'Respons doesn\'t contain magic header')
        else:
            logging.error(f'No data received')

