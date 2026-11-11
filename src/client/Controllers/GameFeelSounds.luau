-- Sounds for the game's small moments that had none [Owner, 2026-11-10; docs/GROWTH_PLAYBOOK.md "action and
-- response": every action needs instant feedback]: each squat, a power bar filling, spending and earning cash, putting
-- a monster down, a tutorial step done. It only listens (player attributes and the own plot), so the systems it sounds
-- for stay untouched. The NEW discovery sound is played by RevealController. Display only; sounds in Config/UiSounds.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PopText = require(ReplicatedStorage.Shared.PopText)
local UiSounds = require(ReplicatedStorage.Shared.Config.UiSounds)
local Sfx = require(script.Parent.Sfx)

local GameFeelSounds = {}

local player = Players.LocalPlayer

local lastAt: { [string]: number } = {}
-- Plays a moment unless the same one just played (a big sale, Equip Best putting many down at once).
local function play(name: string, pitchShift: number?)
	local now = os.clock()
	if now - (lastAt[name] or 0) < UiSounds.cashMinGap then
		return
	end
	lastAt[name] = now
	Sfx.play(name, pitchShift)
end

local function number(name: string): number
	local value = player:GetAttribute(name)
	return if typeof(value) == "number" then value else 0
end

local function watchCash()
	local last: number? = nil
	player:GetAttributeChangedSignal("Cash"):Connect(function()
		local cash = number("Cash")
		if last then
			local change = cash - last
			local tick = number("Income")
			if change < 0 then
				play("purchase")
			elseif change > 0 and math.abs(change - tick) > math.max(1, tick * 0.001) then
				-- The per-second income is left out, the same rule as the floating +$ (PlotController).
				play("cash")
			end
		end
		last = cash
	end)
	last = number("Cash")
end

local function watchTraining()
	local lastXp = number("TrainingXp")
	local lastLevel = number("TrainingLevel")
	player:GetAttributeChangedSignal("TrainingLevel"):Connect(function()
		local level = number("TrainingLevel")
		if level > lastLevel then
			play("powerUp")
		end
		lastLevel = level
	end)
	player:GetAttributeChangedSignal("TrainingXp"):Connect(function()
		local xp = number("TrainingXp")
		if xp > lastXp and player:GetAttribute("IsTraining") == true then
			local needed = math.max(number("TrainingXpNeeded"), 1)
			Sfx.play("squat", 1 + UiSounds.squatClimb * math.clamp(xp / needed, 0, 1))
		end
		lastXp = xp
	end)
end

local function watchTutorial()
	local lastStep = number("TutorialStep")
	player:GetAttributeChangedSignal("TutorialStep"):Connect(function()
		local step = number("TutorialStep")
		if lastStep > 0 and step > lastStep then
			play("step")
		end
		lastStep = step
	end)
end

-- A monster put down on the player's plot: the server counts successful put-downs (PlotService PlacedTick). Watching the
-- Statues folder missed them, because the plot's statues are rebuilt from scratch on every change.
local function watchPlot()
	local last = number("PlacedTick")
	player:GetAttributeChangedSignal("PlacedTick"):Connect(function()
		local tick = number("PlacedTick")
		if tick > last then
			Sfx.play("place") -- not through play(): two quick put-downs both sound
		end
		last = tick
	end)
end

function GameFeelSounds.start()
	Sfx.preload()
	PopText.onShout = function()
		Sfx.play("popup")
	end
	watchCash()
	watchTraining()
	watchTutorial()
	watchPlot()
end

return GameFeelSounds
