import asyncio
from openai import AsyncOpenAI

async def test():
    client = AsyncOpenAI(
        api_key="sk-FIMLVKQn9RoLhjXPENbGsbKKu6pgimZo",
        base_url="https://openai.api.proxyapi.ru/v1"
    )
    try:
        print("🔄 Отправляю запрос через ProxyAPI...")
        response = await client.chat.completions.create(
            model="deepseek/deepseek-chat"
            messages=[{"role": "user", "content": "Привет! Как дела?"}],
            max_tokens=50,
            temperature=0.7
        )
        print("✅ Ответ от DeepSeek через ProxyAPI:", response.choices[0].message.content)
    except Exception as e:
        print("❌ Ошибка при запросе к ProxyAPI:", e)
        print(f"Тип ошибки: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test())
