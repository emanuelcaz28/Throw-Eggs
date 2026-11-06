-- The Welcome back pop-up: what the plot earned while the player was away, counting up, with a
-- pulsing CLAIM button. Display and requests only: the server holds the amount and pays it on CLAIM.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Format = require(ReplicatedStorage.Shared.Format)
local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local WelcomeController = {}

local COUNT_UP_SECONDS = 1.2
local NO_EARNINGS_GRACE = 2 -- seconds past the server's delay before deciding there's no pop-up

local done = false

local function awayText(seconds: number): string
	local hours = seconds // 3600
	local minutes = (seconds % 3600) // 60
	if hours > 0 then
		return `Away for {hours}h {minutes}m`
	end
	return `Away for {math.max(minutes, 1)}m`
end

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "WelcomeHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 8 -- above every panel
	gui.Parent = player:WaitForChild("PlayerGui")

	local panel = UiKit.panel(gui, { name = "WelcomePanel", width = 620, height = 500, header = "gold", title = "Welcome back!" })
	panel.close.Visible = false -- the only way out is CLAIM
	panel.keepOpen = true -- other panels opening don't close it (UiKit.openPanel)

	local line = UiKit.muted(panel.body, "Your dinos kept earning while you were away", 24)
	line.Position = UDim2.fromOffset(0, 18)

	local box = Instance.new("Frame")
	box.AnchorPoint = Vector2.new(0.5, 0)
	box.Position = UDim2.new(0.5, 0, 0, 64)
	box.Size = UDim2.fromOffset(540, 150)
	box.BackgroundColor3 = UiKit.DEEP
	box.Parent = panel.body
	UiKit.corner(box, 24)
	UiKit.stroke(box, 4)
	UiKit.viewport(box, "cash_XL", { spin = true, position = UDim2.fromOffset(6, 6), size = UDim2.fromOffset(170, 138) })
	local amount = UiKit.text(box, "$0", 76, UiKit.CASH, Enum.TextXAlignment.Left)
	amount.Position = UDim2.fromOffset(186, 34)
	amount.Size = UDim2.fromOffset(340, 86)

	local away = UiKit.text(panel.body, "", 28)
	away.Position = UDim2.fromOffset(0, 232)
	local cap = UiKit.muted(panel.body, `(pays up to {Plot.maxOfflineHours}h)`, 18)
	cap.Position = UDim2.fromOffset(0, 270)

	local claim = UiKit.button(panel.body, "CLAIM", "green", 400, 86, 46)
	claim.AnchorPoint = Vector2.new(0.5, 0)
	claim.Position = UDim2.new(0.5, 0, 0, 306)
	UiKit.pulse(claim)

	return { panel = panel, amount = amount, away = away, cap = cap, claim = claim }
end

function WelcomeController.start()
	local remotes = ReplicatedStorage:WaitForChild("PlotRemotes")
	local hud = buildGui()

	remotes.OfflineEarnings.OnClientEvent:Connect(function(earned: number, awaySeconds: number)
		hud.away.Text = if awaySeconds > 0 then awayText(awaySeconds) else "Unclaimed from last time"
		hud.cap.Visible = awaySeconds > 0
		UiKit.openPanel(hud.panel)
		UiKit.countUp(hud.amount, 0, earned, COUNT_UP_SECONDS, Format.cash)
	end)
	hud.claim.Activated:Connect(function()
		remotes.ClaimOffline:FireServer()
		UiKit.closePanel(hud.panel)
		done = true
	end)
	-- The server sends the earnings a few seconds after joining (Plot.offlinePayoutDelay), or not at all.
	task.delay(Plot.offlinePayoutDelay + NO_EARNINGS_GRACE, function()
		if not hud.panel.frame.Visible then
			done = true
		end
	end)
end

-- Waits until the Welcome back pop-up has been claimed, or it's clear none is coming (DailyController opens after).
function WelcomeController.waitUntilDone()
	while not done do
		task.wait(0.2)
	end
end

return WelcomeController
