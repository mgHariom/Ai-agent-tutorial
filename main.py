import os
import json
import requests
from dotenv import load_dotenv
from tools import get_current_time, set_reminder, tell_joke, get_weather

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

FUNCTIONS = [
    {
        "name": "get_current_time",
        "description": "Get the current system time",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "set_reminder",
        "description": "Set a reminder in seconds",
        "parameters": {
            "type": "object",
            "properties": {"seconds": {"type": "integer", "description": "Number of seconds to wait"}},
            "required": ["seconds"]
        },
    },
    {
        "name": "tell_joke",
        "description": "Tells a random programming joke",
        "parameters": {"type": "object", "properties": {}}
    },
    {
    "name": "get_weather",
    "description": "Get the current weather for a given city",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The name of the city to get the weather for"
            }
        },
        "required": ["city"]
    }
}
]

TOOLS = {
    "get_current_time": get_current_time,
    "set_reminder": set_reminder,
    "tell_joke": tell_joke,
    "get_weather": get_weather
}

def call_groq(messages, functions=None):
    payload = {
        "model": "gemma2-9b-it",  # You can also use llama3-8b or gemma
        "messages": messages,
        "temperature": 0.7,
    }
    if functions:
        payload["tools"] = [{"type": "function", "function": f} for f in functions]

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(GROQ_URL, headers=headers, data=json.dumps(payload))
    # 👇 DEBUGGING: print the full response
    try:
        res_json = response.json()
    except Exception as e:
        print("❌ Error parsing JSON:", e)
        print(response.text)
        return {}

    if response.status_code != 200:
        print("❌ API Error:", response.status_code)
        print(json.dumps(res_json, indent=2))
        return {}

    return res_json

def main():
    messages = [{"role": "system", "content": "You're a helpful personal assistant with tools."}]
    while True:
        user_input = input("\n🧠 You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})
        response = call_groq(messages, FUNCTIONS)

        choice = response["choices"][0]
        msg = choice["message"]

        if msg.get("tool_calls"):
            for tool_call in msg["tool_calls"]:
                fn_name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])
                fn = TOOLS.get(fn_name)
                if fn:
                    result = fn(**args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": fn_name,
                        "content": json.dumps(result)
                    })
                    # Get final answer after tool response
                    response = call_groq(messages)
                    print("🤖", response["choices"][0]["message"]["content"])
        else:
            print("🤖", msg["content"])

if __name__ == "__main__":
    main()
