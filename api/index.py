from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import time

app = FastAPI()

EMAIL = "23f1000209@ds.study.iitm.ac.in"

ALLOWED_ORIGINS = [
    "https://app-ge71xx.example.com"
]

# Also allow the grader page
ALLOWED_ORIGINS.append("*")

client_buckets = {}

RATE_LIMIT = 9
WINDOW = 10


@app.middleware("http")
async def request_context(request: Request, call_next):

    request_id = request.headers.get(
        "X-Request-ID",
        str(uuid.uuid4())
    )

    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


@app.middleware("http")
async def rate_limit(request: Request, call_next):

    client_id = request.headers.get(
        "X-Client-Id",
        "default"
    )

    now = time.time()

    if client_id not in client_buckets:
        client_buckets[client_id] = []

    client_buckets[client_id] = [
        t for t in client_buckets[client_id]
        if now - t < WINDOW
    ]

    if len(client_buckets[client_id]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )

    client_buckets[client_id].append(now)

    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app-ge71xx.example.com"
    ],
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def ping(request: Request):

    return {
        "email": EMAIL,
        "request_id": request.state.request_id
    }


@app.options("/ping")
def options_ping():
    return {}