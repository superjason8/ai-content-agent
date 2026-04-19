import anthropic
import json
from ddgs import DDGS

client = anthropic.Anthropic()

tools = [
    {
        "name": "web_search",
        "description": "Search the web for information on a topic",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        }
    }
]

def run_web_search(query):
    print(f"  Searching for: {query}")
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=5):
            results.append({
                "title": r["title"],
                "snippet": r["body"],
                "url": r["href"]
            })
    return json.dumps(results)

def run_research_agent(topic):
    print(f"Researching: {topic}")
    print("=" * 50)
    messages = [
        {
            "role": "user",
            "content": f"Research this topic and write a clear summary report: {topic}"
        }
    ]
    while True:
        print("Thinking...")
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )
        if response.stop_reason == "tool_use":
            tool_uses = [
                b for b in response.content if b.type == "tool_use"
            ]
            tool_results = []
            for tool_use in tool_uses:
                tool_name = tool_use.name
                tool_input = tool_use.input
                print(f"  Using tool: {tool_name}")
                if tool_name == "web_search":
                    tool_result = run_web_search(tool_input["query"])
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": tool_result
                })
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            messages.append({
                "role": "user",
                "content": tool_results
            })
        elif response.stop_reason == "end_turn":
            final_report = next(
                b for b in response.content if hasattr(b, "text")
            )
            print("\n" + "=" * 50)
            print("RESEARCH REPORT")
            print("=" * 50)
            print(final_report.text)
            break

print("What topic do you want to research?")
topic = input("Enter topic: ")
run_research_agent(topic)