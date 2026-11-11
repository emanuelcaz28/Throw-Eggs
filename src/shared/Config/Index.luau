-- The Dino Index. Completing a world gives only a timed XP boost: no cash or luck, on the owner's word. The player
-- collects it by hand, with the world's 2x TRAINING XP button [Owner, 2026-11-11].
return {
	-- Completing a world doubles training XP for a while (not permanent). Time away counts down too.
	xpBoost = { multiplier = 2, seconds = 15 * 60 },
	-- The egg that cracks open when a world's reward is collected (an id from Config/Eggs).
	rewardEgg = "GoldenEgg",
	-- Each map's picture as the whole Index page's background. A map left out here uses its card picture below,
	-- stretched; a taller shot (design/index/maps) looks sharper.
	mapBackdrops = {} :: { [string]: string },
	-- Each map's picture in the Index's ALL MAPS grid: in-game shots from design/index/cards (628x553).
	mapPictures = {
		Forest = "rbxassetid://90987393656790",
		Desert = "rbxassetid://86172229566178",
		Swamp = "rbxassetid://102498954020329",
		Volcano = "rbxassetid://123935383199769",
		FrozenPeaks = "rbxassetid://136383997462611",
		ShadowBog = "rbxassetid://77905966012138",
		Abyss = "rbxassetid://102439005727892",
		StarfallCrater = "rbxassetid://139461709085556",
		EclipseTemple = "rbxassetid://131933281546467",
		ForbiddenLibrary = "rbxassetid://86636215560423",
		MidnightCarnival = "rbxassetid://130293422926761",
		ClockworkCitadel = "rbxassetid://81432942223424",
		ThornKingdom = "rbxassetid://91187719623807",
		SporeHollow = "rbxassetid://95519848959681",
		WeepingDark = "rbxassetid://78926905128766",
	},
}
