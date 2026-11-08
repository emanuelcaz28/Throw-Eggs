-- Admin chat command (Config/Admin lists who is an admin): "/give <player|me|all> <item> [amount]" gives a player in
-- THIS server anything the Shop sells, with no purchase. The client only forwards the typed text (AdminCommandController);
-- everything is checked here, so a non-admin sending the remote does nothing. "/give items" lists the item names.
-- Gives go straight into the save and are saved at once. They don't use receipts, so they can be repeated.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local AdminService = require(script.Parent.AdminService)
local Gifts = require(ReplicatedStorage.Shared.Gifts)
local LuckyThrows = require(ReplicatedStorage.Shared.LuckyThrows)
local PlayerData = require(script.Parent.PlayerData)
local PlotService = require(script.Parent.PlotService)
local Shop = require(ReplicatedStorage.Shared.Config.Shop)
local ShopService = require(script.Parent.ShopService)
local Specials = require(ReplicatedStorage.Shared.Config.Specials)

local AdminCommands = {}

local MAX_COUNT = 1000 -- most of a counted item (lucky throws, packs) in one command
local MAX_MONSTERS = 25 -- most monsters or Prism Eggs in one command: each one needs room on the plot or in the backpack
local CASH_SIZES = { "S", "M", "L", "XL" } -- the cash packs, in Config/Shop order (the Shop's own names)

type Item = {
	key: string,
	name: string,
	max: number,
	give: (player: Player, data: any, amount: number) -> string?, -- an error text, or nil when it worked
}

local items: { Item } = {}
local byKey: { [string]: Item } = {}
local aliases: { [string]: string } = {}

local function normalise(text: string): string
	local stripped = string.gsub(text, "[^%w]", "")
	return string.lower(stripped)
end

local function add(key: string, name: string, max: number, give, extraKeys: { string }?)
	local item = { key = key, name = name, max = max, give = give }
	table.insert(items, item)
	byKey[key] = item
	for _, alias in extraKeys or {} do
		aliases[alias] = key
	end
end

local function givesProduct(productId: number)
	return function(player: Player, data, amount: number): string?
		for _ = 1, amount do
			if not ShopService.grantProduct(player, data, productId) then
				return "that item isn't set up yet (its product id is 0)"
			end
		end
		return nil
	end
end

local function buildItems()
	add("prismegg", Shop.prismEgg.name, MAX_MONSTERS, givesProduct(Shop.prismEgg.productId), { "prism", "egg" })

	for _, special in Specials do
		add(normalise(special.id), special.name, MAX_MONSTERS, function(player, data, amount)
			if special.passId then
				data.specialsGiven[special.id] = true -- so the Shop says OWNED and a later pass check adds no extra one
				player:SetAttribute(`Owns{special.id}`, true)
			end
			for _ = 1, amount do
				PlotService.addSpecial(player, data, special)
			end
			return nil
		end)
	end

	for _, multiplier in LuckyThrows.tiers do
		add(`luck{multiplier}`, `Luck x{multiplier}`, MAX_COUNT, function(player, data, amount)
			ShopService.addLuckyThrows(player, data, multiplier, amount)
			return nil
		end, { `x{multiplier}`, `luckx{multiplier}` })
	end

	add("serverluck", `{Shop.serverLuck.name} ({Shop.serverLuck.seconds // 60} min each)`, 20, givesProduct(Shop.serverLuck.productId))

	-- Game Passes: given the way a gifted pass is (saved on the player), so they last like a bought one. One is enough.
	for _, pass in Gifts.passes do
		local config = Shop[pass.key]
		add(normalise(config.name), config.name, 1, givesProduct(config.giftProductId or 0))
	end

	for index, pack in Shop.cashPacks do
		local size = CASH_SIZES[index] or tostring(index)
		add(`cash{string.lower(size)}`, `Cash Pack {size}`, MAX_COUNT, givesProduct(pack.productId))
	end
	for _, pack in Shop.powerPacks do
		add(`power{pack.amount}`, `+{pack.amount} Power`, MAX_COUNT, givesProduct(pack.productId))
	end
end

local function itemList(): string
	local names = {}
	for _, item in items do
		table.insert(names, item.key)
	end
	return table.concat(names, ", ")
end

local USAGE = "/give <player|me|all> <item> [amount]   e.g. /give pisorcos00 luck500 2"

-- The players a name means: "me", "all", or one player by name or display name (exact, else the start of it).
local function findPlayers(sender: Player, query: string): ({ Player }?, string?)
	local stripped = string.gsub(query, "^@", "")
	local lowered = string.lower(stripped)
	if lowered == "me" then
		return { sender }, nil
	elseif lowered == "all" then
		return Players:GetPlayers(), nil
	end
	local starts = {}
	for _, player in Players:GetPlayers() do
		local name, display = string.lower(player.Name), string.lower(player.DisplayName)
		if name == lowered or display == lowered then
			return { player }, nil
		end
		if string.sub(name, 1, #lowered) == lowered or string.sub(display, 1, #lowered) == lowered then
			table.insert(starts, player)
		end
	end
	if #starts == 1 then
		return starts, nil
	elseif #starts > 1 then
		return nil, `more than one player starts with "{query}", type more of the name`
	end
	return nil, `no player named "{query}" in this server (the command only reaches players in the server you are in)`
end

local remote: RemoteEvent

local function reply(player: Player, text: string)
	remote:FireClient(player, text)
end

local function onCommand(sender: Player, text: any)
	if typeof(text) ~= "string" or #text > 200 or not AdminService.isAdmin(sender) then
		return
	end
	local words = {}
	for word in string.gmatch(text, "%S+") do
		table.insert(words, word)
	end
	table.remove(words, 1) -- "/give" itself
	if #words == 0 or string.lower(words[1]) == "items" or string.lower(words[1]) == "help" then
		reply(sender, `{USAGE}\nItems: {itemList()}`)
		return
	end
	if #words < 2 or #words > 3 then
		reply(sender, `Usage: {USAGE}`)
		return
	end

	local key = normalise(words[2])
	local item = byKey[aliases[key] or key]
	if not item then
		reply(sender, `Unknown item "{words[2]}". Items: {itemList()}`)
		return
	end
	local amount = if words[3] then tonumber(words[3]) else 1
	if not amount or amount ~= math.floor(amount) or amount < 1 then
		reply(sender, `The amount must be a whole number, 1 or more (got "{words[3]}")`)
		return
	end
	if amount > item.max then
		reply(sender, `At most {item.max} {item.name} at a time`)
		return
	end
	local targets, problem = findPlayers(sender, words[1])
	if not targets then
		reply(sender, `Not given: {problem}`)
		return
	end

	local lines = {}
	for _, target in targets do
		local data = PlayerData.get(target)
		if not data then
			table.insert(lines, `{target.Name}: still loading, try again in a moment`)
			continue
		end
		local failure = item.give(target, data, amount)
		if failure then
			table.insert(lines, `{target.Name}: {failure}`)
			continue
		end
		local saved = PlayerData.saveNow(target)
		if target ~= sender then
			PlotService.notify(target, `Gift: {amount} {item.name}!`)
		end
		print(`[AdminCommands] {sender.Name} gave {target.Name} {amount} x {item.name} (saved: {saved})`)
		table.insert(lines, `Gave {target.Name} {amount} x {item.name}{if saved then "" else " (save failed, will retry with the next autosave)"}`)
	end
	reply(sender, table.concat(lines, "\n"))
end

function AdminCommands.start()
	buildItems()
	remote = Instance.new("RemoteEvent")
	remote.Name = "Give"
	remote.Parent = ReplicatedStorage:WaitForChild("AdminRemotes") -- made by AdminService.start
	remote.OnServerEvent:Connect(onCommand)
end

return AdminCommands
