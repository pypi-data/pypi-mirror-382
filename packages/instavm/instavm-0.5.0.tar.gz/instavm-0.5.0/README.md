# InstaVM Client

A comprehensive Python client library for InstaVM's code execution and browser automation APIs.

## Features

- **Code Execution**: Run Python, Bash, and other languages in secure cloud environments
- **Browser Automation**: Control web browsers for testing, scraping, and automation
- **Session Management**: Automatic session creation and server-side expiration
- **File Operations**: Upload files to execution environments
- **Async Support**: Execute commands asynchronously for long-running tasks
- **Error Handling**: Comprehensive exception handling for different failure modes

## Installation

You can install the package using pip:
```bash
pip install instavm
```

## Quick Start

### Code Execution
```python
from instavm import InstaVM, ExecutionError, NetworkError

# Create client with automatic session management
client = InstaVM(api_key='your_api_key')

try:
    # Execute a command
    result = client.execute("print(100**100)")
    print(result)

    # Get usage info for the session
    usage = client.get_usage()
    print(usage)

except ExecutionError as e:
    print(f"Code execution failed: {e}")
except NetworkError as e:
    print(f"Network issue: {e}")
finally:
    client.close_session()
```

### File Upload
```python
from instavm import InstaVM

client = InstaVM(api_key='your_api_key')

# Upload a file to the execution environment
result = client.upload_file("local_script.py", "/remote/path/script.py")
print(result)

# Execute the uploaded file
execution_result = client.execute("python /remote/path/script.py", language="bash")
print(execution_result)
```

### Error Handling
```python
from instavm import InstaVM, AuthenticationError, RateLimitError, SessionError

try:
    client = InstaVM(api_key='invalid_key')
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded - try again later")
except SessionError as e:
    print(f"Session error: {e}")
```

### Async Execution
```python
from instavm import InstaVM

client = InstaVM(api_key='your_api_key')

# Execute command asynchronously (returns task ID)
result = client.execute_async("sleep 5 && echo 'Long task complete!'", language="bash")
task_id = result['task_id']
print(f"Task {task_id} is running in background...")

# Note: Task status checking requires OAuth2 authentication
# Use execute() for immediate results
```

## Browser Automation

### Basic Browser Usage
```python
from instavm import InstaVM

client = InstaVM(api_key='your_api_key')

# Create browser session
session_id = client.create_browser_session(1920, 1080)
print(f"Browser session: {session_id}")

# Navigate to a webpage
nav_result = client.browser_navigate("https://example.com", session_id)
print(f"Navigation: {nav_result}")

# Take screenshot (returns base64 string)
screenshot = client.browser_screenshot(session_id)
print(f"Screenshot size: {len(screenshot)} characters")

# Extract page elements
elements = client.browser_extract_elements(session_id, "title", attributes=["text"])
print(f"Page title: {elements}")

# Interact with page
client.browser_scroll(session_id, y=200)
client.browser_click("button#submit", session_id)
client.browser_fill("input[name='email']", "test@example.com", session_id)

# Sessions auto-expire on server side (no explicit close needed)
# But you can close manually if desired:
# client.close_browser_session(session_id)
```

### Browser Manager (High-Level Interface)
```python
from instavm import InstaVM

client = InstaVM(api_key='your_api_key')

# Create managed browser session
browser_session = client.browser.create_session(1366, 768)
print(f"Managed session: {browser_session.session_id}")

# Use session object for operations
browser_session.navigate("https://example.com")
browser_session.click("button#submit")
browser_session.fill("input[name='email']", "test@example.com")
browser_session.type("textarea", "Hello world!")

# Take screenshot
screenshot = browser_session.screenshot()
print(f"Screenshot: {len(screenshot)} chars")

# Extract elements
titles = browser_session.extract_elements("h1", attributes=["text"])
print(f"H1 elements: {titles}")

# Close session when done
browser_session.close()
```

### Convenience Methods (Auto-Session)
```python
from instavm import InstaVM

client = InstaVM(api_key='your_api_key')

# These methods auto-create a browser session if needed
client.browser.navigate("https://example.com")
screenshot = client.browser.screenshot()
elements = client.browser.extract_elements("title")

print(f"Auto-session screenshot: {len(screenshot)} chars")
print(f"Elements found: {elements}")
```

### Available Browser Methods

**Session Management:**
- `create_browser_session(width, height, user_agent)` - Create new browser session
- `get_browser_session(session_id)` - Get session information  
- `list_browser_sessions()` - List active sessions
- `close_browser_session(session_id)` - Close session (optional - sessions auto-expire)

**Navigation & Interaction:**
- `browser_navigate(url, session_id, timeout)` - Navigate to URL
- `browser_click(selector, session_id, force, timeout)` - Click element
- `browser_type(selector, text, session_id, delay, timeout)` - Type text
- `browser_fill(selector, value, session_id, timeout)` - Fill form field
- `browser_scroll(session_id, selector, x, y)` - Scroll page or element
- `browser_wait(condition, session_id, selector, timeout)` - Wait for condition

**Data Extraction:**
- `browser_screenshot(session_id, full_page, clip, format)` - Take screenshot
- `browser_extract_elements(session_id, selector, attributes)` - Extract DOM elements

### Browser Error Handling
```python
from instavm import (
    InstaVM, BrowserSessionError, BrowserInteractionError, 
    ElementNotFoundError, BrowserTimeoutError, QuotaExceededError
)

client = InstaVM(api_key='your_api_key')

try:
    session_id = client.create_browser_session(1920, 1080)
    client.browser_navigate("https://example.com", session_id)
    client.browser_click("button#nonexistent", session_id)
    
except BrowserSessionError:
    print("Browser session error - may be down or quota exceeded")
except ElementNotFoundError as e:
    print(f"Element not found: {e}")
except BrowserTimeoutError:
    print("Browser operation timed out")
except BrowserInteractionError as e:
    print(f"Browser interaction failed: {e}")
```

## Complete Automation Example
```python
from instavm import InstaVM
import base64

def web_automation_example():
    client = InstaVM(api_key='your_api_key')
    
    # 1. Execute setup code
    setup = client.execute("""
import json
data = {"timestamp": "2024-01-01", "status": "starting"}
print(json.dumps(data))
    """, language="python")
    print("Setup result:", setup)
    
    # 2. Browser automation
    session_id = client.create_browser_session(1920, 1080)
    
    # Navigate and interact
    client.browser_navigate("https://httpbin.org/forms/post", session_id) 
    client.browser_fill("input[name='custname']", "Test User", session_id)
    client.browser_fill("input[name='custemail']", "test@example.com", session_id)
    
    # Take screenshot before submission
    screenshot = client.browser_screenshot(session_id)
    
    # Save screenshot
    with open("automation_screenshot.png", "wb") as f:
        f.write(base64.b64decode(screenshot))
    
    # Get page info
    elements = client.browser_extract_elements(session_id, "input", attributes=["name", "value"])
    
    # 3. Process results
    analysis = client.execute(f"""
elements_count = {len(elements)}
screenshot_size = {len(screenshot)}
print(f"Found {{elements_count}} form elements")
print(f"Screenshot size: {{screenshot_size}} characters")
print("Automation completed successfully")
    """, language="python")
    
    return {
        "setup": setup,
        "elements": elements,
        "analysis": analysis,
        "screenshot_saved": True
    }

# Run automation
result = web_automation_example()
print("Final result:", result)
```

## LLM Framework Integrations

InstaVM now includes built-in integrations with popular LLM frameworks, eliminating boilerplate code for AI-powered automation.

### OpenAI Integration

```python
from instavm import InstaVM
from instavm.integrations.openai import get_tools, execute_tool
from openai import OpenAI

client = InstaVM(api_key='your_api_key')
openai_client = OpenAI(api_key='your_openai_key')

# Get pre-built OpenAI function definitions
tools = get_tools()

# Let the LLM decide what to do
response = openai_client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Navigate to example.com and take a screenshot"}],
    tools=tools,
    tool_choice="auto"
)

# Execute the LLM's tool calls
browser_session = None
for tool_call in response.choices[0].message.tool_calls:
    result = execute_tool(client, tool_call, browser_session)
    if result.get("session"):
        browser_session = result["session"]
    print(f"Tool result: {result}")
```

### Azure OpenAI Integration

```python
from instavm import InstaVM
from instavm.integrations.azure_openai import get_azure_tools, execute_azure_tool
from openai import AzureOpenAI

client = InstaVM(api_key='your_api_key')
azure_client = AzureOpenAI(
    api_key="your_azure_key",
    api_version="2024-02-01",
    azure_endpoint="https://your-resource.openai.azure.com/"
)

tools = get_azure_tools()
browser_session = None

response = azure_client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Find the current weather in New York"}],
    tools=tools
)

for tool_call in response.choices[0].message.tool_calls:
    result = execute_azure_tool(client, tool_call, browser_session)
    if result.get("session"):
        browser_session = result["session"]
```

### Ollama Integration

```python
from instavm import InstaVM
from instavm.integrations.ollama import get_ollama_tools, execute_ollama_tool
import requests

client = InstaVM(api_key='your_api_key')

# Get tool definitions for Ollama
tools = get_ollama_tools()

# Make request to local Ollama instance
response = requests.post('http://localhost:11434/api/chat', json={
    'model': 'llama3',
    'messages': [{'role': 'user', 'content': 'Navigate to github.com and extract the page title'}],
    'tools': tools,
    'stream': False
})

# Execute tool calls from Ollama response
browser_session = None
if response.json().get('message', {}).get('tool_calls'):
    for tool_call in response.json()['message']['tool_calls']:
        result = execute_ollama_tool(client, tool_call, browser_session)
        if result.get("session"):
            browser_session = result["session"]
```

### LangChain Integration

```python
from instavm import InstaVM
from instavm.integrations.langchain import InstaVMTool
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI

# Create InstaVM client and LangChain tool
client = InstaVM(api_key='your_api_key')
instavm_tool = InstaVMTool(client)

# Initialize LangChain agent
llm = OpenAI(api_key='your_openai_key')
tools = [instavm_tool]

agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
    verbose=True
)

# Let the agent use InstaVM for web automation
result = agent.run("Go to example.com and tell me what you see on the page")
print(result)
```

### LlamaIndex Integration

```python
from instavm import InstaVM
from instavm.integrations.llamaindex import get_llamaindex_tools
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import ReActAgent

# Create InstaVM client
client = InstaVM(api_key='your_api_key')

# Get InstaVM function tools for LlamaIndex
tools = get_llamaindex_tools(client)

# Create agent with InstaVM capabilities
llm = OpenAI(model="gpt-4", api_key='your_openai_key')
agent = ReActAgent(
    tools=tools,
    llm=llm,
    verbose=True
)

# Use the agent for web tasks
response = agent.chat("Navigate to news.ycombinator.com and summarize the top 3 posts")
print(response)
```

### Complete LLM Intelligence Example

```python
from instavm import InstaVM
from instavm.integrations.openai import get_tools, execute_tool
from openai import OpenAI
import json

class WebIntelligenceAgent:
    def __init__(self, instavm_key, openai_key):
        self.instavm = InstaVM(api_key=instavm_key)
        self.openai = OpenAI(api_key=openai_key)
        self.tools = get_tools()
        self.browser_session = None
    
    def run_task(self, task_description):
        messages = [
            {"role": "system", "content": "You are a web intelligence agent. Use browser automation and code execution to complete tasks."},
            {"role": "user", "content": task_description}
        ]
        
        for turn in range(5):  # Max 5 turns
            response = self.openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": message.tool_calls
            })
            
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    result = execute_tool(self.instavm, tool_call, self.browser_session)
                    if result.get("session"):
                        self.browser_session = result["session"]
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": json.dumps(result)
                    })
            else:
                # Task complete
                return message.content
        
        return "Task completed with maximum turns reached"

# Usage
agent = WebIntelligenceAgent('your_instavm_key', 'your_openai_key')
result = agent.run_task("Find the current Bitcoin price and create a Python chart showing the trend")
print(result)
```
