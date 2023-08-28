import asyncio, logging, argparse
from device.abb07device import abb07_device

async def main():
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-a", "--adapter", help="Bluetooth adapter", required=True)
    argParser.add_argument("-d", "--device", help="ABB07 Device ID", required=True)

    args = argParser.parse_args()

    ADAPTER = args.adapter
    DEVICE =  args.device

    my_abb07 = abb07_device()
    await my_abb07.connect(ADAPTER, DEVICE, "public", 10.0)
    await asyncio.sleep(5.0)
    print(my_abb07.sensordata())
    await my_abb07.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

