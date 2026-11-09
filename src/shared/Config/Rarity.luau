-- How each rarity word looks and moves (RarityLabel), from the Figma file "Throw Eggs - Rarity Labels"
-- https://www.figma.com/design/YhU5tNXWcOYihiYq8jrZhv, frame "Rarity Labels v1" [Owner, 2026-11-07: "design the rarities
-- and animate them to look even better"]. Each step up adds one more effect, so the rarest look the most alive.
-- Every rarity plays one loop of `loop` seconds. Colours are hex; `top`/`bottom` is the letters' gradient, `ink`
-- their outline, `glow` a soft halo behind them (none on the two commonest).
return {
	loop = 3,
	bob = 0.09, -- how far the bobbing ones rise, as a share of the text size
	strokeShare = 1 / 9, -- outline thickness against the text size
	-- The soft glow: outlines { thickness against the text size, how strong at full glow (0-1) }, innermost first.
	glowLayers = { { 0.14, 0.55 }, { 0.22, 0.3 }, { 0.3, 0.15 } },
	shineWidth = 0.12, -- the shine band's width, as a share of the word
	styles = {
		common = { top = "#ffffff", bottom = "#c3c9d4", ink = "#2a2540" },
		uncommon = { top = "#d9ffc4", bottom = "#52c43f", ink = "#123a12", bob = true },
		rare = { top = "#d6f1ff", bottom = "#2f8fe6", ink = "#0d2a52", glow = "#2f8fe6", glowRange = { 0.55, 0.55 }, bob = true, shine = { { 0.6, 1.4 } } },
		epic = { top = "#f1dcff", bottom = "#9150e8", ink = "#2a0f52", glow = "#b46cff", glowRange = { 0.25, 0.85 }, bob = true, shine = { { 0.9, 1.7 } } },
		legendary = { top = "#fff4c2", bottom = "#ff9a1f", ink = "#4a2400", glow = "#ffb627", glowRange = { 0.4, 1 }, pulse = 0.06, shine = { { 0.7, 1.4 } }, sparkles = { { 0.02, 0.18, 0.4, 0.2 }, { 0.96, 0.8, 0.3, 1.6 } } },
		mythic = { top = "#ffd6e6", bottom = "#e8265a", ink = "#4a0018", glow = "#ff3d7f", glowRange = { 0.6, 1 }, glowTwice = true, pulse = 0.07, pulseTwice = true, wobble = 2.5, shine = { { 0.3, 0.9 }, { 1.8, 2.4 } }, sparkles = { { 0, 0.2, 0.42, 0.1 }, { 0.98, 0.15, 0.3, 0.75 }, { 0.06, 0.86, 0.26, 1.4 }, { 0.94, 0.85, 0.4, 2.05 } }, sparkleSpeed = 0.8 },
		ancient = { top = "#ffe0c2", bottom = "#c2602a", ink = "#3a1400", glow = "#ff7a2e", flicker = true, shake = true, shine = { { 1.6, 2.4 } }, embers = { 0.12, 0.35, 0.6, 0.85, 0.48 } },
		-- Secret is dark [Owner, 2026-11-07]: near-black purple letters, a light violet outline and glow so it still reads.
		-- The "?" of a monster bought with Robux [Owner, 2026-11-09]: plain black, no glow, sparkles or movement, with a
		-- light outline so it reads on dark cards.
		mystery = { top = "#1a1a1a", bottom = "#000000", ink = "#ffffff" },
		secret = { top = "#4a3596", bottom = "#0d0720", ink = "#c9b8ff", glow = "#8a5cff", glowRange = { 0.4, 0.95 }, glitch = true, shine = { { 2.0, 2.7 } } },
	},
	-- Sparkles: { x, y (0-1 across and down the word), size (share of the text size), when it starts (seconds) }.
	-- A sparkle grows and shrinks over 1 second (times sparkleSpeed) while turning a quarter turn.
	-- Ancient's embers start at these places across the word and rise 1.25x the text size over 0.8 seconds.
}
