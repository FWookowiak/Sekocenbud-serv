import sentry_sdk
import os
from fastapi import FastAPI
from routers.routerexample import router
from dbf_views import router as test_router

ENVIRONMENT = os.environ.get("environment", "local")


app = FastAPI()

if ENVIRONMENT != "local":
    sentry_sdk.init(dsn="SENTRY_DSN")
    app.add_middleware(SentryAsgiMiddleware)

app.include_router(router)
app.include_router(test_router)

@app.get("/health-check", response_model=dict)
def health_check():
    return {"message": "success"}
