import os
import time
from dataclasses import asdict, dataclass


SETTINGS_FILE = os.path.expanduser("~/.deepcode/settings.json")


PROVIDER_MODEL_LISTS = {
    "OpenAI 兼容": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
    ],
    "DeepSeek": [
        "deepseek-chat",
        "deepseek-reasoner",
    ],
    "智谱 AI (GLM)": [
        "glm-4-flash",
        "glm-4",
        "glm-4-plus",
    ],
    "通义千问 (Qwen)": [
        "qwen-plus",
        "qwen-max",
        "qwen-turbo",
    ],
    "Moonshot": [
        "moonshot-v1-8k",
        "moonshot-v1-32k",
        "moonshot-v1-128k",
    ],
    "硅基流动": [
        "deepseek-ai/DeepSeek-V3",
        "deepseek-ai/DeepSeek-R1",
        "Qwen/Qwen2.5-72B-Instruct",
    ],
}


PROVIDER_URLS = {
    "OpenAI 兼容": "https://api.openai.com/v1/chat/completions",
    "DeepSeek": "https://api.deepseek.com/v1/chat/completions",
    "智谱 AI (GLM)": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    "通义千问 (Qwen)": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    "Moonshot": "https://api.moonshot.cn/v1/chat/completions",
    "硅基流动": "https://api.siliconflow.cn/v1/chat/completions",
}


PROVIDER_ENV_KEYS = {
    "OpenAI 兼容": ["OPENAI_API_KEY", "API_KEY"],
    "DeepSeek": ["DEEPSEEK_API_KEY", "API_KEY"],
    "智谱 AI (GLM)": ["ZHIPU_API_KEY", "GLM_API_KEY", "API_KEY"],
    "通义千问 (Qwen)": ["DASHSCOPE_API_KEY", "QWEN_API_KEY", "API_KEY"],
    "Moonshot": ["MOONSHOT_API_KEY", "API_KEY"],
    "硅基流动": ["SILICONFLOW_API_KEY", "API_KEY"],
}


@dataclass(frozen=True)
class SoilProfile:
    name: str
    ph_low: float
    ph_high: float
    organic_low: float
    organic_high: float
    nitrogen_low: float
    nitrogen_high: float
    phosphorus_low: float
    phosphorus_high: float
    potassium_low: float
    potassium_high: float
    note: str


CROP_PROFILES = {
    "茶树": SoilProfile("茶树", 4.5, 6.5, 1.5, 3.0, 60, 120, 10, 30, 80, 150, "偏酸性土壤更适合茶树，重点关注酸化过度和有机质维护。"),
    "水稻": SoilProfile("水稻", 5.5, 7.0, 2.0, 4.0, 80, 150, 10, 30, 80, 160, "水田管理要结合灌排条件，避免长期还原环境造成养分失衡。"),
    "小麦": SoilProfile("小麦", 6.0, 7.5, 1.5, 3.0, 70, 140, 10, 30, 90, 180, "小麦对土壤通气和基础肥力较敏感，返青拔节期需重点管理氮肥。"),
    "玉米": SoilProfile("玉米", 6.0, 7.5, 2.0, 4.0, 80, 160, 15, 35, 100, 200, "玉米需肥量较高，钾素和中后期氮素供应会影响产量稳定性。"),
    "番茄": SoilProfile("番茄", 6.0, 7.0, 2.5, 5.0, 80, 180, 20, 50, 150, 300, "番茄对钾和钙镁供应较敏感，设施栽培还要关注盐分累积。"),
    "通用作物": SoilProfile("通用作物", 5.5, 7.5, 1.5, 4.0, 60, 150, 10, 40, 80, 200, "通用范围仅用于初筛，具体阈值应结合当地土壤检测标准修正。"),
}


DEFAULT_SETTINGS = {
    "provider": "DeepSeek",
    "model_name": "deepseek-chat",
    "temperature": 0.7,
}


def get_provider_models(provider):
    return PROVIDER_MODEL_LISTS.get(provider, PROVIDER_MODEL_LISTS[DEFAULT_SETTINGS["provider"]])


def get_default_model(provider):
    return get_provider_models(provider)[0]


def load_app_settings():
    try:
        import json

        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {**DEFAULT_SETTINGS, "legacy_api_token": "", "loaded": False}

    env = data.get("env", {})
    provider = data.get("provider", DEFAULT_SETTINGS["provider"])
    if provider == "OpenAI 格式（兼容大多数）":
        provider = "OpenAI 兼容"
    if provider == "Moonshot (月之暗面)":
        provider = "Moonshot"
    if provider == "硅基流动 (SiliconFlow)":
        provider = "硅基流动"

    model_name = env.get("MODEL") or data.get("model_name") or get_default_model(provider)
    if model_name not in get_provider_models(provider):
        model_name = get_default_model(provider)

    return {
        "provider": provider,
        "model_name": model_name,
        "temperature": data.get("temperature", DEFAULT_SETTINGS["temperature"]),
        "legacy_api_token": env.get("API_KEY", ""),
        "loaded": True,
    }


def save_app_settings(provider, model_name, temperature):
    import json

    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    data = {
        "provider": provider,
        "model_name": model_name,
        "base_url": PROVIDER_URLS.get(provider, ""),
        "temperature": temperature,
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "security_note": "API key is not saved here. Use environment variables, Streamlit secrets, or the session input.",
    }
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def profile_to_dict(profile):
    return asdict(profile)
