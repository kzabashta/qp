import logging
import json
import os

import asyncio
from influxdb import InfluxDBClient

from questrade import QTClient

logging.basicConfig(level=logging.DEBUG,
                        format="[%(asctime)s:%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s",
                        handlers=[logging.FileHandler("finances.log"),
                                  logging.StreamHandler()])

REFRESH_TOKEN = os.environ["QUESTRADE_TOKEN"]
INFLUXDB_SERVER = os.environ["INFLUXDB_SERVER"]
INFLUXDB_DATABASE = os.environ["INFLUXDB_DATABASE"]

def insert_tick(tick, influx_client):
    try:
        json_body = [
            {
                "measurement": "market",
                "tags": {
                    "symbol": tick['symbol']
                },
                "fields": {
                    "bidPrice": tick['bidPrice'],
                    "bidSize": tick['bidSize'],
                    "askPrice": tick['askPrice'],
                    "askSize": tick['askSize'],
                    "lastTradePrice": tick['lastTradePrice'],
                    "lastTradeSize": tick['lastTradeSize'],
                    "volume": tick['volume'],
                    "VWAP": tick['VWAP']
                }
            }
        ]
        influx_client.write_points(json_body)
    except Exception:
        logging.exception("message")

if __name__ == '__main__':
    logging.info("Connecting to Questrdate")
    client = QTClient(REFRESH_TOKEN)
    logging.info("Connecting to InfluxDB")
    influx_client = InfluxDBClient(host=INFLUXDB_SERVER, database=INFLUXDB_DATABASE)
    logging.info("OK")
    async def scraper(ticks):
        ticks = json.loads(ticks)
        if 'quotes' in ticks:
            for tick in ticks['quotes']:
                insert_tick(tick, influx_client)

    asyncio.get_event_loop().run_until_complete(client.subscribe(['8049', '9292'], scraper))