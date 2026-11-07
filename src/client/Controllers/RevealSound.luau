-- The sounds of every reveal: the walk's footfalls, the counter's ticks and the unveil's roar (Config/Reveal sounds). The
-- mood of rare catches, the drone, heartbeat and rising strings, is RevealDrama's. All from Roblox's licensed libraries or
-- built into Roblox. Display only.
local ContentProvider = game:GetService("ContentProvider")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")

local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)

local RevealSound = {}

local settings = Reveal.sounds
local lastTick = 0

local function lerp(a: number, b: number, u: number): number
	return a + (b - a) * u
end

-- Plays once and clears itself up.
local function play(id: string, volume: number, speed: number)
	local sound = Instance.new("Sound")
	sound.Name = "RevealSound"
	sound.SoundId = id
	sound.Volume = volume
	sound.PlaybackSpeed = speed
	sound.Parent = SoundService
	sound:Play()
	sound.Ended:Once(function()
		sound:Destroy()
	end)
end

-- Loads them ahead of time, so the first step isn't silent.
function RevealSound.preload()
	local sounds = {}
	for _, id in { settings.step, settings.tick, settings.roar } do
		local sound = Instance.new("Sound")
		sound.SoundId = id
		table.insert(sounds, sound)
	end
	task.spawn(function()
		pcall(function()
			ContentProvider:PreloadAsync(sounds)
		end)
		for _, sound in sounds do
			sound:Destroy()
		end
	end)
end

-- A footfall on the walk. `bigness` 0 for the smallest monster, 1 for the biggest.
function RevealSound.step(bigness: number)
	play(settings.step, lerp(settings.stepVolume[1], settings.stepVolume[2], bigness), lerp(settings.stepSpeed[1], settings.stepSpeed[2], bigness))
end

-- The counter stepping up, higher as `pitch` goes from 0 to 1.
function RevealSound.tick(pitch: number)
	local now = os.clock()
	if now - lastTick < settings.tickEvery then
		return
	end
	lastTick = now
	play(settings.tick, settings.tickVolume, lerp(settings.tickSpeed[1], settings.tickSpeed[2], pitch))
end

-- The monster's roar at the unveil. `strength` 0 for the least of them, 1 for the biggest.
function RevealSound.roar(strength: number)
	play(settings.roar, lerp(settings.roarVolume[1], settings.roarVolume[2], strength), lerp(settings.roarSpeed[1], settings.roarSpeed[2], strength))
end

return RevealSound
