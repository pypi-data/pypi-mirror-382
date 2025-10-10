#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : runware
# @Time         : 2025/10/9 16:34
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from meutils.db.redis_db import redis_aclient
from meutils.llm.clients import AsyncClient
from meutils.notice.feishu import send_message_for_images
from meutils.io.files_utils import to_url, to_url_fal
from meutils.schemas.image_types import ImageRequest, RecraftImageRequest, ImagesResponse
from openai import BadRequestError

from meutils.apis.translator import deeplx


async def generate(request: ImageRequest, api_key: str, base_url: Optional[str] = None):
    payload = {
        **request.model_dump(exclude_none=True, exclude={"extra_fields", "aspect_ratio"}),
        **(request.extra_fields or {})
    }
    payload = [
        {
            "taskUUID": str(uuid.uuid4()),
            "taskType": "imageInference",
            "model": request.model,
            "positivePrompt": await deeplx.llm_translate(request.prompt),

            "numberResults": request.n,
            # "width": 1024,
            # "height": 1024,  # aspect_ratio todo 如何映射到 width/height
            "aspectRatio": request.aspect_ratio,

            "includeCost": True,
            "outputFormat": "PNG",
            "outputType": [
                "URL"
            ],

            **payload
        }
    ]

    if image_urls := request.image_urls:
        if not image_urls[0].startswith("http"):  # 转换为url
            image_urls = await to_url_fal(image_urls, content_type="image/png")

        payload[0]["referenceImages"] = image_urls

    if aspect_ratio_mapping := await redis_aclient.get(f"runware:{request.model}"):
        aspect_ratio_mapping = aspect_ratio_mapping.decode()
        logger.debug(aspect_ratio_mapping)
        aspect_ratio_mapping = json.loads(aspect_ratio_mapping)

        size = aspect_ratio_mapping.get(request.aspect_ratio)
        if size and isinstance(size, list):
            size = size[-1]  # 取最高清

        payload[0]["width"], payload[0]["height"] = map(int, size.split("x"))

    logger.debug(bjson(payload))
    try:
        client = AsyncClient(base_url="https://api.runware.ai/v1", api_key=api_key, timeout=300)
        response = await client.post(
            "/",
            body=payload,
            cast_to=object
        )

        if data := response.get("data"):
            for d in data:
                d["url"] = d["imageURL"]

            payload[0]["data"] = data
            send_message_for_images(payload[0], title=__file__)  # 存图片

            return ImagesResponse(data=data)
        elif errors := response.get("errors"):
            raise Exception(errors[0].get("message"))

    except BadRequestError as e:
        _ = e.response.json().get("errors")[0].get("allowedValues", "")  # 缓存redis
        logger.error(bjson(_))

        await redis_aclient.set(f"runware:{request.model}", json.dumps(_), ex=30 * 24 * 3600)

        raise e


if __name__ == '__main__':
    model = "google:2@1"
    model = "google:2@3"
    # model = "bfl:3@1"
    # prompt = "一个裸体少女"
    prompt = "a cat"
    request = ImageRequest(model=model, prompt=prompt, aspect_ratio="1:1")

    # request = ImageRequest(
    #     model=model,
    #     prompt="将鸭子放在女人的t恤上",
    #     aspect_ratio="1:1",
    #     image=[
    #         "https://v3.fal.media/files/penguin/XoW0qavfF-ahg-jX4BMyL_image.webp",
    #         "https://v3.fal.media/files/tiger/bml6YA7DWJXOigadvxk75_image.webp"
    #     ]
    # )

    logger.debug(request)
    arun(generate(request, api_key="Fk3Clsgcwc3faIvbsjDajGFATJLfaWpE"))
