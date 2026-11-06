-- The market stalls. Stepping on a stall's pad opens its panel; walking off closes it.
-- Each base has its own Egg Shop stall, right outside the fence left of the gate, which only the
-- base's owner can see (EggShopController builds it on their client). The SELL stall is shared and
-- stands in the arena's open ground. A stall faces `facing`, and its pad sits in front of the counter.
local Plot = require(script.Parent.Plot)

local Hub = {
	stallSize = Vector3.new(12, 9, 8), -- width, height to the awning, depth
	padRadius = 3.5,
	padHeight = 8,
	padGap = 4.5, -- studs from the counter's front to the pad's centre

	eggStall = {
		offset = Vector3.new(15, 0, -5), -- from the middle of its base's gate (Plot.gatePosition)
		facing = Vector3.new(0, 0, -1), -- out of the base
		title = "EGG SHOP",
		stripes = { Color3.fromRGB(60, 140, 220), Color3.fromRGB(240, 240, 240) },
		padColor = Color3.fromRGB(70, 220, 230),
	},
	sellStall = {
		-- Front left of the arena seen from the platform, out in the open ground, its counter and pad facing the
		-- bases, where players come from (it used to face the front wall, showing them its back).
		position = Vector3.new(64, 0, 30), -- beside the throw platform, where a leaderboard stood (2026-11-05)
		facing = Vector3.new(0, 0, 1),
		title = "SELL",
		stripes = { Color3.fromRGB(220, 50, 50), Color3.fromRGB(240, 240, 240) },
		padColor = Color3.fromRGB(230, 60, 60),
	},
}

-- Where a stall stands: the centre of its floor, turned to face its way. The egg stall needs the
-- base it belongs to.
function Hub.stallCFrame(stall, plotIndex: number?): CFrame
	local position = if stall.offset and plotIndex then Plot.gatePosition(plotIndex) + stall.offset else stall.position
	return CFrame.lookAt(position, position + stall.facing)
end

-- Where a stall's pad sits on the ground.
function Hub.padPosition(stallCFrame: CFrame): Vector3
	return stallCFrame.Position + stallCFrame.LookVector * (Hub.stallSize.Z / 2 + Hub.padGap)
end

-- Whether a character's root part is standing on a stall's pad.
function Hub.isOnPad(stallCFrame: CFrame, rootPosition: Vector3): boolean
	local offset = rootPosition - Hub.padPosition(stallCFrame)
	return Vector2.new(offset.X, offset.Z).Magnitude <= Hub.padRadius and offset.Y >= 0 and offset.Y <= Hub.padHeight
end

return Hub
