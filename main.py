from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from descriptor import ALL_INSTRUCTIONS
from control import Runner
from custom_exception import Unconnect

runner = Runner()
instructions = ALL_INSTRUCTIONS()

def commandLoop():
    session = PromptSession()
    instruction_completer = WordCompleter(instructions.keys())
    prompt = "> "
    while True:
        try:
            text = session.prompt(prompt, completer=instruction_completer)
            if not runner.run(text):
                # command execute error
                continue
            if text.startswith("connect"):
                prompt = "% "
            elif text.startswith("disconnect"):
                prompt = "> "
        except Unconnect as e:
            print(e)
            continue
        except KeyboardInterrupt:
            continue    # Control - C pressed. Try again.
        except EOFError:
            runner.run("disconnect")
            break    # Control - D pressed.

if __name__ == "__main__":
    commandLoop()
