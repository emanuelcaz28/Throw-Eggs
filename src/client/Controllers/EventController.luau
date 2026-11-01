-- Shows the timed events: a timer at the top right, a big announcement when one starts,
-- a sky tint while it runs and falling meteors during a Meteor Shower. Display only:
-- the server decides when events run and applies their boosts.
local Lighting = game:GetService("Lighting")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Events = require(ReplicatedStorage.Shared.Config.Events)

local player = Players.LocalPlayer

local EventController = {}

local PANEL = Color3.fromRGB(28, 30, 36)
local TEXT = Color3.new(1, 1, 1)
local MUTED = Color3.fromRGB(190, 195, 205)
local TIMER_TOP = 16
local TIMER_BELOW_LUCK = 56 -- moves down when the Server Luck timer is showing
local ANNOUNCE_HOLD = 4 -- seconds the "event started" text stays up
local TINT_STRENGTH = 0.15
local METEOR_EVERY = 0.4 -- seconds between meteors
local METEOR_FALL_TIME = 1.6
local METEOR_SIZE = 3

local function corner(parent: Instance, radius: number)
	local uiCorner = Instance.new("UICorner")
	uiCorner.CornerRadius = UDim.new(0, radius)
	uiCorner.Parent = parent
end

local function makeLabel(parent: Instance, font: Enum.Font, color: Color3, position: UDim2, size: UDim2): TextLabel
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.Font = font
	label.Position = position
	label.Size = size
	label.Text = ""
	label.TextColor3 = color
	label.TextScaled = true
	label.Parent = parent
	return label
end

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "EventHud"
	gui.ResetOnSpawn = false
	gui.Parent = player:WaitForChild("PlayerGui")

	local timer = makeLabel(gui, Enum.Font.GothamBlack, TEXT, UDim2.new(1, -16, 0, TIMER_TOP), UDim2.fromOffset(260, 34))
	timer.Name = "EventTimer"
	timer.AnchorPoint = Vector2.new(1, 0)
	timer.BackgroundColor3 = PANEL
	timer.BackgroundTransparency = 0.12
	timer.Visible = false
	corner(timer, 10)
	local padding = Instance.new("UIPadding")
	padding.PaddingTop = UDim.new(0, 6)
	padding.PaddingBottom = UDim.new(0, 6)
	padding.PaddingLeft = UDim.new(0, 10)
	padding.PaddingRight = UDim.new(0, 10)
	padding.Parent = timer

	local announce = makeLabel(gui, Enum.Font.GothamBlack, TEXT, UDim2.fromScale(0.5, 0.2), UDim2.new(0.8, 0, 0, 72))
	announce.Name = "EventAnnounce"
	announce.AnchorPoint = Vector2.new(0.5, 0.5)
	announce.TextStrokeTransparency = 0.3
	announce.Visible = false
	local detail = makeLabel(announce, Enum.Font.GothamBold, TEXT, UDim2.new(0, 0, 1, 4), UDim2.new(1, 0, 0, 30))
	detail.Name = "Detail"
	detail.TextStrokeTransparency = 0.3

	return { timer = timer, announce = announce, detail = detail }
end

local function clock(seconds: number): string
	seconds = math.max(math.ceil(seconds), 0)
	return string.format("%d:%02d", seconds // 60, seconds % 60)
end

local function spawnMeteor(color: Color3)
	local camera = workspace.CurrentCamera
	local start = camera.CFrame.Position
		+ Vector3.new(math.random(-160, 160), math.random(120, 180), math.random(-160, 160))
	local finish = start + Vector3.new(math.random(30, 60), -150, math.random(30, 60))

	local meteor = Instance.new("Part")
	meteor.Name = "Meteor"
	meteor.Anchored = true
	meteor.CanCollide = false
	meteor.CanQuery = false
	meteor.CanTouch = false
	meteor.CastShadow = false
	meteor.Shape = Enum.PartType.Ball
	meteor.Material = Enum.Material.Neon
	meteor.Color = color
	meteor.Size = Vector3.one * METEOR_SIZE
	meteor.Position = start
	meteor.Parent = workspace

	local fall = TweenService:Create(meteor, TweenInfo.new(METEOR_FALL_TIME, Enum.EasingStyle.Linear), {
		Position = finish,
		Transparency = 1,
	})
	fall.Completed:Connect(function()
		meteor:Destroy()
	end)
	fall:Play()
end

function EventController.start()
	local hud = buildGui()

	local tint = Instance.new("ColorCorrectionEffect")
	tint.Name = "EventTint"
	tint.Parent = Lighting

	local shownId = nil
	local announceToken = 0

	local function announce(event)
		announceToken += 1
		local token = announceToken
		hud.announce.Text = `{string.upper(event.name)}!`
		hud.announce.TextColor3 = event.color
		hud.detail.Text = `{event.description} for {clock(event.seconds)}`
		hud.announce.Visible = true
		task.delay(ANNOUNCE_HOLD, function()
			if announceToken == token then
				hud.announce.Visible = false
			end
		end)
	end

	local function onEventChanged()
		local event = Events.active()
		local id = event and event.id
		if id == shownId then
			return
		end
		shownId = id
		local tintColor = if event then TEXT:Lerp(event.color, TINT_STRENGTH) else TEXT
		TweenService:Create(tint, TweenInfo.new(2), { TintColor = tintColor }):Play()
		if event then
			announce(event)
		end
	end

	local lastMeteor = 0
	RunService.Heartbeat:Connect(function()
		onEventChanged()
		local now = workspace:GetServerTimeNow()
		local event = Events.active()
		local serverLuckOn = (ReplicatedStorage:GetAttribute("ServerLuckEndsAt") or 0) > now
		hud.timer.Position = UDim2.new(1, -16, 0, if serverLuckOn then TIMER_BELOW_LUCK else TIMER_TOP)

		if event then
			hud.timer.Text = `{string.upper(event.name)}  {clock(ReplicatedStorage:GetAttribute("EventEndsAt") - now)}`
			hud.timer.TextColor3 = event.color
			hud.timer.Visible = true
		else
			local nextAt = ReplicatedStorage:GetAttribute("NextEventAt")
			hud.timer.Visible = nextAt ~= nil and nextAt > now
			if hud.timer.Visible then
				hud.timer.Text = `Next event in {clock(nextAt - now)}`
				hud.timer.TextColor3 = MUTED
			end
		end

		if event and event.meteors and os.clock() - lastMeteor >= METEOR_EVERY then
			lastMeteor = os.clock()
			spawnMeteor(event.color)
		end
	end)
end

return EventController
