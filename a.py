import requests
import time
import json
from PIL import Image
from io import BytesIO

base_url = 'https://api-inference.modelscope.cn/'
api_key = "ms-7fdaf613-b31e-4711-abcd-04fd2bef4a20" # ModelScope Token

common_headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

response = requests.post(
    f"{base_url}v1/images/generations",
    headers={**common_headers, "X-ModelScope-Async-Mode": "true"},
    data=json.dumps({
        "model": "Tongyi-MAI/Z-Image-Turbo", # ModelScope Model-Id, required
        # "loras": "<lora-repo-id>", # optional lora(s)
        # """
        # LoRA(s) Configuration:
        # - for Single LoRA:
        #   "loras": "<lora-repo-id>"
        # - for Multiple LoRAs:
        #   "loras": {"<lora-repo-id1>": 0.6, "<lora-repo-id2>": 0.4}
        # - Upto 6 LoRAs, all weight-coefficients must sum to 1.0
        # """
        "prompt": "A beautiful girl"
    }, ensure_ascii=False).encode('utf-8')
)

response.raise_for_status()
task_id = response.json()["task_id"]

while True:
    result = requests.get(
        f"{base_url}v1/tasks/{task_id}",
        headers={**common_headers, "X-ModelScope-Task-Type": "image_generation"},
    )
    result.raise_for_status()
    data = result.json()

    if data["task_status"] == "SUCCEED":
        # image = Image.open(BytesIO(requests.get(data["output_images"][0]).content))
        # image.save("result_image.jpg")
        print(data)
        break
    elif data["task_status"] == "FAILED":
        print("Image Generation Failed.")
        break

    time.sleep(1)