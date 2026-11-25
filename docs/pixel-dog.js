// SPDX-License-Identifier: MIT
// WHY: Autonomous 2.5D pixel-art Shiba/Corgi companion with real-dog gait/rest states, calm 14-28s anti-spam pixel emotes, cursor ear-perk glance, and click petting.

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
  U: "#bae6fd"
};

const SPRITE_W = 32;
const SPRITE_H = 28;
const EMOTE_SIZE = 11;
const PIXEL_SCALE = 2;

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
    ".......OWWWO.OSSO..OGCO.OSSO....",
    ".......OOOO..OOOO..OWWWOOWWO....",
    "...................OOOOOOOO.....",
    "................................",
    "................................",
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
    ".......OWWWO.OSSO..OGCO.OSSO....",
    ".......OOOO..OOOO..OWWWOOWWO....",
    "...................OOOOOOOO.....",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................"
  ],
  bow: [
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
    ".......OWWWO.OSSO...OOOGGGGWWOO.",
    ".......OOOO..OOOO....OGGGGGGGWWO",
    ".....................OCCCCWWWWWO",
    "......................OOOOWWWWWO",
    ".........................OOOOOOO",
    "................................",
    "................................",
    "................................",
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
    "................................",
    "................................"
  ]
};

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

function bakeEmoteMap() {
  const map = {};
  const keys = Object.keys(EMOTES);
  for (let k = 0; k < keys.length; k++) {
    const name = keys[k];
    map[name] = bakeSpriteGrid(EMOTES[name], EMOTE_SIZE, EMOTE_SIZE, false);
  }
  return map;
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
    this.emoteSprites = bakeEmoteMap();

    this.mqReduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    this.reducedMotion = this.mqReduced.matches;

    this.docW = 1440;
    this.docH = 1600;
    this.dpr = 1;
    this.dirtyBox = null;

    this.x = 320;
    this.y = 280;
    this.facing = 1;
    this.hopY = 0;

    this.state = this.reducedMotion ? "sit" : "trot";
    this.gait = "trot";
    this.stateTimer = 0;
    this.stateDuration = 2.8;
    this.animTime = 0;
    this.stepAccum = 0;
    this.blinkTimer = 1.9;
    this.earPerkTimer = 0;
    this.cursorNear = false;
    this.petCount = 0;

    this.emote = null;
    this.autoEmoteCooldown = 7.5 + Math.random() * 6.5;
    this.petEmoteGuard = 0;

    this.waypoints = [];
    this.currentWpIdx = -1;
    this.startPt = { x: 320, y: 280 };
    this.targetPt = { x: 520, y: 280, tag: "sky" };
    this.travelT = 0;
    this.travelDur = 3.4;
    this.travelArc = 0;

    this.pawPuffs = [];
    this.sparks = [];
    this.napStars = [];
    this.firefly = null;
    this._looping = false;

    this._resize();
    this._collectWaypoints();
    this._placeInitial();
    this._bindEvents();
    this.render();

    if (!this.reducedMotion) {
      this._startLoop();
    }
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
    this.dirtyBox = { x: 0, y: 0, w, h };
  }

  // WHY: Anchors autonomous roaming waypoints to real observatory ledges, board rims, card corridors, and the Sunflowers garden while avoiding interactive controls.
  _collectWaypoints() {
    const layerRect = this.layer.getBoundingClientRect();
    const ox = layerRect.left;
    const oy = layerRect.top;
    const pts = [];

    const clampX = (val, minPad = 38) => Math.max(minPad, Math.min(this.docW - minPad, val));
    const clampY = (val) => Math.max(48, Math.min(this.docH - 22, val));

    const skyDome = document.querySelector(".sky-dome");
    if (skyDome) {
      const r = skyDome.getBoundingClientRect();
      const left = r.left - ox;
      const top = r.top - oy;
      const yRim = clampY(top + r.height - 12);
      pts.push({ x: clampX(left + r.width * 0.15), y: yRim, tag: "sunflower" });
      pts.push({ x: clampX(left + r.width * 0.38), y: yRim, tag: "sky" });
      pts.push({ x: clampX(left + r.width * 0.64), y: yRim, tag: "sky" });
      pts.push({ x: clampX(left + r.width * 0.85), y: yRim, tag: "sunflower" });
    }

    const boards = document.querySelectorAll("section.board");
    if (boards[0]) {
      const r = boards[0].getBoundingClientRect();
      const left = r.left - ox;
      const yBot = clampY(r.bottom - oy - 4);
      pts.push({ x: clampX(left + r.width * 0.20), y: yBot, tag: "ledge" });
      pts.push({ x: clampX(left + r.width * 0.52), y: yBot, tag: "ledge" });
      pts.push({ x: clampX(left + r.width * 0.82), y: yBot, tag: "ledge" });
    }

    if (boards[1]) {
      const r = boards[1].getBoundingClientRect();
      const left = r.left - ox;
      const yBot = clampY(r.bottom - oy - 4);
      pts.push({ x: clampX(left + Math.min(180, r.width * 0.24)), y: yBot, tag: "ledge" });
      pts.push({ x: clampX(left + r.width * 0.56), y: yBot, tag: "ledge" });
    }

    const viewports = document.querySelectorAll(".forum-viewport");
    viewports.forEach((vp) => {
      const r = vp.getBoundingClientRect();
      const left = r.left - ox;
      const yLedge = clampY(r.bottom - oy - 4);
      pts.push({ x: clampX(left + Math.min(96, r.width * 0.32)), y: yLedge, tag: "card" });
    });

    const garden = document.querySelector(".garden-observatory");
    if (garden) {
      const r = garden.getBoundingClientRect();
      const left = r.left - ox;
      const top = r.top - oy;
      pts.push({ x: clampX(left + r.width * 0.14), y: clampY(top + r.height * 0.84), tag: "sunflower" });
      pts.push({ x: clampX(left + r.width * 0.30), y: clampY(top + r.height * 0.86), tag: "garden" });
      pts.push({ x: clampX(left + r.width * 0.52), y: clampY(top + r.height * 0.89), tag: "garden" });
      pts.push({ x: clampX(left + r.width * 0.72), y: clampY(top + r.height * 0.86), tag: "garden" });
      pts.push({ x: clampX(left + r.width * 0.86), y: clampY(top + r.height * 0.84), tag: "sunflower" });
    }

    if (!pts.length) {
      pts.push({ x: 180, y: 260, tag: "sky" }, { x: 420, y: 260, tag: "garden" });
    }
    this.waypoints = pts;
  }

  _placeInitial() {
    if (this.reducedMotion) {
      this._parkOnGardenLedge();
      return;
    }
    const skyPts = this.waypoints.filter((p) => p.tag === "sky" || p.tag === "sunflower");
    const first = skyPts[0] || this.waypoints[0];
    const second = skyPts[2] || skyPts[1] || this.waypoints[Math.min(1, this.waypoints.length - 1)];
    this.x = first.x;
    this.y = first.y;
    this.facing = 1;
    this.currentWpIdx = this.waypoints.indexOf(second);
    this.startPt = { x: this.x, y: this.y };
    this.targetPt = second;
    const dist = Math.hypot(second.x - first.x, second.y - first.y);
    this.gait = "trot";
    this.state = "trot";
    this.travelDur = Math.max(1.1, Math.min(3.8, dist / 96));
    this.travelT = 0;
    this.travelArc = 0;
    this._syncHitbox();
  }

  _parkOnGardenLedge() {
    const gardenPts = this.waypoints.filter((p) => p.tag === "garden");
    const park = gardenPts[0] || this.waypoints[this.waypoints.length - 1];
    this.x = park.x;
    this.y = park.y;
    this.hopY = 0;
    this.facing = 1;
    this.state = "sit";
    this.pawPuffs.length = 0;
    this.napStars.length = 0;
    this.firefly = null;
    this.emote = null;
    this._syncHitbox();
  }

  // WHY: Enforces strict 14s-28s anti-spam cooldown on autonomous pixel emotes while allowing immediate affectionate heart emote on user petting.
  _maybeShowEmote(kind, forceUser = false) {
    if (!this.emoteSprites[kind]) return;
    if (forceUser) {
      if (this.petEmoteGuard > 0) return;
      this.petEmoteGuard = 1.6;
      this.emote = { kind, age: 0, duration: 1.55 };
      return;
    }
    if (this.autoEmoteCooldown > 0 || this.emote) return;
    this.autoEmoteCooldown = 14 + Math.random() * 14;
    this.emote = { kind, age: 0, duration: 2.0 };
  }

  _pickNextWaypoint() {
    if (!this.waypoints.length) return;
    const viewTop = window.scrollY - 80;
    const viewBot = window.scrollY + (window.innerHeight || 900) + 120;

    const candidates = [];
    for (let i = 0; i < this.waypoints.length; i++) {
      if (i === this.currentWpIdx && this.waypoints.length > 1) continue;
      const wp = this.waypoints[i];
      const dist = Math.hypot(wp.x - this.x, wp.y - this.y);
      if (dist < 36 && this.waypoints.length > 2) continue;
      const inView = wp.y >= viewTop && wp.y <= viewBot;
      const nearJump = dist < 560 ? 2.2 : 0.75;
      const weight = (inView ? 2.8 : 0.85) * nearJump;
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
    this.startPt = { x: this.x, y: this.y };
    this.targetPt = chosen.wp;
    const dist = Math.hypot(this.targetPt.x - this.startPt.x, this.targetPt.y - this.startPt.y);
    const wantsRun = dist > 220 && Math.random() < 0.45;
    this.gait = wantsRun ? "run" : "trot";
    const speed = wantsRun ? (144 + Math.random() * 28) : (90 + Math.random() * 18);
    this.travelDur = Math.max(0.85, Math.min(4.4, dist / speed));
    this.travelT = 0;
    this.travelArc = Math.abs(this.targetPt.y - this.startPt.y) > 42 ? Math.min(18, dist * 0.055) : 0;
    if (Math.abs(this.targetPt.x - this.startPt.x) > 3) {
      this.facing = this.targetPt.x >= this.startPt.x ? 1 : -1;
    }
    this.state = wantsRun ? "run" : "trot";
    if (wantsRun && Math.random() < 0.45) {
      this._maybeShowEmote("note", false);
    }
    this._syncHitbox();
  }

  _chooseIdleBehavior() {
    const tag = this.targetPt ? this.targetPt.tag : "ledge";
    const r = Math.random();
    if (tag === "sunflower" && r < 0.36) {
      this._enterState("sniff", 2.0 + Math.random() * 0.9);
      this._maybeShowEmote("curious", false);
    } else if (r < 0.22) {
      this._enterState("sniff", 1.9 + Math.random() * 0.8);
      this._maybeShowEmote("curious", false);
    } else if (r < 0.48) {
      this._enterState("sit", 2.6 + Math.random() * 1.4);
      this._maybeShowEmote(Math.random() < 0.5 ? "sparkle" : "curious", false);
    } else if (r < 0.72) {
      this._enterState("rest", 3.4 + Math.random() * 1.8);
      this._maybeShowEmote("zzz", false);
    } else if (r < 0.88) {
      this._startFireflyChase();
      this._maybeShowEmote("alert", false);
    } else {
      this._enterState("nap", 3.4);
      this._maybeShowEmote("zzz", false);
    }
  }

  _enterState(nextState, duration) {
    this.state = nextState;
    this.stateTimer = 0;
    this.stateDuration = duration;
    this.hopY = 0;
    if (nextState !== "chase") {
      this.firefly = null;
    }
    this._syncHitbox();
  }

  _startFireflyChase() {
    this.state = "chase";
    this.stateTimer = 0;
    this.stateDuration = 2.5 + Math.random() * 0.7;
    const dir = this.x < this.docW * 0.5 ? 1 : -1;
    const anchorX = Math.max(58, Math.min(this.docW - 58, this.x + dir * (68 + Math.random() * 44)));
    const anchorY = Math.max(58, Math.min(this.docH - 28, this.y - 6));
    this.firefly = {
      ax: anchorX,
      ay: anchorY,
      x: anchorX,
      y: anchorY - 18,
      phase: Math.random() * Math.PI * 2
    };
    this._syncHitbox();
  }

  triggerPet() {
    this.petCount += 1;
    this.firefly = null;
    this.napStars.length = 0;
    this._maybeShowEmote("heart", true);

    if (this.reducedMotion) {
      this.state = "pet";
      this.stateTimer = 0;
      this.stateDuration = 0.65;
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
      this.dirtyBox = { x: 0, y: 0, w: this.docW, h: this.docH };
      this.render();
      clearTimeout(this._rmResetTimer);
      this._rmResetTimer = setTimeout(() => {
        if (!this.reducedMotion) return;
        this.sparks.length = 0;
        this.emote = null;
        this.state = "sit";
        this._syncHitbox();
        this.dirtyBox = { x: 0, y: 0, w: this.docW, h: this.docH };
        this.render();
      }, 750);
      return;
    }

    this._enterState("pet", 1.2);
    this._burstGoldenSparks(14);
    if (this.onJoyPulse) {
      this.onJoyPulse(this.x / Math.max(1, this.docW), this.y / Math.max(1, this.docH));
    }
  }

  _burstGoldenSparks(count) {
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
        this._collectWaypoints();
        if (this.reducedMotion) {
          this._parkOnGardenLedge();
        } else {
          this.x = Math.max(38, Math.min(this.docW - 38, this.x));
          this.y = Math.max(48, Math.min(this.docH - 22, this.y));
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
        this._parkOnGardenLedge();
        this.dirtyBox = { x: 0, y: 0, w: this.docW, h: this.docH };
        this.render();
      } else {
        this._pickNextWaypoint();
        this._startLoop();
      }
    });

    this.hitbox.addEventListener("click", (ev) => {
      ev.stopPropagation();
      this.triggerPet();
    });

    this.hitbox.addEventListener("pointerenter", () => {
      this.earPerkTimer = 1.4;
      if (this.reducedMotion) {
        this.dirtyBox = { x: 0, y: 0, w: this.docW, h: this.docH };
        this.render();
      }
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
        const idleGlance = this.state === "sit" || this.state === "rest" || this.state === "sniff";
        if (idleGlance && Math.abs(px - this.x) > 14) {
          this.facing = px >= this.x ? 1 : -1;
        }
      } else {
        this.cursorNear = false;
      }
    }, { passive: true });
  }

  _syncHitbox() {
    const modal = document.getElementById("stage-modal");
    const modalOpen = Boolean(modal && modal.open);
    if (this.hitbox.hidden !== modalOpen) {
      this.hitbox.hidden = modalOpen;
    }
    const hx = Math.round(Math.max(0, Math.min(this.docW - 48, this.x - 24)));
    const hy = Math.round(Math.max(0, Math.min(this.docH - 48, this.y - 44 + this.hopY)));
    this.hitbox.style.transform = `translate3d(${hx}px, ${hy}px, 0)`;
    this.hitbox.dataset.state = this.state;
    this.hitbox.dataset.pets = String(this.petCount);
    this.hitbox.dataset.emote = this.emote ? this.emote.kind : "";
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

  update(dt) {
    this.animTime += dt;
    if (this.autoEmoteCooldown > 0) this.autoEmoteCooldown = Math.max(0, this.autoEmoteCooldown - dt);
    if (this.petEmoteGuard > 0) this.petEmoteGuard = Math.max(0, this.petEmoteGuard - dt);
    if (this.earPerkTimer > 0) this.earPerkTimer = Math.max(0, this.earPerkTimer - dt);

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
    } else if (this.state === "sniff") {
      this.stateTimer += dt;
      if (Math.random() < dt * 1.8) {
        this.sparks.push({
          x: this.x + this.facing * 24,
          y: this.y - 12,
          vx: this.facing * (6 + Math.random() * 8),
          vy: -12 - Math.random() * 10,
          life: 0.70,
          color: "#fde047",
          big: false
        });
      }
      if (this.stateTimer >= this.stateDuration) {
        this._pickNextWaypoint();
      }
    } else if (this.state === "sit") {
      this.stateTimer += dt;
      if (this.stateTimer >= this.stateDuration) {
        this._pickNextWaypoint();
      }
    } else if (this.state === "rest") {
      this.stateTimer += dt;
      if (this.stateTimer >= this.stateDuration) {
        this._enterState("stretch", 0.68);
      }
    } else if (this.state === "stretch") {
      this.stateTimer += dt;
      if (this.stateTimer >= this.stateDuration) {
        this._pickNextWaypoint();
      }
    } else if (this.state === "chase" && this.firefly) {
      this.stateTimer += dt;
      const f = this.firefly;
      f.phase += dt * 3.8;
      f.x = Math.max(44, Math.min(this.docW - 44, f.ax + Math.cos(f.phase) * 34));
      f.y = Math.max(44, Math.min(this.docH - 28, f.ay - 18 + Math.sin(f.phase * 2) * 10));

      const dx = f.x - this.x;
      const dy = (f.y + 18) - this.y;
      if (Math.abs(dx) > 3) this.facing = dx >= 0 ? 1 : -1;
      const dist = Math.hypot(dx, dy) || 1;
      const move = Math.min(dist, 86 * dt);
      this.x = Math.max(38, Math.min(this.docW - 38, this.x + (dx / dist) * move));
      this.y = Math.max(48, Math.min(this.docH - 22, this.y + (dy / dist) * move));

      const leapWindow = this.stateDuration - this.stateTimer;
      if (leapWindow < 0.48 && leapWindow > 0) {
        this.hopY = -Math.sin(((0.48 - leapWindow) / 0.48) * Math.PI) * 12;
      } else {
        this.hopY = 0;
      }

      this.stepAccum += dt;
      if (this.stepAccum >= 0.15) {
        this.stepAccum = 0;
        this._spawnPawPuff();
      }

      if (this.stateTimer >= this.stateDuration) {
        this._burstGoldenSparks(6);
        this.firefly = null;
        this.hopY = 0;
        this._pickNextWaypoint();
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
        this._enterState("stretch", 0.72);
      }
    } else if (this.state === "pet") {
      this.stateTimer += dt;
      if (this.stateTimer >= 0.30 && this.stateTimer < 0.82) {
        const u = (this.stateTimer - 0.30) / 0.52;
        this.hopY = -Math.sin(u * Math.PI) * 14;
      } else {
        this.hopY = 0;
      }
      if (this.stateTimer >= this.stateDuration) {
        this.hopY = 0;
        this._enterState("sit", 1.5);
      }
    }

    for (let i = this.pawPuffs.length - 1; i >= 0; i--) {
      const p = this.pawPuffs[i];
      p.swirl += dt * 5.2;
      p.x += (p.vx + Math.cos(p.swirl) * 8) * dt;
      p.y += (p.vy + Math.sin(p.swirl) * 4) * dt;
      p.life -= dt * 1.55;
      if (p.life <= 0.02) this.pawPuffs.splice(i, 1);
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
      if (this.state === "pet") return "sitTilt";
      if (this.earPerkTimer > 0) return "sitEar";
      return "sit0";
    }
    if (this.state === "run") {
      if (this.hopY < -8) return "hop";
      return Math.floor(this.animTime * 13.0) % 2 === 0 ? "run0" : "run1";
    }
    if (this.state === "trot") {
      if (this.hopY < -5) return "hop";
      const idx = Math.floor(this.animTime * 9.5) % 4;
      return `trot${idx}`;
    }
    if (this.state === "chase") {
      if (this.hopY < -4) return "hop";
      return Math.floor(this.animTime * 13.5) % 2 === 0 ? "run0" : "run1";
    }
    if (this.state === "sniff") {
      if (this.earPerkTimer > 0) return "sitEar";
      return Math.floor(this.animTime * 6.0) % 2 === 0 ? "sniff0" : "sniff1";
    }
    if (this.state === "rest") {
      if (this.earPerkTimer > 0) return "rest0";
      return Math.floor(this.animTime * 1.4) % 2 === 0 ? "rest0" : "rest1";
    }
    if (this.state === "nap") {
      return Math.floor(this.animTime * 1.3) % 2 === 0 ? "nap0" : "nap1";
    }
    if (this.state === "stretch") {
      return this.stateTimer < 0.48 ? "bow" : "sitEar";
    }
    if (this.state === "pet") {
      if (this.stateTimer < 0.30) return "bow";
      if (this.stateTimer < 0.82) return "hop";
      return Math.floor(this.animTime * 10.0) % 2 === 0 ? "sit1" : "sitTilt";
    }
    if (this.earPerkTimer > 0) {
      return Math.floor(this.animTime * 4.0) % 2 === 0 ? "sitEar" : "sitTilt";
    }
    if (this.blinkTimer <= 0) return "sitBlink";
    if (this.stateTimer > 0.85 && this.stateTimer < 1.85) return "sitTilt";
    return Math.floor(this.animTime * 4.5) % 2 === 0 ? "sit0" : "sit1";
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
    if (this.dirtyBox) {
      ctx.clearRect(this.dirtyBox.x - 6, this.dirtyBox.y - 6, this.dirtyBox.w + 12, this.dirtyBox.h + 12);
    } else {
      ctx.clearRect(0, 0, this.docW, this.docH);
    }

    const drawW = SPRITE_W * PIXEL_SCALE;
    const drawH = SPRITE_H * PIXEL_SCALE;
    const snapX = Math.round((this.x - drawW * 0.5) / PIXEL_SCALE) * PIXEL_SCALE;
    const snapY = Math.round((this.y - drawH + 6 + this.hopY) / PIXEL_SCALE) * PIXEL_SCALE;
    const groundY = Math.round(this.y / PIXEL_SCALE) * PIXEL_SCALE;

    let minX = snapX - 28;
    let minY = snapY - 40;
    let maxX = snapX + drawW + 28;
    let maxY = groundY + 18;

    const hopRatio = Math.min(1, Math.abs(this.hopY) / 16);
    const shW = Math.round((20 * (1 - hopRatio * 0.30)) / PIXEL_SCALE) * PIXEL_SCALE;
    const shMidW = Math.round((15 * (1 - hopRatio * 0.30)) / PIXEL_SCALE) * PIXEL_SCALE;
    const shCoreW = Math.round((10 * (1 - hopRatio * 0.32)) / PIXEL_SCALE) * PIXEL_SCALE;
    const shCenterX = Math.round(this.x / PIXEL_SCALE) * PIXEL_SCALE;

    ctx.save();
    ctx.imageSmoothingEnabled = false;

    ctx.fillStyle = "#040814";
    ctx.globalAlpha = 0.34 * (1 - hopRatio * 0.38);
    ctx.fillRect(shCenterX - shW, groundY - PIXEL_SCALE, shW * 2, PIXEL_SCALE * 2);
    ctx.globalAlpha = 0.46 * (1 - hopRatio * 0.38);
    ctx.fillRect(shCenterX - shMidW, groundY - PIXEL_SCALE * 2, shMidW * 2, PIXEL_SCALE * 4);
    ctx.globalAlpha = 0.58 * (1 - hopRatio * 0.38);
    ctx.fillRect(shCenterX - shCoreW, groundY - PIXEL_SCALE, shCoreW * 2, PIXEL_SCALE * 2);

    for (let i = 0; i < this.pawPuffs.length; i++) {
      const p = this.pawPuffs[i];
      const px = Math.round(p.x / PIXEL_SCALE) * PIXEL_SCALE;
      const py = Math.round(p.y / PIXEL_SCALE) * PIXEL_SCALE;
      minX = Math.min(minX, px - 8);
      minY = Math.min(minY, py - 8);
      maxX = Math.max(maxX, px + 8);
      maxY = Math.max(maxY, py + 8);
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

    if (this.emote && this.emoteSprites[this.emote.kind]) {
      const em = this.emote;
      const norm = Math.min(1, em.age / Math.max(0.2, em.duration));
      const fade = norm < 0.18 ? (norm / 0.18) : (norm > 0.76 ? (1 - norm) / 0.24 : 1);
      const floatLift = this.reducedMotion ? 4 : Math.round(norm * 10);
      const emW = EMOTE_SIZE * PIXEL_SCALE;
      const emX = Math.round((this.x + this.facing * 12 - emW * 0.5) / PIXEL_SCALE) * PIXEL_SCALE;
      const emY = Math.round((snapY - emW + 2 - floatLift) / PIXEL_SCALE) * PIXEL_SCALE;
      minX = Math.min(minX, emX - 6);
      minY = Math.min(minY, emY - 6);
      maxX = Math.max(maxX, emX + emW + 6);
      ctx.globalAlpha = Math.max(0, Math.min(1, fade * 0.96));
      ctx.drawImage(this.emoteSprites[em.kind], emX, emY, emW, emW);
    }

    if (this.firefly) {
      const fx = Math.round(this.firefly.x / PIXEL_SCALE) * PIXEL_SCALE;
      const fy = Math.round(this.firefly.y / PIXEL_SCALE) * PIXEL_SCALE;
      minX = Math.min(minX, fx - 14);
      minY = Math.min(minY, fy - 14);
      maxX = Math.max(maxX, fx + 14);
      maxY = Math.max(maxY, fy + 14);
      const pulse = 0.68 + 0.32 * Math.sin(this.animTime * 14);
      ctx.globalAlpha = pulse * 0.42;
      ctx.fillStyle = "#fde047";
      ctx.fillRect(fx - PIXEL_SCALE * 2, fy - PIXEL_SCALE, PIXEL_SCALE * 5, PIXEL_SCALE * 3);
      ctx.fillRect(fx - PIXEL_SCALE, fy - PIXEL_SCALE * 2, PIXEL_SCALE * 3, PIXEL_SCALE * 5);
      this._drawPixelStar(ctx, fx, fy, "#fef08a", 0.96, true);
    }

    for (let i = 0; i < this.napStars.length; i++) {
      const st = this.napStars[i];
      minX = Math.min(minX, st.x - 10);
      minY = Math.min(minY, st.y - 10);
      maxX = Math.max(maxX, st.x + 10);
      maxY = Math.max(maxY, st.y + 10);
      this._drawPixelStar(ctx, st.x, st.y, st.color, Math.min(1, st.life * 0.92), i % 2 === 0);
    }

    for (let i = 0; i < this.sparks.length; i++) {
      const s = this.sparks[i];
      minX = Math.min(minX, s.x - 10);
      minY = Math.min(minY, s.y - 10);
      maxX = Math.max(maxX, s.x + 10);
      maxY = Math.max(maxY, s.y + 10);
      this._drawPixelStar(ctx, s.x, s.y, s.color, Math.min(1, s.life * 0.95), s.big);
    }

    ctx.restore();
    this.dirtyBox = {
      x: Math.max(0, Math.floor(minX)),
      y: Math.max(0, Math.floor(minY)),
      w: Math.min(this.docW, Math.ceil(maxX - minX)),
      h: Math.min(this.docH, Math.ceil(maxY - minY))
    };
  }
}
