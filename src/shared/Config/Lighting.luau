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

	-- What LightingService calls the effects, so SkyController finds these and not an event's own tint.
	names = { atmosphere = "Atmosphere", colorCorrection = "WorldColor" },

	colorCorrection = {
		Saturation = 0.18, -- the slightly neon greens
		Contrast = 0.06,
		Brightness = 0.02,
		TintColor = Color3.fromRGB(255, 255, 255),
	},

	bloom = { Intensity = 0.4, Size = 24, Threshold = 1.6 },
	sunRays = { Intensity = 0.03, Spread = 0.4 },

	-- Each world's own light while the camera is over it: in flight, at the landing and in the reveal.
	-- Only what differs from the look above is listed; Forest and the arena use the look above.
	-- SkyController blends to it over worldBlendSeconds, so a fast throw slides through the colours.
	worldBlendSeconds = 0.6,
	worlds = {
		Desert = { -- hot and golden
			lighting = { OutdoorAmbient = Color3.fromRGB(175, 155, 130), ExposureCompensation = 0.15 },
			atmosphere = { Color = Color3.fromRGB(255, 226, 170), Decay = Color3.fromRGB(235, 170, 95), Density = 0.3, Haze = 1.2 },
			colorCorrection = { TintColor = Color3.fromRGB(255, 240, 214), Saturation = 0.14 },
		},
		Swamp = { -- murky and green
			lighting = { Brightness = 2, OutdoorAmbient = Color3.fromRGB(120, 145, 120), ExposureCompensation = -0.05 },
			atmosphere = { Color = Color3.fromRGB(165, 200, 150), Decay = Color3.fromRGB(85, 130, 80), Density = 0.4, Haze = 1.8 },
			colorCorrection = { TintColor = Color3.fromRGB(220, 242, 212), Saturation = 0.04 },
		},
		Volcano = { -- smouldering orange haze, a little darker, so the lava glows
			lighting = { Brightness = 1.9, OutdoorAmbient = Color3.fromRGB(160, 118, 100), ExposureCompensation = -0.05 },
			atmosphere = { Color = Color3.fromRGB(255, 168, 120), Decay = Color3.fromRGB(196, 78, 46), Density = 0.42, Haze = 2.2 },
			colorCorrection = { TintColor = Color3.fromRGB(255, 226, 206), Saturation = 0.12 },
		},
		FrozenPeaks = { -- crisp and cold, a pale blue haze; a touch darker so the snow doesn't glare
			lighting = { OutdoorAmbient = Color3.fromRGB(165, 182, 205), ExposureCompensation = -0.1 },
			atmosphere = { Color = Color3.fromRGB(214, 234, 255), Decay = Color3.fromRGB(150, 190, 235), Density = 0.36, Haze = 1.6 },
			colorCorrection = { TintColor = Color3.fromRGB(230, 241, 255), Saturation = 0.06 },
		},
		ShadowBog = { -- dusk over the tar: a violet haze and dimmer light, so the wisps glow
			lighting = { Brightness = 1.7, OutdoorAmbient = Color3.fromRGB(140, 122, 170), ExposureCompensation = -0.1 },
			atmosphere = { Color = Color3.fromRGB(176, 150, 220), Decay = Color3.fromRGB(96, 68, 150), Density = 0.42, Haze = 2 },
			colorCorrection = { TintColor = Color3.fromRGB(232, 222, 255), Saturation = 0.1 },
		},
		Abyss = { -- deep under the sea: dim blue light and a thick blue haze, so the reef's glow stands out
			lighting = { Brightness = 1.5, OutdoorAmbient = Color3.fromRGB(95, 140, 185), ExposureCompensation = -0.1 },
			atmosphere = { Color = Color3.fromRGB(70, 150, 210), Decay = Color3.fromRGB(20, 62, 125), Density = 0.5, Haze = 2.4 },
			colorCorrection = { TintColor = Color3.fromRGB(205, 232, 255), Saturation = 0.18 },
		},
		StarfallCrater = { -- the last world is at night: the sky turns to stars, and the crystals and star-stuff glow
			lighting = { ClockTime = 0, Brightness = 1.2, OutdoorAmbient = Color3.fromRGB(120, 130, 185), ExposureCompensation = 0.25 },
			atmosphere = { Color = Color3.fromRGB(96, 106, 176), Decay = Color3.fromRGB(32, 34, 92), Density = 0.3, Haze = 0.8 },
			colorCorrection = { TintColor = Color3.fromRGB(222, 228, 255), Saturation = 0.2 },
		},
		-- Under the eclipse: still night, with the first glow of dawn behind a thick jade-green jungle mist, so
		-- the jade and the lanterns glow. ClockTime stays below 6 on purpose: the blend tweens it as a number,
		-- and coming from Starfall's 0 anything past dawn would flash through daylight.
		EclipseTemple = {
			lighting = { ClockTime = 5.6, Brightness = 1.4, OutdoorAmbient = Color3.fromRGB(120, 160, 140), ExposureCompensation = 0.2 },
			atmosphere = { Color = Color3.fromRGB(90, 150, 125), Decay = Color3.fromRGB(30, 70, 60), Density = 0.42, Haze = 2.2 },
			colorCorrection = { TintColor = Color3.fromRGB(226, 248, 232), Saturation = 0.18 },
		},
	},

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
