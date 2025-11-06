from ai_wayang_single.config.settings import LOG_CONFIG
from datetime import datetime
import os
import json

class Logger:
    """
    For logging, inspecting and debugging plans.
    Mostly to keep track and monitor on Agents progress

    """

    def __init__(self):
        self.folder_path = LOG_CONFIG.get("log_folder")
        self.logfile = self._create_logfile() or None


    def add_message(self, title: str, msg):
        """
        Append a new log or message to the logfile

        Args:
            title (str): The title of the message to be logged
            msg (str): The message to log

        """

        # Return if no folder path
        if not self.folder_path:
            return None
        
        # Make timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Get log
        with open(self.logfile, "r", encoding="utf-8") as f:
            logs = json.load(f)

        # Write to log
        with open(self.logfile, "w", encoding="utf-8") as f:
            # Size for ID
            size = len(logs)

            # Create new log
            new_log = {
                "id": size + 1,
                "title": title,
                "timestamp": timestamp,
                "log": msg
            }

            # Add new log
            logs.append(new_log)

            # (Over)write the log
            json.dump(logs, f, indent=4)
            

    def _create_logfile(self) -> str:
        """
        Helper function to create a new log file in JSON

        Returns:
            (str): Filepath of created log file

        """

        # Check if folder exists
        if not self.folder_path:
            return None
        
        # Check or create log folder if doesn't exist
        os.makedirs(self.folder_path, exist_ok=True)

        # Create path for log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"log_{timestamp}.json"
        filepath = os.path.join(self.folder_path, filename)

        # Create file
        with open(filepath, "w", encoding="utf-8", ) as f:
            json.dump([], f, indent=4)
            
        return filepath
    
            







