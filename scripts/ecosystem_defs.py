# SPDX-License-Identifier: MIT
import random

try:
    from theme import num
except ImportError:
    def num(value, places=2):
        val = ("%." + str(places) + "f") % float(value)
        if "." in val:
            val = val.rstrip("0").rstrip(".")
        return "0" if val in ("", "-0") else val


# WHY: Ordered dark-outline -> deep-shadow -> midtone -> highlight -> eye-detail -> specular for lossless underfill merging.
ECO_PALETTE = {
    "O": "#271306",
    "k": "#334155",
    "D": "#5c2408",
    "n": "#422006",
    "v": "#581c87",
    "F": "#064e3b",
    "N": "#1e3a8a",
    "R": "#9a3412",
    "u": "#713f12",
    "V": "#be123c",
    "J": "#047857",
    "B": "#2563eb",
    "I": "#0284c7",
    "q": "#9333ea",
    "g": "#64748b",
    "r": "#c2410c",
    "m": "#b45309",
    "t": "#a16207",
    "P": "#ea580c",
    "M": "#d97706",
    "A": "#10b981",
    "H": "#f43f5e",
    "G": "#f59e0b",
    "c": "#eab308",
    "p": "#fb923c",
    "Y": "#34d399",
    "y": "#84cc16",
    "U": "#38bdf8",
    "x": "#c084fc",
    "s": "#94a3b8",
    "K": "#fda4af",
    "S": "#fde047",
    "h": "#fde68a",
    "Z": "#7dd3fc",
    "T": "#a7f3d0",
    "l": "#cbd5e1",
    "L": "#fef3c7",
    "X": "#e0f2fe",
    "C": "#fffbeb",
    "E": "#0f172a",
    "W": "#ffffff",
}

LAYER_ORDER = tuple(ECO_PALETTE.keys())
LAYER_RANK = {ch: idx for idx, ch in enumerate(LAYER_ORDER)}

ANIMAL_SPECIES = (
    "shiba_dog",
    "red_fox",
    "calico_cat",
    "cottontail_rabbit",
    "red_squirrel",
    "tawny_owl",
    "mallard_duck",
    "hedgehog",
    "spotted_deer",
    "tree_frog",
    "azure_bluebird",
)

ANIMATION_NAMES = (
    "walk",
    "trot",
    "gallop",
    "hop",
    "binky_leap",
    "graze_nibble",
    "sniff_ground",
    "drink_ripple",
    "groom_paw",
    "scratch_ear",
    "stretch_bow",
    "yawn",
    "tail_wag_happy",
    "ear_perk_alert",
    "stargaze_meteor",
    "chase_butterfly",
    "boop_firefly",
    "pounce_play",
    "belly_roll",
    "happy_spin",
    "shake_fur",
    "crouch_stalk",
    "perch_sway",
    "sleep_curl_breathe",
    "sun_bask",
)

PROP_NAMES = (
    "sunflower_cluster",
    "lavender_tuft",
    "chamomile_patch",
    "dandelion_puff",
    "clover_bed",
    "wheat_sheaf",
    "glow_mushroom_blue",
    "amanita_mushroom",
    "mossy_stone",
    "hollow_oak_log",
    "acorn_stash",
    "wood_signpost",
    "provence_stone_wall",
    "dew_puddle",
    "lilypad_lotus",
    "stream_brook",
    "pebble_bank",
    "mini_footbridge",
    "cattail_reeds",
    "splash_fountain",
    "iron_lantern",
    "straw_nest",
    "wood_birdhouse",
    "oak_barrel",
    "berry_bush",
    "garden_bench",
    "cypress_alcove",
    "crystal_geode",
    "starlight_windchime",
    "weathervane",
    "firefly_jar",
    "wild_rose_bush",
)

PART_KEYS = ("lb", "tl", "bd", "lf", "hd", "ew")
PART_SHORT = {"rig": "r", "lb": "b", "tl": "t", "bd": "d", "lf": "f", "hd": "h", "ew": "e", "sh": "s"}

ANIMAL_CATALOG = {
    "shiba_dog": {
        "shadow": (10.5, 2.2),
        "nocturnal": False,
        "flying": False,
        "joints": {"lb": (-5, -5), "tl": (-8, -10), "bd": (0, 0), "lf": (5, -5), "hd": (6, -11), "ew": (6, -16)},
        "parts": {
            "bd": (-9, -12, [
                "..OOOOOOOOOO.....",
                ".OLLLLGGGGGBBOO..",
                "OGGGGGGGGGGBBSBO.",
                "OMMMMMMGGGGNBBNO.",
                "OMMMMMMMGGCCCCCO.",
                ".OmmmmmCCCCCCCCO.",
                "..OOOOOOOOOOOOO..",
            ]),
            "hd": (-3, -6, [
                ".OOLLLLOO...",
                "OGGGGGGLGO..",
                "OGGCGGCGGGO.",
                "OGWEGGWECEEO",
                "OPCCCCCCCEEO",
                ".OCCCKCCCCO.",
                "..OOOOOOOO..",
            ]),
            "ew": (-3, -4, [
                "OO....OO.",
                "OMO..OMO.",
                "OMKO.OMKO",
                "OGLO.OGLO",
            ]),
            "tl": (-6, -6, [
                "..OOOO.",
                ".OCCLO.",
                "OCCGGO.",
                "OCGmO..",
                ".OOOO..",
            ]),
            "lf": (-2, 0, [
                "OMMO",
                "OMCO",
                "OCCO",
                "OOO.",
            ]),
            "lb": (-2, 0, [
                "OmMO",
                "OmCO",
                "OCCO",
                ".OOO",
            ]),
        },
    },
    "red_fox": {
        "shadow": (11.2, 2.1),
        "nocturnal": True,
        "flying": False,
        "joints": {"lb": (-5, -5), "tl": (-8, -9), "bd": (0, 0), "lf": (5, -5), "hd": (6, -11), "ew": (6, -16)},
        "parts": {
            "bd": (-9, -11, [
                "..OOOOOOOOOOO....",
                ".OrrrrPPPPPPPOO..",
                "ORRRRRrrrrPPPCCO.",
                "ORRRRRRrrrCCCCCO.",
                ".ODDRRRRCCCCCCCO.",
                "..OOOOOOOOOOOOO..",
            ]),
            "hd": (-3, -6, [
                ".OOrrrrOO....",
                "OrrrrPPPPO...",
                "OrPWErPPCCOO.",
                "OrPEECCCCCPEO",
                ".OCCCCCCCCOO.",
                "..OOOOOOOO...",
            ]),
            "ew": (-3, -5, [
                "OE....OE.",
                "ODO..ODO.",
                "OrKO.OrKO",
                "OPCO.OPCO",
            ]),
            "tl": (-10, -5, [
                "..OOOOOOO..",
                ".OWWCCPPPO.",
                "OWWCCCrrrRO",
                "OCCCrrrrRO.",
                ".OOOOOOOO..",
            ]),
            "lf": (-2, 0, [
                "OrPO",
                "ODDO",
                "OEEO",
                "OOO.",
            ]),
            "lb": (-2, 0, [
                "ORrO",
                "ODDO",
                "OEEO",
                ".OOO",
            ]),
        },
    },
    "calico_cat": {
        "shadow": (9.6, 2.0),
        "nocturnal": False,
        "flying": False,
        "joints": {"lb": (-5, -5), "tl": (-7, -10), "bd": (0, 0), "lf": (4, -5), "hd": (5, -11), "ew": (5, -16)},
        "parts": {
            "bd": (-8, -11, [
                "..OOOOOOOOOO...",
                ".OkkCCCpppCCO..",
                "OkkkCCCppppCHO.",
                "OCCCCCCppCCCSO.",
                ".OCCCCCCCCCCCO.",
                "..OOOOOOOOOOO..",
            ]),
            "hd": (-3, -6, [
                ".OkkCCppOO.",
                "OkkCCCCppCO",
                "OCJWECJWECO",
                "OCCCCKCCCCO",
                ".OCCCCCCCO.",
                "..OOOOOOO..",
            ]),
            "ew": (-3, -4, [
                "OO...OO.",
                "OkO..OpO",
                "OkKO.OpKO",
            ]),
            "tl": (-5, -8, [
                ".OOO..",
                "OkkO..",
                "OCCC..",
                ".OppO.",
                "..OCCO",
                "..OOO.",
            ]),
            "lf": (-2, 0, [
                "OpCO",
                "OCCO",
                "OWWO",
                "OOO.",
            ]),
            "lb": (-2, 0, [
                "OkCO",
                "OCCO",
                "OWWO",
                ".OOO",
            ]),
        },
    },
    "cottontail_rabbit": {
        "shadow": (8.6, 1.9),
        "nocturnal": False,
        "flying": False,
        "joints": {"lb": (-3, -4), "tl": (-7, -7), "bd": (0, 0), "lf": (4, -4), "hd": (4, -10), "ew": (3, -15)},
        "parts": {
            "bd": (-7, -10, [
                "..OOOOOOOO...",
                ".OttthhhhOO..",
                "OuuuutthhhCO.",
                "OuuuutthCCCO.",
                ".OuuuCCCCCCO.",
                "..OOOOOOOOO..",
            ]),
            "hd": (-3, -5, [
                ".OthhhhOO..",
                "OtthWEEhCO.",
                "OtthEEEhCKO",
                ".OCCCCCCCO.",
                "..OOOOOOO..",
            ]),
            "ew": (-2, -7, [
                ".OO..OO.",
                "OtuO.OtuO",
                "OtKO.OtKO",
                "OtKO.OtKO",
                "OthO.OthO",
                ".OO..OO.",
            ]),
            "tl": (-4, -3, [
                ".OOO.",
                "OWWCO",
                "OCCCO",
                ".OOO.",
            ]),
            "lf": (-2, 0, [
                "OthO",
                "OCCO",
                "OOO.",
            ]),
            "lb": (-2, 0, [
                "OuuO",
                "OthCO",
                "OCCCCO",
                ".OOOO.",
            ]),
        },
    },
    "red_squirrel": {
        "shadow": (8.2, 1.8),
        "nocturnal": False,
        "flying": False,
        "joints": {"lb": (-3, -4), "tl": (-6, -8), "bd": (0, 0), "lf": (3, -4), "hd": (4, -10), "ew": (4, -14)},
        "parts": {
            "bd": (-6, -10, [
                "..OOOOOOO...",
                ".OrrrPPPPO..",
                "ORRRrrrPLCO.",
                "ORRRrrCCCCO.",
                ".ODDRCCCCO..",
                "..OOOOOOO...",
            ]),
            "hd": (-2, -5, [
                ".OrrPPPOO.",
                "OrrPWEEPCO",
                "OrrPEEEPLO",
                ".OCCCCCCO.",
                "..OOOOOO..",
            ]),
            "ew": (-2, -4, [
                "OO..OO",
                "ORO.ORO",
                "OPO.OPO",
            ]),
            "tl": (-7, -9, [
                "..OOOOO.",
                ".OPPLLLO",
                "OrrrrPPO",
                "ORRRrrPO",
                "ODDRrrO.",
                ".OOOOO..",
            ]),
            "lf": (-1, 0, [
                "OPO",
                "OrO",
                "OOO",
            ]),
            "lb": (-2, 0, [
                "ORO.",
                "OrPO",
                "OOOO",
            ]),
        },
    },
    "tawny_owl": {
        "shadow": (8.8, 1.9),
        "nocturnal": True,
        "flying": True,
        "joints": {"lb": (-2, -3), "tl": (-5, -5), "bd": (0, 0), "lf": (2, -3), "hd": (1, -12), "ew": (-1, -10)},
        "parts": {
            "bd": (-5, -12, [
                "..OOOOOOO..",
                ".OuuutttOO.",
                "OnnuutthhCO",
                "OnnuuhChChO",
                "OnnuuhChCCO",
                ".OnnuCCCCO.",
                "..OOOOOOO..",
            ]),
            "hd": (-4, -6, [
                ".OOOOOOOOO.",
                "OthhCCChhtO",
                "OhcWEccWEhO",
                "OhcEEOScEhO",
                ".OCCCCSCCO.",
                "..OOOOOOO..",
            ]),
            "ew": (-4, -2, [
                ".OOOOOO..",
                "OnnuuttO.",
                "OnnuutthO",
                "OnnuuttO.",
                ".OOOOOO..",
            ]),
            "tl": (-4, -2, [
                "OOOOO",
                "OnuhO",
                "OnuOO",
            ]),
            "lf": (-1, 0, [
                "OtO",
                "OSO",
                "OOO",
            ]),
            "lb": (-1, 0, [
                "OuO",
                "OSO",
                "OOO",
            ]),
        },
    },
    "mallard_duck": {
        "shadow": (9.8, 2.0),
        "nocturnal": False,
        "flying": False,
        "joints": {"lb": (-2, -4), "tl": (-8, -8), "bd": (0, 0), "lf": (2, -4), "hd": (5, -11), "ew": (-2, -9)},
        "parts": {
            "bd": (-8, -10, [
                "...OOOOOOOOO...",
                "..OggggllWWOO..",
                ".OgggglllmmRRO.",
                "OggggllllmmmRRO",
                ".OllllCCCCCCCO.",
                "..OOOOOOOOOOO..",
            ]),
            "hd": (-2, -6, [
                ".OFFFFOO....",
                "OFJJJAAOO...",
                "OFJWEAAYOOO.",
                "OFJEEAAYSSPO",
                ".OJJAAYPPPPO",
                "..OOOO.OOOO.",
            ]),
            "ew": (-4, -2, [
                ".OOOOOOO.",
                "OgggBBWWO",
                "OggNNBWWO",
                ".OOOOOOO.",
            ]),
            "tl": (-4, -4, [
                "OO...",
                "OkOO.",
                "OkkCO",
                ".OOOO",
            ]),
            "lf": (-2, 0, [
                ".OPO.",
                ".OPO.",
                "OPPPO",
                "OOOOO",
            ]),
            "lb": (-2, 0, [
                ".OPO.",
                ".OPO.",
                "OPPPO",
                "OOOOO",
            ]),
        },
    },
    "hedgehog": {
        "shadow": (8.4, 1.8),
        "nocturnal": True,
        "flying": False,
        "joints": {"lb": (-3, -3), "tl": (-7, -5), "bd": (0, 0), "lf": (3, -3), "hd": (5, -6), "ew": (4, -9)},
        "parts": {
            "bd": (-7, -9, [
                "..OnOnOnOnO..",
                ".OnLunLunLuO.",
                "OnuLuunLuutnO",
                "OnuutLtutthhO",
                "OnuutthhhhhCO",
                ".OCCCCCCCCCO.",
                "..OOOOOOOOO..",
            ]),
            "hd": (-2, -4, [
                ".OthhhOO...",
                "OthWEEhhOO.",
                "OthEEEhhCEO",
                ".OCCCChKKO.",
                "..OOOOOOO..",
            ]),
            "ew": (-2, -3, [
                ".OO.",
                "OuKO",
                "OhKO",
            ]),
            "tl": (-3, -2, [
                "OOO",
                "OutO",
                ".OO.",
            ]),
            "lf": (-1, 0, [
                "OtO",
                "OKO",
                "OOO",
            ]),
            "lb": (-1, 0, [
                "OuO",
                "OKO",
                "OOO",
            ]),
        },
    },
    "spotted_deer": {
        "shadow": (11.5, 2.2),
        "nocturnal": False,
        "flying": False,
        "joints": {"lb": (-6, -8), "tl": (-9, -13), "bd": (0, 0), "lf": (5, -8), "hd": (6, -15), "ew": (5, -20)},
        "parts": {
            "bd": (-9, -15, [
                "..OOOOOOOOOOO...",
                ".OmmmCWmmCWppO..",
                "ORmmmmmmppCWppO.",
                "ORRmmmmppppCCCO.",
                ".ORRmmmCCCCCCCO.",
                "..OOOOOOOOOOOO..",
            ]),
            "hd": (-2, -7, [
                ".OmmpppOO...",
                "OmmpppCCOO..",
                "OmpWEppCCEO.",
                "OmpEEppCCCEO",
                "OmmCCCCCKCO.",
                "OmmOOOOOOO..",
                "OmppO.......",
            ]),
            "ew": (-3, -5, [
                "OD...OD..",
                "OLO.OOLO.",
                "OmKO.OmKO",
                ".OO...OO.",
            ]),
            "tl": (-4, -4, [
                ".OOO.",
                "OmmWO",
                "OCCWO",
                ".OOO.",
            ]),
            "lf": (-2, 0, [
                "OmO",
                "OpO",
                "OpO",
                "OpO",
                "OpO",
                "OpO",
                "ODO",
                "OEO",
            ]),
            "lb": (-2, 0, [
                "ORO",
                "OmO",
                "OmO",
                "OpO",
                "OpO",
                "OpO",
                "ODO",
                "OEO",
            ]),
        },
    },
    "tree_frog": {
        "shadow": (7.6, 1.7),
        "nocturnal": True,
        "flying": False,
        "joints": {"lb": (-3, -3), "tl": (-5, -4), "bd": (0, 0), "lf": (3, -3), "hd": (3, -7), "ew": (4, -5)},
        "parts": {
            "bd": (-5, -8, [
                "..OOOOOOO..",
                ".OAAYYYyyO.",
                "OJJAAYYYYSO",
                "OJJAAASSCCO",
                ".OCCCCCCCO.",
                "..OOOOOOO..",
            ]),
            "hd": (-2, -5, [
                ".OPOO.OPOO.",
                "OPWEOOPWEO.",
                "OAYYYYYyyYO",
                "OAAYYYYYYCO",
                ".OCCCCCCCO.",
            ]),
            "ew": (-2, -2, [
                ".OOOO.",
                "OSCCLO",
                ".OOOO.",
            ]),
            "tl": (-3, -3, [
                ".OOO.",
                "OFJAO",
                "OJAAO",
                ".OOO.",
            ]),
            "lf": (-2, 0, [
                ".OAO.",
                "OPKPO",
                "O.O.O",
            ]),
            "lb": (-2, 0, [
                "OJAO.",
                "OPKPO",
                "O.O.O",
            ]),
        },
    },
    "azure_bluebird": {
        "shadow": (7.4, 1.6),
        "nocturnal": False,
        "flying": True,
        "joints": {"lb": (-1, -3), "tl": (-6, -7), "bd": (0, 0), "lf": (1, -3), "hd": (3, -10), "ew": (-1, -9)},
        "parts": {
            "bd": (-6, -10, [
                "..OOOOOOO..",
                ".ONBBBUUUO.",
                "ONNBBBUrrrO",
                "ONNBBUrpppO",
                ".OCCCCCCCO.",
                "..OOOOOOO..",
            ]),
            "hd": (-2, -5, [
                ".OBUUUOO...",
                "OBBUWEEUO..",
                "OBBUEEEUEEO",
                "OrrppCCCCO.",
                ".OOOOOOOO..",
            ]),
            "ew": (-4, -2, [
                ".OOOOOOO.",
                "ONNBBUUZO",
                "ONNNBUUOO",
                ".OOOOOO..",
            ]),
            "tl": (-5, -3, [
                "OOOOO.",
                "ONNBUO",
                ".ONBOO",
            ]),
            "lf": (-1, 0, [
                "ODO",
                "OEO",
                "OO.",
            ]),
            "lb": (-1, 0, [
                "ODO",
                "OEO",
                ".OO",
            ]),
        },
    },
}

# WHY: 25 GPU-composited animation bindings using ONLY transform + opacity.
ANIM_25 = {
    "walk": {
        "dur": "0.78s",
        "rig": ("k-bob1", "0.39s"),
        "lf": ("k-leg1", "0.78s"),
        "lb": ("k-leg1r", "0.78s"),
        "hd": ("k-nod1", "0.78s"),
        "tl": ("k-wag1", "0.78s"),
        "sh": ("k-sh1", "0.39s"),
    },
    "trot": {
        "dur": "0.46s",
        "rig": ("k-bob2", "0.23s"),
        "lf": ("k-leg2", "0.46s"),
        "lb": ("k-leg2r", "0.46s"),
        "hd": ("k-nod1", "0.46s"),
        "ew": ("k-ear1", "0.46s"),
        "tl": ("k-wag2", "0.46s"),
        "sh": ("k-sh2", "0.23s"),
    },
    "gallop": {
        "dur": "0.38s",
        "rig": ("k-gal", "0.38s"),
        "lf": ("k-leg3", "0.38s"),
        "lb": ("k-leg3r", "0.38s"),
        "hd": ("k-nod2", "0.38s"),
        "ew": ("k-ear2", "0.38s"),
        "tl": ("k-wag3", "0.38s"),
        "sh": ("k-sh3", "0.38s"),
    },
    "hop": {
        "dur": "0.58s",
        "rig": ("k-hop", "0.58s"),
        "lf": ("k-leg2", "0.58s"),
        "lb": ("k-leg2r", "0.58s"),
        "ew": ("k-wing", "0.58s"),
        "tl": ("k-wag1", "0.58s"),
        "sh": ("k-sh3", "0.58s"),
    },
    "binky_leap": {
        "dur": "0.86s",
        "rig": ("k-binky", "0.86s"),
        "lf": ("k-leg3", "0.86s"),
        "lb": ("k-kick", "0.86s"),
        "ew": ("k-ear3", "0.86s"),
        "tl": ("k-wag3", "0.43s"),
        "sh": ("k-sh4", "0.86s"),
    },
    "graze_nibble": {
        "dur": "1.32s",
        "bd": ("k-leanf", "1.32s"),
        "hd": ("k-graze", "0.66s"),
        "ew": ("k-ear1", "1.32s"),
        "tl": ("k-wag1", "0.88s"),
    },
    "sniff_ground": {
        "dur": "0.92s",
        "bd": ("k-leanf", "0.92s"),
        "hd": ("k-sniff", "0.46s"),
        "ew": ("k-ear2", "0.46s"),
        "tl": ("k-wag2", "0.36s"),
    },
    "drink_ripple": {
        "dur": "1.64s",
        "bd": ("k-drinkb", "1.64s"),
        "hd": ("k-drinkh", "1.64s"),
        "tl": ("k-wag1", "1.64s"),
    },
    "groom_paw": {
        "dur": "1.16s",
        "bd": ("k-sit", "1.16s"),
        "lf": ("k-groom", "0.58s"),
        "hd": ("k-groomh", "0.58s"),
        "ew": ("k-ear1", "1.16s"),
    },
    "scratch_ear": {
        "dur": "0.72s",
        "bd": ("k-sit", "0.72s"),
        "lb": ("k-scrat", "0.22s"),
        "hd": ("k-scrath", "0.72s"),
        "ew": ("k-ear3", "0.22s"),
    },
    "stretch_bow": {
        "dur": "2.10s",
        "bd": ("k-bowb", "2.10s"),
        "lf": ("k-bowl", "2.10s"),
        "hd": ("k-bowh", "2.10s"),
        "tl": ("k-wag3", "0.70s"),
    },
    "yawn": {
        "dur": "2.25s",
        "bd": ("k-yawnb", "2.25s"),
        "hd": ("k-yawnh", "2.25s"),
        "ew": ("k-ear2", "2.25s"),
    },
    "tail_wag_happy": {
        "dur": "0.32s",
        "rig": ("k-bob1", "0.32s"),
        "hd": ("k-perk", "1.28s"),
        "ew": ("k-ear1", "0.64s"),
        "tl": ("k-wag4", "0.26s"),
    },
    "ear_perk_alert": {
        "dur": "1.45s",
        "rig": ("k-alert", "1.45s"),
        "hd": ("k-perk", "1.45s"),
        "ew": ("k-ear4", "0.72s"),
        "tl": ("k-wag1", "1.45s"),
    },
    "stargaze_meteor": {
        "dur": "2.50s",
        "bd": ("k-sit", "2.50s"),
        "hd": ("k-star", "2.50s"),
        "ew": ("k-ear1", "2.50s"),
        "tl": ("k-wag1", "1.80s"),
    },
    "chase_butterfly": {
        "dur": "0.64s",
        "rig": ("k-chase", "0.64s"),
        "lf": ("k-bat", "0.64s"),
        "lb": ("k-leg2r", "0.64s"),
        "hd": ("k-star", "0.64s"),
        "ew": ("k-wing", "0.32s"),
        "sh": ("k-sh3", "0.64s"),
    },
    "boop_firefly": {
        "dur": "1.38s",
        "rig": ("k-boop", "1.38s"),
        "hd": ("k-booph", "1.38s"),
        "ew": ("k-ear2", "0.69s"),
        "tl": ("k-wag2", "0.46s"),
    },
    "pounce_play": {
        "dur": "1.18s",
        "rig": ("k-pounce", "1.18s"),
        "lf": ("k-leg3", "1.18s"),
        "lb": ("k-kick", "1.18s"),
        "hd": ("k-nod2", "1.18s"),
        "tl": ("k-wag3", "0.59s"),
        "sh": ("k-sh4", "1.18s"),
    },
    "belly_roll": {
        "dur": "1.68s",
        "rig": ("k-roll", "1.68s"),
        "lf": ("k-leg2", "0.34s"),
        "lb": ("k-leg2r", "0.34s"),
        "tl": ("k-wag2", "0.42s"),
        "sh": ("k-sh2", "0.84s"),
    },
    "happy_spin": {
        "dur": "1.08s",
        "rig": ("k-spin", "1.08s"),
        "lf": ("k-leg2", "0.36s"),
        "lb": ("k-leg2r", "0.36s"),
        "tl": ("k-wag4", "0.27s"),
        "sh": ("k-sh2", "0.54s"),
    },
    "shake_fur": {
        "dur": "0.74s",
        "bd": ("k-shkb", "0.18s"),
        "hd": ("k-shkh", "0.16s"),
        "ew": ("k-ear3", "0.15s"),
        "tl": ("k-wag4", "0.18s"),
    },
    "crouch_stalk": {
        "dur": "1.24s",
        "bd": ("k-stalk", "1.24s"),
        "lf": ("k-leg1", "1.24s"),
        "lb": ("k-leg1r", "1.24s"),
        "hd": ("k-stalkh", "1.24s"),
        "tl": ("k-wag1", "2.48s"),
    },
    "perch_sway": {
        "dur": "2.20s",
        "rig": ("k-sway", "2.20s"),
        "hd": ("k-nod1", "2.20s"),
        "ew": ("k-wing", "1.10s"),
        "tl": ("k-wag1", "2.20s"),
    },
    "sleep_curl_breathe": {
        "dur": "3.20s",
        "bd": ("k-slpb", "3.20s"),
        "hd": ("k-slph", "3.20s"),
        "ew": ("k-slpe", "3.20s"),
        "tl": ("k-slpt", "3.20s"),
        "lf": ("k-slpl", "3.20s"),
        "lb": ("k-slpl", "3.20s"),
    },
    "sun_bask": {
        "dur": "2.90s",
        "bd": ("k-baskb", "2.90s"),
        "hd": ("k-baskh", "2.90s"),
        "ew": ("k-ear1", "2.90s"),
        "tl": ("k-wag1", "2.90s"),
    },
}

PROP_CATALOG = {
    "sunflower_cluster": {
        "kind": "pollen",
        "ox": -8,
        "oy": -18,
        "grid": [
            "....SSS.....SS..",
            "...SGGGS...SGmS.",
            "...SGDFGS..SGGS.",
            "....SSGS....AA..",
            "..SS..A..SS.YA..",
            ".SGGS.YA.SGmJA..",
            "..SS..JA..AAJF..",
            "...T..JA..JAA...",
            "..YA.AYJ.AJAF...",
            "..JA.JAA.JAAF...",
            "...JAJAAJJAF....",
            "...FFJJJJFFF....",
            "..FFFFFFFFFFF...",
        ],
    },
    "lavender_tuft": {
        "kind": "pollen",
        "ox": -7,
        "oy": -15,
        "grid": [
            "..x..q..x..q..",
            ".qx..xq.qx.xq.",
            ".vq..qv.vq.qv.",
            "..q..x...q..x.",
            "..v..q..vq.qv.",
            "..A..A...A..A.",
            ".TYA.YA.AY.AYT",
            "..JA.JA.AJ.AJ.",
            "..JJAAJAAJJAF.",
            "...FFJJJJFFF..",
            "..FFFFFFFFFF..",
        ],
    },
    "chamomile_patch": {
        "kind": "pollen",
        "ox": -8,
        "oy": -11,
        "grid": [
            "..WCW....WCW...",
            ".WCSCW..WCSCW..",
            "..WCW..WCW.WCW.",
            "...A..WCSCW.A..",
            ".WCW..AYCW.YA..",
            "WCSCW.JA..AJT..",
            ".WCW.AYAAJAJA..",
            "..JJFAJJAAJFF..",
            "..FFFFFFFFFFF..",
        ],
    },
    "dandelion_puff": {
        "kind": "dandelion",
        "ox": -7,
        "oy": -14,
        "grid": [
            "...XWX...SS...",
            "..WXlXW.SGGS..",
            "..WlXlW..SS...",
            "...XWX...A....",
            "....A...YA.XWX",
            "...YA..AJ.WXlW",
            "...JA..JA..XWX",
            "..AYAAJAA..JA.",
            "..FFJJJFF.FJF.",
            "..FFFFFFFFFFF.",
        ],
    },
    "clover_bed": {
        "kind": "flora",
        "ox": -8,
        "oy": -7,
        "grid": [
            "..yy.CKC.yy.YY..",
            ".yyyy.C.yyyyYYY.",
            "..AAyyAyyAAJCKC.",
            ".YYJAAJJAAJJAC..",
            "FFJJAAFFAAJJFFF.",
            ".FFFFFFFFFFFFF..",
        ],
    },
    "wheat_sheaf": {
        "kind": "flora",
        "ox": -6,
        "oy": -15,
        "grid": [
            ".L.S.L.S.L..",
            "SLGSGLGSGLS.",
            ".SGGSGSGGS..",
            "..GGGGGGG...",
            "..mmGGGmm...",
            "...VVHVV....",
            "...VHHHV....",
            "..mmGGGmm...",
            ".mGGGGGGGm..",
            ".DmmmmmmmD..",
            "..DDDDDDD...",
        ],
    },
    "glow_mushroom_blue": {
        "kind": "glow_mush",
        "ox": -7,
        "oy": -12,
        "grid": [
            "....ZZZZZ.....",
            "..ZZUUUUUZZ...",
            ".ZUUUXXXUUUZ..",
            ".NIIIIIIIIIN..",
            "...llCCCll.ZZZ",
            "...llCCCllZUUZ",
            "ZZZ.lCCCl.NIIN",
            "ZUUZ.lCl...lCl",
            "NIIN.lCl..llCl",
            ".lClFFJAAJJFF.",
            ".FFFFFFFFFFFF.",
        ],
    },
    "amanita_mushroom": {
        "kind": "shelter",
        "ox": -7,
        "oy": -11,
        "grid": [
            "...HHHHHHH....",
            "..HHWWHHWHH...",
            ".VHHHHHHHHHV..",
            ".VVVWWWWWWVV..",
            "....hCCCCh.HHH",
            "....hCCCChHWHH",
            "....hCCCh.VVVV",
            "...hhCCChh.hCh",
            "..FFJAAAJJFhCh",
            "..FFFFFFFFFFF.",
        ],
    },
    "mossy_stone": {
        "kind": "shelter",
        "ox": -8,
        "oy": -9,
        "grid": [
            "...YYYYAAYY....",
            "..YAAAAJJAAYY..",
            ".FAJJJssssJAAF.",
            ".FJJssllllssggE",
            "EkkgsllllggggkE",
            "EkkkggggggggkkE",
            ".EEEEEEEEEEEEE.",
        ],
    },
    "hollow_oak_log": {
        "kind": "shelter",
        "ox": -10,
        "oy": -9,
        "grid": [
            "...YYAA........GL..",
            ".OOOOOOOOOOOOOOmmO.",
            "ODuuuuummmmuuuuDDDO",
            "ODuEEEDuuuuuuuDDDDO",
            "ODEEEEEDmmmmuuuuEEO",
            "ODuEEEDDDDDDDDDDEEO",
            ".OOOOOOOOOOOOOOOOO.",
        ],
    },
    "acorn_stash": {
        "kind": "shelter",
        "ox": -6,
        "oy": -7,
        "grid": [
            "...OO...OO..",
            "..DnDO.DnDO.",
            ".ODnnDODnnDO",
            "..OmGO.OmLO.",
            ".rrOOpp.OOrr",
            "PrrrrrrrrPP.",
        ],
    },
    "wood_signpost": {
        "kind": "shelter",
        "ox": -7,
        "oy": -17,
        "grid": [
            ".....OOO......",
            ".OOOOOOOOOOO..",
            "OMMMMSCMMMMPO.",
            "OmmmmmmmmmmO..",
            ".OOOOOOuOOOO..",
            "......OuO.....",
            "......OuO.....",
            "......OuO.....",
            "......OuO.....",
            ".....FJuJF....",
            "....FFFFFFF...",
        ],
    },
    "provence_stone_wall": {
        "kind": "shelter",
        "ox": -11,
        "oy": -10,
        "grid": [
            "..YYAA........AAYY...",
            ".OOOOOO.OOOO.OOOOOOO.",
            "OsssllgOthhhOsslllggO",
            "OggggkkOuuuuOggggkkkO",
            "OOOOOOO.OOOO.OOOOOOOO",
            "OthhhOOsslllgOOssllgO",
            "OuuuuOOggggkkOOggggkO",
            ".OOOOOOOOOOOOOOOOOOO.",
        ],
    },
    "dew_puddle": {
        "kind": "water",
        "ox": -10,
        "oy": -6,
        "grid": [
            "...FFJJNNNNNNJJFF...",
            ".FJNNIIUUUUUUUINNJF.",
            "FJNIIUUZZXXXZZUUINJF",
            "FJNIUUUZZUUUUUUUINJF",
            ".FFJNNIIIIIIIIINNJF.",
            "...FFFFNNNNNNFFFF...",
        ],
    },
    "lilypad_lotus": {
        "kind": "water",
        "ox": -9,
        "oy": -8,
        "grid": [
            ".....K.W.K........",
            "....KKWCWKK.......",
            "....VHHSHHV.......",
            "..FFJJVVVJJAAYY...",
            ".FJJAAAAAAAAYYY.AF",
            "NIFFJJAAAAAAJJ..IN",
            ".NIIFFFFFFFFFIIIN.",
        ],
    },
    "stream_brook": {
        "kind": "water",
        "ox": -11,
        "oy": -7,
        "grid": [
            "..gFFNNNNNNNNNNFFs..",
            ".gkFNIIUUUUUUZZINFk.",
            "NIUUZZWWUUUUZZWWUUIN",
            "NIIUUUUUZZUUUUUUUUIN",
            ".FFNNIIIIIIIIIIINFF.",
            "...FFFFNNNNNNFFFF...",
        ],
    },
    "pebble_bank": {
        "kind": "shelter",
        "ox": -8,
        "oy": -6,
        "grid": [
            "....sss....ll...",
            "..sslllgg.sllg..",
            ".EkglllggEkggkE.",
            "EthEEEEEssEEEEE.",
            "EtuO.EkkllggkE..",
            ".EE...EEEEEEE...",
        ],
    },
    "mini_footbridge": {
        "kind": "water",
        "ox": -11,
        "oy": -11,
        "grid": [
            "..OO.....OO.....OO..",
            "..OMO...OMMO...OMO..",
            "..OOOOOOOOOOOOOOO...",
            ".OMMMLLLMMMMLLLMMO..",
            "OmmmmmmmmmmmmmmmmmO.",
            "ODDDDOOOOOOOODDDDDO.",
            "OO..NIIUUUUUUIIN..OO",
            "....NIIUZZZZUIIN....",
        ],
    },
    "cattail_reeds": {
        "kind": "flora",
        "ox": -6,
        "oy": -17,
        "grid": [
            "..L.....L...",
            "..n..L..n...",
            ".Dn..n..nD..",
            ".Dn..u..nD..",
            ".un..u..nu..",
            "..A.YA..A...",
            ".YA.JA.AYT..",
            ".JA.JA.AJA..",
            "..JAJAAJA...",
            "..JJAAJJF...",
            "..FFFFFFFF..",
        ],
    },
    "splash_fountain": {
        "kind": "fountain",
        "ox": -9,
        "oy": -15,
        "grid": [
            ".......XWX........",
            "......ZUWUZ.......",
            ".....ZUU.UUZ......",
            ".....EsssssE......",
            "....EslllllsE.....",
            "......EgggE.......",
            "..EkkkkkkkkkkkE...",
            ".EssUUZZZZZUUsSE..".replace("S", "s"),
            ".EggIIIIIIIIggkE..",
            "..EkkkkkkkkkkkE...",
            "...EEEEEEEEEEE....",
        ],
    },
    "iron_lantern": {
        "kind": "lantern",
        "ox": -6,
        "oy": -19,
        "grid": [
            "....EEEEE...",
            "...EkssskE..",
            "..EkE...EkE.",
            "..EkEEEEEkE.",
            ".EEkGGGGkEE.",
            "..EkSWWSkE..",
            "..EkSWWSkE..",
            "..EEGGGGEE..",
            "....EkkE....",
            "....EkE.....",
            "....EkE.....",
            "....EkE.....",
            "...EEkEE....",
            "..EEEEEE....",
        ],
    },
    "straw_nest": {
        "kind": "shelter",
        "ox": -7,
        "oy": -7,
        "grid": [
            "....ZX..XZ....",
            "...ZWWXZWWX...",
            ".OOtLLLZZLLtO.",
            "OutGGttttGGtuO",
            "OnuuuuuuuuuunO",
            ".OnnnnnnnnnnO.",
            "..OOOOOOOOOO..",
        ],
    },
    "wood_birdhouse": {
        "kind": "hang",
        "ox": -6,
        "oy": -18,
        "grid": [
            ".....FF.....",
            "...FFYYFF...",
            "..FJJYYJJF..",
            ".FJJAAAAJJF.",
            "..OOOOOOOO..",
            "..OMMMMMMO..",
            "..OMMEEMMO..",
            "..OMMEEMMO..",
            "..OmmSSmmO..",
            "..OOOOOOOO..",
            ".....OuO....",
            ".....OuO....",
            ".....OuO....",
            "....OOOOO...",
        ],
    },
    "oak_barrel": {
        "kind": "shelter",
        "ox": -6,
        "oy": -11,
        "grid": [
            "..OOOOOOOO..",
            ".OmmMMMMmmO.",
            "EkkkkkkkkkkE",
            "OummMMMMmmuO",
            "OummMMMMmmuO",
            "EssssssssssE",
            "OummMMMMmmuO",
            ".ODuuuuuuDO.",
            "..OOOOOOOO..",
        ],
    },
    "berry_bush": {
        "kind": "flora",
        "ox": -8,
        "oy": -11,
        "grid": [
            "....YYYYAAY.....",
            "..YYAAHWHAAYY...",
            ".YAAJJVVVJJAAY..",
            ".FAJAAAYYAAHWHF.",
            "FAJJHWHAAJJVVVJF",
            "FAJJVVVJJAAAAJJF",
            ".FFJJJJJJJJJJFF.",
            "..FFFFFFFFFFFF..",
        ],
    },
    "garden_bench": {
        "kind": "shelter",
        "ox": -10,
        "oy": -10,
        "grid": [
            ".E..OOOOOOOOOOOO..E.",
            ".EkOMMMLLLLLLMMMOKE.".replace("K", "k"),
            ".EkOmmmmmmmmmmmmOkE.",
            ".Ek.E..........E.kE.",
            "EEkOOOOOOOOOOOOOOkEE",
            "EkOMMMMLLLLLLMMMMOkE",
            ".E..E..........E..E.",
            ".E..E..........E..E.",
        ],
    },
    "cypress_alcove": {
        "kind": "flora",
        "ox": -6,
        "oy": -21,
        "grid": [
            ".....F......",
            "....FJF.....",
            "....JYA.....",
            "...FJAA.....",
            "...JAAYF....",
            "..FJAAJF....",
            "..JAAYJJF...",
            "..FAAJJAF...",
            ".FJAAYJAAF..",
            ".FAAJJAAJF..",
            ".FFJJAAJFF..",
            "..FFJJJFF...",
            "....OuO.....",
            "...OOOOO....",
        ],
    },
    "crystal_geode": {
        "kind": "crystal",
        "ox": -7,
        "oy": -10,
        "grid": [
            "....xW..Wx....",
            "...qxUxxUxq...",
            "..EvqqUUqqvE..",
            ".EkvqqxxqqvkE.",
            "EkkvvqqqqvvkkE",
            "EkkvvvvvvvvkkE",
            ".EEEEEEEEEEEE.",
        ],
    },
    "starlight_windchime": {
        "kind": "hang",
        "ox": -6,
        "oy": -16,
        "grid": [
            ".....SS.....",
            "..GGGGGGGG..",
            "..Z..X..Z..W",
            "..Z..X..Z..Z",
            "..s..Z..s..Z",
            "..s..Z..s..s",
            ".....s.....s",
            "....S.......",
        ],
    },
    "weathervane": {
        "kind": "hang",
        "ox": -6,
        "oy": -17,
        "grid": [
            ".....SW.....",
            "..SSGGGGSS..",
            "....GGGG....",
            ".....Ek.....",
            "..s..Ek..s..",
            ".ssssssssss.",
            ".....Ek.....",
            ".....Ek.....",
            ".....Ek.....",
            "....EEEE....",
        ],
    },
    "firefly_jar": {
        "kind": "firefly_jar",
        "ox": -5,
        "oy": -10,
        "grid": [
            "...uuuu...",
            "..ummmmu..",
            ".EssssssE.",
            ".EXZWWZXE.",
            ".EXSSWZXE.",
            ".EZZUWZSE.",
            ".EXZZZZXE.",
            "..EEEEEE..",
        ],
    },
    "wild_rose_bush": {
        "kind": "pollen",
        "ox": -8,
        "oy": -11,
        "grid": [
            "...HKH....HKH...",
            "..HVWVH..HVWVH..",
            "...VVV.AA.VVV...",
            ".HKH..YAAY..HKH.",
            "HVWVH.JAAJ.HVWVH",
            ".VVV.AJAAJA.VVV.",
            "..FFJJAAAAJJFF..",
            "..FFFFFFFFFFFF..",
        ],
    },
}

PROPS_32 = PROP_CATALOG

BF_FRAMES = {
    "bfm": (
        [
            "...E...E...",
            "EEE.E.E.EEE",
            "EWUXEEEXUWE",
            "EUXUEEEUXUE",
            ".EUIEEEIUE.",
            "..EEIUIEE..",
            "..EUXEXUE..",
        ],
        [
            "...E...E...",
            ".EEE.E.EEE.",
            ".EWUXEXUWE.",
            "..EUIEIUE..",
            "..EEUIUEE..",
            "...EU.UE...",
            "...........",
        ],
        [
            "...E.E.....",
            "...EEEEE...",
            "....EUXWE..",
            "...EUXXUE..",
            "...EEIEE...",
            "....EEE....",
            "...........",
        ],
    ),
    "bfg": (
        [
            "...E...E...",
            "EEE.E.E.EEE",
            "EWSGEEEGSWE",
            "EGSGEEEGSGE",
            ".EGPEEEPGE.",
            "..EEPGPEE..",
            "..EGPEPGE..",
        ],
        [
            "...E...E...",
            ".EEE.E.EEE.",
            ".EWSGEGSWE.",
            "..EPPEPPE..",
            "..EEPGPEE..",
            "...EP.PE...",
            "...........",
        ],
        [
            "...E.E.....",
            "...EEEEE...",
            "....EGSWE..",
            "...EGGSGE..",
            "...EEPEE...",
            "....EEE....",
            "...........",
        ],
    ),
}

EMOTE_GRIDS = {
    "sparkle": (-3, -21, [
        "...S...",
        ".Z.W.Z.",
        "..WWW..",
        "SWWWWWS",
        "..WWW..",
        ".Z.W.Z.",
        "...S...",
    ]),
    "heart": (-3, -21, [
        ".KK.HH.",
        "KHHHHHH",
        ".HHHHH.",
        "..HHH..",
        "...H...",
    ]),
    "zzz": (-3, -21, [
        "..SSS",
        "...S.",
        "..SSS",
        "ZZZ..",
        ".Z...",
        "ZZZ..",
    ]),
    "note": (-3, -21, [
        "..SSSS",
        "..S..S",
        "..S..S",
        "TTS.TT",
    ]),
}


def _norm_scene(scene_kind):
    s = (scene_kind or "nocturne").lower()
    if "mat" in s or "01" in s:
        return "matrix"
    if "core" in s or "02" in s:
        return "core"
    if "card1" in s:
        return "card1"
    if "card2" in s:
        return "card2"
    if "card3" in s:
        return "card3"
    return "nocturne"


def _compute_merged_spans(rows, ox=0, oy=0):
    present = {ch for row in rows for ch in row if ch != "."}
    spans_by_col = []
    for ch in LAYER_ORDER:
        if ch not in present:
            continue
        rank = LAYER_RANK[ch]
        runs = []
        for r_idx, row in enumerate(rows):
            w = len(row)
            c_idx = 0
            while c_idx < w:
                if row[c_idx] != ch:
                    c_idx += 1
                    continue
                last_need = c_idx
                scan = c_idx + 1
                while scan < w:
                    cell = row[scan]
                    if cell == ch:
                        last_need = scan
                        scan += 1
                    elif cell != "." and LAYER_RANK[cell] > rank:
                        scan += 1
                    else:
                        break
                runs.append([ox + c_idx, oy + r_idx, last_need - c_idx + 1, 1])
                c_idx = last_need + 1

        merged = []
        active = {}
        for x, y, rw, rh in runs:
            key = (x, rw)
            prev = active.get(key)
            if prev is not None and prev[1] + prev[3] == y:
                prev[3] += rh
            else:
                item = [x, y, rw, rh]
                merged.append(item)
                active[key] = item
        spans_by_col.append((ECO_PALETTE[ch], merged))
    return spans_by_col


def _merge_grid_rects(rows, ox=0, oy=0):
    elems = []
    for hex_col, merged in _compute_merged_spans(rows, ox, oy):
        rects = []
        for x, y, rw, rh in merged:
            xa = ' x="%d"' % x if x else ""
            ya = ' y="%d"' % y if y else ""
            rects.append('<rect%s%s width="%d" height="%d"/>' % (xa, ya, rw, rh))
        elems.append('<g fill="%s">%s</g>' % (hex_col, "".join(rects)))
    return "".join(elems)


def _merge_grid_paths(rows, ox=0, oy=0):
    elems = []
    for hex_col, merged in _compute_merged_spans(rows, ox, oy):
        cmds = []
        cx, cy = None, None
        for x, y, rw, rh in merged:
            abs_m = "M%d%s%d" % (x, "" if y < 0 else " ", y)
            if cx is not None:
                dx, dy = x - cx, y - cy
                rel_m = "m%d%s%d" % (dx, "" if dy < 0 else " ", dy)
                move_s = rel_m if len(rel_m) < len(abs_m) else abs_m
            else:
                move_s = abs_m
            close_h = ("H%d" % x) if len("H%d" % x) < len("h-%d" % rw) else ("h-%d" % rw)
            cmds.append("%sh%dv%d%sz" % (move_s, rw, rh, close_h))
            cx, cy = x, y
        elems.append('<path fill="%s" d="%s"/>' % (hex_col, "".join(cmds)))
    return "".join(elems)


SCHED_S = (0.00, 0.12, 0.25, 0.38, 0.50, 0.62, 0.75, 0.88, 1.00)
SCHED_T = (0.00, 0.13, 0.26, 0.39, 0.51, 0.64, 0.77, 0.89, 1.00)


def _build_css(prefix):
    # WHY: 100% GPU-composited CSS transforms/opacity with per-species joint pivots and strict reduced-motion freeze.
    p = prefix
    kf = [
        ".eco-stage{shape-rendering:crispEdges}",
        ".eco-calm,.%s-eco-calm{display:none}" % p,
        ".%s-r,.%s-s,.%s-sway,.%s-rip,#%s-eco-bfm0,#%s-eco-bfg0{transform-origin:0 0}" % (p, p, p, p, p, p),
        ".%s-r,.%s-b,.%s-t,.%s-d,.%s-f,.%s-h,.%s-e,.%s-s{animation-timing-function:cubic-bezier(0.42,0,0.58,1);animation-iteration-count:infinite;will-change:transform}"
        % (p, p, p, p, p, p, p, p),
        ".%s-s{fill:#030712;fill-opacity:.52}" % p,
    ]
    origin_groups = {}
    for s_idx, sp_name in enumerate(ANIMAL_SPECIES):
        joints = ANIMAL_CATALOG[sp_name]["joints"]
        for pk in PART_KEYS:
            jx, jy = joints[pk]
            origin_groups.setdefault((jx, jy), []).append(".%s-sp%d .%s-%s" % (p, s_idx, p, PART_SHORT[pk]))
    for (jx, jy), sels in origin_groups.items():
        kf.append("%s{transform-origin:%dpx %dpx}" % (",".join(sels), jx, jy))

    kf.extend([
        "@keyframes %s-k-bob1{50%%{transform:translateY(-1.1px)}}" % p,
        "@keyframes %s-k-bob2{50%%{transform:translateY(-2.2px)}}" % p,
        "@keyframes %s-k-gal{0%%,100%%{transform:translateY(0) rotate(3.5deg)}50%%{transform:translateY(-4.4px) rotate(-6.5deg)}}" % p,
        "@keyframes %s-k-hop{0%%,100%%{transform:translateY(0) rotate(0deg) scale(1.05,.93)}50%%{transform:translateY(-6.2px) rotate(-6.5deg) scale(.96,1.04)}}" % p,
        "@keyframes %s-k-binky{0%%,100%%{transform:scale(1.07,.91)}35%%{transform:translateY(-9.5px) rotate(-12deg)}65%%{transform:translateY(-7.5px) rotate(9deg)}}" % p,
        "@keyframes %s-k-leg1{0%%,100%%{transform:rotate(-17deg)}50%%{transform:rotate(17deg)}}" % p,
        "@keyframes %s-k-leg1r{0%%,100%%{transform:rotate(17deg)}50%%{transform:rotate(-17deg)}}" % p,
        "@keyframes %s-k-leg2{0%%,100%%{transform:rotate(-25deg)}50%%{transform:rotate(25deg)}}" % p,
        "@keyframes %s-k-leg2r{0%%,100%%{transform:rotate(25deg)}50%%{transform:rotate(-25deg)}}" % p,
        "@keyframes %s-k-leg3{0%%,100%%{transform:rotate(-33deg)}50%%{transform:rotate(31deg)}}" % p,
        "@keyframes %s-k-leg3r{0%%,100%%{transform:rotate(31deg)}50%%{transform:rotate(-33deg)}}" % p,
        "@keyframes %s-k-kick{45%%{transform:rotate(40deg)}75%%{transform:rotate(-15deg)}}" % p,
        "@keyframes %s-k-nod1{0%%,100%%{transform:rotate(-3deg)}50%%{transform:rotate(4deg)}}" % p,
        "@keyframes %s-k-nod2{0%%,100%%{transform:rotate(-9deg)}50%%{transform:rotate(8deg)}}" % p,
        "@keyframes %s-k-ear1{0%%,100%%{transform:rotate(-4deg)}50%%{transform:rotate(5deg)}}" % p,
        "@keyframes %s-k-ear2{0%%,100%%{transform:rotate(-11deg)}50%%{transform:rotate(8deg)}}" % p,
        "@keyframes %s-k-ear3{0%%,100%%{transform:rotate(-20deg)}50%%{transform:rotate(14deg)}}" % p,
        "@keyframes %s-k-ear4{0%%,70%%,100%%{transform:rotate(-18deg)}35%%{transform:rotate(-4deg)}}" % p,
        "@keyframes %s-k-wing{0%%,100%%{transform:rotate(6deg) scaleY(1)}50%%{transform:rotate(-26deg) scaleY(.8)}}" % p,
        "@keyframes %s-k-wag1{0%%,100%%{transform:rotate(-9deg)}50%%{transform:rotate(11deg)}}" % p,
        "@keyframes %s-k-wag2{0%%,100%%{transform:rotate(-15deg)}50%%{transform:rotate(19deg)}}" % p,
        "@keyframes %s-k-wag3{0%%,100%%{transform:rotate(-20deg)}50%%{transform:rotate(25deg)}}" % p,
        "@keyframes %s-k-wag4{0%%,100%%{transform:rotate(-24deg)}50%%{transform:rotate(30deg)}}" % p,
        "@keyframes %s-k-sh1{50%%{transform:scale(.93,.95)}}" % p,
        "@keyframes %s-k-sh2{50%%{transform:scale(.86,.9)}}" % p,
        "@keyframes %s-k-sh3{0%%,100%%{transform:scale(1.04,1)}50%%{transform:scale(.75,.82)}}" % p,
        "@keyframes %s-k-sh4{0%%,100%%{transform:scale(1.05,1)}50%%{transform:scale(.66,.74)}}" % p,
        "@keyframes %s-k-leanf{0%%,100%%{transform:rotate(5deg) translateY(.8px)}50%%{transform:rotate(7deg) translateY(1.2px)}}" % p,
        "@keyframes %s-k-graze{0%%,100%%{transform:translate(1px,2px) rotate(22deg)}50%%{transform:translate(1.5px,2.8px) rotate(29deg)}}" % p,
        "@keyframes %s-k-sniff{0%%,100%%{transform:translate(1px,1.5px) rotate(18deg)}50%%{transform:translate(2.4px,2.2px) rotate(25deg)}}" % p,
        "@keyframes %s-k-drinkb{35%%,65%%{transform:rotate(8deg) translateY(1.4px)}}" % p,
        "@keyframes %s-k-drinkh{0%%,100%%{transform:rotate(-8deg)}35%%,62%%{transform:translate(1px,2.5px) rotate(28deg)}}" % p,
        "@keyframes %s-k-sit{0%%,100%%{transform:rotate(-9deg) translateY(1px)}50%%{transform:rotate(-11deg) translateY(1.4px)}}" % p,
        "@keyframes %s-k-groom{0%%,100%%{transform:rotate(-44deg) translate(1px,-2px)}50%%{transform:rotate(-62deg) translate(2px,-3px)}}" % p,
        "@keyframes %s-k-groomh{0%%,100%%{transform:rotate(8deg)}50%%{transform:rotate(16deg)}}" % p,
        "@keyframes %s-k-scrat{0%%,100%%{transform:rotate(-42deg) translate(2px,-2px)}50%%{transform:rotate(-58deg) translate(2px,-3px)}}" % p,
        "@keyframes %s-k-scrath{0%%,100%%{transform:rotate(12deg)}50%%{transform:rotate(17deg)}}" % p,
        "@keyframes %s-k-bowb{35%%,70%%{transform:rotate(12deg) translateY(1.8px)}}" % p,
        "@keyframes %s-k-bowl{35%%,70%%{transform:rotate(-44deg)}}" % p,
        "@keyframes %s-k-bowh{35%%,70%%{transform:rotate(-14deg)}}" % p,
        "@keyframes %s-k-yawnb{45%%,65%%{transform:scale(1.06,1.08)}}" % p,
        "@keyframes %s-k-yawnh{40%%,68%%{transform:rotate(-25deg) translate(-1px,-1px)}}" % p,
        "@keyframes %s-k-perk{0%%,100%%{transform:rotate(-10deg)}50%%{transform:rotate(-16deg)}}" % p,
        "@keyframes %s-k-alert{0%%,100%%{transform:scale(.98,1.04)}50%%{transform:translateY(-1.2px) scale(.96,1.08)}}" % p,
        "@keyframes %s-k-star{0%%,100%%{transform:rotate(-24deg)}45%%{transform:rotate(-34deg)}75%%{transform:rotate(-28deg)}}" % p,
        "@keyframes %s-k-chase{45%%{transform:translate(1px,-5.5px) rotate(-11deg)}}" % p,
        "@keyframes %s-k-bat{0%%,100%%{transform:rotate(-12deg)}45%%{transform:rotate(-52deg)}}" % p,
        "@keyframes %s-k-boop{45%%{transform:translate(2.5px,-1px)}72%%{transform:translate(-1px,-3px)}}" % p,
        "@keyframes %s-k-booph{0%%,100%%{transform:rotate(-6deg)}45%%{transform:rotate(-18deg)}72%%{transform:rotate(-24deg)}}" % p,
        "@keyframes %s-k-pounce{0%%,38%%{transform:translate(-1px,1.6px) scale(1.12,.82)}68%%{transform:translate(4px,-7.2px) rotate(-13deg)}}" % p,
        "@keyframes %s-k-roll{30%%,70%%{transform:translateY(-5.5px) rotate(172deg)}50%%{transform:translateY(-5.5px) rotate(160deg)}}" % p,
        "@keyframes %s-k-spin{25%%,75%%{transform:translateY(-4px) scale(.18,1.04)}50%%{transform:translateY(-2px) scale(-1,1)}}" % p,
        "@keyframes %s-k-shkb{0%%,100%%{transform:translateX(-1px) rotate(-4deg)}50%%{transform:translateX(1px) rotate(4deg)}}" % p,
        "@keyframes %s-k-shkh{0%%,100%%{transform:rotate(-11deg)}50%%{transform:rotate(11deg)}}" % p,
        "@keyframes %s-k-stalk{0%%,100%%{transform:translateY(2px) scale(1.08,.84)}50%%{transform:translate(.8px,2.3px) scale(1.1,.82)}}" % p,
        "@keyframes %s-k-stalkh{0%%,100%%{transform:translate(1.5px,1.5px) rotate(7deg)}50%%{transform:translate(2.2px,1.8px) rotate(11deg)}}" % p,
        "@keyframes %s-k-sway{0%%,100%%{transform:rotate(-3.5deg)}50%%{transform:rotate(3.5deg)}}" % p,
        "@keyframes %s-k-slpb{0%%,100%%{transform:translateY(2.5px) scale(1.06,.83)}50%%{transform:translateY(2.2px) scale(1.1,.88)}}" % p,
        "@keyframes %s-k-slph{0%%,100%%{transform:translate(-1.5px,2.8px) rotate(18deg)}50%%{transform:translate(-1.5px,2.4px) rotate(15deg)}}" % p,
        "@keyframes %s-k-slpe{0%%,100%%{transform:translate(-1px,2.6px) rotate(14deg)}50%%{transform:translate(-1px,2.3px) rotate(11deg)}}" % p,
        "@keyframes %s-k-slpt{0%%,100%%{transform:translate(2px,2px) rotate(-24deg)}50%%{transform:translate(2px,2px) rotate(-20deg)}}" % p,
        "@keyframes %s-k-slpl{0%%,100%%{transform:scaleY(.45)}}" % p,
        "@keyframes %s-k-baskb{0%%,100%%{transform:translateY(1.8px) scale(1.1,.87)}50%%{transform:translateY(1.5px) scale(1.13,.9)}}" % p,
        "@keyframes %s-k-baskh{0%%,100%%{transform:rotate(-14deg)}50%%{transform:rotate(-19deg)}}" % p,
        "@keyframes %s-night-env{0%%,23%%{opacity:.96}33%%,69%%{opacity:.04}80%%,100%%{opacity:.96}}" % p,
        "@keyframes %s-ltn-env{0%%,23%%{opacity:.95}31%%,71%%{opacity:0}81%%,100%%{opacity:.95}}" % p,
        "@keyframes %s-ff-pulse{0%%,100%%{transform:scale(.72);opacity:.38}50%%{transform:scale(1.24);opacity:1}}" % p,
        "@keyframes %s-breeze{0%%,100%%{transform:skewX(-3.2deg)}50%%{transform:skewX(3.6deg)}}" % p,
        "@keyframes %s-pend{0%%,100%%{transform:rotate(-5deg)}50%%{transform:rotate(5.5deg)}}" % p,
        "@keyframes %s-rip{0%%{transform:scale(.35);opacity:.88}80%%,100%%{transform:scale(1.55,1.45);opacity:0}}" % p,
        "@keyframes %s-glint{0%%,100%%{opacity:.3}50%%{opacity:.98}}" % p,
    ])
    for tag, sched in (("s", SCHED_S), ("t", SCHED_T)):
        pcts = [int(round(v * 100)) for v in sched]
        n_ph = len(pcts) - 1
        for slot in range(n_ph):
            on_start, on_end = pcts[slot], pcts[slot + 1]
            if slot == 0:
                vals = "0%%{opacity:1}%d%%{opacity:0}" % on_end
            elif slot == n_ph - 1:
                vals = "0%%{opacity:0}%d%%{opacity:1}" % on_start
            else:
                vals = "0%%{opacity:0}%d%%{opacity:1}%d%%{opacity:0}" % (on_start, on_end)
            kf.append("@keyframes %s-q%s%d{%s}" % (p, tag, slot, vals))
        for slot in range(n_ph):
            kf.append(".%s-q%s%d{animation:%s-q%s%d 60s step-end infinite}" % (p, tag, slot, p, tag, slot))
    kf.extend([
        ".%s-night-glow{animation:%s-night-env 60s ease-in-out infinite}" % (p, p),
        ".%s-ltn-glow{animation:%s-ltn-env 60s ease-in-out infinite}" % (p, p),
        ".%s-breeze{animation:%s-breeze 4.6s ease-in-out infinite}" % (p, p),
        ".%s-pend{animation:%s-pend 3.8s ease-in-out infinite}" % (p, p),
        ".%s-rip{animation:%s-rip 2.8s ease-out infinite}" % (p, p),
        ".%s-glint{animation:%s-glint 2.1s ease-in-out infinite}" % (p, p),
    ])
    for a_idx, anim_name in enumerate(ANIMATION_NAMES):
        spec = ANIM_25[anim_name]
        for part_key in ("rig", "bd", "hd", "lf", "lb", "tl", "ew", "sh"):
            if part_key in spec:
                kname, kdur = spec[part_key]
                kf.append(
                    ".%s-a%d .%s-%s{animation:%s-%s %s cubic-bezier(0.42,0,0.58,1) infinite}"
                    % (p, a_idx, p, PART_SHORT[part_key], p, kname, kdur)
                )
    kf.append(
        "@keyframes %s-seed{0%%,25%%,65%%,100%%{opacity:0;transform:translate(0,-8px)}40%%{opacity:.95;transform:translate(4px,-18px)}55%%{opacity:0;transform:translate(7px,-24px)}}" % p
    )
    kf.append(
        ".%s-seed{animation:%s-seed 60s ease-out infinite}" % (p, p)
    )
    kf.append(
        ".%s-ffp{animation:%s-ff-pulse 2.2s ease-in-out infinite;transform-origin:0 0}" % (p, p)
    )
    kf.append(
        "@keyframes %s-k-bfwing{0%%,100%%{transform:scaleY(1) rotate(-5deg)}50%%{transform:scaleY(.22) rotate(9deg)}}" % p
    )
    kf.append(
        "#%s-eco-bfm0,#%s-eco-bfg0{animation:%s-k-bfwing .38s cubic-bezier(0.42,0,0.58,1) infinite;will-change:transform}" % (p, p, p)
    )
    kf.append(
        "@media (prefers-reduced-motion: reduce){"
        ".eco-live,.%s-eco-live,.pup-live{display:none !important;animation:none !important}"
        ".eco-live *,.%s-eco-live *,#%s-eco-bfm0,#%s-eco-bfg0{animation:none !important}"
        ".eco-calm,.%s-eco-calm,.pup-calm{display:inline !important;animation:none !important}"
        "}" % (p, p, p, p, p)
    )
    return "<style>%s</style>" % "".join(kf)


def render_ecosystem_defs(prefix, scene_kind="nocturne"):
    _ = _norm_scene(scene_kind)
    p = prefix
    defs = [
        '<radialGradient id="%s-eco-ltn-cone" cx="0.5" cy="0.18" r="0.82">' % p,
        '<stop offset="0%" stop-color="#fef08a" stop-opacity="0.62"/>',
        '<stop offset="52%" stop-color="#f59e0b" stop-opacity="0.22"/>',
        '<stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/>',
        "</radialGradient>",
        '<radialGradient id="%s-eco-mush-glow" cx="0.5" cy="0.5" r="0.5">' % p,
        '<stop offset="0%" stop-color="#38bdf8" stop-opacity="0.64"/>',
        '<stop offset="58%" stop-color="#34d399" stop-opacity="0.22"/>',
        '<stop offset="100%" stop-color="#0ea5e9" stop-opacity="0"/>',
        "</radialGradient>",
        '<radialGradient id="%s-eco-ff-gold" cx="0.5" cy="0.5" r="0.5">' % p,
        '<stop offset="0%" stop-color="#ffffff" stop-opacity="0.98"/>',
        '<stop offset="34%" stop-color="#fde047" stop-opacity="0.78"/>',
        '<stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/>',
        "</radialGradient>",
        '<radialGradient id="%s-eco-ff-em" cx="0.5" cy="0.5" r="0.5">' % p,
        '<stop offset="0%" stop-color="#fefce8" stop-opacity="0.96"/>',
        '<stop offset="36%" stop-color="#6ee7b7" stop-opacity="0.74"/>',
        '<stop offset="100%" stop-color="#10b981" stop-opacity="0"/>',
        "</radialGradient>",
    ]

    for s_idx, sp_name in enumerate(ANIMAL_SPECIES):
        sp = ANIMAL_CATALOG[sp_name]
        joints = sp["joints"]
        for pk in PART_KEYS:
            jx, jy = joints[pk]
            ox, oy, grid = sp["parts"][pk]
            defs.append(
                '<g id="%s-%d%s">%s</g>'
                % (p, s_idx, PART_SHORT[pk], _merge_grid_paths(grid, ox + jx, oy + jy))
            )
        rx, ry = sp["shadow"]
        full_uses = ['<ellipse class="%s-s" cy="-1.2" rx="%s" ry="%s"/>' % (p, num(rx, 1), num(ry, 1))]
        for pk in PART_KEYS:
            full_uses.append('<use href="#%s-%d%s"/>' % (p, s_idx, PART_SHORT[pk]))
        defs.append('<g id="%s-s%d-full">%s</g>' % (p, s_idx, "".join(full_uses)))

    for p_idx, pr_name in enumerate(PROP_NAMES):
        pr = PROP_CATALOG[pr_name]
        defs.append('<g id="%s-pr%d">%s</g>' % (p, p_idx, _merge_grid_paths(pr["grid"], pr["ox"], pr["oy"])))

    for bf_code, frames in BF_FRAMES.items():
        for f_i, f_grid in enumerate(frames):
            defs.append('<g id="%s-eco-%s%d">%s</g>' % (p, bf_code, f_i, _merge_grid_paths(f_grid, -5, -4)))
        defs.append('<g id="%s-%s-fl"><use href="#%s-eco-%s0"/></g>' % (p, bf_code, p, bf_code))

    for em_key, (ex, ey, egrid) in EMOTE_GRIDS.items():
        defs.append('<g id="%s-em-%s">%s</g>' % (p, em_key, _merge_grid_paths(egrid, ex, ey)))

    defs.append('<g id="%s-ff0"><circle r="5.4" fill="url(#%s-eco-ff-gold)"/><rect x="-1" y="-1" width="2" height="2" fill="#fef9c3"/></g>' % (p, p))
    defs.append('<g id="%s-ff1"><circle r="5.2" fill="url(#%s-eco-ff-em)"/><rect x="-1" y="-1" width="2" height="2" fill="#d1fae5"/></g>' % (p, p))

    return "%s<defs>%s</defs>" % (_build_css(p), "".join(defs))


def _firefly_zones(scene):
    if scene == "matrix":
        return [
            (48, 44, 260, 228),
            (890, 44, 1152, 228),
            (318, 252, 962, 282),
            (72, 318, 850, 462),
        ]
    if scene == "core":
        return [
            (44, 438, 138, 548),
            (356, 438, 468, 548),
            (506, 78, 604, 344),
            (824, 78, 952, 344),
            (972, 400, 1164, 526),
            (520, 538, 1164, 556),
        ]
    if scene.startswith("card"):
        return [
            (48, 44, 246, 144),
            (252, 44, 346, 144),
        ]
    return [
        (42, 48, 380, 348),
        (380, 56, 820, 356),
        (820, 48, 1158, 348),
    ]


def render_fireflies_svg(prefix, scene_kind="nocturne", width=1200, height=388, count=None):
    # WHY: Cubic Bezier 60fps drift + 60s nocturnal luminescence envelope (bright 0-16s & 46-60s, shaded 20-42s).
    scene = _norm_scene(scene_kind)
    p = prefix
    rng = random.Random("eco-ff-%s-%d-%d" % (scene, int(width), int(height)))
    zones = _firefly_zones(scene)
    n_ff = count if count is not None else (16 if scene == "nocturne" else (14 if scene == "matrix" else (4 if scene.startswith("card") else 12)))

    live_items = []
    calm_items = []
    for i in range(n_ff):
        zx0, zy0, zx1, zy1 = zones[i % len(zones)]
        x0 = rng.uniform(zx0 + 8, zx1 - 8)
        y0 = rng.uniform(zy0 + 5, zy1 - 5)
        dx1 = rng.uniform(-28, 28)
        dy1 = rng.uniform(-14, 14)
        dx2 = rng.uniform(-30, 30)
        dy2 = rng.uniform(-16, 16)
        x1 = min(zx1 - 4, max(zx0 + 4, x0 + dx1))
        y1 = min(zy1 - 3, max(zy0 + 3, y0 + dy1))
        x2 = min(zx1 - 4, max(zx0 + 4, x0 + dx2))
        y2 = min(zy1 - 3, max(zy0 + 3, y0 + dy2))
        path_d = "M%s,%s C%s,%s %s,%s %s,%s C%s,%s %s,%s %s,%s" % (
            num(x0, 1), num(y0, 1),
            num(x1, 1), num(y1, 1),
            num(x2, 1), num(y2, 1),
            num((x1 + x2) * 0.5, 1), num((y1 + y2) * 0.5, 1),
            num(min(zx1 - 4, max(zx0 + 4, x0 - dx1 * 0.5)), 1), num(min(zy1 - 3, max(zy0 + 3, y0 - dy1 * 0.5)), 1),
            num(min(zx1 - 4, max(zx0 + 4, x0 + dx2 * 0.4)), 1), num(min(zy1 - 3, max(zy0 + 3, y0 - dy2 * 0.4)), 1),
            num(x0, 1), num(y0, 1),
        )
        ff_ref = "#%s-ff0" % p if i % 3 != 0 else "#%s-ff1" % p
        drift_dur = rng.uniform(9.5, 16.5)
        delay = -rng.uniform(0.2, 14.0)

        live_items.append(
            '<g><animateMotion path="%s" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            '<use class="%s-ffp" href="%s" style="animation-delay:%ss"/></g>'
            % (path_d, num(drift_dur, 1), num(delay, 1), p, ff_ref, num(delay * 0.3, 1))
        )
        if i % 2 == 0:
            calm_items.append(
                '<use href="%s" x="%s" y="%s" opacity="0.86"/>'
                % (ff_ref, num(x0, 1), num(y0, 1))
            )

    return (
        '<g class="eco-live %s-eco-live %s-night-glow" data-firefly-count="%d">%s</g>'
        '<g class="eco-calm %s-eco-calm">%s</g>'
        % (p, p, n_ff, "".join(live_items), p, "".join(calm_items))
    )


def _scene_props_layout(scene):
    if scene == "matrix":
        return [
            ("cypress_alcove", 40, 247.0, 1.12, None),
            ("provence_stone_wall", 66, 247.0, 1.15, None),
            ("iron_lantern", 92, 246.0, 1.10, None),
            ("sunflower_cluster", 114, 247.0, 1.15, (0.28, 0.38)),
            ("wood_birdhouse", 138, 247.0, 1.10, None),
            ("straw_nest", 158, 247.0, 1.12, None),
            ("hollow_oak_log", 184, 247.0, 1.15, None),
            ("acorn_stash", 206, 247.0, 1.15, (0.42, 0.54)),
            ("berry_bush", 228, 247.0, 1.12, None),
            ("mossy_stone", 252, 247.0, 1.12, None),
            ("firefly_jar", 272, 247.0, 1.12, None),
            ("lavender_tuft", 316, 287.5, 1.24, None),
            ("dandelion_puff", 352, 287.5, 1.26, (0.24, 0.36)),
            ("chamomile_patch", 394, 287.5, 1.24, None),
            ("glow_mushroom_blue", 436, 287.5, 1.22, None),
            ("clover_bed", 478, 287.5, 1.24, None),
            ("wood_signpost", 518, 287.5, 1.14, None),
            ("wild_rose_bush", 560, 287.5, 1.22, (0.50, 0.62)),
            ("garden_bench", 608, 287.5, 1.20, None),
            ("wheat_sheaf", 654, 287.5, 1.18, None),
            ("amanita_mushroom", 696, 287.5, 1.20, None),
            ("crystal_geode", 738, 287.5, 1.20, None),
            ("oak_barrel", 780, 287.5, 1.16, None),
            ("mini_footbridge", 824, 287.5, 1.20, None),
            ("stream_brook", 866, 287.5, 1.20, None),
            ("dew_puddle", 906, 287.5, 1.22, (0.62, 0.76)),
            ("lilypad_lotus", 940, 287.5, 1.20, None),
            ("cattail_reeds", 966, 287.5, 1.16, None),
            ("pebble_bank", 928, 247.0, 1.15, None),
            ("splash_fountain", 968, 247.0, 1.14, None),
            ("starlight_windchime", 1098, 247.0, 1.14, None),
            ("weathervane", 1146, 247.0, 1.14, None),
        ]
    if scene == "core":
        return [
            ("cypress_alcove", 506, 342.0, 1.10, None),
            ("iron_lantern", 538, 341.0, 1.12, None),
            ("sunflower_cluster", 568, 342.0, 1.12, (0.26, 0.38)),
            ("straw_nest", 598, 343.0, 1.10, None),
            ("glow_mushroom_blue", 826, 342.0, 1.08, None),
            ("crystal_geode", 856, 342.0, 1.08, None),
            ("amanita_mushroom", 886, 343.0, 1.08, None),
            ("hollow_oak_log", 918, 343.0, 1.06, None),
            ("acorn_stash", 948, 342.0, 1.08, (0.30, 0.44)),
            ("mossy_stone", 974, 368.0, 1.06, None),
            ("firefly_jar", 1016, 368.0, 1.08, None),
            ("wood_signpost", 1060, 369.0, 1.04, None),
            ("starlight_windchime", 1106, 370.0, 1.06, None),
            ("weathervane", 1152, 370.0, 1.06, None),
            ("provence_stone_wall", 30, 546.0, 1.14, None),
            ("dandelion_puff", 62, 548.0, 1.16, (0.44, 0.56)),
            ("lavender_tuft", 92, 550.0, 1.16, None),
            ("clover_bed", 122, 551.0, 1.14, None),
            ("chamomile_patch", 150, 552.0, 1.12, None),
            ("pebble_bank", 344, 552.0, 1.12, None),
            ("dew_puddle", 374, 550.0, 1.16, (0.60, 0.74)),
            ("lilypad_lotus", 406, 550.0, 1.14, None),
            ("cattail_reeds", 436, 548.0, 1.14, None),
            ("wild_rose_bush", 466, 546.0, 1.14, None),
            ("wood_birdhouse", 528, 552.0, 1.04, None),
            ("wheat_sheaf", 604, 553.0, 1.06, None),
            ("berry_bush", 684, 553.0, 1.06, (0.48, 0.60)),
            ("garden_bench", 768, 553.0, 1.06, None),
            ("oak_barrel", 852, 553.0, 1.04, None),
            ("mini_footbridge", 944, 553.0, 1.06, None),
            ("stream_brook", 1042, 553.0, 1.06, None),
            ("splash_fountain", 1144, 552.0, 1.02, None),
        ]
    return [
        ("cypress_alcove", 38, 344, 1.38, None),
        ("provence_stone_wall", 78, 346, 1.34, None),
        ("iron_lantern", 118, 350, 1.34, None),
        ("sunflower_cluster", 154, 356, 1.38, (0.24, 0.36)),
        ("wheat_sheaf", 192, 358, 1.32, None),
        ("oak_barrel", 228, 360, 1.30, None),
        ("wood_signpost", 264, 362, 1.28, None),
        ("lavender_tuft", 302, 366, 1.36, (0.38, 0.50)),
        ("dandelion_puff", 342, 368, 1.38, (0.28, 0.42)),
        ("chamomile_patch", 384, 370, 1.34, None),
        ("clover_bed", 426, 372, 1.34, None),
        ("hollow_oak_log", 470, 368, 1.34, None),
        ("acorn_stash", 506, 370, 1.32, (0.46, 0.58)),
        ("glow_mushroom_blue", 542, 366, 1.36, None),
        ("amanita_mushroom", 580, 368, 1.32, None),
        ("mossy_stone", 618, 366, 1.32, None),
        ("garden_bench", 662, 362, 1.34, None),
        ("firefly_jar", 702, 364, 1.32, None),
        ("wild_rose_bush", 740, 366, 1.34, (0.52, 0.66)),
        ("berry_bush", 782, 368, 1.34, None),
        ("crystal_geode", 822, 366, 1.34, None),
        ("mini_footbridge", 868, 362, 1.34, None),
        ("stream_brook", 914, 364, 1.34, None),
        ("pebble_bank", 954, 366, 1.30, None),
        ("dew_puddle", 994, 364, 1.36, (0.60, 0.74)),
        ("lilypad_lotus", 1034, 362, 1.34, None),
        ("cattail_reeds", 1068, 358, 1.32, None),
        ("splash_fountain", 1104, 352, 1.28, None),
        ("wood_birdhouse", 1138, 346, 1.28, None),
        ("straw_nest", 1166, 344, 1.26, None),
        ("starlight_windchime", 96, 314, 1.24, None),
        ("weathervane", 1152, 312, 1.24, None),
    ]


def _card_props(card_id):
    if card_id == "card1":
        return [
            ("sunflower_cluster", 34, 152, 0.88, (0.24, 0.36)),
            ("lavender_tuft", 72, 153, 0.86, None),
            ("mossy_stone", 316, 153, 0.84, None),
            ("firefly_jar", 352, 152, 0.86, None),
        ]
    if card_id == "card2":
        return [
            ("glow_mushroom_blue", 36, 152, 0.86, None),
            ("clover_bed", 76, 153, 0.84, None),
            ("acorn_stash", 312, 152, 0.86, (0.46, 0.58)),
            ("berry_bush", 350, 152, 0.86, None),
        ]
    return [
        ("cypress_alcove", 34, 151, 0.86, None),
        ("dandelion_puff", 74, 152, 0.86, (0.28, 0.42)),
        ("crystal_geode", 318, 152, 0.86, None),
        ("chamomile_patch", 354, 153, 0.84, None),
    ]


def _render_props_layer(prefix, scene):
    p = prefix
    prop_idx_map = {nm: idx for idx, nm in enumerate(PROP_NAMES)}
    layout = _card_props(scene) if scene.startswith("card") else _scene_props_layout(scene)
    live = []
    calm = []

    for i, (pr_name, px, py, sc, visit_win) in enumerate(layout):
        p_idx = prop_idx_map[pr_name]
        kind = PROP_CATALOG[pr_name]["kind"]
        px_s, py_s, sc_s = num(px, 1), num(py, 1), num(sc, 2)
        ref = "#%s-pr%d" % (p, p_idx)
        calm.append('<use href="%s" transform="translate(%s %s) scale(%s)"/>' % (ref, px_s, py_s, sc_s))

        extras = []
        inner_cls = ""
        inner_style = ""
        if kind == "lantern":
            extras.append(
                '<g class="%s-ltn-glow">'
                '<polygon points="0,-14 -20,2 -10,4 10,4 20,2" fill="url(#%s-eco-ltn-cone)"/>'
                '<ellipse cy="1" rx="15" ry="2.8" fill="#fde047" fill-opacity="0.26"/>'
                "</g>" % (p, p)
            )
        elif kind == "glow_mush":
            extras.append('<circle class="%s-night-glow" cy="-6" r="12" fill="url(#%s-eco-mush-glow)"/>' % (p, p))
        elif kind == "firefly_jar":
            extras.append('<circle class="%s-night-glow" cy="-5" r="9.5" fill="url(#%s-eco-ff-gold)"/>' % (p, p))
        elif kind == "crystal":
            extras.append('<circle class="%s-glint" cy="-7" r="7.5" fill="url(#%s-eco-mush-glow)"/>' % (p, p))
        elif kind in ("water", "fountain"):
            delay = num(-(i * 0.73) % 2.8, 2)
            extras.append(
                '<ellipse class="%s-rip" cy="-2.5" rx="7.5" ry="1.8" fill="none" stroke="#bae6fd" stroke-width="0.7" style="animation-delay:%ss"/>'
                % (p, delay)
            )
        elif kind in ("flora", "pollen", "dandelion"):
            inner_cls = ' class="%s-breeze"' % p
            inner_style = ' style="animation-delay:%ss"' % num(-(i * 0.61) % 4.4, 2)
        elif kind == "hang":
            inner_cls = ' class="%s-pend"' % p
            inner_style = ' style="animation-delay:%ss"' % num(-(i * 0.53) % 3.6, 2)

        if visit_win is not None and kind in ("dandelion", "pollen"):
            seed_col = "#ffffff" if kind == "dandelion" else "#fde047"
            extras.append('<rect class="%s-seed" x="-1" y="-1" width="1.6" height="1.6" fill="%s"/>' % (p, seed_col))
            extras.append('<rect class="%s-seed" x="2" y="-3" width="1.5" height="1.5" fill="%s" style="animation-delay:-9s"/>' % (p, seed_col))

        live.append(
            '<g data-prop="%s" transform="translate(%s %s) scale(%s)">%s<use%s%s href="%s"/></g>'
            % (pr_name, px_s, py_s, sc_s, "".join(extras), inner_cls, inner_style, ref)
        )

    return "".join(live), "".join(calm), len(layout)


def _loop_8(mode, pts, stat_poses, trav_poses):
    sched = SCHED_S if mode == "S" else SCHED_T
    segs = []
    for k in range(4):
        x0, y0 = pts[k]
        x1, y1 = pts[(k + 1) % 4]
        t_dir = 1 if x1 >= x0 else -1
        s_anim, s_face, s_em = stat_poses[k]
        t_anim, t_em = trav_poses[k]
        if mode == "S":
            segs.append((sched[2 * k], x0, y0, s_anim, s_face, s_em))
            segs.append((sched[2 * k + 1], x0, y0, t_anim, t_dir, t_em))
        else:
            segs.append((sched[2 * k], x0, y0, t_anim, t_dir, t_em))
            segs.append((sched[2 * k + 1], x1, y1, s_anim, s_face, s_em))
    segs.append((1.00, pts[0][0], pts[0][1], segs[0][3], segs[0][4], None))
    return segs


def _scene_menagerie_cast(scene):
    # WHY: Strict stationary/travel alternation across 60s loop, exercising all 25 ANIMATION_NAMES with zero moonwalking.
    if scene == "matrix":
        return [
            ("shiba_dog", 1.79, _loop_8(
                "S",
                [(118, 368), (436, 442), (728, 364), (512, 266)],
                [("stargaze_meteor", 1, "sparkle"), ("belly_roll", 1, "heart"), ("stretch_bow", -1, None), ("tail_wag_happy", -1, None)],
                [("trot", None), ("gallop", None), ("walk", None), ("trot", None)],
            )),
            ("red_fox", 1.77, _loop_8(
                "T",
                [(224, 438), (586, 366), (824, 448), (384, 264)],
                [("crouch_stalk", 1, None), ("sleep_curl_breathe", -1, "zzz"), ("sniff_ground", -1, None), ("shake_fur", 1, None)],
                [("pounce_play", "sparkle"), ("trot", None), ("boop_firefly", None), ("gallop", None)],
            )),
            ("calico_cat", 1.74, _loop_8(
                "S",
                [(642, 266), (488, 388), (776, 434), (948, 368)],
                [("groom_paw", -1, None), ("scratch_ear", 1, None), ("sun_bask", 1, "heart"), ("yawn", -1, None)],
                [("walk", None), ("trot", None), ("walk", None), ("trot", None)],
            )),
            ("cottontail_rabbit", 1.77, _loop_8(
                "T",
                [(88, 424), (318, 364), (534, 454), (336, 266)],
                [("ear_perk_alert", 1, None), ("graze_nibble", 1, None), ("sniff_ground", -1, None), ("sun_bask", -1, None)],
                [("binky_leap", "sparkle"), ("hop", None), ("hop", None), ("binky_leap", None)],
            )),
            ("red_squirrel", 1.74, _loop_8(
                "S",
                [(164, 142), (386, 208), (242, 372), (112, 238)],
                [("tail_wag_happy", 1, None), ("happy_spin", -1, "note"), ("graze_nibble", -1, None), ("shake_fur", 1, None)],
                [("hop", None), ("binky_leap", None), ("hop", None), ("trot", None)],
            )),
            ("tawny_owl", 1.80, _loop_8(
                "T",
                [(124, 88), (476, 152), (836, 84), (568, 212)],
                [("perch_sway", 1, "sparkle"), ("stargaze_meteor", -1, None), ("sleep_curl_breathe", -1, "zzz"), ("yawn", -1, None)],
                [("gallop", None), ("chase_butterfly", None), ("gallop", None), ("gallop", None)],
            )),
            ("mallard_duck", 1.74, _loop_8(
                "S",
                [(918, 266), (1086, 372), (952, 452), (792, 374)],
                [("drink_ripple", 1, None), ("graze_nibble", -1, None), ("sleep_curl_breathe", -1, None), ("sun_bask", 1, "note")],
                [("walk", None), ("walk", None), ("trot", None), ("walk", None)],
            )),
            ("hedgehog", 1.74, _loop_8(
                "T",
                [(364, 412), (662, 456), (838, 368), (596, 362)],
                [("sniff_ground", 1, None), ("belly_roll", 1, None), ("scratch_ear", -1, None), ("sleep_curl_breathe", -1, "zzz")],
                [("walk", None), ("trot", None), ("walk", None), ("walk", None)],
            )),
            ("spotted_deer", 1.76, _loop_8(
                "S",
                [(748, 198), (1034, 154), (1128, 398), (788, 264)],
                [("stargaze_meteor", 1, None), ("ear_perk_alert", 1, None), ("drink_ripple", -1, None), ("stretch_bow", -1, None)],
                [("gallop", "sparkle"), ("trot", None), ("gallop", None), ("trot", None)],
            )),
            ("tree_frog", 1.77, _loop_8(
                "T",
                [(936, 256), (1126, 366), (1018, 454), (842, 398)],
                [("sun_bask", 1, None), ("yawn", -1, None), ("perch_sway", -1, "note"), ("crouch_stalk", 1, None)],
                [("hop", "note"), ("boop_firefly", None), ("hop", None), ("pounce_play", None)],
            )),
            ("azure_bluebird", 1.74, _loop_8(
                "S",
                [(1078, 96), (712, 134), (312, 82), (648, 188)],
                [("perch_sway", -1, None), ("happy_spin", -1, "note"), ("sleep_curl_breathe", 1, "zzz"), ("groom_paw", 1, None)],
                [("chase_butterfly", "note"), ("gallop", None), ("gallop", None), ("chase_butterfly", None)],
            )),
        ]
    if scene == "core":
        return [
            ("shiba_dog", 1.70, _loop_8(
                "S",
                [(392, 538), (546, 332), (528, 126), (424, 458)],
                [("stargaze_meteor", 1, "sparkle"), ("belly_roll", 1, "heart"), ("stretch_bow", -1, None), ("tail_wag_happy", -1, None)],
                [("trot", None), ("gallop", None), ("trot", None), ("walk", None)],
            )),
            ("red_fox", 1.66, _loop_8(
                "T",
                [(882, 364), (1128, 368), (1084, 492), (1134, 366)],
                [("crouch_stalk", 1, None), ("sniff_ground", 1, None), ("sleep_curl_breathe", -1, "zzz"), ("shake_fur", -1, None)],
                [("pounce_play", "sparkle"), ("trot", None), ("boop_firefly", None), ("gallop", None)],
            )),
            ("calico_cat", 1.68, _loop_8(
                "S",
                [(538, 118), (562, 326), (878, 334), (862, 312)],
                [("groom_paw", 1, None), ("sun_bask", 1, "heart"), ("scratch_ear", -1, None), ("yawn", -1, None)],
                [("walk", None), ("trot", None), ("walk", None), ("trot", None)],
            )),
            ("cottontail_rabbit", 1.66, _loop_8(
                "T",
                [(56, 538), (114, 452), (68, 544), (128, 536)],
                [("ear_perk_alert", 1, None), ("graze_nibble", -1, None), ("sun_bask", 1, None), ("drink_ripple", -1, None)],
                [("binky_leap", "sparkle"), ("hop", None), ("hop", None), ("binky_leap", None)],
            )),
            ("red_squirrel", 1.66, _loop_8(
                "S",
                [(524, 298), (558, 98), (886, 94), (534, 118)],
                [("tail_wag_happy", 1, None), ("happy_spin", 1, "note"), ("graze_nibble", 1, None), ("shake_fur", -1, None)],
                [("hop", None), ("gallop", None), ("hop", None), ("binky_leap", None)],
            )),
            ("tawny_owl", 1.72, _loop_8(
                "T",
                [(518, 88), (886, 86), (928, 122), (862, 92)],
                [("perch_sway", 1, "sparkle"), ("stargaze_meteor", 1, None), ("sleep_curl_breathe", -1, "zzz"), ("yawn", -1, None)],
                [("gallop", None), ("gallop", None), ("chase_butterfly", None), ("gallop", None)],
            )),
            ("mallard_duck", 1.66, _loop_8(
                "S",
                [(384, 538), (456, 448), (464, 542), (388, 468)],
                [("drink_ripple", 1, None), ("graze_nibble", 1, None), ("sleep_curl_breathe", -1, None), ("sun_bask", -1, "note")],
                [("walk", None), ("trot", None), ("walk", None), ("walk", None)],
            )),
            ("hedgehog", 1.66, _loop_8(
                "T",
                [(1058, 434), (1148, 516), (1064, 522), (1142, 424)],
                [("sniff_ground", 1, None), ("belly_roll", -1, None), ("scratch_ear", 1, None), ("sleep_curl_breathe", -1, "zzz")],
                [("walk", None), ("walk", None), ("trot", None), ("walk", None)],
            )),
            ("spotted_deer", 1.72, _loop_8(
                "S",
                [(864, 324), (926, 366), (1136, 368), (938, 366)],
                [("stargaze_meteor", 1, None), ("drink_ripple", 1, None), ("stretch_bow", -1, None), ("ear_perk_alert", -1, None)],
                [("gallop", "sparkle"), ("trot", None), ("trot", None), ("gallop", None)],
            )),
            ("tree_frog", 1.66, _loop_8(
                "T",
                [(1126, 228), (1154, 368), (1068, 486), (1134, 332)],
                [("sun_bask", 1, None), ("yawn", -1, None), ("crouch_stalk", -1, None), ("perch_sway", 1, "note")],
                [("hop", "note"), ("boop_firefly", None), ("hop", None), ("pounce_play", None)],
            )),
            ("azure_bluebird", 1.68, _loop_8(
                "S",
                [(1134, 96), (1152, 244), (1126, 366), (1146, 178)],
                [("perch_sway", -1, None), ("happy_spin", -1, "note"), ("groom_paw", -1, None), ("sleep_curl_breathe", 1, "zzz")],
                [("chase_butterfly", "note"), ("gallop", None), ("gallop", None), ("chase_butterfly", None)],
            )),
        ]
    if scene.startswith("card"):
        card_casts = {
            "card1": [
                ("shiba_dog", 1.62, _loop_8(
                    "S",
                    [(56, 128), (196, 74), (336, 134), (244, 142)],
                    [("stargaze_meteor", 1, "sparkle"), ("tail_wag_happy", 1, None), ("belly_roll", -1, "heart"), ("stretch_bow", -1, None)],
                    [("trot", None), ("gallop", None), ("trot", None), ("walk", None)],
                )),
                ("calico_cat", 1.58, _loop_8(
                    "T",
                    [(328, 66), (132, 118), (62, 62), (286, 138)],
                    [("groom_paw", -1, None), ("sun_bask", 1, "heart"), ("scratch_ear", 1, None), ("sleep_curl_breathe", -1, "zzz")],
                    [("walk", None), ("trot", None), ("walk", None), ("trot", None)],
                )),
                ("azure_bluebird", 1.56, _loop_8(
                    "S",
                    [(338, 96), (228, 56), (92, 86), (296, 118)],
                    [("perch_sway", -1, None), ("happy_spin", -1, "note"), ("yawn", 1, None), ("perch_sway", -1, None)],
                    [("chase_butterfly", "note"), ("gallop", None), ("gallop", None), ("boop_firefly", None)],
                )),
            ],
            "card2": [
                ("red_fox", 1.62, _loop_8(
                    "S",
                    [(62, 132), (218, 68), (338, 136), (176, 142)],
                    [("crouch_stalk", 1, None), ("sniff_ground", 1, None), ("sleep_curl_breathe", -1, "zzz"), ("shake_fur", -1, None)],
                    [("pounce_play", "sparkle"), ("trot", None), ("walk", None), ("gallop", None)],
                )),
                ("cottontail_rabbit", 1.60, _loop_8(
                    "T",
                    [(326, 122), (156, 136), (58, 66), (278, 92)],
                    [("graze_nibble", -1, None), ("ear_perk_alert", 1, None), ("sun_bask", 1, None), ("drink_ripple", 1, None)],
                    [("hop", None), ("binky_leap", "sparkle"), ("hop", None), ("hop", None)],
                )),
                ("tawny_owl", 1.64, _loop_8(
                    "S",
                    [(340, 58), (186, 56), (88, 98), (298, 78)],
                    [("perch_sway", -1, "sparkle"), ("stargaze_meteor", -1, None), ("yawn", 1, None), ("sleep_curl_breathe", -1, "zzz")],
                    [("gallop", None), ("chase_butterfly", None), ("gallop", None), ("gallop", None)],
                )),
            ],
            "card3": [
                ("spotted_deer", 1.60, _loop_8(
                    "S",
                    [(68, 134), (228, 78), (340, 138), (188, 142)],
                    [("stargaze_meteor", 1, "sparkle"), ("graze_nibble", 1, None), ("ear_perk_alert", -1, None), ("stretch_bow", -1, None)],
                    [("trot", None), ("gallop", None), ("walk", None), ("trot", None)],
                )),
                ("red_squirrel", 1.58, _loop_8(
                    "T",
                    [(324, 66), (144, 58), (62, 98), (286, 132)],
                    [("happy_spin", -1, "note"), ("tail_wag_happy", 1, None), ("groom_paw", 1, None), ("shake_fur", -1, None)],
                    [("hop", None), ("binky_leap", None), ("hop", None), ("hop", None)],
                )),
                ("tree_frog", 1.56, _loop_8(
                    "S",
                    [(336, 126), (254, 142), (128, 118), (298, 76)],
                    [("sun_bask", -1, None), ("yawn", -1, None), ("perch_sway", 1, "note"), ("crouch_stalk", 1, None)],
                    [("hop", None), ("boop_firefly", None), ("hop", None), ("pounce_play", None)],
                )),
            ],
        }
        return card_casts.get(scene, card_casts["card1"])
    return [
        ("shiba_dog", 1.98, _loop_8(
            "S",
            [(118, 332), (486, 248), (784, 344), (368, 192)],
            [("stargaze_meteor", 1, "sparkle"), ("stretch_bow", 1, None), ("belly_roll", -1, "heart"), ("tail_wag_happy", -1, None)],
            [("trot", None), ("gallop", None), ("trot", None), ("walk", None)],
        )),
        ("red_fox", 1.96, _loop_8(
            "T",
            [(456, 338), (742, 226), (968, 326), (628, 286)],
            [("crouch_stalk", 1, None), ("sleep_curl_breathe", -1, "zzz"), ("sniff_ground", -1, None), ("shake_fur", -1, None)],
            [("pounce_play", "sparkle"), ("trot", None), ("boop_firefly", None), ("gallop", None)],
        )),
        ("calico_cat", 1.92, _loop_8(
            "S",
            [(648, 346), (892, 238), (586, 178), (434, 294)],
            [("groom_paw", 1, None), ("scratch_ear", -1, None), ("sun_bask", -1, "heart"), ("yawn", 1, None)],
            [("walk", None), ("trot", None), ("walk", None), ("trot", None)],
        )),
        ("cottontail_rabbit", 1.95, _loop_8(
            "T",
            [(84, 264), (336, 346), (548, 234), (246, 176)],
            [("ear_perk_alert", 1, None), ("graze_nibble", 1, None), ("sniff_ground", -1, None), ("sun_bask", -1, None)],
            [("binky_leap", "sparkle"), ("hop", None), ("hop", None), ("binky_leap", None)],
        )),
        ("red_squirrel", 1.90, _loop_8(
            "S",
            [(218, 198), (442, 156), (294, 298), (96, 214)],
            [("tail_wag_happy", 1, None), ("happy_spin", -1, "note"), ("graze_nibble", -1, None), ("groom_paw", 1, None)],
            [("hop", None), ("hop", None), ("binky_leap", None), ("trot", None)],
        )),
        ("tawny_owl", 1.96, _loop_8(
            "T",
            [(168, 86), (618, 128), (1046, 78), (542, 68)],
            [("perch_sway", 1, "sparkle"), ("stargaze_meteor", -1, None), ("sleep_curl_breathe", -1, "zzz"), ("yawn", 1, None)],
            [("gallop", None), ("gallop", None), ("chase_butterfly", None), ("gallop", None)],
        )),
        ("mallard_duck", 1.92, _loop_8(
            "S",
            [(956, 348), (1132, 264), (924, 212), (836, 326)],
            [("drink_ripple", 1, None), ("graze_nibble", -1, None), ("sun_bask", -1, "note"), ("sleep_curl_breathe", 1, None)],
            [("walk", None), ("walk", None), ("trot", None), ("walk", None)],
        )),
        ("hedgehog", 1.92, _loop_8(
            "T",
            [(718, 354), (942, 294), (1094, 346), (848, 252)],
            [("sniff_ground", 1, None), ("belly_roll", 1, None), ("scratch_ear", -1, None), ("sleep_curl_breathe", -1, "zzz")],
            [("walk", None), ("walk", None), ("trot", None), ("walk", None)],
        )),
        ("spotted_deer", 1.88, _loop_8(
            "S",
            [(812, 296), (1088, 204), (838, 156), (568, 256)],
            [("stargaze_meteor", 1, None), ("drink_ripple", -1, None), ("ear_perk_alert", -1, None), ("stretch_bow", 1, None)],
            [("gallop", "sparkle"), ("trot", None), ("gallop", None), ("trot", None)],
        )),
        ("tree_frog", 1.95, _loop_8(
            "T",
            [(1048, 338), (904, 232), (1126, 196), (988, 296)],
            [("sun_bask", -1, None), ("yawn", 1, None), ("perch_sway", -1, "note"), ("crouch_stalk", 1, None)],
            [("hop", "note"), ("boop_firefly", None), ("hop", None), ("pounce_play", None)],
        )),
        ("azure_bluebird", 1.90, _loop_8(
            "S",
            [(1112, 118), (748, 92), (338, 114), (694, 168)],
            [("perch_sway", -1, None), ("happy_spin", -1, "note"), ("sleep_curl_breathe", 1, "zzz"), ("shake_fur", 1, None)],
            [("chase_butterfly", "note"), ("gallop", None), ("gallop", None), ("chase_butterfly", None)],
        )),
    ]


def _render_single_animal(prefix, actor_idx, species, scale, segments):
    p = prefix
    s_idx = ANIMAL_SPECIES.index(species)
    rx, ry = ANIMAL_CATALOG[species]["shadow"]

    pos_kt = ";".join(num(s[0], 3) for s in segments)
    pos_vals = ";".join("%s %s" % (num(s[1], 1), num(s[2], 1)) for s in segments)
    active = segments[:-1]
    sc_s = num(scale, 2)

    shadow_el = '<ellipse class="%s-s" cy="-1.2" rx="%s" ry="%s"/>' % (p, num(rx, 1), num(ry, 1))
    rig_parts = ['<use class="%s-%s" href="#%s-%d%s"/>' % (p, PART_SHORT[pk], p, s_idx, PART_SHORT[pk]) for pk in PART_KEYS]
    rig_inner = '<g class="%s-r">%s</g>' % (p, "".join(rig_parts))

    q_tag = "t" if len(segments) > 1 and abs(segments[1][0] - 0.13) < 0.005 else "s"
    used_anims = [s[3] for s in active]
    slots_svg = []
    for ph_i, s in enumerate(active):
        anim_name = s[3]
        a_idx = ANIMATION_NAMES.index(anim_name)
        q_cls = "%s-q%s%d" % (p, q_tag, ph_i)
        flip_attr = "" if s[4] >= 0 else ' transform="scale(-1 1)"'
        slots_svg.append(
            '<g class="%s %s-a%d" data-anim="%s"%s>%s%s</g>'
            % (q_cls, p, a_idx, anim_name, flip_attr, shadow_el, rig_inner)
        )

    emotes_svg = []
    for ph_i, s in enumerate(active):
        if s[5]:
            q_cls = "%s-q%s%d" % (p, q_tag, ph_i)
            emotes_svg.append('<use class="%s" href="#%s-em-%s"/>' % (q_cls, p, s[5]))

    live_node = (
        '<g id="%s-eco-act-%d" class="%s-sp%d" data-species="%s" data-anims="%s" transform="translate(%s %s)">'
        '<animateTransform attributeName="transform" type="translate" values="%s" keyTimes="%s" dur="60s" repeatCount="indefinite"/>'
        '<g transform="scale(%s)">%s%s</g></g>'
        % (
            p,
            actor_idx,
            p,
            s_idx,
            species,
            ",".join(used_anims),
            num(segments[0][1], 1),
            num(segments[0][2], 1),
            pos_vals,
            pos_kt,
            sc_s,
            "".join(slots_svg),
            "".join(emotes_svg),
        )
    )

    calm_seg = active[len(active) // 2]
    calm_tr = ("scale(%s)" % sc_s) if calm_seg[4] >= 0 else ("scale(-%s %s)" % (sc_s, sc_s))
    calm_node = '<use href="#%s-s%d-full" transform="translate(%s %s) %s"/>' % (
        p, s_idx, num(calm_seg[1], 1), num(calm_seg[2], 1), calm_tr
    )
    return live_node, calm_node


def _render_butterflies_layer(prefix, scene):
    p = prefix
    if scene == "matrix":
        paths = [
            ("bfm", "M 366,260 C 448,232 566,242 642,262 C 572,272 446,272 366,260 Z", "19s", 1.45),
            ("bfg", "M 744,262 C 818,236 912,240 956,262 C 896,272 806,272 744,262 Z", "22s", 1.42),
            ("bfm", "M 188,396 C 288,362 436,368 498,412 C 412,438 262,432 188,396 Z", "24s", 1.38),
        ]
    elif scene == "core":
        paths = [
            ("bfm", "M 54,518 C 88,486 136,494 144,528 C 118,544 76,542 54,518 Z", "18s", 1.38),
            ("bfg", "M 362,520 C 396,488 446,494 458,528 C 424,544 384,542 362,520 Z", "21s", 1.36),
            ("bfm", "M 852,108 C 886,84 928,90 940,122 C 912,136 872,132 852,108 Z", "23s", 1.34),
        ]
    elif scene.startswith("card"):
        paths = [
            ("bfm", "M 56,78 C 126,48 234,54 276,88 C 214,112 112,106 56,78 Z", "17s", 1.18),
            ("bfg", "M 248,118 C 286,94 332,100 344,128 C 314,142 272,140 248,118 Z", "20s", 1.12),
        ]
    else:
        paths = [
            ("bfm", "M 164,316 C 268,256 418,268 486,324 C 396,348 254,344 164,316 Z", "21s", 1.56),
            ("bfg", "M 548,318 C 658,258 812,268 896,322 C 792,346 648,344 548,318 Z", "24s", 1.52),
            ("bfm", "M 862,306 C 948,254 1068,262 1126,312 C 1046,336 936,332 862,306 Z", "19.5s", 1.48),
            ("bfg", "M 92,228 C 172,178 278,188 318,238 C 254,258 154,254 92,228 Z", "26s", 1.44),
        ]

    live = []
    calm = []
    for idx, (code, d_path, dur_s, sc) in enumerate(paths):
        sc_s = num(sc, 2)
        f1 = "#%s-eco-%s1" % (p, code)
        live.append(
            '<g><animateMotion path="%s" dur="%s" begin="%ss" repeatCount="indefinite"/>'
            '<use href="#%s-%s-fl" transform="scale(%s)"/></g>'
            % (d_path, dur_s, num(-idx * 4.3, 1), p, code, sc_s)
        )
        m_coords = d_path.split("C")[0].replace("M", "").strip().split(",")
        calm.append(
            '<use href="%s" transform="translate(%s %s) scale(%s)"/>'
            % (f1, m_coords[0].strip(), m_coords[1].strip(), sc_s)
        )
    return "".join(live), "".join(calm)


def render_ecosystem_stage(prefix, scene_kind="nocturne", width=1200, height=388):
    scene = _norm_scene(scene_kind)
    p = prefix
    props_live, props_calm, n_props = _render_props_layer(p, scene)
    bf_live, bf_calm = _render_butterflies_layer(p, scene)
    cast = _scene_menagerie_cast(scene)

    animals_live = []
    animals_calm = []
    for idx, (sp_name, sc, segs) in enumerate(cast):
        lnode, cnode = _render_single_animal(p, idx, sp_name, sc, segs)
        animals_live.append(lnode)
        animals_calm.append(cnode)

    ff_markup = render_fireflies_svg(p, scene, width, height)

    return (
        '<g id="%s-eco-stage" class="eco-stage" data-scene="%s" data-species-count="%d" data-anim-count="%d" data-props-count="%d" data-cycle-seconds="60" pointer-events="none">'
        '<g class="eco-live %s-eco-live">%s%s%s</g>'
        '<g class="eco-calm %s-eco-calm">%s%s%s</g>'
        "%s</g>"
        % (
            p,
            scene,
            len(cast),
            len(ANIMATION_NAMES),
            n_props,
            p,
            props_live,
            "".join(animals_live),
            bf_live,
            p,
            props_calm,
            "".join(animals_calm),
            bf_calm,
            ff_markup,
        )
    )
