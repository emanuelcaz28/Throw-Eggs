-- The server's best monster (Config/BestCatch): the highest-$/s monster on the base of anyone in the server, on the
-- pedestal beside the leaderboards. The monster stands on the cushion at twice its map's standard size whatever
-- its size mutation, with a card of its stats at its side (Figma "Throw Eggs - Pop-up Text", "Best monster stats"). It changes whenever a base changes or its owner leaves; a title with
-- the owner's headshot floats over it.
local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BestCatch = require(ReplicatedStorage.Shared.Config.BestCatch)
local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local DinoLife = require(ReplicatedStorage.Shared.Config.DinoLife)
local DinoModel = require(ReplicatedStorage.Shared.DinoModel)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)
local Format = require(ReplicatedStorage.Shared.Format)
local Roles = require(ReplicatedStorage.Shared.Roles)
local UiKit = require(ReplicatedStorage.Shared.UiKit)
local World = require(ReplicatedStorage.Shared.World)
local PlayerData = require(script.Parent.PlayerData)
local PlotService = require(script.Parent.PlotService)

local BestCatchService = {}

local GOLD = { "ffe066", "ff9a1f" }
local ODDS = Color3.fromRGB(255, 122, 217)
local STONE = Color3.fromRGB(143, 151, 171)
local CUSHION = Color3.fromRGB(106, 47, 163)

local folder: Folder
local standPoint: CFrame -- the cushion's middle, facing the bases
local best = nil -- { oneIn, statue } of the catch on show
local face -- the stats card
local title -- the title over the monster

-- Props that face a certain way carry a "Front" part: where it lies from the pivot shows which way the import
-- left it facing. The marker is removed.
local function frontOf(model: Model): Vector3?
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") and Roles.of(part) == "Front" then
			local offset = model:GetPivot():PointToObjectSpace(part.Position)
			part:Destroy()
			if Vector2.new(offset.X, offset.Z).Magnitude > 0.01 then
				return Vector3.new(offset.X, 0, offset.Z)
			end
		end
	end
	return nil
end

-- The pedestal: the Blender model if it's been imported, or a plain stone drum with a cushion. An import from
-- before the sign was taken off (2026-11-05) still has its screen and posts, so those are removed here.
local OLD_SIGN_ROLES = { Screen = true, Wood = true, WoodDark = true }
local function buildPedestal()
	local position, facing = BestCatch.position, BestCatch.facing
	local maps = ReplicatedStorage:FindFirstChild("Assets") and ReplicatedStorage.Assets:FindFirstChild("Maps")
	local source = maps
	for _, name in BestCatch.modelFolder do
		source = source and source:FindFirstChild(name)
	end
	local template = source and source:FindFirstChild(BestCatch.modelName)
	if template then
		local model = template:Clone() :: Model
		model.Name = "Pedestal"
		for _, part in model:GetDescendants() do
			if part:IsA("BasePart") then
				part.Anchored = true
				part.CanTouch = false
				if OLD_SIGN_ROLES[Roles.of(part)] then
					part:Destroy()
				end
			end
		end
		Roles.lightUp(model)
		local front = frontOf(model) or Vector3.new(0, 0, -1)
		local turn = math.atan2(facing.X, facing.Z) - math.atan2(front.X, front.Z)
		model:PivotTo(CFrame.new(position) * CFrame.Angles(0, turn, 0))
		model.Parent = folder
		return
	end
	local model = Instance.new("Model")
	model.Name = "Pedestal"
	model.Parent = folder
	local upright = CFrame.Angles(0, 0, math.pi / 2)
	local drum = World.makePart(model, "Stone", Vector3.new(4.2, 14.8, 14.8), CFrame.new(position + Vector3.new(0, 2.1, 0)) * upright, STONE)
	drum.Shape = Enum.PartType.Cylinder
	local top = World.makePart(model, "Top", Vector3.new(0.4, 14.4, 14.4), CFrame.new(position + Vector3.new(0, BestCatch.standHeight - 0.2, 0)) * upright, CUSHION)
	top.Shape = Enum.PartType.Cylinder
end

local function outline(label: TextLabel, thickness: number)
	local stroke = Instance.new("UIStroke")
	stroke.Color = UiKit.INK
	stroke.Thickness = thickness
	stroke.LineJoinMode = Enum.LineJoinMode.Round
	stroke.Parent = label
end

local function text(parent: Instance, position: UDim2, size: UDim2, color: Color3, stroke: number): TextLabel
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.FontFace = UiKit.FONT
	label.AnchorPoint = Vector2.new(0.5, 0)
	label.Position, label.Size = position, size
	label.TextScaled = true
	label.TextColor3 = color
	label.RichText = true
	label.Parent = parent
	if stroke > 0 then
		outline(label, stroke)
	end
	return label
end

-- A see-through panel fixed in the world, facing the way the pedestal does, with a SurfaceGui of this many
-- pixels on it: the title and the stats card stand beside the monster as part of the map.
local function worldPanel(name: string, pixels: Vector2, pixelsPerStud: number): (Part, SurfaceGui)
	local panel = World.makePart(folder, name, Vector3.new(pixels.X / pixelsPerStud, pixels.Y / pixelsPerStud, 0.05), standPoint, UiKit.PANEL)
	panel.Transparency = 1
	panel.CanCollide = false
	panel.CanQuery = false
	panel.CanTouch = false
	panel.CastShadow = false
	local gui = Instance.new("SurfaceGui")
	gui.Face = Enum.NormalId.Front
	gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	gui.PixelsPerStud = pixelsPerStud
	gui.LightInfluence = 0 -- lit from inside, so it reads in the shade too
	gui.MaxDistance = BestCatch.panelMaxDistance
	gui.Parent = panel
	return panel, gui
end


-- The stats beside the monster (Figma "Best monster stats"): clean outlined text, no card and no labels: the
-- mutation and size, the monster's name, its $/s, its odds and its world.
local STATS = Vector2.new(360, 270)
local function buildStats()
	local panel, gui = worldPanel("StatsPanel", STATS, BestCatch.statsPixelsPerStud)
	local function line(y: number, height: number, color: Color3, stroke: number): TextLabel
		return text(gui, UDim2.fromOffset(STATS.X / 2, y), UDim2.fromOffset(STATS.X - 8, height), color, stroke)
	end
	local extras = line(0, 30, Color3.fromRGB(235, 242, 255), 3)
	local name = line(32, 58, Color3.new(1, 1, 1), 5)
	UiKit.gradient(name, GOLD)
	name.BackgroundTransparency = 1
	face = {
		panel = panel,
		gui = gui,
		extras = extras,
		name = name,
		income = line(100, 48, UiKit.CASH, 4),
		odds = line(156, 48, ODDS, 4),
		world = line(212, 48, Color3.fromRGB(170, 130, 255), 4),
	}
end

local function showEmpty()
	face.gui.Enabled = false
	title.gui.Enabled = false
end

-- The title over the monster (Figma "Best monster title"): a gold "SERVER'S BEST MONSTER", then a dark pill with
-- the owner's headshot, name, and the monster with its $/s. On a see-through panel fixed in the world, facing the
-- way the pedestal does, so it's part of the map and not a label stuck to the screen.
local TITLE = Vector2.new(640, 230) -- the Figma frame's design pixels, without its empty bottom

-- A position or size on the title, in its design pixels, as a share of it (a billboard measured in studs).
local function onTitle(x: number, y: number): UDim2
	return UDim2.fromScale(x / TITLE.X, y / TITLE.Y)
end

-- The title over the monster (Figma "Best monster title"): a gold "SERVER'S BEST MONSTER" over the owner's
-- headshot, name and monster, as clean outlined text. It turns to face whoever looks at it, so it reads from the
-- side too, and it's measured in studs, so it stays in proportion with the monster at any distance.
local function buildTitle()
	local anchor = World.makePart(folder, "TitleAnchor", Vector3.one, standPoint, UiKit.PANEL)
	anchor.Transparency = 1
	anchor.CanCollide = false
	anchor.CanQuery = false
	anchor.CanTouch = false
	local gui = Instance.new("BillboardGui")
	gui.Size = UDim2.fromScale(BestCatch.titleWidth, BestCatch.titleWidth * TITLE.Y / TITLE.X)
	gui.LightInfluence = 0
	gui.MaxDistance = BestCatch.panelMaxDistance
	gui.Adornee = anchor
	gui.Parent = anchor

	local heading = text(gui, onTitle(320, 6), onTitle(600, 60), Color3.new(1, 1, 1), 6)
	heading.Text = "👑 SERVER'S BEST MONSTER"
	UiKit.gradient(heading, GOLD)
	heading.BackgroundTransparency = 1

	local avatar = Instance.new("ImageLabel")
	avatar.Position = onTitle(110, 100)
	avatar.SizeConstraint = Enum.SizeConstraint.RelativeYY
	avatar.Size = UDim2.fromScale(110 / TITLE.Y, 110 / TITLE.Y)
	avatar.BackgroundColor3 = Color3.fromRGB(159, 210, 255)
	avatar.Parent = gui
	local round = Instance.new("UICorner")
	round.CornerRadius = UDim.new(0.5, 0)
	round.Parent = avatar
	UiKit.stroke(avatar, 5, Color3.fromRGB(255, 201, 60))
	local owner = text(gui, onTitle(432, 104), onTitle(400, 56), Color3.new(1, 1, 1), 5)
	owner.TextXAlignment = Enum.TextXAlignment.Left
	local monster = text(gui, onTitle(432, 164), onTitle(400, 38), UiKit.CASH, 3)
	monster.TextXAlignment = Enum.TextXAlignment.Left
	title = { panel = anchor, gui = gui, avatar = avatar, owner = owner, monster = monster }
end

local biomeOf = {}
for _, biome in Biomes do
	for _, dino in Dinos[biome.id] or {} do
		biomeOf[dino.id] = biome
	end
end

-- Turns the statue so its head points the way the pedestal faces. Most imports face their pivot's +Z, a few
-- -Z (as in DinoLifeController), told apart by where the head is against the tail. A CFrame looks down its own -Z,
-- so a +Z-facing model is turned round.
local function faceForward(statue: Model)
	local front, back = nil, nil
	for _, bone in statue:GetDescendants() do
		if bone:IsA("Bone") then
			if bone.Name == "Jaw" or (bone.Name == "Head" and not front) then
				front = bone
			end
			if bone.Name == "Tail1" or ((bone.Name == "Spine" or bone.Name == "Swim") and not back) then
				back = bone
			end
		end
	end
	local pivot = statue:GetPivot()
	local headAhead = front and back and pivot:PointToObjectSpace(front.WorldPosition).Z > pivot:PointToObjectSpace(back.WorldPosition).Z
	statue:PivotTo(standPoint * (if headAhead then CFrame.Angles(0, math.pi, 0) else CFrame.identity))
end

local function show(player: Player, entry, stats)
	if best and best.statue then
		best.statue:Destroy()
	end
	local statue = DinoModel.build(entry.id, entry.mutation, Vector3.zero, DinoStats.standardScale(entry.id) * BestCatch.monsterScale)
	statue.Name = "BestMonster"
	statue.ModelStreamingMode = Enum.ModelStreamingMode.Atomic
	faceForward(statue)
	statue:SetAttribute("Stay", true) -- DinoLifeController: idles and roars in place
	CollectionService:AddTag(statue, DinoLife.tag)
	statue.Parent = folder
	best = { player = player, entry = entry, statue = statue }

	local mutation = DinoStats.findOption(Catch.mutations, entry.mutation)
	local size = DinoStats.findOption(Catch.sizes, entry.size)
	local words = {}
	if mutation then
		table.insert(words, `<font color="#{mutation.color:ToHex()}">{mutation.name}</font>`)
	end
	if size then
		table.insert(words, size.name)
	end
	face.extras.Text = table.concat(words, " · ")
	face.extras.Visible = #words > 0
	face.name.Text = stats.name
	face.odds.Text = `1 in {Format.short(stats.oneIn)}`
	face.income.Text = `{Format.cash(stats.income)}/s`
	local biome = biomeOf[entry.id]
	face.world.Text = if biome then biome.name else "?"

	-- The title floats just over the monster's head.
	-- The title floats just over the monster's head; the card stands at its right as you face it (the standPoint's
	-- -X), its foot on the cushion.
	local _, bounds = statue:GetBoundingBox()
	title.panel.CFrame = standPoint * CFrame.new(0, bounds.Y + title.gui.Size.Y.Scale / 2 + BestCatch.titleGap, 0)
	local half = bounds.X / 2 -- its width as you face it (the pedestal faces +Z)
	face.panel.CFrame = standPoint * CFrame.new(-(half + face.panel.Size.X / 2 + BestCatch.statsGap), face.panel.Size.Y / 2, 0)
	face.gui.Enabled = true
	title.owner.Text = player.DisplayName
	title.monster.Text = `{if mutation then mutation.name .. " " else ""}{stats.name}`
	title.avatar.Image = ""
	task.spawn(function()
		local ok, image = pcall(Players.GetUserThumbnailAsync, Players, player.UserId, Enum.ThumbnailType.HeadShot, Enum.ThumbnailSize.Size150x150)
		if ok and best and best.player == player then
			title.avatar.Image = image
		end
	end)
	title.gui.Enabled = true
end

-- Finds the best monster (highest $/s) on the bases of the players in the server and puts it on show.
local function refresh()
	local bestPlayer, bestEntry, bestStats = nil, nil, nil
	for _, player in Players:GetPlayers() do
		local data = PlayerData.get(player)
		for _, entry in (if data then PlotService.plotted(data) else {}) do
			local stats = DinoStats.describe(entry)
			if stats and (not bestStats or stats.income > bestStats.income) then
				bestPlayer, bestEntry, bestStats = player, entry, stats
			end
		end
	end
	if best and bestEntry and best.player == bestPlayer and best.entry.id == bestEntry.id
		and best.entry.mutation == bestEntry.mutation and best.entry.size == bestEntry.size then
		return -- the same monster: leave it standing
	end
	if bestEntry then
		show(bestPlayer, bestEntry, bestStats)
	else
		if best and best.statue then
			best.statue:Destroy()
		end
		best = nil
		showEmpty()
	end
end

function BestCatchService.start()
	folder = Instance.new("Folder")
	folder.Name = "BestCatch"
	folder.Parent = workspace
	local position = BestCatch.position + Vector3.new(0, BestCatch.standHeight, 0)
	standPoint = CFrame.lookAt(position, position + BestCatch.facing)
	buildPedestal()
	buildStats()
	buildTitle()
	showEmpty()
	PlotService.onPlotChanged(refresh)
	Players.PlayerRemoving:Connect(function()
		task.defer(refresh)
	end)
end

return BestCatchService
