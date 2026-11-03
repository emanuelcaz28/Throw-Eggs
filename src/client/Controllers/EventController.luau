-- Shows the timed events: a timer at the top right, a big announcement when one starts,
-- a sky tint while it runs and falling meteors during a Meteor Shower. Display only:
-- the server decides when events run and applies their boosts.
local Lighting = game:GetService("Lighting")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Events = require(ReplicatedStorage.Shared.Config.Events)
local PopText = require(ReplicatedStorage.Shared.PopText)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local EventController = {}

local TEXT = Color3.new(1, 1, 1)
local MUTED = Color3.fromRGB(190, 195, 205)
local TIMER_TOP = 16
local TIMER_BELOW_LUCK = 70 -- moves down when the Server Luck timer is showing
local TINT_STRENGTH = 0.15
local METEOR_EVERY = 0.4 -- seconds between meteors
local METEOR_FALL_TIME = 1.6
local METEOR_SIZE = 3

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "EventHud"
	gui.ResetOnSpawn = false
	gui.Parent = player:WaitForChild("PlayerGui")

	local timer = UiKit.text(gui, "", 24)
	timer.Name = "EventTimer"
	timer.AnchorPoint = Vector2.new(1, 0)
	timer.Position = UDim2.new(1, -16, 0, TIMER_TOP)
	timer.Size = UDim2.fromOffset(300, 46)
	timer.BackgroundColor3 = UiKit.PANEL
	timer.BackgroundTransparency = 0.05
	timer.Visible = false
	UiKit.corner(timer, 16)
	UiKit.stroke(timer, 4)

	return { timer = timer }
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
			PopText.shout(`{string.upper(event.name)}!`, `{event.description} for {clock(event.seconds)}`, event.color)
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
