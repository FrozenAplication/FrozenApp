from fastapi import FastAPI
from routers import auth, users, access, reports

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(access.router)
app.include_router(reports.router)
