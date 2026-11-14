-- Funnel analytics for the Creator Dashboard (Analytics -> Funnels), logged only from the server so players can't fake
-- steps. Events only send from the published game on live servers; Studio play tests send nothing. Three funnels:
--   Onboarding (one-time): the new-player tutorial, step by step (TutorialService).
--   WorldProgress: the first time a player's egg lands in each world (ThrowService). One session per player.
--   RobuxPurchase: a purchase window closing, then whether it was bought (ShopService), named by product.
-- Never renumber a step once the game is published: the dashboard keeps history by step number. Add new steps at the end.
-- Also the Economy dashboard (every Cash source and sink) and an EconomyProblem watchdog: see ECONOMY below.
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

-- ECONOMY (Analytics -> Economy): every Cash source and sink, logged from the server where the cash changes.
-- Sources: plot income (summed and sent once a minute: one event a second per player would hit Roblox's rate limit),
-- selling monsters, Robux cash packs, offline earnings. Sinks: rack upgrades, eggs, plot upgrades, feeding.
-- Never rename an item once published: the dashboard groups history by name.
-- Watchdog: each change is checked against the last balance seen. Cash that changed with no logged reason (a code path
-- that skips these calls), went below zero, or isn't a number logs an "EconomyProblem" custom event (Analytics ->
-- Custom Events, split by CustomField01 = reason) and a warning in the server log. Each reason logs once per player
-- per session.
local CURRENCY = "Cash"
local INCOME_FLUSH = 60 -- seconds of plot income summed into one event
local FIELD2 = Enum.AnalyticsCustomFieldKeys.CustomField02.Name

type Wallet = { expected: number?, pendingIncome: number, incomeSince: number, balance: number, reported: { [string]: boolean } }
local wallets: { [Player]: Wallet } = {}

local function walletOf(player: Player): Wallet
	local wallet = wallets[player]
	if not wallet then
		wallet = { pendingIncome = 0, incomeSince = os.clock(), balance = 0, reported = {} }
		wallets[player] = wallet
	end
	return wallet
end

local function problem(player: Player, reason: string, item: string, detail: string)
	local wallet = walletOf(player)
	if wallet.reported[reason] then
		return
	end
	wallet.reported[reason] = true
	warn(`Economy problem for {player.Name}: {reason} ({item}) {detail}`)
	safely(function()
		AnalyticsService:LogCustomEvent(player, "EconomyProblem", 1, { [FIELD1] = reason, [FIELD2] = item })
	end)
end

-- Checks the new balance against the last one seen plus this change (delta: + earned, - spent).
local function check(player: Player, delta: number, balance: number, item: string)
	local wallet = walletOf(player)
	if balance ~= balance or math.abs(balance) == math.huge then
		problem(player, "Cash not a number", item, tostring(balance))
	elseif balance < 0 then
		problem(player, "Negative cash", item, tostring(balance))
	elseif wallet.expected then
		local drift = balance - (wallet.expected + delta)
		if math.abs(drift) > 1 + math.abs(balance) * 1e-9 then -- doubles round on big balances
			problem(player, "Untracked cash change", item, `off by {drift}`)
		end
	end
	wallet.expected = balance
	wallet.balance = balance
end

local function logEconomy(player: Player, flow: Enum.AnalyticsEconomyFlowType, amount: number, balance: number,
	transaction: Enum.AnalyticsEconomyTransactionType, item: string)
	if not (amount > 0) or amount == math.huge or balance ~= balance or math.abs(balance) == math.huge then
		return -- check() reports bad numbers; Roblox rejects them
	end
	safely(function()
		AnalyticsService:LogEconomyEvent(player, flow, CURRENCY, amount, balance, transaction.Name, item)
	end)
end

local function flushIncome(player: Player)
	local wallet = wallets[player]
	if not wallet or wallet.pendingIncome <= 0 then
		return
	end
	local amount = wallet.pendingIncome
	wallet.pendingIncome = 0
	wallet.incomeSince = os.clock()
	logEconomy(player, Enum.AnalyticsEconomyFlowType.Source, amount, wallet.balance,
		Enum.AnalyticsEconomyTransactionType.Gameplay, "Plot Income")
end

-- The plot's per-second income was paid. balance: the player's cash after it.
function Analytics.income(player: Player, amount: number, balance: number)
	check(player, amount, balance, "Plot Income")
	local wallet = walletOf(player)
	wallet.pendingIncome += amount
	if os.clock() - wallet.incomeSince >= INCOME_FLUSH then
		flushIncome(player)
	end
end

-- Cash earned. how: "Gameplay", "IAP" or "TimedReward" (Enum.AnalyticsEconomyTransactionType). item: what paid it.
function Analytics.cashIn(player: Player, amount: number, balance: number, how: string, item: string)
	check(player, amount, balance, item)
	logEconomy(player, Enum.AnalyticsEconomyFlowType.Source, amount, balance,
		Enum.AnalyticsEconomyTransactionType[how], item)
end

-- Cash spent. how: "Shop" or "ContextualPurchase". item: what was bought.
function Analytics.cashOut(player: Player, amount: number, balance: number, how: string, item: string)
	check(player, -amount, balance, item)
	logEconomy(player, Enum.AnalyticsEconomyFlowType.Sink, amount, balance,
		Enum.AnalyticsEconomyTransactionType[how], item)
end

-- Cash changed on purpose without being a real source or sink (an admin's test cash): the watchdog starts over here.
function Analytics.cashReset(player: Player, balance: number)
	walletOf(player).expected = balance
	walletOf(player).balance = balance
end

Players.PlayerRemoving:Connect(function(player)
	worldLogged[player] = nil
	flushIncome(player)
	wallets[player] = nil
end)

return Analytics
