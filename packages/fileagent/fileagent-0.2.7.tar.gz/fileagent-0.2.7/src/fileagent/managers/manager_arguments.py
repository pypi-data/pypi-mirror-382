import argparse


class ManagerArguments:
    def set_arguments(self):
        """
        Description:
            Set the arguments for the agent, and save the important information as attributes of the class
        """

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            "-p",
            "--port",
            type=int,
            default=8000,
            help="Port to run the fastapi server on",
        )

        self.parser.add_argument(
            "--host",
            type=str,
            default="0.0.0.0",
            help="Host of the fastapi server",
        )

        self.parser.add_argument(
            "-f",
            "--file",
            type=str,
            default=None,
            help="Path to the file",
        )

        self.parser.add_argument(
            "-d",
            "--directory",
            type=str,
            default=None,
            help="Path to the data directory",
        )

    def assign_attributes(self, attributes):
        """
        Assign attributes dynamically based on provided arguments or defaults.

        Args:
            attributes (dict): A dictionary where keys are attribute names and values are tuples
                            of (provided_value, default_value).
        """
        for attr, (provided_value, default_value) in attributes.items():
            setattr(
                self,
                attr,
                provided_value if provided_value is not None else default_value,
            )
