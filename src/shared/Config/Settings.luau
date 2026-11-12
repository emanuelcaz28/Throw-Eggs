-- The player's settings (Figma "Throw Eggs - Settings UI", mock-ups 18 to 18c): music and sound effect volume, 0 to 100, and
-- whether other players' dinos are hidden. Saved with the player's data (SettingsService) and applied on their client
-- (SettingsState, SettingsController). The Power Limit (Config/PowerLimit, PowerLimitController) is saved here too.
return {
	defaults = {
		music = 80, -- percent of the music's own volume (Config/Music)
		sfx = 100, -- percent of every sound effect's volume
		hideDinos = false, -- other players' dinos stay hidden: "Other bases look empty to you. Helps on slow phones."
		powerLimitOn = false, -- eggs never fly past powerLimit (Config/PowerLimit)
		powerLimit = 0, -- in power; 0 until the player first sets one
		leashMe = true, -- "Let players leash me": off, and nobody can leash this player (Config/Troll playerLeash)
	},
	step = 5, -- the sliders move in steps of this many percent
	-- The highest each number may be (the lowest is 0). Volumes are percent.
	max = { music = 100, sfx = 100, powerLimit = 1e15 },
}
