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
}

function Roles.of(part: Instance): string
	return string.match(part.Name, "([^_]+)$") or part.Name
end

function Roles.lightUp(model: Instance)
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") and Roles.glowing[Roles.of(part)] then
			part.Material = Enum.Material.Neon
			local studs = part:FindFirstChildOfClass("SurfaceAppearance")
			if studs then
				studs:Destroy()
			end
		end
	end
end

return Roles
