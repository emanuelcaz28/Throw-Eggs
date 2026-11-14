-- Makes (or remakes) Shattered Mirror's two metal materials in MaterialService, from the maps assets/textures/make_chrome.py
-- makes (uploaded 2026-11-13). Run once in Studio's Edit mode (command bar or StudioMCP execute_luau), then save the place.
-- studio_tidy.luau puts them on the parts whose roles a build script lists in CHROME; a part's colour tints them, so white
-- shows the whole rainbow and a dark grey makes dark chrome.
local MaterialService = game:GetService("MaterialService")

local VARIANTS = {
	HoloChrome = { -- silver with bands of rainbow flowing through it, almost mirror smooth
		ColorMap = "rbxassetid://85790528467674",
		RoughnessMap = "rbxassetid://119215694550530",
		StudsPerTile = 18,
	},
	PolishedGold = { -- near-white brushed streaks for the part's gold colour to tint, a little less smooth
		ColorMap = "rbxassetid://90225015793447",
		RoughnessMap = "rbxassetid://99019088517129",
		StudsPerTile = 10,
	},
}

local made = {}
for name, maps in VARIANTS do
	local variant = MaterialService:FindFirstChild(name) or Instance.new("MaterialVariant")
	variant.Name = name
	variant.BaseMaterial = Enum.Material.Foil
	variant.ColorMap = maps.ColorMap
	variant.MetalnessMap = "rbxassetid://117866289076427" -- all metal
	variant.RoughnessMap = maps.RoughnessMap
	variant.StudsPerTile = maps.StudsPerTile
	variant.MaterialPattern = Enum.MaterialPattern.Organic -- hides where the tile repeats
	variant.Parent = MaterialService
	table.insert(made, name)
end
table.sort(made)
return "made " .. table.concat(made, ", ")
