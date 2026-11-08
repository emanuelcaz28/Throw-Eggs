-- The player's settings on their client (Config/Settings): the values, a changed event, and the two volume groups every
-- sound effect and the music play through, so the sliders turn all of them up and down at once. The saved values
-- arrive as player attributes from SettingsService; until they do, the defaults apply. Display only.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")

local Settings = require(ReplicatedStorage.Shared.Config.Settings)

local SettingsState = {}

local player = Players.LocalPlayer
local values = table.clone(Settings.defaults)
local changedEvent = Instance.new("BindableEvent")
SettingsState.changed = changedEvent.Event -- (key, value)

local function group(name: string): SoundGroup
	local made = Instance.new("SoundGroup")
	made.Name = name
	made.Parent = SoundService
	return made
end

SettingsState.musicGroup = group("MusicVolume")
SettingsState.sfxGroup = group("SfxVolume")

local function apply()
	SettingsState.musicGroup.Volume = values.music / 100
	SettingsState.sfxGroup.Volume = values.sfx / 100
end
apply()

function SettingsState.get(key: string)
	return values[key]
end

-- Changes a setting on this client at once (the slider following the finger); SettingsController tells the server.
function SettingsState.set(key: string, value)
	if values[key] == value then
		return
	end
	values[key] = value
	apply()
	changedEvent:Fire(key, value)
end

local adopted = false
local function adopt()
	if adopted or player:GetAttribute("SettingsLoaded") ~= true then
		return
	end
	adopted = true
	for key in Settings.defaults do
		local saved = player:GetAttribute("Setting_" .. key)
		if saved ~= nil then
			SettingsState.set(key, saved)
		end
	end
end

function SettingsState.start()
	adopt()
	player:GetAttributeChangedSignal("SettingsLoaded"):Connect(adopt)
end

return SettingsState
