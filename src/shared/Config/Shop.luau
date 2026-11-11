-- The Robux shop. Prices are set on the Creator Dashboard, not here; the game reads them
-- from Roblox. An id of 0 means the item isn't created yet: it shows as "SOON" and can't be bought.
-- giftProductId: GIFT (Shared/Gifts) can't buy a Game Pass for someone else, so each pass has a Developer Product,
-- priced the same, that gives the pass to the player it's gifted to (saved in their giftedPasses).
local Shop = {
	doubleCash = {
		passId = 2067284134, -- "x2 Cash"
		giftProductId = 3728639517, -- gift x2 Cash
		name = "x2 Cash",
		description = "All dinos earn double, forever",
		multiplier = 2,
	},
	doubleTraining = {
		passId = 2068562099, -- "x2 Training"
		giftProductId = 3728639599, -- gift x2 Training
		name = "x2 Training",
		description = "Every rep gives double XP, forever",
		multiplier = 2,
	},
	-- [Owner] Doubles the Throw Power every full bar on the squat rack gives (Config/Training).
	doublePower = {
		passId = 2071212524, -- "x2 Power", R$ 139
		giftProductId = 3728639807, -- gift x2 Power
		name = "x2 Power",
		description = "Every full bar gives double power, forever",
		multiplier = 2,
	},
	-- [Owner, 2026-11-05] The Prism Egg: a Developer Product bought again and again, like the reference's Rainbow Egg.
	-- It hatches at once into one of the special monsters below (Config/Specials), rolled on the server. Roblox wants
	-- the odds shown before buying, so the card shows these: keep them true, in %, adding up to 100.
	prismEgg = {
		productId = 3728638816, -- "Prism Egg"
		name = "Prism Egg",
		description = "Up to 700% of your best monster!",
		hatches = {
			{ id = "Duskeel", chance = 70 },
			{ id = "Umbray", chance = 25 },
			{ id = "Dreadlure", chance = 5 },
		},
	},
	serverLuck = {
		productId = 3728242175, -- "Server Luck x2", R$ 29
		name = "Server Luck x2",
		-- Roblox wants a luck boost's effect in numbers before buying: x2 luck doubles a rare monster's weight in the roll, and
		-- 2 ^ Catch.luckPower is about 1.3.
		description = "3 min for everyone: rare monsters about 2x likelier, colours and sizes 1.3x",
		multiplier = 2,
		seconds = 3 * 60, -- buying again while active adds more time [Owner, 2026-11-09: was 15 min]
		settleEvery = 5, -- seconds between updates of each buyer's saved time left
	},
	-- Asking Roblox which Game Passes a player owns can fail; a pass must never go missing because of that.
	passCheck = { attempts = 5, retryDelay = 3 }, -- seconds; doubles after each failed attempt
	-- After a pass is reported bought in the game, the server asks Roblox whether the player really owns it (the report
	-- itself can be faked): this many times, this many seconds apart. Roblox can be slow to say yes after a real purchase.
	passConfirm = { attempts = 12, every = 5 },
	-- Lucky throws: each is for ONE throw, kept until used; the next throw always uses the biggest one
	-- owned (LuckyThrows). The x number really multiplies that throw's luck, in the roll (DinoRoll) as well
	-- as on screen; description must say truthfully what that does.
	-- x100 has two Developer Products: the deal (R$ 3 on the Creator Dashboard), offered once per player
	-- with the sticker, then the regular one (R$ 9).
	luckyThrows = {
		{
			multiplier = 100,
			productId = 3728190780, -- "Luck x100"
			dealProductId = 3728190387, -- "ONE TIME DEAL LUCK x100"
			dealTag = "ONE TIME DEAL!",
			description = "Any throw you pick: a guaranteed 1 in 1M+ catch",
			colours = { "#e0a8ff", "#8a3fd6" },
		},
		{
			multiplier = 500,
			productId = 3728240108, -- "Luck x500", R$ 39
			description = "Any throw you pick: a guaranteed 1 in 100M+ catch",
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
	-- Lucky throws handed out by the owner: given when the player next joins, once per id. Keep old ids: removing one is
	-- safe, but reusing one means nothing is given.
	gifts = {
		{ id = "GIFT_LUCK500_20_2026-11-05", multiplier = 500, amount = 20, userIds = { 1404164940, 11729966071, 159677990 } },
		{ id = "GIFT_LUCK100_10_2026-11-06", multiplier = 100, amount = 10, userIds = { 234533860, 1404164940, 11729966071, 159677990 } },
		{ id = "GIFT_LUCK500_10_2026-11-06", multiplier = 500, amount = 10, userIds = { 234533860, 1404164940, 11729966071 } },
		{ id = "GIFT_LUCK500_20_2026-11-06", multiplier = 500, amount = 20, userIds = { 159677990 } },
		{ id = "GIFT_LUCK500_10_2026-11-08", multiplier = 500, amount = 10, userIds = { 159677990 } }, -- tibastefan123
		{ id = "GIFT_LUCK500_2_2026-11-08", multiplier = 500, amount = 2, userIds = { 11729966071 } }, -- pisorcos00
		{ id = "GIFT_LUCK100_10_2026-11-08", multiplier = 100, amount = 10, userIds = { 11729966071 } }, -- pisorcos00
	},
	-- Special monsters handed out by the owner, the same way: once per id, kept with the receipts. regive = true gives
	-- the monster again even though the save says it was given before (for a player who lost it); only use it for that.
	specialGifts = {
		{ id = "GIFT_GLOOMFIN_2026-11-06", special = "Gloomfin", userIds = { 159677990 } },
		{ id = "GIFT_GLOOMFIN_REGIVE_2026-11-08", special = "Gloomfin", userIds = { 159677990 }, regive = true }, -- tibastefan123
	},
	-- The owner's own test account: no Game Pass counts for it (its passes and the Game Pass monsters they gave are
	-- taken away when it loads). Roblox still lists the purchases, but the game ignores them. Other players are unaffected.
	ignorePassesFor = { 234533860 },
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
