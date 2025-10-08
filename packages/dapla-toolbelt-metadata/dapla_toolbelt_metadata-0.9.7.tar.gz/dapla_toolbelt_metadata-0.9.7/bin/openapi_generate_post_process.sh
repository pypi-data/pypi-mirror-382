#!/usr/local/bin/bash

# This script is run by the openapi-generator tool.
# It is run after generation and the path to the specific file is given as an argument.

FILE_PATH=$1

if [[ $FILE_PATH =~ generated/vardef_client/.*/.*\.py ]]; then
    echo "Fixing absolute imports in submodule file $FILE_PATH"
    DOTS=".."
else
    # Depending on where the file is located we need different numbers of dots in the relative import
    DOTS="."
fi

# Replace absolute imports with relative imports
echo "Fixing absolute imports in $FILE_PATH"
sed -i "" "s/from vardef_client./from $DOTS/" "$FILE_PATH"
sed -i "" "s/import vardef_client./from $DOTS import /" "$FILE_PATH"

# Use ruff to fix the worst sins
echo "Running ruff"
ruff check --config pyproject.toml --fix-only --target-version py310 "$FILE_PATH"
ruff format "$FILE_PATH"
