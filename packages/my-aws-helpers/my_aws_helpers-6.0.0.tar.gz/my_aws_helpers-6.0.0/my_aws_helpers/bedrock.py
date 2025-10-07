from __future__ import annotations
import boto3
from botocore.config import Config
import json
import time
import os
import io
import re
from copy import copy
from typing import Optional, List, Dict
from enum import Enum
import pymupdf
import concurrent.futures
from dataclasses import dataclass
from my_aws_helpers.s3 import S3Serialiser, BaseS3Object, BaseS3Queries, S3, S3Location

from my_aws_helpers.logging import select_powertools_logger


logger = select_powertools_logger("aws-helpers-bedrock")


class ImageType(str, Enum):
    gif = "gif"
    jpeg = "jpeg"
    png = "png"
    webp = "webp"


class PromptType(str, Enum):
    transaction_headers = "transactions_headers_prompt_v2.txt"
    transactions = "transactions_prompt.txt"
    # json = "json_system_prompt.txt"
    markdown = "markdown_system_prompt.txt"


@dataclass
class TokenUsage:
    input_tokens: int
    output_tokens: int
    total_tokens: int

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> TokenUsage:
        return cls(
            input_tokens=data.get("inputTokens", 0),
            output_tokens=data.get("outputTokens", 0),
            total_tokens=data.get("totalTokens", 0),
        )


@dataclass
class OCRResult(BaseS3Object):
    content: List[Dict[str, str]]
    token_usage: TokenUsage
    page_number: int

    @classmethod
    def from_dict(cls, data: Dict) -> OCRResult:
        return cls(
            content=data.get("content", []),
            token_usage=TokenUsage.from_dict(data.get("token_usage", {})),
            page_number=data.get("page_number", 0),
        )

    @classmethod
    def from_s3_representation(cls, obj: dict) -> OCRResult:
        obj['token_usage'] = TokenUsage.from_dict(obj.get("token_usage", {})),
        return cls(**obj)

    def to_s3_representation(self) -> dict:
        obj = copy(vars(self))
        obj['token_usage'] = S3Serialiser.object_serialiser(obj=vars(obj['token_usage']))
        return S3Serialiser.object_serialiser(obj=obj)

    def get_save_location(self, bucket_name: str) -> S3Location:
        pass


class OCRResultQueries(BaseS3Queries):
    def __init__(self, s3_client: S3, bucket_name: str):
        super().__init__(s3_client=s3_client, bucket_name=bucket_name)

    def save_ocr_result_to_s3(
        self, ocr_result: OCRResult, save_location: S3Location
    ) -> Optional[S3Location]:
        try:
            obj = ocr_result.to_s3_representation()
            return self.s3_client.save_dict_to_s3(
                content=obj,
                s3_location=save_location,
            )
        except Exception as e:
            logger.exception(f"Failed to save ocr result to s3 due to {e}")
        return None

    def _concurrent_s3_read(
        self, locations: List[S3Location], max_workers: int = 10
    ) -> List[OCRResult]:
        results: List[OCRResult] = list()
        futures = list()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for loc in locations:
                future = executor.submit(
                    self.s3_client.read_dict_from_s3,
                    s3_location=loc,
                )
                futures.append(future)
        for f in futures:
            results.append(f.result())
        results = [r for r in results if r is not None]
        return results

    def get_ocr_results_by_key_prefix(self, prefix: str) -> List[OCRResult]:
        locations = self.s3_client.list_objects_by_prefix(
            bucket_name=self.bucket_name, prefix=prefix
        )
        objects = self._concurrent_s3_read(locations=locations)
        ocr_results = [OCRResult.from_s3_representation(obj=obj) for obj in objects]
        return ocr_results


class Bedrock:
    def __init__(
        self,
        model_id: str = "apac.anthropic.claude-3-5-sonnet-20241022-v2:0",#anthropic.claude-sonnet-4-20250514-v1:0
        logger=None,
        sleep_time: float = 1.0,
    ):

        self.session = Bedrock._set_session_params()
        self.logger = logger
        region_name = "ap-southeast-2"
        if self.session is None:
            self.session = boto3.Session(region_name=region_name)
        self.sleep_time = sleep_time

        custom_config = Config(
            retries={
                "max_attempts": 2,  # Total attempts = 1 initial + 1 retry
                "mode": "standard",  # or 'adaptive'
            }
        )
        self.client = self.session.client(
            "bedrock-runtime", region_name=region_name, config=custom_config
        )
        self.model_id = model_id

    @staticmethod
    def _set_session_params():
        try:
            aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
            aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]
            aws_session_token = os.environ["AWS_SESSION_TOKEN"]
            region_name = os.environ["AWS_DEFAULT_REGION"]
            return boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
                region_name=region_name,
            )
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def extract_json_from_markdown(text: str):
        """
        Extracts the JSON object from a string that may be wrapped in ```json ... ``` code block
        """
        # Match a {...} block anywhere in the text
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        else:
            raise ValueError("No JSON object found in the text")

    def _get_prompt(self, prompt_type: str) -> Optional[str]:
        if prompt_type not in list(PromptType):
            raise Exception(f"Error: Invalid prompt type")

        path = os.path.join(os.path.dirname(__file__), "prompts", prompt_type)
        try:
            with open(path, "r") as f:
                prompt = f.read()
                return prompt
        except Exception as e:
            self.logger.exception(f"Failed to get {prompt_type} prompt due to {e}")
        return None

    def _ocr(
        self, prompt: str, image_bytes: bytes, page_number: Optional[int] = 0
    ) -> Optional[OCRResult]:
        system_prompt = [{"text": prompt}]
        message = [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": "png",
                            "source": {
                                "bytes": image_bytes,
                            },
                        }
                    }
                ],
            }
        ]
        retries = 3
        for i in range(retries):
            self.logger.info(f"Attempt number {i} for {self.model_id} converse")
            try:
                response = self.client.converse(
                    modelId=self.model_id, messages=message, system=system_prompt
                )
                if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    break
            except Exception as e:
                self.logger.exception(f"Error during conversation due to {e}")
                if i >= len(retries) - 1:
                    raise Exception(e)
                time.sleep(self.sleep_time)
                continue

        result = {}
        result["content"] = json.loads(
            response["output"]["message"]["content"][0]["text"]
        )
        result["token_usage"] = response["usage"]
        result["page_number"] = page_number
        return OCRResult.from_dict(data=result)

    def _parallel_ocr(
        self,
        image_bytes_list: List[bytes],
        prompt: str,
        max_workers: int = 10,
    ):
        execution_futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i, img in enumerate(image_bytes_list):
                self.logger.info(f"Starting OCR for page: {i}")
                time.sleep(self.sleep_time)  # Stagger start time
                future = executor.submit(self._ocr, prompt=prompt, image_bytes=img)
                execution_futures.append(future)

        # Wait for all tasks and collect results in order of submission
        results = [
            future.result()
            for future in execution_futures
            if future.result() is not None
        ]
        return results

    def get_ocr_result(
        self,
        pdf_bytes: io.BytesIO,
        prompt_type: str,
        zoom: int = 7,
    ) -> List[OCRResult]:
        try:
            self.logger.info("Getting OCR Results")
            document = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            pages: List[pymupdf.Page] = [p for p in document]

            image_bytes_list: List[bytes] = list()
            for i, p in enumerate(pages):
                try:
                    image_bytes: bytes = p.get_pixmap(
                        matrix=pymupdf.Matrix(zoom, zoom)
                    ).tobytes("png")
                    image_bytes_list.append(image_bytes)
                except Exception as e:
                    self.logger.error(f"Could not get pix map for page {i}")
                    continue
            skip_page_zero = False
            header_ocr_result = None
            if len(image_bytes_list) > 1:
                headers_prompt = self._get_prompt(
                    prompt_type=PromptType.transaction_headers.value
                )
                for i in range(2):
                    # try to get headers from the first or second page
                    header_ocr_result = self._ocr(
                        prompt=headers_prompt, image_bytes=image_bytes_list[i]
                    )
                    if header_ocr_result is None:
                        self.logger.info(
                            f"No ocr result returned when getting headers {PromptType.transaction_headers.value}"
                        )
                    headers = header_ocr_result.content.get("headers")
                    if (len(headers) < 1) or (headers is None):
                        skip_page_zero = True
                        continue
                    else:
                        break

            transactions_prompt = self._get_prompt(prompt_type=prompt_type)
            if header_ocr_result:
                transactions_prompt = transactions_prompt.replace(
                    "#### TABLE HEADERS ####", json.dumps(header_ocr_result.content)
                )

            self.logger.info("Got Prompt")
            results = list()

            if skip_page_zero:
                image_bytes_list = image_bytes_list[
                    1:
                ]  # page zero often has account summary info
            results = self._parallel_ocr(
                image_bytes_list=image_bytes_list, prompt=transactions_prompt
            )

            # for i, image_bytes in enumerate(image_bytes_list):
            #     self.logger.info(f"Starting OCR for page: {i}")
            #     results.append(self._ocr(image_bytes=image_bytes, prompt=transactions_prompt))
            return results
        except Exception as e:
            self.logger.exception(e)
            return []

    def _get_image_block(self, image: bytes, image_content_type: ImageType) -> dict:
        return {
            "image": {
                "format": image_content_type,
                "source": {
                    "bytes": image,
                },
            }
        }

    def image_analysis(
        self, images: List[bytes], prompt: str, image_content_type: ImageType
    ) -> OCRResult:

        system_prompt = [{"text": prompt}]
        message = [
            {
                "role": "user",
                "content": [
                    self._get_image_block(
                        image=image, image_content_type=image_content_type
                    )
                    for image in images
                ],
            }
        ]
        response = self.client.converse(
            modelId=self.model_id, messages=message, system=system_prompt
        )

        result = {}
        result["content"] = Bedrock.extract_json_from_markdown(
            text = response["output"]["message"]["content"][0]["text"]
        )
        result["token_usage"] = response["usage"]
        return OCRResult.from_dict(data=result)
