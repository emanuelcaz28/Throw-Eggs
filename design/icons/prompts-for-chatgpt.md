# Icon prompts for ChatGPT

Two groups: the **HUD icons** (the emoji buttons on screen today) and the **dev product art** (the Robux shop cards).
For each one, paste the STYLE block first, then the line for that icon, into ChatGPT's image generation.

Save each result as a **PNG with a transparent background**, named exactly as in the table, into `design/icons/new/`.
Current art for reference is in `design/icons/current/` (the dev product files are the 3D renders the shop uses now).

## STYLE (paste first, every time)

```
Flat cartoon game icon, chunky and bold, like a bright mobile game HUD. One object, centred, filling about 85% of a
square 1024 x 1024 canvas, front-on view. A thick dark navy outline (#1B1230) around the whole shape, about 5% of its
width. Bright saturated colours, with one simple white highlight shape on the upper left. Simple shapes, no fine
detail, no shadow on the floor. No text, letters or numbers anywhere. Transparent background, PNG. It must still read
clearly at 56 pixels. Original design, do not imitate any existing game or brand.
```

## HUD icons

**ui_book.png**: INDEX button (book icon).
```
A closed blue storybook with cream page edges and a red ribbon bookmark hanging from the bottom.
```

**ui_shop.png**: SHOP button and the shop panel header.
```
A shopping basket with a rounded coral-pink body, two white stripes across it and a dark handle.
```

**ui_paw.png**: DINOS button (currently a 🐾 emoji).
```
A paw print: one large pad and four toe beans, white with a soft lilac shade.
```

**ui_cash.png**: the cash counter at the bottom left.
```
A stack of three green banknotes with a gold coin on top.
```

**ui_bolt.png**: the Throw Power counter at the bottom left.
```
A yellow lightning bolt. Keep it clearly different from the cash icon.
```

**ui_egg.png**: the Egg Shop panel header (currently a 🥚 emoji).
```
A cream-coloured egg with orange spots, standing upright.
```

## Dev product art (Robux shop cards, shown about 170 x 140 pixels)

The cards already show the name and the "+30% MORE" style tags, so keep these icons free of text.

**dev_clover.png**: Server Luck x2 boost.
```
A four-leaf clover, bright green with a gold outline.
```

**dev_pass_cash.png**: x2 Cash pass (Game Pass).
```
A fat bundle of banknotes tied with a blue band, with a soft blue glow behind it.
```

**dev_pass_training.png**: x2 Training pass (Game Pass).
```
A purple dumbbell with a soft purple glow.
```

**dev_cash_S.png**: cash pack 1, the smallest.
```
A small pile of three banknotes and two coins.
```

**dev_cash_M.png**: cash pack 2.
```
A bigger pile: five banknotes and a short stack of coins.
```

**dev_cash_L.png**: cash pack 3.
```
A tall stack of banknotes with a gold band around it and a few coins on top.
```

**dev_cash_XL.png**: cash pack 4, the biggest.
```
A chest overflowing with gold coins and banknotes, more gold than the smaller packs.
```

**dev_bolts_S.png**: Throw Power pack 1, the smallest.
```
One small yellow lightning bolt with a soft blue glow.
```

**dev_bolts_M.png**: Throw Power pack 2.
```
Two lightning bolts crossed over each other, with an orange glow.
```

**dev_bolts_L.png**: Throw Power pack 3.
```
Three lightning bolts in a cluster, with a purple glow.
```

**dev_bolts_XL.png**: Throw Power pack 4, the biggest.
```
A big gold lightning bolt with sparks around it.
```

## Notes

- Check each result for stray letters or numbers. ChatGPT often adds text by accident; regenerate if it does.
- The GIFT button in the design isn't built in the game yet, so it has no icon here.
- `design/icons/current/dev_gift.png` is the old gift render, kept for reference only.
- When the files are in `design/icons/new/`, tell Claude and it will wire them into the game in place of the emoji and the 3D renders.
