-- A market stall: a wooden stall with a striped awning, a shopkeeper behind the counter, a big
-- sign and a glowing pad in front. The server builds the shared SELL stall; each client builds
-- its own Egg Shop stall at its base, so nobody else sees it (Config/Hub).
local Hub = require(script.Parent.Config.Hub)
local World = require(script.Parent.World)

local Stall = {}

local WOOD = Color3.fromRGB(150, 95, 55)
local DARK_WOOD = Color3.fromRGB(110, 68, 40)
local SKIN = Color3.fromRGB(255, 205, 70)
local SHIRT = Color3.fromRGB(60, 110, 200)
local STRIPES = 8
local AWNING_TILT = math.rad(14) -- the front edge hangs lower
local COUNTER_HEIGHT = 3
local SIGN_DISTANCE = 250

local function studs(part: BasePart): BasePart
	part.TopSurface = Enum.SurfaceType.Studs
	return part
end

-- Builds a stall from Config/Hub (stall) standing at origin (Hub.stallCFrame) and returns it unparented.
function Stall.build(name: string, stall, origin: CFrame): Model
	local size = Hub.stallSize
	local model = Instance.new("Model")
	model.Name = name

	-- x is across the stall, z towards its front (where the pad is).
	local function at(x: number, y: number, z: number): CFrame
		return origin * CFrame.new(-x, y, -z) * CFrame.Angles(0, math.pi, 0)
	end

	-- Corner posts, back wall and counter.
	for _, x in { -1, 1 } do
		for _, z in { -1, 1 } do
			studs(World.makePart(model, "Post", Vector3.new(0.8, size.Y, 0.8), at(x * (size.X / 2 - 0.4), size.Y / 2, z * (size.Z / 2 - 0.4)), DARK_WOOD))
		end
	end
	studs(World.makePart(model, "BackWall", Vector3.new(size.X, size.Y * 0.6, 0.6), at(0, size.Y * 0.3, -size.Z / 2 + 0.3), WOOD))
	studs(World.makePart(model, "Counter", Vector3.new(size.X, COUNTER_HEIGHT, 2), at(0, COUNTER_HEIGHT / 2, size.Z / 2 - 1), WOOD))

	-- Shopkeeper: a blocky figure standing behind the counter.
	studs(World.makePart(model, "KeeperBody", Vector3.new(2, 2.4, 1), at(0, COUNTER_HEIGHT + 0.2, -0.5), SHIRT))
	studs(World.makePart(model, "KeeperHead", Vector3.new(1.4, 1.4, 1.4), at(0, COUNTER_HEIGHT + 2.1, -0.5), SKIN))

	-- Striped awning, tilted down towards the front.
	local stripeWidth = size.X / STRIPES
	for index = 1, STRIPES do
		local x = -size.X / 2 + stripeWidth * (index - 0.5)
		local stripe = World.makePart(
			model,
			"Awning",
			Vector3.new(stripeWidth, 0.5, size.Z + 2),
			at(x, size.Y, 0.5) * CFrame.Angles(AWNING_TILT, 0, 0),
			stall.stripes[(index - 1) % #stall.stripes + 1]
		)
		studs(stripe)
	end

	local signAnchor = World.makePart(model, "SignAnchor", Vector3.one, at(0, size.Y + 3, 0), WOOD)
	signAnchor.Transparency = 1
	signAnchor.CanCollide = false
	World.makeSign(signAnchor, stall.title, 0, SIGN_DISTANCE, 300)
	signAnchor.Sign.TextLabel.TextColor3 = stall.stripes[1]
	signAnchor.Sign.TextLabel.TextStrokeTransparency = 0

	local pad = World.makePad(model, Hub.padPosition(origin), Hub.padRadius, stall.padColor)
	pad.Name = "StallPad"
	pad.Material = Enum.Material.Neon
	pad.Transparency = 0.25

	return model
end

return Stall
