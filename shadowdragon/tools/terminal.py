import subprocess

class TerminalTools:
    def run_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout if result.stdout else "Command executed successfully."
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Failed to run command: {e}"
