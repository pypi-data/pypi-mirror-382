#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : images
# @Time         : 2025/10/9 11:55
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
import httpx

from meutils.pipe import *
from meutils.llm.clients import AsyncClient

from meutils.schemas.image_types import ImageRequest, ImagesResponse


async def generate(request: ImageRequest, api_key: str, base_url: Optional[str] = None):
    if request.model.startswith("gemini"):
        # model = "gemini-2.5-flash-image-preview"
        if request.image:
            request.model += "-image-edit"
        else:
            request.model += "-text-to-image"

    payload = {
        "model": request.model,
        "prompt": request.prompt
    }

    # gemini-2.5-flash-image-preview-text-to-image
    if request.image_urls:
        payload["image_urls"] = request.image_urls

    logger.debug(bjson(payload))

    base_url = f"https://api.ppinfra.com/v3"
    client = AsyncClient(base_url=base_url, api_key=api_key)
    response = await client.post(
        request.model,
        body=payload,
        cast_to=object
    )
    if image_urls := response.get("image_urls"):
        data = [{"url": image_url} for image_url in image_urls]
        return ImagesResponse(data=data)
    else:
        raise Exception(f"生成图片失败: {response} \n\n{request}")


if __name__ == '__main__':
    # request = ImageRequest(
    #     model="gemini-2.5-flash-image-preview",
    #     # prompt="a cat",
    #
    # )

    request = ImageRequest(
        model="gemini-2.5-flash-image-preview",
        prompt="将小鸭子放在女人的t恤上",
        size="1024x1024",
        image=[
            "https://v3.fal.media/files/penguin/XoW0qavfF-ahg-jX4BMyL_image.webp",
            "https://v3.fal.media/files/tiger/bml6YA7DWJXOigadvxk75_image.webp"
        ]
    )

    arun(generate(request, api_key="sk_eZg7P5Jih5IzqTEHdmSR7OtcSltaDaPlqdxo7x5zWUQ"))

"""
curl --location --request POST 'https://api.ppinfra.com/v3/gemini-2.5-flash-image-preview-text-to-image' \
--header 'Authorization: Bearer sk_eZg7P5Jih5IzqTEHdmSR7OtcSltaDaPlqdxo7x5zWUQ' \
--header 'Content-Type: application/json' \
--data-raw '{
   "prompt":"a cute dog"
}'
"""
