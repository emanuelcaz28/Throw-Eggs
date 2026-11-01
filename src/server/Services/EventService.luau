-- Runs the timed events: waits, starts a random one, lets it run, then waits again.
-- What's running is kept as attributes on ReplicatedStorage so every client can show it,
-- and the boosts are read with Events.multiplier wherever they apply.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Events = require(ReplicatedStorage.Shared.Config.Events)

local EventService = {}

local rng = Random.new()
local lastId: string? = nil

local function pickEvent()
	local choices = {}
	for _, event in Events.list do
		if event.id ~= lastId or #Events.list == 1 then
			table.insert(choices, event)
		end
	end
	return choices[rng:NextInteger(1, #choices)]
end

-- Starts an event now, replacing any that's running. Also handy for testing from the
-- Studio command bar while playing:
-- require(game.ServerScriptService.Server.Services.EventService).startEvent("MeteorShower")
function EventService.startEvent(id: string?)
	local event = pickEvent()
	for _, option in Events.list do
		if option.id == id then
			event = option
		end
	end
	lastId = event.id
	ReplicatedStorage:SetAttribute("EventId", event.id)
	ReplicatedStorage:SetAttribute("EventEndsAt", workspace:GetServerTimeNow() + event.seconds)
	ReplicatedStorage:SetAttribute("NextEventAt", nil)
end

-- Re-reads the attribute every second, since startEvent can move it.
local function waitUntil(attribute: string)
	while workspace:GetServerTimeNow() < (ReplicatedStorage:GetAttribute(attribute) or 0) do
		task.wait(1)
	end
end

function EventService.start()
	task.spawn(function()
		local delay = if RunService:IsStudio() then Events.studioFirstDelay else Events.firstDelay
		ReplicatedStorage:SetAttribute("NextEventAt", workspace:GetServerTimeNow() + delay)
		while true do
			waitUntil("NextEventAt")
			-- startEvent from the command bar may have started one already.
			if not Events.active() then
				EventService.startEvent()
			end
			waitUntil("EventEndsAt")
			ReplicatedStorage:SetAttribute("EventId", nil)
			ReplicatedStorage:SetAttribute("NextEventAt", workspace:GetServerTimeNow() + Events.gap)
		end
	end)
end

return EventService
