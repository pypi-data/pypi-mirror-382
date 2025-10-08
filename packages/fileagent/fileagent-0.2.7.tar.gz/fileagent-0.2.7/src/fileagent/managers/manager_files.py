from pathlib import Path
import datetime
import inspect
import json


class ManagerFiles:
    def __init__(self, *args, **kwargs):
        """
        Description:
            -----------

            This class manages file operations related to the rules and history files.
            It initializes paths for the rules file, backup directory, and history file.
            It also provides a method to create backups of the rules file.
        """
        # Initialize some paths that are deemed important

        self.data_backup_path = Path(self.directory, "backup")
        if not self.data_backup_path.exists():
            self.data_backup_path.mkdir(parents=True, exist_ok=True)

        self.rules_file = Path(self.directory, self.file)
        self.get_history_file(kwargs.get("history_file", None))

    def file_backup(self):
        """
        Description:
            -----------

            Creates a backup of the rules file in the specified backup directory.
            This method ensures that the backup directory exists, then creates a backup
            of the `self.rules_file` by copying its contents to a new file in the backup
            directory. The backup file is named using the original file's stem and the
            current timestamp in the format 'YYYY-MM-DD_HH-MM-SS.bak'.
            Steps:
            1. Ensures the backup directory (`self.data_backup_path`) exists.
            2. Constructs the backup file path using the original file's stem and a timestamp.
            3. Reads the contents of the `self.rules_file`.
            4. Writes the contents to the newly created backup file.
            Raises:
                FileNotFoundError: If `self.rules_file` does not exist.
                IOError: If there is an issue reading from or writing to the files.
            Note:
                - The method assumes `self.rules_file` and `self.data_backup_path` are
                valid `Path` objects.
                - The timestamp ensures that each backup file has a unique name.

        Raises:
            FileNotFoundError: If `self.rules_file` does not exist.
            IOError: If there is an issue reading from or writing to the files.

        """

        print(f"Creating backup in {self.data_backup_path}")
        # Create the backup file path
        backup_file = Path(
            self.data_backup_path,
            f"{self.rules_file.stem}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.bak",
        )

        with open(self.rules_file, "r") as file:
            rules = file.readlines()

        with open(backup_file, "w") as file:
            file.writelines(rules)

    def get_parent(self):
        """
        Description:
            Retrieves the absolute path of the parent directory of the file
            that is at the bottom of the current call stack.
            This method uses the `inspect` module to access the call stack
            and determines the file path of the last frame in the stack.
            It then resolves and returns the parent directory of that file.

        Returns:
            pathlib.Path: The absolute path of the parent directory of the file
            at the bottom of the call stack.
        """

        file_called_frame = inspect.stack()
        file_called_path = Path(file_called_frame[-1].filename)
        return Path(file_called_path).parent.resolve()

    def get_history_file(self, filepath: str = None) -> Path:
        """
        Description:
            this function will get path of the file that contains the history of the notifications.
        Returns:
            pathlib.Path: The absolute path of the history directory.
        """

        # Doesn't contain any checks for filename or filepath. For now
        if filepath:
            self.history_file = Path(filepath)
            return self.history_file

        self.history_file = Path(self.directory, "history.json")
        if not self.history_file.exists():
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            self.history_file.touch()
            with open(self.history_file, "w") as file:
                json.dump({"history": []}, file)
        return self.history_file

    def get_file_content(self, filepath, filetype: str = None):

        with open(filepath, "r") as file:
            content = file.read()
        if filetype == "json":
            return json.loads(content)
        elif filetype == "txt":
            return content.splitlines()
        else:
            return content

    def save_file_content(self, filepath, content, filetype: str = None):
        """
        Description:
            Saves the content of a file to the specified filepath.
            If the filetype is 'json', it saves the content as a JSON string.
            If the filetype is 'txt', it saves the content as plain text.
            If no filetype is specified, it saves the content as a plain text file.

        Args:
            filepath (str): The path where the file should be saved.
            filetype (str, optional): The type of the file ('json', 'txt'). Defaults to None.

        Returns:
            None
        """

        with open(filepath, "w") as file:
            if filetype == "json":
                json.dump(content, file)
            elif filetype == "txt":
                file.write("\n".join(content))
            else:
                file.write(content)

    def save_file_json(self, filepath, content):
        """
        Description:
            Saves the content of a file to the specified filepath in JSON format.
            This method reads the content from `self.content`, which should be a dictionary,
            and writes it to the specified file as a JSON string.

        Args:
            filepath (str): The path where the file should be saved.

        Returns:
            None
        """

        original = self.get_file_content(filepath, "json")
        original["history"].append(content)

        self.save_file_content(filepath, original, "json")

    def save_history(self, content):
        history = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": content,
        }
        self.save_file_json(self.history_file, history)
