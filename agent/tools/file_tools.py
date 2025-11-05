# agent/tools/file_tools.py
import os
import shutil
from pathlib import Path
from agent.tools.base_tool import BaseTool
from logger import logger

class ReadFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "read file"

    @property
    def description(self) -> str:
        return "Reads the content of a text file. Argument should be the file path."

    def execute(self, argument: str) -> str:
        try:
            if not argument:
                return "Error: Please provide a file path."
            
            file_path = Path(argument).resolve()
            
            if not file_path.exists():
                return f"Error: File '{argument}' does not exist."
            
            if not file_path.is_file():
                return f"Error: '{argument}' is not a file."
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Read file: {file_path}")
            return f"Content of {file_path.name}:\n\n{content}"
        
        except PermissionError:
            return f"Error: Permission denied to read '{argument}'."
        except UnicodeDecodeError:
            return f"Error: Unable to read '{argument}'. File may be binary."
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return f"Error reading file: {str(e)}"


class WriteFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "write file"

    @property
    def description(self) -> str:
        return "Writes content to a file. Argument format: 'filepath|||content' (use three pipes as separator)."

    def execute(self, argument: str) -> str:
        try:
            if not argument or '|||' not in argument:
                return "Error: Format should be 'filepath|||content'"
            
            parts = argument.split('|||', 1)
            file_path = Path(parts[0].strip()).resolve()
            content = parts[1] if len(parts) > 1 else ""
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Wrote to file: {file_path}")
            return f"✅ Successfully wrote {len(content)} characters to '{file_path.name}'"
        
        except PermissionError:
            return f"Error: Permission denied to write to '{parts[0]}'."
        except Exception as e:
            logger.error(f"Error writing file: {e}")
            return f"Error writing file: {str(e)}"


class CreateFolderTool(BaseTool):
    @property
    def name(self) -> str:
        return "create folder"

    @property
    def description(self) -> str:
        return "Creates a new folder/directory. Argument should be the folder path."

    def execute(self, argument: str) -> str:
        try:
            if not argument:
                return "Error: Please provide a folder path."
            
            folder_path = Path(argument).resolve()
            
            if folder_path.exists():
                return f"Folder '{argument}' already exists."
            
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created folder: {folder_path}")
            return f"✅ Successfully created folder '{folder_path}'"
        
        except PermissionError:
            return f"Error: Permission denied to create '{argument}'."
        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            return f"Error creating folder: {str(e)}"


class ListFilesTool(BaseTool):
    @property
    def name(self) -> str:
        return "list files"

    @property
    def description(self) -> str:
        return "Lists all files and folders in a directory. Argument should be the directory path (use '.' for current directory)."

    def execute(self, argument: str) -> str:
        try:
            if not argument:
                argument = "."
            
            dir_path = Path(argument).resolve()
            
            if not dir_path.exists():
                return f"Error: Directory '{argument}' does not exist."
            
            if not dir_path.is_dir():
                return f"Error: '{argument}' is not a directory."
            
            # List all items in directory
            items = list(dir_path.iterdir())
            
            if not items:
                return f"Directory '{dir_path}' is empty."
            
            # Separate files and folders
            folders = [item.name + "/" for item in items if item.is_dir()]
            files = [item.name for item in items if item.is_file()]
            
            result = f"Contents of '{dir_path}':\n\n"
            
            if folders:
                result += "📁 Folders:\n" + "\n".join(f"  - {f}" for f in sorted(folders)) + "\n\n"
            
            if files:
                result += "📄 Files:\n" + "\n".join(f"  - {f}" for f in sorted(files))
            
            logger.info(f"Listed directory: {dir_path}")
            return result
        
        except PermissionError:
            return f"Error: Permission denied to access '{argument}'."
        except Exception as e:
            logger.error(f"Error listing directory: {e}")
            return f"Error listing directory: {str(e)}"


class DeleteFileTool(BaseTool):
    @property
    def name(self) -> str:
        return "delete file"

    @property
    def description(self) -> str:
        return "Deletes a file or empty folder. Argument should be the path to delete. USE WITH CAUTION!"

    def execute(self, argument: str) -> str:
        try:
            if not argument:
                return "Error: Please provide a path to delete."
            
            path = Path(argument).resolve()
            
            if not path.exists():
                return f"Error: '{argument}' does not exist."
            
            if path.is_file():
                path.unlink()
                logger.warning(f"Deleted file: {path}")
                return f"✅ Deleted file '{path.name}'"
            elif path.is_dir():
                if any(path.iterdir()):
                    return f"Error: Directory '{argument}' is not empty. Cannot delete."
                path.rmdir()
                logger.warning(f"Deleted folder: {path}")
                return f"✅ Deleted empty folder '{path.name}'"
            
        except PermissionError:
            return f"Error: Permission denied to delete '{argument}'."
        except Exception as e:
            logger.error(f"Error deleting: {e}")
            return f"Error deleting: {str(e)}"


class SearchFilesTool(BaseTool):
    @property
    def name(self) -> str:
        return "search files"

    @property
    def description(self) -> str:
        return "Searches for files by name pattern. Argument format: 'directory|||pattern' (e.g., '.|||*.py' to find all Python files)."

    def execute(self, argument: str) -> str:
        try:
            if not argument or '|||' not in argument:
                return "Error: Format should be 'directory|||pattern'"
            
            parts = argument.split('|||', 1)
            dir_path = Path(parts[0].strip() or ".").resolve()
            pattern = parts[1].strip() if len(parts) > 1 else "*"
            
            if not dir_path.exists():
                return f"Error: Directory '{parts[0]}' does not exist."
            
            # Search for files matching pattern
            matches = list(dir_path.rglob(pattern))
            
            if not matches:
                return f"No files found matching pattern '{pattern}' in '{dir_path}'"
            
            result = f"Found {len(matches)} file(s) matching '{pattern}':\n\n"
            result += "\n".join(f"  - {m.relative_to(dir_path)}" for m in matches[:50])
            
            if len(matches) > 50:
                result += f"\n\n... and {len(matches) - 50} more files"
            
            logger.info(f"Searched for '{pattern}' in {dir_path}")
            return result
        
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return f"Error searching files: {str(e)}"