from typing import Optional, Type, Union

from fastapi_pagination.api import create_page, resolve_params
from fastapi_pagination.bases import (
    AbstractPage,
    AbstractParams,
)
from tortoise.models import Model
from tortoise.queryset import QuerySet

from app.models.comment import CommentModel
from app.models.video import VideoModel
from app.models.user import UserModel


async def video_paginate(
    query: Union[QuerySet, Type[Model]], params: Optional[AbstractParams] = None
) -> AbstractPage:
    if not isinstance(query, QuerySet):
        query = query.all()

    params = resolve_params(params)

    limit_offset_params = params.to_limit_offset()

    total = await query.count()
    items = await VideoModel.from_queryset(
        query.offset(limit_offset_params.offset).limit(limit_offset_params.limit).all()
    )

    return create_page(items, total, params)


async def comments_paginate(
    query: Union[QuerySet, Type[Model]], params: Optional[AbstractParams] = None
) -> AbstractPage:
    if not isinstance(query, QuerySet):
        query = query.all()

    params = resolve_params(params)

    limit_offset_params = params.to_limit_offset()

    total = await query.count()
    items = await CommentModel.from_queryset(
        query.offset(limit_offset_params.offset).limit(limit_offset_params.limit).all()
    )

    return create_page(items, total, params)


async def users_paginate(
    query: Union[QuerySet, Type[Model]], params: Optional[AbstractParams] = None
) -> AbstractPage:
    if not isinstance(query, QuerySet):
        query = query.all()

    params = resolve_params(params)

    limit_offset_params = params.to_limit_offset()

    total = await query.count()
    items = await UserModel.from_queryset(
        query.offset(limit_offset_params.offset).limit(limit_offset_params.limit).all()
    )

    return create_page(items, total, params)
