-- The server's best catch: the rarest monster anyone has caught in this server since it started, standing on a
-- pedestal at the side of the arena at
-- its map's standard size, never its size mutation's, so a 1-in-a-million giant doesn't swallow the arena. Its
-- colour mutation stays. A title over it shows the owner and a card at its side its stats, both fixed in the map.
return {
	-- The pedestal's foot (Config/Map: floor Y = 0, platform edge Z = 16, bases from Z = 96, walls at X = +-144): the
	-- open front-left of the arena, behind the leaderboards and clear of base 1's rack, so nobody walking between a
	-- base and the throw platform has to go round it (the middle was in the way, 2026-11-05).
	position = Vector3.new(-72, 0, 28), -- beside the leaderboards, between them and the throw platform (owner, 2026-11-05)
	facing = Vector3.new(0, 0, 1), -- the monster, its title and its card face the bases
	standHeight = 4.6, -- the cushion's top over the pedestal's foot (assets/models/build_best_catch.py TOP_Z)
	modelFolder = { "Forest", "Arena" }, -- in ReplicatedStorage.Assets.Maps, like the leaderboards
	modelName = "prop_BestCatchPedestal",
	monsterScale = 2, -- the monster stands this many times its map's standard size
	titleWidth = 20, -- studs, the title over the monster (Figma "Best monster title"); it turns to face the viewer
	titleGap = 0.5, -- studs between the monster's head and the title
	statsPixelsPerStud = 36, -- the stats text beside it (Figma "Best monster stats", 360 x 270) is then 10 x 7.5 studs
	statsGap = 0.5, -- studs between the monster and its stats
	panelMaxDistance = 220,
}
