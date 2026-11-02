"""Builds ui.html: the Throw Eggs for Dinosaurs UI mock-ups, one .screen per Figma frame."""
import pathlib

INK = "#1b1230"

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

def egg(size=64, color="#f3e6c8", spot="#c9a46a"):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><path d="M32 3 C18 3 9 25 9 39 C9 53 19 61 32 61 C45 61 55 53 55 39 C55 25 46 3 32 3 Z" fill="{color}" stroke="{INK}" stroke-width="4"/><circle cx="24" cy="34" r="5" fill="{spot}"/><circle cx="40" cy="44" r="6.5" fill="{spot}"/><circle cx="37" cy="22" r="3.5" fill="{spot}"/><ellipse cx="21" cy="19" rx="4" ry="7" transform="rotate(25 21 19)" fill="#ffffff" opacity="0.6"/></svg>'''

def clock(size=32):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><circle cx="32" cy="32" r="26" fill="#ffffff" stroke="{INK}" stroke-width="5"/><path d="M32 16 V32 L43 39" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>'''

def clover(size=40):
    s = f'fill="#4fd15a" stroke="{INK}" stroke-width="3.5"'
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><path d="M32 40 Q30 52 22 60" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/><circle cx="22" cy="22" r="11" {s}/><circle cx="42" cy="22" r="11" {s}/><circle cx="22" cy="40" r="11" {s}/><circle cx="42" cy="40" r="11" {s}/><circle cx="32" cy="31" r="6" fill="#9cf28f"/></svg>'''

def meteor(size=34):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><path d="M6 6 L34 22 L22 34 Z" fill="#ffb13b"/><path d="M14 4 L40 18" stroke="#ff7a2f" stroke-width="5" stroke-linecap="round"/><path d="M4 14 L18 40" stroke="#ff7a2f" stroke-width="5" stroke-linecap="round"/><circle cx="40" cy="40" r="17" fill="#ff7a2f" stroke="{INK}" stroke-width="4"/><circle cx="35" cy="36" r="4" fill="#c4451a"/><circle cx="46" cy="45" r="3" fill="#c4451a"/></svg>'''

def coin(size=26):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><path d="M32 4 L56 18 V46 L32 60 L8 46 V18 Z" fill="#ffd43b" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/><path d="M32 18 L44 25 V39 L32 46 L20 39 V25 Z" fill="none" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/></svg>'''

def check(size=26):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><path d="M10 34 L26 50 L54 16" fill="none" stroke="{INK}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/><path d="M10 34 L26 50 L54 16" fill="none" stroke="#ffffff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></svg>'''

def cross(size=30):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64"><path d="M14 14 L50 50 M50 14 L14 50" stroke="{INK}" stroke-width="18" stroke-linecap="round"/><path d="M14 14 L50 50 M50 14 L14 50" stroke="#ffffff" stroke-width="8" stroke-linecap="round"/></svg>'''

def dino(width=80, color="#7ee06a", shadow=False):
    fill = "#120c20" if shadow else color
    eye = "" if shadow else f'<circle cx="12" cy="12" r="2.6" fill="{INK}"/>'
    return f'''<svg width="{width}" height="{width * 0.8:.0f}" viewBox="0 0 80 64"><g fill="{fill}" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"><rect x="54" y="28" width="22" height="9" rx="3"/><rect x="30" y="44" width="8" height="15" rx="2.5"/><rect x="46" y="44" width="8" height="15" rx="2.5"/><rect x="26" y="25" width="31" height="21" rx="5"/><rect x="18" y="13" width="11" height="22" rx="3"/><rect x="5" y="5" width="24" height="15" rx="5"/></g>{eye}</svg>'''

RARITY = {
    "common": ("#d7dce4", "#a8b0bd"),
    "uncommon": ("#a6f08f", "#5cc94a"),
    "rare": ("#8fd3ff", "#3d9be8"),
    "epic": ("#d4a6ff", "#9a5ae6"),
    "legendary": ("#ffe27a", "#f2a91c"),
    "mythic": ("#ffa6d2", "#ec4f9c"),
}

def tile(rarity, w, h):
    top, bottom = RARITY[rarity]
    return f'background:linear-gradient({top},{bottom});width:{w}px;height:{h}px;'

def button(text, color, w, h, size=30, extra=""):
    return f'<div class="btn {color}" style="width:{w}px;height:{h}px;font-size:{size}px;{extra}">{text}</div>'

def head(title, color, icon, badge="", close=True):
    badge_html = f'<div class="badge">{badge}</div>' if badge else ""
    close_html = f'<div class="close">{cross(28)}</div>' if close else ""
    return f'''<div class="head {color}"><div class="dots"></div><div class="headtitle">{icon}<span class="ol" style="font-size:44px">{title}</span>{badge_html}</div>{close_html}</div>'''

SCENE = '''<div class="scene"><div class="hill" style="left:-80px;top:300px;width:520px;height:260px"></div><div class="hill" style="left:760px;top:320px;width:640px;height:240px"></div><div class="ground"></div><div class="studrow"></div></div>'''

def screen(name, inner, dim=False):
    overlay = '<div class="dim"></div>' if dim else ""
    return f'<section class="screen" data-name="{name}">{SCENE}{overlay}{inner}</section>'

def side_button(icon, label, style):
    return f'<div class="sidebtn" style="{style}">{icon}<span class="ol sidelabel">{label}</span></div>'

def stats():
    return f'''<div class="stat" style="left:24px;bottom:104px">{bolt(54)}<span class="ol" style="font-size:52px;color:#6fe3ff">4,823</span></div>
<div class="stat" style="left:24px;bottom:34px">{cash(56)}<span class="ol" style="font-size:52px;color:#8dff5a">$778.4K</span></div>
<span class="ol" style="position:absolute;left:94px;bottom:12px;font-size:21px">+$1.24K/s</span>'''

def hotbar(selected=1):
    dinos = [("legendary", "#ffb13b", "$1.8M/s"), ("epic", "#b77bff", "$60K/s"), ("rare", "#5ab8ff", "$5.6K/s"),
             ("rare", "#5ab8ff", "$4.1K/s"), ("uncommon", "#7ee06a", "$900/s"), ("uncommon", "#7ee06a", "$250/s"),
             ("common", "#c9ced8", "$25/s"), ("common", "#c9ced8", "$10/s"), None, None]
    slots = []
    for index, d in enumerate(dinos):
        number = (index + 1) % 10
        if d is None:
            slots.append(f'<div class="slot empty"><span class="ol slotnum">{number}</span></div>')
            continue
        rarity, color, income = d
        cls = "slot sel" if index + 1 == selected else "slot"
        slots.append(f'''<div class="{cls}" style="{tile(rarity, 62, 74)}"><span class="ol slotcash">{income}</span>{dino(50, color)}<span class="ol slotnum">{number}</span></div>''')
    return f'<div class="hotbar">{"".join(slots)}</div>'

CSS = f"""
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0e0b18;font-family:'Fredoka One','Fredoka','Arial Rounded MT Bold',sans-serif;color:#fff;padding:40px}}
.screen{{width:1280px;height:720px;position:relative;overflow:hidden;margin-bottom:60px;border-radius:0}}
.scene{{position:absolute;left:0;top:0;width:1280px;height:720px;background:linear-gradient(#69b9ff,#bfe6ff 62%)}}
.hill{{position:absolute;border-radius:50%;background:#4aa84a}}
.ground{{position:absolute;left:0;top:430px;width:1280px;height:290px;background:linear-gradient(#6fd05b,#4fb43f)}}
.studrow{{position:absolute;left:0;top:430px;width:1280px;height:290px;background:repeating-linear-gradient(90deg,rgba(255,255,255,0.07) 0 64px,rgba(0,0,0,0.05) 64px 128px)}}
.dim{{position:absolute;left:0;top:0;width:1280px;height:720px;background:rgba(14,8,30,0.62)}}
.ol{{color:#fff;-webkit-text-stroke:5px {INK};paint-order:stroke fill;letter-spacing:0.5px;line-height:1.1}}
.ol.thin{{-webkit-text-stroke:3px {INK}}}
.muted{{color:#cbbff0;font-family:'Fredoka','Fredoka One',sans-serif;font-weight:600}}
.btn{{display:flex;align-items:center;justify-content:center;gap:8px;border:4px solid {INK};border-radius:18px;box-shadow:inset 0 -7px 0 rgba(0,0,0,0.22),inset 0 4px 0 rgba(255,255,255,0.35),0 5px 0 {INK};color:#fff;-webkit-text-stroke:4px {INK};paint-order:stroke fill}}
.green{{background:linear-gradient(#8af25a,#4cc12a)}}
.blue{{background:linear-gradient(#6cc4ff,#2f8ce6)}}
.red{{background:linear-gradient(#ff7a6b,#e8392f)}}
.yellow{{background:linear-gradient(#ffe066,#f5a815)}}
.grey{{background:linear-gradient(#a9a3bd,#77708f)}}
.panel{{position:absolute;background:#241b3a;border:5px solid {INK};border-radius:30px;box-shadow:0 10px 0 rgba(0,0,0,0.35),inset 0 0 0 4px #3b2d5e;overflow:hidden}}
.head{{height:86px;position:relative;border-bottom:5px solid {INK};display:flex;align-items:center;justify-content:center}}
.head.amber{{background:linear-gradient(#ffd23f,#ff9a1f)}}
.head.jungle{{background:linear-gradient(#6fe27a,#21a352)}}
.head.teal{{background:linear-gradient(#5fe6f2,#1f9ad8)}}
.head.violet{{background:linear-gradient(#c06bff,#ff5ca8)}}
.head.indigo{{background:linear-gradient(#6f9bff,#3d55dd)}}
.dots{{position:absolute;left:0;top:0;right:0;bottom:0;background-image:radial-gradient(circle,rgba(255,255,255,0.22) 22%,transparent 24%);background-size:26px 26px;background-position:0 6px}}
.headtitle{{position:relative;display:flex;align-items:center;gap:12px;margin-right:40px}}
.badge{{background:{INK};border-radius:14px;padding:4px 14px;font-size:24px;color:#ffe066}}
.close{{position:absolute;right:16px;top:14px;width:56px;height:56px;border-radius:16px;border:4px solid {INK};background:linear-gradient(#ff7a6b,#e8392f);box-shadow:inset 0 -6px 0 rgba(0,0,0,0.22),0 4px 0 {INK};display:flex;align-items:center;justify-content:center}}
.sidebtn{{position:absolute;width:104px;height:104px;border-radius:28px;border:5px solid {INK};background:linear-gradient(#4a3a75,#2a2045);box-shadow:inset 0 0 0 4px #5b4a8c,inset 0 -8px 0 rgba(0,0,0,0.25),0 5px 0 {INK};display:flex;align-items:flex-start;justify-content:center;padding-top:10px}}
.sidelabel{{position:absolute;bottom:-16px;left:-10px;right:-10px;text-align:center;font-size:27px}}
.stat{{position:absolute;display:flex;align-items:center;gap:10px}}
.hotbar{{position:absolute;left:316px;bottom:14px;display:flex;gap:6px;align-items:flex-end}}
.slot{{position:relative;width:62px;height:74px;border-radius:15px;border:4px solid {INK};display:flex;align-items:center;justify-content:center;box-shadow:inset 0 -5px 0 rgba(0,0,0,0.2)}}
.slot.empty{{background:rgba(27,18,48,0.55)}}
.slot.sel{{transform:translateY(-10px);outline:4px solid #ffffff}}
.slotcash{{position:absolute;top:-15px;left:-8px;right:-8px;text-align:center;font-size:15px;white-space:nowrap;color:#8dff5a;-webkit-text-stroke:3px {INK}}}
.slotnum{{position:absolute;left:4px;bottom:0px;font-size:17px;-webkit-text-stroke:3px {INK}}}
.pill{{position:absolute;display:flex;align-items:center;gap:8px;height:48px;padding:0 16px 0 10px;border-radius:18px;border:4px solid {INK};background:rgba(36,27,58,0.92);font-size:24px}}
.row{{display:flex;align-items:center;gap:12px;height:98px;padding:0 12px;border-radius:20px;border:4px solid {INK};background:#33275a;box-shadow:inset 0 -5px 0 rgba(0,0,0,0.25)}}
.dinotile{{border-radius:16px;border:4px solid {INK};display:flex;align-items:center;justify-content:center;box-shadow:inset 0 -5px 0 rgba(0,0,0,0.18)}}
.tab{{height:46px;border-radius:15px;border:4px solid {INK};display:flex;align-items:center;justify-content:center;font-size:22px}}
.card{{position:relative;width:170px;height:344px;border-radius:24px;border:5px solid {INK};display:flex;flex-direction:column;align-items:center;padding-top:14px;box-shadow:inset 0 -7px 0 rgba(0,0,0,0.18),0 5px 0 {INK}}}
.tier{{background:{INK};border-radius:12px;padding:3px 12px;font-size:17px;color:#ffe066}}
.luck{{display:flex;align-items:center;gap:4px;font-size:19px}}
.bar{{position:relative;height:26px;border-radius:13px;border:4px solid {INK};background:#160f28;overflow:hidden}}
.fill{{position:absolute;left:0;top:0;bottom:0;border-radius:9px}}
.swatch{{width:112px;height:112px;border-radius:22px;border:5px solid {INK};display:flex;align-items:flex-end;padding:8px;font-size:15px}}
.label{{font-size:22px;margin-bottom:12px;color:#ffe066}}
"""

screens = []

# 1. Style guide
swatches = [("Ink", INK), ("Panel", "#241b3a"), ("Row", "#33275a"), ("Power", "#6fe3ff"), ("Cash", "#8dff5a"),
            ("Amber", "#ffb13b"), ("Jungle", "#21a352"), ("Teal", "#1f9ad8"), ("Violet", "#c06bff")]
sw = "".join(f'<div class="swatch" style="background:{c}"><span class="ol thin">{n}<br>{c}</span></div>' for n, c in swatches)
rar = "".join(f'<div style="display:flex;flex-direction:column;align-items:center;gap:6px"><div class="dinotile" style="{tile(r, 96, 96)}">{dino(74, "#ffffff" if r == "common" else RARITY[r][1])}</div><span class="ol thin" style="font-size:18px">{r.upper()}</span></div>' for r in RARITY)
icons = "".join(f'<div style="width:84px;height:84px;display:flex;align-items:center;justify-content:center">{i}</div>' for i in [bolt(64), cash(64), book(64), bag(64), track(64), egg(64), clover(60), meteor(60), clock(56), coin(56), check(52), cross(52)])
style_guide = f'''<div style="position:absolute;inset:0;background:#150f24"></div>
<div style="position:absolute;left:48px;top:36px"><div class="ol" style="font-size:54px">Throw Eggs for Dinosaurs · UI kit</div><div class="muted" style="font-size:22px;margin-top:6px">Chunky cartoon stickers: thick ink outlines, glossy 3D buttons, dino-scale dot pattern on headers. Font: Fredoka One (Roblox: FredokaOne).</div></div>
<div style="position:absolute;left:48px;top:150px"><div class="label">Colours</div><div style="display:flex;gap:14px">{sw}</div></div>
<div style="position:absolute;left:48px;top:330px"><div class="label">Buttons</div><div style="display:flex;gap:16px;align-items:center">{button("CLAIM", "green", 200, 72, 34)}{button("PICK UP", "blue", 170, 60, 26)}{button("SELL", "red", 150, 60, 26)}{button("EQUIP BEST", "yellow", 230, 64, 28)}{button("OWNED", "grey", 150, 60, 26)}<div class="close" style="position:relative;right:auto;top:auto">{cross(28)}</div></div></div>
<div style="position:absolute;left:48px;top:434px"><div class="label">Rarity tiles</div><div style="display:flex;gap:18px">{rar}</div></div>
<div style="position:absolute;left:48px;top:616px"><div class="label" style="margin-bottom:4px">Icons</div><div style="display:flex;gap:6px">{icons}</div></div>
<div style="position:absolute;left:820px;top:440px;display:flex;flex-direction:column;gap:6px"><div class="label">Type</div><span class="ol" style="font-size:56px">Headline 56</span><span class="ol" style="font-size:36px">Title 36</span><span class="ol" style="font-size:24px">Label 24</span><span class="muted" style="font-size:20px">Body 20 · Fredoka SemiBold</span></div>'''
screens.append(f'<section class="screen" data-name="00 Style guide">{style_guide}</section>')

# 2. Main HUD
hud = f'''{side_button(book(64), "Index", "left:24px;top:236px")}
{side_button(bag(64), "Shop", "left:24px;top:372px")}
{side_button(track(64), "Dinos", "right:24px;top:304px")}
<div class="pill" style="right:20px;top:16px">{meteor(34)}<span class="ol thin" style="color:#ffb13b">METEOR SHOWER</span><span class="ol thin">9:41</span></div>
<div class="pill" style="right:20px;top:72px">{clover(34)}<span class="ol thin" style="color:#8dff5a">SERVER LUCK x2</span><span class="ol thin">12:04</span></div>
<div class="ol" style="position:absolute;left:0;right:0;top:118px;text-align:center;font-size:30px;color:#ffe066">Plot upgraded! It now holds 10 dinos</div>
{stats()}{hotbar(1)}'''
screens.append(screen("01 Main HUD", hud))

# 3. Welcome back
welcome = f'''<div class="panel" style="left:330px;top:120px;width:620px;height:470px">
{head("Welcome back!", "amber", egg(46, "#fff1d6", "#f2a91c"), close=False)}
<div style="display:flex;flex-direction:column;align-items:center;padding-top:22px;gap:16px">
<div class="muted" style="font-size:24px">Your dinos kept earning while you were away</div>
<div style="width:520px;height:118px;border-radius:24px;border:4px solid {INK};background:#170f28;box-shadow:inset 0 6px 0 rgba(0,0,0,0.35);display:flex;align-items:center;justify-content:center;gap:16px">{cash(76)}<span class="ol" style="font-size:76px;color:#8dff5a">$4.18M</span></div>
<div style="display:flex;align-items:center;gap:10px">{clock(32)}<span class="ol thin" style="font-size:28px">Away for 13h 48m</span><span class="muted" style="font-size:18px">(pays up to 8h)</span></div>
{button("CLAIM", "green", 380, 84, 44, "margin-top:6px")}
</div></div>
<div style="position:absolute;left:300px;top:96px;transform:rotate(-16deg)">{egg(70, "#a6f08f", "#3fae4e")}</div>
<div style="position:absolute;left:908px;top:92px;transform:rotate(14deg)">{egg(64, "#8fd3ff", "#2f7fd0")}</div>'''
screens.append(screen("02 Welcome back", welcome, dim=True))

# 4. My Dinos
rows_data = [("legendary", "#ffb13b", "DIAMOND", "#8fe4ff", "Spinosaurus", "HUGE", "$1.8M/s", "SELL $108M"),
             ("epic", "#b77bff", "GOLD", "#ffd43b", "Brachiosaurus", "", "$60K/s", "SELL $3.6M"),
             ("legendary", "#ffb13b", "", "", "T-Rex", "LARGE", "$10K/s", "SELL $600K"),
             ("rare", "#5ab8ff", "EMERALD", "#7ef0a0", "Triceratops", "BIG", "$5.6K/s", "SELL $336K")]
rows = []
for rarity, color, mutation, mcolor, name, size, income, sell in rows_data:
    tag = f'<span class="ol thin" style="font-size:16px;color:{mcolor}">{mutation}</span>' if mutation else '<span style="font-size:16px">&nbsp;</span>'
    size_html = f'<span class="ol thin" style="font-size:16px;color:#ffe066">{size}</span>' if size else ""
    rows.append(f'''<div class="row"><div class="dinotile" style="{tile(rarity, 76, 76)}">{dino(62, color)}</div>
<div style="flex:1;min-width:0;display:flex;flex-direction:column;gap:1px">{tag}<span class="ol" style="font-size:24px;white-space:nowrap">{name}</span><div style="display:flex;gap:8px;align-items:center">{size_html}<span class="ol thin" style="font-size:21px;color:#8dff5a">{income}</span></div></div>
<div style="display:flex;flex-direction:column;gap:7px">{button("PICK UP", "blue", 122, 38, 18)}{button(sell, "red", 122, 38, 16)}</div></div>''')
mydinos = f'''<div class="panel" style="left:790px;top:14px;width:470px;height:692px">
{head("My Dinos", "jungle", track(42, "#ffd166"), badge="8/14")}
<div style="display:flex;gap:10px;padding:14px 16px 10px">
<div class="tab green" style="flex:1"><span class="ol thin">ON PLOT 8/14</span></div>
<div class="tab" style="flex:1;background:#160f28"><span class="ol thin" style="color:#cbbff0">BACKPACK 5</span></div></div>
<div style="display:flex;flex-direction:column;gap:8px;padding:0 16px">{"".join(rows)}</div>
<div style="position:absolute;left:16px;right:16px;bottom:16px">{button("EQUIP BEST", "yellow", 428, 66, 32)}</div></div>
{side_button(book(64), "Index", "left:24px;top:236px")}{side_button(bag(64), "Shop", "left:24px;top:372px")}{stats()}'''
screens.append(screen("03 My Dinos", mydinos))

# 5. Egg Shop
eggs = [("TIER 1", "Dirty Egg", "x1", ("#f6ead2", "#d9bf91"), ("#f3e6c8", "#b08a52"), button(f"{check(22)} EQUIPPED", "grey", 146, 52, 18)),
        ("TIER 2", "Spotted Egg", "x1.25", ("#d8f8e4", "#86dca7"), ("#cff6dc", "#2f9e5a"), button("EQUIP", "blue", 146, 52, 24)),
        ("TIER 3", "Golden Egg", "x1.6", ("#fff3b8", "#ffcf3f"), ("#ffd84a", "#c98a0f"), button("$10K", "green", 146, 52, 26)),
        ("TIER 4", "Lava Egg", "x2.2", ("#ffd3c2", "#ff8a5c"), ("#ff7a3d", "#a8300f"), button("$250K", "red", 146, 52, 26)),
        ("TIER 5", "Cosmic Egg", "x3", ("#e4d2ff", "#a882ff"), ("#8a5cff", "#ffe066"), button("$8M", "red", 146, 52, 26))]
cards = []
for tier, name, luck, (bgtop, bgbottom), (shell, spot), btn in eggs:
    cards.append(f'''<div class="card" style="background:linear-gradient({bgtop},{bgbottom})"><span class="tier">{tier}</span>
<div style="margin-top:12px">{egg(118, shell, spot)}</div><span class="ol" style="font-size:25px;margin-top:8px">{name}</span>
<div class="luck" style="margin-top:4px">{clover(24)}<span class="ol thin" style="color:#8dff5a">LUCK {luck}</span></div>
<div style="position:absolute;bottom:16px">{btn}</div></div>''')
eggshop = f'''<div class="panel" style="left:140px;top:104px;width:1000px;height:512px">
{head("Egg Shop", "teal", egg(48, "#fff1d6", "#5fb8e8"))}
<div style="display:flex;gap:16px;padding:26px 30px 0">{"".join(cards)}</div>
<div class="muted" style="position:absolute;left:0;right:0;bottom:14px;text-align:center;font-size:18px">Better eggs multiply the luck of every throw</div></div>'''
screens.append(screen("04 Egg Shop", eggshop, dim=True))

# 6. Shop
def shoprow(icon, title, desc, action):
    return f'''<div class="row" style="height:118px"><div class="dinotile" style="width:86px;height:86px;background:linear-gradient(#4a3a75,#2a2045)">{icon}</div>
<div style="flex:1;display:flex;flex-direction:column;gap:4px"><span class="ol" style="font-size:26px;white-space:nowrap">{title}</span><span class="muted" style="font-size:16px">{desc}</span></div>{action}</div>'''
robux = lambda price: button(f'{coin(26)}{price}', "green", 132, 58, 26)
shop = f'''<div class="panel" style="left:180px;top:80px;width:920px;height:560px">
{head("Shop", "violet", bag(50))}
<div style="display:flex;gap:20px;padding:22px 24px">
<div style="position:relative;width:360px;height:420px;border-radius:26px;border:5px solid {INK};background:linear-gradient(#ffcf5c,#ff7a8a);display:flex;flex-direction:column;align-items:center;padding-top:20px;box-shadow:inset 0 -8px 0 rgba(0,0,0,0.18)">
<div class="ol" style="position:absolute;top:14px;right:-8px;transform:rotate(12deg);font-size:30px;background:#8dff5a;border:4px solid {INK};border-radius:14px;padding:2px 12px">FREE!</div>
<div style="margin-top:34px">{dino(210, "#7ee06a")}</div>
<span class="ol" style="font-size:32px;margin-top:6px">Starter Gallimimus</span><span class="ol thin" style="font-size:22px;color:#8dff5a">$3/s on your plot</span>
<div style="position:absolute;bottom:22px">{button("CLAIM", "green", 260, 72, 36)}</div></div>
<div style="flex:1;display:flex;flex-direction:column;gap:14px">
{shoprow(clover(60), "Server Luck x2", "2x luck for everyone here · 15 min", robux("19"))}
{shoprow(cash(60), "x2 Cash", "Every dino earns double, forever", robux("99"))}
{shoprow(bolt(60), "x2 Training", "Every rep gives double XP, forever", button(f"{check(22)} OWNED", "grey", 132, 58, 20))}
</div></div></div>'''
screens.append(screen("05 Shop", shop, dim=True))

# 7. Dino Index
def section(name, done, total, reward, tiles):
    pct = done / total
    complete = done == total
    status = f'<span class="ol thin" style="font-size:19px;color:#8dff5a;display:flex;align-items:center;gap:4px">{check(20)} {reward}</span>' if complete else f'<span class="muted" style="font-size:18px">Complete: {reward}</span>'
    tiles_html = "".join(
        f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px"><div class="dinotile" style="{tile(r, 150, 92) if r else "background:#160f28;width:150px;height:92px;"}">{dino(84, c, shadow=not r)}</div><span class="ol thin" style="font-size:17px;{"" if r else "color:#8f84b0"}">{n if r else "???"}</span></div>'
        for r, c, n in tiles)
    return f'''<div style="display:flex;flex-direction:column;gap:10px"><div style="display:flex;align-items:center;gap:14px"><span class="ol" style="font-size:28px;width:200px">{name}</span>
<div class="bar" style="width:260px"><div class="fill" style="width:{pct * 100:.0f}%;background:{"linear-gradient(#8af25a,#4cc12a)" if complete else "linear-gradient(#6fe3ff,#2f8ce6)"}"></div></div><span class="ol thin" style="font-size:22px">{done}/{total}</span>{status}</div>
<div style="display:flex;gap:14px">{tiles_html}</div></div>'''
index = f'''<div class="panel" style="left:140px;top:44px;width:1000px;height:636px">
{head("Dino Index", "indigo", book(50), badge="9/15")}
<div style="display:flex;flex-direction:column;gap:18px;padding:20px 30px">
{section("Fern Valley", 5, 5, "+10% cash · +5% luck", [("common", "#c9ced8", "Compy"), ("uncommon", "#7ee06a", "Gallimimus"), ("rare", "#5ab8ff", "Parasaurolophus"), ("epic", "#b77bff", "Stegosaurus"), ("legendary", "#ffb13b", "Velociraptor")])}
{section("Dry Plains", 3, 5, "+10% cash · +5% luck", [("common", "#c9ced8", "Pachycephalo"), ("uncommon", "#7ee06a", "Ankylosaurus"), ("rare", "#5ab8ff", "Triceratops"), (None, "", ""), (None, "", "")])}
{section("Swamp", 1, 5, "+10% cash · +5% luck", [("common", "#c9ced8", "Baryonyx"), (None, "", ""), (None, "", ""), (None, "", ""), (None, "", "")])}
</div></div>'''
screens.append(screen("06 Dino Index", index, dim=True))

# 8. Training HUD
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

html = f'''<!doctype html><html><head><meta charset="utf-8"><title>Throw Eggs UI</title><style>{CSS}</style></head><body>{"".join(screens)}</body></html>'''
out = pathlib.Path(__file__).with_name("ui.html")
out.write_text(html)
print(out, len(html))
