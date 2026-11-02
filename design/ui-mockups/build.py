"""Builds ui.html: the Throw Eggs for Dinosaurs UI mock-ups (v2), one .screen per Figma frame.

Dino, egg, biome and pack pictures come from renders/: Blender renders of the blueprint models
in assets/models (build_blueprints.py, then render_thumbnails.py). When final models replace the
blueprints, re-render and rebuild; the layout keeps the same image slots.
"""
import base64
import pathlib

HERE = pathlib.Path(__file__).parent
INK = "#1b1230"
_cache = {}


def img(name, w, h=None, extra=""):
    if name not in _cache:
        data = (HERE / "renders" / f"{name}.png").read_bytes()
        _cache[name] = "data:image/png;base64," + base64.b64encode(data).decode()
    h_attr = f"height:{h}px;" if h else ""
    return f'<img src="{_cache[name]}" style="width:{w}px;{h_attr}object-fit:contain;{extra}">'


# --- Vector icons (UI chrome only; content art comes from renders) ------------------------

def bolt(size=56):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><path d="M38 3 L10 37 H28 L22 61 L54 23 H35 Z" fill="#ffd43b" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/><path d="M34 10 L19 31 H27" fill="none" stroke="#fff6c2" stroke-width="3" stroke-linecap="round"/></svg>'''

def cash(size=56):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><rect x="4" y="24" width="48" height="28" rx="6" fill="#2e9e3a" stroke="{INK}" stroke-width="4"/><rect x="12" y="14" width="48" height="28" rx="6" fill="#5bd96a" stroke="{INK}" stroke-width="4"/><circle cx="36" cy="28" r="7" fill="#c9f8c2" stroke="{INK}" stroke-width="3"/><rect x="17" y="19" width="6" height="6" rx="2" fill="#c9f8c2"/><rect x="49" y="31" width="6" height="6" rx="2" fill="#c9f8c2"/></svg>'''

def book(size=64):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><path d="M12 56 Q8 56 8 52 V12 Q8 6 14 6 H52 V50 H14 Q10 50 10 54" fill="#4f8dff" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/><path d="M10 52 Q10 58 15 58 H52 V50" fill="#f6f1e1" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/><rect x="17" y="15" width="24" height="7" rx="3.5" fill="#c6dbff"/><rect x="17" y="27" width="16" height="5" rx="2.5" fill="#c6dbff"/><path d="M40 6 V26 L45.5 21.5 L51 26 V6" fill="#ff5c7a" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/></svg>'''

def bag(size=64):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><path d="M22 24 V17 Q22 6 32 6 Q42 6 42 17 V24" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/><path d="M9 22 H55 L51 55 Q50.6 59 47 59 H17 Q13.4 59 13 55 Z" fill="#ff6b8a" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/><path d="M9.6 22 H54.4 L53.4 31 H10.6 Z" fill="#ffd166" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/><path d="M32 37 L34.6 42.4 L40.5 43.2 L36.2 47.2 L37.3 53 L32 50.2 L26.7 53 L27.8 47.2 L23.5 43.2 L29.4 42.4 Z" fill="#fff3c4" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/></svg>'''

def track(size=64, color="#ff9f43"):
    s = f'fill="{color}" stroke="{INK}" stroke-width="4"'
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><ellipse cx="16" cy="22" rx="6.5" ry="12" transform="rotate(-28 16 22)" {s}/><ellipse cx="32" cy="15" rx="6.5" ry="13" {s}/><ellipse cx="48" cy="22" rx="6.5" ry="12" transform="rotate(28 48 22)" {s}/><path d="M18 42 Q18 30 32 30 Q46 30 46 42 Q46 58 32 58 Q18 58 18 42 Z" {s}/></svg>'''

def clock(size=32):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><circle cx="32" cy="32" r="26" fill="#ffffff" stroke="{INK}" stroke-width="5"/><path d="M32 16 V32 L43 39" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>'''

def meteor(size=34):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><path d="M6 6 L34 22 L22 34 Z" fill="#ffb13b"/><path d="M14 4 L40 18" stroke="#ff7a2f" stroke-width="5" stroke-linecap="round"/><path d="M4 14 L18 40" stroke="#ff7a2f" stroke-width="5" stroke-linecap="round"/><circle cx="40" cy="40" r="17" fill="#ff7a2f" stroke="{INK}" stroke-width="4"/><circle cx="35" cy="36" r="4" fill="#c4451a"/><circle cx="46" cy="45" r="3" fill="#c4451a"/></svg>'''

def coin(size=26):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><path d="M32 4 L56 18 V46 L32 60 L8 46 V18 Z" fill="#ffd43b" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/><path d="M32 18 L44 25 V39 L32 46 L20 39 V25 Z" fill="none" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/></svg>'''

def check(size=26):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><path d="M10 34 L26 50 L54 16" fill="none" stroke="{INK}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/><path d="M10 34 L26 50 L54 16" fill="none" stroke="#ffffff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></svg>'''

def cross(size=30):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><path d="M14 14 L50 50 M50 14 L14 50" stroke="{INK}" stroke-width="18" stroke-linecap="round"/><path d="M14 14 L50 50 M50 14 L14 50" stroke="#ffffff" stroke-width="8" stroke-linecap="round"/></svg>'''

def info(size=40):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><circle cx="32" cy="32" r="27" fill="#4f8dff" stroke="{INK}" stroke-width="5"/><circle cx="32" cy="19" r="4.5" fill="#fff"/><rect x="27.5" y="28" width="9" height="20" rx="4" fill="#fff"/></svg>'''


# --- Data -----------------------------------------------------------------------------------

RARITY = {  # top, bottom of the tile gradient; label colour
    "common": ("#e6e9ef", "#a9b1bf", "#c9ced8"),
    "uncommon": ("#b4f59c", "#52c43f", "#8dff5a"),
    "rare": ("#9ad9ff", "#2f8fe6", "#6fd0ff"),
    "epic": ("#dcb0ff", "#9150e8", "#d4a6ff"),
    "legendary": ("#ffe58a", "#ff9a1f", "#ffcf3f"),
}
BIOMES = [
    ("FernValley", "Fern Valley", ("#4fe0ff", "#1aa6e0"), [("Compy", "Compy", "1 in 2"), ("Gallimimus", "Gallimimus", "1 in 5"), ("Parasaur", "Parasaurolophus", "1 in 20"), ("Stego", "Stegosaurus", "1 in 100"), ("Raptor", "Velociraptor", "1 in 500")], 5),
    ("DryPlains", "Dry Plains", ("#ffc14d", "#ff7a2f"), [("Pachy", "Pachycephalosaurus", "1 in 2"), ("Ankylo", "Ankylosaurus", "1 in 6"), ("Triceratops", "Triceratops", "1 in 30"), ("Carno", "Carnotaurus", "1 in 150"), ("TRex", "T-Rex", "1 in 1,000")], 3),
    ("Swamp", "Swamp", ("#8fe05a", "#2f9e6a"), [("Bary", "Baryonyx", "1 in 2"), ("Dilo", "Dilophosaurus", "1 in 8"), ("Sarco", "Sarcosuchus", "1 in 40"), ("Brachio", "Brachiosaurus", "1 in 250"), ("Spino", "Spinosaurus", "1 in 2,000")], 1),
]
ORDER = ["common", "uncommon", "rare", "epic", "legendary"]


def tile_bg(rarity):
    top, bottom, _ = RARITY[rarity]
    return f"background:linear-gradient({top},{bottom});"


# --- Building blocks ------------------------------------------------------------------------

def button(text, color, w, h, size=30, extra=""):
    return f'<div class="btn {color}" style="width:{w}px;height:{h}px;font-size:{size}px;{extra}">{text}</div>'

def robux(price, w=150, h=58, size=28):
    return button(f'{coin(int(size * 0.95))}<span>{price}</span>', "green", w, h, size)

def tag(text, color, extra=""):
    return f'<span class="tag {color}" style="{extra}">{text}</span>'

def head(title, color, icon=""):
    return f'''<div class="head {color}"><div class="sheen"></div><div class="headtitle">{icon}<span class="ol" style="font-size:46px">{title}</span></div><div class="close">{cross(30)}</div></div>'''

def divider(text):
    return f'<div class="divider"><div class="rule"></div><span class="dpill ol thin">{text}</span><div class="rule"></div></div>'

SCENE = '''<div class="scene"><div class="hill" style="left:-80px;top:300px;width:520px;height:260px"></div><div class="hill" style="left:760px;top:320px;width:640px;height:240px"></div><div class="ground"></div><div class="studrow"></div></div>'''

def screen(name, inner, dim=False, height=720):
    overlay = f'<div class="dim" style="height:{height}px"></div>' if dim else ""
    scene = SCENE.replace("height:720px", f"height:{height}px") if height != 720 else SCENE
    return f'<section class="screen" data-name="{name}" style="height:{height}px">{scene}{overlay}{inner}</section>'

def side_button(icon, label, style):
    return f'<div class="sidebtn" style="{style}">{icon}<span class="ol sidelabel">{label}</span></div>'

def stats():
    return f'''<div class="stat" style="left:24px;bottom:104px">{bolt(54)}<span class="ol" style="font-size:52px;color:#6fe3ff">4,823</span></div>
<div class="stat" style="left:24px;bottom:34px">{cash(56)}<span class="ol" style="font-size:52px;color:#8dff5a">$778.4K</span></div>
<span class="ol" style="position:absolute;left:94px;bottom:12px;font-size:21px">+$1.24K/s</span>'''

def hotbar(selected=1):
    held = [("Spino", "legendary", "$1.8M/s"), ("Brachio", "epic", "$60K/s"), ("Triceratops", "rare", "$5.6K/s"),
            ("Sarco", "rare", "$4.1K/s"), ("Dilo", "uncommon", "$900/s"), ("Ankylo", "uncommon", "$250/s"),
            ("Pachy", "common", "$25/s"), ("Compy", "common", "$10/s"), None, None]
    out = []
    for index, d in enumerate(held):
        number = (index + 1) % 10
        if d is None:
            out.append(f'<div class="slot empty"><span class="ol slotnum">{number}</span></div>')
            continue
        dino, rarity, income = d
        cls = "slot sel" if index + 1 == selected else "slot"
        out.append(f'<div class="{cls}" style="{tile_bg(rarity)}"><span class="ol slotcash">{income}</span>{img("dino_" + dino, 58, 48)}<span class="ol slotnum">{number}</span></div>')
    return f'<div class="hotbar">{"".join(out)}</div>'

def dino_tile(dino_id, name, rarity, w, h, found=True, odds=None, name_size=22):
    if not found:
        return f'''<div class="dtile" style="width:{w}px;height:{h}px;background:linear-gradient(#d9dce3,#9aa1ae)"><span class="ol dname" style="font-size:{name_size}px;position:relative;z-index:2">???</span>{img("dino_" + dino_id + "_shadow", w - 16, h - 36, "margin-top:-8px")}</div>'''
    odds_html = f'<span class="ol thin dodds">{odds}</span>' if odds else ""
    return f'''<div class="dtile" style="width:{w}px;height:{h}px;{tile_bg(rarity)}"><span class="ol dname" style="font-size:{name_size}px;position:relative;z-index:2">{name}</span>{img("dino_" + dino_id, w - 16, h - 36, "margin-top:-8px")}{odds_html}</div>'''


CSS = f"""
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0e0b18;font-family:'Fredoka One','Fredoka','Arial Rounded MT Bold',sans-serif;color:#fff;padding:40px}}
.screen{{width:1280px;position:relative;overflow:hidden;margin-bottom:60px}}
.scene{{position:absolute;left:0;top:0;width:1280px;height:720px;background:linear-gradient(#69b9ff,#bfe6ff 62%)}}
.hill{{position:absolute;border-radius:50%;background:#4aa84a}}
.ground{{position:absolute;left:0;top:430px;width:1280px;height:290px;background:linear-gradient(#6fd05b,#4fb43f)}}
.studrow{{position:absolute;left:0;top:430px;width:1280px;height:290px;background:repeating-linear-gradient(90deg,rgba(255,255,255,0.07) 0 64px,rgba(0,0,0,0.05) 64px 128px)}}
.dim{{position:absolute;left:0;top:0;width:1280px;height:720px;background:rgba(14,8,30,0.6)}}
.ol{{color:#fff;-webkit-text-stroke:5px {INK};paint-order:stroke fill;letter-spacing:0.5px;line-height:1.1}}
.ol.thin{{-webkit-text-stroke:3px {INK}}}
.muted{{color:#cbbff0;font-family:'Fredoka','Fredoka One',sans-serif;font-weight:600}}
.btn{{display:flex;align-items:center;justify-content:center;gap:8px;border:4px solid {INK};border-radius:18px;box-shadow:inset 0 -7px 0 rgba(0,0,0,0.22),inset 0 4px 0 rgba(255,255,255,0.35),0 5px 0 {INK};color:#fff;-webkit-text-stroke:4px {INK};paint-order:stroke fill}}
.green{{background:linear-gradient(#8af25a,#3fbf22)}}
.blue{{background:linear-gradient(#6cc4ff,#2f8ce6)}}
.red{{background:linear-gradient(#ff7a6b,#e8392f)}}
.yellow{{background:linear-gradient(#ffe066,#f5a815)}}
.grey{{background:linear-gradient(#a9a3bd,#77708f)}}
.purple{{background:linear-gradient(#c58bff,#8a46e8)}}
.pink{{background:linear-gradient(#ff8fc8,#ff4d9a)}}
.panel{{position:absolute;background:#1f1a33;border:5px solid {INK};border-radius:30px;box-shadow:0 10px 0 rgba(0,0,0,0.35),inset 0 0 0 4px #2f2750;overflow:hidden}}
.head{{height:88px;position:relative;border-bottom:5px solid {INK};display:flex;align-items:center;padding-left:26px}}
.head.sun{{background:linear-gradient(90deg,#ffd23f,#ff8a1f)}}
.head.berry{{background:linear-gradient(90deg,#ff4fb8,#b13bff)}}
.head.jungle{{background:linear-gradient(90deg,#7ee35a,#1fa860)}}
.head.sky{{background:linear-gradient(90deg,#4fe0ff,#2f7fe6)}}
.head.gold{{background:linear-gradient(90deg,#ffe066,#ff9a1f)}}
.sheen{{position:absolute;left:55%;top:0;width:280px;height:88px;background:repeating-linear-gradient(115deg,rgba(255,255,255,0.22) 0 26px,transparent 26px 52px)}}
.headtitle{{position:relative;display:flex;align-items:center;gap:12px}}
.close{{position:absolute;right:16px;top:14px;width:58px;height:58px;border-radius:16px;border:4px solid {INK};background:linear-gradient(#ff7a6b,#e8392f);box-shadow:inset 0 -6px 0 rgba(0,0,0,0.22),0 4px 0 {INK};display:flex;align-items:center;justify-content:center}}
.sidebtn{{position:absolute;width:104px;height:104px;border-radius:28px;border:5px solid {INK};background:linear-gradient(#4a3a75,#2a2045);box-shadow:inset 0 0 0 4px #5b4a8c,inset 0 -8px 0 rgba(0,0,0,0.25),0 5px 0 {INK};display:flex;align-items:flex-start;justify-content:center;padding-top:10px}}
.sidelabel{{position:absolute;bottom:-16px;left:-10px;right:-10px;text-align:center;font-size:27px}}
.stat{{position:absolute;display:flex;align-items:center;gap:10px}}
.hotbar{{position:absolute;left:316px;bottom:14px;display:flex;gap:6px;align-items:flex-end}}
.slot{{position:relative;width:64px;height:76px;border-radius:15px;border:4px solid {INK};display:flex;align-items:center;justify-content:center;box-shadow:inset 0 -5px 0 rgba(0,0,0,0.18)}}
.slot.empty{{background:rgba(27,18,48,0.55)}}
.slot.sel{{transform:translateY(-10px);outline:4px solid #ffffff}}
.slotcash{{position:absolute;top:-15px;left:-8px;right:-8px;text-align:center;font-size:15px;white-space:nowrap;color:#8dff5a;-webkit-text-stroke:3px {INK}}}
.slotnum{{position:absolute;left:4px;bottom:0;font-size:17px;-webkit-text-stroke:3px {INK}}}
.pill{{position:absolute;display:flex;align-items:center;gap:8px;height:48px;padding:0 16px 0 10px;border-radius:18px;border:4px solid {INK};background:rgba(36,27,58,0.92);font-size:24px}}
.dtile{{position:relative;border-radius:20px;border:4px solid {INK};display:flex;flex-direction:column;align-items:center;padding-top:8px;box-shadow:inset 0 -6px 0 rgba(0,0,0,0.16),inset 0 3px 0 rgba(255,255,255,0.4)}}
.dname{{white-space:nowrap}}
.dodds{{position:absolute;bottom:6px;font-size:16px;color:#ffffff;z-index:2}}
.row{{display:flex;align-items:center;gap:12px;height:98px;padding:0 12px;border-radius:20px;border:4px solid {INK};background:#2b2448;box-shadow:inset 0 -5px 0 rgba(0,0,0,0.25)}}
.tab{{height:46px;border-radius:15px;border:4px solid {INK};display:flex;align-items:center;justify-content:center;font-size:22px}}
.card{{position:relative;border-radius:26px;border:5px solid {INK};box-shadow:inset 0 -8px 0 rgba(0,0,0,0.18),inset 0 4px 0 rgba(255,255,255,0.35),0 6px 0 {INK};overflow:hidden}}
.tag{{display:inline-block;border:4px solid {INK};border-radius:14px;padding:2px 12px;font-size:20px;color:#fff;-webkit-text-stroke:3px {INK};paint-order:stroke fill;transform:rotate(-4deg)}}
.tag.gold{{background:linear-gradient(#fff1a8,#ffc21a);color:{INK};-webkit-text-stroke:0}}
.tag.redt{{background:linear-gradient(#ff7a6b,#e8392f)}}
.tag.purplet{{background:linear-gradient(#c58bff,#8a46e8)}}
.tag.greent{{background:linear-gradient(#8af25a,#3fbf22)}}
.divider{{display:flex;align-items:center;gap:14px;margin:14px 0 12px}}
.rule{{flex:1;height:5px;border-radius:3px;background:#3a3060}}
.dpill{{background:#2f2750;border:4px solid {INK};border-radius:16px;padding:4px 26px;font-size:26px}}
.bar{{position:relative;height:26px;border-radius:13px;border:4px solid {INK};background:#120d22;overflow:hidden}}
.fill{{position:absolute;left:0;top:0;bottom:0;border-radius:9px}}
.glow{{position:absolute;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,0.75),rgba(255,255,255,0) 68%)}}
.label{{font-size:22px;margin-bottom:12px;color:#ffe066}}
.note{{background:#241d3d;border:4px solid {INK};border-radius:20px;padding:14px 18px;display:flex;flex-direction:column;gap:6px}}
"""

screens = []

# --- 00 Style guide --------------------------------------------------------------------------
roles = [("BUY / GO", "#3fbf22"), ("ATTENTION", "#ffc21a"), ("URGENT", "#e8392f"), ("PREMIUM", "#8a46e8"),
         ("TRUST / INFO", "#2f8ce6"), ("POWER", "#6fe3ff"), ("CASH", "#8dff5a"), ("PANEL", "#1f1a33")]
sw = "".join(f'<div style="display:flex;flex-direction:column;align-items:center;gap:6px"><div style="width:104px;height:74px;border-radius:18px;border:4px solid {INK};background:{c}"></div><span class="ol thin" style="font-size:16px">{n}</span></div>' for n, c in roles)
rar = "".join(f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px">{dino_tile(d, r.upper(), r, 118, 128, name_size=17)}</div>' for d, r in zip(["Compy", "Ankylo", "Triceratops", "Brachio", "Spino"], ORDER))
style_guide = f'''<div style="position:absolute;left:0;top:0;width:1280px;height:720px;background:#150f24"></div>
<div style="position:absolute;left:48px;top:30px"><div class="ol" style="font-size:52px">Throw Eggs for Dinosaurs · UI kit v2</div>
<div class="muted" style="font-size:20px;margin-top:6px">Bright, saturated colour on dark panels. Every colour has one job. Dinos, eggs and maps are Blender renders of the blueprint models.</div></div>
<div style="position:absolute;left:48px;top:140px"><div class="label">Colour jobs</div><div style="display:flex;gap:14px">{sw}</div></div>
<div style="position:absolute;left:48px;top:290px"><div class="label">Rarity ladder (tile backgrounds)</div><div style="display:flex;gap:14px">{rar}</div></div>
<div style="position:absolute;left:740px;top:290px"><div class="label">Buttons &amp; tags</div>
<div style="display:flex;flex-wrap:wrap;gap:14px;width:500px;align-items:center">{robux("99")}{button("CLAIM", "green", 170, 58, 28)}{button("EQUIP", "blue", 140, 58, 26)}{button("SELL", "red", 120, 58, 26)}{button("OWNED", "grey", 140, 58, 24)}
{tag("BEST DEAL!", "gold")}{tag("LIMITED", "redt")}{tag("+50% MORE", "purplet")}{tag("NEW!", "greent")}</div></div>
<div style="position:absolute;left:48px;top:500px"><div class="label">Blender renders</div><div style="display:flex;gap:6px;align-items:flex-end">
{img("dino_TRex", 130, 110)}{img("dino_Stego", 130, 110)}{img("dino_Triceratops", 130, 110)}{img("dino_Spino", 130, 110)}{img("dino_Brachio", 130, 110)}{img("egg_GoldenEgg", 80, 100)}{img("egg_PrismEgg", 80, 100)}{img("biome_FernValley", 120, 120)}{img("cash_L", 120, 100)}{img("clover", 90, 90)}{img("gift", 80, 80)}</div></div>'''
screens.append(f'<section class="screen" data-name="00 Style guide" style="height:720px">{style_guide}</section>')

# --- 01 Main HUD -----------------------------------------------------------------------------
hud = f'''{side_button(book(64), "Index", "left:24px;top:236px")}
{side_button(bag(64), "Shop", "left:24px;top:372px")}
{side_button(track(64), "Dinos", "right:24px;top:304px")}
<div class="pill" style="right:20px;top:16px">{meteor(34)}<span class="ol thin" style="color:#ffb13b">METEOR SHOWER</span><span class="ol thin">9:41</span></div>
<div class="ol" style="position:absolute;left:0;right:0;top:110px;text-align:center;font-size:30px;color:#ffe066">Plot upgraded! It now holds 10 dinos</div>
<div style="position:absolute;left:540px;top:250px;display:flex;flex-direction:column;align-items:center">
<span class="ol thin" style="font-size:16px;color:#ffcf3f">HUGE · DIAMOND</span><span class="ol" style="font-size:22px">Spinosaurus</span><span class="ol thin" style="font-size:18px;color:#8dff5a">$1.8M/s</span>
{img("dino_Spino", 220, 180)}</div>
{stats()}{hotbar(1)}'''
screens.append(screen("01 Main HUD", hud))

# --- 02 Welcome back --------------------------------------------------------------------------
welcome = f'''<div class="panel" style="left:330px;top:110px;width:620px;height:490px">
{head("Welcome back!", "gold")}
<div style="display:flex;flex-direction:column;align-items:center;padding-top:18px;gap:14px">
<div class="muted" style="font-size:24px">Your dinos kept earning while you were away</div>
<div style="position:relative;width:540px;height:150px;border-radius:24px;border:4px solid {INK};background:#120d22;box-shadow:inset 0 6px 0 rgba(0,0,0,0.35);display:flex;align-items:center;justify-content:center;gap:10px">
{img("cash_XL", 170, 140)}<span class="ol" style="font-size:78px;color:#8dff5a">$4.18M</span></div>
<div style="display:flex;align-items:center;gap:10px">{clock(32)}<span class="ol thin" style="font-size:28px">Away for 13h 48m</span><span class="muted" style="font-size:18px">(pays up to 8h)</span></div>
{button("CLAIM", "green", 400, 86, 46, "margin-top:4px")}
</div></div>
<div style="position:absolute;left:276px;top:72px;transform:rotate(-14deg)">{img("egg_SpottedEgg", 90, 104)}</div>
<div style="position:absolute;left:900px;top:70px;transform:rotate(12deg)">{img("egg_CosmicEgg", 84, 98)}</div>'''
screens.append(screen("02 Welcome back", welcome, dim=True))

# --- 03 My Dinos ------------------------------------------------------------------------------
rows_data = [("Spino", "legendary", "DIAMOND", "#8fe4ff", "Spinosaurus", "HUGE", "$1.8M/s", "SELL $108M"),
             ("Brachio", "epic", "GOLD", "#ffd43b", "Brachiosaurus", "", "$60K/s", "SELL $3.6M"),
             ("TRex", "legendary", "", "", "T-Rex", "LARGE", "$10K/s", "SELL $600K"),
             ("Triceratops", "rare", "EMERALD", "#7ef0a0", "Triceratops", "BIG", "$5.6K/s", "SELL $336K")]
rows = []
for dino_id, rarity, mutation, mcolor, name, size, income, sell in rows_data:
    tag_html = f'<span class="ol thin" style="font-size:16px;color:{mcolor}">{mutation}</span>' if mutation else '<span style="font-size:16px">&nbsp;</span>'
    size_html = f'<span class="ol thin" style="font-size:16px;color:#ffe066">{size}</span>' if size else ""
    rows.append(f'''<div class="row"><div class="dtile" style="width:80px;height:80px;padding-top:4px;{tile_bg(rarity)}">{img("dino_" + dino_id, 70, 64)}</div>
<div style="flex:1;min-width:0;display:flex;flex-direction:column;gap:1px">{tag_html}<span class="ol" style="font-size:24px;white-space:nowrap">{name}</span><div style="display:flex;gap:8px;align-items:center">{size_html}<span class="ol thin" style="font-size:21px;color:#8dff5a">{income}</span></div></div>
<div style="display:flex;flex-direction:column;gap:7px">{button("PICK UP", "blue", 122, 38, 18)}{button(sell, "red", 122, 38, 16)}</div></div>''')
mydinos = f'''<div class="panel" style="left:790px;top:14px;width:470px;height:692px">
{head("My Dinos", "jungle", track(40, "#ffd166"))}
<div style="display:flex;gap:10px;padding:14px 16px 10px">
<div class="tab green" style="flex:1"><span class="ol thin">ON PLOT 8/14</span></div>
<div class="tab" style="flex:1;background:#120d22"><span class="ol thin" style="color:#cbbff0">BACKPACK 5</span></div></div>
<div style="display:flex;flex-direction:column;gap:8px;padding:0 16px">{"".join(rows)}</div>
<div style="position:absolute;left:16px;right:16px;bottom:16px">{button("EQUIP BEST", "yellow", 428, 66, 32)}</div></div>
{side_button(book(64), "Index", "left:24px;top:236px")}{side_button(bag(64), "Shop", "left:24px;top:372px")}{stats()}'''
screens.append(screen("03 My Dinos", mydinos))

# --- 04 Egg Shop (opened from the stall) ------------------------------------------------------
eggs = [("Dirty Egg", "Common", "x1", ("#f6ead2", "#d9bf91"), "DirtyEgg", button(f"{check(22)} EQUIPPED", "grey", 150, 54, 18)),
        ("Spotted Egg", "Uncommon", "x1.25", ("#d8f8e4", "#5cc98a"), "SpottedEgg", button("EQUIP", "blue", 150, 54, 26)),
        ("Golden Egg", "Rare", "x1.6", ("#fff3b8", "#ffb81f"), "GoldenEgg", button("$10K", "green", 150, 54, 28)),
        ("Lava Egg", "Epic", "x2.2", ("#ffd3c2", "#ff6a3d"), "LavaEgg", button("$250K", "red", 150, 54, 28)),
        ("Cosmic Egg", "Legendary", "x3", ("#e4d2ff", "#8a5cff"), "CosmicEgg", button("$8M", "red", 150, 54, 28))]
cards = []
for name, rarity_word, luck, (top, bottom), egg_id, btn in eggs:
    cards.append(f'''<div class="card" style="width:176px;height:380px;background:linear-gradient({top},{bottom});display:flex;flex-direction:column;align-items:center;padding-top:12px">
<span class="ol" style="font-size:25px;white-space:nowrap">{name}</span><span class="ol thin" style="font-size:18px;color:#ffe066">{rarity_word}</span>
<div class="glow" style="left:18px;top:74px;width:130px;height:130px"></div>
<div style="position:relative;margin-top:8px">{img("egg_" + egg_id, 120, 140)}</div>
<div style="margin-top:6px;background:{INK};border-radius:12px;padding:3px 12px"><span class="ol thin" style="font-size:19px;color:#8dff5a">LUCK {luck}</span></div>
<div style="position:absolute;bottom:16px">{btn}</div></div>''')
eggshop = f'''<div class="panel" style="left:120px;top:90px;width:1040px;height:540px">
{head("Egg Shop", "sky")}
<div style="display:flex;gap:16px;padding:26px 30px 0">{"".join(cards)}</div>
<div class="muted" style="position:absolute;left:0;right:0;bottom:12px;text-align:center;font-size:18px">Better eggs multiply the luck of every throw</div></div>'''
screens.append(screen("04 Egg Shop", eggshop, dim=True))

# --- 05 Shop ---------------------------------------------------------------------------------
def limited_card(width):
    return f'''<div class="card" style="width:{width}px;height:282px;background:linear-gradient(120deg,#ffd23f,#ff7a2f 55%,#ff4fb8)">
<div style="position:absolute;left:10px;top:-40px;opacity:0.9">{img("sunburst", 330, 330)}</div>
<div class="glow" style="left:60px;top:30px;width:220px;height:200px"></div>
<div style="position:absolute;left:18px;top:30px">{img("dino_Spino", 340, 240)}</div>
<div style="position:absolute;left:18px;top:14px">{tag("BEST DEAL!", "gold")}</div>
<div style="position:absolute;left:{width - 430}px;top:18px;width:410px;display:flex;flex-direction:column;align-items:center;gap:8px">
<span class="ol thin" style="font-size:20px;color:#fff3c4">LAVA · HUGE</span><span class="ol" style="font-size:40px;white-space:nowrap">Lava Spinosaurus</span>
<div style="width:390px;border-radius:20px;border:4px solid {INK};background:rgba(27,18,48,0.55);display:flex;flex-direction:column;align-items:center;padding:6px 0">
<div style="display:flex;align-items:center;gap:8px">{cash(44)}<span class="ol" style="font-size:44px;color:#8dff5a">x9</span></div><span class="ol thin" style="font-size:19px">your best dino's $/s</span></div>
{robux("499", 380, 60, 30)}</div></div>'''

def egg_card(width):
    hatch = "".join(f'<div style="display:flex;flex-direction:column;align-items:center;gap:2px"><div class="dtile" style="width:84px;height:70px;padding-top:2px;{tile_bg(r)}">{img("dino_" + d, 70, 58)}</div><span class="ol thin" style="font-size:16px;color:#8dff5a">{p}</span></div>'
                    for d, r, p in [("Raptor", "legendary", "x1"), ("TRex", "legendary", "x2"), ("Brachio", "epic", "x3"), ("Spino", "legendary", "x5"), ("Stego", "epic", "x9")])
    return f'''<div class="card" style="width:{width}px;height:240px;background:linear-gradient(120deg,#c58bff,#7b4dff)">
<div style="position:absolute;left:14px;top:12px">{info(38)}</div>
<div class="glow" style="left:24px;top:36px;width:190px;height:190px"></div>
<div style="position:absolute;left:46px;top:40px">{img("egg_PrismEgg", 150, 176)}</div>
<div style="position:absolute;left:230px;top:14px;display:flex;flex-direction:column;gap:6px">
<span class="ol" style="font-size:38px">Prism Egg</span><span class="ol thin" style="font-size:20px">Hatch up to <span style="color:#8dff5a">x9</span> your best dino!</span>
<div style="display:flex;gap:8px;margin-top:4px">{hatch}</div></div>
<div style="position:absolute;right:20px;top:20px;display:flex;flex-direction:column;align-items:center;gap:6px">
<span class="ol thin" style="font-size:20px">Buy 1</span>{robux("80", 150, 58, 30)}<span class="ol thin" style="font-size:20px">Buy 3</span>{robux("200", 150, 58, 30)}</div></div>'''

def luck_card(width):
    return f'''<div class="card" style="width:{width}px;height:170px;background:linear-gradient(120deg,#9cf28f,#2fbf5a)">
<div style="position:absolute;left:14px;top:12px">{info(34)}</div>
<div style="position:absolute;left:40px;top:6px">{img("clover", 160, 160)}</div>
<div style="position:absolute;left:230px;top:20px;display:flex;flex-direction:column;gap:4px">
<span class="ol" style="font-size:36px">Server Luck</span><span class="ol thin" style="font-size:19px">2x luck for everyone in the server</span>
<div style="display:flex;align-items:center;gap:10px"><span class="ol" style="font-size:46px">x1</span><span class="ol" style="font-size:34px;color:#fff3c4">▸</span><span class="ol" style="font-size:52px;color:#ffe066">x2</span><span class="ol thin" style="font-size:20px;margin-left:8px">+15 min</span></div></div>
<div style="position:absolute;right:20px;top:54px">{robux("19", 150, 62, 32)}</div></div>'''

def pack_cards(kind):
    if kind == "cash":
        items = [("cash_S", "+$12.5K", "24", None), ("cash_M", "+$75K", "59", ("+30% MORE", "greent")), ("cash_L", "+$400K", "79", ("+50% MORE", "purplet")), ("cash_XL", "+$2.4M", "199", ("+100% MORE", "gold"))]
        bg, icon, color = "linear-gradient(#a6f08f,#3fbf5a)", cash(28), "#8dff5a"
    else:
        items = [("bolts_S", "+5", "2", None), ("bolts_M", "+30", "9", ("+30% MORE", "greent")), ("bolts_L", "+150", "39", ("+50% MORE", "purplet")), ("bolts_XL", "+500", "99", ("+100% MORE", "gold"))]
        bg, icon, color = "linear-gradient(#ffe066,#ff8a1f)", bolt(28), "#ffffff"
    cards_html = []
    for art, amount, price, t in items:
        t_html = f'<div style="position:absolute;top:-2px;left:0;right:0;display:flex;justify-content:center">{tag(t[0], t[1], "font-size:16px")}</div>' if t else ""
        cards_html.append(f'''<div style="position:relative;padding-top:12px"><div class="card" style="width:226px;height:250px;background:{bg};display:flex;flex-direction:column;align-items:center;padding-top:14px">
{img(art, 190, 118)}<div style="display:flex;align-items:center;gap:6px">{icon}<span class="ol" style="font-size:28px;color:{color}">{amount}</span></div>
<div style="position:absolute;bottom:12px">{robux(price, 190, 46, 24)}</div></div>{t_html}</div>''')
    return f'<div style="display:flex;gap:14px">{"".join(cards_html)}</div>'

def pass_cards():
    return f'''<div style="display:flex;gap:16px">
<div class="card" style="width:463px;height:200px;background:linear-gradient(120deg,#7fd4ff,#2f7fe6)"><span class="ol" style="position:absolute;left:20px;top:12px;font-size:32px">x2 Cash</span>
<div class="glow" style="left:16px;top:50px;width:160px;height:150px"></div><div style="position:absolute;left:24px;top:60px">{img("cash_L", 150, 120)}</div>
<div style="position:absolute;left:122px;top:138px">{tag("x2", "gold", "font-size:22px")}</div>
<span class="ol thin" style="position:absolute;left:200px;top:62px;width:250px;text-align:center;font-size:22px">Every dino earns double, forever!</span>
<div style="position:absolute;left:220px;top:126px">{robux("99", 210, 58, 30)}</div></div>
<div class="card" style="width:463px;height:200px;background:linear-gradient(120deg,#d3a3ff,#7b4dff)"><span class="ol" style="position:absolute;left:20px;top:12px;font-size:32px">x2 Training</span>
<div class="glow" style="left:16px;top:50px;width:160px;height:150px"></div><div style="position:absolute;left:30px;top:60px">{img("bolts_M", 140, 116)}</div>
<div style="position:absolute;left:122px;top:138px">{tag("x2", "gold", "font-size:22px")}</div>
<span class="ol thin" style="position:absolute;left:200px;top:62px;width:250px;text-align:center;font-size:22px">Double XP on every squat!</span>
<div style="position:absolute;left:220px;top:126px">{robux("149", 210, 58, 30)}</div></div></div>'''

def dino_deals():
    def deal(dino, name, mult, price, t, bg, rarity):
        return f'''<div class="card" style="width:463px;height:210px;background:{bg}">
<div style="position:absolute;left:18px;top:12px">{tag(t[0], t[1])}</div>
<span class="ol" style="position:absolute;left:18px;top:52px;font-size:26px;white-space:nowrap">{name}</span>
<div style="position:absolute;left:18px;top:96px;display:flex;align-items:center;gap:6px">{cash(34)}<span class="ol" style="font-size:34px;color:#8dff5a">{mult}</span></div>
<span class="ol thin" style="position:absolute;left:18px;top:138px;font-size:16px">your best dino's $/s</span>
<div style="position:absolute;left:18px;top:160px">{robux(price, 170, 40, 22)}</div>
<div class="dtile" style="position:absolute;right:14px;top:14px;width:176px;height:178px;{tile_bg(rarity)}">{img("dino_" + dino, 164, 150, "margin-top:4px")}</div></div>'''
    return f'''<div style="display:flex;gap:16px">{deal("Brachio", "Brachiosaurus", "x3", "299", ("HOT DEAL!", "purplet"), "linear-gradient(120deg,#a9b8ff,#6a6cf0)", "epic")}
{deal("Ankylo", "Ankylosaurus", "x1.5", "199", ("GOOD PRICE", "greent"), "linear-gradient(120deg,#ffe2c2,#f0a868)", "uncommon")}</div>'''

def free_card():
    return f'''<div style="display:flex;justify-content:center"><div class="card" style="width:680px;height:170px;background:linear-gradient(120deg,#7fe7ff,#3f8cff)">
<div class="dtile" style="position:absolute;left:16px;top:14px;width:150px;height:134px;{tile_bg("uncommon")}">{img("dino_Gallimimus", 136, 110, "margin-top:2px")}</div>
<div style="position:absolute;left:190px;top:16px;display:flex;flex-direction:column;gap:4px"><span class="ol" style="font-size:34px">Free Dino!</span>
<span class="ol thin" style="font-size:20px">Claim your free Gallimimus</span><span class="ol thin" style="font-size:20px;color:#8dff5a">$3/s on your plot</span></div>
<div style="position:absolute;right:20px;top:52px">{button("CLAIM", "green", 160, 62, 30)}</div></div></div>'''

def shop_body(width):
    return f'''{divider("Limited")}{limited_card(width)}<div style="height:16px"></div>{egg_card(width)}
{divider("Boosts")}{luck_card(width)}
{divider("Packs")}{pack_cards("cash")}<div style="height:16px"></div>{pack_cards("power")}
{divider("Passes")}{pass_cards()}
{divider("Dinos")}{dino_deals()}
{divider("Free")}{free_card()}<div style="height:24px"></div>'''

gift_btn = f'''<div class="btn blue" style="position:absolute;width:200px;height:68px;font-size:32px;gap:6px">{img("gift", 70, 70, "margin-left:-30px;margin-top:-16px")}GIFT!</div>'''

shop_view = f'''<div class="panel" style="left:150px;top:24px;width:980px;height:672px">
{head("Shop", "sun", bag(50))}
<div style="position:absolute;left:24px;right:24px;top:96px;height:560px;overflow:hidden">{shop_body(942)}</div>
<div style="position:absolute;right:8px;top:120px;width:10px;height:150px;border-radius:5px;background:#5b4a8c"></div></div>
{gift_btn.replace('position:absolute;', 'position:absolute;right:120px;bottom:12px;')}'''
screens.append(screen("05 Shop", shop_view, dim=True))

shop_full = f'''<div class="panel" style="left:150px;top:24px;width:980px;height:2500px">
{head("Shop", "sun", bag(50))}
<div style="position:absolute;left:24px;right:24px;top:96px">{shop_body(942)}</div></div>'''
screens.append(screen("05b Shop full scroll", shop_full, dim=True, height=2560))

# --- 06 Dino Index ---------------------------------------------------------------------------
def biome_block(biome_id, name, colors, dinos, found):
    tiles = []
    for i, (dino_id, dino_name, odds) in enumerate(dinos):
        rarity = ORDER[i]
        tiles.append(dino_tile(dino_id, dino_name, rarity, 234, 150, found=i < found, odds=odds if i < found else None, name_size=21))
    complete = found == len(dinos)
    reward = f'''<div class="dtile" style="width:234px;height:150px;background:linear-gradient(#3a3060,#2a2348);justify-content:center;gap:6px">
<span class="ol thin" style="font-size:19px;color:#ffe066">COMPLETE REWARD</span><span class="ol" style="font-size:24px;color:#8dff5a">+10% cash</span><span class="ol" style="font-size:24px;color:#6fe3ff">+5% luck</span>
{f'<div style="position:absolute;right:8px;top:8px">{check(28)}</div>' if complete else ''}</div>'''
    pct = found / len(dinos)
    return f'''<div style="display:flex;gap:16px;margin-bottom:18px">
<div class="card" style="width:250px;height:368px;background:linear-gradient({colors[0]},{colors[1]});display:flex;flex-direction:column;align-items:center;padding-top:14px">
<span class="ol" style="font-size:44px;white-space:nowrap">{name}</span><div style="margin-top:18px">{img("biome_" + biome_id, 220, 236)}</div></div>
<div style="display:flex;flex-direction:column;gap:12px">
<div style="display:flex;gap:12px">{"".join(tiles[:3])}</div><div style="display:flex;gap:12px">{"".join(tiles[3:])}{reward}</div>
<div class="bar" style="width:726px;height:44px;border-radius:16px"><div class="fill" style="width:{pct * 100:.0f}%;border-radius:12px;background:linear-gradient(#8af25a,#3fbf22)"></div><span class="ol" style="position:absolute;left:0;right:0;top:4px;text-align:center;font-size:28px">{found}/{len(dinos)}</span></div>
</div></div>'''

index_blocks = "".join(biome_block(*b) for b in BIOMES)
index = f'''<div class="panel" style="left:110px;top:24px;width:1060px;height:672px">
{head("Dino Index", "berry")}
<div style="position:absolute;left:24px;right:24px;top:108px;height:436px;overflow:hidden">{index_blocks}</div>
<div style="position:absolute;left:1036px;top:120px;width:10px;height:120px;border-radius:5px;background:#5b4a8c"></div>
<div class="bar" style="position:absolute;left:90px;right:30px;bottom:24px;height:72px;border-radius:24px"><div class="fill" style="width:60%;border-radius:20px;background:linear-gradient(#8af25a,#3fbf22)"></div>
<span class="ol" style="position:absolute;left:0;right:0;top:12px;text-align:center;font-size:40px">Unlocked: 9/15</span></div>
<div style="position:absolute;left:24px;bottom:10px;transform:rotate(-12deg)">{book(104)}</div></div>'''
screens.append(screen("06 Dino Index", index, dim=True))

# --- 07 Training HUD -------------------------------------------------------------------------
training = f'''<div style="position:absolute;left:0;right:0;top:88px;display:flex;flex-direction:column;align-items:center"><span class="ol" style="font-size:84px;color:#ffb13b">LEVEL UP!</span><span class="ol" style="font-size:36px;color:#6fe3ff;display:flex;align-items:center;gap:6px">{bolt(40)} Throw Power +20</span></div>
<div style="position:absolute;left:900px;top:260px;width:124px;height:124px;border-radius:50%;border:5px solid {INK};background:radial-gradient(circle at 35% 30%,#e3b8ff,#9a4ff0 70%);box-shadow:0 0 0 6px #ffffff,0 0 0 11px {INK};display:flex;align-items:center;justify-content:center"><span class="ol" style="font-size:54px">x2</span></div>
<div style="position:absolute;left:190px;top:330px;display:flex;flex-direction:column;align-items:center"><span class="ol" style="font-size:40px;color:#8dff5a">$75</span><span class="ol thin" style="font-size:22px">+3 XP / rep</span><div style="width:120px;height:34px;margin-top:64px;border-radius:50%;background:#ffb13b;border:4px solid {INK}"></div></div>
<div class="ol thin" style="position:absolute;left:0;right:0;bottom:96px;text-align:center;font-size:24px">+2 XP</div>
<div style="position:absolute;left:0;right:0;bottom:128px;display:flex;justify-content:center">{button("STOP", "red", 200, 70, 36)}</div>
<div class="bar" style="position:absolute;left:320px;bottom:26px;width:640px;height:60px;border-radius:22px;border-width:5px"><div class="fill" style="width:63%;border-radius:16px;background:linear-gradient(#8ff0ff,#2fb6e6)"></div>
<span class="ol" style="position:absolute;left:20px;top:8px;font-size:32px">Level 12</span><span class="ol" style="position:absolute;right:20px;top:8px;font-size:32px">37 / 59 XP</span></div>
<div class="stat" style="left:24px;bottom:104px">{bolt(54)}<span class="ol" style="font-size:52px;color:#6fe3ff">4,823</span></div>
<div class="stat" style="left:24px;bottom:34px">{cash(56)}<span class="ol" style="font-size:52px;color:#8dff5a">$778.4K</span></div>'''
screens.append(screen("07 Training HUD", training))

# --- 08 Motion & colour notes ------------------------------------------------------------------
motion = [("Spin", "Dino and egg models turn slowly on every tile (one turn every 6 s, in a ViewportFrame). Where a picture is used instead, it bobs 6 px and tilts ±4° every 2 s."),
          ("Sunburst", "Light rays behind Limited and Featured items rotate once every 12 s and pulse brighter."),
          ("Pulse", "Robux and CLAIM buttons breathe: scale 1 → 1.06 → 1 every 1.2 s. Pressing squashes to 0.94."),
          ("Wiggle", "Tags (BEST DEAL!, LIMITED, +50% MORE) rock ±5° every 2 s so the eye lands on them."),
          ("Shimmer", "A white shine sweeps across rare cards and the Prism Egg every 3 s; rainbow text scrolls."),
          ("Count up", "Cash amounts (Welcome back, packs) roll up from 0 in 0.8 s with a tick sound."),
          ("Pop in", "Panels open from 85% to 100% with a small overshoot (0.25 s, back easing).")]
colour = [("Green = buy / go", "Every main action button. Players learn one colour means 'press me'."),
          ("Yellow & orange", "Warm, high-energy colours that grab attention: titles, limited offers, power."),
          ("Red = urgent", "LIMITED tags, close and sell. Used sparingly so it keeps its punch."),
          ("Purple & gold = rare", "Premium and high-rarity items; gold tags mark the best deals."),
          ("Rainbow = special", "Only for the rarest and limited things, never for everyday buttons."),
          ("Bright on dark", "Saturated cards on a dark panel give strong contrast that kids read at a glance."),
          ("One rarity ladder", "grey → green → blue → purple → gold, the order players know from other games.")]
def note_list(title, items, accent):
    rows = "".join(f'<div class="note"><span class="ol" style="font-size:22px;color:{accent}">{t}</span><span class="muted" style="font-size:16px">{d}</span></div>' for t, d in items)
    return f'<div style="display:flex;flex-direction:column;gap:8px;width:580px"><span class="ol" style="font-size:34px">{title}</span>{rows}</div>'
notes = f'''<div style="position:absolute;left:0;top:0;width:1280px;height:720px;background:#150f24"></div>
<div style="position:absolute;left:40px;top:24px;display:flex;gap:40px">{note_list("Motion", motion, "#ffcf3f")}{note_list("Colour", colour, "#8dff5a")}</div>'''
screens.append(f'<section class="screen" data-name="08 Motion and colour notes" style="height:720px">{notes}</section>')

html = f'''<!doctype html><html><head><meta charset="utf-8"><title>Throw Eggs UI v2</title><style>{CSS}</style></head><body>{"".join(screens)}</body></html>'''
out = HERE / "ui.html"
out.write_text(html)
print(out, len(html) // 1024, "KB", len(screens), "screens")
