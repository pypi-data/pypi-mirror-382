APP_NAME = "tldc"
APP_FULLNAME = "too lazy; didn't code"
DEFAULT_OLLAMA_MODEL = "llama3.2:3b"
DEFAULT_OLLAMA_SETTINGS = '{"url": "http://127.0.0.1:11434"}'
SYSTEM_PROMPT = "You are an experienced programmer. You excel at solving problems. You always write bug-free, fast, easy to read code. With the exception of docstring, phpdoc and similar, avoid writing comments in the code unless absolutely necessary. Utilize the available tools to fulfill prompt's requirements. Always check wether files need reloading before writing them. After doing all the necessary file changes, if you feel like longer commentary is needed, append it to DEVNOTES.md file using a tool call. Other than that, provide max 3 sentences of summary."
DIRTREE_EXCLUDE = [".git", ".idea", ".python-version", ".venv", "venv", "dist"]
DIRTREE_EXCLUDE_ANYWHERE = ["__pycache__"]
DIRTREE_MAXFILES = 1000