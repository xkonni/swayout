from importlib.metadata import version
from types import SimpleNamespace

from swayout import __version__
from swayout import libswayout


class FakeI3:
    def __init__(self, outputs):
        self.outputs = outputs
        self.commands = []

    def get_outputs(self):
        return self.outputs

    def command(self, command):
        self.commands.append(command)


def make_output():
    return SimpleNamespace(
        name="DP-1",
        serial="serial-1",
        active=True,
        current_mode=SimpleNamespace(width=1920, height=1080, refresh=60000),
        rect=SimpleNamespace(x=0, y=0),
        scale=1,
        make="Example",
        model="Display",
    )


def make_config():
    return {
        "outputs": [
            {
                "name": "external",
                "serial": "serial-1",
                "options": {"mode": "1920x1080"},
            }
        ],
        "presets": [
            {
                "name": "external",
                "main": "external",
                "outputs": [{"name": "external", "active": True}],
            }
        ],
    }


def test_version():
    assert __version__ == version('swayout')


def test_swayout_initializes_and_shows(monkeypatch, capsys):
    monkeypatch.setattr(libswayout, "Connection", lambda: FakeI3([make_output()]))
    swayout = libswayout.SwayOut(make_config())

    swayout.show("outputs")
    swayout.show("presets")

    output = capsys.readouterr().out
    assert "DP-1" in output
    assert "external" in output


def test_set_mode(monkeypatch):
    monkeypatch.setattr(libswayout, "Connection", lambda: FakeI3([]))
    swayout = libswayout.SwayOut(make_config())

    swayout.set_mode("preset", 1)

    assert swayout.mode == {"mode": "preset", "idx": "1"}


def test_set_output_uses_fake_connection(monkeypatch):
    fake_i3 = FakeI3([make_output()])
    monkeypatch.setattr(libswayout, "Connection", lambda: fake_i3)
    monkeypatch.setattr(libswayout.time, "sleep", lambda _: None)
    swayout = libswayout.SwayOut(make_config())

    swayout.set_output(1, "configure")
    swayout.set_output(1, "disable")
    swayout.set_output(1, "enable")
    swayout.set_output(1, "reconfigure")

    assert fake_i3.commands == [
        "output DP-1 mode 1920x1080",
        "output DP-1 disable",
        "output DP-1 enable",
        "output DP-1 disable",
        "output DP-1 enable",
    ]


def test_set_preset_enables_configured_output(monkeypatch):
    fake_i3 = FakeI3([make_output()])
    monkeypatch.setattr(libswayout, "Connection", lambda: fake_i3)
    swayout = libswayout.SwayOut(make_config())

    swayout.set_preset(1, "enable")

    assert fake_i3.commands == [
        "set $main DP-1",
        "output DP-1 enable mode 1920x1080",
    ]


def test_set_preset_ignores_unconfigured_outputs(monkeypatch, capsys):
    fake_i3 = FakeI3([])
    monkeypatch.setattr(libswayout, "Connection", lambda: fake_i3)
    config = {
        "outputs": [],
        "presets": [
            {
                "name": "external",
                "main": "unconfigured-main",
                "outputs": [
                    {"name": "unconfigured-inactive", "active": False},
                    {"name": "unconfigured-active", "active": True},
                ],
            }
        ],
    }
    swayout = libswayout.SwayOut(config)

    swayout.set_preset(1, "enable")

    output = capsys.readouterr().out
    assert "unconfigured-main, not available" in output
    assert "unconfigured-inactive, not available" in output
    assert "unconfigured-active, not available" in output
