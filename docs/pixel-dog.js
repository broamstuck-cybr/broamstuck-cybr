// SPDX-License-Identifier: MIT
// WHY: Living 2.5D pixel Shiba/Corgi, 3-species fluttering butterflies, elastic meadow grass/wildflowers, natural dog animations, click-pet cycling, and twig fetch.

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
  constructor(layerEl, canvasEl, hitboxEl, onJoyPulse) {
    this.layer = layerEl;
    this.canvas = canvasEl;
    this.ctx = canvasEl.getContext("2d");
    this.hitbox = hitboxEl;
    this.onJoyPulse = onJoyPulse || null;

    this.spritesRight = bakeSpriteMap(false);
    this.spritesLeft = bakeSpriteMap(true);
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

    this.x = 320;
    this.y = 280;
    this.facing = 1;
    this.hopY = 0;

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

    this.petCount = 0;
    this.lastPetReaction = "none";
    this.fetchCount = 0;
    this.visitedStates = new Set();

    this.emote = null;
    this.autoEmoteCooldown = 6.0;
    this.petEmoteGuard = 0;

    this.waypoints = [];
    this.floraClusters = [];
    this.sunflowerPerches = [];
    this.butterflies = [];

    this.currentWpIdx = -1;
    this.startPt = { x: 320, y: 280 };
    this.targetPt = { x: 520, y: 280, tag: "sky" };
    this.travelT = 0;
    this.travelDur = 2.0;
    this.travelArc = 0;

    this.activeFlora = null;
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
      "butterflyNosePerch",
      "bellyRoll",
      "scratchEar",
      "yawnStretch"
    ];
    this.behaviorBag = [];

    this.pawPuffs = [];
    this.sparks = [];
    this.napStars = [];
    this.pollenMotes = [];
    this._looping = false;

    this._resize();
    this._collectWaypointsAndFlora();
    this._initButterflies();
    this._placeInitial();
    this._bindEvents();
    this.render();

    if (!this.reducedMotion) {
      this._startLoop();
    }
  }

  _recordState(st) {
    if (st) this.visitedStates.add(st);
  }

  _resize() {
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.max(320, this.layer.clientWidth || document.documentElement.clientWidth || 1440);
    const h = Math.max(480, this.layer.clientHeight || document.body.offsetHeight || 1400);
    this.docW = w;
    this.docH = h;
    this.canvas.width = Math.round(w * this.dpr);
    this.canvas.height = Math.round(h * this.dpr);
    this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    this.ctx.imageSmoothingEnabled = false;
  }

  // WHY: Builds real observatory waypoints, meadow grass/wildflower clusters, and painted Sunflower landing perches across .sky-dome, .board, and .garden-observatory.
  _collectWaypointsAndFlora() {
    const layerRect = this.layer.getBoundingClientRect();
    const ox = layerRect.left;
    const oy = layerRect.top;
    const pts = [];
    const rawFlora = [];
    const perches = [];

    const clampX = (val, minPad = 36) => Math.max(minPad, Math.min(this.docW - minPad, val));
    const clampY = (val) => Math.max(46, Math.min(this.docH - 18, val));

    const skyDome = document.querySelector(".sky-dome");
    if (skyDome) {
      const r = skyDome.getBoundingClientRect();
      const left = r.left - ox;
      const top = r.top - oy;
      const yRim = clampY(top + r.height - 10);
      pts.push({ x: clampX(left + r.width * 0.14), y: yRim, tag: "sunflower", zone: "sky" });
      pts.push({ x: clampX(left + r.width * 0.36), y: yRim, tag: "sky", zone: "sky" });
      pts.push({ x: clampX(left + r.width * 0.64), y: yRim, tag: "sky", zone: "sky" });
      pts.push({ x: clampX(left + r.width * 0.86), y: yRim, tag: "sunflower", zone: "sky" });

      const skyFloraFracs = [0.08, 0.21, 0.37, 0.56, 0.74, 0.88];
      for (let i = 0; i < skyFloraFracs.length; i++) {
        rawFlora.push({
          x: clampX(left + r.width * skyFloraFracs[i], 28),
          y: clampY(top + r.height - 2),
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

    const boards = document.querySelectorAll("section.board");
    if (boards[0]) {
      const r = boards[0].getBoundingClientRect();
      const left = r.left - ox;
      const yBot = clampY(r.bottom - oy - 2);
      pts.push({ x: clampX(left + r.width * 0.20), y: yBot, tag: "ledge", zone: "board" });
      pts.push({ x: clampX(left + r.width * 0.52), y: yBot, tag: "ledge", zone: "board" });
      pts.push({ x: clampX(left + r.width * 0.82), y: yBot, tag: "ledge", zone: "board" });

      rawFlora.push({ x: clampX(left + r.width * 0.14, 28), y: clampY(r.bottom - oy), zone: "board", lush: 1 });
      rawFlora.push({ x: clampX(left + r.width * 0.50, 28), y: clampY(r.bottom - oy), zone: "board", lush: 1 });
      rawFlora.push({ x: clampX(left + r.width * 0.86, 28), y: clampY(r.bottom - oy), zone: "board", lush: 1 });
    }

    if (boards[1] && this.docW >= 1024) {
      const r = boards[1].getBoundingClientRect();
      const left = r.left - ox;
      const yBot = clampY(r.bottom - oy - 2);
      pts.push({ x: clampX(left + Math.min(168, r.width * 0.15)), y: yBot, tag: "ledge", zone: "board" });
    }

    const viewports = document.querySelectorAll(".forum-viewport");
    viewports.forEach((vp) => {
      const r = vp.getBoundingClientRect();
      const left = r.left - ox;
      const yLedge = clampY(r.bottom - oy - 4);
      pts.push({ x: clampX(left + Math.min(96, r.width * 0.32)), y: yLedge, tag: "card", zone: "card" });
    });

    const garden = document.querySelector(".garden-observatory");
    if (garden) {
      const r = garden.getBoundingClientRect();
      const left = r.left - ox;
      const top = r.top - oy;
      pts.push({ x: clampX(left + r.width * 0.14), y: clampY(top + r.height * 0.84), tag: "sunflower", zone: "garden" });
      pts.push({ x: clampX(left + r.width * 0.30), y: clampY(top + r.height * 0.87), tag: "garden", zone: "garden" });
      pts.push({ x: clampX(left + r.width * 0.50), y: clampY(top + r.height * 0.90), tag: "garden", zone: "garden" });
      pts.push({ x: clampX(left + r.width * 0.70), y: clampY(top + r.height * 0.87), tag: "garden", zone: "garden" });
      pts.push({ x: clampX(left + r.width * 0.86), y: clampY(top + r.height * 0.84), tag: "sunflower", zone: "garden" });

      const garFlora = [
        [0.08, 0.89, 2],
        [0.19, 0.91, 2],
        [0.32, 0.92, 2],
        [0.46, 0.94, 1],
        [0.60, 0.93, 2],
        [0.74, 0.91, 2],
        [0.88, 0.89, 2]
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

    if (!pts.length) {
      pts.push({ x: 160, y: 260, tag: "sky", zone: "sky" }, { x: 340, y: 260, tag: "garden", zone: "garden" });
      rawFlora.push({ x: 200, y: 262, zone: "sky", lush: 2 }, { x: 310, y: 262, zone: "garden", lush: 2 });
    }

    const minSpacing = this.docW < 520 ? 44 : 54;
    const filteredFlora = [];
    for (let i = 0; i < rawFlora.length; i++) {
      const cand = rawFlora[i];
      let tooClose = false;
      for (let j = 0; j < filteredFlora.length; j++) {
        const ex = filteredFlora[j];
        if (Math.abs(ex.y - cand.y) < 36 && Math.abs(ex.x - cand.x) < minSpacing) {
          tooClose = true;
          break;
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

    return {
      x: spot.x,
      y: spot.y,
      zone: spot.zone,
      blades,
      flowers,
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

  // WHY: Parks pup calmly in 'sit' beside a resting wildflower and perched butterfly with zero continuous motion (0px delta) under prefers-reduced-motion: reduce.
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
    this.state = "sit";
    this._recordState("sit");
    this.earPerkTimer = 0;
    this.pawPuffs.length = 0;
    this.sparks.length = 0;
    this.napStars.length = 0;
    this.pollenMotes.length = 0;
    this.emote = null;
    this.twig = null;

    for (let i = 0; i < this.floraClusters.length; i++) {
      this.floraClusters[i].bend = 0;
      this.floraClusters[i].bendVel = 0;
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

  // WHY: Enforces strict 15s-28s anti-spam cooldown on autonomous pixel emotes while allowing immediate affectionate feedback on user click-pet or twig fetch.
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

    if (preferFlora && this.floraClusters.length) {
      const maxFloraDist = inOpening ? 190 : 380;
      const nearFlora = this.floraClusters.filter((c) => {
        const d = Math.hypot(c.x - this.x, c.y - this.y);
        const vis = !inOpening || (c.y >= viewTop && c.y <= viewBot);
        return vis && d > 28 && d < maxFloraDist;
      });
      const pool = nearFlora.length ? nearFlora : this.floraClusters;
      const cl = pool[Math.floor(Math.random() * pool.length)];
      const side = cl.x > this.docW * 0.5 ? -1 : 1;
      const tx = Math.max(38, Math.min(this.docW - 38, cl.x - side * 18));
      const ty = Math.max(46, Math.min(this.docH - 18, cl.y - 1));
      this._beginTravelTo({ x: tx, y: ty, tag: "sunflower", zone: cl.zone, floraRef: cl });
      return;
    }

    const candidates = [];
    for (let i = 0; i < this.waypoints.length; i++) {
      if (i === this.currentWpIdx && this.waypoints.length > 1) continue;
      const wp = this.waypoints[i];
      const dist = Math.hypot(wp.x - this.x, wp.y - this.y);
      if (dist < 34 && this.waypoints.length > 2) continue;
      const inView = wp.y >= viewTop && wp.y <= viewBot;
      const nearJump = inOpening ? (dist < 190 ? 4.5 : 0.15) : (dist < 520 ? 2.2 : 0.75);
      const weight = (inView ? 3.2 : 0.55) * nearJump;
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
    this.startPt = { x: this.x, y: this.y };
    this.targetPt = destWp;
    const dist = Math.hypot(this.targetPt.x - this.startPt.x, this.targetPt.y - this.startPt.y);
    const wantsRun = dist > 210 && Math.random() < 0.42;
    this.gait = wantsRun ? "run" : "trot";
    const speed = wantsRun ? (148 + Math.random() * 26) : (94 + Math.random() * 18);
    this.travelDur = Math.max(0.75, Math.min(3.8, dist / speed));
    this.travelT = 0;
    this.travelArc = Math.abs(this.targetPt.y - this.startPt.y) > 42 ? Math.min(18, dist * 0.055) : 0;
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
      const deck = [
        "sniffFlora",
        "stalkButterfly",
        "butterflyNosePerch",
        "bellyRoll",
        "scratchEar",
        "yawnStretch",
        "sit",
        "rest",
        "nap",
        "sniffFlora"
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
    const drawW = SPRITE_W * PIXEL_SCALE;
    const drawH = SPRITE_H * PIXEL_SCALE;
    const snapX = Math.round((this.x - drawW * 0.5) / PIXEL_SCALE) * PIXEL_SCALE;
    const snapY = Math.round((this.y - drawH + 6 + this.hopY) / PIXEL_SCALE) * PIXEL_SCALE;
    const noseCol = this.facing >= 0 ? 25 : (SPRITE_W - 1 - 25);
    return {
      x: snapX + noseCol * PIXEL_SCALE,
      y: snapY + 8 * PIXEL_SCALE - 2
    };
  }

  _getMouthTwigAnchor() {
    const drawW = SPRITE_W * PIXEL_SCALE;
    const drawH = SPRITE_H * PIXEL_SCALE;
    const snapX = Math.round((this.x - drawW * 0.5) / PIXEL_SCALE) * PIXEL_SCALE;
    const snapY = Math.round((this.y - drawH + 6 + this.hopY) / PIXEL_SCALE) * PIXEL_SCALE;
    const mouthCol = this.facing >= 0 ? 28 : (SPRITE_W - 1 - 28);
    return {
      x: snapX + mouthCol * PIXEL_SCALE,
      y: snapY + 12 * PIXEL_SCALE
    };
  }

  // WHY: Cycles click-pet reactions cleanly through play-bow hop -> belly-rub roll -> tail-chase spin with affectionate pixel heart/note emotes.
  triggerPet() {
    this.petCount += 1;
    this._releaseInteractiveButterfly();
    this._startleNearbyButterflies(this.x, this.y, 56);
    this.napStars.length = 0;
    if (this.twig && this.twig.phase === "carried") {
      this.twig.phase = "delivered";
      this.twig.x = this.x + this.facing * 18;
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
          x: this.x + Math.cos(a) * 20,
          y: this.y - 24 + Math.sin(a) * 14,
          vx: 0,
          vy: 0,
          life: 0.9,
          color: SPARK_COLORS[i % SPARK_COLORS.length],
          big: i % 2 === 0
        });
      }
      this._syncHitbox();
      this.render();
      clearTimeout(this._rmResetTimer);
      this._rmResetTimer = setTimeout(() => {
        if (!this.reducedMotion) return;
        this.sparks.length = 0;
        this.emote = null;
        this.state = "sit";
        this._syncHitbox();
        this.render();
      }, 750);
      return;
    }

    const dur = variant === 1 ? 1.55 : 1.3;
    this._enterState(chosenState, dur);
    this._burstGoldenSparks(12);
    if (this.onJoyPulse) {
      this.onJoyPulse(this.x / Math.max(1, this.docW), this.y / Math.max(1, this.docH), 7, -6);
    }
  }

  // WHY: Tosses a pixel golden starlight twig onto open .sky-dome or .garden-observatory space, attracts a curious butterfly, and triggers pup fetch-and-return.
  triggerTwigToss(clientX, clientY, zoneEl) {
    const modal = document.getElementById("stage-modal");
    if (modal && modal.open) return;

    const layerRect = this.layer.getBoundingClientRect();
    const rawX = clientX - layerRect.left;
    const rawY = clientY - layerRect.top;
    const zr = zoneEl.getBoundingClientRect();
    const zLeft = zr.left - layerRect.left;
    const zTop = zr.top - layerRect.top;

    const landX = Math.max(38, Math.min(this.docW - 38, Math.max(zLeft + 34, Math.min(zLeft + zr.width - 34, rawX))));
    let landY;
    if (zoneEl.classList.contains("sky-dome")) {
      landY = Math.max(48, Math.min(this.docH - 18, zTop + zr.height - 10));
    } else {
      const minGY = zTop + zr.height * 0.76;
      const maxGY = zTop + zr.height * 0.91;
      landY = Math.max(48, Math.min(this.docH - 18, Math.max(minGY, Math.min(maxGY, rawY))));
    }

    this.fetchCount += 1;
    this._releaseInteractiveButterfly();

    if (this.reducedMotion) {
      this.twig = {
        phase: "delivered",
        startX: landX,
        startY: landY,
        x: Math.min(this.docW - 32, this.x + this.facing * 22),
        y: this.y - 2,
        landX,
        landY,
        t: 1,
        dur: 0.3,
        holdTimer: 1.0
      };
      this._maybeShowEmote("sparkle", true);
      this._syncHitbox();
      this.render();
      clearTimeout(this._rmTwigTimer);
      this._rmTwigTimer = setTimeout(() => {
        if (!this.reducedMotion) return;
        this.twig = null;
        this.emote = null;
        this._syncHitbox();
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

    const sameLedge = Math.abs(this.y - landY) < 90 && Math.abs(this.x - landX) >= 56 && Math.abs(this.x - landX) <= 280;
    const retDir = landX > this.docW * 0.5 ? -1 : 1;
    this.fetchReturnPt = sameLedge
      ? { x: this.x, y: this.y }
      : {
          x: Math.max(42, Math.min(this.docW - 42, landX + retDir * Math.min(104, zr.width * 0.24))),
          y: landY
        };

    this.fetchGoalPt = { x: landX, y: landY };
    this.fetchStartPt = { x: this.x, y: this.y };
    this.facing = landX >= this.x ? 1 : -1;
    this.fetchPhase = "perk";
    this.fetchTimer = 0;
    const dist = Math.hypot(landX - this.x, landY - this.y);
    this.fetchMoveDur = Math.max(0.55, Math.min(1.85, dist / 168));
    this.state = "fetchTwig";
    this._recordState("fetchTwig");
    this.hopY = 0;
    this._maybeShowEmote("alert", true);

    if (this.onJoyPulse) {
      this.onJoyPulse(landX / Math.max(1, this.docW), landY / Math.max(1, this.docH), 6, -5);
    }
    this._syncHitbox();
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
        if (this.reducedMotion) {
          this._parkCalmEcosystem();
        } else {
          this.x = Math.max(38, Math.min(this.docW - 38, this.x));
          this.y = Math.max(48, Math.min(this.docH - 18, this.y));
          for (let i = 0; i < this.butterflies.length; i++) {
            this.butterflies[i].x = Math.max(32, Math.min(this.docW - 32, this.butterflies[i].x));
            this.butterflies[i].y = Math.max(36, Math.min(this.docH - 26, this.butterflies[i].y));
          }
          this._syncHitbox();
        }
        this.render();
      }, 80);
    };

    window.addEventListener("resize", handleResize);

    if (typeof ResizeObserver === "function") {
      const ro = new ResizeObserver(() => {
        const nextH = Math.max(480, document.body.offsetHeight || 1400);
        if (Math.abs(nextH - this.docH) > 12) handleResize();
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

    const tossZones = document.querySelectorAll(".sky-dome, .garden-observatory");
    tossZones.forEach((zoneEl) => {
      zoneEl.addEventListener("dblclick", (ev) => {
        if (ev.target && ev.target.closest && ev.target.closest("button, a")) return;
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
      const dist = Math.hypot(px - this.x, py - (this.y - 20));
      if (dist < 108) {
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

  _syncHitbox() {
    const modal = document.getElementById("stage-modal");
    const modalOpen = Boolean(modal && modal.open);
    if (this.hitbox.hidden !== modalOpen) {
      this.hitbox.hidden = modalOpen;
    }
    const hx = Math.round(Math.max(0, Math.min(this.docW - 56, this.x - 28)));
    const hy = Math.round(Math.max(0, Math.min(this.docH - 56, this.y - 48 + this.hopY)));
    if (this.reducedMotion || this._lastSyncState !== this.state || Math.hypot(hx - this._lastHx, hy - this._lastHy) >= 12) {
      this._lastHx = hx;
      this._lastHy = hy;
      this._lastSyncState = this.state;
      this.hitbox.style.transform = `translate3d(${hx}px, ${hy}px, 0)`;
    }
    this.hitbox.dataset.state = this.state;
    this.hitbox.dataset.pets = String(this.petCount);
    this.hitbox.dataset.petReaction = this.lastPetReaction;
    this.hitbox.dataset.butterflies = String(this.butterflies.length);
    this.hitbox.dataset.flora = String(this.floraClusters.length);
    this.hitbox.dataset.fetches = String(this.fetchCount);
    this.hitbox.dataset.twig = this.twig ? this.twig.phase : "none";
    this.hitbox.dataset.emote = this.emote ? this.emote.kind : "";
    this.hitbox.dataset.history = Array.from(this.visitedStates).join(",");
  }

  _startLoop() {
    if (this._looping) return;
    this._looping = true;
    let last = performance.now();
    const step = (now) => {
      if (this.reducedMotion) {
        this._looping = false;
        return;
      }
      const dt = Math.min(0.05, Math.max(0.001, (now - last) / 1000));
      last = now;
      this.update(dt);
      this.render();
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

  update(dt) {
    this.animTime += dt;
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
        const nx = this.startPt.x + (this.targetPt.x - this.startPt.x) * smooth;
        const ny = this.startPt.y + (this.targetPt.y - this.startPt.y) * smooth;
        const vx = nx - this.x;
        if (Math.abs(vx) > 0.25) {
          this.facing = vx >= 0 ? 1 : -1;
        }
        this.x = nx;
        this.y = ny;
        const strideBounce = this.state === "run" ? Math.abs(Math.sin(this.animTime * 13)) * 3.2 : 0;
        this.hopY = -Math.sin(u * Math.PI) * this.travelArc - strideBounce;

        this.stepAccum += dt;
        const puffStep = this.state === "run" ? 0.12 : 0.18;
        if (this.stepAccum >= puffStep) {
          this.stepAccum = 0;
          this._spawnPawPuff();
        }

        if (u >= 1) {
          this.hopY = 0;
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
    }

    this._updateFlora(dt);
    this._updateButterflies(dt);
    this._updateTwig(dt);

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
    if (this.state === "run") {
      if (this.hoverPauseTimer > 0) return "sitEar";
      if (this.hopY < -8) return "hop";
      return Math.floor(this.animTime * 13.0) % 2 === 0 ? "run0" : "run1";
    }
    if (this.state === "trot") {
      if (this.hoverPauseTimer > 0) return "sitEar";
      if (this.hopY < -5) return "hop";
      const idx = Math.floor(this.animTime * 9.5) % 4;
      return `trot${idx}`;
    }
    if (this.state === "sniffFlora") {
      if (this.sniffWillSneeze && this.stateTimer >= this.stateDuration - 0.58) {
        return this.stateTimer < this.stateDuration - 0.34 ? "sneeze0" : "sneeze1";
      }
      return Math.floor(this.animTime * 5.8) % 2 === 0 ? "sniffLow0" : "sniffLow1";
    }
    if (this.state === "stalkButterfly") {
      return Math.floor(this.animTime * 8.5) % 2 === 0 ? "stalk0" : "stalk1";
    }
    if (this.state === "pounceButterfly") {
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
    if (this.state === "yawnStretch") {
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
    if (this.state === "nap") {
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

  _selectButterflyFrame(bf) {
    if (this.reducedMotion) return "folded";
    if (bf.mode === "perched" || bf.mode === "nosePerched") {
      const pulse = (this.animTime * 0.75 + bf.id * 0.9) % 2.4;
      return (pulse > 1.85 && pulse < 2.12) ? "mid" : "folded";
    }
    const seq = ["open", "mid", "folded", "mid"];
    return seq[Math.floor(bf.flapPhase) % seq.length];
  }

  _drawFloraClusters(ctx) {
    for (let i = 0; i < this.floraClusters.length; i++) {
      const cl = this.floraClusters[i];
      const baseX = Math.round(cl.x / PIXEL_SCALE) * PIXEL_SCALE;
      const baseY = Math.round(cl.y / PIXEL_SCALE) * PIXEL_SCALE;

      ctx.fillStyle = "#040814";
      ctx.globalAlpha = 0.38;
      ctx.fillRect(baseX - 8 * PIXEL_SCALE, baseY - PIXEL_SCALE, 16 * PIXEL_SCALE, PIXEL_SCALE * 2);

      ctx.globalAlpha = 1;
      for (let b = 0; b < cl.blades.length; b++) {
        const bl = cl.blades[b];
        const breeze = this.reducedMotion ? 0 : Math.sin(this.animTime * 1.65 + cl.x * 0.012 + bl.phase) * 0.82;
        const tipShift = bl.lean + cl.bend + breeze;
        const shades = BLADE_SHADES[bl.shade];
        for (let s = 0; s < bl.height; s++) {
          const frac = s / Math.max(1, bl.height - 1);
          const curve = Math.round(frac * frac * tipShift);
          const px = baseX + (bl.dx + curve) * PIXEL_SCALE;
          const py = baseY - s * PIXEL_SCALE;
          ctx.fillStyle = frac < 0.35 ? shades[0] : (frac < 0.78 ? shades[1] : shades[2]);
          ctx.fillRect(px, py, PIXEL_SCALE, PIXEL_SCALE);
        }
      }

      for (let f = 0; f < cl.flowers.length; f++) {
        const fl = cl.flowers[f];
        const breeze = this.reducedMotion ? 0 : Math.sin(this.animTime * 1.55 + cl.x * 0.012 + fl.phase) * 0.78;
        const sway = cl.bend * 0.9 + breeze;
        let topX = baseX + fl.dx * PIXEL_SCALE;
        let topY = baseY;
        for (let s = 0; s < fl.stemH; s++) {
          const frac = s / Math.max(1, fl.stemH - 1);
          const curve = Math.round(frac * frac * sway);
          topX = baseX + (fl.dx + curve) * PIXEL_SCALE;
          topY = baseY - s * PIXEL_SCALE;
          ctx.fillStyle = s < 2 ? "#064e3b" : "#15803d";
          ctx.fillRect(topX, topY, PIXEL_SCALE, PIXEL_SCALE);
        }
        const bloom = this.flowerSprites[fl.kind] || this.flowerSprites.gold;
        ctx.drawImage(bloom, topX - 2 * PIXEL_SCALE, topY - 4 * PIXEL_SCALE, 5 * PIXEL_SCALE, 5 * PIXEL_SCALE);
      }
    }
  }

  _drawTwig(ctx) {
    if (!this.twig) return;
    const tw = this.twig;
    const sprite = this.facing >= 0 ? this.twigSpriteRight : this.twigSpriteLeft;
    const w = TWIG_W * PIXEL_SCALE;
    const h = TWIG_H * PIXEL_SCALE;
    const tx = Math.round((tw.x - w * 0.5) / PIXEL_SCALE) * PIXEL_SCALE;
    const ty = Math.round((tw.y - h * 0.5) / PIXEL_SCALE) * PIXEL_SCALE;

    if (tw.phase === "landed" || tw.phase === "delivered") {
      ctx.fillStyle = "#040814";
      ctx.globalAlpha = 0.36;
      ctx.fillRect(tx + PIXEL_SCALE, ty + h - PIXEL_SCALE, w - PIXEL_SCALE * 2, PIXEL_SCALE * 2);
      const glow = this.reducedMotion ? 0.55 : (0.45 + 0.25 * Math.sin(this.animTime * 6.0));
      this._drawPixelStar(ctx, tx + w - PIXEL_SCALE * 2, ty - PIXEL_SCALE, "#fde047", glow, false);
    }
    ctx.globalAlpha = 1;
    ctx.drawImage(sprite, tx, ty, w, h);
  }

  _drawButterflies(ctx) {
    const drawW = BF_W * PIXEL_SCALE;
    const drawH = BF_H * PIXEL_SCALE;
    for (let i = 0; i < this.butterflies.length; i++) {
      const bf = this.butterflies[i];
      const spBank = this.butterflySprites[bf.species];
      if (!spBank) continue;
      const dirBank = bf.facing >= 0 ? spBank.right : spBank.left;
      const fKey = this._selectButterflyFrame(bf);
      const sprite = dirBank[fKey] || dirBank.open;

      const bob = (this.reducedMotion || bf.mode === "perched" || bf.mode === "nosePerched")
        ? 0
        : (fKey === "open" ? 1 : (fKey === "folded" ? -2 : 0));
      const bx = Math.round((bf.x - drawW * 0.5) / PIXEL_SCALE) * PIXEL_SCALE;
      const by = Math.round((bf.y - drawH + 4 + bob) / PIXEL_SCALE) * PIXEL_SCALE;

      if (!this.reducedMotion && bf.mode !== "perched" && bf.mode !== "nosePerched") {
        ctx.globalAlpha = 0.20;
        ctx.fillStyle = bf.species === "morpho" ? "#7dd3fc" : "#fde047";
        ctx.fillRect(bx + 4 * PIXEL_SCALE, by + 3 * PIXEL_SCALE, 5 * PIXEL_SCALE, 4 * PIXEL_SCALE);
      }

      ctx.globalAlpha = 1;
      ctx.drawImage(sprite, bx, by, drawW, drawH);
    }
  }

  _drawPixelStar(ctx, x, y, color, alpha, big) {
    const px = Math.round(x / PIXEL_SCALE) * PIXEL_SCALE;
    const py = Math.round(y / PIXEL_SCALE) * PIXEL_SCALE;
    ctx.globalAlpha = alpha;
    ctx.fillStyle = color;
    ctx.fillRect(px, py, PIXEL_SCALE, PIXEL_SCALE);
    if (big) {
      ctx.fillRect(px - PIXEL_SCALE, py, PIXEL_SCALE, PIXEL_SCALE);
      ctx.fillRect(px + PIXEL_SCALE, py, PIXEL_SCALE, PIXEL_SCALE);
      ctx.fillRect(px, py - PIXEL_SCALE, PIXEL_SCALE, PIXEL_SCALE);
      ctx.fillRect(px, py + PIXEL_SCALE, PIXEL_SCALE, PIXEL_SCALE);
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(px, py, PIXEL_SCALE, PIXEL_SCALE);
    }
  }

  render() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.docW, this.docH);

    const drawW = SPRITE_W * PIXEL_SCALE;
    const drawH = SPRITE_H * PIXEL_SCALE;
    const snapX = Math.round((this.x - drawW * 0.5) / PIXEL_SCALE) * PIXEL_SCALE;
    const snapY = Math.round((this.y - drawH + 6 + this.hopY) / PIXEL_SCALE) * PIXEL_SCALE;
    const groundY = Math.round(this.y / PIXEL_SCALE) * PIXEL_SCALE;

    const hopRatio = Math.min(1, Math.abs(this.hopY) / 18);
    const shW = Math.round((20 * (1 - hopRatio * 0.30)) / PIXEL_SCALE) * PIXEL_SCALE;
    const shMidW = Math.round((15 * (1 - hopRatio * 0.30)) / PIXEL_SCALE) * PIXEL_SCALE;
    const shCoreW = Math.round((10 * (1 - hopRatio * 0.32)) / PIXEL_SCALE) * PIXEL_SCALE;
    const shCenterX = Math.round(this.x / PIXEL_SCALE) * PIXEL_SCALE;

    ctx.save();
    ctx.imageSmoothingEnabled = false;

    this._drawFloraClusters(ctx);

    ctx.fillStyle = "#040814";
    ctx.globalAlpha = 0.34 * (1 - hopRatio * 0.38);
    ctx.fillRect(shCenterX - shW, groundY - PIXEL_SCALE, shW * 2, PIXEL_SCALE * 2);
    ctx.globalAlpha = 0.46 * (1 - hopRatio * 0.38);
    ctx.fillRect(shCenterX - shMidW, groundY - PIXEL_SCALE * 2, shMidW * 2, PIXEL_SCALE * 4);
    ctx.globalAlpha = 0.58 * (1 - hopRatio * 0.38);
    ctx.fillRect(shCenterX - shCoreW, groundY - PIXEL_SCALE, shCoreW * 2, PIXEL_SCALE * 2);

    if (this.twig && this.twig.phase !== "carried") {
      this._drawTwig(ctx);
    }

    for (let i = 0; i < this.pawPuffs.length; i++) {
      const p = this.pawPuffs[i];
      const px = Math.round(p.x / PIXEL_SCALE) * PIXEL_SCALE;
      const py = Math.round(p.y / PIXEL_SCALE) * PIXEL_SCALE;
      ctx.globalAlpha = Math.max(0, p.life * 0.82);
      ctx.fillStyle = p.color;
      ctx.fillRect(px, py, PIXEL_SCALE, PIXEL_SCALE);
      if (p.life > 0.45) {
        ctx.fillStyle = "#fff8e3";
        ctx.fillRect(px + PIXEL_SCALE, py - PIXEL_SCALE, PIXEL_SCALE, PIXEL_SCALE);
      }
    }

    const frameKey = this._selectFrameKey();
    const bank = this.facing >= 0 ? this.spritesRight : this.spritesLeft;
    const sprite = bank[frameKey] || bank.sit0;
    ctx.globalAlpha = 1;
    ctx.drawImage(sprite, snapX, snapY, drawW, drawH);

    if (this.twig && this.twig.phase === "carried") {
      this._drawTwig(ctx);
    }

    this._drawButterflies(ctx);

    for (let i = 0; i < this.pollenMotes.length; i++) {
      const m = this.pollenMotes[i];
      const mx = Math.round(m.x / PIXEL_SCALE) * PIXEL_SCALE;
      const my = Math.round(m.y / PIXEL_SCALE) * PIXEL_SCALE;
      ctx.globalAlpha = Math.max(0, Math.min(1, m.life * 0.92));
      ctx.fillStyle = m.color;
      ctx.fillRect(mx, my, PIXEL_SCALE, PIXEL_SCALE);
    }

    if (this.emote && this.emoteSprites[this.emote.kind]) {
      const em = this.emote;
      const norm = Math.min(1, em.age / Math.max(0.2, em.duration));
      const fade = this.reducedMotion ? 0.96 : (norm < 0.18 ? (norm / 0.18) : (norm > 0.76 ? (1 - norm) / 0.24 : 1));
      const floatLift = this.reducedMotion ? 4 : Math.round(norm * 10);
      const emW = EMOTE_SIZE * PIXEL_SCALE;
      const emX = Math.round((this.x + this.facing * 12 - emW * 0.5) / PIXEL_SCALE) * PIXEL_SCALE;
      const emY = Math.round((snapY - emW + 2 - floatLift) / PIXEL_SCALE) * PIXEL_SCALE;
      ctx.globalAlpha = Math.max(0, Math.min(1, fade * 0.96));
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
