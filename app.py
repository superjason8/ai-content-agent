import os
import anthropic
import streamlit as st
from ddgs import DDGS
import json

st.set_page_config(page_title="AI Content Team", page_icon="✍️", layout="centered")
st.title("✍️ AI Content Team")
st.markdown("Enter any topic and your AI team will research, write and edit a professional article automatically.")
st.divider()

topic = st.text_input("What topic do you want an article about?", placeholder="e.g. AI automation for small businesses in Malaysia")
generate = st.button("Generate Article", type="primary")

def search_web(query):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=5):
            results.append(f"Title: {r['title']}\nSummary: {r['body']}\nURL: {r['href']}")
    return "\n\n".join(results)

def run_agent(system_prompt, user_prompt):
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": user_prompt}],
        system=system_prompt
    )
    return message.content[0].text

if generate and topic:
    st.divider()

    with st.status("AI team is working...", expanded=True) as status:

        st.write("Agent 1 — Researcher is searching the web...")
        search_results = search_web(topic)
        research = run_agent(
            "You are an expert researcher. Summarise the key facts, insights and data from the search results provided.",
            f"Topic: {topic}\n\nSearch results:\n{search_results}"
        )

        st.write("Agent 2 — Writer is writing the article...")
        article = run_agent(
            "You are a professional content writer. Write a clear, engaging article using the research provided. Include an introduction, sections with headings, and a conclusion. Aim for 400-600 words.",
            f"Topic: {topic}\n\nResearch:\n{research}"
        )

        st.write("Agent 3 — Editor is polishing the article...")
        final = run_agent(
            "You are a senior editor. Improve this article — fix clarity, flow, strengthen the opening and closing. Return the final polished version only.",
            f"Article to edit:\n{article}"
        )

        status.update(label="Article ready!", state="complete")

    st.divider()
    st.subheader("Your Article")
    st.markdown(final)
    st.divider()
    st.download_button("Download Article", data=final, file_name=f"{topic[:30].replace(' ', '_')}.txt", mime="text/plain")

elif generate and not topic:
    st.warning("Please enter a topic first!")