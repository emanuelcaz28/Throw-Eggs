-- What plays on the buyer's screen after a Robux purchase goes through (PurchaseMoments), from Figma "Shop" page
-- "Shop v2" (2026-11-12). Looks only: the server has already given the item when one of these starts.
--   Prism Egg: the egg lands, shakes, bursts, and the monster is revealed. A tap skips to the reveal.
--   Special monster (Gloomfin): lights out, eyes, a lunge and a bite, then it's yours.
--   Game Pass: a short "unlocked" card, closes by itself.
--   Everything else (cash, Throw Power, luck): a quick pop that flies to where the thing now is. Never blocks taps.
-- Times are seconds. Colours are hex.
local Reveal = require(script.Parent.Reveal)

local images = Reveal.showcase.backdrop.images -- white on see-through, tinted in the game

return {
	images = {
		sunburst = images.sunburst, -- light rays from the middle
		glow = images.glow, -- a soft round glow
		speedLines = images.speedLines,
	},

	prism = {
		land = 0.5, -- the egg drops in and lands
		shakes = { 0.6, 1.05, 1.5 }, -- when each shake starts; the light climbs one tier per shake, up to the real one
		shakeLength = 0.36,
		shakeTilt = { 7, 11, 16 }, -- degrees, harder each time
		burstAt = 2.0, -- the shell bursts...
		jackpotBurstAt = 3.0, -- ...later for the jackpot: the last shake trembles on in gold first
		burst = 0.25, -- flash, rings and shards
		buttonsAfter = 0.9, -- after the monster shows, the buttons come...
		jackpotHold = 0.5, -- ...this much later for the jackpot
		closeAfter = 20, -- left alone this long with the buttons up, it closes by itself
		veil = 0.93, -- how dark the game (and the Shop, when it's open) goes behind (1 is black)
		-- The Prism Egg's tiers, most common first, matching Config/Shop prismEgg.hatches: deep colour, light colour.
		tiers = { { "#2f8fe6", "#9ad9ff" }, { "#9150e8", "#dcb0ff" }, { "#e8265a", "#ff8aa6" } },
		lights = { "#2f8fe6", "#9150e8", "#ffd23f" }, -- the three small lights under the egg, and the light from its cracks
		confetti = 22,
		jackpotConfetti = 46,
	},

	special = {
		dark = 0.7, -- lights out, the eyes open
		bite = 0.5, -- the lunge and the bite
		nameAfter = 0.3, -- after the bite: its name slams in...
		ribbonAfter = 0.6, -- ...the gold ribbon stamps on...
		incomeAfter = 0.85, -- ...its share and $/s...
		buttonAfter = 1.3, -- ...and the button
		closeAfter = 6, -- with the button up, it closes by itself after this
		veil = 0.96,
		colour = "#ff2438",
		ring = { seconds = 1.1, size = 26 }, -- back in the game: a red ring spreads on the floor under it (studs across)
	},

	pass = {
		seconds = 2.2,
		minimum = 0.6, -- a tap closes it, but not before this
		veil = 0.86,
		confetti = 26,
		-- By Config/Shop key: the word under the x2, and the card's colours (light, deep).
		looks = {
			doubleCash = { label = "CASH", colours = { "#7fd4ff", "#2f6fe6" } },
			doubleTraining = { label = "TRAINING XP", colours = { "#d3a3ff", "#6b3dff" } },
			doublePower = { label = "THROW POWER", colours = { "#ffe066", "#ff7a1a" } },
		},
	},

	pop = {
		seconds = 1.1,
		burst = 0.35, -- it pops; then it flies to its counter
		colours = { cash = "#5aff6a", power = "#ffb21a", luck100 = "#b06bff", luck500 = "#ffd23f", serverLuck = "#5aff6a" },
		pieces = { cash = 9, power = 7, luck = 6 }, -- coins, sparks or clovers that fly to the counter
	},

	-- Sounds already in the game (Config/Reveal sounds, Config/UiSounds moments). An empty id is silent.
	sounds = {
		eggLand = { id = Reveal.sounds.eggDrop, volume = 0.7 },
		shake = { id = Reveal.sounds.meterTap, volume = 0.5, skip = Reveal.sounds.meterTapSkip },
		burst = { id = Reveal.sounds.slam.mid, volume = 0.6 },
		jackpot = { id = Reveal.sounds.bigReveal, volume = 0.5 },
		eyes = { id = Reveal.sounds.step, volume = 0.6, speed = 0.7 }, -- a low thud as the eyes open
		bite = { id = Reveal.sounds.slam.huge, volume = 0.7 },
		slam = { id = Reveal.sounds.slam.small, volume = 0.5 },
	},
}
