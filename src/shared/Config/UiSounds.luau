-- Sounds of the interface and the game's small moments (UiClickSound, GameFeelSounds, Sfx). An empty id is simply
-- silent. To swap a sound, paste a new id here: everything else follows.
return {
	click = "rbxassetid://129944293842553", -- [Owner, 2026-11-10] "sound-1" (assets/sounds/ui_click.mp3), every button tap unless the button has the attribute NoClickSound; was the ElevenLabs click 104040155289982
	clickVolume = 0.5,
	-- The screens whose buttons click. nil = every screen [Owner, 2026-11-10: satisfying sounds for the whole UI; it
	-- was { "ShopHud", "IndexHud" } only before].
	clickScreens = nil :: { string }?,
	clickPitch = { 0.97, 1.05 }, -- a little different each time, so rapid taps don't sound machine-made

	-- [Owner, 2026-11-10] the moments that had no sound (docs/GROWTH_PLAYBOOK.md "action and response"). Free Creator
	-- Store sounds picked 2026-11-10 without being heard: listen in Studio and swap any that don't feel right.
	-- id, volume, pitch = { lowest, highest } picked at random each time.
	moments = {
		-- One squat: a soft pop that climbs in pitch as the bar fills (pitch is stretched by squatClimb below).
		squat = { id = "rbxassetid://17779566040", volume = 0.35, pitch = { 0.95, 1.0 } }, -- "minimal-pop-click-ui"
		-- A power bar filled: Throw Power went up.
		powerUp = { id = "rbxassetid://112485797063762", volume = 0.6, pitch = { 1, 1 } }, -- "UI - Level Up"
		-- Cash spent: rack upgrade, egg, plot upgrade, feeding.
		purchase = { id = "rbxassetid://134810204798705", volume = 0.55, pitch = { 0.98, 1.04 } }, -- "Cash Register"
		-- Cash gained that isn't the per-second income: selling, offline earnings, gifts, daily rewards.
		cash = { id = "rbxassetid://135483737426662", volume = 0.5, pitch = { 0.97, 1.06 } }, -- "Coin Collect"
		-- A monster put down on your plot.
		place = { id = "rbxassetid://73843963159060", volume = 1, pitch = { 0.97, 1.03 } }, -- [Owner, 2026-11-10] "sound-3" (was "sound-2", 84874091543221)
		-- A tutorial step done.
		step = { id = "rbxassetid://103516326607012", volume = 0.5, pitch = { 1, 1 } }, -- "achievement bell" (mixkit)
		-- A monster caught for the first time (NEW in the Index), as its card shows.
		discovery = { id = "rbxassetid://4612374393", volume = 0.6, pitch = { 1, 1 } }, -- "bling_diamond_pickup_2"
		-- A pop-up: the ready cards (UPGRADE / SHOP) and the big shouts (events, Index complete, rewards, hooks).
		popup = { id = "rbxassetid://109791938627797", volume = 0.6, pitch = { 0.98, 1.03 } }, -- [Owner, 2026-11-10] "sound-12" (assets/sounds/popup.mp3)
		-- Tried to buy an egg or a squat rack upgrade without enough cash.
		error = { id = "rbxassetid://121739806488164", volume = 0.3, pitch = { 1, 1 } }, -- [Owner, 2026-11-10] "Error Sound Effect - Soundspace Sound Effects"
	},
	squatClimb = 0.35, -- the squat pop is this much higher-pitched on a nearly full bar than on an empty one
	cashMinGap = 0.25, -- seconds: cash sounds closer together than this play once (no machine-gun on a big sale)
}
