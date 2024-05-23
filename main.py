import random
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from gen import get_board

app = FastAPI() # This is what will be refrenced in config
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root(seed: Optional[str]=None, motto: Optional[int]=None, bottom: Optional[int]=0):
    if not motto:
        motto = random.randint(1,10)
    html = get_board(seed, motto, bottom)
    return HTMLResponse(html)
