
#2. Add API Key Safely
"""

from google.colab import userdata
from IPython.display import Markdown
api_key=userdata.get('main_api')

"""#4. First Simple Test"""

import requests
import json

# First API call with reasoning
response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
  },
  data=json.dumps({
    "model": "qwen/qwen3.6-flash",
    "messages": [
        {
          "role": "user",
          "content": "How many r's are in the word 'strawberry'?"
        },


      ],
    "reasoning": {"enabled": True},
    'max_tokens':500,
  })
)

response_data=response.json()

Markdown(response_data['choices'][0]['message']['reasoning'])

"""#5. Simple AI Agent With Chat History"""

# Extract the assistant message with reasoning_details
#response = response.json()
#response = response['choices'][0]['message']

# Preserve the assistant message with reasoning_details
messages = [
  {"role": "user", "content": "How many r's are in the word 'strawberry'?"},
  {
    "role": "assistant",
    "content": response.get('content'),
    #"reasoning_details": response.get('reasoning_details')  # Pass back unmodified
  },
  {"role": "user", "content": "Are you sure? Think carefully."}
]

# Second API call - model continues reasoning from where it left off
response2 = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
  },
  data=json.dumps({
    "model": "qwen/qwen3.6-flash",
    "messages": messages,  # Includes preserved reasoning_details
    "reasoning": {"enabled": True},
    'max_tokens':500,

  })
)

"""#6. Test Agent"""



"""#7. Test Memory

#### First Prompt (The Input)
"Hey AI, remember this completely unique project statistic for my course: My students built an AI agent called Alpha-9 that successfully ran 4,350 automated code deployments across 12 different countries with a 99.4% success rate without a single human intervention."

#### Second Prompt (The Memory Test)
"What was the name of the agent my students built, and how many deployments did it run?"
"""

import requests
import json

# Initialize chat history
chat_history = []

print("Simple AI Agent: Type 'quit' or 'exit' to end the conversation.")

while True:
    user_input = input("You: ")

    if user_input.lower() in ['quit', 'exit']:
        print("Agent: Goodbye!")
        break

    # Add user message to history
    chat_history = []
    chat_history.append({"role": "user", "content": user_input})

    try:
        # Make API call to OpenRouter with the current chat history
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "qwen/qwen3.6-flash", # Using the model from previous successful calls
                "messages": chat_history,
                "max_tokens": 500, # Keep max_tokens to avoid credit issues
                "reasoning": {"enabled": True}
            })
        )

        if response.ok:
            response_data = response.json()
            try:
                assistant_message_content = response_data['choices'][0]['message']['content']
                print(f"Agent: {assistant_message_content}")
                # Add assistant's response to history
                chat_history.append({"role": "assistant", "content": assistant_message_content})
            except KeyError as e:
                print(f"Agent Error: Expected key not found in response: {e}")
                print(f"Full response data: {response_data}")
        else:
            print(f"Agent Error: API call failed with status code {response.status_code}:")
            print(response.text)
            # If API call fails, do not add to history to avoid propagating bad states
            chat_history.pop() # Remove the last user message to try again

    except requests.exceptions.RequestException as e:
        print(f"Agent Error: Network or request issue: {e}")
        chat_history.pop() # Remove the last user message to try again

import requests
import json

# 1. Define real local Python tools that the agent can execute
def calculate(expression: str) -> str:
    """Safely evaluate simple arithmetic expressions."""
    try:
        # Using a restricted global dictionary for basic math safety
        allowed_chars = "0123456789+-*/(). "
        if not all(char in allowed_chars for char in expression):
            return "Error: Invalid characters in mathematical expression."
        return str(eval(expression, {"__builtins__": None}, {}))
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

def get_weather(location: str) -> str:
    """Mock weather tool that returns data based on the city."""
    city = location.lower()
    if "london" in city:
        return "15°C and raining heavily."
    elif "tokyo" in city:
        return "22°C and clear skies."
    elif "addis ababa" in city:
        return "24°C and beautifully sunny."
    else:
        return "18°C and partly cloudy."

# Mapping tool names to their actual Python functions
AVAILABLE_TOOLS = {
    "calculate": calculate,
    "get_weather":get_weather
}

# 2. Define the JSON schemas so the LLM knows what tools are available
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Use this tool to solve math equations or complex arithmetic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The math expression to solve, e.g., '2350 * 1.15'"
                    }
                },
                "required": ["expression"]
            }
        },
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a specific city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name, e.g., 'London' or 'Tokyo'"
                    }
                },
                "required": ["location"]
            }
        }

    }
]

# Initialize chat history with a system prompt setting agent rules
chat_history = [
    {"role": "system", "content": "You are an autonomous AI Agent equipped with local tools. Use your tools whenever you need to resolve complex logic or math questions precisely."}
]

print("Agentic AI System Active. Type 'quit' or 'exit' to end.")

while True:
    user_input = input("\nYou: ")

    if user_input.lower() in ['quit', 'exit']:
        print("Agent: Goodbye!")
        break

    # Add user message to history
    chat_history.append({"role": "user", "content": user_input})

    # The Agent Reasoning Loop
    # We loop up to 5 times to let the agent call multiple tools back-to-back if needed
    max_loops = 5
    for loop_count in range(max_loops):
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "model": "qwen/qwen3.6-flash",
                    "messages": chat_history,
                    "tools": tools_schema,       # Pass available tools to the LLM
                    "tool_choice": "auto",       # Let the LLM choose if it needs a tool
                    "max_tokens": 500
                })
            )

            if not response.ok:
                print(f"API Error ({response.status_code}): {response.text}")
                chat_history.pop()  # Safe fallback rollback
                break

            response_data = response.json()
            message_data = response_data['choices'][0]['message']

            # CRITICAL AGENTIC CHECK: Did the LLM request to run a tool?
            if 'tool_calls' in message_data and message_data['tool_calls']:
                # Append the assistant's decision to call the tool into history
                chat_history.append(message_data)

                for tool_call in message_data['tool_calls']:
                    tool_name = tool_call['function']['name']
                    tool_args = json.loads(tool_call['function']['arguments'])
                    tool_id = tool_call['id']

                    print(f"\n[Agent Thought]: I need to use the '{tool_name}' tool with arguments: {tool_args}")

                    # Run the local function
                    if tool_name in AVAILABLE_TOOLS:
                        tool_function = AVAILABLE_TOOLS[tool_name]
                        # Extract parameter values dynamically
                        execution_result = tool_function(**tool_args)
                    else:
                        execution_result = f"Error: Tool '{tool_name}' is not registered locally."

                    print(f"[Tool Output]: {execution_result}")

                    # Send the result of the tool run back to the AI's history
                    chat_history.append({
                        "role": "tool",
                        "tool_call_id": tool_id,
                        "name": tool_name,
                        "content": execution_result
                    })

                # Continue the loop so the model can read the tool's results and answer
                continue

            else:
                # No tools were requested, this is the final verbal response
                final_answer = message_data['content']
                print(f"\nAgent: {final_answer}")

                # Fixes original code memory bug: save the answer so it remembers next turn!
                chat_history.append({"role": "assistant", "content": final_answer})
                break # Exit the reasoning loop since the problem is resolved

        except requests.exceptions.RequestException as e:
            print(f"Network Error: {e}")
            chat_history.pop()
            break

"""1. What is 4350 times 12?
2. What is the weather like in Addis Ababa right now?


"""
