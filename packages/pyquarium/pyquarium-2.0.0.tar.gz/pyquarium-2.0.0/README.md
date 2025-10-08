# pyquarium
ASCII art aquarium for your terminal. Written in Python.
```
               ]-<)))b>
                                                            O
                                                                  O
                                                                         )
                                                            (            )
                                                             )           )
       >-==>        >\\>                                    (            )
        o                                                   (            )
                                (                            )          (
                                (                            )           )
                                 )                          (           (
                                (              <><  o        )          (
     o                          ( .||<                       ) o        (
             <dX{+++(            )  )                       (           (
                                 ) (                    o   (            )
      o                          )  )                       (           (
                                (   )    >||>       O       (            )
                                (   )                        )  O       (
                                (  (                         )          (
         }>=b>                   ) (                        (           (
                                (   )                        ) O        (
                                 )  )                       (           (
                                 )  )                       (           (
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```
## Install
```shell
pip install pyquarium
```
## Synopsis
pyquarium [OPTION] [FPS]
## Description
Run pyquarium in the terminal at the rate of FPS frames-per-second.

**-b,  --bubblers**  
&nbsp;&nbsp;&nbsp;&nbsp;Number of bubble nucleation points to display.

**-f, --fish**  
&nbsp;&nbsp;&nbsp;&nbsp;Number of fish to display.

**-k, --kelp**  
&nbsp;&nbsp;&nbsp;&nbsp;Number of kelp strands to display.

**-v, --version**  
&nbsp;&nbsp;&nbsp;&nbsp;Print the version number and exit.

### Controls
**f, d**  
&nbsp;&nbsp;&nbsp;&nbsp;Add / remove a fish.

**k, j**  
&nbsp;&nbsp;&nbsp;&nbsp;Add / remove kelp.

**b, v**  
&nbsp;&nbsp;&nbsp;&nbsp;Add / remove bubbles.

**+, -**  
&nbsp;&nbsp;&nbsp;&nbsp;Increase / decrease the refresh rate.

**q**  
&nbsp;&nbsp;&nbsp;&nbsp;Quit the program.

## Examples
Run pyquarium with all default options.
```shell
python3 -m pyquarium
```

Run pyquarum at 10 fps.
```shell
python3 -m pyquarium 10
```

Run pyquarium at 7 fps with 9 fish, 10 bubblers, 4 kelp.
```shell
python3 -m pyquarium -f 9 -b 10 -k 4 7
```
