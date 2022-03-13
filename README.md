# swayout

switch between sway output presets


## configuration

edit `~/.config/swayout.json`

example

```
{
    "outputs": [
        { "name": "intern", "serial": "0x00000000", "mode": "1920x1080"},
        { "name": "extern", "serial": "008NTLEFY912", "mode": "3840x1600"},
        { "name": "extern2", "serial": "J257M96B00FL", "mode": "1920x1200", "scale": 1.3 }
    ],
    "presets": {
        "laptop": [
            { "name": "intern", "active": true , "position": "0 0" },
            { "name": "extern", "active": false },
            { "name": "extern2", "active": false }
        ],
        "dock1": [
            { "name": "intern", "active": false },
            { "name": "extern", "active": true, "position": "0 0" },
            { "name": "extern2", "active": false }
        ],
        "dock2": [
            { "name": "intern", "active": false },
            { "name": "extern", "active": true, "position": "1920 0" },
            { "name": "extern2", "active": true, "position": "0 0" }
        ]
    }
}
```

parameters can be set to a default in `outputs[]` and overriden in `presets[]`

implemented parameters are

- `mode`
- `position`
- `scale`



## run

```
$ swayout

>> connected outputs
  - DP-5  [active  ] Goldstar Company Ltd 38GN950 008NTLEFY912
  - DP-2  [active  ] Unknown KNH monitor J257M96B00FL
  - eDP-1 [inactive] Unknown 0x633D 0x00000000

>> presets
  1: laptop
  2: dock1
  3: dock2

>> Select preset from 1 to 3, any other key to abort...
3

>> activating preset dock2
>> apply preset dock2
output eDP-1 disable
output DP-5 enable mode 3840x1600 position 1920 0
output DP-2 enable mode 1920x1200 position 0 0 scale 1.3
```