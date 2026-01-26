
#!/bin/bash

# Usage: ./edit_pysteprc.sh <mamba_executable> <env_name>

if [ $# -eq 0 ]; then
    echo "Error: Please provide a conda environment name"
    echo "Usage: $0 <env_name>"
    exit 1
fi

CONDA_CMD="$1"
ENV_NAME="$2"

# Get environment info
ENV_INFO=$($CONDA_CMD env list | grep "^${ENV_NAME} " | awk '{print $NF}')

if [ -z "$ENV_INFO" ]; then
    echo "Error: Environment '${ENV_NAME}' not found"
    echo "Available environments:"
    $CONDA_CMD env list
    exit 1
fi

# Find the pystepsrc file
PYSTEPSRC_PATH="${ENV_INFO}/lib/python*/site-packages/pysteps/pystepsrc"

# Expand wildcard
PYSTEPSRC_FILE=$(ls $PYSTEPSRC_PATH 2>/dev/null | head -n 1)

if [ -z "$PYSTEPSRC_FILE" ]; then
    echo "Error: pystepsrc file not found in environment '${ENV_NAME}'"
    echo "Expected path pattern: ${PYSTEPSRC_PATH}"
    exit 1
fi

echo "Found pystepsrc at: ${PYSTEPSRC_FILE}"

# Check if file exists and is writable
if [ ! -w "$PYSTEPSRC_FILE" ]; then
    echo "Error: Cannot write to ${PYSTEPSRC_FILE}"
    echo "You may need to run this script with appropriate permissions"
    exit 1
fi

# Create backup
BACKUP_FILE="${PYSTEPSRC_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$PYSTEPSRC_FILE" "$BACKUP_FILE"
echo "Created backup at: ${BACKUP_FILE}"

# Edit the file using sed
sed -i 's/"silent_import": false/"silent_import": true/' "$PYSTEPSRC_FILE"

# Verify the change
if grep -q '"silent_import": true' "$PYSTEPSRC_FILE"; then
    echo "Successfully changed silent_import to true"
else
    echo "Warning: Could not verify the change was made"
    echo "Please check the file manually: ${PYSTEPSRC_FILE}"
fi
