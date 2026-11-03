-- Sets the light, atmosphere and screen effects from Config/Lighting when the server starts.
-- Lighting replicates, so every player sees the same. Effects the config doesn't use are removed.
local Lighting = game:GetService("Lighting")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage.Shared.Config.Lighting)

local LightingService = {}

-- The one child of this class, made if missing, with `values` set on it.
local function effect(className: string, values: { [string]: any }): Instance
	local object = Lighting:FindFirstChildOfClass(className) or Instance.new(className)
	for key, value in values do
		(object :: any)[key] = value
	end
	object.Parent = Lighting
	return object
end

function LightingService.start()
	for key, value in Config.lighting do
		(Lighting :: any)[key] = value
	end
	effect("Atmosphere", Config.atmosphere)
	effect("ColorCorrectionEffect", Config.colorCorrection)
	effect("BloomEffect", Config.bloom)
	effect("SunRaysEffect", Config.sunRays)

	-- Depth of field blurs the far corridor, which is exactly what the egg flies down.
	local blur = Lighting:FindFirstChildOfClass("DepthOfFieldEffect")
	if blur then
		blur:Destroy()
	end
end

return LightingService
