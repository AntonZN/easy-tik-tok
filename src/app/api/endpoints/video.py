import os
from typing import Any, Optional

from fastapi import (
    APIRouter,
    status,
    Depends,
    BackgroundTasks,
    UploadFile,
    File,
    Form,
    HTTPException,
)
from fastapi.responses import FileResponse, StreamingResponse
from fastapi_pagination import Page
from fastapi_pagination import PaginationParams
from fastapi_versioning import version
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import F

from app import schemas
from app.api import deps
from app.core.config import Storages
from app.core.config import get_settings
from app.models.video import VideoModel, Video, Tag
from app.utils.paginator import video_paginate
from app.utils.video import write_video, remove_video, video_streamer

settings = get_settings()
router = APIRouter()


@router.get(
    "/",
    response_model=Page[VideoModel],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.HTTPUnauthorized},
    },
)
@version(1)
async def all_videos(
    tag: Optional[str] = None,
    params: PaginationParams = Depends(),
) -> Any:
    if tag is not None:
        tag_obj = await Tag.get_or_none(name=tag.strip())
        if tag_obj is not None:
            return await video_paginate(
                tag_obj.videos.filter(
                    loading_status=Video.LoadingStatus.SUCCESS
                ).order_by("-created"),
                params,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video by tag not found"
            )
    return await video_paginate(
        Video.filter(loading_status=Video.LoadingStatus.SUCCESS).order_by("-created"),
        params,
    )


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def create_video(
    tasks: BackgroundTasks,
    title: str = Form(...),
    tags: str = Form(...),
    file: UploadFile = File(...),
    user=Depends(deps.get_current_user),
):
    if file.content_type not in settings.UPLOAD_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect file type",
        )
    upload_to = "videos"
    video_obj = await Video.create(
        title=title,
        user=user,
    )
    tag_objs = []

    for tag in tags.strip().split(","):
        obj, _ = await Tag.get_or_create(name=tag)
        tag_objs.append(obj)

    await video_obj.tags.add(*tag_objs)
    tasks.add_task(write_video, video_obj, upload_to, file)
    return await VideoModel.from_tortoise_orm(video_obj)


@router.get(
    "/{video_id}/",
    response_model=VideoModel,
    responses={status.HTTP_404_NOT_FOUND: {"model": schemas.HTTPNotFound}},
)
async def get_video(
    video_id: str,
):
    try:
        await Video.filter(id=video_id).update(views=F("views") + 1)
        video = await Video.get(id=video_id)
        tags = await video.tags.all().values_list("id", flat=True)
        await Tag.filter(id__in=tags).update(views=F("views") + 1)
        return await VideoModel.from_tortoise_orm(video)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video file not found"
        )


@router.get(
    "/{video_id}/play/",
    responses={status.HTTP_404_NOT_FOUND: {"model": schemas.HTTPNotFound}},
)
async def play_video(
    video_id: str,
):
    try:
        video_obj = await Video.get(id=video_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )
    if video_obj.storage == Storages.AWS_S3:
        return StreamingResponse(video_streamer(video_obj.path), media_type="video/mp4")
    elif video_obj.storage == Storages.LOCAL:
        file_path = os.path.join(settings.MEDIA_ROOT, video_obj.path)
        return FileResponse(file_path)


@router.delete(
    "/{video_id}/",
    responses={status.HTTP_404_NOT_FOUND: {"model": schemas.HTTPNotFound}},
)
async def remove_video(
    tasks: BackgroundTasks, video_id: str, user=Depends(deps.get_current_user)
):
    video = await Video.get_or_none(id=video_id, user=user)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Video not found"
        )
    tasks.add_task(remove_video, video.path)
    await video.delete()


@router.patch(
    "/{video_id}/like/",
    response_model=VideoModel,
    responses={status.HTTP_404_NOT_FOUND: {"model": schemas.HTTPNotFound}},
)
async def like_video(video_id: str, _=Depends(deps.get_current_active_user)):
    try:
        await Video.filter(id=video_id).update(likes=F("likes") + 1)
        return await VideoModel.from_queryset_single(Video.get(id=video_id))
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video file not found"
        )


@router.patch(
    "/{video_id}/dislike/",
    response_model=VideoModel,
    responses={status.HTTP_404_NOT_FOUND: {"model": schemas.HTTPNotFound}},
)
async def dislike_video(video_id: str, _=Depends(deps.get_current_active_user)):
    try:
        await Video.filter(id=video_id).update(dislikes=F("dislikes") + 1)
        return await VideoModel.from_queryset_single(Video.get(id=video_id))
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video file not found"
        )
