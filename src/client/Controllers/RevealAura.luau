-- The luck building up round a caught monster during its reveal (docs/GAME_SPEC.md section 7), with the monster in
-- full view the whole time [Owner, 2026-11-06]: a glowing outline in the luck label's colour, lights rising off the
-- ground under it and a light on it, a shockwave ring racing out along the ground each time a new label lands, from
-- GODLY! on lightning striking round it, and on IMPOSSIBLE! all of it cycling through the rainbow. At the final moment
-- it bursts once. Built from parts, lights and built-in Roblox textures, so nothing has to be uploaded. Display only;
-- numbers in Config/Reveal aura. RevealController plays it.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)

local RevealAura = {}

local settings = Reveal.aura
local MOTE_TEXTURE = "rbxasset://textures/particles/sparkles_main.dds"
local WHITE = Color3.new(1, 1, 1)

local function lerp(a: number, b: number, u: number): number
	return a + (b - a) * u
end

-- A value from a { first label, rarest label } pair, `strength` of the way (0 to 1).
local function pick(pair: { number }, strength: number): number
	return lerp(pair[1], pair[2], strength)
end

local function effectPart(name: string, size: Vector3, cframe: CFrame, color: Color3): Part
	local part = Instance.new("Part")
	part.Name = name
	part.Anchored = true
	part.CanCollide = false
	part.CanQuery = false
	part.CanTouch = false
	part.CastShadow = false
	part.Material = Enum.Material.Neon
	part.Color = color
	part.Size = size
	part.CFrame = cframe
	return part
end

export type Aura = {
	setTier: (tier: any, index: number, slam: boolean?) -> (),
	final: (strength: number, color: Color3) -> (),
	update: (now: number) -> (),
	destroy: () -> (),
}

-- Sets up the (still dark) aura round `model`, standing on the ground at `groundY`. Everything goes in one folder.
function RevealAura.new(model: Model, groundY: number): Aura
	local box, size = model:GetBoundingBox()
	local radius = math.max(size.X, size.Z) / 2
	local feet = Vector3.new(box.Position.X, groundY, box.Position.Z)
	local folder = Instance.new("Folder")
	folder.Name = "RevealAura"
	folder.Parent = workspace

	local outline = Instance.new("Highlight")
	outline.Name = "LuckOutline"
	outline.Adornee = model
	outline.DepthMode = Enum.HighlightDepthMode.Occluded
	outline.FillTransparency = 1
	outline.OutlineTransparency = 1
	outline.Parent = folder

	-- Lights rising off the ground round the monster's feet: an invisible pad as wide as the monster.
	local pad = effectPart("RisingLights", Vector3.new(size.X, 0.2, size.Z):Min(Vector3.one * 2048), CFrame.new(feet) * box.Rotation, WHITE)
	pad.Transparency = 1
	pad.Parent = folder
	local motes = Instance.new("ParticleEmitter")
	motes.Texture = MOTE_TEXTURE
	motes.EmissionDirection = Enum.NormalId.Top
	motes.Rate = 0
	motes.Lifetime = NumberRange.new(1.2, 2)
	motes.Speed = NumberRange.new(size.Y * 0.18, size.Y * 0.4)
	motes.SpreadAngle = Vector2.new(12, 12)
	local moteSize = math.clamp(math.max(size.Y, size.X) * 0.06, 0.6, 60)
	motes.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, moteSize), NumberSequenceKeypoint.new(1, moteSize * 0.3) })
	motes.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.1), NumberSequenceKeypoint.new(0.7, 0.3), NumberSequenceKeypoint.new(1, 1) })
	motes.LightEmission = 1
	motes.Parent = pad

	local glow = Instance.new("PointLight")
	glow.Brightness = 0
	glow.Range = math.clamp(math.max(size.X, size.Y, size.Z) * 1.2, 8, 60)
	glow.Shadows = false
	local glowAt = Instance.new("Attachment")
	glowAt.WorldPosition = box.Position
	glowAt.Parent = pad
	glow.Parent = glowAt

	local color = WHITE
	local strength = 0
	local rainbow = false
	local lightning = false
	local nextStrike = 0
	local rings = {}
	local bolts = {}
	local pulseAt = -math.huge

	-- A flat ring of glowing pieces at the monster's feet that races out along the ground and fades.
	local function shockwave(ringColor: Color3, reach: number)
		local pieces = {}
		local thickness = math.clamp(radius * 0.06, 0.25, 30)
		for index = 1, settings.ringPieces do
			local piece = effectPart("Shockwave", Vector3.new(thickness, thickness * 0.4, 1), CFrame.new(feet), ringColor)
			piece.Parent = folder
			pieces[index] = piece
		end
		table.insert(rings, { pieces = pieces, born = os.clock(), reach = reach, thickness = thickness })
	end

	-- A jagged bolt from high above to the ground somewhere round the monster.
	local function strike(boltColor: Color3)
		local angle = math.random() * math.pi * 2
		local out = radius * lerp(1.1, settings.lightningSpread, math.random())
		local bottom = feet + Vector3.new(math.cos(angle) * out, 0, math.sin(angle) * out)
		local top = bottom + Vector3.new(0, math.clamp(size.Y * 2.5, 40, 900), 0)
		local width = math.clamp(size.Y * 0.025, 0.3, 12)
		local pieces = {}
		local last = top
		local steps = settings.lightningSteps
		for step = 1, steps do
			local point = top:Lerp(bottom, step / steps)
			if step < steps then
				local wobble = (top - bottom).Magnitude / steps * 0.45
				point += Vector3.new((math.random() - 0.5) * wobble, 0, (math.random() - 0.5) * wobble)
			end
			local length = (point - last).Magnitude
			local piece = effectPart("Lightning", Vector3.new(width, width, length), CFrame.lookAt((last + point) / 2, point), WHITE:Lerp(boltColor, 0.35))
			piece.Parent = folder
			table.insert(pieces, piece)
			last = point
		end
		local flash = Instance.new("PointLight")
		flash.Color = boltColor
		flash.Brightness = 4
		flash.Range = math.clamp(size.Y, 10, 60)
		flash.Parent = pieces[#pieces]
		table.insert(bolts, { pieces = pieces, born = os.clock() })
		shockwave(boltColor, settings.ringReach * 0.5)
	end

	local function paint(now: number)
		local shown = if rainbow then Color3.fromHSV((now * settings.rainbowSpeed) % 1, 0.75, 1) else color
		outline.OutlineColor = shown
		outline.FillColor = shown
		motes.Color = ColorSequence.new(shown:Lerp(WHITE, 0.4), shown)
		glow.Color = shown
		return shown
	end

	local aura = {}

	-- A new luck label (`index` 1 for LUCKY! up to the rarest): the colours change to its, everything grows, and
	-- with `slam` a shockwave races out and the outline flashes.
	function aura.setTier(tier, index: number, slam: boolean?)
		color = tier.color
		strength = math.clamp((index - 1) / math.max(#Reveal.tiers - 1, 1), 0, 1)
		rainbow = index >= settings.rainbowFrom
		lightning = index >= settings.lightningFrom
		motes.Rate = pick(settings.motes, strength)
		glow.Brightness = pick(settings.light, strength)
		if slam then
			pulseAt = os.clock()
			shockwave(color, settings.ringReach)
			motes:Emit(math.round(pick(settings.burst, strength)))
		end
	end

	-- The final moment: one big shockwave (two for the rarest), a burst of lights and a bright flash of the outline,
	-- which then settles to a soft glow. `strength` is 0 for a catch with no luck label up to 1 for the rarest.
	function aura.final(finalStrength: number, finalColor: Color3)
		if strength == 0 then
			color = finalColor
		end
		strength = math.max(strength, finalStrength)
		pulseAt = os.clock()
		shockwave(paint(os.clock()), settings.ringReach * lerp(1, 1.6, finalStrength))
		if finalStrength > 0.5 then
			task.delay(0.15, function()
				if folder.Parent then
					shockwave(paint(os.clock()), settings.ringReach * 2)
				end
			end)
		end
		motes:Emit(math.round(pick(settings.burst, finalStrength) * 2))
		if lightning then
			for _ = 1, 3 do
				strike(paint(os.clock()))
			end
		end
		motes.Rate = pick(settings.motes, finalStrength) * 0.5
		glow.Brightness = pick(settings.light, finalStrength)
	end

	function aura.update(now: number)
		local shown = paint(now)
		if strength > 0 or now - pulseAt < 1 then
			-- Breathes in and out, and flashes bright when a label lands.
			local flash = math.max(1 - (now - pulseAt) / settings.flashTime, 0)
			local breathe = (math.sin(now * settings.breatheRate * math.pi * 2) + 1) / 2
			outline.OutlineTransparency = math.clamp(pick(settings.outline, strength) - breathe * 0.12 - flash * 0.5, 0, 1)
			outline.FillTransparency = math.clamp(pick(settings.fill, strength) - flash * 0.35, 0, 1)
		end

		for index = #rings, 1, -1 do
			local ring = rings[index]
			local t = (now - ring.born) / settings.ringTime
			if t >= 1 then
				for _, piece in ring.pieces do
					piece:Destroy()
				end
				table.remove(rings, index)
			else
				local eased = 1 - (1 - t) ^ 3
				local r = radius * lerp(0.6, ring.reach, eased)
				local count = #ring.pieces
				local length = 2 * math.pi * r / count * 1.08
				for i, piece in ring.pieces do
					local a = (i - 1) / count * math.pi * 2
					local at = feet + Vector3.new(math.cos(a) * r, ring.thickness * 0.2, math.sin(a) * r)
					piece.Size = Vector3.new(ring.thickness, ring.thickness * 0.4, length)
					piece.CFrame = CFrame.lookAt(at, at + Vector3.new(-math.sin(a), 0, math.cos(a)))
					piece.Transparency = t * t
				end
			end
		end

		if lightning and now >= nextStrike then
			nextStrike = now + pick(settings.lightningEvery, strength) * lerp(0.6, 1.4, math.random())
			strike(shown)
		end
		for index = #bolts, 1, -1 do
			local bolt = bolts[index]
			local t = (now - bolt.born) / settings.lightningTime
			if t >= 1 then
				for _, piece in bolt.pieces do
					piece:Destroy()
				end
				table.remove(bolts, index)
			else
				for _, piece in bolt.pieces do
					piece.Transparency = t * t
				end
			end
		end
	end

	function aura.destroy()
		folder:Destroy()
	end

	return aura
end

return RevealAura
