-- Daily tasks (Config/Daily tasks): three small goals that start again each UTC day. Finishing all three gives the same timed
-- x2 XP as completing a world in the Index, with no lasting reward [Owner, 2026-11-07]. The server counts everything.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Daily = require(ReplicatedStorage.Shared.Config.Daily)
local Index = require(ReplicatedStorage.Shared.Config.Index)
local IndexService = require(script.Parent.IndexService)
local PlayerData = require(script.Parent.PlayerData)
local PlotService = require(script.Parent.PlotService)

local DailyTasks = {}

local CHECK_EVERY = 30 -- seconds; picks up midnight UTC for players who stay online

-- Starts the day's tasks over once the day has changed.
local function freshen(data)
	local day = os.time() // Daily.daySeconds
	if data.dailyTaskDay ~= day then
		data.dailyTaskDay = day
		data.dailyTaskCounts = {}
		data.dailyTasksDone = false
	end
end

local function publish(player: Player, data)
	freshen(data)
	for _, task in Daily.tasks do
		player:SetAttribute(`DailyTask_{task.id}`, data.dailyTaskCounts[task.id] or 0)
	end
	player:SetAttribute("DailyTasksDone", data.dailyTasksDone)
end

-- One more of a task ("perfects", "bubbles", "catches").
function DailyTasks.count(player: Player, id: string)
	local data = PlayerData.get(player)
	if not data then
		return
	end
	freshen(data)
	if data.dailyTasksDone then
		return
	end
	local finished, reachedGoal = 0, false
	for _, task in Daily.tasks do
		local count = data.dailyTaskCounts[task.id] or 0
		if task.id == id and count < task.goal then
			count += 1
			data.dailyTaskCounts[id] = count
			reachedGoal = count == task.goal
		end
		finished += if count >= task.goal then 1 else 0
	end
	if finished == #Daily.tasks then
		data.dailyTasksDone = true
		data.xpBoostEndsAt = math.max(data.xpBoostEndsAt, os.time()) + Daily.taskBoostSeconds
		IndexService.publishXpBoost(player, data)
		PlotService.notify(player, `Daily tasks done! x{Index.xpBoost.multiplier} XP for {Daily.taskBoostSeconds // 60} minutes`)
	elseif reachedGoal then
		PlotService.notify(player, `Daily task done: {finished} of {#Daily.tasks}`)
	end
	publish(player, data)
end

function DailyTasks.start()
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

return DailyTasks
