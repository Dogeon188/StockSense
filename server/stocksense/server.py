from fastapi import FastAPI

from stocksense.api import data_router, pilot_router


app = FastAPI(
    title="StockSense API",
    description="API for Stock Trading Automation",
    version="0.0.0",
)

app.include_router(data_router)
app.include_router(pilot_router)
