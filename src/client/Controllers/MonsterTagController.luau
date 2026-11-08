-- Tags floating over the monsters on the bases: its mutations (only when it has some: the colour word in its
-- colour, the size word in silver), its name in white and its $/s in green. They show only while you're on or next
-- to a base, on the few of its monsters nearest to you, so a full base never piles its tags into a heap (docs/GAME_SPEC.md section 4, numbers in Config/Plot
-- `tags`). A giant's tag stops at a ceiling over its feet, so it can be read from its base. Display only: the
-- server puts what each tag says on the monster (PlotService).
-- The monster a player carries on their head has a tag too, with its rarity word under the mutations [Owner,
-- 2026-11-07: "I can't see their name tag and rarity at all while holding it"]: your own always, anywhere, except
-- while it's hidden (aiming, the throw, the reveal, training); other players' when you're within maxDistance.
local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Shared = ReplicatedStorage.Shared
local Catch = require(Shared.Config.Catch)
local DinoLife = require(Shared.Config.DinoLife)
local Plot = require(Shared.Config.Plot)
local DinoStats = require(Shared.DinoStats)
local Format = require(Shared.Format)
local HudStyle = require(Shared.HudStyle)
local UiKit = require(Shared.UiKit)

local RevealController = require(script.Parent.RevealController)
local RarityLabel = require(script.Parent.RarityLabel)

local MonsterTagController = {}

local settings = Plot.tags
local player = Players.LocalPlayer
local WHITE = Color3.new(1, 1, 1)
local PICK_EVERY = 0.2 -- seconds between choosing which monsters show a tag

local holder: Instance = nil -- PlayerGui: billboards draw only as its direct children
-- [model] = { gui, root, scale, height, radius, adornee }
local tags = {}

local function gradient(label: TextLabel, top: Color3, bottom: Color3)
	local g = Instance.new("UIGradient")
	g.Color = ColorSequence.new(top, bottom)
	g.Rotation = 90
	g.Parent = label
end

local function line(parent: Instance, text: string, height: number, order: number): TextLabel
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.FontFace = UiKit.FONT
	label.Text = text
	label.TextSize = height
	label.TextColor3 = WHITE
	label.LayoutOrder = order
	label.Parent = parent
	HudStyle.outline(label, settings.outline)
	return label
end

local function word(parent: Instance, text: string, order: number): TextLabel
	local label = line(parent, text, settings.mutationText, order)
	label.AutomaticSize = Enum.AutomaticSize.X
	label.Size = UDim2.fromOffset(0, settings.mutationText + settings.outline)
	return label
end

local function brightness(color: Color3): number
	return 0.3 * color.R + 0.59 * color.G + 0.11 * color.B
end

local function build(model: Model)
	local gui = Instance.new("BillboardGui")
	gui.Name = "MonsterTag"
	gui.Size = UDim2.fromOffset(settings.size.X, settings.size.Y)
	gui.SizeOffset = Vector2.new(0, 0.5) -- the tag's bottom edge sits on its point, so it grows upwards
	gui.AlwaysOnTop = true -- a giant's tag sits in front of its body, which would hide it
	gui.LightInfluence = 0
	gui.ResetOnSpawn = false
	gui.Enabled = false

	local root = Instance.new("Frame")
	root.BackgroundTransparency = 1
	root.Size = UDim2.fromScale(1, 1)
	root.AnchorPoint = Vector2.new(0.5, 1) -- shrinks with distance towards its bottom middle, its point
	root.Position = UDim2.fromScale(0.5, 1)
	root.Parent = gui
	local scale = Instance.new("UIScale")
	scale.Parent = root
	local list = Instance.new("UIListLayout")
	list.FillDirection = Enum.FillDirection.Vertical
	list.HorizontalAlignment = Enum.HorizontalAlignment.Center
	list.VerticalAlignment = Enum.VerticalAlignment.Bottom
	list.SortOrder = Enum.SortOrder.LayoutOrder
	list.Parent = root

	-- Top line: the mutations, colour first ("GOLD  MEGA CHONK"); none, no line.
	local colour = DinoStats.findOption(Catch.mutations, model:GetAttribute("TagMutation"))
	local size = DinoStats.findOption(Catch.sizes, model:GetAttribute("TagSize"))
	local lines = {}
	local tall = settings.nameText + settings.incomeText + 2 * settings.outline
	if colour or size then
		tall += settings.mutationText + settings.outline
		local row = Instance.new("Frame")
		row.BackgroundTransparency = 1
		row.Size = UDim2.new(1, 0, 0, settings.mutationText + settings.outline)
		row.LayoutOrder = 1
		row.Parent = root
		local rowList = Instance.new("UIListLayout")
		rowList.FillDirection = Enum.FillDirection.Horizontal
		rowList.HorizontalAlignment = Enum.HorizontalAlignment.Center
		rowList.SortOrder = Enum.SortOrder.LayoutOrder
		rowList.Padding = UDim.new(0, settings.mutationText * 0.4)
		rowList.Parent = row
		if colour then
			local label = word(row, colour.name, 1)
			table.insert(lines, label)
			if brightness(colour.color) <= settings.darkBelow then
				gradient(label, colour.color:Lerp(WHITE, settings.darkTop), colour.color:Lerp(WHITE, settings.darkBottom))
			else
				gradient(label, colour.color:Lerp(WHITE, settings.colourLift), colour.color)
			end
		end
		if size then
			local label = word(row, size.name, 2)
			table.insert(lines, label)
			gradient(label, Color3.fromHex(settings.sizeWord[1]), Color3.fromHex(settings.sizeWord[2]))
		end
	end

	-- The carried monster's rarity, in its rarity's colour (TagId is only on carried ones).
	local id = model:GetAttribute("TagId")
	if id then
		-- The animated rarity word (RarityLabel, Config/Rarity).
		local label = RarityLabel.create(root, UiKit.rarityOf(id), settings.rarityText)
		label.Size = UDim2.new(1, 0, 0, settings.rarityText + settings.outline * 2)
		label.LayoutOrder = 2
		table.insert(lines, label:FindFirstChild("Word", true))
		tall += settings.rarityText + settings.outline * 2
	end

	local name = line(root, model:GetAttribute("TagName") or "", settings.nameText, 3)
	name.Size = UDim2.new(1, 0, 0, settings.nameText + settings.outline)
	local income = line(root, `{Format.cash(model:GetAttribute("TagIncome") or 0)}/s`, settings.incomeText, 4)
	income.Size = UDim2.new(1, 0, 0, settings.incomeText + settings.outline)
	gradient(income, Color3.fromHex(settings.income[1]), Color3.fromHex(settings.income[2]))
	table.insert(lines, name)
	table.insert(lines, income)

	-- How tall it stands over its feet (its pivot) and how wide it is, from its shape as placed.
	local pivot = model:GetPivot()
	local box, extents = model:GetBoundingBox()
	local top = box.Position.Y + extents.Y / 2 - pivot.Position.Y
	local gap = settings.headGap
	if id then
		-- The carried one's tag hugs its head: measured from the parts you can see (the invisible root and
		-- hitbox reach higher), with a smaller gap, and drawn smaller (Config/Plot tags carried).
		top = 0
		for _, part in model:GetDescendants() do
			if part:IsA("BasePart") and part.Transparency < 1 then
				local half = part.Size / 2
				local reach = math.abs(part.CFrame.RightVector.Y) * half.X
					+ math.abs(part.CFrame.UpVector.Y) * half.Y
					+ math.abs(part.CFrame.LookVector.Y) * half.Z
				top = math.max(top, part.Position.Y + reach - pivot.Position.Y)
			end
		end
		gap = settings.carried.gap
	end
	local adornee = model.PrimaryPart or model:FindFirstChildWhichIsA("BasePart", true)
	gui.Adornee = adornee
	gui.Parent = holder
	tags[model] = {
		gui = gui,
		scale = scale,
		height = math.min(top + gap, settings.ceiling),
		carried = id ~= nil,
		radius = math.min(extents.X, extents.Z) / 2,
		adornee = adornee,
		lines = lines,
		tall = tall, -- pixels its lines fill, up close
	}
end

-- Models whose parts changed since their tag was built, so it's built again on the next pick.
local stale = {}

local function add(model: Instance)
	if tags[model] or not model:IsA("Model") or not model:GetAttribute("TagName") then
		return
	end
	build(model)
	-- Another player's carried monster can reach this screen before its body does (their character streams in part
	-- by part), which left a tag with nothing to hang on and no height, never shown [Owner, 2026-11-08: "I can't
	-- see the monster name tag on this other player"]. A part arriving later builds it again, measured.
	tags[model].watch = model.DescendantAdded:Connect(function(child)
		if child:IsA("BasePart") then
			stale[model] = true
		end
	end)
end

local function remove(model: Instance)
	local tag = tags[model]
	if tag then
		tag.gui:Destroy()
		tag.watch:Disconnect()
		tags[model] = nil
	end
	stale[model] = nil
end

local function rebuildStale()
	for model in stale do
		stale[model] = nil
		if tags[model] then
			remove(model)
			add(model)
		end
	end
end

-- Turns on the tags of the few monsters nearest to you, within reach, and off all the others.
local shown = {}
local order = {} -- the shown ones, nearest first
local function pick()
	local character = player.Character
	local body = character and character:FindFirstChild("HumanoidRootPart")
	local nearby = {}
	-- The base you're on or next to, if any.
	local plotIndex = nil
	if body then
		for index, centre in Plot.positions do
			local offset = body.Position - centre
			if
				math.abs(offset.X) <= Plot.size.X / 2 + settings.plotMargin
				and math.abs(offset.Z) <= Plot.size.Z / 2 + settings.plotMargin
			then
				plotIndex = index
				break
			end
		end
	end
	if plotIndex and not RevealController.isPlaying() then
		local here = body.Position * Vector3.new(1, 0, 1)
		for model, tag in tags do
			if
				model.Parent
				and tag.adornee
				and tag.adornee.Parent
				and model:GetAttribute("PlotIndex") == plotIndex
				and not model:GetAttribute("HiddenForMe") -- the player switched other players' dinos off (SettingsController)
			then
				local feet = model:GetPivot().Position * Vector3.new(1, 0, 1)
				local distance = math.max((feet - here).Magnitude - tag.radius, 0)
				table.insert(nearby, { model = model, distance = distance })
			end
		end
		table.sort(nearby, function(a, b)
			return a.distance < b.distance
		end)
	end
	-- Carried monsters: your own (nearest of all), and other players' within reach.
	local hidden = RevealController.isPlaying()
		or workspace.CurrentCamera.CameraType == Enum.CameraType.Scriptable
		or player:GetAttribute("IsTraining") == true
	for model, tag in tags do
		if model:GetAttribute("Carried") and model.Parent and tag.adornee and tag.adornee.Parent then
			if model.Parent == character then
				if not hidden then
					table.insert(nearby, 1, { model = model, distance = 0, carried = true })
				end
			elseif body and not RevealController.isPlaying() then
				local distance = (model:GetPivot().Position - body.Position).Magnitude
				if distance <= settings.maxDistance then
					table.insert(nearby, { model = model, distance = distance, carried = true })
				end
			end
		end
	end

	local keep = {}
	order = {}
	local onBase = 0
	for index = 1, #nearby do
		local model = nearby[index].model
		if not nearby[index].carried then
			onBase += 1
			if onBase > settings.nearest then
				continue
			end
		end
		table.insert(order, model)
		local tag = tags[model]
		keep[model] = true
		tag.gui.Enabled = true
		tag.scale.Scale = (1 - (1 - settings.farScale) * math.min(nearby[index].distance / settings.maxDistance, 1))
			* (if tag.carried then settings.carried.scale else 1)
	end
	for model in shown do
		if not keep[model] and tags[model] then
			tags[model].gui.Enabled = false
		end
	end
	shown = keep
end

-- How wide a tag's text is on screen, in pixels.
local function widthOf(tag): number
	local widest = 0
	for _, label in tag.lines do
		widest = math.max(widest, label.TextBounds.X)
	end
	return (widest + 2 * settings.outline) * tag.scale.Scale
end

-- Keeps each shown tag over its monster's head (or at the ceiling) as the monster walks and sways. Where two
-- tags would overlap on screen, the further monster's tag is lifted above the nearer one's.
local function follow()
	local camera = workspace.CurrentCamera
	local placed = {}
	for _, model in order do
		local tag = tags[model]
		if tag and model.Parent and tag.adornee then
			local point = model:GetPivot().Position + Vector3.new(0, tag.height, 0)
			tag.gui.StudsOffsetWorldSpace = point - tag.adornee.Position
			local screen = camera:WorldToViewportPoint(point)
			local width, tall = widthOf(tag), tag.tall * tag.scale.Scale
			local bottom = screen.Y
			local moved = true
			while moved do
				moved = false
				for _, other in placed do
					local apart = math.abs(screen.X - other.x) >= (width + other.width) / 2
					if not apart and bottom > other.top and bottom - tall < other.bottom then
						bottom = other.top
						moved = true
					end
				end
			end
			tag.gui.SizeOffset = Vector2.new(0, 0.5 + (screen.Y - bottom) / settings.size.Y)
			table.insert(placed, { x = screen.X, width = width, top = bottom - tall, bottom = bottom })
		end
	end
end

function MonsterTagController.start()
	holder = player:WaitForChild("PlayerGui")

	for _, model in CollectionService:GetTagged(DinoLife.tag) do
		task.defer(add, model)
	end
	CollectionService:GetInstanceAddedSignal(DinoLife.tag):Connect(function(model)
		-- Waits a frame so a model that's still arriving has its parts.
		task.defer(add, model)
	end)
	CollectionService:GetInstanceRemovedSignal(DinoLife.tag):Connect(remove)

	local since = 0
	RunService.Heartbeat:Connect(function(dt)
		since += dt
		if since >= PICK_EVERY then
			since = 0
			rebuildStale()
			pick()
		end
	end)
	RunService.RenderStepped:Connect(follow)
end

return MonsterTagController
