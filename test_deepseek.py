import asyncio
from openai import AsyncOpenAI

async def test():
    # Используем твой реальный ключ из .env
    client = AsyncOpenAI(
        api_key="sk-FIMLVKQn9RoLhjXPENbGsbKKu6pgimZo",
        base_url="https://api.deepseek.com/v1"
    )
    try:
        print("🔄 Отправляю запрос к DeepSeek...")
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Привет! Как дела?"}],
            max_tokens=50,
            temperature=0.7
        )
        print("✅ Ответ от DeepSeek:", response.choices[0].message.content)
    except Exception as e:
        print("❌ Ошибка:", e)

if __name__ == "__main__":
    asyncio.run(test())

