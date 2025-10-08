import asyncio

from src.pyutx import apyutx


async def test_okx():
    okx = apyutx("okx", config={"demo": True})

    candles = await okx.get_candles("BTC-USDT-SWAP", "1h", limit=100)

    await okx.close()

    print(candles)
    print(len(candles))


async def test_binance_usdm():
    binance_usdm = apyutx("binance_usdm", config={"demo": True})

    candles = await binance_usdm.get_candles("BTCUSDTe", "1h", limit=100)

    await binance_usdm.close()

    print(candles)
    print(len(candles))


async def test_bybit_usdm():
    bybit = apyutx("bybitusdm", config={"demo": True})

    candles = await bybit.get_candles("BTCUSDT", "1h", limit=100)

    await bybit.close()

    print(candles)
    print(len(candles))


async def test_bingxusdm():
    bingx = apyutx("bingxusdm", config={"demo": True})

    candles = await bingx.get_candles("BTC-USDT", "1h", limit=100, since=1759590000000)

    await bingx.close()

    print(candles)
    print(len(candles))


if __name__ == "__main__":
    asyncio.run(test_binance_usdm())
