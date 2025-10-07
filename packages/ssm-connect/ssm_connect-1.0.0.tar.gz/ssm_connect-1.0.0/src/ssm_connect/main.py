## Copyright 2025 Siby Jose
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# !/usr/bin/env python3
import os
import sys
import subprocess
import stat
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from enum import Enum
import shutil
import platform
import shlex
import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

Instance = Dict[str, str]

class ConnectionType(Enum):
    SSM = "ssm"
    SSH = "ssh"

def make_boto3_session() -> boto3.Session:
    os.environ.setdefault("AWS_SDK_LOAD_CONFIG", "1")
    return boto3.Session()

def get_session_credentials(session: boto3.Session) -> Dict[str, str]:
    try:
        credentials = session.get_credentials()
        if not credentials:
            return {}
        frozen = credentials.get_frozen_credentials()
        env_creds = {
            "AWS_ACCESS_KEY_ID": frozen.access_key,
            "AWS_SECRET_ACCESS_KEY": frozen.secret_key,
        }
        if frozen.token:
            env_creds["AWS_SESSION_TOKEN"] = frozen.token
        return env_creds
    except NoCredentialsError:
        print("Warning: Could not resolve AWS credentials from the session.", file=sys.stderr)
        return {}

def _get_instance_name(tags: Optional[List[Dict[str, str]]]) -> str:
    if not tags:
        return "Unnamed"
    for tag in tags:
        if tag.get("Key") == "Name":
            return tag.get("Value", "Unnamed")
    return "Unnamed"

def validate_key_permissions(key_path: Path) -> bool:
    if os.name == 'nt':
        return True
    try:
        mode = key_path.stat().st_mode
        if mode & (stat.S_IRWXG | stat.S_IRWXO):
            print(f"\nWarning: Private key '{key_path}' has overly permissive access.", file=sys.stderr)
            print(f"         To fix, run: chmod 600 {key_path}", file=sys.stderr)
            return False
        return True
    except Exception as e:
        print(f"Warning: Could not check key permissions: {e}", file=sys.stderr)
        return True

def list_running_instances(session: boto3.Session) -> List[Instance]:
    ec2 = session.client("ec2", config=Config(retries={"max_attempts": 5}))
    paginator = ec2.get_paginator("describe_instances")
    filters = [{"Name": "instance-state-name", "Values": ["running"]}]
    instances = []
    for page in paginator.paginate(Filters=filters):
        for reservation in page.get("Reservations", []):
            for inst in reservation.get("Instances", []):
                tags = inst.get("Tags") or []
                flat_tags = {tag['Key'].lower(): (tag.get('Value') or '').lower() for tag in tags if 'Key' in tag}
                all_tag_values = ' '.join(flat_tags.values())
                instances.append({
                    "InstanceId": inst.get("InstanceId"), 
                    "Name": _get_instance_name(tags),
                    "AllTagsBlob": all_tag_values
                })
    return instances

def prompt_for_keywords() -> Optional[List[str]]:
    raw = input("\n(Optional) Enter keywords to filter instances (or press ENTER to list all): ").strip()
    if not raw:
        return None
    return [s.lower() for s in raw.replace(',', ' ').split() if s.strip()]

def filter_instances_by_keywords(instances: List[Instance], keywords: Optional[List[str]]) -> List[Instance]:
    if not keywords:
        return instances
    filtered = []
    for inst in instances:
        search_blob = (
            inst.get("Name", "").lower() + " " +
            inst.get("InstanceId", "").lower() + " " +
            inst.get("AllTagsBlob", "")
        )
        if all(kw in search_blob for kw in keywords):
            filtered.append(inst)
    return filtered

def choose_instance(instances: List[Instance]) -> Optional[str]:
    if not instances:
        return None
    print("\nSelect an EC2 Instance:")
    for idx, inst in enumerate(instances, start=1):
        print(f"[{idx}] {inst['Name']} ({inst['InstanceId']})")
    print("[0] Exit / Refine Search")
    try:
        raw_choice = input("\nEnter the number of the instance to connect to: ").strip()
        if raw_choice == "0":
            return "RETRY"
        choice_idx = int(raw_choice) - 1
        if 0 <= choice_idx < len(instances):
            return instances[choice_idx]["InstanceId"]
    except (ValueError, IndexError):
        return None
    return None

def choose_connection_type() -> Optional[ConnectionType]:
    print("\nSelect connection type:")
    print("[1] SSM Session (interactive shell)")
    print("[2] SSH over SSM (requires private key)")
    try:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        if choice == "1":
            return ConnectionType.SSM
        elif choice == "2":
            return ConnectionType.SSH
        else:
            return None
    except (ValueError, KeyboardInterrupt):
        return None

def prompt_for_ssh_details() -> Optional[Tuple[str, Path]]:
    key_path_str = input("\nEnter the path to your private key file: ").strip()
    if not key_path_str:
        print("Error: Private key path cannot be empty.", file=sys.stderr)
        return None
    key_path = Path(key_path_str.strip('"\'')).expanduser()
    if not key_path.is_file():
        print(f"Error: Private key file not found or is not a file at '{key_path}'", file=sys.stderr)
        return None
    if not validate_key_permissions(key_path):
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            return None
    username = input("Enter SSH username (e.g., ec2-user, ubuntu): ").strip()
    if not username:
        print("Error: Username cannot be empty.", file=sys.stderr)
        return None
    return username, key_path

def get_host_key_checking_choice() -> bool:
    choice = input(
        "Enable strict SSH host key checking? [y/N]: "
    ).strip().lower()
    return choice == "y"

def _prepare_subprocess_env(session: boto3.Session) -> Dict[str, str]:
    env = os.environ.copy()
    creds = get_session_credentials(session)
    env.update(creds)
    if session.region_name:
        env["AWS_REGION"] = session.region_name
        env["AWS_DEFAULT_REGION"] = session.region_name
    return env

def open_in_new_terminal(command: list, env: dict):
    if sys.platform.startswith("linux"):
        if shutil.which("gnome-terminal"):
            safe_command = " ".join(shlex.quote(arg) for arg in command) + "; exec bash"
            subprocess.Popen(["gnome-terminal", "--", "bash", "-c", safe_command], env=env)
        elif shutil.which("konsole"):
            subprocess.Popen(["konsole", "-e"] + command, env=env)
        elif shutil.which("xterm"):
            subprocess.Popen(["xterm", "-e"] + command, env=env)
        elif shutil.which("x-terminal-emulator"):
            subprocess.Popen(["x-terminal-emulator", "-e"] + command, env=env)
        else:
            print("No supported terminal emulator found, running in current window.", file=sys.stderr)
            subprocess.Popen(command, env=env)
    
    elif sys.platform == "darwin":
        safe_command = " ".join(shlex.quote(arg) for arg in command)
        applescript_safe_command = safe_command.replace('"', '\\"')
        subprocess.Popen([
            "osascript",
            "-e",
            f'tell application "Terminal" to do script "{applescript_safe_command}"'
        ], env=env)
    
    elif os.name == "nt":
        safe_command = subprocess.list2cmdline(command)
        
        if shutil.which("wt"):
            subprocess.Popen(["wt", "new-tab", "cmd", "/k", safe_command], env=env)
        elif shutil.which("powershell"):
            subprocess.Popen([
                "powershell", 
                "-Command", 
                f"Start-Process powershell -ArgumentList '-NoExit', '-Command', {repr(safe_command)}"
            ], env=env)
        else:
            # Fallback to cmd - use start with quoted command
            subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", safe_command], env=env)
    
    else:
        print("Unknown OS: running the command in the current terminal.")
        subprocess.Popen(command, env=env)

def start_ssm_session(instance_id: str, session: boto3.Session) -> int:
    env = _prepare_subprocess_env(session)
    cmd = ["aws", "ssm", "start-session", "--target", instance_id]
    try:
        print(f"\nOpening SSM session to {instance_id} in a new terminal window.")
        print("You can now open additional sessions by making another selection.\n")
        open_in_new_terminal(cmd, env)
        return 0
    except Exception as e:
        print(f"Error opening terminal: {e}", file=sys.stderr)
        print("Falling back to current terminal session.", file=sys.stderr)
        try:
            result = subprocess.run(cmd, env=env)
            return result.returncode
        except FileNotFoundError:
            print("Error: 'aws' command not found. Please ensure the AWS CLI is installed.", file=sys.stderr)
            return 1
        except KeyboardInterrupt:
            print("\nSSM session terminated.")
            return 0

def start_ssh_session(instance_id: str, username: str, key_path: Path, session: boto3.Session) -> int:
    env = _prepare_subprocess_env(session)
    proxy_command = (
        f"aws ssm start-session --target {instance_id} "
        f"--document-name AWS-StartSSHSession --parameters portNumber=%p"
    )
    strict_host_check = get_host_key_checking_choice()
    ssh_cmd = [
        "ssh", "-i", str(key_path.resolve()),
        "-o", f"ProxyCommand={proxy_command}",
        "-o", "IdentitiesOnly=yes"
    ]
    if not strict_host_check:
        ssh_cmd += [
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null"
        ]
    ssh_cmd.append(f"{username}@{instance_id}")
    try:
        print(f"\nOpening SSH over SSM session to {instance_id} as '{username}' in a new terminal window.")
        print("You can now open additional sessions by making another selection.\n")
        open_in_new_terminal(ssh_cmd, env)
        return 0
    except Exception as e:
        print(f"Error opening terminal: {e}", file=sys.stderr)
        print("Falling back to current terminal session.", file=sys.stderr)
        try:
            result = subprocess.run(ssh_cmd, env=env)
            return result.returncode
        except FileNotFoundError:
            print("Error: 'ssh' or 'aws' command not found. Ensure both are installed.", file=sys.stderr)
            return 1
        except KeyboardInterrupt:
            print("\nSSH session terminated.")
            return 0

def ask_continue_or_exit():
    choice = input("\nWould you like to open another session? [Y/n]: ").strip().lower()
    return choice != 'n' and choice != 'no'

def main():
    try:
        session = make_boto3_session()
        all_instances = list_running_instances(session)
    except (BotoCoreError, ClientError) as e:
        print(f"AWS API Error: Failed to list instances: {e}", file=sys.stderr)
        print("\nTip: Ensure your AWS credentials are configured correctly.", file=sys.stderr)
        sys.exit(1)
    
    if not all_instances:
        print(f"No running instances found in region '{session.region_name}'.")
        sys.exit(0)
    
    print(f"Found {len(all_instances)} running instances in region '{session.region_name}'.")
    
    while True:
        instance_id = None
        
        while not instance_id:
            keywords = prompt_for_keywords()
            filtered_instances = filter_instances_by_keywords(all_instances, keywords)
            
            if not filtered_instances:
                print("No instances found matching your keywords. Please try again.")
                continue
            
            selection = choose_instance(filtered_instances)
            if selection is None:
                print("Invalid selection. Please try again.", file=sys.stderr)
                continue
            elif selection == "RETRY":
                continue
            else:
                instance_id = selection
        
        connection_type = choose_connection_type()
        if not connection_type:
            print("Invalid connection type. Exiting.", file=sys.stderr)
            sys.exit(1)
        
        if connection_type == ConnectionType.SSM:
            start_ssm_session(instance_id, session)
        elif connection_type == ConnectionType.SSH:
            ssh_details = prompt_for_ssh_details()
            if ssh_details:
                username, key_path = ssh_details
                start_ssh_session(instance_id, username, key_path, session)
            else:
                print("Failed to get SSH details.")
                continue
        
        if not ask_continue_or_exit():
            break
    
    print("Goodbye!")

if __name__ == "__main__":
    main()