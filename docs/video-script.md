# Lenny Growth Assistant — 2-Minute Demo Video Script

**Target Length:** ~2 Minutes (~260 words)
**Tone:** Professional, clear, and product-focused

---

## 0:00 - 0:15 | Introduction & Value Prop
**[Visual: Screen recording starts on the Lenny Growth Assistant Welcome Screen. The cursor circles the logo and feature cards.]**

**Speaker:** 
"Hi, I'm Rahul, and this is the Lenny Growth Assistant. It’s an AI-powered product management advisor grounded entirely in the transcripts of 50 episodes of Lenny’s Podcast and 10 of his newsletters. It solves a core problem for PMs: finding specific frameworks or insights hidden inside hours of audio."

## 0:15 - 0:45 | RAG & Source Citations
**[Visual: Click 'New Chat'. Type a prompt like: *"How did Duolingo reignite user growth?"* Hit enter. Show the loading state, then the generated response. Scroll down to highlight the clickable source citations.]**

**Speaker:** 
"Let's see it in action. If I ask, 'How did Duolingo reignite user growth?' the backend uses a RAG pipeline—specifically pgvector and sentence-transformers—to retrieve the most relevant chunks from the database. 

Notice how the LLM generates a highly detailed response based *only* on the transcripts. More importantly, it provides exact source citations at the bottom. Clicking one takes you directly to the source episode, ensuring 100% traceability."

## 0:45 - 1:20 | Ship 30 Essays & Artifact Viewer
**[Visual: Type another prompt: *"Write an essay about founder-led sales."* Fast forward slightly through generation. Click the 'View Essay' button to open the Artifact Viewer side-panel.]**

**Speaker:** 
"Beyond simple Q&A, the assistant has specialized agent skills. If I ask it to write an essay about 'founder-led sales,' the agent routes this to a Ship 30-for-30 skill. 

Instead of cluttering the chat, it generates a publication-ready, 1,200-word essay and renders it in our custom Artifact Viewer side-panel. This viewer is sandboxed for security and supports both Markdown and HTML generation, allowing for a clean, side-by-side reading experience."

## 1:20 - 1:45 | Architecture & Model Toggling
**[Visual: Open the 'AI Model' dropdown in the bottom left corner. Show the options (Ollama, OpenAI, Anthropic). Then briefly show a graphic of the Architecture diagram from the README.]**

**Speaker:** 
"Under the hood, the backend is built with FastAPI and PostgreSQL. One of my favorite features is the pluggable LLM architecture. Using a provider factory pattern, you can easily toggle between running entirely locally with Ollama for privacy, or using cloud models like OpenAI and Anthropic—all controlled via environment variables."

## 1:45 - 2:00 | Conclusion
**[Visual: Close the Artifact Viewer, toggle the mobile responsive view using browser dev tools to show the sidebar sliding in.]**

**Speaker:** 
"The frontend is built with React and Tailwind, featuring a fully responsive layout with persistent chat sessions. The entire stack is containerized and deploys with a single `docker compose up` command. 

Thanks for watching!"
