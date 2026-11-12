-- Gifts for staying (Config/PlayGifts): free lucky throws after so many minutes of play, and a new player's own
-- first event. The server counts the seconds (only once the tutorial is finished) and gives everything itself;
-- clients only read the attributes: PlayGiftAt (server time the next free throw arrives), PlayGiftLuck (its
-- multiplier), PlayGiftsGiven (set when one is given, for the shout), FirstEventId and FirstEventEndsAt
-- (read by Config/Events).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Events = require(ReplicatedStorage.Shared.Config.Events)
local PlayGifts = require(ReplicatedStorage.Shared.Config.PlayGifts)
local PlayerData = require(script.Parent.PlayerData)
local ShopService = require(script.Parent.ShopService)
local TutorialService = require(script.Parent.TutorialService)

local PlayGiftService = {}

local TICK = 1 -- seconds
local DRIFT = 2 -- seconds the shown arrival time may be off before it's set again

local function finished(data): boolean
	return data.playGiftsGiven >= #PlayGifts.luckyThrows and data.firstEventDone
end

local function publish(player: Player, data)
	local nextThrow = PlayGifts.luckyThrows[data.playGiftsGiven + 1]
	if not nextThrow then
		player:SetAttribute("PlayGiftAt", nil)
		player:SetAttribute("PlayGiftLuck", nil)
		return
	end
	local at = workspace:GetServerTimeNow() + nextThrow.at - data.playGiftSeconds
	local shown = player:GetAttribute("PlayGiftAt")
	player:SetAttribute("PlayGiftLuck", nextThrow.multiplier)
	if not shown or math.abs(shown - at) > DRIFT then
		player:SetAttribute("PlayGiftAt", at)
	end
end

local function step(player: Player, data, seconds: number)
	if finished(data) or not TutorialService.finished(data) then
		return
	end
	data.playGiftSeconds += seconds

	local first = PlayGifts.firstEvent
	if not data.firstEventDone and data.playGiftSeconds >= first.at then
		data.firstEventDone = true
		if not Events.active() then
			player:SetAttribute("FirstEventId", first.id)
			player:SetAttribute("FirstEventEndsAt", workspace:GetServerTimeNow() + Events.seconds)
		end
	end

	local nextThrow = PlayGifts.luckyThrows[data.playGiftsGiven + 1]
	if nextThrow and data.playGiftSeconds >= nextThrow.at then
		data.playGiftsGiven += 1
		ShopService.addLuckyThrows(player, data, nextThrow.multiplier, 1)
		player:SetAttribute("PlayGiftsGiven", data.playGiftsGiven)
	end
	publish(player, data)
end

function PlayGiftService.start()
	task.spawn(function()
		local last = os.clock()
		while true do
			task.wait(TICK)
			local now = os.clock()
			for _, player in Players:GetPlayers() do
				local data = PlayerData.get(player)
				if data then
					step(player, data, now - last)
				end
			end
			last = now
		end
	end)
end

return PlayGiftService
