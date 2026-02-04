#!/bin/bash

# --- CONFIGURATION ---
VAULT_DIR="./agents/vault_agent"
SEC_DIR="./agents/secretary_agent"
CORE_DIR="./core-orchestrator"
SENTINEL_DIR="./sentinel-ui/MondaySentinel.App" # Path to your .NET app

PYTHON_EXE="C:/Users/abdem/miniconda3/envs/monday-vault/python.exe"

cleanup() {
    echo -e "\n🛑 Monday Kernel: Shutting down services..."
    # Kill the background processes and their children
    pkill -P $$
    # Specifically ensure dotnet processes are cleaned up
    # (Sometimes dotnet run leaves a persistent process on Windows)
    taskkill //F //IM MondaySentinel.App.exe //T 2>/dev/null
    echo "✅ All services stopped."
    exit
}

trap cleanup SIGINT

echo "🚀 Monday Kernel: Starting polyglot ecosystem..."

# 1. Start Vault Agent
echo "📡 Starting Vault Agent (Port 8001)..."
cd "$VAULT_DIR"
"$PYTHON_EXE" main.py &
cd - > /dev/null

# 2. Start Secretary Agent
echo "📝 Starting Secretary Agent (Port 8002)..."
cd "$SEC_DIR"
"$PYTHON_EXE" secretary.py &
cd - > /dev/null

# 2. Start Secretary Agent
echo "📝 Starting Secretary Agent (Port 8003)..."
cd "$SEC_DIR"
"$PYTHON_EXE" live_listener.py &
cd - > /dev/null

# 3. Start Core Orchestrator (Rust)
echo "🦀 Starting Rust Orchestrator (Port 3000)..."
cd "$CORE_DIR"
cargo run &
cd - > /dev/null

# 4. Start Sentinel (C#)
echo "🔍 Starting Sentinel Observer..."
cd "$SENTINEL_DIR"
dotnet run &
cd - > /dev/null

echo "✨ All systems online. Press Ctrl+C to stop."

wait