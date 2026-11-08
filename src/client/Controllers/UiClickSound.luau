-- The click on the buttons of the shop and the index [Owner, 2026-11-07: only those two]: it listens for any button
-- that shows up on screen, so new buttons there click without being touched, and checks which screen a button
-- is in when it's tapped (Config/UiSounds clickScreens). A button with the attribute NoClickSound stays quiet.
-- Display only.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local UiSounds = require(ReplicatedStorage.Shared.Config.UiSounds)
local SoundPool = require(script.Parent.SoundPool)

local UiClickSound = {}

local hooked = setmetatable({}, { __mode = "k" })
local random = Random.new()

local function click()
	-- From loaded copies (SoundPool): a new Sound each tap had to load first, so the click came late.
	SoundPool.play(UiSounds.click, UiSounds.clickVolume, random:NextNumber(UiSounds.clickPitch[1], UiSounds.clickPitch[2]))
end

local function wantsClick(object: GuiButton): boolean
	local screen = object:FindFirstAncestorOfClass("ScreenGui")
	return screen ~= nil and table.find(UiSounds.clickScreens, screen.Name) ~= nil and not object:GetAttribute("NoClickSound")
end

local function hook(object: Instance)
	if not object:IsA("GuiButton") or hooked[object] then
		return
	end
	hooked[object] = true
	-- A mouse clicks on the press, not the release, so it sounds the moment the button goes down. Touch and gamepad
	-- still click on Activated, so dragging a list on a phone doesn't click.
	object.InputBegan:Connect(function(input)
		if input.UserInputType == Enum.UserInputType.MouseButton1 and object.Active and wantsClick(object) then
			click()
		end
	end)
	object.Activated:Connect(function(input)
		if input and input.UserInputType == Enum.UserInputType.MouseButton1 then
			return -- already clicked on the press
		end
		if wantsClick(object) then
			click()
		end
	end)
end

function UiClickSound.start()
	SoundPool.preload({ UiSounds.click })

	local gui = Players.LocalPlayer:WaitForChild("PlayerGui")
	for _, object in gui:GetDescendants() do
		hook(object)
	end
	gui.DescendantAdded:Connect(hook)
end

return UiClickSound
