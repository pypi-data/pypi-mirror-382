import time  # noqa: F401
import sys
import random
last_input = ""

def handle_exit(exc_type, exc_value, exc_traceback):
    if exc_type is KeyboardInterrupt:
        print("You run screaming in fear so loudly that you don't even think to use the 'quit' command.")
        sys.exit(0)
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


def init_game():
    player = {
        "location": "spawn",
        "coins": 60,
        "inventory": [],
        "battle": [],
        "weapon": "fists",
        "armor": "clothes",
        "min_dmg": 3,
        "max_dmg": 10,
        "hp": 30,
        "max_hp": 30
    }
    rooms = {
        "spawn": {
            "flavor": "A hidden room at the back of a tavern.",
            "text": "You enter into the room at the back of the tavern and \n"
                    "notice a gaping hole at the back of it. What lies at the end \n"
                    "is unknown, but it's thought that it contains the legendary \n"
                    "treasure of the Schmamework 69.",
            "exits": {
                "north": "entrance",
                "south": "tavern",
            },
            "items": ["moldybaguette"],
            "enemies": []
        },
        "entrance": {
            "flavor": "A gaping, dusty, damp cave.",
            "text": "The cave begins to widen. You can tell something is definitely\n"
                    "down here, although you have no clue where to even begin knowing\n"
                    "what it might be.",
            "exits": {
                "south": "spawn",
                "north": "entrance2"
            },
            "items": ["gruehair"],
            "enemies": ["grue"]
        },
        "tavern": {
            "flavor": "A bustling tavern full of drunken men.",
            "text": "You decide that the rumored treasure isn't worth the loss\n"
                    "of your sleep schedule and return to the tavern, drinking\n"
                    "with your buddies and trying to forget about the cave.",
            "exits": {},
            "items": [],
            "enemies": []
        },
        "entrance2": {
            "flavor": "More cave, getting narrower as you continue.",
            "text": "As you continue down the cave, it begins to shrink. As it gets\n"
                    "even tighter, you eventually have to crawl on your hands and\n"
                    "knees to make it through, but it finally widens. After it widens,\n"
                    "you can see that it's been intentionally hollowed out.",
            "exits": {
                "west": "gamble",
                "north": "pit",
                "south": "entrance"
                },
            "items": [],
            "enemies": []
        },
        "gamble": {
            "flavor": "An aging room styled like a '70s diner.",
            "text": "You enter the room. It looks straight out of an old black-and-white\n"
                    "poorly produced sitcom, which you're not sure if it is a good or a\n"
                    "bad thing. Multiple people sit in time-appropriate outfits, playing\n"
                    "cards or other various games at booth tables and eating food that\n"
                    "looks like sand.",
            "exits": {
                "east": "entrance2",
                "down": "gamblebasement"
            },
            "items": ["brandy"],
            "enemies": []
        },
        "gamblebasement": {
            "flavor": "The dingy basement of a '70s diner.",
            "text": "It's filled with questionably sanitary food storage racks. Nobody\n"
                    "is down here at the moment, but it's clearly a well-used area.\n"
                    "However, the pest control measures of the time are made very\n"
                    "obvious.",
            "exits": {
                "up": "gamble"
            },
            "items": ["rottentomato"],
            "enemies": ["rat", "rat", "rat", "rat", "rat"]
        },
        "pit": {
            "flavor": "A pit.",
            "text": "You can see the bottom, and there's no way around it. What might\n"
                    "be down here is anyone's guess. Its edges are very rough, and you\n"
                    "will have to be careful to not tear your clothes up.",
            "exits": {
                "south": "entrance2",
                "down": "gate"
            },
            "items": [],
            "enemies": []
        },
        "gate": {
            "flavor": "A rusted shut gate at the bottom of a pit",
            "text": "The gate lists a myriad of prices in languages you do not know,\n"
                    "but near the bottom it lists 5 coins as the price of entry. An\n"
                    "automated machine accepts your coins and lets you through.\n"
                    "It appears it was impossible to climb out of the pit anyways.\n"
                    "(-5 Coins)",
            "exits": {
                "south": "doors"
            },
            "items": ["datestamp"],
            "enemies": []
        },
        "doors": {
            "flavor": "A set of three doors, guarded by clockwork puppets.",
            "text": "Three robotic puppets stand in front of their respective doors.\n"
                    "They're all clearly different, but you can't tell which door might\n"
                    "lead where. A sign on a wall reads where they lead, but not which-\n"
                    " TRUTH - DEATH - LIES.",
            "exits": {
                "south": "death",
                "west": "truth",
                "east": "lies"
                },
            "items": [],
            "enemies": []
        },
        "death": {
            "flavor": "An ornate, antique wooden door.",
            "text": "As you walk through the ornate door, your hand sticks to the doorknob.\n"
                    "As you struggle to pull it off, there is a rumbling from inside the\n"
                    "tunnel within, getting louder, but your hand only sticks more. The\n"
                    "noise reaches a crescendo and finally a tidal wave of locusts covers\n"
                    "your face and nose, suffocating you and leaving you to perish in the\n"
                    "room. A set of robots comes through to clean the room again, but the\n"
                    "life has already left your eyes.",
            "exits": {},
            "items": [],
            "enemies": []
        },
        "truth": {
            "flavor": "An incredibly heavy pure-white marble door.",
            "text": "You walk through into a similarly bright marble tunnel and the door locks\n"
                    "behind you. No threats appear to exist in this tunnel, and you even find \n"
                    "a small cabinet tucked away in the wall. It ends with a similar door.",
            "exits": {
                "south": "mud"
            },
            "items": ["brandy"],
            "enemies": []
        },
        "lies": {
            "flavor": "A door absolutely covered in vines. Not threatening, but very natural.",
            "text": "The door has no doorknob on the inside, but you step inside anyway. \n"
                    "As you walk down the tunnel, it's poorly lit, but it's kind of nice\n"
                    "in some post-brutalist way. A single rat's nest is visible, and you\n"
                    "make it through with almost no trouble.",
            "exits": {
                "east": "pain",
                "south": "illusion"
            },
            "items": [],
            "enemies": ["rat"],
        },
        "pain": {
            "flavor": "The tunnel continues and gets muddier, almost warning you.",
            "text": "You're not sure as to what this tunnel even contains. To your\n"
                    "side scares you deeply, but the next room isn't much better.",
            "exits": {
                "west": "lies",
                "east": "noreturn",
            },
            "items": [],
            "enemies": []
        },
        "noreturn": {
            "flavor": "The tunnel opens up, is very muddy, and contains many weeds and puddles.",
            "text": "Past this point, you don't think you'll be able to return to the\n"
                    "tunnel before - and you're not sure if that's a good thing. As you\n"
                    "continue to walk, something stings your leg but gets away.",
            "exits": {
                "west": "pain",
                "east": "freepassage"
            },
            "items": [],
            "enemies": []
        },
        "freepassage": {
            "flavor": "A ladder that will collapse if you climb down it, blocking return.",
            "text": "The ladder disintegrates into flakes of rust, irritating your eyes\n"
                    "as you climb down in to the dark. You can tell you've passed some\n"
                    "other area - whether that's good or bad, you don't know.",
            "exits": {
                "down": "sewers",
            },
            "items": [],
            "enemies": []
        },
        "sewers": {
            "flavor": "The sewers, not used for a while, but still gross.",
            "text": "It appears you've climbed down into at least somewhat of a civilized\n"
                    "area, much nicer than just a cave. It leads into a room, but you're\n"
                    "effectively in the toilet for hundreds of miners, years ago. The stench\n"
                    "is barely survivable.",
            "exits": {
                "west": "antechamber",
            },
            "items": [],
            "enemies": []
        },
        "illusion": {
            "flavor": "A haze blocks you from seeing or knowing what is ahead.",
            "text": "You see nothing. You thought you saw many creatures and almost got hold\n"
                    "of them, but did not. You thought you saw coins littered around the\n"
                    "ground, but your hand passed through them. Everything is shifting as if\n"
                    "you were melting in to the earth, but eventually you pass.",
            "exits": {
                "north": "lies",
                "south": "snakes"
            },
            "items": [],
            "enemies": []
        },
        "snakes": {
            "flavor": "A tunnel - plain with many small burrows in the earthy clay ground.",
            "text": "Snakes appear from the holes as you walk dizzily into the room.\n"
                    "Most don't want to cause harm, but one snake really wants blood.",
            "exits": {
                "north": "illusion",
                "south": "beehive"
            },
            "items": [],
            "enemies": ["cobra"]
        },
        "beehive": {
            "flavor": "A muddy field with flowers everywhere.",
            "text": "Bees swarm everywhere, collecting pollen from the flowers. It's a nice\n"
                    "change from the snakes, and you pause for a bit. It's safe here, despite\n"
                    "the fact that bees are somehow living and thriving underground.",
            "exits": {
                "north": "snakes",
                "south": "elevator"
            },
            "items": ["honey"],
            "enemies": []
        },
        "mud": {
            "flavor": "A room full of 2-foot deep mud, but it looks incredibly pure...?",
            "text": "You wade through the mud and even happen to find 5 coins buried in it.\n"
                    "You have... no clue as to how they got here, but not complaining.",
            "exits": {
                "north": "truth",
                "south": "rockfall"
            },
            "items": [],
            "enemies": []
        },
        "rockfall": {
            "flavor": "A chamber with a collapsed ceiling.",
            "text": "You come in and notice layers of rocks with stuff underneath.\n"
                    "It appears there was a wishing well here with coins still here,\n"
                    "but it's under a few feet of stones.",
            "exits": {
                "north": "mud",
                "east": "swordstone"
            },
            "items": [],
            "enemies": []
        },
        "swordstone": {
            "flavor": "The chamber turns to roman architecture, a single stone in the centre.",
            "text": "The stone in the middle of the room has a sword in it, but it's not even\n"
                    "stuck. It makes you wonder why someone might put it here. Cool sword though",
            "exits": {
                "south": "drawings",
                "west": "rockfall"
            },
            "items": ["coolsword"],
            "enemies": ["grue"]
        },
        "drawings": {
            "flavor": "A Roman room full of incomprehensible diagrams and drawings.",
            "text": "You spend a good half hour trying to make sense of the scrawlings on the\n"
                    "walls, but they only get more confusing as you look on. They are either\n"
                    "scrawlings of madmen or definitely in a different language you don't know.",
            "exits": {
                "north": "swordstone",
                "south": "gambleturtle"
            },
            "items": [],
            "enemies": []
        },
        "gambleturtle": {
            "flavor": "A very small room containing a single turtle",
            "text": "What do you know, the turtle... wants to gamble with you? How does it know\n"
                    "English? You don't know, but you're incredibly compulsed to gamble with the\n"
                    "turtle to the point you cannot stop yourself.",
            "exits": {
                "north": "drawings",
                "east": "elevator"
            },
            "items": [],
            "enemies": []
        },
        "elevator": {
            "flavor": "An elevator.",
            "text": "The elevator has a coin slot on it, reading \"10 coins a trip\", which\n"
                    "someone scribbled out and replaced with 5 hastily. Clearly, the price was"
                    "not appreciated by whoever was here last. You pay the updated toll and the\n"
                    "elevator whirrs to life, taking you down.",
            "exits": {
                "down": "collapsedmine",
            },
            "items": [],
            "enemies": []
        },
        "collapsedmine": {
            "flavor": "A mineshaft with a collapsed ceiling.",
            "text": "Skeletons are scattered about. The miners that were here before must have\n"
                    "been working when the ceiling came down on them. A result of poor management.",
            "exits": {
                "south": "office", 
            },
            "items": [],
            "enemies": ["ghost"]
        },
        "office": {
            "flavor": "An office clearly designed to get work and not play done.",
            "text": "Many books are scattered on shelves. Many disintegrate the second you touch\n"
                    "them, and what few are left ironically record the pay of people making coins.",
            "exits": {
                "north": "collapsedmine",
                "west": "refinery",
                "east": "robotguards" 
            },
            "items": [],
            "enemies": []
        },
        "refinery": {
            "flavor": "Belts and furnaces where ore once was refined into pure gold.",
            "text": "Somehow, things are still active and definitely hot. Maybe robots help, or magic -\n"
                    "you're not entirely sure. This area was worked by many staff before scooping the"
                    "molten gold into coin-shaped molds and pushed around, but it's long dormant.",
            "exits": {
                "east": "office",
                "south": "smeltery"
            },
            "items": [],
            "enemies": []
        },
        "smeltery": {
            "flavor": "Molten gold continues to flow in circles in eroded channels.",
            "text": "There's an island in the middle that contains a half-full tray of fresh coins,\n"
                    "but you'll have to be careful as you cross over it - you might fall in, burning\n"
                    "yourself horribly. Molten gold is not fun to get off skin.",
            "exits": {
                "north": "refinery",
            },
            "items": [],
            "enemies": []
        },
        "barracks": {
            "flavor": "Half-buried miner's bunks, not designed for comfort",
            "text": "The bunks are decayed, the straw mattresses turned to dust. One skeletal arm\n"
                    "still clutches a coin purse with a single coin left inside. A translucent miner\n"
                    "wanders here, endlessly searching for his pay. He does not like being disturbed.\n",
            "exits": {
                "north": "office",
                "south": "airvent"
            },
            "items": [],
            "enemies": ["ghost"]
        },
        "airvent": {
            "flavor": "A vent leading straight downwards with a wide grate over it.",
            "text": "The grate rattles beneath your feet. As you step onto it, two coins fall from your\n"
                    "pocket down to whatever lies below. You can make out air rising through the shaft,\n"
                    "smelling uncannily like old incense.",
            "exits": {
                "north": "barracks",
                "down": "shrine"
            },
            "items": [],
            "enemies": []
        },
        "shrine": {
            "flavor": "A room containing a hill with a shrine of some kind on it.",
            "text": "An old altar rests atop a mound of dust. A cracked plaque reads:\n"
                    "'Give, and be made whole. Take, and be hollow.' You sense powerful energy.",
            "exits": {
                "up": "airvent",
            },
            "items": [],
            "enemies": []
        },
        "robotguards": {
            "flavor": "Multiple humanoid robotic sentries guard a door.",
            "text": "You approach the guards and fans whir to life - a message appears\n"
                    "on their worn nixie tube screens: '20 COINS OR ATTACK'.",
            "exits": {
                "west": "office",
                "south": "cranklift",
            },
            "items": [],
            "enemies": ["guard", "guard"]
        },
        "cranklift": {
            "flavor": "A crank-operated mine elevator.",
            "text": "The elevator was designed to be operated by multiple strong miners,\n"
                    "so you'll have to risk it - it might descend too fast and hurt you.",
            "exits": {
                "north": "robotguards",
                "down": "antechamber"
            },
            "items": [],
            "enemies": []
        },
        "antechamber": {
            "flavor": "Walls engraved with endless dollar symbols. How vain.",
            "text": "This chamber hums faintly, as if the gold in the walls remembers every\n"
                    "coin ever minted. It feels like a final warning as to what comes ahead.",
            "exits": {
                "south": "hall",
            },
            "items": [],
            "enemies": []
        },
        "hall": {
            "flavor": "The antechamber continues into a hall.",
            "text": "Echoes of coins clattering on marble follow your every step.",
            "exits": {
                "west": "shrines",
                "south": "grueboss",
                "east": "echoes"
            },
            "items": [],
            "enemies": []
        },
        "shrines": {
            "flavor": "Many tiny shrines on their own little pedestals, like a cemetery.",
            "text": "Each shrine has a tiny coin slot on each for some reason. Most appear filled,\n"
                    "but a few have slots clogged with rust over time.",
            "exits": {
                "down": "treasury",
                "east": "hall"
            },
            "items": ["silvercharm"],
            "enemies": []
        },
        "treasury": {
            "flavor": "A huge vault door.",
            "text": "You find piles of ancient coins, but touching them feels wrong, like the coins\n"    
                    "are hollow inside. You sense these won't be usable as actual currency.",
            "exits": {
                "up": "shrines",
            },
            "items": ["brandy"],
            "enemies": []
        },
        "echoes": {
            "flavor": "A cubic room completely devoid of anything but a thick haze.",
            "text": "You hear every coin you've lost echo around you, as if they were alive.\n"
                    "The air here feels alive. A pulse below draws you downward.",
            "exits": {
                "west": "hall",
                "down": "heart"
            },
            "items": [],
            "enemies": []
        },
        "heart": {
            "flavor": "A pulsating chamber of living stone, veined with gold.",
            "text": "You realize the entire dungeon is alive, beating to the rhythm of greed.\n"
                    "A huge beating monolith rests at the center, shaped like a heart.",
            "exits": {
                "up": "echoes"
            },
            "items": [],
            "enemies": []
        },
        "grueboss": {
            "flavor": "An obvious arena - in your path.",
            "text": "The floor trembles as a deep growl fills the chamber. From the shadows emerges\n"
                    "a towering, ancient Grue - stronger and hungrier than the rest. Prepare yourself.",
            "exits": {
                "south": "toll",
            },
            "items": [],
            "enemies": ["ancient_grue"]
        },
        "toll": {
            "flavor": "Two massive, fortified gates, marked with golden lettering.",
            "text": "The inscription reads: 'Only those who paid their dues may pass.'\n"
                    "You notice a glowing slot - it asks 50 coins' penance.",
            "exits": {
                "south": "victory",
            },
            "items": [],
            "enemies": []
        },
        "victory": {
            "flavor": "Your victory!",
            "text": "A huge, sentient olive appears to judge your progress. Seeing that you\n"
                    "passed the toll, they descend upon you and hand you your prize with their\n"
                    "olive-ish hands, finally disappearing in a wave of thousands of golden coins.",
            "exits": {},
            "items": ["framework"],
            "enemies": []
        }
    }
    items = {
        "framework": {
            "name": "Schmamework 69",
            "flavor": "Legally distinct, not related to Framework (TM)",
            "type": "potion",
            "description": "The fruits of your labor."
        },
        "silvercharm": {
            "name": "Silver Charm",
            "flavor": "Etched with tiny runes for protection.",
            "type": "armor",
            "hp": 60,
            "description": "Wearing it feels like luck itself clings to you."
        },
        "fang": {
            "name": "Cobra's Fang",
            "flavor": "Still imbued with heavy poison.",
            "type": "weapon",
            "description": "Can be mounted to a stick and used to cause huge damage.",
            "min_dmg": 10,
            "max_dmg": 20
        },
        "coolsword": {
            "name": "Really Cool Sword",
            "flavor": "This is the most badass sword you've ever seen, and you've seen a lot.",
            "type": "weapon",
            "description": "A hilt encrusted with rubies, and a copper-coated blade that will\n"
                           "easily inspire fear in your enemies.",
            "min_dmg": 12,
            "max_dmg": 25
        },
        "datestamp": {
            "name": "Rotating date stamp",
            "flavor": "It's one of those rotating stamp things you find at the bank.",
            "type": "junk",
            "description": "Clearly used many times, but now abandoned. It's completely\n"
                           "dried out - you won't be able to use it any time soon."
            },
        "brandy": {
            "name": "Aged Brandy",
            "flavor": "It's some low quality brandy left in a cabinet for decades",
            "type": "potion",
            "description": "This would likely be worth some decent coin if sold to one who\n"
                           "understood the worth of aged alcohol, especially with this\n"
                           "much time put in. Quite a rare find."
        },
        "honey": {
            "name": "Jar of Honey",
            "flavor": "Super fresh raw honey collected from underground bees (???)",
            "type": "potion",
            "description": "So good that it would give you a jolt of energy unrivaled\n"
                           "by even that of pure alcohol."
        },
        "rottentomato": {
            "name": "Rotten, moldy tomato",
            "flavor": "A tomato that clearly hasn't been touched for months.",
            "type": "junk",
            "description": "This further confirms your suspicion that whoever lives\n"
                           "here REALLY doesn't understand modern food safety laws."
        },
        "moldybaguette": {
            "name": "Moldy Baguette",
            "flavor": "It's been here for two or three weeks.",
            "type": "junk",  # potion, armor, weapon, jewelry, junk
            "description": "A certain red-haired pear dropped this on her way to starting\n"
                           "on this quest a few weeks ago. There are drool stains and teeth marks.\n"
                           "Please don't eat this if you don't want to turn sillier than you are.",
        },
        "gruehair": {
            "name": "Grue Hair",
            "flavor": "It's simply a distinctive hair fallen off a grue.",
            "type": "junk",
            "description": "This is a good sign that a grue is nearby, but that's always the case,\n"
                           "so it means nothing at all. Be ready to fight a grue."
        },
        "gruepaw": {
            "name": "Grue's Paw",
            "flavor": "It's a grue's paw, with its claws permanently extended.",
            "type": "weapon",
            "min_dmg": 1,
            "max_dmg": 12,
            "description": "The grue doesn't part with its hand very easily. But I suppose a human\n"
                           "probably wouldn't part with its hand very easily either."
        },
        "grueshield": {
            "name": "Grue's Hide",
            "flavor": "It's the tough hide of a Grue.",
            "type": "armor",
            "hp": 40,
            "description": "The grue doesn't part with its hand very easily. But I suppose a human\n"
                           "probably wouldn't part with its hand very easily either."
        },
        "fists": {
            "name": "Fists",
            "flavor": "Your bare fists.",
            "type": "weapon",
            "max_dmg": 10,
            "min_dmg": 3,
            "description": "You have poor form, but your sheer strength seems to make up for it for the moment."
        },
        "clothes": {
            "name": "Plainclothes",
            "flavor": "Your average every day clothes.",
            "type": "armor",
            "hp": 30,
            "description": "The clothes of a jester. Just like you! What a coincidence"
        }
    }
    enemies = {
        "ancient_grue": {
            "name": "Ancient Grue",
            "hitpoints": 80,
            "attacktext": "The Ancient Grue emits a roar and swipes violently, dealing ",
            "misstext": "The Grue's claws narrowly miss you, tearing the air itself.",
            "damage": 10,
            "killtext": "You have been eaten by a Grue.",
            "flavor": "A beast older than greed itself, awakened by the sound of coin on stone.",
            "drops": ["gruehair"]
        },
        "ghost": {
            "name": "Miner's Ghost",
            "hitpoints": 100,
            "attacktext": "The ghost floats into you, somehow damaging you for ",
            "misstext": "The ghost floats into you.",
            "damage": 1,
            "killtext": "You become a ghost. How ironic.",
            "flavor": "It's clearly angry about being killed due to a poor manager.",
            "drops": []
        },
        "cobra": {
            "name": "Cobra",
            "hitpoints": 8, 
            "attacktext": "The cobra strikes and bites your ankle powerfully, causing ",
            "misstext": "The cobra sinks its fangs into thin air.",
            "damage": 20,
            "killtext": "You quickly lose consciousness from the paralyzing venom, never regaining it.",
            "flavor": "It moves faster than you can keep track of.",
            "drops": ["fang"]
        },
        "grue": {
            "name": "Grue",
            "hitpoints": 20,
            "attacktext": "The Grue swings its hairy fist, dealing ",
            "misstext": "The Grue swings and misses you by a single grue hair.",
            "damage": 5,
            "killtext": "You have been eaten by a Grue",
            "flavor": "It's just doing grue things.",
            "drops": ["gruehair", "gruepaw", "grueshield"]
        },
        "rat": {
            "name": "Rat",
            "hitpoints": 5,
            "attacktext": "The rat bit your shin while you weren't looking, dealing ",
            "misstext": "The rat closes its teeth on thin air",
            "damage": 2,
            "killtext": "The rat overwhelms you and knocks you over.",
            "flavor": "It's perusing the rotten tomatoes.",
            "drops": []
        },
        "guard": {
            "name": "Clockwork Guard",
            "hitpoints": 30,
            "attacktext": "The mechanical guard slams its metal arm into you for ",
            "misstext": "The guard's gears jam, missing its strike.",
            "damage": 8,
            "killtext": "You are crushed beneath the guard's cold iron frame.",
            "flavor": "Old security machines - still somehow alive, powered by unseen cables.",
            "drops": []
        },
    }
    return player, rooms, items, enemies


def help():
    print("Welcome to Greednought! \n"
          "look: Take another look around \n"
          "get/take item: Pick an item up \n"
          "use item: Activate a consumable item \n"
          "drop item: Get rid of an item \n"
          "equip item: Put on armor or hold a weapon \n"
          "examine item: Look closer at an item \n"
          "inventory/inv: View your backpack \n"
          "go north/east/south/west/up/down: Move around \n"
          "attack creature: Swing at a creature \n"
          "attack: Type alone to get a battle overview \n"
          "run: Escape a battle \n"
          "win: Naturally... \n"
          "quit: Why would you ever want to do that?\n"
          "g: Repeat last command"
          )

def get_item(item, player, rooms, items, enemies):
    if item in rooms[player["location"]]["items"]:
        player["inventory"].append(item)
        rooms[player["location"]]["items"].remove(item)
        print(f"Picked up a {items[item]['name']}.")
    else:
        print(f"You can't see any {item} here")
    enemy_phase(player, rooms, items, enemies)

def use_item(item, player, rooms, items, enemies):
    if item not in items:
        print("That item does not exist.")
        return
    if items[item]["type"] == "potion":
        if item == "brandy":
            player["hp"] = min(player["hp"] + 15, player["max_hp"])
            print("The brandy stings the inside of your mouth and heals you for 15 HP.")
            player["inventory"].remove(item)
        elif item == "honey":
            player["hp"] = min(player["hp"] + 15, player["max_hp"])
            print("The honey gives you a warm feeling inside as you drink it. +15HP.")
            player["inventory"].remove(item)
        elif item == "framework":
            print("You eat the laptop. Yummy.")
            sys.exit(0)
    else:
        print("You can't use this item! Try 'equip'ping it?")

    enemy_phase(player, rooms, items, enemies)

def drop_item(item, player, rooms, items, enemies):
    if item in player["inventory"]:
        if item == player["weapon"]:
            print(f"Unequipped your {item}\n")
            equip_item("fists", player, rooms, items, enemies)
        if item == player["armor"]:
            print(f"Unequipped your {item}\n")
            equip_item("clothes", player, rooms, items, enemies)
        rooms[player["location"]]["items"].append(item)
        player["inventory"].remove(item)
        print(f"You dropped the {items[item]['name']}.")
    else:
        print("You don't have that item.")
        
    enemy_phase(player, rooms, items, enemies)

def equip_item(item, player, rooms, items, enemies):
    if item not in items:
        print("That item does not exist.")
        return
    if items[item]["type"] == "weapon":
        player["weapon"] = item
        player["min_dmg"] = items[item]["min_dmg"]
        player["max_dmg"] = items[item]["max_dmg"]
        print(f"Equipped your {items[item]['name']}.")
    elif items[item]["type"] == "armor":
        player["armor"] = item
        player["max_hp"] = items[item]["hp"]
        if player["hp"] > player["max_hp"]:
            player["hp"] = player["max_hp"]
        print(f"Equipped your {items[item]['name']}.")
    else:
        print("That's not armor or a weapon. Maybe you meant to 'use' this?")
        
    enemy_phase(player, rooms, items, enemies)

def describe_room(location, player, rooms, items, enemies):
    print(f"You are in {rooms[location]['flavor'].lower()}\n")
    print(rooms[location]["text"])
    
    if rooms[location]["items"]:
        for i in rooms[location]["items"]:
            print(f"There is a {i} here. {items[i]['flavor']}")
    print("")
    
    for direction, target in rooms[location]["exits"].items():
        if direction == "up":
            print(f"Above you: {rooms[target]['flavor']}")
        elif direction == "down":
            print(f"Below you: {rooms[target]['flavor']}")
        else:
            print(f"To your {direction}: {rooms[target]['flavor']}")
        
def move_player(direction, player, rooms, items, enemies):
    location = player["location"]
    if direction not in rooms[location]["exits"]:
        print("You can't go that way.")
        return
    
    next_room = rooms[location]["exits"][direction]
    player["location"] = next_room
    print(f"You move {direction}.")
    describe_room(next_room, player, rooms, items, enemies)
    check_location(next_room, player, rooms, items, enemies)
    
    base_enemies = rooms[next_room].get("enemies", [])
    if base_enemies:
        rooms[next_room]["active_enemies"] = []
        for i, enemy_type in enumerate(base_enemies):
            inst = {
                "id": f"{enemy_type}_{i+1}",
                "type": enemy_type,
                "hp": enemies[enemy_type]["hitpoints"]
            }
            rooms[next_room]["active_enemies"].append(inst)
            
        player["battle"] = rooms[next_room]["active_enemies"]
        for i in player["battle"]:
            print(f"- A {enemies[i['type']]['name']} appears! {enemies[i['type']]['flavor']} [{i['id']}]")
    else:
        rooms[next_room]["active_enemies"] = []
        player["battle"] = []
    
def attack(target_name, player, rooms, items, enemies):
    if not player["battle"]:
        print("You aren't in combat.")
        return
    
    if target_name.strip() == "":
        print("Enemies present:")
        for e in player["battle"]:
            etype = enemies[e["type"]]
            print(f"- {etype['name']} (HP: {e['hp']}) [{e['id']}]")
        return
    
    target = None
    for e in player["battle"]:
        if target_name == e["id"] or target_name == e["type"]:
            target = e
            break
    if not target:
        print(f"There is no {target_name} here")
        return
    
    dmg = random.randint(player["min_dmg"], player["max_dmg"])
    target["hp"] -= dmg
    print(f"You strike the {enemies[target['type']]['name']} ({target['id']}) for {dmg} damage.")
    
    if target["hp"] <= 0:
        print(f"You defeat the {enemies[target['type']]['name']} ({target['id']}).")
        drops = enemies[target['type']]['drops']
        if drops:
            print(f"It dropped: {', '.join(d for d in drops)}")
            for drop in drops:
                rooms[player["location"]]["items"].append(drop)
        player["battle"].remove(target)
        rooms[player['location']]['enemies'].remove(target['type'])
        
    enemy_phase(player, rooms, items, enemies)

def enemy_phase(player, rooms, items, enemies):
    if not player["battle"]:
        return
    
    total_damage = 0
    for e in list(player["battle"]): # make a copy to avoid it changing?
        etype = enemies[e["type"]]
        if e["hp"] > 0:
            if random.random() < 0.75:
                dmg = etype["damage"]
                total_damage += dmg
                print(f"{etype['attacktext']}{dmg} damage! ({e['id']})")
                player["hp"] -= dmg
                if player["hp"] <= 0:
                    print(etype['killtext'])
                    sys.exit(0)
            else:
                print(f"{etype['misstext']} ({e['id']})")
                
    if total_damage > 0:
        print(f"Player: [{player['hp']}/{player['max_hp']}]")

def run(player, rooms, items, enemies):
    if not player["battle"]:
        print("There is nothing to run from.")
        
    if random.random() < 0.5:
        print("You successfully escape!")
        player["battle"] = []
    
    print("You failed to escape.")
    enemy_phase(player, rooms, items, enemies)

def check_location(location, player, rooms, items, enemies):
    if location == "tavern":
        print("Game Over! Neutral ending...?")
        sys.exit(0)
    elif location == "gamble":
        print("A man would like to gamble with you. He proposes a 5 coin toss-up.")
        choice = input("[Y/N]? > ")
        if choice.lower() == "y":
            flip = random.randint(0, 1)
            if flip == 0:
                player["coins"] -= 5
                print(f"Bad luck! You lost 5 of your coins. You're down to {player['coins']}")
                print("Man (?): Come back if you ever want to try your luck again :3")
            else:
                player["coins"] += 5
                print(f"You win! You're up 5 coins, with your total now being {player['coins']}")
                print("(the man sighs): Maybe you'll come back another time and give me another chance")
    elif location == "death":
        sys.exit(0)
    elif location == "gate":
        player["coins"] -= 5
    elif location == "doors":
        print("The clockwork puppets offer to help you through the room,")
        print("but they request payment of 50 coins for their guidance. Oblige?")
        choice = input("[Y/N] > ")
        if choice.lower() == "y":
            if player["coins"] < 50:
                print("You don't have enough coins for that!")
                return
            player["coins"] -= 50
            print("The guards speak:")
            print("> Through the marble door, you will find truth, and loot with it.")
            print("> Through the ivy door, you will find only lies, yet move quickly.")
            print("> The wooden door holds only death, and nothing else.")
    elif location == "mud":
        player["coins"] += 5
    elif location == "rockfall":
        choice = input("Dig for coins? [Y/N]")
        if choice.lower() == "y":
            print("You find 10 coins buried in the well, but a rock falls on your")
            print("head, dealing 4 damage to you.")
            player["coins"] += 10
            player["hp"] -= 4
    elif location == "gambleturtle":
        print("Pick a wager (over 5 coins)")
        wager = int(input("...> "))
        print("The turtle rolled... ", end = "")
        turtleroll = random.randint(1, 6)
        yourroll = random.randint(1, 6)
        time.sleep(1)
        print(turtleroll)
        print("You rolled... ", end = "")
        time.sleep(1)
        print(yourroll)
        if turtleroll > yourroll:
            player["coins"] -= wager
            print("The turtle chuckles, takes your coins, then retracts into his shell.")
        else:
            player["coins"] += wager
            print("The turtle is mad and retracts into his shell, spitting out the coins owed.")
    elif location == "elevator":
        player["coins"] -= 5
    elif location == "smeltery":
        print("Attempt to retrieve the coins?")
        choice = input("[Y/N]...> ")
        if choice.lower() == "y":
            if random.random() > 0.2:
                print("You make it across and grab 20 coins off a tray!")
                player["coins"] += 20
            else:
                print("You trip and fall into a vat of boiling gold. 20 damage.")
                player["hp"] -= 20
    elif location == "barracks":
        player["coins"] += 1
    elif location == "airvent":
        player["coins"] -= 2
    elif location == "shrine":
        print("Give, or take?")
        choice = input("[G/T] ...>")
        if choice.lower() == "g":
            print("You give a single coin and your body is flooded with warmth.")
            player["hp"] = player["max_hp"]
        elif choice.lower() == "t":
            print("You are struck by unseen hands, a punishment for meddling with the gods.")
            player["hp"] = (player["max_hp"] / 2)
    elif location == "cranklift":
        if random.random() > 0.5:
            time.sleep(2)
            print("You make it down the elevator safely.")
        else:
            time.sleep(2)
            print("The elevator runs away from you and slams against the ground, dealing 5 HP")
            player["hp"] -= 5
            
    elif location == "toll":
        time.sleep(5)
        if player["coins"] >= 50:
            print("You insert the coins, and the gate lets you pass.")
            player["coins"] -= 50
        else:
            print("You insert all you have, but it does not total 50. The gate grows")
            print("a pair of massive arms, then crushes you against the ground for even")
            print("thinking you might be able to get past. GAME OVER.")
            sys.exit(0)
        pass

def input_parser(cmd_in, player, rooms, items, enemies):
    global last_input
    command = cmd_in.lower()
    if command != "g":
        last_input = command

    fail = [
        "What are you trying to do?", "You screwed SOMETHING up.", "You feel a disturbance in the Force.",
        "You feel a disturbance in the Schwartz.", "Do better", "Something's wrong, but you don't know what...",
        "How do you mess up this bad??", "Work on your typing skills!"
    ]
    random.shuffle(fail)

    if command == "g":
        command = last_input
    
    if command == "help":
        help()

    elif command == "look":
        describe_room(player["location"], player, rooms, items, enemies)
        
    elif command.startswith("get") or command.startswith("take"):
        try:
            if command == "get" or command == "get ":
                print("What are you trying to get?")
                return
            get = command.split(" ", 1)[1]
            get_item(get, player, rooms, items, enemies)
        except Exception:
            print(fail[1])

    elif command.startswith("use"):
        try:
            if command == "use" or command == "use ":
                print("What are you trying to use?")
                return
            use = command.split(" ", 1)[1]
            use_item(use, player, rooms, items, enemies)
        except Exception:
            print(fail[1])

    elif command.startswith("drop"):
        try:
            if command == "drop" or command == "drop ":
                print("Drop what?")
                return
            drop = command.split(" ", 1)[1]
            drop_item(drop, player, rooms, items, enemies)
        except Exception:
            print(fail[1])

    elif command.startswith("equip"):
        try:
            if command == "equip" or command == "equip ":
                print("Equip what?")
                return
            equip = command.split(" ", 1)[1]
            equip_item(equip, player, rooms, items, enemies)
        except Exception:
            print(fail[1])

    elif command.startswith("examine"):
        try:
            if command == "examine" or command == "examine ":
                print("What are you examining?")
                return
            item = command.split(" ", 1)[1]
            if item in player["inventory"]:
                print(f"It's a {items[item]['name']}.")
                print(items[item]["flavor"])
                print(items[item]["description"])
            else:
                print("You don't have that item.")
        except Exception:
            print(fail[1])

    elif command == "inventory" or command == "inv":
        print(f"Player | HP: {player['hp']}/{player['max_hp']} | Coins: {player['coins']}")
        print(f"Armor: {player['armor']} | Weapon: {player['weapon']} ({player['min_dmg']}-{player['max_dmg']} dmg)\n")
        print("Your backpack contains:")
        for i in player["inventory"]:
            print(f"{i}: {items[i]['flavor']}")

    elif command.startswith("go"):
        if command == "go" or command == "go ":
                print("I can't tell where you want to go.")
                return
        direction = command.split(" ", 1)[1]
        if not player["battle"]:
            move_player(direction, player, rooms, items, enemies)
        else:
            print("You can't just leave, you're in a fight!\n")

    elif command.startswith("attack"):
        parts = command.split(" ", 1)
        target = parts[1] if len(parts) > 1 else ""
        attack(target, player, rooms, items, enemies)
            
    elif command == "run":
        run(player, rooms, items, enemies)

    elif command == "win":
        win = [
            "It won't be that easy...", "What about alcohol?", "Naturally.", "Yes, but not at this game",
            "Lose!", "Six seven or something idk i hate slang", "Peanut butter jelly time!",
            "badgers badgers badgers badgers MUSHROOM MUSHROOM", "Do the work first!", "nuh uh", "Pong!",
            "COOL FLAVOR TEXT", "FUNNY REPLY", "Traceback (most recent call last):"
        ]
        random.shuffle(win)
        print(win[0])

    elif command == "quit" or command == "exit":
        print("You give up. Don't worry... you'll be back...")
        sys.exit(0)

    elif command == "hi" or command == "hello":
        print("Good afternoon.")

    elif command == "i like men":
        print("Me too")

    else:
        print(f"I don't understand. {fail[1]}")

def game_loop(player, rooms, items, enemies):
    first_time = True
    while True:
        location = str(player["location"])
        if first_time:
            first_time = False

        command = input("\n...> ")
        input_parser(command, player, rooms, items, enemies)
        if player["location"] != location:
            first_time = True
            location = str(player["location"])
        
        if player['hp'] <= 0:
            print("Your vision fades to black. You Died.")
            sys.exit(0)

def main():
    sys.excepthook = handle_exit
    player, rooms, items, enemies = init_game()
    print("Welcome to Greednought!")
    print("Type help if you need assistance.\n")
    describe_room(player["location"], player, rooms, items, enemies)
    game_loop(player, rooms, items, enemies)

if __name__ == "__main__":
    main()
