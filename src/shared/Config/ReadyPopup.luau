-- Ready pop-ups: a card at the top of the screen the moment the player can afford the next squat rack upgrade
-- ("UPGRADE" buys it from anywhere) or the next egg ("SHOP" opens the Egg Shop from anywhere), like the reference
-- game's "new equipment" and "new food" cards. Design: Figma "Throw Eggs - Tutorial", Ready Pop-up
-- (https://www.figma.com/design/dBuqHxoqQRZ0KrgtU0zve5). Each card shows once per upgrade or egg, never during
-- the tutorial (it has its own upgrade and egg steps). Sizes are design pixels on the 1280 x 720 screen.
return {
	showFor = 8, -- seconds a card stays (the yolk timer bar runs down); X closes it sooner
	gap = 1.5, -- seconds between two cards when both are ready at once
	settle = 5, -- seconds the rack price must hold still first, so buying upgrade after upgrade on the pad shows no card
	firstDelay = 6, -- seconds after joining before the first card, so it doesn't land on the welcome pop-up
	top = 14, -- design px under the top of the safe area (where the tutorial banner sat)
	width = 520,
	touchBoost = 1.3, -- phones and tablets: the card is this much bigger so its buttons are easy to tap
	maxScreenShare = 0.7, -- and never wider than this share of the screen

	rack = {
		title = "UPGRADE READY!",
		newRackTitle = "NEW RACK!", -- when the upgrade brings a new rack model (Config/Training rackModels)
		lead = "You can afford",
		button = "UPGRADE",
		header = { "B57CFF", "7A3CF0" },
		tile = { "6FE3FF", "2D8CD6" },
	},
	egg = {
		title = "NEW EGG READY!",
		lead = "You can afford",
		button = "SHOP",
		header = { "FFD23F", "FF8A1F" },
	},

	buyCooldown = 1, -- server: seconds between two upgrades bought from the card (a double tap buys one)
}
