from fastapi import APIRouter

from app.api.endpoints import video, login, user, comment, profile

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(profile.router, tags=["profile"])
api_router.include_router(user.router, tags=["user"])
api_router.include_router(video.router, prefix="/videos", tags=["video"])
api_router.include_router(comment.router, prefix="/comments", tags=["comment"])
