-- Keeps the world loaded where a player's egg is. The corridor's props reach a device only near the player's
-- character (Config/Map streaming), back on the platform. While an egg flies, and through the reveal at its landing
-- spot, the server keeps asking Roblox for the props on the stretch just ahead of the egg, so they arrive before
-- the camera gets there. The character stays the player's focus, so the bases at home never unload.
-- ThrowService starts and ends it.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Map = require(ReplicatedStorage.Shared.Config.Map)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)

local FlightStreaming = {}

local runs: { [Player]: {} } = {}

local function request(player: Player, along: number)
	local lane = Throw.lane
	local point = lane.origin + lane.direction * math.max(along, 0)
	pcall(player.RequestStreamAroundAsync, player, Vector3.new(point.X, lane.floorY, point.Z), Map.streaming.timeout)
end

-- Asks for the stretch from `around - back` to `around + forward` (studs down the corridor), one spot every `spacing`
-- studs, nearest `around` first. One ask at a time: asked all at once, Roblox kept only the last few.
local function requestStretch(player: Player, around: number, back: number, forward: number)
	local spacing = Map.streaming.spacing
	for step = 0, math.max(back, forward), spacing do
		if step <= forward then
			request(player, around + step)
		end
		if step > 0 and step <= back then
			request(player, around - step)
		end
	end
end

-- From the throw on: down the corridor with the egg (Throw.flightShare, the curve the egg flies on), just ahead of
-- it, then the landing spot and the reveal walk up to it until stop().
function FlightStreaming.follow(player: Player, distance: number)
	local streaming = Map.streaming
	local run = {}
	runs[player] = run
	local launchedAt = os.clock() + Throw.releaseDelay()
	task.spawn(function()
		while runs[player] == run and player.Parent do
			local elapsed = os.clock() - launchedAt
			local share = if elapsed > 0 then Throw.flightShare(elapsed, distance) else 0
			if share >= 1 then
				break
			end
			local egg = share * distance
			requestStretch(player, egg + streaming.spacing, 0, streaming.ahead - streaming.spacing)
			task.wait(streaming.flightEvery)
		end
		while runs[player] == run and player.Parent do
			requestStretch(player, distance, streaming.behind, streaming.past)
			task.wait(streaming.landedEvery)
		end
	end)
end

-- The reveal is over (or the player left): the world loads round the character alone again.
function FlightStreaming.stop(player: Player)
	runs[player] = nil
end

return FlightStreaming
