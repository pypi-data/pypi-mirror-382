import base64
import io
import json
import logging
import re

import numpy as np
import torch
from comfy_api_nodes.apinode_utils import (
    bytesio_to_image_tensor,
    tensor_to_base64_string,
)
from PIL import Image, ImageOps

from bizyengine.core import BizyAirBaseNode, pop_api_key_and_prompt_id
from bizyengine.core.common import client
from bizyengine.core.common.env_var import BIZYAIR_SERVER_ADDRESS


# Tensor to PIL
def tensor_to_pil(image):
    return Image.fromarray(
        np.clip(255.0 * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8)
    )


def image_to_base64(pil_image, pnginfo=None):
    # 创建一个BytesIO对象，用于临时存储图像数据
    image_data = io.BytesIO()

    # 将图像保存到BytesIO对象中，格式为PNG
    pil_image.save(image_data, format="PNG", pnginfo=pnginfo)

    # 将BytesIO对象的内容转换为字节串
    image_data_bytes = image_data.getvalue()

    # 将图像数据编码为Base64字符串
    encoded_image = "data:image/png;base64," + base64.b64encode(
        image_data_bytes
    ).decode("utf-8")

    return encoded_image


def base64_to_image(base64_string):
    # 去除前缀
    base64_list = base64_string.split(",", 1)
    if len(base64_list) == 2:
        prefix, base64_data = base64_list
    else:
        base64_data = base64_list[0]

    # 从base64字符串中解码图像数据
    image_data = base64.b64decode(base64_data)

    # 创建一个内存流对象
    image_stream = io.BytesIO(image_data)

    # 使用PIL的Image模块打开图像数据
    image = Image.open(image_stream)

    return image


def get_parts_from_response(
    response: dict,
):
    return response["candidates"][0]["content"]["parts"]


def get_parts_by_type(response: dict, part_type: str):
    parts = []
    for part in get_parts_from_response(response):
        if part_type == "text" and part.get("text", None):
            parts.append(part)
        elif (
            part.get("inlineData", None) and part["inlineData"]["mimeType"] == part_type
        ):
            parts.append(part)
        # Skip parts that don't match the requested type
    return parts


def get_text_from_response(response: dict) -> str:
    parts = get_parts_by_type(response, "text")
    logging.debug(f"Text parts: {parts}")
    return "\n".join([part["text"] for part in parts])


def get_image_from_response(response: dict) -> torch.Tensor:
    image_tensors: list[torch.Tensor] = []
    parts = get_parts_by_type(response, "image/png")
    for part in parts:
        b64_data = part["inlineData"]["data"]
        if b64_data:
            image_data = base64.b64decode(b64_data)
            returned_image = bytesio_to_image_tensor(io.BytesIO(image_data))
            image_tensors.append(returned_image)
    if len(image_tensors) == 0:
        return torch.zeros((1, 1024, 1024, 4))
    return torch.cat(image_tensors, dim=0)


# FROM: https://github.com/ShmuelRonen/ComfyUI-NanoBanano/blob/9eeb8f2411fd0ff08791bdf5e24eec347456c8b8/nano_banano.py#L191
def build_prompt_for_operation(
    prompt,
    operation,
    has_references=False,
    aspect_ratio="1:1",
    character_consistency=True,
):
    """Build optimized prompt based on operation type"""

    aspect_instructions = {
        "1:1": "square format",
        "16:9": "widescreen landscape format",
        "9:16": "portrait format",
        "4:3": "standard landscape format",
        "3:4": "standard portrait format",
    }

    base_quality = "Generate a high-quality, photorealistic image"
    format_instruction = f"in {aspect_instructions.get(aspect_ratio, 'square format')}"

    if operation == "generate":
        if has_references:
            final_prompt = f"{base_quality} inspired by the style and elements of the reference images. {prompt}. {format_instruction}."
        else:
            final_prompt = f"{base_quality} of: {prompt}. {format_instruction}."

    elif operation == "edit":
        if not has_references:
            return "Error: Edit operation requires reference images"
        # No aspect ratio for edit - preserve original image dimensions
        final_prompt = f"Edit the provided reference image(s). {prompt}. Maintain the original composition and quality while making the requested changes."

    elif operation == "style_transfer":
        if not has_references:
            return "Error: Style transfer requires reference images"
        final_prompt = f"Apply the style from the reference images to create: {prompt}. Blend the stylistic elements naturally. {format_instruction}."

    elif operation == "object_insertion":
        if not has_references:
            return "Error: Object insertion requires reference images"
        final_prompt = f"Insert or blend the following into the reference image(s): {prompt}. Ensure natural lighting, shadows, and perspective. {format_instruction}."

    if character_consistency and has_references:
        final_prompt += " Maintain character consistency and visual identity from the reference images."

    return final_prompt


class NanoBanana(BizyAirBaseNode):
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
                "operation": (
                    ["generate", "edit", "style_transfer", "object_insertion"],
                    {
                        "default": "generate",
                        "tooltip": "Choose the type of image operation",
                    },
                ),
                "temperature": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05},
                ),
                "top_p": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05},
                ),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
                "max_tokens": ("INT", {"default": 8192, "min": 1, "max": 8192}),
            },
            "optional": {
                "image": ("IMAGE",),
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
                "image4": ("IMAGE",),
                "image5": ("IMAGE",),
                "quality": (
                    ["standard", "high"],
                    {"default": "high", "tooltip": "Image generation quality"},
                ),
                "aspect_ratio": (
                    ["1:1", "16:9", "9:16", "4:3", "3:4"],
                    {"default": "1:1", "tooltip": "Output image aspect ratio"},
                ),
                "character_consistency": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "Maintain character consistency across edits",
                    },
                ),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    FUNCTION = "execute"
    OUTPUT_NODE = False
    CATEGORY = "☁️BizyAir/External APIs/Gemini"

    def execute(
        self,
        prompt,
        operation,
        temperature,
        top_p,
        seed,
        max_tokens,
        quality=None,
        aspect_ratio=None,
        character_consistency=None,
        **kwargs,
    ):
        try:
            url = f"{BIZYAIR_SERVER_ADDRESS}/proxy_inference/VertexAI/gemini-2.5-flash-image-preview"
            extra_data = pop_api_key_and_prompt_id(kwargs)

            parts = []
            for _, img in enumerate(
                [
                    kwargs.get("image", None),
                    kwargs.get("image2", None),
                    kwargs.get("image3", None),
                    kwargs.get("image4", None),
                    kwargs.get("image5", None),
                ],
                1,
            ):
                if img is not None:
                    parts.append(
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": tensor_to_base64_string(img),
                            }
                        }
                    )

            prompt = build_prompt_for_operation(
                prompt,
                operation,
                has_references=len(parts) > 0,
                aspect_ratio=aspect_ratio,
                character_consistency=character_consistency,
            )
            if quality == "high":
                prompt += " Use the highest quality settings available."
            parts.append({"text": prompt})

            data = {
                "contents": {
                    "parts": parts,
                    "role": "user",
                },
                "generationConfig": {
                    "seed": seed,
                    "responseModalities": ["TEXT", "IMAGE"],
                    "temperature": temperature,
                    "topP": top_p,
                    "maxOutputTokens": max_tokens,
                },
            }
            json_payload = json.dumps(data).encode("utf-8")
            headers = client.headers(api_key=extra_data["api_key"])
            headers["X-BIZYAIR-PROMPT-ID"] = extra_data[
                "prompt_id"
            ]  # 额外参数vertexai会拒绝，所以用请求头传
            resp = client.send_request(
                url=url,
                data=json_payload,
                headers=headers,
            )
            # 解析潜在错误
            prompt_feedback = resp.get("promptFeedback", None)
            if prompt_feedback:
                logging.error(f"Response: {resp}")
                raise ValueError(f"Prompt blocked: {prompt_feedback}")
            if len(resp.get("candidates", [])) == 0:
                logging.error(f"Response: {resp}")
                raise ValueError("No candidates found in response")
            if resp["candidates"][0]["finishReason"] != "STOP":
                logging.error(f"Response: {resp}")
                raise ValueError(
                    f"Erroneous finish reason: {resp['candidates'][0]['finishReason']}"
                )

            # 解析文本
            text = get_text_from_response(resp)

            # 解析base64图片
            image = get_image_from_response(resp)

            return (image, text)

        except Exception as e:
            logging.error(f"Gemini API error: {e}")
            raise e
