# ASCII scenes and logos used by the story pages and terminal screens.
def to_lines(picture):
    lines = picture.split("\n")
    if lines and lines[0] == "":
        lines = lines[1:]
    if lines and lines[-1].strip() == "":
        lines = lines[:-1]
    return lines


TITLE_LOGO = to_lines(r"""
     __        __   ___    ____    __  __   _   _    ___    _       _____
     \ \      / /  / _ \  |  _ \  |  \/  | | | | |  / _ \  | |     | ____|
      \ \ /\ / /  | | | | | |_) | | |\/| | | |_| | | | | | | |     |  _|
       \ V  V /   | |_| | |  _ <  | |  | | |  _  | | |_| | | |___  | |___
        \_/\_/     \___/  |_| \_\ |_|  |_| |_| |_|  \___/  |_____| |_____|
""")

TITLE_SHIP = to_lines(r"""
  .        *          .         .-~~~~~~-.       *
        _______              .' .-~~~~-. '.          .
   ____/  [o]  \____        (  (  (  )  )  )     *
  <==== ODYSSEY-7 ====>==-   '. '-~~~~-' .'
       \_________/              '-~~~~~~-'     .
    *          .        *          WORMHOLE
""")

SHIP = to_lines(r"""
          _______
     ____/  [o]  \____
    <==== ODYSSEY-7 ====>==-  ~ ~
         \_________/
""")

BLACK_HOLE = to_lines(r"""
          .   . - ~ ~ - .   .
       *   .'   _______   '.
    ~~~~~~(~~~ (       ) ~~~)~~~~~~
       .   '.   ~~~~~~~   .'   *
          .   ' - ~ ~ - '   .
              K R O N O S
""")

TARS = to_lines(r"""
     .---.---.---.---.
     |   |[o]|   |   |   TARS
     |   | = |   |   |   humor    75%
     |   |   |   |   |   honesty  90%
     |   |   |   |   |
     '---'---'---'---'
""")

TARS_SAD = to_lines(r"""
     .---.---.---.---.
     |   |[-]|   |   |   TARS
     |   | ~ |   |   |   humor     0%
     |   |   |   |   |   (in mourning)
     |   |   |   |   |
     '---'---'---'---'
""")

SEED_VAULT = to_lines(r"""
     .-------------------.
     |  SEED VAULT  #01  |
     | [~] [~] [~] [~]   |
     |  10,000 SEEDS: OK |
     '-------------------'
""")

SIGNAL = to_lines(r"""
  (( ( o ) ))   ..-. ..- - ..- .-. .
 ((  (   )  ))
  (( ( o ) ))   signal: ???
""")

SIGNAL_FRIEND = to_lines(r"""
  (( ( o ) ))   ..-. .-. .. . -. -..
 ((  (   )  ))
  (( ( o ) ))   signal: FRIEND
""")

KIP_SLEEPING = to_lines(r"""
        .-=====-.
       (  -   -  )  zzz    KIP
       |=========|         maintenance drone
        '-/   \-'
""")

KIP_AWAKE = to_lines(r"""
        .-=====-.
       (  o   o  )  !!!    KIP
       |=========|         maintenance drone
        '-/   \-'
""")

ASTEROIDS = to_lines(r"""
     .   <*>    .     o
   o    .    <**>   .
      <*>  .     o     <*>
   .      o    <**>  .
""")

BREAKER_PANEL = to_lines(r"""
    +---------------------+
    | LIFE SUPPORT GRID   |
    |  [*] [*] [ ] [*]    |
    |  ~~ O2   CO2   H2O  |
    +---------------------+
""")

ENGINE_CORE = to_lines(r"""
       +----------+
       |  ######  |
       |  # XX #  |  DRIVE CORE
       |  ######  |
       +----||----+
""")

ENDING_PERFECT = to_lines(r"""
   *        .          *            .        .-~~~-.
         _______                    *      .' ~  o  '.
    ____/  [o]  \____   ~~>  ~~>  ~~>     | HALCYON ~ |
   <==== ODYSSEY-7 ====>=============-    '.  ~   ~ .'
        \_________/                         '-~~~-'
   .         *         .          *     new home: FOUND
""")

ENDING_BUMPY = to_lines(r"""
                         (  )  ( )
         _______        (  ) (  )
    ____/  [o]  \____  ( )
   <==== ODYSSEY-7 ====>=--  ~   *clunk*
        \_________/
           \/    \/    sparks: yes    legs: 3 of 4
""")

ENDING_JELLY = to_lines(r"""
         _______           .  - ~ ~ ~ -  .
    ____/  [o]  \____    .'   _________   '.
   <==== ODYSSEY-7 ====>~~~~~(           )~~~~~
        \_________/      '.   ~~~~~~~~~   .'
                            '  - ~ ~ ~ -  '
     ship clock:  +2 hours      earth clock:  +31 YEARS
""")

DIFFICULTY_NAMES = {
    "easy": "CADET",
    "medium": "PILOT",
    "hard": "COMMANDER",
}
