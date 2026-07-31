import json
import re
from app.core.config import settings

DEFAULT_PROMPT_TEMPLATE = (
    "你是保险营销文案专家。请根据以下客户画像生成一封个性化车险营销邮件。\n"
    "客户画像：性别{gender}，年龄{age}岁，{driving_license}驾照，"
    "车龄{vehicle_age}，车辆{vehicle_damage}，年保费{annual_premium}元。\n"
    "要求：语气专业有温度，突出该客户画像的痛点与利益，包含行动号召(CTA)。\n"
    "仅返回严格 JSON，格式：{{\"subject\":\"邮件主题\",\"content\":\"HTML格式正文\"}}"
)


def _decode_customer(customer: dict) -> dict:
    return {
        "gender": "男" if customer.get("gender") == "Male" else "女",
        "age": customer.get("age", ""),
        "driving_license": "有" if int(customer.get("driving_license", 0)) == 1 else "无",
        "vehicle_age": customer.get("vehicle_age", ""),
        "vehicle_damage": "曾受损" if customer.get("vehicle_damage") == "Yes" else "未受损",
        "annual_premium": customer.get("annual_premium", ""),
    }


class LLMService:
    def __init__(self):
        self.client = None
        if settings.LLM_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_API_BASE)
            except Exception:
                self.client = None

    def generate_email(self, customer: dict, prompt_template: str = None) -> dict:
        if not self.client:
            return {"success": False, "error": "LLM_API_KEY 未配置"}
        decoded = _decode_customer(customer)
        template = prompt_template or DEFAULT_PROMPT_TEMPLATE
        try:
            prompt = template.format(**decoded)
        except KeyError as e:
            return {"success": False, "error": f"模板占位符缺失: {e}"}
        try:
            resp = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            content = resp.choices[0].message.content.strip()
            content = re.sub(r'^```json\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
            result = json.loads(content)
            return {"success": True, "subject": result.get("subject", ""), "content": result.get("content", "")}
        except Exception as e:
            return {"success": False, "error": str(e)}