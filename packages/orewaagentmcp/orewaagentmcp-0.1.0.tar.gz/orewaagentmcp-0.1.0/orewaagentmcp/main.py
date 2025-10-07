from fastmcp import FastMCP, Context
from fastmcp.utilities.types import Image
from fastmcp.prompts.prompt import TextContent
from .utility import web_search, fetch, current_time, gemini_image_generate, gemini_codegen, GitMan, DeepResearch, download_image
from dotenv import dotenv_values
import os
import asyncio

mcp = FastMCP("OrewaAgentMCP")

class TodoList:
    def __init__(self):
        self.todos = []
    def add(self, item: str) -> str:
        self.todos.append(item)
        return f"Added todo: {item}"
    def remove(self, item: str) -> str:
        if item in self.todos:
            self.todos.remove(item)
            return f"Removed todo: {item}"
        return f"Todo item not found: {item}"
    def set(self, items: list) -> str:
        self.todos = items
        return "Todo list updated."
    def get(self) -> list:
        return self.todos
todo_list = TodoList()

class BaseMemory:
    def __init__(self):
        self.memory = {}
    def set(self, key: str, value: str) -> str:
        self.memory[key] = value
        return f"Set memory[{key}] = {value}"
    def get(self, key: str) -> str:
        return self.memory.get(key, "Key not found.")
    def delete(self, key: str) -> str:
        if key in self.memory:
            del self.memory[key]
            return f"Deleted memory key: {key}"
        return "Key not found."
    def clear(self) -> str:
        self.memory.clear()
        return "Memory cleared."
    def search(self, keyword: str) -> dict:
        results = {k: v for k, v in self.memory.items() if keyword in k or keyword in v}
        return results
    def keys(self) -> list:
        return list(self.memory.keys())
    def items(self) -> dict:
        return self.memory.items()

memory = BaseMemory()

@mcp.tool
async def Read(file_path: str, ctx: Context) -> str:
    """Reads the full contents of a file."""
    try:
        ctx.log(f"Reading file at: {file_path}")
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        ctx.log(f"Error reading file: {str(e)}")
        return f"Error reading file, additional info: {str(e)}"

@mcp.tool
async def Write(file_path: str, content: str, ctx: Context) -> str:
    """Writes content to a file. Overwrites if the file already exists."""
    try:
        ctx.log(f"Writing file at: {file_path}")
        with open(file_path, 'w') as file:
            file.write(content)
        return "File written successfully."
    except Exception as e:
        ctx.log(f"Error writing file: {str(e)}")
        return f"Error writing file, additional info: {str(e)}"

@mcp.tool
async def Edit(file_path: str, replacement: str, new_content: str, ctx: Context) -> str:
    """Replaces occurrences of a string in a file with new content."""
    try:
        ctx.log(f"Editing file at: {file_path}")
        with open(file_path, 'r') as file:
            content = file.read()
        updated_content = content.replace(replacement, new_content)
        with open(file_path, 'w') as file:
            file.write(updated_content)
        return "File edited successfully."
    except Exception as e:
        ctx.log(f"Error editing file: {str(e)}")
        return f"Error editing file, additional info: {str(e)}"

@mcp.tool
async def MultiRead(file_paths: list, ctx: Context) -> dict:
    """Reads multiple files and returns their contents in a dictionary."""
    contents = {}
    for path in file_paths:
        try:
            ctx.log(f"Reading file at: {path}")
            with open(path, 'r') as file:
                contents[path] = file.read()
        except Exception as e:
            ctx.log(f"Error reading file at {path}: {str(e)}")
            contents[path] = f"Error reading file, additional info: {str(e)}"
    return contents

@mcp.tool
async def MultiWrite(file_dict: dict, ctx: Context) -> str:
    """Writes multiple files given a dictionary of file paths and their contents."""
    for path, content in file_dict.items():
        try:
            ctx.log(f"Writing file at: {path}")
            with open(path, 'w') as file:
                file.write(content)
        except Exception as e:
            ctx.log(f"Error writing file at {path}: {str(e)}")
            return f"Error writing file at {path}, additional info: {str(e)}"
    return "All files written successfully."

@mcp.tool
async def MultiEdit(edit_dict: dict, ctx: Context) -> str:
    """Edits multiple files given a dictionary of file paths and their replacement rules or apply multiple edits on one file."""
    for path, edits in edit_dict.items():
        try:
            ctx.log(f"Editing file at: {path}")
            with open(path, 'r') as file:
                content = file.read()
            for replacement, new_content in edits.items():
                content = content.replace(replacement, new_content)
            with open(path, 'w') as file:
                file.write(content)
        except Exception as e:
            ctx.log(f"Error editing file at {path}: {str(e)}")
            return f"Error editing file at {path}, additional info: {str(e)}"
    return "All files edited successfully."

@mcp.tool
async def FileExists(file_path: str, ctx: Context) -> bool:
    """Checks if a file exists at the given path."""
    ctx.log(f"Checking if file exists at: {file_path}")
    return os.path.isfile(file_path)

@mcp.tool
async def MultiFileExists(file_paths: list, ctx: Context) -> dict:
    """Checks if multiple files exist and returns a dictionary with the results."""
    results = {}
    for path in file_paths:
        ctx.log(f"Checking if file exists at: {path}")
        results[path] = os.path.isfile(path)
    return results

@mcp.tool
async def ListFiles(directory_path: str, ctx: Context) -> list:
    """Lists all files in the specified directory."""
    ctx.log(f"Listing files in directory at: {directory_path}")
    try:
        return [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    except Exception as e:
        ctx.log(f"Error listing files in directory at {directory_path}: {str(e)}")
        return f"Error listing files, additional info: {str(e)}"

@mcp.tool
async def TreeDirectory(directory_path: str, ctx: Context) -> list:
    """Returns a smart tree view of the directory structure.
    - Skips common large/irrelevant folders (node_modules, .git, venv, .venv, __pycache__, .idea, .vscode, etc.).
    - Returns a list of dicts: {"dir": <abs_path>, "files": [<file1>,...], "num_files": <total_files_in_dir>, "skipped_files": <files_not_listed>, "depth": <depth_from_root>}
    """
    ctx.log(f"Creating smart tree directory view at: {directory_path}")
    try:
        IGNORE_NAMES = {
            "node_modules", ".git", "__pycache__", "venv", ".venv", "env", ".env",
            ".idea", ".vscode", "dist", "build", "target", ".pytest_cache", ".cache",
            "vendor", ".next", ".nuxt", ".parcel-cache", ".sass-cache", ".terraform",
            ".gradle", ".m2", "logs", "log", "tmp", "temp", ".history"
        }

        MAX_DEPTH = 5  # maximum relative depth to traverse (root is depth 0)
        MAX_FILES_PER_DIR = 200  # limit files listed per directory to avoid huge lists
        MAX_ENTRIES_TO_DESCEND = 5000  # if a directory appears enormous, skip descending into it

        start = os.path.abspath(directory_path)
        tree = []

        for root, dirs, files in os.walk(start, topdown=True):
            # calculate depth relative to start
            rel = os.path.relpath(root, start)
            depth = 0 if rel == "." else rel.count(os.sep) + 1

            # If depth exceeded, prune all subdirectories so walk won't go deeper
            if depth > MAX_DEPTH:
                ctx.log(f"Pruning deeper directories at depth {depth} in: {root}")
                dirs[:] = []  # don't descend further
                continue

            # Normalize and prune directories in-place to avoid descending into ignored ones
            pruned = []
            for d in list(dirs):
                # skip by name, hidden dirs, or obvious large dirs
                if d in IGNORE_NAMES or d.startswith("."):
                    pruned.append(d)
                    dirs.remove(d)
                else:
                    # also check combined path for ignored segments (e.g., subfolders named node_modules)
                    combined = os.path.join(root, d)
                    if any(part in IGNORE_NAMES for part in combined.split(os.sep)):
                        pruned.append(d)
                        dirs.remove(d)

            if pruned:
                ctx.log(f"Pruned directories in {root}: {pruned}")

            # quick sanity check: if this directory already contains an enormous number of entries, skip its contents
            try:
                total_entries = len(files) + len(dirs)
                if total_entries > MAX_ENTRIES_TO_DESCEND:
                    ctx.log(f"Skipping huge directory {root} with {total_entries} entries")
                    dirs[:] = []
                    tree.append({
                        "dir": root,
                        "files": [],
                        "num_files": len(files),
                        "skipped_files": len(files),
                        "depth": depth,
                        "note": "skipped listing due to large directory size"
                    })
                    continue
            except Exception:
                # if counting fails for any reason, continue gracefully
                pass

            # sort and limit files to MAX_FILES_PER_DIR, hide common binary/lock files? (keep it simple)
            visible_files = [f for f in sorted(files) if not f.startswith(".")]
            skipped_files = 0
            if len(visible_files) > MAX_FILES_PER_DIR:
                skipped_files = len(visible_files) - MAX_FILES_PER_DIR
                visible_files = visible_files[:MAX_FILES_PER_DIR]

            tree.append({
                "dir": root,
                "files": visible_files,
                "num_files": len(files),
                "skipped_files": skipped_files,
                "depth": depth
            })

        return tree
    except Exception as e:
        ctx.log(f"Error creating tree directory view at {directory_path}: {str(e)}")
        return f"Error creating tree directory view, additional info: {str(e)}"

@mcp.tool
async def MultiListFiles(directory_paths: list, ctx: Context) -> dict:
    """Lists files in multiple directories and returns a dictionary with the results."""
    results = {}
    for path in directory_paths:
        ctx.log(f"Listing files in directory at: {path}")
        try:
            results[path] = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        except Exception as e:
            ctx.log(f"Error listing files in directory at {path}: {str(e)}")
            results[path] = f"Error listing files, additional info: {str(e)}"
    return results

@mcp.tool
async def Bash(command: str, ctx: Context) -> str:
    """Executes a bash command and returns the output."""
    try:
        ctx.log(f"Executing bash command: {command}")
        result = os.popen(command).read()
        return result
    except Exception as e:
        ctx.log(f"Error executing bash command: {str(e)}")
        return f"Error executing command, additional info: {str(e)}"

@mcp.tool
async def WebSearch(query: str, max_results: int = 10, ctx: Context = None) -> dict:
    """Performs a web search using DuckDuckGo and returns a list of results."""
    ctx.log(f"Performing web search for query: {query} with max results: {max_results}")
    try:
        results = web_search(query, max_results)
        return results
    except Exception as e:
        ctx.log(f"Error performing web search: {str(e)}")
        return {"error": f"Error performing web search, additional info: {str(e)}"}

@mcp.tool
async def Fetch(url: str, ctx: Context) -> str:
    """Fetches and extracts text content from a given URL."""
    ctx.log(f"Fetching content from URL: {url}")
    try:
        content = fetch(url)
        return content
    except Exception as e:
        ctx.log(f"Error fetching content from URL: {str(e)}")
        return f"Error fetching content, additional info: {str(e)}"

@mcp.tool
async def RunPy(code: str, ctx: Context) -> str:
    """Executes a Python code snippet and returns the output or error.\nExample: `result = 2 + 2` -> returns 4. Make sure to assign the output to a variable named `result`. Usecases: data processing, calculations, metrics, etc."""
    try:
        ctx.log(f"Executing Python code:\n{code}")
        local_vars = {}
        exec(code, {}, local_vars)
        return str(local_vars.get('result', 'Code executed successfully.'))
    except Exception as e:
        ctx.log(f"Error executing Python code: {str(e)}")
        return f"Error executing code, additional info: {str(e)}"

@mcp.tool
async def Time(ctx: Context) -> str:
    """Returns the current system time."""
    ctx.log("Fetching current system time.")
    try:
        current = current_time()
        return current
    except Exception as e:
        ctx.log(f"Error fetching current time: {str(e)}")
        return f"Error fetching time, additional info: {str(e)}"

@mcp.tool
async def Todo(action: str, item: str = None, items: list = None, ctx: Context = None) -> dict:
    ctx.log(f"Todo action: {action}, item: {item}, items: {items}")
    try:
        if action == "add" and item:
            message = todo_list.add(item)
            return {"message": message, "todos": todo_list.get()}
        elif action == "remove" and item:
            message = todo_list.remove(item)
            return {"message": message, "todos": todo_list.get()}
        elif action == "set" and items is not None:
            message = todo_list.set(items)
            return {"message": message, "todos": todo_list.get()}
        elif action == "get":
            return {"todos": todo_list.get()}
        else:
            return {"error": "Invalid action or missing parameters."}
    except Exception as e:
        ctx.log(f"Error managing todo list: {str(e)}")
        return {"error": f"Error managing todo list, additional info: {str(e)}"}

@mcp.tool
async def Summerize(text: str, ctx: Context) -> str:
    """Summarizes the given text."""
    try:
        ctx.log("Summarizing text.")
        if len(text) > 1000:
            text = text[:1000] + "..."  # Truncate to first 1000 characters
        prompt = f"Summarize the following text:\n\n{text}\n\nSummary:"
        response = await mcp.llm.complete(prompt)
        return response.strip()
    except Exception as e:
        ctx.log(f"Error summarizing text: {str(e)}")
        return f"Error summarizing text, additional info: {str(e)}"

if dotenv_values(".env").get("GEMINI_API_KEY"):
    @mcp.tool
    async def ImageGen(prompt: str, save_to: str, ctx: Context) -> str:
        """Generates an image based on the given prompt and saves it to the specified path."""
        try:
            ctx.log(f"Generating image with prompt: {prompt}, saving to: {save_to}")
            api_key = dotenv_values(".env").get("GEMINI_API_KEY")
            message = gemini_image_generate(prompt, save_to, api_key)
            return message
        except Exception as e:
            ctx.log(f"Error generating image: {str(e)}")
            return f"Error generating image, additional info: {str(e)}"
    @mcp.tool
    async def GenerateCode(prompt: str, ctx: Context) -> str:
        """Generates code based on the given prompt using Gemini Codegen model."""
        try:
            ctx.log(f"Generating code with prompt: {prompt}")
            api_key = dotenv_values(".env").get("GEMINI_API_KEY")
            code = gemini_codegen(prompt, api_key)
            return code
        except Exception as e:
            ctx.log(f"Error generating code: {str(e)}")
            return f"Error generating code, additional info: {str(e)}"
    @mcp.tool
    async def DeepResearch(query: str, output_md_file: str = "research.md", ctx: Context = None) -> dict:
        """Performs deep research on a topic using web search and summarizes findings into a markdown file. Example: DeepResearch("Best shadcn components", "shadcn_research.md")"""
        ctx.log(f"DeepResearch Agent Activated.")
        ctx.log(f"Research Topic: {query}, Output File: {output_md_file}, This may take a while...")
        try:
            api_key = dotenv_values(".env").get("GENAI_API_KEY")
            result = DeepResearch(query, output_md_file, api_key)
            return result
        except Exception as e:
            ctx.log(f"Error performing deep research: {str(e)}")
            return {"error": f"Error performing deep research, additional info: {str(e)}"}

@mcp.tool
async def Memory(action: str, key: str = None, value: str = None, keyword: str = None, ctx: Context = None) -> dict:
    """Manages a simple key-value memory store with actions: set, get, delete, clear, search, keys, items. example: Memory("set", "username", "john_doe"), Memory("search", keyword="john"), Memory("get", "username"), Memory("delete", "username"), Memory("clear"), Memory("keys"), Memory("items")"""
    ctx.log(f"Memory action: {action}, key: {key}, value: {value}, keyword: {keyword}")
    try:
        if action == "set" and key and value:
            message = memory.set(key, value)
            return {"message": message}
        elif action == "get" and key:
            value = memory.get(key)
            return {"value": value}
        elif action == "delete" and key:
            message = memory.delete(key)
            return {"message": message}
        elif action == "clear":
            message = memory.clear()
            return {"message": message}
        elif action == "search" and keyword:
            results = memory.search(keyword)
            return {"results": results}
        elif action == "keys":
            keys = memory.keys()
            return {"keys": keys}
        elif action == "items":
            items = memory.items()
            return {"items": items}
        else:
            return {"error": "Invalid action or missing parameters."}
    except Exception as e:
        ctx.log(f"Error managing memory: {str(e)}")
        return {"error": f"Error managing memory, additional info: {str(e)}"}

@mcp.tool
async def GitTool(action: str, repo_path: str, message: str = None, ctx: Context = None) -> str:
    """Manages git operations with actions: pull, commit, set_identity, diff, push, status, clone, init. Example: GitTool("pull", "/path/to/repo"), GitTool("commit", "/path/to/repo", "Commit message"), GitTool("set_identity", "/path/to/repo", "Name <email>"), GitTool("diff", "/path/to/repo"), GitTool("push", "/path/to/repo"), GitTool("status", "/path/to/repo"), GitTool("clone", "<repo_url>", "/path/to/clone"), GitTool("init", "/path/to/repo")"""
    ctx.log(f"Git action: {action}, repo_path: {repo_path}, message: {message}")
    try:
        if action == "clone" and message:
            result = GitMan.clone(repo_path, message)
            return result
        elif action == "init":
            result = GitMan.init(repo_path)
            return result
        else:
            gitman = GitMan(repo_path)
            if action == "pull":
                return gitman.pull()
            elif action == "commit" and message:
                return gitman.commit(message)
            elif action == "set_identity" and message:
                name_email = message.split("<")
                if len(name_email) == 2:
                    name = name_email[0].strip()
                    email = name_email[1].replace(">", "").strip()
                    return gitman.identity_set(name, email)
                else:
                    return "Error: Invalid format for set_identity. Use 'Name <email>'."
            elif action == "diff":
                return gitman.diff()
            elif action == "push":
                return gitman.push()
            elif action == "status":
                return gitman.status()
            else:
                return "Error: Invalid action or missing parameters."
    except Exception as e:
        ctx.log(f"Error managing git: {str(e)}")
        return f"Error managing git, additional info: {str(e)}"
    
@mcp.tool
async def Vision(image_path: str, ctx: Context) -> Image:
    """Returns the image at the specified path."""
    try:
        image = Image(path=image_path)
        return image
    except Exception as e:
        ctx.log(f"Error loading image at {image_path}: {str(e)}")
        return None

@mcp.tool
async def VisionURL(image_url: str, ctx: Context) -> Image:
    """Returns the image from the specified URL."""
    try:
        image = Image(path=download_image(image_url))
        return image
    except Exception as e:
        ctx.log(f"Error loading image from URL {image_url}: {str(e)}")
        return None

@mcp.tool
async def Thinking(thought: str, ctx: Context) -> str:
    """Logs a thought process or internal note."""
    ctx.log(f"Thought: {thought}")
    return "Thought logged."

@mcp.tool
async def PlanGenerate(plan: str, ctx: Context) -> str:
    """Generates a detailed plan based on the given outline."""
    try:
        ctx.log(f"Generating plan for outline: {plan}")
        prompt = f"Generate a detailed plan based on the following outline:\n\n{plan}\n\nDetailed Plan:"
        response = await ctx.sample(prompt, system_prompt="You are a meticulous planner. Break down the outline into clear, actionable steps with explanations.", max_tokens=1000, temperature=0.3, top_p=0.9)
        return response.text
    except Exception as e:
        ctx.log(f"Error generating plan: {str(e)}")
        return f"Error generating plan, additional info: {str(e)}"

async def main():
    await mcp.run_stdio_async(show_banner=False)

if __name__ == "__main__":
    asyncio.run(main())