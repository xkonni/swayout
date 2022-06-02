from i3ipc import Connection
import json
import readchar
import time


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class SwayOut:
    def __init__(self, config):
        self.config = config
        self.i3 = Connection()
        # runtime
        self.outputs = self.i3.get_outputs()
        self.output_cmds = {
            "#": {"cmd": "f'self.set_mode(\"output\",{x})'", "help": "f'select output {x}'"},
            "s": {"cmd": "self.show('outputs')", "help": "show outputs"}
        }
        self.output_sub_cmds = {
            "c": {"cmd": "f'self.set_output({x},\"configure\")'", "help": "configure output"},
            "e": {"cmd": "f'self.set_output({x},\"enable\")'", "help": "enable output"},
            "d": {"cmd": "f'self.set_output({x},\"disable\")'", "help": "disable output"},
            "o": {"cmd": "f'self.set_mode(\"output\")'", "help": "output configuration"},
            "r": {"cmd": "f'self.set_output({x},\"reconfigure\")'", "help": "reconfigure output"},
            "s": {"cmd": "f'self.show(\"outputs\", {x})'", "help": "show output"},
        }
        self.preset_cmds = {
            "#": {"cmd": "f'self.set_mode(\"preset\",{x})'", "help": "f'select preset {x}'"},
            "s": {"cmd": "self.show('presets')", "help": "show presets"}
        }
        self.preset_sub_cmds = {
            "e": {"cmd": "f'self.set_preset({x},\"enable\")'", "help": "enable preset"},
            "r": {"cmd": "f'self.set_preset({x},\"reconfigure\")'", "help": "reconfigure preset"},
            "s": {"cmd": "f'self.show(\"presets\", {x})'", "help": "show preset"},
        }
        self.commands = {
            "main": {
                "q": {"cmd": "sys.exit()", "help": "quit swayout"},
                "m": {"cmd": "self.set_mode('main')", "help": "main menu"},
                "?": {"cmd": "self.show('help')", "help": "show help"},
                "h": {"cmd": "self.show('help')", "help": "show help"},
                "o": {"cmd": "self.set_mode('output')", "help": "output configuration"},
                "p": {"cmd": "self.set_mode('preset')", "help": "preset configuration"},
                "u": {"cmd": "print(json.dumps(self.commands, indent=4))", "help": "dump commands"},
            },
            "output": {},
            "preset": {}
        }
        self.mode = {}
        self.set_mode("main")
        self.update_commands()

    def set_mode(self, mode=None, idx=None):
        # print(f"set_mode {mode}, {idx}")
        self.mode["mode"] = mode
        if idx is not None:
            self.mode["idx"] = str(idx)
        else:
            self.mode["idx"] = None

    def prompt(self):
        while True:
            mode = self.mode.get("mode")
            idx = self.mode.get("idx")
            # print(f"mode: {mode} idx: {idx}")
            m = f"{mode}{':' if idx is not None else ''}{idx if idx is not None else ''}"
            print(f"{Colors.BOLD}{Colors.BLUE}::swayout::"
                  f" {Colors.GREEN}{m:>8}{Colors.ENDC}{Colors.BOLD} > {Colors.ENDC}",
                  end="", flush=True)
            sel = readchar.readchar().lower()
            print(sel)
            # quit
            if sel in ["q"]:
                print(f"{Colors.BOLD}{Colors.MAGENTA}> quit")
                break
            # main
            elif sel in self.commands["main"].keys():
                cmds = self.commands["main"]
                cmd = cmds[sel]["cmd"]
                exec(cmd)
                continue
            elif mode in self.commands.keys():
                # idx is not set
                if idx is None:
                    # print(f"idx is none: {idx}")
                    cmds = self.commands[mode]
                    if sel in cmds.keys():
                        if "cmd" in cmds[sel]:
                            cmd = cmds[sel]["cmd"]
                            exec(cmd)
                            continue
                # idx is set
                else:
                    cmds = self.commands[mode][idx]["sub_cmds"]
                    # print(f"cmds: {cmds}")
                    if sel in cmds.keys():
                        if "cmd" in cmds[sel]:
                            cmd = cmds[sel]["cmd"]
                            exec(cmd)
                            continue
            print(f"{Colors.YELLOW}> invalid input {sel}, press h/? for help{Colors.ENDC}")

    def update_commands(self):
        for c in self.output_cmds:
            if c == "#":
                for x in range(1, len(self.outputs) + 1):
                    self.commands["output"].update({
                        str(x): {
                            "cmd": eval(self.output_cmds["#"]["cmd"]),
                            "help": eval(self.output_cmds["#"]["help"]),
                            "sub_cmds": {
                                k: {
                                    "cmd": eval(self.output_sub_cmds[k]["cmd"],
                                                {'k': f'{k}', 'x': x}),
                                    "help": self.output_sub_cmds[k]["help"]
                                } for k in self.output_sub_cmds
                            }
                        }
                    })
            else:
                self.commands["output"].update({c: self.output_cmds[c]})

        for c in self.preset_cmds:
            if c == "#":
                for x in range(1, len(self.config["presets"]) + 1):
                    self.commands["preset"].update({
                        str(x): {
                            "cmd": eval(self.preset_cmds["#"]["cmd"]),
                            "help": eval(self.preset_cmds["#"]["help"]),
                            "sub_cmds": {
                                k: {
                                    "cmd": eval(self.preset_sub_cmds[k]["cmd"],
                                                {'k': f'{k}', 'x': x}),
                                    "help": self.preset_sub_cmds[k]["help"]
                                } for k in self.preset_sub_cmds
                            }
                        }
                    })
            else:
                self.commands["preset"].update({c: self.preset_cmds[c]})


    def set_output(self, idx, action, quiet=False):
        output = self.outputs[int(idx) - 1]
        if not quiet:
            print(f"{Colors.MAGENTA}> output: {output.name} {action}{Colors.CYAN}")

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
            print("  - sleep 10")
            time.sleep(10)
            self.set_output(idx, "enable", quiet=True)
            return
        elif action == "show":
            self.show("outputs", item_idx=idx)
            return

        print(f"  - {cmd}")
        self.i3.command(cmd)

    def set_preset(self, idx, action, quiet=False):
        outputs = self.config["outputs"]
        preset = self.config["presets"][int(idx) - 1]
        if not quiet:
            print(f"{Colors.MAGENTA}> preset: {preset.get('name')} {action}{Colors.CYAN}")

        i3_outputs = self.i3.get_outputs()
        preset_outputs = preset["outputs"]

        # disable active: False
        for p in filter(lambda x: not x["active"], preset_outputs):
            output = next(
                filter(lambda x: x["name"] == p["name"], outputs))
            try:
                i3_output = next(filter(lambda x: x.serial
                                == output["serial"], i3_outputs))
            except StopIteration:
                print(f"  - ignoring output {output['name']}, not connected")
                continue
            cmd = f"output {i3_output.name} disable"
            print(f"  - {cmd}")
            self.i3.command(cmd)

        if action == "reconfigure":
            for p in filter(lambda x: x["active"], preset_outputs):
                output = next(
                    filter(lambda x: x["name"] == p["name"], outputs))
                try:
                    i3_output = next(filter(lambda x: x.serial
                                    == output["serial"], i3_outputs))
                except StopIteration:
                    print(f"  - ignoring output {output['name']}, not connected")
                    continue
                cmd = f"output {i3_output.name} disable"
                print(f"  - {cmd}")
                self.i3.command(cmd)
            print("  - sleep 10")
            time.sleep(10)
            self.set_preset(idx, "enable", quiet=True)
        elif action == "enable":
            # enable active: True
            for p in filter(lambda x: x["active"], preset_outputs):
                output = next(
                    filter(lambda x: x["name"] == p["name"], outputs))
                try:
                    i3_output = next(filter(lambda x: x.serial
                                    == output["serial"], i3_outputs))
                except StopIteration:
                    print(f"  - ignoring output {output['name']}, not connected")
                    continue
                cmd = f"output {i3_output.name} enable"
                # work on copy of dict
                options = dict(output["options"])
                options.update(p["options"])
                for key in options:
                    cmd = cmd + f" {key} {options[key]}"
                print(f"  - {cmd}")
                self.i3.command(cmd)

            print(f"{Colors.ENDC}", end="")

    def show(self, item, item_idx=None):
        print(f"{Colors.BOLD}{Colors.MAGENTA}> show {item}{Colors.ENDC}")
        idx = 0
        if item == "help":
            for k in self.commands.keys():
                print(f"{Colors.CYAN}mode: {k}{Colors.GREEN}")
                c_k = self.commands[k]
                for k2 in c_k.keys():
                    c_k2 = c_k[k2]
                    h2 = c_k2["help"]
                    if k2.isdigit():
                        if k2 == "1":
                            h2 = h2.replace(f" {k2}", "")
                            print(f"  - #: {h2}")
                            if "sub_cmds" in c_k2:
                                print(f"{Colors.CYAN}  mode: {k}-#{Colors.GREEN}")
                                for k3 in c_k2["sub_cmds"]:
                                    h3 = c_k2["sub_cmds"][k3]["help"]
                                    print(f"    - {k3}: {h3}")
                    else:
                        print(f"  - {k2}: {h2}")

        elif item == "outputs":
            self.outputs = self.i3.get_outputs()
            for output in self.outputs:
                idx += 1
                if idx == item_idx or item_idx is None:
                    if output.active:
                        mode = f"{Colors.GREEN}"
                        mode += f"{output.current_mode.width:>4d}x{output.current_mode.height:<4d}"
                        mode += f"@{output.current_mode.refresh/1000:3.2f}"
                        mode += f" +{output.rect.x:>4d}/{output.rect.y:<4d}"
                        mode += f" %{output.scale:1.2f}"
                        mode += f"{Colors.CYAN}"
                    else:
                        mode = f"{Colors.RED}inactive{Colors.CYAN}"
                    print(
                        f"{Colors.CYAN}  {idx}: {output.name:5s} {mode:42s}"
                        f" {output.make[:10]:10s} {output.model[:8]:8s} {output.serial}{Colors.ENDC}")
        elif item == "presets":
            for preset_name in [x["name"] for x in self.config["presets"]]:
                idx += 1
                if idx == item_idx or item_idx is None:
                    print(f"{Colors.CYAN}  {idx}: {preset_name}{Colors.ENDC}")
