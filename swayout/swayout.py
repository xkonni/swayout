from i3ipc import Connection
import json
import readchar
from xdg import XDG_CONFIG_HOME

CONFIG_FILE = f"{XDG_CONFIG_HOME}/swayout.json"


class SwayOut:
    def __init__(self, config):
        self.i3 = Connection()
        self.config = config

    def apply(self, preset_name):
        presets = self.config["presets"]
        outputs = self.config["outputs"]
        if not preset_name in presets:
            print(f"preset {preset_name} not defined")
            return False

        print(f">> apply preset {preset_name}")
        preset = presets[preset_name]
        i3_outputs = self.i3.get_outputs()

        # disable active: False
        for p in filter(lambda x: not x["active"], preset):
            output = next(
                filter(lambda x: x["name"] == p["name"], outputs))
            i3_output = next(filter(lambda x: x.serial ==
                             output["serial"], i3_outputs))
            cmd = f"output {i3_output.name} disable"
            print(cmd)
            self.i3.command(cmd)

        # enable active: True
        for p in filter(lambda x: x["active"], preset):
            output = next(
                filter(lambda x: x["name"] == p["name"], outputs))
            i3_output = next(filter(lambda x: x.serial ==
                             output["serial"], i3_outputs))
            cmd = f"output {i3_output.name} enable"
            for k in ["mode", "position", "scale"]:
                if k in p:
                    cmd = cmd + f" {k} {p[k]}"
                elif k in output:
                    cmd = cmd + f" {k} {output[k]}"
            print(cmd)
            self.i3.command(cmd)

    def select(self):
        presets = self.config["presets"]
        i3_outputs = self.i3.get_outputs()
        print(">> connected outputs")
        for i3_output in i3_outputs:
            print(f"  - {i3_output.name:5s} [{'active' if i3_output.active else 'inactive':8s}] {i3_output.make} {i3_output.model} {i3_output.serial}")

        print("\n>> presets")
        list = {}
        idx = 0
        for preset_name in presets:
            idx += 1
            print(f"  {idx}: {preset_name}")
            list[idx] = preset_name

        print(f"\n>> Select preset from 1 to {idx}, any other key to abort... ")
        sel = readchar.readchar()

        try:
            print(sel)
            sel = int(sel)
            p = list[sel]
            print(f"\n>> activating preset {p}")
            self.apply(p)
        except:
            print("aborting")


def main():
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    swayout = SwayOut(config)
    swayout.select()


if __name__ == "__main__":
    main()
