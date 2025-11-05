# 🤖 Local AI Agent with Voice Control

A powerful, fully local AI assistant built with Llama 3 8B, featuring voice control, long-term memory, web automation, and 31 intelligent tools. Everything runs on your machine—no cloud dependencies, no API costs, complete privacy.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)

## ✨ Features

### 🎤 **Voice Interface**
- **Speech-to-Text**: Powered by OpenAI Whisper
- **Text-to-Speech**: Natural voice responses
- **Hands-free Operation**: Full voice control
- **Multi-modal**: Switch between voice and text seamlessly

### 🧠 **Long-term Memory**
- **Vector Database**: ChromaDB for semantic storage
- **Semantic Search**: Find conversations by meaning, not just keywords
- **Persistent Memory**: Remembers across sessions
- **Context Awareness**: Understands conversation history

### 🌐 **Web Automation**
- **Google Search**: Find information on the web
- **Web Scraping**: Extract content from any webpage
- **Content Reading**: Read and summarize articles
- **File Downloads**: Download files from URLs
- **URL Analysis**: Check status and metadata

### ⏰ **Productivity Tools**
- **Advanced Calculator**: Math expressions, percentages, functions
- **Smart Reminders**: Background timers with notifications
- **Clipboard Manager**: Copy/paste with history
- **Screenshot Capture**: Automated screen capture
- **Weather Integration**: Real-time weather data (API key required)

### 💻 **System Control**
- **File Operations**: Create, read, write, delete, search files
- **System Monitoring**: CPU, memory, disk usage
- **Process Management**: List and manage running processes
- **Application Launching**: Open notepad, VS Code, browsers

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Windows 11 (tested), Linux, or macOS
- 8GB+ RAM recommended
- Microphone (for voice input)
- Speakers (for voice output)

### Installation

1. **Clone the repository**
git clone https://github.com/yourusername/local-ai-agent.git
cd local-ai-agent

2. **Create virtual environment**
python -m venv .venv
.venv\Scripts\activate # Windows

3. **Install dependencies**
pip install -r requirements.txt

4. **Download LLM model**

Download Llama 3 8B Instruct (Q4_0 quantization):
- [Meta-Llama-3-8B-Instruct.Q4_0.gguf](https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF)

Place in 'any directory' and update `config.ini` with your path.

5. **Configure the agent**

Edit `config.ini`:
[Paths]
llm_model_path = your/llm/path

[Voice]
enabled = true # Set to false to disable voice

6. **Run the agent**

**CLI mode:**
python main.py

**GUI mode:**
python gradio_app.py

**Voice mode:**
python voice_main.py


## 📖 Usage Examples

### Voice Commands
🎤 "Calculate fifteen percent of two thousand five hundred"
🤖 Agent: 15% of 2500 = 375.0

🎤 "Search Google for AI robotics news"
🤖 Agent: [Shows 5 search results with links]

🎤 "What did we discuss earlier?"
🤖 Agent: [Shows recent conversation history]

🎤 "Take a screenshot"
🤖 Agent: Screenshot saved to agent_data/screenshots/

🎤 "Remind me in 5 minutes to take a break"
🤖 Agent: Reminder set for 1:30 AM

### Text Commands
You: show me system information
Agent: [Displays CPU, RAM, disk usage, OS details]

You: search google for Python tutorials
Agent: [Returns top 5 search results]

You: scrape webpage https://example.com
Agent: [Extracts and displays page content]

You: calculate sqrt(144) + 2^8
Agent: sqrt(144) + 2^8 = 268.0

## 🛠️ Available Tools (31 Total)

### Daily Productivity (5 tools)
- `calculate` - Advanced math with functions
- `set_reminder` - Timers with notifications
- `clipboard` - Copy/paste operations
- `screenshot` - Screen capture
- `weather` - Real-time weather data

### Web Automation (5 tools)
- `google_search` - Web search
- `scrape_webpage` - Content extraction
- `read_webpage` - Article reading
- `download_file` - File downloads
- `url_info` - URL analysis

### Memory (5 tools)
- `search_memory` - Semantic search
- `recent_conversations` - Recent history
- `conversations_on_date` - Date-based recall
- `memory_stats` - Memory statistics
- `memory usage` - System memory info

### System Control (16 tools)
- File operations (6): create, read, write, delete, list, search
- System monitoring (6): CPU, memory, disk, processes, system info, kill process
- Applications (4): open notepad, VS Code, go to URL, search YouTube

## 📁 Project Structure
AI Agent Final/
├── agent/
│ ├── tools/ # All tool implementations
│ │ ├── base_tool.py
│ │ ├── file_tools.py
│ │ ├── system_tools.py
│ │ ├── application_tools.py
│ │ ├── memory_tools.py
│ │ ├── daily_tools.py
│ │ └── web_tools.py
│ └── init.py
├── llm_host/
│ └── host_integration.py # Core agent logic
├── memory/
│ ├── vectorstore.py # Memory system
│ └── init.py
├── voice/
│ ├── voice_interface.py # Voice I/O
│ └── init.py
├── config_manager.py # Configuration handler
├── logger.py # Logging system
├── main.py # Text mode entry
├── voice_main.py # Voice mode entry
├── config.ini # Configuration file
├── requirements.txt
└── README.md

## 🎯 Use Cases

### Research & Learning
- Search and summarize articles
- Save important information
- Recall past research sessions

### Productivity
- Set reminders for tasks
- Quick calculations
- Screenshot important screens
- System monitoring

### Automation
- Web scraping for data collection
- Automated file operations
- System maintenance tasks

### Development
- Quick Python calculations
- File management
- Process monitoring

## 🔒 Privacy & Security

- ✅ **100% Local**: All processing on your machine
- ✅ **No Cloud**: No data sent to external servers
- ✅ **No Tracking**: No telemetry or analytics
- ✅ **Offline Capable**: Works without internet (except web tools)
- ✅ **Open Source**: Full code transparency

## 🐛 Troubleshooting

### Voice not working
- Check microphone permissions
- Verify `[Voice] enabled = true` in config.ini
- Install audio dependencies: `pip install pyaudio`

### Model loading slow
- Use smaller model (base or small)
- Reduce `n_ctx` in config.ini
- Ensure GPU drivers installed for acceleration

### Memory issues
- Reduce `max_memory_entries` in config
- Clear old memories: Delete `.agent_data/chromadb/`
- Use smaller embedding model

### Tool errors
- Check logs in `.logs/agent.log`
- Verify tool-specific dependencies installed
- Review tool permissions (file access, etc.)

## 📊 Performance

**Tested on:**
- CPU: AMD Ryzen 5 (6 cores)
- RAM: 16GB
- GPU: None (CPU-only mode)

**Results:**
- Model load time: ~3-4 seconds
- Response time: ~5-10 seconds per query
- Memory usage: ~2GB (model) + ~500MB (ChromaDB)
- Voice transcription: ~2 seconds (base model)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Llama 3** by Meta AI
- **Whisper** by OpenAI
- **ChromaDB** for vector storage
- **Sentence Transformers** for embeddings
- **llama-cpp-python** for local inference

## 📧 Contact

For questions or suggestions:
- GitHub Issues: [Report bugs or request features]
- Email: [your-email@example.com]

## 🎯 Roadmap

- [ ] Multi-language support (Spanish, French, etc.)
- [ ] Wake word detection ("Hey Assistant")
- [ ] Web UI (Gradio interface)
- [ ] Plugin system for custom tools
- [ ] Mobile app integration
- [ ] Cloud sync (optional)

---

**Built with ❤️ using Python, Llama 3, and Open Source Tools**

⭐ If you find this project useful, please star it on GitHub!

