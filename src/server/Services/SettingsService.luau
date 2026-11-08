-- Keeps each player's settings (Config/Settings) in their save and tells their client the saved values once they load.
-- The client only asks to change one setting at a time; the server checks the name and the value and clamps it.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Settings = require(ReplicatedStorage.Shared.Config.Settings)
local PlayerData = require(script.Parent.PlayerData)

local SettingsService = {}

-- Fills in any setting an older save doesn't have yet.
local function complete(data)
	if typeof(data.settings) ~= "table" then
		data.settings = {}
	end
	for key, default in Settings.defaults do
		if typeof(data.settings[key]) ~= typeof(default) then
			data.settings[key] = default
		end
	end
	return data.settings
end

local function publish(player: Player, data)
	local settings = complete(data)
	for key in Settings.defaults do
		player:SetAttribute("Setting_" .. key, settings[key])
	end
	player:SetAttribute("SettingsLoaded", true)
end

local function onSet(player: Player, key: any, value: any)
	local data = PlayerData.get(player)
	if not data or typeof(key) ~= "string" then
		return
	end
	local default = Settings.defaults[key]
	if default == nil then
		return
	end
	if typeof(default) == "number" then
		if typeof(value) ~= "number" or value ~= value then
			return
		end
		value = math.clamp(math.floor(value + 0.5), 0, 100)
	elseif typeof(value) ~= "boolean" then
		return
	end
	complete(data)[key] = value
end

function SettingsService.start()
	local remote = Instance.new("RemoteEvent")
	remote.Name = "SetSetting"
	remote.Parent = ReplicatedStorage
	remote.OnServerEvent:Connect(onSet)
	PlayerData.onLoaded(publish)
end

return SettingsService
