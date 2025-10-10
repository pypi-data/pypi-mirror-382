import shlex, subprocess

from muffinbite.commands.build import build
from muffinbite.commands.reset_config import reset_user_config
from muffinbite.commands.campaign import campaign_command
from muffinbite.commands.send import send_command
from muffinbite.commands.configure import configure_command
from muffinbite.commands.quit import quit
from muffinbite.management.session_watcher import start_watcher
from muffinbite.utils.hybridcompleter import HybridCompleter

from prompt_toolkit import PromptSession

def help():
    """
    Shows all the available commands and their uses
    """
    print("\nAvailable MuffinBite commands:\n")
    for name, func in COMMANDS.items():
        doc = func.__doc__.strip() if func.__doc__ else "No documentation available."
        print(f"    {name} - {doc}\n")
    print("Use !<command> for direct shell commands like `ls`, `clear`, `pwd`, etc.")

COMMANDS = {
    'build': build,
    'camp': campaign_command,
    'send': send_command,
    'config': configure_command,
    'exit': quit,
    'reset': reset_user_config,
    'help': help,
}

def run_cli():

    start_watcher()
    prompt = PromptSession(completer=HybridCompleter())

    while True:
        try:
            raw_input = prompt.prompt("bite> ").strip()

            if not raw_input:
                continue

            # much complex shell commands
            if raw_input.startswith('!'):
                print()
                shell_command = raw_input[1:]
                subprocess.run(shell_command, shell=True)
                continue

            parts = shlex.split(raw_input)
            cmd = parts[0]
            args = parts[1:]

            if cmd in COMMANDS:
                COMMANDS[cmd](*args)
            else:
                print(f"\nUnknown command: {cmd}\n")
                
        except KeyboardInterrupt:
            print("\nExiting.\n")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
