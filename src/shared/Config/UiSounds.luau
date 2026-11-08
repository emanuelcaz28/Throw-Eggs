-- Sounds of the interface (UiClickSound). From ElevenLabs, uploaded by the owner. An empty id is simply silent.
return {
	click = "rbxassetid://104040155289982", -- [Owner, 2026-11-08] the owner's new click (replaced ui_click_v2_a_loud.mp3, 92957196484020): every button tap, unless the button has the attribute NoClickSound
	clickVolume = 0.5,
	clickScreens = { "ShopHud", "IndexHud" }, -- the click only plays for buttons inside these screens (the shop and the index)
	clickPitch = { 0.97, 1.05 }, -- a little different each time, so rapid taps don't sound machine-made
}
