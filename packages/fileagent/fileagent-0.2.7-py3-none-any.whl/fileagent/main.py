from pathlib import Path
from fileagent.managers.manager_api import ManagerAPI
from fileagent.managers.manager_arguments import ManagerArguments
from fileagent.managers.manager_files import ManagerFiles
from fileagent.managers.manager_snort import ManagerSnort


class FileAgent(ManagerAPI, ManagerArguments, ManagerFiles, ManagerSnort):
    def __init__(self, *args, **kwargs):
        # The arguments are handled by the Inheritance of the ManagerArguments class

        # The default values are assigned. The default values for now are inside the ManagerArgument class, per argument.
        self.default_values(**kwargs)

        # TODO: Add a universal config file

        # Initialize the ManagerFiles class
        # This entails more variables assigned, needed for the envisioned structured of the project
        ManagerFiles.__init__(self, *args, **kwargs)

        # Handle the api
        ManagerAPI.__init__(self, *args, **kwargs)

    def default_values(self, **kwargs):
        """
        Description:
            This function is meant to be run by the init function of the class
            Set the default values for the agent
            This function sets the default values for the agent. It checks if the arguments passed to the Class are None, and calls the arguments from argparse.
            If the arguments are not None, it assigns the values to the attribute of the class.
            If the directory is None, it sets the directory to the parent of the file.
            It also checks if the file is None, and raises a ValueError if it is.

        Args:
            port (int): Port to run the fastapi server on
            host (str): Host of the fastapi server
            directory (str): Path to the data directory
            file (str): Path to the file

        Raises:
            ValueError: File name is required
        """

        # This should be changed.
        if any(value is None for value in kwargs.values()) or len(kwargs) == 0:
            self.set_arguments()
            self.args = self.parser.parse_args()

            attributes = {
                "port": (kwargs.get("port"), self.args.port),
                "host": (kwargs.get("host"), self.args.host),
                "directory": (kwargs.get("directory"), self.args.directory),
                "file": (kwargs.get("file"), self.args.file),
            }
        else:
            attributes = {
                "port": (kwargs.get("port"), 8000),
                "host": (kwargs.get("host"), "0.0.0.0"),
                "directory": (kwargs.get("directory"), None),
                "file": (kwargs.get("file"), None),
            }

        self.assign_attributes(attributes)

        if self.file is None:
            raise ValueError("File name is required")

        if self.directory is None:
            self.directory = self.get_parent()


if __name__ == "__main__":

    agent = FileAgent()
    agent.run_uvicorn()
