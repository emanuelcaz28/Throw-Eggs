-- Plays one of Config/UiSounds moments by name, from loaded copies (SoundPool) so it sounds at once. Display only.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local UiSounds = require(ReplicatedStorage.Shared.Config.UiSounds)
local SoundPool = require(script.Parent.SoundPool)

local Sfx = {}

local random = Random.new()

-- pitchShift multiplies the pitch picked from the moment's range (the squat's climb).
function Sfx.play(name: string, pitchShift: number?)
	local moment = UiSounds.moments[name]
	if not moment or moment.id == "" then
		return
	end
	local pitch = random:NextNumber(moment.pitch[1], moment.pitch[2]) * (pitchShift or 1)
	SoundPool.play(moment.id, moment.volume, pitch)
end

function Sfx.preload()
	local ids = {}
	for _, moment in UiSounds.moments do
		table.insert(ids, moment.id)
	end
	SoundPool.preload(ids)
end

return Sfx
