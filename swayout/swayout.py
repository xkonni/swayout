from i3ipc import Connection
import json
import time
from xdg import XDG_CONFIG_HOME, XDG_CACHE_HOME
import readchar
import time
import sys

CONFIG_FILE = f"{XDG_CONFIG_HOME}/swayout.json"
CONFIG_DEFAULT = {"outputs": [], "presets": []}
swayout = None


class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class SwayOut:
    def __init__(self, config):
        self.i3 = Connection()
        self.config = config
        # runtime
        self.outputs = self.i3.get_outputs()
        self.output_cmd = {
            "cmd": "f'self.set_mode_idx({x})'",
            "help": "f'select output {x}'",
        }
        self.output_sub_cmds = {
            "c": {"cmd": "f'self.set_output({x},\"configure\")'", "help": "configure output"},
            "e": {"cmd": "f'self.set_output({x},\"enable\")'", "help": "enable output"},
            "d": {"cmd": "f'self.set_output({x},\"disable\")'", "help": "disable output"},
            "r": {"cmd": "f'self.set_output({x},\"reconfigure\")'", "help": "reconfigure output"},
            "s": {"cmd": "f'self.set_output({x},\"show\")'", "help": "show output"}
        }
        self.preset_cmd = {
            "cmd": "f'self.set_preset({x})'", "help": "f'switch to preset {x}'"}
        self.commands = {
            "any": {
                "q": {"cmd": "sys.exit()", "help": "quit swayout"},
                "m": {"cmd": "self.set_mode('main')", "help": "main menu"},
                "?": {"cmd": "self.show('help')", "help": "show help"},
                "h": {"cmd": "self.show('help')", "help": "show help"},
                "d": {"cmd": "print(json.dumps(self.commands, indent=4))", "help": "dump commands"},
            },
            "main": {
                "o": {"cmd": "self.set_mode('output')", "help": "output configuration"},
                "p": {"cmd": "self.set_mode('preset')", "help": "preset configuration"},
                "s": {"cmd": "self.set_mode('show')", "help": "show outputs/presets"},
            },
            "output": {},
            "preset": {},
            "show": {
                "o": {"cmd": "self.show('outputs')", "help": "show outputs"},
                "p": {"cmd": "self.show('presets')", "help": "show presets"},
            }
        }
        self.mode = {}
        self.set_mode("main")
        self.update_commands()

    def set_mode(self, mode, idx=None):
        self.mode["mode"] = mode
        self.mode["idx"] = None

    def set_mode_idx(self, idx):
        self.mode["idx"] = str(idx)

    def prompt(self):
        while True:
            mode = self.mode["mode"]
            idx = self.mode.get("idx")
            m = f"{mode}{':' if idx is not None else ''}{idx if idx is not None else ''}"
            print(f"{bcolors.BOLD}{bcolors.BLUE}::swayout:: {bcolors.CYAN}{m:>8}{bcolors.ENDC}{bcolors.BOLD} > {bcolors.ENDC}", end="", flush=True)
            sel = readchar.readchar().lower()
            print(sel)
            # quit
            if sel in ["q"]:
                print(f"{bcolors.BOLD}{bcolors.HEADER}> quit")
                break
            # any
            elif sel in self.commands["any"].keys():
                cmds = self.commands["any"]
                cmd = cmds[sel]["cmd"]
                # print(f"{cmd = }")
                exec(cmd)
                continue
            else:
                if mode in self.commands.keys():
                    # idx is not set
                    if idx is None:
                        cmds = self.commands[mode]
                        if sel in cmds.keys():
                            if "cmd" in cmds[sel]:
                                cmd = cmds[sel]["cmd"]
                                exec(cmd)
                                continue
                    # idx is set
                    else:
                        cmds = self.commands[mode][idx]["sub_cmds"]
                        if sel in cmds.keys():
                            if "cmd" in cmds[sel]:
                                cmd = cmds[sel]["cmd"]
                                exec(cmd)
                                continue
            print(f"{bcolors.WARNING}> invalid input {sel}, press h/? for help")

    def update_commands(self):
        self.commands["output"] = {
            str(x): {
                "cmd": eval(self.output_cmd["cmd"]),
                "help": eval(self.output_cmd["help"]),
                "sub_cmds": {}
            } for x in range(1, len(self.config["outputs"])+1)
        }

        for x in self.commands["output"]:
            self.commands["output"][x]["sub_cmds"] = {
                k: {
                    "cmd": eval(self.output_sub_cmds[k]["cmd"], {'k': f'{k}', 'x': x}),
                    "help": self.output_sub_cmds[k]["help"]
                } for k in self.output_sub_cmds
            }

        self.commands["preset"] = {
            str(x): {"cmd": eval(self.preset_cmd["cmd"]), "help": eval(self.preset_cmd["help"])} for x in range(1, len(self.config["presets"])+1)
        }

    def output_enable(self, idx):
        self.set_output(idx, "enable")

    def set_output(self, idx, action, quiet=False):
        output = self.outputs[int(idx)-1]
        if not quiet:
            print(f"{bcolors.HEADER}> output {output.name} {action}{bcolors.GREEN}")

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
        elif action == "reconfigure":
            self.set_output(idx, "disable", quiet=True)
            print("  - sleep 5")
            time.sleep(5)
            self.set_output(idx, "enable", quiet=True)
            return
        elif action == "show":
            self.show("outputs")
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
        print(f"{bcolors.BOLD}{bcolors.HEADER}> show {item}{bcolors.ENDC}")
        list = {}
        idx = 0
        if item == "help":
            # any, main, ...
            for k in self.commands.keys():
                print(f"{bcolors.CYAN}mode: {k}{bcolors.GREEN}")
                c_k = self.commands[k]
                for k2 in c_k.keys():
                    c_k2 = c_k[k2]
                    h2 = c_k2["help"]
                    if k2.isdigit():
                        if k2 == "1":
                            h2 = h2.replace(f" {k2}", "")
                            print(f"    - #: {h2}")
                            if "sub_cmds" in c_k2:
                                print(f"{bcolors.CYAN}  mode: {k}-#{bcolors.GREEN}")
                                for k3 in c_k2["sub_cmds"]:
                                    h3 = c_k2["sub_cmds"][k3]["help"]
                                    print(f"    - {k3}: {h3}")

                    else:
                        print(f"  - {k2}: {h2}")

                    # if k2.isdigit():
                    #     if k2 == "1":
                    #         if c_k2 is None:
                    #             print(f"  - {k} #")
                    #             continue
                    #         else:
                    #             print(
                    #                 f"  - {k} # [{'|'.join(k3 for k3 in c_k2.keys())}]")
                    #             continue
                    #     else:
                    #         continue
                    # else:
                    #     print(f"  - {k2}: {h2}")
        elif item == "outputs":
            self.outputs = self.i3.get_outputs()
            # self.update_output_validator()
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


def main():
    global swayout
    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
    except Exception as ex:
        print(f"Exception Type:{type(ex).__name__}, args:{ex.args}")
        print("running with empty config")
        config = CONFIG_DEFAULT

    swayout = SwayOut(config)
    swayout.show("outputs")
    swayout.show("presets")
    swayout.prompt()


if __name__ == "__main__":
    main()
