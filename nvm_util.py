#!/usr/bin/env python3
import os
import subprocess
import sys
import pathlib
import json

def get_directory_path(__file__in, up_directories=0):
    return str(pathlib.Path(__file__in).parents[up_directories].resolve()).replace("\\", "/")

class LocalNodeReact:
    def __init__(self, parent_dir: str, build_dir: str, node_version="18.16.0", project_name:str = "my-app"):
        self.parent_dir = os.path.abspath(parent_dir)
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.nvm_dir = os.path.join(self.script_dir, "nvm")
        self.node_version = node_version
        self.build_dir = build_dir
        self.project_name = project_name
        self.project_path = os.path.join(parent_dir, project_name)

        self.nvm_sh = os.path.join(self.nvm_dir, "nvm.sh")
        if not os.path.isfile(self.nvm_sh):
            raise FileNotFoundError(f"nvm.sh not found in {self.nvm_dir}")

        self.package_json = os.path.join(self.project_path, "package.json")
        if os.path.isfile(self.package_json):
            self._detect_project_type()
        else:
            self.project_type = "unknown"  # No package.json yet


    def _detect_project_type(self):
        """Detect if the project is Vite or CRA."""
        with open(self.package_json, "r") as f:
            package_data = json.load(f)
        scripts = package_data.get("scripts", {})
        if "vite" in scripts.get("dev", "") or "vite" in scripts.get("build", ""):
            self.project_type = "vite"
        elif "react-scripts" in " ".join(scripts.values()):
            self.project_type = "cra"
        else:
            self.project_type = "unknown"

    def _run_in_nvm_shell(self, commands, dir_path: str):
        """
        Run commands in a shell with local nvm sourced and Node active.
        """
        full_command = f'''
        export NVM_DIR="{self.nvm_dir}"
        [ -s "{self.nvm_sh}" ] && . "{self.nvm_sh}"
        nvm install {self.node_version} --no-progress
        nvm use {self.node_version}
        cd "{dir_path}"
        {commands}
        '''
        return subprocess.run(full_command, shell=True, executable="/bin/bash")

    def install_dependencies(self):
        print("Installing npm dependencies...")
        result = self._run_in_nvm_shell("npm install", dir_path=self.parent_dir)
        if result.returncode == 0:
            print("Dependencies installed successfully.")
        return result.returncode

    def build_project(self):
        output_dir = self.build_dir
        print(f"Building React project into: {output_dir}")

        # Use correct build command based on project type
        if self.project_type == "vite":
            cmd = f'npm run build -- --outDir "{output_dir}"'
        elif self.project_type == "cra":
            cmd = f'REACT_APP_BUILD_PATH="{output_dir}" npm run build'
        else:
            cmd = f'npm run build'

        result = self._run_in_nvm_shell(cmd, dir_path=self.project_path)
        if result.returncode == 0:
            print(f"Build completed successfully. Files are in {output_dir}")
        return result.returncode

    def start_dev_server(self):
        print("Starting React development server...")

        # Use correct dev command
        if self.project_type == "vite":
            cmd = "npm run dev"
        elif self.project_type == "cra":
            cmd = "npm start"
        else:
            cmd = "npm start"

        result = self._run_in_nvm_shell(cmd, dir_path=self.project_path)
        return result.returncode
    
    def create_default_project(self, template="cra"):
        project_path = self.project_path
        if os.path.exists(project_path):
            raise FileExistsError(f"The directory {project_path} already exists.")

        if template.lower() == "cra":
            cmd = f"npx create-react-app {self.project_name}"
        elif template.lower() == "vite":
            cmd = f"npm create vite@latest {self.project_name} -- --template react"
        else:
            raise ValueError("Template must be 'cra' or 'vite'")

        print(f"Creating {template.upper()} project at {project_path}...")
        result = self._run_in_nvm_shell(cmd, dir_path=self.parent_dir)
        if result.returncode == 0:
            print(f"Project '{self.project_name}' created successfully.")

            # Update instance to point to new project
            self.project_dir = project_path
            self.package_json = os.path.join(self.project_path, "package.json")
            self._detect_project_type()
        return result.returncode

# -------------------------
# CLI interface
# -------------------------
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Local Node + React build helper")
    parser.add_argument("action", choices=["install", "build", "start"], help="Action to perform")
    parser.add_argument("--project-dir", default=".", help="Path to React project")
    parser.add_argument("--node-version", default="18.16.0", help="Node version to use")
    parser.add_argument("--output-dir", default="build", help="Output directory for build")
    args = parser.parse_args()

    helper = LocalNodeReact(
        project_dir=args.project_dir,
        node_version=args.node_version,
        build_dir=args.output_dir
    )

    if args.action == "install":
        sys.exit(helper.install_dependencies())
    elif args.action == "build":
        sys.exit(helper.build_project())
    elif args.action == "start":
        sys.exit(helper.start_dev_server())

if __name__ == "__main__":
    main()
