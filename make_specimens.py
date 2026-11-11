from pathlib import Path
from html import escape

OUT = Path(__file__).parent

# Hand-drawn 5×7 block alphabet. Lowercase deliberately shares the capitals,
# with a slightly reduced cap height in the specimen setting.
FONT1 = {
"A":["01110","10001","10001","11111","10001","10001","10001"],
"B":["11110","10001","10001","11110","10001","10001","11110"],
"C":["01111","10000","10000","10000","10000","10000","01111"],
"D":["11110","10001","10001","10001","10001","10001","11110"],
"E":["11111","10000","10000","11110","10000","10000","11111"],
"F":["11111","10000","10000","11110","10000","10000","10000"],
"G":["01111","10000","10000","10111","10001","10001","01111"],
"H":["10001","10001","10001","11111","10001","10001","10001"],
"I":["11111","00100","00100","00100","00100","00100","11111"],
"J":["00111","00010","00010","00010","10010","10010","01100"],
"K":["10001","10010","10100","11000","10100","10010","10001"],
"L":["10000","10000","10000","10000","10000","10000","11111"],
"M":["10001","11011","10101","10101","10001","10001","10001"],
"N":["10001","11001","10101","10011","10001","10001","10001"],
"O":["01110","10001","10001","10001","10001","10001","01110"],
"P":["11110","10001","10001","11110","10000","10000","10000"],
"Q":["01110","10001","10001","10001","10101","10010","01101"],
"R":["11110","10001","10001","11110","10100","10010","10001"],
"S":["01111","10000","10000","01110","00001","00001","11110"],
"T":["11111","00100","00100","00100","00100","00100","00100"],
"U":["10001","10001","10001","10001","10001","10001","01110"],
"V":["10001","10001","10001","10001","10001","01010","00100"],
"W":["10001","10001","10001","10101","10101","10101","01010"],
"X":["10001","10001","01010","00100","01010","10001","10001"],
"Y":["10001","10001","01010","00100","00100","00100","00100"],
"Z":["11111","00001","00010","00100","01000","10000","11111"],
"0":["01110","10001","10011","10101","11001","10001","01110"],
"1":["00100","01100","00100","00100","00100","00100","01110"],
"2":["01110","10001","00001","00010","00100","01000","11111"],
"3":["11110","00001","00001","01110","00001","00001","11110"],
"4":["00010","00110","01010","10010","11111","00010","00010"],
"5":["11111","10000","10000","11110","00001","00001","11110"],
"6":["01111","10000","10000","11110","10001","10001","01110"],
"7":["11111","00001","00010","00100","01000","01000","01000"],
"8":["01110","10001","10001","01110","10001","10001","01110"],
"9":["01110","10001","10001","01111","00001","00001","11110"],
"!":["00100","00100","00100","00100","00100","00000","00100"],
"?":["01110","10001","00001","00010","00100","00000","00100"],
".":["00000","00000","00000","00000","00000","00110","00110"],
",":["00000","00000","00000","00000","00110","00110","00100"],
":":["00000","00110","00110","00000","00110","00110","00000"],
"'": ["00100","00100","00010","00000","00000","00000","00000"],
'"':["01010","01010","00100","00000","00000","00000","00000"],
"-": ["00000","00000","00000","11111","00000","00000","00000"],
"+": ["00000","00100","00100","11111","00100","00100","00000"],
"&": ["01100","10010","10100","01000","10101","10010","01101"],
"%": ["11001","11010","00100","01000","10110","00110","00000"],
"$": ["00100","01111","10100","01110","00101","11110","00100"],
"/": ["00001","00010","00010","00100","01000","01000","10000"],
}

FONT2 = {
"0":["0110","1001","1011","1101","1001","1001","0110"],
"1":["0010","0110","0010","0010","0010","0010","0111"],
"2":["1110","0001","0001","0110","1000","1000","1111"],
"3":["1110","0001","0001","0110","0001","0001","1110"],
"4":["0010","0110","1010","1010","1111","0010","0010"],
"5":["1111","1000","1000","1110","0001","0001","1110"],
"6":["0111","1000","1000","1110","1001","1001","0110"],
"7":["1111","0001","0010","0010","0100","0100","0100"],
"8":["0110","1001","1001","0110","1001","1001","0110"],
"9":["0110","1001","1001","0111","0001","0001","1110"],
"$":FONT1["$"], "x":["00000","10001","01010","00100","01010","10001","00000"],
"%":FONT1["%"], "+":FONT1["+"], "-":FONT1["-"], "/":FONT1["/"],
":":FONT1[":"], ".":FONT1["."], ",":FONT1[","]
}

def svg_head(title, desc, w=1800, h=1500):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<title>{escape(title)}</title><desc>{escape(desc)}</desc>
<defs><pattern id="grain" width="90" height="90" patternUnits="userSpaceOnUse"><circle cx="9" cy="11" r="1" fill="#fff" opacity=".035"/><circle cx="58" cy="53" r="1" fill="#fff" opacity=".025"/></pattern></defs>'''

def textline(s, x, y, cell=13, gap=3, step=99, color="#fff", outline="#17202b", font=FONT1, small=False, slant=True, centered=False):
    glyph_w = (len(font.get(next((c.upper() for c in s if c != ' '), 'A'), FONT1['A'])[0]) * (cell+gap))
    advance = step
    width = sum((advance*0.65 if c==' ' else advance) for c in s)
    if centered: x -= width/2
    out=[]
    cursor=x
    for idx,ch in enumerate(s):
        if ch==' ':
            cursor += advance*0.65; continue
        pat=font.get(ch, font.get(ch.upper(), FONT1.get(ch.upper(), FONT1['?'])))
        cw=max(map(len,pat)); scale=.72 if (small and ch.islower()) else 1
        # Font 1 gets a lively but restrained lean and bounce. Digits stay square and steady.
        rot=((-2.0 if idx%3==0 else 1.4 if idx%3==1 else 0) if slant else 0)
        dy=((idx%3)-1)*2.0 if slant else 0
        ox=cursor+(advance-(cw*(cell+gap)-gap)*scale)/2
        for row,line in enumerate(pat):
            for col,v in enumerate(line):
                if v!='1': continue
                xx=ox+col*(cell+gap)*scale
                yy=y+row*(cell+gap)*scale+dy
                ww=(cell*scale)
                # Separate, softened blocks create open counters and a carved, hand-set rhythm.
                out.append(f'<rect x="{xx:.1f}" y="{yy:.1f}" width="{ww:.1f}" height="{ww:.1f}" rx="{ww*.34:.1f}" fill="{color}" stroke="{outline}" stroke-width="{min(5,ww*.28):.1f}" transform="rotate({rot:.1f} {xx+ww/2:.1f} {yy+ww/2:.1f})"/>')
        cursor+=advance
    return ''.join(out)

def panel(x, y, w, h, fill, bright=False):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="28" fill="{fill}"/><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="28" fill="url(#grain)"/>'

def f1_sheet():
    a=svg_head("RUMBLE CAPS — Lettering specimen", "Original chunky small-caps display lettering, shown on dark and bright fields.")
    a+='<rect width="1800" height="1500" fill="#f5f2e9"/>'
    a+='<text x="70" y="78" font-family="Arial,sans-serif" font-size="25" font-weight="700" letter-spacing="5" fill="#34404b">THROW EGGS FOR DINOSAURS · LETTER SYSTEM 01</text>'
    for x,fill in [(60,"#17202b"),(920,"#cfff37")]:
        a+=panel(x,110,820,1330,fill,fill!="#17202b")
        fg="#fff"; ol="#17202b"
        a+=f'<text x="{x+38}" y="158" font-family="Arial,sans-serif" font-size="17" font-weight="700" letter-spacing="3" fill="{fg if fill=="#17202b" else "#253222"}">{"NIGHT FIELD" if fill=="#17202b" else "DAY FIELD"} · WHITE INK / DARK KEYLINE</text>'
        # alphabet grid, clearly separated, lowercase is small-caps scale
        rows=["ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"]
        for ri,row in enumerate(rows):
            yy=205+ri*112
            for j,ch in enumerate(row):
                a+=textline(ch,x+40+j*29,yy,cell=4.6,gap=.5,step=29,color=fg,outline=ol,small=True,slant=True)
        a+=textline("! ? . , : ' \" - + & %",x+45,440,cell=10,gap=1,step=48,color=fg,outline=ol)
        a+=textline("THROW EGGS",x+30,550,cell=13,gap=1.5,step=75,color=fg,outline=ol,centered=False)
        a+=textline("LEGENDARY",x+30,665,cell=13,gap=1.5,step=75,color=fg,outline=ol)
        a+=textline("NEW MONSTER!",x+30,780,cell=13,gap=1.5,step=65,color=fg,outline=ol)
        a+=textline("SELL",x+30,895,cell=13,gap=1.5,step=75,color=fg,outline=ol)
        a+=textline("SHOP",x+30,1010,cell=13,gap=1.5,step=75,color=fg,outline=ol)
        a+=f'<text x="{x+45}" y="1265" font-family="Arial,sans-serif" font-size="18" font-weight="600" fill="{fg if fill=="#17202b" else "#263120"}">Heavy block forms · broad counters · tidy chips · lively set</text>'
    return a+'</svg>'

def f2_sheet():
    a=svg_head("SCOREKEEP — Number specimen", "Original condensed geometric tabular numerals and score symbols on dark and bright fields.")
    a+='<rect width="1800" height="1500" fill="#f5f2e9"/>'
    a+='<text x="70" y="78" font-family="Arial,sans-serif" font-size="25" font-weight="700" letter-spacing="5" fill="#34404b">THROW EGGS FOR DINOSAURS · NUMBER SYSTEM 02</text>'
    for x,fill in [(60,"#17202b"),(920,"#cfff37")]:
        a+=panel(x,110,820,1330,fill)
        fg="#fff"; ol="#17202b"
        a+=f'<text x="{x+38}" y="158" font-family="Arial,sans-serif" font-size="17" font-weight="700" letter-spacing="3" fill="{fg if fill=="#17202b" else "#253222"}">{"NIGHT FIELD" if fill=="#17202b" else "DAY FIELD"} · TABULAR / SCOREBOARD</text>'
        for j,ch in enumerate("0123456789"):
            a+=textline(ch,x+54+j*72,230,cell=16,gap=3,step=72,color=fg,outline=ol,font=FONT2,slant=False)
        a+=textline(", . $ x % + - / :",x+75,400,cell=8,gap=1,step=50,color=fg,outline=ol,font=FONT2,slant=False)
        for sample,yy in [("$1,250,000",540),("x500",695),("99.5%",850),("12:34",1005),("+5 POWER",1160)]:
            # draw digits with condensed 4-column cell; map letters from lettering alphabet
            font={**FONT1,**FONT2}
            a+=textline(sample,x+45,yy,cell=12,gap=1.5,step=70,color=fg,outline=ol,font=font,slant=False)
        a+=f'<text x="{x+50}" y="1355" font-family="Arial,sans-serif" font-size="18" font-weight="600" fill="{fg if fill=="#17202b" else "#263120"}">Fixed-width figures · clear 1 / 7 · oval 0 / open 8</text>'
    return a+'</svg>'

def mockup():
    a=svg_head("Rumble Caps + Scorekeep — game UI mockup", "Mock Roblox game shop button and reveal banner using the two original display systems.", h=1000)
    a+='<rect width="1800" height="1000" fill="#111923"/><rect width="1800" height="1000" fill="url(#grain)"/>'
    a+='<text x="70" y="75" font-family="Arial,sans-serif" font-size="24" font-weight="700" letter-spacing="5" fill="#aeb8c2">UI PAIRING STUDY · BUTTON + REVEAL</text>'
    # mock button with thick shadow and keyline
    a+='<rect x="130" y="180" width="510" height="210" rx="54" fill="#070b10"/><rect x="130" y="150" width="510" height="210" rx="54" fill="#cfff37" stroke="#090f15" stroke-width="16"/><rect x="147" y="167" width="476" height="176" rx="42" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="4"/>'
    a+=textline("SHOP",198,205,cell=16,gap=2,step=66,color="#fff",outline="#17202b",centered=False)
    a+=textline("$1,250",205,290,cell=11,gap=2,step=50,color="#fff",outline="#17202b",font={**FONT1,**FONT2},slant=False)
    # reveal banner layered on night field
    a+='<rect x="700" y="150" width="970" height="670" rx="54" fill="#080c13"/><rect x="700" y="126" width="970" height="670" rx="54" fill="#3a76ff" stroke="#080c13" stroke-width="20"/><rect x="724" y="150" width="922" height="622" rx="39" fill="none" stroke="#cfff37" stroke-width="7"/>'
    a+='<rect x="1065" y="184" width="240" height="48" rx="24" fill="#cfff37" stroke="#111923" stroke-width="8"/>'
    a+=textline("LEGENDARY",1082,192,cell=4.5,gap=.4,step=22,color="#fff",outline="#17202b",centered=False)
    a+=textline("NEW",810,310,cell=25,gap=3,step=145,color="#fff",outline="#17202b")
    a+=textline("MONSTER!",824,480,cell=17,gap=2,step=100,color="#fff",outline="#17202b")
    a+=textline("x500",1150,690,cell=15,gap=2,step=65,color="#fff",outline="#17202b",font={**FONT1,**FONT2},slant=False)
    a+='<text x="132" y="455" font-family="Arial,sans-serif" font-size="19" font-weight="700" letter-spacing="3" fill="#aeb8c2">MOCK SHOP BUTTON</text><text x="700" y="865" font-family="Arial,sans-serif" font-size="19" font-weight="700" letter-spacing="3" fill="#aeb8c2">MOCK REVEAL BANNER</text>'
    a+='<text x="70" y="950" font-family="Arial,sans-serif" font-size="17" fill="#aeb8c2">RUMBLE CAPS: punchy small caps, carved block rhythm · SCOREKEEP: compact fixed-width figures for fast counters</text>'
    return a+'</svg>'

for name, data in [("rumble-caps-specimen.svg",f1_sheet()),("scorekeep-specimen.svg",f2_sheet()),("ui-pairing-mockup.svg",mockup())]:
    (OUT/name).write_text(data)
    print(OUT/name)
