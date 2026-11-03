-- The game's light and sky: bright, saturated and cheerful like the reference, with a clear blue
-- horizon so the island reads as floating in the sky. LightingService applies it when the server
-- starts, replacing whatever the place file has, so the look lives in the project.
return {
	-- Properties set straight on the Lighting service.
	lighting = {
		ClockTime = 13,
		GeographicLatitude = 20,
		Brightness = 2.6,
		Ambient = Color3.fromRGB(110, 110, 125),
		OutdoorAmbient = Color3.fromRGB(150, 150, 165), -- lifts the shade, so walls and dinos never go dark
		ShadowSoftness = 0.35,
		EnvironmentDiffuseScale = 0.6,
		EnvironmentSpecularScale = 0.15, -- studs look like matte plastic, not glossy
		ExposureCompensation = 0.1,
		GlobalShadows = true,
		FogEnd = 100000,
	},

	-- A thin, blue atmosphere: distant corridor fades into sky blue instead of grey.
	atmosphere = {
		Density = 0.22,
		Offset = 0.1,
		Color = Color3.fromRGB(185, 222, 255),
		Decay = Color3.fromRGB(95, 160, 235),
		Glare = 0,
		Haze = 0.4,
	},

	colorCorrection = {
		Saturation = 0.18, -- the slightly neon greens
		Contrast = 0.06,
		Brightness = 0.02,
		TintColor = Color3.fromRGB(255, 255, 255),
	},

	bloom = { Intensity = 0.4, Size = 24, Threshold = 1.6 },
	sunRays = { Intensity = 0.03, Spread = 0.4 },

	-- Chunky block clouds drifting around the island, built on each player's screen only.
	clouds = {
		count = 18,
		seed = 11,
		height = { 90, 150 }, -- studs above the arena floor
		ringRadius = { 280, 650 }, -- from the arena's middle, so they circle the island and the corridor
		blocks = { 3, 6 }, -- puffs per cloud
		blockSize = { 24, 56 },
		speed = { 2, 5 }, -- studs per second, all drifting the same way
		direction = Vector3.new(1, 0, -0.35),
		color = Color3.fromRGB(255, 255, 255),
		transparency = 0, -- solid: see-through parts are the costliest thing to draw on phones
		wrap = 800, -- a cloud that drifts this far from its start comes back on the other side
	},
}
