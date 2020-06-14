import websockets
import asyncio
import logging

import settings

logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(name)s: %(message)s", level=logging.WARNING
)
logger = logging.getLogger(__name__)


async def send_websocket(websocket, path):
    """Sends meter data to the websocket when connected"""
    while True:

        # Grab a json object of the current data
        if path != "/":
            try:
                meter_id = int(path[1])
            except ValueError:  # Not a number was passed
                meter_id = 0
        else:
            meter_id = 0

        # Grab the meter object from the settings file using the index passed
        meter = settings.multi_meters[meter_id]

        try:
            data = meter.get_json()
        except IndexError:  # Default to meter 0 if value passed is invalid
            data = meter.get_json()

        try:
            # Send it to the web socket
            await websocket.send(data)
        except websockets.exceptions.ConnectionClosedOK:
            # Catch if a client disconnects and ignore it
            # This was done to prevent traceback errors in the console
            pass

        # Send data to the console
        logger.debug(data)

        # We don't need the data at blazing fast speeds, plus it causes websocket errors when sending too fast.
        await asyncio.sleep(0.25)


if __name__ == "__main__":
    print("Ready to connect to the meter...")

    # Setup our websocket loop
    websocket_loop = websockets.serve(send_websocket, "0.0.0.0", 18881)

    # Create our async loop
    loop = asyncio.get_event_loop()

    # Run all of our loops
    loop.run_until_complete(websocket_loop)

    # Load all of the meters that are in settings into the loop
    for meter in settings.multi_meters:
        loop.create_task(meter.run())

    # forever
    loop.run_forever()