import sys
import pathlib
import os
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from nvm_util import LocalNodeReact, get_directory_path

react_node = LocalNodeReact(parent_dir=get_directory_path(__file__), project_name="my-app")

react_node.install_dependencies()

if not os.path.exists(get_directory_path(__file__) + "/" + react_node.project_name):
    react_node.create_default_project()

react_node.build_project()
react_node.start_dev_server()