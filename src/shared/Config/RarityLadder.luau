-- Each map's rarity words, one per monster in its Config/Dinos list (commonest first) [Owner, 2026-11-08: "as you make
-- progress in the game the rarities should only be higher"]. Map 1 tops out at Epic, the first Legendary is on map 3,
-- the first Secret on map 11, and map 15 is half Secrets. Only the word changes: the odds stay in Config/Dinos.
-- Rules that name a rarity follow these words: the surprise gift (Config/Hooks) and x100/x500 lucky throws
-- (Config/Catch luckyHits). The Deep End mixes every map, so its monsters keep their home map's word.
-- C Common, U Uncommon, R Rare, E Epic, L Legendary, M Mythic, A Ancient, S Secret.
-- [Owner, 2026-11-14] Four more words above Secret, only for the end-game maps' 9th to 12th monsters (Config/Dinos
-- apex): N Nightmare, D Doomsday, O Oblivion, X Unknown. And no Mythic from The Weeping Dark on.
-- A new 12-monster map: its first 8 letters one step up from the map before, then N D O X (docs/MAP_RECIPE.md).
local WORDS = {
	C = "common",
	U = "uncommon",
	R = "rare",
	E = "epic",
	L = "legendary",
	M = "mythic",
	A = "ancient",
	S = "secret",
	N = "nightmare",
	D = "doomsday",
	O = "oblivion",
	X = "unknown",
}

local ladder = {
	Forest = "CCCUURRE", -- map 1
	Desert = "CCUURREE", -- map 2
	Swamp = "UURRREEL", -- map 3
	Volcano = "UURREELL", -- map 4
	FrozenPeaks = "URREELLM", -- map 5
	ShadowBog = "RREELLMM", -- map 6
	Abyss = "REELLLMM", -- map 7
	StarfallCrater = "REELLMMA", -- map 8
	EclipseTemple = "EELLMMAA", -- map 9
	ForbiddenLibrary = "ELLMMMAA", -- map 10
	MidnightCarnival = "ELLMMAAS", -- map 11
	ClockworkCitadel = "LLMMAAAS", -- map 12
	ThornKingdom = "LLMMAASS", -- map 13
	SporeHollow = "MMAAASSSNDOX", -- map 14
	WeepingDark = "AAAASSSSNDOX", -- map 15
	ShatteredMirror = "AAASSSSSNDOX", -- map 16 (used once its monsters are in Config/Dinos)
}

-- byBiome: biome id -> list of rarity words, commonest monster first. order: every word, commonest first; a word's
-- place in it is its level (1 Common ... 8 Secret, 9 Nightmare, 10 Doomsday, 11 Oblivion, 12 Unknown).
local byBiome = {}
for biomeId, letters in ladder do
	local words = {}
	for index = 1, #letters do
		table.insert(words, WORDS[string.sub(letters, index, index)])
	end
	byBiome[biomeId] = words
end

return {
	order = { "common", "uncommon", "rare", "epic", "legendary", "mythic", "ancient", "secret", "nightmare", "doomsday", "oblivion", "unknown" },
	byBiome = byBiome,
}
