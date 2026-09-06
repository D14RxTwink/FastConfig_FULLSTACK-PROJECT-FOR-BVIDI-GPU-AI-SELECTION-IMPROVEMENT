import os
from openai import AsyncOpenAI

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

async def get_gpu_analysis_from_ai(gpu_name: str, vram: int, bus: int, arch: str) -> dict:
    # 1. Если API-ключ есть, пробуем запросить у DeepSeek
    if DEEPSEEK_API_KEY:
        try:
            client = AsyncOpenAI(
                api_key=DEEPSEEK_API_KEY, 
                base_url="https://api.deepseek.com"
            )
            
            prompt = f"""
            Проанализируй видеокарту {gpu_name} ({vram}GB VRAM, шина {bus}-bit, архитектура {arch}).
            Оцени в процентах (0-100%) её пригодность для 4 категорий:
            1. Игры
            2. 3D рендеринг / Моделирование
            3. Machine Learning (ML) / AI
            4. Офис / Базовые задачи

            Верни ответ STRICTLY в формате JSON с ключами:
            "verdict": "короткий текст с выводом (до 150 символов)",
            "games_pct": число,
            "render_3d_pct": число,
            "ml_pct": число,
            "office_pct": число
            """

            response = await client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            import json
            data = json.loads(response.choices[0].message.content)
            return {
                "verdict": data.get("verdict", "Анализ завершен успешно."),
                "games_score": int(data.get("games_pct", 50)),
                "render_3d_score": int(data.get("render_3d_pct", 50)),
                "ml_score": int(data.get("ml_pct", 50)),
                "office_score": int(data.get("office_pct", 100))
            }
        except Exception as e:
            print(f"Ошибка DeepSeek API: {e}. Переходим на авто-расчет.")

    # 2. Умный локальный расчет процентов (Локальный AI / Fallback)
    
    # Офис: любая современная карта справляется на 100%
    office_score = 100
    
    # Игры: расчет на основе объёма VRAM и шины
    if vram >= 16:
        games_score = 95
    elif vram >= 12:
        games_score = 85
    elif vram >= 8:
        games_score = 70
    elif vram >= 6:
        games_score = 50
    else:
        games_score = 30

    # 3D Рендеринг: важны VRAM (от 12GB) и шина (от 192-bit)
    if vram >= 16 and bus >= 256:
        render_score = 95
    elif vram >= 12:
        render_score = 80
    elif vram >= 8:
        render_score = 60
    else:
        render_score = 35

    # Machine Learning (ML): критически важен объем VRAM (PyTorch/CUDA)
    if vram >= 24:
        ml_score = 98
    elif vram >= 16:
        ml_score = 85
    elif vram >= 12:
        ml_score = 70
    elif vram >= 8:
        ml_score = 45
    else:
        ml_score = 15

    verdict_text = f"Оценка {gpu_name}: {vram}GB VRAM подходит для "
    if ml_score >= 70:
        verdict_text += "тяжелых задач ML и 3D."
    elif games_score >= 70:
        verdict_text += "современных игр и работы."
    else:
        verdict_text += "базовых мультимедийных и офисных задач."

    return {
        "verdict": verdict_text,
        "games_score": games_score,
        "render_3d_score": render_score,
        "ml_score": ml_score,
        "office_score": office_score
    }