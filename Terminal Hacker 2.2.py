import subprocess
import os
import sys
import json



COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "reset": "\033[0m"
}

CONFIG_PATH = os.path.join("C:/", "Users", os.getlogin(), ".terminalhacker", ".terminalhacker")

def ensure_config_directory():
    directory = os.path.dirname(CONFIG_PATH)
    if not os.path.exists(directory):
        os.makedirs(directory)

def read_config():
    if not os.path.isfile(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def write_config(config):
    ensure_config_directory()
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

def cmdloop(prompt=f"{COLORS['red']}TH{COLORS['reset']}", mode="none"):
    current_dir = os.getcwd()
    while True:
        command = input(f"{prompt} {current_dir}> ").strip().lower()

        if command in ['exit', 'quit']:
            break
        elif command.startswith("cd "):
            try:
                os.chdir(command[3:].strip())
                current_dir = os.getcwd()
            except Exception as e:
                print(f"Error: {e}")
        elif command == "doiuseth":
            print(f"You are using {COLORS['red']}Terminal Hacker{COLORS['reset']} right now")
        elif command == "normalize":
            prompt = "PS"
        elif command == "setup":
            print("Deleting .terminalhacker")
            if os.path.exists(CONFIG_PATH):
                os.remove(CONFIG_PATH)
            setup_terminal_hacker()
        elif command == "rename":
            new_prompt = input("New prompt: ")
            color = input("Color (red, green, yellow, blue, magenta, cyan, white): ").lower()
            prompt = f"{COLORS.get(color, COLORS['red'])}{new_prompt}{COLORS['reset']}"
        elif command == "get psexec":
            with open(CONFIG_PATH, "r") as config:
                data = json.load(config)
                psexec_path = data.get("psexec_path", os.path.join(os.path.dirname(CONFIG_PATH), "PsExec.exe"))
                if os.path.isfile(psexec_path):
                    print(f"{COLORS['green']}Psexec is available at {psexec_path}{COLORS['reset']}")
                else:
                    print(f"{COLORS['yellow']}Before downloading PSExec, you need to agree to the Sysinternals terms of service.{COLORS['reset']}")
                    print("Terms of Service: https://docs.microsoft.com/en-us/sysinternals/license-terms")
                    agree = input("Do you agree to the terms of service? (yes/no): ").strip().lower()
                    if agree != "yes":
                        print(f"{COLORS['red']}You must agree to the terms to download PSExec.{COLORS['reset']}")
                        return

                    print(f"{COLORS['red']}Downloading PSExec{COLORS['reset']}")
                    pstools_zip_path = os.path.join(os.path.dirname(CONFIG_PATH), "PSTools.zip")
                    pstools_extract_path = os.path.join(os.path.dirname(CONFIG_PATH), "PSTools")

                    subprocess.run([
                        "powershell", "-Command", 
                        f"Invoke-WebRequest -Uri 'https://download.sysinternals.com/files/PSTools.zip' -OutFile '{pstools_zip_path}'"
                    ])
                    subprocess.run([
                        "powershell", "-Command", 
                        f"Expand-Archive -Path '{pstools_zip_path}' -DestinationPath '{pstools_extract_path}'"
                    ])
                    subprocess.run([
                        "powershell", "-Command", 
                        f"Move-Item -Path '{os.path.join(pstools_extract_path, 'PsExec.exe')}' -Destination '{psexec_path}'"
                    ])
                    subprocess.run([
                        "powershell", "-Command", f"Remove-Item -Path '{pstools_zip_path}'"
                    ])
                    subprocess.run([
                        "powershell", "-Command", f"Remove-Item -Path '{pstools_extract_path}' -Recurse"
                    ])

                    data["psexec_path"] = psexec_path
                    with open(CONFIG_PATH, "w") as config:
                        json.dump(data, config, indent=4)
        elif command.startswith("use psexec"):
            with open(CONFIG_PATH, "r") as config:
                data = json.load(config)
                psexec_path = data.get("psexec_path", os.path.join(os.path.dirname(CONFIG_PATH), "PsExec.exe"))
                if os.path.isfile(psexec_path):
                    arguments = command[len("use psexec"):].strip()
                    subprocess.run([psexec_path] + arguments.split())
                else:
                    print(f"{COLORS['red']}PSExec is not available. Use 'get psexec' to download it.{COLORS['reset']}")
        elif command.startswith("install"):
            arguments = command[len("install"):].strip()
            temp_flag = "--temp" in arguments
            if temp_flag:
                arguments = arguments.replace("--temp", "").strip()

            if not arguments:
                print(f"{COLORS['red']}ERROR: Please provide a file path or URL to install.{COLORS['reset']}")
                return

            if arguments.startswith("http://") or arguments.startswith("https://"):
                print(f"{COLORS['yellow']}Downloading and installing from URL: {arguments}{COLORS['reset']}")
                file_name = arguments.split("/")[-1]
                download_path = os.path.join(os.path.dirname(CONFIG_PATH), file_name)
                subprocess.run([
                    "powershell", "-Command", 
                    f"Invoke-WebRequest -Uri '{arguments}' -OutFile '{download_path}'"
                ])
                subprocess.run(download_path, shell=True)
                if temp_flag:
                    os.remove(download_path)
                    print(f"{COLORS['cyan']}Temporary file deleted: {download_path}{COLORS['reset']}")
            elif os.path.isfile(arguments):
                print(f"{COLORS['yellow']}Installing from file: {arguments}{COLORS['reset']}")
                subprocess.run(arguments, shell=True)
                if temp_flag:
                    os.remove(arguments)
                    print(f"{COLORS['cyan']}Temporary file deleted: {arguments}{COLORS['reset']}")
            elif os.path.isfile(arguments):
                print(f"{COLORS['yellow']}Installing from file: {arguments}{COLORS['reset']}")
                subprocess.run(arguments, shell=True)
            else:
                print(f"{COLORS['red']}ERROR: Invalid file path or URL.{COLORS['reset']}")

        elif command == "mode":
            print("+----------------------+-------------------------------------------------+")
            print("| Mode                 | Description                                     |")
            print("+----------------------+-------------------------------------------------+")
            print("| os.system            | Command from the Python library OS              |")
            print("| powershell           | Runs commands with PowerShell                   |")
            print("| both                 | Uses os.system and PowerShell                   |")
            print("+----------------------+-------------------------------------------------+")
            mode_input = input("Which mode do you want to use? ").strip().lower()
            if mode_input in ["os.system", "powershell", "both"]:
                mode = mode_input
                prompt = f"{COLORS.get(mode_input.split('.')[0], COLORS['red'])}{mode_input.upper()}{COLORS['reset']}"
                config = read_config() or {}
                config['mode'] = mode_input
                write_config(config)
            else:
                print(f"Invalid mode: {mode_input}")
        else:
            if mode == "powershell":
                subprocess.run(["powershell", "-Command", command])
            elif mode == "os.system":
                os.system(command)
            elif mode == "both":
                print(f"{COLORS['red']}Powershell Response{COLORS['reset']}")
                subprocess.run(["powershell", "-Command", command])
                print(f"{COLORS['red']}os.system Response{COLORS['reset']}")
                os.system(command)
            else:
                print(f"{COLORS['red']}ERROR: Non-shell mode selected{COLORS['reset']}")

def setup_terminal_hacker():
    config = read_config()
    if not config:
        print("Hey " + os.getlogin() + ", Welcome to Terminal Hacker. It seems like you're using Terminal Hacker for the first time, so let's configure it.")
        print("+--------------------------+---------------------------------------------+")
        print("| Mode                     | Description                                 |")
        print("+--------------------------+---------------------------------------------+")
        print("| os.system                | Command from the Python library OS          |")
        print(f"| powershell {COLORS['green']}(recommended){COLORS['reset']} | Runs commands with PowerShell               |")
        print("| both                     | Uses os.system and PowerShell               |")
        print("+--------------------------+---------------------------------------------+")
        mode_input = input("Which mode do you want to use? ").strip().lower()
        if mode_input in ["os.system", "powershell", "both"]:
            config = {'mode': mode_input}
            write_config(config)
            cmdloop(f"{COLORS.get(mode_input.split('.')[0], COLORS['red'])}{mode_input.upper()}{COLORS['reset']}", mode_input)
        else:
            print(f"Invalid mode: {mode_input}")
    else:
        cmdloop(f"{COLORS.get(config['mode'].split('.')[0], COLORS['red'])}{config['mode'].upper()}{COLORS['reset']}", config['mode'])

def print_welcome_message():
    print(f"Welcome to {COLORS['red']}Terminal Hacker{COLORS['reset']}\nBy Finn\n")
    print('Commands: "exit", "quit", "doiuseth", "normalize", "rename", "mode"')

if __name__ == "__main__":
    print_welcome_message()
    default_prompt = "PS" if len(sys.argv) > 1 and sys.argv[1].lower() == "normal" else f"{COLORS['red']}TH{COLORS['reset']}"
    setup_terminal_hacker()
