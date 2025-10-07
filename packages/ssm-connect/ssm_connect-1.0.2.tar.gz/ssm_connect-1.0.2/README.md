Interactive CLI to connect to AWS EC2 instances via:

SSM Session Manager (shell)

SSH over SSM (with your SSH key)

Multiple sessions in parallel (opens each in a new terminal)

Keyword search across Name/ID/all tag values

Simple, cross-platform, and secure by default.

Features
Search instances by keywords (matches Name, InstanceId, and all tag values)

Choose SSM or SSH-over-SSM per connection

Optional strict SSH host key checking (security toggle)

Opens each session in a new terminal window (Linux, macOS, Windows)

Uses your existing AWS credentials (SSO, profiles, env vars)

Validates SSH key path and permissions (Unix)

Requirements
AWS account permissions to use SSM Session Manager

Locally installed:

AWS CLI v2

SSM Session Manager plugin

OpenSSH client (ssh)

Python 3.8+

boto3 (installed automatically if using PyPI package)

On Linux/macOS, ensure a terminal emulator exists (e.g., gnome-terminal, xterm, or Terminal.app on macOS). On Windows, PowerShell or Windows Terminal recommended.

Install
From source:

Clone this repo and run the script with Python 3.

From PyPI (if published):

pip install ssm-connect

ssm-connect

Usage
Run the tool

Optionally enter keywords to filter instances (e.g., “prod web”)

Select an instance

Choose connection type:

SSM (interactive shell)

SSH over SSM (enter SSH key path and user)

For SSH, choose whether to enable strict host key checking

Each session opens in a new terminal; you can open more without restarting the tool

Notes
SSH over SSM uses AWS-StartSSHSession and does not require port 22 open in security groups.

Strict host key checking is disabled by default for convenience; enable it for production/security-sensitive use.

The tool does not print or store credentials; it inherits your AWS session from the environment/AWS CLI.

Troubleshooting
If “aws” or “ssh” not found: ensure AWS CLI v2 and OpenSSH are on PATH.

If SSO token expired: run aws sso login or refresh your Granted/SSO session.

If SSH key error: ensure the private key exists locally and has correct permissions (chmod 600 on Unix). Avoid cloud-only paths (e.g., OneDrive placeholders).

License
Apache License 2.0. See LICENSE for details.

Contributing
Issues and PRs are welcome. Please keep changes focused and add brief notes to the README when behavior changes.