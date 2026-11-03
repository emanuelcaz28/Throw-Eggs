-- The Robux shop. Prices are set on the Creator Dashboard, not here; the game reads them
-- from Roblox. An id of 0 means the item isn't created yet: it shows as "SOON" and can't be bought.
local Shop = {
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
	-- Cash packs: Developer Products that pay this many minutes of the plot's $/s (events not
	-- counted), never less than minimum, so they stay worth buying as the plot grows.
	cashPacks = {
		{ productId = 0, minutes = 10, minimum = 1000, art = "cash_S" }, -- paste each Developer Product id here
		{ productId = 0, minutes = 60, minimum = 6000, art = "cash_M", tag = "+30% MORE", tagStyle = "green" },
		{ productId = 0, minutes = 300, minimum = 30000, art = "cash_L", tag = "+50% MORE", tagStyle = "purple" },
		{ productId = 0, minutes = 1800, minimum = 180000, art = "cash_XL", tag = "+100% MORE", tagStyle = "tagGold" },
	},
	-- Throw Power packs: Developer Products that add Throw Power for good, on top of training.
	-- 20 power is one training level (Config/Training powerPerLevel). tag is the sticker on the
	-- card; keep it true to the prices set on the Creator Dashboard. art is a block model name.
	powerPacks = {
		{ productId = 0, amount = 100, art = "bolts_S" }, -- paste each Developer Product id here
		{ productId = 0, amount = 600, art = "bolts_M", tag = "+30% MORE", tagStyle = "green" },
		{ productId = 0, amount = 3000, art = "bolts_L", tag = "+50% MORE", tagStyle = "purple" },
		{ productId = 0, amount = 10000, art = "bolts_XL", tag = "+100% MORE", tagStyle = "tagGold" },
	},
	starterDino = {
		name = "Free Starter Dino",
		description = "A free Gallimimus to start your plot",
		id = "Gallimimus",
		biomeId = "Forest",
	},
}

-- What a cash pack pays a player whose plot earns baseIncome $/s (without events).
function Shop.cashPackAmount(pack, baseIncome: number): number
	return math.max(math.floor(baseIncome * pack.minutes * 60), pack.minimum)
end

return Shop
