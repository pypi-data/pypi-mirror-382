## What is this?
This package includes lexers for JSX and TSX files for Pygment, as well as RSX, a language called "Toolscript" developed by retool that was syntactically close enough to add in.
Pull requests are requested, and the code is released under the [Creative Commons Non-Commercial License (CC BY-NC-ND 4.0)](https://creativecommons.org/licenses/by-nc-nd/4.0/). 

## To use
Either:
`pip install techlens-pygments-tsx`

or add us to your requirements wherever they may be these days. (Looking at you, SetupTools, Poetry, PyPi... get it together.)

## Acknowledgments
This includes [Flavio Curella](https://github.com/fcurella)'s awesome package [JSX Lexer](https://github.com/fcurella/jsx-lexer), and includes the ideas and some code from [Igor Hatarist](https://github.com/hatarist)'s stab at this same problem [pygments-tsx](https://github.com/hatarist/pygments-tsx). Flaws were introduced by StartupOS, good stuff came from them.

There's also a hack in here for forcing pygments to accept classes programatically. That was based on discussions in this [thread](https://github.com/pygments/pygments/issues/1096), and specifically suggestions from [Vincent Bernat](https://github.com/vincentbernat) and [Jean Abou-Samra](https://github.com/jeanas)
