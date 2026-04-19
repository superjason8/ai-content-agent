import os
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

# ─── API KEYS ───────────────────────────────────────────
# We use Anthropic Claude as the AI brain
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "")

# Serper gives agents free web search (get free key at serper.dev)
os.environ["SERPER_API_KEY"] = "f32b6059f1d20a7120747f48eccdb5be2db05ead"

# Tell CrewAI to use Claude instead of ChatGPT
os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["OPENAI_MODEL_NAME"] = "anthropic/claude-sonnet-4-6"

# ─── TOOLS ──────────────────────────────────────────────
search_tool = SerperDevTool()

# ─── AGENTS ─────────────────────────────────────────────

researcher = Agent(
    role="Research Specialist",
    goal="Find accurate and detailed information about the given topic",
    backstory="""You are an expert researcher with years of experience 
    finding reliable information. You search thoroughly and collect 
    the most relevant facts, statistics, and insights.""",
    tools=[search_tool],
    verbose=True
)

writer = Agent(
    role="Content Writer",
    goal="Write a clear, engaging and well structured article",
    backstory="""You are a professional content writer who specialises 
    in turning research into compelling articles. You write in a clear, 
    friendly tone that is easy to understand for business readers.""",
    verbose=True
)

editor = Agent(
    role="Senior Editor",
    goal="Review and improve the article to make it polished and professional",
    backstory="""You are a senior editor with decades of experience. 
    You improve clarity, fix structure, strengthen the opening and 
    closing, and ensure the article is ready to publish.""",
    verbose=True
)

# ─── TASKS ──────────────────────────────────────────────

research_task = Task(
    description="""Research this topic thoroughly: {topic}
    Find key facts, recent developments, statistics, and 
    important insights. Collect at least 5 solid points.""",
    expected_output="A detailed research summary with key facts and insights",
    agent=researcher
)

writing_task = Task(
    description="""Using the research provided, write a professional 
    article about: {topic}
    Include an engaging introduction, clear sections with headings, 
    and a strong conclusion. Aim for 400-600 words.""",
    expected_output="A well structured article with introduction, body sections and conclusion",
    agent=writer,
    context=[research_task]
)

editing_task = Task(
    description="""Review and improve the article written about: {topic}
    Fix any issues with clarity, flow, and structure. 
    Strengthen the opening line and conclusion. 
    Return the final polished version.""",
    expected_output="A polished, publish-ready article",
    agent=editor,
    context=[writing_task]
)

# ─── CREW ───────────────────────────────────────────────

crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    verbose=True
)

# ─── RUN ────────────────────────────────────────────────

print("\n" + "=" * 50)
print("AI CONTENT TEAM")
print("=" * 50)

topic = input("Enter a topic for your article: ")

result = crew.kickoff(inputs={"topic": topic})

print("\n" + "=" * 50)
print("FINAL ARTICLE")
print("=" * 50)
print(result)