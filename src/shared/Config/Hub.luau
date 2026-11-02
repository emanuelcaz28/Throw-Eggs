-- The market stalls in the hub. Stepping on a stall's pad opens its panel; walking off closes it.
-- position is the centre of the stall's floor; the stall faces +Z (towards spawn) and its pad
-- sits in front of the counter.
local Hub = {
	stallSize = Vector3.new(12, 9, 8), -- width, height to the awning, depth
	padRadius = 3.5,
	padHeight = 8,
	padGap = 4.5, -- studs from the counter's front to the pad's centre

	eggStall = {
		position = Vector3.new(6, 0, -20),
		title = "EGG SHOP",
		stripes = { Color3.fromRGB(60, 140, 220), Color3.fromRGB(240, 240, 240) },
		padColor = Color3.fromRGB(70, 220, 230),
	},
	sellStall = {
		position = Vector3.new(26, 0, -20),
		title = "SELL",
		stripes = { Color3.fromRGB(220, 50, 50), Color3.fromRGB(240, 240, 240) },
		padColor = Color3.fromRGB(230, 60, 60),
	},
}

-- Where a stall's pad sits on the ground.
function Hub.padPosition(stall): Vector3
	return stall.position + Vector3.new(0, 0, Hub.stallSize.Z / 2 + Hub.padGap)
end

-- Whether a character's root part is standing on a stall's pad.
function Hub.isOnPad(stall, rootPosition: Vector3): boolean
	local offset = rootPosition - Hub.padPosition(stall)
	return Vector2.new(offset.X, offset.Z).Magnitude <= Hub.padRadius and offset.Y >= 0 and offset.Y <= Hub.padHeight
end

return Hub
