-- After a reveal: says why a catch was guaranteed (the new-map gift or pity, Config/Hooks) and
-- "SO CLOSE!" when the egg landed just short of the next world. The server decides all of it; this
-- only shows what the catch says.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

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
		elseif catch.guarantee == "pity" then
			table.insert(messages, { "LUCKY STREAK!", `{Hooks.pity.throws} throws without a rare, so this one was guaranteed` })
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
