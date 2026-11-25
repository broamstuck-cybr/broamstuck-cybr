// SPDX-License-Identifier: MIT
// WHY: 60 FPS living 2D pixel ecosystem: 11 shaded species x 25 animations, >=40 interactive micro-habitat props, bioluminescent fireflies, 60s day-night cycle, and full-viewport free roaming.

import {
  SPECIES_IDS,
  ANIMATION_25,
  COMPANION_SPECIES_DEFS,
  PROP_CATALOG,
  bakeCompanionSprites,
  bakePropSprites
} from "./ecosystem-data.js";
import { evaluateDayNightCycle, DAY_NIGHT_CYCLE_SEC } from "./sky-engine.js";

const FIREFLY_COLORS = ["#bef264", "#fde047", "#86efac", "#fef08a", "#34d399"];
const DEW_COLORS = ["#bae6fd", "#7dd3fc", "#fef9c3", "#ffffff"];
const LOCOMOTION_ANIMS = new Set(["walk", "trot", "gallop", "hop", "chaseButterfly", "crouchStalk"]);

const PALETTE = {
  O: "#2b150c",
  D: "#632b15",
  R: "#a44c1b",
  C: "#d67425",
  G: "#f4a23a",
  H: "#fcd268",
  S: "#e2d2ad",
  W: "#fff8e3",
  E: "#170e19",
  L: "#ffffff",
  P: "#f48fb1",
  B: "#1d4ed8",
  N: "#3b82f6",
  Y: "#fde047",
  K: "#be123c",
  M: "#f43f5e",
  Q: "#fda4af",
  T: "#38bdf8",
  U: "#bae6fd",
  A: "#fb923c",
  F: "#fbbf24",
  I: "#fef08a",
  J: "#0c1e3d",
  V: "#064e3b",
  Z: "#15803d",
  X: "#34d399",
  g: "#6ee7b7"
};

const SPRITE_W = 32;
const SPRITE_H = 28;
const EMOTE_SIZE = 11;
const BF_W = 13;
const BF_H = 11;
const TWIG_W = 9;
const TWIG_H = 5;
const PIXEL_SCALE = 2;
// WHY: 1.30x animal scale renders all 11 species +30% larger across desktop/tablet/mobile while keeping crisp nearest-neighbor texels.
const ANIMAL_SCALE = PIXEL_SCALE * 1.3;
const BF_SCALE = PIXEL_SCALE * 1.25;

const PAN_SUNFLOWERS = [
  [0.036, 0.81],
  [0.088, 0.88],
  [0.964, 0.82],
  [0.914, 0.89]
];

const GAR_SUNFLOWERS = [
  [0.044, 0.57],
  [0.114, 0.67],
  [0.058, 0.83],
  [0.176, 0.79],
  [0.242, 0.88],
  [0.956, 0.57],
  [0.886, 0.67],
  [0.942, 0.83],
  [0.824, 0.79],
  [0.758, 0.88]
];

const FRAMES = {
  trot0: [
    "................................",
    "................................",
    "................OO.....OO.......",
    "...............OHGO...OHGO......",
    "...............OGWGO.OGPGO......",
    "...............OGPWOOOHGGO......",
    "...............OHHHHHHHHGGO.....",
    "..............OHGGGGWGGGWGO.....",
    "..............OGGGGLEEGGLEGO....",
    "..............OGGGPEEEGGEEOO....",
    "....OOO.......OCGGGWWWWWWEEO....",
    "...OWWHO......OCGWWWWWWWWWWOO...",
    "..OWWWGHO......OCWWWWWWWWWWO....",
    "..OWGHGGRO.....OOBBNNNNYYBBO....",
    "...ORGGGHOOOOOOHHHHHBNYYNBBBO...",
    "....ORGGGGGGGGGGGGGGGBNNWWWWWO..",
    ".....ORGGGGGGGGGGGGGGWWWWWWWWWO.",
    "......ORCCCCCCCCGGGGGGWWWWWWWWO.",
    "......ORCCCCCCCCCCGGGGWWWWWWWSO.",
    ".......ORRRRRCCCCCCCSSWWWWWWSSO.",
    "........OORRRDDDDDDDDSSSSSSSOO..",
    ".......ORCO.ODDO..ODDO.OGGO.....",
    "......OCCO..ODDO..ODDO..OGCO....",
    ".....OWWWO..OSSO..OSSO..OWWWO...",
    ".....OOOO...OOOO..OOOO...OOOO...",
    "................................",
    "................................",
    "................................"
  ],
  trot1: [
    "................................",
    "................OO.....OO.......",
    "...............OHGO...OHGO......",
    "...............OGWGO.OGPGO......",
    "...............OGPWOOOHGGO......",
    "...............OHHHHHHHHGGO.....",
    "..............OHGGGGWGGGWGO.....",
    "..............OGGGGLEEGGLEGO....",
    "..............OGGGPEEEGGEEOO....",
    "...OOO........OCGGGWWWWWWEEO....",
    "..OWWHO.......OCGWWWWWWWWWWOO...",
    "..OWWWHO.......OCWWWWWWWWWWO....",
    "..OWGHGRO......OOBBNNNNYYBBO....",
    "...ORGGGHOOOOOOHHHHBNYYNNBBBO...",
    "....ORGGGGGGGGGGGGGBNYNWWWWWO...",
    ".....ORGGGGGGGGGGGGGGWWWWWWWWWO.",
    "......ORCCCCCCCCGGGGGGWWWWWWWWO.",
    "......ORCCCCCCCCCCGGGGWWWWWWWSO.",
    ".......ORRRRRCCCCCCCSSWWWWWWSSO.",
    "........OORRRDDDDDDDDSSSSSSSOO..",
    "........ORCO.ODDO..ODDO.OGGO....",
    "........OCCO.OSSO..OSSO.OGCO....",
    "........OWWO.OOOO..OOOO.OWWO....",
    "........OOOO............OOOO....",
    "................................",
    "................................",
    "................................",
    "................................"
  ],
  trot2: [
    "................................",
    "................................",
    "...............OO.....OO........",
    "..............OHGO...OHGO.......",
    "..............OGWGO.OGPGO.......",
    "...............OGPWOOOHGGO......",
    "...............OHHHHHHHHGGO.....",
    "..............OHGGGGWGGGWGO.....",
    "..............OGGGGLEEGGLEGO....",
    "..............OGGGPEEEGGEEOO....",
    ".....OOO......OCGGGWWWWWWEEO....",
    "....OWWHO.....OCGWWWWWWWWWWOO...",
    "...OWWWGHO.....OCWWWWWWWWWWO....",
    "...OWGHGGRO....OOBBNNNNYYBBO....",
    "....ORGGHOOOOOOHHHHHBNYYNBBBO...",
    "....ORGGGGGGGGGGGGGGGBNNWWWWWO..",
    ".....ORGGGGGGGGGGGGGGWWWWWWWWWO.",
    "......ORCCCCCCCCGGGGGGWWWWWWWWO.",
    "......ORCCCCCCCCCCGGGGWWWWWWWSO.",
    ".......ORRRRRCCCCCCCSSWWWWWWSSO.",
    "........OORRRDDDDDDDDSSSSSSSOO..",
    ".......ODDO.ORCO..OGGO.ODDO.....",
    "......ODDO..OCCO..OGCO..ODDO....",
    "......OSSO..OWWWO.OWWWO..OSSO...",
    "......OOOO..OOOO..OOOO...OOOO...",
    "................................",
    "................................",
    "................................"
  ],
  trot3: [
    "................................",
    "................OO.....OO.......",
    "...............OHGO...OHGO......",
    "...............OGWGO.OGPGO......",
    "...............OGPWOOOHGGO......",
    "...............OHHHHHHHHGGO.....",
    "..............OHGGGGWGGGWGO.....",
    "..............OGGGGLEEGGLEGO....",
    "..............OGGGPEEEGGEEOO....",
    "....OOO.......OCGGGWWWWWWEEO....",
    "...OWWHO......OCGWWWWWWWWWWOO...",
    "..OWWWGHO......OCWWWWWWWWWWO....",
    "..OWGHGGRO.....OOBBNNNNYYBBO....",
    "...ORGGGHOOOOOOHHHHHBNYYNBBBO...",
    "....ORGGGGGGGGGGGGGGGBNNWWWWWO..",
    ".....ORGGGGGGGGGGGGGGWWWWWWWWWO.",
    "......ORCCCCCCCCGGGGGGWWWWWWWWO.",
    "......ORCCCCCCCCCCGGGGWWWWWWWSO.",
    ".......ORRRRRCCCCCCCSSWWWWWWSSO.",
    "........OORRRDDDDDDDDSSSSSSSOO..",
    ".........ODDO.ORCOOGGO.ODDO.....",
    ".........OSSO.OCCOOGCO.OSSO.....",
    ".........OOOO.OWWOOWWO.OOOO.....",
    "..............OOOOOOOO..........",
    "................................",
    "................................",
    "................................",
    "................................"
  ],
  run0: [
    "................................",
    ".................OO.....OO......",
    "................OHGO...OHGO.....",
    "...............OGWGO..OGPGO.....",
    "...............OGPWOOOOHGGO.....",
    "...............OHHHHHHHHHGGO....",
    "..............OHGGGGWGGGWGO.....",
    "..............OGGGGLEEGGLEGO....",
    "..OOOO........OGGGPEEEGGEEOO....",
    ".OWWWHO.......OCGGGWWWWWWEEO....",
    ".OWWWGHO......OCGWWWWWWWWWWOO...",
    "..OWGHGRO......OCWWWWWWWWWWO....",
    "...ORGGGHOOOOOOBBNNNNYYBBBO.....",
    "....ORHHHHHHHHHHBNYYNNWWWWWO....",
    ".....ORGGGGGGGGGGGBNNWWWWWWWO...",
    "......ORCCCCCCCCGGGGGWWWWWWWWO..",
    ".......ORRRRRCCCCCCCSWWWWWWWSSO.",
    "........OORRRDDDDDDDDSSSSSSSOO..",
    ".....ORCCO.ODDO.......OGGCO.OSSO",
    "....OWWWO.OSSO.........OWWWOOWWO",
    "....OOOO..OOOO..........OOOOOOOO",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................"
  ],
  run1: [
    "................................",
    "................................",
    "................OO.....OO.......",
    "...............OHGO...OHGO......",
    "...............OGWGO.OGPGO......",
    "...............OGPWOOOHGGO......",
    "...............OHHHHHHHHGGO.....",
    "..............OHGGGGWGGGWGO.....",
    "..............OGGGGLEEGGLEGO....",
    "...OOOO.......OGGGPEEEGGEEOO....",
    "..OWWWHO......OCGGGWWWWWWEEO....",
    "..OWGHGRO.....OCGWWWWWWWWWWOO...",
    "...ORGGGHO.....OCWWWWWWWWWWO....",
    "....ORGGGHOOOOOBBNNNNYYBBBO.....",
    ".....ORHHHHHHHHHHBNYYNWWWWWO....",
    ".....ORGGGGGGGGGGGGBNWWWWWWWO...",
    "......ORCCCCCCCCGGGGGWWWWWWWWO..",
    ".......ORRRRRCCCCCCCSWWWWWWWSSO.",
    "........OORRRDDDDDDDDSSSSSSSOO..",
    "..........ODDOORCO..OGGOODDO....",
    ".........OSSO.OCCO..OGCO.OSSO...",
    ".........OOOO.OWWO..OWWO.OOOO...",
    "..............OOOO..OOOO........",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................"
  ],
  sit0: [
    "................................",
    "...............OO.....OO........",
    "..............OHGO...OHGO.......",
    "..............OGWGO.OGPGO.......",
    "..............OGPWOOOHGGO.......",
    "..............OHHHHHHHHGGO......",
    ".............OHGGGGWGGGWGO......",
    ".............OGGGGLEEGGLEGO.....",
    ".............OGGGPEEEGGEEOO.....",
    ".............OCGGGWWWWWWEEO.....",
    ".............OCGWWWWWWWWWWOO....",
    "..............OCWWWWWWWWWWO.....",
    "..............OOBBNNNNYYBBO.....",
    "............OOOHHHBNYYNNBBBO....",
    "...........OHGGGGGGGBNNWWWWWO...",
    "....OOO...OHGGGGGGGGWWWWWWWWWO..",
    "...OWWHO.OHGGGGGGGGGWWWWWWWWWO..",
    "..OWWWGHOOGGGGGGGGGWWWWWWWWWWSO.",
    "..OWGHGGROCCCCCCCCGWWWWWWWWWWSSO",
    "...ORGGGGCCCCCCCCCCSWWWWWWWWWSSO",
    "....ORRRRRCCCCCCCCCSSSWWWWWWSSOO",
    ".....OORRRRRRDDDDDDSSSOOWWWOSSO.",
    ".......OORRRRRRDDDDSSOOOWWWOO...",
    "........OWWWOOOOOOOOO..OOOOO....",
    "........OOOOO...................",
    "................................",
    "................................",
    "................................"
  ],
  sit1: [
    "................................",
    "...............OO.....OO........",
    "..............OHGO...OHGO.......",
    "..............OGWGO.OGPGO.......",
    "..............OGPWOOOHGGO.......",
    "..............OHHHHHHHHGGO......",
    ".............OHGGGGWGGGWGO......",
    ".............OGGGGLEEGGLEGO.....",
    ".............OGGGPEEEGGEEOO.....",
    ".............OCGGGWWWWWWEEO.....",
    ".............OCGWWWWWWWWWWOO....",
    "..............OCWWWWWWWWWWO.....",
    "..............OOBBNNNNYYBBO.....",
    "............OOOHHHBNYYNNBBBO....",
    "...OOO.....OHGGGGGGGBNNWWWWWO...",
    "..OWWHO...OHGGGGGGGGWWWWWWWWWO..",
    ".OWWWGHO.OHGGGGGGGGGWWWWWWWWWO..",
    "..OWGHGROOGGGGGGGGGWWWWWWWWWWSO.",
    "...ORGGGGOCCCCCCCCGWWWWWWWWWWSSO",
    "....ORGGGCCCCCCCCCCSWWWWWWWWWSSO",
    ".....ORRRRCCCCCCCCCSSSWWWWWWSSOO",
    ".....OORRRRRRDDDDDDSSSOOWWWOSSO.",
    ".......OORRRRRRDDDDSSOOOWWWOO...",
    "........OWWWOOOOOOOOO..OOOOO....",
    "........OOOOO...................",
    "................................",
    "................................",
    "................................"
  ],
  sitBlink: [
    "................................",
    "...............OO.....OO........",
    "..............OHGO...OHGO.......",
    "..............OGWGO.OGPGO.......",
    "..............OGPWOOOHGGO.......",
    "..............OHHHHHHHHGGO......",
    ".............OHGGGGWGGGWGO......",
    ".............OGGGGGGGGGGGGO.....",
    ".............OGGGPEEEGGEEOO.....",
    ".............OCGGGWWWWWWEEO.....",
    ".............OCGWWWWWWWWWWOO....",
    "..............OCWWWWWWWWWWO.....",
    "..............OOBBNNNNYYBBO.....",
    "............OOOHHHBNYYNNBBBO....",
    "...........OHGGGGGGGBNNWWWWWO...",
    "....OOO...OHGGGGGGGGWWWWWWWWWO..",
    "...OWWHO.OHGGGGGGGGGWWWWWWWWWO..",
    "..OWWWGHOOGGGGGGGGGWWWWWWWWWWSO.",
    "..OWGHGGROCCCCCCCCGWWWWWWWWWWSSO",
    "...ORGGGGCCCCCCCCCCSWWWWWWWWWSSO",
    "....ORRRRRCCCCCCCCCSSSWWWWWWSSOO",
    ".....OORRRRRRDDDDDDSSSOOWWWOSSO.",
    ".......OORRRRRRDDDDSSOOOWWWOO...",
    "........OWWWOOOOOOOOO..OOOOO....",
    "........OOOOO...................",
    "................................",
    "................................",
    "................................"
  ],
  sitTilt: [
    "..............OO................",
    ".............OHGO......OO.......",
    ".............OGWGO....OHGO......",
    ".............OGPWOO..OGPGO......",
    "..............OHHHHOOOHGGO......",
    ".............OHHHHHHHHGGO.......",
    ".............OHGGGWGGGGWGO......",
    ".............OGGGLEEGGLGGO......",
    ".............OGGGPEEEGGEEOO.....",
    ".............OCGGGWWWWWWEEO.....",
    ".............OCGWWWWWWWWWWOO....",
    "..............OCWWWWWWWWWWO.....",
    "..............OOBBNNNNYYBBO.....",
    "............OOOHHHBNYYNNBBBO....",
    "...OOO.....OHGGGGGGGBNNWWWWWO...",
    "..OWWHO...OHGGGGGGGGWWWWWWWWWO..",
    ".OWWWGHO.OHGGGGGGGGGWWWWWWWWWO..",
    "..OWGHGROOGGGGGGGGGWWWWWWWWWWSO.",
    "...ORGGGGOCCCCCCCCGWWWWWWWWWWSSO",
    "....ORGGGCCCCCCCCCCSWWWWWWWWWSSO",
    ".....ORRRRCCCCCCCCCSSSWWWWWWSSOO",
    ".....OORRRRRRDDDDDDSSSOOWWWOSSO.",
    ".......OORRRRRRDDDDSSOOOWWWOO...",
    "........OWWWOOOOOOOOO..OOOOO....",
    "........OOOOO...................",
    "................................",
    "................................",
    "................................"
  ],
  sitEar: [
    "...............OO......OO.......",
    "..............OHGO....OHGO......",
    "..............OGWGO...OGPGO.....",
    "..............OGPWOOOOHGGO......",
    "..............OHHHHHHHHHGGO.....",
    ".............OHGGGGWGGGWGO......",
    ".............OGGGGLEEGGLEGO.....",
    ".............OGGGPEEEGGEEOO.....",
    ".............OCGGGWWWWWWEEO.....",
    ".............OCGWWWWWWWWWWOO....",
    "..............OCWWWWWWWWWWO.....",
    "..............OOBBNNNNYYBBO.....",
    "............OOOHHHBNYYNNBBBO....",
    "...........OHGGGGGGGBNNWWWWWO...",
    "...OOO....OHGGGGGGGGWWWWWWWWWO..",
    "..OWWHO..OHGGGGGGGGGWWWWWWWWWO..",
    "..OWWWHO.OGGGGGGGGGWWWWWWWWWWSO.",
    "..OWGHGROOCCCCCCCCGWWWWWWWWWWSSO",
    "...ORGGGGCCCCCCCCCCSWWWWWWWWWSSO",
    "....ORRRRRCCCCCCCCCSSSWWWWWWSSOO",
    ".....OORRRRRRDDDDDDSSSOOWWWOSSO.",
    ".......OORRRRRRDDDDSSOOOWWWOO...",
    "........OWWWOOOOOOOOO..OOOOO....",
    "........OOOOO...................",
    "................................",
    "................................",
    "................................",
    "................................"
  ],
  rest0: [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................OO.....OO.......",
    "...............OHGO...OHGO......",
    "...............OGWGO.OGPGO......",
    "...............OGPWOOOHGGO......",
    "...............OHHHHHHHHGGO.....",
    "..............OHGGGGWGGGWGO.....",
    "....OOO.......OGGGGLEEGGLEGO....",
    "...OWWHO......OGGGPEEEGGEEOO....",
    "..OWWWGHO.....OCGGGWWWWWWEEO....",
    "..OWGHGGROOOOOOCGWWWWWWWWWWOO...",
    "...ORHHHHHHHHHHOCWWWWWWWWWWO....",
    "....ORGGGGGGGGGGOOBBNNNNYYBBO...",
    "....ORGGGGGGGGGGGGBNYYNNWWWWWO..",
    ".....ORCCCCCCCCCCCGBNNWWWWWWWWOO",
    ".....ORRRRRRDDDDDDDWWWWWWWWWWWWO",
    "......OOOWWWWRDDDDDSSWWWWWOOWWWO",
    "........OOOOOOOOOOOOOOOOOO..OOOO",
    "................................",
    "................................",
    "................................"
  ],
  rest1: [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................OO.....OO.......",
    "...............OHGO...OHGO......",
    "...............OGWGO.OGPGO......",
    "...............OGPWOOOHGGO......",
    "...............OHHHHHHHHGGO.....",
    "..............OHGGGGWGGGWGO.....",
    "....OOO.......OGGGGGGGGGGGGO....",
    "...OWWHO......OGGGPEEEGGEEOO....",
    "..OWWWGHOOOOOOOCGGGWWWWWWEEO....",
    "..OWGHGGHHHHHHHHCGWWWWWWWWWWOO..",
    "...ORGGGGGGGGGGGOCWWWWWWWWWWO...",
    "....ORGGGGGGGGGGGOOBBNNNNYYBBO..",
    "....ORCCCCCCCCCCCGBNYYNNWWWWWO..",
    ".....ORCCCCCCCCCCCGBNNWWWWWWWWOO",
    ".....ORRRRRRDDDDDDDWWWWWWWWWWWWO",
    "......OOOWWWWRDDDDDSSWWWWWOOWWWO",
    "........OOOOOOOOOOOOOOOOOO..OOOO",
    "................................",
    "................................",
    "................................"
  ],
  sniff0: [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "....OOO.........................",
    "...OWWHO...........OO.....OO....",
    "..OWWWGHO.........OHGO...OHGO...",
    "..OWGHGGRO........OGWGO.OGPGO...",
    "...ORGGGHOOOOOOOO.OGPWOOOHGGO...",
    "....ORHHHHHHHHHHHOOHHHHHHHGGO...",
    ".....ORGGGGGGGGGGOBGGGGWGGGWGO..",
    "......ORGGGGGGGGGBNGGGLEEGGLEGO.",
    "......ORCCCCCCCCGBNYGGPEEEGGEEOO",
    "......ORCCCCCCCCCBNNYGWWWWWWEEOO",
    ".......ORRRRRCCCCBBNWWWWWWWWWWOO",
    "........OORRRDDDDDDWWWWWWWWWWOO.",
    "........ORCO.ODDO..OOOWWWWWOO...",
    ".......OCCO..ODDO..OGGOOOOO.....",
    ".......OCCO..ODDO..OGCO.OSSO....",
    ".......OWWWO.OSSO..OWWWOOWWO....",
    ".......OOOO..OOOO..OOOOOOOO.....",
    "................................",
    "................................",
    "................................",
    "................................"
  ],
  sniff1: [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "...OOO..........................",
    "..OWWHO.........................",
    "..OWWWHO...........OO.....OO....",
    "..OWGHGRO.........OHGO...OHGO...",
    "...ORGGGHO........OGWGO.OGPGO...",
    "....ORGGHOOOOOOOO.OGPWOOOHGGO...",
    ".....ORHHHHHHHHHHOOHHHHHHHGGO...",
    ".....ORGGGGGGGGGGOBGGGGWGGGWGO..",
    "......ORGGGGGGGGGBNGGGLEEGGLEGO.",
    "......ORCCCCCCCCGBNYGGPEEEGGEEOO",
    "......ORCCCCCCCCCBNNYGWWWWWWEEO.",
    ".......ORRRRRCCCCBBNWWWWWWWWWWOO",
    "........OORRRDDDDDDWWWWWWWWWWOO.",
    "........ORCO.ODDO..OOOWWWWWOO...",
    ".......OCCO..ODDO..OGGOOOOO.....",
    ".......OCCO..ODDO..OGCO.OSSO....",
    ".......OWWWO.OSSO..OWWWOOWWO....",
    ".......OOOO..OOOO..OOOOOOOO.....",
    "................................",
    "................................",
    "................................",
    "................................"
  ],
  sniffLow0: [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "....OOO.........................",
    "...OWWHO........................",
    "..OWWWGHO.......................",
    "..OWGHGGRO..........OO....OO....",
    "...ORGGGHOOOOOOO...OHGO..OHGO...",
    "....ORHHHHHHHHHHO..OGWGOOGPGO...",
    ".....ORGGGGGGGGGGO.OGPWOOHGGO...",
    "......ORGGGGGGGGGOBOHHHHHHGGO...",
    "......ORCCCCCCCCGBNOGGGWGGGWGO..",
    ".......ORCCCCCCCBNYOGGGLEEGGLEGO",
    ".......ORRRRRCCCBNNYGGGPEEEGGEEO",
    "........OORRRDDDDBBNWWWWWWWWEEOO",
    "........ORCO.ODDO..OCWWWWWWWWWOO",
    ".......OCCO..ODDO..OGGOOOOOOOO..",
    ".......OCCO..ODDO..OGCO.OGGO....",
    "......OWWWO..OSSO..OWWWOOGCO....",
    "......OOOO...OOOO..OOOO.OWWWO...",
    "........................OOOO....",
    "................................",
    "................................",
    "................................"
  ],
  sniffLow1: [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "...OOO..........................",
    "..OWWHO.........................",
    "..OWWWHO........................",
    "..OWGHGRO...........OO....OO....",
    "...ORGGGHO.........OHGO..OHGO...",
    "....ORGGHOOOOOOO...OGWGOOGPGO...",
    ".....ORHHHHHHHHHO..OGPWOOHGGO...",
    ".....ORGGGGGGGGGGO.OHHHHHHGGO...",
    "......ORGGGGGGGGGOBGGGGWGGGWGO..",
    "......ORCCCCCCCCGBNGGGGLEEGGLEGO",
    ".......ORCCCCCCCBNYGGGGPEEEGGEEO",
    ".......ORRRRRCCCBNNYCGGWWWWWWEEO",
    "........OORRRDDDDBBNCGWWWWWWWWOO",
    "........ORCO.ODDO..OCWWWWWWWWWOO",
    ".......OCCO..ODDO..OGGOOOOOOOO..",
    ".......OCCO..ODDO..OGCO.OGGO....",
    "......OWWWO..OSSO..OWWWOOGCO....",
    "......OOOO...OOOO..OOOO.OWWWO...",
    "........................OOOO....",
    "................................",
    "................................",
    "................................"
  ],
  sneeze0: [
    "................................",
    "................................",
    "..............OO.....OO.........",
    ".............OHGO...OHGO........",
    ".............OGWGO.OGPGO........",
    "..............OGPWOOOHGGO.......",
    "..............OHHHHHHHHGGO......",
    ".............OHGGGGWGGGWGO......",
    ".............OGGGGOOGGGOOGO.....",
    "....OOO......OGGGPOGGGGGGEEO....",
    "...OWWHO.....OCGGGWWWWWWPPWO....",
    "..OWWWGHO....OCGWWWWWWWWWWOO....",
    "..OWGHGGRO....OCWWWWWWWWWWO.....",
    "...ORGGGHOOOOOOBBNNNNYYBBO......",
    "....ORHHHHHHHHHHBNYYNNBBBO......",
    ".....ORGGGGGGGGGGBNNWWWWWO......",
    ".....ORGGGGGGGGGGGWWWWWWWWWO....",
    "......ORCCCCCCCCGGGWWWWWWWWO....",
    "......ORCCCCCCCCCCGGWWWWWWWSO...",
    ".......ORRRRRCCCCCCCSWWWWWWSSO..",
    "........OORRRDDDDDDDDSSSSSSSOO..",
    ".......ORCO.ODDO..ODDO.OGGO.....",
    "......OCCO..ODDO..ODDO..OGCO....",
    ".....OWWWO..OSSO..OSSO..OWWWO...",
    ".....OOOO...OOOO..OOOO...OOOO...",
    "................................",
    "................................",
    "................................"
  ],
  sneeze1: [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "...OOO..........................",
    "..OWWHO..........OOO....OOO.....",
    ".OWWWGHO........OHGGO..OHGGO....",
    "..OWGHGRO.......OGPWGOOGPWGO....",
    "...ORGGGHO......OHHHHHHHHHGGO...",
    "....ORGGGHOOOOOOOHGGGGWGGGWGO...",
    "....ORHHHHHHHHHHOGGGGOOGGGOOGO..",
    ".....ORGGGGGGGGGGOGGGPEEEGGEEOO.",
    "......ORCCCCCCCCGBNNGWWWWWWPPWOO",
    "......ORCCCCCCCCBNNYGWWWWWWWWOO.",
    ".......ORRRRRCCCCBBNWWWWWWWWWWO.",
    "........OORRRDDDDDDDWWWWWWWWWSO.",
    "........ORCO.ODDO..OSSSSSSSSOO..",
    ".......OCCO..ODDO..OGGO..ODDO...",
    ".......OCCO..ODDO..OGCO..ODDO...",
    "......OWWWO..OSSO..OWWWO.OSSO...",
    "......OWWWO..OSSO..OWWWO.OSSO...",
    "......OOOO...OOOO..OOOO..OOOO...",
    "................................",
    "................................",
    "................................"
  ],
  stalk0: [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "...OOO..........................",
    "..OWWHO.........................",
    ".OWWWGHO..........OO.....OO.....",
    "..OWGHGRO........OHGO...OHGO....",
    "...ORGGGHO.......OGWGO.OGPGO....",
    "....ORHHHHHOOOOO.OGPWOOOHGGO....",
    ".....ORHHHHHHHHHOOHHHHHHHHGGO...",
    "......ORGGGGGGGGGOBGGGGWGGGWGO..",
    "......ORCCCCCCCCGBNGGGLEEGGLEGO.",
    ".......ORCCCCCCCCBNYGGPEEEGGEEOO",
    ".......ORRRRRCCCCBNNYGWWWWWWEEO.",
    "........OORRRDDDDBBNWWWWWWWWWWOO",
    "........ORCO.ODDO..OCWWWWWWWWWO.",
    ".......OCCO..ODDO..OOBBNNYYWWWO.",
    ".......OCCO..ODDO...OOOGGGGWWOO.",
    "......OCCO...ODDO....OGGGGGGGWWO",
    "......OWWWO..OSSO....OCCCCWWWWWO",
    "......OWWWO..OSSO.....OOOOWWWWWO",
    "......OOOO...OOOO........OWWWWWO",
    ".........................OOOOOOO",
    "................................",
    "................................",
    "................................"
  ],
  stalk1: [
    "................................",
    "................................",
    "................................",
    "................................",
    "..OOO...........................",
    ".OWWHO..........................",
    ".OWWWGHO..........OO.....OO.....",
    "..OWGHGRO........OHGO...OHGO....",
    "...ORGGGHO.......OGWGO.OGPGO....",
    "....ORGGGGHOOOOO.OGPWOOOHGGO....",
    ".....ORHHHHHHHHHOOHHHHHHHHGGO...",
    "......ORGGGGGGGGGOBGGGGWGGGWGO..",
    "......ORCCCCCCCCGBNGGGLEEGGLEGO.",
    ".......ORCCCCCCCCBNYGGPEEEGGEEOO",
    ".......ORRRRRCCCCBNNYGWWWWWWEEO.",
    "........OORRRDDDDBBNWWWWWWWWWWOO",
    "........ORCO.ODDO..OCWWWWWWWWWO.",
    ".......OCCO..ODDO..OOBBNNYYWWWO.",
    ".......OCCO..ODDO...OOOGGGGWWOO.",
    "......OCCO...ODDO....OGGGGGGGWWO",
    "......OWWWO..OSSO....OCCCCWWWWWO",
    "......OWWWO..OSSO.....OOOOWWWWWO",
    "......OOOO...OOOO........OWWWWWO",
    ".........................OOOOOOO",
    "................................",
    "................................",
    "................................",
    "................................"
  ],
  pounce0: [
    "................................",
    ".................OO.....OO......",
    "................OHGO...OHGO.....",
    "................OGWGO.OGPGO.....",
    "................OGPWOOOHGGO.....",
    "................OHHHHHHHHGGO....",
    "...............OHGGGGWGGGWGO....",
    "...............OGGGGLEEGGLEGO...",
    "...............OGGGPEEEGGEEOO...",
    "...............OCGGGWWWWWWEEO...",
    "....OOO........OCGWWWWWWPPWWOO..",
    "...OWWHO........OCWWWWWWWWWWO...",
    "..OWWWGHO.......OOBBNNNNYYBBO...",
    "..OWGHGGRO....OOOHHHBNYYNNBBBO..",
    "...ORGGGHO..OOHGGGGGGGBNNWWWWWO.",
    "....ORGGGGHOHGGGGGGGGWWWWWWWWWWO",
    ".....ORGGGGGGGGGGGGGWWWWWWOOOWWO",
    "......ORCCCCCCCCGGGGWWWWWO..OOOO",
    "......ORCCCCCCCCCCGWWWWWWO......",
    ".......ORRRRRCCCCCCSSWWWWO......",
    ".......OORRRRRDDDDDDSSSSOO......",
    "......ORCCO.OODDDDDDSSOO........",
    ".....OCCO....ODDO.OSSO..........",
    "....OWWWO....OSSO.OWWWO.........",
    "....OOOO.....OOOO.OOOO..........",
    "................................",
    "................................",
    "................................"
  ],
  pounce1: [
    ".................OO.....OO......",
    "................OHGO...OHGO.....",
    "................OGWGO.OGPGO.....",
    "................OGPWOOOHGGO.....",
    "................OHHHHHHHHGGO....",
    "...............OHGGGGWGGGWGO....",
    "...............OGGGGLEEGGLEGO...",
    "...............OGGGPEEEGGEEOO...",
    "...............OCGGGWWWWWWEEO...",
    "...OOO.........OCGWWWWWWPPWWOO..",
    "..OWWHO.........OCWWWWWWWWWWO...",
    ".OWWWGHO........OOBBNNNNYYBBO...",
    "..OWGHGRO.....OOOHHHBNYYNNBBBO..",
    "...ORGGGHO..OOHGGGGGGGBNNWWWWWO.",
    "....ORGGGGHOHGGGGGGGGWWWWWWWWWWO",
    ".....ORGGGGGGGGGGGGGWWWWWWOOOWWO",
    "......ORCCCCCCCCGGGGWWWWWO..OOOO",
    "......ORCCCCCCCCCCGWWWWWWO......",
    ".......ORRRRRCCCCCCSSWWWWO......",
    ".......OORRRRRDDDDDDSSSSOO......",
    "......ORCCO.OODDDDDDSSOO........",
    ".....OCCO....ODDO.OSSO..........",
    "....OWWWO....OSSO.OWWWO.........",
    "....OOOO.....OOOO.OOOO..........",
    "................................",
    "................................",
    "................................",
    "................................"
  ],
  nosePerch0: [
    "................................",
    "...............OO.....OO........",
    "..............OHGO...OHGO.......",
    "..............OGWGO.OGPGO.......",
    "..............OGPWOOOHGGO.......",
    "..............OHHHHHHHHGGO......",
    ".............OHGGGGWGGGWGO......",
    ".............OGGGGLEEGGLEGO.....",
    ".............OCGGGPEEEGGEEOO....",
    ".............OCGGGGWWWWWWEEO....",
    ".............OCGWWWWWWWWWWOO....",
    "..............OCWWWWWWWWWWO.....",
    "..............OOBBNNNNYYBBO.....",
    "............OOOHHHBNYYNNBBBO....",
    "...........OHGGGGGGGBNNWWWWWO...",
    "....OOO...OHGGGGGGGGWWWWWWWWWO..",
    "...OWWHO.OHGGGGGGGGGWWWWWWWWWO..",
    "..OWWWGHOOGGGGGGGGGWWWWWWWWWWSO.",
    "..OWGHGGROCCCCCCCCGWWWWWWWWWWSSO",
    "...ORGGGGCCCCCCCCCCSWWWWWWWWWSSO",
    "....ORRRRRCCCCCCCCCSSSWWWWWWSSOO",
    ".....OORRRRRRDDDDDDSSSOOWWWOSSO.",
    ".......OORRRRRRDDDDSSOOOWWWOO...",
    "........OWWWOOOOOOOOO..OOOOO....",
    "........OOOOO...................",
    "................................",
    "................................",
    "................................"
  ],
  nosePerch1: [
    "................................",
    "..............OO......OO........",
    ".............OHGO....OHGO.......",
    ".............OGWGO..OGPGO.......",
    "..............OGPWOOOHGGO.......",
    "..............OHHHHHHHHGGO......",
    ".............OHGGGGWGGGWGO......",
    ".............OGGGGLEEGGLEGO.....",
    ".............OCGGGPEEEGGEEOO....",
    ".............OCGGGGWWWWWWEEO....",
    ".............OCGWWWWWWWWWWOO....",
    "..............OCWWWWWWWWWWO.....",
    "..............OOBBNNNNYYBBO.....",
    "............OOOHHHBNYYNNBBBO....",
    "...OOO.....OHGGGGGGGBNNWWWWWO...",
    "..OWWHO...OHGGGGGGGGWWWWWWWWWO..",
    ".OWWWGHO.OHGGGGGGGGGWWWWWWWWWO..",
    "..OWGHGROOGGGGGGGGGWWWWWWWWWWSO.",
    "...ORGGGGOCCCCCCCCGWWWWWWWWWWSSO",
    "....ORGGGCCCCCCCCCCSWWWWWWWWWSSO",
    ".....ORRRRCCCCCCCCCSSSWWWWWWSSOO",
    ".....OORRRRRRDDDDDDSSSOOWWWOSSO.",
    ".......OORRRRRRDDDDSSOOOWWWOO...",
    "........OWWWOOOOOOOOO..OOOOO....",
    "........OOOOO...................",
    "................................",
    "................................",
    "................................"
  ],
  bellyRoll0: [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "........OOOO......OOOO..........",
    ".......OWWWO.....OWWWO..........",
    ".......OSSOO.OOOO.OSSOO..OOOO...",
    "........ODDOOWWWWOODDO..OWWWPO..",
    "...OOO..OSSSSSSSSSSSSO.OWWWWWEEO",
    "..OWWHOOWWWWWWWWWWWWWOBNWWWWWWOO",
    "..OWWWGOWWWWWWWWWWWWWBNYGGGGGOO.",
    "...ORGGOWWWWWWWWWWWWBBNGGOOGGO..",
    "....ORGCCCCCCCCCCCCCGGGGGGGGGO..",
    ".....ORRRRRCCCCCCCCCCGGGGHGGO...",
    "......OORRRRRRRRDDDDDDHHHHGGO...",
    "........OOOOOOOORRRRRROOHGGO....",
    "................OOOOOOOOOOO.....",
    "................................",
    "................................",
    "................................",
    "................................"
  ],
  bellyRoll1: [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    ".........OOOO....OOOO...........",
    "........OWWWO...OWWWO...........",
    ".......OOSSOO..OOSSOO....OOOO...",
    "....OOO.ODDOOOOODDOOO...OWWWPO..",
    "...OWWHOOSSSSSSSSSSSSO.OWWWWWEEO",
    "..OWWWGOWWWWWWWWWWWWWOBNWWWWWWOO",
    "...ORGGOWWWWWWWWWWWWWBNYGGGGGOO.",
    "....ORGOWWWWWWWWWWWWBBNGGOOGGO..",
    ".....ORCCCCCCCCCCCCCGGGGGGGGGO..",
    "......ORRRRRRCCCCCCCCGGGGHGGO...",
    ".......OORRRRRRRRDDDDDHHHHGGO...",
    ".........OOOOOOOORRRRROOHGGO....",
    ".................OOOOOOOOOO.....",
    "................................",
    "................................",
    "................................"
  ],
  bellyRoll2: [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "...........OOOO......OOOO.......",
    "..........OWWWO.....OWWWO.......",
    "......OOOO.OSSOO...OOSSO.OOOO...",
    ".....OWWWOODDOOOOOOODDO.OWWWPO..",
    "..OOO.OSSSSSSSSSSSSSSOOOWWWWWEEO",
    ".OWWHOOWWWWWWWWWWWWWWOBNWWWWWWOO",
    ".OWGHROWWWWWWWWWWWWWWBNYGGGGGOO.",
    "..ORGGOWWWWWWWWWWWWWBBNGGOOGGO..",
    "...ORGGCCCCCCCCCCCCCGGGGGGGGGO..",
    "....ORRRRRRCCCCCCCCCCGGGGHGGO...",
    ".....OORRRRRRRRRDDDDDDHHHHGGO...",
    ".......OOOOOOOOORRRRRROOHGGO....",
    "................OOOOOOOOOOO.....",
    "................................",
    "................................",
    "................................",
    "................................"
  ],
  scratchEar0: [
    "................................",
    "..............OO................",
    ".............OHGO.......OO......",
    ".............OGWGO.....OHGO.....",
    ".............OGPWOO...OGPGO.....",
    "..............OHHHHOOOOHGGO.....",
    ".............OHHHHHHHHHGGO......",
    ".............OHGGGWGGGGWGO......",
    ".............OGGGLEEGGOOGO......",
    "..........OOOOGGGPEEEGGEEOO.....",
    ".........OWWWOCGGGWWWWWWEEO.....",
    ".........OSSWOCGWWWWWWWWWWOO....",
    "..........OODDOCWWWWWWWWWWO.....",
    "...........OOOBBNNNNYYBBBBO.....",
    "...OOO.....OHHHHBNYYNNWWWWWO....",
    "..OWWHO...OHGGGGGGGBNNWWWWWWO...",
    "..OWWWGHOOHGGGGGGGGWWWWWWWWWWO..",
    "..OWGHGGROGGGGGGGGGWWWWWWWWWWSO.",
    "...ORGGGGCCCCCCCCCGWWWWWWWWWWSSO",
    "....ORRRRRCCCCCCCCCSWWWWWWWWWSSO",
    ".....OORRRRRDDDDDDDSSSWWWWWSSOO.",
    ".......OORRRRRDDDDSSSOOWWWOSSO..",
    ".........OOOOOOOOOO..OOWWWOO....",
    "......................OOOOO.....",
    "................................",
    "................................",
    "................................",
    "................................"
  ],
  scratchEar1: [
    "................................",
    "..............OO................",
    ".............OHGO.......OO......",
    ".............OGWGO.....OHGO.....",
    ".............OGPWOO...OGPGO.....",
    "..............OHHHHOOOOHGGO.....",
    ".............OHHHHHHHHHGGO......",
    ".............OHGGGWGGGGWGO......",
    ".............OGGGLEEGGOOGO......",
    ".............OGGGPEEEGGEEOO.....",
    ".............OCGGGWWWWWWEEO.....",
    ".........OOOOOCGWWWWWWWWWWOO....",
    "........OWWWWOOCWWWWWWWWWWO.....",
    "........OSSO.OOBBNNNNYYBBBO.....",
    "...OOO...ODDOHHHBNYYNNWWWWWO....",
    "..OWWHO..OOHGGGGGGGBNNWWWWWWO...",
    "..OWWWGHOOHGGGGGGGGWWWWWWWWWWO..",
    "..OWGHGGROGGGGGGGGGWWWWWWWWWWSO.",
    "...ORGGGGCCCCCCCCCGWWWWWWWWWWSSO",
    "....ORRRRRCCCCCCCCCSWWWWWWWWWSSO",
    ".....OORRRRRDDDDDDDSSSWWWWWSSOO.",
    ".......OORRRRRDDDDSSSOOWWWOSSO..",
    ".........OOOOOOOOOO..OOWWWOO....",
    "......................OOOOO.....",
    "................................",
    "................................",
    "................................",
    "................................"
  ],
  yawnStretch0: [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "...OOO..........................",
    "..OWWHO.........................",
    ".OWWWGHO.........OO.....OO......",
    "..OWGHGRO.......OHGO...OHGO.....",
    "...ORGGGHO......OGWGO.OGPGO.....",
    "....ORHHHHHOOOO.OGPWOOOHGGO.....",
    ".....ORHHHHHHHHHOHHHHHHHHGGO....",
    "......ORGGGGGGGGGOBGGGGWGGGWGO..",
    "......ORCCCCCCCCGBNGGGOOGGGOOGO.",
    ".......ORCCCCCCCCBNYGGPGGGGGGEEO",
    ".......ORRRRRCCCCBNNYGWWWWPMMPOO",
    "........OORRRDDDDBBNWWWWWWPMMWO.",
    "........ORCO.ODDO..OCWWWWWWWWWOO",
    ".......OCCO..ODDO..OOBBNNYYWWOO.",
    ".......OCCO..ODDO...OOOGGGGWWOO.",
    "......OCCO...ODDO....OGGGGGGGWWO",
    "......OWWWO..OSSO....OCCCCWWWWWO",
    "......OWWWO..OSSO.....OOOOWWWWWO",
    "......OOOO...OOOO........OWWWWWO",
    ".........................OOOOOOO",
    "................................",
    "................................",
    "................................"
  ],
  yawnStretch1: [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "...OOO..........................",
    "..OWWHO.........................",
    ".OWWWGHO.........OO.....OO......",
    "..OWGHGRO.......OHGO...OHGO.....",
    "...ORGGGHO......OGWGO.OGPGO.....",
    "....ORHHHHHOOOO.OGPWOOOHGGO.....",
    ".....ORHHHHHHHHHOHHHHHHHHGGO....",
    "......ORGGGGGGGGGOBGGGGWGGGWGO..",
    "......ORCCCCCCCCGBNGGGLEEGGLEGO.",
    ".......ORCCCCCCCCBNYGGPEEEGGEEOO",
    ".......ORRRRRCCCCBNNYGWWWWWPPEO.",
    "........OORRRDDDDBBNWWWWWWWWWWOO",
    "........ORCO.ODDO..OCWWWWWWWWWO.",
    ".......OCCO..ODDO..OOBBNNYYWWWO.",
    ".......OCCO..ODDO...OOOGGGGWWOO.",
    "......OCCO...ODDO....OGGGGGGGWWO",
    "......OWWWO..OSSO....OCCCCWWWWWO",
    "......OWWWO..OSSO.....OOOOWWWWWO",
    "......OOOO...OOOO........OWWWWWO",
    ".........................OOOOOOO",
    "................................",
    "................................",
    "................................"
  ],
  bow: [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "...OOO..........................",
    "..OWWHO.........................",
    ".OWWWGHO.........OO.....OO......",
    "..OWGHGRO.......OHGO...OHGO.....",
    "...ORGGGHO......OGWGO.OGPGO.....",
    "....ORHHHHHOOOO.OGPWOOOHGGO.....",
    ".....ORHHHHHHHHHOHHHHHHHHGGO....",
    "......ORGGGGGGGGGOBGGGGWGGGWGO..",
    "......ORCCCCCCCCGBNGGGEEGGGEEGO.",
    ".......ORCCCCCCCCBNYGGPGGGGGGGOO",
    ".......ORRRRRCCCCBNNYGWWWWWWEEO.",
    "........OORRRDDDDBBNWWWWWWWWWWOO",
    "........ORCO.ODDO..OCWWWWWWWWWO.",
    ".......OCCO..ODDO..OOBBNNYYWWWO.",
    ".......OCCO..ODDO...OOOGGGGWWOO.",
    "......OWWWO..OSSO....OGGGGGGGWWO",
    "......OOOO...OOOO....OCCCCWWWWWO",
    "......................OOOOWWWWWO",
    ".........................OWWWWWO",
    ".........................OOOOOOO",
    "................................",
    "................................",
    "................................"
  ],
  hop: [
    "................OO.....OO.......",
    "...............OHGO...OHGO......",
    "...............OGWGO.OGPGO......",
    "...............OGPWOOOHGGO......",
    "...............OHHHHHHHHGGO.....",
    "..............OHGGGGWGGGWGO.....",
    "..............OGGGGLEEGGLEGO....",
    "...OOO........OGGGPEEEGGEEOO....",
    "..OWWHO.......OCGGGWWWWWWEEO....",
    ".OWWWGHO......OCGWWWWWWWWWWOO...",
    "..OWGHGRO......OCWWWWWWWWWWO....",
    "...ORGGGHOOOOOOOBBNNNNYYBBO.....",
    "....ORHHHHHHHHHHHBNYYNNBBBO.....",
    ".....ORGGGGGGGGGGGGBNNWWWWWO....",
    "......ORGGGGGGGGGGGGWWWWWWWWWO..",
    "......ORCCCCCCCCGGGGWWWWWWWWWO..",
    ".......ORRRRRCCCCCCSWWWWWWWSSO..",
    "........OORRRDDDDDDSSSSSSSSOO...",
    "......ORCCO.ODDO....OGGCO.OSSO..",
    ".....OWWWO..OSSO.....OWWWOOWWO..",
    ".....OOOO...OOOO......OOOOOOOO..",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................"
  ],
  nap0: [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    ".................OO....OO.......",
    "................OHGO..OHGO......",
    "........OOOOOOOOOGWGOOGPGO......",
    "......OOHHHHHHHHOOHHHHHGGO......",
    ".....OHGGGGGGGGGGOBGGGGGGGO.....",
    "....OHGGGGGGGGGGGBNGGGEEGGEEO...",
    "...OHGGGGCCCCCCCCBNYGGPWWWWEEO..",
    "...OGGGGCCCCCCCCCCBNNWWWWWWWWWO.",
    "...ORRRRCCCCCCCCCCWWWWWWWWWWWWO.",
    "...OORRRRRRDDDDDOOWWWWOOWWWWWWO.",
    "....OOOWWWWWWOOOOOWWWOOOOOWWWOO.",
    "......OOOOOOOO...OOOOO...OOOOO..",
    "................................",
    "................................",
    "................................",
    "................................"
  ],
  nap1: [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    ".................OO....OO.......",
    "................OHGO..OHGO......",
    "........OOOOOOOOOGWGOOGPGO......",
    "......OOHHHHHHHHOOHHHHHGGO......",
    ".....OHGGGGGGGGGGOBGGGGGGGO.....",
    "....OHGGGGGGGGGGGBNGGGEEGGEEO...",
    "...OHGGGGCCCCCCCCBNYGGPWWWWEEO..",
    "...OGGGGCCCCCCCCCCBNNWWWWWWWWWO.",
    "...OGGGGCCCCCCCCCCWWWWWWWWWWWWO.",
    "...ORRRRCCCCCCCCCCWWWWWWWWWWWWO.",
    "...OORRRRRRDDDDDOOWWWWOOWWWWWWO.",
    "....OOOWWWWWWOOOOOWWWOOOOOWWWOO.",
    "......OOOOOOOO...OOOOO...OOOOO..",
    "................................",
    "................................",
    "................................",
    "................................"
  ]
};

const BUTTERFLY_SPECIES = {
  morpho: {
    open: [
      "....J...J....",
      ".JJJJJ.JJJJJ.",
      "JLTUUJ.JUUTLJ",
      "JTTUNJJJNUTTJ",
      ".JBNTJEJTNBJ.",
      "..JJJJEJJJJ..",
      "..JBTNENTBJ..",
      "..JBTUJUTBJ..",
      "...JJL.LJJ...",
      "....JJ.JJ....",
      "............."
    ],
    mid: [
      ".....J.J.....",
      "..JJJJ.JJJJ..",
      "..JLUT.TULJ..",
      "..JTTNJNTTJ..",
      "...JBNENBJ...",
      "...JJJEJJJ...",
      "...JBTETBJ...",
      "....JBLBJ....",
      "....JJ.JJ....",
      ".............",
      "............."
    ],
    folded: [
      ".......J.J...",
      "....JJJJJ....",
      "...JLUUTJ....",
      "...JTTNBJ....",
      "....JBNJJE...",
      "....JJBTJE...",
      ".....JBTJE...",
      ".....JBLJ....",
      "......JJ.....",
      ".............",
      "............."
    ]
  },
  monarch: {
    open: [
      "....O...O....",
      ".OOOOO.OOOOO.",
      "OLYYFO.OFYYLO",
      "OFAAYOOOYAAFO",
      ".OAAFOEOFAAO.",
      "..OOOOEOOOO..",
      "..OAFYEYFAO..",
      "..OAAFOFAAO..",
      "...OOL.LOO...",
      "....OO.OO....",
      "............."
    ],
    mid: [
      ".....O.O.....",
      "..OOOO.OOOO..",
      "..OLYF.FYLO..",
      "..OFAOOOAFO..",
      "...OAFEFAO...",
      "...OOOEOOO...",
      "...OAFEFAO...",
      "....OALAO....",
      "....OO.OO....",
      ".............",
      "............."
    ],
    folded: [
      ".......O.O...",
      "....OOOOO....",
      "...OLYYFO....",
      "...OFAAOO....",
      "....OAFOOE...",
      "....OOFAOE...",
      ".....OAFOE...",
      ".....OALO....",
      "......OO.....",
      ".............",
      "............."
    ]
  },
  swallowtail: {
    open: [
      "....E...E....",
      ".EEEEE.EEEEE.",
      "ELWIIE.EIIWLE",
      "EIHEIEEEIEHIE",
      ".EIIHEEEHIIE.",
      "..EEEEEEEEE..",
      "..EIHTETHIE..",
      "..EIMWEWMIE..",
      "...EEL.LEE...",
      "...E.E.E.E...",
      "...E.....E..."
    ],
    mid: [
      ".....E.E.....",
      "..EEEE.EEEE..",
      "..ELWI.IWLE..",
      "..EIHEEEHIE..",
      "...EIIEIIE...",
      "...EEEEEEE...",
      "...EITETIE...",
      "....EMLME....",
      "....EE.EE....",
      "....E...E....",
      "............."
    ],
    folded: [
      ".......E.E...",
      "....EEEEE....",
      "...ELWIIE....",
      "...EIHEIE....",
      "....EIIEEE...",
      "....EEITEE...",
      ".....EIMEE...",
      ".....EELE....",
      "....EE.......",
      "...E.........",
      "............."
    ]
  }
};

const FLOWER_BLOOMS = {
  gold: [
    ".IYY.",
    "IYAYY",
    "YAAFY",
    ".YFY.",
    "..Z.."
  ],
  ivory: [
    ".LWW.",
    "LWWWL",
    "WWFWW",
    ".WSW.",
    "..Z.."
  ],
  starlight: [
    ".LUU.",
    "LUTUL",
    "UTYTU",
    ".TTT.",
    "..Z.."
  ]
};

const TWIG_GRID = [
  "......YL.",
  "..XZ..YIY",
  "OOFFHFFY.",
  ".OOOZX...",
  "........."
];

const EMOTES = {
  heart: [
    "...........",
    "..OO...OO..",
    ".OLLM.OMMO.",
    "OLMMQOOMMMO",
    "OMMMMMMMMMO",
    "OMMMMMMMKKO",
    ".OMMMMMKKO.",
    "..OMMMKKO..",
    "...OMMKO...",
    "....OKO....",
    ".....O....."
  ],
  zzz: [
    "......OOOOO",
    "......OYYLO",
    ".......OYYO",
    "..OOOO.OOYO",
    "..OTULO.OOO",
    "...OTUO....",
    "...OOTO....",
    "OOOO.OO....",
    "OYYO.......",
    "OYOO.......",
    "OOOO......."
  ],
  note: [
    "....OOOOOO.",
    "....OYYYYO.",
    "....OYOOOO.",
    "....OYO..OO",
    "....OYO..OY",
    "..OOOYO.OOY",
    ".OYYLYOOYYO",
    ".OYYYYO.OOO",
    "..OOOO.....",
    "...........",
    "..........."
  ],
  sparkle: [
    ".....O.....",
    "....OYO....",
    "....OYO..O.",
    "...OYYYO.Y.",
    ".OOYYLYYOO.",
    "OYYYYLYYYYO",
    ".OOYYLYYOO.",
    "...OYYYO...",
    "....OYO....",
    ".Y..OYO....",
    ".....O....."
  ],
  curious: [
    "...OOOOO...",
    "..OYYYYYO..",
    "..OYYOOYYO.",
    "..OOO.OYYO.",
    ".....OYYO..",
    "....OYYO...",
    "....OOOO...",
    "...........",
    "....OOOO...",
    "....OYYO...",
    "....OOOO..."
  ],
  alert: [
    "....OOOO...",
    "....OYYO...",
    "....OYLO...",
    "....OYYO...",
    "....OYYO...",
    "....OYYO...",
    "....OOOO...",
    "...........",
    "....OOOO...",
    "....OYYO...",
    "....OOOO..."
  ]
};

const SPARK_COLORS = ["#fde047", "#fef08a", "#fbbf24", "#7dd3fc", "#93c5fd", "#fff8e3"];
const POLLEN_COLORS = ["#fde047", "#fef08a", "#fff8e3", "#fbbf24"];
const BLADE_SHADES = [
  ["#064e3b", "#15803d", "#34d399"],
  ["#064e3b", "#166534", "#6ee7b7"],
  ["#0f5132", "#15803d", "#a7f3d0"]
];

function bakeSpriteGrid(rows, width, height, flipX = false) {
  const c = document.createElement("canvas");
  c.width = width;
  c.height = height;
  const ctx = c.getContext("2d");
  for (let y = 0; y < height; y++) {
    const row = rows[y] || "";
    for (let x = 0; x < width; x++) {
      const ch = row[x];
      if (!ch || ch === ".") continue;
      const hex = PALETTE[ch];
      if (!hex) continue;
      ctx.fillStyle = hex;
      const dx = flipX ? (width - 1 - x) : x;
      ctx.fillRect(dx, y, 1, 1);
    }
  }
  return c;
}

function bakeSpriteMap(flipX) {
  const map = {};
  const keys = Object.keys(FRAMES);
  for (let k = 0; k < keys.length; k++) {
    const name = keys[k];
    map[name] = bakeSpriteGrid(FRAMES[name], SPRITE_W, SPRITE_H, flipX);
  }
  return map;
}

function bakeButterflyBank() {
  const bank = {};
  const speciesList = Object.keys(BUTTERFLY_SPECIES);
  for (let i = 0; i < speciesList.length; i++) {
    const sp = speciesList[i];
    const spec = BUTTERFLY_SPECIES[sp];
    bank[sp] = {
      right: {
        open: bakeSpriteGrid(spec.open, BF_W, BF_H, false),
        mid: bakeSpriteGrid(spec.mid, BF_W, BF_H, false),
        folded: bakeSpriteGrid(spec.folded, BF_W, BF_H, false)
      },
      left: {
        open: bakeSpriteGrid(spec.open, BF_W, BF_H, true),
        mid: bakeSpriteGrid(spec.mid, BF_W, BF_H, true),
        folded: bakeSpriteGrid(spec.folded, BF_W, BF_H, true)
      }
    };
  }
  return bank;
}

function bakeFlowerBank() {
  const bank = {};
  const keys = Object.keys(FLOWER_BLOOMS);
  for (let i = 0; i < keys.length; i++) {
    const k = keys[i];
    bank[k] = bakeSpriteGrid(FLOWER_BLOOMS[k], 5, 5, false);
  }
  return bank;
}

function bakeEmoteMap() {
  const map = {};
  const keys = Object.keys(EMOTES);
  for (let k = 0; k < keys.length; k++) {
    const name = keys[k];
    map[name] = bakeSpriteGrid(EMOTES[name], EMOTE_SIZE, EMOTE_SIZE, false);
  }
  return map;
}

function seededRand(seed) {
  let s = (seed >>> 0) || 1;
  return () => {
    s = (1664525 * s + 1013904223) >>> 0;
    return (s & 0xffff) / 65535;
  };
}

export class StarlightPixelDog {
  constructor(layerEl, canvasEl, hitboxEl, onJoyPulse, getEnv = null) {
    this.layer = layerEl;
    this.canvas = canvasEl;
    this.ctx = canvasEl.getContext("2d");
    this.hitbox = hitboxEl;
    this.onJoyPulse = onJoyPulse || null;
    this.getEnv = typeof getEnv === "function" ? getEnv : null;

    this.spritesRight = bakeSpriteMap(false);
    this.spritesLeft = bakeSpriteMap(true);
    this.companionSprites = bakeCompanionSprites();
    this.propSprites = bakePropSprites();
    this.propDefsById = new Map(PROP_CATALOG.map((p) => [p.id, p]));
    this.butterflySprites = bakeButterflyBank();
    this.flowerSprites = bakeFlowerBank();
    this.twigSpriteRight = bakeSpriteGrid(TWIG_GRID, TWIG_W, TWIG_H, false);
    this.twigSpriteLeft = bakeSpriteGrid(TWIG_GRID, TWIG_W, TWIG_H, true);
    this.emoteSprites = bakeEmoteMap();

    this.mqReduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    this.reducedMotion = this.mqReduced.matches;

    this.docW = 1440;
    this.docH = 1600;
    this.dpr = 1;
    this.localCycleTime = this.reducedMotion ? 4.0 : 0.0;

    this.x = 320;
    this.y = 280;
    this.facing = 1;
    this.hopY = 0;
    this.shakeX = 0;

    this.state = this.reducedMotion ? "sit" : "trot";
    this.gait = "trot";
    this.stateTimer = 0;
    this.stateDuration = 2.4;
    this.animTime = 0;
    this.stepAccum = 0;
    this.blinkTimer = 1.9;
    this.earPerkTimer = 0;
    this.hoverPauseTimer = 0;
    this.cursorNear = false;
    this._lastHx = -999;
    this._lastHy = -999;
    this._lastSyncState = "";
    this._datasetAccum = 0;

    this.petCount = 0;
    this.lastPetReaction = "none";
    this.fetchCount = 0;
    this.visitedStates = new Set();
    this.visitedAnims25 = new Set();

    this.emote = null;
    this.autoEmoteCooldown = 6.0;
    this.petEmoteGuard = 0;

    this.waypoints = [];
    this.exclusionZones = [];
    this.portraitCircle = null;
    this.props = [];
    this.floraClusters = [];
    this.sunflowerPerches = [];
    this.butterflies = [];
    this.fireflies = [];
    this.companions = [];

    this.currentWpIdx = -1;
    this.startPt = { x: 320, y: 280 };
    this.ctrlPt = { x: 420, y: 260 };
    this.targetPt = { x: 520, y: 280, tag: "sky" };
    this.travelT = 0;
    this.travelDur = 2.0;
    this.travelArc = 0;
    this.tilt = 0;
    this.squashX = 1;
    this.squashY = 1;

    this.activeFlora = null;
    this.activeProp = null;
    this.sniffWillSneeze = false;
    this.sneezeTriggered = false;
    this.activeButterfly = null;
    this.pounceStartX = 0;
    this.pounceTargetX = 0;

    this.twig = null;
    this.fetchPhase = "none";
    this.fetchTimer = 0;
    this.fetchStartPt = { x: 0, y: 0 };
    this.fetchGoalPt = { x: 0, y: 0 };
    this.fetchReturnPt = { x: 0, y: 0 };
    this.fetchMoveDur = 1.0;

    this.openingQueue = [
      "sniffFlora",
      "stalkButterfly",
      "boopFirefly",
      "binky",
      "drink",
      "bellyRoll",
      "scratchEar",
      "yawnStretch"
    ];
    this.behaviorBag = [];

    this.pawPuffs = [];
    this.sparks = [];
    this.napStars = [];
    this.pollenMotes = [];
    this.dandelionSeeds = [];
    this.waterRipples = [];
    this.dewDrops = [];
    this._looping = false;

    this._resize();
    this._collectWaypointsAndFlora();
    this._initButterflies();
    this._initFireflies();
    this._initCompanions();
    this._placeInitial();
    this._bindEvents();
    this.render();

    if (!this.reducedMotion) {
      this._startLoop();
    }
  }

  _currentEnv() {
    if (this.getEnv) {
      return this.getEnv();
    }
    const base = evaluateDayNightCycle(this.localCycleTime);
    return { ...base, meteorsLaunched: 0, activeMeteors: 0 };
  }

  _mapDogStateToAnim25(st) {
    if (ANIMATION_25.includes(st)) return st;
    const table = {
      run: "gallop",
      fetchTwig: "gallop",
      sniffFlora: "sniff",
      stalkButterfly: "crouchStalk",
      pounceButterfly: "pounce",
      butterflyNosePerch: "earPerk",
      yawnStretch: "yawn",
      sit: "tailWag",
      rest: "sunBask",
      nap: "sleepCurl",
      petBowHop: "binky",
      petBellyRoll: "bellyRoll",
      petTailSpin: "happySpin"
    };
    return table[st] || "tailWag";
  }

  _recordState(st) {
    if (st) {
      this.visitedStates.add(st);
      this.visitedAnims25.add(this._mapDogStateToAnim25(st));
    }
  }

  _recordAnim25(anim) {
    if (anim && ANIMATION_25.includes(anim)) {
      this.visitedAnims25.add(anim);
    }
  }

  notifyMeteor(meteorInfo) {
    if (this.reducedMotion) return;
    const dir = meteorInfo && meteorInfo.dirX ? meteorInfo.dirX : 1;
    let count = 0;
    for (let i = 0; i < this.companions.length; i++) {
      const c = this.companions[i];
      if (c.anim === "sleepCurl") continue;
      if ((i + (meteorInfo ? meteorInfo.slot : 0)) % 2 === 0 && count < 4) {
        c.anim = "stargazeMeteor";
        this._recordAnim25("stargazeMeteor");
        c.timer = 0;
        c.duration = 1.45 + (i % 3) * 0.22;
        c.hopY = 0;
        c.facing = dir;
        count += 1;
      }
    }
    const calmDog = this.state === "sit" || this.state === "rest" || this.state === "tailWag" || this.state === "earPerk";
    if (calmDog) {
      this.facing = dir;
      this._enterState("stargazeMeteor", 1.55);
      this._maybeShowEmote("sparkle", false);
    }
  }

  _resize() {
    this.dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    const w = Math.max(320, this.layer.clientWidth || document.documentElement.clientWidth || 1440);
    const h = Math.max(480, this.layer.clientHeight || document.body.offsetHeight || 1400);
    this.docW = w;
    this.docH = h;
    this.canvas.width = Math.max(1, Math.round(w * this.dpr));
    this.canvas.height = Math.max(1, Math.round(h * this.dpr));
    this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    this.ctx.imageSmoothingEnabled = false;
  }

  _buildExclusionZones(ox, oy) {
    const zones = [];
    this.portraitCircle = null;
    const portEl = document.getElementById("portrait-canvas");
    if (portEl) {
      const pr = portEl.getBoundingClientRect();
      if (pr.width > 0 && pr.height > 0) {
        const cx = pr.left - ox + pr.width * 0.5;
        const cy = pr.top - oy + pr.height * 0.5;
        const rad = Math.max(pr.width, pr.height) * 0.5;
        this.portraitCircle = { cx, cy, r: rad };
        zones.push({ kind: "circle", cx, cy, r: rad + 26 });
      }
    }
    const textEls = document.querySelectorAll(
      ".portrait-identity, .board-head, .radar-top, .metrics-stack, .console-bar, .forum-content"
    );
    textEls.forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.width > 0 && r.height > 0) {
        zones.push({
          kind: "rect",
          x0: r.left - ox - 12,
          y0: r.top - oy - 10,
          x1: r.right - ox + 12,
          y1: r.bottom - oy + 48
        });
      }
    });
    this.exclusionZones = zones;
  }

  _pushOutOfExclusions(x, y, pad = 12) {
    let px = x;
    let py = y;
    for (let i = 0; i < this.exclusionZones.length; i++) {
      const z = this.exclusionZones[i];
      if (z.kind === "circle") {
        const dx = px - z.cx;
        const dy = py - z.cy;
        const dist = Math.hypot(dx, dy);
        const minR = z.r + pad;
        if (dist < minR) {
          const ang = dist > 0.5 ? Math.atan2(dy, dx) : 0.65;
          px = z.cx + Math.cos(ang) * minR;
          py = z.cy + Math.sin(ang) * minR;
        }
      } else if (px >= z.x0 - pad * 0.5 && px <= z.x1 + pad * 0.5 && py >= z.y0 - pad * 0.5 && py <= z.y1 + pad * 0.5) {
        const dTop = Math.abs(py - z.y0);
        const dBot = Math.abs(z.y1 - py);
        const dLeft = Math.abs(px - z.x0);
        const dRight = Math.abs(z.x1 - px);
        const m = Math.min(dTop, dBot, dLeft, dRight);
        if (m === dBot) py = z.y1 + pad * 0.6;
        else if (m === dTop) py = z.y0 - pad * 0.6;
        else if (m === dLeft) px = z.x0 - pad * 0.6;
        else px = z.x1 + pad * 0.6;
      }
    }

    px = Math.max(32, Math.min(this.docW - 32, px));

    for (let pass = 0; pass < 2; pass++) {
      for (let i = 0; i < this.exclusionZones.length; i++) {
        const z = this.exclusionZones[i];
        if (z.kind === "rect" && px >= z.x0 && px <= z.x1 && py >= z.y0 && py <= z.y1) {
          py = py < (z.y0 + z.y1) * 0.5 ? z.y0 - 10 : z.y1 + 10;
        }
      }
      if (this.portraitCircle) {
        const pc = this.portraitCircle;
        const minR = pc.r + 44;
        if (Math.hypot(px - pc.cx, py - pc.cy) < minR) {
          py = py < pc.cy ? pc.cy - minR : pc.cy + minR + 56;
        }
      }
    }

    return {
      x: px,
      y: Math.max(46, Math.min(this.docH - 18, py))
    };
  }

  _makeCurvedControlPt(sx, sy, tx, ty, seed = 0) {
    const mx = (sx + tx) * 0.5;
    const my = (sy + ty) * 0.5;
    const dx = tx - sx;
    const dy = ty - sy;
    const dist = Math.hypot(dx, dy) || 1;
    const nx = -dy / dist;
    const ny = dx / dist;
    const sign = seed % 2 === 0 ? 1 : -1;
    const bend = Math.min(68, dist * 0.20) * sign;
    let cx = mx + nx * bend;
    let cy = my + ny * bend;

    if (this.portraitCircle) {
      const pc = this.portraitCircle;
      const pdx = cx - pc.cx;
      const pdy = cy - pc.cy;
      const pDist = Math.hypot(pdx, pdy);
      const safeR = pc.r + 36;
      if (pDist < safeR) {
        const ang = pDist > 1 ? Math.atan2(pdy, pdx) : (my >= pc.cy ? 1.45 : -1.45);
        cx = pc.cx + Math.cos(ang) * safeR;
        cy = pc.cy + Math.sin(ang) * safeR;
      }
    }

    return {
      x: Math.max(26, Math.min(this.docW - 26, cx)),
      y: Math.max(38, Math.min(this.docH - 16, cy))
    };
  }

  // WHY: Scatters 2D free-roam waypoints and >=40 open-pocket props across sky, Dec-Aug matrix, Stack/Console pockets, 3D cards, and Provence garden.
  _collectWaypointsAndFlora() {
    const layerRect = this.layer.getBoundingClientRect();
    const ox = layerRect.left;
    const oy = layerRect.top;
    this._buildExclusionZones(ox, oy);

    const pts = [];
    const rawFlora = [];
    const perches = [];

    const clampX = (val, minPad = 34) => Math.max(minPad, Math.min(this.docW - minPad, val));
    const clampY = (val) => Math.max(46, Math.min(this.docH - 18, val));
    const pushWp = (x, y, tag, zone) => {
      const safe = this._pushOutOfExclusions(clampX(x), clampY(y), 16);
      pts.push({ x: safe.x, y: safe.y, tag, zone });
    };

    const skyDome = document.querySelector(".sky-dome");
    if (skyDome) {
      const r = skyDome.getBoundingClientRect();
      const left = r.left - ox;
      const top = r.top - oy;
      const skySpots = [
        [0.12, 0.34, "sky"], [0.34, 0.28, "sky"], [0.64, 0.32, "sky"], [0.86, 0.38, "sky"],
        [0.14, 0.88, "sunflower"], [0.38, 0.78, "sky"], [0.66, 0.82, "sky"], [0.88, 0.90, "sunflower"]
      ];
      for (let i = 0; i < skySpots.length; i++) {
        const [fx, fy, tg] = skySpots[i];
        pushWp(left + r.width * fx, top + r.height * fy, tg, "sky");
      }

      const skyFloraFracs = [0.08, 0.22, 0.38, 0.56, 0.74, 0.90];
      for (let i = 0; i < skyFloraFracs.length; i++) {
        rawFlora.push({
          x: clampX(left + r.width * skyFloraFracs[i], 28),
          y: clampY(top + r.height - 3),
          zone: "sky",
          lush: i === 0 || i === 5 ? 2 : 1
        });
      }

      for (let i = 0; i < PAN_SUNFLOWERS.length; i++) {
        const [fx, fy] = PAN_SUNFLOWERS[i];
        perches.push({
          x: clampX(left + r.width * fx, 24),
          y: clampY(top + r.height * fy - 6),
          kind: "sunflower",
          zone: "sky"
        });
      }
    }

    const matrixCanvas = document.getElementById("matrix-canvas");
    if (matrixCanvas) {
      const mr = matrixCanvas.getBoundingClientRect();
      const mLeft = mr.left - ox;
      const mTop = mr.top - oy;
      const matOpen = [
        [0.10, 0.38], [0.22, 0.72], [0.34, 0.44], [0.46, 0.78],
        [0.58, 0.42], [0.68, 0.76], [0.80, 0.86], [0.92, 0.88]
      ];
      for (let i = 0; i < matOpen.length; i++) {
        pushWp(mLeft + mr.width * matOpen[i][0], mTop + mr.height * matOpen[i][1], "matrix", "board");
      }
      const matFloraFracs = [0.16, 0.40, 0.64, 0.88];
      for (let i = 0; i < matFloraFracs.length; i++) {
        rawFlora.push({
          x: clampX(mLeft + mr.width * matFloraFracs[i], 28),
          y: clampY(mTop + mr.height - 2),
          zone: "board",
          lush: 1
        });
      }
    }

    const radarCanvas = document.getElementById("radar-canvas");
    if (radarCanvas) {
      const rr = radarCanvas.getBoundingClientRect();
      const rLeft = rr.left - ox;
      const rTop = rr.top - oy;
      const radarFlanks = [
        [0.10, 0.36], [0.14, 0.82], [0.50, 0.90], [0.86, 0.38], [0.90, 0.84]
      ];
      for (let i = 0; i < radarFlanks.length; i++) {
        pushWp(rLeft + rr.width * radarFlanks[i][0], rTop + rr.height * radarFlanks[i][1], "stack", "board");
      }
    }

    const consoleBox = document.querySelector(".console-box");
    if (consoleBox) {
      const cr = consoleBox.getBoundingClientRect();
      const cLeft = cr.left - ox;
      const cTop = cr.top - oy;
      pushWp(cLeft + cr.width * 0.74, cTop + cr.height * 0.56, "console", "board");
      pushWp(cLeft + cr.width * 0.90, cTop + cr.height * 0.78, "console", "board");
      pushWp(cLeft + cr.width * 0.42, cTop + cr.height * 0.92, "console", "board");
    }

    if (this.portraitCircle) {
      const pc = this.portraitCircle;
      pushWp(pc.cx - pc.r * 0.86, pc.cy + pc.r + 28, "core", "board");
      pushWp(pc.cx + pc.r * 0.86, pc.cy + pc.r + 28, "core", "board");
    }

    const viewports = document.querySelectorAll(".forum-viewport");
    viewports.forEach((vp, idx) => {
      const r = vp.getBoundingClientRect();
      const left = r.left - ox;
      const top = r.top - oy;
      pushWp(left + r.width * 0.22, top + r.height * 0.48, "card", "card");
      pushWp(left + r.width * 0.74, top + r.height * 0.82, "card", "card");
      if (idx < viewports.length - 1 && this.docW >= 900) {
        pushWp(left + r.width + 6, top + r.height * 0.65, "corridor", "card");
      }
    });

    const garden = document.querySelector(".garden-observatory");
    if (garden) {
      const r = garden.getBoundingClientRect();
      const left = r.left - ox;
      const top = r.top - oy;
      const garPts = [
        [0.12, 0.44, "sunflower"], [0.34, 0.38, "garden"], [0.56, 0.48, "garden"], [0.84, 0.42, "sunflower"],
        [0.16, 0.74, "sunflower"], [0.42, 0.68, "garden"], [0.68, 0.72, "garden"], [0.88, 0.78, "sunflower"],
        [0.24, 0.91, "garden"], [0.52, 0.92, "garden"], [0.78, 0.90, "garden"]
      ];
      for (let i = 0; i < garPts.length; i++) {
        pushWp(left + r.width * garPts[i][0], top + r.height * garPts[i][1], garPts[i][2], "garden");
      }

      const garFlora = [
        [0.08, 0.88, 2],
        [0.20, 0.91, 2],
        [0.34, 0.66, 1],
        [0.48, 0.93, 2],
        [0.62, 0.70, 1],
        [0.76, 0.91, 2],
        [0.90, 0.88, 2]
      ];
      for (let i = 0; i < garFlora.length; i++) {
        const [fx, fy, lush] = garFlora[i];
        rawFlora.push({
          x: clampX(left + r.width * fx, 28),
          y: clampY(top + r.height * fy),
          zone: "garden",
          lush
        });
      }

      for (let i = 0; i < GAR_SUNFLOWERS.length; i++) {
        const [fx, fy] = GAR_SUNFLOWERS[i];
        perches.push({
          x: clampX(left + r.width * fx, 24),
          y: clampY(top + r.height * fy - 8),
          kind: "sunflower",
          zone: "garden"
        });
      }
    }

    const shell = document.querySelector("main.observatory-shell");
    if (shell && this.docW >= 1240) {
      const sr = shell.getBoundingClientRect();
      const sLeft = sr.left - ox;
      const sRight = sr.right - ox;
      const marginYFracs = [0.16, 0.38, 0.62, 0.84];
      for (let i = 0; i < marginYFracs.length; i++) {
        const my = this.docH * marginYFracs[i];
        if (sLeft > 52) pushWp(sLeft * 0.5, my, "margin", "sky");
        if (this.docW - sRight > 52) pushWp(sRight + (this.docW - sRight) * 0.5, my, "margin", "garden");
      }
    }

    if (!pts.length) {
      pts.push({ x: 160, y: 260, tag: "sky", zone: "sky" }, { x: 340, y: 520, tag: "garden", zone: "garden" });
      rawFlora.push({ x: 200, y: 262, zone: "sky", lush: 2 }, { x: 310, y: 522, zone: "garden", lush: 2 });
    }

    const minPropDist = this.docW < 520 ? 18 : 26;
    const rawProps = this._buildRawPropPlacements(ox, oy, clampX, clampY);
    const placedProps = [];
    for (let i = 0; i < rawProps.length; i++) {
      const cand = rawProps[i];
      const safe = this._pushOutOfExclusions(cand.x, cand.y, 14);
      let collide = false;
      for (let j = 0; j < placedProps.length; j++) {
        if (Math.hypot(placedProps[j].x - safe.x, placedProps[j].y - safe.y) < minPropDist) {
          collide = true;
          break;
        }
      }
      if (!collide) {
        const def = this.propDefsById.get(cand.id) || PROP_CATALOG[0];
        placedProps.push({
          uid: placedProps.length,
          id: def.id,
          category: def.category,
          width: def.width,
          height: def.height,
          glowColor: def.glowColor || null,
          glowRadius: def.glowRadius || 0,
          x: safe.x,
          y: safe.y,
          zone: cand.zone,
          bend: 0,
          bendVel: 0,
          glowBoost: 0,
          cooldown: 0,
          phase: (placedProps.length * 1.37) % (Math.PI * 2)
        });
      }
    }
    this.props = placedProps;

    const minSpacing = this.docW < 520 ? 44 : 54;
    const filteredFlora = [];
    for (let i = 0; i < rawFlora.length; i++) {
      const cand = rawFlora[i];
      const safeF = this._pushOutOfExclusions(cand.x, cand.y, 12);
      cand.x = safeF.x;
      cand.y = safeF.y;
      let tooClose = false;
      for (let j = 0; j < filteredFlora.length; j++) {
        const ex = filteredFlora[j];
        if (Math.abs(ex.y - cand.y) < 36 && Math.abs(ex.x - cand.x) < minSpacing) {
          tooClose = true;
          break;
        }
      }
      if (!tooClose) {
        for (let p = 0; p < this.props.length; p++) {
          if (Math.hypot(this.props[p].x - cand.x, this.props[p].y - cand.y) < 22) {
            tooClose = true;
            break;
          }
        }
      }
      if (!tooClose) filteredFlora.push(cand);
    }

    this.floraClusters = filteredFlora.map((spot, idx) => this._createFloraCluster(spot, idx));
    for (let i = 0; i < this.floraClusters.length; i++) {
      const cl = this.floraClusters[i];
      if (cl.flowers.length) {
        const f = cl.flowers[0];
        perches.push({
          x: cl.x + f.dx * PIXEL_SCALE,
          y: cl.y - f.stemH * PIXEL_SCALE - 4,
          kind: "wildflower",
          zone: cl.zone,
          clusterIdx: i
        });
      }
    }

    this.waypoints = pts;
    this.sunflowerPerches = perches;
  }

  _buildRawPropPlacements(ox, oy, clampX, clampY) {
    const slots = [];
    const add = (id, x, y, zone) => {
      slots.push({ id, x: clampX(x, 22), y: clampY(y), zone });
    };

    const skyDome = document.querySelector(".sky-dome");
    if (skyDome) {
      const r = skyDome.getBoundingClientRect();
      const left = r.left - ox;
      const top = r.top - oy;
      add("starlightWindchime", left + r.width * 0.76, top + 34, "sky");
      add("weathervane", left + r.width * 0.92, top + 36, "sky");

      const skyPockets = [
        ["ironLantern", 0.06, 0.96],
        ["sunflowerCluster", 0.17, 0.88],
        ["dandelionPuff", 0.30, 0.95],
        ["dewPuddle", 0.45, 0.92],
        ["lavenderTuft", 0.60, 0.96],
        ["glowMushroomBlue", 0.74, 0.90],
        ["woodBirdhouse", 0.87, 0.95],
        ["chamomilePatch", 0.95, 0.86]
      ];
      for (let i = 0; i < skyPockets.length; i++) {
        const [id, fx, fy] = skyPockets[i];
        add(id, left + r.width * fx, top + r.height * fy, "sky");
      }
    }

    const matrixCanvas = document.getElementById("matrix-canvas");
    if (matrixCanvas) {
      const mr = matrixCanvas.getBoundingClientRect();
      const mLeft = mr.left - ox;
      const mTop = mr.top - oy;
      const matProps = [
        ["mossyStone", 0.08, 0.82],
        ["fireflyJar", 0.19, 0.46],
        ["cloverBed", 0.31, 0.84],
        ["crystalGeode", 0.43, 0.42],
        ["glowMushroomBlue", 0.55, 0.80],
        ["dandelionPuff", 0.67, 0.48],
        ["lavenderTuft", 0.79, 0.92],
        ["acornStash", 0.92, 0.94]
      ];
      for (let i = 0; i < matProps.length; i++) {
        const [id, fx, fy] = matProps[i];
        add(id, mLeft + mr.width * fx, mTop + mr.height * fy, "board");
      }
    }

    const radarCanvas = document.getElementById("radar-canvas");
    if (radarCanvas) {
      const rr = radarCanvas.getBoundingClientRect();
      const rLeft = rr.left - ox;
      const rTop = rr.top - oy;
      add("provenceStoneWall", rLeft + rr.width * 0.09, rTop + rr.height * 0.88, "board");
      add("hollowOakLog", rLeft + rr.width * 0.91, rTop + rr.height * 0.90, "board");
      if (this.docW >= 900) {
        add("ironLantern", rLeft + rr.width * 0.12, rTop + rr.height * 0.36, "board");
        add("berryBush", rLeft + rr.width * 0.88, rTop + rr.height * 0.24, "board");
      }
    }

    const consoleBox = document.querySelector(".console-box");
    if (consoleBox && this.docW >= 900) {
      const cr = consoleBox.getBoundingClientRect();
      const cLeft = cr.left - ox;
      const cBot = cr.bottom - oy - 3;
      add("fireflyJar", cLeft + cr.width * 0.84, cBot, "board");
      add("mossyStone", cLeft + cr.width * 0.94, cBot, "board");
    }

    const boards = document.querySelectorAll("section.board");
    if (boards[1]) {
      const br = boards[1].getBoundingClientRect();
      const bLeft = br.left - ox;
      const bBot = br.bottom - oy - 3;
      add("chamomilePatch", bLeft + 34, bBot, "board");
      add("cloverBed", bLeft + Math.min(310, br.width * 0.28), bBot, "board");
    }

    const viewports = document.querySelectorAll(".forum-viewport");
    const cardPairs = [
      ["strawNest", "amanitaMushroom"],
      ["pebbleBank", "oakBarrel"],
      ["woodSignpost", "steppingStones"]
    ];
    viewports.forEach((vp, idx) => {
      const r = vp.getBoundingClientRect();
      const left = r.left - ox;
      const top = r.top - oy;
      const pair = cardPairs[idx % cardPairs.length];
      add(pair[0], left + r.width * 0.16, top + r.height * 0.86, "card");
      add(pair[1], left + r.width * 0.74, top + r.height * 0.82, "card");
    });

    const garden = document.querySelector(".garden-observatory");
    if (garden) {
      const r = garden.getBoundingClientRect();
      const left = r.left - ox;
      const top = r.top - oy;
      const garProps = [
        ["cypressAlcove", 0.08, 0.48],
        ["wheatSheaf", 0.26, 0.44],
        ["gardenBench", 0.48, 0.52],
        ["wildRoseBush", 0.72, 0.46],
        ["sunflowerCluster", 0.91, 0.50],
        ["cattailReeds", 0.14, 0.73],
        ["streamBrook", 0.32, 0.76],
        ["miniFootbridge", 0.51, 0.74],
        ["lilypadLotus", 0.69, 0.77],
        ["splashFountain", 0.87, 0.74],
        ["fernFrond", 0.09, 0.94],
        ["glowMushroomBlue", 0.30, 0.93],
        ["dandelionPuff", 0.50, 0.95],
        ["ironLantern", 0.70, 0.93],
        ["lavenderTuft", 0.89, 0.94]
      ];
      for (let i = 0; i < garProps.length; i++) {
        const [id, fx, fy] = garProps[i];
        add(id, left + r.width * fx, top + r.height * fy, "garden");
      }
    }

    if (slots.length < 42) {
      for (let i = slots.length; i < 42; i++) {
        const p = PROP_CATALOG[i % PROP_CATALOG.length];
        const col = i % 6;
        const row = Math.floor((i - 20) / 6);
        add(p.id, 72 + col * ((this.docW - 144) / 5), Math.min(this.docH - 28, 360 + Math.max(0, row) * 140), "board");
      }
    }

    return slots;
  }

  _createFloraCluster(spot, idx) {
    const rand = seededRand(7391 + idx * 977);
    const bladeCount = spot.lush >= 2 ? (7 + Math.floor(rand() * 3)) : (5 + Math.floor(rand() * 3));
    const blades = [];
    const span = spot.lush >= 2 ? 7 : 5;
    for (let b = 0; b < bladeCount; b++) {
      const norm = bladeCount > 1 ? (b / (bladeCount - 1)) * 2 - 1 : 0;
      const dx = Math.round(norm * span + (rand() - 0.5) * 1.6);
      const centerBoost = 1 - Math.abs(norm) * 0.35;
      const height = Math.max(4, Math.round((spot.lush >= 2 ? 6 : 5) * centerBoost + rand() * 3.5));
      blades.push({
        dx,
        height,
        lean: norm * 1.15 + (rand() - 0.5) * 0.65,
        shade: b % BLADE_SHADES.length,
        phase: rand() * Math.PI * 2
      });
    }

    const flowerKinds = ["gold", "ivory", "starlight"];
    const flowerCount = spot.lush >= 2 ? (1 + (idx % 2)) : 1;
    const flowers = [];
    for (let f = 0; f < flowerCount; f++) {
      const fdx = flowerCount === 1 ? Math.round((rand() - 0.5) * 3) : (f === 0 ? -3 : 3);
      flowers.push({
        dx: fdx,
        stemH: (spot.lush >= 2 ? 6 : 5) + Math.floor(rand() * 3),
        kind: flowerKinds[(idx + f) % flowerKinds.length],
        phase: rand() * Math.PI * 2
      });
    }

    const sw = 24;
    const sh = 18;
    const sc = document.createElement("canvas");
    sc.width = sw;
    sc.height = sh;
    const sctx = sc.getContext("2d");
    const cx = 12;
    const cy = 16;
    for (let b = 0; b < blades.length; b++) {
      const bl = blades[b];
      const shades = BLADE_SHADES[bl.shade];
      for (let s = 0; s < bl.height; s++) {
        const frac = s / Math.max(1, bl.height - 1);
        const curve = Math.round(frac * frac * bl.lean);
        sctx.fillStyle = frac < 0.35 ? shades[0] : (frac < 0.78 ? shades[1] : shades[2]);
        sctx.fillRect(cx + bl.dx + curve, cy - s, 1, 1);
      }
    }
    for (let f = 0; f < flowers.length; f++) {
      const fl = flowers[f];
      let topX = cx + fl.dx;
      let topY = cy;
      for (let s = 0; s < fl.stemH; s++) {
        topY = cy - s;
        sctx.fillStyle = s < 2 ? "#064e3b" : "#15803d";
        sctx.fillRect(topX, topY, 1, 1);
      }
      const bloom = this.flowerSprites[fl.kind] || this.flowerSprites.gold;
      sctx.drawImage(bloom, topX - 2, topY - 4, 5, 5);
    }

    return {
      x: spot.x,
      y: spot.y,
      zone: spot.zone,
      blades,
      flowers,
      sprite: sc,
      spW: sw,
      spH: sh,
      bend: 0,
      bendVel: 0,
      rustleCooldown: 0
    };
  }

  _initButterflies() {
    const specs = ["morpho", "monarch", "swallowtail"];
    this.butterflies = specs.map((species, idx) => {
      const perch = this.sunflowerPerches[idx % Math.max(1, this.sunflowerPerches.length)] || { x: 180 + idx * 90, y: 220 };
      return {
        id: idx,
        species,
        x: perch.x,
        y: perch.y - 18,
        startX: perch.x,
        startY: perch.y - 18,
        destX: perch.x,
        destY: perch.y,
        facing: idx % 2 === 0 ? 1 : -1,
        mode: "cruise",
        t: 0,
        dur: 3.6 + idx * 0.7,
        perchTimer: 0,
        perchDur: 2.6,
        flapPhase: idx * 2.1,
        wavePhase: idx * 1.7,
        arcLift: 26,
        perchClusterIdx: -1
      };
    });

    if (!this.reducedMotion) {
      for (let i = 0; i < this.butterflies.length; i++) {
        const bf = this.butterflies[i];
        if (i === 0 && this.waypoints[0]) {
          bf.x = Math.max(40, Math.min(this.docW - 40, this.waypoints[0].x + 84));
          bf.y = Math.max(48, this.waypoints[0].y - 38);
        }
        this._assignButterflyDestination(bf, false);
      }
    }
  }

  _assignButterflyDestination(bf, startled = false) {
    bf.startX = bf.x;
    bf.startY = bf.y;
    bf.t = 0;

    const clampX = (v) => Math.max(32, Math.min(this.docW - 32, v));
    const clampY = (v) => Math.max(36, Math.min(this.docH - 26, v));

    if (!startled && this.sunflowerPerches.length && Math.random() < 0.62) {
      const candidates = this.sunflowerPerches.filter((p) => Math.hypot(p.x - bf.x, p.y - bf.y) > 48);
      const pickPool = candidates.length ? candidates : this.sunflowerPerches;
      const target = pickPool[Math.floor(Math.random() * pickPool.length)];
      bf.destX = clampX(target.x);
      bf.destY = clampY(target.y);
      bf.willPerch = true;
      bf.perchClusterIdx = typeof target.clusterIdx === "number" ? target.clusterIdx : -1;
    } else {
      const refWp = this.waypoints[Math.floor(Math.random() * Math.max(1, this.waypoints.length))] || { x: this.docW * 0.5, y: 240 };
      const spreadX = (Math.random() - 0.5) * Math.min(280, this.docW * 0.42);
      const liftY = 34 + Math.random() * 68;
      bf.destX = clampX(refWp.x + spreadX);
      bf.destY = clampY(refWp.y - liftY);
      bf.willPerch = false;
      bf.perchClusterIdx = -1;
    }

    const dist = Math.hypot(bf.destX - bf.startX, bf.destY - bf.startY);
    const speed = startled ? 132 : (68 + Math.random() * 26);
    bf.dur = Math.max(1.25, Math.min(5.8, dist / speed));
    bf.arcLift = startled ? (24 + Math.random() * 22) : (16 + Math.random() * 24);
    bf.mode = startled ? "startled" : "cruise";
    if (Math.abs(bf.destX - bf.startX) > 2) {
      bf.facing = bf.destX >= bf.startX ? 1 : -1;
    }
  }

  _startleButterfly(bf) {
    if (!bf || this.reducedMotion) return;
    if (bf.mode === "nosePerched" || bf.mode === "noseApproach") return;
    this._spawnPollenMotes(bf.x, bf.y, 2, bf.species === "morpho" ? "#7dd3fc" : "#fde047");
    this._assignButterflyDestination(bf, true);
  }

  _startleNearbyButterflies(cx, cy, radius) {
    for (let i = 0; i < this.butterflies.length; i++) {
      const bf = this.butterflies[i];
      if (Math.hypot(bf.x - cx, bf.y - cy) < radius) {
        this._startleButterfly(bf);
      }
    }
  }

  _summonButterflyTo(tx, ty) {
    if (!this.butterflies.length) return;
    let best = this.butterflies[0];
    let bestD = Infinity;
    for (let i = 0; i < this.butterflies.length; i++) {
      const bf = this.butterflies[i];
      const d = Math.hypot(bf.x - tx, bf.y - ty);
      if (d < bestD) {
        bestD = d;
        best = bf;
      }
    }
    best.mode = "twigCurious";
    best.startX = best.x;
    best.startY = best.y;
    best.destX = Math.max(32, Math.min(this.docW - 32, tx));
    best.destY = Math.max(38, Math.min(this.docH - 32, ty));
    best.t = 0;
    best.dur = 2.6;
    best.facing = best.destX >= best.x ? 1 : -1;
  }

  _initFireflies() {
    const count = 28;
    const rand = seededRand(51829);
    const shadeProps = this.props.filter((p) => p.category === "flora" || p.category === "dandelion" || p.category === "lantern" || p.category === "glow");
    const anchorPool = shadeProps.length ? shadeProps : this.props;
    this.fireflies = [];

    for (let i = 0; i < count; i++) {
      const home = anchorPool[i % Math.max(1, anchorPool.length)] || { x: 120 + i * 32, y: 260, zone: "garden" };
      const lift = 14 + rand() * 28;
      this.fireflies.push({
        id: i,
        homeX: home.x + (rand() - 0.5) * 14,
        homeY: home.y - 3,
        x: home.x,
        y: home.y - lift,
        roamRx: 18 + rand() * 30,
        roamRy: 10 + rand() * 16,
        lift,
        phase: rand() * Math.PI * 2,
        pulsePhase: rand() * Math.PI * 2,
        speed: 0.65 + rand() * 0.65,
        color: FIREFLY_COLORS[i % FIREFLY_COLORS.length],
        boopFlash: 0,
        zone: home.zone
      });
    }
  }

  _initCompanions() {
    const order = [
      { sp: "bluebird", zone: "sky", initAnim: "perchSway" },
      { sp: "rabbit", zone: "board", initAnim: "hop" },
      { sp: "squirrel", zone: "board", initAnim: "trot" },
      { sp: "hedgehog", zone: "board", initAnim: "sniff" },
      { sp: "calicoCat", zone: "board", initAnim: "walk" },
      { sp: "tawnyOwl", zone: "card", initAnim: "earPerk" },
      { sp: "redFox", zone: "card", initAnim: "gallop" },
      { sp: "mallardDuck", zone: "garden", initAnim: "drink" },
      { sp: "treeFrog", zone: "garden", initAnim: "hop" },
      { sp: "spottedDeer", zone: "garden", initAnim: "walk" }
    ];

    const usedPropUids = new Set();
    this.companions = order.map((item, idx) => {
      const def = COMPANION_SPECIES_DEFS[item.sp];
      const zoneProps = this.props.filter((p) => p.zone === item.zone && !usedPropUids.has(p.uid));
      const prefProps = zoneProps.filter((p) => def.preferredProps.includes(p.id));
      const allUnused = this.props.filter((p) => !usedPropUids.has(p.uid));
      const homeProp = prefProps[0] || zoneProps[idx % Math.max(1, zoneProps.length)] || allUnused[idx % Math.max(1, allUnused.length)] || this.props[idx % Math.max(1, this.props.length)] || { x: 140 + idx * 76, y: 260, zone: item.zone, uid: -1 };
      if (homeProp.uid >= 0) usedPropUids.add(homeProp.uid);

      const offsetSide = idx % 2 === 0 ? -14 : 14;
      const perchLift = (homeProp.category === "perch" && (item.sp === "bluebird" || item.sp === "tawnyOwl" || item.sp === "calicoCat" || item.sp === "squirrel")) ? -8 : 0;
      const safeStart = this._pushOutOfExclusions(homeProp.x + offsetSide, homeProp.y + perchLift, 16);

      const comp = {
        id: idx,
        species: item.sp,
        rhythm: def.rhythm,
        width: def.width,
        height: def.height,
        speed: def.speed,
        preferredProps: def.preferredProps,
        homeZone: item.zone,
        x: safeStart.x,
        y: safeStart.y,
        facing: idx % 2 === 0 ? 1 : -1,
        hopY: 0,
        shakeX: 0,
        tilt: 0,
        squashX: 1,
        squashY: 1,
        anim: this.reducedMotion ? (def.rhythm === "nocturnal" ? "perchSway" : "tailWag") : item.initAnim,
        timer: 0,
        duration: 1.4 + (idx % 4) * 0.35,
        startPt: { x: safeStart.x, y: safeStart.y },
        ctrlPt: { x: safeStart.x, y: safeStart.y },
        targetPt: { x: safeStart.x, y: safeStart.y },
        travelArc: 0,
        targetProp: homeProp,
        stepAccum: 0,
        tripCount: idx,
        bag: []
      };
      this._recordAnim25(comp.anim);
      if (!this.reducedMotion && LOCOMOTION_ANIMS.has(comp.anim)) {
        this._assignCompanionTravel(comp, comp.anim);
      }
      return comp;
    });
  }

  _assignCompanionTravel(comp, animName) {
    comp.tripCount = (comp.tripCount || 0) + 1;
    let tx = comp.x;
    let ty = comp.y;
    let destProp = null;

    const roll = Math.random();
    if (animName === "chaseButterfly" && this.butterflies.length) {
      const bf = this.butterflies[(comp.id + comp.tripCount) % this.butterflies.length];
      tx = bf.destX || bf.x;
      ty = (bf.destY || bf.y) + 12;
    } else if (roll < 0.22 && this.fireflies.length) {
      const ff = this.fireflies[(comp.id * 3 + comp.tripCount) % this.fireflies.length];
      tx = ff.homeX || ff.x;
      ty = (ff.homeY || ff.y) + 6;
    } else if (roll < 0.62 && this.waypoints.length) {
      const farWps = this.waypoints.filter((wp) => {
        const d = Math.hypot(wp.x - comp.x, wp.y - comp.y);
        return d > 64 && d < 680;
      });
      const wpPool = farWps.length ? farWps : this.waypoints;
      const wp = wpPool[Math.floor(Math.random() * wpPool.length)];
      tx = wp.x + (Math.random() - 0.5) * 34;
      ty = wp.y + (Math.random() - 0.5) * 26;
    } else if (this.props.length) {
      const candidates = this.props.filter((p) => {
        const d = Math.hypot(p.x - comp.x, p.y - comp.y);
        return d > 48 && d < 640;
      });
      const pickPool = candidates.length ? candidates : this.props;
      const prefMatches = pickPool.filter((p) => comp.preferredProps.includes(p.id));
      const finalPool = (prefMatches.length && Math.random() < 0.45) ? prefMatches : pickPool;
      destProp = finalPool[Math.floor(Math.random() * finalPool.length)];
      const side = destProp.x >= comp.x ? -12 : 12;
      const perchLift = (destProp.category === "perch" && (comp.species === "bluebird" || comp.species === "tawnyOwl" || comp.species === "calicoCat" || comp.species === "squirrel")) ? -8 : 0;
      tx = destProp.x + (perchLift ? 0 : side);
      ty = destProp.y + perchLift;
    }

    const safeDest = this._pushOutOfExclusions(tx, ty, 18);
    tx = safeDest.x;
    ty = safeDest.y;
    if (!destProp && this.props.length) {
      let nearest = this.props[0];
      let bestD = Infinity;
      for (let i = 0; i < this.props.length; i++) {
        const d = Math.hypot(this.props[i].x - tx, this.props[i].y - ty);
        if (d < bestD) {
          bestD = d;
          nearest = this.props[i];
        }
      }
      if (bestD < 72) destProp = nearest;
    }

    comp.startPt = { x: comp.x, y: comp.y };
    comp.targetPt = { x: tx, y: ty };
    comp.ctrlPt = this._makeCurvedControlPt(comp.x, comp.y, tx, ty, comp.id + comp.tripCount);
    comp.targetProp = destProp;
    const dist = Math.hypot(tx - comp.x, ty - comp.y);
    const mult = animName === "gallop" || animName === "chaseButterfly" ? 1.42 : (animName === "walk" || animName === "crouchStalk" ? 0.82 : 1.12);
    comp.duration = Math.max(0.85, Math.min(3.4, dist / Math.max(44, comp.speed * mult)));
    comp.travelArc = animName === "hop" ? 11 : 0;
    comp.timer = 0;
    comp.anim = animName;
    if (Math.abs(tx - comp.x) > 2) comp.facing = tx >= comp.x ? 1 : -1;
    this._recordAnim25(animName);
  }

  _pickCompanionNextAction(comp, env) {
    const prop = comp.targetProp;
    const cat = prop ? prop.category : "flora";
    const isDay = env.daylight >= 0.48;
    const sleepyPhase = (comp.rhythm === "diurnal" && !isDay) || (comp.rhythm === "nocturnal" && isDay);

    const unvisited = ANIMATION_25.filter((a) => !this.visitedAnims25.has(a));
    if (unvisited.length && Math.random() < 0.58) {
      const nextUnvisited = unvisited[comp.id % unvisited.length];
      if (LOCOMOTION_ANIMS.has(nextUnvisited)) {
        this._assignCompanionTravel(comp, nextUnvisited);
      } else {
        this._enterCompanionIdle(comp, nextUnvisited);
      }
      return;
    }

    if (Math.random() < 0.58) {
      const movePool = sleepyPhase
        ? ["walk", "trot"]
        : (comp.species === "rabbit" || comp.species === "treeFrog"
            ? ["hop", "hop", "binky", "trot"]
            : ["walk", "trot", "gallop", "chaseButterfly", "crouchStalk"]);
      const mv = movePool[Math.floor(Math.random() * movePool.length)];
      if (mv === "binky") {
        this._enterCompanionIdle(comp, "binky");
      } else {
        this._assignCompanionTravel(comp, mv);
      }
      return;
    }

    const weighted = [];
    if (cat === "water") weighted.push("drink", "drink", "shakeFur", "hop");
    if (cat === "flora" || cat === "dandelion") weighted.push("sniff", "graze", "bellyRoll", "pounce");
    if (cat === "perch" || cat === "chime") weighted.push("perchSway", "groom", "scratchEar", "stretch");
    if (cat === "lantern" || cat === "glow") weighted.push("boopFirefly", "earPerk", "stargazeMeteor", "tailWag");

    if (sleepyPhase) {
      weighted.push("sleepCurl", "sleepCurl", "yawn", "stretch");
    } else if (isDay) {
      weighted.push("sunBask", "sunBask", "binky", "happySpin", "tailWag", "chaseButterfly");
    } else {
      weighted.push("boopFirefly", "boopFirefly", "stargazeMeteor", "earPerk", "pounce");
    }

    const chosen = weighted[Math.floor(Math.random() * weighted.length)] || "tailWag";
    if (LOCOMOTION_ANIMS.has(chosen)) {
      this._assignCompanionTravel(comp, chosen);
    } else {
      this._enterCompanionIdle(comp, chosen);
    }
  }

  _enterCompanionIdle(comp, animName) {
    comp.anim = animName;
    comp.timer = 0;
    comp.hopY = 0;
    comp.shakeX = 0;
    comp.duration = animName === "sleepCurl" || animName === "sunBask" ? (2.3 + Math.random() * 1.1) : (1.25 + Math.random() * 0.85);
    this._recordAnim25(animName);

    if (comp.targetProp) {
      if (Math.abs(comp.targetProp.x - comp.x) > 3 && animName !== "perchSway") {
        comp.facing = comp.targetProp.x >= comp.x ? 1 : -1;
      }
      this._interactWithProp(comp.targetProp, comp.facing * 5.5, animName);
    }
    if (animName === "shakeFur") {
      this._spawnDewDrops(comp.x, comp.y - 12, 4);
    } else if (animName === "boopFirefly") {
      this._boopNearestFirefly(comp.x, comp.y - 16);
    }
  }

  _boopNearestFirefly(x, y) {
    if (!this.fireflies.length || this.reducedMotion) return;
    let best = this.fireflies[0];
    let bestD = Infinity;
    for (let i = 0; i < this.fireflies.length; i++) {
      const d = Math.hypot(this.fireflies[i].x - x, this.fireflies[i].y - y);
      if (d < bestD) {
        bestD = d;
        best = this.fireflies[i];
      }
    }
    if (best && bestD < 140) {
      best.boopFlash = 1.0;
      this._spawnPollenMotes(best.x, best.y, 3, "#bef264");
    }
  }

  // WHY: Triggers physical bend, concentric water ripples, floating dandelion seeds, chime swing, or bioluminescent glow pulse when an animal touches a prop.
  _interactWithProp(prop, impulse = 5, animHint = "") {
    if (!prop || this.reducedMotion) return;
    prop.bendVel = Math.max(-20, Math.min(20, prop.bendVel + impulse));
    if (prop.cooldown > 0) return;
    prop.cooldown = 0.45;

    if (prop.category === "water" || animHint === "drink") {
      this._spawnWaterRipple(prop.x, prop.y - 4);
    } else if (prop.category === "dandelion") {
      this._spawnDandelionSeeds(prop.x, prop.y - prop.height * PIXEL_SCALE + 6, 4);
    } else if (prop.category === "glow" || prop.category === "lantern") {
      prop.glowBoost = 1.0;
      this._spawnPollenMotes(prop.x, prop.y - 14, 2, prop.glowColor || "#fde047");
    } else if (prop.category === "chime") {
      prop.bendVel = impulse * 1.6;
      this._spawnPollenMotes(prop.x, prop.y - 18, 3, "#fde047");
    } else if (prop.category === "flora") {
      this._spawnPollenMotes(prop.x, prop.y - 14, 2);
    }
  }

  _spawnWaterRipple(x, y) {
    if (this.reducedMotion) return;
    if (this.waterRipples.length > 24) this.waterRipples.shift();
    this.waterRipples.push({ x, y, r: 3, maxR: 18, life: 1.0 });
  }

  _spawnDandelionSeeds(x, y, count = 4) {
    if (this.reducedMotion) return;
    for (let i = 0; i < count; i++) {
      if (this.dandelionSeeds.length > 36) this.dandelionSeeds.shift();
      this.dandelionSeeds.push({
        x: x + (Math.random() - 0.5) * 10,
        y: y + (Math.random() - 0.5) * 6,
        vx: 8 + Math.random() * 14,
        vy: -9 - Math.random() * 10,
        phase: Math.random() * Math.PI * 2,
        life: 1.0
      });
    }
  }

  _spawnDewDrops(x, y, count = 4) {
    if (this.reducedMotion) return;
    for (let i = 0; i < count; i++) {
      if (this.dewDrops.length > 32) this.dewDrops.shift();
      const ang = -Math.PI * 0.85 + (i / Math.max(1, count - 1)) * Math.PI * 0.7;
      this.dewDrops.push({
        x,
        y,
        vx: Math.cos(ang) * (20 + Math.random() * 18),
        vy: Math.sin(ang) * 24 - 10,
        life: 1.0,
        color: DEW_COLORS[i % DEW_COLORS.length]
      });
    }
  }

  _placeInitial() {
    if (this.reducedMotion) {
      this._parkCalmEcosystem();
      return;
    }
    const skyFlora = this.floraClusters.filter((c) => c.zone === "sky");
    const firstCluster = skyFlora[1] || skyFlora[0] || this.floraClusters[0];
    const startX = firstCluster ? Math.max(38, firstCluster.x - 68) : (this.waypoints[0] ? this.waypoints[0].x : 180);
    const startY = firstCluster ? firstCluster.y - 2 : (this.waypoints[0] ? this.waypoints[0].y : 260);
    const destX = firstCluster ? Math.max(38, Math.min(this.docW - 38, firstCluster.x - 18)) : startX + 72;
    const destY = firstCluster ? firstCluster.y - 2 : startY;

    this.x = startX;
    this.y = startY;
    this.facing = destX >= startX ? 1 : -1;
    this.startPt = { x: startX, y: startY };
    this.targetPt = { x: destX, y: destY, tag: "sunflower", zone: "sky" };
    this.gait = "trot";
    this.state = "trot";
    this._recordState("trot");
    this.travelDur = 0.82;
    this.travelT = 0;
    this.travelArc = 0;
    this._syncHitbox();
  }

  _parkCalmEcosystem() {
    const gardenFlora = this.floraClusters.filter((c) => c.zone === "garden");
    const anchorCluster = gardenFlora[1] || gardenFlora[0] || this.floraClusters[0];
    if (anchorCluster) {
      this.x = Math.max(42, Math.min(this.docW - 72, anchorCluster.x - 42));
      this.y = anchorCluster.y - 1;
      this.facing = 1;
    } else {
      const wp = this.waypoints[this.waypoints.length - 1] || { x: 180, y: 260 };
      this.x = wp.x;
      this.y = wp.y;
      this.facing = 1;
    }

    this.hopY = 0;
    this.shakeX = 0;
    this.state = "sit";
    this._recordState("sit");
    this.earPerkTimer = 0;
    this.pawPuffs.length = 0;
    this.sparks.length = 0;
    this.napStars.length = 0;
    this.pollenMotes.length = 0;
    this.dandelionSeeds.length = 0;
    this.waterRipples.length = 0;
    this.dewDrops.length = 0;
    this.emote = null;
    this.twig = null;

    for (let i = 0; i < this.floraClusters.length; i++) {
      this.floraClusters[i].bend = 0;
      this.floraClusters[i].bendVel = 0;
    }

    for (let i = 0; i < this.props.length; i++) {
      this.props[i].bend = 0;
      this.props[i].bendVel = 0;
      this.props[i].glowBoost = 0;
    }

    for (let i = 0; i < this.fireflies.length; i++) {
      const ff = this.fireflies[i];
      ff.x = Math.max(24, Math.min(this.docW - 24, ff.homeX + ((i % 3) - 1) * 10));
      ff.y = Math.max(32, Math.min(this.docH - 18, ff.homeY - 14 - (i % 4) * 4));
      ff.boopFlash = 0;
    }

    for (let i = 0; i < this.companions.length; i++) {
      const c = this.companions[i];
      const hp = c.targetProp || this.props[i % Math.max(1, this.props.length)];
      if (hp) {
        c.x = Math.max(28, Math.min(this.docW - 28, hp.x + (i % 2 === 0 ? -12 : 12)));
        c.y = Math.max(40, Math.min(this.docH - 14, hp.y));
      }
      c.hopY = 0;
      c.shakeX = 0;
      c.anim = c.rhythm === "nocturnal" ? "perchSway" : "tailWag";
    }

    if (this.butterflies[0]) {
      const bf0 = this.butterflies[0];
      if (anchorCluster && anchorCluster.flowers[0]) {
        const fl = anchorCluster.flowers[0];
        bf0.x = anchorCluster.x + fl.dx * PIXEL_SCALE;
        bf0.y = anchorCluster.y - fl.stemH * PIXEL_SCALE - 4;
      } else {
        bf0.x = Math.min(this.docW - 34, this.x + 28);
        bf0.y = this.y - 16;
      }
      bf0.facing = -1;
      bf0.mode = "perched";
    }

    for (let i = 1; i < this.butterflies.length; i++) {
      const bf = this.butterflies[i];
      const perch = this.sunflowerPerches[(i * 3) % Math.max(1, this.sunflowerPerches.length)];
      if (perch) {
        bf.x = perch.x;
        bf.y = perch.y;
      }
      bf.mode = "perched";
      bf.facing = i % 2 === 0 ? 1 : -1;
    }

    this._syncHitbox();
  }

  _maybeShowEmote(kind, forceUser = false) {
    if (!this.emoteSprites[kind]) return;
    if (forceUser) {
      if (this.petEmoteGuard > 0) return;
      this.petEmoteGuard = 1.1;
      this.emote = { kind, age: 0, duration: 1.55 };
      return;
    }
    if (this.autoEmoteCooldown > 0 || this.emote) return;
    this.autoEmoteCooldown = 15 + Math.random() * 13;
    this.emote = { kind, age: 0, duration: 1.95 };
  }

  _rustleFloraCluster(cl, impulse, spawnPollen = true) {
    if (!cl || this.reducedMotion) return;
    cl.bendVel = Math.max(-22, Math.min(22, cl.bendVel + impulse));
    if (spawnPollen && cl.rustleCooldown <= 0) {
      cl.rustleCooldown = 0.42;
      const fx = cl.x + (cl.flowers[0] ? cl.flowers[0].dx * PIXEL_SCALE : 0);
      const fy = cl.y - (cl.flowers[0] ? cl.flowers[0].stemH * PIXEL_SCALE : 10);
      this._spawnPollenMotes(fx, fy, 2 + Math.floor(Math.random() * 2));
    }
  }

  _spawnPollenMotes(x, y, count = 3, customColor = null) {
    if (this.reducedMotion) return;
    for (let i = 0; i < count; i++) {
      if (this.pollenMotes.length > 36) this.pollenMotes.shift();
      this.pollenMotes.push({
        x: x + (Math.random() - 0.5) * 12,
        y: y + (Math.random() - 0.5) * 6,
        vx: (Math.random() - 0.5) * 10,
        vy: -10 - Math.random() * 11,
        phase: Math.random() * Math.PI * 2,
        life: 1.0,
        color: customColor || POLLEN_COLORS[i % POLLEN_COLORS.length]
      });
    }
  }

  _findNearestFlora(maxDist = 180) {
    let best = null;
    let bestD = maxDist;
    for (let i = 0; i < this.floraClusters.length; i++) {
      const cl = this.floraClusters[i];
      const d = Math.hypot(cl.x - this.x, cl.y - this.y);
      if (d < bestD) {
        bestD = d;
        best = cl;
      }
    }
    return best;
  }

  _pickNextWaypoint(preferFlora = false) {
    if (!this.waypoints.length) return;
    const viewTop = window.scrollY - 80;
    const viewBot = window.scrollY + (window.innerHeight || 900) + 120;
    const inOpening = this.openingQueue.length > 0;

    if (preferFlora && Math.random() < 0.42 && this.floraClusters.length) {
      const maxFloraDist = inOpening ? 240 : 540;
      const nearFlora = this.floraClusters.filter((c) => {
        const d = Math.hypot(c.x - this.x, c.y - this.y);
        const vis = !inOpening || (c.y >= viewTop && c.y <= viewBot);
        return vis && d > 36 && d < maxFloraDist;
      });
      const pool = nearFlora.length ? nearFlora : this.floraClusters;
      const cl = pool[Math.floor(Math.random() * pool.length)];
      const side = cl.x > this.docW * 0.5 ? -1 : 1;
      const safe = this._pushOutOfExclusions(cl.x - side * 22, cl.y - 1, 18);
      this._beginTravelTo({ x: safe.x, y: safe.y, tag: "sunflower", zone: cl.zone, floraRef: cl });
      return;
    }

    const candidates = [];
    for (let i = 0; i < this.waypoints.length; i++) {
      if (i === this.currentWpIdx && this.waypoints.length > 1) continue;
      const wp = this.waypoints[i];
      const dist = Math.hypot(wp.x - this.x, wp.y - this.y);
      if (dist < 42 && this.waypoints.length > 2) continue;
      const inView = wp.y >= viewTop && wp.y <= viewBot;
      const crossY = Math.abs(wp.y - this.y) > 48 ? 1.45 : 0.9;
      const nearJump = inOpening ? (dist < 280 ? 3.2 : 0.4) : (dist < 680 ? 2.0 : 0.9);
      const weight = (inView ? 2.4 : 0.85) * nearJump * crossY;
      candidates.push({ idx: i, wp, weight });
    }

    const pool = candidates.length ? candidates : this.waypoints.map((wp, idx) => ({ idx, wp, weight: 1 }));
    let total = 0;
    for (let i = 0; i < pool.length; i++) total += pool[i].weight;
    let pick = Math.random() * total;
    let chosen = pool[0];
    for (let i = 0; i < pool.length; i++) {
      pick -= pool[i].weight;
      if (pick <= 0) {
        chosen = pool[i];
        break;
      }
    }

    this.currentWpIdx = chosen.idx;
    this._beginTravelTo(chosen.wp);
  }

  _beginTravelTo(destWp) {
    this._releaseInteractiveButterfly();
    const safe = this._pushOutOfExclusions(destWp.x, destWp.y, 18);
    this.startPt = { x: this.x, y: this.y };
    this.targetPt = { ...destWp, x: safe.x, y: safe.y };
    this.ctrlPt = this._makeCurvedControlPt(this.x, this.y, safe.x, safe.y, Math.max(0, this.currentWpIdx));
    const dist = Math.hypot(this.targetPt.x - this.startPt.x, this.targetPt.y - this.startPt.y);
    const wantsRun = dist > 220 && Math.random() < 0.46;
    this.gait = wantsRun ? "run" : "trot";
    const speed = wantsRun ? (158 + Math.random() * 28) : (102 + Math.random() * 20);
    this.travelDur = Math.max(0.75, Math.min(3.8, dist / speed));
    this.travelT = 0;
    this.travelArc = 0;
    if (Math.abs(this.targetPt.x - this.startPt.x) > 3) {
      this.facing = this.targetPt.x >= this.startPt.x ? 1 : -1;
    }
    this.state = wantsRun ? "run" : "trot";
    this._recordState(this.state);
    if (wantsRun && Math.random() < 0.4) {
      this._maybeShowEmote("note", false);
    }
    this._syncHitbox();
  }

  _nextFromBag() {
    if (this.openingQueue.length) {
      return this.openingQueue.shift();
    }
    if (!this.behaviorBag.length) {
      const env = this._currentEnv();
      const deck = [
        "sniffFlora",
        "stalkButterfly",
        "butterflyNosePerch",
        "binky",
        "drink",
        "boopFirefly",
        "shakeFur",
        "bellyRoll",
        "scratchEar",
        "yawnStretch",
        "groom",
        "graze",
        "happySpin",
        env.daylight >= 0.45 ? "sunBask" : "stargazeMeteor",
        env.daylight >= 0.45 ? "sit" : "nap"
      ];
      for (let i = deck.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        const tmp = deck[i];
        deck[i] = deck[j];
        deck[j] = tmp;
      }
      this.behaviorBag = deck;
    }
    return this.behaviorBag.pop();
  }

  _chooseIdleBehavior() {
    const choice = this._nextFromBag();
    if (choice === "sniffFlora") {
      this._startSniffFlora();
    } else if (choice === "stalkButterfly") {
      this._startStalkButterfly();
    } else if (choice === "butterflyNosePerch") {
      this._startButterflyNosePerch();
    } else if (choice === "binky") {
      this._enterState("binky", 1.25);
      this._burstGoldenSparks(7);
    } else if (choice === "drink") {
      const waterProp = this.props.find((p) => p.category === "water" && Math.hypot(p.x - this.x, p.y - this.y) < 160) || this.props.find((p) => p.category === "water");
      if (waterProp) this._interactWithProp(waterProp, 4, "drink");
      this._enterState("drink", 1.55);
    } else if (choice === "boopFirefly") {
      this._boopNearestFirefly(this.x, this.y - 18);
      this._enterState("boopFirefly", 1.35);
    } else if (choice === "shakeFur") {
      this._spawnDewDrops(this.x, this.y - 16, 5);
      this._enterState("shakeFur", 1.15);
    } else if (choice === "groom") {
      this._enterState("groom", 1.45);
    } else if (choice === "graze") {
      this._enterState("graze", 1.5);
    } else if (choice === "happySpin") {
      this._enterState("happySpin", 1.25);
    } else if (choice === "stargazeMeteor") {
      this._enterState("stargazeMeteor", 1.65);
    } else if (choice === "sunBask") {
      this._enterState("sunBask", 2.4);
    } else if (choice === "bellyRoll") {
      this._enterState("bellyRoll", 1.75 + Math.random() * 0.45);
      this._maybeShowEmote("heart", false);
    } else if (choice === "scratchEar") {
      this._enterState("scratchEar", 1.55 + Math.random() * 0.4);
    } else if (choice === "yawnStretch") {
      this._enterState("yawnStretch", 1.65 + Math.random() * 0.35);
    } else if (choice === "rest") {
      this._enterState("rest", 2.8 + Math.random() * 1.1);
      this._maybeShowEmote("zzz", false);
    } else if (choice === "nap") {
      this._enterState("nap", 3.0);
      this._maybeShowEmote("zzz", false);
    } else {
      this._enterState("sit", 2.2 + Math.random() * 0.9);
      this._maybeShowEmote("curious", false);
    }
  }

  _enterState(nextState, duration) {
    if (nextState !== "stalkButterfly" && nextState !== "pounceButterfly" && nextState !== "butterflyNosePerch") {
      this._releaseInteractiveButterfly();
    }
    this.state = nextState;
    this._recordState(nextState);
    this.stateTimer = 0;
    this.stateDuration = duration;
    this.hopY = 0;
    this._syncHitbox();
  }

  _startSniffFlora() {
    const near = (this.targetPt && this.targetPt.floraRef) || this._findNearestFlora(96);
    this.activeFlora = near || null;
    if (near && Math.abs(near.x - this.x) > 4) {
      this.facing = near.x >= this.x ? 1 : -1;
    }
    this.sniffWillSneeze = Math.random() < 0.65;
    this.sneezeTriggered = false;
    this._enterState("sniffFlora", this.sniffWillSneeze ? 1.95 : 1.65);
    this._maybeShowEmote("curious", false);
    if (near) {
      this._rustleFloraCluster(near, this.facing * 6.5, true);
    }
  }

  _pickPartnerButterfly() {
    if (!this.butterflies.length) return null;
    let best = this.butterflies[0];
    let bestD = Infinity;
    for (let i = 0; i < this.butterflies.length; i++) {
      const bf = this.butterflies[i];
      const d = Math.hypot(bf.x - this.x, bf.y - this.y);
      if (d < bestD) {
        bestD = d;
        best = bf;
      }
    }
    return best;
  }

  _releaseInteractiveButterfly() {
    if (!this.activeButterfly) return;
    const bf = this.activeButterfly;
    this.activeButterfly = null;
    if (bf.mode === "playDance" || bf.mode === "noseApproach" || bf.mode === "nosePerched") {
      this._spawnPollenMotes(bf.x, bf.y, 2, bf.species === "morpho" ? "#7dd3fc" : "#fde047");
      this._assignButterflyDestination(bf, false);
    }
  }

  _startStalkButterfly() {
    const bf = this._pickPartnerButterfly();
    if (!bf) {
      this._enterState("sit", 1.8);
      return;
    }
    this.activeButterfly = bf;
    const dir = this.x < this.docW * 0.5 ? 1 : (this.x > this.docW - 140 ? -1 : (bf.x >= this.x ? 1 : -1));
    this.facing = dir;
    const danceX = Math.max(46, Math.min(this.docW - 46, this.x + dir * 56));
    const danceY = Math.max(44, Math.min(this.docH - 36, this.y - 26));
    bf.mode = "playDance";
    bf.startX = bf.x;
    bf.startY = bf.y;
    bf.destX = danceX;
    bf.destY = danceY;
    bf.t = 0;
    this._enterState("stalkButterfly", 1.15);
    this._maybeShowEmote("alert", false);
  }

  _startPounceButterfly() {
    const bf = this.activeButterfly;
    this.pounceStartX = this.x;
    const dir = this.facing;
    this.pounceTargetX = Math.max(40, Math.min(this.docW - 40, this.x + dir * 48));
    if (bf) {
      bf.destX = this.pounceTargetX + dir * 10;
      bf.destY = Math.max(36, this.y - 44);
    }
    this.state = "pounceButterfly";
    this._recordState("pounceButterfly");
    this.stateTimer = 0;
    this.stateDuration = 1.15;
    this._syncHitbox();
  }

  _startButterflyNosePerch() {
    const bf = this._pickPartnerButterfly();
    if (!bf) {
      this._enterState("sit", 2.0);
      return;
    }
    this.activeButterfly = bf;
    if (Math.abs(bf.x - this.x) > 6) {
      this.facing = bf.x >= this.x ? 1 : -1;
    }
    this.state = "butterflyNosePerch";
    this._recordState("butterflyNosePerch");
    this.stateTimer = 0;
    this.stateDuration = 2.95;
    this.hopY = 0;

    const snout = this._getSnoutAnchor();
    bf.mode = "noseApproach";
    bf.startX = bf.x;
    bf.startY = bf.y;
    bf.destX = snout.x;
    bf.destY = snout.y;
    bf.t = 0;
    bf.dur = 0.45;
    bf.facing = -this.facing;
    this._syncHitbox();
  }

  _getSnoutAnchor() {
    const drawW = SPRITE_W * ANIMAL_SCALE;
    const drawH = SPRITE_H * ANIMAL_SCALE;
    const leftX = this.x - drawW * 0.5;
    const topY = this.y - drawH + 6 + this.hopY;
    const noseCol = this.facing >= 0 ? 25 : (SPRITE_W - 1 - 25);
    return {
      x: leftX + noseCol * ANIMAL_SCALE,
      y: topY + 8 * ANIMAL_SCALE - 2
    };
  }

  _getMouthTwigAnchor() {
    const drawW = SPRITE_W * ANIMAL_SCALE;
    const drawH = SPRITE_H * ANIMAL_SCALE;
    const leftX = this.x - drawW * 0.5;
    const topY = this.y - drawH + 6 + this.hopY;
    const mouthCol = this.facing >= 0 ? 28 : (SPRITE_W - 1 - 28);
    return {
      x: leftX + mouthCol * ANIMAL_SCALE,
      y: topY + 12 * ANIMAL_SCALE
    };
  }

  triggerPet() {
    this.petCount += 1;
    this._releaseInteractiveButterfly();
    this._startleNearbyButterflies(this.x, this.y, 56);
    this.napStars.length = 0;
    if (this.twig && this.twig.phase === "carried") {
      this.twig.phase = "delivered";
      this.twig.x = this.x + this.facing * 22;
      this.twig.y = this.y - 2;
      this.twig.holdTimer = 1.8;
    }

    const variant = (this.petCount - 1) % 3;
    const reactionNames = ["play-bow-hop", "belly-rub-roll", "tail-chase-spin"];
    const stateNames = ["petBowHop", "petBellyRoll", "petTailSpin"];
    const chosenReaction = reactionNames[variant];
    const chosenState = stateNames[variant];
    this.lastPetReaction = chosenReaction;
    this._maybeShowEmote(variant === 2 ? "note" : "heart", true);

    if (this.reducedMotion) {
      this.state = chosenState;
      this._recordState(chosenState);
      this.sparks.length = 0;
      for (let i = 0; i < 8; i++) {
        const a = (i * Math.PI * 2) / 8;
        this.sparks.push({
          x: this.x + Math.cos(a) * 24,
          y: this.y - 28 + Math.sin(a) * 16,
          vx: 0,
          vy: 0,
          life: 0.9,
          color: SPARK_COLORS[i % SPARK_COLORS.length],
          big: i % 2 === 0
        });
      }
      this._syncHitbox(true);
      this.render();
      clearTimeout(this._rmResetTimer);
      this._rmResetTimer = setTimeout(() => {
        if (!this.reducedMotion) return;
        this.sparks.length = 0;
        this.emote = null;
        this.state = "sit";
        this._syncHitbox(true);
        this.render();
      }, 750);
      return;
    }

    const dur = variant === 1 ? 1.55 : 1.3;
    this._enterState(chosenState, dur);
    this._syncHitbox(true);
    this._burstGoldenSparks(12);
    if (this.onJoyPulse) {
      this.onJoyPulse(this.x / Math.max(1, this.docW), this.y / Math.max(1, this.docH), 7, -6);
    }
  }

  triggerTwigToss(clientX, clientY, zoneEl) {
    const modal = document.getElementById("stage-modal");
    if (modal && modal.open) return;

    const layerRect = this.layer.getBoundingClientRect();
    const rawX = clientX - layerRect.left;
    const rawY = clientY - layerRect.top;
    const zr = zoneEl ? zoneEl.getBoundingClientRect() : layerRect;
    const zLeft = zr.left - layerRect.left;
    const zTop = zr.top - layerRect.top;

    const clampedX = Math.max(38, Math.min(this.docW - 38, Math.max(zLeft + 28, Math.min(zLeft + zr.width - 28, rawX))));
    const clampedY = Math.max(48, Math.min(this.docH - 20, Math.max(zTop + 28, Math.min(zTop + zr.height - 14, rawY))));
    const safeLand = this._pushOutOfExclusions(clampedX, clampedY, 18);
    const landX = safeLand.x;
    const landY = safeLand.y;

    this.fetchCount += 1;
    this._releaseInteractiveButterfly();

    if (this.reducedMotion) {
      this.twig = {
        phase: "delivered",
        startX: landX,
        startY: landY,
        x: Math.min(this.docW - 32, this.x + this.facing * 26),
        y: this.y - 2,
        landX,
        landY,
        t: 1,
        dur: 0.3,
        holdTimer: 1.0
      };
      this._maybeShowEmote("sparkle", true);
      this._syncHitbox(true);
      this.render();
      clearTimeout(this._rmTwigTimer);
      this._rmTwigTimer = setTimeout(() => {
        if (!this.reducedMotion) return;
        this.twig = null;
        this.emote = null;
        this._syncHitbox(true);
        this.render();
      }, 850);
      return;
    }

    this.twig = {
      phase: "tossed",
      startX: Math.max(24, Math.min(this.docW - 24, rawX)),
      startY: Math.max(20, Math.min(rawY, landY - 34)),
      x: rawX,
      y: Math.min(rawY, landY - 34),
      landX,
      landY,
      t: 0,
      dur: 0.32,
      holdTimer: 0
    };

    this._summonButterflyTo(landX, landY - 24);

    const nearby = Math.hypot(this.x - landX, this.y - landY) <= 320 && Math.hypot(this.x - landX, this.y - landY) >= 56;
    const retDir = landX > this.docW * 0.5 ? -1 : 1;
    const fallbackRet = this._pushOutOfExclusions(
      landX + retDir * Math.min(112, zr.width * 0.24),
      landY + (landY > this.docH * 0.5 ? -24 : 24),
      18
    );
    this.fetchReturnPt = nearby ? { x: this.x, y: this.y } : fallbackRet;

    this.fetchGoalPt = { x: landX, y: landY };
    this.fetchStartPt = { x: this.x, y: this.y };
    this.facing = landX >= this.x ? 1 : -1;
    this.fetchPhase = "perk";
    this.fetchTimer = 0;
    const dist = Math.hypot(landX - this.x, landY - this.y);
    this.fetchMoveDur = Math.max(0.55, Math.min(1.95, dist / 172));
    this.state = "fetchTwig";
    this._recordState("fetchTwig");
    this.hopY = 0;
    this._maybeShowEmote("alert", true);

    if (this.onJoyPulse) {
      this.onJoyPulse(landX / Math.max(1, this.docW), landY / Math.max(1, this.docH), 6, -5);
    }
    this._syncHitbox(true);
  }

  _burstGoldenSparks(count) {
    if (this.reducedMotion) return;
    for (let i = 0; i < count; i++) {
      const a = -Math.PI * 0.92 + (i / Math.max(1, count - 1)) * Math.PI * 0.84 + (Math.random() - 0.5) * 0.25;
      const spd = 28 + Math.random() * 44;
      this.sparks.push({
        x: this.x + (Math.random() - 0.5) * 18,
        y: this.y - 24 + (Math.random() - 0.5) * 10,
        vx: Math.cos(a) * spd,
        vy: Math.sin(a) * spd - 14,
        life: 1.0,
        color: SPARK_COLORS[i % SPARK_COLORS.length],
        big: i % 3 === 0
      });
    }
  }

  _spawnPawPuff() {
    if (this.pawPuffs.length > 28) this.pawPuffs.shift();
    const backX = this.x - this.facing * 14 + (Math.random() - 0.5) * 6;
    const baseY = this.y - 2 + (Math.random() - 0.5) * 3;
    this.pawPuffs.push({
      x: backX,
      y: baseY,
      vx: -this.facing * (8 + Math.random() * 10),
      vy: -8 - Math.random() * 8,
      swirl: Math.random() * Math.PI * 2,
      life: 1.0,
      color: Math.random() < 0.65 ? "#fde047" : "#7dd3fc"
    });
  }

  _bindEvents() {
    let resizeTimer = 0;
    const handleResize = () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        this._resize();
        this._collectWaypointsAndFlora();
        this._initFireflies();
        this._initCompanions();
        if (this.reducedMotion) {
          this._parkCalmEcosystem();
        } else {
          this.x = Math.max(38, Math.min(this.docW - 38, this.x));
          this.y = Math.max(48, Math.min(this.docH - 18, this.y));
          for (let i = 0; i < this.butterflies.length; i++) {
            this.butterflies[i].x = Math.max(32, Math.min(this.docW - 32, this.butterflies[i].x));
            this.butterflies[i].y = Math.max(36, Math.min(this.docH - 26, this.butterflies[i].y));
          }
          this._syncHitbox(true);
        }
        this.render();
      }, 80);
    };

    window.addEventListener("resize", handleResize);

    if (typeof ResizeObserver === "function") {
      const ro = new ResizeObserver(() => {
        const nextH = Math.max(480, document.body.offsetHeight || 1400);
        if (Math.abs(nextH - this.docH) > 96) handleResize();
      });
      ro.observe(document.body);
    }

    this.mqReduced.addEventListener("change", (ev) => {
      this.reducedMotion = ev.matches;
      if (this.reducedMotion) {
        this._parkCalmEcosystem();
        this.render();
      } else {
        this._initButterflies();
        this._initFireflies();
        this._initCompanions();
        this._pickNextWaypoint(true);
        this._startLoop();
      }
    });

    this.hitbox.addEventListener("click", (ev) => {
      ev.stopPropagation();
      this.triggerPet();
    });

    this.hitbox.addEventListener("dblclick", (ev) => {
      ev.stopPropagation();
    });

    const tossZones = document.querySelectorAll(".sky-dome, .garden-observatory, section.board");
    tossZones.forEach((zoneEl) => {
      zoneEl.addEventListener("dblclick", (ev) => {
        if (ev.target && ev.target.closest && ev.target.closest("button, a, #portrait-canvas, #radar-canvas")) return;
        this.triggerTwigToss(ev.clientX, ev.clientY, zoneEl);
      });
    });

    this.hitbox.addEventListener("pointerenter", () => {
      if (this.reducedMotion) return;
      this.earPerkTimer = 1.3;
      this.hoverPauseTimer = 0.85;
    });

    window.addEventListener("pointermove", (ev) => {
      if (this.reducedMotion) return;
      const modal = document.getElementById("stage-modal");
      if (modal && modal.open) return;
      const r = this.layer.getBoundingClientRect();
      const px = ev.clientX - r.left;
      const py = ev.clientY - r.top;
      const dist = Math.hypot(px - this.x, py - (this.y - 24));
      if (dist < 116) {
        this.cursorNear = true;
        this.earPerkTimer = 0.9;
        const idleGlance = this.state === "sit" || this.state === "rest";
        if (idleGlance && Math.abs(px - this.x) > 14) {
          this.facing = px >= this.x ? 1 : -1;
        }
      } else {
        this.cursorNear = false;
      }

      if (Math.hypot(ev.movementX || 0, ev.movementY || 0) > 9) {
        this._startleNearbyButterflies(px, py, 40);
      }
    }, { passive: true });
  }

  _syncHitbox(forceTelemetry = false) {
    const modal = document.getElementById("stage-modal");
    const modalOpen = Boolean(modal && modal.open);
    if (this.hitbox.hidden !== modalOpen) {
      this.hitbox.hidden = modalOpen;
    }
    const hx = Math.round(Math.max(0, Math.min(this.docW - 72, this.x - 36)));
    const hy = Math.round(Math.max(0, Math.min(this.docH - 72, this.y - 62 + this.hopY)));
    const tickReady = this._datasetAccum >= 0.25;
    if (forceTelemetry || this.reducedMotion || tickReady || Math.hypot(hx - this._lastHx, hy - this._lastHy) >= 18) {
      this._lastHx = hx;
      this._lastHy = hy;
      this._lastSyncState = this.state;
      this.hitbox.style.transform = `translate3d(${hx}px, ${hy}px, 0)`;
    }

    if (forceTelemetry || this.reducedMotion || tickReady) {
      this._datasetAccum = 0;
      const env = this._currentEnv();
      const activeSet = new Set([this._mapDogStateToAnim25(this.state)]);
      for (let i = 0; i < this.companions.length; i++) {
        activeSet.add(this.companions[i].anim);
      }

      const setD = (k, v) => {
        if (this.hitbox.dataset[k] !== v) this.hitbox.dataset[k] = v;
      };
      setD("state", this.state);
      setD("pets", String(this.petCount));
      setD("petReaction", this.lastPetReaction);
      setD("butterflies", String(this.butterflies.length));
      setD("flora", String(this.floraClusters.length));
      setD("fetches", String(this.fetchCount));
      setD("twig", this.twig ? this.twig.phase : "none");
      setD("emote", this.emote ? this.emote.kind : "");
      setD("history", Array.from(this.visitedStates).join(","));
      setD("speciesCount", String(SPECIES_IDS.length));
      setD("animCount", String(ANIMATION_25.length));
      setD("propsCount", String(this.props.length));
      setD("fireflies", String(this.fireflies.length));
      setD("dayPhase", env.phase);
      setD("daylight", env.daylight.toFixed(2));
      setD("meteors", String(env.meteorsLaunched || 0));
      setD("activeAnims", Array.from(activeSet).join(","));
      setD("visitedAnims", String(this.visitedAnims25.size));
    }
  }

  _startLoop() {
    if (this._looping) return;
    this._looping = true;
    this._prevBandTop = 0;
    this._prevBandBot = this.docH;
    this._fullSyncTick = 0;
    let last = performance.now();
    const step = (now) => {
      if (this.reducedMotion) {
        this._looping = false;
        return;
      }
      const dt = Math.min(0.05, Math.max(0.001, (now - last) / 1000));
      last = now;
      this.update(dt);
      this._fullSyncTick = (this._fullSyncTick + 1) % 45;
      this.render(this._fullSyncTick === 0);
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  _updateFlora(dt) {
    const movingDog = this.state === "trot" || this.state === "run" || this.state === "pounceButterfly" || (this.state === "fetchTwig" && (this.fetchPhase === "go" || this.fetchPhase === "return"));
    for (let i = 0; i < this.floraClusters.length; i++) {
      const cl = this.floraClusters[i];
      if (cl.rustleCooldown > 0) cl.rustleCooldown = Math.max(0, cl.rustleCooldown - dt);

      if (movingDog && Math.abs(this.x - cl.x) < 24 && Math.abs(this.y - cl.y) < 20) {
        const pushDir = this.x <= cl.x ? 1 : -1;
        this._rustleFloraCluster(cl, pushDir * 34 * dt, true);
      }

      cl.bendVel += (-26 * cl.bend - 5.6 * cl.bendVel) * dt;
      cl.bend = Math.max(-3.6, Math.min(3.6, cl.bend + cl.bendVel * dt));
    }
  }

  _updateButterflies(dt) {
    for (let i = 0; i < this.butterflies.length; i++) {
      const bf = this.butterflies[i];
      bf.flapPhase += dt * (bf.mode === "startled" ? 13.5 : 9.2);

      if (bf.mode === "cruise" || bf.mode === "startled") {
        bf.t += dt / Math.max(0.5, bf.dur);
        const u = Math.min(1, bf.t);
        const ease = u * u * (3 - 2 * u);
        const breezeX = Math.sin(u * Math.PI * 2 + bf.wavePhase) * 14 * (1 - Math.abs(2 * u - 1));
        const breezeY = -Math.sin(u * Math.PI) * bf.arcLift + Math.sin(this.animTime * 4.6 + bf.wavePhase) * 4.5 * (1 - u * 0.65);
        const nx = bf.startX + (bf.destX - bf.startX) * ease + breezeX;
        const ny = bf.startY + (bf.destY - bf.startY) * ease + breezeY;
        if (Math.abs(nx - bf.x) > 0.25) bf.facing = nx >= bf.x ? 1 : -1;
        bf.x = Math.max(26, Math.min(this.docW - 26, nx));
        bf.y = Math.max(30, Math.min(this.docH - 22, ny));

        if (u >= 1) {
          if (bf.willPerch) {
            bf.mode = "perched";
            bf.x = bf.destX;
            bf.y = bf.destY;
            bf.perchTimer = 0;
            bf.perchDur = 2.2 + Math.random() * 2.4;
            if (bf.perchClusterIdx >= 0 && this.floraClusters[bf.perchClusterIdx]) {
              this._rustleFloraCluster(this.floraClusters[bf.perchClusterIdx], bf.facing * 3.2, false);
            }
          } else {
            this._assignButterflyDestination(bf, false);
          }
        }
      } else if (bf.mode === "perched") {
        bf.perchTimer += dt;
        const dogNear = (this.state === "run" || this.state === "trot" || this.state === "pounceButterfly") && Math.hypot(this.x - bf.x, (this.y - 16) - bf.y) < 42;
        if (dogNear) {
          this._startleButterfly(bf);
        } else if (bf.perchTimer >= bf.perchDur) {
          this._assignButterflyDestination(bf, false);
        }
      } else if (bf.mode === "playDance") {
        bf.t += dt * 3.4;
        const weaveX = bf.destX + Math.cos(bf.t * 1.4) * 16;
        const weaveY = bf.destY + Math.sin(bf.t * 2.2) * 8;
        bf.x += (weaveX - bf.x) * Math.min(1, dt * 6.5);
        bf.y += (weaveY - bf.y) * Math.min(1, dt * 6.5);
        bf.facing = this.x >= bf.x ? 1 : -1;
      } else if (bf.mode === "noseApproach") {
        const snout = this._getSnoutAnchor();
        bf.destX = snout.x;
        bf.destY = snout.y;
        bf.t += dt / Math.max(0.25, bf.dur);
        const u = Math.min(1, bf.t);
        const ease = 1 - Math.pow(1 - u, 3);
        bf.x = bf.startX + (bf.destX - bf.startX) * ease;
        bf.y = bf.startY + (bf.destY - bf.startY) * ease - Math.sin(u * Math.PI) * 14;
        bf.facing = -this.facing;
        if (u >= 1) {
          bf.mode = "nosePerched";
          bf.x = snout.x;
          bf.y = snout.y;
          bf.perchTimer = 0;
        }
      } else if (bf.mode === "nosePerched") {
        const snout = this._getSnoutAnchor();
        bf.x = snout.x;
        bf.y = snout.y;
        bf.facing = -this.facing;
        bf.perchTimer += dt;
      } else if (bf.mode === "twigCurious") {
        bf.t += dt;
        const u = Math.min(1, bf.t / 0.7);
        const orbitX = bf.destX + Math.cos(bf.t * 4.2) * 18;
        const orbitY = bf.destY + Math.sin(bf.t * 6.4) * 8;
        bf.x = bf.x + (orbitX - bf.x) * Math.min(1, dt * (u < 1 ? 6.0 : 4.5));
        bf.y = bf.y + (orbitY - bf.y) * Math.min(1, dt * (u < 1 ? 6.0 : 4.5));
        bf.facing = Math.sin(bf.t * 4.2) <= 0 ? 1 : -1;
        if (bf.t >= bf.dur) {
          this._assignButterflyDestination(bf, false);
        }
      }
    }
  }

  _updateTwig(dt) {
    if (!this.twig) return;
    const tw = this.twig;
    if (tw.phase === "tossed") {
      tw.t += dt / Math.max(0.16, tw.dur);
      const u = Math.min(1, tw.t);
      tw.x = tw.startX + (tw.landX - tw.startX) * u;
      tw.y = tw.startY + (tw.landY - tw.startY) * u - Math.sin(u * Math.PI) * 32;
      if (u >= 1) {
        tw.phase = "landed";
        tw.x = tw.landX;
        tw.y = tw.landY;
        this._spawnPollenMotes(tw.x, tw.y - 4, 4, "#fde047");
      }
    } else if (tw.phase === "carried") {
      const jaw = this._getMouthTwigAnchor();
      tw.x = jaw.x;
      tw.y = jaw.y;
    } else if (tw.phase === "delivered") {
      tw.holdTimer -= dt;
      if (tw.holdTimer <= 0) {
        this._spawnPollenMotes(tw.x, tw.y - 4, 3, "#fef08a");
        this.twig = null;
      }
    }
  }

  _updateProps(dt) {
    const movingDog = this.state === "trot" || this.state === "run" || this.state === "pounceButterfly" || (this.state === "fetchTwig" && (this.fetchPhase === "go" || this.fetchPhase === "return"));
    for (let i = 0; i < this.props.length; i++) {
      const p = this.props[i];
      if (p.cooldown > 0) p.cooldown = Math.max(0, p.cooldown - dt);
      if (p.glowBoost > 0) p.glowBoost = Math.max(0, p.glowBoost - dt * 0.85);

      if (movingDog && Math.abs(this.x - p.x) < 22 && Math.abs(this.y - p.y) < 18) {
        this._interactWithProp(p, (this.x <= p.x ? 1 : -1) * 7, this.state);
      }

      p.bendVel += (-24 * p.bend - 5.2 * p.bendVel) * dt;
      p.bend = Math.max(-3.5, Math.min(3.5, p.bend + p.bendVel * dt));
    }
  }

  _updateFireflies(dt, env) {
    const nightVis = Math.max(0, Math.min(1, env.nightGlow));
    for (let i = 0; i < this.fireflies.length; i++) {
      const ff = this.fireflies[i];
      ff.phase += dt * ff.speed * 1.45;
      ff.pulsePhase += dt * (2.2 + (i % 4) * 0.45);
      if (ff.boopFlash > 0) ff.boopFlash = Math.max(0, ff.boopFlash - dt * 1.6);

      const targetX = nightVis > 0.14
        ? ff.homeX + Math.cos(ff.phase) * ff.roamRx + Math.sin(ff.phase * 1.7) * 8
        : ff.homeX + Math.sin(ff.phase * 0.4) * 3;
      const targetY = nightVis > 0.14
        ? ff.homeY - ff.lift + Math.sin(ff.phase * 1.3) * ff.roamRy
        : ff.homeY - 2;

      const clampedX = Math.max(20, Math.min(this.docW - 20, targetX));
      const clampedY = Math.max(26, Math.min(this.docH - 14, targetY));
      ff.x += (clampedX - ff.x) * Math.min(1, dt * 3.8);
      ff.y += (clampedY - ff.y) * Math.min(1, dt * 3.8);
    }
  }

  // WHY: Integrates 60 Hz continuous sub-pixel 2D curved steering, stride bob, tilt, and squash-stretch with zero moonwalking on stationary poses.
  _updateCompanions(dt, env) {
    for (let i = 0; i < this.companions.length; i++) {
      const c = this.companions[i];
      c.timer += dt;

      if (LOCOMOTION_ANIMS.has(c.anim)) {
        const u = Math.min(1, c.timer / Math.max(0.45, c.duration));
        const ease = u * u * (3 - 2 * u);
        const inv = 1 - ease;
        const ctrl = c.ctrlPt || c.targetPt;
        let nx = inv * inv * c.startPt.x + 2 * inv * ease * ctrl.x + ease * ease * c.targetPt.x;
        let ny = inv * inv * c.startPt.y + 2 * inv * ease * ctrl.y + ease * ease * c.targetPt.y;

        if (c.anim === "chaseButterfly" && this.butterflies.length) {
          const bf = this.butterflies[c.id % this.butterflies.length];
          nx += Math.sin(this.animTime * 5.4 + c.id) * 3.5;
          if (Math.hypot(bf.x - c.x, bf.y - c.y) < 42) {
            this._startleButterfly(bf);
          }
        }

        if (this.portraitCircle) {
          const pc = this.portraitCircle;
          const minR = pc.r + 40;
          const pd = Math.hypot(nx - pc.cx, ny - pc.cy);
          if (pd < minR) {
            if (this.docW < 540) {
              ny = ny < pc.cy ? Math.max(46, pc.cy - minR) : Math.min(this.docH - 18, pc.cy + minR + 50);
            } else {
              const pa = pd > 1 ? Math.atan2(ny - pc.cy, nx - pc.cx) : 0.7;
              nx = Math.max(32, Math.min(this.docW - 32, pc.cx + Math.cos(pa) * minR));
              ny = Math.max(46, Math.min(this.docH - 18, pc.cy + Math.sin(pa) * minR));
            }
          }
        }

        if (Math.abs(nx - c.x) > 0.12) c.facing = nx >= c.x ? 1 : -1;
        c.x = nx;
        c.y = ny;

        if (c.anim === "hop") {
          const ph = this.animTime * 8.4 + c.id * 1.1;
          const s = Math.abs(Math.sin(ph));
          c.hopY = -s * 10.5 - Math.sin(u * Math.PI) * c.travelArc;
          c.tilt = Math.cos(ph) * 0.062 * c.facing;
          c.squashX = 1 - (s - 0.4) * 0.065;
          c.squashY = 1 + (s - 0.4) * 0.075;
        } else if (c.anim === "gallop" || c.anim === "chaseButterfly") {
          const ph = this.animTime * 12.6 + c.id * 0.9;
          c.hopY = -Math.abs(Math.sin(ph)) * 5.0;
          c.tilt = Math.sin(ph) * 0.052 * c.facing;
          c.squashX = 1 + Math.cos(ph * 2) * 0.038;
          c.squashY = 1 - Math.cos(ph * 2) * 0.032;
        } else {
          const freq = c.anim === "walk" || c.anim === "crouchStalk" ? 6.8 : 9.6;
          const ph = this.animTime * freq + c.id * 1.3;
          c.hopY = -Math.abs(Math.sin(ph)) * 2.2;
          c.tilt = Math.sin(ph) * 0.028 * c.facing;
          c.squashX = 1 + Math.cos(ph * 2) * 0.022;
          c.squashY = 1 - Math.cos(ph * 2) * 0.020;
        }
        c.shakeX = 0;

        if (u >= 1) {
          c.hopY = 0;
          c.tilt = 0;
          c.squashX = 1;
          c.squashY = 1;
          if (c.anim === "crouchStalk") {
            this._enterCompanionIdle(c, "pounce");
          } else {
            this._pickCompanionNextAction(c, env);
          }
        }
      } else {
        const u = Math.min(1, c.timer / Math.max(0.4, c.duration));
        const br = Math.sin(this.animTime * 2.6 + c.id * 0.95);
        c.shakeX = 0;
        c.squashX = 1 - br * 0.015;
        c.squashY = 1 + br * 0.021;
        c.tilt = c.anim === "perchSway" ? Math.sin(this.animTime * 2.2 + c.id) * 0.048 : br * 0.010;

        if (c.anim === "binky") {
          const lift = Math.sin(u * Math.PI);
          c.hopY = -lift * 17;
          c.squashX = 1 - lift * 0.05;
          c.squashY = 1 + lift * 0.07;
          if (u > 0.42 && u < 0.56) c.facing = -c.facing;
        } else if (c.anim === "pounce") {
          const lift = u < 0.7 ? Math.sin((u / 0.7) * Math.PI) : 0;
          c.hopY = -lift * 14;
          c.tilt = lift * 0.07 * c.facing;
        } else if (c.anim === "boopFirefly") {
          c.hopY = -Math.sin(u * Math.PI) * 10;
        } else if (c.anim === "happySpin") {
          c.facing = Math.floor(c.timer / 0.16) % 2 === 0 ? 1 : -1;
          c.hopY = -Math.abs(Math.sin(c.timer * 10)) * 5;
        } else if (c.anim === "shakeFur") {
          c.hopY = 0;
          c.shakeX = Math.sin(this.animTime * 38 + c.id) * 2.2;
          c.tilt = Math.sin(this.animTime * 34 + c.id) * 0.06;
        } else if (c.anim === "drink" && c.targetProp && Math.random() < dt * 1.8) {
          this._spawnWaterRipple(c.targetProp.x, c.targetProp.y - 4);
        } else {
          c.hopY = 0;
        }

        if (c.timer >= c.duration) {
          c.hopY = 0;
          c.shakeX = 0;
          c.tilt = 0;
          c.squashX = 1;
          c.squashY = 1;
          this._pickCompanionNextAction(c, env);
        }
      }
    }
  }

  update(dt) {
    this.animTime += dt;
    this.localCycleTime = (this.localCycleTime + dt) % DAY_NIGHT_CYCLE_SEC;
    this._datasetAccum += dt;
    this.shakeX = 0;
    const idleBr = Math.sin(this.animTime * 2.7);
    this.tilt = idleBr * 0.010;
    this.squashX = 1 - idleBr * 0.014;
    this.squashY = 1 + idleBr * 0.020;

    if (this.autoEmoteCooldown > 0) this.autoEmoteCooldown = Math.max(0, this.autoEmoteCooldown - dt);
    if (this.petEmoteGuard > 0) this.petEmoteGuard = Math.max(0, this.petEmoteGuard - dt);
    if (this.earPerkTimer > 0) this.earPerkTimer = Math.max(0, this.earPerkTimer - dt);
    if (this.hoverPauseTimer > 0) this.hoverPauseTimer = Math.max(0, this.hoverPauseTimer - dt);

    if (this.emote) {
      this.emote.age += dt;
      if (this.emote.age >= this.emote.duration) {
        this.emote = null;
      }
    }

    this.blinkTimer -= dt;
    if (this.blinkTimer <= -0.16) {
      this.blinkTimer = 2.0 + Math.random() * 2.4;
    }

    if (this.state === "trot" || this.state === "run") {
      if (this.hoverPauseTimer > 0) {
        this.hopY = 0;
      } else {
        this.travelT += dt / Math.max(0.4, this.travelDur);
        const u = Math.min(1, this.travelT);
        const ramp = 0.08;
        let smooth;
        if (u < ramp) {
          smooth = (u * u) / (2 * ramp * (1 - ramp));
        } else if (u > 1 - ramp) {
          const d = 1 - u;
          smooth = 1 - (d * d) / (2 * ramp * (1 - ramp));
        } else {
          smooth = (u - 0.5 * ramp) / (1 - ramp);
        }
        const inv = 1 - smooth;
        const ctrl = this.ctrlPt || this.targetPt;
        let nx = inv * inv * this.startPt.x + 2 * inv * smooth * ctrl.x + smooth * smooth * this.targetPt.x;
        let ny = inv * inv * this.startPt.y + 2 * inv * smooth * ctrl.y + smooth * smooth * this.targetPt.y;
        if (this.portraitCircle) {
          const pc = this.portraitCircle;
          const minR = pc.r + 44;
          const pd = Math.hypot(nx - pc.cx, ny - pc.cy);
          if (pd < minR) {
            if (this.docW < 540) {
              ny = ny < pc.cy ? Math.max(46, pc.cy - minR) : Math.min(this.docH - 18, pc.cy + minR + 52);
            } else {
              const pa = pd > 1 ? Math.atan2(ny - pc.cy, nx - pc.cx) : 0.7;
              nx = Math.max(32, Math.min(this.docW - 32, pc.cx + Math.cos(pa) * minR));
              ny = Math.max(46, Math.min(this.docH - 18, pc.cy + Math.sin(pa) * minR));
            }
          }
        }
        const vx = nx - this.x;
        if (Math.abs(vx) > 0.14) {
          this.facing = vx >= 0 ? 1 : -1;
        }
        this.x = nx;
        this.y = ny;

        const isRun = this.state === "run";
        const ph = this.animTime * (isRun ? 13.4 : 9.8);
        const strideBounce = Math.abs(Math.sin(ph)) * (isRun ? 4.4 : 2.2);
        this.hopY = -strideBounce;
        this.tilt = Math.sin(ph) * (isRun ? 0.052 : 0.028) * this.facing;
        this.squashX = 1 + Math.cos(ph * 2) * (isRun ? 0.038 : 0.022);
        this.squashY = 1 - Math.cos(ph * 2) * (isRun ? 0.032 : 0.020);

        this.stepAccum += dt;
        const puffStep = isRun ? 0.12 : 0.18;
        if (this.stepAccum >= puffStep) {
          this.stepAccum = 0;
          this._spawnPawPuff();
        }

        if (u >= 1) {
          this.hopY = 0;
          this.tilt = 0;
          this.squashX = 1;
          this.squashY = 1;
          this._chooseIdleBehavior();
        }
      }
    } else if (this.state === "sniffFlora") {
      this.stateTimer += dt;
      const sneezePhase = this.sniffWillSneeze && this.stateTimer >= this.stateDuration - 0.58;
      if (!sneezePhase) {
        if (this.activeFlora) {
          this.activeFlora.bendVel += Math.sin(this.animTime * 12) * 18 * dt;
        }
        if (Math.random() < dt * 3.2) {
          this._spawnPollenMotes(this.x + this.facing * 24, this.y - 10, 1);
        }
      } else if (!this.sneezeTriggered) {
        this.sneezeTriggered = true;
        this._spawnPollenMotes(this.x + this.facing * 26, this.y - 14, 4, "#fff8e3");
        if (this.activeFlora) {
          this._rustleFloraCluster(this.activeFlora, this.facing * 9, false);
        }
      }
      if (sneezePhase && this.stateTimer >= this.stateDuration - 0.34 && this.stateTimer < this.stateDuration - 0.16) {
        this.hopY = -3;
      } else {
        this.hopY = 0;
      }

      if (this.stateTimer >= this.stateDuration) {
        this.activeFlora = null;
        this.hopY = 0;
        this._pickNextWaypoint();
      }
    } else if (this.state === "stalkButterfly") {
      this.stateTimer += dt;
      const creep = this.facing * 14 * dt;
      this.x = Math.max(38, Math.min(this.docW - 38, this.x + creep));
      const bf = this.activeButterfly;
      if (bf) {
        const dy = (bf.y - this.y) * dt * 0.8;
        this.y = Math.max(46, Math.min(this.docH - 18, this.y + dy));
      }
      if (this.stateTimer >= this.stateDuration) {
        this._startPounceButterfly();
      }
    } else if (this.state === "pounceButterfly") {
      this.stateTimer += dt;
      const u = Math.min(1, this.stateTimer / Math.max(0.3, this.stateDuration));
      this.x = this.pounceStartX + (this.pounceTargetX - this.pounceStartX) * u;
      if (u < 0.72) {
        const lu = u / 0.72;
        this.hopY = -Math.sin(lu * Math.PI) * 18;
      } else {
        this.hopY = 0;
      }
      if (this.activeButterfly && u > 0.25 && this.activeButterfly.mode === "playDance") {
        this._spawnPollenMotes(this.activeButterfly.x, this.activeButterfly.y, 3, "#fde047");
        this._assignButterflyDestination(this.activeButterfly, true);
        this.activeButterfly = null;
      }
      if (u >= 1) {
        this.hopY = 0;
        this._releaseInteractiveButterfly();
        this._maybeShowEmote("sparkle", false);
        this._pickNextWaypoint(true);
      }
    } else if (this.state === "butterflyNosePerch") {
      this.stateTimer += dt;
      if (this.stateTimer >= this.stateDuration - 0.35 && this.activeButterfly) {
        this._maybeShowEmote("heart", false);
        this._releaseInteractiveButterfly();
      }
      if (this.stateTimer >= this.stateDuration) {
        this._releaseInteractiveButterfly();
        this._pickNextWaypoint();
      }
    } else if (this.state === "bellyRoll") {
      this.stateTimer += dt;
      if (Math.random() < dt * 2.2) {
        this._spawnPollenMotes(this.x + (Math.random() - 0.5) * 20, this.y - 16, 1, "#fef08a");
      }
      if (this.stateTimer >= this.stateDuration) {
        this._pickNextWaypoint();
      }
    } else if (this.state === "scratchEar") {
      this.stateTimer += dt;
      if (this.stateTimer >= this.stateDuration) {
        this._pickNextWaypoint(true);
      }
    } else if (this.state === "yawnStretch") {
      this.stateTimer += dt;
      if (this.stateTimer >= this.stateDuration) {
        this._pickNextWaypoint();
      }
    } else if (this.state === "sit") {
      this.stateTimer += dt;
      if (this.stateTimer >= this.stateDuration) {
        this._pickNextWaypoint(true);
      }
    } else if (this.state === "rest") {
      this.stateTimer += dt;
      if (this.stateTimer >= this.stateDuration) {
        this._enterState("yawnStretch", 1.35);
      }
    } else if (this.state === "nap") {
      this.stateTimer += dt;
      if (Math.random() < dt * 1.6 && this.napStars.length < 4) {
        this.napStars.push({
          x: this.x + this.facing * 8 + (Math.random() - 0.5) * 14,
          y: this.y - 26,
          vy: -9 - Math.random() * 5,
          drift: Math.random() * Math.PI * 2,
          life: 1.0,
          color: Math.random() < 0.6 ? "#fde047" : "#7dd3fc"
        });
      }
      if (this.stateTimer >= this.stateDuration) {
        this.napStars.length = 0;
        this._enterState("yawnStretch", 1.45);
      }
    } else if (this.state === "petBowHop") {
      this.stateTimer += dt;
      if (this.stateTimer >= 0.30 && this.stateTimer < 0.86) {
        const u = (this.stateTimer - 0.30) / 0.56;
        this.hopY = -Math.sin(u * Math.PI) * 15;
      } else {
        this.hopY = 0;
      }
      if (this.stateTimer >= this.stateDuration) {
        this.hopY = 0;
        this._enterState("sit", 1.4);
      }
    } else if (this.state === "petBellyRoll") {
      this.stateTimer += dt;
      if (this.stateTimer >= this.stateDuration) {
        this._enterState("sit", 1.4);
      }
    } else if (this.state === "petTailSpin") {
      this.stateTimer += dt;
      const spinStep = Math.floor(this.stateTimer / 0.18);
      this.facing = spinStep % 2 === 0 ? 1 : -1;
      this.hopY = -Math.abs(Math.sin(this.stateTimer * 9.5)) * 6;
      if (this.stateTimer >= this.stateDuration) {
        this.hopY = 0;
        this.facing = 1;
        this._enterState("sit", 1.4);
      }
    } else if (this.state === "fetchTwig") {
      this.fetchTimer += dt;
      if (this.fetchPhase === "perk") {
        if (this.fetchTimer >= 0.24) {
          this.fetchPhase = "go";
          this.fetchTimer = 0;
        }
      } else if (this.fetchPhase === "go") {
        const u = Math.min(1, this.fetchTimer / Math.max(0.35, this.fetchMoveDur));
        const ease = u * u * (3 - 2 * u);
        const nx = this.fetchStartPt.x + (this.fetchGoalPt.x - this.fetchStartPt.x) * ease;
        const ny = this.fetchStartPt.y + (this.fetchGoalPt.y - this.fetchStartPt.y) * ease;
        if (Math.abs(nx - this.x) > 0.2) this.facing = nx >= this.x ? 1 : -1;
        this.x = nx;
        this.y = ny;
        this.hopY = -Math.abs(Math.sin(this.animTime * 13)) * 2.8;
        this.stepAccum += dt;
        if (this.stepAccum >= 0.14) {
          this.stepAccum = 0;
          this._spawnPawPuff();
        }
        if (u >= 1) {
          this.hopY = 0;
          this.fetchPhase = "pickup";
          this.fetchTimer = 0;
          if (this.twig) {
            this.twig.phase = "carried";
          }
          this._burstGoldenSparks(6);
        }
      } else if (this.fetchPhase === "pickup") {
        if (this.fetchTimer >= 0.28) {
          this.fetchPhase = "return";
          this.fetchTimer = 0;
          this.fetchStartPt = { x: this.x, y: this.y };
          const retDist = Math.hypot(this.fetchReturnPt.x - this.x, this.fetchReturnPt.y - this.y);
          this.fetchMoveDur = Math.max(0.55, Math.min(1.45, retDist / 118));
        }
      } else if (this.fetchPhase === "return") {
        const u = Math.min(1, this.fetchTimer / Math.max(0.35, this.fetchMoveDur));
        const ease = u * u * (3 - 2 * u);
        const nx = this.fetchStartPt.x + (this.fetchReturnPt.x - this.fetchStartPt.x) * ease;
        const ny = this.fetchStartPt.y + (this.fetchReturnPt.y - this.fetchStartPt.y) * ease;
        if (Math.abs(nx - this.x) > 0.2) this.facing = nx >= this.x ? 1 : -1;
        this.x = nx;
        this.y = ny;
        this.stepAccum += dt;
        if (this.stepAccum >= 0.18) {
          this.stepAccum = 0;
          this._spawnPawPuff();
        }
        if (u >= 1) {
          this.fetchPhase = "drop";
          this.fetchTimer = 0;
          if (this.twig) {
            this.twig.phase = "delivered";
            this.twig.x = Math.max(28, Math.min(this.docW - 28, this.x + this.facing * 20));
            this.twig.y = this.y - 2;
            this.twig.holdTimer = 2.4;
          }
          this._maybeShowEmote("heart", true);
          this._burstGoldenSparks(8);
        }
      } else if (this.fetchPhase === "drop") {
        if (this.fetchTimer >= 0.55) {
          this.fetchPhase = "none";
          this._enterState("sit", 1.8);
        }
      }
    } else if (this.state === "binky") {
      this.stateTimer += dt;
      const u = Math.min(1, this.stateTimer / Math.max(0.3, this.stateDuration));
      this.hopY = -Math.sin(u * Math.PI) * 18;
      if (this.stateTimer >= this.stateDuration) {
        this.hopY = 0;
        this._pickNextWaypoint(true);
      }
    } else if (this.state === "boopFirefly") {
      this.stateTimer += dt;
      const u = Math.min(1, this.stateTimer / Math.max(0.3, this.stateDuration));
      this.hopY = -Math.sin(u * Math.PI) * 12;
      if (this.stateTimer >= this.stateDuration) {
        this.hopY = 0;
        this._pickNextWaypoint();
      }
    } else if (this.state === "shakeFur") {
      this.stateTimer += dt;
      this.shakeX = Math.sin(this.animTime * 40) * 2;
      if (this.stateTimer >= this.stateDuration) {
        this.shakeX = 0;
        this._pickNextWaypoint();
      }
    } else if (this.state === "happySpin") {
      this.stateTimer += dt;
      this.facing = Math.floor(this.stateTimer / 0.16) % 2 === 0 ? 1 : -1;
      this.hopY = -Math.abs(Math.sin(this.stateTimer * 10)) * 6;
      if (this.stateTimer >= this.stateDuration) {
        this.hopY = 0;
        this._pickNextWaypoint();
      }
    } else {
      this.stateTimer += dt;
      if (this.stateTimer >= this.stateDuration) {
        this.hopY = 0;
        this._pickNextWaypoint(true);
      }
    }

    const env = this._currentEnv();
    this._updateFlora(dt);
    this._updateProps(dt);
    this._updateButterflies(dt);
    this._updateFireflies(dt, env);
    this._updateCompanions(dt, env);
    this._updateTwig(dt);

    for (let i = this.waterRipples.length - 1; i >= 0; i--) {
      const rp = this.waterRipples[i];
      rp.r += dt * 16;
      rp.life -= dt * 1.15;
      if (rp.life <= 0.02) this.waterRipples.splice(i, 1);
    }

    for (let i = this.dandelionSeeds.length - 1; i >= 0; i--) {
      const sd = this.dandelionSeeds[i];
      sd.phase += dt * 3.1;
      sd.x += (sd.vx + Math.sin(sd.phase) * 9) * dt;
      sd.y += sd.vy * dt;
      sd.life -= dt * 0.55;
      if (sd.life <= 0.02) this.dandelionSeeds.splice(i, 1);
    }

    for (let i = this.dewDrops.length - 1; i >= 0; i--) {
      const d = this.dewDrops[i];
      d.x += d.vx * dt;
      d.y += d.vy * dt;
      d.vy += 58 * dt;
      d.life -= dt * 1.65;
      if (d.life <= 0.02) this.dewDrops.splice(i, 1);
    }

    for (let i = this.pawPuffs.length - 1; i >= 0; i--) {
      const p = this.pawPuffs[i];
      p.swirl += dt * 5.2;
      p.x += (p.vx + Math.cos(p.swirl) * 8) * dt;
      p.y += (p.vy + Math.sin(p.swirl) * 4) * dt;
      p.life -= dt * 1.55;
      if (p.life <= 0.02) this.pawPuffs.splice(i, 1);
    }

    for (let i = this.pollenMotes.length - 1; i >= 0; i--) {
      const m = this.pollenMotes[i];
      m.phase += dt * 3.4;
      m.x += (m.vx + Math.sin(m.phase) * 7) * dt;
      m.y += m.vy * dt;
      m.life -= dt * 0.92;
      if (m.life <= 0.02) this.pollenMotes.splice(i, 1);
    }

    for (let i = this.sparks.length - 1; i >= 0; i--) {
      const s = this.sparks[i];
      s.x += s.vx * dt;
      s.y += s.vy * dt;
      s.vy += 42 * dt;
      s.life -= dt * 1.35;
      if (s.life <= 0.02) this.sparks.splice(i, 1);
    }

    for (let i = this.napStars.length - 1; i >= 0; i--) {
      const st = this.napStars[i];
      st.drift += dt * 3.0;
      st.x += Math.sin(st.drift) * 7 * dt;
      st.y += st.vy * dt;
      st.life -= dt * 0.88;
      if (st.life <= 0.02) this.napStars.splice(i, 1);
    }

    this._syncHitbox();
  }

  _selectFrameKey() {
    if (this.reducedMotion) {
      if (this.state === "petBellyRoll") return "bellyRoll0";
      if (this.state === "petTailSpin") return "sitEar";
      if (this.state === "petBowHop") return "sitTilt";
      return "sit0";
    }
    if (this.state === "run" || this.state === "gallop") {
      if (this.hoverPauseTimer > 0) return "sitEar";
      if (this.hopY < -8) return "hop";
      return Math.floor(this.animTime * 13.0) % 2 === 0 ? "run0" : "run1";
    }
    if (this.state === "trot" || this.state === "walk") {
      if (this.hoverPauseTimer > 0) return "sitEar";
      if (this.hopY < -5) return "hop";
      const idx = Math.floor(this.animTime * (this.state === "walk" ? 6.0 : 9.5)) % 4;
      return `trot${idx}`;
    }
    if (this.state === "binky" || this.state === "boopFirefly" || this.state === "hop") {
      return this.hopY < -4 ? "hop" : "bow";
    }
    if (this.state === "drink" || this.state === "graze") {
      return Math.floor(this.animTime * 5.2) % 2 === 0 ? "sniffLow0" : "sniffLow1";
    }
    if (this.state === "groom") {
      return Math.floor(this.animTime * 6.5) % 2 === 0 ? "scratchEar0" : "sitTilt";
    }
    if (this.state === "stargazeMeteor") {
      return Math.floor(this.animTime * 3.0) % 2 === 0 ? "sitTilt" : "sitEar";
    }
    if (this.state === "shakeFur") {
      return Math.floor(this.animTime * 16.0) % 2 === 0 ? "sneeze0" : "trot1";
    }
    if (this.state === "sunBask") {
      return Math.floor(this.animTime * 1.5) % 2 === 0 ? "rest0" : "rest1";
    }
    if (this.state === "happySpin") {
      const sub = Math.floor(this.stateTimer / 0.14) % 3;
      if (sub === 0) return "bow";
      if (sub === 1) return "hop";
      return "trot1";
    }
    if (this.state === "sniffFlora" || this.state === "sniff") {
      if (this.sniffWillSneeze && this.stateTimer >= this.stateDuration - 0.58) {
        return this.stateTimer < this.stateDuration - 0.34 ? "sneeze0" : "sneeze1";
      }
      return Math.floor(this.animTime * 5.8) % 2 === 0 ? "sniffLow0" : "sniffLow1";
    }
    if (this.state === "stalkButterfly" || this.state === "crouchStalk") {
      return Math.floor(this.animTime * 8.5) % 2 === 0 ? "stalk0" : "stalk1";
    }
    if (this.state === "pounceButterfly" || this.state === "pounce") {
      const u = this.stateTimer / Math.max(0.3, this.stateDuration);
      if (u < 0.72) {
        return Math.floor(this.animTime * 9.0) % 2 === 0 ? "pounce0" : "pounce1";
      }
      return "sitEar";
    }
    if (this.state === "butterflyNosePerch") {
      if (this.stateTimer > this.stateDuration - 0.35) return "sit1";
      return Math.floor(this.animTime * 2.4) % 2 === 0 ? "nosePerch0" : "nosePerch1";
    }
    if (this.state === "bellyRoll" || this.state === "petBellyRoll") {
      const seq = ["bellyRoll0", "bellyRoll1", "bellyRoll2", "bellyRoll1"];
      return seq[Math.floor(this.animTime * 6.5) % seq.length];
    }
    if (this.state === "scratchEar") {
      return Math.floor(this.animTime * 9.5) % 2 === 0 ? "scratchEar0" : "scratchEar1";
    }
    if (this.state === "yawnStretch" || this.state === "yawn" || this.state === "stretch") {
      const u = this.stateTimer / Math.max(0.4, this.stateDuration);
      if (u < 0.22) return "bow";
      if (u < 0.74) return "yawnStretch0";
      if (u < 0.90) return "yawnStretch1";
      return "sitEar";
    }
    if (this.state === "fetchTwig") {
      if (this.fetchPhase === "perk") return "sitEar";
      if (this.fetchPhase === "go") {
        return Math.floor(this.animTime * 13.0) % 2 === 0 ? "run0" : "run1";
      }
      if (this.fetchPhase === "pickup") return "sniffLow0";
      if (this.fetchPhase === "return") {
        return `trot${Math.floor(this.animTime * 10.0) % 4}`;
      }
      return this.fetchTimer < 0.22 ? "sniffLow1" : "sit1";
    }
    if (this.state === "rest") {
      if (this.earPerkTimer > 0) return "rest0";
      return Math.floor(this.animTime * 1.4) % 2 === 0 ? "rest0" : "rest1";
    }
    if (this.state === "nap" || this.state === "sleepCurl") {
      return Math.floor(this.animTime * 1.3) % 2 === 0 ? "nap0" : "nap1";
    }
    if (this.state === "petBowHop") {
      if (this.stateTimer < 0.30) return "bow";
      if (this.stateTimer < 0.86) return "hop";
      return Math.floor(this.animTime * 10.0) % 2 === 0 ? "sit1" : "sitTilt";
    }
    if (this.state === "petTailSpin") {
      const sub = Math.floor(this.stateTimer / 0.14) % 3;
      if (sub === 0) return "bow";
      if (sub === 1) return "hop";
      return "trot1";
    }
    if (this.earPerkTimer > 0) {
      return Math.floor(this.animTime * 4.0) % 2 === 0 ? "sitEar" : "sitTilt";
    }
    if (this.blinkTimer <= 0) return "sitBlink";
    if (this.stateTimer > 0.85 && this.stateTimer < 1.85) return "sitTilt";
    return Math.floor(this.animTime * 4.5) % 2 === 0 ? "sit0" : "sit1";
  }

  _selectCompanionFrame(comp) {
    if (this.reducedMotion) {
      return comp.rhythm === "nocturnal" ? "idle0" : "idle0";
    }
    const t = this.animTime + comp.id * 0.7;
    const a = comp.anim;
    if (a === "walk") return Math.floor(t * 5.8) % 2 === 0 ? "move0" : "move1";
    if (a === "trot") return Math.floor(t * 9.2) % 2 === 0 ? "move0" : "move1";
    if (a === "gallop" || a === "chaseButterfly") {
      return comp.hopY < -3 ? "leap" : (Math.floor(t * 13.0) % 2 === 0 ? "move0" : "move1");
    }
    if (a === "hop" || a === "binky" || a === "boopFirefly" || a === "pounce") {
      return comp.hopY < -3 ? "leap" : "low";
    }
    if (a === "crouchStalk" || a === "graze" || a === "drink" || a === "sniff") {
      return Math.floor(t * 4.6) % 2 === 0 ? "low" : "idle1";
    }
    if (a === "sleepCurl") return "sleep";
    if (a === "sunBask") return Math.floor(t * 1.4) % 2 === 0 ? "sleep" : "idle0";
    if (a === "stretch") return comp.timer < comp.duration * 0.55 ? "low" : "idle1";
    if (a === "yawn") return comp.timer < comp.duration * 0.6 ? "idle1" : "sleep";
    if (a === "bellyRoll") return Math.floor(t * 5.2) % 2 === 0 ? "sleep" : "low";
    if (a === "groom" || a === "scratchEar") return Math.floor(t * 8.4) % 2 === 0 ? "low" : "idle1";
    if (a === "happySpin" || a === "shakeFur") return Math.floor(t * 11.0) % 2 === 0 ? "move0" : "idle1";
    if (a === "stargazeMeteor" || a === "earPerk") return "idle1";
    if (a === "perchSway") return Math.floor(t * 2.2) % 2 === 0 ? "idle0" : "idle1";
    return Math.floor(t * 4.2) % 2 === 0 ? "idle0" : "idle1";
  }

  _getGlowHaloSprite(hex) {
    if (!this._glowHaloCache) this._glowHaloCache = new Map();
    const hit = this._glowHaloCache.get(hex);
    if (hit) return hit;
    const size = 24;
    const c = document.createElement("canvas");
    c.width = size;
    c.height = size;
    const gctx = c.getContext("2d");
    const half = (size - 1) * 0.5;
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const d = Math.hypot(x - half, y - half) / half;
        if (d > 1) continue;
        const a = d < 0.35 ? 0.85 : (d < 0.68 ? 0.45 : 0.18);
        gctx.fillStyle = hex;
        gctx.globalAlpha = a;
        gctx.fillRect(x, y, 1, 1);
      }
    }
    this._glowHaloCache.set(hex, c);
    return c;
  }

  _drawProps(ctx, env, minY = -Infinity, maxY = Infinity) {
    const nightGlow = env.nightGlow;
    for (let i = 0; i < this.props.length; i++) {
      const p = this.props[i];
      if (p.y < minY || p.y > maxY) continue;
      const sp = this.propSprites[p.id];
      if (!sp) continue;

      const drawW = sp.width * PIXEL_SCALE;
      const drawH = sp.height * PIXEL_SCALE;
      const breeze = this.reducedMotion ? 0 : (p.category === "flora" || p.category === "dandelion" || p.category === "chime"
        ? Math.sin(this.animTime * 1.8 + p.phase) * 1.2
        : 0);
      const swayPx = Math.round((p.bend * 1.5 + breeze) / PIXEL_SCALE) * PIXEL_SCALE;
      const px = Math.round((p.x - drawW * 0.5) / PIXEL_SCALE) * PIXEL_SCALE + swayPx;
      const py = Math.round((p.y - drawH + 4) / PIXEL_SCALE) * PIXEL_SCALE;

      if (p.glowColor && (nightGlow > 0.14 || p.glowBoost > 0.05)) {
        const gAlpha = Math.min(0.54, nightGlow * 0.40 + p.glowBoost * 0.26);
        const halo = this._getGlowHaloSprite(p.glowColor);
        const gr = p.glowRadius;
        ctx.globalAlpha = gAlpha;
        ctx.drawImage(halo, Math.round(px + drawW * 0.5 - gr), Math.round(py + drawH * 0.42 - gr * 0.78), gr * 2, Math.round(gr * 1.6));
      }

      ctx.fillStyle = "#040814";
      ctx.globalAlpha = 0.32;
      ctx.fillRect(px + PIXEL_SCALE * 2, Math.round(p.y / PIXEL_SCALE) * PIXEL_SCALE, drawW - PIXEL_SCALE * 4, PIXEL_SCALE * 2);

      const useNightSprite = sp.night && (nightGlow > 0.35 || p.glowBoost > 0.2);
      ctx.globalAlpha = 1;
      ctx.drawImage(useNightSprite ? sp.night : sp.day, px, py, drawW, drawH);
    }
  }

  _drawWaterRipples(ctx) {
    for (let i = 0; i < this.waterRipples.length; i++) {
      const rp = this.waterRipples[i];
      const rx = Math.round(rp.x / PIXEL_SCALE) * PIXEL_SCALE;
      const ry = Math.round(rp.y / PIXEL_SCALE) * PIXEL_SCALE;
      const w = Math.round(rp.r) * PIXEL_SCALE;
      const h = Math.max(PIXEL_SCALE * 2, Math.round(rp.r * 0.38) * PIXEL_SCALE);
      ctx.globalAlpha = Math.max(0, rp.life * 0.78);
      ctx.strokeStyle = "#bae6fd";
      ctx.lineWidth = PIXEL_SCALE;
      ctx.strokeRect(rx - w * 0.5, ry - h * 0.5, w, h);
    }
    ctx.globalAlpha = 1;
  }

  _drawAnimalBody(ctx, sprite, cx, groundY, drawW, drawH, hopY, tilt, sx, sy) {
    ctx.save();
    ctx.translate(cx, groundY + 5 + hopY);
    if (!this.reducedMotion) {
      if (tilt) ctx.rotate(tilt);
      if (sx !== 1 || sy !== 1) ctx.scale(sx, sy);
    }
    ctx.imageSmoothingEnabled = false;
    ctx.globalAlpha = 1;
    ctx.drawImage(sprite, -drawW * 0.5, -drawH, drawW, drawH);
    ctx.restore();
  }

  _drawCompanionRange(ctx, minY, maxY) {
    for (let i = 0; i < this.companions.length; i++) {
      const c = this.companions[i];
      if (c.y < minY || c.y >= maxY) continue;
      const bank = this.companionSprites[c.species];
      if (!bank) continue;

      const drawW = bank.width * ANIMAL_SCALE;
      const drawH = bank.height * ANIMAL_SCALE;
      const swayX = (!this.reducedMotion && c.anim === "perchSway") ? Math.sin(this.animTime * 2.2 + c.id) * 1.8 : 0;
      const cx = c.x + c.shakeX + swayX;
      const topY = c.y - drawH + 5 + c.hopY;

      const hopRatio = Math.min(1, Math.abs(c.hopY) / 16);
      const shRx = Math.max(7, drawW * 0.34 * (1 - hopRatio * 0.30));
      const shRy = Math.max(2.6, PIXEL_SCALE * 1.45 * (1 - hopRatio * 0.25));

      ctx.fillStyle = "#040814";
      ctx.globalAlpha = 0.38 * (1 - hopRatio * 0.35);
      ctx.beginPath();
      ctx.ellipse(cx, c.y, shRx, shRy, 0, 0, Math.PI * 2);
      ctx.fill();

      const dirSet = c.facing >= 0 ? bank.right : bank.left;
      const fk = this._selectCompanionFrame(c);
      const sprite = dirSet[fk] || dirSet.idle0;
      this._drawAnimalBody(ctx, sprite, cx, c.y, drawW, drawH, c.hopY, c.tilt || 0, c.squashX || 1, c.squashY || 1);

      if (!this.reducedMotion && c.anim === "stargazeMeteor") {
        this._drawPixelStar(ctx, cx + c.facing * 10, topY - 4, "#fde047", 0.90, true);
      } else if (!this.reducedMotion && c.anim === "sleepCurl" && Math.floor(this.animTime * 2 + c.id) % 2 === 0) {
        this._drawPixelStar(ctx, cx + c.facing * 10, topY - 2, "#7dd3fc", 0.72, false);
      }
    }
  }

  _drawFireflies(ctx, env, minY = -Infinity, maxY = Infinity) {
    const nightVis = this.reducedMotion ? 0.85 : Math.max(0.05, env.nightGlow);
    for (let i = 0; i < this.fireflies.length; i++) {
      const ff = this.fireflies[i];
      if (ff.y < minY || ff.y > maxY) continue;
      const pulse = this.reducedMotion ? 0.78 : (0.38 + 0.62 * (0.5 + 0.5 * Math.sin(ff.pulsePhase)));
      const alpha = Math.min(1, nightVis * pulse + ff.boopFlash * 0.85);
      if (alpha <= 0.06) continue;

      const fx = ff.x;
      const fy = ff.y;

      ctx.fillStyle = ff.color;
      ctx.globalAlpha = alpha * 0.28;
      ctx.fillRect(fx - PIXEL_SCALE * 2, fy - PIXEL_SCALE * 2, PIXEL_SCALE * 5, PIXEL_SCALE * 5);

      ctx.globalAlpha = alpha * 0.62;
      ctx.fillRect(fx - PIXEL_SCALE, fy - PIXEL_SCALE, PIXEL_SCALE * 3, PIXEL_SCALE * 3);

      ctx.fillStyle = ff.boopFlash > 0.2 ? "#ffffff" : "#fef9c3";
      ctx.globalAlpha = Math.min(1, alpha * 1.1);
      ctx.fillRect(fx, fy, PIXEL_SCALE, PIXEL_SCALE);
    }
    ctx.globalAlpha = 1;
  }

  _drawSeedsAndDew(ctx) {
    for (let i = 0; i < this.dandelionSeeds.length; i++) {
      const sd = this.dandelionSeeds[i];
      ctx.globalAlpha = Math.max(0, Math.min(1, sd.life * 0.9));
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(sd.x - PIXEL_SCALE, sd.y - PIXEL_SCALE, PIXEL_SCALE * 3, PIXEL_SCALE);
      ctx.fillStyle = "#dfd2b5";
      ctx.fillRect(sd.x, sd.y, PIXEL_SCALE, PIXEL_SCALE * 2);
    }

    for (let i = 0; i < this.dewDrops.length; i++) {
      const d = this.dewDrops[i];
      ctx.globalAlpha = Math.max(0, Math.min(1, d.life * 0.92));
      ctx.fillStyle = d.color;
      ctx.fillRect(d.x, d.y, PIXEL_SCALE, PIXEL_SCALE);
    }
    ctx.globalAlpha = 1;
  }

  _selectButterflyFrame(bf) {
    if (this.reducedMotion) return "folded";
    if (bf.mode === "perched" || bf.mode === "nosePerched") {
      const pulse = (this.animTime * 0.75 + bf.id * 0.9) % 2.4;
      return (pulse > 1.85 && pulse < 2.12) ? "mid" : "folded";
    }
    const seq = ["open", "mid", "folded", "mid"];
    return seq[Math.floor(bf.flapPhase) % seq.length];
  }

  _drawFloraClusters(ctx, minY = -Infinity, maxY = Infinity) {
    for (let i = 0; i < this.floraClusters.length; i++) {
      const cl = this.floraClusters[i];
      if (cl.y < minY || cl.y > maxY) continue;
      const baseX = Math.round(cl.x / PIXEL_SCALE) * PIXEL_SCALE;
      const baseY = Math.round(cl.y / PIXEL_SCALE) * PIXEL_SCALE;
      const sway = this.reducedMotion ? 0 : (cl.bend * 1.1 + Math.sin(this.animTime * 1.6 + cl.x * 0.012) * 1.1);

      ctx.fillStyle = "#040814";
      ctx.globalAlpha = 0.36;
      ctx.fillRect(baseX - 8 * PIXEL_SCALE, baseY - PIXEL_SCALE, 16 * PIXEL_SCALE, PIXEL_SCALE * 2);

      ctx.globalAlpha = 1;
      ctx.drawImage(
        cl.sprite,
        Math.round(baseX - 12 * PIXEL_SCALE + sway),
        baseY - 16 * PIXEL_SCALE,
        cl.spW * PIXEL_SCALE,
        cl.spH * PIXEL_SCALE
      );
    }
  }

  _drawTwig(ctx) {
    if (!this.twig) return;
    const tw = this.twig;
    const sprite = this.facing >= 0 ? this.twigSpriteRight : this.twigSpriteLeft;
    const w = TWIG_W * ANIMAL_SCALE;
    const h = TWIG_H * ANIMAL_SCALE;
    const tx = tw.x - w * 0.5;
    const ty = tw.y - h * 0.5;

    if (tw.phase === "landed" || tw.phase === "delivered") {
      ctx.fillStyle = "#040814";
      ctx.globalAlpha = 0.36;
      ctx.fillRect(tx + PIXEL_SCALE, ty + h - PIXEL_SCALE, w - PIXEL_SCALE * 2, PIXEL_SCALE * 2);
      const glow = this.reducedMotion ? 0.55 : (0.45 + 0.25 * Math.sin(this.animTime * 6.0));
      this._drawPixelStar(ctx, tx + w - PIXEL_SCALE * 2, ty - PIXEL_SCALE, "#fde047", glow, false);
    }
    ctx.globalAlpha = 1;
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(sprite, tx, ty, w, h);
  }

  _drawButterflies(ctx, minY = -Infinity, maxY = Infinity) {
    const drawW = BF_W * BF_SCALE;
    const drawH = BF_H * BF_SCALE;
    for (let i = 0; i < this.butterflies.length; i++) {
      const bf = this.butterflies[i];
      if (bf.y < minY || bf.y > maxY) continue;
      const spBank = this.butterflySprites[bf.species];
      if (!spBank) continue;
      const dirBank = bf.facing >= 0 ? spBank.right : spBank.left;
      const fKey = this._selectButterflyFrame(bf);
      const sprite = dirBank[fKey] || dirBank.open;

      const perched = this.reducedMotion || bf.mode === "perched" || bf.mode === "nosePerched";
      const bob = perched ? 0 : Math.sin(bf.flapPhase) * 2.2;
      const bx = bf.x - drawW * 0.5;
      const by = bf.y - drawH + 4 + bob;

      if (!perched) {
        ctx.globalAlpha = 0.20;
        ctx.fillStyle = bf.species === "morpho" ? "#7dd3fc" : "#fde047";
        ctx.fillRect(bx + 4 * BF_SCALE, by + 3 * BF_SCALE, 5 * BF_SCALE, 4 * BF_SCALE);
      }

      ctx.save();
      ctx.translate(bf.x, bf.y + bob);
      if (!perched) {
        ctx.rotate(Math.cos(bf.flapPhase * 0.5) * 0.08 * bf.facing);
        ctx.scale(1, 0.90 + 0.14 * Math.abs(Math.sin(bf.flapPhase)));
      }
      ctx.imageSmoothingEnabled = false;
      ctx.globalAlpha = 1;
      ctx.drawImage(sprite, -drawW * 0.5, -drawH + 4, drawW, drawH);
      ctx.restore();
    }
  }

  _drawPixelStar(ctx, x, y, color, alpha, big) {
    ctx.globalAlpha = alpha;
    ctx.fillStyle = color;
    ctx.fillRect(x, y, PIXEL_SCALE, PIXEL_SCALE);
    if (big) {
      ctx.fillRect(x - PIXEL_SCALE, y, PIXEL_SCALE, PIXEL_SCALE);
      ctx.fillRect(x + PIXEL_SCALE, y, PIXEL_SCALE, PIXEL_SCALE);
      ctx.fillRect(x, y - PIXEL_SCALE, PIXEL_SCALE, PIXEL_SCALE);
      ctx.fillRect(x, y + PIXEL_SCALE, PIXEL_SCALE, PIXEL_SCALE);
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(x, y, PIXEL_SCALE, PIXEL_SCALE);
    }
  }

  render(fullPass = true) {
    const ctx = this.ctx;
    const env = this._currentEnv();

    let bandTop = 0;
    let bandBot = this.docH;
    let clearTop = 0;
    let clearBot = this.docH;

    if (!fullPass && !this.reducedMotion) {
      const vh = window.innerHeight || 900;
      const sy = window.scrollY || 0;
      bandTop = Math.max(0, Math.floor(sy - 120));
      bandBot = Math.min(this.docH, Math.ceil(sy + vh + 120));
      clearTop = Math.min(bandTop, this._prevBandTop ?? bandTop);
      clearBot = Math.max(bandBot, this._prevBandBot ?? bandBot);
    }
    this._prevBandTop = bandTop;
    this._prevBandBot = bandBot;

    ctx.save();
    ctx.clearRect(0, clearTop, this.docW, clearBot - clearTop);
    ctx.imageSmoothingEnabled = false;

    const minY = fullPass || this.reducedMotion ? -Infinity : clearTop + 20;
    const maxY = fullPass || this.reducedMotion ? Infinity : clearBot - 20;

    const drawW = SPRITE_W * ANIMAL_SCALE;
    const drawH = SPRITE_H * ANIMAL_SCALE;
    const cx = this.x + this.shakeX;
    const topY = this.y - drawH + 5 + this.hopY;
    const dogInBand = this.y >= minY && this.y <= maxY;

    const hopRatio = Math.min(1, Math.abs(this.hopY) / 18);
    const shOuterRx = 27 * (1 - hopRatio * 0.30);
    const shMidRx = 20 * (1 - hopRatio * 0.30);
    const shCoreRx = 13 * (1 - hopRatio * 0.32);

    this._drawProps(ctx, env, minY, maxY);
    this._drawWaterRipples(ctx);
    this._drawFloraClusters(ctx, minY, maxY);
    this._drawCompanionRange(ctx, minY, Math.min(maxY, this.y));

    if (dogInBand) {
      ctx.fillStyle = "#040814";
      ctx.globalAlpha = 0.32 * (1 - hopRatio * 0.38);
      ctx.beginPath();
      ctx.ellipse(cx, this.y, shOuterRx, 3.8, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 0.44 * (1 - hopRatio * 0.38);
      ctx.beginPath();
      ctx.ellipse(cx, this.y, shMidRx, 2.8, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 0.56 * (1 - hopRatio * 0.38);
      ctx.beginPath();
      ctx.ellipse(cx, this.y, shCoreRx, 1.9, 0, 0, Math.PI * 2);
      ctx.fill();
    }

    if (this.twig && this.twig.phase !== "carried") {
      this._drawTwig(ctx);
    }

    for (let i = 0; i < this.pawPuffs.length; i++) {
      const p = this.pawPuffs[i];
      if (p.y < minY || p.y > maxY) continue;
      ctx.globalAlpha = Math.max(0, p.life * 0.82);
      ctx.fillStyle = p.color;
      ctx.fillRect(p.x, p.y, PIXEL_SCALE, PIXEL_SCALE);
      if (p.life > 0.45) {
        ctx.fillStyle = "#fff8e3";
        ctx.fillRect(p.x + PIXEL_SCALE, p.y - PIXEL_SCALE, PIXEL_SCALE, PIXEL_SCALE);
      }
    }

    if (dogInBand) {
      const frameKey = this._selectFrameKey();
      const bank = this.facing >= 0 ? this.spritesRight : this.spritesLeft;
      const sprite = bank[frameKey] || bank.sit0;
      this._drawAnimalBody(ctx, sprite, cx, this.y, drawW, drawH, this.hopY, this.tilt, this.squashX, this.squashY);
    }

    if (this.twig && this.twig.phase === "carried" && dogInBand) {
      this._drawTwig(ctx);
    }

    this._drawCompanionRange(ctx, Math.max(minY, this.y), maxY);
    this._drawButterflies(ctx, minY, maxY);
    this._drawFireflies(ctx, env, minY, maxY);
    this._drawSeedsAndDew(ctx);

    for (let i = 0; i < this.pollenMotes.length; i++) {
      const m = this.pollenMotes[i];
      ctx.globalAlpha = Math.max(0, Math.min(1, m.life * 0.92));
      ctx.fillStyle = m.color;
      ctx.fillRect(m.x, m.y, PIXEL_SCALE, PIXEL_SCALE);
    }

    if (this.emote && this.emoteSprites[this.emote.kind]) {
      const em = this.emote;
      const norm = Math.min(1, em.age / Math.max(0.2, em.duration));
      const fade = this.reducedMotion ? 0.96 : (norm < 0.18 ? (norm / 0.18) : (norm > 0.76 ? (1 - norm) / 0.24 : 1));
      const floatLift = this.reducedMotion ? 4 : norm * 12;
      const emW = EMOTE_SIZE * ANIMAL_SCALE;
      const emX = cx + this.facing * 15 - emW * 0.5;
      const emY = topY - emW + 2 - floatLift;
      ctx.globalAlpha = Math.max(0, Math.min(1, fade * 0.96));
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(this.emoteSprites[em.kind], emX, emY, emW, emW);
    }

    for (let i = 0; i < this.napStars.length; i++) {
      const st = this.napStars[i];
      this._drawPixelStar(ctx, st.x, st.y, st.color, Math.min(1, st.life * 0.92), i % 2 === 0);
    }

    for (let i = 0; i < this.sparks.length; i++) {
      const s = this.sparks[i];
      this._drawPixelStar(ctx, s.x, s.y, s.color, Math.min(1, s.life * 0.95), s.big);
    }

    ctx.restore();
  }
}
