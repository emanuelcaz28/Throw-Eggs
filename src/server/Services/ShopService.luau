-- The Robux shop: Game Passes, Server Luck, lucky throws, cash and Throw Power packs and the free starter dino. Roblox retries a
-- purchase until told it was granted, so each receipt is saved with the player's data
-- before saying so. That way a purchase is never lost or given twice.
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local IndexService = require(script.Parent.IndexService)
local LuckBoosts = require(ReplicatedStorage.Shared.LuckBoosts)
local LuckyThrows = require(ReplicatedStorage.Shared.LuckyThrows)
local PlayerData = require(script.Parent.PlayerData)
local PlotService = require(script.Parent.PlotService)
local Shop = require(ReplicatedStorage.Shared.Config.Shop)
local TrainingService = require(script.Parent.TrainingService)

local ShopService = {}

local LUCK_ATTRIBUTE = "ServerLuckEndsAt" -- set on ReplicatedStorage so every client can show the timer
local DEAL_ATTRIBUTE = "LuckDealBought" -- set on the player once the one-time Luck x100 deal is used

local remotes: { [string]: RemoteEvent } = {}

local function makeRemotes()
	local folder = Instance.new("Folder")
	folder.Name = "ShopRemotes"
	for _, name in { "ClaimStarter", "StarterClaimed" } do
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

local function grantServerLuck()
	local now = workspace:GetServerTimeNow()
	local start = math.max(ReplicatedStorage:GetAttribute(LUCK_ATTRIBUTE) or 0, now)
	ReplicatedStorage:SetAttribute(LUCK_ATTRIBUTE, start + Shop.serverLuck.seconds)
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

-- Uses up the biggest lucky throw owned and returns its multiplier, or 1 with none.
function ShopService.takeLuckyThrow(player: Player, data): number
	for _, multiplier in LuckyThrows.tiers do
		local key = tostring(multiplier)
		if (data.luckyThrows[key] or 0) > 0 then
			data.luckyThrows[key] -= 1
			publishLuckyThrows(player, data)
			return multiplier
		end
	end
	return 1
end

-- What each Developer Product gives, by product id.
local function grantFor(productId: number): ((Player, any) -> ())?
	if productId == 0 then
		return nil
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
		grant(player, data)
		data.receipts[info.PurchaseId] = true
	end
	if PlayerData.saveNow(player) then
		return Enum.ProductPurchaseDecision.PurchaseGranted
	end
	return Enum.ProductPurchaseDecision.NotProcessedYet
end

local function setPassAttribute(player: Player, passId: number)
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

local function checkOwnedPasses(player: Player)
	for _, pass in { Shop.doubleCash, Shop.doubleTraining, Shop.doublePower } do
		if pass.passId ~= 0 then
			local ok, owns = pcall(function()
				return MarketplaceService:UserOwnsGamePassAsync(player.UserId, pass.passId)
			end)
			if ok and owns then
				setPassAttribute(player, pass.passId)
			elseif not ok then
				warn(`[ShopService] Couldn't check {pass.name} for {player.Name}: {owns}`)
			end
		end
	end
end

local function onPassPurchased(player: Player, passId: number, purchased: boolean)
	if purchased and passId ~= 0 then
		setPassAttribute(player, passId)
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

local function onLoaded(player: Player, data)
	remotes.StarterClaimed:FireClient(player, data.starterClaimed)
	publishLuckyThrows(player, data)
	player:SetAttribute(DEAL_ATTRIBUTE, data.luckDealBought)
	checkOwnedPasses(player)
end

function ShopService.start()
	makeRemotes()
	MarketplaceService.ProcessReceipt = ShopService.processReceipt
	MarketplaceService.PromptGamePassPurchaseFinished:Connect(onPassPurchased)
	remotes.ClaimStarter.OnServerEvent:Connect(onClaimStarter)
	PlayerData.onLoaded(onLoaded)
end

return ShopService
