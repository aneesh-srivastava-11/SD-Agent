import os
import subprocess
from fuzzywuzzy import process

class AppLauncher:
    def __init__(self):
        self.start_menu_paths = [
            os.path.join(os.environ["ProgramData"], "Microsoft", "Windows", "Start Menu", "Programs"),
            os.path.join(os.environ["AppData"], "Microsoft", "Windows", "Start Menu", "Programs")
        ]
        self.apps = self._scan_apps()

    def _scan_apps(self):
        apps = {}
        for path in self.start_menu_paths:
            if not os.path.exists(path):
                continue
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(".lnk"):
                        app_name = file.replace(".lnk", "").lower()
                        apps[app_name] = os.path.join(root, file)
        return apps

    def launch(self, app_query):
        best_match, score = process.extractOne(app_query.lower(), self.apps.keys())
        if score > 50:
            app_path = self.apps[best_match]
            try:
                os.startfile(app_path)
                return f"Launching {best_match}."
            except Exception as e:
                return f"Error launching {best_match}: {e}"
        return f"Could not find an app matching '{app_query}'."
