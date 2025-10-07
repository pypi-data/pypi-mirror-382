# Karen

> *"Congratulations on completing the rigorous Training Wheels Protocol and gaining access to your suit’s full capabilities... Would you like me to engage Enhanced Combat Mode?"* - Karen

`karen` is named after Spider-Man's virtual assistant in *Spider-Man: Homecoming*, who advised Peter in strategy and combat. This python script is designed to quickly, easily, and accurately analyse Spider-Man's combos in Marvel Rivals.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
    - [Initial State](#initial-state)
    - [Move Stacks](#move-stacks)
- [Roadmap](#roadmap)
- [License](#license)

## Installation

Install the `karen` python package using [pip](https://pypi.org/project/pip/):

```bash
pip install karen
```

The functions in this library can be used to create your own interface - but most likely you will prefer to download and run one of the scripts in the [tests folder](https://github.com/EvilDuck14/Karen/tree/main/tests), where command line & discord bot interfaces have already been implemented.

## Usage

`karen` evaluates combos given to it by the **!eval** command:

```
    !eval tGusto
```

The above evaluates the combo **tracer > get over here targeting > uppercut > swing > tracer > overhead slam**. Each action in a combo is assigned a single letter for maximum efficiency, but a combo can also be given in long-form by breaking up actions with instances of "**>**" - so the following is another valid way of writing the same command:

```
    !eval tracer > goht > upper > swing > tracer > oh
```

Note that shortened names are still used; in this format, single letter, shorthand names, or full names can be used to refer to each action. The full list is given below:

| Action | Letter | Other Names |
| :---: | :---: | :---:|
| Jump | j | jump |
| Double Jump | d | double jump <br> dj |
| Land | l | land |
| Punch | p | punch <br> punch A <br> punch B <br> melee punch <br> melee punch A <br> melee punch B |
| Kick | k | kick <br> melee kick |
| Overhead Slam | o | overhead slam <br> overhead <br> over <br> oh <br> melee overhead <br> slam |
| Tracer | t | tracer <br> web tracer <br> cluster <br> web cluster |
| Swing | s <br> z | swing <br> web swing <br> high swing <br> low swing <br> web zip <br> zip |
| Auto Swing | a | automatic swing <br> auto swing <br> auto <br> simple swing <br> easy swing |
| Whiff | w | whiff <br> web whiff <br> swing whiff |
| Get Over Here | g | get over here <br> goh <br> web pull <br> pull |
| Get Over Here Targeting | G | get over here targeting <br> goht |
| Uppercut | u | uppercut <br> upper <br> amazing combo |
| Burn Tracer | b | burn tracer <br> burn cluster <br> burn <br> fire tracer <br> fire cluster <br> fire <br> flame tracer <br> flame cluster <br> flame |

> [!TIP]
> Spaces and anything between parentheses is ignored by the bot. The single letter names of actions are case sensitive, while all of the longer-form versions of names ignore case, so *"MeleePU N(N)CH b"* will be interpreted as a punch.

> [!WARNING]
> Certain names such as *"dj"* and *"meleePunchB"* imply that the actions occur in contexts that aren't strictly enforced by the evaluation function - since *'dj'* is parsed as a jump, the calculator will interpret it as a single jump if it believes you're on the ground.

### Initial State

Some combos involve a setup that you don't want to list as a part of the combo - `karen` will automatically infer certain properties about the initial state.

If you use Get Over Here Targeting before tagging the target with a tracer/burn tracer, `karen` will infer that the target initially had a tracer applied (this will send a warning in the console).

If you use a kick before using two punches, `karen` will infer punches had been used immediately before beginning the combo.

If you use an overhead before getting airborne with a jump, burn tracer, or upercut, `karen` will assume you started the combo in an airborne state. If you use an overhead before acquiring one with a jump, swing, whiff, or burn tracer, `karen` will infer you started with a swing overhead. If you use two overheads before acquiring one, `karen` will assume you started with both overheads and no double jump.

### Move Stacks

A movestack is indicated by a "**+**" - for example, a FFAme stack would be written as follows:

```
    !eval (t)G+u
```

In long-form commands, the "**>**" separator can be entirely replaced by a "**+**", or they can be used in conjunction. If the command contains no instaces of the "**>**" character, it will not be recognised as a command, so the following are valid:

```
    !eval tracer goht >+ upper
```

```
    !eval tracer > goht + upper
```

But the following will not work, as the command will not be recognised as being long-form, since no "**>**" characters are present:

```
    !eval goht + upper
```

All movestacks are listed below:

|Name | Short notation(/s) | Other Names |
| :---: | :---: | :---: |
| FFAme Stack | G+u <br> f | ffame stack <br> ffame | 
| Saporen Tech (Overhead) | o+G | saporen <br> sap <br> overhead saporen <br> oh sap |
| Saporen Tech (Punch) | p+G | punch saporen <br> punch sap |
| Saporen Tech (Kick) | k+G | kick saporen <br> kick sap |
| Saporen FFAme Stack (Overhead) | o+G+u <br> F | saporen ffame stack <br> sap ffame stack <br> sap ffame <br> overhead saporen ffame stack <br> oh sap ffame stack <br> oh sap ffame |
| Saporen FFAme Stack (Punch) | p+G+u | punch saporen ffame stack <br> punch sap ffame stack <br> punch sap ffame |
| Saporen FFAme Stack (Kick) | k+G+u | kick saporen ffame stack <br> kick sap ffame stack <br> kick sap ffame |
| Space Jam | u+w+G <br> J | space jam <br> sj |
| Reverse Trigger (Punch) | p+t <br> r | reverse trigger <br> rt <br> punch reverse trigger <br> punch rt <br>  black flash <br> punch backflash |
| Reverse Trigger (Kick) | k+t | kick reverse trigger <br> kick rt <br> kick black flash <br> jash flash |
| Reverse Trigger (Overhead) | o+t |  overhead reverse trigger <br> oh reverse trigger <br> overhead rt <br> oh rt <br> overhead black flash <br> oh black flash |
| Punch Overhead Stack | p+o | punch overhead stack <br> punch oh stack <br> unique 3 hit punch stack <br> unique 3 hit punch <br> u3h punch |
| Kick Overhead Stack | k+o | kick overhead stack <br> kick oh stack <br> unique 3 hit kick stack <br> unique 3 hit kick <br> u3h kick |

## Roadmap

- [x] Add parsing of commands in all formats
- [x] Measure & record all action timings
- [x] Add evaluation function
- [x] Add error detection & warnings
- [x] Add discord bot functionality
- [ ] Add combo generator
- [ ] Optimise combo generator by removing unneeded actions

More detailed/frequent progress updates are given on the [testing discord server](https://discord.gg/RpQf2zVAMP).

## Acknowledgement

Special thanks to NonJohns for feedback on the design/featureset and for help with quality assurance.

Additional thanks to Venom, Fancy_Spider, and Mrpoolman, Katapult, and all other testers who helped find bugs.

## License

`karen` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.