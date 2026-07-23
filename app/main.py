from fastapi import FastAPI
from app.api.routes import auth, candidature, offre, stats
from app.api.routes import admin
from app.middlewares.request_id import RequestIDMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware
app = FastAPI(
title="StageFlow API",
description="Gestion sécurisée des stages data — Master DSIA",
version="1.0.0",
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

app.include_router(auth.router)
app.include_router(offre.router)
app.include_router(candidature.router)
app.include_router(auth.router_users)
app.include_router(stats.router)
app.include_router(admin.router)
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}