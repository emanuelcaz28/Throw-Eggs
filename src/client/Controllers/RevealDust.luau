-- Dust thrown up off the ground round a caught monster when something big lands: the camera switching to its feet, each
-- luck label, the unveil (docs/GAME_SPEC.md section 7). [Owner, 2026-11-07: the flashy effects round the monster had to go, or
-- be better] So nothing glows or sparkles any more: this is plain dust, lit by the world like the ground it comes from.
-- Built-in Roblox texture, so nothing has to be uploaded. Display only; numbers in Config/Reveal dust.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)

local RevealDust = {}

local settings = Reveal.dust
local TEXTURE = "rbxasset://textures/particles/smoke_main.dds"
local MAX_PUFF = 100 -- studs: Roblox's limit for a particle

export type Dust = {
	burst: (strength: number) -> (),
	slow: (speed: number) -> (),
	destroy: () -> (),
}

-- Sets up the dust under `model`, standing on the ground at `groundY`. `burst` throws it up, `strength` from 0 to 1.
function RevealDust.new(model: Model, groundY: number): Dust
	local box, size = model:GetBoundingBox()
	local pad = Instance.new("Part")
	pad.Name = "RevealDust"
	pad.Anchored = true
	pad.CanCollide = false
	pad.CanQuery = false
	pad.CanTouch = false
	pad.Transparency = 1
	pad.Size = Vector3.new(size.X, 0.2, size.Z):Min(Vector3.one * 2000)
	pad.CFrame = CFrame.new(box.Position.X, groundY + 0.2, box.Position.Z) * box.Rotation
	pad.Parent = workspace

	local height = math.max(size.Y, 1)
	local puff = math.clamp(math.max(size.X, height) * settings.size, settings.smallest, MAX_PUFF)
	local emitter = Instance.new("ParticleEmitter")
	emitter.Texture = TEXTURE
	emitter.Rate = 0
	emitter.EmissionDirection = Enum.NormalId.Top
	emitter.SpreadAngle = Vector2.new(75, 75)
	emitter.Lifetime = NumberRange.new(settings.life[1], settings.life[2])
	emitter.Speed = NumberRange.new(height * settings.speed[1], height * settings.speed[2])
	emitter.Drag = settings.drag
	emitter.Rotation = NumberRange.new(0, 360)
	emitter.RotSpeed = NumberRange.new(-25, 25)
	emitter.Color = ColorSequence.new(settings.color)
	emitter.LightEmission = 0
	emitter.LightInfluence = 1
	emitter.Size = NumberSequence.new({
		NumberSequenceKeypoint.new(0, puff * 0.5),
		NumberSequenceKeypoint.new(1, math.min(puff * 1.7, MAX_PUFF)),
	})
	emitter.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, settings.thickest),
		NumberSequenceKeypoint.new(0.35, settings.thickest + 0.1),
		NumberSequenceKeypoint.new(1, 1),
	})
	emitter.Parent = pad

	return {
		burst = function(strength: number)
			emitter:Emit(math.round(settings.puffs[1] + (settings.puffs[2] - settings.puffs[1]) * strength))
		end,
		-- The dust in the air slows down, as if time did (the showcase's frozen moment): 1 is normal speed.
		slow = function(speed: number)
			emitter.TimeScale = math.clamp(speed, 0, 1)
		end,
		destroy = function()
			pad:Destroy()
		end,
	}
end

return RevealDust
