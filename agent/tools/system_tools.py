# agent/tools/system_tools.py
from agent.tools.base_tool import BaseTool
from agent.tools.app_launcher import open_application, open_vscode, open_Youtube, open_url

class NotepadTool(BaseTool):
    @property
    def name(self) -> str:
        return "open notepad"

    @property
    def description(self) -> str:
        return "Opens the Notepad application on the user's computer for taking notes."

    def execute(self, argument: str) -> str:
        open_application("notepad.exe")
        return "Notepad opened."

class OpenVSCodeTool(BaseTool):
    @property
    def name(self) -> str:
        return "open vscode"

    @property
    def description(self) -> str:
        return "Opens the Visual Studio Code application."

    def execute(self, argument: str) -> str:
        open_vscode()
        return "VS Code opened."

class SearchYouTubeTool(BaseTool):
    @property
    def name(self) -> str:
        return "search youtube for"

    @property
    def description(self) -> str:
        return "Searches YouTube for a given topic and opens the results in a web browser. The argument should be the topic to search for."

    def execute(self, argument: str) -> str:
        if not argument:
            return "Please specify what you want to search for on YouTube."
        return open_Youtube(argument)

class OpenURLTool(BaseTool):
    @property
    def name(self) -> str:
        return "go to"

    @property
    def description(self) -> str:
        return "Opens a specified URL or website in the default web browser. The argument should be a valid web address (e.g., google.com)."

    def execute(self, argument: str) -> str:
        if not argument:
            return "Please specify a website address to open."
        return open_url(argument)

class GenerateCodeTool(BaseTool):
    @property
    def name(self) -> str:
        return "generate code"

    @property
    def description(self) -> str:
        return "Generates Python code based on a user's request. The argument should be a clear description of the desired functionality (e.g., 'a snake game')."

    def execute(self, argument: str) -> str:
        if not self.llm_client:
            return "Error: LLM client is not available to this tool."
        if not argument:
            return "Please specify what code you need."
        
        # We create a specific prompt for code generation
        code_prompt = f"Please write a complete, executable Python script that {argument}. The code should be well-commented. Only output the code itself, inside a single markdown code block."
        
        # Use the llm_client passed during initialization
        return self.llm_client.generate_response(code_prompt, [])