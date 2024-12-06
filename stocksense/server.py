from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from stocksense.api import data_router, pilot_router


app = FastAPI(
    title="StockSense API",
    description="API for Stock Trading Automation",
    version="0.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data_router)
app.include_router(pilot_router)
