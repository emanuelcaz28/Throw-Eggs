-- The reveal after the landing, the soul of the game [Owner, 2026-11-07]. First the caught monster walks slowly all the
-- way to the egg, seen through its eyes (RevealWalk), with the big "1 in X" locked on 1 then creeping up a little (on
-- catches rarer than Config/Reveal counterMinOneIn only). Then the camera switches to its feet and zooms out very slowly
-- while the numbers climb for real and the name fills in, never showing the whole body (RevealCloseUp). When the numbers
-- finish it all holds its breath, then the camera whips back to the whole monster: a flash, a roar, light rays burst out
-- behind it in the rarity's colour (RevealRays), and the catch is written straight on the screen. Display only: the
-- server has already rolled the catch, and all of this is suspense leading up to that result.
-- The look is UI design v2 (mock-ups 09-10 for the counter, 15-16b for the letters and the final
-- colour moment, in design/ui-mockups/build.py), built with UiKit.
local ContextActionService = game:GetService("ContextActionService")
local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local Index = require(ReplicatedStorage.Shared.Config.Index)
local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local DinoLifeController = require(script.Parent.DinoLifeController)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)
local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local RevealCloseUp = require(script.Parent.RevealCloseUp)
local RevealDrama = require(script.Parent.RevealDrama)
local RevealDust = require(script.Parent.RevealDust)
local RevealOpening = require(script.Parent.RevealOpening)
local RevealRays = require(script.Parent.RevealRays)
local RevealSound = require(script.Parent.RevealSound)
local RevealWalk = require(script.Parent.RevealWalk)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local RevealController = {}

local SKIP_ACTION = "RevealSkip"
local WHITE = Color3.new(1, 1, 1)
local BLOCKER_FOLDERS = { "CorridorDecor", "ArenaDecor" } -- the map's decorations that may hide in the reveal
local LETTER_POP = 1.3 -- a letter lands this big and settles back to normal size
local LETTER_SIZE = 64
local LABEL_WIGGLE = 3 -- degrees the luck label rocks either way
local NEW_COLORS = { "#ffc14d", "#ff7a2f" }
local BANNER_HEIGHT = 132
local STICKER_ROW = 84
local LUCK_ABOVE_BOTTOM = 150 -- design pixels from the screen's bottom to the luck label and counter, clear of the letters
local LUCK_ROW = 60 -- design pixels: the settled luck label's row, above the number
local NUMBER_ROW = 140 -- and the number's
local MIN_TEXT_BRIGHTNESS = 0.55 -- mutation names darker than this are lifted towards white
-- The final text's rows, in design pixels (as built in buildGui), from the screen's bottom edge up: its gap, "tap to
-- continue", the message, the odds, $/s, the name, size and mutation, then the tier sticker. The camera frames the
-- monster above them.
local FINAL_ROWS = { gap = 16, hint = 30, message = 30, odds = 52, income = 44, name = 86, tags = 34, sticker = STICKER_ROW }
local STORED_TEXT = {
	backpack = "Plot full: sent to your backpack",
	sold = "Plot and backpack full: sold",
}

local hud = nil

local function tween(instance: Instance, time: number, goal, style: Enum.EasingStyle?, direction: Enum.EasingDirection?)
	local info = TweenInfo.new(time, style or Enum.EasingStyle.Quad, direction or Enum.EasingDirection.Out)
	local created = TweenService:Create(instance, info, goal)
	created:Play()
	return created
end

-- Puts the character back on its own plot, by the exit. Players without a plot stay put.
-- The client moves its own character, the same way walking does.
local function returnHome()
	local plotIndex = player:GetAttribute("PlotIndex")
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	local root = character and character:FindFirstChild("HumanoidRootPart")
	if not plotIndex or not humanoid or not root or humanoid.Health <= 0 then
		return
	end
	local home = Plot.homeCFrame(plotIndex) + Vector3.new(0, humanoid.HipHeight + root.Size.Y / 2, 0)
	character:PivotTo(home)
	root.AssemblyLinearVelocity = Vector3.zero
	-- Behind and above the character, so the view opens on the plot.
	workspace.CurrentCamera.CFrame = CFrame.lookAt((home * CFrame.new(0, 8, 16)).Position, home.Position)
end

-- Hides, on this screen only, what would stand between the reveal's camera and the catch. A giant's camera ends
-- hundreds of studs back, and over the arena a huge statue on a base would block it, so all the bases' statues hide
-- (statues placed during the reveal too, like the new catch going onto the base). Of the map's decorations, those in
-- the line of sight from any of `eyes` (where the camera will be) to the monster (`box`, `size`) hide, and those it
-- stands on. Returns the function that brings them all back.
local function hideBlockers(eyes: { Vector3 }, box: CFrame, size: Vector3): () -> ()
	local hidden = {}
	local function hide(part: Instance)
		if part:IsA("BasePart") and hidden[part] == nil then
			hidden[part] = part.LocalTransparencyModifier
			part.LocalTransparencyModifier = 1
		end
	end
	local plots = workspace:FindFirstChild("Plots")
	local added = nil
	if plots then
		for _, part in plots:GetDescendants() do
			if part:FindFirstAncestor("Statues") then
				hide(part)
			end
		end
		added = plots.DescendantAdded:Connect(function(part)
			if part:FindFirstAncestor("Statues") then
				hide(part)
			end
		end)
	end

	-- The sight line widens from the camera to the monster's width, like the view of it does.
	local width = math.max(size.X, size.Y, size.Z) / 2
	local function inSight(position: Vector3, reach: number): boolean
		for _, eye in eyes do
			local sight = box.Position - eye
			local length = sight.Magnitude
			local along = sight.Unit
			local offset = position - eye
			local ahead = offset:Dot(along)
			local aside = (offset - along * ahead).Magnitude
			if ahead > 0 and ahead < length - width * 0.5 and aside < width * (ahead / length) + reach then
				return true
			end
		end
		return false
	end
	local map = workspace:FindFirstChild("Map")
	for _, folderName in BLOCKER_FOLDERS do
		local folder = map and map:FindFirstChild(folderName)
		for _, prop in if folder then folder:GetChildren() else {} do
			local ok, frame, propSize = pcall(function()
				if prop:IsA("Model") then
					return prop:GetBoundingBox()
				end
				return prop.CFrame, prop.Size
			end)
			if ok and frame then
				local underIt = box:PointToObjectSpace(frame.Position)
				local standsOn = math.abs(underIt.X) < size.X / 2 and math.abs(underIt.Z) < size.Z / 2 and frame.Position.Y < box.Position.Y
				if standsOn or inSight(frame.Position, propSize.Magnitude / 2) then
					hide(prop)
					for _, part in prop:GetDescendants() do
						hide(part)
					end
				end
			end
		end
	end

	return function()
		if added then
			added:Disconnect()
		end
		for part, modifier in hidden do
			if part.Parent then
				part.LocalTransparencyModifier = modifier
			end
		end
	end
end

local function addScale(object: GuiObject, scale: number)
	local uiScale = Instance.new("UIScale")
	uiScale.Scale = scale
	uiScale.Parent = object
	return uiScale
end

local function row(parent: Instance, padding: number): UIListLayout
	local layout = Instance.new("UIListLayout")
	layout.FillDirection = Enum.FillDirection.Horizontal
	layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	layout.VerticalAlignment = Enum.VerticalAlignment.Center
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Padding = UDim.new(0, padding)
	layout.Parent = parent
	return layout
end

-- Outlined text that grows sideways to fit, for use inside a row.
local function rowText(parent: Instance, value: string, size: number, color: Color3?, height: number): TextLabel
	local label = UiKit.text(parent, value, size, color)
	label.AutomaticSize = Enum.AutomaticSize.X
	label.Size = UDim2.fromOffset(0, height)
	return label
end

-- Text in the three layers of the design (Figma "Throw Eggs - Reveal Text", Config/Reveal text): a hard shadow, a rim in
-- the luck tier's deep colour, and the lit text in its dark outline. `stretch` fills its parent's width; otherwise it grows
-- sideways to fit, for use inside a row. `strokeScale` is how big it's shown, since outlines ignore UIScale.
local function layered(parent: Instance, style, value: string, strokeScale: number, stretch: boolean?)
	local height = math.ceil(style.size * 1.22)
	local holder = Instance.new("Frame")
	holder.BackgroundTransparency = 1
	if stretch then
		holder.Size = UDim2.new(1, 0, 0, height)
	else
		holder.AutomaticSize = Enum.AutomaticSize.X
		holder.Size = UDim2.fromOffset(0, height + (style.raise or 0))
	end
	holder.Parent = parent

	local function layer(name: string, color: Color3, outline: Color3, thickness: number, drop: number, order: number): TextLabel
		local label = UiKit.text(holder, value, style.size, color)
		label.Name = name
		label.ZIndex = order
		if stretch then
			label.Size = UDim2.fromScale(1, 1)
		else
			label.AutomaticSize = Enum.AutomaticSize.X
			label.Size = UDim2.fromOffset(0, height)
		end
		label.Position = UDim2.fromOffset(0, drop)
		local stroke = label:FindFirstChildOfClass("UIStroke")
		stroke.Color = outline
		stroke.Thickness = thickness * strokeScale
		return label
	end
	local shadow = layer("Shadow", UiKit.INK, UiKit.INK, style.rim, style.drop, 1)
	local rim = layer("Rim", UiKit.INK, UiKit.INK, style.rim, 0, 2)
	local front = layer("Front", WHITE, UiKit.INK, style.ink, 0, 3)
	local gradient = Instance.new("UIGradient")
	gradient.Rotation = 90
	gradient.Parent = front
	return {
		holder = holder,
		labels = { shadow, rim, front },
		rim = rim,
		gradient = gradient,
	}
end

local function setLayered(text, value: string)
	for _, label in text.labels do
		label.Text = value
	end
end

-- Lit in `tier`'s colours; the plain walk look without one.
local function paintLayered(text, tier)
	local walk = Reveal.text
	text.gradient.Color = if tier
		then ColorSequence.new({
			ColorSequenceKeypoint.new(0, tier.color:Lerp(WHITE, 0.7)),
			ColorSequenceKeypoint.new(0.15, tier.color:Lerp(WHITE, 0.7)),
			ColorSequenceKeypoint.new(0.85, tier.color),
			ColorSequenceKeypoint.new(1, tier.color),
		})
		else ColorSequence.new(walk.walkTop, walk.walkBottom)
	local color = if tier then tier.rim else UiKit.INK
	text.rim.TextColor3 = color
	text.rim:FindFirstChildOfClass("UIStroke").Color = color
end

-- The top or bottom edge of the screen, lit in the luck tier's colour and fading towards the middle.
local function edgeGlow(parent: Instance, top: boolean): Frame
	local glow = Instance.new("Frame")
	glow.Name = if top then "GlowTop" else "GlowBottom"
	glow.AnchorPoint = Vector2.new(0, if top then 0 else 1)
	glow.Position = UDim2.fromScale(0, if top then 0 else 1)
	glow.Size = UDim2.fromScale(1, 0.22) -- [Owner, 2026-11-06] was 0.36: with a strong label it washed the whole screen
	glow.BackgroundTransparency = 1
	glow.BorderSizePixel = 0
	glow.Parent = parent
	local fade = Instance.new("UIGradient")
	fade.Rotation = if top then 90 else -90
	fade.Transparency = NumberSequence.new(0, 1)
	fade.Parent = glow
	return glow
end

-- A layer for what must cover the whole screen, past a phone's notch and round corners too [Owner, 2026-11-07: the eyes
-- closing left the screen's sides open on a phone]. The text stays on RevealHud, inside the safe area, so it's never cut off.
local function coverLayer(name: string, order: number): ScreenGui
	local layer = Instance.new("ScreenGui")
	layer.Name = name
	layer.IgnoreGuiInset = true
	layer.ScreenInsets = Enum.ScreenInsets.None
	layer.ResetOnSpawn = false
	layer.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	layer.DisplayOrder = order
	layer.Parent = player:WaitForChild("PlayerGui")
	return layer
end

local function buildGui()
	local behind = coverLayer("RevealBehind", 10) -- under the text: the eyes, the screen's edges, the colour wash
	local inFront = coverLayer("RevealInFront", 12) -- over the text: the cuts to black and the flashes
	local gui = Instance.new("ScreenGui")
	gui.Name = "RevealHud"
	gui.IgnoreGuiInset = true
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 11
	gui.Parent = player:WaitForChild("PlayerGui")
	local scale = UiKit.scale()
	local inset = GuiService:GetGuiInset().Y

	local glows = { edgeGlow(behind, true), edgeGlow(behind, false) }
	-- Lucky catches darken the screen's edges as their luck builds, so the monster in the middle stands out
	-- (Config/Reveal lucky vignette). Built-in Roblox image: black at the edges, clear in the middle.
	local vignette = Instance.new("ImageLabel")
	vignette.Name = "Vignette"
	vignette.AnchorPoint = Vector2.new(0.5, 0.5)
	vignette.Position = UDim2.fromScale(0.5, 0.5)
	vignette.Size = UDim2.fromScale(1.25, 1.25)
	vignette.BackgroundTransparency = 1
	vignette.Image = Reveal.walk.glow.darkImage
	vignette.ImageTransparency = 1
	vignette.ZIndex = 0
	vignette.Parent = behind

	-- The luck label (LUCKY! ... GODLY!) and the "1 in X" counter, just above the letters at the bottom, so the monster
	-- has the top of the screen to itself and stays where it is when the final text comes [Owner, 2026-11-06: at the
	-- top, the counter sat on the monster]. [Owner, 2026-11-07] Big, as designed in Figma "Throw Eggs - Reveal Text".
	local look = Reveal.text
	local top = Instance.new("Frame")
	top.Name = "Top"
	top.AnchorPoint = Vector2.new(0.5, 1)
	top.Position = UDim2.new(0.5, 0, 1, -LUCK_ABOVE_BOTTOM * scale)
	top.Size = UDim2.fromOffset(1200, LUCK_ROW + NUMBER_ROW)
	top.BackgroundTransparency = 1
	top.Visible = false
	top.ZIndex = 3
	top.Parent = gui
	addScale(top, scale)

	local luck = layered(top, look.label, "", scale, true)
	luck.holder.Name = "Luck"
	local luckPop = addScale(luck.holder, 1)

	-- The counter: "1 in" small and the number big, no box or icon.
	local pill = Instance.new("Frame")
	pill.Name = "Counter"
	pill.AnchorPoint = Vector2.new(0.5, 1)
	pill.Position = UDim2.new(0.5, 0, 1, 0)
	pill.AutomaticSize = Enum.AutomaticSize.X
	pill.Size = UDim2.fromOffset(0, NUMBER_ROW)
	pill.BackgroundTransparency = 1
	pill.Parent = top
	row(pill, 16).VerticalAlignment = Enum.VerticalAlignment.Bottom
	local pillPop = addScale(pill, 1)
	local oneIn = layered(pill, look.lead, "1 in", scale)
	oneIn.holder.LayoutOrder = 1
	local counter = layered(pill, look.number, "1", scale)
	counter.holder.LayoutOrder = 2

	-- A new luck label first slams in huge in the middle of the screen, then flies down to its place over the number.
	local slamText = layered(gui, look.slam, "", scale * Reveal.lucky.slamScale, true)
	local slam = slamText.holder
	slam.Name = "LuckSlam"
	slam.AnchorPoint = Vector2.new(0.5, 0.5)
	slam.Size = UDim2.fromOffset(1000, math.ceil(look.slam.size * 1.22))
	slam.Visible = false
	slam.ZIndex = 4
	local slamScale = addScale(slam, scale)

	-- Bottom: the name as blank dashes, filled in out of order (mock-up 15).
	local letters = Instance.new("Frame")
	letters.Name = "Letters"
	letters.AnchorPoint = Vector2.new(0.5, 1)
	letters.Position = UDim2.fromScale(0.5, 1)
	letters.Size = UDim2.fromOffset(1200, 160)
	letters.BackgroundTransparency = 1
	letters.Visible = false
	letters.ZIndex = 3
	letters.Parent = gui
	addScale(letters, scale)
	local tileRow = Instance.new("Frame")
	tileRow.BackgroundTransparency = 1
	tileRow.AnchorPoint = Vector2.new(0, 1)
	tileRow.Position = UDim2.new(0, 0, 1, -74)
	tileRow.Size = UDim2.new(1, 0, 0, math.round(LETTER_SIZE * 1.1))
	tileRow.Parent = letters
	row(tileRow, 4).VerticalAlignment = Enum.VerticalAlignment.Bottom
	local hint = UiKit.text(letters, "tap to skip", 20)
	hint.AnchorPoint = Vector2.new(0, 1)
	hint.Position = UDim2.new(0, 0, 1, -22)

	-- The final text, straight on the screen with no panel (mock-ups 16 and 16b): size and
	-- mutation small, the name big in its rarity colour with a NEW! sticker, $/s, then the odds on
	-- lucky catches and "tap to continue".
	local final = Instance.new("Frame")
	final.Name = "Final"
	final.AnchorPoint = Vector2.new(0.5, 1)
	final.Position = UDim2.new(0.5, 0, 1, -16)
	final.Size = UDim2.fromOffset(1200, 400)
	final.BackgroundTransparency = 1
	final.Visible = false
	final.ZIndex = 3
	final.Parent = gui
	addScale(final, scale)
	local stack = Instance.new("UIListLayout")
	stack.HorizontalAlignment = Enum.HorizontalAlignment.Center
	stack.VerticalAlignment = Enum.VerticalAlignment.Bottom
	stack.SortOrder = Enum.SortOrder.LayoutOrder
	stack.Parent = final

	local tags = Instance.new("Frame")
	tags.BackgroundTransparency = 1
	tags.Size = UDim2.new(1, 0, 0, 34)
	tags.LayoutOrder = 1
	tags.Parent = final
	row(tags, 12)
	local sizeName = rowText(tags, "", 26, UiKit.GOLD, 34)
	sizeName.LayoutOrder = 1
	local mutation = rowText(tags, "", 26, nil, 34)
	mutation.LayoutOrder = 2

	local nameRow = Instance.new("Frame")
	nameRow.BackgroundTransparency = 1
	nameRow.Size = UDim2.new(1, 0, 0, 86)
	nameRow.LayoutOrder = 2
	nameRow.Parent = final
	local namePop = addScale(nameRow, 1)
	local name = rowText(nameRow, "", 70, nil, 86)
	name.AnchorPoint = Vector2.new(0.5, 0)
	name.Position = UDim2.fromScale(0.5, 0)
	name:FindFirstChildOfClass("UIStroke").Thickness = 8
	-- Hangs off the name's right end, so the name itself stays centred.
	local newTag = UiKit.tag(nameRow, "NEW!", NEW_COLORS, 30, 9)
	newTag.AnchorPoint = Vector2.new(0, 0.5)
	newTag.Visible = false
	-- TextBounds is in screen pixels, already shrunk or grown by the UIScales above the name, while the tag's
	-- position is in design pixels; divide that out, or on a phone (scale ~0.5) the tag landed on the name.
	local function placeNewTag()
		local shown = name.AbsoluteSize.Y / 86
		local halfWidth = if shown > 0 then name.TextBounds.X / shown / 2 else 0
		newTag.Position = UDim2.new(0.5, halfWidth + 14, 0, 22)
	end
	name:GetPropertyChangedSignal("TextBounds"):Connect(placeNewTag)
	name:GetPropertyChangedSignal("AbsoluteSize"):Connect(placeNewTag)
	placeNewTag()

	local income = UiKit.text(final, "", 36, UiKit.CASH)
	income.Size = UDim2.new(1, 0, 0, 44)
	income.LayoutOrder = 3
	income:FindFirstChildOfClass("UIStroke").Thickness = 6

	-- The odds on lucky catches: plain big outlined text in the luck tier's colour, no box or icon.
	local oddsRow = Instance.new("Frame")
	oddsRow.BackgroundTransparency = 1
	oddsRow.Size = UDim2.new(1, 0, 0, 52)
	oddsRow.LayoutOrder = 4
	oddsRow.Parent = final
	local finalOdds = UiKit.text(oddsRow, "", 42)
	finalOdds.Size = UDim2.fromScale(1, 1)
	finalOdds:FindFirstChildOfClass("UIStroke").Thickness = 7
	local oddsGradient = Instance.new("UIGradient")
	oddsGradient.Rotation = 90
	oddsGradient.Parent = finalOdds

	local message = UiKit.text(final, "", 22, UiKit.GOLD)
	message.Size = UDim2.new(1, 0, 0, 30)
	message.LayoutOrder = 5

	local continueHint = UiKit.text(final, "tap to continue", 18)
	continueHint.Size = UDim2.new(1, 0, 0, 30)
	continueHint.LayoutOrder = 6
	addScale(continueHint, 1)
	UiKit.pulse(continueHint)

	-- On lucky catches the luck tier's sticker sits on top of the final text, so the top of the screen stays clear for
	-- the monster's head.
	local stickerHolder = Instance.new("Frame")
	stickerHolder.Name = "TierSticker"
	stickerHolder.Size = UDim2.new(1, 0, 0, STICKER_ROW)
	stickerHolder.BackgroundTransparency = 1
	stickerHolder.LayoutOrder = 0
	stickerHolder.Visible = false
	stickerHolder.Parent = final

	-- The colour moment: the rarity's colour lights the screen's top and bottom, leaving the middle clear.
	local wash = Instance.new("Frame")
	wash.Name = "Wash"
	wash.Size = UDim2.fromScale(1, 1)
	wash.BackgroundTransparency = 1
	wash.BorderSizePixel = 0
	wash.ZIndex = 0
	wash.Parent = behind
	-- Clearer in the middle, where the dino stands, stronger towards the top and bottom.
	local washFade = Instance.new("UIGradient")
	washFade.Rotation = 90
	washFade.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 0),
		NumberSequenceKeypoint.new(0.28, 0.8),
		NumberSequenceKeypoint.new(0.5, 1),
		NumberSequenceKeypoint.new(0.72, 0.8),
		NumberSequenceKeypoint.new(1, 0),
	})
	washFade.Parent = wash

	-- Back on the plot, very rare catches keep a "YOU CAUGHT!" banner up for a while.
	local banner = Instance.new("Frame")
	banner.Name = "CaughtBanner"
	banner.AnchorPoint = Vector2.new(0.5, 0)
	banner.Size = UDim2.fromOffset(660, BANNER_HEIGHT)
	banner.BackgroundColor3 = UiKit.PANEL
	banner.Visible = false
	banner.Parent = gui
	UiKit.corner(banner, 28)
	UiKit.stroke(banner, 5)
	addScale(banner, scale)
	local bannerEdge = Instance.new("Frame")
	bannerEdge.BackgroundTransparency = 1
	bannerEdge.Position = UDim2.fromOffset(4, 4)
	bannerEdge.Size = UDim2.new(1, -8, 1, -8)
	bannerEdge.Parent = banner
	UiKit.corner(bannerEdge, 24)
	UiKit.stroke(bannerEdge, 4, UiKit.PANEL_EDGE)
	local bannerTile = Instance.new("Frame")
	bannerTile.BackgroundTransparency = 1
	bannerTile.Position = UDim2.fromOffset(16, 16)
	bannerTile.Size = UDim2.fromOffset(100, 100)
	bannerTile.Parent = banner
	local caught = UiKit.text(banner, "YOU CAUGHT!", 22, UiKit.GOLD, Enum.TextXAlignment.Left)
	caught.Position = UDim2.fromOffset(132, 12)
	caught.Size = UDim2.new(1, -148, 0, 28)
	local bannerName = UiKit.text(banner, "", 30, nil, Enum.TextXAlignment.Left)
	bannerName.Position = UDim2.fromOffset(132, 40)
	bannerName.Size = UDim2.new(1, -148, 0, 38)
	bannerName.TextScaled = true
	local bannerNameLimit = Instance.new("UITextSizeConstraint")
	bannerNameLimit.MaxTextSize = 30
	bannerNameLimit.Parent = bannerName
	local bannerOdds = UiKit.text(banner, "", 26, UiKit.GOLD, Enum.TextXAlignment.Left)
	bannerOdds.Position = UDim2.fromOffset(132, 82)
	bannerOdds.Size = UDim2.new(1, -148, 0, 36)

	local flash = Instance.new("Frame")
	flash.Name = "Flash"
	flash.Size = UDim2.fromScale(1, 1)
	flash.BackgroundColor3 = WHITE
	flash.BackgroundTransparency = 1
	flash.BorderSizePixel = 0
	flash.ZIndex = 10
	flash.Parent = inFront

	-- The walk to the egg: its rings round the screen, and the cuts to black before and after it.
	local walkGlow = RevealWalk.buildGlow(behind)
	local black = Instance.new("Frame")
	black.Name = "Black"
	black.Size = UDim2.fromScale(1, 1)
	black.BackgroundColor3 = Color3.new(0, 0, 0)
	black.BackgroundTransparency = 1
	black.BorderSizePixel = 0
	black.ZIndex = 11
	black.Parent = inFront

	return {
		walkGlow = walkGlow,
		black = black,
		scale = scale,
		inset = inset,
		glows = glows,
		vignette = vignette,
		top = top,
		luck = luck,
		luckPop = luckPop,
		pill = pill,
		pillPop = pillPop,
		oneIn = oneIn,
		slam = slam,
		slamText = slamText,
		slamScale = slamScale,
		counter = counter,
		letters = letters,
		tileRow = tileRow,
		final = final,
		name = name,
		namePop = namePop,
		newTag = newTag,
		mutation = mutation,
		sizeName = sizeName,
		income = income,
		oddsRow = oddsRow,
		finalOdds = finalOdds,
		oddsGradient = oddsGradient,
		message = message,
		stickerHolder = stickerHolder,
		sticker = nil,
		wash = wash,
		rays = nil,
		banner = banner,
		bannerTile = bannerTile,
		bannerName = bannerName,
		bannerOdds = bannerOdds,
		flash = flash,
	}
end

-- One slot per letter or digit with a white dash under it, a gap between words. Other characters
-- (the "-" in T-Rex) show from the start. Each letter has a fixed slot, so the name never shifts.
-- Returns the slots by their position in the name.
local function buildLetterTiles(name: string)
	for _, child in hud.tileRow:GetChildren() do
		if child:IsA("GuiObject") then
			child:Destroy()
		end
	end
	local tiles = {}
	local cellWidth = math.round(LETTER_SIZE * 0.72)
	local cellHeight = math.round(LETTER_SIZE * 1.1)
	for index = 1, #name do
		local char = name:sub(index, index)
		local cell = Instance.new("Frame")
		cell.BackgroundTransparency = 1
		cell.LayoutOrder = index
		cell.Size = UDim2.fromOffset(if char == " " then LETTER_SIZE // 2 else cellWidth, cellHeight)
		cell.Parent = hud.tileRow
		if char == " " then
			continue
		end
		local label = UiKit.text(cell, if char:match("%w") then "" else char, LETTER_SIZE)
		label.AnchorPoint = Vector2.new(0.5, 1)
		label.Position = UDim2.fromScale(0.5, 1)
		label.Size = UDim2.new(0, cellWidth * 2, 1, 0) -- wide letters (M, W) may spill into the gap
		label:FindFirstChildOfClass("UIStroke").Thickness = 7
		if char:match("%w") then
			local dash = Instance.new("Frame")
			dash.AnchorPoint = Vector2.new(0.5, 1)
			dash.Position = UDim2.new(0.5, 0, 1, -math.round(LETTER_SIZE * 0.12))
			dash.Size = UDim2.fromOffset(math.round(LETTER_SIZE * 0.58), 12)
			dash.BackgroundColor3 = WHITE
			dash.Parent = cell
			UiKit.corner(dash, 5)
			UiKit.stroke(dash, 4)
			tiles[index] = { dash = dash, label = label, pop = addScale(label, 1), char = char }
		end
	end
	return tiles
end

local function showLetter(entry)
	entry.dash.Visible = false
	entry.label.Text = entry.char
	entry.pop.Scale = LETTER_POP
	tween(entry.pop, 0.3, { Scale = 1 }, Enum.EasingStyle.Back)
end

local function shuffledLetterIndexes(name: string): { number }
	local indexes = {}
	for index = 1, #name do
		if name:sub(index, index):match("%w") then
			table.insert(indexes, index)
		end
	end
	for index = #indexes, 2, -1 do
		local swap = math.random(index)
		indexes[index], indexes[swap] = indexes[swap], indexes[index]
	end
	return indexes
end

-- How long the climb lasts: the counter's natural pace, within the configured limits. Lucky catches (with the
-- counter) climb slower, from Reveal.lucky minClimb to maxClimb, not counting the pauses on each label.
local function climbTime(oneIn: number): number
	if oneIn >= Reveal.counterMinOneIn then
		local lucky = Reveal.lucky
		local share = math.log(oneIn / Reveal.counterMinOneIn) / math.log(lucky.rarestOneIn / Reveal.counterMinOneIn)
		return lucky.minClimb + (lucky.maxClimb - lucky.minClimb) * math.clamp(share, 0, 1)
	end
	local steps = math.log(math.max(oneIn, 1)) / math.log(Reveal.counterRate)
	return math.clamp(steps * Reveal.counterStepTime, Reveal.minClimbTime, Reveal.maxClimbTime)
end

local function tierFor(value: number)
	local current = nil
	for _, tier in Reveal.tiers do
		if value >= tier.minOneIn then
			current = tier
		end
	end
	return current
end

-- A colour lifted until it reads against the text's dark outline (Shadow's near-black navy turns lavender).
local function readable(color: Color3): Color3
	local brightness = 0.3 * color.R + 0.59 * color.G + 0.11 * color.B
	return if brightness < MIN_TEXT_BRIGHTNESS then color:Lerp(WHITE, 1 - brightness / MIN_TEXT_BRIGHTNESS) else color
end

-- Lit text: light at the top fading to the tier's colour at the bottom.
local function tierGradient(tier): ColorSequence
	return ColorSequence.new(tier.color:Lerp(WHITE, 0.55), tier.color)
end

local slamShows = 0

-- A new luck label slams in huge in the middle of the screen with a flash in its colour, holds there for the
-- counter's pause, then flies up to its place at the top. A newer label or the final screen cuts it short.
local function slamLabel(tier)
	local settings = Reveal.lucky
	slamShows += 1
	local show = slamShows
	local slam = hud.slam
	setLayered(hud.slamText, tier.label)
	paintLayered(hud.slamText, tier)
	-- At slamY down the screen: between the monster and the counter below, which keeps climbing in view.
	local screenHeight = workspace.CurrentCamera.ViewportSize.Y
	slam.Position = UDim2.new(0.5, 0, 0, screenHeight * settings.slamY)
	slam.Rotation = -4
	hud.slamScale.Scale = hud.scale * settings.slamScale * settings.slamFrom
	slam.Visible = true
	local landing = TweenInfo.new(settings.slamIn, Enum.EasingStyle.Back, Enum.EasingDirection.Out)
	TweenService:Create(hud.slamScale, landing, { Scale = hud.scale * settings.slamScale }):Play()
	TweenService:Create(slam, TweenInfo.new(settings.slamIn * 0.6), { Rotation = 0 }):Play()
	for _, label in hud.slamText.labels do
		local stroke = label:FindFirstChildOfClass("UIStroke")
		label.TextTransparency = 1
		stroke.Transparency = 1
		TweenService:Create(label, TweenInfo.new(settings.slamIn * 0.6), { TextTransparency = 0 }):Play()
		TweenService:Create(stroke, TweenInfo.new(settings.slamIn * 0.6), { Transparency = 0 }):Play()
	end
	setLayered(hud.luck, "")

	task.delay(settings.slamIn, function()
		if show ~= slamShows then
			return
		end
		hud.flash.BackgroundColor3 = tier.color:Lerp(WHITE, 0.5)
		hud.flash.BackgroundTransparency = settings.flash
		tween(hud.flash, settings.flashTime, { BackgroundTransparency = 1 })
	end)
	task.delay(math.max(settings.holdTime - settings.slamFly, settings.slamIn), function()
		if show ~= slamShows then
			return
		end
		local target = hud.luck.holder.AbsolutePosition + hud.luck.holder.AbsoluteSize / 2
		local settled = hud.scale * Reveal.text.label.size / Reveal.text.slam.size
		tween(slam, settings.slamFly, { Position = UDim2.fromOffset(target.X, target.Y) }, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		tween(hud.slamScale, settings.slamFly, { Scale = settled }, Enum.EasingStyle.Quad, Enum.EasingDirection.In).Completed:Wait()
		if show ~= slamShows then
			return
		end
		slam.Visible = false
		setLayered(hud.luck, tier.label)
		hud.luckPop.Scale = 1.25
		tween(hud.luckPop, 0.25, { Scale = 1 }, Enum.EasingStyle.Back)
	end)
end

local function hideSlam()
	slamShows += 1
	hud.slam.Visible = false
end

-- A new luck tier: its label pops in (or slams in, `slam`), the counter and the screen edges light up in its colour.
local function pulse(tier, slam: boolean?)
	for _, glow in hud.glows do
		glow.BackgroundColor3 = tier.color
		glow.BackgroundTransparency = 1 - math.min(tier.glow + 0.15, 1)
		tween(glow, 0.5, { BackgroundTransparency = 1 - tier.glow })
	end

	paintLayered(hud.luck, tier)
	paintLayered(hud.counter, tier)
	paintLayered(hud.oneIn, tier)
	if slam then
		slamLabel(tier)
		return
	end
	setLayered(hud.luck, tier.label)
	hud.luckPop.Scale = 0.3
	tween(hud.luckPop, 0.35, { Scale = 1 }, Enum.EasingStyle.Back)
end

local bannerShows = 0
local playing = false
local finishedEvent = Instance.new("BindableEvent")

-- Fires with the catch once the player has tapped through its reveal and is back on their base.
RevealController.finished = finishedEvent.Event

RevealController.returnHome = returnHome

function RevealController.isPlaying(): boolean
	return playing
end

-- The colour moment: a white flash, the rarity colour lights the screen's edges, light rays burst out behind the
-- monster. `strength` is 0 for a catch with no luck label up to 1 for the rarest label.
local function colourMoment(rarity: string, stage, strength: number)
	local pair = UiKit.RARITY[rarity]
	local light, deep = Color3.fromHex(pair[1]), Color3.fromHex(pair[2])
	hud.flash.BackgroundColor3 = WHITE
	hud.flash.BackgroundTransparency = Reveal.flashTransparency
	tween(hud.flash, Reveal.flashTime, { BackgroundTransparency = 1 })
	hud.wash.BackgroundColor3 = deep
	hud.wash.BackgroundTransparency = 1
	tween(hud.wash, Reveal.washTime, { BackgroundTransparency = Reveal.washTransparency })
	for _, glow in hud.glows do
		glow.BackgroundColor3 = deep
		-- The luck glow was strong during the climb; at the end it settles to a soft edge, so the sky stays the sky.
		tween(glow, Reveal.washTime, { BackgroundTransparency = math.max(glow.BackgroundTransparency, 1 - Reveal.finalGlow) })
	end
	if hud.rays then
		hud.rays.destroy()
	end
	-- Centred on the monster itself, not on the box round it and the egg.
	local monsterBox, monsterSize = stage.model:GetBoundingBox()
	hud.rays = RevealRays.burst(monsterBox, monsterSize, workspace.CurrentCamera.CFrame, light, deep, strength)
end

local function clearColourMoment()
	hud.wash.BackgroundTransparency = 1
	if hud.rays then
		hud.rays.destroy()
		hud.rays = nil
	end
	if hud.sticker then
		hud.sticker:Destroy()
		hud.sticker = nil
	end
end

-- Slides the "YOU CAUGHT!" banner down from the top, and back up after a while.
local function showCaughtBanner(catch, fullName: string)
	bannerShows += 1
	local show = bannerShows
	for _, child in hud.bannerTile:GetChildren() do
		child:Destroy()
	end
	UiKit.dinoTile(hud.bannerTile, catch.id, catch.name, 100, 100, { mutation = catch.mutation })
	hud.bannerName.Text = fullName
	hud.bannerOdds.Text = `1 in {Format.commas(catch.oneIn)}`

	local hidden = UDim2.new(0.5, 0, 0, -(BANNER_HEIGHT + 20) * hud.scale)
	hud.banner.Position = hidden
	hud.banner.Visible = true
	tween(hud.banner, 0.45, { Position = UDim2.new(0.5, 0, 0, hud.inset + 12) }, Enum.EasingStyle.Back)
	task.delay(Reveal.caughtBannerTime, function()
		if show ~= bannerShows then
			return
		end
		tween(hud.banner, 0.3, { Position = hidden }, Enum.EasingStyle.Quad, Enum.EasingDirection.In).Completed:Wait()
		if show == bannerShows then
			hud.banner.Visible = false
		end
	end)
end

function RevealController.start()
	hud = buildGui()
	hud.undo = {} -- what the reveal changed in the world, to put back at its end
	RevealSound.preload()
end

-- Puts back everything the reveal changed in the world: the corridor's walls, the things it hid.
local function undoWorld()
	for index = #hud.undo, 1, -1 do -- last in, first out: two of them may have hidden the same part
		hud.undo[index]()
	end
	table.clear(hud.undo)
end

local function play(catch, egg: BasePart)
	local camera = workspace.CurrentCamera
	local landing = egg.Position
	-- The light and haze stay the egg's world's all through the reveal (SkyController), even when the camera ends up
	-- over the next world.
	camera:SetAttribute("WorldFocusZ", landing.Z)
	local ground = Vector3.new(landing.X, landing.Y - egg.Size.Y / 2, landing.Z)
	local drama = RevealDrama.plan(catch) -- the mood of rare and big catches; nil for common ones
	local hushed = false
	local showCounter = catch.oneIn >= Reveal.counterMinOneIn
	local mutation = DinoStats.findOption(Catch.mutations, catch.mutation)
	local size = DinoStats.findOption(Catch.sizes, catch.size)

	local walkPlan = nil
	local planned, planError = pcall(function()
		walkPlan = RevealWalk.plan(catch, ground, mutation and mutation.color)
	end)
	if not planned then
		warn(`[RevealController] Walk failed: {planError}`)
	end
	-- How long it all takes, kept under Config/Reveal maxTotal: the walk, the climb, and the held breath.
	local duration = math.max(climbTime(catch.oneIn), if drama then drama.minClimb else 0)
	if walkPlan then
		local hush = if drama then drama.hushTime else 0
		local shrink = math.min((Reveal.maxTotal - hush) / (walkPlan.duration + duration), 1)
		walkPlan.duration *= shrink
		duration *= shrink
	end
	-- A monster too wide for the corridor gets more room (RevealOpening).
	local wallHalf = RevealOpening.halfWidth(if walkPlan then walkPlan.width else 0)

	-- The number the counter starts on: random, and higher the rarer the catch. It's locked there for a while, then creeps
	-- up a little to `teaser` on the walk, and only goes up for real from the feet.
	local tease = Reveal.tease
	local teaseLock = tease.lock[1] + (tease.lock[2] - tease.lock[1]) * math.random()
	local rareShare = math.clamp(math.log(math.max(catch.oneIn, Reveal.counterMinOneIn) / Reveal.counterMinOneIn) / math.log(tease.rarestOneIn / Reveal.counterMinOneIn), 0, 1)
	local lowest = tease.common[1] + (tease.rarest[1] - tease.common[1]) * rareShare
	local highest = tease.common[2] + (tease.rarest[2] - tease.common[2]) * rareShare
	local firstNumber = math.floor(lowest + (highest - lowest) * math.random())
	if firstNumber % 5 == 0 then
		firstNumber += 1
	end
	local teaseRise = tease.rise[1] + (tease.rise[2] - tease.rise[1]) * math.random()
	local teaser = math.max(math.min(math.floor(firstNumber * teaseRise), tease.most), firstNumber + 1)
	local shownNumber = firstNumber
	local upperName = catch.name:upper()
	local letterOrder = shuffledLetterIndexes(upperName)
	local tiles = buildLetterTiles(upperName)
	-- Only catches that show the counter get a luck label, sticker and odds at the end.
	local finalTier = if showCounter then tierFor(catch.oneIn) else nil
	local message = if catch.completedBiome
		then `{catch.completedBiome} complete! x{Index.xpBoost.multiplier} XP for {Index.xpBoost.seconds // 60} min`
		elseif catch.newBest and not catch.isNew then "NEW BEST!"
		else STORED_TEXT[catch.storedIn]
	local finalTierIndex = if finalTier then table.find(Reveal.tiers, finalTier) else 0
	local shakeAngle = math.rad(Reveal.shake[finalTierIndex + 1] or 0)
	local impact = Reveal.impact
	local hitsHard = showCounter or drama ~= nil -- common catches get no shaking or instant zooms
	-- The counter never stops [Owner, 2026-11-06]: each luck label slams onto the screen while the numbers keep
	-- climbing past it. (It used to pause on every label.)
	local climbed = 0
	local lastFrame = 0
	local joltAt, joltAngle = 0, 0
	-- The instant zooms: the field of view is multiplied by zoomBy, snapping in at zoomAtTime, held for zoomHold seconds.
	-- The unveil starts wider (unveilBy) and eases back.
	local zoomAtTime, zoomBy, zoomHold = -math.huge, 1, impact.zoomHold
	local unveilBy = 1
	local nextBeat = math.huge
	local revealedCount = 0
	local currentTier = nil
	local dino = nil
	local dust = nil -- thrown up off the ground when something big lands (RevealDust), once it stands there
	local roarNow = nil -- makes the monster roar (DinoLifeController.reveal)
	-- The shot from the feet (RevealCloseUp), set up once the walk is over. The slow zoom runs from zoomAt to the last
	-- number; the final move goes from whipFrom to the end in whipLength seconds, quicker after a tap to skip.
	local stage = nil
	local zoomAt = math.huge
	local whipFrom, whipLength = 0, 1
	local startedAt = os.clock()
	local finished = false
	local cardShown = false
	local cardShownAt = 0
	local rarity = UiKit.rarityOf(catch.id)
	local done = Instance.new("BindableEvent")
	-- First the monster walks up to the egg, seen through its eyes (RevealWalk); a tap cuts it short.
	local walking = true
	local walkSkipped = false

	for _, glow in hud.glows do
		glow.BackgroundTransparency = 1
	end
	setLayered(hud.luck, "")
	paintLayered(hud.counter, nil)
	paintLayered(hud.oneIn, nil)
	hud.pill.Visible = showCounter
	setLayered(hud.counter, Format.commas(firstNumber))
	hud.pill.Rotation = 0
	hud.top.Visible = false -- it shows behind the first cut to black, the letters once the walk is over
	hud.letters.Visible = false
	hud.final.Visible = false
	clearColourMoment()

	-- An instant zoom, `by` the field of view, starting `after` seconds from now and held for `hold` seconds.
	local function punch(by: number, after: number?, hold: number?)
		zoomAtTime, zoomBy, zoomHold = os.clock() + (after or 0), by, hold or impact.zoomHold
	end

	-- What the field of view is multiplied by right now.
	local function zoomNow(now: number): number
		local since = now - zoomAtTime
		local share = 0
		if since >= 0 then
			if since < impact.zoomIn then
				share = since / impact.zoomIn
			elseif since < impact.zoomIn + zoomHold then
				share = 1
			else
				local u = math.clamp((since - impact.zoomIn - zoomHold) / impact.zoomOut, 0, 1)
				share = 1 - u * u * (3 - 2 * u)
			end
		end
		return 1 + (zoomBy - 1) * share
	end

	-- `slam` on the climb: the label slams in and the camera jolts and snaps in, while the counter keeps climbing.
	local function setTier(tier, slam: boolean?)
		currentTier = tier
		pulse(tier, slam)
		local index = table.find(Reveal.tiers, tier) or 1
		local strength = (index - 1) / math.max(#Reveal.tiers - 1, 1)
		local vignette = Reveal.lucky.vignette
		tween(hud.vignette, 0.5, { ImageTransparency = vignette[1] + (vignette[2] - vignette[1]) * strength })
		if slam then
			local landsIn = Reveal.lucky.slamIn
			joltAt = os.clock() + landsIn
			joltAngle = math.rad(Reveal.lucky.jolt[index] or 0)
			punch(impact.zoom[index] or 1, landsIn)
			task.delay(landsIn, function()
				RevealSound.slam(index, #Reveal.tiers) -- the hit lands with the label
				if dust and not cardShown then
					dust.burst(strength)
				end
			end)
		end
	end

	-- The counter steps to a new whole number with a tick, `pitch` 0 to 1. On the walk each step pops.
	local function setCounter(value: number, pitch: number, pop: boolean)
		local whole = math.floor(value)
		if whole == shownNumber then
			return
		end
		shownNumber = whole
		setLayered(hud.counter, Format.commas(whole))
		RevealSound.tick(pitch)
		if pop then
			hud.pillPop.Scale = tease.size * tease.pop
			tween(hud.pillPop, tease.popTime, { Scale = tease.size })
		end
	end

	-- How far through the whole move the camera is: the very slow zoom up to the last number, then the final move.
	local function pulled(now: number): number
		if cardShown then
			local share = math.clamp((now - cardShownAt) / whipLength, 0, 1)
			return whipFrom + (1 - whipFrom) * TweenService:GetValue(share, Enum.EasingStyle.Quart, Enum.EasingDirection.Out)
		end
		local share = math.clamp((now - zoomAt) / math.max(duration - stage.hold, 0.1), 0, 1)
		return stage.countShare * share ^ Reveal.closeUp.creep
	end

	-- `skipped` when a tap cut the climb short: the final move hurries.
	local function showCard(skipped: boolean)
		local now = os.clock()
		whipFrom = pulled(now)
		whipLength = if skipped then Reveal.closeUp.skipTime else stage.whipTime
		cardShown = true
		cardShownAt = now
		hideSlam()
		if drama then
			drama.unveil()
		end
		RevealSound.bigReveal(catch.size)
		if roarNow then
			roarNow()
		end
		if hitsHard then
			local strength = math.max(finalTierIndex / #Reveal.tiers, if walkPlan then walkPlan.bigness else 0)
			RevealSound.roar(strength)
			-- It snaps wide at once, showing the whole monster, while the camera whips back.
			unveilBy = impact.unveilWide[1] + (impact.unveilWide[2] - impact.unveilWide[1]) * strength
			zoomAtTime = -math.huge
			dust.burst(math.max(strength, 0.5))
		end
		if showCounter then
			setLayered(hud.counter, Format.commas(catch.oneIn))
		end
		if finalTier and finalTier ~= currentTier then
			setTier(finalTier)
		end
		hud.top.Visible = false
		hud.letters.Visible = false
		colourMoment(rarity, stage, finalTierIndex / #Reveal.tiers)
		if drama then -- out of the black, the flash hits harder
			hud.flash.BackgroundTransparency = 0.05
			tween(hud.flash, Reveal.flashTime * 1.6, { BackgroundTransparency = 1 })
		end

		if finalTier then
			local sticker = UiKit.tag(hud.stickerHolder, finalTier.sticker.label, finalTier.sticker.colors, 44, -4)
			sticker.AnchorPoint = Vector2.new(0.5, 0.5)
			sticker.Position = UDim2.fromScale(0.5, 0.5)
			hud.sticker = sticker
		end
		hud.stickerHolder.Visible = finalTier ~= nil

		hud.sizeName.Visible = size ~= nil
		hud.sizeName.Text = if size then size.name else ""
		hud.mutation.Visible = mutation ~= nil
		hud.mutation.Text = if mutation then mutation.name else ""
		hud.mutation.TextColor3 = if mutation then readable(mutation.color) else WHITE
		hud.name.Text = upperName
		hud.name.TextColor3 = Color3.fromHex(UiKit.RARITY_TEXT[rarity])
		hud.newTag.Visible = catch.isNew == true
		hud.namePop.Scale = Reveal.namePop
		tween(hud.namePop, 0.4, { Scale = 1 }, Enum.EasingStyle.Back)
		hud.income.Text = `{Format.cash(catch.income)}/s`
		hud.oddsRow.Visible = finalTier ~= nil
		hud.finalOdds.Text = `1 in {Format.commas(catch.oneIn)}`
		if finalTier then
			hud.oddsGradient.Color = tierGradient(finalTier)
		end

		hud.message.Visible = message ~= nil
		hud.message.Text = message or ""
		hud.final.Visible = true
	end

	local function onTap()
		local now = os.clock()
		if now - startedAt < Reveal.skipDelay then
			return
		end
		if walking then
			walkSkipped = true
			return
		end
		if not cardShown then
			showCard(true)
		elseif now - cardShownAt >= Reveal.skipDelay and not finished then
			finished = true
			done:Fire()
		end
	end

	local inputConnection = UserInputService.InputBegan:Connect(function(input, gameProcessed)
		if
			not gameProcessed
			and (
				input.UserInputType == Enum.UserInputType.MouseButton1
				or input.UserInputType == Enum.UserInputType.Touch
			)
		then
			onTap()
		end
	end)
	ContextActionService:BindAction(SKIP_ACTION, function(_, inputState)
		if inputState == Enum.UserInputState.Begin then
			onTap()
		end
		return Enum.ContextActionResult.Sink
	end, false, Enum.KeyCode.Space, Enum.KeyCode.ButtonA)

	-- The monster's meshes load during the walk, so it stands there from the shot's first frame.
	task.spawn(pcall, RevealCloseUp.preload, catch.id)

	-- Whatever goes wrong in the walk, the reveal still plays and the screen comes back from black.
	local fieldOfView = camera.FieldOfView
	hud.fieldOfView = fieldOfView
	local walkOk, walkError = pcall(function()
		if not walkPlan then
			return
		end
		RevealWalk.play(walkPlan, egg, hud.black, hud.walkGlow, function()
			return walkSkipped
		end, {
			lids = if drama then drama.lids else nil,
			-- Behind the black, the corridor opens for a big monster, and the big counter is ready for the eyes to open on.
			onBlack = function()
				table.insert(hud.undo, RevealOpening.open(wallHalf))
				local eyeLine = Vector3.new(0, walkPlan.eye, 0)
				local path = math.max(walkPlan.eye, 8)
				table.insert(hud.undo, hideBlockers({ walkPlan.start + eyeLine }, CFrame.new(walkPlan.ground), Vector3.one * path))
				if drama then
					drama.mood()
				end
				if showCounter then
					hud.pillPop.Scale = tease.size
					hud.top.Position = UDim2.new(0.5, 0, 1, -tease.above * hud.scale)
					hud.top.Visible = true
				end
			end,
			onFrame = function(elapsed: number, u: number, footfall: boolean)
				if footfall then
					RevealSound.step(walkPlan.bigness)
				end
				if drama then
					drama.onWalk(u)
				end
				-- Locked on its first number for a while, then creeping up a little.
				if showCounter then
					local rise = (elapsed - teaseLock) / math.max(walkPlan.duration * tease.riseEnd - teaseLock, 0.5)
					setCounter(firstNumber * (teaser / firstNumber) ^ math.clamp(rise, 0, 1) + 1e-6, 0, true)
				end
			end,
		})
	end)
	if not walkOk then
		warn(`[RevealController] Walk failed: {walkError}`)
		RevealWalk.hideGlow(hud.walkGlow)
	end
	camera.FieldOfView = fieldOfView

	-- Behind the black, the monster is simply there, right by the egg, where its walk ended. The egg lies upright by
	-- its feet and stays put.
	egg.CFrame = CFrame.new(egg.Position)
	-- The camera frames the monster and the egg in the part of the screen the final text leaves free.
	-- Small monsters stay clear of all of it, so the egg by their feet shows. Big ones fill more of the screen: their
	-- feet may stand behind the sticker, the size line and the top half of the name (their egg is a speck anyway).
	local belowName = FINAL_ROWS.gap + FINAL_ROWS.hint + FINAL_ROWS.income
	if finalTier then
		belowName += FINAL_ROWS.odds
	end
	if message then
		belowName += FINAL_ROWS.message
	end
	local textHeight = belowName + FINAL_ROWS.name + FINAL_ROWS.tags + (if finalTier then FINAL_ROWS.sticker else 0)
	local screenHeight = math.max(camera.ViewportSize.Y, 1)
	local band = {
		(hud.inset + Reveal.closeUp.topGap * hud.scale) / screenHeight,
		1 - (textHeight + Reveal.closeUp.textGap) * hud.scale / screenHeight,
		1 - (belowName + FINAL_ROWS.name / 2) * hud.scale / screenHeight,
	}
	stage = RevealCloseUp.stage(catch, egg, walkPlan and walkPlan.approach, nil, band, wallHalf)
	dino = stage.model
	roarNow = DinoLifeController.reveal(stage.model)
	dust = RevealDust.new(stage.model, ground.Y)
	if drama then
		drama.shade(stage.model)
	end
	local monsterFrame, monsterExtent = stage.model:GetBoundingBox()
	local cameraSpots = {
		RevealCloseUp.cameraAt(stage, 0).Position,
		RevealCloseUp.cameraAt(stage, stage.countShare).Position,
		RevealCloseUp.cameraAt(stage, 1).Position,
	}
	table.insert(hud.undo, hideBlockers(cameraSpots, monsterFrame, monsterExtent))
	-- Seen from far off, a giant would be lost in the world's haze, so the haze thins the further back the camera ends.
	camera:SetAttribute("HazeScale", math.clamp(Reveal.closeUp.clearDistance / stage.distance[2], Reveal.closeUp.minHaze, 1))
	camera.CameraType = Enum.CameraType.Scriptable
	camera.CFrame = RevealCloseUp.cameraAt(stage, 0)
	walking = false

	-- The feet fade in, and the numbers start climbing for real here.
	startedAt = os.clock()
	lastFrame = startedAt
	zoomAt = startedAt + stage.hold
	hud.pillPop.Scale = 1
	hud.top.Position = UDim2.new(0.5, 0, 1, -LUCK_ABOVE_BOTTOM * hud.scale)
	shownNumber = if showCounter then teaser else 1
	if showCounter then
		setLayered(hud.counter, Format.commas(teaser))
	end
	hud.top.Visible = showCounter
	hud.letters.Visible = true
	if drama then
		drama.climb(duration)
		nextBeat = startedAt + impact.beatEvery[1]
	end
	tween(hud.black, Reveal.walk.closeUpFadeIn, { BackgroundTransparency = 1 })
	-- The switch to the feet lands like a stomp.
	if hitsHard then
		punch(impact.arrive)
		joltAt, joltAngle = startedAt, math.rad(impact.arriveJolt)
		dust.burst(if walkPlan then walkPlan.bigness else 0)
		RevealSound.step(math.max(if walkPlan then walkPlan.bigness else 0, 0.6))
	end

	local stepConnection = RunService.RenderStepped:Connect(function()
		local now = os.clock()
		local elapsed = now - startedAt
		climbed += now - lastFrame
		lastFrame = now
		local progress = math.min(climbed / duration, 1)

		hud.luck.holder.Rotation = LABEL_WIGGLE * math.sin(elapsed * 4)

		camera.CameraType = Enum.CameraType.Scriptable -- in case anything else took the camera back
		local view = RevealCloseUp.cameraAt(stage, pulled(now))
		if hud.rays then
			hud.rays.update(now, view)
		end
		-- Lucky catches shake the camera as the final moment hits, and jolt it as each label lands, dying away quickly.
		local shaking = if cardShown then math.max(1 - (now - cardShownAt) / Reveal.shakeTime, 0) else 0
		local jolting = if now >= joltAt then math.max(1 - (now - joltAt) / Reveal.lucky.joltTime, 0) else 0
		local amount = shakeAngle * shaking * shaking + joltAngle * jolting * jolting
		if drama then
			drama.onClimb(progress)
		end
		-- The camera never stops trembling once a label is up, more and more as the numbers run away.
		if currentTier and not hushed then
			local rumble = impact.rumble[table.find(Reveal.tiers, currentTier) or 1] or 0
			amount += math.rad(rumble) * (0.5 + 0.5 * progress)
		end
		-- Smaller instant zooms on a beat that speeds up, on rare and big catches.
		if drama and not hushed and now >= nextBeat then
			nextBeat = now + impact.beatEvery[1] + (impact.beatEvery[2] - impact.beatEvery[1]) * progress
			if now - zoomAtTime > impact.zoomIn + zoomHold + impact.zoomOut * 0.5 then
				punch(impact.beat[drama.level] or 1)
				joltAt, joltAngle = now, math.rad(impact.beatJolt)
			end
		end
		if amount > 0 then
			local speed = now * impact.rumbleSpeed
			view *= CFrame.Angles(
				amount * math.noise(speed, 1.3),
				amount * math.noise(speed, 7.1),
				amount * 0.6 * math.noise(speed, 4.7)
			)
		end
		camera.CFrame = view
		-- The field of view: the instant zooms, and at the unveil the snap wide easing back as the camera lands.
		local wide = 1
		if cardShown then
			local eased = TweenService:GetValue(math.clamp((now - cardShownAt) / whipLength, 0, 1), Enum.EasingStyle.Quart, Enum.EasingDirection.Out)
			wide = unveilBy + (1 - unveilBy) * eased
		end
		camera.FieldOfView = math.min(fieldOfView * zoomNow(now) * wide, 115)

		if cardShown then
			return
		end

		-- The numbers go up for real: slowly at first, then running away, and the counter grows and trembles with them.
		if showCounter then
			local lucky = Reveal.lucky
			local value = teaser * (catch.oneIn / teaser) ^ (progress ^ lucky.climbPower)
			setCounter(value, progress, false)
			if not hushed then
				hud.pillPop.Scale = 1 + lucky.grow * progress
				hud.pill.Rotation = lucky.shake * progress * progress * math.sin(elapsed * 38)
			end
			local tier = tierFor(value)
			if tier and tier ~= currentTier then
				setTier(tier, true)
			end
		end

		-- A shadow keeps its name back until late.
		local targetLetters = math.floor(progress ^ (if drama then drama.letterPower else 1) * #letterOrder)
		while revealedCount < targetLetters do
			revealedCount += 1
			showLetter(tiles[letterOrder[revealedCount]])
		end

		if progress >= 1 and not hushed then
			hushed = true
			hud.pill.Rotation = 0
			if drama then
				drama.hush()
				punch(impact.lastNumber, 0, drama.hushTime) -- the last number snaps in and holds
				task.delay(drama.hushTime, function()
					if not cardShown then
						showCard(false)
					end
				end)
			else
				showCard(false)
			end
		end
	end)

	done.Event:Wait()
	done:Destroy()
	stepConnection:Disconnect()
	inputConnection:Disconnect()
	ContextActionService:UnbindAction(SKIP_ACTION)

	-- The text goes at once, the screen fades to white, holds, then fades into the player's base.
	hud.final.Visible = false
	hud.top.Visible = false
	hud.letters.Visible = false
	if hud.sticker then
		hud.sticker.Visible = false
	end
	hideSlam()
	hud.flash.BackgroundColor3 = WHITE
	tween(hud.flash, Reveal.whiteIn, { BackgroundTransparency = 0 }).Completed:Wait()
	camera:SetAttribute("WorldFocusZ", nil)
	camera:SetAttribute("HazeScale", nil)
	camera.FieldOfView = fieldOfView
	undoWorld()
	returnHome()
	clearColourMoment()
	for _, glow in hud.glows do
		glow.BackgroundTransparency = 1
	end
	if dust then
		dust.destroy()
	end
	if drama then
		drama.destroy()
	end
	hud.vignette.ImageTransparency = 1
	if dino then
		dino:Destroy()
	end
	if egg.Parent then
		egg:Destroy()
	end
	camera.CameraType = Enum.CameraType.Custom
	task.wait(Reveal.whiteHold)
	tween(hud.flash, Reveal.whiteOut, { BackgroundTransparency = 1 })

	-- Rare enough for the lucky catch banner (LuckyBannerController shows it): no second banner.
	if catch.oneIn >= Reveal.caughtBannerMinOneIn and catch.oneIn < Reveal.luckyBanner.minOneIn then
		local prefix = ""
		if size then
			prefix ..= size.name .. " "
		end
		if mutation then
			prefix ..= mutation.name .. " "
		end
		showCaughtBanner(catch, prefix .. upperName)
	end
end

-- Plays the whole reveal and returns once the player has tapped through it.
-- The egg part is taken over and destroyed here.
function RevealController.play(catch, egg: BasePart)
	playing = true
	local ok, err = pcall(play, catch, egg)
	playing = false
	if not ok then
		-- Never leave the screen black or the monster standing in the corridor.
		hud.black.BackgroundTransparency = 1
		clearColourMoment()
		workspace.CurrentCamera:SetAttribute("WorldFocusZ", nil)
		workspace.CurrentCamera:SetAttribute("HazeScale", nil)
		undoWorld()
		ContextActionService:UnbindAction(SKIP_ACTION)
		if hud.fieldOfView then
			workspace.CurrentCamera.FieldOfView = hud.fieldOfView
		end
		for _, name in { "RevealDino", "RevealDust" } do
			local leftover = workspace:FindFirstChild(name)
			if leftover then
				leftover:Destroy()
			end
		end
		local dark = game:GetService("Lighting"):FindFirstChild("RevealDark")
		if dark then
			dark:Destroy()
		end
		hud.vignette.ImageTransparency = 1
		error(err, 0)
	end
	finishedEvent:Fire(catch)
end

return RevealController
