-- Competition on screen (Config/Competition, docs/GAME_SPEC.md section 12):
--   * the server ranking in the top left: everyone here by $/s, you highlighted;
--   * "+$X" rising from every base each second, so you see who's making the most;
--   * an alert when someone passes you or you pass someone;
--   * a shout when someone is the first in the server to reach a world.
-- Everything comes from the Income and PlotIndex attributes the server sets; display only.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local Competition = require(ReplicatedStorage.Shared.Config.Competition)
local Format = require(ReplicatedStorage.Shared.Format)
local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local Pop = require(ReplicatedStorage.Shared.Config.Pop)
local PopText = require(ReplicatedStorage.Shared.PopText)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local RankingController = {}

local ROW = 34
local WIDTH = 300
local TOP = 64 -- clear of Roblox's own buttons
local POP_HEIGHT = 16 -- studs above a base where its money rises from
local POP_RISE = 8
local POP_TIME = 1.2

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "RankingHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.Parent = player:WaitForChild("PlayerGui")

	local holder = Instance.new("Frame")
	holder.Position = UDim2.fromOffset(16, TOP)
	holder.Size = UDim2.fromOffset(WIDTH, 0)
	holder.AutomaticSize = Enum.AutomaticSize.Y
	holder.BackgroundColor3 = UiKit.PANEL
	holder.BackgroundTransparency = 0.15
	holder.Parent = gui
	UiKit.corner(holder, 14)
	UiKit.stroke(holder, 3)
	local scale = Instance.new("UIScale")
	scale.Scale = UiKit.scale()
	scale.Parent = holder
	local pad = Instance.new("UIPadding")
	pad.PaddingTop = UDim.new(0, 6)
	pad.PaddingBottom = UDim.new(0, 6)
	pad.PaddingLeft = UDim.new(0, 10)
	pad.PaddingRight = UDim.new(0, 10)
	pad.Parent = holder
	local layout = Instance.new("UIListLayout")
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = holder

	local title = UiKit.text(holder, "SERVER RANKING", 18, UiKit.MUTED, Enum.TextXAlignment.Left)
	title.Size = UDim2.new(1, 0, 0, 24)
	title.LayoutOrder = 0

	local rows = {}
	for index = 1, Competition.listRows do
		local row = Instance.new("Frame")
		row.BackgroundTransparency = 1
		row.Size = UDim2.new(1, 0, 0, ROW)
		row.LayoutOrder = index
		row.Parent = holder
		UiKit.corner(row, 8)
		local name = UiKit.text(row, "", 20, nil, Enum.TextXAlignment.Left)
		name.Size = UDim2.new(0.55, 0, 1, 0)
		name.Position = UDim2.fromOffset(6, 0)
		name.TextTruncate = Enum.TextTruncate.AtEnd
		local income = UiKit.text(row, "", 20, UiKit.CASH, Enum.TextXAlignment.Right)
		income.AnchorPoint = Vector2.new(1, 0)
		income.Position = UDim2.new(1, -6, 0, 0)
		income.Size = UDim2.new(0.45, 0, 1, 0)
		rows[index] = { frame = row, name = name, income = income }
	end
	return { rows = rows }
end

-- "+$X" rising over a base, in the world so it shrinks with distance like the base does.
local function basePop(plotIndex: number, income: number)
	local plots = workspace:FindFirstChild("Plots")
	local plotModel = plots and plots:FindFirstChild(`Plot{plotIndex}`)
	if not plotModel then
		return
	end
	local anchor = Instance.new("Part")
	anchor.Anchored = true
	anchor.CanCollide = false
	anchor.CanQuery = false
	anchor.CanTouch = false
	anchor.Transparency = 1
	anchor.Size = Vector3.one
	anchor.Position = Plot.positions[plotIndex] + Vector3.new((math.random() - 0.5) * 16, POP_HEIGHT, (math.random() - 0.5) * 16)
	anchor.Parent = plotModel
	local gui = Instance.new("BillboardGui")
	gui.Size = UDim2.fromScale(18, 4)
	gui.LightInfluence = 0
	gui.Parent = anchor
	local label = UiKit.text(gui, `+{Format.cash(income)}`, 40, Pop.colors.cash)
	label.Size = UDim2.fromScale(1, 1)
	label.TextScaled = true
	local info = TweenInfo.new(POP_TIME, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
	TweenService:Create(anchor, info, { Position = anchor.Position + Vector3.new(0, POP_RISE, 0) }):Play()
	local fade = TweenService:Create(label, info, { TextTransparency = 1 })
	fade:Play()
	local stroke = label:FindFirstChildOfClass("UIStroke")
	if stroke then
		TweenService:Create(stroke, info, { Transparency = 1 }):Play()
	end
	fade.Completed:Once(function()
		anchor:Destroy()
	end)
end

function RankingController.start()
	local hud = buildGui()
	local lastOrder: { Player } = {}

	local function ranked(): { Player }
		local list = {}
		for _, other in Players:GetPlayers() do
			table.insert(list, other)
		end
		table.sort(list, function(a, b)
			return (a:GetAttribute("Income") or 0) > (b:GetAttribute("Income") or 0)
		end)
		return list
	end

	local function render(list: { Player })
		for index, row in hud.rows do
			local other = list[index]
			row.frame.Visible = other ~= nil
			if other then
				local crown = if index == 1 and (other:GetAttribute("Income") or 0) > 0 then "👑 " else ""
				row.name.Text = `{index}. {crown}{other.DisplayName}`
				row.income.Text = `{Format.cash(other:GetAttribute("Income") or 0)}/s`
				row.frame.BackgroundTransparency = if other == player then 0.6 else 1
				row.frame.BackgroundColor3 = Pop.colors.good
			end
		end
	end

	-- Who passed whom since the last check: only pairs involving this player.
	local function alerts(list: { Player })
		local myPlace = table.find(list, player)
		local before = table.find(lastOrder, player)
		if not myPlace or not before or myPlace == before then
			return
		end
		for _, other in list do
			local was, now = table.find(lastOrder, other), table.find(list, other)
			if other ~= player and was and now then
				if was > before and now < myPlace then
					PopText.notice(`{other.DisplayName} passed you! You're #{myPlace}`, false)
					return
				elseif was < before and now > myPlace then
					PopText.notice(`You passed {other.DisplayName}! You're #{myPlace}`, true)
					return
				end
			end
		end
	end

	task.spawn(function()
		while true do
			local list = ranked()
			render(list)
			alerts(list)
			lastOrder = list
			for _, other in list do
				local plotIndex = other:GetAttribute("PlotIndex")
				local income = other:GetAttribute("Income") or 0
				if plotIndex and income > 0 then
					basePop(plotIndex, income)
				end
			end
			task.wait(1)
		end
	end)

	ReplicatedStorage:WaitForChild("WorldFirst").OnClientEvent:Connect(function(name: string, world: string, color: Color3)
		PopText.shout(`{string.upper(world)}!`, `{name} is the first here to reach it`, color)
	end)
end

return RankingController
