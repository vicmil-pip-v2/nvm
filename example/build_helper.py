import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from nvm_util import LocalNodeReact, get_directory_path

react_node = LocalNodeReact(project_dir=get_directory_path(__file__), build_dir=get_directory_path(__file__) + "/build")

react_node.install_dependencies()
react_node.create_default_project()
react_node.build_project()
react_node.start_dev_server()