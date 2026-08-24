from fastapi import FastAPI

from backend.app.database import Base, engine
from backend.app.models.transaction import Transaction
from backend.app.routes.payments import router as payment_router
from backend.app.models.payment_attempt import PaymentAttempt
from backend.app.routes.analytics import router as analytics_router
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Payment Reliability and Recovery Agent",
    description="AI-powered payment failure analysis and recovery system",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payment_router)
app.include_router(analytics_router)


@app.get("/")
def root():
    return {
        "message": "AI Payment Reliability and Recovery Agent is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected"
    }