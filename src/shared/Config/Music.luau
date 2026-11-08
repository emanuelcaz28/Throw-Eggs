-- The game's background music (MusicController). From ElevenLabs, uploaded by the owner. An empty id is silent.
return {
	lobby = "rbxassetid://127823403871575", -- sounds/lobby_music_a.mp3 (60 seconds, instrumental, loops): playful pizzicato strings and marimba
	volume = 0.4, -- at the Settings slider's default 80% this plays at 0.32: well under the sound effects, so the slams and clicks stand out
	fade = 1.5, -- seconds to fade in, out and back in
	-- The throwing area's track (60 seconds, loops): tense and playful but serious, not childish. It plays from the aim until
	-- the egg lands, then is cut off; the lobby music is cut off while it plays.
	throwing = "rbxassetid://79547211497224", -- [Owner, 2026-11-08] the owner's pick
	throwVolume = 0.35, -- [Owner, 2026-11-08] a bit louder than the first 0.25: at the Settings slider's default 80% this plays at 0.28
	throwFlightVolume = 0.15, -- [Owner, 2026-11-08] lowered once the egg leaves the hand, until it lands
	throwFlightFade = 0.4, -- seconds to drop to it
	throwFadeIn = 0.8, -- seconds
	throwCut = 0.25, -- seconds: it is cut off, not faded slowly, when the egg lands
	lobbyCut = 0.6, -- seconds the lobby music takes to leave when the player steps into the throwing area
	quietDuringReveal = true, -- a reveal has its own sounds, so the music fades out until it's over
}
