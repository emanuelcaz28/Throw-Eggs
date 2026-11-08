-- The background music, two looping tracks through the player's music volume (Settings panel, SettingsState):
--   Lobby: fades in when the player arrives, fades out while a reveal plays (it has its own sounds), and comes back after.
--   Throwing area [Owner, 2026-11-07]: a tenser, more serious track that starts when the player steps into the throwing
--   area (the aim) and stays on until their egg lands, or the throw is called off, then is cut off. The lobby music is
--   cut off while it plays and returns after the reveal.
-- ThrowController tells this when the throwing starts and ends (MusicController.setThrowing). Config/Music. Display only:
-- nothing here touches the server.
local ContentProvider = game:GetService("ContentProvider")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")
local TweenService = game:GetService("TweenService")

local Music = require(ReplicatedStorage.Shared.Config.Music)
local RevealController = require(script.Parent.RevealController)
local SettingsState = require(script.Parent.SettingsState)

local MusicController = {}

local throwing = false
local thrown = false -- the egg has left the hand: the throwing music drops lower until it lands

-- Called by ThrowController: true when the player steps into the throwing area, false when their egg lands (or the
-- throw is called off).
function MusicController.setThrowing(on: boolean)
	throwing = on
	thrown = false
end

-- Called by ThrowController at the release: the throwing music is lowered while the egg flies.
function MusicController.setThrown()
	thrown = true
end

local function track(name: string, id: string): Sound?
	if id == "" then
		return nil
	end
	local sound = Instance.new("Sound")
	sound.Name = name
	sound.SoundId = id
	sound.Looped = true
	sound.Volume = 0
	sound.SoundGroup = SettingsState.musicGroup
	sound.Parent = SoundService
	task.spawn(function()
		pcall(function()
			ContentProvider:PreloadAsync({ sound })
		end)
	end)
	return sound
end

function MusicController.start()
	local lobby = track("LobbyMusic", Music.lobby)
	local aim = track("ThrowMusic", Music.throwing)
	if lobby then
		lobby:Play()
	end

	local targets = { lobby = -1, aim = -1 }
	local function fade(sound: Sound, key: string, want: number, seconds: number)
		if targets[key] == want then
			return
		end
		targets[key] = want
		TweenService:Create(sound, TweenInfo.new(seconds, Enum.EasingStyle.Sine), { Volume = want }):Play()
	end

	local wasThrowing = false
	task.spawn(function()
		while true do
			-- The throwing music starts from the top each time and is stopped once it has faded out.
			if aim then
				if throwing then
					if not wasThrowing then
						aim.TimePosition = 0
						aim:Play()
					end
					if thrown then
						fade(aim, "aim", Music.throwFlightVolume, Music.throwFlightFade)
					else
						fade(aim, "aim", Music.throwVolume, Music.throwFadeIn)
					end
				else
					fade(aim, "aim", 0, Music.throwCut)
					if aim.IsPlaying and aim.Volume < 0.01 then
						aim:Stop()
					end
				end
			end
			if lobby then
				if throwing then
					fade(lobby, "lobby", 0, Music.lobbyCut)
				elseif Music.quietDuringReveal and RevealController.isPlaying() then
					fade(lobby, "lobby", 0, Music.fade)
				else
					fade(lobby, "lobby", Music.volume, Music.fade)
				end
			end
			wasThrowing = throwing
			task.wait(0.1)
		end
	end)
end

return MusicController
