import asyncio
from graph import generate_chat_responses

async def log_events():
    # message = "what is the toronto weather tmr?"
    message = "what is the nvida stock price?"
    try:
        async for event in generate_chat_responses(message):
            print(event)  # Print to console for real-time feedback
    except asyncio.TimeoutError:
        print("The operation timed out.")


if __name__ == "__main__":
    asyncio.run(log_events())