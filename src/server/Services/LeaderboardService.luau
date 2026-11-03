-- The three leaderboards in the arena. Every minute each player's scores are saved to an
-- OrderedDataStore (one per board) and the top lists are read back and drawn on the boards.
-- If the stores can't be reached (Studio without API access), the boards show the players in
-- this server instead.
local DataStoreService = game:GetService("DataStoreService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)
local Leaderboards = require(ReplicatedStorage.Shared.Config.Leaderboards)
local PlayerData = require(script.Parent.PlayerData)
local World = require(ReplicatedStorage.Shared.World)

local LeaderboardService = {}

local FIRST_UPDATE_DELAY = 5 -- seconds after the server starts
local LOG_SCALE = 1e6 -- huge values are stored as log10 * this, since stores only keep whole numbers
local PANEL = Color3.fromRGB(28, 30, 36)
local ROW = Color3.fromRGB(48, 52, 62)
local TOP_ROW = Color3.fromRGB(230, 140, 40)
local TEXT = Color3.new(1, 1, 1)
local MUTED = Color3.fromRGB(190, 195, 205)
local TOP_ROWS = 3

local boardGuis: { [string]: SurfaceGui } = {}
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

local function makeText(parent: Instance, font: Enum.Font, color: Color3, position: UDim2, size: UDim2, align: Enum.TextXAlignment): TextLabel
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.Font = font
	label.Position = position
	label.Size = size
	label.TextColor3 = color
	label.TextScaled = true
	label.TextXAlignment = align
	label.Text = ""
	label.Parent = parent
	return label
end

local function corner(parent: Instance, radius: UDim)
	local uiCorner = Instance.new("UICorner")
	uiCorner.CornerRadius = radius
	uiCorner.Parent = parent
end

local function buildBoard(parent: Instance, board, position: Vector3)
	local size = Leaderboards.size
	local center = position + Vector3.new(0, size.Y / 2, 0)
	local part = World.makePart(parent, board.id, size, CFrame.lookAt(center, center + Leaderboards.facing), PANEL)
	part.TopSurface = Enum.SurfaceType.Studs

	local gui = Instance.new("SurfaceGui")
	gui.Face = Enum.NormalId.Front
	gui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	gui.PixelsPerStud = 40
	gui.Parent = part

	local header = Instance.new("Frame")
	header.Size = UDim2.fromScale(1, 0.16)
	header.BackgroundColor3 = board.color
	header.BorderSizePixel = 0
	header.Parent = gui
	local title = makeText(header, Enum.Font.GothamBlack, TEXT, UDim2.fromScale(0.05, 0.08), UDim2.fromScale(0.9, 0.55), Enum.TextXAlignment.Center)
	title.Text = board.title
	title.TextStrokeTransparency = 0
	local subtitle = makeText(header, Enum.Font.GothamBold, TEXT, UDim2.fromScale(0.05, 0.64), UDim2.fromScale(0.9, 0.28), Enum.TextXAlignment.Center)
	subtitle.Text = board.subtitle

	local list = Instance.new("Frame")
	list.Name = "List"
	list.BackgroundTransparency = 1
	list.Position = UDim2.fromScale(0.04, 0.19)
	list.Size = UDim2.fromScale(0.92, 0.74)
	list.Parent = gui
	local layout = Instance.new("UIListLayout")
	layout.Padding = UDim.new(0.01, 0)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = list

	for rank = 1, Leaderboards.rows do
		local row = Instance.new("Frame")
		row.Name = `Row{rank}`
		row.LayoutOrder = rank
		row.Size = UDim2.fromScale(1, 0.09)
		row.BackgroundColor3 = if rank <= TOP_ROWS then TOP_ROW else ROW
		row.Visible = false
		row.Parent = list
		corner(row, UDim.new(0.3, 0))

		local rankLabel = makeText(row, Enum.Font.GothamBlack, TEXT, UDim2.fromScale(0.02, 0.15), UDim2.fromScale(0.08, 0.7), Enum.TextXAlignment.Center)
		rankLabel.Text = tostring(rank)
		local headshot = Instance.new("ImageLabel")
		headshot.Name = "Headshot"
		headshot.BackgroundTransparency = 1
		headshot.Position = UDim2.fromScale(0.11, 0.08)
		headshot.Size = UDim2.fromScale(0.1, 0.84)
		headshot.Parent = row
		local aspect = Instance.new("UIAspectRatioConstraint")
		aspect.Parent = headshot
		corner(headshot, UDim.new(0.5, 0))
		local nameLabel = makeText(row, Enum.Font.GothamBold, TEXT, UDim2.fromScale(0.23, 0.2), UDim2.fromScale(0.45, 0.6), Enum.TextXAlignment.Left)
		nameLabel.Name = "PlayerName"
		local value = makeText(row, Enum.Font.GothamBlack, TEXT, UDim2.fromScale(0.68, 0.2), UDim2.fromScale(0.3, 0.6), Enum.TextXAlignment.Right)
		value.Name = "Value"
	end

	local footer = makeText(gui, Enum.Font.GothamBold, MUTED, UDim2.fromScale(0.05, 0.945), UDim2.fromScale(0.9, 0.04), Enum.TextXAlignment.Center)
	local interval = Leaderboards.updateInterval
	footer.Text = if interval == 60 then "Updates every minute" else `Updates every {interval} seconds`

	boardGuis[board.id] = gui
end

local function storeFor(board): OrderedDataStore
	return DataStoreService:GetOrderedDataStore(`Leaderboard_v{Leaderboards.storeVersion}_{board.id}`)
end

-- Saves scores that changed since the last write.
local function writeScores()
	for _, player in Players:GetPlayers() do
		local data = PlayerData.get(player)
		if data then
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
			table.insert(top, { userId = tonumber(item.key), value = decode(board, item.value) })
		end
		return top
	end
	for _, player in Players:GetPlayers() do
		local data = PlayerData.get(player)
		if data and data[board.stat] > 0 then
			table.insert(top, { userId = player.UserId, value = data[board.stat] })
		end
	end
	table.sort(top, function(a, b)
		return a.value > b.value
	end)
	return top
end

local function drawBoard(board, top)
	local list = boardGuis[board.id].List
	for rank = 1, Leaderboards.rows do
		local row = list[`Row{rank}`]
		local entry = top[rank]
		row.Visible = entry ~= nil
		if entry then
			row.PlayerName.Text = nameOf(entry.userId)
			row.Value.Text = valueText(board, entry.value)
			row.Headshot.Image = `rbxthumb://type=AvatarHeadShot&id={entry.userId}&w=48&h=48`
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
local function onLoaded(_player: Player, data)
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
	for index, board in Leaderboards.boards do
		buildBoard(folder, board, Leaderboards.positions[index])
	end
	folder.Parent = workspace

	PlayerData.onLoaded(onLoaded)
	Players.PlayerRemoving:Connect(function(player)
		lastWritten[player.UserId] = nil
	end)
	task.spawn(function()
		task.wait(FIRST_UPDATE_DELAY)
		while true do
			refresh()
			task.wait(Leaderboards.updateInterval)
		end
	end)
end

return LeaderboardService
