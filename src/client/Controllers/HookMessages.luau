-- After a reveal: says why a catch was guaranteed (the new-map gift or pity, Config/Hooks; never the surprise gift) and
-- "SO CLOSE!" when the egg landed just short of the next world. The server decides all of it; this
-- only shows what the catch says.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local DeepEnd = require(ReplicatedStorage.Shared.Config.DeepEnd)
local Hooks = require(ReplicatedStorage.Shared.Config.Hooks)
local PopText = require(ReplicatedStorage.Shared.PopText)
local RevealController = require(script.Parent.RevealController)

local HookMessages = {}

local FIRST_DELAY = 0.4 -- after the reveal closes, so the screen is back
local NEXT_DELAY = 2.6 -- between two messages from the same catch

function HookMessages.start()
	RevealController.finished:Connect(function(catch)
		local messages = {}
		if catch.guarantee == "newMap" then
			table.insert(messages, { "NEW WORLD BONUS!", "Your first egg in a new world is always a rare one" })
		elseif catch.guarantee == "jackpot" then
			table.insert(messages, { "JACKPOT STREAK!", `{Hooks.jackpotPity.throws} throws without this world's rarest, so here it is` })
		elseif catch.guarantee == "pity" then
			table.insert(messages, { "LUCKY STREAK!", `{Hooks.pity.throws} throws without a rare, so this one was guaranteed` })
		end
		if catch.newDepth then
			local boost = 1 + DeepEnd.boostPerDepth * catch.newDepth
			table.insert(messages, { `DEPTH {catch.newDepth}!`, `Rare colours and sizes x{boost} on throws this deep` })
		end
		if catch.almostThere then
			table.insert(messages, { "SO CLOSE!", `{catch.almostThere.studs} studs short of {catch.almostThere.name}` })
		end
		for index, message in messages do
			task.delay(FIRST_DELAY + (index - 1) * NEXT_DELAY, PopText.shout, message[1], message[2])
		end
	end)
end

return HookMessages
