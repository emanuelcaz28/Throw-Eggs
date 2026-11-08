-- Sounds that play the instant they're asked for. A brand-new Sound has to load its file before it can play, which
-- made the button clicks and the meter tap come late; here each sound keeps a few loaded copies in SoundService and
-- reuses them, so a play is just "rewind and go". Display only.
local ContentProvider = game:GetService("ContentProvider")
local SoundService = game:GetService("SoundService")

local SettingsState = require(script.Parent.SettingsState)

local SoundPool = {}

local COPIES = 4 -- how many of one sound can overlap (fast taps, quick footfalls)

local pools: { [string]: { sounds: { Sound }, next: number } } = {}

local function poolFor(id: string)
	local pool = pools[id]
	if pool then
		return pool
	end
	pool = { sounds = {}, next = 1 }
	for i = 1, COPIES do
		local sound = Instance.new("Sound")
		sound.Name = "Pooled"
		sound.SoundId = id
		sound.SoundGroup = SettingsState.sfxGroup -- the player's sound effects slider
		sound.Parent = SoundService
		pool.sounds[i] = sound
	end
	pools[id] = pool
	return pool
end

-- Loads these sounds ahead of time. Empty ids are skipped.
function SoundPool.preload(ids: { string })
	local sounds = {}
	for _, id in ids do
		if id ~= "" then
			for _, sound in poolFor(id).sounds do
				table.insert(sounds, sound)
			end
		end
	end
	task.spawn(function()
		pcall(function()
			ContentProvider:PreloadAsync(sounds)
		end)
	end)
end

-- Plays `id` at once. `skip` jumps past silence at the start of the file, in seconds. An empty id is silent.
function SoundPool.play(id: string, volume: number, speed: number, skip: number?)
	if id == "" then
		return
	end
	local pool = poolFor(id)
	local sound = pool.sounds[pool.next]
	pool.next = pool.next % COPIES + 1
	sound.SoundGroup = SettingsState.sfxGroup
	sound.Volume = volume
	sound.PlaybackSpeed = speed
	sound.TimePosition = skip or 0
	sound:Play()
end

return SoundPool
