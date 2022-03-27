# swayout

switch between sway output presets


## configuration

edit `~/.config/swayout.json`

example

```
{
    "outputs": [
        { "name": "intern", "serial": "0x00000000",
            "options": { "mode": "1920x1080" }
        },
        {
            "name": "extern-38", "serial": "008NTLEFY912",
            "options": { "mode": "3840x1600" }
        },
    ],
    "presets": [
        {
            "name": "intern",
            "outputs": [
                {
                  "name": "intern", "active": true,
                    "options": { "position": "0 0" }
                },
                { "name": "extern-38", "active": false }
            ]
        },
        {
            "name": "intern & extern-38",
            "outputs": [
                {
                    "name": "intern", "active": true,
                    "options": { "position": "1600 0" }
                },
                {
                    "name": "extern-38", "active": true,
                    "options": { "position": "0 0" }
                }
            ]
        },
        {
            "name": "extern-38",
            "outputs": [
                { "name": "intern", "active": false },
                {
                    "name": "extern-38", "active": true,
                    "options": { "position": "0 0" }
                }
            ]
        }
    ]
}
```

options can be set to a default in `outputs[]` and overriden in `presets[]`


## run

swayout spawns an interactive shell with completion and validation of entered commands.
see all possible commands with `?` or just press `tab`.

```
$ swayout

swayout: outputs
  1: DP-8  [active]   2560x1600  Unknown              CX133      0x00000001
  2: DP-5  [active]   3840x1600  Goldstar Company Ltd 38GN950    008NTLEFY912

swayout: presets
  1: intern
  2: intern & extern-38
  3: extern-38

swayout > ?
swayout: help
available commands:
  - ?
  - output # [enable|configure|disable|reenable]
  - preset #
  - show outputs
  - show presets
  - quit

swayout > output 2 disable
>> output DP-5
  - output DP-5 disable
swayout > output 2 enable
>> output DP-5
  - output DP-5 enable

swayout > quit
```
