-- The three leaderboards in the arena, the Blender boards from assets/models/build_leaderboards.py. Every
-- minute each player's scores are saved to an OrderedDataStore (one per board) and the top lists are read
-- back and drawn on the boards' screens.
-- If the stores can't be reached (Studio without API access), the boards show the players in
-- this server instead.
local DataStoreService = game:GetService("DataStoreService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)
local Leaderboards = require(ReplicatedStorage.Shared.Config.Leaderboards)
local PlayerData = require(script.Parent.PlayerData)
local Roles = require(ReplicatedStorage.Shared.Roles)
local World = require(ReplicatedStorage.Shared.World)

local LeaderboardService = {}

local FIRST_UPDATE_DELAY = 5 -- seconds after the server starts
local LOG_SCALE = 1e6 -- huge values are stored as log10 * this, since stores only keep whole numbers
-- The HUD's look (UiKit, which is client only): chunky Fredoka One with a thick ink outline on dark purple panels.
local FONT = Font.new("rbxasset://fonts/families/FredokaOne.json")
local INK = Color3.fromRGB(27, 18, 48)
local PANEL = Color3.fromRGB(31, 26, 51)
local PANEL_TOP = Color3.fromRGB(52, 42, 86)
local ROW = Color3.fromRGB(43, 36, 72)
local EMPTY_ROW = Color3.fromRGB(37, 31, 62)
local TEXT = Color3.new(1, 1, 1)
local MUTED = Color3.fromRGB(203, 191, 240)
local PIXELS_PER_STUD = 48

local boardLists: { [string]: Frame } = {} -- each board's list of rows
local lastWritten: { [number]: { [string]: number } } = {}
local names: { [number]: string } = {}

local function encode(board, value: number): number
	if board.kind == "count" then
		return math.floor(value)
	end
	return if value >= 1 then math.floor(math.log10(value) * LOG_SCALE) else 0
end

local function decode(board, stored: number): number
	if board.kind == "count" then
		return stored
	end
	-- Rounded, since the stored log is cut a hair short (400 would come back as 399.9997).
	return if stored > 0 then math.round(10 ^ (stored / LOG_SCALE)) else 0
end

local function valueText(board, value: number): string
	if board.kind == "cash" then
		return Format.cash(value)
	elseif board.kind == "oneIn" then
		return `1 in {Format.short(value)}`
	end
	return Format.commas(value)
end

local function nameOf(userId: number): string
	if names[userId] then
		return names[userId]
	end
	local player = Players:GetPlayerByUserId(userId)
	if player then
		names[userId] = player.Name
		return player.Name
	end
	local ok, name = pcall(function()
		return Players:GetNameFromUserIdAsync(userId)
	end)
	names[userId] = if ok then name else "Someone"
	return names[userId]
end

local function makeText(parent: Instance, color: Color3, position: UDim2, size: UDim2, align: Enum.TextXAlignment, outline: number): TextLabel
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.FontFace = FONT
	label.Position = position
	label.Size = size
	label.TextColor3 = color
	label.TextScaled = true
	label.TextXAlignment = align
	label.Text = ""
	label.Parent = parent
	if outline > 0 then
		local stroke = Instance.new("UIStroke")
		stroke.Color = INK
		stroke.Thickness = outline
		stroke.LineJoinMode = Enum.LineJoinMode.Round
		stroke.Parent = label
	end
	return label
end

local function corner(parent: Instance, radius: UDim)
	local uiCorner = Instance.new("UICorner")
	uiCorner.CornerRadius = radius
	uiCorner.Parent = parent
end

local function outline(parent: Instance, thickness: number)
	local stroke = Instance.new("UIStroke")
	stroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	stroke.Color = INK
	stroke.Thickness = thickness
	stroke.Parent = parent
end

local function darker(color: Color3, amount: number): Color3
	return color:Lerp(Color3.new(0, 0, 0), amount)
end

-- How far a part reaches along a direction, from its middle to its edge.
local function reach(part: BasePart, direction: Vector3): number
	local cf, size = part.CFrame, part.Size
	return (math.abs(cf.RightVector:Dot(direction)) * size.X + math.abs(cf.UpVector:Dot(direction)) * size.Y
		+ math.abs(cf.LookVector:Dot(direction)) * size.Z) / 2
end

-- A see-through sheet over the front of a part, for a SurfaceGui: the gui can then face the right way
-- whatever way the importer left the part's own faces.
local function sheetOver(parent: Instance, part: BasePart, facing: Vector3, name: string, forward: number?): Part
	local right = Vector3.yAxis:Cross(facing).Unit * -1
	local width, height = reach(part, right) * 2, reach(part, Vector3.yAxis) * 2
	local centre = part.Position + facing * (reach(part, facing) + 0.03 + (forward or 0))
	local sheet = World.makePart(parent, name, Vector3.new(width, height, 0.05), CFrame.lookAt(centre, centre + facing), PANEL)
	sheet.Transparency = 1
	sheet.CanCollide = false
	sheet.CanQuery = false
	sheet.CanTouch = false
	sheet.CastShadow = false
	return sheet
end

local function surfaceGui(sheet: BasePart): SurfaceGui
	local gui = Instance.new("SurfaceGui")
	gui.Face = Enum.NormalId.Front
	gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	gui.PixelsPerStud = PIXELS_PER_STUD / Leaderboards.scale -- smaller boards keep the same layout
	gui.LightInfluence = 0 -- lit from inside, like a screen, so it reads in the shade too
	gui.MaxDistance = 260
	gui.Parent = sheet
	return gui
end

-- Props that face a certain way carry a "Front" part (as in MapDecor): where it lies from the pivot shows
-- which way the import left the board facing. The marker is removed.
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

local function partByRole(model: Model, role: string): BasePart?
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") and Roles.of(part) == role then
			return part
		end
	end
	return nil
end

-- The board's body: the Blender board if it's been imported, or two plain parts. Returns its screen and its
-- header, the parts the text goes on.
local function buildBody(parent: Instance, board, position: Vector3, facing: Vector3): (BasePart, BasePart)
	local maps = ReplicatedStorage:FindFirstChild("Assets") and ReplicatedStorage.Assets:FindFirstChild("Maps")
	local folder = maps
	for _, name in Leaderboards.modelFolder do
		folder = folder and folder:FindFirstChild(name)
	end
	local template = folder and folder:FindFirstChild(`board_{board.id}`)
	if template then
		local model = template:Clone() :: Model
		model:ScaleTo(Leaderboards.scale)
		model.Name = board.id
		for _, part in model:GetDescendants() do
			if part:IsA("BasePart") then
				part.Anchored = true
				part.CanTouch = false
			end
		end
		Roles.lightUp(model)
		local front = frontOf(model) or Vector3.new(0, 0, -1)
		local turn = math.atan2(facing.X, facing.Z) - math.atan2(front.X, front.Z)
		model:PivotTo(CFrame.new(position) * CFrame.Angles(0, turn, 0))
		model.Parent = parent
		local screen, header = partByRole(model, "Screen"), partByRole(model, "Header")
		if screen and header then
			return screen, header
		end
		warn(`[LeaderboardService] board_{board.id} has no Screen or Header part`)
		model:Destroy()
	end
	local size = Leaderboards.size * Leaderboards.scale
	local model = Instance.new("Model")
	model.Name = board.id
	model.Parent = parent
	local look = CFrame.lookAt(position, position + facing)
	local screen = World.makePart(model, "Screen", Vector3.new(size.X, size.Y * 0.84, size.Z), look * CFrame.new(0, size.Y * 0.42, 0), PANEL)
	local header = World.makePart(model, "Header", Vector3.new(size.X, size.Y * 0.16, size.Z), look * CFrame.new(0, size.Y * 0.92, 0), board.color)
	return screen, header
end

local function buildBoard(parent: Instance, board, placement)
	local yaw = math.rad(placement.yaw)
	local facing = Vector3.new(math.sin(yaw), 0, math.cos(yaw))
	local screen, header = buildBody(parent, board, placement.position, facing)
	local holder = screen.Parent

	-- The title on the header plaque.
	-- In front of the plaque's gold bands and bulbs (0.3 out), the text kept between the two bands.
	local titleGui = surfaceGui(sheetOver(holder, header, facing, "TitleSheet", 0.3))
	local title = makeText(titleGui, TEXT, UDim2.fromScale(0.06, 0.14), UDim2.fromScale(0.88, 0.48), Enum.TextXAlignment.Center, 6)
	title.Text = board.title
	local subtitle = makeText(titleGui, TEXT, UDim2.fromScale(0.14, 0.62), UDim2.fromScale(0.72, 0.22), Enum.TextXAlignment.Center, 3)
	subtitle.Text = board.subtitle
	subtitle.TextColor3 = board.color:Lerp(Color3.new(1, 1, 1), 0.75)

	-- The top 10 on the screen.
	local gui = surfaceGui(sheetOver(holder, screen, facing, "ListSheet"))
	local panel = Instance.new("Frame")
	panel.Size = UDim2.fromScale(1, 1)
	panel.BackgroundColor3 = TEXT
	panel.BorderSizePixel = 0
	panel.Parent = gui
	local shade = Instance.new("UIGradient")
	shade.Color = ColorSequence.new(PANEL_TOP, PANEL)
	shade.Rotation = 90
	shade.Parent = panel

	local list = Instance.new("Frame")
	list.Name = "List"
	list.BackgroundTransparency = 1
	list.Position = UDim2.fromScale(0.04, 0.035)
	list.Size = UDim2.fromScale(0.92, 0.88)
	list.Parent = panel
	local layout = Instance.new("UIListLayout")
	layout.Padding = UDim.new(0.012, 0)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = list

	local valueColor = Leaderboards.valueColors[board.kind] or TEXT
	for rank = 1, Leaderboards.rows do
		local medal = Leaderboards.medals[rank]
		local row = Instance.new("Frame")
		row.Name = `Row{rank}`
		row.LayoutOrder = rank
		row.Size = UDim2.fromScale(1, 0.088)
		row.BackgroundColor3 = medal or ROW
		row.Parent = list
		corner(row, UDim.new(0.32, 0))
		outline(row, 3)
		if medal then -- a shine across the top half
			local gloss = Instance.new("UIGradient")
			gloss.Color = ColorSequence.new({
				ColorSequenceKeypoint.new(0, Color3.new(1, 1, 1)),
				ColorSequenceKeypoint.new(0.5, Color3.new(1, 1, 1)),
				ColorSequenceKeypoint.new(0.51, Color3.fromRGB(215, 215, 215)),
				ColorSequenceKeypoint.new(1, Color3.fromRGB(215, 215, 215)),
			})
			gloss.Rotation = 90
			gloss.Parent = row
		end

		local badge = Instance.new("Frame")
		badge.Name = "Badge"
		badge.AnchorPoint = Vector2.new(0, 0.5)
		badge.Position = UDim2.fromScale(0.015, 0.5)
		badge.Size = UDim2.fromScale(0.86, 0.86)
		badge.SizeConstraint = Enum.SizeConstraint.RelativeYY
		badge.BackgroundColor3 = if medal then darker(medal, 0.35) else INK
		badge.Parent = row
		corner(badge, UDim.new(0.5, 0))
		outline(badge, 2)
		local rankLabel = makeText(badge, TEXT, UDim2.fromScale(0.1, 0.12), UDim2.fromScale(0.8, 0.76), Enum.TextXAlignment.Center, 2)
		rankLabel.Text = tostring(rank)

		local headshot = Instance.new("ImageLabel")
		headshot.Name = "Headshot"
		headshot.AnchorPoint = Vector2.new(0, 0.5)
		headshot.Position = UDim2.fromScale(0.105, 0.5)
		headshot.Size = UDim2.fromScale(0.82, 0.82)
		headshot.SizeConstraint = Enum.SizeConstraint.RelativeYY
		headshot.BackgroundColor3 = PANEL_TOP
		headshot.Parent = row
		corner(headshot, UDim.new(0.5, 0))
		outline(headshot, 2)

		local nameLabel = makeText(row, TEXT, UDim2.fromScale(0.2, 0.17), UDim2.fromScale(0.47, 0.66), Enum.TextXAlignment.Left, 2.5)
		nameLabel.Name = "PlayerName"
		local value = makeText(row, valueColor, UDim2.fromScale(0.66, 0.17), UDim2.fromScale(0.32, 0.66), Enum.TextXAlignment.Right, 2.5)
		value.Name = "Value"
	end

	local footer = makeText(panel, MUTED, UDim2.fromScale(0.05, 0.935), UDim2.fromScale(0.9, 0.045), Enum.TextXAlignment.Center, 0)
	local interval = Leaderboards.updateInterval
	footer.Text = if interval == 60 then "Updates every minute" else `Updates every {interval} seconds`

	boardLists[board.id] = list
end

local function storeFor(board): OrderedDataStore
	return DataStoreService:GetOrderedDataStore(`Leaderboard_v{Leaderboards.storeVersion}_{board.id}`)
end

-- UserIds kept off the boards (Leaderboards.hiddenNames), filled at start.
local hidden: { [number]: boolean } = {}

local function loadHidden()
	for _, name in Leaderboards.hiddenNames or {} do
		local ok, userId = pcall(Players.GetUserIdFromNameAsync, Players, name)
		if ok and userId then
			hidden[userId] = true
			for _, board in Leaderboards.boards do
				pcall(function()
					storeFor(board):RemoveAsync(tostring(userId))
				end)
			end
		else
			warn(`[LeaderboardService] Couldn't find hidden player {name}`)
		end
	end
end

-- Saves scores that changed since the last write.
local function writeScores()
	for _, player in Players:GetPlayers() do
		local data = PlayerData.get(player)
		if data and not PlayerData.isTestSave(player) and not hidden[player.UserId] then -- a Studio test save would overwrite the real scores
			local written = lastWritten[player.UserId] or {}
			lastWritten[player.UserId] = written
			for _, board in Leaderboards.boards do
				local value = encode(board, data[board.stat])
				if value > 0 and written[board.id] ~= value then
					local ok, err = pcall(function()
						storeFor(board):SetAsync(tostring(player.UserId), value)
					end)
					if ok then
						written[board.id] = value
					else
						warn(`[LeaderboardService] Couldn't save {board.id} for {player.Name}: {err}`)
					end
				end
			end
		end
	end
end

-- The top entries as { userId, value }, best first. Falls back to this server's players.
local function readTop(board): { { userId: number, value: number } }
	local ok, page = pcall(function()
		return storeFor(board):GetSortedAsync(false, Leaderboards.rows):GetCurrentPage()
	end)
	local top = {}
	if ok then
		for _, item in page do
			local userId = tonumber(item.key)
			if userId and not hidden[userId] then
				table.insert(top, { userId = userId, value = decode(board, item.value) })
			end
		end
		return top
	end
	for _, player in Players:GetPlayers() do
		local data = PlayerData.get(player)
		if data and data[board.stat] > 0 and not hidden[player.UserId] then
			table.insert(top, { userId = player.UserId, value = data[board.stat] })
		end
	end
	table.sort(top, function(a, b)
		return a.value > b.value
	end)
	return top
end

-- Every rank always shows, so the board looks full: empty ones are dimmed placeholders.
local function drawBoard(board, top)
	local list = boardLists[board.id]
	for rank = 1, Leaderboards.rows do
		local row = list[`Row{rank}`]
		local entry = top[rank]
		local medal = Leaderboards.medals[rank]
		row.BackgroundColor3 = if entry then medal or ROW else EMPTY_ROW
		row.Badge.BackgroundColor3 = if entry and medal then darker(medal, 0.35) else INK
		row.Headshot.Visible = entry ~= nil
		row.PlayerName.TextTransparency = if entry then 0 else 0.6
		if entry then
			row.PlayerName.Text = nameOf(entry.userId)
			row.Value.Text = valueText(board, entry.value)
			row.Headshot.Image = `rbxthumb://type=AvatarHeadShot&id={entry.userId}&w=48&h=48`
		else
			row.PlayerName.Text = "- - -"
			row.Value.Text = ""
		end
	end
end

local function refresh()
	writeScores()
	for _, board in Leaderboards.boards do
		drawBoard(board, readTop(board))
	end
end

-- Saves from before the leaderboards get their stats estimated from what they own, once.
local function onLoaded(player: Player, data)
	-- A reset save (Config/Save resets) comes off the boards; its new scores go back on as they're earned.
	if player:GetAttribute("SaveWasReset") then
		task.spawn(function()
			for _, board in Leaderboards.boards do
				local ok, err = pcall(function()
					storeFor(board):RemoveAsync(tostring(player.UserId))
				end)
				if not ok then
					warn(`[LeaderboardService] Couldn't clear {board.id} for {player.Name}: {err}`)
				end
			end
		end)
	end
	if data.statsStarted then
		return
	end
	data.statsStarted = true
	data.totalCaught = math.max(data.totalCaught, #data.dinos)
	data.totalEarned = math.max(data.totalEarned, data.cash)
	for _, entry in data.dinos do
		local stats = DinoStats.describe(entry)
		if stats then
			data.rarestOneIn = math.max(data.rarestOneIn, stats.oneIn)
		end
	end
end

function LeaderboardService.start()
	local folder = Instance.new("Folder")
	folder.Name = "Leaderboards"
	folder.Parent = workspace
	for index, board in Leaderboards.boards do
		buildBoard(folder, board, Leaderboards.placements[index])
		drawBoard(board, {})
	end

	PlayerData.onLoaded(onLoaded)
	Players.PlayerRemoving:Connect(function(player)
		lastWritten[player.UserId] = nil
	end)
	task.spawn(function()
		loadHidden()
		task.wait(FIRST_UPDATE_DELAY)
		while true do
			refresh()
			task.wait(Leaderboards.updateInterval)
		end
	end)
end

return LeaderboardService
