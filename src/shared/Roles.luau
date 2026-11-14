-- The colour roles of parts imported from Blender. Every model is built in Blender with one mesh per
-- colour role, and Studio's importer names each part after its Blender object (prop_LavaPool_Lava,
-- dino_ObsidianRex_Body), so the role is the last word of the name. A part renamed to the bare role works too.
local Roles = {}

-- Roles lit from inside: lava, fire, embers, lanterns, lit windows, and the Volcano monsters' eyes and
-- mouths, Frozen Peaks' ice crystals, Shadow Bog's will-o'-wisps, The Abyss's
-- bioluminescent jellyfish, anemones, pearls and sea glass. They get the Neon material, and lose any stud texture so it can't cover the glow.
Roles.glowing = {
	Lava = true,
	Ember = true,
	Flame = true,
	Furnace = true,
	EyeGlow = true, -- also Frozen Peaks' fierce monsters' frosty eyes
	IceGlow = true, -- glowing ice crystals on Frozen Peaks' fierce monsters
	Glow = true, -- the Swamp's lanterns, Shadow Bog's wisps, pods and eyes
	Wisp = true, -- the white-hot heart of Shadow Bog's wisps
	Shine = true, -- The Abyss's glowing anemone tips, polyps and gems (pink, next to its cyan Glow)
	Window = true, -- the Swamp hut's windows, and the Starfall observatory's
	-- Starfall Crater (assets/models/build_starfall_crater.py): crystals, star-stuff and nebula light, and the
	-- glowing parts that move (Config/PropMotion).
	CrystalGlow = true,
	NebulaGlow = true,
	StarGlow = true,
	Sparkle = true,
	Motes = true,
	Shard = true,
	Core = true,
	Bloom = true,
	Bud = true,
	Beacon = true,
	Halo = true,
	Gyro = true,
	Orb = true,
	Stream = true,
	Falling = true,
	CometHead = true,
	CometTail = true,
	LampStar = true,
	-- Eclipse Temple (assets/models/build_eclipse_temple.py): jade runes, eyes and spirit fire, lantern light,
	-- glowing pods and the eclipse's corona. Flame, Ember, Orb, Stream and Falling are above.
	Jade = true,
	Gaze = true,
	Pod = true,
	Lamp = true,
	FlameCore = true,
	Iris = true,
	Sigil = true,
	RuneInner = true,
	RuneOuter = true,
	Glyph = true,
	RuneA = true,
	RuneB = true,
	RuneC = true,
	LampA = true,
	LampB = true,
	LampC = true,
	Corona = true,
	EclipseRing = true,
	BellGlow = true,
	-- Midnight Carnival (assets/models/build_midnight_carnival.py): carnival bulbs, pink neon, the fortune teller's
	-- crystal ball and eyes, the moon, the ghost riders and the big top's searchlights. Lamp, Window, Flame, Gaze
	-- and LampStar are above.
	Bulb = true,
	Neon = true,
	Seer = true,
	Trance = true,
	Crescent = true,
	Ghost = true,
	Searchbeam = true,
	-- Forbidden Library (assets/models/build_forbidden_library.py): living violet ink, spell circles and sigils,
	-- candle flames, glowing sand, eyes in the bookcases, moths, the clock face and the door to nowhere. Flame,
	-- FlameCore, Gaze, Lamp, Window, Orb, Crescent, Stream and Falling are above.
	InkGlow = true,
	Spell = true,
	SpellRing = true,
	Letters = true,
	FlipGlow = true,
	FlameA = true,
	FlameB = true,
	TimeSand = true,
	Grain = true,
	Peeper = true,
	Moths = true,
	TomeGlow = true,
	ClockGlow = true,
	DoorGlow = true,
	InkL = true,
	InkR = true,
	-- Clockwork Citadel (assets/models/build_clockwork_citadel.py): electric blue lamps and orbs, lightning arcs,
	-- racing sparks, molten brass, gauge and watch faces. Furnace, Ember, Lamp, Window and Falling are above.
	Volt = true,
	Arc = true,
	Spark = true,
	Charge = true,
	Molten = true,
	Dial = true,
	-- Thorn Kingdom (assets/models/build_thorn_kingdom.py): glowing roses and falling petals, gold thread, the magic
	-- mirror, crown gems, stained glass and the moon. Bud, Motes, Glow, Lamp, Window, Stream, Falling and Gaze are above.
	RoseGlow = true,
	PetalGlow = true,
	Thread = true,
	MirrorGlow = true,
	CrownGem = true,
	Pane = true,
	PaneB = true,
	Lunar = true,
	-- Spore Hollow (assets/models/build_spore_hollow.py): glowing gills and specks on the caps, spores, the lamp
	-- mushrooms' bulbs, the morels' pits, mycelium veins, the heart, the wavecaps' bells, coral tips and the drifting
	-- spores in the sky. Glow, Bulb, Moths, Motes, Window, Lamp, LampA, LampB and Falling are above.
	GillGlow = true,
	Speck = true,
	Spore = true,
	BulbB = true,
	Pit = true,
	Vein = true,
	VeinB = true,
	HeartGlow = true,
	BellA = true,
	BellB = true,
	BellC = true,
	TipGlow = true,
	SporeCore = true,
	Filament = true,
	Drifter = true,
	-- Spore Hollow's monsters (assets/models/build_spore_hollow_monsters.py): the lilac light in Gillotine's wings. Their
	-- eyes, gills, spores and mycelium threads use EyeGlow, GillGlow, Spore, Speck, Glow, Vein, Pit and HeartGlow.
	Lilac = true,
	-- The Deep End (assets/models/build_deep_end.py): the gauges, stone fang tips, seams, seeps and eyes.
	ColumnRing = true,
	DeepEye = true,
	DeepSpore = true,
	FangTip = true,
	GaugeMark = true,
	GaugeTick = true,
	SeamGlow = true,
	SeepDrop = true,
	SeepFall = true,
	SeepRing = true,
	-- The Weeping Dark (assets/models/build_weeping_dark.py): tears and rings on the tear pools, the red of anything
	-- looking at you, souls, the lighthouse's beam and the procession's lead lantern. Flame, FlameA, FlameB, Lamp, LampA,
	-- Window, Stream, Beacon and Motes are above.
	Tears = true,
	Stare = true,
	Soul = true,
	Ripple = true,
	RippleB = true,
	Sweep = true,
	Leader = true,
	-- Shattered Mirror (assets/models/build_shattered_mirror.py): cracks of light, the cold eyes of what's in the glass,
	-- glints, the rainbow bands of light through glass, and the splinters pouring down the walls. FlameA is above.
	Fracture = true,
	Gleam = true,
	Facet = true,
	SpecA = true,
	SpecB = true,
	SpecC = true,
	SpecD = true,
	SpecE = true,
	Cascade = true,
	CascadeB = true,
	Note = true, -- the music box's notes of light
	Spray = true, -- the light pouring from the fountains
	SprayB = true,
	ChandFlame = true, -- the candles on the Ballroom's swinging chandeliers
	-- The Egg Shop's eggs (assets/models/build_eggs.py): lava cracks, lure dots, stars, gems, bulbs, roses, the halo, and
	-- the glowing yolk of the dearer eggs. Every part of an egg's top half ends in Lid (EggModel), so each has a twin.
	EggGlow = true,
	EggGlowLid = true,
	EggGlowB = true,
	EggGlowBLid = true,
	YolkGlow = true,
	YolkGlowLid = true,
}

-- Glowing roles you can see through, by how far: a beam of light.
Roles.sheer = {
	Sweep = 0.72,
}

function Roles.of(part: Instance): string
	return string.match(part.Name, "([^_]+)$") or part.Name
end

function Roles.lightUp(model: Instance)
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") and Roles.glowing[Roles.of(part)] then
			part.Material = Enum.Material.Neon
			part.Transparency = Roles.sheer[Roles.of(part)] or part.Transparency
			local studs = part:FindFirstChildOfClass("SurfaceAppearance")
			if studs then
				studs:Destroy()
			end
		end
	end
end

return Roles
