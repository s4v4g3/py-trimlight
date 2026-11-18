import asyncio
import logging

from py_trimlight.trimlight_local_client import TrimlightLocalClient


async def main():
    async with TrimlightLocalClient("10.4.1.90", reply_timeout=1) as _client:
        print("Connected to Trimlight device")
        # state = await client.get_state()
        # print(f"Device state: {state}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    asyncio.run(main())
