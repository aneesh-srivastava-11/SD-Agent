import subprocess

class TerminalTools:
    def run_command(self, command):
        try:
            # Security verification: block dangerous Windows command tokens
            cmd_clean = command.strip().lower()
            blocked_words = {"del", "rmdir", "rd", "format", "erase", "shutdown", "sfc", "dism", "reg", "attrib", "mkfs"}
            
            # Normalize split chars to scan all chained commands
            tokens = cmd_clean.replace("&&", " ").replace("||", " ").replace(";", " ").replace("|", " ").replace("&", " ").split()
            
            if any(token in blocked_words for token in tokens):
                return "Security Alert: Execution of dangerous commands is blocked for system safety."
                
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout if result.stdout else "Command executed successfully."
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Failed to run command: {e}"

