-- Timed server events: one starts every `every` seconds and runs for `seconds`, taking turns in the order of
-- `list`. The schedule comes from the server clock, so every server and every client agrees on it without
-- messages, and players can see what's next. Boosts not listed on an event stay at 1.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Events = {
	every = 15 * 60, -- seconds from one event's start to the next one's
	seconds = 5 * 60, -- how long each one runs
	list = {
		{
			id = "DoubleLuck",
			name = "Double Luck",
			description = "2x luck on every throw",
			icon = "🍀",
			luck = 2,
			color = Color3.fromRGB(110, 230, 120),
		},
		{
			id = "GhostRush",
			name = "Ghost Rush",
			description = "GHOST monsters 10x more likely",
			icon = "👻",
			mutations = { Ghost = 10 }, -- multiplies that mutation's chance (Config/Catch)
			color = Color3.fromRGB(200, 215, 255),
		},
	},
}

-- The clock the schedule runs on. For testing in Studio, set the attribute EventTestOffset (seconds) on
-- ReplicatedStorage to jump it; e.g. from the command bar while playing (Server):
-- game.ReplicatedStorage:SetAttribute("EventTestOffset", 900 - workspace:GetServerTimeNow() % 900)
function Events.now(): number
	return workspace:GetServerTimeNow() + (ReplicatedStorage:GetAttribute("EventTestOffset") or 0)
end

local function eventOfSlot(slot: number)
	return Events.list[slot % #Events.list + 1]
end

-- A new player's own first event (Config/PlayGifts firstEvent): PlayGiftService sets these attributes on the player.
local function ownEvent(player: Player?, now: number): (any?, number?)
	local id = player and player:GetAttribute("FirstEventId")
	local endsAt = player and player:GetAttribute("FirstEventEndsAt")
	local left = if id and endsAt then endsAt - workspace:GetServerTimeNow() else 0
	if left > 0 then
		for _, event in Events.list do
			if event.id == id then
				return event, now + left
			end
		end
	end
	return nil, nil
end

-- The event running right now and when it ends (on Events.now's clock), or nil. With a player, their own first
-- event counts too when no real one is running.
function Events.active(player: Player?): (any?, number?)
	local now = Events.now()
	local slot = now // Events.every
	local startsAt = slot * Events.every
	if now - startsAt < Events.seconds then
		return eventOfSlot(slot), startsAt + Events.seconds
	end
	return ownEvent(player, now)
end

-- The next event to start and when it starts.
function Events.upcoming(): (any, number)
	local slot = Events.now() // Events.every + 1
	return eventOfSlot(slot), slot * Events.every
end

-- boost is "luck"; 1 when no event gives it.
function Events.multiplier(boost: string, player: Player?): number
	local event = Events.active(player)
	return if event and event[boost] then event[boost] else 1
end

-- Per-mutation chance multipliers of the running event ({ Ghost = 10 }), or an empty table.
function Events.mutationBoosts(player: Player?): { [string]: number }
	local event = Events.active(player)
	return if event and event.mutations then event.mutations else {}
end

return Events
