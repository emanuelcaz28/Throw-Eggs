-- Loads and saves each player's data with a session lock, so two servers can
-- never write the same player at once (which is how progress gets lost or duplicated).
--
-- Stored record: { data = <save table>, lock = { token, time } or nil }
-- Every session gets its own token. A write only goes through while the record
-- still holds that token, so a stale save can never overwrite newer progress.
local DataStoreService = game:GetService("DataStoreService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Save = require(ReplicatedStorage.Shared.Config.Save)

local PlayerData = {}

type Session = {
	token: string,
	data: { [string]: any },
	memoryOnly: boolean, -- Studio without API access: nothing is read or written
	released: boolean,
}

local sessions: { [Player]: Session } = {}
local loadedCallbacks: { (Player, { [string]: any }) -> () } = {}
local pendingReleases = 0

local function keyFor(userId: number): string
	return "player_" .. userId
end

local function getStore(): (DataStore?, string?)
	local ok, result = pcall(function()
		return DataStoreService:GetDataStore(Save.storeName)
	end)
	if ok then
		return result, nil
	end
	return nil, tostring(result)
end

local function withDefaults(saved: { [string]: any }?): { [string]: any }
	local data = table.clone(Save.defaults)
	for key, value in saved or {} do
		data[key] = value
	end
	return data
end

-- Returns (data, nil) on success, or (nil, reason) if the store failed or the lock is held.
local function tryAcquire(store: DataStore, userId: number, token: string): ({ [string]: any }?, string?)
	local lockedByOther = false
	local record
	local ok, err = pcall(function()
		record = store:UpdateAsync(keyFor(userId), function(current)
			lockedByOther = false
			current = current or {}
			local lock = current.lock
			if lock and os.time() - lock.time < Save.lockExpiry then
				lockedByOther = true
				return nil -- leave the record untouched
			end
			current.lock = { token = token, time = os.time() }
			return current
		end)
	end)
	if not ok then
		return nil, tostring(err)
	end
	if lockedByOther then
		return nil, "locked by another session"
	end
	return withDefaults(record.data), nil
end

-- Writes the session's data. Returns "saved", "failed" (store errors) or "lockLost".
local function write(player: Player, session: Session, releaseLock: boolean): string
	if session.memoryOnly then
		return "saved"
	end
	local store = getStore()
	local lockLost = false
	local retryDelay = Save.saveRetryDelay
	for attempt = 1, Save.saveAttempts do
		local ok, err = pcall(function()
			store:UpdateAsync(keyFor(player.UserId), function(current)
				lockLost = false
				if not current or not current.lock or current.lock.token ~= session.token then
					lockLost = true
					return nil
				end
				current.data = session.data
				current.lock = if releaseLock then nil else { token = session.token, time = os.time() }
				return current
			end)
		end)
		if ok then
			return if lockLost then "lockLost" else "saved"
		end
		warn(`[PlayerData] {player.Name}: save attempt {attempt} failed: {err}`)
		if attempt < Save.saveAttempts then
			task.wait(retryDelay)
			retryDelay *= 2
		end
	end
	return "failed"
end

local function load(player: Player)
	local token = HttpService:GenerateGUID(false)
	local store, storeErr = getStore()
	local data, reason = nil, storeErr

	if store then
		for attempt = 1, Save.loadAttempts do
			data, reason = tryAcquire(store, player.UserId, token)
			-- Studio with API access off fails the same way every time, so don't sit retrying.
			if data or not player.Parent or (RunService:IsStudio() and reason ~= "locked by another session") then
				break
			end
			warn(`[PlayerData] {player.Name}: load attempt {attempt} failed: {reason}`)
			task.wait(Save.loadRetryDelay)
		end
	end

	local session: Session
	if data then
		session = { token = token, data = data, memoryOnly = false, released = false }
	elseif RunService:IsStudio() and reason ~= "locked by another session" then
		warn(
			`[PlayerData] Saving is OFF in this Studio session: {reason}\n`
				.. "Turn on Game Settings > Security > Enable Studio Access to API Services to test saving."
		)
		session = { token = token, data = withDefaults(nil), memoryOnly = true, released = false }
	else
		-- Never play on blank data: the first save would wipe real progress.
		warn(`[PlayerData] {player.Name}: giving up on load: {reason}`)
		player:Kick("We couldn't load your save, so nothing was changed. Please rejoin in a minute.")
		return
	end

	if not player.Parent then
		-- Left while loading: give the lock straight back.
		write(player, session, true)
		return
	end

	sessions[player] = session
	for _, callback in loadedCallbacks do
		task.spawn(callback, player, session.data)
	end
end

local function release(player: Player)
	local session = sessions[player]
	if not session or session.released then
		return
	end
	session.released = true
	sessions[player] = nil
	pendingReleases += 1
	local result = write(player, session, true)
	if result ~= "saved" then
		warn(`[PlayerData] {player.Name}: final save not written: {result}`)
	end
	pendingReleases -= 1
end

-- The player's live save table, or nil until it has loaded. Changes are saved automatically.
function PlayerData.get(player: Player): { [string]: any }?
	local session = sessions[player]
	return session and session.data
end

-- Runs for every player once their data is ready, including players already loaded.
function PlayerData.onLoaded(callback: (Player, { [string]: any }) -> ())
	table.insert(loadedCallbacks, callback)
	for player, session in sessions do
		task.spawn(callback, player, session.data)
	end
end

function PlayerData.start()
	Players.PlayerAdded:Connect(load)
	Players.PlayerRemoving:Connect(release)
	for _, player in Players:GetPlayers() do
		task.spawn(load, player)
	end

	task.spawn(function()
		while true do
			task.wait(Save.autosaveInterval)
			for player, session in sessions do
				task.spawn(function()
					local result = write(player, session, false)
					if result == "lockLost" and not session.released then
						-- Another server owns this player now, so stop before the two diverge.
						session.released = true
						sessions[player] = nil
						player:Kick("You joined from another server. Please rejoin.")
					elseif result == "failed" then
						warn(`[PlayerData] {player.Name}: autosave failed, will try again next round`)
					end
				end)
			end
		end
	end)

	-- The server gives us up to 30 seconds on shutdown to finish saving.
	game:BindToClose(function()
		for _, player in Players:GetPlayers() do
			task.spawn(release, player)
		end
		while pendingReleases > 0 do
			task.wait()
		end
	end)
end

return PlayerData
