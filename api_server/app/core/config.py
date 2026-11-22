# -*- coding: utf-8 -*-
"""
config.py — NutriScale API Server Configuration
"""
import os

# Project root and paths
API_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(API_DIR)
TA2_DIR = os.path.join(PROJECT_ROOT, "ta2")
TA1_DIR = os.path.join(PROJECT_ROOT, "ta1")

# Service Configuration
HOST = os.getenv("NUTRISCALE_HOST", "0.0.0.0")
PORT = int(os.getenv("NUTRISCALE_PORT", "8000"))

# Ollama settings matching TA2
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = "qwen2.5:3b"
EMBEDDING_MODEL = "nomic-embed-text"
