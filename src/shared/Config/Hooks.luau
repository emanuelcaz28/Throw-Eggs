-- Small rewards that keep a run going (docs/GAME_SPEC.md section 8b). Placeholder numbers; tune
-- during playtesting. rarest counts from the end of a map's list in Config/Dinos (most common first), so
-- rarest = 3 means the map's 3 rarest monsters however many it has, not counting its prizes (Config/Dinos).
return {
	-- Pity: after this many throws in a row without one of the map's rarest monsters, the next throw
	-- is guaranteed one.
	pity = { throws = 25, rarest = 3 },
	-- Jackpot pity: after this many throws in a row without a map's rarest monster, the next one is it.
	-- With 6 monsters a map it comes naturally about 1 in 250 to 1 in 900 throws (a simulation of the roll,
	-- 2026-11-06), so this mostly helps unlucky players; 250 throws is roughly 2 hours of play.
	jackpotPity = { throws = 250, rarest = 1 },
	-- End-game streak [Owner, 2026-11-14: the end-game monsters were "that unfair for free players", fix it without
	-- making them "way too powerful"]. On a map with a 9th to 12th monster (Config/Dinos apex), after this many throws
	-- in a row there without catching one of them, the next plain throw is the map's 9th or 10th (minPlace/maxPlace:
	-- Nightmare about 4 times in 5, Doomsday 1 in 5, by their own odds), with colour and size rolled as usual. Never
	-- the 11th or 12th: Oblivion and Unknown stay for luck and x500. 300 throws is about two and a half hours of
	-- throwing, so a free player who plays an hour a day gets one or two a week; a x500 gives one 1 time in 4 at once.
	-- Catching one any other way starts the count again. A throw with another guarantee, or a lucky throw, keeps its
	-- own rules and the streak waits for the next plain one. Told after the reveal ("NIGHTMARE STREAK!").
	apexStreak = { throws = 300, minPlace = 9, maxPlace = 10 },
	-- Surprise gift [Owner, 2026-11-08]: every 60th throw is a Legendary or a Mythic (rarity words 5 and 6,
	-- Config/RarityLadder), never Ancient or Secret, and only one in the rarer half of its map (minPlace: 5th place or
	-- rarer). It only counts on maps that have one, where Legendary and Mythic are high rarities: maps 3 to 11 and The
	-- Deep End. Throws on maps 1-2 (no Legendary) and 12-15 (there they're the commonest) don't count towards the 60
	-- [Owner, 2026-11-08]. A lucky throw on the 60th keeps its own odds and the gift waits for the next plain one.
	-- prizeOnlyRarity: where the only Legendaries are the map's prizes (maps 3 and 4), the gift is one of its Epics
	-- (rarity 4) instead [Owner, 2026-11-08: "for the 3 and 4 only give an epic from those 2"]. A fixed beat, not pity: a Legendary caught on its own doesn't move it. No countdown is
	-- shown ("they should not see it coming"). Normal odds pick which of the two, so Legendary is the usual one.
	-- A throw that already has a guarantee (new map, jackpot, a lucky throw, the tutorial) keeps it, and the gift
	-- waits for the next plain throw.
	surpriseGift = { throws = 60, minRarity = 5, maxRarity = 6, minPlace = 5, prizeOnlyRarity = 4 },
	-- The first egg that lands in a biome you've never caught anything in hatches one of its rarest.
	newMapGift = { rarest = 3 },
	-- Starter run [Owner, 2026-11-10: "on their third or fourth throw they always get Compy, which makes no sense";
	-- new players need better monsters and that dopamine to stay, docs/GROWTH_PLAYBOOK.md]. A save's first `catches`
	-- catches (the tutorial's two included) never give one of the map's `skipCommonest` commonest monsters, and while
	-- a monster above those (not counting the map's prizes) is still missing from the player's Index, the catch is one
	-- of the missing ones: every early throw is a NEW monster, climbing to the map's rarest. After that, normal odds
	-- from the third commonest up. The tutorial's set throws, a lucky throw and the new-map gift keep their own rules.
	-- Hidden, like the surprise gift: it's never named on screen.
	starterRun = { catches = 10, skipCommonest = 2, newFirst = true },
	-- Big shots [Owner, 2026-11-11: after the starter boosts, three fixed lucky shots so new players feel great]. Once a
	-- new player has caught something on map `fromMap` (its new-world gift comes first), their next plain throws that
	-- land on that map or any later one give these, in order, with this size and colour. Throws that only land on map 1
	-- don't use one, and a throw with another guarantee (a new world's gift, a lucky throw) keeps it and the shot waits.
	-- Only saves started after this was added (Config/Save bigShotsLeft). Hidden, like the gift: the reveal shows the
	-- size and colour, nothing says it was set.
	-- The monster [Owner, 2026-11-11: never the map's rarest, and not always Scorchion, and not so rich it skips a map]:
	-- the rarest one on the map it lands on, never its very rarest, whose $/s with the shot's size and colour stays at
	-- or under incomeCap times the map's best normal monster (its rarest before the prizes, plain). The bigger the size
	-- and colour, the commoner the monster, so map 2 gives Scorchion, then T-Rex, then Carnotaurus, and every shot earns
	-- about 15x the map's best normal monster: a great pet, about a good catch on the next map.
	bigShots = {
		fromMap = 2,
		incomeCap = 20,
		shots = {
			{ size = "AbsoluteUnit", mutation = "Gold" },
			{ size = "Chonker", mutation = "Ruby" },
			{ size = "MegaChonk", mutation = "Diamond" },
		},
	},
	-- Landing this close before the next biome shows "SO CLOSE!" after the reveal.
	almostThere = { studs = 60 },
}
