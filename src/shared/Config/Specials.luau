-- Special monsters: from no map, earning a share of the buyer's best monster. The income is fixed when given and saved
-- on the monster, and other special monsters never count as "best", so one can't multiply another. Ids are saved, so
-- never rename one. Models: assets/models/build_special_monsters.py.
--   With a passId: a Game Pass, bought once. It can't be sold, since the pass only gives its monster once.
--   With an egg: hatched from that Robux egg (Config/Shop prismEgg), which can be bought again and again, so these
--   can be sold like any monster.
return {
	{
		id = "Gloomfin",
		name = "Gloomfin",
		passId = 2072970340, -- "Gloomfin", R$ 499
		giftProductId = 3728641289, -- "Gift Gloomfin", priced like the pass (Config/Shop explains)
		share = 9, -- 900% of your best monster's $/s
		minimumIncome = 100, -- counted as the best monster's $/s for a player with nothing better yet
		description = "The angriest shark there is. It bites every 4 seconds",
	},
	-- The Prism Egg's three: Gloomfin's dark family (owner's choice, 2026-11-05).
	{
		id = "Duskeel",
		name = "Duskeel",
		egg = "PrismEgg",
		share = 1.5, -- 150%
		minimumIncome = 100,
		description = "A rearing serpent with a burning sail",
	},
	{
		id = "Umbray",
		name = "Umbray",
		egg = "PrismEgg",
		share = 3, -- 300%
		minimumIncome = 100,
		description = "A bat-winged ray with hooked horns",
	},
	{
		id = "Dreadlure",
		name = "Dreadlure",
		egg = "PrismEgg",
		share = 7, -- 700%
		minimumIncome = 100,
		description = "A hulking anglerfish that is mostly mouth",
	},
}
