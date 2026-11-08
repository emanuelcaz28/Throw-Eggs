-- The sounds of every reveal: the walk's footfalls, the counter's ticks and the unveil's roar (Config/Reveal sounds). The
-- mood of rare catches, the drone, heartbeat and rising strings, is RevealDrama's. All from Roblox's licensed libraries or
-- built into Roblox. Display only.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local SoundPool = require(script.Parent.SoundPool)

local RevealSound = {}

local settings = Reveal.sounds
local lastTick = 0

local function lerp(a: number, b: number, u: number): number
	return a + (b - a) * u
end

-- Plays at once from loaded copies (SoundPool), so nothing comes late.
local function play(id: string, volume: number, speed: number, skip: number?)
	SoundPool.play(id, volume, speed, skip)
end

-- Loads them ahead of time, so the first step isn't silent.
function RevealSound.preload()
	SoundPool.preload({ settings.step, settings.tick, settings.roar, settings.slam.small, settings.slam.mid, settings.slam.huge, settings.eggDrop, settings.eggSlice, settings.throwWhoosh, settings.bigReveal, settings.plainReveal, settings.meterTap, settings.meterPerfect })
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

-- The egg touching down, and the cut that follows. `mine` is false for other players' throws, which play quieter.
function RevealSound.eggDrop(mine: boolean)
	if settings.eggDrop ~= "" then
		play(settings.eggDrop, if mine then settings.eggVolume.mine else settings.eggVolume.others, 1)
	end
end

-- The sound at the end of a big catch's reveal. Silent for sizes not listed in bigRevealSizes.
function RevealSound.bigReveal(sizeId: string?)
	local volume = sizeId and settings.bigRevealSizes[sizeId]
	if volume and settings.bigReveal ~= "" then
		play(settings.bigReveal, volume, 1)
	end
end

-- The owner's sound when a plain catch (no luck label) shows whole.
function RevealSound.plainReveal()
	if settings.plainReveal ~= "" then
		play(settings.plainReveal, settings.plainRevealVolume, 1)
	end
end

-- The same sound, quieter, when a tap skips the reveal.
function RevealSound.skip()
	if settings.plainReveal ~= "" then
		play(settings.plainReveal, settings.skipVolume, 1)
	end
end

-- Every monster's slam when its whole body is shown. `strength` 0 for the weakest catch, 1 for the rarest.
function RevealSound.unveilSlam(strength: number)
	local u = settings.unveilSlam
	local id = if strength >= u.hugeFrom then settings.slam.huge else settings.slam.mid
	play(id, lerp(u.volume[1], u.volume[2], strength), 1)
end

-- The whoosh, started throwWhooshLead seconds before the egg leaves the hand so its loudest part lands on the release.
function RevealSound.throwWhoosh(mine: boolean)
	if settings.throwWhoosh ~= "" then
		play(settings.throwWhoosh, if mine then settings.eggVolume.mine else settings.eggVolume.others, 1, settings.throwWhooshSkip)
	end
end

function RevealSound.eggSlice(mine: boolean)
	if settings.eggSlice ~= "" then
		play(settings.eggSlice, if mine then settings.eggVolume.mine else settings.eggVolume.others, 1)
	end
end

-- The tap on the throw meter: the soft pop for levels 1 to 9, the PERFECT sound for the top level.
function RevealSound.meterTap(perfect: boolean)
	local id = if perfect then settings.meterPerfect else settings.meterTap
	if id ~= "" then
		play(id, if perfect then settings.meterPerfectVolume else settings.meterTapVolume, 1, if perfect then settings.meterPerfectSkip else settings.meterTapSkip)
	end
end

-- The slam of a luck label hitting the screen. `index` is the tier, 1 to `count`; the higher, the heavier it hits.
function RevealSound.slam(index: number, count: number)
	local slam = settings.slam
	local id = slam[slam.weights[index] or slam.weights[#slam.weights]]
	if id == nil or id == "" then
		return
	end
	local u = (index - 1) / math.max(count - 1, 1)
	play(id, lerp(slam.volume[1], slam.volume[2], u), lerp(slam.speed[1], slam.speed[2], u))
end

-- The weakest slam, for the 2X XP hit while training.
function RevealSound.boostSlam()
	play(settings.slam.small, settings.slam.boostVolume, settings.slam.speed[1])
end

return RevealSound
