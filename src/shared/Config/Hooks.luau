-- Small rewards that keep a run going (docs/GAME_SPEC.md section 8b). Placeholder numbers; tune
-- during playtesting. rarest counts from the end of a map's list in Config/Dinos (most common first), so
-- rarest = 3 means the map's 3 rarest monsters however many it has.
return {
	-- Pity: after this many throws in a row without one of the map's rarest monsters, the next throw
	-- is guaranteed one.
	pity = { throws = 25, rarest = 3 },
	-- Jackpot pity: after this many throws in a row without a map's rarest monster, the next one is it.
	-- With 6 monsters a map it comes naturally about 1 in 250 to 1 in 900 throws (a simulation of the roll,
	-- 2026-11-06), so this mostly helps unlucky players; 250 throws is roughly 2 hours of play.
	jackpotPity = { throws = 250, rarest = 1 },
	-- The first egg that lands in a biome you've never caught anything in hatches one of its rarest.
	newMapGift = { rarest = 3 },
	-- Landing this close before the next biome shows "SO CLOSE!" after the reveal.
	almostThere = { studs = 60 },
}
