import os
import json
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

async def get_gpu_analysis_from_ai(gpu_name: str, vram: int, bus: int, arch: str):
    if not DEEPSEEK_API_KEY:
        return {
            "reason": "API-ключ DeepSeek не настроен в .env",
            "scores": {"games": 0, "3d": 0, "ml": 0, "office": 0}
        }

    prompt = f"""
    Проанализируй видеокарту {gpu_name} (VRAM: {vram}GB, Шина: {bus}bit, Архитектура: {arch}).
    Верни ответ СТРОГО в формате JSON:
    {{
        "reason": "Краткое объяснение (1-2 предложения), почему она в своем сегменте и для чего подходит лучше всего.",
        "scores": {{
            "games": 90,
            "3d": 85,
            "ml": 80,
            "office": 50
        }}
    }}
    Оцени применимость под каждую задачу от 0 до 100%.
    """

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ты эксперт по компьютерному железу. Отвечаешь только валидным JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=15.0)
            
            # Проверяем статус HTTP ответа перед парсингом
            response.raise_for_status()
            
            res_data = response.json()
            content = res_data["choices"][0]["message"]["content"]
            
            # Очищаем ответ от возможных triple backticks (```json ... ```)
            clean_content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            
            return json.loads(clean_content)

        except httpx.HTTPStatusError as e:
            logging.error(f"DeepSeek API HTTP Error: {e.response.status_code} - {e.response.text}")
        except json.JSONDecodeError as e:
            logging.error(f"JSON Parse Error: {e}. Raw content: {content if 'content' in locals() else 'None'}")
        except Exception as e:
            logging.error(f"Unexpected error in GPU analysis: {e}")

        # Динамический fallback: высчитывает разницу на основе VRAM и шины, если API упал
        vram_factor = min(vram / 24.0, 1.0)
        bus_factor = min(bus / 384.0, 1.0)
        
        return {
            "reason": f"Базовый расчет на основе спеков ({vram}GB VRAM, {bus}-bit). ИИ временно недоступен.",
            "scores": {
                "games": min(100, int(vram_factor * 60 + bus_factor * 40)),
                "3d": min(100, int(vram_factor * 70 + bus_factor * 30)),
                "ml": min(100, int(vram_factor * 90 + 10)),
                "office": 95
            }
        }