-- Play simulation on the game's real Config modules (docs/GAME_SPEC.md section 12): each kind of player in TYPES below
-- trains, throws and shops in their own way, a session a day. Run it from the repo's top folder:
--   ~/.rokit/tool-storage/lune-org/lune/0.10.4/lune run tools/pace_sim.luau
-- Not part of the game: Rojo doesn't sync this folder.
local fs = require("@lune/fs")
local luau = require("@lune/luau")
local roblox = require("@lune/roblox")

local ROOT = "src/shared"
local cache = {}
local node
local RandomStub = { new = function() return { NextNumber = function(_, a, b) return (a or 0) + math.random() * ((b or 1) - (a or 0)) end, NextInteger = function(_, a, b) return math.random(a, b) end } end }
local stubs = { [ROOT .. "/Config/Events"] = { mutationBoosts = function() return nil end } }

local function load(path)
	if stubs[path] then return stubs[path] end
	if cache[path] ~= nil then return cache[path] end
	local src = fs.readFile(path .. ".luau")
	local env = setmetatable({
		script = node(path), require = function(n) return load(rawget(n, "__p")) end,
		game = { GetService = function(_, name) return node(ROOT .. "/__RS") end },
		Color3 = roblox.Color3, Vector3 = roblox.Vector3, Vector2 = roblox.Vector2, UDim2 = roblox.UDim2, UDim = roblox.UDim,
		CFrame = roblox.CFrame, Enum = roblox.Enum, NumberRange = roblox.NumberRange, NumberSequence = roblox.NumberSequence,
		ColorSequence = roblox.ColorSequence, Font = roblox.Font, Random = RandomStub,
	}, { __index = _G })
	local fn = luau.load(luau.compile(src), { debugName = path, environment = env })
	local result = fn()
	cache[path] = result
	return result
end
function node(path)
	return setmetatable({ __p = path }, { __index = function(_, k)
		if k == "Parent" then return node((string.gsub(path, "/[^/]+$", ""))) end
		if k == "Shared" then return node(ROOT) end
		return node(path .. "/" .. k)
	end })
end

local Training = load(ROOT .. "/Config/Training")
local Throw = load(ROOT .. "/Config/Throw")
local Luck = load(ROOT .. "/Config/Luck")
local Biomes = load(ROOT .. "/Config/Biomes")
local DeepEnd = load(ROOT .. "/Config/DeepEnd")
local Dinos = load(ROOT .. "/Config/Dinos")
local Catch = load(ROOT .. "/Config/Catch")
local Plot = load(ROOT .. "/Config/Plot")
local Eggs = load(ROOT .. "/Config/Eggs")
local Hooks = load(ROOT .. "/Config/Hooks")
local CatchOdds = load(ROOT .. "/CatchOdds")
local DinoStats = load(ROOT .. "/DinoStats")

local LAST_WORLD = 15 -- the last world with its own monsters; The Deep End comes after it

local function mapsPassed(d)
	for i, b in Biomes do
		if d <= b.endDist then return i - 1 + math.clamp((d - b.startDist) / (b.endDist - b.startDist), 0, 1) end
	end
	return #Biomes
end

local function rollExtra(options, boost)
	for _, o in options do
		if math.random() < math.min(boost / o.chance, Catch.maxChance) then return o end
	end
end

local function rollCatch(biome, luck, minRank, recent, extraBoost, minRarity)
	local pool = biome.rollFrom or biome.id
	local dinos = Dinos[pool]
	local odds = CatchOdds.monsters(pool, luck, minRank, recent, minRarity)
	local pick, rank = math.random(), #dinos
	for r in dinos do
		pick -= odds[r]
		if odds[r] > 0 and pick <= 0 then rank = r break end
	end
	local boost = math.max(luck, 1) ^ Catch.luckPower * (extraBoost or 1)
	local m, s = rollExtra(Catch.mutations, boost), rollExtra(Catch.sizes, boost)
	local income = dinos[rank].income * (m and m.incomeMultiplier or 1) * (s and s.incomeMultiplier or 1)
	return dinos[rank], rank, income
end

local function rarest(biome, count)
	local dinos = Dinos[biome.rollFrom or biome.id]
	local last = #dinos
	while last > 1 and dinos[last].prize do last -= 1 end
	return last - count + 1
end

local function meterMultiplier(opts)
	if math.random() < (opts.perfect or 0.15) then return Throw.meter.perfectMultiplier end
	local level = math.random(opts.lowLevel or 5, opts.highLevel or 9)
	local m = Throw.meter
	return m.minMultiplier + (m.maxMultiplier - m.minMultiplier) * (level - 1) / (m.levels - 2)
end

-- A lucky throw's catch (DinoRoll.rollCatch with minOneIn): the colour and size make it at least that rare.
local function luckyCatch(biome, luck, multiplier, recent)
	local hit = CatchOdds.luckyHit(multiplier)
	local dino, rank = rollCatch(biome, luck * multiplier, nil, recent, nil, hit.minRarity)
	local options, total = CatchOdds.hitOptions(dino.id, hit.minOneIn, hit.colourAndSize)
	if #options == 0 then
		local dinos = Dinos[biome.rollFrom or biome.id]
		dino, rank = dinos[#dinos], #dinos
		options, total = CatchOdds.hitOptions(dino.id, hit.minOneIn, hit.colourAndSize)
	end
	local pick, chosen = math.random() * total, options[#options]
	for _, option in options do
		pick -= option.weight
		if pick <= 0 then chosen = option break end
	end
	return dino, rank, DinoStats.describe(chosen.entry).income
end

-- One player. opts: session (minutes a day), trainSeconds, throws, tap (share of bubbles tapped), perfect, lowLevel,
-- highLevel (the meter), shop ("cheapest", "noRack", "rackOnly"), passXp, passPower, passCash, packs (+1,000 power packs a day).
local function play(opts)
	local s = { t = 0, day = 1, left = (opts.session or 60) * 60, lucky = 50, power = Training.startPower, xp = 0, ups = 0, cash = 0, plot = {}, plotUps = 0, egg = 1, recent = {}, sinceRare = 0, sinceTop = 0, caught = {}, income = 0 }
	local reached = { [1] = { t = 0, day = 1 } }
	s.power += (opts.packs or 0) * 1000 -- the first day's packs
	local passXp, passPower, passCash = opts.passXp or 1, opts.passPower or 1, opts.passCash or 1
	local capH = opts.capHours or 300

	local function tick(dt) s.t += dt; s.left -= dt; s.cash += s.income * passCash * dt end
	-- Time away between sessions: offline earnings, then the daily reward and any power packs.
	local function nextDay()
		local session = (opts.session or 60) * 60
		local away = math.min(86400 - session, Plot.maxOfflineHours * 3600)
		s.cash += s.income * passCash * Plot.offlineRate * away
		s.day += 1
		s.left = session
		s.lucky = if (s.day - 1) % 7 == 6 then 500 else 50
		s.power += (opts.packs or 0) * 1000
	end
	local function recount()
		table.sort(s.plot, function(a, b) return a > b end)
		local cap = Plot.capacity(s.plotUps)
		while #s.plot > cap do
			s.cash += table.remove(s.plot) * (Plot.sellSeconds or 0)
		end
		local total = 0
		for _, v in s.plot do total += v end
		s.income = total
	end
	local function addXp(amount)
		s.xp += amount
		local gain, need = Training.barFor(s.power, s.ups)
		while s.xp >= need do
			s.xp -= need
			s.power += gain * passPower
			gain, need = Training.barFor(s.power, s.ups)
		end
	end
	local function buy()
		while true do
			local options = {}
			if opts.shop ~= "noRack" then table.insert(options, { price = Training.xpUpgradePrice(s.ups), go = function() s.ups += 1 end }) end
			if s.egg < #Eggs and opts.shop ~= "rackOnly" then table.insert(options, { price = Eggs[s.egg + 1].price, go = function() s.egg += 1 end }) end
			if Plot.capacity(s.plotUps) < Plot.maxSlots and opts.shop ~= "rackOnly" then table.insert(options, { price = Plot.upgradePrice(s.plotUps), go = function() s.plotUps += 1; recount() end }) end
			table.sort(options, function(a, b) return a.price < b.price end)
			local o = options[1]
			if o and o.price <= s.cash then s.cash -= o.price; o.go() else return end
		end
	end

	local sinceBubble = 0
	local depths = {}
	local depthGoal = opts.depthGoal or 0
	local function finished()
		return reached[LAST_WORLD] and (depthGoal == 0 or depths[depthGoal])
	end
	while s.t < capH * 3600 and not finished() do
		if s.left <= 0 then nextDay() end
		-- train
		local train = opts.trainSeconds or 40
		for _ = 1, train do
			tick(Training.repInterval)
			addXp(Training.xpPerRepFor(s.ups) * passXp)
			sinceBubble += 1
			if sinceBubble >= (opts.interval or 3) then
				sinceBubble = 0
				if math.random() < (opts.tap or 0) then addXp(Training.xpPerRepFor(s.ups) * passXp * Training.bubble.multiplier) end
			end
		end
		tick(8) -- walk to the throw pad
		for _ = 1, opts.throws or 4 do
			local reach = s.power * meterMultiplier(opts)
			local distance = math.min(reach, Throw.farthestLanding())
			tick(2 + Throw.releaseDelay() + Throw.flightTime(distance) + 8) -- meter, wind-up, flight, reveal, then home and the walk back (about 3 s at walkSpeed 32)
			local biome = Luck.biomeAt(distance)
			local index = table.find(Biomes, biome)
			local minRank
			if not s.caught[biome.id] then minRank = rarest(biome, Hooks.newMapGift.rarest)
			elseif s.sinceTop + 1 >= Hooks.jackpotPity.throws then minRank = rarest(biome, Hooks.jackpotPity.rarest)
			elseif s.sinceRare + 1 >= Hooks.pity.throws then minRank = rarest(biome, Hooks.pity.rarest) end
			local luck = Luck.forRoll(distance, Eggs[s.egg].luckBonus)
			local dino, rank, income
			if s.lucky then
				dino, rank, income = luckyCatch(biome, luck, s.lucky, s.recent)
				s.lucky = nil
			else
				dino, rank, income = rollCatch(biome, luck, minRank, s.recent, DeepEnd.boostAt(reach))
			end
			s.sinceRare = if rank >= rarest(biome, Hooks.pity.rarest) then 0 else s.sinceRare + 1
			s.sinceTop = if rank >= rarest(biome, Hooks.jackpotPity.rarest) then 0 else s.sinceTop + 1
			s.recent = { dino.id, s.recent[1] }
			s.caught[biome.id] = true
			table.insert(s.plot, income)
			recount()
			for depth = 1, DeepEnd.depthAt(reach) do
				depths[depth] = depths[depth] or s.t
			end
			for m = 2, math.min(index, LAST_WORLD) do
				if not reached[m] then
					reached[m] = { t = s.t, day = s.day, ups = s.ups, need = select(2, Training.barFor(s.power, s.ups)), perRep = Training.xpPerRepFor(s.ups) * passXp, perBar = Training.barFor(s.power, s.ups) * passPower, power = s.power, income = s.income, cash = s.cash }
				end
			end
			buy()
		end
		tick(8)
	end
	reached.depths = depths
	return reached
end

local function median(list)
	table.sort(list)
	return list[math.ceil(#list / 2)]
end

local function fmt(sec)
	if not sec then return " -  " end
	if sec < 3600 then return string.format("%dm", math.floor(sec / 60 + 0.5)) end
	return string.format("%.1fh", sec / 3600)
end

local RUNS = 9
local SHOWN = { 3, 5, 8, 10, 12, 13, 14, 15 }

local function report(label, opts)
	local all = {}
	for r = 1, RUNS do all[r] = play(opts) end
	local cells = {}
	local function at(run, m) return run[m] and run[m].t or math.huge end
	for _, m in SHOWN do
		local ts = {}
		for _, run in all do table.insert(ts, at(run, m)) end
		local t = median(ts)
		table.insert(cells, if t == math.huge then "never" else fmt(t))
	end
	-- days to map 10 and 15, the longest late map, and squats a bar at the end
	local function days(m)
		local ds = {}
		for _, run in all do table.insert(ds, run[m] and run[m].day or math.huge) end
		local d = median(ds)
		return if d == math.huge then "never" else tostring(d)
	end
	local gaps, spread, squats = {}, {}, {}
	for _, run in all do
		local worst = 0
		for m = 11, LAST_WORLD do
			if run[m] and run[m - 1] then worst = math.max(worst, run[m].t - run[m - 1].t) end
		end
		table.insert(gaps, worst)
		table.insert(spread, at(run, LAST_WORLD))
		local e = run[LAST_WORLD] or run[12]
		if e then table.insert(squats, e.need / e.perRep) end
	end
	table.sort(spread)
	local shownSpread = if spread[#spread] == math.huge then "-" else `{fmt(spread[1])}-{fmt(spread[#spread])}`
	print(`| {label} | {table.concat(cells, " | ")} | {days(10)} | {days(LAST_WORLD)} | {fmt(median(gaps))} | {shownSpread} |`)
end

-- Every kind of player. session = minutes a day; the rest is how they spend it.
local AVERAGE = { session = 60, trainSeconds = 40, throws = 4, tap = 0.7 }
local function with(extra)
	local copy = table.clone(AVERAGE)
	for key, value in extra do copy[key] = value end
	return copy
end
local TYPES = {
	{ "Free: casual (20 min a day)", with({ session = 20, trainSeconds = 20, throws = 3, tap = 0.3, perfect = 0.07, lowLevel = 3, highLevel = 8 }) },
	{ "Free: average (1 h a day)", AVERAGE },
	{ "Free: keen (3 h a day)", with({ session = 180, trainSeconds = 60, tap = 0.9, perfect = 0.25, lowLevel = 6 }) },
	{ "Free: grinder (6 h a day)", with({ session = 360, trainSeconds = 120, throws = 3, tap = 1, perfect = 0.3, lowLevel = 6 }) },
	{ "Free: leaves it squatting (2 h)", with({ session = 120, trainSeconds = 300, throws = 2, tap = 0 }) },
	{ "Free: loves throwing", with({ trainSeconds = 10, throws = 8, tap = 0.5, perfect = 0.25, lowLevel = 6 }) },
	{ "Free: bad at the meter", with({ perfect = 0.03, lowLevel = 2, highLevel = 7 }) },
	{ "Free: never taps bubbles", with({ tap = 0 }) },
	{ "Free: never buys rack upgrades", with({ shop = "noRack" }) },
	{ "Free: only buys rack upgrades", with({ shop = "rackOnly" }) },
	{ "Paid: x2 Cash", with({ passCash = 2 }) },
	{ "Paid: x2 Training", with({ passXp = 2 }) },
	{ "Paid: x2 Power", with({ passPower = 2 }) },
	{ "Paid: x2 Training + x2 Power", with({ passXp = 2, passPower = 2 }) },
	{ "Paid: all 3 passes, keen", with({ session = 180, trainSeconds = 60, tap = 0.9, perfect = 0.25, lowLevel = 6, passXp = 2, passPower = 2, passCash = 2 }) },
	{ "Paid: all passes + a pack a day", with({ session = 180, trainSeconds = 60, tap = 0.9, perfect = 0.25, lowLevel = 6, passXp = 2, passPower = 2, passCash = 2, packs = 1 }) },
}

do
	local run = play(AVERAGE)
	local cells = {}
	for m = 2, LAST_WORLD do
		local e = run[m]
		table.insert(cells, if e then string.format("w%d %.0f sq +%d", m, e.need / e.perRep, e.perBar) else `w{m} -`)
	end
	print("Average player's bar on arriving at each world: " .. table.concat(cells, ", "))
end
-- The Deep End: play time to reach each Depth, for those who'd keep at it.
local GOAL = 10
print(`Play time to Depth 1 to {GOAL}, median of 5 runs, capped at 900 h.`)
for _, entry in TYPES do
	local name = entry[1]
	if name:find("average") or name:find("keen") or name:find("grinder") or name:find("casual") or name:find("all 3") then
		local opts = table.clone(entry[2])
		opts.depthGoal, opts.capHours = GOAL, 900
		local all = {}
		for r = 1, 5 do all[r] = play(opts) end
		local cells = {}
		for depth = 1, GOAL do
			local ts = {}
			for _, run in all do table.insert(ts, run.depths[depth] or math.huge) end
			local t = median(ts)
			table.insert(cells, if t == math.huge then "-" else fmt(t))
		end
		print(`| {name} | {table.concat(cells, " | ")} |`)
	end
end
print(`Play time to reach each map, median of {RUNS} runs, capped at 300 h of play.`)
print(`| Player | m{table.concat(SHOWN, " | m")} | days to m10 | days to m15 | longest late map | m15 fastest-slowest |`)
for _, entry in TYPES do
	report(entry[1], entry[2])
end
