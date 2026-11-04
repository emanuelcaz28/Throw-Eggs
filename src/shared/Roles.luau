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
