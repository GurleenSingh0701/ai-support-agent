from fastapi import FastAPI, Depends
from database import Base, engine
from logs.log_analytics_engine import analytics_engine
from users.auth_utils import require_role

# Import models to register on Base metadata
from users.user_crud import User
from tickets.ticket_crud import Ticket
from chat.chat_crud import Chat

# Create database tables
Base.metadata.create_all(bind=engine)

# Setup FastAPI application
app = FastAPI(title="Autodesk AI Support Ticketing System Backend")

# Import module routers
from users.user_routes import router as users_router
from users.user_info import router as user_info_router
from users.user_history import router as history_router
from tickets.ticket_routes import router as tickets_router
from chat.chat_routes import router as chat_router

app.include_router(users_router)
app.include_router(user_info_router)
app.include_router(history_router)
app.include_router(tickets_router)
app.include_router(chat_router)

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "Autodesk AI Ticketing System",
        "version": "2.2.0"
    }

@app.get("/analytics/summary")
def get_analytics_summary(current_user: User = Depends(require_role(["ADMIN", "SUPPORT_AGENT"]))):
    return analytics_engine.get_summary_metrics()
