# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
import requests
import os

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "file://",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data directory setup
# Get the absolute path to the directory where this file (backend/main.py) is located
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
print("Backend directory:", BACKEND_DIR)
# Construct the absolute path to the data directory
DATA_DIR = os.path.join(BACKEND_DIR , "data")
print(f"Data directory: {DATA_DIR}")
# DATA_DIR = Path("data")
print(f"Data directory: {DATA_DIR}")
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

# Create default topic files if they don't exist
DEFAULT_TOPICS = ["General", "Math", "Science", "History", "Programming"]
for topic in DEFAULT_TOPICS:
    topic_file = os.path.join(DATA_DIR, f"{topic}.md")
    if not os.path.exists(topic_file):
        print(f"Creating topic file: {topic_file}")
        with open(topic_file, "w") as f:
            f.write(f"# {topic} Chat\n\nWelcome to the {topic} chat room!\n")
    else:
        print(f"Topic file already exists: {topic_file}")

def load_topic_content(topic: str) -> str:
    """Loads the content of a topic from its markdown file."""
    topic_file = os.path.join(DATA_DIR, f"{topic}.md")
    print(f"Data directory: {DATA_DIR}, Topic file: {topic_file}")
    if not os.path.exists(topic_file):
        raise HTTPException(status_code=404, detail=f"Topic '{topic}' not found")
    with open(topic_file, "r") as f:
        return f.read()

def get_available_topics():
    """Gets the list of available topics from the data directory."""
    print(f"Data directory: {DATA_DIR}")
    files_in_data = os.listdir(DATA_DIR)
    files_in_data = [f for f in files_in_data if f.endswith(".md")]
    print(f"Files in data: {files_in_data}")
    topics = [f for f in files_in_data]
    # remove .md extension
    topics = [f.replace(".md", "") for f in topics]
    print(f"Topics: {topics}")
    return topics

## Ollama APIs
def is_ollama_running():
    """Checks if Ollama is running by attempting to connect to its API."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()  # Raise an exception for bad status codes
        return True
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error checking Ollama status: {e}")
        return False

def get_ollama_models():
    """Gets the list of models from Ollama."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        data = response.json()
        models = [model["name"] for model in data["models"]]
        return models
    except requests.exceptions.RequestException as e:
        print(f"Error getting Ollama models: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Ollama models")

@app.get("/api/data")
async def get_data():
    print("Backend accessed!")
    return {"message": "Hello from the FastAPI backend!"}

@app.get("/api/ollama/status")
async def get_ollama_status():
    """Checks if Ollama is running and returns its status."""
    running = is_ollama_running()
    return {"running": running}

@app.get("/api/ollama/models")
async def get_models():
    """Gets the list of models from Ollama."""
    if not is_ollama_running():
        raise HTTPException(status_code=503, detail="Ollama is not running")
    try:
        models = get_ollama_models()
        return {"models": models}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/api/topics")
async def get_topics():
    """Gets the list of available topics."""
    topics = get_available_topics()
    return {"topics": topics}

@app.get("/api/topics/{topic}")
async def get_topic_content(topic: str):
    """Gets the content of a specific topic."""
    try:
        content = load_topic_content(topic)
        return {"content": content}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

class BackendAgent:
    def __init__(self):
        self.process = None
        if not is_ollama_running():
            self.start_ollama()
            

    def start_ollama(self):
        """Starts the Ollama server."""
        if self.process is not None:
            raise Exception("Ollama is already running")
        self.process = subprocess.Popen(["ollama", "serve", "-p", "11434"])
        print("Ollama started")

    def stop_ollama(self):
        """Stops the Ollama server."""
        if self.process is None:
            raise Exception("Ollama is not running")
        self.process.terminate()
        self.process.wait()
        self.process = None
        print("Ollama stopped")
    
    def update(self):
        print("Updating...")


backend_agent = BackendAgent()


if __name__ == "__main__":
    import uvicorn
    # Run on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
