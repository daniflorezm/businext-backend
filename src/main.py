from fastapi import FastAPI
from .routers import reservation, configuration, product, finances
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(reservation.router)
app.include_router(configuration.router)
app.include_router(product.router)
app.include_router(finances.router)
