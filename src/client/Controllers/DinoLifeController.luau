-- Brings plot dinos to life: each walks to a roomy spot on its plot (steering round the others), idles, and repeats,
-- and while the plot's owner stands on it they gather in a circle round them (updateRings). Each moves its
-- skeleton as it goes. Runs on each client only; the server just places the dino. The poses copy the
-- Walk and Idle loops in assets/models/build_forest.py, and the jaw and roar of the monsters that
-- have a Jaw bone copy build_volcano.py. Monsters with a Swim bone swim and hover instead (SWIM and HOVER,
-- copying build_abyss_monsters.py). Monsters with Lash bones thrash on top of it all (THRASH, copying
-- build_thorn_kingdom_monsters.py), and ones with a Drip bone attack too, crying as they do (RAGE and DRIP, copying
-- build_weeping_dark_monsters.py). Monsters with Vent bones pour spores and pounce (VENT and POUNCE, copying
-- build_spore_hollow_monsters.py). Each map's 7th and 8th monsters add SWAY on top: swaying feathers, snapping pincers, a
-- stabbing sting, a slithering body, a lunging neck (copying assets/models/rare_kit.py). Every monster with an attack plays it only
-- once a DinoLife.attackCycle, standing still for it, and roams like the rest in between. Dinos without
-- bones still walk, stiffly.
local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Config = ReplicatedStorage.Shared.Config
local DinoLife = require(Config.DinoLife)
local DinoModel = require(ReplicatedStorage.Shared.DinoModel)
local Plot = require(Config.Plot)
local Troll = require(Config.Troll)
local LowDetail = require(script.Parent.LowDetail)
local LOW = require(Config.Settings).lowDetailLook.monsters

local DinoLifeController = {}

local TAU = 2 * math.pi
local sin, cos = math.sin, math.cos

-- Each pose returns pitch, roll, yaw and how far the bone rises.
-- p runs through one stride; t runs through one idle loop.
local WALK = {}
local IDLE = {}

WALK.Spine = function(p)
	return 0.02 * sin(2 * p), 0.05 * sin(p), 0.05 * sin(p), 0.07 * cos(2 * p)
end
IDLE.Spine = function(t)
	return 0.025 * sin(4 * t), 0, 0, 0.03 * sin(4 * t)
end

for letter, phase in { L = 0, R = math.pi } do
	local side = if letter == "L" then -1 else 1
	WALK["Leg" .. letter] = function(p)
		return 0.45 * sin(p + phase), 0, 0, 0
	end
	WALK["Shin" .. letter] = function(p)
		return -0.6 * (0.5 + 0.5 * cos(p + phase)) ^ 2, 0, 0, 0
	end
	WALK["Arm" .. letter] = function(p)
		return -0.3 * sin(p + phase), 0, 0, 0
	end
	WALK["Wing" .. letter] = function(p)
		return 0, side * 0.14 * sin(2 * p), 0, 0
	end
	WALK["WingTip" .. letter] = function(p)
		return 0, side * 0.1 * sin(2 * p - 0.8), 0, 0
	end
	IDLE["Arm" .. letter] = function(t)
		return 0.08 * sin(4 * t + 0.5), 0, 0, 0
	end
	IDLE["Wing" .. letter] = function(t)
		return 0, side * 0.07 * sin(4 * t), 0, 0
	end
	IDLE["WingTip" .. letter] = function(t)
		return 0, side * 0.06 * sin(4 * t - 0.8), 0, 0
	end
end

-- Four-legged walkers move opposite corners together.
for name, phase in { FrontL = 0, BackR = 0, FrontR = math.pi, BackL = math.pi } do
	WALK[name] = function(p)
		return 0.32 * sin(p + phase), 0, 0, 0
	end
end

for i = 1, 3 do
	WALK["Tail" .. i] = function(p)
		return 0.03 * sin(2 * p - i * 0.6), 0, 0.16 * sin(p - i * 0.7), 0
	end
	IDLE["Tail" .. i] = function(t)
		return 0.02 * sin(4 * t - i * 0.5), 0, 0.14 * sin(2 * t - i * 0.6), 0
	end
end

WALK.Neck = function(p)
	return 0.05 * sin(2 * p + 0.5), 0, 0.05 * sin(p + 0.6), 0
end
IDLE.Neck = function(t)
	return 0.05 * sin(2 * t + 1), 0, 0.14 * sin(t), 0
end
WALK.Head = function(p)
	return -0.06 * sin(2 * p + 0.5), 0, 0.08 * sin(p + 1.2), 0
end
IDLE.Head = function(t)
	return 0.09 * sin(3 * t), 0, 0.36 * sin(t) + 0.08 * sin(3 * t), 0
end

-- Monsters with a Jaw bone (from Volcano on) snap it in time with their steps, and roar once
-- per idle loop: head thrown up, jaw dropped wide, arms out and a shake of the head. ROAR is added on
-- top of the idle above, for those monsters only.
local function roar(t: number): number
	return ((1 - cos(t)) / 2) ^ 10 -- 0 most of the loop, up to 1 halfway through it
end
local ROAR_FROM = math.pi - 0.75 -- where in its idle loop a monster starts a roar, about a second before its peak

WALK.Jaw = function(p)
	return -0.08 * (0.5 + 0.5 * sin(2 * p)), 0, 0, 0
end
IDLE.Jaw = function(t)
	return -0.03 * (0.5 + 0.5 * sin(4 * t)) - 0.55 * roar(t), 0, 0, 0
end

local ROAR = {}
ROAR.Spine = function(t)
	return 0.03 * roar(t), 0, 0, 0
end
ROAR.ArmL = function(t)
	return 0.45 * roar(t), 0, 0, 0
end
ROAR.ArmR = ROAR.ArmL
ROAR.Tail1 = function(t)
	return 0.08 * roar(t), 0, 0, 0
end
ROAR.Neck = function(t)
	return 0.12 * roar(t), 0, 0, 0
end
ROAR.Head = function(t)
	local r = roar(t)
	return 0.3 * r, 0, 0.08 * sin(14 * t) * r, 0
end
ROAR.PalmL = function(t) -- Endless Grief's hands pull away from its face
	return 0, 0, 0.8 * roar(t), 0
end
ROAR.PalmR = function(t)
	return 0, 0, -0.8 * roar(t), 0
end
ROAR.MandL = function(t) -- Spore Hollow's side jaws fling open
	return 0, 0, 0.6 * roar(t), 0
end
ROAR.MandR = function(t)
	return 0, 0, -0.6 * roar(t), 0
end
ROAR.PinchL = function(t) -- Scorchion's pincers fling open
	return 0, 0, 0.55 * roar(t), 0
end
ROAR.PinchR = function(t)
	return 0, 0, -0.55 * roar(t), 0
end

-- Monsters with a Swim bone (from The Abyss on) swim instead of walking: SWIM while they move and HOVER while
-- they wait, which ends each loop with an attack (they rear up and lunge, jaw wide, shaking their head and
-- thrashing their tail). The poses copy assets/models/build_abyss_monsters.py. Each also returns surge: how far
-- the bone moves forward, for the lunge. Their models float just above the ground, so they hover over the base.
local SWIM = {}
local HOVER = {}

-- Spiral Gary's eight tentacles ring its beak; tentacle n sits at this angle round the front (0 = its right).
local function tentacleTurn(n: number, spread: number, wriggle: number): (number, number)
	local angle = (n - 1) * TAU / 8 + math.pi / 8
	return spread * sin(angle) + wriggle * cos(angle), -spread * cos(angle) + wriggle * sin(angle)
end

SWIM.Swim = function(p)
	return 0.03 * sin(2 * p), 0.05 * sin(p), -0.05 * sin(p), 0.06 * sin(2 * p), 0
end
HOVER.Swim = function(t)
	local r = roar(t)
	return 0.02 * sin(2 * t) + 0.12 * r, 0.03 * sin(t) + 0.05 * sin(14 * t) * r, 0, 0.12 * sin(2 * t), 0.6 * r
end
SWIM.Head = function(p)
	return 0.02 * sin(2 * p), 0, -0.06 * sin(p), 0, 0
end
HOVER.Head = function(t)
	local r = roar(t)
	return 0.06 * sin(3 * t) + 0.22 * r, 0, 0.15 * sin(t) + 0.05 * sin(3 * t) + 0.12 * sin(14 * t) * r, 0, 0
end
for i = 1, 3 do
	SWIM["Neck" .. i] = function(p)
		return 0.03 * sin(2 * p - 0.4 * i), 0, -0.05 * sin(p - 0.4 * i), 0, 0
	end
	HOVER["Neck" .. i] = function(t)
		return 0.05 * sin(2 * t + i) + 0.1 * roar(t), 0, 0.12 * sin(t - 0.3 * i), 0, 0
	end
end
for i = 1, 4 do
	SWIM["Tail" .. i] = function(p)
		return 0.02 * sin(2 * p - i), 0, (0.14 + 0.05 * i) * sin(p - 0.75 * i), 0, 0
	end
	HOVER["Tail" .. i] = function(t)
		return 0, 0, (0.06 + 0.03 * i) * sin(4 * t - 0.75 * i) + 0.22 * sin(10 * t - i) * roar(t), 0, 0
	end
end
for letter, side in { L = -1, R = 1 } do
	SWIM["Fin" .. letter] = function(p)
		return 0.08 * sin(p + 1), side * 0.18 * sin(p), 0, 0, 0
	end
	HOVER["Fin" .. letter] = function(t)
		return 0, side * (0.1 * sin(4 * t) + 0.4 * roar(t)), 0, 0, 0
	end
	-- Front and back flippers beat in turn.
	for pair, phase in { F = 0, B = math.pi } do
		SWIM["Flipper" .. pair .. letter] = function(p)
			return 0.25 * cos(p + phase), side * 0.45 * sin(p + phase), 0, 0, 0
		end
		HOVER["Flipper" .. pair .. letter] = function(t)
			return 0.1 * cos(4 * t + phase), side * (0.18 * sin(4 * t + phase) - 0.45 * roar(t)), 0, 0, 0
		end
	end
end
SWIM.Jaw = function(p)
	return -0.1 * (0.5 + 0.5 * sin(2 * p)), 0, 0, 0, 0
end
HOVER.Jaw = function(t)
	return -0.04 * (0.5 + 0.5 * sin(4 * t)) - 0.7 * roar(t), 0, 0, 0, 0
end
SWIM.Lure = function(p)
	return 0.15 * sin(2 * p), 0, 0.1 * sin(p), 0, 0
end
HOVER.Lure = function(t)
	return 0.1 * sin(3 * t) - 0.3 * roar(t), 0, 0.25 * sin(t), 0, 0
end
SWIM.LureTip = function(p)
	return 0.2 * sin(2 * p - 1), 0, 0, 0, 0
end
HOVER.LureTip = function(t)
	return 0.15 * sin(3 * t - 1) - 0.25 * roar(t), 0, 0, 0, 0
end
for n = 1, 8 do
	-- Each tentacle on two bones: they pulse open and shut as it swims, and flare wide in the attack.
	SWIM["Tentacle" .. n] = function(p)
		local pitch, yaw = tentacleTurn(n, 0.08 + 0.16 * (0.5 + 0.5 * sin(p)), 0.12 * sin(2 * p - 0.8 * n))
		return pitch, 0, yaw, 0, 0
	end
	SWIM["Tentacle" .. n .. "b"] = function(p)
		local pitch, yaw = tentacleTurn(n, 0.18 * sin(p - 1.2), 0.18 * sin(2 * p - 0.8 * n - 1))
		return pitch, 0, yaw, 0, 0
	end
	HOVER["Tentacle" .. n] = function(t)
		local pitch, yaw = tentacleTurn(n, 0.1 + 0.06 * sin(2 * t) + 0.5 * roar(t), 0.14 * sin(4 * t - 0.8 * n))
		return pitch, 0, yaw, 0, 0
	end
	HOVER["Tentacle" .. n .. "b"] = function(t)
		local r = roar(t)
		local pitch, yaw =
			tentacleTurn(n, 0.1 * sin(2 * t - 1) + 0.35 * r, 0.16 * sin(4 * t - 0.8 * n - 1) + 0.1 * sin(14 * t) * r)
		return pitch, 0, yaw, 0, 0
	end
end

-- Clockwork monsters (Clockwork Citadel on) have parts that turn for ever on their own bone, whatever the monster is
-- doing: the wind-up key in their back (Key, round the upright), Drillhorn's nose drill (Drill, round its forward
-- axis), Gearjaw's saw and Chrono Rex's gear sail (Cog, round the sideways axis). Radians a second, on top of the walk
-- and idle; the same as SPIN in assets/models/build_clockwork_citadel_monsters.py, whose preview turns them alike.
local SPIN = {
	Key = { speed = math.pi, axis = "yaw" },
	Drill = { speed = 4 * math.pi, axis = "roll" },
	Cog = { speed = math.pi, axis = "pitch" },
	Orbit = { speed = math.pi / 4, axis = "yaw" }, -- Moonwhale's little moon, going round it
	-- Maps 14 and 15's 9th to 12th monsters (assets/models/apex_kit.py, SPIN): what floats over them or rides on them, turning.
	Halo = { speed = math.pi / 2, axis = "yaw" }, -- Acid Reign's crown, Sporeactor's upright ring, Mourning Star's star, Nevermore's feathers
	Wheel = { speed = math.pi / 2, axis = "roll" }, -- Grim Weeper's wheel of eyes
	Hoop = { speed = math.pi / 2, axis = "pitch" }, -- Sporeactor's level ring
	Saw = { speed = 2 * math.pi, axis = "pitch" }, -- Cap Punishment's saw
}

-- Thorn Kingdom monsters (from map 13 on) never settle, whatever they're doing. A monster with Lash bones gets all of
-- THRASH on top of its walk and idle: its briar whips (Lash<n>a, b, c, three bones down each) thrash with a rhythm of
-- their own, swelling, dying down and cracking every 4 seconds; its head snaps round in sudden jerks, its jaw gnashes
-- in bursts, its body shudders, its arms and tail twitch. Snap<n> bones are the jaws of Hydrangry's spare heads. Each
-- takes seconds and returns pitch, roll and yaw; the same as thrash_of in
-- assets/models/build_thorn_kingdom_monsters.py, whose preview moves them alike.
local QUARTER = math.pi / 2 -- everything thrashes at whole multiples of this, so the pattern repeats every 4 seconds

local function crack(x: number): number -- 0 nearly all the time, jolting up to 1 and back once a turn of x
	return ((1 + cos(x)) / 2) ^ 14
end

local function burst(x: number): number -- quiet about half the time, then swelling to 1 and dying away
	return ((1 + sin(x)) / 2) ^ 3
end

local THRASH = {}
for n = 1, 8 do
	for k, letter in { "a", "b", "c" } do
		local phase = 1.9 * n - 0.85 * (k - 1)
		local reach = 0.3 + 0.16 * (k - 1) -- each bone bends further than the one before it
		local snap = 0.5 + 0.3 * (k - 1)
		THRASH["Lash" .. n .. letter] = function(s: number)
			local w = QUARTER * s
			local size = reach * (0.55 + 0.45 * sin(w + 2.1 * n))
			local cracked = snap * crack(w + 2.4 * n - 0.5 * (k - 1))
			return size * (sin(6 * w + phase) + 0.4 * sin(11 * w + 1.3 * phase)) + cracked,
				size * sin(5 * w + 2 * phase),
				size * (sin(7 * w + 0.7 * phase) + 0.4 * sin(13 * w + phase)) - 0.6 * cracked
		end
	end
	THRASH["Snap" .. n] = function(s: number)
		local w = QUARTER * s
		return -0.14 - 0.14 * sin(10 * w + 1.7 * n) - 0.3 * crack(2 * w + 1.3 * n), 0, 0
	end
end
THRASH.Head = function(s: number)
	local w = QUARTER * s
	local a, b = crack(2 * w + 0.7), crack(3 * w + 2.2)
	return 0.16 * b - 0.12 * a, 0.2 * a * cos(w), 0.34 * a * sin(w + 1) - 0.26 * b * cos(w)
end
THRASH.Neck = function(s: number)
	local w = QUARTER * s
	local shiver = 0.05 * sin(16 * w) * burst(w + 2)
	return shiver, 0, shiver
end
THRASH.Jaw = function(s: number)
	local w = QUARTER * s
	return -0.2 * (0.5 + 0.5 * sin(12 * w)) * burst(2 * w), 0, 0
end
THRASH.Spine = function(s: number)
	local w = QUARTER * s
	local b = burst(w + 4)
	return 0.02 * sin(16 * w) * b, 0.03 * sin(12 * w) * b, 0
end
for letter, offset in { L = 0, R = 2.5 } do
	THRASH["Arm" .. letter] = function(s: number)
		return -0.35 * crack(3 * QUARTER * s + offset), 0, 0
	end
end
for i = 1, 3 do
	THRASH["Tail" .. i] = function(s: number)
		local w = QUARTER * s
		return 0, 0, 0.22 * sin(6 * w - 0.9 * i) * burst(w + i)
	end
end

-- The Prism Egg's swimmers (Duskeel, Umbray, Dreadlure; assets/models/build_special_monsters.py) swim and have Lash
-- bones, but theirs are whiskers, not briar whips, and their heads are the front of their bodies, not on a neck. THRASH
-- flung the whiskers 80 degrees and jerked the head (eyes, horns and all) right off the hull, so instead the whiskers
-- trail in a slow wave (WHISKER) and the head and jaw move only this much of the swim and hover.
local WHISKER = {}
for n = 1, 8 do
	for k, letter in { "a", "b", "c" } do
		local reach = 0.05 + 0.04 * (k - 1) -- the tip sways most, about 18 degrees from the lip in all
		WHISKER["Lash" .. n .. letter] = function(s: number)
			local w = QUARTER * s
			return reach * sin(2 * w - 0.8 * k + 1.3 * n), 0, 0.7 * reach * sin(w - 0.8 * k + 2 * n)
		end
	end
end
local WHISKERED_DAMPING = { Head = 0.3, Jaw = 0.6, Neck1 = 0.5, Neck2 = 0.5, Neck3 = 0.5 }

local function damped(pose, k: number)
	return function(x: number)
		local a, b, c, d, e = pose(x)
		return a * k, b * k, c * k, (d or 0) * k, (e or 0) * k
	end
end

-- The Weeping Dark's monsters (map 15) don't just thrash, they attack. A monster with a tear bone (DRIP) gets all of RAGE on
-- top of the rest: every 4 seconds it loads up and lunges, heaving back, slamming forward, its head driving in, its jaw
-- dropping and biting shut, its tail cracking; its arms claw one after the other, 2 seconds apart; it snaps at the air
-- between lunges; and it pants and shakes all the time. Each takes seconds and returns pitch, roll, yaw, rise and surge.
-- It also charges: a stride takes rageStrideSeconds (Config/DinoLife). The same as rage_of in
-- assets/models/build_weeping_dark_monsters.py, whose preview moves them alike.
local function smooth(t: number): number
	return t * t * (3 - 2 * t)
end

local function strike(x: number): number -- 0 most of the time; once a turn of x, a slam to 1, held, then a slower recovery
	local u = (x / TAU) % 1
	if u < 0.05 then
		return smooth(u / 0.05)
	elseif u < 0.12 then
		return 1
	elseif u < 0.34 then
		return 1 - smooth((u - 0.12) / 0.22)
	end
	return 0
end

local function windup(x: number): number -- the moment before strike: up to 1 at the end of the turn, gone as strike lands
	local u = (x / TAU) % 1
	if u > 0.9 then
		return smooth((u - 0.9) / 0.1)
	elseif u < 0.05 then
		return 1 - smooth(u / 0.05)
	end
	return 0
end

local RAGE = {}
RAGE.Spine = function(s: number)
	local w = QUARTER * s
	local hit, load = strike(w), windup(w)
	return -0.1 * hit + 0.09 * load + 0.014 * sin(8 * w), 0, 0, 0.05 * sin(8 * w) - 0.1 * hit, 0.55 * hit - 0.3 * load
end
RAGE.Neck = function(s: number)
	local w = QUARTER * s
	return -0.2 * strike(w) + 0.14 * windup(w) - 0.08 * strike(2 * w + math.pi), 0, 0, 0, 0
end
RAGE.Head = function(s: number)
	local w = QUARTER * s
	local hit = strike(w)
	return 0.16 * hit - 0.1 * windup(w) + 0.1 * strike(2 * w + math.pi), 0.03 * sin(20 * w) * (0.3 + hit), 0.1 * sin(14 * w) * hit, 0, 0
end
RAGE.Jaw = function(s: number)
	local w = QUARTER * s
	local nip = 2 * w + math.pi
	return -0.5 * windup(w) + 0.2 * strike(w) - 0.3 * windup(nip) + 0.12 * strike(nip), 0, 0, 0, 0
end
for letter, offset in { L = 0, R = math.pi } do -- one claw, then the other
	RAGE["Arm" .. letter] = function(s: number)
		local x = QUARTER * s + offset
		return 1.2 * windup(x) - 0.6 * strike(x), 0, 0, 0, 0
	end
end
for letter, side in { L = 1, R = -1 } do
	RAGE["Front" .. letter] = function(s: number)
		local w = QUARTER * s
		return 0.42 * strike(w) - 0.24 * windup(w), 0, 0, 0, 0
	end
	RAGE["Back" .. letter] = function(s: number)
		local w = QUARTER * s
		return -0.2 * strike(w) + 0.1 * windup(w), 0, 0, 0, 0
	end
	RAGE["Leg" .. letter] = function(s: number)
		local w = QUARTER * s
		return side * (0.3 * strike(w) - 0.1 * windup(w)), 0, 0, 0, 0
	end
	RAGE["Shin" .. letter] = function(s: number)
		return (if letter == "L" then -0.2 else -0.5) * strike(QUARTER * s), 0, 0, 0, 0
	end
	RAGE["Palm" .. letter] = function(s: number) -- Endless Grief's hands, pulling away from its face
		local w = QUARTER * s
		return 0, 0, side * (0.5 * strike(w) + 0.24 * windup(w)), 0, 0
	end
end
for i = 1, 3 do
	RAGE["Tail" .. i] = function(s: number)
		local crack_ = strike(QUARTER * s - 0.3 * i)
		return 0.1 * crack_, 0, 0.42 * crack_, 0, 0
	end
end

-- Tears that fall for ever on a bone, whatever the head is doing, like a prop's `fall`: they're `gap` studs apart (at
-- the first map's size) and each takes `period` seconds to reach where the next began, so they loop seamlessly. Periods
-- divide 4, the length of the thrash clock. The same as DRIP in build_weeping_dark_monsters.py.
local DRIP = {
	Drip = { gap = 0.6, period = 0.8 },
	DripB = { gap = 1.6, period = 1 },
}

-- Spore Hollow's monsters (map 14) pour spores and pounce. A monster with Vent bones has a column of spore clouds over
-- each vent in its hide, lifted one gap every period and dropped back, so the spores pour out for ever (each cloud only
-- goes as far as where the one above it began; studs at the first map's size). It also gets all of POUNCE on top of the
-- rest: every 4 seconds it rears back, front legs up and side jaws (MandL, MandR) spread wide, then lunges, neck down,
-- jaw flung open, arms raking and side jaws slamming shut, and slowly draws back; the rest of the time its side jaws
-- gnash. Each takes seconds and returns pitch, roll and yaw. The same as VENT_GAP, VENT_PERIOD and pounce_of in
-- assets/models/build_spore_hollow_monsters.py, whose preview moves them alike.
local VENT = { gap = 0.6, period = 0.8 }

-- 0, easing up to 1 over `rise` seconds from `start`, held for `hold`, easing back over `fall`; once every 4 seconds.
local function pounceCurve(s: number, start: number, rise: number, hold: number, fall: number): number
	local function ease(u: number): number
		return u * u * (3 - 2 * u)
	end
	local t = (s - start) % 4
	if t < rise then
		return ease(t / rise)
	end
	t -= rise
	if t < hold then
		return 1
	end
	t -= hold
	if t < fall then
		return 1 - ease(t / fall)
	end
	return 0
end

local function rearing(s: number): number -- rearing back, before the lunge
	return pounceCurve(s, 0.15, 0.5, 0.15, 0.12)
end

local function lunging(s: number): number -- the lunge, and drawing slowly back
	return pounceCurve(s, 0.8, 0.12, 0.22, 0.6)
end

local POUNCE = {}
POUNCE.Spine = function(s: number)
	return 0.06 * rearing(s) - 0.08 * lunging(s), 0, 0
end
POUNCE.Neck = function(s: number)
	return 0.2 * rearing(s) - 0.4 * lunging(s), 0, 0
end
POUNCE.Head = function(s: number)
	return 0.14 * rearing(s) + 0.2 * lunging(s), 0, 0
end
POUNCE.Jaw = function(s: number)
	return -0.12 * rearing(s) - 0.7 * lunging(s), 0, 0
end
POUNCE.Tail1 = function(s: number)
	return 0.14 * rearing(s) - 0.06 * lunging(s), 0, 0
end
for letter, side in { L = 1, R = -1 } do
	POUNCE["Mand" .. letter] = function(s: number)
		return 0, 0, side * ((0.1 + 0.08 * sin(8 * QUARTER * s)) * (1 - lunging(s)) + 0.5 * rearing(s))
	end
	POUNCE["Arm" .. letter] = function(s: number)
		return -0.3 * rearing(s) + 0.9 * lunging(s), 0, 0
	end
	POUNCE["Front" .. letter] = function(s: number)
		return 0.3 * rearing(s) - 0.06 * lunging(s), 0, 0
	end
	POUNCE["Wing" .. letter] = function(s: number)
		return 0, side * 0.35 * rearing(s), 0
	end
end

local function zero()
	return 0, 0, 0, 0, 0
end

local function plus(a, b)
	return function(x)
		local ax, ay, az, ab, asurge = a(x)
		local bx, by, bz, bb, bsurge = b(x)
		return ax + bx, ay + by, az + bz, ab + bb, (asurge or 0) + (bsurge or 0)
	end
end

local dinos: { [Model]: any } = {}
-- The walking monsters on each plot (not the best catch on its pedestal, not carried ones), so they can circle their owner
-- and keep out of each other's way.
local plotMembers: { [number]: { any } } = {}
-- Each plot's circle while its owner stands on it (DinoLife ring): who's in it, how wide, and each one's place.
local rings: { [number]: any } = {}
-- Where each plot monster stood when it was last removed. The server rebuilds a plot's monsters whenever one is placed,
-- picked up or sold, and the new ones carry on from here instead of jumping back to their saved spots.
local lastPlaces: { [string]: any } = {}

local function flat(v: Vector3): Vector3
	return Vector3.new(v.X, 0, v.Z)
end

local function placeKey(model: Model): string?
	local plotIndex, key = model:GetAttribute("PlotIndex"), model:GetAttribute("DinoKey")
	return if plotIndex and key then `{plotIndex}:{key}` else nil
end

local function joinPlot(state)
	local list = plotMembers[state.plotIndex] or {}
	plotMembers[state.plotIndex] = list
	table.insert(list, state)
	local ring = rings[state.plotIndex]
	if ring then
		ring.dirty = true
	end
end

local function leavePlot(state)
	local list = plotMembers[state.plotIndex]
	local i = list and table.find(list, state)
	if i then
		table.remove(list, i)
	end
	local ring = rings[state.plotIndex]
	if ring then
		ring.dirty = true
	end
end

-- How much free ground a spot has: the gap to the nearest other monster on the plot (where it stands, or where it's
-- heading), less both their bodies.
local function room(state, spot: Vector3): number
	local best = math.huge
	for _, other in plotMembers[state.plotIndex] or {} do
		if other ~= state then
			local here = flat(spot - other.position).Magnitude
			local there = if other.target then flat(spot - other.target).Magnitude else math.huge
			best = math.min(best, math.min(here, there) - other.radius - state.radius)
		end
	end
	return best
end

-- A spot on the plot to wander to: of a few tried, the roomiest, so monsters spread out instead of bunching up. Room past
-- a couple of body widths counts no more, and a little chance stays in, so they don't all head for the corners.
local function wanderSpot(state): Vector3
	local half = Plot.size / 2
	local enough = state.radius * 2 + DinoLife.ring.gap * 2
	local best, bestScore = nil, -math.huge
	for _ = 1, DinoLife.steer.spotTries do
		local x = (math.random() * 2 - 1) * (half.X - Plot.placeMargin)
		local z = (math.random() * 2 - 1) * (half.Z - Plot.placeMargin)
		local spot = state.centre + Vector3.new(x, 0, z)
		local score = math.min(room(state, spot), enough) + math.random() * enough * 0.5
		if flat(spot - state.position).Magnitude < state.radius then
			score -= enough -- hardly a walk at all
		end
		if score > bestScore then
			best, bestScore = spot, score
		end
	end
	return Vector3.new(best.X, state.position.Y, best.Z)
end

local function idleTime(): number
	return DinoLife.idleSeconds + (math.random() * 2 - 1) * DinoLife.idleJitter
end

-- Where a plot's owner stands, if they're on their plot (a little past its edge still counts once the circle has formed).
-- Only the local player's own plot: other players' monsters never circle anyone on this screen.
local function ownerOnPlot(plotIndex: number, formed: boolean): Vector3?
	for _, player in { Players.LocalPlayer } do
		if player:GetAttribute("PlotIndex") == plotIndex then
			if player:GetAttribute("IsTraining") == true then
				return nil
			end
			local character = player.Character
			local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
			local humanoid = character and character:FindFirstChildOfClass("Humanoid")
			if not root or not humanoid or humanoid.Health <= 0 then
				return nil
			end
			local margin = if formed then DinoLife.ring.leaveMargin else 0
			local half = Plot.size / 2
			local offset = root.Position - Plot.positions[plotIndex]
			if math.abs(offset.X) <= half.X + margin and math.abs(offset.Z) <= half.Z + margin then
				return root.Position
			end
			return nil
		end
	end
	return nil
end

-- Hands out the places in a circle round the owner. Every monster's nose is the same distance from the owner, so small
-- ones stand close and giants stand further back with their bodies behind them. Each takes a slice of the circle wide
-- enough for its body plus the gap at its own distance, in the order they already stand round the owner (so nobody crosses
-- the circle), and the circle is turned so they walk as little as they can. The noses' circle is as small as lets every
-- slice fit; any slack is shared out evenly.
local function sliceOf(state, front: number): number
	local half = (state.width + DinoLife.ring.gap) / 2
	return 2 * math.asin(math.min(1, half / (front + state.depth / 2)))
end

local function layOut(ring, owner: Vector3)
	local members = ring.members
	for _, state in members do
		local offset = flat(state.position - owner)
		state.ringNow = if offset.Magnitude > 0.01 then math.atan2(offset.Z, offset.X) else math.random() * TAU
	end
	table.sort(members, function(a, b)
		return a.ringNow < b.ringNow
	end)
	local function slices(front: number): number
		local total = 0
		for _, state in members do
			total += sliceOf(state, front)
		end
		return total
	end
	local low, high = DinoLife.ring.ownerGap, DinoLife.ring.ownerGap
	if #members > 1 then
		while slices(high) > TAU and high < 1e5 do
			high *= 2
		end
		for _ = 1, 30 do
			local mid = (low + high) / 2
			if slices(mid) > TAU then
				low = mid
			else
				high = mid
			end
		end
	end
	local front = math.min(high, math.max(DinoLife.ring.maxFront, DinoLife.ring.ownerGap))
	local total = slices(front)
	local stretch = if #members > 1 then TAU / total else 1
	local at = 0
	for _, state in members do
		local share = sliceOf(state, front) * stretch
		state.ringBase = at + share / 2
		state.ringRadius = front + state.depth / 2
		at += share
	end
	-- The turn that moves everyone least: the average of how far each one's place is from where it stands now.
	local sx, sz = 0, 0
	for _, state in members do
		local d = state.ringNow - state.ringBase
		sx += math.cos(d)
		sz += math.sin(d)
	end
	local turn = math.atan2(sz, sx)
	for _, state in members do
		state.ringAngle = state.ringBase + turn
		state.ringDelay = math.random() * DinoLife.ring.reactJitter
		state.ringSlack = 0
	end
	ring.dirty = false
end

-- Each plot's circle, every frame: forms when the owner steps on, follows them, re-forms when monsters come or go, and
-- breaks up when they leave, everyone standing a moment before wandering off again.
local function updateRings()
	for plotIndex, members in plotMembers do
		local ring = rings[plotIndex]
		local owner = if #members > 0 then ownerOnPlot(plotIndex, ring ~= nil) else nil
		if owner and not ring then
			ring = { members = table.clone(members), dirty = true }
			rings[plotIndex] = ring
		elseif ring and not owner then
			rings[plotIndex] = nil
			for _, state in members do
				state.ring = nil
				state.target = nil
				state.idleLeft = DinoLife.ring.scatterIdle[1]
					+ math.random() * (DinoLife.ring.scatterIdle[2] - DinoLife.ring.scatterIdle[1])
			end
			ring = nil
		end
		if ring then
			if ring.dirty then
				ring.members = table.clone(members)
				layOut(ring, owner)
			end
			ring.owner = owner
			for _, state in members do
				state.ring = ring
			end
		end
	end
end

-- Each map's 7th and 8th monsters: bones that move for ever on top of the walk and idle, whatever the monster is doing. Each
-- takes seconds (repeating every 4) and how far it's walking (0 at rest, 1 on the move), and returns pitch, roll, yaw and how
-- far the bone slides ahead, in studs at the first map's size. The same as sway_of in assets/models/rare_kit.py, number for
-- number, whose previews move them alike:
--   Sway<n>a, b, c     slow waves down a chain of up to three bones: feathers, cloth, sails, moss. n moves each chain's wave
--                      along, so a row of them ripples. Wriggle<n>a, b, c is the same, faster and wider: a worm lure
--   PinchL, PinchR     a pincer's moving finger: eases open and snaps shut every 2 seconds, one half a beat after the other
--   Flick              a forked tongue: darts out twice and back every 2 seconds
--   Sting              a scorpion's stinger: draws back, then stabs, every 4 seconds
--   Slither<n>         a snake's body, bone after bone: a wave runs down it, gently at rest and wide on the move
--   Strike             under the Neck: rears back and lunges every 4 seconds; the Jaw of a monster with one bites along with it
--   Spit1 to 6         fire parked in the head, thrown out one after the other as the Strike lunges
--   Step<n>            a centipede's legs, one set after the next: a ripple down its sides, wide on the move
--   Kick1 to 4         snow flung off the hooves as it charges
--   Shard1 to 6        ice flung off the ground as its fists land
--   Stab               a needle that stabs twice every 4 seconds
--   BuzzL, BuzzR       wings that blur
--   Curl1 to 4, Thumb  a hand's fingers: taps them out one after the other, then grabs
--   Shock1 and 2, Bubble1 to 4   rings of cracked water and bubbles off a punch (Punch, Club L and R)
--   Spout1 to 6        a whale's fountain of stars
--   Fall1 to 6         meteors, falling round a monster that sings
--   Crescent1 and 2    blades that fly out spinning and come back (Arm, Scythe L and R)
--   Ring1 to 4         rings of sound from a bat that climbs, screams and drops
--   Maul               maps 10 to 12: nothing but the body, between the Spine and the Neck. Every 2 seconds it throws itself forward,
--                      bites three times, shakes what it caught and drags back, arms raking, trembling all the time
--   Whirl, Gore, Gulp, Bounce, Pummel, Reach1   maps 13 to 15: bare, the most aggressive of all, each with its own attack (see their tables)
-- A monster with a marker bone (MARKED, below) has the rest of its body moved by that bone's table, on top of the walk and idle.
-- They also return how far the bone rises and how far it slides to the monster's right.
local SWAY = {}

local function smooth(u: number): number
	return u * u * (3 - 2 * u)
end

local function keys(u: number, points: { { number } }): number -- a smooth run through { u, value } pairs, u from 0 to 1
	for i = 1, #points - 1 do
		local a, b = points[i], points[i + 1]
		if u <= b[1] then
			return a[2] + (b[2] - a[2]) * smooth((u - a[1]) / (b[1] - a[1]))
		end
	end
	return points[#points][2]
end

local function pinchOpen(u: number): number -- 0 to 1 over a cycle: eases open, holds, snaps shut, rests
	u %= 1
	if u < 0.55 then
		return smooth(u / 0.55)
	elseif u < 0.62 then
		return 1
	elseif u < 0.68 then
		return 1 - smooth((u - 0.62) / 0.06)
	end
	return 0
end

local function bump(u: number, start: number, length: number): number -- a quick rise to 1 and back, 0 elsewhere
	u = (u - start) % 1
	return if u < length then sin(math.pi * u / length) else 0
end

for _, family in { { "Sway", 1, 0.1, 0.05 }, { "Wriggle", 3, 0.16, 0.08 } } do
	local name, speed, firstReach, reachStep = family[1], family[2], family[3], family[4]
	for n = 1, 8 do
		for k, letter in { "a", "b", "c" } do
			local phase = 0.8 * n - 0.9 * (k - 1)
			local reach = firstReach + reachStep * (k - 1)
			SWAY[name .. n .. letter] = function(s: number)
				local v = speed * QUARTER * s
				return reach * (sin(2 * v + phase) + 0.35 * sin(5 * v + 1.3 * phase)),
					0.6 * reach * sin(3 * v + 2 * phase),
					0.7 * reach * sin(2 * v + 0.7 * phase + 1),
					0
			end
		end
	end
end
SWAY.PinchL = function(s: number)
	return 0, 0, 0.5 * pinchOpen(s / 2), 0
end
SWAY.PinchR = function(s: number)
	return 0, 0, -0.5 * pinchOpen(s / 2 + 0.5), 0
end
SWAY.Flick = function(s: number)
	local e = bump((s / 2) % 1, 0, 0.12) + bump((s / 2) % 1, 0.2, 0.12)
	return 0.22 * e * sin(12 * QUARTER * s), 0, 0, 0.55 * e
end
local STING = { { 0, 0 }, { 0.3, 0.4 }, { 0.35, -0.8 }, { 0.44, -0.8 }, { 0.7, 0 }, { 1, 0 } }
SWAY.Sting = function(s: number)
	return keys((s / 4) % 1, STING), 0, 0, 0
end
local STRIKE = { { 0, 0 }, { 0.3, 1 }, { 0.345, -1 }, { 0.42, -1 }, { 0.7, 0 }, { 1, 0 } } -- 1 reared back, -1 lunged
SWAY.Strike = function(s: number)
	local e = keys((s / 4) % 1, STRIKE)
	return 0.2 * e, 0, 0, -1.4 * e
end
for n = 1, 8 do
	SWAY["Slither" .. n] = function(s: number, walking: number)
		return 0, 0, (0.05 + 0.2 * walking) * sin(2 * QUARTER * s - 0.8 * n), 0
	end
end
local STRIKE_JAW = { { 0, 0 }, { 0.3, -0.3 }, { 0.38, -0.3 }, { 0.43, 0.42 }, { 0.6, 0.42 }, { 0.75, 0 }, { 1, 0 } }

-- Bits thrown out for a moment: when (seconds into the 4), how long, from and to (right, ahead, up from where they're parked,
-- studs at the first map's size) and how high the arc (a number) or which way it bows (a Vector3). They jump to `from`, fly to
-- `to`, and snap back out of sight. spin: how far they turn on the way, in radians.
local function fling(start: number, seconds: number, from: Vector3, to: Vector3, arc: any, spin: number?)
	local bow = if typeof(arc) == "number" then Vector3.new(0, 0, arc) else arc
	return function(s: number)
		local t = ((s - start) % 4) / seconds
		if t >= 1 then
			return 0, 0, 0, 0, 0, 0
		end
		local at = from:Lerp(to, t) + bow * (4 * t * (1 - t))
		return 0, 0, (spin or 0) * t, at.Y, at.Z, at.X
	end
end
for n = 1, 6 do
	SWAY["Spit" .. n] = fling(1.38 + 0.07 * (n - 1), 0.62, Vector3.new(0, 2, -1.4), Vector3.new(0, 19, -16), 1)
end
SWAY.Kick1 = fling(1.2, 0.7, Vector3.new(-3.1, -5, -7.6), Vector3.new(-5.5, -13, -9), 3.2)
SWAY.Kick2 = fling(1.2, 0.7, Vector3.new(3.1, -5, -7.6), Vector3.new(5.5, -13, -9), 3.2)
SWAY.Kick3 = fling(1.28, 0.6, Vector3.new(-3, 4.6, -7.6), Vector3.new(-6.5, -3, -9), 2.4)
SWAY.Kick4 = fling(1.28, 0.6, Vector3.new(3, 4.6, -7.6), Vector3.new(6.5, -3, -9), 2.4)
SWAY.Shard1 = fling(1.34, 0.75, Vector3.new(-8.3, 8.4, -9.5), Vector3.new(-13.5, 15, -11.5), 6)
SWAY.Shard2 = fling(1.34, 0.65, Vector3.new(-8.3, 8.4, -9.5), Vector3.new(-16, 7, -11.5), 4.5)
SWAY.Shard3 = fling(1.38, 0.7, Vector3.new(-8.3, 8.4, -9.5), Vector3.new(-5, 17, -11.5), 5)
SWAY.Shard4 = fling(1.34, 0.75, Vector3.new(8.3, 8.4, -9.5), Vector3.new(13.5, 15, -11.5), 6)
SWAY.Shard5 = fling(1.34, 0.65, Vector3.new(8.3, 8.4, -9.5), Vector3.new(16, 7, -11.5), 4.5)
SWAY.Shard6 = fling(1.38, 0.7, Vector3.new(8.3, 8.4, -9.5), Vector3.new(5, 17, -11.5), 5)
SWAY.Shock1 = fling(1.26, 0.5, Vector3.new(-3.2, 14, -3.7), Vector3.new(-3.2, 44, -3.7), 0)
SWAY.Shock2 = fling(2.26, 0.5, Vector3.new(3.2, 14, -3.7), Vector3.new(3.2, 44, -3.7), 0)
SWAY.Bubble1 = fling(1.26, 0.9, Vector3.new(-3.2, 13, -3.7), Vector3.new(-5, 21, 2), 1.5)
SWAY.Bubble2 = fling(1.32, 0.8, Vector3.new(-3.2, 13, -3.7), Vector3.new(-1.5, 19, 4), 1)
SWAY.Bubble3 = fling(2.26, 0.9, Vector3.new(3.2, 13, -3.7), Vector3.new(5, 21, 2), 1.5)
SWAY.Bubble4 = fling(2.32, 0.8, Vector3.new(3.2, 13, -3.7), Vector3.new(1.5, 19, 4), 1)
SWAY.Crescent1 = fling(1.3, 1.3, Vector3.new(-3, 17, 6.2), Vector3.new(-3, 17, 6.2), Vector3.new(-9, 26, -2), 25)
SWAY.Crescent2 = fling(1.4, 1.3, Vector3.new(3, 17, 6.2), Vector3.new(3, 17, 6.2), Vector3.new(9, 26, -2), -25)
for n, spot in { { -7, 3 }, { 6, 8 }, { -3, -6 }, { 9, -2 }, { -10, -3 }, { 3, 5 } } do
	SWAY["Spout" .. n] = fling(0.6 + 0.18 * (n - 1), 1.4, Vector3.new(0, 0.4, 2.6), Vector3.new(spot[1], spot[2], -12), 12, 3)
end
local METEOR = Vector3.new(0.22, 0.5, -1).Unit * 42 -- which way Constellion's meteors fall, and from how far up
for n, spot in { { -12, 16 }, { 10, 20 }, { -4, 26 }, { 14, 8 }, { -16, 6 }, { 3, 14 } } do
	local landing = Vector3.new(spot[1], spot[2], -11)
	SWAY["Fall" .. n] = fling(0.9 + 0.28 * (n - 1), 0.55, landing - METEOR, landing, 0)
end
for n = 1, 4 do
	SWAY["Ring" .. n] = fling(0.72 + 0.08 * (4 - n), 0.46, Vector3.new(0, 5.6, 3.4), Vector3.new(0, 46, -2), 0)
end
for n = 1, 8 do
	SWAY["Step" .. n] = function(s: number, walking: number)
		return (0.06 + 0.42 * walking) * sin(8 * QUARTER * s - 1.2 * n), 0, 0, 0
	end
end
SWAY.BuzzL = function(s: number)
	return 0, 0.1 + 0.26 * sin(32 * QUARTER * s), 0, 0
end
SWAY.BuzzR = function(s: number)
	return 0, -(0.1 + 0.26 * sin(32 * QUARTER * s)), 0, 0
end
local STAB_NEEDLE = { { 0, 0 }, { 0.2, -1 }, { 0.26, 3.4 }, { 0.3, 3.4 }, { 0.38, -0.4 }, { 0.44, 3.4 }, { 0.48, 3.4 }, { 0.7, 0 }, { 1, 0 } }
SWAY.Stab = function(s: number)
	return 0, 0, 0, keys((s / 4) % 1, STAB_NEEDLE)
end

local function track(points: { { number } }, pitch: number?, delay: number?) -- a bone that pitches along points, over the 4 seconds
	local scale, late = pitch or 1, delay or 0
	return function(s: number)
		return scale * keys((s / 4 - late) % 1, points), 0, 0, 0, 0, 0
	end
end
local function rolled(points: { { number } }, sign: number)
	return function(s: number)
		return 0, sign * keys((s / 4) % 1, points), 0, 0, 0, 0
	end
end
local function yawed(points: { { number } }, sign: number)
	return function(s: number)
		return 0, 0, sign * keys((s / 4) % 1, points), 0, 0, 0
	end
end
local function plusPitch(move, points: { { number } }, sign: number?) -- a leg turned against the body's lean, so its foot stays down
	local scale = sign or 1
	return function(s: number)
		local pitch, roll, yaw, ahead, rise, across = move(s)
		return pitch + scale * keys((s / 4) % 1, points), roll, yaw, ahead, rise, across
	end
end

-- The fire: wide jaws, side jaws thrown open then shut, wings up as it rears and beating down on the lunge.
local SPIT_JAW = { { 0, 0 }, { 0.3, -0.3 }, { 0.345, -0.5 }, { 0.55, -0.5 }, { 0.75, 0 }, { 1, 0 } }
local SPIT_MAND = { { 0, 0 }, { 0.3, 0.42 }, { 0.345, 0.42 }, { 0.4, -0.12 }, { 0.55, -0.12 }, { 0.75, 0 }, { 1, 0 } }
local SPIT_WING = { { 0, 0 }, { 0.3, 0.36 }, { 0.345, -0.12 }, { 0.42, -0.12 }, { 0.7, 0 }, { 1, 0 } }
local SPIT_TIP = { { 0, 0 }, { 0.32, 0.26 }, { 0.38, -0.2 }, { 0.46, -0.2 }, { 0.72, 0 }, { 1, 0 } }
local SPITTER = {
	Jaw = track(SPIT_JAW),
	MandL = yawed(SPIT_MAND, 1),
	MandR = yawed(SPIT_MAND, -1),
	WingL = rolled(SPIT_WING, 1),
	WingR = rolled(SPIT_WING, -1),
	WingTipL = rolled(SPIT_TIP, 1),
	WingTipR = rolled(SPIT_TIP, -1),
}

-- The charge: paw twice, sink back, throw the whole body forward head down, toss the head on impact, walk back.
local CHARGE_AHEAD = { { 0, 0 }, { 0.2, 0 }, { 0.29, -1.2 }, { 0.345, 4.2 }, { 0.42, 4.2 }, { 0.78, 0 }, { 1, 0 } }
local CHARGE_LEAN = { { 0, 0 }, { 0.2, 0 }, { 0.29, -0.06 }, { 0.345, -0.13 }, { 0.385, 0.08 }, { 0.46, 0.08 }, { 0.72, 0 }, { 1, 0 } }
local CHARGE_NECK = { { 0, 0 }, { 0.12, -0.12 }, { 0.29, -0.42 }, { 0.345, -0.42 }, { 0.385, 0.2 }, { 0.46, 0.2 }, { 0.72, 0 }, { 1, 0 } }
local CHARGE_HEAD = { { 0, 0 }, { 0.29, -0.2 }, { 0.345, -0.2 }, { 0.385, 0.24 }, { 0.46, 0.24 }, { 0.72, 0 }, { 1, 0 } }
local CHARGE_JAW = { { 0, 0 }, { 0.29, 0.05 }, { 0.345, -0.1 }, { 0.385, -0.5 }, { 0.5, -0.5 }, { 0.72, 0 }, { 1, 0 } }
local CHARGE_FRONT = { { 0, 0 }, { 0.29, -0.2 }, { 0.345, 0.55 }, { 0.42, 0.3 }, { 0.7, 0 }, { 1, 0 } }
local CHARGE_BACK = { { 0, 0 }, { 0.29, 0.25 }, { 0.345, -0.55 }, { 0.42, -0.2 }, { 0.7, 0 }, { 1, 0 } }
local CHARGE_TAIL = { { 0, 0 }, { 0.29, -0.2 }, { 0.345, 0.4 }, { 0.5, 0.2 }, { 0.7, 0 }, { 1, 0 } }
local function paw(s: number)
	local u = (s / 4) % 1
	return 0.55 * (bump(u, 0.02, 0.09) + bump(u, 0.12, 0.09)), 0, 0, 0, 0, 0
end
local CHARGER = {
	Spine = function(s: number)
		local u = (s / 4) % 1
		return keys(u, CHARGE_LEAN), 0, 0, keys(u, CHARGE_AHEAD), 0, 0
	end,
	Neck = track(CHARGE_NECK),
	Head = track(CHARGE_HEAD),
	Jaw = track(CHARGE_JAW),
	Tail1 = track(CHARGE_TAIL),
	FrontL = plusPitch(track(CHARGE_FRONT), CHARGE_LEAN, -1),
	FrontR = plusPitch(plusPitch(paw, CHARGE_FRONT), CHARGE_LEAN, -1),
	BackL = plusPitch(track(CHARGE_BACK), CHARGE_LEAN, -1),
	BackR = plusPitch(track(CHARGE_BACK), CHARGE_LEAN, -1),
}

-- The smash: both arms up over the head, leaning back, then down with everything it has.
local SLAM_ARM = { { 0, 0 }, { 0.19, 2.35 }, { 0.285, 2.55 }, { 0.335, 0.4 }, { 0.44, 0.4 }, { 0.72, 0 }, { 1, 0 } }
local SLAM_LEAN = { { 0, 0 }, { 0.19, 0.2 }, { 0.285, 0.24 }, { 0.335, -0.36 }, { 0.44, -0.36 }, { 0.72, 0 }, { 1, 0 } }
local SLAM_NECK = { { 0, 0 }, { 0.19, 0.18 }, { 0.285, 0.22 }, { 0.335, -0.05 }, { 0.44, -0.05 }, { 0.72, 0 }, { 1, 0 } }
local SLAM_HEAD = { { 0, 0 }, { 0.19, 0.3 }, { 0.285, 0.34 }, { 0.335, 0.24 }, { 0.44, 0.24 }, { 0.72, 0 }, { 1, 0 } }
local SLAM_JAW = { { 0, 0 }, { 0.19, -0.22 }, { 0.285, -0.22 }, { 0.335, 0.3 }, { 0.44, 0.3 }, { 0.72, 0 }, { 1, 0 } }
local SLAMMER = {
	Spine = track(SLAM_LEAN),
	Neck = track(SLAM_NECK),
	Head = track(SLAM_HEAD),
	Jaw = track(SLAM_JAW),
	ArmL = track(SLAM_ARM),
	ArmR = track(SLAM_ARM),
	LegL = track(SLAM_LEAN, -1),
	LegR = track(SLAM_LEAN, -1),
}

-- The needle: rise, stab, draw back, stab again, the front legs reaching in to hold on.
local STAB_HEAD = { { 0, 0 }, { 0.2, 0.12 }, { 0.26, -0.22 }, { 0.3, -0.22 }, { 0.38, 0.06 }, { 0.44, -0.22 }, { 0.48, -0.22 }, { 0.7, 0 }, { 1, 0 } }
local STAB_LEAN = { { 0, 0 }, { 0.2, 0.06 }, { 0.26, -0.12 }, { 0.48, -0.12 }, { 0.7, 0 }, { 1, 0 } }
local STAB_RISE = { { 0, 0 }, { 0.2, 0.6 }, { 0.26, -0.7 }, { 0.48, -0.7 }, { 0.7, 0 }, { 1, 0 } }
local STAB_LEGS = { { 0, 0 }, { 0.2, 0.3 }, { 0.26, -0.25 }, { 0.48, -0.25 }, { 0.7, 0 }, { 1, 0 } }
local STABBER = {
	Spine = function(s: number)
		local u = (s / 4) % 1
		return keys(u, STAB_LEAN), 0, 0, 0, keys(u, STAB_RISE), 0
	end,
	Head = track(STAB_HEAD),
	FrontL = track(STAB_LEGS),
	FrontR = track(STAB_LEGS),
}

-- The hand: taps out its fingers twice, one after the other, rears up, then grabs.
local GRAB_LEAN = { { 0, 0 }, { 0.42, 0 }, { 0.52, 0.42 }, { 0.57, -0.4 }, { 0.64, -0.4 }, { 0.9, 0 }, { 1, 0 } }
local GRAB_AHEAD = { { 0, 0 }, { 0.42, 0 }, { 0.52, -1 }, { 0.57, 3.6 }, { 0.64, 3.6 }, { 0.9, 0 }, { 1, 0 } }
local GRAB_RISE = { { 0, 0 }, { 0.42, 0 }, { 0.52, -1 }, { 0.57, 0.4 }, { 0.64, 0.4 }, { 0.9, 0 }, { 1, 0 } }
local GRAB_JAW = { { 0, 0 }, { 0.42, 0 }, { 0.52, -0.5 }, { 0.565, -0.5 }, { 0.58, 0.14 }, { 0.64, 0.14 }, { 0.9, 0 }, { 1, 0 } }
local GRAB_THUMB = { { 0, 0 }, { 0.42, 0 }, { 0.52, -0.5 }, { 0.57, 0.75 }, { 0.64, 0.75 }, { 0.9, 0 }, { 1, 0 } }
local GRAB_CURL = { { 0, 0 }, { 0.42, 0 }, { 0.52, 0.5 }, { 0.57, -0.75 }, { 0.64, -0.75 }, { 0.9, 0 }, { 1, 0 } }
local function curl(n: number)
	return function(s: number)
		local u = (s / 4) % 1
		local tap = bump(u, 0.02 + 0.045 * n, 0.07) + bump(u, 0.22 + 0.045 * n, 0.07)
		return 0.5 * tap + keys(u, GRAB_CURL), 0, 0, 0, 0, 0
	end
end
local GRABBER = {
	Spine = function(s: number)
		local u = (s / 4) % 1
		return keys(u, GRAB_LEAN), 0, 0, keys(u, GRAB_AHEAD), keys(u, GRAB_RISE), 0
	end,
	Jaw = track(GRAB_JAW),
	Thumb = yawed(GRAB_THUMB, 1),
	Tail1 = track(GRAB_LEAN, -1),
	FrontL = track(GRAB_LEAN, -1),
	FrontR = track(GRAB_LEAN, -1),
	BackL = track(GRAB_LEAN, -1),
	BackR = track(GRAB_LEAN, -1),
	Curl1 = curl(0),
	Curl2 = curl(1),
	Curl3 = curl(2),
	Curl4 = curl(3),
}

-- The punch: cocked, then out in an instant, one fist and a quarter of the way round the clock the other.
local PUNCH_CLUB = { { 0, 0 }, { 0.27, -0.22 }, { 0.3, -0.22 }, { 0.315, 2.9 }, { 0.36, 2.9 }, { 0.5, 0 }, { 1, 0 } }
local PUNCH_ARM = { { 0, 0 }, { 0.27, 0.15 }, { 0.3, 0.15 }, { 0.315, -0.2 }, { 0.36, -0.2 }, { 0.5, 0 }, { 1, 0 } }
local PUNCH_JAW = { { 0, 0 }, { 0.27, -0.2 }, { 0.6, -0.2 }, { 0.75, 0 }, { 1, 0 } }
local PUNCHER = {
	ClubL = track(PUNCH_CLUB),
	PunchL = track(PUNCH_ARM),
	ClubR = track(PUNCH_CLUB, 1, 0.25),
	PunchR = track(PUNCH_ARM, 1, 0.25),
	Jaw = track(PUNCH_JAW),
}

-- The hunting arms: drawn back, unrolled straight in an instant, held, then dragged home, where the jaw snaps. 1 is straight.
local SEIZE_REACH = { { 0, 0 }, { 0.25, -0.12 }, { 0.32, -0.12 }, { 0.365, 1 }, { 0.43, 1 }, { 0.62, 0.55 }, { 0.72, 0 }, { 1, 0 } }
local SEIZE_AHEAD = { { 0, 0 }, { 0.32, 0 }, { 0.365, 6 }, { 0.43, 6 }, { 0.62, 2 }, { 0.72, 0 }, { 1, 0 } }
local SEIZE_TURN = { -1.527, 0.48, 0.611, 0.703, 0.735 } -- how far each joint turns to lay the arm out straight
local SEIZE_JAW = { { 0, 0 }, { 0.36, -0.1 }, { 0.45, -0.35 }, { 0.68, -0.35 }, { 0.72, 0.1 }, { 0.78, 0.1 }, { 0.9, 0 }, { 1, 0 } }
local function seize(k: number, delay: number)
	return function(s: number)
		local u = (s / 4 - delay) % 1
		return SEIZE_TURN[k] * keys(u, SEIZE_REACH), 0, 0, if k == 1 then keys(u, SEIZE_AHEAD) else 0, 0, 0
	end
end
local SEIZER = { Jaw = track(SEIZE_JAW) }
for k = 1, 5 do
	SEIZER["SeizeL" .. k] = seize(k, 0)
	SEIZER["SeizeR" .. k] = seize(k, 0.06)
end

-- The whale breathes out: its head lifts a little and its mouth parts.
local SPOUT_HEAD = { { 0, 0 }, { 0.12, 0.06 }, { 0.5, 0.06 }, { 0.7, 0 }, { 1, 0 } }
local SPOUT_JAW = { { 0, 0 }, { 0.12, -0.06 }, { 0.5, -0.06 }, { 0.7, 0 }, { 1, 0 } }
local SPOUTER = { Head = track(SPOUT_HEAD), Jaw = track(SPOUT_JAW) }

-- The lion lifts its head and sings.
local FALL_NECK = { { 0, 0 }, { 0.16, 0.24 }, { 0.62, 0.24 }, { 0.8, 0 }, { 1, 0 } }
local FALL_HEAD = { { 0, 0 }, { 0.16, 0.14 }, { 0.62, 0.14 }, { 0.8, 0 }, { 1, 0 } }
local FALL_JAW = { { 0, 0 }, { 0.2, -0.2 }, { 0.6, -0.2 }, { 0.75, 0 }, { 1, 0 } }
local CALLER = { Neck = track(FALL_NECK), Head = track(FALL_HEAD), Jaw = track(FALL_JAW) }

-- The mantis: scythes up and open, flung down as the crescents fly, up again to catch them.
local THROW_ARM = { { 0, 0 }, { 0.2, 0.7 }, { 0.3, 0.8 }, { 0.335, -0.1 }, { 0.4, -0.1 }, { 0.66, 0.5 }, { 0.72, 0.3 }, { 0.85, 0 }, { 1, 0 } }
local THROW_SCYTHE = { { 0, 0 }, { 0.2, 1.7 }, { 0.3, 2 }, { 0.335, 0.5 }, { 0.4, 0.4 }, { 0.66, 1.4 }, { 0.72, 1 }, { 0.85, 0 }, { 1, 0 } }
local THROW_NECK = { { 0, 0 }, { 0.2, 0.1 }, { 0.3, 0.12 }, { 0.335, -0.2 }, { 0.4, -0.2 }, { 0.8, 0 }, { 1, 0 } }
local THROW_MAND = { { 0, 0 }, { 0.2, 0.4 }, { 0.3, 0.4 }, { 0.335, -0.1 }, { 0.4, -0.1 }, { 0.8, 0 }, { 1, 0 } }
local THROW_JAW = { { 0, 0 }, { 0.2, -0.35 }, { 0.34, -0.35 }, { 0.42, 0 }, { 1, 0 } }
local THROWER = {
	ArmL = track(THROW_ARM),
	ArmR = track(THROW_ARM),
	ScytheL = track(THROW_SCYTHE),
	ScytheR = track(THROW_SCYTHE),
	Neck = track(THROW_NECK),
	Jaw = track(THROW_JAW),
	MandL = yawed(THROW_MAND, 1),
	MandR = yawed(THROW_MAND, -1),
}

-- The bat: beats its wings, climbs, screams, folds them and drops on you, and climbs back.
local DIVE_UP = { { 0, 0 }, { 0.16, 6 }, { 0.3, 6.4 }, { 0.36, 6.4 }, { 0.44, -2.5 }, { 0.5, -2.5 }, { 0.8, 0 }, { 1, 0 } }
local DIVE_AHEAD = { { 0, 0 }, { 0.3, -2 }, { 0.36, -2 }, { 0.44, 11 }, { 0.5, 11 }, { 0.8, 0 }, { 1, 0 } }
local DIVE_LEAN = { { 0, 0 }, { 0.3, 0.2 }, { 0.36, 0.25 }, { 0.44, -0.5 }, { 0.5, -0.5 }, { 0.72, 0 }, { 1, 0 } }
local DIVE_FOLD = { { 0, 0 }, { 0.36, 0 }, { 0.4, 1 }, { 0.5, 1 }, { 0.6, 0 }, { 1, 0 } }
local DIVE_HEAD = { { 0, 0 }, { 0.2, 0.1 }, { 0.3, 0.15 }, { 0.36, 0.15 }, { 0.44, 0.3 }, { 0.5, 0.3 }, { 0.72, 0 }, { 1, 0 } }
local DIVE_JAW = { { 0, 0 }, { 0.2, -0.35 }, { 0.34, -0.35 }, { 0.44, -0.1 }, { 0.5, -0.2 }, { 0.7, 0 }, { 1, 0 } }
local function diveWing(side: number, beat: number, lag: number, fold: number)
	return function(s: number)
		local f = keys((s / 4) % 1, DIVE_FOLD)
		return 0, side * ((1 - f) * beat * sin(8 * QUARTER * s - lag) - fold * f), 0, 0, 0, 0
	end
end
local DIVER = {
	Swim = function(s: number)
		local u = (s / 4) % 1
		return keys(u, DIVE_LEAN), 0, 0, keys(u, DIVE_AHEAD), keys(u, DIVE_UP), 0
	end,
	Head = track(DIVE_HEAD),
	Jaw = track(DIVE_JAW),
	WingL = diveWing(1, 0.3, 0, 0.9),
	WingR = diveWing(-1, 0.3, 0, 0.9),
	WingTipL = diveWing(1, 0.22, 0.8, 1),
	WingTipR = diveWing(-1, 0.22, 0.8, 1),
}

-- Maps 10 to 12: nothing but the body. Every 2 seconds it sinks back, throws itself forward, bites three times, shakes what it
-- caught and drags itself back to go again, its arms raking one after the other, trembling all the time.
local MAUL_AHEAD = { { 0, 0 }, { 0.26, -1.2 }, { 0.33, 3 }, { 0.5, 3 }, { 0.8, 0 }, { 1, 0 } }
local MAUL_LEAN = { { 0, 0 }, { 0.26, 0.18 }, { 0.33, -0.18 }, { 0.5, -0.18 }, { 0.8, 0 }, { 1, 0 } }
local MAUL_SURGE = { { 0, 0 }, { 0.26, -0.5 }, { 0.33, 1.6 }, { 0.5, 1.6 }, { 0.8, 0 }, { 1, 0 } }
local MAUL_NECK = { { 0, 0 }, { 0.26, 0.2 }, { 0.33, -0.3 }, { 0.5, -0.2 }, { 0.8, 0 }, { 1, 0 } }
local MAUL_HEAD = { { 0, 0 }, { 0.26, 0.1 }, { 0.33, 0.22 }, { 0.5, 0.12 }, { 0.8, 0 }, { 1, 0 } }
local MAUL_JAW = { { 0, 0 }, { 0.26, -0.5 }, { 0.32, -0.5 }, { 0.345, 0.4 }, { 0.39, -0.2 }, { 0.42, 0.4 }, { 0.46, -0.2 }, { 0.49, 0.4 }, { 0.8, 0 }, { 1, 0 } }
local MAUL_ARM = { { 0, 0 }, { 0.22, 1.5 }, { 0.33, -0.3 }, { 0.5, -0.3 }, { 0.8, 0 }, { 1, 0 } }
local MAUL_FRONT = { { 0, 0 }, { 0.26, -0.2 }, { 0.33, 0.45 }, { 0.5, 0.3 }, { 0.8, 0 }, { 1, 0 } }
local MAUL_BACK = { { 0, 0 }, { 0.26, 0.2 }, { 0.33, -0.4 }, { 0.5, -0.2 }, { 0.8, 0 }, { 1, 0 } }
local function fast(points: { { number } }, delay: number?) -- a bone that pitches along points, over 2 seconds
	local late = delay or 0
	return function(s: number)
		return keys((s / 2 - late) % 1, points), 0, 0, 0, 0, 0
	end
end
local function maulShake(points: { { number } }, reach: number, roll: boolean) -- pitches, and shakes from side to side while it has hold
	return function(s: number)
		local u = (s / 2) % 1
		local shake = reach * sin(32 * QUARTER * s) * bump(u, 0.34, 0.2)
		return keys(u, points), if roll then shake else 0, if roll then 0 else shake, 0, 0, 0
	end
end
local MAULER = {
	Spine = function(s: number)
		return 0.012 * sin(20 * QUARTER * s), 0, 0, keys((s / 2) % 1, MAUL_SURGE), 0, 0
	end,
	Maul = function(s: number)
		local u = (s / 2) % 1
		return keys(u, MAUL_LEAN), 0, 0, keys(u, MAUL_AHEAD), 0, 0
	end,
	Neck = maulShake(MAUL_NECK, 0.3, false),
	Head = maulShake(MAUL_HEAD, 0.16, true),
	Jaw = fast(MAUL_JAW),
	ArmL = fast(MAUL_ARM),
	ArmR = fast(MAUL_ARM, 0.5),
	FrontL = fast(MAUL_FRONT),
	FrontR = fast(MAUL_FRONT),
	BackL = fast(MAUL_BACK),
	BackR = fast(MAUL_BACK),
	Tail1 = function(s: number)
		return 0, 0, 0.34 * sin(8 * QUARTER * s), 0, 0, 0
	end,
}
for n = 1, 8 do
	MAULER["Slither" .. n] = function(s: number)
		return 0, 0, 0.16 * sin(8 * QUARTER * s - 0.8 * n), 0, 0, 0
	end
end

-- Maps 13 to 15, the last and worst: each has its own attack, all of them at least twice as often as the Maul. They're written with four small
-- pieces, so the two files stay line for line: beat (a run of keys over some seconds), wave, hop (a bounce) and stacked (moves added up).
local PITCH, ROLL, YAW, AHEAD, RISE, ACROSS = 1, 2, 3, 4, 5, 6
local function slotted(slot: number, v: number)
	if slot == PITCH then
		return v, 0, 0, 0, 0, 0
	elseif slot == ROLL then
		return 0, v, 0, 0, 0, 0
	elseif slot == YAW then
		return 0, 0, v, 0, 0, 0
	elseif slot == AHEAD then
		return 0, 0, 0, v, 0, 0
	elseif slot == RISE then
		return 0, 0, 0, 0, v, 0
	end
	return 0, 0, 0, 0, 0, v
end
local function beat(points: { { number } }, seconds: number?, slot: number?, scale: number?, delay: number?)
	local long, where, size, late = seconds or 2, slot or PITCH, scale or 1, delay or 0
	return function(s: number)
		return slotted(where, size * keys((s / long - late) % 1, points))
	end
end
local function wave(speed: number, reach: number, slot: number?, phase: number?)
	local where, late = slot or PITCH, phase or 0
	return function(s: number)
		return slotted(where, reach * sin(speed * QUARTER * s - late))
	end
end
local function hop(speed: number, reach: number)
	return function(s: number)
		return slotted(RISE, reach * math.abs(sin(speed * QUARTER * s)))
	end
end
local function stacked(...)
	local moves = { ... }
	return function(s: number)
		local a, b, c, d, e, f = 0, 0, 0, 0, 0, 0
		for _, move in moves do
			local p, q, r, t, u, v = move(s)
			a, b, c, d, e, f = a + p, b + q, c + r, d + t, e + u, f + v
		end
		return a, b, c, d, e, f
	end
end
-- Thornado (Whirl, its waist): winds up, spins twice on its own hips with its four arms flung out, then falls forward biting. Every 2 seconds.
local WHIRL_TURN = { { 0, 0 }, { 0.16, -0.8 }, { 0.24, -0.8 }, { 0.6, 4 * math.pi }, { 1, 4 * math.pi } }
local WHIRL_LEAN = { { 0, 0 }, { 0.24, 0.16 }, { 0.62, 0.16 }, { 0.68, -0.34 }, { 0.8, -0.34 }, { 1, 0 } }
local WHIRL_FLING = { { 0, 0 }, { 0.16, -0.3 }, { 0.24, -0.3 }, { 0.34, 1.35 }, { 0.52, 1.35 }, { 0.62, 0 }, { 1, 0 } }
local WHIRL_RAKE = { { 0, 0 }, { 0.6, 0 }, { 0.64, 1.2 }, { 0.7, -0.3 }, { 0.8, -0.3 }, { 1, 0 } }
local WHIRL_NECK = { { 0, 0 }, { 0.24, 0.25 }, { 0.62, 0.25 }, { 0.68, -0.3 }, { 0.8, -0.3 }, { 1, 0 } }
local WHIRL_JAW = { { 0, 0 }, { 0.24, -0.4 }, { 0.66, -0.4 }, { 0.69, 0.45 }, { 0.73, -0.2 }, { 0.76, 0.45 }, { 0.85, 0.1 }, { 1, 0 } }
local WHIRLER = {
	Spine = wave(20, 0.012),
	Whirl = stacked(beat(WHIRL_TURN, 2, YAW), beat(WHIRL_LEAN)),
	Neck = beat(WHIRL_NECK),
	Jaw = beat(WHIRL_JAW),
	ArmL = stacked(beat(WHIRL_FLING, 2, ROLL), beat(WHIRL_RAKE)),
	ArmR = stacked(beat(WHIRL_FLING, 2, ROLL, -1.0), beat(WHIRL_RAKE, 2, PITCH, 1.0, 0.03)),
	WingL = beat(WHIRL_FLING, 2, ROLL, 0.8, 0.02),
	WingR = beat(WHIRL_FLING, 2, ROLL, -0.8, 0.02),
}

-- Thorn to Bits (Gore, its chest): head down, every thorn on its back standing up, it rams and hooks upward three times, left, right and through.
local GORE_SURGE = { { 0, 0 }, { 0.2, -2 }, { 0.3, 6 }, { 0.72, 6 }, { 0.92, 0 }, { 1, 0 } }
local GORE_CHEST = { { 0, 0 }, { 0.2, 0.1 }, { 0.3, -0.16 }, { 0.36, -0.16 }, { 0.42, 0.2 }, { 0.5, -0.16 }, { 0.58, 0.2 }, { 0.66, -0.16 }, { 0.72, 0.26 }, { 0.92, 0 }, { 1, 0 } }
local GORE_NECK = { { 0, 0 }, { 0.2, -0.3 }, { 0.3, -0.55 }, { 0.36, -0.55 }, { 0.42, 0.55 }, { 0.5, -0.55 }, { 0.58, 0.55 }, { 0.66, -0.55 }, { 0.72, 0.65 }, { 0.92, 0 }, { 1, 0 } }
local GORE_HOOK = { { 0, 0 }, { 0.36, 0 }, { 0.42, 0.4 }, { 0.5, 0 }, { 0.58, -0.4 }, { 0.66, 0 }, { 1, 0 } }
local GORE_JAW = { { 0, 0 }, { 0.2, -0.1 }, { 0.3, 0.2 }, { 0.36, -0.3 }, { 0.42, 0.3 }, { 0.5, -0.3 }, { 0.58, 0.3 }, { 0.66, -0.3 }, { 0.72, 0.35 }, { 0.92, 0 }, { 1, 0 } }
local GORE_FRONT = { { 0, 0 }, { 0.2, -0.2 }, { 0.3, 0.6 }, { 0.72, 0.3 }, { 0.92, 0 }, { 1, 0 } }
local GORE_BACK = { { 0, 0 }, { 0.2, 0.25 }, { 0.3, -0.6 }, { 0.72, -0.3 }, { 0.92, 0 }, { 1, 0 } }
local GORE_QUILL = { { 0, 0 }, { 0.18, -0.9 }, { 0.72, -0.9 }, { 0.9, 0 }, { 1, 0 } }
local GORER = {
	Spine = beat(GORE_SURGE, 2, AHEAD),
	Gore = beat(GORE_CHEST),
	Neck = stacked(beat(GORE_NECK), beat(GORE_HOOK, 2, YAW)),
	Jaw = beat(GORE_JAW),
	FrontL = beat(GORE_FRONT),
	FrontR = beat(GORE_FRONT),
	BackL = beat(GORE_BACK),
	BackR = beat(GORE_BACK),
	Tail1 = wave(8, 0.4, YAW),
}
for n = 1, 8 do
	GORER["Quill" .. n] = stacked(beat(GORE_QUILL, 2, PITCH, 1.0, 0.012 * n), wave(20, 0.1, PITCH, 0.7 * n))
end

-- Mouth Breather (Gulp, what little neck it has): all mouth on legs. Every second it leaps with its skull flung right back and comes down jaws first.
local GULP_HEAD = { { 0, 0 }, { 0.32, 0.72 }, { 0.4, 0.72 }, { 0.47, -0.16 }, { 0.6, -0.16 }, { 1, 0 } }
local GULP_JAW = { { 0, 0 }, { 0.32, -0.7 }, { 0.4, -0.7 }, { 0.47, 0.55 }, { 0.6, 0.55 }, { 1, 0 } }
local GULP_THROAT = { { 0, 0 }, { 0.32, 0.2 }, { 0.47, -0.12 }, { 0.6, -0.12 }, { 1, 0 } }
local GULP_RISE = { { 0, 0 }, { 0.3, 4 }, { 0.47, 0 }, { 1, 0 } }
local GULP_AHEAD = { { 0, 0 }, { 0.3, 2 }, { 0.47, 5 }, { 0.6, 5 }, { 1, 0 } }
local GULP_TUCK = { { 0, 0 }, { 0.3, 0.5 }, { 0.47, -0.2 }, { 0.6, 0 }, { 1, 0 } }
local GULPER = {
	Spine = stacked(beat(GULP_RISE, 1, RISE), beat(GULP_AHEAD, 1, AHEAD)),
	Gulp = beat(GULP_THROAT, 1),
	Head = beat(GULP_HEAD, 1),
	Jaw = beat(GULP_JAW, 1),
	FrontL = beat(GULP_TUCK, 1),
	FrontR = beat(GULP_TUCK, 1),
	BackL = beat(GULP_TUCK, 1, PITCH, -1.0),
	BackR = beat(GULP_TUCK, 1, PITCH, -1.0),
	Tail1 = wave(8, 0.3, YAW),
}

-- Spore Loser (Bounce, its chest): never touches the ground for long. Twice a second it springs, left, right, ahead and home, biting as it lands.
local BOUNCE_ACROSS = { { 0, 0 }, { 0.25, -7 }, { 0.5, 7 }, { 0.75, 0 }, { 1, 0 } }
local BOUNCE_AHEAD = { { 0, 0 }, { 0.25, 3 }, { 0.5, 3 }, { 0.75, 9 }, { 1, 0 } }
local BOUNCE_TURN = { { 0, 0 }, { 0.25, 0.5 }, { 0.5, -0.5 }, { 0.75, 0 }, { 1, 0 } }
local BOUNCE_HOCK = { { 0, -0.5 }, { 0.12, 0.8 }, { 0.3, 0.8 }, { 1, -0.5 } }
local BOUNCE_THIGH = { { 0, 0.3 }, { 0.12, -0.7 }, { 0.3, -0.7 }, { 1, 0.3 } }
local BOUNCE_CLAW = { { 0, -0.3 }, { 0.3, 0.9 }, { 0.6, 0.9 }, { 1, -0.3 } }
local BOUNCE_JAW = { { 0, 0.35 }, { 0.2, -0.5 }, { 0.86, -0.5 }, { 1, 0.35 } }
local BOUNCE_NECK = { { 0, -0.2 }, { 0.5, 0.3 }, { 1, -0.2 } }
local BOUNCER = {
	Spine = stacked(beat(BOUNCE_ACROSS, 2, ACROSS), beat(BOUNCE_AHEAD, 2, AHEAD), beat(BOUNCE_TURN, 2, YAW), hop(4, 6)),
	Bounce = wave(8, 0.12, PITCH, 1.0),
	Neck = beat(BOUNCE_NECK, 0.5),
	Jaw = beat(BOUNCE_JAW, 0.5),
	FrontL = beat(BOUNCE_CLAW, 0.5),
	FrontR = beat(BOUNCE_CLAW, 0.5, PITCH, 1.0, 0.1),
	BackL = beat(BOUNCE_THIGH, 0.5),
	BackR = beat(BOUNCE_THIGH, 0.5),
	HockL = beat(BOUNCE_HOCK, 0.5),
	HockR = beat(BOUNCE_HOCK, 0.5),
}

-- Inconsolable (Pummel, its chest): never stops. Both fists hammer the ground in turn, four blows a second, its mouth wide in one long scream.
local PUMMEL_ARM = { { 0, 0 }, { 0.45, 1.8 }, { 0.58, 1.85 }, { 0.72, -0.05 }, { 0.85, -0.05 }, { 1, 0 } }
local PUMMEL_FORE = { { 0, 0 }, { 0.45, 0.7 }, { 0.58, 0.7 }, { 0.72, 0 }, { 1, 0 } }
local PUMMELER = {
	Spine = hop(8, 0.9),
	Pummel = stacked(wave(8, 0.16, ROLL), wave(16, 0.05)),
	Neck = stacked(wave(16, 0.1), wave(8, 0.12, ROLL, 1.0)),
	Head = wave(32, 0.06, YAW),
	Jaw = stacked(wave(24, 0.1), beat({ { 0, -0.3 }, { 1, -0.3 } })),
	ArmL = beat(PUMMEL_ARM, 0.5),
	ArmR = beat(PUMMEL_ARM, 0.5, PITCH, 1.0, 0.5),
	ForeL = beat(PUMMEL_FORE, 0.5),
	ForeR = beat(PUMMEL_FORE, 0.5, PITCH, 1.0, 0.5),
	LegL = wave(8, 0.08),
	LegR = wave(8, -0.08),
}

-- Last Breath (Reach1 to 12, its neck): the end of it all. Every second its neck stretches far past what a neck can, left, ahead, right, ahead, and snaps shut.
local REACH = { { 0, 0 }, { 0.3, -0.12 }, { 0.42, 1 }, { 0.62, 1 }, { 1, 0 } }
local REACH_FAN = { { 0, 0 }, { 0.25, 0.6 }, { 0.5, 0 }, { 0.75, -0.6 }, { 1, 0 } }
local REACH_JAW = { { 0, 0 }, { 0.3, -0.45 }, { 0.42, -0.5 }, { 0.47, 0.4 }, { 0.62, 0.4 }, { 1, 0 } }
local REACH_HEAD = { { 0, 0 }, { 0.3, 0.2 }, { 0.42, -0.1 }, { 0.62, -0.1 }, { 1, 0 } }
local REACH_RAKE = { { 0, 0 }, { 0.3, 0.5 }, { 0.42, -0.3 }, { 0.62, -0.3 }, { 1, 0 } }
local REACHER = {
	Spine = wave(20, 0.012),
	Reach1 = stacked(beat(REACH, 1, AHEAD, 1.7), beat(REACH, 1, RISE, -0.35), beat(REACH_FAN, 4, YAW)),
	Head = beat(REACH_HEAD, 1),
	Jaw = beat(REACH_JAW, 1),
	FrontL = beat(REACH_RAKE, 1),
	FrontR = beat(REACH_RAKE, 1, PITCH, 1.0, 0.5),
}
for n = 2, 12 do
	REACHER["Reach" .. n] = stacked(beat(REACH, 1, AHEAD, 1.7), beat(REACH, 1, RISE, -0.35))
end

-- A monster with one of these bones has the rest of its body moved by that bone's table. Strike is the least of them: the
-- Volcano's pair have it too, and spit instead of biting. The same as MARKED and marked_of in assets/models/rare_kit.py.
local MARKED = {
	Spit1 = SPITTER,
	Kick1 = CHARGER,
	Shard1 = SLAMMER,
	Stab = STABBER,
	Curl1 = GRABBER,
	Shock1 = PUNCHER,
	SeizeL1 = SEIZER,
	Spout1 = SPOUTER,
	Fall1 = CALLER,
	Crescent1 = THROWER,
	Ring1 = DIVER,
	Maul = MAULER,
	Whirl = WHIRLER,
	Gore = GORER,
	Gulp = GULPER,
	Bounce = BOUNCER,
	Pummel = PUMMELER,
	Reach1 = REACHER,
	Strike = { Jaw = track(STRIKE_JAW) }, -- flung wide, then bitten shut
}

-- The shop's four special monsters (Config/Specials) each have an attack nothing else has [Owner, 2026-11-12], 4 seconds long,
-- played once every DinoLife.attackCycle like every other attack. Nothing leaves the body. The same as FRENZY, HOODED, LOOPER and
-- BAITER in assets/models/build_special_monsters.py, number for number, whose preview moves them alike.
-- In a function of its own, added to MARKED: a script can only hold 200 locals at its top level, and this one is nearly there.
;(function()
	local function shaken(points: { { number } }, speed: number, reach: number, slot: number?, phase: number?) -- a wave that only runs while its envelope is up
		local where, late = slot or PITCH, phase or 0
		return function(s: number)
			return slotted(where, reach * keys((s / 4) % 1, points) * sin(speed * QUARTER * s - late))
		end
	end

	-- Gloomfin (Dorsal, its fin): the death roll. It draws back, hits you like a train, and rolls over twice with its jaws going, tail
	-- thrashing; one last bite and a shake, and it drifts home.
	local FRENZY_AHEAD = { { 0, 0 }, { 0.14, -2.2 }, { 0.2, 7 }, { 0.62, 7 }, { 0.68, 8.2 }, { 0.78, 8.2 }, { 1, 0 } }
	local FRENZY_LEAN = { { 0, 0 }, { 0.14, 0.18 }, { 0.2, -0.1 }, { 0.62, -0.1 }, { 0.68, 0.14 }, { 0.8, 0 }, { 1, 0 } }
	local FRENZY_ROLL = { { 0, 0 }, { 0.2, 0 }, { 0.6, 4 * math.pi }, { 1, 4 * math.pi } }
	local FRENZY_ROLLING = { { 0, 0 }, { 0.2, 0 }, { 0.26, 1 }, { 0.56, 1 }, { 0.62, 0 }, { 1, 0 } }
	local FRENZY_SHAKE = { { 0, 0 }, { 0.66, 0 }, { 0.69, 1 }, { 0.78, 1 }, { 0.84, 0 }, { 1, 0 } }
	local FRENZY_JAW = { { 0, 0 }, { 0.14, -0.5 }, { 0.2, -0.5 }, { 0.23, 0.3 }, { 0.26, 0 }, { 0.6, 0 }, { 0.64, -0.55 }, { 0.68, 0.42 }, { 0.8, 0.42 }, { 1, 0 } }
	local FRENZY_FIN = { { 0, 0 }, { 0.14, -0.45 }, { 0.2, 0.5 }, { 0.6, 0.5 }, { 0.8, 0 }, { 1, 0 } }
	local FRENZY = {
		Swim = stacked(beat(FRENZY_AHEAD, 4, AHEAD), beat(FRENZY_LEAN, 4), beat(FRENZY_ROLL, 4, ROLL), shaken(FRENZY_SHAKE, 20, 0.16, YAW)),
		Jaw = stacked(beat(FRENZY_JAW, 4), shaken(FRENZY_ROLLING, 16, 0.26)),
		Dorsal = shaken(FRENZY_ROLLING, 12, 0.14, ROLL),
		FinL = beat(FRENZY_FIN, 4, ROLL, -1.0),
		FinR = beat(FRENZY_FIN, 4, ROLL),
	}
	for i = 1, 4 do
		FRENZY["Tail" .. i] = stacked(shaken(FRENZY_ROLLING, 12, 0.3 + 0.05 * i, YAW, 0.8 * i), shaken(FRENZY_SHAKE, 20, 0.2, YAW, 0.8 * i))
	end

	-- Duskeel (HoodL and R, its frill): the hooded strike. It rears like a cobra and throws its hood wide, sways, strikes down ahead of
	-- it, rears again and strikes to the side.
	local HOOD_REAR = { { 0, 0 }, { 0.22, 1 }, { 0.5, 1 }, { 0.55, 0 }, { 0.62, 0.8 }, { 0.7, 0.8 }, { 0.745, 0 }, { 0.84, 0 }, { 1, 0 } }
	local HOOD_STRIKE = { { 0, 0 }, { 0.5, 0 }, { 0.55, 1 }, { 0.58, 1 }, { 0.62, 0 }, { 0.7, 0 }, { 0.745, 1 }, { 0.82, 1 }, { 0.92, 0 }, { 1, 0 } }
	local HOOD_FLARE = { { 0, 0 }, { 0.18, 1 }, { 0.84, 1 }, { 1, 0 } }
	local HOOD_SWAY = { { 0, 0 }, { 0.2, 0 }, { 0.26, 1 }, { 0.45, 1 }, { 0.5, 0 }, { 1, 0 } }
	local HOOD_SIDE = { { 0, 0 }, { 0.62, 0 }, { 0.7, 0.4 }, { 0.82, 0.4 }, { 1, 0 } }
	local HOOD_JAW = { { 0, 0 }, { 0.22, -0.35 }, { 0.5, -0.45 }, { 0.555, 0.45 }, { 0.6, 0.45 }, { 0.66, -0.4 }, { 0.7, -0.45 }, { 0.75, 0.45 }, { 0.84, 0.45 }, { 1, 0 } }
	local HOODED = {
		Swim = stacked(beat(HOOD_REAR, 4, RISE, 1.6), beat(HOOD_REAR, 4, AHEAD, -1.4), beat(HOOD_STRIKE, 4, AHEAD, 5.5), beat(HOOD_REAR, 4, PITCH, 0.16), beat(HOOD_SIDE, 4, YAW)),
		Neck1 = stacked(beat(HOOD_REAR, 4, PITCH, 0.5), beat(HOOD_STRIKE, 4, PITCH, -0.24), shaken(HOOD_SWAY, 4, 0.3, YAW)),
		Neck2 = stacked(beat(HOOD_REAR, 4, PITCH, 0.22), beat(HOOD_STRIKE, 4, PITCH, -0.12), shaken(HOOD_SWAY, 4, -0.12, YAW)),
		Neck3 = beat(HOOD_REAR, 4, PITCH, -0.45),
		Head = stacked(beat(HOOD_REAR, 4, PITCH, -0.2), beat(HOOD_STRIKE, 4, PITCH, 0.1)),
		Jaw = beat(HOOD_JAW, 4),
		HoodL = stacked(beat(HOOD_FLARE, 4, YAW, -0.95), shaken(HOOD_FLARE, 24, 0.07, YAW)),
		HoodR = stacked(beat(HOOD_FLARE, 4, YAW, 0.95), shaken(HOOD_FLARE, 24, -0.07, YAW)),
	}
	for i = 1, 4 do
		HOODED["Tail" .. i] = shaken(HOOD_FLARE, 6, 0.1 + 0.04 * i, YAW, 0.8 * i)
	end

	-- Umbray (Stinger, the end of its tail): the loop and the sting. It dips, beats its wings once and loops the loop, tail curled under
	-- it; as it levels out the tail whips over its back and the stinger stabs twice.
	local LOOP_R = 4 -- the loop's radius, studs at the first map's size
	local LOOP_TURN = { { 0, 0 }, { 0.14, -0.22 }, { 0.2, -0.22 }, { 0.56, TAU }, { 1, TAU } }
	local LOOP_LIFT = { { 0, 0 }, { 0.14, -0.6 }, { 0.3, 1.5 }, { 0.84, 1.5 }, { 1, 0 } }
	local LOOP_BEATING = { { 0, 0 }, { 0.2, 0 }, { 0.26, 1 }, { 0.54, 1 }, { 0.6, 0 }, { 1, 0 } }
	local LOOP_WING = { { 0, 0 }, { 0.14, -0.5 }, { 0.21, 0.42 }, { 0.3, 0 }, { 0.56, 0 }, { 0.62, -0.3 }, { 0.84, -0.3 }, { 1, 0 } }
	local LOOP_CURL = { { 0, 0 }, { 0.2, 0.3 }, { 0.56, 0.3 }, { 0.63, 0.72 }, { 0.66, 1 }, { 0.7, 1 }, { 0.74, 0.7 }, { 0.77, 1 }, { 0.84, 1 }, { 1, 0 } }
	local LOOP_STAB = { { 0, 0 }, { 0.63, 0 }, { 0.66, 1 }, { 0.7, 1 }, { 0.74, 0 }, { 0.77, 1 }, { 0.84, 1 }, { 0.9, 0 }, { 1, 0 } }
	local LOOP_JAW = { { 0, 0 }, { 0.2, -0.3 }, { 0.56, -0.3 }, { 0.63, -0.45 }, { 0.66, 0.35 }, { 0.72, -0.3 }, { 0.77, 0.35 }, { 0.86, 0.35 }, { 1, 0 } }
	local LOOPER = {
		-- The body goes round a circle as it turns over, so it flies the loop instead of spinning on the spot.
		Swim = function(s: number)
			local u = (s / 4) % 1
			local turn = keys(u, LOOP_TURN)
			return turn, 0, 0, LOOP_R * sin(turn), LOOP_R * (1 - cos(turn)) + keys(u, LOOP_LIFT), 0
		end,
		Jaw = beat(LOOP_JAW, 4),
		FinL = stacked(beat(LOOP_WING, 4, ROLL, -1.0), shaken(LOOP_BEATING, 10, -0.45, ROLL)),
		FinR = stacked(beat(LOOP_WING, 4, ROLL), shaken(LOOP_BEATING, 10, 0.45, ROLL)),
		FlipperFL = shaken(LOOP_BEATING, 10, -0.35, ROLL, 0.9),
		FlipperFR = shaken(LOOP_BEATING, 10, 0.35, ROLL, 0.9),
		Stinger = beat(LOOP_STAB, 4, AHEAD, -1.6),
	}
	for i, curl in { 0.5, 0.7, 0.8, 0.9 } do
		LOOPER["Tail" .. i] = beat(LOOP_CURL, 4, PITCH, -curl)
	end

	-- Dreadlure (Bait, the threads under its lure): the bait. It shuts that mouth for once, sinks, and dangles its lure out in front,
	-- twitching; then the mouth is all there is: it takes everything in front of it, shakes it, and backs away.
	local BAIT_SHUT = { { 0, 0 }, { 0.12, 0.5 }, { 0.5, 0.5 }, { 0.535, -0.5 }, { 0.56, -0.5 }, { 0.6, 0.55 }, { 0.66, 0.2 }, { 0.7, 0.55 }, { 0.8, 0.3 }, { 1, 0 } }
	local BAIT_AHEAD = { { 0, 0 }, { 0.12, -0.5 }, { 0.5, -2 }, { 0.58, 8 }, { 0.78, 8 }, { 1, 0 } }
	local BAIT_RISE = { { 0, 0 }, { 0.12, -0.6 }, { 0.5, -0.8 }, { 0.58, 0.8 }, { 0.78, 0.4 }, { 1, 0 } }
	local BAIT_LEAN = { { 0, 0 }, { 0.5, -0.05 }, { 0.54, 0.14 }, { 0.6, -0.1 }, { 0.78, -0.05 }, { 1, 0 } }
	local BAIT_DANGLE = { { 0, 0 }, { 0.12, -0.42 }, { 0.5, -0.48 }, { 0.56, 0.5 }, { 0.78, 0.3 }, { 1, 0 } }
	local BAIT_TWITCH = { { 0, 0 }, { 0.1, 0 }, { 0.16, 1 }, { 0.46, 1 }, { 0.5, 0 }, { 1, 0 } }
	local BAIT_SHAKE = { { 0, 0 }, { 0.58, 0 }, { 0.61, 1 }, { 0.74, 1 }, { 0.8, 0 }, { 1, 0 } }
	local BAIT_FIN = { { 0, 0 }, { 0.12, 0.2 }, { 0.5, 0.2 }, { 0.56, -0.6 }, { 0.78, -0.3 }, { 1, 0 } }
	local BAITER = {
		Swim = stacked(beat(BAIT_AHEAD, 4, AHEAD), beat(BAIT_RISE, 4, RISE), beat(BAIT_LEAN, 4), shaken(BAIT_SHAKE, 20, 0.15, YAW)),
		Jaw = beat(BAIT_SHUT, 4),
		Lure = stacked(beat(BAIT_DANGLE, 4), shaken(BAIT_TWITCH, 6, 0.14, YAW)),
		LureTip = stacked(beat(BAIT_DANGLE, 4, PITCH, 0.6), shaken(BAIT_TWITCH, 12, 0.22)),
		Bait = stacked(shaken(BAIT_TWITCH, 16, 0.4), shaken(BAIT_TWITCH, 12, 0.3, ROLL, 1.0)),
		FinL = beat(BAIT_FIN, 4, ROLL, -1.0),
		FinR = beat(BAIT_FIN, 4, ROLL),
	}
	for i = 1, 4 do
		BAITER["Tail" .. i] = shaken(BAIT_SHAKE, 12, 0.22 + 0.04 * i, YAW, 0.8 * i)
	end

	MARKED.Dorsal = FRENZY
	MARKED.HoodL = HOODED
	MARKED.Stinger = LOOPER
	MARKED.Bait = BAITER
end)()

-- The 9th to 12th monsters of Spore Hollow and The Weeping Dark [Owner, 2026-11-13]: rarer than the 8 each map has, each with an attack
-- nothing else has, 4 seconds long, played once every DinoLife.attackCycle like every other attack. A marker bone picks the table.
-- Nothing leaves the body. The same as the tables in assets/models/apex_kit.py, number for number, whose Attack action moves them alike.
-- What turns on them all the time (crowns, wheels of eyes, the gyroscope, the saw) is in SPIN, above.
;(function()
	local function shaken(points: { { number } }, speed: number, reach: number, slot: number?, phase: number?) -- a wave that only runs while its envelope is up
		local where, late = slot or PITCH, phase or 0
		return function(s: number)
			return slotted(where, reach * keys((s / 4) % 1, points) * sin(speed * QUARTER * s - late))
		end
	end
	-- A short run of keys, `seconds` long, repeated from `start` on, only while its envelope is up: pecks.
	local function pulsed(points: { { number } }, seconds: number, envelope: { { number } }, slot: number, scale: number, start: number)
		return function(s: number)
			return slotted(slot, scale * keys(((s - start) / seconds) % 1, points) * keys((s / 4) % 1, envelope))
		end
	end

	-- Rot Weiler (Triad, its chest): three heads. It sinks back, the left head strikes, then the right, then the middle; then all three rear
	-- and it throws itself forward on them, shaking what they caught.
	local SNAP = { { 0, 0 }, { 0.06, 0.4 }, { 0.1, -0.55 }, { 0.16, -0.55 }, { 0.26, 0 }, { 1, 0 } }
	local SNAP_JAW = { { 0, 0 }, { 0.06, -0.5 }, { 0.094, -0.5 }, { 0.11, 0.42 }, { 0.17, 0.42 }, { 0.26, 0 }, { 1, 0 } }
	local SNAP_OUT = { { 0, 0 }, { 0.06, 0.3 }, { 0.1, 0.45 }, { 0.16, 0.45 }, { 0.26, 0 }, { 1, 0 } }
	local TRI_ALL = { { 0, 0 }, { 0.64, 0 }, { 0.7, 0.35 }, { 0.735, -0.4 }, { 0.86, -0.4 }, { 0.95, 0 }, { 1, 0 } }
	local TRI_ALL_JAW = { { 0, 0 }, { 0.64, 0 }, { 0.7, -0.6 }, { 0.73, -0.6 }, { 0.745, 0.42 }, { 0.86, 0.42 }, { 0.95, 0 }, { 1, 0 } }
	local TRI_SURGE = { { 0, 0 }, { 0.08, -1.5 }, { 0.64, -1.5 }, { 0.7, -2.6 }, { 0.735, 6 }, { 0.86, 6 }, { 0.96, 0 }, { 1, 0 } }
	local TRI_LEAN = { { 0, 0 }, { 0.08, 0.08 }, { 0.64, 0.08 }, { 0.7, 0.2 }, { 0.735, -0.14 }, { 0.86, -0.14 }, { 0.96, 0 }, { 1, 0 } }
	local TRI_SHAKE = { { 0, 0 }, { 0.735, 0 }, { 0.76, 1 }, { 0.84, 1 }, { 0.88, 0 }, { 1, 0 } }
	local TRI_LEGS = { { 0, 0 }, { 0.08, -0.1 }, { 0.64, -0.1 }, { 0.7, -0.18 }, { 0.735, 0.5 }, { 0.86, 0.3 }, { 0.96, 0 }, { 1, 0 } }
	local TRI_WAG = { { 0, 0 }, { 0.08, 1 }, { 0.9, 1 }, { 1, 0 } }
	local TRIAD = {
		Spine = stacked(beat(TRI_SURGE, 4, AHEAD), shaken(TRI_WAG, 20, 0.01)),
		Triad = beat(TRI_LEAN, 4),
		NeckL = stacked(beat(SNAP, 4, PITCH, 1.0, 0.1), beat(SNAP_OUT, 4, YAW, 1.0, 0.1), beat(TRI_ALL, 4), shaken(TRI_SHAKE, 24, 0.12, YAW)),
		NeckR = stacked(beat(SNAP, 4, PITCH, 1.0, 0.24), beat(SNAP_OUT, 4, YAW, -1.0, 0.24), beat(TRI_ALL, 4), shaken(TRI_SHAKE, 24, -0.12, YAW)),
		Neck = stacked(beat(SNAP, 4, PITCH, 1.0, 0.38), beat(TRI_ALL, 4), shaken(TRI_SHAKE, 24, 0.16, YAW, 1.0)),
		JawL = stacked(beat(SNAP_JAW, 4, PITCH, 1.0, 0.1), beat(TRI_ALL_JAW, 4)),
		JawR = stacked(beat(SNAP_JAW, 4, PITCH, 1.0, 0.24), beat(TRI_ALL_JAW, 4)),
		Jaw = stacked(beat(SNAP_JAW, 4, PITCH, 1.0, 0.38), beat(TRI_ALL_JAW, 4)),
		FrontL = beat(TRI_LEGS, 4), FrontR = beat(TRI_LEGS, 4), BackL = beat(TRI_LEGS, 4, PITCH, -1.0), BackR = beat(TRI_LEGS, 4, PITCH, -1.0),
		Tail1 = shaken(TRI_WAG, 16, 0.3, YAW),
	}

	-- Acid Reign (Crown, the crown over its head): it draws itself up to its full height, hood flung wide, and sways; the crown tips down
	-- over its face like a saw and it throws its whole length at the ground, once ahead and once to the side.
	local REIGN_RISE = { { 0, 0 }, { 0.16, 1 }, { 0.44, 1 }, { 0.5, 0 }, { 0.62, 0.7 }, { 0.68, 0.7 }, { 0.73, 0 }, { 1, 0 } }
	local REIGN_HIT = { { 0, 0 }, { 0.44, 0 }, { 0.5, 1 }, { 0.58, 1 }, { 0.64, 0 }, { 0.68, 0 }, { 0.73, 1 }, { 0.84, 1 }, { 0.94, 0 }, { 1, 0 } }
	local REIGN_SWAY = { { 0, 0 }, { 0.14, 0 }, { 0.2, 1 }, { 0.4, 1 }, { 0.45, 0 }, { 1, 0 } }
	local REIGN_SIDE = { { 0, 0 }, { 0.6, 0 }, { 0.68, 0.5 }, { 0.84, 0.5 }, { 0.96, 0 }, { 1, 0 } }
	local REIGN_FLARE = { { 0, 0 }, { 0.14, 1 }, { 0.86, 1 }, { 1, 0 } }
	local REIGN_JAW = { { 0, 0 }, { 0.16, -0.3 }, { 0.46, -0.4 }, { 0.505, 0.4 }, { 0.58, 0.4 }, { 0.64, -0.35 }, { 0.69, -0.4 }, { 0.735, 0.4 }, { 0.84, 0.4 }, { 1, 0 } }
	local REIGN_VISOR = { { 0, 0 }, { 0.16, 0 }, { 0.44, 0.15 }, { 0.5, 1 }, { 0.58, 1 }, { 0.64, 0.25 }, { 0.68, 0.25 }, { 0.73, 1 }, { 0.84, 1 }, { 0.95, 0 }, { 1, 0 } }
	local REIGN = {
		Rear1 = stacked(beat(REIGN_RISE, 4, PITCH, 0.16), beat(REIGN_HIT, 4, PITCH, -0.5), shaken(REIGN_SWAY, 4, 0.22, YAW), beat(REIGN_SIDE, 4, YAW)),
		Rear2 = stacked(beat(REIGN_RISE, 4, PITCH, 0.1), beat(REIGN_HIT, 4, PITCH, -0.45), shaken(REIGN_SWAY, 4, -0.12, YAW)),
		Rear3 = stacked(beat(REIGN_RISE, 4, PITCH, -0.2), beat(REIGN_HIT, 4, PITCH, -0.3)),
		Neck = beat(REIGN_HIT, 4, PITCH, 0.3),
		Head = beat(REIGN_HIT, 4, PITCH, 0.2),
		Jaw = beat(REIGN_JAW, 4),
		FrillL = stacked(beat(REIGN_FLARE, 4, YAW, -0.85), shaken(REIGN_FLARE, 24, 0.05, YAW)),
		FrillR = stacked(beat(REIGN_FLARE, 4, YAW, 0.85), shaken(REIGN_FLARE, 24, -0.05, YAW)),
		Crown = stacked(beat(REIGN_RISE, 4, RISE, 1.5), beat(REIGN_VISOR, 4, PITCH, -1.45), beat(REIGN_VISOR, 4, AHEAD, 8.5), beat(REIGN_VISOR, 4, RISE, -7.5)),
	}

	-- Cap Punishment (SawArm1, the arm out of its back): the saw is cocked back, brought down on the ground ahead and dragged across, left to
	-- right, the whole beast shaking with it; up again and down again.
	local SAW_ARM = { { 0, 0 }, { 0.16, -0.3 }, { 0.24, -0.34 }, { 0.29, 1 }, { 0.52, 1 }, { 0.6, -0.2 }, { 0.66, -0.24 }, { 0.71, 1 }, { 0.82, 1 }, { 0.94, 0 }, { 1, 0 } } -- 1: down on the ground
	local SAW_DRAG = { { 0, 0 }, { 0.24, 0 }, { 0.29, -1 }, { 0.52, 1 }, { 0.6, 0 }, { 1, 0 } }
	local SAW_ON = { { 0, 0 }, { 0.27, 0 }, { 0.3, 1 }, { 0.52, 1 }, { 0.56, 0 }, { 0.7, 0 }, { 0.72, 1 }, { 0.82, 1 }, { 0.86, 0 }, { 1, 0 } }
	local SAW_LEAN = { { 0, 0 }, { 0.16, 0.14 }, { 0.24, 0.16 }, { 0.29, -0.2 }, { 0.52, -0.2 }, { 0.6, 0.1 }, { 0.66, 0.12 }, { 0.71, -0.24 }, { 0.82, -0.24 }, { 0.94, 0 }, { 1, 0 } }
	local SAW_JAW = { { 0, 0 }, { 0.16, -0.2 }, { 0.29, -0.55 }, { 0.52, -0.55 }, { 0.6, 0 }, { 0.71, -0.55 }, { 0.82, -0.55 }, { 0.94, 0 }, { 1, 0 } }
	local SAW_RAKE = { { 0, 0 }, { 0.24, 0.9 }, { 0.29, -0.2 }, { 0.52, -0.2 }, { 0.66, 0.9 }, { 0.71, -0.2 }, { 0.82, -0.2 }, { 0.94, 0 }, { 1, 0 } }
	local SAW_REACH = { -0.9, 0.05, 0.35 } -- how far each joint of the arm turns to put the saw on the ground
	local SAWYER = {
		Spine = stacked(beat(SAW_LEAN, 4), shaken(SAW_ON, 28, 0.012, ROLL)),
		LegL = beat(SAW_LEAN, 4, PITCH, -1.0), LegR = beat(SAW_LEAN, 4, PITCH, -1.0),
		Neck = beat(SAW_LEAN, 4, PITCH, 0.6),
		Head = shaken(SAW_ON, 28, 0.05, YAW),
		Jaw = beat(SAW_JAW, 4),
		ArmL = beat(SAW_RAKE, 4), ArmR = beat(SAW_RAKE, 4, PITCH, 1.0, 0.02),
		Tail1 = shaken(SAW_ON, 12, 0.2, YAW),
		SawArm1 = stacked(beat(SAW_ARM, 4, PITCH, SAW_REACH[1]), beat(SAW_DRAG, 4, YAW, 0.3)),
		SawArm2 = beat(SAW_ARM, 4, PITCH, SAW_REACH[2]),
		SawArm3 = stacked(beat(SAW_ARM, 4, PITCH, SAW_REACH[3]), shaken(SAW_ON, 32, 0.025)),
	}

	-- Sporeactor (Core, the light over its back): it sinks, the core climbs and whirls three times round, the rods in its back rising one
	-- after the other; it rears, and the core comes down as its front feet do. Everything shakes.
	local MELT_CHARGE = { { 0, 0 }, { 0.14, 0.3 }, { 0.46, 1 }, { 0.5, 1 }, { 0.53, -0.2 }, { 0.6, -0.2 }, { 0.8, 0.1 }, { 1, 0 } }
	local MELT_SPIN = { { 0, 0 }, { 0.1, 0 }, { 0.5, 6 * math.pi }, { 1, 6 * math.pi } }
	local MELT_ROD = { { 0, 0 }, { 0.1, 0 }, { 0.42, 1 }, { 0.48, 1 }, { 0.52, -0.1 }, { 0.62, 0 }, { 1, 0 } }
	local MELT_SINK = { { 0, 0 }, { 0.14, -1 }, { 0.4, -1 }, { 0.5, 0.6 }, { 0.53, -1.2 }, { 0.62, -1.2 }, { 0.8, 0 }, { 1, 0 } }
	local MELT_REAR = { { 0, 0 }, { 0.4, 0 }, { 0.5, 0.3 }, { 0.53, -0.06 }, { 0.62, -0.06 }, { 0.8, 0 }, { 1, 0 } }
	local MELT_PAW = { { 0, 0 }, { 0.4, 0 }, { 0.5, 0.6 }, { 0.53, -0.06 }, { 0.62, -0.06 }, { 0.8, 0 }, { 1, 0 } }
	local MELT_ROAR = { { 0, 0 }, { 0.14, 0.2 }, { 0.46, 0.34 }, { 0.53, -0.3 }, { 0.62, -0.3 }, { 0.8, 0 }, { 1, 0 } }
	local MELT_JAW = { { 0, 0 }, { 0.14, -0.25 }, { 0.46, -0.5 }, { 0.7, -0.5 }, { 0.8, 0 }, { 1, 0 } }
	local MELT_QUAKE = { { 0, 0 }, { 0.52, 0 }, { 0.54, 1 }, { 0.7, 0.4 }, { 0.8, 0 }, { 1, 0 } }
	local MELTER = {
		Spine = stacked(beat(MELT_SINK, 4, RISE), beat(MELT_REAR, 4), shaken(MELT_QUAKE, 28, 0.03, ROLL)),
		Neck = beat(MELT_ROAR, 4),
		Jaw = stacked(beat(MELT_JAW, 4), shaken(MELT_QUAKE, 24, 0.08)),
		FrontL = beat(MELT_PAW, 4), FrontR = beat(MELT_PAW, 4, PITCH, 1.0, 0.01),
		BackL = beat(MELT_REAR, 4, PITCH, -1.0), BackR = beat(MELT_REAR, 4, PITCH, -1.0),
		Tail1 = shaken(MELT_QUAKE, 16, 0.3, YAW),
		Core = stacked(beat(MELT_CHARGE, 4, RISE, 6.0), beat(MELT_SPIN, 4, YAW)),
	}
	for n = 1, 6 do
		MELTER["Rod" .. n] = beat(MELT_ROD, 4, RISE, 4.2, 0.012 * n)
	end

	-- Grim Weeper (Reap, its waist): both blades wound back to the right, one cut right across to the left and one back; then both up over
	-- its head, and down, falling forward on them.
	local REAP_TURN = { { 0, 0 }, { 0.16, -1 }, { 0.2, -1 }, { 0.27, 1 }, { 0.36, 1 }, { 0.43, -1 }, { 0.5, -0.6 }, { 0.58, 0 }, { 1, 0 } }
	local REAP_LIFT = { { 0, 0 }, { 0.5, 0 }, { 0.6, 1 }, { 0.64, 1 }, { 0.68, -0.16 }, { 0.82, -0.16 }, { 0.94, 0 }, { 1, 0 } }
	local REAP_SPREAD = { { 0, 0 }, { 0.16, 1 }, { 0.46, 1 }, { 0.56, 0.2 }, { 0.66, 0.2 }, { 0.7, 0 }, { 1, 0 } }
	local REAP_LEAN = { { 0, 0 }, { 0.16, 0.1 }, { 0.5, 0.1 }, { 0.6, 0.3 }, { 0.64, 0.32 }, { 0.68, -0.45 }, { 0.82, -0.45 }, { 0.94, 0 }, { 1, 0 } }
	local REAP_AHEAD = { { 0, 0 }, { 0.2, 0 }, { 0.27, 2.5 }, { 0.36, 2.5 }, { 0.43, 4 }, { 0.6, 3 }, { 0.64, 3 }, { 0.68, 7 }, { 0.82, 7 }, { 0.95, 0 }, { 1, 0 } }
	local REAP_JAW = { { 0, 0 }, { 0.16, -0.3 }, { 0.2, -0.45 }, { 0.27, 0.3 }, { 0.36, -0.4 }, { 0.43, 0.3 }, { 0.6, -0.5 }, { 0.66, -0.5 }, { 0.69, 0.4 }, { 0.82, 0.4 }, { 1, 0 } }
	local REAP_TRAIL = { { 0, 0 }, { 0.2, 0 }, { 0.27, -1 }, { 0.36, 0 }, { 0.43, 1 }, { 0.52, 0 }, { 0.64, 0 }, { 0.68, 1.2 }, { 0.82, 0.6 }, { 0.94, 0 }, { 1, 0 } }
	local REAPER = {
		Spine = beat(REAP_AHEAD, 4, AHEAD),
		Reap = stacked(beat(REAP_TURN, 4, YAW, 1.0), beat(REAP_LEAN, 4)),
		Neck = beat(REAP_TURN, 4, YAW, -0.7),
		Jaw = beat(REAP_JAW, 4),
		ArmL = stacked(beat(REAP_SPREAD, 4, ROLL, 0.8), beat(REAP_LIFT, 4, PITCH, 2.2)),
		ArmR = stacked(beat(REAP_SPREAD, 4, ROLL, -0.8), beat(REAP_LIFT, 4, PITCH, 2.2)),
		ReapL = beat(REAP_SPREAD, 4, YAW, 0.45), ReapR = beat(REAP_SPREAD, 4, YAW, -0.45),
		Tail1 = stacked(beat(REAP_TRAIL, 4, YAW, 0.5), beat(REAP_TRAIL, 4, PITCH, 0.2)),
		Tail2 = beat(REAP_TRAIL, 4, YAW, 0.4, 0.03),
	}

	-- Cage Rage (RibL1, its ribs): it rears right up and its ribs fling open one pair after the other, like a second mouth; it falls on you,
	-- they clamp shut, and it chews three times.
	local CAGE_REAR = { { 0, 0 }, { 0.14, 0.75 }, { 0.3, 0.8 }, { 0.36, -0.08 }, { 0.8, -0.08 }, { 0.92, 0 }, { 1, 0 } }
	local CAGE_OPEN = { { 0, 0 }, { 0.1, 1 }, { 0.3, 1 }, { 0.36, 0 }, { 0.44, 0.8 }, { 0.5, 0 }, { 0.56, 0.8 }, { 0.62, 0 }, { 0.68, 0.8 }, { 0.74, 0 }, { 1, 0 } }
	local CAGE_AHEAD = { { 0, 0 }, { 0.14, -1 }, { 0.3, -1 }, { 0.36, 7 }, { 0.8, 7 }, { 0.94, 0 }, { 1, 0 } }
	local CAGE_JAW = { { 0, 0 }, { 0.1, -0.5 }, { 0.3, -0.55 }, { 0.36, 0.4 }, { 0.44, -0.3 }, { 0.5, 0.4 }, { 0.56, -0.3 }, { 0.62, 0.4 }, { 0.68, -0.3 }, { 0.74, 0.4 }, { 0.9, 0 }, { 1, 0 } }
	local CAGE_REACH = { { 0, 0 }, { 0.14, 1 }, { 0.3, 1 }, { 0.36, 0 }, { 1, 0 } }
	local CAGER = {
		Spine = stacked(beat(CAGE_REAR, 4), beat(CAGE_AHEAD, 4, AHEAD)),
		BackL = beat(CAGE_REAR, 4, PITCH, -1.0), BackR = beat(CAGE_REAR, 4, PITCH, -1.0),
		FrontL = stacked(beat(CAGE_REACH, 4, PITCH, 0.5), beat(CAGE_REACH, 4, ROLL, 0.5)),
		FrontR = stacked(beat(CAGE_REACH, 4, PITCH, 0.5), beat(CAGE_REACH, 4, ROLL, -0.5)),
		Neck = beat(CAGE_REAR, 4, PITCH, -0.6),
		Jaw = beat(CAGE_JAW, 4),
		Tail1 = beat(CAGE_REAR, 4, PITCH, -0.5),
	}
	for n = 1, 5 do
		CAGER["RibL" .. n] = beat(CAGE_OPEN, 4, ROLL, 1.2, 0.012 * n)
		CAGER["RibR" .. n] = beat(CAGE_OPEN, 4, ROLL, -1.2, 0.012 * n)
	end

	-- Mourning Star (Flail1, the root of its tail): the tail winds back and whirls three times round over it, flung out straight; then the
	-- star comes over its head and down on the ground in front of it, and bounces.
	local MOURN_WHIRL = { { 0, 0 }, { 0.1, -0.5 }, { 0.16, -0.5 }, { 0.6, 6 * math.pi }, { 1, 6 * math.pi } }
	local MOURN_OUT = { { 0, 0 }, { 0.14, 0.3 }, { 0.24, 1 }, { 0.56, 1 }, { 0.62, 0 }, { 1, 0 } }
	local MOURN_SMASH = { { 0, 0 }, { 0.6, 0 }, { 0.66, -0.3 }, { 0.7, 1 }, { 0.76, 1 }, { 0.8, 0.8 }, { 0.83, 1 }, { 0.88, 1 }, { 0.96, 0 }, { 1, 0 } }
	local MOURN_BRACE = { { 0, 0 }, { 0.16, -0.6 }, { 0.6, -0.6 }, { 0.66, 0.4 }, { 0.7, -1.2 }, { 0.88, -1.2 }, { 0.96, 0 }, { 1, 0 } }
	local MOURN_HEAD = { { 0, 0 }, { 0.16, -0.25 }, { 0.6, -0.25 }, { 0.66, 0.3 }, { 0.7, -0.2 }, { 0.88, -0.2 }, { 0.96, 0 }, { 1, 0 } }
	local MOURN_JAW = { { 0, 0 }, { 0.16, -0.3 }, { 0.6, -0.4 }, { 0.7, -0.55 }, { 0.88, -0.55 }, { 0.96, 0 }, { 1, 0 } }
	local MOURN_QUAKE = { { 0, 0 }, { 0.69, 0 }, { 0.71, 1 }, { 0.84, 0.4 }, { 0.9, 0 }, { 1, 0 } }
	local MOURN_UNROLL = { 0.0, -0.7, 0.0, 0.1, 0.4 } -- how far each joint opens to fling the star out level
	local MOURN_REACH = { -1.4, 0.0, 0.0, 0.2, 0.4 } -- and turns to put it on the ground ahead
	local MOURNER = {
		Spine = stacked(beat(MOURN_BRACE, 4, RISE), shaken(MOURN_QUAKE, 28, 0.03, ROLL)),
		Neck = beat(MOURN_HEAD, 4),
		Jaw = beat(MOURN_JAW, 4),
		Flail1 = stacked(beat(MOURN_WHIRL, 4, YAW), beat(MOURN_SMASH, 4, PITCH, MOURN_REACH[1])),
	}
	for n = 2, 5 do
		MOURNER["Flail" .. n] = stacked(beat(MOURN_OUT, 4, PITCH, MOURN_UNROLL[n]), beat(MOURN_SMASH, 4, PITCH, MOURN_REACH[n]))
	end

	-- Nevermore (Plume1, the feathers circling over it): wings up, beaten down, and it hops at you as the feathers burst outward; four pecks,
	-- fast; then wings flung wide, one long caw, and the feathers burst again.
	local PLUMES = 8
	local MURDER_WING = { { 0, 0 }, { 0.12, 1 }, { 0.16, 1 }, { 0.2, -0.35 }, { 0.28, 0.3 }, { 0.7, 0.3 }, { 0.76, 1 }, { 0.8, 1 }, { 0.84, 0.5 }, { 0.94, 0 }, { 1, 0 } }
	local MURDER_HOP = { { 0, 0 }, { 0.16, -0.8 }, { 0.22, 5 }, { 0.3, 0 }, { 1, 0 } }
	local MURDER_AHEAD = { { 0, 0 }, { 0.16, -1 }, { 0.3, 5 }, { 0.72, 5 }, { 0.94, 0 }, { 1, 0 } }
	local MURDER_LEAN = { { 0, 0 }, { 0.16, 0.2 }, { 0.3, -0.25 }, { 0.7, -0.25 }, { 0.78, 0.15 }, { 0.94, 0 }, { 1, 0 } }
	local MURDER_PECKING = { { 0, 0 }, { 0.3, 0 }, { 0.33, 1 }, { 0.68, 1 }, { 0.71, 0 }, { 1, 0 } }
	local MURDER_PECK = { { 0, 0 }, { 0.35, 0.45 }, { 0.55, -1 }, { 0.75, -1 }, { 1, 0 } }
	local MURDER_PECK_JAW = { { 0, 0 }, { 0.35, -0.5 }, { 0.55, -0.5 }, { 0.62, 0.35 }, { 0.8, 0.35 }, { 1, 0 } }
	local MURDER_CAW = { { 0, 0 }, { 0.72, 0 }, { 0.78, -0.7 }, { 0.9, -0.7 }, { 0.96, 0 }, { 1, 0 } }
	local MURDER_BURST = { { 0, 0 }, { 0.16, 0 }, { 0.21, 1 }, { 0.28, 1 }, { 0.4, 0 }, { 0.74, 0 }, { 0.79, 1 }, { 0.86, 1 }, { 0.96, 0 }, { 1, 0 } }
	local MURDER_TREMBLE = { { 0, 0 }, { 0.28, 0 }, { 0.32, 1 }, { 0.9, 1 }, { 0.96, 0 }, { 1, 0 } }
	local MURDERER = {
		Spine = stacked(beat(MURDER_HOP, 4, RISE), beat(MURDER_AHEAD, 4, AHEAD), beat(MURDER_LEAN, 4)),
		LegL = beat(MURDER_LEAN, 4, PITCH, -1.0), LegR = beat(MURDER_LEAN, 4, PITCH, -1.0),
		Neck = stacked(pulsed(MURDER_PECK, 0.38, MURDER_PECKING, PITCH, 0.6, 1.2), beat(MURDER_CAW, 4, PITCH, -0.3)),
		Head = pulsed(MURDER_PECK, 0.38, MURDER_PECKING, PITCH, 0.35, 1.2),
		Jaw = stacked(pulsed(MURDER_PECK_JAW, 0.38, MURDER_PECKING, PITCH, 1.0, 1.2), beat(MURDER_CAW, 4)),
		WingL = stacked(beat(MURDER_WING, 4, ROLL, 0.9), shaken(MURDER_TREMBLE, 24, 0.05, ROLL)),
		WingR = stacked(beat(MURDER_WING, 4, ROLL, -0.9), shaken(MURDER_TREMBLE, 24, -0.05, ROLL)),
		WingTipL = beat(MURDER_WING, 4, ROLL, 0.5, 0.02), WingTipR = beat(MURDER_WING, 4, ROLL, -0.5, 0.02),
		Tail1 = beat(MURDER_WING, 4, PITCH, 0.4),
	}
	for n = 1, PLUMES do
		local angle = (n - 1) * TAU / PLUMES
		MURDERER["Plume" .. n] = stacked(beat(MURDER_BURST, 4, ACROSS, 7 * cos(angle), 0.004 * n), beat(MURDER_BURST, 4, AHEAD, 7 * sin(angle), 0.004 * n))
	end

	MARKED.Triad = TRIAD
	MARKED.Crown = REIGN
	MARKED.SawArm1 = SAWYER
	MARKED.Core = MELTER
	MARKED.Reap = REAPER
	MARKED.RibL1 = CAGER
	MARKED.Flail1 = MOURNER
	MARKED.Plume1 = MURDERER
end)()

-- Shattered Mirror's monsters (map 16) [Owner, 2026-11-13: "aggressive, but at the same time magnificent", each with an animation of
-- its own]: 4-second attacks played once every DinoLife.attackCycle, like the rest. New: a table's "@always" holds moves that run all the
-- time on top of everything, attack or not (the mane's stadium wave, the frill's and the mirror ball's turning, the swan's mirrored
-- necks). The same as the tables in assets/models/build_shattered_mirror_monsters.py, number for number, whose preview moves them alike.
-- Nothing leaves the body: the shards slide out of the skin and back, never out of it. In a function of its own, like the block above.
;(function()
	local ALWAYS = "@always"
	local function shaken(points: { { number } }, speed: number, reach: number, slot: number?, phase: number?) -- a wave while its envelope is up
		local where, late = slot or PITCH, phase or 0
		return function(s: number)
			return slotted(where, reach * keys((s / 4) % 1, points) * sin(speed * QUARTER * s - late))
		end
	end
	local function along(way: Vector3, amount: (number) -> number) -- slides along a way in the model's own axes: X across, Y ahead, Z up
		return function(s: number)
			local v = amount(s)
			return 0, 0, 0, way.Y * v, way.Z * v, way.X * v
		end
	end
	local function stepped(move, fps: number?) -- the move in jerks, like a broken doll
		local rate = fps or 8
		return function(s: number)
			return move(math.floor(s * rate) / rate)
		end
	end
	local function spun(turns: number, slot: number?) -- turns for ever (round the forward axis unless told), whole turns every 4 seconds
		local where = slot or ROLL
		return function(s: number)
			return slotted(where, turns * QUARTER * s)
		end
	end
	local function mirrored(move) -- the same move seen in a mirror across the middle
		return function(s: number)
			local p, r, y, a, u, x = move(s)
			return p, -r, -y, a, u, -x
		end
	end
	local function rightOf(name: string): string
		return (string.gsub(name, "L(%d*)$", "R%1"))
	end

	-- Paw de Deux (Prowl, its chest): it sidesteps a whole circle round a spot in front of it, always facing it, crouches, wriggles,
	-- springs and rakes with one paw and then the other.
	local PROWL_R = 6.0 -- the circle's radius, studs at the first map's size
	local PROWL_TURN = { { 0, 0 }, { 0.12, 0 }, { 0.62, 2 * math.pi }, { 1, 2 * math.pi } }
	local PROWL_LOW = { { 0, 0 }, { 0.1, -0.7 }, { 0.62, -0.7 }, { 0.68, -1.1 }, { 0.72, -1.1 }, { 0.76, 0.3 }, { 0.84, 0 }, { 1, 0 } }
	local PROWL_LUNGE = { { 0, 0 }, { 0.7, 0 }, { 0.75, 4.5 }, { 0.86, 4.5 }, { 1, 0 } }
	local PROWL_LEAN = { { 0, 0 }, { 0.1, -0.06 }, { 0.62, -0.06 }, { 0.7, 0.12 }, { 0.75, -0.1 }, { 0.86, -0.1 }, { 1, 0 } }
	local PROWL_PACING = { { 0, 0 }, { 0.12, 0 }, { 0.16, 1 }, { 0.58, 1 }, { 0.62, 0 }, { 1, 0 } }
	local PROWL_WIGGLE = { { 0, 0 }, { 0.63, 0 }, { 0.65, 1 }, { 0.71, 1 }, { 0.73, 0 }, { 1, 0 } }
	local PROWL_SWIPE = { { 0, 0 }, { 0.7, 0 }, { 0.74, 1.3 }, { 0.77, -0.35 }, { 0.84, -0.35 }, { 0.94, 0 }, { 1, 0 } }
	local PROWL_NECK = { { 0, 0 }, { 0.1, -0.18 }, { 0.62, -0.18 }, { 0.7, -0.3 }, { 0.75, 0.08 }, { 0.86, 0.08 }, { 1, 0 } }
	local PROWL_HEAD = { { 0, 0 }, { 0.1, 0.1 }, { 0.62, 0.1 }, { 0.75, 0.22 }, { 0.86, 0.22 }, { 1, 0 } }
	local PROWL_JAW = { { 0, 0 }, { 0.1, -0.15 }, { 0.62, -0.15 }, { 0.7, -0.55 }, { 0.76, -0.55 }, { 0.78, 0.1 }, { 0.8, -0.5 }, { 0.86, -0.5 }, { 1, 0 } }
	local PROWL_LASH = { { 0, 0 }, { 0.08, 1 }, { 0.9, 1 }, { 1, 0 } }
	local function prowlCircle(s: number) -- round a circle PROWL_R in front of it, turning as it goes, so it faces the middle all the way round
		local a = keys((s / 4) % 1, PROWL_TURN)
		return 0, 0, a, PROWL_R * (1 - cos(a)), 0, PROWL_R * sin(a)
	end
	local PROWLER = {
		Spine = stacked(prowlCircle, beat(PROWL_LOW, 4, RISE), beat(PROWL_LUNGE, 4, AHEAD), beat(PROWL_LEAN, 4), shaken(PROWL_WIGGLE, 12, 0.1, YAW)),
		Prowl = shaken(PROWL_PACING, 8, 0.05, ROLL),
		Neck = beat(PROWL_NECK, 4),
		Head = beat(PROWL_HEAD, 4),
		Jaw = beat(PROWL_JAW, 4),
		FrontL = stacked(shaken(PROWL_PACING, 8, 0.38), beat(PROWL_SWIPE, 4)),
		FrontR = stacked(shaken(PROWL_PACING, 8, 0.38, PITCH, math.pi), beat(PROWL_SWIPE, 4, PITCH, 1.0, 0.08)),
		BackL = shaken(PROWL_PACING, 8, 0.3, PITCH, math.pi),
		BackR = shaken(PROWL_PACING, 8, 0.3),
	}
	for i = 1, 3 do
		PROWLER["Tail" .. i] = shaken(PROWL_LASH, 6, 0.18 + 0.06 * i, YAW, 0.7 * i)
	end

	-- Frill Seeker (Frill, its frill's hub): it rears onto its hind legs, its kaleidoscope whirls a whole turn on top of its own turning,
	-- and it runs at you on two legs, hissing, then backs off and drops. Rosette, the petals, turns for ever.
	local FRILL_REAR = { { 0, 0 }, { 0.12, 1 }, { 0.84, 1 }, { 0.95, 0 }, { 1, 0 } }
	local FRILL_DASH = { { 0, 0 }, { 0.24, 0 }, { 0.48, 1 }, { 0.6, 1 }, { 0.84, 0 }, { 1, 0 } }
	local FRILL_RUN = { { 0, 0 }, { 0.18, 0 }, { 0.24, 1 }, { 0.82, 1 }, { 0.88, 0 }, { 1, 0 } }
	local FRILL_SPIN = { { 0, 0 }, { 0.1, 0 }, { 0.6, 2 * math.pi }, { 1, 2 * math.pi } }
	local FRILL_HISS = { { 0, 0 }, { 0.1, -0.62 }, { 0.84, -0.62 }, { 0.95, 0 }, { 1, 0 } }
	local FRILL_SHIVER = { { 0, 0 }, { 0.08, 0 }, { 0.12, 1 }, { 0.84, 1 }, { 0.9, 0 }, { 1, 0 } }
	local DASHER = {
		Spine = stacked(beat(FRILL_REAR, 4, PITCH, 0.62), beat(FRILL_REAR, 4, RISE, 1.0), beat(FRILL_DASH, 4, AHEAD, 7.0), shaken(FRILL_RUN, 12, 0.05, ROLL)),
		BackL = stacked(beat(FRILL_REAR, 4, PITCH, -0.62), shaken(FRILL_RUN, 12, 0.7)),
		BackR = stacked(beat(FRILL_REAR, 4, PITCH, -0.62), shaken(FRILL_RUN, 12, 0.7, PITCH, math.pi)),
		FrontL = stacked(beat(FRILL_REAR, 4, PITCH, 0.5), shaken(FRILL_RUN, 12, 0.3, PITCH, math.pi)),
		FrontR = stacked(beat(FRILL_REAR, 4, PITCH, 0.5), shaken(FRILL_RUN, 12, 0.3)),
		Neck = beat(FRILL_REAR, 4, PITCH, -0.45),
		Head = beat(FRILL_REAR, 4, PITCH, -0.1),
		Jaw = stacked(beat(FRILL_HISS, 4), shaken(FRILL_SHIVER, 20, 0.05)),
		Frill = stacked(beat(FRILL_SPIN, 4, ROLL), shaken(FRILL_SHIVER, 24, 0.035)),
		Tail1 = beat(FRILL_REAR, 4, PITCH, -0.5),
		Tail2 = beat(FRILL_REAR, 4, PITCH, 0.2),
		Tail3 = shaken(FRILL_RUN, 6, 0.25, YAW),
		[ALWAYS] = { Rosette = spun(1) },
	}

	-- Dressed to Kill (Twist, its chest): its head turns slowly right round to look behind it, tilts, then snaps the rest of the way
	-- round, and it lunges: arms thrown out, its mirror of a face split open. The lunge comes in jerks, eight poses a second.
	local TWIST_TURN = { { 0, 0 }, { 0.08, 0 }, { 0.4, math.pi }, { 0.55, math.pi }, { 0.585, 2 * math.pi }, { 1, 2 * math.pi } }
	local TWIST_TILT = { { 0, 0 }, { 0.32, 0 }, { 0.42, 0.42 }, { 0.54, 0.42 }, { 0.58, 0 }, { 1, 0 } }
	local TWIST_LUNGE = { { 0, 0 }, { 0.58, 0 }, { 0.64, 1 }, { 0.76, 1 }, { 0.9, 0 }, { 1, 0 } }
	local TWIST_REACH = { { 0, 0 }, { 0.56, 0 }, { 0.6, -0.25 }, { 0.64, 1 }, { 0.76, 1 }, { 0.9, 0 }, { 1, 0 } }
	local TWIST_JAW = { { 0, 0 }, { 0.08, 0 }, { 0.4, -0.12 }, { 0.55, -0.12 }, { 0.6, -0.75 }, { 0.76, -0.75 }, { 0.9, 0 }, { 1, 0 } }
	local TWIST_JITTER = { { 0, 0 }, { 0.58, 0 }, { 0.6, 1 }, { 0.76, 1 }, { 0.8, 0 }, { 1, 0 } }
	local TWISTER = {
		Spine = stepped(stacked(beat(TWIST_LUNGE, 4, AHEAD, 3.6), beat(TWIST_LUNGE, 4, RISE, -0.5))),
		Twist = stepped(stacked(beat(TWIST_LUNGE, 4, PITCH, -0.38), shaken(TWIST_JITTER, 14, 0.05, ROLL))),
		Neck = stepped(beat(TWIST_LUNGE, 4, PITCH, -0.12)),
		Head = stacked(beat(TWIST_TURN, 4, YAW), beat(TWIST_TILT, 4, ROLL), stepped(beat(TWIST_LUNGE, 4, PITCH, 0.3))),
		Jaw = stepped(stacked(beat(TWIST_JAW, 4), shaken(TWIST_JITTER, 20, 0.08))),
		ArmL = stepped(beat(TWIST_REACH, 4, PITCH, 1.45)),
		ArmR = stepped(beat(TWIST_REACH, 4, PITCH, 1.45, 0.02)),
		ForeL = stepped(beat(TWIST_REACH, 4, PITCH, 0.5)),
		ForeR = stepped(beat(TWIST_REACH, 4, PITCH, 0.5, 0.02)),
		LegL = stepped(beat(TWIST_LUNGE, 4, PITCH, 0.45)),
		ShinL = stepped(beat(TWIST_LUNGE, 4, PITCH, -0.5)),
		LegR = stepped(beat(TWIST_LUNGE, 4, PITCH, -0.3)),
	}

	-- Wrecking Ballroom (Swing, its chest): the tail swings like a pendulum, higher each time, the body leaning against it; then it heaves
	-- the mirror ball up over its back and slams it down, hopping on its front feet, roaring. Club, the ball, turns for ever and faster in it.
	local PEND = { { 0, 0 }, { 0.06, 0.25 }, { 0.56, 1 }, { 0.6, 0 }, { 1, 0 } }
	local PEND_LIFT = { { 0, 0 }, { 0.56, 0 }, { 0.66, 1 }, { 0.71, 1 }, { 0.75, -0.12 }, { 0.84, -0.12 }, { 1, 0 } }
	local PEND_HOP = { { 0, 0 }, { 0.72, 0 }, { 0.755, 1 }, { 0.8, 0 }, { 1, 0 } }
	local PEND_DIP = { { 0, 0 }, { 0.56, 0 }, { 0.66, -1 }, { 0.71, -1 }, { 0.75, 1 }, { 0.84, 0.6 }, { 1, 0 } }
	local PEND_JAW = { { 0, 0 }, { 0.6, 0 }, { 0.7, -0.55 }, { 0.88, -0.55 }, { 1, 0 } }
	local PEND_SPIN = { { 0, 0 }, { 0.06, 0 }, { 0.75, 4 * math.pi }, { 1, 4 * math.pi } }
	local SWINGER = {
		Spine = stacked(shaken(PEND, 4, -0.08, YAW), beat(PEND_DIP, 4, PITCH, 0.1), beat(PEND_HOP, 4, RISE, 0.9)),
		Swing = shaken(PEND, 4, -0.06, YAW, 0.4),
		Neck = stacked(beat(PEND_DIP, 4, PITCH, 0.12), shaken(PEND, 4, -0.1, YAW, 0.6)),
		Head = beat(PEND_DIP, 4, PITCH, 0.1),
		Jaw = beat(PEND_JAW, 4),
		FrontL = beat(PEND_HOP, 4, PITCH, 0.35),
		FrontR = beat(PEND_HOP, 4, PITCH, 0.35),
		Tail1 = stacked(shaken(PEND, 4, 0.5, YAW), beat(PEND_LIFT, 4, PITCH, -0.8)),
		Tail2 = stacked(shaken(PEND, 4, 0.32, YAW, 0.6), beat(PEND_LIFT, 4, PITCH, -0.5)),
		Tail3 = stacked(shaken(PEND, 4, 0.26, YAW, 1.2), beat(PEND_LIFT, 4, PITCH, -0.35)),
		Club = beat(PEND_SPIN, 4, ROLL),
		[ALWAYS] = { Club = spun(1) },
	}

	-- Swanquish (Reflect, its breast): the wings flare up and out, both necks coil back hissing and weave, mirror images of each other,
	-- then strike together, closing like shears, twice. The right neck always does what the left does, seen in a mirror.
	local SWAN_FLARE = { { 0, 0 }, { 0.12, 1 }, { 0.84, 1 }, { 1, 0 } }
	local SWAN_COIL = { { 0, 0 }, { 0.12, 0 }, { 0.3, 1 }, { 0.44, 1 }, { 0.48, -0.7 }, { 0.56, -0.7 }, { 0.6, 0.5 }, { 0.64, -0.7 }, { 0.72, -0.7 }, { 0.86, 0 }, { 1, 0 } }
	local SWAN_PINCH = { { 0, 0 }, { 0.44, 0 }, { 0.48, 1 }, { 0.56, 1 }, { 0.6, 0.2 }, { 0.64, 1 }, { 0.72, 1 }, { 0.86, 0 }, { 1, 0 } }
	local SWAN_BILL = { { 0, 0 }, { 0.14, -0.45 }, { 0.44, -0.45 }, { 0.47, 0.05 }, { 0.52, -0.4 }, { 0.6, -0.4 }, { 0.63, 0.05 }, { 0.68, -0.4 }, { 0.86, 0 }, { 1, 0 } }
	local SWAN_BEATS = { { 0, 0 }, { 0.42, 0 }, { 0.46, 1 }, { 0.74, 1 }, { 0.8, 0 }, { 1, 0 } }
	local SWAN_WEAVE = { { 0, 0 }, { 0.14, 0 }, { 0.2, 1 }, { 0.42, 1 }, { 0.46, 0 }, { 1, 0 } }
	local SWAN_LUNGE = { { 0, 0 }, { 0.44, 0 }, { 0.48, 1 }, { 0.72, 1 }, { 0.86, 0 }, { 1, 0 } }
	local SWAN_LEFT = {
		NeckL1 = stacked(beat(SWAN_COIL, 4, PITCH, 0.45), beat(SWAN_PINCH, 4, YAW, -0.16), shaken(SWAN_WEAVE, 6, 0.22, YAW)),
		NeckL2 = stacked(beat(SWAN_COIL, 4, PITCH, -0.55), shaken(SWAN_WEAVE, 6, -0.18, YAW, 0.8)),
		NeckL3 = stacked(beat(SWAN_COIL, 4, PITCH, 0.5), shaken(SWAN_WEAVE, 6, 0.15, YAW, 1.6)),
		HeadL = beat(SWAN_COIL, 4, PITCH, -0.35),
		BillL = beat(SWAN_BILL, 4),
		WingL = stacked(beat(SWAN_FLARE, 4, ROLL, -0.35), beat(SWAN_FLARE, 4, YAW, -0.3), shaken(SWAN_BEATS, 8, 0.2, ROLL)),
		WingTipL = stacked(beat(SWAN_FLARE, 4, ROLL, -0.25), shaken(SWAN_BEATS, 8, 0.22, ROLL, 0.8)),
	}
	local SWAN_IDLE = { -- always: the necks sway, the right the mirror of the left
		NeckL1 = wave(1, 0.1, YAW),
		NeckL2 = wave(2, 0.06, PITCH, 0.6),
		NeckL3 = wave(1, -0.09, YAW, 1.2),
		HeadL = stacked(wave(1, 0.08, ROLL, 0.4), wave(2, 0.05, PITCH, 1.4)),
	}
	local MIRRORER = {
		Spine = stacked(beat(SWAN_LUNGE, 4, AHEAD, 1.6), beat(SWAN_LUNGE, 4, PITCH, -0.06)),
		Reflect = beat(SWAN_COIL, 4, PITCH, 0.08),
		Tail1 = beat(SWAN_FLARE, 4, PITCH, -0.3),
		[ALWAYS] = {},
	}
	for name, move in SWAN_LEFT do
		MIRRORER[name], MIRRORER[rightOf(name)] = move, mirrored(move)
	end
	for name, move in SWAN_IDLE do
		MIRRORER[ALWAYS][name], MIRRORER[ALWAYS][rightOf(name)] = move, mirrored(move)
	end

	-- Mane Event (Rampant, its chest): it rears up rampant, pawing the air, and every shard bursts out at once and rattles; it roars, slams
	-- down onto its front paws and the shards ripple back in, mane first. Always: a wave runs round the mane and down its back, each shard
	-- sliding out of the skin and back in (Sliver1 to 20), the owner's stadium wave. MANE_SUNK of each shard is in the skin at rest, and
	-- MANE_WAVE + MANE_BURST stay under it, so a shard never comes right out.
	local MANE_AXIS = Vector3.new(0, 0.72, 0.69).Unit -- the neck's line, which the mane rings (Blender's axes: X across, Y ahead, Z up)
	local MANE_UP = Vector3.xAxis:Cross(MANE_AXIS).Unit
	local MANE_BACK = Vector3.new(0, -0.4, 1).Unit
	local MANE_WAVE, MANE_BURST = 0.25, 0.22
	local RAMP_UP = { { 0, 0 }, { 0.15, 1 }, { 0.48, 1 }, { 0.58, -0.25 }, { 0.7, -0.25 }, { 0.86, 0 }, { 1, 0 } }
	local RAMP_SLAM = { { 0, 0 }, { 0.48, 0 }, { 0.58, 2.6 }, { 0.72, 2.6 }, { 0.9, 0 }, { 1, 0 } }
	local RAMP_PAW = { { 0, 0 }, { 0.1, 0 }, { 0.16, 1 }, { 0.46, 1 }, { 0.5, 0 }, { 1, 0 } }
	local RAMP_JAW = { { 0, 0 }, { 0.12, -0.2 }, { 0.2, -0.78 }, { 0.5, -0.78 }, { 0.58, 0.05 }, { 0.66, -0.35 }, { 0.82, 0 }, { 1, 0 } }
	local RAMP_ROAR = { { 0, 0 }, { 0.18, 0 }, { 0.22, 1 }, { 0.48, 1 }, { 0.52, 0 }, { 1, 0 } }
	local RAMP_RATTLE = { { 0, 0 }, { 0.17, 0 }, { 0.2, 1 }, { 0.56, 1 }, { 0.6, 0 }, { 1, 0 } }
	local RAMPANT = {
		Spine = stacked(beat(RAMP_UP, 4, PITCH, 0.62), beat(RAMP_UP, 4, RISE, 1.6), beat(RAMP_SLAM, 4, AHEAD)),
		Rampant = stacked(beat(RAMP_UP, 4, PITCH, 0.12), shaken(RAMP_ROAR, 20, 0.03, ROLL)),
		BackL = beat(RAMP_UP, 4, PITCH, -0.62),
		BackR = beat(RAMP_UP, 4, PITCH, -0.62),
		FrontL = stacked(beat(RAMP_UP, 4, PITCH, 0.55), shaken(RAMP_PAW, 6, 0.55)),
		FrontR = stacked(beat(RAMP_UP, 4, PITCH, 0.55), shaken(RAMP_PAW, 6, 0.55, PITCH, math.pi)),
		Neck = beat(RAMP_UP, 4, PITCH, -0.15),
		Head = stacked(beat(RAMP_ROAR, 4, PITCH, 0.3), shaken(RAMP_ROAR, 20, 0.04, YAW)),
		Jaw = stacked(beat(RAMP_JAW, 4), shaken(RAMP_ROAR, 24, 0.05)),
		Tail1 = beat(RAMP_UP, 4, PITCH, -0.45),
		Tail2 = shaken(RAMP_PAW, 4, 0.3, YAW),
		Tail3 = shaken(RAMP_PAW, 4, 0.4, YAW, 1.0),
		[ALWAYS] = {},
	}
	-- Every moving shard, in the order the burst lets them go: the mane from its right over the top to its left, the back, the tail's tip.
	local slivers = {}
	for k = 0, 11 do
		local a = -0.8 + k * (math.pi + 1.6) / 11
		local way = (Vector3.xAxis * cos(a) + MANE_UP * sin(a) - MANE_AXIS * 0.42).Unit
		table.insert(slivers, { way = way, length = 5.0 + 1.0 * sin(a), phase = a })
	end
	for k = 0, 5 do
		table.insert(slivers, { way = MANE_BACK, length = 3.6 - 0.25 * k, phase = 4.4 + 0.5 * k })
	end
	for _, s in { -1, 1 } do
		table.insert(slivers, { way = Vector3.new(s * 0.4, -0.8, 0.45).Unit, length = 2.4, phase = 7.8 + (if s > 0 then 0.4 else 0) })
	end
	for n, sliver in slivers do
		local length, phase, late = sliver.length, sliver.phase, 0.012 * (n - 1)
		local points = { { 0, 0 }, { 0.12, 0 }, { 0.19, 1 }, { 0.6 + late, 1 }, { 0.7 + late, 0 }, { 1, 0 } } -- all out together, back in one by one
		RAMPANT[ALWAYS]["Sliver" .. n] = along(sliver.way, function(s: number)
			return MANE_WAVE * length * ((1 + cos(2 * QUARTER * s - phase)) / 2) ^ 4
		end)
		RAMPANT["Sliver" .. n] = along(sliver.way, function(s: number)
			local u = (s / 4) % 1
			return MANE_BURST * length * keys(u, points) + 0.05 * length * keys(u, RAMP_RATTLE) * sin(24 * QUARTER * s)
		end)
	end

	-- The six rarest (assets/models/build_shattered_mirror_rare.py) [Owner, 2026-11-14: unique bodies, no shared mouth, "I want them
	-- shards to be floating and waving and doing stuff"]. Every one carries shards that float free of its body and never stop moving
	-- ("@always"), and has its own 4-second attack. The same as the tables at the bottom of that file, number for number.
	local function bob(way: Vector3, reach: number, speed: number, phase: number?) -- floats back and forth along a way, for ever
		local late = phase or 0
		return along(way, function(s: number)
			return reach * sin(speed * QUARTER * s - late)
		end)
	end
	local function thrust(way: Vector3, reach: number, points: { { number } }) -- slides out along a way and back, by keys over the 4 seconds
		return along(way, function(s: number)
			return reach * keys((s / 4) % 1, points)
		end)
	end
	local function volley(order: number, start: number, step: number, rise: number, holdTo: number, fall: number) -- one of a row, each later than the last
		local late = step * order
		return { { 0, 0 }, { start + late, 0 }, { start + late + rise, 1 }, { holdTo + late, 1 }, { holdTo + late + fall, 0 }, { 1, 0 } }
	end
	local function bothSides(tbl, left) -- a left-hand table, with its mirror for the right
		for name, move in left do
			tbl[name], tbl[rightOf(name)] = move, mirrored(move)
		end
	end
	local UPWARD = Vector3.new(0, 0, 1) -- Blender's axes, as `along` takes them: X across, Y ahead, Z up

	-- Stilt Life (Stilt, its chest): the neck coils back, the bill opens, and it stabs three times, driving forward each time, its blades
	-- flung wide and shaking. Always: the blades hang beside it and a wave runs up each fan.
	local STAB_COIL = { { 0, 0 }, { 0.14, 1 }, { 0.3, 1 }, { 0.335, -1 }, { 0.4, 0.5 }, { 0.435, -1 }, { 0.5, 0.5 }, { 0.535, -1 }, { 0.66, -1 }, { 0.86, 0 }, { 1, 0 } }
	local STAB_LUNGE = { { 0, 0 }, { 0.3, -0.3 }, { 0.335, 1 }, { 0.4, 0.3 }, { 0.435, 1 }, { 0.5, 0.3 }, { 0.535, 1 }, { 0.66, 1 }, { 0.86, 0 }, { 1, 0 } }
	local STAB_BILL = { { 0, 0 }, { 0.14, -0.35 }, { 0.3, -0.35 }, { 0.34, 0.05 }, { 0.4, -0.3 }, { 0.44, 0.05 }, { 0.5, -0.3 }, { 0.54, 0.05 }, { 0.66, 0.05 }, { 0.75, -0.4 }, { 0.86, 0 }, { 1, 0 } }
	local STAB_FLARE = { { 0, 0 }, { 0.14, 1 }, { 0.7, 1 }, { 0.9, 0 }, { 1, 0 } }
	local STABBER = {
		Spine = stacked(beat(STAB_LUNGE, 4, AHEAD, 2.4), beat(STAB_LUNGE, 4, PITCH, -0.08)),
		Neck = beat(STAB_COIL, 4, PITCH, 0.3),
		NeckB = beat(STAB_COIL, 4, PITCH, 0.35),
		NeckC = beat(STAB_COIL, 4, PITCH, -0.45),
		Head = beat(STAB_COIL, 4, PITCH, -0.2),
		Jaw = beat(STAB_BILL, 4),
		LegL = beat(STAB_LUNGE, 4, PITCH, 0.2),
		LegR = beat(STAB_LUNGE, 4, PITCH, -0.2),
		[ALWAYS] = {},
	}
	for k = 1, 5 do
		bothSides(STABBER, { ["VaneL" .. k] = stacked(beat(STAB_FLARE, 4, YAW, -0.6), beat(STAB_FLARE, 4, PITCH, -0.25), shaken(STAB_FLARE, 16, 0.05, ROLL, 0.5 * k)) })
		bothSides(STABBER[ALWAYS], { ["VaneL" .. k] = stacked(bob(UPWARD, 0.45, 2, 0.7 * k), wave(2, 0.1, PITCH, 0.7 * k)) })
	end

	-- Prism Break (Prism, its chest): it drops its head and its whole sail tips forward over it; blade after blade fires ahead and comes
	-- back, front one first; then it charges, jaw wide. Always: the sail floats in a wave, the tail's shards drift.
	local RAY_LOW = { { 0, 0 }, { 0.15, 1 }, { 0.72, 1 }, { 0.9, 0 }, { 1, 0 } }
	local RAY_CHARGE = { { 0, 0 }, { 0.5, 0 }, { 0.6, 1 }, { 0.72, 1 }, { 0.92, 0 }, { 1, 0 } }
	local RAY_RUN = { { 0, 0 }, { 0.48, 0 }, { 0.52, 1 }, { 0.72, 1 }, { 0.78, 0 }, { 1, 0 } }
	local RAY_JAW = { { 0, 0 }, { 0.15, -0.2 }, { 0.5, -0.2 }, { 0.58, -0.7 }, { 0.72, -0.7 }, { 0.78, 0.1 }, { 0.9, 0 }, { 1, 0 } }
	local RAY_WAY = Vector3.new(0, 1, 0.15)
	local RAYER = {
		Spine = stacked(beat(RAY_LOW, 4, PITCH, -0.2), beat(RAY_LOW, 4, RISE, -0.6), beat(RAY_CHARGE, 4, AHEAD, 5.5)),
		Neck = beat(RAY_LOW, 4, PITCH, -0.35),
		Head = beat(RAY_LOW, 4, PITCH, 0.25),
		Jaw = beat(RAY_JAW, 4),
		LegL = stacked(beat(RAY_LOW, 4, PITCH, 0.2), shaken(RAY_RUN, 12, 0.6)),
		LegR = stacked(beat(RAY_LOW, 4, PITCH, 0.2), shaken(RAY_RUN, 12, 0.6, PITCH, math.pi)),
		ArmL = beat(RAY_CHARGE, 4, PITCH, 0.8),
		ArmR = beat(RAY_CHARGE, 4, PITCH, 0.8),
		[ALWAYS] = {},
	}
	for i = 1, 3 do
		RAYER["Tail" .. i] = shaken(RAY_LOW, 6, 0.12 + 0.05 * i, YAW, 0.8 * i)
		RAYER[ALWAYS]["Drift" .. i] = stacked(bob(UPWARD, 0.5, 2, 0.9 * i), wave(2, 0.25, ROLL, 0.9 * i))
	end
	for k = 1, 7 do
		RAYER["Sail" .. k] = stacked(beat(RAY_LOW, 4, PITCH, -1.0), thrust(RAY_WAY, 4.0, volley(k - 1, 0.2, 0.04, 0.05, 0.3, 0.1)))
		RAYER[ALWAYS]["Sail" .. k] = stacked(bob(UPWARD, 0.7, 2, 0.8 * k), wave(2, 0.12, ROLL, 0.8 * k))
	end

	-- Moth-er of Pearl (Flutter, its thorax): it climbs, draws its wings back, claps them shut in front of it twice, and dives through
	-- you; its rings spin up. Always: all four wings beat, its tail curls, the two rings turn opposite ways.
	local MOTH_RISE = { { 0, 0 }, { 0.2, 1 }, { 0.4, 1 }, { 0.5, -0.3 }, { 0.62, -0.3 }, { 0.85, 0 }, { 1, 0 } }
	local MOTH_DIVE = { { 0, 0 }, { 0.4, -0.15 }, { 0.5, 1 }, { 0.62, 1 }, { 0.86, 0 }, { 1, 0 } }
	local MOTH_CLAP = { { 0, 0 }, { 0.2, 0.35 }, { 0.4, 0.35 }, { 0.47, -1 }, { 0.52, -1 }, { 0.57, 0.3 }, { 0.62, -1 }, { 0.68, -1 }, { 0.86, 0 }, { 1, 0 } }
	local MOTH_SPIN = { { 0, 0 }, { 0.2, 0 }, { 0.8, 4 * math.pi }, { 1, 4 * math.pi } }
	local MOTH_BUSY = { { 0, 0 }, { 0.18, 0 }, { 0.24, 1 }, { 0.8, 1 }, { 0.86, 0 }, { 1, 0 } }
	local FLUTTERER = {
		Swim = stacked(beat(MOTH_RISE, 4, RISE, 2.6), beat(MOTH_DIVE, 4, AHEAD, 6.5), beat(MOTH_RISE, 4, PITCH, 0.25)),
		Flutter = shaken(MOTH_BUSY, 16, 0.04, ROLL),
		Head = beat(MOTH_RISE, 4, PITCH, -0.2),
		LoopA = beat(MOTH_SPIN, 4, YAW),
		LoopB = stacked(beat(MOTH_SPIN, 4, YAW, -1.0), shaken(MOTH_BUSY, 4, 0.12)),
		[ALWAYS] = { LoopA = spun(1, YAW), LoopB = spun(-1, YAW), AbdA = wave(2, 0.1), AbdB = wave(2, 0.14, PITCH, 0.8) },
	}
	bothSides(FLUTTERER, { WingL = beat(MOTH_CLAP, 4, YAW, 1.1), HindL = beat(MOTH_CLAP, 4, YAW, 0.7, 0.02) })
	bothSides(FLUTTERER[ALWAYS], { WingL = wave(8, 0.28, ROLL), HindL = wave(8, 0.24, ROLL, 0.9) })

	-- Vainglory (Train, the root of its train): the fan goes up and shivers, it struts at you with its neck pumping, screams, and the
	-- eyes stab outward, the middle one first, and come back. Always: a wave runs across the train, the crest bobs.
	local VAIN_UP = { { 0, 0 }, { 0.16, 1 }, { 0.8, 1 }, { 0.94, 0 }, { 1, 0 } }
	local VAIN_SHIVER = { { 0, 0 }, { 0.18, 0 }, { 0.22, 1 }, { 0.5, 1 }, { 0.56, 0 }, { 1, 0 } }
	local VAIN_STRUT = { { 0, 0 }, { 0.22, 0 }, { 0.5, 1 }, { 0.74, 1 }, { 0.94, 0 }, { 1, 0 } }
	local VAIN_STEPS = { { 0, 0 }, { 0.2, 0 }, { 0.24, 1 }, { 0.5, 1 }, { 0.54, 0 }, { 1, 0 } }
	local VAIN_SCREAM = { { 0, 0 }, { 0.5, 0 }, { 0.54, -0.6 }, { 0.72, -0.6 }, { 0.78, 0 }, { 1, 0 } }
	local VAIN_HEAD = { { 0, 0 }, { 0.5, 0 }, { 0.54, 0.3 }, { 0.72, 0.3 }, { 0.8, 0 }, { 1, 0 } }
	local TRAIN_UP = Vector3.new(0, -0.57, 0.82).Unit
	local function trainWay(k: number): Vector3 -- the way feather k of 13 points: 0.2 radians a feather either side of the middle one
		local a = (k - 7) * 0.2
		return (Vector3.xAxis * sin(a) + TRAIN_UP * cos(a)).Unit
	end
	local VAUNTER = {
		Spine = stacked(beat(VAIN_STRUT, 4, AHEAD, 3.2), shaken(VAIN_STEPS, 8, 0.2, RISE)),
		Train = stacked(beat(VAIN_UP, 4, PITCH, -0.5), shaken(VAIN_SHIVER, 24, 0.04, ROLL)),
		Neck = stacked(beat(VAIN_UP, 4, PITCH, 0.15), shaken(VAIN_STEPS, 8, 0.12)),
		NeckB = shaken(VAIN_STEPS, 8, -0.1),
		Head = beat(VAIN_HEAD, 4),
		Jaw = beat(VAIN_SCREAM, 4),
		LegL = shaken(VAIN_STEPS, 8, 0.5),
		LegR = shaken(VAIN_STEPS, 8, 0.5, PITCH, math.pi),
		Crest = shaken(VAIN_SHIVER, 24, 0.08, ROLL),
		[ALWAYS] = { Crest = bob(UPWARD, 0.25, 2), Train = wave(1, 0.04, ROLL) },
	}
	for k = 1, 13 do
		VAUNTER["Eye" .. k] = thrust(trainWay(k), 2.6, volley(math.abs(k - 7), 0.5, 0.02, 0.04, 0.62, 0.12))
		VAUNTER[ALWAYS]["Eye" .. k] = bob(trainWay(k), 0.5, 2, 0.5 * k)
	end

	-- Mirror Mirror (Glass1, the first piece of its glass): the glass bursts out of the frame, each piece spinning in its own plane; what
	-- lives inside leans out through the hole and looks left and right for you; then it draws back and the glass closes over it. Always:
	-- the two rings wheel opposite ways, and the glass breathes.
	local GLASS_TUMBLE = { { 0, 0 }, { 0.14, 0 }, { 0.3, 2 * math.pi }, { 0.66, 2 * math.pi }, { 0.8, 4 * math.pi }, { 1, 4 * math.pi } }
	local GLASS_EMERGE = { { 0, 0 }, { 0.24, 0 }, { 0.36, 1 }, { 0.62, 1 }, { 0.72, 0 }, { 1, 0 } }
	local GLASS_LOOK = { { 0, 0 }, { 0.36, 0 }, { 0.4, 1 }, { 0.6, 1 }, { 0.64, 0 }, { 1, 0 } }
	local GLASS_SPIN = { { 0, 0 }, { 0.14, 0 }, { 0.8, 2 * math.pi }, { 1, 2 * math.pi } }
	local SHATTERER = {
		Spine = stacked(beat(GLASS_EMERGE, 4, PITCH, -0.1), shaken(GLASS_LOOK, 8, 0.25, RISE)),
		Head = stacked(beat(GLASS_EMERGE, 4, AHEAD, 2.6), shaken(GLASS_LOOK, 4, 0.4, YAW)),
		LegL = shaken(GLASS_LOOK, 8, 0.3),
		LegR = shaken(GLASS_LOOK, 8, 0.3, PITCH, math.pi),
		LoopA = beat(GLASS_SPIN, 4, ROLL),
		LoopB = beat(GLASS_SPIN, 4, ROLL, -1.0),
		[ALWAYS] = { LoopA = spun(1), LoopB = spun(-1) },
	}
	for k = 1, 8 do
		local b = (k - 0.5) * TAU / 8
		local way = Vector3.new(cos(b), 0.9, sin(b)).Unit -- out from the middle of the glass and at you
		SHATTERER["Glass" .. k] = stacked(thrust(way, 3.6, volley(k - 1, 0.14, 0.012, 0.06, 0.66, 0.1)), beat(GLASS_TUMBLE, 4, ROLL, if k % 2 == 1 then 1.0 else -1.0))
		SHATTERER[ALWAYS]["Glass" .. k] = bob(Vector3.new(0, 1, 0), 0.12, 2, 0.8 * k)
	end

	-- Royal Pane (Royal, its chest): it rears, spreads its wings high, coils its neck, then beats the wings forward: the panes fly out of
	-- them at you, one after another, and back, as it strikes down roaring. Always: the panes ripple in their frames, the ring over its
	-- head turns, the neck sways.
	local ROYAL_REAR = { { 0, 0 }, { 0.18, 1 }, { 0.6, 1 }, { 0.72, -0.2 }, { 0.82, -0.2 }, { 1, 0 } }
	local ROYAL_SPREAD = { { 0, 0 }, { 0.18, 1 }, { 0.46, 1 }, { 0.54, -0.3 }, { 0.7, -0.3 }, { 0.9, 0 }, { 1, 0 } }
	local ROYAL_GUST = { { 0, 0 }, { 0.46, 0 }, { 0.54, 1 }, { 0.7, 1 }, { 0.9, 0 }, { 1, 0 } }
	local ROYAL_COIL = { { 0, 0 }, { 0.18, 1 }, { 0.46, 1 }, { 0.54, -1 }, { 0.72, -1 }, { 0.9, 0 }, { 1, 0 } }
	local ROYAL_JAW = { { 0, 0 }, { 0.18, -0.2 }, { 0.46, -0.25 }, { 0.54, -0.75 }, { 0.74, -0.75 }, { 0.86, 0 }, { 1, 0 } }
	local ROYAL_ROAR = { { 0, 0 }, { 0.52, 0 }, { 0.56, 1 }, { 0.74, 1 }, { 0.8, 0 }, { 1, 0 } }
	local PANE_WAY = Vector3.new(-0.5, 0.8, 0.3) -- the left wing's panes in the gust: ahead, out and up
	local REGENT = {
		Spine = stacked(beat(ROYAL_REAR, 4, PITCH, 0.4), beat(ROYAL_REAR, 4, RISE, 1.4)),
		LegL = beat(ROYAL_REAR, 4, PITCH, -0.4),
		LegR = beat(ROYAL_REAR, 4, PITCH, -0.4),
		Neck = beat(ROYAL_COIL, 4, PITCH, 0.25),
		NeckB = beat(ROYAL_COIL, 4, PITCH, 0.2),
		NeckC = beat(ROYAL_COIL, 4, PITCH, -0.3),
		Head = stacked(beat(ROYAL_COIL, 4, PITCH, -0.15), shaken(ROYAL_ROAR, 20, 0.04, YAW)),
		Jaw = stacked(beat(ROYAL_JAW, 4), shaken(ROYAL_ROAR, 24, 0.05)),
		Tail1 = beat(ROYAL_REAR, 4, PITCH, -0.35),
		Tail2 = shaken(ROYAL_SPREAD, 4, 0.25, YAW),
		Tail3 = shaken(ROYAL_SPREAD, 4, 0.35, YAW, 1.0),
		[ALWAYS] = { Tiara = spun(1, YAW), NeckB = wave(1, 0.05, YAW) },
	}
	bothSides(REGENT, {
		WingL = stacked(beat(ROYAL_SPREAD, 4, ROLL, 0.45), beat(ROYAL_GUST, 4, YAW, -0.4)),
		WingTipL = stacked(beat(ROYAL_SPREAD, 4, ROLL, 0.3), beat(ROYAL_GUST, 4, YAW, -0.25)),
	})
	for k = 1, 5 do
		bothSides(REGENT, { ["PaneL" .. k] = thrust(PANE_WAY, 4.2, volley(k - 1, 0.5, 0.025, 0.05, 0.64, 0.12)) })
		bothSides(REGENT[ALWAYS], { ["PaneL" .. k] = stacked(bob(UPWARD, 0.3, 2, 0.9 * k), wave(2, 0.06, ROLL, 0.9 * k)) })
	end

	MARKED.Stilt = STABBER
	MARKED.Prism = RAYER
	MARKED.Flutter = FLUTTERER
	MARKED.Train = VAUNTER
	MARKED.Glass1 = SHATTERER
	MARKED.Royal = REGENT

	MARKED.Prowl = PROWLER
	MARKED.Frill = DASHER
	MARKED.Twist = TWISTER
	MARKED.Swing = SWINGER
	MARKED.Reflect = MIRRORER
	MARKED.Rampant = RAMPANT
end)()

local function add(model: Model)
	-- A monster with Stay set (the server's best catch on its pedestal) idles where it is and never walks. One with
	-- Carried set rides on a player's head (PlotService): it walks while they move and idles while they stand.
	local carried = model:GetAttribute("Carried") == true
	local stays = model:GetAttribute("Stay") == true or carried
	local plotIndex = model:GetAttribute("PlotIndex")
	local position = if stays then model:GetPivot().Position else plotIndex and Plot.positions[plotIndex]
	if not position then
		return
	end
	local key = not stays and placeKey(model)
	local last = key and lastPlaces[key]
	if last and os.clock() - last.at < 5 then
		-- Rebuilt by the server a moment ago: carry on from where it stood, not its saved spot.
		local here = Vector3.new(last.position.X, model:GetPivot().Y, last.position.Z)
		local look = if DinoModel.facesBack(model) then -last.facing else last.facing
		model:PivotTo(CFrame.lookAt(here, here + look))
	end
	local pivot = model:GetPivot()
	local scale = model:GetScale()
	local _, extents = model:GetBoundingBox()
	local bones = {}
	local legHeight = nil
	local roars = false
	local swims = false
	local thrashes = false
	local rages = false
	local vents = false
	local marked = nil
	for _, bone in model:GetDescendants() do
		if bone:IsA("Bone") then
			roars = roars or bone.Name == "Jaw"
			if MARKED[bone.Name] and (not marked or bone.Name ~= "Strike") then
				marked = MARKED[bone.Name]
			end
			swims = swims or bone.Name == "Swim"
			thrashes = thrashes or string.sub(bone.Name, 1, 4) == "Lash"
			rages = rages or DRIP[bone.Name] ~= nil
			vents = vents or string.sub(bone.Name, 1, 4) == "Vent"
		end
	end
	-- Which way the model faces from its pivot. Most imported models face the pivot's +Z (the importer turns them
	-- round) and a few its -Z, so the poses take the model's own right and forward, and it moves head first whichever
	-- it is.
	-- Every monster with an attack plays it only once a cycle (DinoLife.attackCycle): its attack moves (below, `gated`) wait for
	-- it. What isn't an attack goes on all the time: feathers, feelers and lures swaying, a snake's slither, a centipede's legs,
	-- wings blurring, a tongue flicking, pincers clicking, and the Prism Egg swimmers' whiskers.
	local cycle = DinoLife.attackCycle
	local function gated(name: string, move): boolean
		if move == nil then
			return false
		end
		for _, family in cycle.ambient do
			if string.match(name, "^" .. family) then
				return false
			end
		end
		return true
	end
	local turned = DinoModel.facesBack(model)
	local right = if turned then -Vector3.xAxis else Vector3.xAxis
	local ahead = if turned then Vector3.zAxis else -Vector3.zAxis
	for _, bone in model:GetDescendants() do
		if bone:IsA("Bone") then
			-- The pose axes, in the bone's own space, measured while the dino stands at rest.
			local function axis(direction: Vector3): Vector3
				return bone.WorldCFrame:VectorToObjectSpace(pivot:VectorToWorldSpace(direction))
			end
			local walk = (if swims then SWIM else WALK)[bone.Name] or zero
			local idle = (if swims then HOVER else IDLE)[bone.Name] or zero
			if roars and not swims and ROAR[bone.Name] then
				idle = plus(idle, ROAR[bone.Name])
			end
			local whiskered = swims and thrashes
			local damping = whiskered and WHISKERED_DAMPING[bone.Name]
			if damping then
				walk, idle = damped(walk, damping), damped(idle, damping)
			end
			table.insert(bones, {
				bone = bone,
				walk = walk,
				idle = idle,
				pitch = axis(right),
				roll = axis(ahead),
				yaw = axis(Vector3.yAxis),
				spin = SPIN[bone.Name],
				angle = math.random() * TAU, -- so a plot's keys don't all turn in step
				thrash = if whiskered then WHISKER[bone.Name] elseif thrashes then THRASH[bone.Name] else nil,
				rage = if rages then RAGE[bone.Name] else nil,
				drip = DRIP[bone.Name],
				pounce = if vents then POUNCE[bone.Name] else nil,
				vent = string.sub(bone.Name, 1, 4) == "Vent",
				sway = marked and marked[bone.Name] or SWAY[bone.Name],
				gated = gated(bone.Name, marked and marked[bone.Name] or SWAY[bone.Name]),
				always = marked and marked["@always"] and marked["@always"][bone.Name], -- runs all the time, attack or not (map 16)
				steady = whiskered, -- whiskers, not an attack: they never wait
			})
			if bone.Name == "LegL" or bone.Name == "FrontL" then
				legHeight = bone.WorldPosition.Y - pivot.Y
			end
		end
	end
	local every = nil
	for _, entry in bones do
		if entry.gated or (entry.thrash and not entry.steady) or entry.rage or entry.pounce then
			every = cycle
			break
		end
	end
	-- Fast enough that the feet don't look like they slide: a stride covers about this much ground.
	local isBiped = model:FindFirstChild("LegL", true) ~= nil
	local strideLength = (legHeight or 1.5 * scale) * (if isBiped then 1.74 else 1.26)
	local strideSeconds = if rages and not every then DinoLife.rageStrideSeconds else DinoLife.strideSeconds
	dinos[model] = {
		model = model,
		bones = bones,
		scale = scale,
		reach = extents.Magnitude, -- generous: the whole box's diagonal around its feet, so it never vanishes from view early
		centre =Vector3.new(position.X, pivot.Y, position.Z),
		position = pivot.Position,
		facing = pivot:VectorToWorldSpace(ahead), -- where its head points
		turned = turned,
		speed = if swims then DinoLife.swim.speed * scale else strideLength / strideSeconds,
		strideSeconds = if swims then DinoLife.swim.strideSeconds else strideSeconds,
		target = nil,
		idleLeft = if stays then math.huge else math.random() * DinoLife.idleSeconds, -- so a plot's dinos don't all set off together
		blend = 0,
		stride = math.random() * TAU,
		idleClock = math.random() * TAU,
		thrashClock = math.random() * 4, -- seconds; the pattern is 4 long, so a plot's monsters don't thrash in step
		attackCycle = every,
		attackClock = if every then math.random() * every.every else 0, -- so a plot's monsters don't all attack at once
		-- Where in its 4-second pattern the attack starts: RAGE winds up at the end of its pattern and lunges at the start.
		attackFrom = if rages then 3.4 else 0,
		attacking = false,
		frame = math.random(0, DinoLife.farFrameSkip),
		pending = 0,
		carrier = if carried then (model.Parent and model.Parent:FindFirstChild("HumanoidRootPart")) :: BasePart? else nil,
		mine = carried and model.Parent == Players.LocalPlayer.Character,
		walking = false,
		hidden = false,
		looks = {}, -- each part's own Transparency, for showing it again after hiding it
		-- Its body on the ground, in its own axes at rest: width across and depth from nose to tail, in studs.
		width = extents.X,
		depth = extents.Z,
		radius = (extents.X + extents.Z) / 4, -- roughly, for keeping out of others' way
		plotIndex = if stays then nil else plotIndex,
		ring = nil,
		ringDelay = 0,
		stuck = 0,
		closest = math.huge,
		gait = 1,
		turning = false,
	}
	if not stays then
		joinPlot(dinos[model])
	end
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			dinos[model].looks[part] = part.Transparency
		end
	end
end

-- A carried monster walks while its carrier moves and idles while they stand. On the carrier's own screen it hides
-- while the camera is scripted (aiming, the throw, the reveal) and while training, where the rack's bar would run
-- through it.
local function ride(state)
	local velocity = state.carrier.AssemblyLinearVelocity
	state.walking = Vector3.new(velocity.X, 0, velocity.Z).Magnitude > DinoLife.carry.walkSpeed
	if not state.mine then
		return
	end
	local hidden = workspace.CurrentCamera.CameraType == Enum.CameraType.Scriptable
		or Players.LocalPlayer:GetAttribute("IsTraining") == true
	if hidden ~= state.hidden then
		state.hidden = hidden
		for part, transparency in state.looks do
			part.Transparency = if hidden then 1 else transparency
		end
	end
end

-- Turns it toward a direction at its turning speed. Returns how far off it was.
local function turnToward(state, wanted: Vector3, dt: number): number
	local angle = math.acos(math.clamp(state.facing:Dot(wanted), -1, 1))
	if angle > 0.001 then
		local sign = if state.facing:Cross(wanted).Y >= 0 then 1 else -1
		state.facing = CFrame.Angles(0, sign * math.min(DinoLife.turnSpeed * dt, angle), 0):VectorToWorldSpace(state.facing)
	end
	return angle
end

local function placeModel(state)
	local look = if state.turned then -state.facing else state.facing
	state.model:PivotTo(CFrame.lookAt(state.position, state.position + look))
end

-- Its place in its owner's circle, right now (the circle moves with the owner).
local function ringSpot(state, ring): Vector3
	local radius = state.ringRadius
	local spot = ring.owner + Vector3.new(cos(state.ringAngle) * radius, 0, sin(state.ringAngle) * radius)
	return Vector3.new(spot.X, state.position.Y, spot.Z)
end

-- Which way to walk: at its spot, bent to one side round any monster (or the owner) in its way ahead, less so near the spot
-- so it can settle in beside its neighbours. It only ever swerves, at most 45 degrees, never backs away, so it always gets
-- closer: on a small plot the giants can't help touching, and pushing them apart would walk them off it.
local function steerFrom(state, wanted: Vector3, distance: number, ring): Vector3
	local side = Vector3.new(-wanted.Z, 0, wanted.X)
	local lateral = 0
	local function avoid(point: Vector3, reach: number)
		local to = flat(point - state.position)
		local d = to.Magnitude
		local ahead = to:Dot(wanted)
		if d < reach and d > 0.01 and ahead > 0 and ahead < distance + reach then
			local across = to:Dot(side)
			lateral -= (if across >= 0 then 1 else -1) * ((reach - d) / reach)
		end
	end
	for _, other in plotMembers[state.plotIndex] or {} do
		if other ~= state then
			avoid(other.position, (state.width + other.width) / 2 + DinoLife.ring.gap / 2)
		end
	end
	if ring then
		avoid(ring.owner, state.width / 2 + DinoLife.steer.ownerRadius + DinoLife.ring.ownerGap / 2)
	end
	local fade = math.clamp(distance / (state.width + 0.01), 0, 1)
	lateral = math.clamp(lateral * DinoLife.steer.avoidWeight * fade, -1, 1)
	return (wanted + side * lateral).Unit
end

local HOME_DROP = 40 -- studs a second a released monster comes down to its plot's ground

local function moveAlong(state, dt: number)
	state.turning = false
	if state.attacking then
		return -- it stands its ground while it attacks, and carries on where it was going after (DinoLife.attackCycle)
	end
	local ring = state.ring
	if ring and state.ringDelay > 0 then
		-- A moment before it reacts to its owner: it finishes the step it was taking.
		state.ringDelay -= dt
		if not state.target then
			return
		end
		ring = nil
	end
	if ring then
		local spot = ringSpot(state, ring)
		if state.ringSlackAt and flat(ring.owner - state.ringSlackAt).Magnitude > DinoLife.ring.followDistance then
			state.ringSlack, state.ringSlackAt = 0, nil -- the owner moved on: walk to the real place again
		end
		local slack = DinoLife.ring.followDistance + state.width / 4 + (state.ringSlack or 0)
		if state.target or flat(spot - state.position).Magnitude > slack then
			if not state.target then
				state.stuck = 0
				state.closest = math.huge
			end
			state.target = spot
		else
			-- In its place: it turns to face its owner, stepping round if it's far off.
			local toOwner = flat(ring.owner - state.position)
			if toOwner.Magnitude > 0.01 then
				local off = turnToward(state, toOwner.Unit, dt)
				state.turning = off > DinoLife.steer.turnInPlace
				if off > 0.001 then
					placeModel(state)
				end
			end
			return
		end
	elseif not state.target then
		state.idleLeft -= dt
		if state.idleLeft <= 0 then
			state.target = wanderSpot(state)
			state.stuck = 0
			state.closest = math.huge
		end
		return
	end
	local offset = flat(state.target - state.position)
	local distance = offset.Magnitude
	if distance < DinoLife.arriveDistance * state.scale then
		state.target = nil
		state.gait = 1
		state.idleLeft = idleTime()
		if state.hurry then -- home after a leash: back on its plot's ground
			state.hurry = nil
			state.position = Vector3.new(state.position.X, state.homeY, state.position.Z)
			placeModel(state)
		end
		return
	end
	-- Getting no closer (walled in by others): it stops. In the circle it settles where it is and turns to its owner.
	if distance < state.closest - 0.5 then
		state.closest = distance
		state.stuck = 0
	else
		state.stuck += dt
		if ring and state.stuck > DinoLife.steer.giveUpSeconds * 0.5 then
			state.target = nil
			state.gait = 1
			state.ringSlack = distance
			state.ringSlackAt = ring.owner
			return
		end
		if not ring and state.stuck > DinoLife.steer.giveUpSeconds then
			state.target = nil
			state.gait = 1
			state.idleLeft = 1 + math.random() * 2
			return
		end
	end
	local wanted = steerFrom(state, offset / distance, distance, ring)
	turnToward(state, wanted, dt)
	-- It slows while turning, so it doesn't drift sideways, and as it nears its spot, so it doesn't stop dead.
	local slowing = math.clamp(distance / (state.speed * DinoLife.steer.slowSeconds), DinoLife.steer.minPace, 1)
	local pace = math.max(state.facing:Dot(wanted), 0) * slowing
	state.gait = math.max(pace, 0.5)
	local hurry = state.hurry
	if hurry then
		-- Hurrying home after a leash (release): faster, and coming down (or up) to its plot's ground as it goes.
		pace *= hurry
		local y = state.position.Y
		y += math.clamp(state.homeY - y, -HOME_DROP * dt, HOME_DROP * dt)
		state.position = Vector3.new(state.position.X, y, state.position.Z)
	end
	state.position += state.facing * state.speed * pace * dt
	placeModel(state)
end

-- A leashed monster is a ragdoll: every bone hangs loose on a spring. Each one swings toward wherever "down" is
-- for the body right now (gravity, plus being yanked, flung or stopped dead), overshoots and wobbles, so legs, tail
-- and head trail behind a drag, splay in a tumble and droop when it lies on its side. One rule for every monster,
-- whatever its bones (Config/Troll limp). `down` is that direction in the model's own space, about 1 long at rest;
-- nil once it's let go, when the bones swing back to their own pose and the ragdoll fades out.
local function flop(state, dt: number, down: Vector3?)
	local limp = state.limp
	local settings = Troll.limp
	local targetX, targetZ = 0, 0
	if down then
		local right = if state.turned then -down.X else down.X
		local ahead = if state.turned then down.Z else -down.Z
		targetX = math.clamp(math.atan2(ahead, -down.Y), -settings.maxAngle, settings.maxAngle)
		targetZ = math.clamp(-math.atan2(right, -down.Y), -settings.maxAngle, settings.maxAngle)
		limp.weight = math.min(1, limp.weight + dt / settings.fadeIn)
	else
		limp.weight -= dt / settings.fadeOut
		if limp.weight <= 0 then
			state.limp = nil
			return
		end
	end
	local steps = math.clamp(math.ceil(dt * 60), 1, 6)
	local h = dt / steps
	for _, entry in state.bones do
		local rate, reach = entry.limpRate, entry.limpReach
		local x, z, vx, vz = entry.limpX, entry.limpZ, entry.limpVX, entry.limpVZ
		local drag = 2 * settings.damping * rate
		for _ = 1, steps do
			vx += (rate * rate * (targetX * reach - x) - drag * vx) * h
			vz += (rate * rate * (targetZ * reach - z) - drag * vz) * h
			x += vx * h
			z += vz * h
		end
		local most = settings.maxAngle * 1.3
		entry.limpX, entry.limpZ = math.clamp(x, -most, most), math.clamp(z, -most, most)
		entry.limpVX, entry.limpVZ = vx, vz
	end
end

local function pose(state, dt: number)
	-- A monster that attacks now and then (DinoLife.attackCycle): sa is how far it is into its attack pattern and k how much of it
	-- shows, 0 between attacks, easing up to 1 and back down at either end of one. Everyone else attacks nonstop: sa = s, k = 1.
	local cycle = state.attackCycle
	local k, sa = 1, nil
	if cycle then
		state.attackClock = (state.attackClock + dt) % cycle.every
		local c = state.attackClock
		state.attacking = c < cycle.seconds
		if state.attacking then
			local u = math.clamp(math.min(c, cycle.seconds - c) / cycle.ease, 0, 1)
			k = u * u * (3 - 2 * u)
			sa = state.attackFrom + c
		else
			k, sa = 0, state.attackFrom
		end
	end
	local goal = if (state.target and not state.attacking) or state.walking or state.turning then 1 else 0
	local step = dt / DinoLife.blendTime
	state.blend += math.clamp(goal - state.blend, -step, step)
	local w = state.blend
	local eased = w * w * (3 - 2 * w)
	state.stride = (state.stride + dt * state.gait / state.strideSeconds * TAU) % TAU
	state.idleClock = (state.idleClock + dt / DinoLife.idleLoopSeconds * TAU) % TAU
	state.thrashClock = (state.thrashClock + dt) % 4
	local p, t, s = state.stride, state.idleClock, state.thrashClock
	sa = sa or s
	local limp = state.limp
	for _, entry in state.bones do
		local wx, wy, wz, wb, ws = entry.walk(p)
		local ix, iy, iz, ib, is = entry.idle(t)
		local rise = (ib + (wb - ib) * eased) * state.scale
		local surge = ((is or 0) + ((ws or 0) - (is or 0)) * eased) * state.scale
		local transform = CFrame.new(entry.yaw * rise + entry.roll * surge)
			* CFrame.fromAxisAngle(entry.pitch, ix + (wx - ix) * eased)
			* CFrame.fromAxisAngle(entry.roll, iy + (wy - iy) * eased)
			* CFrame.fromAxisAngle(entry.yaw, iz + (wz - iz) * eased)
		local spin = entry.spin
		if spin then
			entry.angle = (entry.angle + spin.speed * dt) % TAU
			transform *= CFrame.fromAxisAngle(entry[spin.axis], entry.angle)
		end
		local thrash = entry.thrash
		if thrash then
			local kt = if entry.steady then 1 else k
			local tx, ty, tz = thrash(if entry.steady then s else sa)
			transform *= CFrame.fromAxisAngle(entry.pitch, kt * tx)
				* CFrame.fromAxisAngle(entry.roll, kt * ty)
				* CFrame.fromAxisAngle(entry.yaw, kt * tz)
		end
		local rage = entry.rage
		if rage then
			local rx, ry, rz, rrise, rsurge = rage(sa)
			transform = CFrame.new((entry.yaw * rrise + entry.roll * rsurge) * k * state.scale)
				* transform
				* CFrame.fromAxisAngle(entry.pitch, k * rx)
				* CFrame.fromAxisAngle(entry.roll, k * ry)
				* CFrame.fromAxisAngle(entry.yaw, k * rz)
		end
		local drip = entry.drip
		if drip then
			transform = CFrame.new(entry.yaw * (-drip.gap * ((s / drip.period) % 1) * state.scale)) * transform
		end
		local pounce = entry.pounce
		if pounce then
			local px, py, pz = pounce(sa)
			transform *= CFrame.fromAxisAngle(entry.pitch, k * px)
				* CFrame.fromAxisAngle(entry.roll, k * py)
				* CFrame.fromAxisAngle(entry.yaw, k * pz)
		end
		if entry.vent then
			transform = CFrame.new(entry.yaw * (VENT.gap * ((s / VENT.period) % 1) * state.scale)) * transform
		end
		local sway = entry.sway
		if sway then
			local g = if entry.gated then k else 1 -- an attack move waits for its turn; a feather sways all the time
			local ax, ay, az, ahead, up, across = sway(if entry.gated then sa else s, eased)
			if g < 1 then
				-- Whole turns left over from a spin (the Whirl ends two turns round) are no turn at all: without this, easing
				-- the attack out would unwind them.
				ax, ay, az = (ax + math.pi) % TAU - math.pi, (ay + math.pi) % TAU - math.pi, (az + math.pi) % TAU - math.pi
			end
			transform = CFrame.new((entry.roll * ahead + entry.yaw * (up or 0) + entry.pitch * (across or 0)) * g * state.scale)
				* transform
				* CFrame.fromAxisAngle(entry.pitch, g * ax)
				* CFrame.fromAxisAngle(entry.roll, g * ay)
				* CFrame.fromAxisAngle(entry.yaw, g * az)
		end
		local always = entry.always
		if always then -- a marker table's "@always": on top of everything, never waiting for the attack
			local ax, ay, az, ahead, up, across = always(s)
			transform = CFrame.new((entry.roll * ahead + entry.yaw * up + entry.pitch * across) * state.scale)
				* transform
				* CFrame.fromAxisAngle(entry.pitch, ax)
				* CFrame.fromAxisAngle(entry.roll, ay)
				* CFrame.fromAxisAngle(entry.yaw, az)
		end
		if limp then
			transform *= CFrame.fromAxisAngle(entry.pitch, entry.limpX * limp.weight)
				* CFrame.fromAxisAngle(entry.roll, entry.limpZ * limp.weight)
		end
		entry.bone.Transform = transform
	end
end

local function step(dt: number)
	local camera = workspace.CurrentCamera
	local cameraPosition = camera.CFrame.Position
	local look = camera.CFrame.LookVector
	-- Half the angle across the screen's diagonal, so anything near a corner still counts as in view.
	local viewport = camera.ViewportSize
	local aspect = viewport.X / math.max(viewport.Y, 1)
	local halfView = math.atan(math.tan(math.rad(camera.FieldOfView) / 2) * math.sqrt(1 + aspect * aspect))
	updateRings()
	local pace = if LowDetail.on() then LOW else DinoLife -- Low detail (Settings): far monsters move less smoothly, sooner
	for _, state in dinos do
		state.pending += dt
		state.frame += 1
		local carrier = state.carrier
		local offset = (if carrier then carrier.Position else state.position) - cameraPosition
		local distance = offset.Magnitude
		local inView = distance <= state.reach
			or math.acos(math.clamp(offset:Dot(look) / distance, -1, 1)) <= halfView + math.asin(state.reach / distance)
		local shown = state.shown
		local skip = if state.held then 1 -- leashed: it follows its tumbling body every frame
			elseif shown then (if shown() then 1 else math.huge)
			elseif not inView and not state.mine then pace.offScreenFrameSkip -- your own carried one hides on cue (ride)
			elseif distance > pace.farDistance
			then pace.farFrameSkip
			elseif distance > pace.nearDistance then pace.midFrameSkip
			else 1
		if state.frame % skip == 0 then
			local elapsed = state.pending
			state.pending = 0
			if state.held then
				local at = state.held()
				state.model:PivotTo(at)
				state.position = at.Position
				-- Which way is "down" for its loose bones: gravity, less however its body is being thrown about.
				local limp = state.limp
				local seconds = math.max(elapsed, 1 / 240)
				local velocity = (at.Position - limp.last) / seconds
				local push = (velocity - limp.velocity) / seconds
				if push.Magnitude > Troll.limp.maxPush then
					push = push.Unit * Troll.limp.maxPush
				end
				limp.last, limp.velocity = at.Position, velocity
				flop(state, elapsed, at:VectorToObjectSpace(Vector3.new(0, -workspace.Gravity, 0) - push) / workspace.Gravity)
			elseif state.limp then
				flop(state, elapsed, nil) -- let go: its bones swing back
				moveAlong(state, elapsed)
			elseif carrier then
				ride(state)
			else
				moveAlong(state, elapsed)
			end
			pose(state, elapsed)
		end
	end
end

-- The walking monster on a plot nearest a point, for the Leash button (LeashController).
function DinoLifeController.nearest(plotIndex: number, from: Vector3): Model?
	local best, bestDistance = nil, math.huge
	for _, state in plotMembers[plotIndex] or {} do
		local distance = flat(state.position - from).Magnitude
		if not state.held and distance < bestDistance then
			best, bestDistance = state.model, distance
		end
	end
	return best
end

-- A leashed monster stops deciding where it goes: every frame it stands where `where` says, tumbling and all, and
-- its bones go limp (flop). False if this isn't a walking plot monster.
function DinoLifeController.hold(model: Model, where: () -> CFrame): boolean
	local state = dinos[model]
	if not state or not state.plotIndex or state.carrier then
		return false
	end
	if not state.held then
		state.homeY = state.position.Y
	end
	if not state.limp then
		for _, entry in state.bones do
			if not entry.limpRate then
				-- Each bone swings at its own pace, so they never move as one. A bone that carries others (spine, neck,
				-- thigh) only gives a little: the loose ends do the flailing.
				local settings = Troll.limp
				local carries = entry.bone:FindFirstChildWhichIsA("Bone") ~= nil
				entry.limpRate = settings.rate * (0.7 + 0.6 * math.random())
				entry.limpReach = if carries then settings.innerReach else 1
			end
			entry.limpX, entry.limpZ, entry.limpVX, entry.limpVZ = 0, 0, 0, 0
		end
		state.limp = { weight = 0, last = state.position, velocity = Vector3.zero }
	end
	state.held = where
	state.target = nil
	state.walking = false
	state.gait = 1
	return true
end

-- A knock: every loose bone is thrown out of place, harder the harder the hit (0 to 1), and wobbles back (flop).
-- For a slam into the ground or a wall, and the shake as it gets up.
function DinoLifeController.jolt(model: Model, strength: number)
	local state = dinos[model]
	if not state or not state.limp then
		return
	end
	local kick = Troll.limp.joltAngle * strength
	for _, entry in state.bones do
		entry.limpVX += (math.random() * 2 - 1) * kick * entry.limpRate * entry.limpReach
		entry.limpVZ += (math.random() * 2 - 1) * kick * entry.limpRate * entry.limpReach
	end
end

-- Let go: it stands up where it lies, facing the way it was, and hurries back to a spot on its plot at `hurry` times
-- its walking speed.
function DinoLifeController.release(model: Model, hurry: number)
	local state = dinos[model]
	if not state or not state.held then
		return
	end
	state.held = nil
	state.walking = false
	state.gait = 1
	local look = flat(model:GetPivot().LookVector)
	if look.Magnitude > 0.05 then
		state.facing = if state.turned then -look.Unit else look.Unit
	end
	state.hurry = hurry
	state.target = wanderSpot(state)
	state.stuck = 0
	state.closest = math.huge
	state.pending = 0
	placeModel(state)
end

-- A monster shown in the UI (the Shop's ViewportFrames): it plays its own idle where it stands, for ever (swimmers
-- hover, thrashers thrash, ragers bite), every frame while shown() says it's on screen, and is dropped when destroyed.
function DinoLifeController.showcase(model: Model, shown: () -> boolean)
	model:SetAttribute("Stay", true)
	add(model)
	local state = dinos[model]
	if not state then
		return
	end
	state.shown = shown
	model.Destroying:Connect(function()
		dinos[model] = nil
	end)
end

-- The monster in a reveal, alive on its spot: it breathes and sways through its own idle. Returns the function that
-- makes it roar now, for the unveil (monsters with no roar just carry on with their idle), and the function that
-- freezes it as it is, like a photo (true), or lets it move again (false) [Owner, 2026-11-11: "make the monster not
-- move for a better shot"]. `still` on the roar: it doesn't attack as it's unveiled, so it can be frozen in its roar.
function DinoLifeController.reveal(model: Model): ((still: boolean?) -> (), (frozen: boolean) -> ())
	local held = false
	DinoLifeController.showcase(model, function()
		return model.Parent ~= nil and not held
	end)
	local state = dinos[model]
	return function(still: boolean?)
		if state then
			state.idleClock = ROAR_FROM
			-- A monster that attacks now and then (DinoLife.attackCycle) attacks as it's unveiled, unless it's to hold still:
			-- then its clock goes to just after an attack.
			local cycle = state.attackCycle
			state.attackClock = if still and cycle then cycle.seconds else 0
		end
	end, function(frozen: boolean)
		held = frozen
		if state and not frozen then
			state.pending = 0 -- the time it stood frozen doesn't count: its next pose starts from now
		end
	end
end

function DinoLifeController.start()
	for _, model in CollectionService:GetTagged(DinoLife.tag) do
		add(model)
	end
	CollectionService:GetInstanceAddedSignal(DinoLife.tag):Connect(function(model)
		-- Waits a frame so a model that's still arriving has its parts.
		task.defer(add, model)
	end)
	CollectionService:GetInstanceRemovedSignal(DinoLife.tag):Connect(function(model)
		local state = dinos[model]
		if state and state.plotIndex then
			leavePlot(state)
			local key = placeKey(model)
			if key then
				lastPlaces[key] = { position = state.position, facing = state.facing, at = os.clock() }
			end
		end
		dinos[model] = nil
	end)
	RunService.Heartbeat:Connect(step)
end

return DinoLifeController
