-- The Robux shop. Prices are set on the Creator Dashboard, not here; the game reads them
-- from Roblox. An id of 0 means the item isn't created yet: it shows as "SOON" and can't be bought.
local Shop = {
	doubleCash = {
		passId = 2067284134, -- "x2 Cash"
		name = "x2 Cash",
		description = "All dinos earn double, forever",
		multiplier = 2,
	},
	doubleTraining = {
		passId = 2068562099, -- "x2 Training"
		name = "x2 Training",
		description = "Every rep gives double XP, forever",
		multiplier = 2,
	},
	-- [Owner] Doubles the Throw Power every full bar on the squat rack gives (Config/Training).
	doublePower = {
		passId = 2071212524, -- "x2 Power", R$ 139
		name = "x2 Power",
		description = "Every full bar gives double power, forever",
		multiplier = 2,
	},
	serverLuck = {
		productId = 3728242175, -- "Server Luck x2", R$ 29
		name = "Server Luck x2",
		description = "2x luck for everyone here for 15 minutes",
		multiplier = 2,
		seconds = 15 * 60, -- buying again while active adds more time
	},
	-- Lucky throws: each is for ONE throw, kept until used; the next throw always uses the biggest one
	-- owned (LuckyThrows). The x number is for show (the luck number in flight); what each one really
	-- hatches is Config/LuckyOutcomes, and description must say so truthfully.
	-- x100 has two Developer Products: the deal (R$ 3 on the Creator Dashboard), offered once per player
	-- with the sticker, then the regular one (R$ 9).
	luckyThrows = {
		{
			multiplier = 100,
			productId = 3728190780, -- "Luck x100"
			dealProductId = 3728190387, -- "ONE TIME DEAL LUCK x100"
			dealTag = "ONE TIME DEAL!",
			description = "Next throw: a rare monster with a colour, guaranteed",
			colours = { "#e0a8ff", "#8a3fd6" },
		},
		{
			multiplier = 500,
			productId = 3728240108, -- "Luck x500", R$ 39
			description = "Next throw: the map's rarest, rare colour, GIANT",
			colours = { "#fff1a8", "#ffb21a" },
		},
	},
	-- Cash packs: Developer Products that pay this many minutes of the plot's $/s (events not
	-- counted), never less than minimum, so they stay worth buying as the plot grows.
	cashPacks = {
		{ productId = 3728242268, minutes = 10, minimum = 1000, art = "cash_S" }, -- "Cash Pack S", R$ 9
		{ productId = 3728242360, minutes = 60, minimum = 6000, art = "cash_M", tag = "+30% MORE", tagStyle = "green" }, -- R$ 41
		{ productId = 3728242484, minutes = 300, minimum = 30000, art = "cash_L", tag = "+50% MORE", tagStyle = "purple" }, -- R$ 179
		{ productId = 3728242580, minutes = 1800, minimum = 180000, art = "cash_XL", tag = "+100% MORE", tagStyle = "tagGold" }, -- R$ 799
	},
	-- Throw Power packs: Developer Products that add this much Throw Power straight to the player's stats,
	-- for good, on top of training. [Owner] Small amounts at small prices, so everything looks cheap. tag is
	-- the sticker on the card; keep it true to the prices set on the Creator Dashboard. art is a block model.
	powerPacks = {
		-- R$ 19 / 39 / 69: per Robux, +500 gives 2.4x and +1,000 2.7x what +100 does (rounded down on the tags).
		{ productId = 3728240331, amount = 100, art = "bolts_S" }, -- "+100 Power", R$ 19
		{ productId = 3728240522, amount = 500, art = "bolts_L", tag = "+140% MORE", tagStyle = "green" }, -- R$ 39
		{ productId = 3728240659, amount = 1000, art = "bolts_XL", tag = "+170% MORE", tagStyle = "purple" }, -- R$ 69
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
