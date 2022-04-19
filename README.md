# swayout

switch between sway output presets


## configure swayout

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


## run swayout

swayout spawns an interactive shell with minimal interaction.
see all possible commands with `?/h`

```
$ swayout

swayout: outputs
  1: DP-8  [active]   2560x1600  Unknown              CX133      0x00000001
  2: DP-5  [active]   3840x1600  Goldstar Company Ltd 38GN950    008NTLEFY912

> show outputs
  1: DP-8  [active]   2560x1600  Unknown              CX133      0x00000001
  2: DP-5  [active]   3840x1600  Goldstar Company Ltd 38GN950    008NTLEFY912
  3: eDP-1 [inactive] -          Unknown              0x5B2D     0x00000000
> show presets
  1: intern
  2: extern-13
  3: extern-13 & extern-38
::swayout::     main > h
> show help
mode: any
  - q: quit swayout
  - m: main menu
  - ?: show help
  - h: show help
  - u: dump commands
mode: main
  - o: output configuration
  - p: preset configuration
  - s: show outputs/presets
mode: output
  - #: select output
  mode: output-#
    - c: configure output
    - e: enable output
    - d: disable output
    - o: output configuration
    - r: reconfigure output
    - s: show output
  - s: show outputs
mode: preset
  - #: switch to preset
  - s: show presets
mode: show
  - o: show outputs
  - p: show presets
::swayout::     main > o
::swayout::   output > 2
::swayout:: output:2 > d
> output: DP-5 disable
  - output DP-5 disable
::swayout:: output:2 > m
::swayout::     main > o
::swayout::   output > s
> show outputs
  1: DP-8  [active]   2560x1600  Unknown              CX133      0x00000001
  2: DP-5  [inactive] -          Goldstar Company Ltd 38GN950    008NTLEFY912
  3: eDP-1 [inactive] -          Unknown              0x5B2D     0x00000000
::swayout::   output > 2
::swayout:: output:2 > e
> output: DP-5 enable
  - output DP-5 enable
::swayout:: output:2 > m
::swayout::     main > s
::swayout::     show > o
> show outputs
  1: DP-8  [active]   2560x1600  Unknown              CX133      0x00000001
  2: DP-5  [active]   3840x1600  Goldstar Company Ltd 38GN950    008NTLEFY912
  3: eDP-1 [inactive] -          Unknown              0x5B2D     0x00000000
::swayout::     show > p
> show presets
  1: intern
  2: extern-13
  3: extern-13 & extern-38
::swayout::     show > q
> quit
```


## test swayout


### pytest

```
$ poetry run pytest
==================================================================== test session starts ====================================================================
platform linux -- Python 3.10.4, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
rootdir: /home/konni/workspace/swayout
plugins: metadata-1.11.0, html-3.1.1
collected 6 items

tests/test_swayout.py ......                                                                                                                          [100%]

===================================================================== 6 passed in 8.90s =====================================================================
```


### coverage

```
$ poetry run coverage run -m pytest && poetry run coverage report
==================================================================== test session starts ====================================================================
platform linux -- Python 3.10.4, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
rootdir: /home/konni/workspace/swayout
plugins: metadata-1.11.0, html-3.1.1
collected 6 items

tests/test_swayout.py ......                                                                                                                          [100%]

===================================================================== 6 passed in 8.38s =====================================================================
Name                    Stmts   Miss  Cover
-------------------------------------------
swayout/__init__.py         8      4    50%
swayout/libswayout.py     170     36    79%
-------------------------------------------
TOTAL                     178     40    78%
```


### flake8

this on the todo list...

```
$ poetry run flake8
./swayout/libswayout.py:222:5: C901 'SwayOut.show' is too complex (14)
```

