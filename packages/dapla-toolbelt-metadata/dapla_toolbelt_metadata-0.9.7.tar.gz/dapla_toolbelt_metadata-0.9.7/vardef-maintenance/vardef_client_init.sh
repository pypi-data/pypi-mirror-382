#! /bin/bash

LOG_PREFIX="[Personal init script] Vardef Forvaltning:"
BRANCH="main"
BASE_DIR=$HOME

while [ "$#" -gt 0 ]; do
  case "$1" in
    --branch=*) BRANCH="${1#*=}"; shift 1;;
    --base-dir=*) BASE_DIR="${1#*=}"; shift 1;;
    --branch|--base-dir) echo "$1 requires an argument" >&2; exit 1;;

    -*) echo "$LOG_PREFIX unknown option: $1" >&2; exit 1;;
    # Skip positional arguments
    *) shift 1;;
  esac
done

TMP_CHECKOUT_DIR="$BASE_DIR"/tmp/dapla-toolbelt-metadata
VARIABLE_DEFINITIONS_DIR="$BASE_DIR"/work/variable_definitions

if [ -d "$VARIABLE_DEFINITIONS_DIR" ]; then
  echo "$LOG_PREFIX $VARIABLE_DEFINITIONS_DIR already exists. Exiting to avoid overwriting work."
  exit
fi

mkdir -p "$VARIABLE_DEFINITIONS_DIR"

echo "$LOG_PREFIX Retrieve the notebooks from statisticsnorway/dapla-toolbelt-metadata"
# Retrieve the vardef interface notebooks and put them in the /home/onyxia/work/variable_definitions directory
git clone -n --filter=tree:0 \
  https://github.com/statisticsnorway/dapla-toolbelt-metadata.git "$TMP_CHECKOUT_DIR"
pushd "$TMP_CHECKOUT_DIR" || exit
git sparse-checkout set --no-cone /demo/variable_definitions --no-cone /vardef-maintenance/vardef-maintenance.toml
git checkout "$BRANCH"
cp demo/variable_definitions/* "$VARIABLE_DEFINITIONS_DIR"
cp vardef-maintenance/vardef-maintenance.toml "$VARIABLE_DEFINITIONS_DIR"/pyproject.toml
popd || exit
rm -rf "$TMP_CHECKOUT_DIR"

echo "$LOG_PREFIX Run ssb-project build"
pushd "$VARIABLE_DEFINITIONS_DIR" || exit
echo "n" | ssb-project build --no-verify

echo "$LOG_PREFIX Configure kernel for all Notebooks"
KERNELSPEC_OBJECT='{"kernelspec": {"display_name": "variable_definitions", "language": "python", "name": "variable_definitions"}}'
for file in ./*.ipynb; do
    echo "$LOG_PREFIX Inserting kernelspec into $file"
    # shellcheck disable=SC2005
    input=$(cat "$file") && jq ".metadata += $KERNELSPEC_OBJECT" <<< "$input" > "$file"
done
