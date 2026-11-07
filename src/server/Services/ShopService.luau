-- The Robux shop: Game Passes, Server Luck, lucky throws, cash and Throw Power packs, the Prism Egg, GIFT (buying for
-- another player, Shared/Gifts) and the free starter dino. Roblox retries a
-- purchase until told it was granted, so each receipt is saved with the player's data
-- before saying so. That way a purchase is never lost or given twice.
local MarketplaceService = game:GetService("MarketplaceService")
local PolicyService = game:GetService("PolicyService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)
local Gifts = require(ReplicatedStorage.Shared.Gifts)
local IndexService = require(script.Parent.IndexService)
local LuckBoosts = require(ReplicatedStorage.Shared.LuckBoosts)
local LuckyThrows = require(ReplicatedStorage.Shared.LuckyThrows)
local PlayerData = require(script.Parent.PlayerData)
local PlotService = require(script.Parent.PlotService)
local Shop = require(ReplicatedStorage.Shared.Config.Shop)
local Specials = require(ReplicatedStorage.Shared.Config.Specials)
local TrainingService = require(script.Parent.TrainingService)

local ShopService = {}

local LUCK_ATTRIBUTE = "ServerLuckEndsAt" -- set on ReplicatedStorage so every client can show the timer
local DEAL_ATTRIBUTE = "LuckDealBought" -- set on the player once the one-time Luck x100 deal is used

local remotes: { [string]: RemoteEvent } = {}

-- GIFT: who each buyer is gifting to, from asking for the purchase prompt until its receipt (or the prompt closing
-- unbought). { productId, to = Player }.
local pendingGifts: { [Player]: { productId: number, to: Player, at: number } } = {}

local function makeRemotes()
	local folder = Instance.new("Folder")
	folder.Name = "ShopRemotes"
	-- Gift: client asks to gift (productId, receiver's UserId). Shout: server shows a big moment (title, detail).
	-- BuyRandom: client asks to buy a paid random item (productId); the server checks the policy, then prompts.
	for _, name in { "ClaimStarter", "StarterClaimed", "Gift", "Shout", "BuyRandom" } do
		local remote = Instance.new("RemoteEvent")
		remote.Name = name
		remote.Parent = folder
		remotes[name] = remote
	end
	folder.Parent = ReplicatedStorage
end

local function serverLuckActive(): boolean
	return (ReplicatedStorage:GetAttribute(LUCK_ATTRIBUTE) or 0) > workspace:GetServerTimeNow()
end

function ShopService.serverLuckMultiplier(): number
	return if serverLuckActive() then Shop.serverLuck.multiplier else 1
end

-- Timed boosts multiplying this player's luck (Server Luck). Lucky throws are separate.
function ShopService.luckMultiplier(player: Player): number
	return LuckBoosts.multiplier(player, workspace:GetServerTimeNow())
end

local function serverLuckSecondsLeft(): number
	return math.max((ReplicatedStorage:GetAttribute(LUCK_ATTRIBUTE) or 0) - workspace:GetServerTimeNow(), 0)
end

local function grantServerLuck(_player: Player, data)
	local start = math.max(ReplicatedStorage:GetAttribute(LUCK_ATTRIBUTE) or 0, workspace:GetServerTimeNow())
	ReplicatedStorage:SetAttribute(LUCK_ATTRIBUTE, start + Shop.serverLuck.seconds)
	data.serverLuckLeft += Shop.serverLuck.seconds
end

-- Server Luck runs for the whole server, but each buyer also keeps in their save the time they paid
-- for and haven't used. It only counts down while they're playing, so what's left comes back when they
-- join again, even if the server closed. When buyers in the server hold more than the timer has
-- left, the time is taken from them in turn, so stacked purchases are used one after the other.
local function settleServerLuck()
	local left = serverLuckSecondsLeft()
	for _, player in Players:GetPlayers() do
		local data = PlayerData.get(player)
		if data then
			data.serverLuckLeft = math.min(data.serverLuckLeft, left)
			left -= data.serverLuckLeft
		end
	end
end

-- A buyer joined with time left: the timer grows to cover what the buyers here hold. It doesn't add
-- on top, so coming back to a server still running their time doesn't count it twice.
local function resumeServerLuck()
	local held = 0
	for _, player in Players:GetPlayers() do
		local data = PlayerData.get(player)
		held += if data then data.serverLuckLeft else 0
	end
	if held > serverLuckSecondsLeft() then
		ReplicatedStorage:SetAttribute(LUCK_ATTRIBUTE, workspace:GetServerTimeNow() + held)
	end
end

-- Lucky throws (LuckyThrows): counts live in the save by multiplier, mirrored to player attributes.
local function publishLuckyThrows(player: Player, data)
	for _, multiplier in LuckyThrows.tiers do
		player:SetAttribute(LuckyThrows.attribute(multiplier), data.luckyThrows[tostring(multiplier)] or 0)
	end
end

function ShopService.addLuckyThrows(player: Player, data, multiplier: number, amount: number)
	local key = tostring(multiplier)
	data.luckyThrows[key] = (data.luckyThrows[key] or 0) + amount
	publishLuckyThrows(player, data)
end

-- Uses up the lucky throw the player picked (if they still own it), else the biggest owned that goes by itself (the
-- daily x50; LuckyThrows), and returns its multiplier, or 1 with none.
function ShopService.takeLuckyThrow(player: Player, data, picked: number?): number
	if picked and LuckyThrows.isPicked(picked) and (data.luckyThrows[tostring(picked)] or 0) > 0 then
		data.luckyThrows[tostring(picked)] -= 1
		publishLuckyThrows(player, data)
		return picked
	end
	for _, multiplier in LuckyThrows.tiers do
		local key = tostring(multiplier)
		if not LuckyThrows.isPicked(multiplier) and (data.luckyThrows[key] or 0) > 0 then
			data.luckyThrows[key] -= 1
			publishLuckyThrows(player, data)
			return multiplier
		end
	end
	return 1
end

-- Hatches a Prism Egg into one of its monsters by its odds (Config/Shop prismEgg), with a shout. The caller saves.
local function hatchPrismEgg(player: Player, data)
	local hatches = Shop.prismEgg.hatches
	local hatched = hatches[#hatches]
	local roll = math.random() * 100
	for _, option in hatches do
		roll -= option.chance
		if roll < 0 then
			hatched = option
			break
		end
	end
	local special = DinoStats.special(hatched.id)
	local income = PlotService.addSpecial(player, data, special)
	remotes.Shout:FireClient(player, `{string.upper(special.name)}!`, `{special.share * 100}% of your best: +{Format.cash(income)}/s`)
end

-- Gives a Game Pass's special monster, only ever once. The caller saves.
local function giveSpecialTo(player: Player, data, special)
	player:SetAttribute(`Owns{special.id}`, true)
	if not data.specialsGiven[special.id] then
		data.specialsGiven[special.id] = true
		PlotService.addSpecial(player, data, special)
	end
end

-- A Game Pass gifted by another player (Gifts.passes): kept in the save, so it lasts like a bought one.
local function giveGiftedPass(player: Player, data, pass)
	data.giftedPasses[pass.key] = true
	player:SetAttribute(pass.attribute, true)
end

-- What each Developer Product gives, by product id.
local function grantFor(productId: number): ((Player, any) -> ())?
	if productId == 0 then
		return nil
	end
	if productId == Shop.prismEgg.productId then
		return hatchPrismEgg
	end
	for _, pass in Gifts.passes do
		if productId == Shop[pass.key].giftProductId then
			return function(player, data)
				giveGiftedPass(player, data, pass)
			end
		end
	end
	for _, special in Specials do
		if special.passId and productId == special.giftProductId then
			return function(player, data)
				giveSpecialTo(player, data, special)
			end
		end
	end
	if productId == Shop.serverLuck.productId then
		return grantServerLuck
	end
	for _, item in Shop.luckyThrows do
		if productId == item.productId then
			return function(player, data)
				ShopService.addLuckyThrows(player, data, item.multiplier, 1)
			end
		end
		if productId == item.dealProductId then
			-- Granted even if somehow bought twice: they paid. The shop only offers it once.
			return function(player, data)
				data.luckDealBought = true
				player:SetAttribute(DEAL_ATTRIBUTE, true)
				ShopService.addLuckyThrows(player, data, item.multiplier, 1)
			end
		end
	end
	for _, pack in Shop.cashPacks do
		if productId == pack.productId then
			return function(player, data)
				PlotService.payCashPack(player, data, pack)
			end
		end
	end
	for _, pack in Shop.powerPacks do
		if productId == pack.productId then
			return function(player, data)
				TrainingService.addBonusPower(player, data, pack.amount)
			end
		end
	end
	return nil
end

-- The receiver of a gift is told who it's from; the buyer that it arrived.
local function announceGift(from: Player, to: Player, productId: number)
	local item = Gifts.find(productId)
	local name = if item then item.name else "a gift"
	if productId == Shop.prismEgg.productId then
		PlotService.notify(to, `{from.DisplayName} gifted you a {name}!`) -- the hatch has the shout
	else
		remotes.Shout:FireClient(to, `GIFT FROM {string.upper(from.DisplayName)}!`, name)
	end
	PlotService.notify(from, `Gift sent to {to.DisplayName}!`)
end

-- The player this purchase is a gift for, if the buyer asked to gift this product in the last GIFT_WINDOW seconds.
local GIFT_WINDOW = 120
local function giftReceiver(player: Player, productId: number): Player?
	local gift = pendingGifts[player]
	if gift and gift.productId == productId then
		pendingGifts[player] = nil
		if os.clock() - gift.at < GIFT_WINDOW then
			return gift.to
		end
	end
	return nil
end

function ShopService.processReceipt(info)
	local grant = grantFor(info.ProductId)
	if not grant then
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
	local player = Players:GetPlayerByUserId(info.PlayerId)
	local data = player and PlayerData.get(player)
	if not data then
		-- Left or still loading: Roblox tries again the next time they join.
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end

	if not data.receipts[info.PurchaseId] then
		local receiver = giftReceiver(player, info.ProductId)
		local receiverData = receiver and receiver.Parent and PlayerData.get(receiver)
		if receiver and receiverData then
			grant(receiver, receiverData)
			data.receipts[info.PurchaseId] = true
			announceGift(player, receiver, info.ProductId)
			PlayerData.saveNow(receiver)
		else
			-- Not a gift, or its receiver left before it arrived: the buyer keeps it.
			if receiver then
				PlotService.notify(player, `{receiver.DisplayName} left, so the gift is yours`)
			end
			grant(player, data)
			data.receipts[info.PurchaseId] = true
		end
	end
	if PlayerData.saveNow(player) then
		return Enum.ProductPurchaseDecision.PurchaseGranted
	end
	return Enum.ProductPurchaseDecision.NotProcessedYet
end

local function setPassAttribute(player: Player, passId: number)
	if table.find(Shop.ignorePassesFor, player.UserId) then
		return -- the owner's test account: passes are ignored (Config/Shop)
	end
	if passId == Shop.doubleCash.passId then
		player:SetAttribute("HasDoubleCash", true)
	end
	if passId == Shop.doubleTraining.passId then
		player:SetAttribute("HasDoubleTraining", true)
	end
	if passId == Shop.doublePower.passId then
		player:SetAttribute("HasDoublePower", true)
	end
end

-- Whether the player owns a pass, asking again if Roblox doesn't answer.
local function ownsPass(player: Player, pass): boolean
	if table.find(Shop.ignorePassesFor, player.UserId) then
		return false
	end
	local retryDelay = Shop.passCheck.retryDelay
	for attempt = 1, Shop.passCheck.attempts do
		local ok, owns = pcall(function()
			return MarketplaceService:UserOwnsGamePassAsync(player.UserId, pass.passId)
		end)
		if ok then
			return owns
		end
		warn(`[ShopService] Couldn't check {pass.name} for {player.Name} (try {attempt}): {owns}`)
		if attempt == Shop.passCheck.attempts or not player.Parent then
			break
		end
		task.wait(retryDelay)
		retryDelay *= 2
	end
	return false
end

-- Gives a special monster for its pass, only ever once, and saves straight away.
function ShopService.giveSpecial(player: Player, special)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	local given = data.specialsGiven[special.id]
	giveSpecialTo(player, data, special)
	if not given then
		PlayerData.saveNow(player)
	end
end

local function checkOwnedPasses(player: Player)
	for _, pass in { Shop.doubleCash, Shop.doubleTraining, Shop.doublePower } do
		if pass.passId ~= 0 and ownsPass(player, pass) then
			setPassAttribute(player, pass.passId)
		end
	end
	-- Also covers a pass bought outside the game, from the Store page.
	for _, special in Specials do
		if special.passId and ownsPass(player, special) then
			ShopService.giveSpecial(player, special)
		end
	end
end

-- Passes another player gifted, and special monsters already had (bought or gifted), so the shop says OWNED.
local function restoreGifted(player: Player, data)
	for _, pass in Gifts.passes do
		if data.giftedPasses[pass.key] then
			player:SetAttribute(pass.attribute, true)
		end
	end
	for _, special in Specials do
		if special.passId and data.specialsGiven[special.id] then
			player:SetAttribute(`Owns{special.id}`, true)
		end
	end
end

-- PAID RANDOM ITEMS: the Prism Egg, lucky throws and Server Luck, a paid luck boost (Config/Shop). Roblox's policy can restrict them in a player's
-- region, and then they must not be offered. PolicyService is asked once per player when their data loads. Until
-- it answers, and if it never does, they count as restricted (not sold).
local PAID_RANDOM_ATTRIBUTE = "PaidRandomBlocked" -- on the player, so the shop's buttons can say UNAVAILABLE
local policyAllowed: { [Player]: boolean } = {}

local function isPaidRandom(productId: number): boolean
	if productId == Shop.prismEgg.productId or productId == Shop.serverLuck.productId then
		return true
	end
	for _, item in Shop.luckyThrows do
		if productId == item.productId or productId == item.dealProductId then
			return true
		end
	end
	return false
end

local function checkPaidRandomPolicy(player: Player)
	local blocked = true
	for attempt = 1, 3 do
		local ok, result = pcall(function()
			return PolicyService:GetPolicyInfoForPlayerAsync(player)
		end)
		if ok then
			blocked = result.ArePaidRandomItemsRestricted == true
			break
		end
		warn(`[ShopService] Couldn't check the paid random item policy for {player.Name} (try {attempt}): {result}`)
		if attempt == 3 or not player.Parent then
			break
		end
		task.wait(2 * attempt)
	end
	if not player.Parent then
		return
	end
	policyAllowed[player] = not blocked
	player:SetAttribute(PAID_RANDOM_ATTRIBUTE, blocked)
end

-- The client asks to buy a paid random item. The server checks the policy before it shows the prompt.
local function onBuyRandom(player: Player, productId: unknown)
	if typeof(productId) ~= "number" or productId == 0 or not isPaidRandom(productId) then
		return
	end
	if policyAllowed[player] ~= true then
		PlotService.notify(player, "Not available in your area", true)
		return
	end
	MarketplaceService:PromptProductPurchase(player, productId)
end

-- GIFT: a player asks to gift a product to another player here. Checked, remembered, then the server shows the
-- purchase prompt, so the receipt can be matched to the receiver.
local function onGift(player: Player, productId: unknown, receiverId: unknown)
	if typeof(productId) ~= "number" or typeof(receiverId) ~= "number" then
		return
	end
	local item = Gifts.find(productId)
	local receiver = Players:GetPlayerByUserId(receiverId)
	if not item or not receiver or receiver == player or not PlayerData.get(receiver) then
		return
	end
	if item.ownedAttribute and receiver:GetAttribute(item.ownedAttribute) then
		PlotService.notify(player, `{receiver.DisplayName} already has {item.name}`, true)
		return
	end
	if isPaidRandom(productId) and policyAllowed[player] ~= true then
		PlotService.notify(player, "Not available in your area", true)
		return
	end
	pendingGifts[player] = { productId = productId, to = receiver, at = os.clock() }
	MarketplaceService:PromptProductPurchase(player, productId)
end

-- A gift's prompt closed without buying: forget it, so a later purchase isn't taken for a gift.
local function onProductPromptFinished(userId: number, productId: number, purchased: boolean)
	local player = Players:GetPlayerByUserId(userId)
	local gift = player and pendingGifts[player]
	if gift and gift.productId == productId and not purchased then
		pendingGifts[player] = nil
	end
end

local function onPassPurchased(player: Player, passId: number, purchased: boolean)
	if purchased and passId ~= 0 and not table.find(Shop.ignorePassesFor, player.UserId) then
		setPassAttribute(player, passId)
		for _, special in Specials do
			if passId == special.passId then
				ShopService.giveSpecial(player, special)
			end
		end
	end
end

local function onClaimStarter(player: Player)
	local data = PlayerData.get(player)
	if not data or data.starterClaimed then
		return
	end
	local starter = Shop.starterDino
	data.starterClaimed = true
	IndexService.discover(player, starter.id, DinoStats.findOption(Biomes, starter.biomeId))
	PlotService.addCatch(player, { id = starter.id })
	remotes.StarterClaimed:FireClient(player, true)
end

-- The owner's gifts (Config/Shop gifts), each kept with the receipts so it's only ever given once.
local function giveGifts(player: Player, data)
	for _, gift in Shop.gifts do
		if table.find(gift.userIds, player.UserId) and not data.receipts[gift.id] then
			data.receipts[gift.id] = true
			ShopService.addLuckyThrows(player, data, gift.multiplier, gift.amount)
			PlotService.notify(player, `Gift: {gift.amount} Luck x{gift.multiplier} throws!`)
			PlayerData.saveNow(player)
		end
	end
end

-- The owner's special monsters (Config/Shop specialGifts). A special is only given once, so a pass owner keeps just one.
local function giveSpecialGifts(player: Player, data)
	for _, gift in Shop.specialGifts do
		if table.find(gift.userIds, player.UserId) and not data.receipts[gift.id] then
			data.receipts[gift.id] = true
			for _, special in Specials do
				if special.id == gift.special then
					ShopService.giveSpecial(player, special)
				end
			end
			PlayerData.saveNow(player)
		end
	end
end

local function onLoaded(player: Player, data)
	task.spawn(checkPaidRandomPolicy, player)
	resumeServerLuck()
	remotes.StarterClaimed:FireClient(player, data.starterClaimed)
	publishLuckyThrows(player, data)
	giveGifts(player, data)
	player:SetAttribute(DEAL_ATTRIBUTE, data.luckDealBought)
	restoreGifted(player, data)
	checkOwnedPasses(player)
	giveSpecialGifts(player, data)
end

function ShopService.start()
	makeRemotes()
	MarketplaceService.ProcessReceipt = ShopService.processReceipt
	MarketplaceService.PromptGamePassPurchaseFinished:Connect(onPassPurchased)
	MarketplaceService.PromptProductPurchaseFinished:Connect(onProductPromptFinished)
	remotes.ClaimStarter.OnServerEvent:Connect(onClaimStarter)
	remotes.Gift.OnServerEvent:Connect(onGift)
	remotes.BuyRandom.OnServerEvent:Connect(onBuyRandom)
	Players.PlayerRemoving:Connect(function(player)
		pendingGifts[player] = nil
		policyAllowed[player] = nil
	end)
	PlayerData.onLoaded(onLoaded)
	task.spawn(function()
		while true do
			task.wait(Shop.serverLuck.settleEvery)
			settleServerLuck()
		end
	end)
end

return ShopService
