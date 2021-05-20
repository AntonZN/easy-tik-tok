from typing import Any

from fastapi import APIRouter, HTTPException, status, Response, Depends
from fastapi_versioning import version
from tortoise.exceptions import DoesNotExist

from app import schemas
from app.api import deps
from app.core import security
from app.models.user import UserModel, User, UserFollowing

router = APIRouter()


@router.post(
    "/user/",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": schemas.HTTPBadRequest},
    },
)
@version(1)
async def create(form_data: schemas.UserCreate) -> Any:
    user, created = await User.get_or_create(
        email=form_data.email, username=form_data.username
    )
    if not created:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email: {form_data.email} already exists",
        )
    user.password_hash = security.get_password_hash(form_data.password)
    await user.save()
    return Response(status_code=status.HTTP_201_CREATED)


@router.get(
    "/user/{user_id}",
    response_model=UserModel,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": schemas.HTTPBadRequest},
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.HTTPUnauthorized},
        status.HTTP_403_FORBIDDEN: {"model": schemas.HTTPForbidden},
        status.HTTP_404_NOT_FOUND: {"model": schemas.HTTPNotFound},
    },
)
@version(1)
async def get_user(
    user_id: int,
    _=Depends(deps.get_current_active_user),
) -> Any:
    try:
        return await UserModel.from_queryset_single(User.get(id=user_id))
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found"
        )


@router.post(
    "/user/{user_id}/follow",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": schemas.HTTPBadRequest},
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.HTTPUnauthorized},
        status.HTTP_403_FORBIDDEN: {"model": schemas.HTTPForbidden},
        status.HTTP_404_NOT_FOUND: {"model": schemas.HTTPNotFound},
    },
)
@version(1)
async def follow_user(
    user_id: int,
    current_user=Depends(deps.get_current_user),
) -> Any:
    try:
        print(current_user)
        user, created = await UserFollowing.get_or_create(
            user=current_user, following_user_id=user_id
        )
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The user you want to subscribe to no longer exists",
        )
    if not created:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You are already subscribed to the user",
        )


@router.delete(
    "/user/{user_id}/unfollow",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": schemas.HTTPBadRequest},
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.HTTPUnauthorized},
        status.HTTP_403_FORBIDDEN: {"model": schemas.HTTPForbidden},
        status.HTTP_404_NOT_FOUND: {"model": schemas.HTTPNotFound},
    },
)
@version(1)
async def un_follow_user(
    user_id: int,
    current_user=Depends(deps.get_current_user),
) -> Any:
    await UserFollowing.filter(user=current_user, following_user_id=user_id).delete()


@router.delete(
    "/user/{user_id}",
    response_model=None,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": schemas.HTTPBadRequest},
        status.HTTP_401_UNAUTHORIZED: {"model": schemas.HTTPUnauthorized},
        status.HTTP_403_FORBIDDEN: {"model": schemas.HTTPForbidden},
        status.HTTP_404_NOT_FOUND: {"model": schemas.HTTPNotFound},
    },
)
@version(1)
async def delete_user(user_id: int, _=Depends(deps.get_current_super_user)):
    deleted_count = await User.filter(id=user_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found"
        )
