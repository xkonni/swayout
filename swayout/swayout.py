from i3ipc import Connection
import json
import time
from xdg import XDG_CONFIG_HOME, XDG_CACHE_HOME
import time
# prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.completion import FuzzyCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import Validator, ValidationError

CONFIG_FILE = f"{XDG_CONFIG_HOME}/swayout.json"
swayout = None


class SwayOut:
    def __init__(self, config):
        self.i3 = Connection()
        self.config = config
        # runtime
        self.output_cmd = {"enable": None, "configure": None, "disable": None, "reenable": None}
        self.preset_cmd = None
        self.outputs = self.i3.get_outputs()
        self.commands = {
            "?": None,
            "output": {},
            "preset": {},
            "show": {"outputs": None, "presets": None},
            "quit": None
        }
        self.update_outputs()
        self.update_presets()

    def update_outputs(self):
        self.commands["output"] = {
            str(x+1): self.output_cmd for x in range(len(self.outputs))}

    def update_presets(self):
        self.commands["preset"] = {
            str(x+1): self.preset_cmd for x in range(len(self.config["presets"]))}

    def set_output(self, idx, action, quiet=False):
        output = self.outputs[int(idx)-1]
        if not quiet:
            print(f">> output {output.name}")
        if action == "configure":
            cmd = f"output {output.name}"
            config_output = next(
                filter(lambda x: x["serial"] == output.serial, self.config["outputs"]))
            options = config_output.get("options", [])
            for key in options:
                cmd = cmd + f" {key} {options[key]}"
        elif action == "disable":
            cmd = f"output {output.name} disable"
        elif action == "enable":
            cmd = f"output {output.name} enable"
        elif action == "reenable":
            self.set_output(idx, "disable", quiet=True)
            print("  - sleep 5")
            time.sleep(5)
            self.set_output(idx, "enable", quiet=True)
            return
        print(f"  - {cmd}")
        self.i3.command(cmd)

    def set_preset(self, idx):
        outputs = self.config["outputs"]
        preset = self.config["presets"][int(idx)-1]
        if not preset:
            print(f"preset {idx} not defined")
            return False

        print(f">> preset: {preset['name']}")
        i3_outputs = self.i3.get_outputs()
        preset_outputs = preset["outputs"]

        # disable active: False
        for p in filter(lambda x: not x["active"], preset_outputs):
            output = next(
                filter(lambda x: x["name"] == p["name"], outputs))
            i3_output = next(filter(lambda x: x.serial ==
                             output["serial"], i3_outputs))
            cmd = f"output {i3_output.name} disable"
            print(f"  - {cmd}")
            self.i3.command(cmd)

        # enable active: True
        for p in filter(lambda x: x["active"], preset_outputs):
            output = next(
                filter(lambda x: x["name"] == p["name"], outputs))
            i3_output = next(filter(lambda x: x.serial ==
                             output["serial"], i3_outputs))
            cmd = f"output {i3_output.name} enable"
            # work on copy of dict
            options = dict(output["options"])
            options.update(p["options"])
            for key in options:
                cmd = cmd + f" {key} {options[key]}"
            print(f"  - {cmd}")
            self.i3.command(cmd)

    def show(self, item):
        print(f"swayout: {item}")
        list = {}
        idx = 0
        if item == "help":
            print("available commands:")
            for k in self.commands.keys():
                c_k = self.commands[k]
                if c_k is None:
                    print(f"  - {k}")
                    continue
                for k2 in c_k.keys():
                    if k2 is None:
                        break
                    c_k2 = c_k[k2]
                    if k2.isdigit():
                        if k2 == "1":
                            if c_k2 is None:
                                print(f"  - {k} #")
                                continue
                            else:
                                print(f"  - {k} # [{'|'.join(k3 for k3 in c_k2.keys())}]")
                                continue
                        else:
                            continue
                    else:
                        print(f"  - {k} {k2}")
        elif item == "outputs":
            self.outputs = self.i3.get_outputs()
            self.update_outputs()
            for output in self.outputs:
                idx += 1
                if output.active:
                    state = "[active]"
                    mode = f"{output.current_mode.width}x{output.current_mode.height}"
                else:
                    state = "[inactive]"
                    mode = "-"
                print(
                    f"  {idx}: {output.name:5s} {state:10s} {mode:10s} {output.make:20s} {output.model:10s} {output.serial}")
        elif item == "presets":
            for preset_name in [x["name"] for x in self.config["presets"]]:
                idx += 1
                print(f"  {idx}: {preset_name}")
        print("")


class CommandValidator(Validator):
    def validate(self, document):
        global swayout
        text = document.text
        cmds = swayout.commands
        words = text.split(" ")
        pos = 0
        for word in words:
            if len(word) == 0:
                raise ValidationError(
                    message="enter command or press tab", cursor_position=0)
            elif word in cmds:
                if isinstance(cmds, dict):
                    cmds = cmds[word]
                    if cmds is None or cmds == " ":
                        return
                    else:
                        pos = text.find(word)+len(word)
            else:
                pos = text.find(word)+len(word)
                break
        raise ValidationError(
            message=f"wrong argument \"{word}\" in command \"{text}\"", cursor_position=pos)


def main():
    global swayout
    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
    except Exception as ex:
        print(f"Exception Type:{type(ex).__name__}, args:{ex.args}")
        return False
    swayout = SwayOut(config)
    bindings = KeyBindings()
    @bindings.add("c-q")
    def _(event):
        event.app.exit()
    @bindings.add(" ")
    def _(event):
        buff = event.app.current_buffer
        if buff.complete_state:
            buff.complete_next()
            buff.insert_text(" ")
        else:
            buff.start_completion(select_first=False)
            buff.insert_text(" ")

    swayout.show("outputs")
    swayout.show("presets")


    def bottom_toolbar():
        return HTML(f"<style bg='#268bd2'><b> :: swayout</b></style>")
    style = Style.from_dict({
        'completion-menu.completion': 'bg:#808080 fg:#ffffff',
        'completion-menu.completion.current': 'bg:#404040 #268bd2',
        'scrollbar.background': 'bg:#606060',
        'scrollbar.button': 'bg:#202020',
    })
    while True:
        try:
            command_completer = NestedCompleter.from_nested_dict(
                swayout.commands)
            fuzzy_command_completer = FuzzyCompleter(command_completer)
            session = PromptSession(
                completer=fuzzy_command_completer, complete_while_typing=True,
                history=FileHistory(f"{XDG_CACHE_HOME}/swayout"),
                style=style,
                validator=CommandValidator(), validate_while_typing=False)
            cmd = session.prompt("swayout > ", bottom_toolbar=bottom_toolbar, key_bindings=bindings)
        except KeyboardInterrupt:
            continue  # Control-C pressed. Try again.
        except EOFError:
            break  # Control-D pressed.
        if cmd is None:
            break
        cmd = cmd.split(" ")
        if cmd[0] == "?":
            swayout.show("help")
        # output
        elif cmd[0] == "output":
            swayout.set_output(cmd[1], cmd[2])
        # preset
        elif cmd[0] == "preset":
            swayout.set_preset(cmd[1])
        # show
        elif cmd[0] == "show":
            # if cmd[1] == "outputs":
            swayout.show(cmd[1])
        elif cmd[0] == "quit":
            break
        else:
            print(f"unknown command \"{cmd}\"")


if __name__ == "__main__":
    main()
