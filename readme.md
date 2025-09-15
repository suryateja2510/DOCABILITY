# Docability – AI-Powered Document Accessibility Companion

**Docability** is a Proof of Concept (PoC) that makes documents more accessible for everyone.  
It provides **summarization, translation, and audio narration** using **AI Agents enhanced with MCP (Model Context Protocol)** for modular, scalable processing.

---

## 🌟 Features
- 📄 **Summarize Documents** – Generate concise summaries of uploaded documents.  
- 🌍 **Translate Content** – Convert documents into multiple languages.  
- 🔊 **Audio Narration** – Listen to documents in natural-sounding speech.  
- 🤝 **Accessibility First** – Designed to support users with visual or cognitive challenges.  
- 🧩 **Agent + MCP** – Each task (summarization, translation, TTS) is handled by dedicated MCP-enabled tools orchestrated by an AI Agent.  

---

## 🏗️ Tech Stack
- **Backend**: FastAPI (Python)  
- **AI Orchestration**: Azure AI Agent Service (with MCP protocol support)  
- **AI Models**: Azure OpenAI (or OpenAI API)  
- **Text-to-Speech**: Azure Cognitive Services (TTS) or other free TTS APIs  
- **Frontend (optional)**: React (for user interaction)  
- **Storage**: Local / Azure Blob (depending on setup)  

---

## ⚙️ How It Works
1. **Admin uploads a document** (PDF, Word, or Text).  
2. **Docability extracts text** from the file.  
3. **AI Agent orchestrates tasks via MCP**:  
   - Summarizer tool (MCP service) → generates summary  
   - Translator tool (MCP service) → provides translations  
   - TTS tool (MCP service) → produces audio narration  
4. The **User accesses results** from their dashboard:  
   - Read summary  
   - View translation  
   - Play audio narration  

---

## 🚀 Getting Started

### 1. Clone the Repo
```bash
git clone https://github.com/suryateja2510/DOCABILITY
cd DOCABILITY
