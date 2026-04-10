from dotenv import load_dotenv

load_dotenv()  # loads .env for local dev; no-op on Lambda

from app.services.secrets import load_secrets
load_secrets()  # injects AWS Secrets Manager values into os.environ (Lambda only)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.routers import auth, cart, generation, products, projects

app = FastAPI(
    title="RoomStyle API",
    version="0.1.0",
    description="Backend API for the RoomStyle interior design app.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock down to CloudFront domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(generation.router)
app.include_router(products.router)
app.include_router(cart.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Lambda entry point (Mangum adapts ASGI → Lambda event format)
handler = Mangum(app, lifespan="off")
