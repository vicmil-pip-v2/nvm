#!/usr/bin/env python3
import os
import subprocess
import sys

class LocalNodeReact:
    """
    Helper class to manage local Node (via nvm) and React project operations.
    """

    def __init__(self, project_dir=None, node_version="18.16.0", build_dir="build"):
        self.project_dir = os.path.abspath(project_dir or ".")
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.nvm_dir = os.path.join(self.script_dir, "nvm")  # nvm is always next to the script
        self.node_version = node_version
        self.build_dir = os.path.join(self.project_dir, build_dir)

        self.nvm_sh = os.path.join(self.nvm_dir, "nvm.sh")
        if not os.path.isfile(self.nvm_sh):
            raise FileNotFoundError(f"nvm.sh not found in {self.nvm_dir}")

    def _run_in_nvm_shell(self, commands):
        """
        Run commands in a shell with local nvm sourced and Node active.
        """
        full_command = f'''
        export NVM_DIR="{self.nvm_dir}"
        [ -s "{self.nvm_sh}" ] && . "{self.nvm_sh}"
        nvm install {self.node_version} --no-progress
        nvm use {self.node_version}
        cd "{self.project_dir}"
        {commands}
        '''
        return subprocess.run(full_command, shell=True, executable="/bin/bash")

    def install_dependencies(self):
        print("Installing npm dependencies...")
        result = self._run_in_nvm_shell("npm install")
        if result.returncode == 0:
            print("Dependencies installed successfully.")
        return result.returncode

    def build_project(self, output_dir=None):
        output_dir = output_dir or self.build_dir
        print(f"Building React project into: {output_dir}")
        env_cmd = f"npm run build -- --output-path {output_dir}"
        result = self._run_in_nvm_shell(env_cmd)
        if result.returncode == 0:
            print(f"Build completed successfully. Files are in {output_dir}")
        return result.returncode

    def start_dev_server(self):
        print("Starting React development server...")
        result = self._run_in_nvm_shell("npm start")
        return result.returncode

# -------------------------
# CLI interface for convenience
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
