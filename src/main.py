from fastapi import FastAPI
from .routers import reservation, configuration, product, finances, auth_context, employee, google_reviews, working_hours, intelligence
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://businext.greenfourtech.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth_context.router)
app.include_router(employee.router)
app.include_router(reservation.router)
app.include_router(configuration.router)
app.include_router(product.router)
app.include_router(finances.router)
app.include_router(google_reviews.router)
app.include_router(working_hours.router)
app.include_router(intelligence.router)
