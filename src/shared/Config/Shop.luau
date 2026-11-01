-- The Robux shop. Prices are set on the Creator Dashboard, not here; the game reads them
-- from Roblox. An id of 0 means the item isn't created yet: it shows as "SOON" and can't be bought.
return {
	doubleCash = {
		passId = 0, -- paste the Game Pass id here
		name = "x2 Cash",
		description = "All dinos earn double, forever",
		multiplier = 2,
	},
	doubleTraining = {
		passId = 0, -- paste the Game Pass id here
		name = "x2 Training",
		description = "Every rep gives double XP, forever",
		multiplier = 2,
	},
	serverLuck = {
		productId = 0, -- paste the Developer Product id here
		name = "Server Luck x2",
		description = "2x luck for everyone here for 15 minutes",
		multiplier = 2,
		seconds = 15 * 60, -- buying again while active adds more time
	},
	starterDino = {
		name = "Free Starter Dino",
		description = "A free Gallimimus to start your plot",
		id = "Gallimimus",
		biomeId = "FernValley",
	},
}
