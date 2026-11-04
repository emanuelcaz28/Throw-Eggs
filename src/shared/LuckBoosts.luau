-- Timed luck boosts and what they multiply to: Server Luck (bought by anyone, for everyone in the
-- server). The server sets the attribute on ReplicatedStorage; clients can't change it, so the server's
-- rolls read it too. One-throw boosts are LuckyThrows.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Shop = require(script.Parent.Config.Shop)

local LuckBoosts = {}

export type Boost = { name: string, multiplier: number, endsAt: number }

function LuckBoosts.active(_player: Player, now: number): { Boost }
	local list = {}
	local endsAt = ReplicatedStorage:GetAttribute("ServerLuckEndsAt")
	if endsAt and endsAt > now then
		table.insert(list, { name = Shop.serverLuck.name, multiplier = Shop.serverLuck.multiplier, endsAt = endsAt })
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
