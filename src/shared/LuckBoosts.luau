-- Timed luck boosts and what they multiply to: Server Luck (bought by anyone, for everyone in the
-- server) and the Double Luck event (Config/Events). The server sets the Server Luck attribute on
-- ReplicatedStorage; clients can't change it, so the server's rolls read it too. One-throw boosts are LuckyThrows.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Events = require(script.Parent.Config.Events)
local Shop = require(script.Parent.Config.Shop)

local LuckBoosts = {}

export type Boost = { name: string, multiplier: number, endsAt: number, event: boolean? }

function LuckBoosts.active(_player: Player, now: number): { Boost }
	local list = {}
	local endsAt = ReplicatedStorage:GetAttribute("ServerLuckEndsAt")
	if endsAt and endsAt > now then
		table.insert(list, { name = "Server Luck", multiplier = Shop.serverLuck.multiplier, endsAt = endsAt })
	end
	-- A luck event (Config/Events). Its end is on the events' clock, so it's turned back into server time.
	local event, eventEndsAt = Events.active()
	if event and event.luck then
		table.insert(list, { name = event.name, multiplier = event.luck, endsAt = eventEndsAt - Events.now() + now, event = true })
	end
	return list
end

function LuckBoosts.multiplier(player: Player, now: number): number
	local total = 1
	for _, boost in LuckBoosts.active(player, now) do
		total *= boost.multiplier
	end
	return total
end

return LuckBoosts
