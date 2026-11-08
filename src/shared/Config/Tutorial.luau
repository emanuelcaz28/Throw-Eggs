-- The new-player tutorial (docs/GDD.md "New-player tutorial"). Its flow follows the reference game's tutorial, from
-- the owner's recording (2026-11-07): throw, place the catch, upgrade the rack, train, buy a better egg, throw again,
-- place again. No text but a word or two on the arrow (owner, 2026-11-08). Design: Figma "Throw Eggs - Tutorial"
-- (https://www.figma.com/design/dBuqHxoqQRZ0KrgtU0zve5). The server decides the two tutorial catches (ThrowService,
-- TutorialService); the client only shows the steps and saves how far the player got. Tune during playtesting.
local Tutorial = {
	-- The first egg ever thrown hatches this monster of the map it lands in (1 = the most common), with no colour or
	-- size: a modest start, like the reference's first catch. It replaces that map's new-world gift (Config/Hooks).
	firstThrow = { rank = 3 },
	-- The second egg is always better than the first: one of the map's `rarest` rarest monsters (not counting its
	-- prizes, Config/Dinos), and never one earning less than the first catch. Colour and size are rolled as usual.
	secondThrow = { rarest = 3 },
	-- Both tutorial catches go onto the player's head instead of straight onto the base, so the player places them.
	carryCatches = true,
	trainBars = 5, -- power bars to fill on the rack before the next step (the reference's player did about 5 levels)
	freeFeed = false, -- the old feeding step's free feed (the feeding step was dropped 2026-11-08)

	-- In order, staged so each step pays for the next (owner, 2026-11-08): two throws first, so their monsters earn the
	-- cash for the upgrade and the egg, then train, buy the egg and throw with it. No banner and no instructions: the
	-- player follows the beam and the arrow. word: a word or two over the arrow, only where the spot alone doesn't say
	-- what to do. A step is done as soon as what it asks for is true (TutorialController).
	steps = {
		{ id = "throw" },
		{ id = "place" },
		{ id = "throw2" },
		{ id = "place2" },
		{ id = "upgrade", word = "Upgrade!" },
		{ id = "train" },
		{ id = "egg", word = "New egg!" },
		{ id = "throw3" },
	},
	throwsCounted = 3, -- throws the save counts for the steps: the two set catches, then the one with the new egg

	-- HUDs hidden until the tutorial is over: nothing but cash, power, training and throwing on screen. Names are
	-- ScreenGuis in PlayerGui; "PlotHud/OpenDinos" hides one button inside one.
	hiddenHuds = {
		"IndexHud", "ShopHud", "DailyButtonHud", "DailyHud", "BoostHud", "BoostCardHud", "GoalHud", "SettingsHud", "SettingsButtonHud",
		"LuckyBannerHud", "LuckOffer", "WelcomeHud", "GiftHud", "ReadyPopupHud",
		"PlotHud/OpenDinos",
	},

	-- What the player sees (Figma "Tutorial flow"). Studs for the world, design pixels for the screen.
	guide = {
		-- The beam on the ground from the player to the target (TutorialGuide); texture from the owner, 2026-11-08.
		beam = {
			texture = "rbxassetid://52513855",
			width = 3, -- studs
			textureLength = 3, -- studs one arrow takes along the beam
			speed = 1.2, -- how fast the arrows scroll toward the target
			colour = Color3.fromRGB(255, 201, 60),
			glow = 0.6, -- LightEmission
		},
		rebuildDistance = 4, -- the trail is redrawn when the player has moved this far
		arrowHeight = 7, -- the floating arrow's height over its target
		arrowBob = 1.2,
		arrowWidth = 4.5,
		pointerBob = 10, -- design px the screen pointer bobs toward its button
		colours = {
			yolk = Color3.fromRGB(255, 201, 60),
			yolkDeep = Color3.fromRGB(255, 159, 28),
			lit = Color3.fromRGB(255, 236, 120), -- a footprint as the light passes
			dim = Color3.fromRGB(255, 170, 30), -- and the rest of the time
		},
	},
}

-- The index of a step by id, or nil.
function Tutorial.indexOf(id: string): number?
	for index, step in Tutorial.steps do
		if step.id == id then
			return index
		end
	end
	return nil
end

-- The step number a finished tutorial is saved with.
Tutorial.doneStep = #Tutorial.steps + 1

return Tutorial
