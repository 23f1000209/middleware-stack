from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from uuid import uuid4
import time

app = FastAPI()

EMAIL = "23f1000209@ds.study.iitm.ac.in"

RATE_LIMIT = 9
WINDOW = 10

client_requests = {}

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app-ge71xx.example.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Context Middleware
@app.middleware("http")
async def request_context(request: Request, call_next):

    request_id = request.headers.get("X-Request-ID")

    if not request_id:
        request_id = str(uuid4())

    request.state.request_id = request_id

    response = await call_next(request)

    # REQUIRED BY GRADER
    response.headers["X-Request-ID"] = request_id

    return response


# Rate Limit Middleware
@app.middleware("http")
async def rate_limit(request: Request, call_next):

    client_id = request.headers.get("X-Client-Id", "default")
    now = time.time()

    if client_id not in client_requests:
        client_requests[client_id] = []

    client_requests[client_id] = [
        t for t in client_requests[client_id]
        if now - t < WINDOW
    ]

    if len(client_requests[client_id]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )

    client_requests[client_id].append(now)

    return await call_next(request)


@app.get("/")
def home():
    return {"message": "Middleware Stack API"}


@app.get("/ping")
def ping(request: Request):
    return {
        "email": EMAIL,
        "request_id": request.state.request_id
    }


@app.options("/ping")
def options_ping():
    return {}