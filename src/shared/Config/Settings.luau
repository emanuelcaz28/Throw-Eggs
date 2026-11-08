-- The player's settings (Figma "Throw Eggs - Settings UI", mock-ups 18 to 18c): music and sound effect volume, 0 to 100, and
-- whether other players' dinos are hidden. Saved with the player's data (SettingsService) and applied on their client
-- (SettingsState, SettingsController).
return {
	defaults = {
		music = 80, -- percent of the music's own volume (Config/Music)
		sfx = 100, -- percent of every sound effect's volume
		hideDinos = false, -- other players' dinos stay hidden: "Other bases look empty to you. Helps on slow phones."
	},
	step = 5, -- the sliders move in steps of this many percent
}
