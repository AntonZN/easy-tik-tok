from typing import Any

from fastapi import (
    APIRouter,
    status,
    Depends,
    HTTPException,
)
from fastapi_pagination import Page
from fastapi_pagination import PaginationParams
from fastapi_versioning import version

from app import schemas
from app.api import deps
from app.core.config import get_settings
from app.models.comment import Comment, CommentModel, CommentCreateModel
from app.models.video import Video
from app.utils.paginator import comments_paginate

settings = get_settings()

router = APIRouter()


@router.get(
    "/{video_id}/",
    response_model=Page[CommentModel],
)
@version(1)
async def get_comments(
    video_id: str,
    params: PaginationParams = Depends(),
) -> Any:
    return await comments_paginate(Comment.filter(video_id=video_id), params)


@router.post(
    "/",
    response_model=CommentModel,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.HTTPUnauthorized},
    },
)
@version(1)
async def create_comment(
    comment: CommentCreateModel,
    user=Depends(deps.get_current_user),
) -> Any:
    if await Video.filter(id=comment.video_id).exists():
        comment_obj = await Comment.create(
            **comment.dict(exclude_unset=True), user=user
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video {comment.video_id} not found",
        )
    return await CommentModel.from_tortoise_orm(comment_obj)
