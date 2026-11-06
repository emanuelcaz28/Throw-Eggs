-- GIFT [Owner, 2026-11-05]: a player buys a Developer Product or a Game Pass for another player in the same server.
-- This is what can be gifted, in the order the Gift panel shows it. ShopService decides what each gives; GiftController
-- shows it. Developer Products are gifted with their own ids. A Game Pass can't be bought for someone else, so it is
-- gifted with its giftProductId (Config/Shop, Config/Specials). Server Luck isn't here: it's for the whole server already,
-- and the one-time Luck x100 deal is only for the buyer.
local Format = require(script.Parent.Format)
local Shop = require(script.Parent.Config.Shop)
local Specials = require(script.Parent.Config.Specials)

local Gifts = {}

-- The Game Passes, by Config/Shop key, and the player attribute that says a player has one.
Gifts.passes = {
	{ key = "doubleCash", attribute = "HasDoubleCash", art = "cash_L", artKey = "pass_cash" },
	{ key = "doubleTraining", attribute = "HasDoubleTraining", art = "bolts_M", artKey = "pass_training" },
	{ key = "doublePower", attribute = "HasDoublePower", art = "bolts_XL", artKey = "bolts_XL" },
}

local CASH_SIZES = { "S", "M", "L", "XL" }

-- Each item: name, productId (0 = not created yet), monster or art (+ artKey) for its picture, and ownedAttribute when
-- the receiver can only have one (a pass): set on them, it can't be gifted to them.
local items = {}
table.insert(items, { name = Shop.prismEgg.name, productId = Shop.prismEgg.productId, monster = "Dreadlure" })
for _, special in Specials do
	if special.passId then
		table.insert(items, { name = special.name, productId = special.giftProductId or 0, monster = special.id, ownedAttribute = `Owns{special.id}` })
	end
end
for _, item in Shop.luckyThrows do
	table.insert(items, { name = `Luck x{item.multiplier}`, productId = item.productId, art = "clover", artKey = "clover" })
end
for _, pass in Gifts.passes do
	local config = Shop[pass.key]
	table.insert(items, { name = config.name, productId = config.giftProductId or 0, art = pass.art, artKey = pass.artKey, ownedAttribute = pass.attribute })
end
for index, pack in Shop.cashPacks do
	table.insert(items, { name = `Cash Pack {CASH_SIZES[index] or index}`, productId = pack.productId, art = pack.art, artKey = pack.art })
end
for _, pack in Shop.powerPacks do
	table.insert(items, { name = `+{Format.commas(pack.amount)} Power`, productId = pack.productId, art = pack.art, artKey = pack.art })
end
Gifts.items = items

-- The giftable item bought with this product id, or nil.
function Gifts.find(productId: number)
	if productId == 0 then
		return nil
	end
	for _, item in items do
		if item.productId == productId then
			return item
		end
	end
	return nil
end

return Gifts
