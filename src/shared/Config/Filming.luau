-- Filming mode, for recording TikTok clips in Studio only (FilmingService, FilmingController).
-- Turn it on: in Edit mode select Workspace, add the attribute below as a ticked boolean, then press Play.
-- While it's on: your real save is loaded as a copy that is never written, the tutorial is skipped, a FILM panel
-- picks the monster every throw catches (and the egg lands in that monster's map), and the hide key clears the HUD.
-- It never does anything in the live game: both sides check RunService:IsStudio().
return {
	attribute = "StudioFilming", -- the Workspace attribute that turns it on
	hideKey = Enum.KeyCode.H, -- hides / shows the HUD and Roblox's own buttons (chat, player list, backpack)
	landAt = 0.55, -- where in the picked map the egg lands: 0 its near edge, 1 its far edge
	-- What stays on screen with the HUD hidden: the throw meter, the flight fade and the whole reveal. Every other
	-- ScreenGui in PlayerGui is hidden (so new HUD added later is hidden too).
	keepVisible = { "ThrowHud", "ThrowBars", "ThrowFade", "DoorBurst", "PerfectMoment" }, -- the FILM button hides too
	keepPrefix = "Reveal", -- any ScreenGui whose name starts with this stays (RevealHud, RevealBehind, ...)
}
