-- The look of each boost in the row of icons at the bottom of the screen (BoostRowController; Figma "Throw Eggs -
-- Pop-up Text", "Active boosts"). What the boosts do lives in Config/Shop, Config/Index and Config/Catch.
return {
	serverLuck = { color = Color3.fromRGB(141, 255, 90) },
	xp = { color = Color3.fromRGB(111, 227, 255) },
	-- By multiplier. The clover takes the colour too. x50 only comes from the daily reward (Config/Daily).
	luckyThrows = {
		[500] = { color = Color3.fromRGB(255, 210, 63) },
		[100] = { color = Color3.fromRGB(224, 168, 255) },
		[50] = { color = Color3.fromRGB(255, 154, 213) },
	},
}
