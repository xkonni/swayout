import argparse
import json
import pkg_resources
from xdg import BaseDirectory
import swayout.libswayout as libswayout

__version__ = pkg_resources.get_distribution('swayout').version

CONFIG_FILE = f"{BaseDirectory.xdg_config_home}/swayout.json"
CONFIG_DEFAULT = {"outputs": [], "presets": []}


def setup():
    ## arguments
    parser = argparse.ArgumentParser(description="swayout")
    parser.add_argument("-c", "--config", dest="config",
                        type=str, default=CONFIG_FILE, help="config file")
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("-d", "--debug", dest="debug", action="store_true",
                        help="debug mode")
    ## parse arguments
    args = parser.parse_args()
    config = {}
    try:
        with open(args.config) as f:
            config = json.load(f)
    except Exception as ex:
        print(f"Exception Type:{type(ex).__name__}, args:{ex.args}")
        print("running with empty config")
        config = CONFIG_DEFAULT

    return config

def main():
    config = setup()
    swayout = libswayout.SwayOut(config)
    swayout.show("outputs")
    swayout.show("presets")
    swayout.prompt()
