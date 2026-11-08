-- Sounds of the interface (UiClickSound). From ElevenLabs, uploaded by the owner. An empty id is simply silent.
return {
	click = "rbxassetid://92957196484020", -- sounds/ui_click_v2_a_loud.mp3 (the first upload was 30 dB too quiet): every button tap, unless the button has the attribute NoClickSound
	clickVolume = 0.5,
	clickScreens = { "ShopHud", "IndexHud" }, -- the click only plays for buttons inside these screens (the shop and the index)
	clickPitch = { 0.97, 1.05 }, -- a little different each time, so rapid taps don't sound machine-made
}
