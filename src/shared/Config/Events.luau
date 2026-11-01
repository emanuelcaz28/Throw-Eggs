-- Timed server events. One runs at a time, picked at random; then there's a break before
-- the next. Boosts not listed on an event stay at 1. Placeholder numbers; tune during playtesting.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Events = {
	firstDelay = 5 * 60, -- seconds after a server starts before its first event
	studioFirstDelay = 15, -- shorter in Studio so you can test without waiting
	gap = 20 * 60, -- seconds between the end of one event and the start of the next

	list = {
		{
			id = "MeteorShower",
			name = "Meteor Shower",
			description = "2x mutation chance",
			seconds = 10 * 60,
			mutationChance = 2,
			color = Color3.fromRGB(255, 140, 70),
			meteors = true,
		},
		{
			id = "GrowthSpurt",
			name = "Growth Spurt",
			description = "2x chance of big dinos",
			seconds = 10 * 60,
			sizeChance = 2,
			color = Color3.fromRGB(120, 226, 140),
		},
		{
			id = "GoldRush",
			name = "Gold Rush",
			description = "2x cash from every plot",
			seconds = 10 * 60,
			income = 2,
			color = Color3.fromRGB(255, 205, 70),
		},
	},
}

-- The event running right now, or nil. Read from ReplicatedStorage, so it works on the
-- server and on every client.
function Events.active()
	local id = ReplicatedStorage:GetAttribute("EventId")
	if not id or (ReplicatedStorage:GetAttribute("EventEndsAt") or 0) <= workspace:GetServerTimeNow() then
		return nil
	end
	for _, event in Events.list do
		if event.id == id then
			return event
		end
	end
	return nil
end

-- boost is "mutationChance", "sizeChance", "income" or "luck".
function Events.multiplier(boost: string): number
	local event = Events.active()
	return if event and event[boost] then event[boost] else 1
end

return Events
