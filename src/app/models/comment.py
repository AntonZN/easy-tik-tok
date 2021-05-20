from tortoise import Tortoise
from tortoise import models, fields
from tortoise.contrib.pydantic import pydantic_model_creator


class Comment(models.Model):
    id = fields.IntField(pk=True)
    text = fields.TextField()
    user = fields.ForeignKeyField("models.User", related_name="user_comments")
    video = fields.ForeignKeyField("models.Video", related_name="video_comments")
    reply_to = fields.ForeignKeyField(
        "models.Comment", null=True, on_delete=fields.CASCADE, related_name="replies"
    )


Tortoise.init_models(
    ["app.models.video", "app.models.user", "app.models.comment"], "models"
)
CommentModel = pydantic_model_creator(
    Comment, exclude=("video", "reply_to", "video_id", "replies")
)
CommentCreateModel = pydantic_model_creator(
    Comment, exclude=("user_id",), exclude_readonly=True
)
