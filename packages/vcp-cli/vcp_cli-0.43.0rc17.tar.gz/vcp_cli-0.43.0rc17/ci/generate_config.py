#!/usr/bin/env python3
"""
Script: generate_config.py
Reads required environment variables and writes out a YAML config file.
"""

import argparse
import os
import sys
from pathlib import Path


def require_env(var_name):
    val = os.getenv(var_name)
    if not val:
        print(f"Error: environment variable '{var_name}' is not set.", file=sys.stderr)
        sys.exit(1)
    return val


def main():
    parser = argparse.ArgumentParser(
        description="Generate YAML config from environment or in test mode"
    )
    parser.add_argument(
        "out_path",
        nargs="?",
        default="src/vcp/config/config.yaml",
        help="Output config file path",
    )
    parser.add_argument(
        "--mode",
        choices=["test"],
        help="If set to 'test', populate config values as empty strings",
        default=None,
    )
    args = parser.parse_args()

    if args.mode == "test":
        api_base = ""
        data_api_base = ""
        cognito_up = ""
        cognito_id = ""
        cognito_dom = ""
        # enable all feature flags for testing
        data_command_enabled = True
        model_command_enabled = True
        benchmarks_command_enabled = True
        data_credentials_enabled = True
    else:
        api_base = require_env("VCP_API_BASE_URL")
        data_api_base = require_env("DATA_API_BASE_URL")
        cognito_up = require_env("COGNITO_USER_POOL_ID")
        cognito_id = require_env("COGNITO_CLIENT_ID")
        cognito_dom = require_env("COGNITO_DOMAIN")
        # Production feature flag values
        data_command_enabled = True
        model_command_enabled = False
        benchmarks_command_enabled = True
        data_credentials_enabled = False

    yaml_content = f"""
models:
  base_url: {api_base}

data_api:
  base_url: {data_api_base}

benchmarks_api:
  base_url: {api_base}

aws:
  region: "us-west-2"
  cognito:
    user_pool_id: {cognito_up}
    client_id: {cognito_id}
    domain: {cognito_dom}
    flow: web

feature_flags:
  data_command: {data_command_enabled}
  model_command: {model_command_enabled}
  benchmarks_command: {benchmarks_command_enabled}
  data_subcommands:
    credentials: {data_credentials_enabled}
""".lstrip()

    out_file = Path(args.out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(yaml_content)
    print(f"Config written to {out_file.resolve()}")


if __name__ == "__main__":
    main()
