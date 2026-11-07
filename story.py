import art


PROLOGUE = [
    {
        "title": "PROLOGUE 1/3  //  EARTH IS RUNNING OUT OF TIME",
        "art": art.SHIP,
        "text": "Dust storms. Failing crops. One last plan.\n\n"
                "You are {name}, pilot of the ODYSSEY-7. In the cargo hold sits "
                "Seed Vault #01: ten thousand seeds that could start a new world. "
                "Your mission: fly through the wormhole near Saturn and deliver "
                "them to the planet HALCYON on the other side.",
    },
    {
        "title": "PROLOGUE 2/3  //  INSIDE THE WORMHOLE",
        "art": art.TITLE_SHIP,
        "text": "The stars fold like paper. Gravity twists the hull with a long, "
                "low groan.\n\n"
                "Then a gravity wave hits. Panels pop. Alarms howl. The drive "
                "core shakes loose and the ship spins out of the far side of the "
                "wormhole, coughing smoke.",
    },
    {
        "title": "PROLOGUE 3/3  //  HELLO, KRONOS",
        "art": art.BLACK_HOLE,
        "text": "Dead ahead glows KRONOS, a black hole wrapped in a ring of "
                "burning light, and the ship is drifting toward it. The rest of "
                "the crew is still frozen in cryo-sleep.\n\n"
                "That leaves you, KIP the maintenance drone, and TARS, the "
                "ship's robot, whose humor setting is stuck at 75%.",
    },
]


CHOICES = {
    "wakeup": {
        "title": "TARS CHECKS IN  //  BEFORE CHAPTER 1",
        "art": art.TARS,
        "text": "TARS: \"Good news, {name}: I still work. Bad news: we are "
                "drifting into the Shard Field, the ring of ice debris around "
                "the wormhole, and the nav scanner is blind. Before you start, "
                "pick one.\"",
        "options": [
            "Turn TARS's humor down to 60%  (your first shard hit is free)",
            "Let TARS send a gravity ping   (one free scanner hint)",
            "Fix KIP's bent antenna         (the drone will remember this...)",
        ],
    },
    "goose": {
        "title": "A KNOCK FROM NOWHERE  //  BEFORE CHAPTER 2",
        "art": art.SIGNAL,
        "text": "The life support grid is failing, strangely, its "
                "switches start flipping by themselves, tapping out a pattern.\n"
                "TARS: \"That is not me. Something beyond the wormhole is "
                "knocking.\"",
        "options": [
            "Decode the knocks in Morse     (one free grid hint)",
            "Power down the cryo lounge     (+10 battery)",
            "Knock back with your own signal (risky!)",
        ],
    },
    "cat": {
        "title": "THE LAST JAM  //  BEFORE CHAPTER 3",
        "art": art.KIP_SLEEPING,
        "text": "The drive core X is wedged between cargo crates in the drive "
                "bay. KIP has docked on top of it to recharge and dozed off. "
                "Through the window, the burning ring of KRONOS is getting VERY "
                "big.",
        "options": [
            "Ping KIP's homing beacon      (one free bay hint)",
            "Lift KIP off by hand          (does KIP trust you?)",
            "Ask TARS to hum KIP to sleep  (+5 battery)",
        ],
    },
}


CHOICE_RESULTS = {
    "coffee": (art.TARS, "TARS: \"Humor at 60%. Spare processing sent to the "
                         "deflectors.\" It sounds a little offended.\n\n"
                         "[DEFLECTOR ON: your first shard strike costs no battery]"),
    "poem": (art.TARS, "TARS hums one deep note. The ping bounces off the ice and "
                       "comes back as a rough map. TARS calls it \"modern art\".\n\n"
                       "[+1 FREE SCANNER HINT]"),
    "belly_rub": (art.KIP_AWAKE, "You straighten KIP's antenna. It beeps three happy "
                                 "beeps and bumps your helmet like a puppy.\n\n"
                                 "[KIP TRUSTS YOU NOW]"),
    "frosting": (art.SIGNAL, "Dot. Dash. Dot. The knocks point at one exact switch. "
                             "Whoever is sending them knows this panel very "
                             "well.\n\n[+1 FREE GRID HINT]"),
    "snacks": (art.TARS_SAD, "The cryo lounge goes dark and the battery climbs. TARS "
                             "plays a slow, sad tune for the lounge's very comfy "
                             "chairs.\n\n[+10 BATTERY]"),
    "goose_win": (art.SIGNAL_FRIEND, "You tap out HELLO. A pause. Then the switches "
                                     "spell F-R-I-E-N-D and the flickering steadies. "
                                     "Someone out there is on your side.\n\n"
                                     "[+5 BATTERY, A FRIEND IN THE DARK]"),
    "goose_lose": (art.SIGNAL, "Your signal feeds back through the grid. A battery "
                               "cell blows its fuse with a sad little pop.\n\n"
                               "[-5 BATTERY]"),
    "laser": (art.KIP_AWAKE, "KIP wakes at full speed, bounces off three walls, "
                             "shoves a crate aside and sticks itself to the "
                             "ceiling.\n\n[+1 FREE BAY HINT]"),
    "lift_friend": (art.KIP_AWAKE, "KIP remembers you fixing antenna. It beeps, floats off "
                                   "the core and projects a bay blueprint on the "
                                   "wall.\n\n[+1 FREE BAY HINT]"),
    "lift_angry": (art.KIP_AWAKE, "KIP does not know you yet. It flashes red and "
                                  "zaps your glove. You drop a power cell.\n\n"
                                  "[-5 BATTERY]"),
    "lullaby": (art.TARS, "TARS hums so low the floor shakes. KIP drifts off the "
                          "core, still asleep, and its spare charge trickles into "
                          "the grid.\n\n[+5 BATTERY]"),
}


CHAPTER_INTROS = {
    "navigation": "CHAPTER 1: THE SHARD FIELD. Tap squares to plot a safe route. "
                  "A number tells you how many ice shards touch that square.",
    "power": "CHAPTER 2: LIFE SUPPORT GRID. A switch flips itself AND its up, "
             "down, left and right neighbours. Turn every light ON.",
    "engine": "CHAPTER 3: THE DRIVE BAY. Three bays, three drive cores. Press "
              "ENTER to open the bay.",
}


ENDINGS = {
    "perfect": {
        "title": "ENDING: SLINGSHOT TO HALCYON",
        "art": art.ENDING_PERFECT,
        "text": "The drive core locks in. You skim the edge of KRONOS, borrow a "
                "little of its spin and fling the Odyssey-7 toward HALCYON, a "
                "blue-green world with real rain. TARS: \"Landing in nine days. "
                "Humor back to 75%. You earned it.\" The seeds arrive safe.",
    },
    "bumpy": {
        "title": "ENDING: LIMPING LANDFALL",
        "art": art.ENDING_BUMPY,
        "text": "The core clunks into place. The engines cough, sputter and "
                "finally roar. The Odyssey-7 crawls free of KRONOS trailing "
                "sparks and lands on HALCYON with one leg missing. TARS rates "
                "the landing \"survivable\". From TARS, that is basically a medal.",
    },
    "jelly": {
        "title": "ENDING: TIME SLIP",
        "art": art.ENDING_JELLY,
        "text": "The core locks in one second too late. You dip so close to "
                "KRONOS that time stretches like taffy. You escape and reach "
                "HALCYON... but 31 years have passed on Earth. Your inbox is "
                "full. TARS: \"Good news: I had plenty of time to write new jokes.\"",
    },
}


TARS_RATING_LINES = {
    1: "Not a scratch. Raising the difficulty, because you can clearly take it.",
    0: "Solid work. Keeping the difficulty where it is.",
    -1: "That was bumpy. I will make the next one gentler. You are welcome.",
}


EPILOGUE_LINES = {
    "goose_crew": "Years later, you work out who was knocking. It was you.",
    "frosting": "The Morse transcript is framed above the life support panel.",
    "laser": "KIP is still stuck to the ceiling. It seems happy up there.",
    "coffee": "TARS sets its humor back to 100% the moment you land.",
    "poem": "TARS's \"modern art\" map becomes the official Shard Field chart.",
    "belly_rub": "KIP now follows you everywhere on HALCYON, beeping.",
    "snacks": "TARS holds a short memorial for the cryo lounge chairs.",
    "lullaby": "TARS releases a lullaby album. KIP is the cover star.",
}


HOW_TO_PLAY = [
    [
        "THE MISSION",
        "",
        "Fix three broken systems on the Odyssey-7 before it falls into the",
        "black hole KRONOS. Between chapters you make story choices with TARS",
        "that give you battery, free hints or... surprises.",
        "",
        "SMART DIFFICULTY: TARS rates each system EFFICIENT, STEADY or SLOPPY.",
        "Efficient play makes the next system one level harder, sloppy play",
        "one level easier. Your drive bay run sets your next mission's level.",
        "",
        "BATTERY is shared by everything. Shard hits and hints cost battery.",
        "Anytime:  help   restart   quit       Stuck?  skip (scores 0)",
    ],
    [
        "CHAPTER 1: THE SHARD FIELD  (Minesweeper, 9 x 9)",
        "  t 3 4     tap (open) row 3, column 4",
        "  f 3 4     put or remove a flag where you think a shard is",
        "  b 3 4     break: open all around a number once it has enough flags",
        "  hint      the scanner suggests a square (8 battery)",
        "  Hitting a shard costs 10 battery. Open every safe square to win.",
        "",
        "CHAPTER 2: LIFE SUPPORT GRID  (Lights Out)",
        "  p 2 3     press the switch at row 2, column 3 (1 battery)",
        "  hint      shows a switch worth pressing (4 battery)",
        "  Each press flips that light and the lights next to it.",
        "  Turn every light ON to win.",
    ],
    [
        "CHAPTER 3: THE DRIVE BAY  (Klotski, 3 bays)",
        "  A up      slide crate A up one square (down, left, right too)",
        "  hint      show a halfway blueprint (1 hint energy)",
        "  reset     reset this bay        quit   give up on the bay",
        "  Move the 2x2 core X to the gap at the bottom middle, three times.",
        "  Hint energy comes from free hints and your battery (6 each).",
        "",
        "ENDINGS",
        "  Your score uses battery left, shards hit, moves and hints.",
        "  80+ is a Slingshot to Halcyon. Under 50, or an empty battery,",
        "  means a Time Slip. Every ending is a win... sort of.",
    ],
]
