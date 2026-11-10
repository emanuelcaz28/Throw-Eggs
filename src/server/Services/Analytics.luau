-- Funnel analytics for the Creator Dashboard (Analytics -> Funnels), logged only from the server so players can't fake
-- steps. Events only send from the published game on live servers; Studio play tests send nothing. Three funnels:
--   Onboarding (one-time): the new-player tutorial, step by step (TutorialService).
--   WorldProgress: the first time a player's egg lands in each world (ThrowService). One session per player.
--   RobuxPurchase: a purchase window closing, then whether it was bought (ShopService), named by product.
-- Never renumber a step once the game is published: the dashboard keeps history by step number. Add new steps at the end.
local AnalyticsService = game:GetService("AnalyticsService")
local HttpService = game:GetService("HttpService")
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local Tutorial = require(ReplicatedStorage.Shared.Config.Tutorial)

local Analytics = {}

local FIELD1 = Enum.AnalyticsCustomFieldKeys.CustomField01.Name

-- Onboarding step names. Step 1 is the join; the tutorial's step N (Config/Tutorial steps) finishing is step N + 1.
local ONBOARDING = {
	"Player Joined",
	"First Throw", -- throw
	"Placed First Monster", -- place
	"Second Throw", -- throw2
	"Placed Second Monster", -- place2
	"Bought Rack Upgrade", -- upgrade
	"Trained", -- train
	"Bought New Egg", -- egg
	"Tutorial Done", -- throw3
}
assert(#ONBOARDING == #Tutorial.steps + 1, "Analytics: ONBOARDING names must match Config/Tutorial steps")

local worldLogged: { [Player]: number } = {} -- the farthest world logged this session, per player

-- Logs without ever breaking the game: an analytics error must not stop a throw, a tutorial step or a purchase.
local function safely(fn: () -> ())
	local ok, err = pcall(fn)
	if not ok then
		warn("Analytics: " .. tostring(err))
	end
end

-- A new player's save loaded with the tutorial not finished: the funnel's anchor.
function Analytics.tutorialJoined(player: Player)
	safely(function()
		AnalyticsService:LogOnboardingFunnelStepEvent(player, 1, ONBOARDING[1])
	end)
end

-- The tutorial moved from showing step `from` to showing step `to` (Config/Tutorial; doneStep = finished): every step
-- in between was finished. Steps only go forward (TutorialService checks), and each logs once per player anyway.
function Analytics.tutorialAdvanced(player: Player, from: number, to: number)
	safely(function()
		for finished = from, to - 1 do
			local step = finished + 1
			local name = ONBOARDING[step]
			if name then
				AnalyticsService:LogOnboardingFunnelStepEvent(player, step, name)
			end
		end
	end)
end

-- A throw landed in this world (a Config/Biomes entry). Logs the world as a step the first time this session it's the
-- farthest yet; the dashboard counts each step once per player, and a later step fills in the earlier ones.
function Analytics.landedIn(player: Player, biome)
	local index = table.find(Biomes, biome)
	if not index or index <= (worldLogged[player] or 0) then
		return
	end
	worldLogged[player] = index
	safely(function()
		AnalyticsService:LogFunnelStepEvent(
			player,
			"WorldProgress",
			tostring(player.UserId),
			index,
			`World {index} - {biome.name}`
		)
	end)
end

-- Product and Game Pass names, looked up once from Roblox; the id stands in while the lookup fails.
local names: { [string]: string } = {}
local function nameOf(id: number, infoType: Enum.InfoType): string
	local key = `{infoType.Name}{id}`
	if not names[key] then
		local ok, info = pcall(MarketplaceService.GetProductInfo, MarketplaceService, id, infoType)
		names[key] = if ok and info and info.Name then info.Name else `{infoType.Name} {id}`
	end
	return names[key]
end

-- A Robux purchase window closed: step 1, and step 2 if bought. Filter by Item in the dashboard (custom field 1).
function Analytics.purchasePromptClosed(player: Player, id: number, infoType: Enum.InfoType, purchased: boolean)
	if id == 0 then
		return
	end
	task.spawn(function() -- nameOf may wait on Roblox
		local fields = { [FIELD1] = "Item - " .. nameOf(id, infoType) }
		local sessionId = HttpService:GenerateGUID(false)
		safely(function()
			AnalyticsService:LogFunnelStepEvent(player, "RobuxPurchase", sessionId, 1, "Prompt Opened", fields)
			if purchased then
				AnalyticsService:LogFunnelStepEvent(player, "RobuxPurchase", sessionId, 2, "Purchased", fields)
			end
		end)
	end)
end

Players.PlayerRemoving:Connect(function(player)
	worldLogged[player] = nil
end)

return Analytics
