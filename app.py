import os
import streamlit as st
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

# ─── PAGE CONFIG ────────────────────────────────────────
st.set_page_config(
    page_title="AI Content Team",
    page_icon="✍️",
    layout="centered"
)

# ─── HEADER ─────────────────────────────────────────────
st.title("✍️ AI Content Team")
st.markdown("Enter any topic and your 3-agent AI team will research, write and edit a professional article automatically.")
st.divider()

# ─── INPUT ──────────────────────────────────────────────
topic = st.text_input(
    "What topic do you want an article about?",
    placeholder="e.g. AI automation for small businesses in Malaysia"
)

generate = st.button("Generate Article", type="primary")

# ─── RUN AGENTS ─────────────────────────────────────────
if generate and topic:

    # Set API keys
    os.environ["SERPER_API_KEY"] = st.secrets["SERPER_API_KEY"]
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
    os.environ["OPENAI_API_KEY"] = "fake-key"
    os.environ["OPENAI_MODEL_NAME"] = "anthropic/claude-sonnet-4-6"

    search_tool = SerperDevTool()

    # Progress display
    st.divider()
    progress = st.empty()
    status = st.status("AI team is working...", expanded=True)

    with status:
        # ─── AGENTS ─────────────────────────────────────
        st.write("Setting up your AI team...")

        researcher = Agent(
            role="Research Specialist",
            goal="Find accurate and detailed information about the given topic",
            backstory="""You are an expert researcher with years of experience
            finding reliable information. You search thoroughly and collect
            the most relevant facts, statistics, and insights.""",
            tools=[search_tool],
            verbose=False
        )

        writer = Agent(
            role="Content Writer",
            goal="Write a clear, engaging and well structured article",
            backstory="""You are a professional content writer who specialises
            in turning research into compelling articles. You write in a clear,
            friendly tone that is easy to understand for business readers.""",
            verbose=False
        )

        editor = Agent(
            role="Senior Editor",
            goal="Review and improve the article to make it polished and professional",
            backstory="""You are a senior editor with decades of experience.
            You improve clarity, fix structure, strengthen the opening and
            closing, and ensure the article is ready to publish.""",
            verbose=False
        )

        # ─── TASKS ──────────────────────────────────────
        research_task = Task(
            description=f"""Research this topic thoroughly: {topic}
            Find key facts, recent developments, statistics, and
            important insights. Collect at least 5 solid points.""",
            expected_output="A detailed research summary with key facts and insights",
            agent=researcher
        )

        writing_task = Task(
            description=f"""Using the research provided, write a professional
            article about: {topic}
            Include an engaging introduction, clear sections with headings,
            and a strong conclusion. Aim for 400-600 words.""",
            expected_output="A well structured article with introduction, body sections and conclusion",
            agent=writer,
            context=[research_task]
        )

        editing_task = Task(
            description=f"""Review and improve the article written about: {topic}
            Fix any issues with clarity, flow, and structure.
            Strengthen the opening line and conclusion.
            Return the final polished version.""",
            expected_output="A polished, publish-ready article",
            agent=editor,
            context=[writing_task]
        )

        # ─── CREW ───────────────────────────────────────
        crew = Crew(
            agents=[researcher, writer, editor],
            tasks=[research_task, writing_task, editing_task],
            verbose=False
        )

        # ─── RUN ────────────────────────────────────────
        st.write("Agent 1 — Researcher is searching the web...")
        result = crew.kickoff()
        st.write("Agent 2 — Writer is writing the article...")
        st.write("Agent 3 — Editor is polishing the article...")
        status.update(label="Article ready!", state="complete")

    # ─── RESULTS ────────────────────────────────────────
    st.divider()
    st.subheader("Your Article")
    st.markdown(str(result))

    st.divider()
    st.download_button(
        label="Download Article",
        data=str(result),
        file_name=f"{topic[:30].replace(' ', '_')}.txt",
        mime="text/plain"
    )

elif generate and not topic:
    st.warning("Please enter a topic first!")