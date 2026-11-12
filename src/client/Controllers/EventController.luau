-- The timed events (Config/Events), display only: a shout in the event's colour when one starts and a light tint
-- on the world while it runs. Its icon is in the row at the bottom (BoostRowController). The server applies the
-- boosts itself.
local Lighting = game:GetService("Lighting")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Events = require(ReplicatedStorage.Shared.Config.Events)
local PopText = require(ReplicatedStorage.Shared.PopText)

local EventController = {}

local TINT_STRENGTH = 0.12 -- how far the world's colour moves towards the event's
local TINT_FADE = 2 -- seconds

function EventController.start()
	local tint = Instance.new("ColorCorrectionEffect")
	tint.Name = "EventTint"
	tint.Parent = Lighting

	local shownId: string? = nil
	local joined = false -- an event already running when you join gets its icon and tint but no shout
	RunService.Heartbeat:Connect(function()
		local event = Events.active(Players.LocalPlayer)
		local id = if event then event.id else nil
		if id ~= shownId then
			shownId = id
			local tintColor = if event then Color3.new(1, 1, 1):Lerp(event.color, TINT_STRENGTH) else Color3.new(1, 1, 1)
			TweenService:Create(tint, TweenInfo.new(TINT_FADE), { TintColor = tintColor }):Play()
			if event and joined then
				PopText.shout(`{event.name:upper()}!`, `{event.description} for {Events.seconds // 60} minutes`, event.color)
			end
		end
		joined = true
	end)
end

return EventController
