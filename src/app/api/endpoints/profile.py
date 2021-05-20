from typing import Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi_versioning import version

from app import schemas
from app.api import deps
from app.core.config import get_settings
from app.models.user import User, UserModel, UserFollowing
from fastapi_pagination import Page
from fastapi_pagination import PaginationParams
from app.models.video import VideoModel, Video
from app.utils.paginator import video_paginate, users_paginate

settings = get_settings()
router = APIRouter()


@router.get(
    "/my",
    response_model=UserModel,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": schemas.HTTPBadRequest},
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.HTTPUnauthorized},
        status.HTTP_403_FORBIDDEN: {"model": schemas.HTTPForbidden},
        status.HTTP_404_NOT_FOUND: {"model": schemas.HTTPNotFound},
    },
)
@version(1)
async def read_user(
    current_user: UserModel = Depends(deps.get_current_active_user),
) -> Any:
    return current_user


@router.get(
    "/my/videos",
    response_model=Page[VideoModel],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.HTTPUnauthorized},
    },
)
@version(1)
async def all_videos(
    params: PaginationParams = Depends(),
    current_user=Depends(deps.get_current_user),
) -> Any:
    return await video_paginate(
        Video.filter(user=current_user).order_by("-created"),
        params,
    )


@router.get(
    "/my/followings",
    response_model=Page[UserModel],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.HTTPUnauthorized},
    },
)
@version(1)
async def followings(
    params: PaginationParams = Depends(),
    current_user=Depends(deps.get_current_user),
) -> Any:
    followings = (
        await UserFollowing.filter(user=current_user)
        .order_by("-created")
        .values_list("following_user_id", flat=True)
    )

    return await users_paginate(
        User.filter(id__in=followings),
        params,
    )


@router.get(
    "/my/followers",
    response_model=Page[UserModel],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.HTTPUnauthorized},
    },
)
@version(1)
async def followers(
    params: PaginationParams = Depends(),
    current_user=Depends(deps.get_current_user),
) -> Any:
    followings = await UserFollowing.filter(following_user=current_user).values_list(
        "user_id", flat=True
    )

    return await users_paginate(
        User.filter(id__in=followings),
        params,
    )
