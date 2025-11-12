# Import libraries
import os
from dotenv import load_dotenv

# Read env variables from .env file
load_dotenv()

# Server port for MCP server
MCP_CONFIG = {
    "port": int(os.getenv("MCP_PORT", 9500))
}

# LLMs
SPECIFIER_AGENT_CONFIG =  {
    "model": os.getenv("SPECIFIER_LLM", "gpt-5-nano"),
    "reason_effort": os.getenv("SPECIFIER_REASON_EFFORT", None)
}

SELECTOR_AGENT_CONFIG =  {
    "model": os.getenv("SELECTORLLM", "gpt-5-nano"),
    "reason_effort": os.getenv("SELECTOR_REASON_EFFORT", None)
}

DECOMPOSER_AGENT_CONFIG =  {
    "model": os.getenv("DECOMPOSER_LLM", "gpt-5-nano"),
    "reason_effort": os.getenv("DECOMPOSER_REASON_EFFORT", None)
}

BUILDER_AGENT_CONFIG = {
    "model": os.getenv("BUILDER_LLM", "gpt-5-nano"),
    "reason_effort": os.getenv("BUILDER_REASON_EFFORT", None)
}

REFINER_AGENT_CONFIG =  {
    "model": os.getenv("REFINER_LLM", "gpt-5-nano"),
    "reason_effort": os.getenv("REFINER_REASON_EFFORT", None)
}

# Debugger LLM model settings
DEBUGGER_AGENT_CONFIG = {
    "use_debugger": os.getenv("USE_DEBUGGER", "False"),
    "model": os.getenv("DEBUGGER_LLM", "gpt-5-nano"),
    "reason_effort": os.getenv("DEBUGGER_REASON_EFFORT", None),
    "max_itr": os.getenv("MAX_ITERATIONS", 5)
}

# Input settings
INPUT_CONFIG = {
    "jdbc_uri": os.getenv("JDBC_URI", "jdbc:postgresql://localhost:5432/master_thesis_db"),
    "jdbc_username": os.getenv("JDBC_USERNAME", "master_thesis"),
    "jdbc_password": os.getenv("JDBC_PASSWORD", "master"),
    "input_folder": os.getenv("INPUT_FOLDER", None)
}

# Output settings
OUTPUT_CONFIG = {
    "output_folder": os.getenv("OUTPUT_FOLDER", None)
}

# Log settings
LOG_CONFIG = {
    "log_folder": os.getenv("LOG_FOLDER", None)
}

# Wayang server settings
WAYANG_CONFIG = {
    "server_url": os.getenv("WAYANG_URL")
}