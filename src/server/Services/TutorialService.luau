-- The new-player tutorial's server side (Config/Tutorial). It decides the two tutorial catches, so the second is
-- always better than the first, and keeps the tutorial's progress in the save (data.tutorial), so neither can be
-- farmed: the guarantees count the save's first two throws ever, whatever the steps say. The client shows the steps
-- and reports finished ones (TutorialRemotes.Step); the steps change nothing but the free feed, which is one feed once.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)
local Tutorial = require(ReplicatedStorage.Shared.Config.Tutorial)
local RemoteGuard = require(script.Parent.RemoteGuard)
local Analytics = require(script.Parent.Analytics)
local PlayerData = require(script.Parent.PlayerData)

local TutorialService = {}

local POLL = 0.25 -- seconds between updates of the attributes the steps watch

local stepRemote: RemoteEvent

-- The save's tutorial record, made on first use. A save from before the tutorial existed (Config/Save default false)
-- that has played already starts it finished: only new players see it.
local function stateOf(data)
	if typeof(data.tutorial) ~= "table" then
		local played = (data.totalCaught or 0) > 0 or #data.dinos > 0
		data.tutorial = {
			step = if played then Tutorial.doneStep else 1, -- the step being shown; doneStep = finished
			throws = if played then 2 else 0, -- tutorial throws used, 0 to 2
			firstIncome = 0, -- $/s of the first tutorial catch, which the second must beat
			firstKey = nil, -- dino keys of the two tutorial catches, for the feeding step
			secondKey = nil,
			fedFree = false, -- the free feed has been used
		}
	end
	return data.tutorial
end

-- Where one of the tutorial's monsters is: "plot", "backpack" or "gone" (sold or fed), and its name and Chonk level.
local function monsterState(data, key: number?): (string?, string?, number?)
	if not key then
		return nil, nil, nil
	end
	for _, entry in data.dinos do
		if entry.key == key then
			local stats = DinoStats.describe(entry)
			return if entry.onPlot then "plot" else "backpack", stats and stats.name, entry.chonk or 0
		end
	end
	return "gone", nil, nil
end

-- Attributes the client's TutorialController reads: the tutorial's progress, and while it runs, what its steps ask for.
local function publish(player: Player, data)
	local state = stateOf(data)
	if state.step < Tutorial.doneStep then
		local first, firstName = monsterState(data, state.firstKey)
		local second, secondName, secondChonk = monsterState(data, state.secondKey)
		player:SetAttribute("TutorialFirst", first)
		player:SetAttribute("TutorialFirstName", firstName)
		player:SetAttribute("TutorialSecond", second)
		player:SetAttribute("TutorialSecondName", secondName)
		player:SetAttribute("TutorialSecondChonk", secondChonk)
		local eggs = 0
		for _ in data.ownedEggs do
			eggs += 1
		end
		player:SetAttribute("TutorialEggs", eggs)
		player:SetAttribute("TutorialUpgrades", data.xpUpgrades)
	end
	player:SetAttribute("TutorialStep", state.step)
	player:SetAttribute("TutorialThrows", state.throws)
	player:SetAttribute("TutorialFirstKey", state.firstKey)
	player:SetAttribute("TutorialSecondKey", state.secondKey)
	-- The monster whose next feed is free, so the Feed panel can say so.
	local free = Tutorial.freeFeed and not state.fedFree and state.step < Tutorial.doneStep and state.secondKey
	player:SetAttribute("TutorialFreeFeed", if free then state.secondKey else nil)
end

-- What the next throw's tutorial guarantee is, or nil once both tutorial throws are used. rarest(count) is the lowest
-- rank among the pool's `count` rarest monsters before its prizes (ThrowService). Returns { kind = "first", rank } or
-- { kind = "second", minRank }.
function TutorialService.planThrow(data, pool: string, rarest: (number) -> number)
	local state = stateOf(data)
	local dinos = Dinos[pool]
	if not dinos then
		return nil
	end
	local lastPlain = rarest(1) -- the map's rarest monster before its prizes
	if state.throws == 0 then
		return { kind = "first", rank = math.clamp(Tutorial.firstThrow.rank, 1, lastPlain) }
	elseif state.throws == 1 then
		local minRank = rarest(Tutorial.secondThrow.rarest)
		-- Never below the first catch: the most common monster here that earns more than it. Colour and size only add.
		for rank, dino in dinos do
			if dino.income > state.firstIncome then
				minRank = math.max(minRank, rank)
				break
			end
		end
		return { kind = "second", minRank = math.min(minRank, lastPlain) }
	end
	return nil
end

-- The first tutorial catch: exactly this monster, no colour or size, in DinoRoll.rollCatch's shape.
function TutorialService.plainCatch(pool: string, rank: number)
	local dino = Dinos[pool][rank]
	local stats = DinoStats.describe({ id = dino.id })
	return { id = dino.id, rank = rank, name = stats.name, oneIn = stats.oneIn, income = stats.income }
end

-- Whether the tutorial is over (or was never shown).
function TutorialService.finished(data): boolean
	return stateOf(data).step >= Tutorial.doneStep
end

-- Whether the next catch goes onto the player's head for them to place, instead of straight onto the base.
function TutorialService.carriesCatch(data): boolean
	return Tutorial.carryCatches and stateOf(data).throws < 2
end

-- After a throw's catch is stored: counts the tutorial's throws (the two set catches, then the throw with the new
-- egg that ends it, Config/Tutorial steps).
function TutorialService.recordCatch(player: Player, data, catch, key: number?)
	local state = stateOf(data)
	if state.throws >= Tutorial.throwsCounted then
		return
	end
	state.throws += 1
	if state.throws == 1 then
		state.firstIncome = catch.income
		state.firstKey = key
	elseif state.throws == 2 then
		state.secondKey = key
	end
	publish(player, data)
end

-- Whether feeding this monster costs nothing: the tutorial's one free feed, for its second catch.
function TutorialService.isFreeFeed(data, targetKey: number): boolean
	local state = stateOf(data)
	return Tutorial.freeFeed and not state.fedFree and state.step < Tutorial.doneStep and state.secondKey == targetKey
end

function TutorialService.usedFreeFeed(player: Player, data)
	stateOf(data).fedFree = true
	publish(player, data)
end

-- The client finished steps up to `step` - 1 and now shows `step`. Steps only go forward.
local function onStep(player: Player, step: any)
	local data = PlayerData.get(player)
	if not data or typeof(step) ~= "number" or step ~= step or step % 1 ~= 0 then -- step ~= step is only true for NaN
		return
	end
	local state = stateOf(data)
	if step > state.step and step <= Tutorial.doneStep then
		local from = state.step
		state.step = step
		publish(player, data)
		Analytics.tutorialAdvanced(player, from, step)
	end
end

function TutorialService.start()
	local folder = Instance.new("Folder")
	folder.Name = "TutorialRemotes"
	stepRemote = Instance.new("RemoteEvent")
	stepRemote.Name = "Step"
	stepRemote.Parent = folder
	folder.Parent = ReplicatedStorage
	RemoteGuard.connect(stepRemote, onStep)
	PlayerData.onLoaded(publish)
	-- The onboarding funnel's first step, for players who haven't finished the tutorial (Analytics).
	PlayerData.onLoaded(function(player, data)
		if stateOf(data).step < Tutorial.doneStep then
			Analytics.tutorialJoined(player)
		end
	end)
	-- While a player is in the tutorial, keep what its steps watch up to date (unchanged values send nothing).
	task.spawn(function()
		while true do
			task.wait(POLL)
			for _, player in Players:GetPlayers() do
				local data = PlayerData.get(player)
				if data and stateOf(data).step < Tutorial.doneStep then
					publish(player, data)
				end
			end
		end
	end)
end

return TutorialService
