# This script tests that the generated distributions (wheel and sdist) can be installed and that it meets expectations:
# - A generated config.yaml file is included
# - The package can be imported successfully (as "vcp")
# This is useful to run prior to releases to ensure that the distributions are valid, before testing via pypi installs.
# Particularly if you have made changes to pyproject.toml or the build process.  Other assertions can be added, as needed.
set -e

rm -rf /tmp/.venv-local-* || true
rm -rf dist/ || true
CONFIG_PATH="src/vcp/config/config.yaml"

if [ ! -f "$CONFIG_PATH" ]; then
    uv run python ci/generate_config.py --mode=test $CONFIG_PATH
fi

uv build

uv run python -c 'import vcp' || { echo "FAIL: Failed to import vcp using local source"; exit 1; }
uv run vcp --help > /dev/null || { echo "FAIL: vcp command failed using local source"; exit 1; }

tmp_venv_dir=$(mktemp -d /tmp/venv-vcp-dist-test-XXXXXX)
echo "Using temp venv dir: $tmp_venv_dir"
trap "rm -rf $tmpdir" EXIT
python3 -m venv "$tmp_venv_dir"
. "$tmp_venv_dir/bin/activate"
whl_path="$(ls -t dist/vcp_cli-*.whl | head -n1)"
pip install "$whl_path" > /dev/null
site_packages_dir=$(python -c "import site; print(site.getsitepackages()[0])")
find "$site_packages_dir" -name "config.yaml" | grep -q "vcp/config/config.yaml" || { echo "FAIL: config.yaml not found in installed package (whl)"; exit 1; }
python -c 'import vcp' || { echo "FAIL: Failed to import vcp using whl"; exit 1; }
deactivate

python3 -m venv /tmp/.venv-local-src/
. /tmp/.venv-local-src/bin/activate
tgz_path="$(ls -t dist/vcp_cli-*.tar.gz | head -n1)"
pip install "$tgz_path" > /dev/null
site_packages_dir=$(python -c "import site; print(site.getsitepackages()[0])")
find "$site_packages_dir" -name "config.yaml" | grep -q "vcp/config/config.yaml" || { echo "FAIL: config.yaml not found in installed package (tgz)"; exit 1; }
python -c 'import vcp' || { echo "FAIL: Failed to import vcp using tgz"; exit 1; }
deactivate
