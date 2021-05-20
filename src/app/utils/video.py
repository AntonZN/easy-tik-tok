import logging
import os
from uuid import uuid4

import aioboto3
import aiofiles
import filetype
from fastapi import UploadFile

from app.core.config import Storages
from app.core.config import get_settings
from app.helpers.media import get_file_size, encode_file
from app.models.video import Video

settings = get_settings()

logger = logging.getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL)


async def video_streamer(path: str):
    if settings.STORAGE == Storages.AWS_S3:
        chunk_size = 69 * 1024
        async with aioboto3.client(
            service_name="s3",
            endpoint_url=settings.STORAGE_ENDPOINT_URL,
        ) as s3:
            logger.debug(f"Serving {settings.BUCKET_NAME} {path}")
            s3_ob = await s3.get_object(Bucket=settings.BUCKET_NAME, Key=path)
            async with s3_ob["Body"] as stream:
                while True:
                    chunk = await stream.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

    elif settings.STORAGE == Storages.LOCAL:
        async with aiofiles.open(path, mode="rb") as f:
            lines = await f.readlines()
            for line in lines:
                yield line


def _generate_filename(file: UploadFile):
    content_type = filetype.get_type(file.content_type)
    return f"{uuid4().hex}.{content_type.EXTENSION}"


def remove_video(file_path: str):
    os.remove(file_path)
    logger.debug(f"Tmp file {file_path} - removed")


async def write_video(video_obj: Video, upload_to: str, file: UploadFile):
    filename = _generate_filename(file)
    tmp_file_root = os.path.join(settings.MEDIA_ROOT, "tmp")
    tmp_file = os.path.join(tmp_file_root, filename)
    final_file_root = os.path.join(settings.MEDIA_ROOT, upload_to)
    final_file_path = os.path.join(final_file_root, filename)

    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)

    if not os.path.exists(tmp_file_root):
        os.makedirs(tmp_file_root)

    if not os.path.exists(final_file_root):
        os.makedirs(final_file_root)

    try:
        logger.debug(f" Start saving file: {filename}")
        async with aiofiles.open(tmp_file, mode="wb") as f:
            data = await file.read()
            await f.write(data)
    except OSError as e:
        logger.error(str(e))
        video_obj.loading_status = Video.LoadingStatus.FAIL
        await video_obj.save()

    logger.debug(f"File {filename} - saved")
    video_obj.loading_status = Video.LoadingStatus.RUNNING
    await video_obj.save()
    logger.debug(f"Start encoding file: {filename}")
    status, detail = await encode_file(tmp_file, final_file_path)

    if not status:
        logger.error(f"Encoding file fail: {detail}")
        video_obj.loading_status = Video.LoadingStatus.FAIL
        await video_obj.save()
    else:
        logger.debug(f"Encoding file success")
        logger.debug(f"Start upload file to aws")
        file_size = await get_file_size(final_file_path)
        video_obj.size = file_size
        video_obj.loading_status = Video.LoadingStatus.SUCCESS

        if settings.STORAGE == Storages.AWS_S3:
            key = f"{upload_to}/{filename}"
            aws_upload_status = await upload_to_aws(key, final_file_path)
            if aws_upload_status:
                video_obj.path = key
                video_obj.storage = Storages.AWS_S3
                remove_video(final_file_path)
            else:
                video_obj.path = final_file_path
                video_obj.storage = Storages.LOCAL
        await video_obj.save()
    remove_video(tmp_file)


async def upload_to_aws(
    filename: str,
    staging_path: str,
):
    async with aioboto3.client(
        service_name="s3",
        endpoint_url=settings.STORAGE_ENDPOINT_URL,
    ) as s3:
        try:
            async with aiofiles.open(staging_path, mode="rb") as file:
                await s3.upload_fileobj(file, settings.BUCKET_NAME, filename)
            logger.debug(f"Upload file to aws success")
            return True
        except Exception as e:
            logger.error(f"Upload file to aws error, detail: {e}")
            return False
