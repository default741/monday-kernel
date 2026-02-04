# 🚀 Monday Kernel
### The Context-Aware Personal Operating System

**Monday Kernel** is a local-first, polyglot intelligence engine designed to act as a "Digital Twin" of your technical brain. It bridges the gap between your real-time activity and your long-term memory by integrating OS-level hooks, live audio transcription, and a hybrid knowledge graph.



---

## 🏗️ System Architecture

The project is built using a "Best Tool for the Job" philosophy across three primary languages:

* **Rust (Core Orchestrator):** Acts as the high-performance "Executive Function," routing data between agents and maintaining thread-safe system state.
* **Python (Intelligence Vault & Secretary):** Handles the heavy lifting of AI models. It runs **OpenAI Whisper** for local transcription and manages the **ChromaDB** (Vector) and **Neo4j** (Graph) databases.
* **C# / .NET (Sentinel UI):** Interfaces directly with the Windows API to monitor focused windows and provides the **Cerebro HUD**—a global `Alt+Space` search interface.

---

## 🧠 Key Features

* **Hybrid GraphRAG:** Combines semantic search (Vector) with relational mapping (Graph) to provide context-aware retrieval.
* **Sentinel Focus Tracking:** Automatically tags every ingested note with the application you were using at that moment (e.g., VS Code, Chrome, Slack).
* **Command-Driven Audio:** Toggle local audio recording via `/listen` slash commands in the search bar to capture meeting notes and thoughts.
* **100% Local & Private:** No data ever leaves your machine. Whisper, the databases, and the orchestrator all run on localhost.



---

## 🚦 Getting Started

### Prerequisites
* **Python 3.10+** (Conda recommended)
* **Rust 1.75+** (Cargo)
* **.NET 9.0 SDK**
* **FFmpeg** (Required for Whisper audio processing)
* **Docker Desktop** (For Neo4j and ChromaDB)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/monday-kernel.git
   cd monday-kernel
   ```

2. **Setup the Databases:**
    ```Bash
    docker-compose up -d
    ```

3. **Install Python Dependencies:**
    ```Bash
    pip install -r requirements.txt
    ```

4. **Build the Sentinel:**
    ```Bash
    cd sentinel-ui/MondaySentinel.App
    dotnet build
    ```

### Running the System

The entire ecosystem is managed by a single "Butter Script."
```Bash
./run_monday.sh
```



---

## ⌨️ Global Commands

 - Alt + Space: Open/Close the Cerebro HUD.
 - /listen: Toggle live audio transcription.
 - [Query]: Search your brain using natural language.



---

## 🛠️ Roadmap

 - [x] OS-level context tracking
 - [x] Hybrid Vector/Graph retrieval
 - [x] Command-driven live audio transcription
 - [ ] Next: Local LLM Synthesis (Llama 3 Integration)
 - [ ] Next: Automated Deep Work "Do Not Disturb" mode


---

### How to use this file
1. Create a new file in your root folder: `touch README.md`.
2. Paste the content above.
3. Commit it: `git add README.md && git commit -m "docs: add comprehensive readme and architecture overview"`.
