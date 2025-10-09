import io
import json
import logging

import requests
from comfy_api.latest._input_impl import VideoFromFile
from comfy_api_nodes.apinode_utils import tensor_to_bytesio

from bizyengine.bizyair_extras.utils.audio import save_audio
from bizyengine.core import BizyAirBaseNode, pop_api_key_and_prompt_id
from bizyengine.core.common import client
from bizyengine.core.common.client import send_request
from bizyengine.core.common.env_var import BIZYAIR_X_SERVER

from .utils.aliyun_oss import upload_file_without_sdk


def parse_upload_token(resp) -> dict:
    logging.debug(f"parsing token resp: {resp}")
    if "data" not in resp:
        logging.error(f"Invalid response, data not found: {resp}")
        raise ValueError(f"Invalid response: {resp}")
    data = resp["data"]
    if "file" not in data:
        logging.error(f"Invalid response, file not found: {resp}")
        raise ValueError(f"Invalid response: {resp}")
    file = data["file"]
    if "storage" not in data:
        logging.error(f"Invalid response, storage not found: {resp}")
        raise ValueError(f"Invalid response: {resp}")
    storage = data["storage"]
    return file | storage


class Wan_V2_5_I2V_API(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "audio": ("AUDIO",),
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "negative_prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "resolution": (
                    ["480P", "720P", "1080P"],
                    {"default": "1080P"},
                ),
                "duration": ([5, 10], {"default": 5}),
                "prompt_extend": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "是否开启prompt智能改写。开启后使用大模型对输入prompt进行智能改写。对于较短的prompt生成效果提升明显，但会增加耗时。",
                    },
                ),
                "auto_audio": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "是否由模型自动生成声音，优先级低于audio参数。",
                    },
                ),
            },
        }

    NODE_DISPLAY_NAME = "Wan2.5 Image To Video"
    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "actual_prompt")
    CATEGORY = "☁️BizyAir/External APIs/WanVideo"
    FUNCTION = "api_call"

    def api_call(self, image, **kwargs):
        extra_data = pop_api_key_and_prompt_id(kwargs)
        headers = client.headers(api_key=extra_data["api_key"])
        prompt_id = extra_data["prompt_id"]
        headers["X-BIZYAIR-PROMPT-ID"] = prompt_id

        # 参数
        prompt = kwargs.get("prompt", "")
        negative_prompt = kwargs.get("negative_prompt", "")
        audio = kwargs.get("audio", None)
        resolution = kwargs.get("resolution", "1080P")
        duration = kwargs.get("duration", 5)
        prompt_extend = kwargs.get("prompt_extend", True)
        auto_audio = kwargs.get("auto_audio", True)

        input = {}
        if prompt is not None and prompt.strip() != "":
            input["prompt"] = prompt
        if negative_prompt is not None and negative_prompt.strip() != "":
            input["negative_prompt"] = negative_prompt

        # 上传图片&音频
        if image is not None:
            oss_token_url = f"{BIZYAIR_X_SERVER}/upload/token?file_name={prompt_id}.png&file_type=inputs"
            token_resp = send_request("GET", oss_token_url, headers=headers)
            auth_info = parse_upload_token(token_resp)
            input["img_url"] = upload_file_without_sdk(
                tensor_to_bytesio(image), **auth_info
            )
        if audio is not None:
            oss_token_url = f"{BIZYAIR_X_SERVER}/upload/token?file_name={prompt_id}.flac&file_type=inputs"
            token_resp = send_request("GET", oss_token_url, headers=headers)
            auth_info = parse_upload_token(token_resp)
            audio_bytes = save_audio(audio)
            input["audio_url"] = upload_file_without_sdk(audio_bytes, **auth_info)

        # 调用API
        model = "wan2.5-i2v-preview"
        api_url = f"{BIZYAIR_X_SERVER}/proxy_inference/Wan/{model}"
        data = {
            "model": model,
            "input": input,
            "parameters": {
                "resolution": resolution,
                "prompt_extend": prompt_extend,
                "duration": duration,
                "audio": auto_audio,
            },
        }
        json_payload = json.dumps(data).encode("utf-8")
        logging.debug(f"json_payload: {json_payload}")
        api_resp = send_request(
            url=api_url,
            data=json_payload,
            headers=headers,
        )
        logging.debug(f"api resp: {api_resp}")
        if "output" not in api_resp or "video_url" not in api_resp["output"]:
            raise ValueError(f"Invalid response: {api_resp}")
        video_url = api_resp["output"]["video_url"]
        actual_prompt = api_resp["output"].get("actual_prompt", prompt)
        # 下载视频
        video_resp = requests.get(video_url, stream=True, timeout=30)
        video_resp.raise_for_status()  # 非 2xx 会抛异常
        return (VideoFromFile(io.BytesIO(video_resp.content)), actual_prompt)


class Wan_V2_5_T2V_API(BizyAirBaseNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
            },
            "optional": {
                "audio": ("AUDIO",),
                "negative_prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "size": (
                    [
                        "832*480",
                        "480*832",
                        "624*624",
                        "1280*720",
                        "720*1280",
                        "960*960",
                        "1088*832",
                        "832*1088",
                        "1920*1080",
                        "1080*1920",
                        "1440*1440",
                        "1632*1248",
                        "1248*1632",
                    ],
                    {"default": "1920*1080"},
                ),
                "duration": ([5, 10], {"default": 5}),
                "prompt_extend": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "是否开启prompt智能改写。开启后使用大模型对输入prompt进行智能改写。对于较短的prompt生成效果提升明显，但会增加耗时。",
                    },
                ),
                "auto_audio": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "是否由模型自动生成声音，优先级低于audio参数。",
                    },
                ),
            },
        }

    NODE_DISPLAY_NAME = "Wan2.5 Text To Video"
    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "actual_prompt")
    CATEGORY = "☁️BizyAir/External APIs/WanVideo"
    FUNCTION = "api_call"

    def parse_upload_token(self, resp) -> dict:
        logging.debug(f"parsing token resp: {resp}")
        if "data" not in resp:
            logging.error(f"Invalid response, data not found: {resp}")
            raise ValueError(f"Invalid response: {resp}")
        data = resp["data"]
        if "file" not in data:
            logging.error(f"Invalid response, file not found: {resp}")
            raise ValueError(f"Invalid response: {resp}")
        file = data["file"]
        if "storage" not in data:
            logging.error(f"Invalid response, storage not found: {resp}")
            raise ValueError(f"Invalid response: {resp}")
        storage = data["storage"]
        return file | storage

    def api_call(self, prompt, **kwargs):
        extra_data = pop_api_key_and_prompt_id(kwargs)
        headers = client.headers(api_key=extra_data["api_key"])
        prompt_id = extra_data["prompt_id"]
        headers["X-BIZYAIR-PROMPT-ID"] = prompt_id

        # 参数
        negative_prompt = kwargs.get("negative_prompt", "")
        audio = kwargs.get("audio", None)
        size = kwargs.get("size", "1920*1080")
        duration = kwargs.get("duration", 5)
        prompt_extend = kwargs.get("prompt_extend", True)
        auto_audio = kwargs.get("auto_audio", True)

        input = {}
        if prompt is not None and prompt.strip() != "":
            input["prompt"] = prompt
        if negative_prompt is not None and negative_prompt.strip() != "":
            input["negative_prompt"] = negative_prompt

        # 上传音频
        if audio is not None:
            oss_token_url = f"{BIZYAIR_X_SERVER}/upload/token?file_name={prompt_id}.flac&file_type=inputs"
            token_resp = send_request("GET", oss_token_url, headers=headers)
            auth_info = parse_upload_token(token_resp)
            audio_bytes = save_audio(audio)
            input["audio_url"] = upload_file_without_sdk(audio_bytes, **auth_info)

        # 调用API
        model = "wan2.5-t2v-preview"
        api_url = f"{BIZYAIR_X_SERVER}/proxy_inference/Wan/{model}"
        data = {
            "model": model,
            "input": input,
            "parameters": {
                "size": size,
                "prompt_extend": prompt_extend,
                "duration": duration,
                "audio": auto_audio,
            },
        }
        json_payload = json.dumps(data).encode("utf-8")
        logging.debug(f"json_payload: {json_payload}")
        api_resp = send_request(
            url=api_url,
            data=json_payload,
            headers=headers,
        )
        logging.debug(f"api resp: {api_resp}")
        if "output" not in api_resp or "video_url" not in api_resp["output"]:
            raise ValueError(f"Invalid response: {api_resp}")
        video_url = api_resp["output"]["video_url"]
        actual_prompt = api_resp["output"].get("actual_prompt", prompt)
        # 下载视频
        video_resp = requests.get(video_url, stream=True, timeout=30)
        video_resp.raise_for_status()  # 非 2xx 会抛异常
        return (VideoFromFile(io.BytesIO(video_resp.content)), actual_prompt)
