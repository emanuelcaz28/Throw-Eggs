-- Sets the light, atmosphere and screen effects from Config/Lighting when the server starts.
-- Lighting replicates, so every player sees the same. Effects the config doesn't use are removed.
-- Each player's SkyController then blends towards a world's own look while their camera is over it.
local Lighting = game:GetService("Lighting")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage.Shared.Config.Lighting)

local LightingService = {}

-- The effect called `name` (any other of its class goes, so the place file's own can't double up),
-- made if missing, with `values` set on it. Names let the client tell these apart from effects it
-- makes itself, like an event's tint.
local function effect(className: string, name: string, values: { [string]: any }): Instance
	local object = nil
	for _, child in Lighting:GetChildren() do
		if child.ClassName == className then
			if child.Name == name and not object then
				object = child
			else
				child:Destroy()
			end
		end
	end
	object = object or Instance.new(className)
	object.Name = name
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
	effect("Atmosphere", Config.names.atmosphere, Config.atmosphere)
	effect("ColorCorrectionEffect", Config.names.colorCorrection, Config.colorCorrection)
	effect("BloomEffect", "Bloom", Config.bloom)
	effect("SunRaysEffect", "SunRays", Config.sunRays)

	-- Depth of field blurs the far corridor, which is exactly what the egg flies down.
	local blur = Lighting:FindFirstChildOfClass("DepthOfFieldEffect")
	if blur then
		blur:Destroy()
	end
end

return LightingService
