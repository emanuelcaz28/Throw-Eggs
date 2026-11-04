-- The final moment's light rays: a burst of light in the rarity's colour behind the caught monster, slowly turning.
-- No discs or rings: the owner found the old rings ugly. They live in the 3D world just behind the monster, so its body hides their middle
-- and they fan out round its outline. Rarer catches get more rays, brighter and turning faster.
-- Numbers live in Config/Reveal rays. RevealController plays them.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)

local RevealRays = {}

local settings = Reveal.rays
local WHITE = Color3.new(1, 1, 1)

local function lerp(a: number, b: number, u: number): number
	return a + (b - a) * u
end

export type Rays = {
	update: (now: number, camera: CFrame) -> (),
	destroy: () -> (),
}

-- `box` and `size` are round the monster (and the egg), `light` and `deep` the rarity's colours, `strength` 0 for a
-- catch with no luck label up to 1 for the rarest label.
function RevealRays.burst(box: CFrame, size: Vector3, camera: CFrame, light: Color3, deep: Color3, strength: number): Rays
	local count = math.round(lerp(settings.count, settings.bigCount, strength))
	local opacity = lerp(settings.opacity, settings.bigOpacity, strength)
	local spin = math.rad(lerp(settings.turnSpeed, settings.bigTurnSpeed, strength))
	local radius = math.max(size.X, size.Y) * settings.length

	local anchor = Instance.new("Part")
	anchor.Name = "RevealRays"
	anchor.Anchored = true
	anchor.CanCollide = false
	anchor.CanQuery = false
	anchor.CanTouch = false
	anchor.CastShadow = false
	anchor.Transparency = 1
	anchor.Size = Vector3.one
	anchor.Parent = workspace

	local centre = Instance.new("Attachment")
	centre.Parent = anchor

	-- Two layers of rays: long wide ones turning one way, and thinner, fainter ones between them turning the other.
	local rays = {}
	for layer = 1, 2 do
		local main = layer == 1
		for index = 1, count do
			local tip = Instance.new("Attachment")
			tip.Parent = anchor
			local beam = Instance.new("Beam")
			beam.Attachment0 = centre
			beam.Attachment1 = tip
			beam.FaceCamera = true
			beam.LightEmission = 1
			beam.LightInfluence = 0
			beam.Segments = 1
			beam.Brightness = settings.brightness
			beam.Color = ColorSequence.new(WHITE:Lerp(light, 0.4), deep)
			local start = 1 - opacity * (if main then 1 else settings.innerOpacity)
			beam.Transparency = NumberSequence.new({
				NumberSequenceKeypoint.new(0, start),
				NumberSequenceKeypoint.new(0.6, lerp(start, 1, 0.55)),
				NumberSequenceKeypoint.new(1, 1),
			})
			beam.Parent = anchor
			-- Every other ray is a little shorter, so the outline isn't a perfect circle.
			local reach = if main then (if index % 2 == 0 then 1 else settings.shortShare) else settings.innerLength
			local width = 2 * math.pi * radius * reach / count * (if main then settings.width else settings.innerWidth)
			table.insert(rays, {
				tip = tip,
				beam = beam,
				reach = reach,
				width = width,
				angle = (index - 1) / count * 2 * math.pi + (if main then 0 else math.pi / count),
				spin = if main then spin else -spin * settings.innerSpin,
			})
		end
	end

	local startedAt = os.clock()

	local function update(now: number, cameraFrame: CFrame)
		-- Just behind the monster's middle, as seen from the camera, so its body covers the rays' middle.
		local look = box.Position - cameraFrame.Position
		look = if look.Magnitude > 1e-3 then look.Unit else cameraFrame.LookVector
		anchor.CFrame = CFrame.new(box.Position + look * size.Magnitude * settings.behind)
		local right, up = cameraFrame.RightVector, cameraFrame.UpVector
		local elapsed = now - startedAt
		local grow = TweenService:GetValue(math.clamp(elapsed / settings.openTime, 0, 1), Enum.EasingStyle.Back, Enum.EasingDirection.Out)
		local pulse = 1 + settings.pulse * math.sin(elapsed * settings.pulseRate * 2 * math.pi)
		for _, ray in rays do
			local angle = ray.angle + ray.spin * elapsed
			-- Rays pointing down shrink away, so none streak across the ground in front of the monster.
			local downward = math.clamp(1 + math.sin(angle) * settings.downFade, 0, 1)
			local reach = radius * ray.reach * grow * pulse * downward
			-- Attachments sit in the anchor's space, which isn't turned, so world directions work as they are.
			ray.tip.Position = (right * math.cos(angle) + up * math.sin(angle)) * reach
			ray.beam.Width0 = ray.width * settings.rootWidth * grow * downward
			ray.beam.Width1 = ray.width * grow * downward
		end
	end

	update(startedAt, camera)
	return {
		update = update,
		destroy = function()
			anchor:Destroy()
		end,
	}
end

return RevealRays
