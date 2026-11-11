-- A limit on how often one player may send each message to the server. A cheat tool can send a message thousands of
-- times a second; handlers that rebuild models (equip, place, pick up) would then lag the server for everyone. Each
-- player has an allowance per message that refills at `perSecond` up to `burst`; a message with no allowance left is
-- dropped without a word. The limits are far above what a real player's taps reach.
local Players = game:GetService("Players")

local RemoteGuard = {}

local DEFAULT_PER_SECOND = 10
local DEFAULT_BURST = 20

local buckets: { [Player]: { [string]: { left: number, at: number } } } = {}

-- Whether `player` may send message `name` now. Takes one from their allowance when they may.
function RemoteGuard.allow(player: Player, name: string, perSecond: number?, burst: number?): boolean
	local rate = perSecond or DEFAULT_PER_SECOND
	local most = burst or DEFAULT_BURST
	local now = os.clock()
	local mine = buckets[player]
	if not mine then
		if not player.Parent then
			return false -- already left: nothing to remember them by
		end
		mine = {}
		buckets[player] = mine
	end
	local bucket = mine[name]
	if not bucket then
		bucket = { left = most, at = now }
		mine[name] = bucket
	end
	bucket.left = math.min(most, bucket.left + (now - bucket.at) * rate)
	bucket.at = now
	if bucket.left < 1 then
		return false
	end
	bucket.left -= 1
	return true
end

-- Like remote.OnServerEvent:Connect(handler), with the limit in front.
function RemoteGuard.connect(remote: RemoteEvent, handler: (Player, ...any) -> (), perSecond: number?, burst: number?)
	local name = remote:GetFullName()
	return remote.OnServerEvent:Connect(function(player: Player, ...)
		if RemoteGuard.allow(player, name, perSecond, burst) then
			handler(player, ...)
		end
	end)
end

Players.PlayerRemoving:Connect(function(player)
	buckets[player] = nil
end)

return RemoteGuard
