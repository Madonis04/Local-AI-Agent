# 🛠️ Complete Tool Reference

This document provides detailed information about all 31 tools available in the Local AI Agent.

## Table of Contents
- [Daily Productivity Tools](#daily-productivity-tools)
- [Web Automation Tools](#web-automation-tools)
- [Memory Tools](#memory-tools)
- [System Control Tools](#system-control-tools)

---

## Daily Productivity Tools

### 1. Calculator (`calculate`)

**Description**: Perform advanced mathematical calculations including percentages, functions, and expressions.

**Usage**:
You: calculate 15% of 2500
Agent: 15% of 2500 = 375.0

You: calculate sqrt(144) + 2^8
Agent: sqrt(144) + 2^8 = 268.0

You: calculate sin(45) * 100
Agent: sin(45) * 100 = 85.090352

**Supported Functions**:
- Basic: `+`, `-`, `*`, `/`, `^` (power)
- Functions: `sqrt`, `sin`, `cos`, `tan`, `log`, `exp`, `factorial`
- Constants: `pi`, `e`
- Percentages: "X% of Y"

---

### 2. Set Reminder (`set_reminder`)

**Description**: Set timers and reminders with background execution and notifications.

**Usage**:
You: set reminder 5 take a break
Agent: ✓ Reminder set for 1:35 AM (5 min): take a break

You: remind me in 30 minutes to check email
Agent: ✓ Reminder set for 2:00 AM (30 min): check email

**Format**: `<minutes> <message>`

**Features**:
- Background execution
- System notifications
- Console alerts
- Up to 1440 minutes (24 hours)

---

### 3. Clipboard Manager (`clipboard`)

**Description**: Manage clipboard operations with history tracking.

**Operations**:

**Copy text**:
You: clipboard copy Hello from AI Agent
Agent: ✓ Copied to clipboard: Hello from AI Agent

**Paste**:
You: clipboard paste
Agent: Clipboard content: Hello from AI Agent

**View history**:
You: clipboard history
Agent: Clipboard History (last 10 items):

[11:30 PM] Hello from AI Agent

[11:25 PM] Previous text...

**Clear**:
You: clipboard clear
Agent: ✓ Clipboard cleared

---

### 4. Screenshot Tool (`screenshot`)

**Description**: Capture screenshots and save to file.

**Usage**:
You: screenshot
Agent: ✓ Screenshot saved successfully
📁 File: .agent_data/screenshots/screenshot_2025-11-06_01-23-45.png
📊 Size: 234.5 KB
🖼️ Resolution: 1920x1080

You: screenshot my_desktop
Agent: ✓ Screenshot saved as my_desktop.png

**Save Location**: `.agent_data/screenshots/`

---

### 5. Weather Tool (`weather`)

**Description**: Get real-time weather information (requires API key).

**Setup**:
1. Get free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Add to `config.ini`:
[Weather]
api_key = YOUR_API_KEY_HERE

**Usage**:
You: weather Mumbai
Agent: 🌤️ Weather in Mumbai
🌡️ Temperature: 28.5°C (Feels like 31.2°C)
☁️ Conditions: Partly Cloudy
💧 Humidity: 65%
💨 Wind Speed: 3.5 m/s

---

## Web Automation Tools

### 6. Google Search (`google_search`)

**Description**: Search the web and get structured results with links and snippets.

**Usage**:
You: search google for Python tutorials
Agent: 🔍 Search Results for 'Python tutorials':
Python Tutorial - W3Schools
🔗 https://w3schools.com/python/
📝 Learn Python programming with examples...

Official Python Tutorial
🔗 https://docs.python.org/tutorial/
📝 Official documentation for Python...

[Shows top 5 results]

**Backend**: Uses DuckDuckGo (no API key required)

---

### 7. Web Scraper (`scrape_webpage`)

**Description**: Extract text content from any webpage.

**Usage**:
You: scrape webpage https://example.com
Agent: 📄 Scraped Content from: https://example.com
📌 Title: Example Domain
Example Domain
This domain is for use in illustrative examples...
[Full page text content]

**Features**:
- Removes scripts, styles, navigation
- Extracts main content
- Cleans formatting

---

### 8. Web Content Reader (`read_webpage`)

**Description**: Read and extract main article content from webpages.

**Usage**:
You: read webpage https://blog.example.com/article
Agent: 📰 Article Content
🔗 URL: https://blog.example.com/article
📌 Title: How to Build AI Agents
📝 Heading: Building Your First AI Agent

Introduction paragraph...
Main content...

**Best For**: Blog posts, articles, documentation

---

### 9. Download File (`download_file`)

**Description**: Download files from URLs and save locally.

**Usage**:
You: download file https://example.com/document.pdf
Agent: ✓ File downloaded successfully!
📁 Saved to: .agent_data/downloads/document.pdf
📊 Size: 2.45 MB

**Save Location**: `.agent_data/downloads/`

**Supported**: Any file type (PDF, images, documents, etc.)

---

### 10. URL Info (`url_info`)

**Description**: Get information about a URL including status, headers, and metadata.

**Usage**:
You: url info https://github.com
Agent: 🔗 URL Information
📍 URL: https://github.com
🌐 Domain: github.com
📊 Status Code: 200 (OK)
🔄 Final URL: https://github.com/

📋 Response Headers:

Content-Type: text/html; charset=utf-8

Server: GitHub.com

Date: Thu, 06 Nov 2025 01:25:00 GMT

📌 Page Title: GitHub · Build software better, together

---

## Memory Tools

### 11. Search Memory (`search_memory`)

**Description**: Search past conversations using semantic similarity.

**Usage**:
You: search memory about calculations
Agent: Found 3 relevant conversations:

[2025-11-06]
User: calculate 15% of 2500
Agent: 15% of 2500 = 375.0
Tools: calculate

[2025-11-05]
User: what is sqrt(144)
Agent: sqrt(144) = 12
Tools: calculate

**How it works**: Uses AI embeddings to find conversations by meaning, not just keywords.

---

### 12. Recent Conversations (`recent_conversations`)

**Description**: Get the most recent conversation history.

**Usage**:
You: show recent conversations
Agent: Last 5 conversations:

[2025-11-06 01:20:45]
User: What did we just discuss?
Agent: Last 3 conversations...

[2025-11-06 01:20:30]
User: Calculate 10 plus 20
Agent: 10 + 20 = 30

**Default**: Shows 10 most recent

**Custom**: `recent conversations 20` for 20 most recent

---

### 13. Conversations by Date (`conversations_on_date`)

**Description**: Retrieve all conversations from a specific date.

**Usage**:
You: conversations on date 2025-11-05
Agent: Conversations on 2025-11-05 (8 total):

[21:30:45]
User: Show system information
Agent: SYSTEM INFORMATION...

[21:25:12]
User: Calculate 15% of 2500
Agent: 375.0

**Format**: YYYY-MM-DD

---

### 14. Memory Statistics (`memory_stats`)

**Description**: View memory system statistics.

**Usage**:
You: memory stats
Agent: Memory System Statistics:

Total Conversations: 27
Date Range: 2025-11-05 to 2025-11-06
Database Path: .agent_data/chromadb

---

### 15. Memory Usage (`memory usage`)

**Description**: Show system memory (RAM) usage.

**Usage**:
You: memory usage
Agent: 💾 MEMORY USAGE
Total: 15.35 GB
Used: 13.2 GB (86.0%)
Available: 2.15 GB

---

## System Control Tools

### File Operations (6 tools)

#### 16. Create Folder (`create folder`)
You: create folder projects
Agent: ✓ Folder created: projects

#### 17. Write File (`write file`)
You: write file test.txt Hello World
Agent: ✓ File created: test.txt (11 bytes)

#### 18. Read File (`read file`)
You: read file test.txt
Agent: Content of test.txt:
Hello World

#### 19. Delete File (`delete file`)
You: delete file test.txt
Agent: ✓ File deleted: test.txt

#### 20. List Files (`list files`)
You: list files .
Agent: Files in current directory:
📁 projects/
📄 test.txt (11 bytes)
📄 main.py (2.4 KB)

#### 21. Search Files (`search files`)
You: search files *.py
Agent: Found 5 files:
main.py
config_manager.py
logger.py

---

### System Monitoring (6 tools)

#### 22. System Info (`system info`)
You: show system information
Agent: 🖥️ SYSTEM INFORMATION
💻 OS: Windows 11
🧠 CPU: AMD Ryzen 5 (6 cores, 12 threads)
💾 RAM: 15.35 GB (86% used)
💿 Disk: 147 GB (85% used)
⏰ Boot Time: 2025-11-03 22:17:38

#### 23. CPU Usage (`cpu usage`)
You: cpu usage
Agent: 🧠 CPU USAGE: 18.5%
Physical Cores: 6
Logical Cores: 12
Frequency: 3.3 GHz

#### 24. Disk Usage (`disk usage`)
You: disk usage
Agent: 💿 DISK USAGE
Total: 147.46 GB
Used: 125.86 GB (85.4%)
Free: 21.6 GB

#### 25. List Processes (`list processes`)
You: list processes
Agent: Running Processes (Top 10):

python.exe - 2.1 GB RAM

chrome.exe - 1.8 GB RAM

vscode.exe - 0.9 GB RAM

#### 26. Kill Process (`kill process`)
You: kill process 12345
Agent: ✓ Process terminated: PID 12345

⚠️ **Warning**: Use with caution!

---

### Applications (4 tools)

#### 27. Open Notepad (`open notepad`)
You: open notepad
Agent: ✓ Notepad opened

#### 28. Open VS Code (`open vscode`)
You: open vscode
Agent: ✓ VS Code opened

#### 29. Go To URL (`go to`)
You: go to https://github.com
Agent: ✓ Opening https://github.com in browser

#### 30. Search YouTube (`search youtube for`)
You: search youtube for Python tutorials
Agent: ✓ Searching YouTube for: Python tutorials

---

## Tool Combinations

### Research Workflow
search google for AI news

scrape webpage [article URL]

search memory about similar topics

### Productivity Workflow
set reminder 30 meeting starts

clipboard copy [meeting link]

screenshot

### System Maintenance
system info

list processes

cpu usage

---

## Tips & Tricks

1. **Chain commands**: Use multiple tools in sequence
2. **Voice shortcuts**: Say numbers naturally ("fifteen" instead of "15")
3. **Memory search**: Use semantic search for fuzzy matching
4. **File paths**: Use relative or absolute paths
5. **Error recovery**: Agent automatically retries failed operations

---

**Need help?** Check the main [README.md](README.md) or open an issue on GitHub.
