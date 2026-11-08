-- The mood of rare and big catches (docs/GAME_SPEC.md section 7, Config/Reveal drama). [Owner, 2026-11-07] The reveal is the
-- soul of the game: the rarer and bigger the monster, the more dramatic and mysterious. It starts on the walk, so you feel
-- it coming: the world dims, a drone and a heartbeat build. On the shot from the feet the monster's colours sink low and
-- strings climb with the numbers, peaking on the last one. Then it all holds its breath (hush), and at the unveil the
-- colours burst back with a boom. Common catches don't come here. RevealController plays it. Display only.
local Lighting = game:GetService("Lighting")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")
local TweenService = game:GetService("TweenService")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local Roles = require(ReplicatedStorage.Shared.Roles)
local SettingsState = require(script.Parent.SettingsState)

local RevealDrama = {}

local settings = Reveal.drama
local SHADOW = Color3.fromRGB(4, 4, 8)
local CLIMB_START = 0.35 -- how far the heartbeat has sped up by the end of the walk

local function makeSound(id: string, volume: number, looped: boolean): Sound
	local sound = Instance.new("Sound")
	sound.Name = "RevealDrama"
	sound.SoundId = id
	sound.Volume = volume
	sound.Looped = looped
	sound.SoundGroup = SettingsState.sfxGroup -- the player's sound effects slider
	sound.Parent = SoundService
	return sound
end

-- Parts that stay lit in the shadow: whatever glows, and the eyes.
local function staysLit(part: BasePart): boolean
	return Roles.glowing[part.Name] == true or string.find(part.Name, "Eye", 1, true) ~= nil
end

-- How dramatic a catch is: 0 for none (nil is returned), up to #settings.levels.
local function levelOf(catch): number
	local size = DinoStats.findOption(Catch.sizes, catch.size)
	local level = 0
	for index, step in settings.levels do
		if catch.oneIn >= step.oneIn or (size and size.scale >= step.scale) then
			level = index
		end
	end
	return level
end

-- The drama for this catch, or nil for a common one.
function RevealDrama.plan(catch)
	local level = levelOf(catch)
	if level == 0 then
		return nil
	end
	local step = settings.levels[level]
	local drama = { level = level, minClimb = step.minClimb, hushTime = step.hush, letterPower = settings.letterPower, lids = step.lids }

	local shaded = {}
	local dark: ColorCorrectionEffect? = nil
	local drone = makeSound(settings.sounds.drone, 0, true)
	local heart = makeSound(settings.sounds.heart, 0, true)
	local rise = makeSound(settings.sounds.rise, 0, false)
	local boom = makeSound(settings.sounds.boom, step.boom, false)
	local unveiled = false

	-- As the walk starts: the world dims and the sound builds, slowly.
	function drama.mood()
		local effect = Instance.new("ColorCorrectionEffect")
		effect.Name = "RevealDark"
		effect.Parent = Lighting
		dark = effect
		TweenService:Create(effect, TweenInfo.new(settings.darkenTime), {
			TintColor = Color3.new(step.dim, step.dim, step.dim),
			Saturation = -0.3,
			Contrast = 0.1,
		}):Play()
		drone:Play()
		heart:Play()
		TweenService:Create(drone, TweenInfo.new(settings.darkenTime), { Volume = settings.droneVolume }):Play()
		TweenService:Create(heart, TweenInfo.new(settings.darkenTime), { Volume = settings.heartVolume }):Play()
	end

	-- The monster's colours sink low, its eyes and glowing parts staying lit, until the unveil.
	function drama.shade(model: Model)
		for _, part in model:GetDescendants() do
			if part:IsA("BasePart") and part.Transparency < 1 and not staysLit(part) then
				table.insert(shaded, { part = part, color = part.Color })
				part.Color = part.Color:Lerp(SHADOW, settings.shadow)
			end
		end
	end

	-- The numbers start climbing: the strings start so that their peak lands on the last number, `seconds` from now.
	function drama.climb(seconds: number)
		rise.TimePosition = math.max(settings.riseLength - seconds, 0)
		rise:Play()
		TweenService:Create(rise, TweenInfo.new(math.min(seconds * 0.3, 2)), { Volume = settings.riseVolume }):Play()
	end

	-- Each frame: the heart speeds up with `progress`, 0 at the start of the walk to 1 on the last number.
	function drama.update(progress: number)
		if unveiled then
			return
		end
		heart.PlaybackSpeed = settings.heartSpeed[1] + (settings.heartSpeed[2] - settings.heartSpeed[1]) * progress
		drone.PlaybackSpeed = 1 + 0.15 * progress
	end

	-- How far along `progress` is on the walk (`u` of it) and on the climb (`u` of it).
	function drama.onWalk(u: number)
		drama.update(CLIMB_START * u)
	end
	function drama.onClimb(u: number)
		drama.update(CLIMB_START + (1 - CLIMB_START) * u)
	end

	-- The last number is up: the world sinks and everything goes quiet, holding its breath.
	function drama.hush()
		if dark then
			local dim = settings.hushDim
			TweenService:Create(dark, TweenInfo.new(drama.hushTime * 0.5), { TintColor = Color3.new(dim, dim, dim) }):Play()
		end
		for _, sound in { drone, heart, rise } do
			TweenService:Create(sound, TweenInfo.new(drama.hushTime * 0.6), { Volume = 0 }):Play()
		end
	end

	-- BOOM: the colours come back under the flash.
	function drama.unveil()
		if unveiled then
			return
		end
		unveiled = true
		for _, entry in shaded do
			if entry.part.Parent then
				entry.part.Color = entry.color
			end
		end
		table.clear(shaded)
		if dark then
			dark:Destroy()
			dark = nil
		end
		drone:Stop()
		heart:Stop()
		rise:Stop()
		boom:Play()
	end

	function drama.destroy()
		if dark then
			dark:Destroy()
		end
		drone:Destroy()
		heart:Destroy()
		rise:Destroy()
		task.delay(6, function()
			boom:Destroy()
		end)
	end

	return drama
end

return RevealDrama
