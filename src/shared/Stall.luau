-- A market stall: the Blender stall (BaseKit base_Stall) with its awning in the stall's colours, a big
-- sign over it and a glowing pad in front. The server builds the shared SELL stall; each client builds
-- its own Egg Shop stall at its base, so nobody else sees it (Config/Hub).
local BaseKit = require(script.Parent.BaseKit)
local Hub = require(script.Parent.Config.Hub)
local World = require(script.Parent.World)

local Stall = {}

local SIGN_DISTANCE = 250

-- Builds a stall from Config/Hub (stall) standing at origin (Hub.stallCFrame) and returns it unparented.
function Stall.build(name: string, stall, origin: CFrame): Model
	local model = Instance.new("Model")
	model.Name = name

	BaseKit.place("base_Stall", origin, model, {
		StripeA = stall.stripes[1],
		StripeB = stall.stripes[2],
	})

	local signAnchor = World.makePart(model, "SignAnchor", Vector3.one, origin * CFrame.new(0, Hub.stallSize.Y + 4, 0), stall.stripes[1])
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
