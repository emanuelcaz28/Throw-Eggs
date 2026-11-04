-- Small rewards that keep a run going (docs/GAME_SPEC.md section 8b). Placeholder numbers; tune
-- during playtesting. A rank is a monster's place in its biome's list in Config/Dinos: 1 is the most
-- common, 6 the rarest.
return {
	-- Pity: after this many throws in a row without a monster of minRank or rarer, the next throw
	-- is guaranteed one.
	pity = { throws = 25, minRank = 4 },
	-- The first egg that lands in a biome you've never caught anything in hatches minRank or rarer.
	newMapGift = { minRank = 4 },
	-- Landing this close before the next biome shows "SO CLOSE!" after the reveal.
	almostThere = { studs = 60 },
}
