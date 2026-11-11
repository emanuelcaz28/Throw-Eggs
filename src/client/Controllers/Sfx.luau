-- Plays one of Config/UiSounds moments by name, from loaded copies (SoundPool) so it sounds at once. Display only.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")
local TweenService = game:GetService("TweenService")

local UiSounds = require(ReplicatedStorage.Shared.Config.UiSounds)
local SettingsState = require(script.Parent.SettingsState)
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

-- Starts a looping moment (the egg's flight) and returns a function that fades it out and stops it. It stops by
-- itself after maxSeconds, so a throw that breaks halfway never leaves it running.
function Sfx.loop(name: string, maxSeconds: number): () -> ()
	local moment = UiSounds.moments[name]
	if not moment or moment.id == "" then
		return function() end
	end
	local sound = Instance.new("Sound")
	sound.SoundId = moment.id
	sound.Looped = true
	sound.Volume = moment.volume
	sound.PlaybackSpeed = random:NextNumber(moment.pitch[1], moment.pitch[2])
	sound.SoundGroup = SettingsState.sfxGroup
	sound.Parent = SoundService
	sound:Play()
	local stopped = false
	local function stop()
		if stopped then
			return
		end
		stopped = true
		local fade = TweenService:Create(sound, TweenInfo.new(0.15), { Volume = 0 })
		fade.Completed:Connect(function()
			sound:Destroy()
		end)
		fade:Play()
	end
	task.delay(maxSeconds, stop)
	return stop
end

function Sfx.preload()
	local ids = {}
	for _, moment in UiSounds.moments do
		table.insert(ids, moment.id)
	end
	SoundPool.preload(ids)
end

return Sfx
