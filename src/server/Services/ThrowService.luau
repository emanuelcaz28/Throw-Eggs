-- Marks the throw lane on the corridor floor and runs each player's throw: aiming -> flying -> aiming again.
-- The client only reports how high the meter marker was when it tapped. The server checks that the tap
-- is allowed and works out the distance itself.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local AdminBoosts = require(ReplicatedStorage.Shared.AdminBoosts)
local Biomes = require(ReplicatedStorage.Shared.Config.Biomes)
local DeepEnd = require(ReplicatedStorage.Shared.Config.DeepEnd)
local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)
local Hooks = require(ReplicatedStorage.Shared.Config.Hooks)
local Luck = require(ReplicatedStorage.Shared.Config.Luck)
local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local PowerLimit = require(ReplicatedStorage.Shared.Config.PowerLimit)
local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)
local CatchOdds = require(ReplicatedStorage.Shared.CatchOdds)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local LuckyThrows = require(ReplicatedStorage.Shared.LuckyThrows)
local RemoteGuard = require(script.Parent.RemoteGuard)
local Analytics = require(script.Parent.Analytics)
local DailyTasks = require(script.Parent.DailyTasks)
local DinoLibrary = require(script.Parent.DinoLibrary)
local DinoRoll = require(script.Parent.DinoRoll)
local CompetitionService = require(script.Parent.CompetitionService)
local EggService = require(script.Parent.EggService)
local FilmingService = require(script.Parent.FilmingService)
local FlightStreaming = require(script.Parent.FlightStreaming)
local IndexService = require(script.Parent.IndexService)
local LeashService = require(script.Parent.LeashService)
local PlayerData = require(script.Parent.PlayerData)
local PlotService = require(script.Parent.PlotService)
local RagdollService = require(script.Parent.RagdollService)
local ShopService = require(script.Parent.ShopService)
local TrainingService = require(script.Parent.TrainingService)
local TutorialService = require(script.Parent.TutorialService)
local World = require(ReplicatedStorage.Shared.World)

local ThrowService = {}

local TICK = 0.1
local MARKER_COLOR = Color3.new(1, 1, 1)
local MARKER_LIFT = 0.05 -- just above the corridor floor, so the two don't flicker

type ThrowState = {
	phase: "idle" | "aiming" | "flying" | "revealing",
	aimStartedAt: number,
	revealStartedAt: number,
	mustLeave: boolean?,
	revealDone: boolean?, -- the client said it's done before the catch landed here (it gave up waiting, or broke)
	lucky: number?, -- the lucky throw picked with USE for the egg in the air, used up when it lands
	carryKey: number?, -- a tutorial catch put on the player's head once the reveal is done
}

local states: { [Player]: ThrowState } = {}
local homeBiome = {} -- by monster id
for _, biome in Biomes do
	for _, dino in Dinos[biome.id] or {} do
		homeBiome[dino.id] = biome
	end
end
local remotes: { [string]: RemoteEvent } = {}

local function makeRemotes()
	local folder = Instance.new("Folder")
	folder.Name = "ThrowRemotes"
	for _, name in { "MeterStart", "MeterCancel", "MeterDeclined", "Tap", "Launched", "Landed", "RevealDone", "LuckyCatch" } do
		local remote = Instance.new("RemoteEvent")
		remote.Name = name
		remote.Parent = folder
		remotes[name] = remote
	end
	folder.Parent = ReplicatedStorage
end

-- Thin lines across the corridor floor every markerSpacing studs and THROW HERE over the platform. The floor
-- itself is MapService's. There are no floating labels down the corridor, as in the reference: the world's name
-- shows in the flight's luck panel instead.
local function buildLane()
	local lane = Throw.lane
	local model = Instance.new("Model")
	model.Name = "ThrowLane"
	-- The lane runs far from the player. Without this, Roblox may not send distant
	-- parts to the client.
	model.ModelStreamingMode = Enum.ModelStreamingMode.Persistent

	local function floorPoint(distance: number): Vector3
		local point = lane.origin + lane.direction * distance
		return Vector3.new(point.X, lane.floorY, point.Z)
	end

	local maxDistance = Throw.maxDistance()
	for distance = lane.markerSpacing, maxDistance, lane.markerSpacing do
		local marker = World.makePart(
			model,
			"Marker",
			Vector3.new(lane.width, 0.1, 1),
			CFrame.new(floorPoint(distance) + Vector3.new(0, MARKER_LIFT, 0)),
			MARKER_COLOR
		)
		marker.CanCollide = false
		marker.Material = Enum.Material.SmoothPlastic
		marker.Transparency = 0.4
	end

	local signAnchor = World.makePart(model, "ThrowSign", Vector3.one, CFrame.new(lane.zoneCenter + Vector3.new(0, 10, 0)), MARKER_COLOR)
	signAnchor.Transparency = 1
	signAnchor.CanCollide = false
	World.makeSign(signAnchor, "THROW HERE", 0, 150, 220)

	model.Parent = workspace
end

local function isOnPad(player: Player): boolean
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	-- A ragdolled player, or one holding a leash, never counts as on the platform, so they can't start a throw
	-- [Owner, 2026-11-12].
	return root ~= nil and humanoid ~= nil and humanoid.Health > 0 and Throw.onPlatform(root.Position)
		and not RagdollService.isRagdolled(player) and not LeashService.isHolding(player)
end

-- The player is home again: the catch goes onto their head, ready to place, and the next throw can start once the
-- reveal's shortest time has passed.
local function finishReveal(player: Player, state: ThrowState)
	if state.carryKey then
		PlotService.carry(player, state.carryKey)
		state.carryKey = nil
	end
	local remaining = Reveal.minTime - (os.clock() - state.revealStartedAt)
	task.delay(math.max(remaining, 0), function()
		if states[player] == state and state.phase == "revealing" then
			state.phase = "idle"
			FlightStreaming.stop(player)
		end
	end)
end

local function onTap(player: Player, height: any, lucky: any)
	local state = states[player]
	if not state or state.phase ~= "aiming" then
		return
	end
	-- height ~= height is only true for NaN.
	local power = TrainingService.getThrowPower(player)
	power = power and power * AdminBoosts.multiplier("power") -- an admin's server power boost (admin panel)
	if typeof(height) ~= "number" or height ~= height or os.clock() - state.aimStartedAt < Throw.meter.minTime
		or not isOnPad(player) or not power
	then
		-- A tap that can't throw calls the meter off: the player's screen has stopped taking taps, and they'd stand
		-- frozen on it. It starts again while they're on the platform.
		state.phase = "idle"
		remotes.MeterCancel:FireClient(player)
		return
	end

	height = math.clamp(height, 0, 1)
	-- The lucky throw picked on the meter, if it's one picked by hand and the player owns it. Nothing is used up yet:
	-- leaving before the egg lands keeps it. A picked one is always a PERFECT throw [Owner, 2026-11-09]; the daily
	-- task still only counts a perfect the player hit themselves.
	local data = PlayerData.get(player)
	local owned = data and typeof(lucky) == "number" and (data.luckyThrows[tostring(lucky)] or 0) > 0
	local pickedLuck = if owned and LuckyThrows.isPicked(lucky) then lucky else nil
	local hitPerfect = Throw.isPerfect(height)
	if pickedLuck then
		height = 1
	end
	-- reach is how far the throw really goes; past the last world the egg lands on The Deep End's floor (Config/DeepEnd).
	-- The player's Power Limit (Config/PowerLimit) stops it short, so strong players can still reach earlier maps.
	local settings = (PlayerData.get(player) or {}).settings or {}
	local fullReach = power * Throw.multiplier(height)
	local reach = PowerLimit.apply(fullReach, settings.powerLimitOn, settings.powerLimit)
	local limited = reach < fullReach
	local distance = math.min(reach, Throw.farthestLanding())
	-- Studio filming mode (FilmingService): the egg lands in the picked monster's map, whatever the power.
	local filmed = FilmingService.pick(player)
	if filmed then
		fullReach, reach, distance, limited = filmed.distance, filmed.distance, filmed.distance, false
	end

	-- The egg in hand when it leaves counts, even if the player swaps mid-flight.
	local egg = EggService.equipped(player)

	state.phase = "flying"
	-- A monster still carried goes back to the hotbar, so it's not on the player's head through the throw and the
	-- reveal walk, where a big one would hide the view. The new catch takes its place after the reveal.
	if Plot.carryNewCatches then
		PlotService.putAway(player)
	end
	state.lucky = pickedLuck
	state.mustLeave = true -- the next meter waits until this player has stepped off the platform
	state.revealDone = nil
	if hitPerfect then
		DailyTasks.count(player, "perfects")
	end
	local luckDistance = Throw.luckDistance(reach)
	remotes.Launched:FireAllClients(player, distance, Throw.isPerfect(height), egg.id, luckDistance)
	FlightStreaming.follow(player, distance) -- the world loads ahead of the egg, not only round the player

	local function land()
		if states[player] ~= state then
			return
		end
		local data = PlayerData.get(player)
		local timedLuck = ShopService.luckMultiplier(player)
		local biome = Luck.biomeAt(distance)
		local pool = biome.rollFrom or biome.id
		local deep = biome.rollFrom ~= nil
		-- The lowest rank among the map's `count` rarest monsters (Config/Hooks counts from the rarest), not counting its
		-- prizes (Config/Dinos): luck reaches those, a guarantee never picks them out.
		local function rarest(count: number): number
			local dinos = Dinos[pool]
			local last = #dinos
			while last > 1 and dinos[last].prize do
				last -= 1
			end
			return last - count + 1
		end

		-- Guarantees (Config/Hooks): the first catch in a new biome, too many throws without a rare one, or the surprise
		-- gift (every 60th throw a Legendary or Mythic; band is the monsters it may be). Only throws on maps where
		-- Legendary and Mythic are high rarities count towards the gift (Config/Hooks surpriseGift).
		local giftBand = CatchOdds.giftFilter(pool, Hooks.surpriseGift)
		local giftMap = giftBand ~= nil
		-- The end-game streak (Config/Hooks apexStreak) only counts where the map has a 9th to 12th monster.
		local apexMap = false
		for _, dino in Dinos[pool] do
			apexMap = apexMap or dino.apex == true
		end
		local minRank, reason, band = nil, nil, nil
		if data and not IndexService.hasCaughtIn(data, pool) then
			minRank, reason = rarest(Hooks.newMapGift.rarest), "newMap"
		elseif data and apexMap and (data.throwsSinceApex or 0) + 1 >= Hooks.apexStreak.throws then
			band, reason = { minPlace = Hooks.apexStreak.minPlace, maxPlace = Hooks.apexStreak.maxPlace }, "apexStreak"
		elseif data and data.throwsSinceRarest + 1 >= Hooks.jackpotPity.throws then
			minRank, reason = rarest(Hooks.jackpotPity.rarest), "jackpot"
		elseif
			data
			and giftMap
			and data.throwsSinceGift + 1 >= Hooks.surpriseGift.throws
		then
			band, reason = giftBand, "gift"
		elseif data and data.throwsSinceRare + 1 >= Hooks.pity.throws then
			minRank, reason = rarest(Hooks.pity.rarest), "pity"
		end
		-- A lucky throw (bought or from the daily reward) is used up here, when the egg lands. Its x number multiplies
		-- the roll's luck, and the catch is guaranteed rare (below).
		local luckyThrow = if data then ShopService.takeLuckyThrow(player, data, state.lucky) else 1
		if luckyThrow > 1 then
			-- Already a guaranteed hit, and its odds must stay what its Details panel showed before buying (CatchOdds).
			minRank, reason, band = nil, nil, nil
		end

		-- The tutorial's two throws (Config/Tutorial): the first is a set modest monster, the second always beats it.
		-- They take the place of the guarantees above. A lucky throw keeps its own odds, but still counts.
		local tutorial = if data and luckyThrow == 1 then TutorialService.planThrow(data, pool, rarest) else nil
		if tutorial then
			minRank = if tutorial.kind == "second" then tutorial.minRank else nil
			reason, band = nil, nil
		end

		-- A new player's first catches (Config/Hooks starterRun): never the map's commonest, and a NEW monster while one
		-- above them is missing from the Index. Only plain throws with no other guarantee; minRank keeps prizes out.
		local starter = Hooks.starterRun
		if data and not tutorial and luckyThrow == 1 and reason == nil and data.totalCaught < starter.catches then
			local lastPlain = rarest(1)
			local floor = math.min(starter.skipCommonest + 1, lastPlain)
			minRank = math.max(minRank or 1, floor)
			if starter.newFirst then
				local missing, anyMissing = {}, false
				for rank = minRank, lastPlain do
					local dino = Dinos[pool][rank]
					if not data.discovered[dino.id] then
						missing[dino.id], anyMissing = true, true
					end
				end
				if anyMissing then
					band = { only = missing }
				end
			end
		end

		-- A new player's big shots (Config/Hooks bigShots): from map 2 on, after its new-world gift, the next plain throws
		-- give a set size and colour on the rarest monster (never the map's very rarest) that stays under the income cap.
		local shots = Hooks.bigShots
		if data and data.bigShotsLeft == -1 then
			data.bigShotsLeft = if data.totalCaught == 0 then #shots.shots else 0 -- only saves started after this existed
		end
		local bigShot = nil
		local mapIndex = if deep then nil else table.find(Biomes, biome)
		if data and data.bigShotsLeft > 0 and not tutorial and luckyThrow == 1 and reason ~= "newMap"
			and mapIndex and mapIndex >= shots.fromMap
		then
			local dinos = Dinos[pool]
			local shot = shots.shots[#shots.shots - data.bigShotsLeft + 1]
			local cap = shots.incomeCap * dinos[rarest(1)].income
			local pickRank = 1 -- the map's commonest if nothing fits (it always does with these numbers)
			for rank = #dinos - 1, 1, -1 do -- rarest first, never the map's very rarest
				local stats = DinoStats.describe({ id = dinos[rank].id, mutation = shot.mutation, size = shot.size })
				if stats and stats.income <= cap then
					pickRank = rank
					break
				end
			end
			bigShot = { rank = pickRank, size = shot.size, mutation = shot.mutation }
			minRank, reason, band = nil, nil, nil
		end

		-- The big number is what players see; the roll counts luck from the biome's par (Luck.forRoll).
		local rollLuck = Luck.forRoll(luckDistance, egg.luckBonus) * timedLuck * luckyThrow
		-- A lucky throw is a guaranteed hit (Config/Catch luckyHits). The luck shown leaves its x out [Owner, 2026-11-06].
		local hit = if luckyThrow > 1 then DinoRoll.luckyHit(luckyThrow) else nil
		local depth = if deep then DeepEnd.depthAt(reach) else 0
		local catch = if filmed and filmed.biome == pool
			then DinoRoll.fixedCatch(pool, filmed.rank, filmed.mutation :: any, filmed.size :: any)
			elseif tutorial and tutorial.kind == "first"
			then TutorialService.plainCatch(pool, tutorial.rank)
			elseif bigShot then DinoRoll.fixedCatch(pool, bigShot.rank, bigShot.mutation, bigShot.size)
			else DinoRoll.rollCatch(pool, rollLuck, minRank, data and data.recentCatches, hit, DeepEnd.boostAt(reach), band, player)
		catch.luck = Luck.at(luckDistance) * Luck.eggFactor(egg.luckBonus, luckDistance) * timedLuck
		-- The surprise gift is never told to the client: it must look like a lucky catch [Owner, 2026-11-08].
		catch.guarantee = if reason == "gift" or filmed then nil else reason
		if data then
			data.throwsSinceRare = if catch.rank >= rarest(Hooks.pity.rarest) then 0 else data.throwsSinceRare + 1
			data.throwsSinceRarest = if catch.rank >= rarest(Hooks.jackpotPity.rarest) then 0 else data.throwsSinceRarest + 1
			-- A streak that had to wait (a lucky throw, a big shot) stays due: the count keeps going until one is caught.
			if apexMap then
				data.throwsSinceApex = if Dinos[pool][catch.rank].apex then 0 else (data.throwsSinceApex or 0) + 1
			end
			-- A gift that had to wait (the 60th throw already had a guarantee or was a lucky throw) comes on the next
			-- plain throw. Throws on maps without the gift don't count.
			data.throwsSinceGift = if reason == "gift" then 0 elseif giftMap then data.throwsSinceGift + 1 else data.throwsSinceGift
			data.recentCatches = { catch.id, data.recentCatches[1] }
			if bigShot then
				data.bigShotsLeft -= 1
			end
			data.farthestThrow = math.max(data.farthestThrow, math.floor(reach))
			if depth > data.deepestDepth then
				data.deepestDepth = depth
				catch.newDepth = depth
			end
		end
		CompetitionService.landedIn(player, biome)
		Analytics.landedIn(player, biome)

		-- Just short of the next biome: the client shows how close it was. Not when the Power Limit stopped it there:
		-- the player chose that spot.
		local nextBiome = Biomes[table.find(Biomes, biome) + 1]
		if limited then
			-- no hint
		elseif deep then
			local nextDepth = DeepEnd.distanceOf(depth + 1)
			if nextDepth - reach <= Hooks.almostThere.studs then
				catch.almostThere = { name = `Depth {depth + 1}`, studs = math.max(math.ceil(nextDepth - reach), 1) }
			end
		elseif nextBiome and nextBiome.startDist - distance <= Hooks.almostThere.studs then
			catch.almostThere = { name = nextBiome.name, studs = math.max(math.ceil(nextBiome.startDist - distance), 1) }
		end
		catch.newBest = data ~= nil and catch.income > data.bestIncome
		if catch.newBest then
			data.bestIncome = catch.income
		end
		if data then
			data.totalCaught += 1
			data.rarestOneIn = math.max(data.rarestOneIn, catch.oneIn)
		end
		-- The world the monster belongs to, which isn't The Deep End's: a Deep End catch can complete it.
		catch.isNew, catch.completedBiome = IndexService.discover(player, catch.id, homeBiome[catch.id] or biome)
		-- Catches wait in the backpack and go onto the player's head when the reveal is done (onRevealDone): every
		-- catch with Config/Plot carryNewCatches, and the tutorial's either way.
		local carry = Plot.carryNewCatches or (data ~= nil and TutorialService.carriesCatch(data))
		local catchKey
		catch.storedIn, catchKey = PlotService.addCatch(player, catch, carry)
		if data then
			TutorialService.recordCatch(player, data, catch, catchKey)
		end
		state.carryKey = if catch.storedIn == "carried" then catchKey else nil
		DailyTasks.count(player, "catches")

		state.phase = "revealing"
		state.revealStartedAt = os.clock()
		DinoLibrary.give(player, { catch.id }) -- the model reaches the player before the reveal needs it
		remotes.Landed:FireClient(player, catch)
		if state.revealDone then
			finishReveal(player, state)
		end

		-- Lucky catch banner for everyone else in the server. The catcher's own client shows it
		-- after their reveal, from the catch it already has.
		if catch.oneIn >= Reveal.luckyBanner.minOneIn then
			local announcement = {
				player = player.Name,
				id = catch.id,
				name = catch.name,
				size = catch.size,
				mutation = catch.mutation,
				oneIn = catch.oneIn,
			}
			for _, other in Players:GetPlayers() do
				if other ~= player then
					remotes.LuckyCatch:FireClient(other, announcement)
				end
			end
		end
	end
	-- If anything in the landing breaks, the player isn't left "in flight" for the rest of their visit: they can throw
	-- again, and their screen stops waiting for the catch.
	task.delay(Throw.releaseDelay() + Throw.flightTime(distance), function()
		local ok, problem = xpcall(land, debug.traceback)
		if not ok then
			warn(`[ThrowService] {player.Name}: the landing failed: {problem}`)
			if states[player] == state and state.phase == "flying" then
				state.phase = "idle"
				FlightStreaming.stop(player)
				remotes.MeterCancel:FireClient(player)
			end
		end
	end)
end

local function onRevealDone(player: Player)
	local state = states[player]
	if not state then
		return
	end
	-- Done before the catch landed here: the client gave up waiting for it, or its throw broke. Before, this was
	-- ignored and the player could never throw again in that server; now the reveal ends as soon as the egg lands.
	if state.phase == "flying" then
		state.revealDone = true
	elseif state.phase == "revealing" then
		finishReveal(player, state)
	end
end

local function step()
	for player, state in states do
		local onPad = isOnPad(player)
		-- Back on the platform right after a throw (the walk home didn't happen) must not start the meter again and
		-- trap the player: they step off first, then back on to throw.
		if not onPad then
			state.mustLeave = false
		end
		if state.phase == "idle" and onPad and not state.mustLeave and TrainingService.getThrowPower(player) then
			state.phase = "aiming"
			state.aimStartedAt = os.clock()
			remotes.MeterStart:FireClient(player)
		elseif state.phase == "aiming" and not onPad then
			state.phase = "idle"
			remotes.MeterCancel:FireClient(player)
		end
	end
end

local function addPlayer(player: Player)
	states[player] = { phase = "idle", aimStartedAt = 0, revealStartedAt = 0 }
end

-- The meter is called off from the player's side: their screen turned it down because they had already walked off
-- the platform (with lag the server sees them there late), or they pressed Back to Plot (HomeService). The next one
-- waits until the server sees them off the platform, so a late position can't start it again. Not during a throw.
function ThrowService.leaveMeter(player: Player)
	local state = states[player]
	if state and (state.phase == "aiming" or state.phase == "idle") then
		state.phase = "idle"
		state.mustLeave = true
	end
end

-- True from the tap until the reveal is done: the egg is in the air or the catch is showing, and nothing may move
-- the thrower. While only aiming they may leave (the meter is called off once they're off the platform).
function ThrowService.isThrowing(player: Player): boolean
	local state = states[player]
	return state ~= nil and (state.phase == "flying" or state.phase == "revealing")
end

function ThrowService.start()
	makeRemotes()
	buildLane()
	RagdollService.addBlocker(ThrowService.isThrowing) -- no ragdoll from the tap until the reveal is done

	RemoteGuard.connect(remotes.Tap, onTap)
	RemoteGuard.connect(remotes.RevealDone, onRevealDone)
	RemoteGuard.connect(remotes.MeterDeclined, ThrowService.leaveMeter)
	Players.PlayerAdded:Connect(addPlayer)
	Players.PlayerRemoving:Connect(function(player)
		states[player] = nil
		FlightStreaming.stop(player)
	end)
	for _, player in Players:GetPlayers() do
		addPlayer(player)
	end

	task.spawn(function()
		while true do
			task.wait(TICK)
			step()
		end
	end)
end

return ThrowService
