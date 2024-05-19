import random
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from gen import get_board

app = FastAPI() # This is what will be refrenced in config
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root(seed: Optional[str]=None):
    html = get_board(seed)
    return HTMLResponse(html)
