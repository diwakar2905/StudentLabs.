from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, research, generate, export

app = FastAPI(
    title="StudentLabs API",
    description="Engine for turning topics into fully researched assignments and presentations.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(auth.users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(research.router, prefix="/api/v1/research", tags=["Research"])
app.include_router(generate.router, prefix="/api/v1/generate", tags=["Generate"])
app.include_router(export.router, prefix="/api/v1/export", tags=["Export"])

@app.get("/")
def root():
    return {"message": "Welcome to StudentLabs API"}
