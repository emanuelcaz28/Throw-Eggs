-- Filming mode for TikTok clips, Studio only (Config/Filming, FilmingService). A FILM button opens a panel that picks
-- the monster, size and colour every throw catches; the hide key (H) clears the HUD and Roblox's own buttons so only
-- the game world, the throw meter and the reveal are left on screen.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local StarterGui = game:GetService("StarterGui")
local UserInputService = game:GetService("UserInputService")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)
local Filming = require(ReplicatedStorage.Shared.Config.Filming)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local FilmingController = {}

-- Hiding the HUD -------------------------------------------------------------------------------------------------------

local hidden = false
local wanted: { [ScreenGui]: boolean } = {} -- what the game wants each hidden gui's Enabled to be
local watchers: { [ScreenGui]: RBXScriptConnection } = {}
local coreWas: { [Enum.CoreGuiType]: boolean } = {}

local function keeps(gui: Instance): boolean
	return not gui:IsA("ScreenGui")
		or table.find(Filming.keepVisible, gui.Name) ~= nil
		or string.sub(gui.Name, 1, #Filming.keepPrefix) == Filming.keepPrefix
end

local function hideOne(gui: Instance)
	if keeps(gui) or watchers[gui] then
		return
	end
	local screen = gui :: ScreenGui
	wanted[screen] = screen.Enabled
	screen.Enabled = false
	-- The game may switch it back on while hidden (after a throw, say): remember that, and keep it off.
	watchers[screen] = screen:GetPropertyChangedSignal("Enabled"):Connect(function()
		if screen.Enabled then
			wanted[screen] = true
			screen.Enabled = false
		end
	end)
end

local function setHidden(on: boolean)
	if on == hidden then
		return
	end
	hidden = on
	local playerGui = player:WaitForChild("PlayerGui")
	if on then
		for _, gui in playerGui:GetChildren() do
			hideOne(gui)
		end
		for _, kind in Enum.CoreGuiType:GetEnumItems() do
			if kind ~= Enum.CoreGuiType.All then
				coreWas[kind] = StarterGui:GetCoreGuiEnabled(kind)
			end
		end
		StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.All, false)
	else
		for screen, connection in watchers do
			connection:Disconnect()
			if screen.Parent then
				screen.Enabled = wanted[screen] == true
			end
		end
		table.clear(watchers)
		table.clear(wanted)
		for kind, was in coreWas do
			StarterGui:SetCoreGuiEnabled(kind, was)
		end
		table.clear(coreWas)
	end
end

-- The panel ------------------------------------------------------------------------------------------------------------

local function maps()
	local list = {}
	for _, biome in Biomes do
		if not biome.hidden and not biome.rollFrom and Dinos[biome.id] then
			table.insert(list, biome)
		end
	end
	return list
end

-- A row: "<" label ">", cycling through `count` choices.
local function picker(parent: Instance, order: number, onStep: (number) -> ()): TextLabel
	local row = Instance.new("Frame")
	row.BackgroundTransparency = 1
	row.Size = UDim2.fromOffset(400, 50)
	row.LayoutOrder = order
	row.Parent = parent
	local back = UiKit.button(row, "<", "blue", 56, 50, 26)
	back.AnchorPoint = Vector2.new(0, 0.5)
	back.Position = UDim2.fromScale(0, 0.5)
	local forward = UiKit.button(row, ">", "blue", 56, 50, 26)
	forward.AnchorPoint = Vector2.new(1, 0.5)
	forward.Position = UDim2.fromScale(1, 0.5)
	local label = UiKit.text(row, "", 22, nil, Enum.TextXAlignment.Center)
	label.AnchorPoint = Vector2.new(0.5, 0.5)
	label.Position = UDim2.fromScale(0.5, 0.5)
	label.Size = UDim2.new(1, -130, 1, 0)
	label.TextScaled = true
	back.Activated:Connect(function()
		onStep(-1)
	end)
	forward.Activated:Connect(function()
		onStep(1)
	end)
	return label
end

local function wrap(index: number, count: number): number
	return (index - 1) % count + 1
end

function FilmingController.start()
	if not RunService:IsStudio() or workspace:GetAttribute(Filming.attribute) ~= true then
		return
	end
	local remote = ReplicatedStorage:WaitForChild("FilmingRemotes"):WaitForChild("Pick")
	local playerGui = player:WaitForChild("PlayerGui")

	local gui = Instance.new("ScreenGui")
	gui.Name = "FilmingHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 3
	gui.Parent = playerGui

	local scale = UiKit.scale()
	local open = UiKit.button(gui, "FILM", "purple", 110, 40, 20)
	open.Name = "FilmButton"
	open.AnchorPoint = Vector2.new(0, 0)
	open.Position = UDim2.fromOffset(12 * scale, 60 * scale) -- under ADMIN
	local openScale = open:FindFirstChildOfClass("UIScale")
	if openScale then
		openScale.Scale = scale
	end

	local panel = UiKit.panel(gui, { name = "FilmingPanel", width = 460, height = 590, header = "purple", title = "Filming" })
	local list = Instance.new("Frame")
	list.BackgroundTransparency = 1
	list.Position = UDim2.fromOffset(30, 14)
	list.Size = UDim2.new(1, -60, 1, -28)
	list.Parent = panel.body
	local layout = Instance.new("UIListLayout")
	layout.Padding = UDim.new(0, 10)
	layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = list

	local worlds = maps()
	local sizes = { false :: any }
	for index = #Catch.sizes, 1, -1 do -- smallest first
		table.insert(sizes, Catch.sizes[index])
	end
	local colours = { false :: any }
	for index = #Catch.mutations, 1, -1 do -- commonest first
		table.insert(colours, Catch.mutations[index])
	end
	local mapIndex, rank, sizeIndex, colourIndex = 1, #Dinos[worlds[1].id], 1, 1
	local catching = false

	local mapLabel, monsterLabel, sizeLabel, colourLabel, oddsLabel, toggle
	local function refresh()
		local biome = worlds[mapIndex]
		local dinos = Dinos[biome.id]
		rank = math.clamp(rank, 1, #dinos)
		local size, colour = sizes[sizeIndex], colours[colourIndex]
		mapLabel.Text = `Map {mapIndex}: {biome.name}`
		monsterLabel.Text = `{rank}/{#dinos}: {dinos[rank].name}`
		sizeLabel.Text = if size then size.name else "Normal size"
		colourLabel.Text = if colour then colour.name else "No colour"
		local stats = DinoStats.describe({ id = dinos[rank].id, size = size and size.id, mutation = colour and colour.id })
		oddsLabel.Text = if stats then `1 in {Format.commas(stats.oneIn)}   |   {Format.cash(stats.income)}/s` else ""
		UiKit.restyle(toggle, if catching then "Every throw catches this: ON" else "Every throw catches this: OFF",
			if catching then "green" else "red")
		if catching then
			remote:FireServer({
				biome = biome.id,
				rank = rank,
				size = size and size.id or nil,
				mutation = colour and colour.id or nil,
			})
		else
			remote:FireServer(nil)
		end
	end

	mapLabel = picker(list, 1, function(step)
		mapIndex = wrap(mapIndex + step, #worlds)
		rank = #Dinos[worlds[mapIndex].id]
		refresh()
	end)
	monsterLabel = picker(list, 2, function(step)
		rank = wrap(rank + step, #Dinos[worlds[mapIndex].id])
		refresh()
	end)
	sizeLabel = picker(list, 3, function(step)
		sizeIndex = wrap(sizeIndex + step, #sizes)
		refresh()
	end)
	colourLabel = picker(list, 4, function(step)
		colourIndex = wrap(colourIndex + step, #colours)
		refresh()
	end)
	oddsLabel = UiKit.muted(list, "", 20, Enum.TextXAlignment.Center)
	oddsLabel.LayoutOrder = 5
	oddsLabel.Size = UDim2.fromOffset(400, 28)

	toggle = UiKit.button(list, "", "red", 400, 52, 20)
	toggle.LayoutOrder = 6
	toggle.Activated:Connect(function()
		catching = not catching
		refresh()
	end)
	local hideButton = UiKit.button(list, `Hide HUD (press {Filming.hideKey.Name} to bring it back)`, "blue", 400, 52, 18)
	hideButton.LayoutOrder = 7
	hideButton.Activated:Connect(function()
		UiKit.closePanel(panel)
		task.delay(0.4, setHidden, true) -- after the panel's closing animation
	end)
	local tip = UiKit.muted(list, "The egg lands in the picked map, whatever your power. Nothing is saved.", 16, Enum.TextXAlignment.Center)
	tip.LayoutOrder = 8
	tip.Size = UDim2.fromOffset(400, 44)
	tip.TextWrapped = true
	refresh()

	open.Activated:Connect(function()
		UiKit.togglePanel(panel)
	end)
	playerGui.ChildAdded:Connect(function(child)
		if hidden then
			hideOne(child)
		end
	end)
	UserInputService.InputBegan:Connect(function(input, processed)
		if not processed and input.KeyCode == Filming.hideKey then
			setHidden(not hidden)
		end
	end)
end

return FilmingController
