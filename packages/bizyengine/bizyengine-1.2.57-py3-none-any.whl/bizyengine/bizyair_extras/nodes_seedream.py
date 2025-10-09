import base64
import io
import json
import logging
import re
from pathlib import Path

import requests
import torch
from comfy_api_nodes.apinode_utils import (
    bytesio_to_image_tensor,
    tensor_to_base64_string,
)

from bizyengine.core import BizyAirBaseNode, pop_api_key_and_prompt_id
from bizyengine.core.common import client
from bizyengine.core.common.env_var import BIZYAIR_SERVER_ADDRESS


def download_png(url: str) -> bytes:
    """下载 PNG 图片"""
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()  # 非 2xx 会抛异常
    return resp.content


class Seedream4(BizyAirBaseNode):
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "size": (
                    [
                        "1K Square (1024x1024)",
                        "2K Square (2048x2048)",
                        "4K Square (4096x4096)",
                        "HD 16:9 (1920x1080)",
                        "2K 16:9 (2560x1440)",
                        "4K 16:9 (3840x2160)",
                        "Portrait 9:16 (1080x1920)",
                        "Portrait 3:4 (1536x2048)",
                        "Landscape 4:3 (2048x1536)",
                        "Ultra-wide 21:9 (3440x1440)",
                        "Custom",
                    ],
                    {
                        "default": "HD 16:9 (1920x1080)",
                    },
                ),
                "custom_width": ("INT", {"default": 1920, "min": 1024, "max": 4096}),
                "custom_height": ("INT", {"default": 1080, "min": 1024, "max": 4096}),
                "model": (
                    ["doubao-seedream-4-0-250828"],
                    {"default": "doubao-seedream-4-0-250828"},
                ),
            },
            "optional": {
                "image": ("IMAGE",),
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
                "image4": ("IMAGE",),
                "image5": ("IMAGE",),
                "image6": ("IMAGE",),
                "image7": ("IMAGE",),
                "image8": ("IMAGE",),
                "image9": ("IMAGE",),
                "image10": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    OUTPUT_NODE = False
    CATEGORY = "☁️BizyAir/External APIs/Doubao"

    def execute(self, **kwargs):
        try:
            model = kwargs.get("model", "doubao-seedream-4-0-250828")
            url = f"{BIZYAIR_SERVER_ADDRESS}/proxy_inference/Doubao/{model}"
            extra_data = pop_api_key_and_prompt_id(kwargs)

            prompt = kwargs.get("prompt", "")
            size = kwargs.get("size", "1K Square (1024x1024)")

            match size:
                case "1K Square (1024x1024)":
                    width = 1024
                    height = 1024
                case "2K Square (2048x2048)":
                    width = 2048
                    height = 2048
                case "4K Square (4096x4096)":
                    width = 4096
                    height = 4096
                case "HD 16:9 (1920x1080)":
                    width = 1920
                    height = 1080
                case "2K 16:9 (2560x1440)":
                    width = 2560
                    height = 1440
                case "4K 16:9 (3840x2160)":
                    width = 3840
                    height = 2160
                case "Portrait 9:16 (1080x1920)":
                    width = 1080
                    height = 1920
                case "Portrait 3:4 (1536x2048)":
                    width = 1536
                    height = 2048
                case "Landscape 4:3 (2048x1536)":
                    width = 2048
                    height = 1536
                case "Ultra-wide 21:9 (3440x1440)":
                    width = 3440
                    height = 1440
                case "Custom":
                    width = kwargs.get("custom_width", 1920)
                    height = kwargs.get("custom_height", 1080)

                case _:
                    raise ValueError(f"Invalid size: {size}")

            sizeStr = f"{width}x{height}"

            images = []
            total_size = 0
            for _, img in enumerate(
                [
                    kwargs.get("image", None),
                    kwargs.get("image2", None),
                    kwargs.get("image3", None),
                    kwargs.get("image4", None),
                    kwargs.get("image5", None),
                    kwargs.get("image6", None),
                    kwargs.get("image7", None),
                    kwargs.get("image8", None),
                    kwargs.get("image9", None),
                    kwargs.get("image10", None),
                ],
                1,
            ):
                if img is not None:
                    # 都当作PNG就行
                    b64_data = tensor_to_base64_string(img)
                    if len(b64_data) > 10 * 1024 * 1024:
                        raise ValueError(
                            "Image size is too large, Seedream 4.0 only supports up to 10MB"
                        )
                    images.append(f"data:image/png;base64,{b64_data}")
                    total_size += len(b64_data)
                    if total_size > 50 * 1024 * 1024:
                        raise ValueError(
                            "Total size of images is too large, BizyAir only supports up to 50MB"
                        )

            data = {
                "prompt": prompt,
                "size": sizeStr,
                "image": images,
                "model": model,
                "watermark": False,
                "response_format": "url",
            }

            json_payload = json.dumps(data).encode("utf-8")
            headers = client.headers(api_key=extra_data["api_key"])
            headers["X-BIZYAIR-PROMPT-ID"] = extra_data["prompt_id"]
            resp = client.send_request(
                url=url,
                data=json_payload,
                headers=headers,
            )

            # 结果会包含图片URL，客户端这里负责下载
            if not "data" in resp:
                raise ValueError(f"Invalid response: {resp}")
            if not "url" in resp["data"][0]:
                raise ValueError(f"Invalid response: {resp}")

            image_data = download_png(resp["data"][0]["url"])
            return (bytesio_to_image_tensor(io.BytesIO(image_data)),)

        except Exception as e:
            logging.error(f"Seedream 4.0 API error: {e}")
            raise e
