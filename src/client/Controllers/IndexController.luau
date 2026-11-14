-- The Dino Index panel, from Figma "Throw Eggs - Index & Inventory" (Index v4) [Owner, 2026-11-11: a total redesign].
-- One map fills the panel, its picture as the background. Left: one monster standing over the map, the real model playing its
-- idle, with its name, rarity and odds under it. Right: the map's 8 monsters as still cards (12 smaller ones on the
-- end-game maps, whose last four are extras the reward doesn't need: Config/Dinos apex); tapping one puts it on
-- the spotlight. Under them the reward button (+10% CASH FOREVER, with the timed 2x training XP), which goes green once the map is complete and is pressed to
-- collect the boost (an egg cracks open). Scrolling (mouse wheel, or a swipe up or down) moves to the next map; ALL
-- MAPS opens a grid of every world. A map too far to reach shows a lock and your Throw Power against what it needs.
-- A red dot on the HUD's Index button counts the rewards waiting. Display only: the server decides what's been found
-- and what's been collected.
local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TextService = game:GetService("TextService")
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)
local DinoModel = require(ReplicatedStorage.Shared.DinoModel)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)
local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local Index = require(ReplicatedStorage.Shared.Config.Index)
local PopText = require(ReplicatedStorage.Shared.PopText)
local UiKit = require(ReplicatedStorage.Shared.UiKit)
local Rarity = require(ReplicatedStorage.Shared.Config.Rarity)
local DinoLifeController = require(script.Parent.DinoLifeController)
local RevealController = require(script.Parent.RevealController)
local RarityLabel = require(script.Parent.RarityLabel)
local Sfx = require(script.Parent.Sfx)

local player = Players.LocalPlayer

local IndexController = {}
IndexController.discovered = {} -- every monster id this player has caught, as the server last said (PowerLimitController reads it)

-- Everything below is in the panel's design pixels (the panel is scaled to the screen as a whole).
local PANEL = Vector2.new(1060, 672)
local SPOT = { x = 22, y = 134, width = 430, height = 516 } -- the selected monster's side
local ART = { x = 17, y = 36, width = 396, height = 300 } -- the selected monster, in SPOT
local TILE = Vector2.new(133, 212) -- one monster's card
local TILE_GAP = Vector2.new(11, 12)
local TILES = Vector2.new(470, 104) -- the first card's corner
local TILE_COLUMNS = 4
local XP_BUTTON = { y = 556, height = 80 } -- as wide as the cards above it
-- What a completed world's button gives (Config/Index cashBonus); the timed XP boost comes with it.
local CASH_REWARD = `+{math.round(Index.cashBonus.perWorld * 100)}% CASH FOREVER`
local THUMB = Vector2.new(190, 164) -- a map in the ALL MAPS grid
local THUMB_PITCH = Vector2.new(202, 176)
local THUMB_COLUMNS = 5
local SLIDE = 0.3 -- seconds from one map to the next
local SWIPE = 60 -- screen pixels a finger must travel up or down to change map
local GREY = { "#6b6390", "#4a4370" } -- a 2x XP button that can't be pressed yet (or has been)
local GREY_TEXT = Color3.fromRGB(201, 192, 228)
local SHADE = Color3.fromRGB(18, 10, 36)

-- Text that shrinks to fit its box but never grows past its own size.
local function fitText(label: TextLabel, size: number)
	label.TextScaled = true
	local limit = Instance.new("UITextSizeConstraint")
	limit.MaxTextSize = size
	limit.Parent = label
end

local function frame(parent: Instance, name: string, x: number, y: number, width: number, height: number): Frame
	local f = Instance.new("Frame")
	f.Name = name
	f.Position = UDim2.fromOffset(x, y)
	f.Size = UDim2.fromOffset(width, height)
	f.BackgroundTransparency = 1
	f.BorderSizePixel = 0
	f.Parent = parent
	return f
end

local function tween(object: Instance, seconds: number, goal, style: Enum.EasingStyle?, direction: Enum.EasingDirection?)
	local t = TweenService:Create(object, TweenInfo.new(seconds, style or Enum.EasingStyle.Quad, direction or Enum.EasingDirection.Out), goal)
	t:Play()
	return t
end

-- A dark bar with a coloured fill and text over it.
local function progressBar(parent: Instance, x: number, y: number, width: number, height: number, textSize: number)
	local bar = frame(parent, "Progress", x, y, width, height)
	bar.BackgroundTransparency = 0
	bar.BackgroundColor3 = UiKit.DEEP
	bar.ClipsDescendants = true
	UiKit.corner(bar, height // 2)
	UiKit.stroke(bar, 4)
	local fill = Instance.new("Frame")
	fill.Name = "Fill"
	fill.BorderSizePixel = 0
	fill.Size = UDim2.fromScale(0, 1)
	fill.Parent = bar
	local colours = UiKit.gradient(fill, "green")
	UiKit.corner(fill, height // 2 - 4)
	local label = UiKit.text(bar, "", textSize)
	label.Size = UDim2.fromScale(1, 1)
	label.ZIndex = 2
	return function(share: number, text: string, style: string?)
		fill.Size = UDim2.fromScale(math.clamp(share, 0, 1), 1)
		fill.Visible = share > 0
		label.Text = text
		local pair = UiKit.GRADIENTS[style or "green"]
		colours.Color = ColorSequence.new(Color3.fromHex(pair[1]), Color3.fromHex(pair[2]))
	end
end

-- The red dot that says something is waiting: on the HUD button (with how many), ALL MAPS, a map and the XP button.
local function redDot(parent: Instance, size: number, x: UDim2, count: boolean?): (Frame, TextLabel?)
	local dot = Instance.new("Frame")
	dot.Name = "RedDot"
	dot.AnchorPoint = Vector2.new(0.5, 0.5)
	dot.Position = x
	dot.Size = UDim2.fromOffset(size, size)
	dot.ZIndex = 6
	dot.Parent = parent
	UiKit.gradient(dot, "red")
	UiKit.corner(dot, size)
	UiKit.stroke(dot, math.max(2, size // 9))
	local grow = Instance.new("UIScale")
	grow.Parent = dot
	UiKit.pulse(dot)
	local label
	if count then
		label = UiKit.text(dot, "", math.floor(size * 0.62))
		label.Size = UDim2.fromScale(1, 1)
	end
	return dot, label
end

-- A padlock drawn from frames (phones have no glyph for one), `size` wide.
local function lock(parent: Instance, x: number, y: number, size: number, color: Color3): Frame
	local holder = frame(parent, "Lock", x, y, size, size * 1.2)
	local shackle = frame(holder, "Shackle", size * 0.2, 0, size * 0.6, size * 0.8)
	UiKit.corner(shackle, size)
	UiKit.stroke(shackle, size * 0.12, color)
	local body = frame(holder, "Body", 0, size * 0.42, size, size * 0.78)
	body.BackgroundTransparency = 0
	body.BackgroundColor3 = color
	body.ZIndex = 2
	UiKit.corner(body, size * 0.17)
	UiKit.stroke(body, math.max(2, size * 0.045))
	local hole = frame(body, "Keyhole", 0, 0, size * 0.18, size * 0.18)
	hole.AnchorPoint = Vector2.new(0.5, 0.5)
	hole.Position = UDim2.fromScale(0.5, 0.5)
	hole.BackgroundTransparency = 0
	hole.BackgroundColor3 = UiKit.INK
	UiKit.corner(hole, size)
	return holder
end

-- A tick drawn from two bars, in a green disc.
local function tickMark(parent: Instance, x: number, y: number, size: number)
	local disc = frame(parent, "Tick", x, y, size, size)
	disc.BackgroundTransparency = 0
	UiKit.gradient(disc, "green")
	UiKit.corner(disc, size)
	UiKit.stroke(disc, 3)
	for _, bar in { { 0.35, 0.58, 0.14, 0.34, -45 }, { 0.58, 0.47, 0.14, 0.56, 45 } } do
		local b = frame(disc, "Bar", 0, 0, size * bar[3], size * bar[4])
		b.AnchorPoint = Vector2.new(0.5, 0.5)
		b.Position = UDim2.fromScale(bar[1], bar[2])
		b.Rotation = bar[5]
		b.BackgroundTransparency = 0
		b.BackgroundColor3 = Color3.new(1, 1, 1)
		UiKit.corner(b, 3)
	end
end

-- The worlds with monsters of their own, in order: The Deep End has none, so no page.
local maps = {}
for number, biome in Biomes do
	if Dinos[biome.id] then
		table.insert(maps, { biome = biome, number = number })
	end
end

-- A map's monsters from most common to rarest.
local function monstersOf(biome)
	local list = table.clone(Dinos[biome.id] or {})
	table.sort(list, function(a, b)
		return a.chance < b.chance
	end)
	return list
end

-- How many of a map's monsters are found, and how many it has; then the same for the ones its reward needs (all but
-- the end-game maps' extras, Config/Dinos apex; IndexService decides the same way).
local function countFound(biome, discovered): (number, number, number, number)
	local found, count, neededFound, needed = 0, 0, 0, 0
	for _, dino in Dinos[biome.id] or {} do
		count += 1
		needed += if dino.apex then 0 else 1
		if discovered[dino.id] then
			found += 1
			neededFound += if dino.apex then 0 else 1
		end
	end
	return found, count, neededFound, needed
end

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "IndexHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 3 -- above the other panels
	gui.Parent = player:WaitForChild("PlayerGui")

	-- Left column, above Shop. Its red dot counts the rewards waiting.
	local open = HudStyle.iconButton(gui, "📖", "Index", "book")
	open.AnchorPoint = Vector2.new(0, 0.5)
	open.Position = UDim2.new(0, 16, HudStyle.COLUMN_CENTER, -(HudStyle.BUTTON_SIZE + HudStyle.BUTTON_GAP) / 2 * HudStyle.scale())
	open.Name = "OpenIndex"
	local badgeSize = math.floor(34 * HudStyle.scale())
	local badge, badgeCount = redDot(open, badgeSize, UDim2.new(1, -badgeSize * 0.2, 0, badgeSize * 0.2), true)
	badge.Visible = false

	-- UiKit's panel gives the frame, its X (finger-sized on phones), the veil and the springy opening; its coloured
	-- header isn't used: the map's picture fills the whole panel.
	local panel = UiKit.panel(gui, { name = "IndexPanel", width = PANEL.X, height = PANEL.Y, title = "", openEffect = "rise" })
	panel.header.Visible = false
	panel.body.Visible = false
	panel.close.ZIndex = 7
	panel.frame.Active = true -- so a click or the wheel on the panel doesn't reach the game behind it

	-- Two pictures, so one map's can fade into the next's.
	local pictures = {}
	for index = 1, 2 do
		local picture = Instance.new("ImageLabel")
		picture.Name = "MapPicture" .. index
		picture.BackgroundColor3 = UiKit.PANEL
		picture.BackgroundTransparency = if index == 1 then 0 else 1
		picture.ImageTransparency = if index == 1 then 0 else 1
		picture.ScaleType = Enum.ScaleType.Crop
		picture.Size = UDim2.fromScale(1, 1)
		picture.Parent = panel.frame
		UiKit.corner(picture, 30)
		pictures[index] = picture
	end
	-- Darker at the top and the bottom, where the words are.
	local shade = frame(panel.frame, "Shade", 0, 0, 0, 0)
	shade.Size = UDim2.fromScale(1, 1)
	shade.BackgroundTransparency = 0
	shade.BackgroundColor3 = SHADE
	UiKit.corner(shade, 30)
	local fade = Instance.new("UIGradient")
	fade.Rotation = 90
	fade.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 0.28),
		NumberSequenceKeypoint.new(0.22, 0.7),
		NumberSequenceKeypoint.new(0.55, 0.72),
		NumberSequenceKeypoint.new(1, 0.14),
	})
	fade.Parent = shade
	-- A map you can't reach yet is darker all over.
	local lockDim = frame(panel.frame, "LockedDim", 0, 0, 0, 0)
	lockDim.Size = UDim2.fromScale(1, 1)
	lockDim.BackgroundColor3 = SHADE
	UiKit.corner(lockDim, 30)

	-- The pages slide up and down inside this.
	local clip = frame(panel.frame, "Pages", 0, 0, 0, 0)
	clip.Size = UDim2.fromScale(1, 1)
	clip.ClipsDescendants = true

	local edge = frame(panel.frame, "LightEdge", 4, 4, 0, 0)
	edge.Size = UDim2.new(1, -8, 1, -8)
	UiKit.corner(edge, 26)
	UiKit.stroke(edge, 3, Color3.new(1, 1, 1)).Transparency = 0.84

	-- These stay put while the pages move: how many of every map's monsters you've found, and ALL MAPS.
	local totalX = PANEL.X - panel.closeInset - 12 - 214
	local totalHolder = frame(panel.frame, "TotalFound", totalX, 19, 214, 50)
	totalHolder.ZIndex = 7 -- over the ALL MAPS grid too
	local total = progressBar(totalHolder, 0, 0, 214, 50, 22)

	local allMaps = Instance.new("TextButton")
	allMaps.Name = "AllMaps"
	allMaps.AutoButtonColor = false
	allMaps.Text = ""
	allMaps.Position = UDim2.fromOffset(totalX - 12 - 150, 19)
	allMaps.Size = UDim2.fromOffset(150, 50)
	allMaps.BackgroundColor3 = UiKit.INK
	allMaps.BackgroundTransparency = 0.22
	allMaps.ZIndex = 7
	allMaps.Parent = panel.frame
	UiKit.corner(allMaps, 18)
	UiKit.stroke(allMaps, 3, Color3.new(1, 1, 1)).Transparency = 0.65
	for square = 0, 3 do
		local s = frame(allMaps, "Square", 18 + (square % 2) * 10, 16 + (square // 2) * 10, 8, 8)
		s.BackgroundTransparency = 0
		s.BackgroundColor3 = Color3.new(1, 1, 1)
		UiKit.corner(s, 2)
	end
	local allLabel = UiKit.text(allMaps, "ALL MAPS", 16, nil, Enum.TextXAlignment.Left)
	allLabel.Position = UDim2.fromOffset(46, 0)
	allLabel.Size = UDim2.new(1, -52, 1, 0)
	local allDot = redDot(allMaps, 22, UDim2.new(1, -4, 0, 4))
	allDot.Visible = false

	-- Where you are among the maps.
	local scrollBar = frame(panel.frame, "ScrollBar", PANEL.X - 18, 100, 8, 540)
	scrollBar.BackgroundTransparency = 0.4
	scrollBar.BackgroundColor3 = UiKit.DEEP
	scrollBar.ZIndex = 4
	UiKit.corner(scrollBar, 4)
	local thumb = frame(scrollBar, "Thumb", 0, 0, 8, 64)
	thumb.BackgroundTransparency = 0.25
	thumb.BackgroundColor3 = Color3.new(1, 1, 1)
	UiKit.corner(thumb, 4)

	-- ALL MAPS: every world at a glance, over the page.
	local overlay = frame(panel.frame, "AllMapsGrid", 0, 0, 0, 0)
	overlay.Size = UDim2.fromScale(1, 1)
	overlay.BackgroundTransparency = 0.07
	overlay.BackgroundColor3 = Color3.fromRGB(20, 14, 40)
	overlay.Active = true
	overlay.Visible = false
	overlay.ZIndex = 5
	UiKit.corner(overlay, 30)
	local title = UiKit.text(overlay, "ALL MAPS", 42, nil, Enum.TextXAlignment.Left)
	title.Position = UDim2.fromOffset(32, 18)
	title.Size = UDim2.fromOffset(240, 54)
	local hint = UiKit.muted(overlay, "Tap a map to go there", 18, Enum.TextXAlignment.Left)
	hint.Position = UDim2.fromOffset(262, 36)
	hint.Size = UDim2.fromOffset(300, 26)
	local grid = frame(overlay, "Grid", 0, 0, 0, 0)
	grid.Size = UDim2.fromScale(1, 1)

	return {
		gui = gui,
		open = open,
		badge = badge,
		badgeCount = badgeCount,
		panel = panel,
		pictures = pictures,
		lockDim = lockDim,
		clip = clip,
		total = total,
		allMaps = allMaps,
		allDot = allDot,
		nameWidth = totalX - 12 - 150 - 28 - 14, -- room for a map's name before ALL MAPS
		thumb = thumb,
		overlay = overlay,
		grid = grid,
	}
end

-- The reward's moment, over the whole screen: an egg shakes, cracks, and the boost bursts out.
local function buildReward()
	local gui = Instance.new("ScreenGui")
	gui.Name = "IndexRewardHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.ScreenInsets = Enum.ScreenInsets.None -- the dimming reaches the screen's edges on phones
	gui.DisplayOrder = 6
	gui.Enabled = false
	gui.Parent = player:WaitForChild("PlayerGui")
	local dim = frame(gui, "Dim", 0, 0, 0, 0)
	dim.Size = UDim2.fromScale(1, 1)
	dim.BackgroundColor3 = Color3.fromRGB(12, 8, 24)
	dim.Active = true
	local centre = frame(gui, "Centre", 0, 0, 0, 0)
	centre.Position = UDim2.fromScale(0.5, 0.5)
	local scale = Instance.new("UIScale")
	scale.Scale = UiKit.scale()
	scale.Parent = centre
	local rays = frame(centre, "Rays", 0, 0, 0, 0)
	-- A starburst from turned squares (there are no triangles to draw rays with): a big faint one, a brighter small one.
	local beams = {}
	for index = 0, 7 do
		local small = index >= 4
		local side = if small then 250 else 430
		local beam = frame(rays, "Beam", 0, 0, side, side)
		beam.AnchorPoint = Vector2.new(0.5, 0.5)
		beam.Rotation = index * 22.5 + (if small then 11 else 0)
		beam.BackgroundColor3 = if small then Color3.fromRGB(255, 243, 160) else Color3.fromRGB(255, 216, 74)
		table.insert(beams, beam)
	end
	local flash = frame(centre, "Flash", 0, 0, 10, 10)
	flash.AnchorPoint = Vector2.new(0.5, 0.5)
	flash.BackgroundColor3 = Color3.new(1, 1, 1)
	UiKit.corner(flash, 400)
	-- Seen from further back than usual, so the lifted top half stays in view.
	local egg = UiKit.viewport(centre, "egg_" .. Index.rewardEgg, { size = UDim2.fromOffset(380, 420), zoom = 1.6 })
	egg.Name = "Egg"
	egg.AnchorPoint = Vector2.new(0.5, 0.5)
	egg.Position = UDim2.fromOffset(0, 50)
	-- The egg's top half (the parts named ...Lid, EggModel) lifts off when it cracks.
	local lids = {}
	for _, part in egg:GetDescendants() do
		if part:IsA("BasePart") and string.sub(part.Name, -3) == "Lid" then
			table.insert(lids, { part = part, home = part.CFrame })
		end
	end
	local words = frame(centre, "Words", 0, -218, 0, 0)
	local wordsScale = Instance.new("UIScale")
	wordsScale.Parent = words
	local reward = UiKit.text(words, CASH_REWARD, 76, Color3.fromRGB(226, 190, 255))
	reward.AnchorPoint = Vector2.new(0.5, 0.5)
	reward.Size = UDim2.fromOffset(900, 96)
	local detail = UiKit.text(words, `and {Index.xpBoost.multiplier}x training XP for {math.round(Index.xpBoost.seconds / 60)} minutes  ·  the timer has started`, 22)
	detail.AnchorPoint = Vector2.new(0.5, 0.5)
	detail.Position = UDim2.fromOffset(0, 62)
	detail.Size = UDim2.fromOffset(900, 30)
	local done = UiKit.button(centre, "AWESOME!", "green", 250, 60, 30)
	done.AnchorPoint = Vector2.new(0.5, 0.5)
	done.Position = UDim2.fromOffset(0, 262)
	local sparks = {}
	for index = 1, 12 do
		local spark = frame(centre, "Spark", 0, 0, 18, 18)
		spark.AnchorPoint = Vector2.new(0.5, 0.5)
		spark.Rotation = 45
		spark.BackgroundColor3 = if index % 2 == 0 then Color3.fromRGB(255, 224, 102) else Color3.fromRGB(197, 139, 255)
		UiKit.corner(spark, 4)
		table.insert(sparks, spark)
	end
	return { gui = gui, dim = dim, rays = rays, beams = beams, flash = flash, egg = egg, lids = lids, words = words, wordsScale = wordsScale, done = done, sparks = sparks }
end

function IndexController.start()
	local remotes = ReplicatedStorage:WaitForChild("IndexRemotes")
	local changed = remotes:WaitForChild("IndexChanged")
	local claimRemote = remotes:WaitForChild("Claim")
	local hud = buildGui()
	local rewardHud = buildReward()
	local discovered = {}
	local claimed = {} -- biome ids whose 2x XP has been collected
	local completed = {} -- biome ids with every monster caught
	local heardFromServer = false -- the first list is what they already had, so it shouts nothing
	local current = 1 -- which of `maps` is on screen
	local farthestSeen: number? = nil -- the farthest map last time it opened, to jump to a new one but not move you otherwise
	local selected = {} -- the monster in the spotlight, by biome id
	local page: { frame: Frame, biomeId: string }? = nil
	local sliding = false
	local picture = 1 -- which of the two pictures is showing
	local rewardToken = 0

	local function shown(): boolean
		return hud.panel.frame.Visible
	end

	local function power(): number
		return player:GetAttribute("ThrowPower") or 0
	end

	local function isComplete(biome): boolean
		local _, _, neededFound, needed = countFound(biome, discovered)
		return needed > 0 and neededFound == needed
	end

	local function isWaiting(biome): boolean
		return isComplete(biome) and not claimed[biome.id]
	end

	local function waitingCount(): (number, number?)
		local count, first = 0, nil
		for index, map in maps do
			if isWaiting(map.biome) then
				count += 1
				first = first or index
			end
		end
		return count, first
	end

	-- The farthest map you've found anything in, so you see what you're hunting.
	local function farthestMap(): number
		local pick = 1
		for index, map in maps do
			if countFound(map.biome, discovered) > 0 then
				pick = index
			end
		end
		return pick
	end

	local function refreshBadges()
		local waiting = waitingCount()
		hud.badge.Visible = waiting > 0
		hud.badgeCount.Text = tostring(waiting)
		hud.allDot.Visible = waiting > 0
		local seen, all = 0, 0
		for _, map in maps do
			local found, count = countFound(map.biome, discovered)
			seen += found
			all += count
		end
		hud.total(if all > 0 then seen / all else 0, `{seen} / {all} found`)
	end

	-- The egg cracks open and the boost bursts out. The server starts the timer when it hears the claim.
	local function playReward()
		rewardToken += 1
		local token = rewardToken
		local r = rewardHud
		r.gui.Enabled = true
		r.dim.BackgroundTransparency = 1
		tween(r.dim, 0.2, { BackgroundTransparency = 0.12 })
		for _, beam in r.beams do
			beam.BackgroundTransparency = 1
		end
		for _, spark in r.sparks do
			spark.Visible = false
		end
		r.flash.BackgroundTransparency = 1
		r.words.Visible = false
		r.done.Visible = false
		r.egg.Position = UDim2.fromOffset(0, 50)
		for _, lid in r.lids do
			lid.part.CFrame = lid.home
		end
		task.spawn(function()
			-- Three shakes, each a little harder and higher. (Side to side: a turned ViewportFrame draws nothing.)
			for shake = 1, 3 do
				Sfx.play("squat", 0.9 + shake * 0.12)
				for _, across in { 8 + shake * 5, -(8 + shake * 5), 0 } do
					tween(r.egg, 0.07, { Position = UDim2.fromOffset(across, 50) }, Enum.EasingStyle.Sine).Completed:Wait()
				end
				task.wait(0.12)
			end
			if token ~= rewardToken then
				return
			end
			Sfx.play("powerUp")
			r.flash.Size = UDim2.fromOffset(40, 40)
			r.flash.BackgroundTransparency = 0.1
			tween(r.flash, 0.45, { Size = UDim2.fromOffset(900, 900), BackgroundTransparency = 1 })
			-- The top half pops up and tips over; the cracked egg stays under the words.
			local lift = Instance.new("NumberValue")
			lift.Changed:Connect(function(amount)
				for _, lid in r.lids do
					lid.part.CFrame = CFrame.new(0.55 * amount, 1.25 * amount, 0) * CFrame.Angles(0, 0, -math.rad(32) * amount) * lid.home
				end
			end)
			local lifting = tween(lift, 0.4, { Value = 1 }, Enum.EasingStyle.Back)
			lifting.Completed:Once(function()
				lift:Destroy()
			end)
			for _, beam in r.beams do
				tween(beam, 0.3, { BackgroundTransparency = 0.86 })
			end
			for index, spark in r.sparks do
				local angle = index / #r.sparks * 2 * math.pi
				spark.Visible = true
				spark.Position = UDim2.fromOffset(0, 30)
				spark.BackgroundTransparency = 0
				tween(spark, 0.7, { Position = UDim2.fromOffset(math.cos(angle) * 360, 30 + math.sin(angle) * 250), BackgroundTransparency = 1 })
				spark.Rotation = 45 + index * 30
			end
			r.words.Visible = true
			r.wordsScale.Scale = 0.3
			tween(r.wordsScale, 0.35, { Scale = 1 }, Enum.EasingStyle.Back)
			task.wait(0.5)
			if token ~= rewardToken then
				return
			end
			r.done.Visible = true
			task.wait(6)
			if token == rewardToken then
				r.gui.Enabled = false -- nobody pressed AWESOME: it leaves by itself
			end
		end)
	end
	rewardHud.done.Activated:Connect(function()
		rewardToken += 1
		rewardHud.gui.Enabled = false
	end)
	RunService.Heartbeat:Connect(function(dt)
		if rewardHud.gui.Enabled then
			rewardHud.rays.Rotation += dt * 25
		end
	end)

	-- Builds one map's page. deal: the cards pop in one after another (opening the Index).
	local function buildPage(index: number, deal: boolean)
		local map = maps[index]
		local biome = map.biome
		local monsters = monstersOf(biome)
		local _, _, _, needed = countFound(biome, discovered)
		local locked = power() < biome.startDist
		local root = frame(hud.clip, biome.id, 0, 0, PANEL.X, PANEL.Y)
		-- More than two rows of cards (the end-game maps' 12): shorter cards, so they fill the same space.
		local tileRows = math.max(2, math.ceil(#monsters / TILE_COLUMNS))
		local compact = tileRows > 2
		local tileHeight = math.floor((2 * TILE.Y + TILE_GAP.Y - (tileRows - 1) * TILE_GAP.Y) / tileRows)
		local artTop = if compact then 32 else 66 -- where a card's model starts, under its rarity pill
		local artHeight = if compact then tileHeight - artTop - 28 else 98
		local this = { frame = root, biomeId = biome.id }

		local name = UiKit.text(root, biome.name, 42, nil, Enum.TextXAlignment.Left)
		name.Position = UDim2.fromOffset(28, 12)
		name.Size = UDim2.fromOffset(hud.nameWidth, 54)
		fitText(name, 42)

		-- How much Throw Power reaches this map: a PERFECT throw flies exactly as far as your power, so it's where the
		-- map starts.
		if not locked then
			local pill = Instance.new("Frame")
			pill.Name = "PowerNeeded"
			pill.AutomaticSize = Enum.AutomaticSize.X
			pill.Position = UDim2.fromOffset(28, 70)
			pill.Size = UDim2.fromOffset(0, 36)
			pill.Parent = root
			UiKit.gradient(pill, "green")
			UiKit.corner(pill, 12)
			UiKit.stroke(pill, 3)
			local pad = Instance.new("UIPadding")
			pad.PaddingLeft = UDim.new(0, 12)
			pad.PaddingRight = UDim.new(0, 14)
			pad.Parent = pill
			local row = Instance.new("UIListLayout")
			row.FillDirection = Enum.FillDirection.Horizontal
			row.VerticalAlignment = Enum.VerticalAlignment.Center
			row.Padding = UDim.new(0, 6)
			row.Parent = pill
			row.SortOrder = Enum.SortOrder.LayoutOrder
			local bolt = UiKit.iconImage(pill, "bolt", { size = UDim2.fromOffset(22, 22) })
			if bolt then
				bolt.LayoutOrder = 1
			end
			local words = UiKit.text(pill, if biome.startDist > 0 then `{Format.commas(biome.startDist)} POWER NEEDED` else "NO POWER NEEDED", 17)
			words.AutomaticSize = Enum.AutomaticSize.X
			words.Size = UDim2.fromScale(0, 1)
			words.LayoutOrder = 2
		end

		local spot = frame(root, "Spotlight", SPOT.x, SPOT.y, SPOT.width, SPOT.height)
		local ring = frame(root, "SelectedRing", 0, 0, TILE.X + 12, TILE.Y + 12)
		ring.Visible = false
		UiKit.corner(ring, 26)
		UiKit.stroke(ring, 5, Color3.new(1, 1, 1))
		local tiles = {}

		-- Puts a monster in the spotlight: the real model playing its idle if you've caught it, a still black shape if not.
		local shownMonster = frame(spot, "Monster", 0, 0, SPOT.width, SPOT.height)
		local function showMonster(dino, hop: boolean)
			shownMonster:ClearAllChildren()
			local seen = discovered[dino.id] == true
			local rarity = UiKit.rarityOf(dino.id)
			-- Nothing behind or under it, just the monster over the map [Owner, 2026-11-11: pedestal and round glow removed].

			local view, model = UiKit.monster(shownMonster, dino.id, {
				live = seen,
				silhouette = not seen,
				position = UDim2.fromOffset(ART.x, ART.y),
				size = UDim2.fromOffset(ART.width, ART.height),
				aspect = ART.width / ART.height,
			})
			view.ZIndex = 2
			if seen then
				-- Only this one moves [Owner, 2026-11-11: idle animation only on the selected monster].
				DinoLifeController.showcase(model, function()
					return shown() and view.Parent ~= nil
				end)
			end
			if hop then
				view.Position = UDim2.fromOffset(ART.x, ART.y - 46)
				tween(view, 0.4, { Position = UDim2.fromOffset(ART.x, ART.y) }, Enum.EasingStyle.Bounce)
			end

			local title = UiKit.text(shownMonster, if seen then dino.name else "???", 54)
			title.Position = UDim2.fromOffset(0, ART.y + ART.height + 38)
			title.Size = UDim2.fromOffset(SPOT.width, 66)
			fitText(title, 54)
			local row = frame(shownMonster, "Rarity", 0, ART.y + ART.height + 106, SPOT.width, 44)
			local layout = Instance.new("UIListLayout")
			layout.FillDirection = Enum.FillDirection.Horizontal
			layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
			layout.VerticalAlignment = Enum.VerticalAlignment.Center
			layout.Padding = UDim.new(0, 12)
			layout.SortOrder = Enum.SortOrder.LayoutOrder
			layout.Parent = row
			local wordWidth = TextService:GetTextSize(string.upper(rarity), 30, Enum.Font.FredokaOne, Vector2.new(1000, 100)).X + 10
			local wordHolder = frame(row, "Word", 0, 0, wordWidth, 40)
			wordHolder.LayoutOrder = 1
			RarityLabel.create(wordHolder, rarity, 30)
			local dot = frame(row, "Dot", 0, 0, 8, 8)
			dot.BackgroundTransparency = 0.3
			dot.BackgroundColor3 = Color3.new(1, 1, 1)
			dot.LayoutOrder = 2
			UiKit.corner(dot, 8)
			local odds = UiKit.text(row, `1 in {Format.commas(DinoStats.monsterOneIn(dino.id))}`, 30, UiKit.GOLD)
			odds.AutomaticSize = Enum.AutomaticSize.X
			odds.Size = UDim2.fromOffset(0, 40)
			odds.LayoutOrder = 3
			if hop then
				local grow = Instance.new("UIScale")
				grow.Scale = 0.7
				grow.Parent = title
				tween(grow, 0.25, { Scale = 1 }, Enum.EasingStyle.Back)
			end
		end

		local function select(dino, hop: boolean)
			selected[biome.id] = dino.id
			local tile = tiles[dino.id]
			ring.Visible = true
			local goal = tile.Position - UDim2.fromOffset(6, 6)
			if hop then
				tween(ring, 0.15, { Position = goal })
			else
				ring.Position = goal
			end
			showMonster(dino, hop)
		end

		if locked then
			-- Too far to reach: a lock, and your Throw Power against what the map needs.
			local padlock = lock(spot, SPOT.width / 2 - 55, 104, 110, Color3.new(1, 1, 1))
			local card = frame(spot, "Locked", 3, 264, 424, 124)
			card.BackgroundTransparency = 0.2
			card.BackgroundColor3 = UiKit.INK
			UiKit.corner(card, 22)
			UiKit.stroke(card, 4)
			local words = UiKit.text(card, "TOO FAR TO REACH", 34)
			words.Position = UDim2.fromOffset(0, 12)
			words.Size = UDim2.new(1, 0, 0, 46)
			local bar = progressBar(card, 22, 66, 380, 42, 22)
			bar(power() / biome.startDist, `{Format.commas(math.floor(power()))} / {Format.commas(biome.startDist)}`, "gold")
			local press = Instance.new("TextButton")
			press.Name = "Press"
			press.BackgroundTransparency = 1
			press.Text = ""
			press.Size = UDim2.fromScale(1, 1)
			press.ZIndex = 3
			press.Parent = padlock
			press.Activated:Connect(function()
				for _, angle in { -10, 10, -6, 6, 0 } do
					tween(padlock, 0.05, { Rotation = angle }, Enum.EasingStyle.Sine).Completed:Wait()
				end
			end)
		end

		-- The map's monsters as cards, most common first. Their models are still [Owner, 2026-11-07: moving ones lagged].
		for order, dino in monsters do
			local seen = discovered[dino.id] == true
			local rarity = UiKit.rarityOf(dino.id)
			local tile = Instance.new("TextButton")
			tile.Name = dino.id
			tile.AutoButtonColor = false
			tile.Text = ""
			tile.Position = UDim2.fromOffset(
				TILES.X + ((order - 1) % TILE_COLUMNS) * (TILE.X + TILE_GAP.X),
				TILES.Y + ((order - 1) // TILE_COLUMNS) * (tileHeight + TILE_GAP.Y)
			)
			tile.Size = UDim2.fromOffset(TILE.X, tileHeight)
			tile.Parent = root
			-- Found cards are painted in the rarity word's own colour (Config/Rarity), so card and tag match
			-- [Owner, 2026-11-08]; the others are dark.
			if seen then
				local base = Color3.fromHex((Rarity.styles[rarity] or Rarity.styles.common).bottom)
				UiKit.gradient(tile, { base:Lerp(Color3.new(1, 1, 1), 0.35):ToHex(), base:Lerp(Color3.new(0, 0, 0), 0.08):ToHex() })
			else
				UiKit.gradient(tile, { "#4a4466", "#2a2542" })
			end
			UiKit.corner(tile, 20)
			UiKit.stroke(tile, 4)
			local glow = frame(tile, "Glow", (TILE.X - 112) / 2, artTop + 10, 112, artHeight - 14)
			glow.BackgroundColor3 = Color3.new(1, 1, 1)
			glow.BackgroundTransparency = if seen then 0.7 else 0.92
			UiKit.corner(glow, 60)
			-- One fixed width for every pill: sized to its word, LEGENDARY ran to the card's edge.
			local pill = frame(tile, "RarityPill", 9, if compact then 6 else 9, 100, if compact then 22 else 24)
			pill.BackgroundColor3 = UiKit.INK
			pill.BackgroundTransparency = 0.35
			pill.ZIndex = 3
			UiKit.corner(pill, 9)
			local word = RarityLabel.create(pill, rarity, 12, nil, nil, true)
			word.AnchorPoint = Vector2.new(0.5, 0.5)
			word.Position = UDim2.fromScale(0.5, 0.5)
			word.Size = UDim2.fromScale(1, 1)
			local label = UiKit.text(tile, if seen then dino.name else "???", 16)
			label.Position = UDim2.fromOffset(4, tileHeight - (if compact then 28 else 36))
			label.Size = UDim2.fromOffset(TILE.X - 8, 24)
			label.ZIndex = 3
			fitText(label, 16)
			local press = Instance.new("UIScale")
			press.Parent = tile
			tile.MouseButton1Down:Connect(function()
				press.Scale = 0.94
			end)
			tile.MouseButton1Up:Connect(function()
				press.Scale = 1
			end)
			tile.MouseLeave:Connect(function()
				press.Scale = 1
			end)
			if deal then
				press.Scale = 0
				task.delay((order - 1) * 0.035, function()
					tween(press, 0.22, { Scale = 1 }, Enum.EasingStyle.Back)
				end)
			end
			tiles[dino.id] = tile
			if not locked then
				tile.Activated:Connect(function()
					if selected[biome.id] ~= dino.id then
						select(dino, true)
					end
				end)
			end
		end

		-- The reward: grey until every monster is found, then green and waiting to be pressed; grey with a tick after.
		local width = TILE_COLUMNS * TILE.X + (TILE_COLUMNS - 1) * TILE_GAP.X
		local ready = isWaiting(biome)
		local xp = UiKit.button(root, CASH_REWARD, if ready then "green" else GREY, width, XP_BUTTON.height, 36)
		xp.Name = "XpButton"
		xp.Position = UDim2.fromOffset(TILES.X, XP_BUTTON.y)
		if ready then
			UiKit.pulse(xp)
			redDot(xp, 30, UDim2.new(1, -3, 0, 3))
		else
			xp.TextColor3 = GREY_TEXT
			if claimed[biome.id] then
				tickMark(xp, width - 62, (XP_BUTTON.height - 38) / 2, 38)
			end
		end
		xp.Activated:Connect(function()
			if isWaiting(biome) then
				claimed[biome.id] = true -- shown at once; the server says the same a moment later
				claimRemote:FireServer(biome.id)
				playReward()
			elseif not claimed[biome.id] then
				for _, angle in { -2, 2, -1, 1, 0 } do
					tween(xp, 0.05, { Rotation = angle }, Enum.EasingStyle.Sine).Completed:Wait()
				end
				PopText.notice(`Find {biome.name}'s first {needed} monsters first`, false)
			end
		end)

		-- The cards' models come on demand (DinoLibrary): ask for the whole map in one go, then stand them in, the
		-- spotlight first.
		task.spawn(function()
			local ids = {}
			for _, dino in monsters do
				table.insert(ids, dino.id)
			end
			DinoModel.need(ids)
			if not root.Parent then
				return -- scrolled away while waiting
			end
			if not locked then
				-- In the spotlight: the one picked last time, else the rarest you've caught, else the most common.
				local pick = monsters[1]
				for _, dino in monsters do
					if discovered[dino.id] then
						pick = dino
					end
				end
				for _, dino in monsters do
					if dino.id == selected[biome.id] then
						pick = dino
					end
				end
				select(pick, deal)
			end
			-- Then the cards' still models, one a frame: all eight at once dropped a frame on every scroll (2026-11-11).
			for _, dino in monsters do
				task.wait()
				if not root.Parent then
					return
				end
				local view = UiKit.monster(tiles[dino.id], dino.id, {
					spin = false,
					silhouette = discovered[dino.id] ~= true,
					position = UDim2.fromOffset(2, artTop),
					size = UDim2.fromOffset(TILE.X - 4, artHeight),
					aspect = (TILE.X - 4) / artHeight,
				})
				view.ZIndex = 2
			end
		end)
		return this
	end

	local function setScene(index: number, instant: boolean)
		local biome = maps[index].biome
		local image = Index.mapBackdrops[biome.id] or Index.mapPictures[biome.id] or ""
		local locked = power() < biome.startDist
		local seconds = if instant then 0 else SLIDE
		local old, new = hud.pictures[picture], hud.pictures[3 - picture]
		if instant then
			old.Image = image
			old.ImageColor3 = if locked then Color3.fromRGB(120, 120, 140) else Color3.new(1, 1, 1)
			old.ImageTransparency = 0
			old.ZIndex = 1
			new.ImageTransparency = 1
			new.ZIndex = 0
		else
			-- The new picture fades in over the old one.
			new.Image = image
			new.ImageColor3 = if locked then Color3.fromRGB(120, 120, 140) else Color3.new(1, 1, 1)
			new.ZIndex = 1
			old.ZIndex = 0
			new.ImageTransparency = 1
			tween(new, seconds, { ImageTransparency = 0 })
			picture = 3 - picture
		end
		tween(hud.lockDim, seconds, { BackgroundTransparency = if locked then 0.45 else 1 })
		tween(hud.thumb, seconds, { Position = UDim2.fromOffset(0, (index - 1) / math.max(1, #maps - 1) * (540 - 64)) })
	end

	-- Shows a map with no slide: opening the Index, or the server changing what's on it.
	local function show(index: number, deal: boolean)
		current = index
		if page then
			page.frame:Destroy()
		end
		setScene(index, true)
		page = buildPage(index, deal)
	end

	-- Slides to another map: the old page leaves one way as the new one comes in from the other.
	local function go(index: number)
		if sliding or not shown() then
			return
		end
		index = math.clamp(index, 1, #maps)
		if index == current then
			-- The first or last map: a little nudge says there's nothing further.
			if page then
				sliding = true
				local bump = tween(page.frame, 0.08, { Position = UDim2.fromOffset(0, -14) })
				bump.Completed:Wait()
				tween(page.frame, 0.12, { Position = UDim2.new() }).Completed:Wait()
				sliding = false
			end
			return
		end
		sliding = true
		local direction = if index > current then 1 else -1
		local old = page
		current = index
		setScene(index, false)
		local new = buildPage(index, false)
		page = new
		new.frame.Position = UDim2.fromOffset(0, direction * PANEL.Y)
		tween(new.frame, SLIDE, { Position = UDim2.new() })
		if old then
			tween(old.frame, SLIDE, { Position = UDim2.fromOffset(0, -direction * PANEL.Y) })
		end
		task.delay(SLIDE, function()
			if old then
				old.frame:Destroy()
			end
			sliding = false
		end)
	end

	-- ALL MAPS: every world with its picture, how far along it is, its lock or its waiting reward.
	local function buildGrid()
		hud.grid:ClearAllChildren()
		for index, map in maps do
			local biome = map.biome
			local found, count = countFound(biome, discovered)
			local locked = power() < biome.startDist
			local waiting = isWaiting(biome)
			local x = 31 + ((index - 1) % THUMB_COLUMNS) * THUMB_PITCH.X
			local y = 100 + ((index - 1) // THUMB_COLUMNS) * THUMB_PITCH.Y
			if index == current then
				local here = frame(hud.grid, "Here", x - 6, y - 6, THUMB.X + 12, THUMB.Y + 12)
				UiKit.corner(here, 24)
				UiKit.stroke(here, 5, Color3.new(1, 1, 1))
			end
			local thumb = Instance.new("ImageButton")
			thumb.Name = biome.id
			thumb.AutoButtonColor = false
			thumb.Image = Index.mapPictures[biome.id] or ""
			thumb.ImageColor3 = if locked then Color3.fromRGB(110, 110, 128) else Color3.new(1, 1, 1)
			thumb.ScaleType = Enum.ScaleType.Crop
			thumb.BackgroundColor3 = UiKit.DEEP
			thumb.Position = UDim2.fromOffset(x, y)
			thumb.Size = UDim2.fromOffset(THUMB.X, THUMB.Y)
			thumb.Parent = hud.grid
			UiKit.corner(thumb, 18)
			UiKit.stroke(thumb, if waiting then 5 else 4, if waiting then UiKit.GOLD else nil)
			local dark = frame(thumb, "Shade", 0, 0, 0, 0)
			dark.Size = UDim2.fromScale(1, 1)
			dark.BackgroundTransparency = 0
			dark.BackgroundColor3 = SHADE
			UiKit.corner(dark, 18)
			local fade = Instance.new("UIGradient")
			fade.Rotation = 90
			fade.Transparency = if locked
				then NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.6), NumberSequenceKeypoint.new(0.55, 0.5), NumberSequenceKeypoint.new(1, 0.1) })
				else NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.65), NumberSequenceKeypoint.new(0.4, 0.9), NumberSequenceKeypoint.new(0.7, 0.25), NumberSequenceKeypoint.new(1, 0.08) })
			fade.Parent = dark
			local chip = frame(thumb, "Number", 10, 10, 36, 26)
			chip.BackgroundTransparency = 0.2
			chip.BackgroundColor3 = UiKit.INK
			UiKit.corner(chip, 9)
			local number = UiKit.text(chip, tostring(map.number), 16)
			number.Size = UDim2.fromScale(1, 1)
			local name = UiKit.text(thumb, biome.name, 17, if locked then UiKit.MUTED else nil, Enum.TextXAlignment.Left)
			name.Position = UDim2.fromOffset(12, 98)
			name.Size = UDim2.fromOffset(THUMB.X - 24, 24)
			fitText(name, 17)
			if locked then
				lock(thumb, THUMB.X / 2 - 19, 40, 38, Color3.new(1, 1, 1))
				local need = UiKit.text(thumb, `Needs {Format.commas(biome.startDist)} Power`, 14, Color3.fromRGB(255, 179, 171), Enum.TextXAlignment.Left)
				need.Position = UDim2.fromOffset(12, 128)
				need.Size = UDim2.fromOffset(THUMB.X - 24, 20)
			else
				local done = count > 0 and found == count
				local bar = progressBar(thumb, 12, 126, THUMB.X - 24, 26, 14)
				bar(if count > 0 then found / count else 0, if done then "COMPLETE!" else `{found} / {count}`, if done then "gold" else "green")
			end
			if waiting then
				redDot(thumb, 24, UDim2.new(1, -4, 0, 4))
			end
			thumb.Activated:Connect(function()
				hud.overlay.Visible = false
				if index ~= current then
					go(index)
				end
			end)
		end
	end

	-- Catching a biome's last monster says its reward is waiting, once the reveal of that monster is over.
	local function shoutCompleted(biome)
		task.spawn(function()
			while RevealController.isPlaying() do
				task.wait(0.25)
			end
			task.wait(1)
			PopText.shout(`{string.upper(biome.name)} COMPLETE!`, "Reward waiting in the Index")
		end)
	end

	hud.open.Activated:Connect(function()
		UiKit.togglePanel(hud.panel)
	end)
	hud.allMaps.Activated:Connect(function()
		if hud.overlay.Visible then
			hud.overlay.Visible = false
		else
			buildGrid()
			hud.overlay.Visible = true
		end
	end)
	hud.panel.frame:GetPropertyChangedSignal("Visible"):Connect(function()
		hud.overlay.Visible = false
		if shown() then
			-- It opens on a map with a reward waiting; else on a new farthest map; else where you left it.
			local _, firstWaiting = waitingCount()
			local farthest = farthestMap()
			local target = current
			if firstWaiting then
				target = firstWaiting
			elseif farthest ~= farthestSeen then
				target = farthest
			end
			farthestSeen = farthest
			show(target, true)
		elseif page then
			page.frame:Destroy() -- its models go with it: nothing is drawn while the Index is closed
			page = nil
		end
	end)

	-- Scrolling: the mouse wheel over the panel, or a finger swiped up or down on it.
	local function overPanel(position: Vector2): boolean
		local corner, size = hud.panel.frame.AbsolutePosition, hud.panel.frame.AbsoluteSize
		return position.X >= corner.X and position.X <= corner.X + size.X and position.Y >= corner.Y and position.Y <= corner.Y + size.Y
	end
	UserInputService.InputChanged:Connect(function(input)
		if input.UserInputType == Enum.UserInputType.MouseWheel and shown() and not hud.overlay.Visible then
			local mouse = UserInputService:GetMouseLocation() - GuiService:GetGuiInset()
			if overPanel(mouse) then
				go(current + (if input.Position.Z > 0 then -1 else 1))
			end
		end
	end)
	local touches = {}
	UserInputService.InputBegan:Connect(function(input)
		if input.UserInputType == Enum.UserInputType.Touch and shown() and not hud.overlay.Visible then
			local at = Vector2.new(input.Position.X, input.Position.Y)
			if overPanel(at) then
				touches[input] = at
			end
		end
	end)
	UserInputService.InputEnded:Connect(function(input)
		local from = touches[input]
		if not from then
			return
		end
		touches[input] = nil
		local moved = Vector2.new(input.Position.X, input.Position.Y) - from
		if math.abs(moved.Y) >= SWIPE and math.abs(moved.Y) > math.abs(moved.X) * 1.5 and shown() and not hud.overlay.Visible then
			go(current + (if moved.Y < 0 then 1 else -1))
		end
	end)

	changed.OnClientEvent:Connect(function(newDiscovered, newClaimed)
		discovered = newDiscovered
		claimed = newClaimed or {}
		IndexController.discovered = newDiscovered
		for _, map in maps do
			local biome = map.biome
			if isComplete(biome) and not completed[biome.id] then
				completed[biome.id] = true
				if heardFromServer and not claimed[biome.id] then
					shoutCompleted(biome)
				end
			end
		end
		heardFromServer = true
		refreshBadges()
		if shown() and not sliding then
			show(current, false)
			if hud.overlay.Visible then
				buildGrid()
			end
		end
	end)
	refreshBadges()
end

return IndexController
