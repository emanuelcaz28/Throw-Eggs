-- The Prism Egg: a low-poly crystal egg, every facet its own spectrum colour, with a glowing core inside (Figma
-- "Shop v2", component "Prism Egg"). Built here from flat triangles, so it needs no imported model: the Shop's card
-- and the egg's opening show the same egg. Display only.
-- pose() stands it up, opens its cracks (the facets part and the core shines through) and bursts it into shards.
local PrismEgg = {}

local THICK = 0.04 -- a facet's thickness, studs
local TOP, FOOT = 1.45, -1.3 -- the egg's tip and foot on its upright; its middle is 0
local RINGS = { -- from the top down: height, radius, how far round its six corners start (turns of a sixth)
	{ 1.0, 0.6, 0 },
	{ 0.25, 0.98, 0.5 },
	{ -0.55, 0.9, 0 },
	{ -1.05, 0.5, 0.5 },
}
local SIDES = 6
local CORE_SIZE = Vector3.new(1.45, 2.2, 1.45)
local GAP = 0.16 -- how far the facets part when fully cracked, studs
local FOV = 30

PrismEgg.HEIGHT = TOP - FOOT

export type Egg = {
	model: Model,
	core: Part,
	facets: { { parts: { BasePart }, homes: { CFrame }, centre: Vector3, normal: Vector3, spin: Vector3, reach: number } },
}

local function wedge(parent: Instance, colour: Color3): WedgePart
	local part = Instance.new("WedgePart")
	part.Anchored = true
	part.CanCollide = false
	part.CastShadow = false
	part.Material = Enum.Material.SmoothPlastic
	part.Color = colour
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	part.Parent = parent
	return part
end

-- A flat triangle from two wedges (the usual way: split it along the height onto its longest side).
local function triangle(a: Vector3, b: Vector3, c: Vector3, parent: Instance, colour: Color3): { BasePart }
	local ab, ac, bc = b - a, c - a, c - b
	local abd, acd, bcd = ab:Dot(ab), ac:Dot(ac), bc:Dot(bc)
	if abd > acd and abd > bcd then
		c, a = a, c
	elseif acd > bcd and acd > abd then
		a, b = b, a
	end
	ab, ac, bc = b - a, c - a, c - b
	local right = ac:Cross(ab).Unit
	local up = bc:Cross(right).Unit
	local back = bc.Unit
	local height = math.abs(ab:Dot(up))
	local first = wedge(parent, colour)
	first.Size = Vector3.new(THICK, height, math.abs(ab:Dot(back)))
	first.CFrame = CFrame.fromMatrix((a + b) / 2, right, up, back)
	local second = wedge(parent, colour)
	second.Size = Vector3.new(THICK, height, math.abs(ac:Dot(back)))
	second.CFrame = CFrame.fromMatrix((a + c) / 2, -right, up, -back)
	return { first, second }
end

-- A facet's colour: the spectrum winding round the egg as it climbs, so every side shows several colours; paler
-- towards the top, every other facet a little paler still.
local function facetColour(centre: Vector3, index: number): Color3
	local high = (centre.Y - FOOT) / (TOP - FOOT)
	local hue = (math.atan2(centre.Z, centre.X) / (2 * math.pi) + 0.92 + 0.7 * high) % 1
	local saturation = (if index % 2 == 0 then 0.72 else 0.5) * (1 - 0.25 * high)
	return Color3.fromHSV(hue, saturation, 1)
end

function PrismEgg.build(): Egg
	local model = Instance.new("Model")
	model.Name = "PrismEgg"
	local rings = {}
	for _, ring in RINGS do
		local corners = {}
		for side = 0, SIDES - 1 do
			local angle = (side + ring[3]) / SIDES * 2 * math.pi
			table.insert(corners, Vector3.new(math.cos(angle) * ring[2], ring[1], math.sin(angle) * ring[2]))
		end
		table.insert(rings, corners)
	end
	local random = Random.new(7)
	local egg: Egg = { model = model, core = Instance.new("Part"), facets = {} }
	local function facet(a: Vector3, b: Vector3, c: Vector3)
		local centre = (a + b + c) / 3
		local normal = (b - a):Cross(c - a).Unit
		if normal:Dot(centre) < 0 then
			normal = -normal
		end
		local parts = triangle(a, b, c, model, facetColour(centre, #egg.facets))
		table.insert(egg.facets, {
			parts = parts,
			homes = { parts[1].CFrame, parts[2].CFrame },
			centre = centre,
			normal = normal,
			spin = Vector3.new(random:NextNumber(-7, 7), random:NextNumber(-7, 7), random:NextNumber(-7, 7)),
			reach = random:NextNumber(3.5, 8),
		})
	end
	local tip, foot = Vector3.new(0, TOP, 0), Vector3.new(0, FOOT, 0)
	for side = 1, SIDES do
		local nextSide = side % SIDES + 1
		facet(tip, rings[1][side], rings[1][nextSide])
		facet(foot, rings[#rings][side], rings[#rings][nextSide])
	end
	for band = 1, #rings - 1 do
		local upper, lower = rings[band], rings[band + 1]
		-- The lower ring is turned half a side from the upper one, whichever way round this band is.
		local ahead = RINGS[band + 1][3] > RINGS[band][3]
		for side = 1, SIDES do
			local nextSide = side % SIDES + 1
			if ahead then
				facet(upper[side], lower[side], upper[nextSide])
				facet(lower[side], lower[nextSide], upper[nextSide])
			else
				facet(lower[side], upper[side], lower[nextSide])
				facet(upper[side], upper[nextSide], lower[nextSide])
			end
		end
	end
	local core = egg.core
	core.Name = "Core"
	core.Anchored = true
	core.CanCollide = false
	core.CastShadow = false
	core.Material = Enum.Material.Neon
	core.Color = Color3.new(1, 1, 1)
	core.Size = CORE_SIZE
	core.Parent = model
	local shape = Instance.new("SpecialMesh") -- a ball stretched into an egg
	shape.MeshType = Enum.MeshType.Sphere
	shape.Parent = core
	return egg
end

-- Where everything is now. tilt rocks the egg about its foot (degrees); crack 0 to 1 parts the facets so the core
-- shows; burst 0 to 1 throws them outwards, spinning; light is the core's colour.
function PrismEgg.pose(egg: Egg, tilt: number, crack: number, burst: number, light: Color3?)
	local stand = CFrame.new(0, FOOT, 0) * CFrame.Angles(0, 0, math.rad(tilt)) * CFrame.new(0, -FOOT, 0)
	for _, facet in egg.facets do
		local out = facet.normal * (crack * GAP + burst * facet.reach)
		local turn = facet.spin * burst
		local move = CFrame.new(facet.centre + out) * CFrame.Angles(turn.X, turn.Y, turn.Z) * CFrame.new(-facet.centre)
		for index, part in facet.parts do
			part.CFrame = stand * move * facet.homes[index]
		end
	end
	egg.core.CFrame = stand
	egg.core.Size = CORE_SIZE * (1 + 0.5 * burst)
	egg.core.Transparency = if burst > 0.6 then 1 else 0
	if light then
		egg.core.Color = light
	end
end

-- A view of the egg. span is how many studs of height the view shows (the egg is PrismEgg.HEIGHT tall), so a bigger
-- span leaves room round it for its shards. Returns the view and a function that looks at it from an angle (radians).
function PrismEgg.view(parent: Instance, egg: Egg, span: number): (ViewportFrame, (number) -> ())
	local view = Instance.new("ViewportFrame")
	view.Name = "PrismEgg"
	view.BackgroundTransparency = 1
	view.Ambient = Color3.fromRGB(190, 185, 205)
	view.LightColor = Color3.new(1, 1, 1)
	view.LightDirection = Vector3.new(-0.5, -1, -0.6)
	view.Parent = parent
	egg.model.Parent = view
	local camera = Instance.new("Camera")
	camera.FieldOfView = FOV
	camera.Parent = view
	view.CurrentCamera = camera
	local middle = Vector3.new(0, (TOP + FOOT) / 2, 0)
	local distance = span / 2 / math.tan(math.rad(FOV / 2))
	local function look(yaw: number)
		local from = middle + Vector3.new(math.sin(yaw), 0.12, math.cos(yaw)).Unit * distance
		camera.CFrame = CFrame.lookAt(from, middle)
	end
	look(0)
	return view, look
end

return PrismEgg
