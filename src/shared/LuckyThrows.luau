-- Lucky throws: one throw with a big luck multiplier, bought in the Shop (Config/Shop luckyThrows) or
-- given by the daily reward (Config/Daily). A player can own several; the next throw uses the biggest.
-- The server keeps the counts in the save and mirrors each one to a player attribute
-- (LuckyThrows100 = 2), which clients read to show them.
local Daily = require(script.Parent.Config.Daily)
local Shop = require(script.Parent.Config.Shop)

local LuckyThrows = {}

-- Every multiplier a lucky throw can have, biggest first.
LuckyThrows.tiers = {}
do
	local seen = {}
	local function add(multiplier: number)
		if not seen[multiplier] then
			seen[multiplier] = true
			table.insert(LuckyThrows.tiers, multiplier)
		end
	end
	for _, item in Shop.luckyThrows do
		add(item.multiplier)
	end
	for _, day in Daily.days do
		add(day.luckyThrow)
	end
	table.sort(LuckyThrows.tiers, function(a, b)
		return a > b
	end)
end

function LuckyThrows.attribute(multiplier: number): string
	return `LuckyThrows{multiplier}`
end

function LuckyThrows.count(player: Player, multiplier: number): number
	return player:GetAttribute(LuckyThrows.attribute(multiplier)) or 0
end

-- The multiplier the next throw will use (the biggest owned), or nil with none.
function LuckyThrows.nextOf(player: Player): number?
	for _, multiplier in LuckyThrows.tiers do
		if LuckyThrows.count(player, multiplier) > 0 then
			return multiplier
		end
	end
	return nil
end

function LuckyThrows.total(player: Player): number
	local total = 0
	for _, multiplier in LuckyThrows.tiers do
		total += LuckyThrows.count(player, multiplier)
	end
	return total
end

return LuckyThrows
