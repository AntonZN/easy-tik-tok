from enum import Enum

from tortoise import Tortoise
from tortoise import models, fields
from tortoise.contrib.pydantic import pydantic_model_creator

from app.core.config import get_settings, Storages

settings = get_settings()


class Category(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=64)
    views = fields.IntField(default=0, index=True)


class Video(models.Model):
    class LoadingStatus(str, Enum):
        PENDING = "pending"
        RUNNING = "running"
        FAIL = "fail"
        SUCCESS = "success"

    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="videos")
    category = fields.ForeignKeyField(
        "models.Category",
        null=True,
        on_delete=fields.SET_NULL,
        related_name="category_videos",
    )
    tags = fields.ManyToManyField("models.Tag", related_name="videos", null=True)
    loading_status = fields.CharEnumField(
        LoadingStatus, max_length=20, default=LoadingStatus.PENDING
    )
    storage = fields.IntEnumField(Storages, default=settings.STORAGE)
    title = fields.CharField(max_length=128)
    likes = fields.IntField(default=0, index=True)
    dislikes = fields.IntField(default=0)
    views = fields.IntField(index=True, default=0)
    size = fields.CharField(max_length=20, null=True)
    path = fields.CharField(max_length=1024, null=True)
    created = fields.DatetimeField(auto_now_add=True, index=True)

    class PydanticMeta:
        exclude = ["path"]
        exclude_raw_fields = False


class Tag(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=64, unique=True)
    views = fields.IntField(default=0, index=True)

    videos: fields.ManyToManyRelation[Video]


Tortoise.init_models(
    ["app.models.video", "app.models.user", "app.models.comment"], "models"
)
VideoAdminModel = pydantic_model_creator(Video)
VideoModel = pydantic_model_creator(
    Video,
    exclude=(
        "loading_status",
        "size",
        "video_comments",
        "storage",
        "user_id",
        "category_id",
    ),
)
CategoryModel = pydantic_model_creator(Category, name="Category")
TagModel = pydantic_model_creator(Tag, name="Tag")
