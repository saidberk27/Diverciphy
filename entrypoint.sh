#!/bin/bash
set -e

# entrypoint.sh - Single entry point for all container roles.
# Implements Strategy Pattern via shell script.
# Closed for modification (generic logic), Open for extension (via new ROLE types).

echo "[Diverciphy] Starting container with ROLE: ${ROLE}"

if [ "$ROLE" = "MASTER_SHREDDER" ]; then
    echo "[Diverciphy] Initializing Master Shredder..."
    # Configurable Port
    PORT=${PORT:-5555}
    exec python src/master/master_shred.py
    
elif [ "$ROLE" = "MASTER_ASSEMBLER" ]; then
    echo "[Diverciphy] Initializing Master Assembler..."
    PORT=${PORT:-5556}
    exec python src/master/master_assemble.py

elif [ "$ROLE" = "WORKER" ]; then
    # Workers need dynamic identity management in K8s (StatefulSet)
    # Hostname is usually worker-0, worker-1. We can use this to derive an index.
    
    HOSTNAME=$(hostname)
    echo "[Diverciphy] Initializing Worker Node ($HOSTNAME)..."
    
    # Simple logic to extract index if hostname ends with number (worker-0 -> 0)
    # Using python for robust string handling inside script
    INDEX=$(python -c "import re; m = re.search(r'\d+$', '$HOSTNAME'); print(m.group(0)) if m else '0'")
    
    # Set Worker Base Port if needed, or stick to one internal port per container (recommended for K8s)
    # In K8s, each pod has its own IP, so they can all listen on 5000.
    PORT=5000
    
    echo "[Diverciphy] Worker Index: $INDEX, Port: $PORT"
    
    # We pass .worker_env dynamically or setup env vars via K8s
    # In K8s, we rely on ENV vars, not .env files.
    # But to keep compatibility with existing code that looks for dotenv, we might skip it or mock it.
    
    exec python src/worker/worker_main.py --port $PORT --env "none"

else
    echo "[!] Error: Unknown ROLE: ${ROLE}"
    echo "Available ROLES: MASTER_SHREDDER, MASTER_ASSEMBLER, WORKER"
    exit 1
fi
