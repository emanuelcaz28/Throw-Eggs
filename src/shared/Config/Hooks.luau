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
	-- Landing this close before the next biome shows "SO CLOSE!" after the reveal.
	almostThere = { studs = 60 },
}
