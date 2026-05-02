from dataclasses import dataclass

from config import CROP_PROFILES


METRICS = {
    "ph": ("土壤 pH", ""),
    "organic": ("有机质", "%"),
    "nitrogen": ("速效氮", "mg/kg"),
    "phosphorus": ("速效磷", "mg/kg"),
    "potassium": ("速效钾", "mg/kg"),
}


@dataclass(frozen=True)
class SoilReading:
    crop: str
    region: str
    growth_stage: str
    area_mu: float
    ph: float
    organic: float
    nitrogen: float
    phosphorus: float
    potassium: float
    observation: str = ""
    photo_name: str = ""


def get_crop_profile(crop_name):
    return CROP_PROFILES.get(crop_name, CROP_PROFILES["通用作物"])


def assess_metric(value, low, high):
    if value < low:
        gap = low - value
        return {"level": "偏低", "icon": "🔴", "gap": gap}
    if value > high:
        gap = value - high
        return {"level": "偏高", "icon": "🟡", "gap": gap}
    return {"level": "适宜", "icon": "🟢", "gap": 0}


def assess_soil(reading, profile):
    return {
        "ph": assess_metric(reading.ph, profile.ph_low, profile.ph_high),
        "organic": assess_metric(reading.organic, profile.organic_low, profile.organic_high),
        "nitrogen": assess_metric(reading.nitrogen, profile.nitrogen_low, profile.nitrogen_high),
        "phosphorus": assess_metric(reading.phosphorus, profile.phosphorus_low, profile.phosphorus_high),
        "potassium": assess_metric(reading.potassium, profile.potassium_low, profile.potassium_high),
    }


def metric_range(profile, key):
    range_map = {
        "ph": (profile.ph_low, profile.ph_high),
        "organic": (profile.organic_low, profile.organic_high),
        "nitrogen": (profile.nitrogen_low, profile.nitrogen_high),
        "phosphorus": (profile.phosphorus_low, profile.phosphorus_high),
        "potassium": (profile.potassium_low, profile.potassium_high),
    }
    return range_map[key]


def risk_summary(assessments):
    problems = [result["level"] for result in assessments.values() if result["level"] != "适宜"]
    if not problems:
        return "低", "全部核心指标处于参考范围内"
    if len(problems) <= 2:
        return "中", f"{len(problems)} 项指标需要关注"
    return "高", f"{len(problems)} 项指标偏离参考范围"


def build_prompt(reading, profile, assessments):
    lines = []
    for key, result in assessments.items():
        label, unit = METRICS[key]
        low, high = metric_range(profile, key)
        value = getattr(reading, key)
        unit_text = f" {unit}" if unit else ""
        lines.append(f"- {label}：{value}{unit_text}，参考范围 {low} ~ {high}{unit_text}，状态：{result['level']}")

    observation = reading.observation.strip() or "无额外田间观察"
    photo_note = "未上传照片"
    if reading.photo_name:
        photo_note = f"用户上传了照片文件 {reading.photo_name}。当前系统没有启用图像识别，请不要声称已经看过图片，只能结合用户文字观察进行判断。"

    return f"""
你是一位资深农业土壤专家和植物营养学家。请基于用户输入生成一份科学、谨慎、可执行的土壤改良方案。

## 农田信息
- 当前作物：{reading.crop}
- 所在地区：{reading.region or "未填写"}
- 生育阶段：{reading.growth_stage or "未填写"}
- 面积：{reading.area_mu} 亩
- 作物参考说明：{profile.note}
- 病害/长势观察：{observation}
- 图片信息：{photo_note}

## 土壤检测指标
{chr(10).join(lines)}

## 输出要求
1. 先给出一句总体判断，说明风险等级和最优先处理的问题。
2. 分成「现状评估」「短期处理」「本季施肥/改良方案」「长期养护」「复检建议」五部分。
3. 建议要尽量量化到每亩用量、施用时间、注意事项；不确定时给出保守范围并说明需结合当地农技标准。
4. 不要编造已经完成的图片识别结果；如果需要判断病害，请明确建议用户补充叶片、根系、田间分布等观察。
5. 用 Markdown 输出，语言适合一线农户阅读。
""".strip()
