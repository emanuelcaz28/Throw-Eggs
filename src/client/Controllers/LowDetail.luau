-- Low detail (the Settings switch, Config/Settings lowDetail) [Owner, 2026-11-13: a switch the player turns on, never
-- automatic]. For slow phones and old computers: this player's own screen drops the things that cost the most and
-- matter the least. Nothing changes for anyone else, and nothing about the game itself (odds, money, timing).
-- Here: the screen glow and sun rays, and the map's shadows. Elsewhere, by asking LowDetail.on(): the moving props
-- stand still (PropMotionController), the clouds go (SkyController) and far monsters move less smoothly
-- (DinoLifeController). Turning it off puts everything back.
local Lighting = game:GetService("Lighting")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Settings = require(ReplicatedStorage.Shared.Config.Settings)
local SettingsState = require(script.Parent.SettingsState)

local LowDetail = {}

local look = Settings.lowDetailLook

function LowDetail.on(): boolean
	return SettingsState.get("lowDetail") == true
end

-- The screen effects (made by the server's LightingService, so they can arrive after this starts).
local function applyEffects()
	local on = LowDetail.on()
	for _, name in look.effectsOff do
		local effect = Lighting:FindFirstChild(name)
		if effect and effect:IsA("PostEffect") then
			effect.Enabled = not on
		end
	end
end

-- The map's shadows. The world streams in round the player, so parts keep arriving: each is done as it comes, and
-- remembered (while it exists) so turning the switch off gives its shadow back.
local shadowless: { [BasePart]: boolean } = setmetatable({}, { __mode = "k" }) :: any
local arriving: RBXScriptConnection? = nil
local run = 0 -- goes up at every switch, so a pass that is still working knows to stop

local function dropShadow(part: Instance)
	if part:IsA("BasePart") and part.CastShadow then
		shadowless[part] = true
		part.CastShadow = false
	end
end

local function applyShadows()
	run += 1
	local mine = run
	if arriving then
		arriving:Disconnect()
		arriving = nil
	end
	task.spawn(function()
		if LowDetail.on() then
			local map = workspace:WaitForChild("Map")
			if run ~= mine then
				return
			end
			arriving = map.DescendantAdded:Connect(dropShadow)
			for index, part in map:GetDescendants() do
				dropShadow(part)
				if index % look.shadowBatch == 0 then
					task.wait()
					if run ~= mine then
						return
					end
				end
			end
		else
			local done = 0
			for part in table.clone(shadowless) do
				shadowless[part] = nil
				part.CastShadow = true
				done += 1
				if done % look.shadowBatch == 0 then
					task.wait()
					if run ~= mine then
						return
					end
				end
			end
		end
	end)
end

function LowDetail.start()
	applyEffects()
	applyShadows()
	SettingsState.changed:Connect(function(key)
		if key == "lowDetail" then
			applyEffects()
			applyShadows()
		end
	end)
	Lighting.ChildAdded:Connect(applyEffects)
end

return LowDetail
