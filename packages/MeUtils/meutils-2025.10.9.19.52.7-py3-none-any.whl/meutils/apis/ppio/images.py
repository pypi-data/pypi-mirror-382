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

from meutils.schemas.image_types import ImageRequest


async def generate(request: ImageRequest, api_key: str, base_url: Optional[str] = None):
    if request.model.startswith("gemini"):
        # model = "gemini-2.5-flash-image-preview"
        if request.image:
            request.model += "-image-edit"
        else:
            request.model += "-text-to-image"

    # gemini-2.5-flash-image-preview-text-to-image
    base_url = f"https://api.ppinfra.com/v3/{request.model}"

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "prompt": request.prompt,
                # "image_urls": request.image_urls,
            },
        )
        response.raise_for_status()
        return response.json()


if __name__ == '__main__':
    request = ImageRequest(
        model="gemini-2.5-flash-image-preview",
        prompt="a cat",
    )

    arun(generate(request, api_key="sk_fRr6ieXTMfym7Q6cnbj0YBlB1QsE74G8ygqIE2AyGz0"))
