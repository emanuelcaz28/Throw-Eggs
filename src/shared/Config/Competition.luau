-- Competition inside a server (docs/GAME_SPEC.md section 12): players ranked by $/s. #1 wears a crown
-- and the top three bases glow and show a medal on their owner plate. Also "first to reach a world".
return {
	rankEvery = 2, -- seconds between re-ranking
	medals = { -- #1, #2, #3: colour and the word on the owner plate
		{ color = Color3.fromRGB(255, 201, 60), label = "👑 #1" },
		{ color = Color3.fromRGB(200, 212, 230), label = "#2" },
		{ color = Color3.fromRGB(226, 146, 84), label = "#3" },
	},
	crown = {
		color = Color3.fromRGB(255, 201, 60),
		gem = Color3.fromRGB(230, 40, 70),
		lift = 1.1, -- studs above the head's top
	},
	-- The ranking list in the top left, and the "overtaken" alert when someone passes you.
	listRows = 5,
}
