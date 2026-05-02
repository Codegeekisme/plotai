import json

import requests


class ApiError(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


def _extract_error_message(response):
    try:
        data = response.json()
    except ValueError:
        return response.text[:500] or "接口没有返回可读错误信息"

    if isinstance(data, dict):
        error = data.get("error")
        if isinstance(error, dict):
            return error.get("message") or json.dumps(error, ensure_ascii=False)
        if isinstance(error, str):
            return error
        return data.get("message") or json.dumps(data, ensure_ascii=False)
    return str(data)


def stream_chat_completion(api_url, api_key, model, messages, temperature, max_tokens=2048):
    try:
        response = requests.post(
            url=api_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
            },
            timeout=120,
            stream=True,
        )
    except requests.exceptions.Timeout as exc:
        raise ApiError("请求超时，请稍后重试或调低 max_tokens。") from exc
    except requests.exceptions.ConnectionError as exc:
        raise ApiError("无法连接到模型接口，请检查网络、代理或 API 地址。") from exc

    if response.status_code != 200:
        message = _extract_error_message(response)
        raise ApiError(message, status_code=response.status_code)

    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue
        if not line.startswith("data: "):
            continue

        data_str = line[6:].strip()
        if data_str == "[DONE]":
            break

        try:
            chunk = json.loads(data_str)
        except json.JSONDecodeError:
            continue

        choices = chunk.get("choices", [])
        if not choices:
            continue

        delta = choices[0].get("delta", {})
        content = delta.get("content")
        if content:
            yield content
