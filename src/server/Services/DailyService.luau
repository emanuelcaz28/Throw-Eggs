-- Daily reward (Config/Daily): one claim per UTC day gives a lucky throw (ShopService.addLuckyThrows). Each claim
-- moves the streak on (day 7 is the big one, then back to day 1), and a missed day only pauses it.
-- The client only asks to claim; the server checks the day.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Daily = require(ReplicatedStorage.Shared.Config.Daily)
local RemoteGuard = require(script.Parent.RemoteGuard)
local PlayerData = require(script.Parent.PlayerData)
local ShopService = require(script.Parent.ShopService)

local DailyService = {}

local CHECK_EVERY = 30 -- seconds; picks up midnight UTC for players who stay online

local claimRemote: RemoteEvent

local function today(): number
	return os.time() // Daily.daySeconds
end

-- The day the next claim gives (1 to 7), and whether it can be claimed now.
local function nextClaim(data): (number, boolean)
	local day = today()
	return data.dailyStreak % #Daily.days + 1, data.dailyLastDay < day
end

-- What the client shows: DailyDay is the day the next claim gives, or the one claimed today.
local function publish(player: Player, data)
	local nextDay, claimable = nextClaim(data)
	player:SetAttribute("DailyDay", if claimable then nextDay else data.dailyStreak)
	player:SetAttribute("DailyClaimable", claimable)
	player:SetAttribute("DailyNextAt", (today() + 1) * Daily.daySeconds)
end

local function onClaim(player: Player)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	local nextDay, claimable = nextClaim(data)
	if not claimable then
		return
	end
	local reward = Daily.days[nextDay]
	data.dailyStreak = nextDay
	data.dailyLastDay = today()
	ShopService.addLuckyThrows(player, data, reward.luckyThrow, 1)
	publish(player, data)
end

function DailyService.start()
	claimRemote = Instance.new("RemoteEvent")
	claimRemote.Name = "ClaimDaily"
	claimRemote.Parent = ReplicatedStorage
	RemoteGuard.connect(claimRemote, onClaim)
	PlayerData.onLoaded(publish)

	task.spawn(function()
		while true do
			task.wait(CHECK_EVERY)
			for _, player in Players:GetPlayers() do
				local data = PlayerData.get(player)
				if data then
					publish(player, data)
				end
			end
		end
	end)
end

return DailyService
