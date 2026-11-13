-- What the buyer sees after a Robux purchase goes through, from Figma "Shop" page "Shop v2" (2026-11-12). The server
-- has already given the item and says so on ShopRemotes.Moment; this only shows it. Numbers live in Config/ShopMoments.
--   Prism Egg: the egg lands, shakes three times while the light from its cracks climbs blue, purple, gold up to the
--     monster's real tier (only show: the server rolled it before), bursts, and the monster is revealed. A tap skips
--     to the reveal. OPEN ANOTHER asks for the next egg; several eggs open one after the other.
--   A Game Pass monster (Gloomfin): lights out, two eyes, it lunges and bites, then it's yours.
--   A Game Pass: a short UNLOCKED FOREVER card that closes by itself (a tap closes it sooner).
--   Cash, Throw Power and luck: a quick pop that flies to its counter. No veil, takes no taps: you keep playing.
-- A gift plays the same moment for the receiver, with "A GIFT FROM (name)" over it.
-- Drawn on a 1280 x 720 stage scaled to fit the screen, like the design's frames.
local CollectionService = game:GetService("CollectionService")
local MarketplaceService = game:GetService("MarketplaceService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local DinoLife = require(ReplicatedStorage.Shared.Config.DinoLife)
local DinoLifeController = require(script.Parent.DinoLifeController)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)
local Gifts = require(ReplicatedStorage.Shared.Gifts)
local PopText = require(ReplicatedStorage.Shared.PopText)
local PrismEgg = require(script.Parent.PrismEgg)
local Sfx = require(script.Parent.Sfx)
local Shop = require(ReplicatedStorage.Shared.Config.Shop)
local ShopLook = require(script.Parent.ShopLook)
local ShopMoments = require(ReplicatedStorage.Shared.Config.ShopMoments)
local SoundPool = require(script.Parent.SoundPool)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local PurchaseMoments = {}

local W, H = 1280, 720
local WHITE = Color3.new(1, 1, 1)
local GOLD = { "#fff1a8", "#ffb21a" }
local hex = ShopLook.hex
local blank = ShopLook.blank

-- What the Shop lends: closing its panel, and asking to buy another Prism Egg.
local hooks = { closeShop = function() end, buyPrism = function() end }
local prismPrice: number? = nil

local gui: ScreenGui? = nil
local function layer(): ScreenGui
	if gui then
		return gui
	end
	local made = Instance.new("ScreenGui")
	made.Name = "ShopMomentHud"
	made.ResetOnSpawn = false
	made.ScreenInsets = Enum.ScreenInsets.None -- the veil and the edge glows reach the screen's edges
	made.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	made.DisplayOrder = 8 -- over the Shop and the pop-up text, under the gift toast and the reveal
	made.Parent = player:WaitForChild("PlayerGui")
	gui = made
	return made
end

local function sound(name: string, speed: number?)
	local found = ShopMoments.sounds[name]
	if found then
		SoundPool.play(found.id, found.volume, speed or found.speed or 1, found.skip)
	end
end

-- 0 before `from`, 1 after `from + length`, climbing evenly between.
local function seg(t: number, from: number, length: number): number
	return math.clamp((t - from) / length, 0, 1)
end

local function lerp(a: number, b: number, u: number): number
	return a + (b - a) * u
end

local function outCubic(u: number): number
	return 1 - (1 - u) ^ 3
end

local function outBack(u: number): number
	return 1 + 2.70158 * (u - 1) ^ 3 + 1.70158 * (u - 1) ^ 2
end

-- Something slamming in: far too big, down to its size with a small dip past it. 0 while it hasn't started.
local function slam(u: number, from: number?): number
	return if u <= 0 then 0 else lerp(from or 2.6, 1, outBack(u))
end

type Scene = {
	root: Frame,
	veil: Frame,
	stage: Frame,
	scale: number, -- screen pixels per design pixel
	fx: ShopLook.Effects,
	tapped: boolean,
	ahead: number, -- seconds a tap skipped
	shake: number, -- how hard the stage shakes right now, design pixels
}

-- A scene over the game: a veil (see-through until the moment darkens it), the stage, and, for a moment that takes
-- taps, a catcher under the stage so nothing behind can be pressed.
local function newScene(name: string, blocking: boolean, veilColour: Color3?): Scene
	local root = blank(layer(), name)
	root.Size = UDim2.fromScale(1, 1)
	local veil = ShopLook.block(root, "Veil", veilColour or hex("#0d0822"), 0, 0, 0, 0, 0)
	veil.Size = UDim2.fromScale(1, 1)
	veil.ZIndex = -1
	local catcher: TextButton? = nil
	if blocking then
		local button = Instance.new("TextButton")
		button.Name = "Catcher"
		button.Text = ""
		button.BackgroundTransparency = 1
		button.AutoButtonColor = false
		button.Size = UDim2.fromScale(1, 1)
		button:SetAttribute("NoClickSound", true)
		button.Parent = root
		catcher = button
	end
	local screen = workspace.CurrentCamera.ViewportSize
	local scene: Scene = {
		root = root,
		veil = veil,
		stage = blank(root, "Stage"), -- made after the catcher, so the stage's buttons get their taps first
		scale = math.min(screen.X / W, screen.Y / H),
		fx = ShopLook.effects(),
		tapped = false,
		ahead = 0,
		shake = 0,
	}
	if catcher then
		catcher.Activated:Connect(function()
			scene.tapped = true
		end)
	end
	local stage = scene.stage
	stage.AnchorPoint = Vector2.new(0.5, 0.5)
	stage.Position = UDim2.fromScale(0.5, 0.5)
	stage.Size = UDim2.fromOffset(W, H)
	local fit = Instance.new("UIScale")
	fit.Scale = scene.scale
	fit.Parent = stage
	return scene
end

-- Calls step every frame with the seconds since it started (plus what a tap skipped) until step says it's done.
local function run(scene: Scene, step: (t: number, dt: number) -> boolean)
	local start = os.clock()
	local last = start
	while scene.root.Parent do
		local now = os.clock()
		local dt = now - last
		last = now
		scene.fx.step(now)
		if scene.shake > 0 then
			local by = scene.shake * scene.scale
			scene.stage.Position = UDim2.new(0.5, (math.random() * 2 - 1) * by, 0.5, (math.random() * 2 - 1) * by)
			scene.shake = math.max(0, scene.shake - dt * 60)
		else
			scene.stage.Position = UDim2.fromScale(0.5, 0.5)
		end
		if step(now - start + scene.ahead, dt) then
			break
		end
		RunService.RenderStepped:Wait()
	end
end

-- Fades the whole scene away and removes it.
local function close(scene: Scene, seconds: number)
	local fade = ShopLook.fader(scene.root)
	scene.shake = 0
	run(scene, function(t)
		fade(1 - seg(t - scene.ahead, 0, seconds))
		return t - scene.ahead >= seconds
	end)
	scene.root:Destroy()
end

-- Glows along the four edges of the screen. Returns a function that sets how strong they are, 0 to 1.
local function edges(root: Frame, colour: Color3, depth: number): (number) -> ()
	local strips = {}
	for _, spec in
		{
			{ UDim2.new(), UDim2.new(1, 0, 0, depth), 90, false },
			{ UDim2.new(0, 0, 1, -depth), UDim2.new(1, 0, 0, depth), 90, true },
			{ UDim2.new(), UDim2.new(0, depth, 1, 0), 0, false },
			{ UDim2.new(1, -depth, 0, 0), UDim2.new(0, depth, 1, 0), 0, true },
		}
	do
		local strip = ShopLook.block(root, "Edge glow", colour, 0, 0, 0, 0, 1)
		strip.ZIndex = 0 -- over the veil, under the stage
		strip.Position = spec[1]
		strip.Size = spec[2]
		local gradient = ShopLook.fade(strip, 1, 1, spec[3])
		table.insert(strips, { gradient, spec[4] })
	end
	return function(strength: number)
		for _, strip in strips do
			strip[1].Transparency = if strip[2] then NumberSequence.new(1, 1 - strength) else NumberSequence.new(1 - strength, 1)
		end
	end
end

-- A circle drawn as a line, its middle at (cx, cy): the rings that race out of a burst.
local function ring(parent: Instance, cx: number, cy: number, colour: Color3, thickness: number): (Frame, UIStroke)
	local frame = blank(parent, "Ring")
	frame.AnchorPoint = Vector2.new(0.5, 0.5)
	frame.Position = UDim2.fromOffset(cx, cy)
	ShopLook.round(frame, 0.5)
	local line = UiKit.stroke(frame, thickness, colour)
	line.Transparency = 1
	return frame, line
end

-- The monster, alive, in a box whose middle is at (cx, cy). Returns its holder and the UIScale that sizes it.
local function monsterView(parent: Instance, id: string, cx: number, cy: number, w: number, h: number, turn: number?, zoom: number?): (Frame, UIScale)
	local holder = blank(parent, "Monster")
	holder.AnchorPoint = Vector2.new(0.5, 0.5)
	ShopLook.at(holder, cx, cy, w, h)
	local size = Instance.new("UIScale")
	size.Parent = holder
	local view, model = UiKit.monster(holder, id, { live = true, aspect = w / h, zoom = zoom or 0.95, turn = turn })
	view.Size = UDim2.fromScale(1, 1)
	view.Ambient = Color3.fromRGB(170, 160, 190)
	view.LightColor = WHITE
	view.LightDirection = Vector3.new(-0.4, -1, -0.8)
	DinoLifeController.showcase(model, function()
		return holder.Visible and holder.Parent ~= nil
	end)
	return holder, size
end

-- Something that pops in: a holder with its middle at (cx, cy) and the UIScale that sizes it.
local function popper(parent: Instance, name: string, cx: number, cy: number, w: number, h: number): (Frame, UIScale)
	local holder = blank(parent, name)
	holder.AnchorPoint = Vector2.new(0.5, 0.5)
	ShopLook.at(holder, cx, cy, w, h)
	local size = Instance.new("UIScale")
	size.Scale = 0
	size.Parent = holder
	return holder, size
end

-- A button that pops in, its middle at (cx, cy).
local function popButton(parent: Instance, value: string, style: string, cx: number, cy: number, w: number, h: number, textSize: number): (TextButton, UIScale)
	local holder, size = popper(parent, value, cx, cy, w, h)
	local button = UiKit.button(holder, value, style, w, h, textSize)
	return button, size
end

-- A gold sticker stamped on, its middle at (cx, cy).
local function ribbon(parent: Instance, value: string, style: string | { string }, textSize: number, cx: number, cy: number, tilt: number): UIScale
	local tag = UiKit.tag(parent, value, style, textSize, tilt)
	tag.AnchorPoint = Vector2.new(0.5, 0.5)
	tag.Position = UDim2.fromOffset(cx, cy)
	local size = Instance.new("UIScale")
	size.Scale = 0
	size.Parent = tag
	return size
end

local function giftLine(parent: Instance, from: string?)
	if from then
		local line = UiKit.text(parent, `A GIFT FROM {string.upper(from)}`, 26)
		line.Position = UDim2.fromOffset(0, 6)
		ShopLook.paint(line, GOLD)
	end
end

-- PRISM EGG ---------------------------------------------------------------------------------------------------------

local queue: { any } = {}

local function playPrism(moment)
	local look = ShopMoments.prism
	local hatches = Shop.prismEgg.hatches
	local tier = 1
	for index, option in hatches do
		if option.id == moment.id then
			tier = index
		end
	end
	local special = DinoStats.special(moment.id)
	if not special then
		return
	end
	local jackpot = tier == #hatches
	local colours = look.tiers[tier] or look.tiers[#look.tiers]
	local deep, light = hex(colours[1]), hex(colours[2])
	local lights = {}
	for index, colour in look.lights do
		lights[index] = hex(colour)
	end

	local scene = newScene("Prism Egg", true)
	local stage, fx = scene.stage, scene.fx

	-- Behind the egg: rays and the light from its cracks, in the colour of the tier reached so far.
	local crackRays = fx.rays(stage, lights[1], 640, 330, 640, 0, 12)
	local crackGlow = fx.glow(stage, lights[1], 640, 330, 620, 620, 0)
	local floor = blank(stage, "Floor")
	floor.Size = UDim2.fromOffset(W, H)
	ShopLook.image(floor, "glow", hex("#c9a8ff"), 640, 478, 560, 130, 0.55)
	ShopLook.pedestal(floor, 640, 478, 300, 54, hex("#e6d6ff"), 5)
	local streaks = {}
	for index, dx in { -64, 0, 64 } do
		local streak = ShopLook.block(floor, "Drop streak", WHITE, 640 + dx - 5, 40 + (index % 2) * 36, 10, 150, 1, 5)
		streaks[index] = ShopLook.fade(streak, 1, 1)
	end

	-- The egg, in a view as big as the stage so its shards have room to fly.
	local egg = PrismEgg.build()
	local eggView, lookAt = PrismEgg.view(stage, egg, PrismEgg.HEIGHT * H / 226)
	eggView.AnchorPoint = Vector2.new(0.5, 0.5)
	eggView.Size = UDim2.fromOffset(W, H)
	PrismEgg.pose(egg, 0, 0, 0, lights[1])

	local puffs = {}
	for index, puff in { { -160, 478, 44 }, { 158, 482, 36 }, { -204, 490, 22 }, { 206, 492, 20 } } do
		puffs[index] = { ShopLook.ellipse(stage, "Dust puff", hex("#e6d6ff"), 0, 0, 0, 0, 0), puff }
	end

	-- The three small lights under the egg: how far the light has climbed.
	local pips = {}
	local unlit, unlitEdge = hex("#2a2148"), hex("#4a3f78")
	for index, colour in lights do
		local cx = 570 + (index - 1) * 70
		local halo = ShopLook.image(stage, "glow", colour, cx, 580, 120, 120, 0)
		local pip = ShopLook.block(stage, "Tier light", unlit, cx, 580, 34, 34, 1, 8)
		pip.AnchorPoint = Vector2.new(0.5, 0.5)
		pip.Rotation = 45
		local edge = UiKit.stroke(pip, 4, unlitEdge)
		local size = Instance.new("UIScale")
		size.Parent = pip
		pips[index] = { pip = pip, edge = edge, halo = halo, size = size, colour = colour }
	end

	-- The burst: a white flash over everything and two rings racing out.
	local flash = ShopLook.block(scene.root, "Flash", WHITE, 0, 0, 0, 0, 0)
	flash.Size = UDim2.fromScale(1, 1)
	flash.ZIndex = 3
	local ringA, lineA = ring(stage, 640, 330, WHITE, 16)
	local ringB, lineB = ring(stage, 640, 330, light, 8)

	-- The reveal: the monster on rays in its tier's colour, its name, its chance and share, what it earns, the buttons.
	local reveal = blank(stage, "Reveal")
	reveal.Size = UDim2.fromOffset(W, H)
	reveal.Visible = false
	local rays = fx.rays(reveal, if jackpot then hex("#ffd23f") else deep, 640, 305, if jackpot then 820 else 760, 0)
	local glow = fx.glow(reveal, light, 640, 305, 860, 660, 0)
	fx.confetti(
		reveal,
		if jackpot then look.jackpotConfetti else look.confetti,
		if jackpot then { "#ffd23f", "#ff5a7a", "#ffffff", "#ff9ec4" } else { colours[2], "#ffffff", colours[1] },
		W,
		H,
		tier
	)
	local gold = if jackpot then edges(scene.root, hex("#ffd23f"), 130 * scene.scale) else nil
	ShopLook.shadow(reveal, 640, if jackpot then 476 else 452, 300, 26, 0.4)
	local _, monsterSize = monsterView(reveal, moment.id, 640, 292, 760, 350, if moment.id == "Umbray" then math.rad(22) else nil, 0.8)
	monsterSize.Scale = 0
	for index, spot in { { 250, 180, 30 }, { 1010, 150, 24 }, { 1050, 420, 30 }, { 230, 430, 20 } } do
		fx.sparkle(reveal, spot[1], spot[2], spot[3], index * 1.4)
	end
	local _, titleSize = ShopLook.words(reveal, `{string.upper(special.name)}!`, if jackpot then 98 else 108, 640, 96, if jackpot then GOLD else { "#ffffff", colours[2] })
	titleSize.Scale = 0
	giftLine(reveal, moment.from)
	local sticker = if jackpot then ribbon(reveal, "JACKPOT!", { "#ff9ec4", "#e8265a" }, 40, 330, 150, -10) else nil

	local row, rowSize = popper(reveal, "Odds and share", 640, if jackpot then 512 else 496, 0, 44)
	row.AutomaticSize = Enum.AutomaticSize.X
	local rowLayout = Instance.new("UIListLayout")
	rowLayout.FillDirection = Enum.FillDirection.Horizontal
	rowLayout.VerticalAlignment = Enum.VerticalAlignment.Center
	rowLayout.Padding = UDim.new(0, 18)
	rowLayout.SortOrder = Enum.SortOrder.LayoutOrder
	rowLayout.Parent = row
	local chip = ShopLook.block(row, "Chance", hex("#0d0822"), 0, 0, 0, 40, 0.7, 20)
	chip.AutomaticSize = Enum.AutomaticSize.X
	chip.LayoutOrder = 1
	UiKit.stroke(chip, 3, light)
	local chipPad = Instance.new("UIPadding")
	chipPad.PaddingLeft = UDim.new(0, 18)
	chipPad.PaddingRight = UDim.new(0, 18)
	chipPad.Parent = chip
	local chance = UiKit.text(chip, `{hatches[tier].chance}% CHANCE`, 24, light)
	chance.AutomaticSize = Enum.AutomaticSize.X
	chance.Size = UDim2.fromScale(0, 1)
	chance:FindFirstChildOfClass("UIStroke").Enabled = false
	local share = UiKit.text(row, `{special.share * 100}% OF YOUR BEST`, 32)
	share.AutomaticSize = Enum.AutomaticSize.X
	share.Size = UDim2.fromOffset(0, 44)
	share.LayoutOrder = 2
	ShopLook.paint(share, GOLD)

	local _, incomeSize, setIncome = ShopLook.words(reveal, "+$0/s", 56, 640, if jackpot then 574 else 558, UiKit.CASH)
	incomeSize.Scale = 0

	local blocked = player:GetAttribute("PaidRandomBlocked") == true
	local choice: string? = nil
	local again, againSize = popButton(reveal, if prismPrice then `OPEN ANOTHER   R$ {prismPrice}` else "OPEN ANOTHER", "green", 520, 655, 340, 70, 27)
	local nice, niceSize = popButton(reveal, "NICE!", "purple", if blocked then 640 else 820, 655, 220, 70, 30)
	again.Visible = not blocked
	local askedAt = -math.huge
	again.Activated:Connect(function()
		if os.clock() - askedAt > 1.5 then
			askedAt = os.clock()
			hooks.buyPrism()
		end
	end)
	nice.Activated:Connect(function()
		choice = "nice"
	end)

	local burstAt = if jackpot then look.jackpotBurstAt else look.burstAt
	local revealAt = burstAt + look.burst
	local buttonsAt = revealAt + look.buttonsAfter + (if jackpot then look.jackpotHold else 0)
	local trembleFrom = look.shakes[#look.shakes] + look.shakeLength
	local played: { [string]: boolean } = {}
	local function once(name: string): boolean
		if played[name] then
			return false
		end
		played[name] = true
		return true
	end
	local crack = 0
	local lastIncome = ""

	run(scene, function(t, dt)
		if scene.tapped then
			scene.tapped = false
			if t < burstAt then
				-- A tap skips to the reveal: none of the sounds on the way play late.
				scene.ahead += burstAt - t
				t = burstAt
				played.land = true
				for index in look.shakes do
					played[`shake{index}`] = true
				end
			end
		end

		scene.veil.BackgroundTransparency = 1 - look.veil * seg(t, 0, 0.3)

		-- The egg drops in, lands with a hop and a puff of dust.
		local fall = seg(t, 0, look.land * 0.7)
		local hop = seg(t, look.land * 0.7, look.land * 0.3)
		eggView.Position = UDim2.fromOffset(640, 338 - (1 - fall * fall) * 620 - math.sin(hop * math.pi) * 22)
		for _, streak in streaks do
			streak.Transparency = NumberSequence.new(1, 1 - 0.45 * (1 - fall) * seg(t, 0, 0.08))
		end
		if fall >= 1 and once("land") then
			sound("eggLand")
			scene.shake = 7
		end
		local settle = seg(t, look.land * 0.7, 0.45)
		for _, entry in puffs do
			local dust, puff = entry[1], entry[2]
			local size = puff[3] * (0.6 + 1.1 * settle)
			dust.Position = UDim2.fromOffset(640 + puff[1] * (0.55 + 0.6 * settle), puff[2])
			dust.Size = UDim2.fromOffset(size, size * 0.7)
			dust.ImageTransparency = if fall < 1 then 1 else 1 - 0.5 * (1 - settle)
		end

		-- Three shakes, each harder. The light climbs a tier per shake and stops at the real one.
		local level, tilt = 0, 0
		for index, at in look.shakes do
			if t >= at then
				level = math.min(index, tier)
				local v = seg(t, at, look.shakeLength)
				if v < 1 then
					tilt = math.sin(v * 4 * math.pi) * look.shakeTilt[index] * (1 - v)
				end
				if once(`shake{index}`) then
					sound("shake", 0.9 + 0.15 * index)
					scene.shake = 3 + 2 * index
				end
			end
		end
		local tremble = if jackpot then seg(t, trembleFrom, burstAt - trembleFrom) else 0
		if tremble > 0 and t < burstAt then
			tilt = math.sin(t * 60) * (2 + 6 * tremble)
			scene.shake = math.max(scene.shake, 2 + 5 * tremble)
		end
		local wanted = level / #look.shakes + 0.5 * tremble
		crack += (wanted - crack) * math.min(1, dt * 12)
		local burst = seg(t, burstAt, 0.55)
		local lit = lights[math.max(level, 1)]
		PrismEgg.pose(egg, if burst > 0 then 0 else tilt, crack, outCubic(burst), if burst > 0 then WHITE else lit)
		lookAt(t * 0.4)
		eggView.ImageTransparency = seg(t, burstAt + 0.2, 0.35)
		eggView.Visible = t < burstAt + 0.55

		local before = 1 - seg(t, burstAt, 0.1) -- what belongs to the egg goes as it bursts
		crackRays.ImageColor3 = lit
		crackRays.ImageTransparency = 1 - (0.4 + 0.3 * tremble) * math.min(level, 1) * seg(t, look.shakes[1], 0.2) * before
		crackGlow.ImageColor3 = lit
		crackGlow.ImageTransparency = 1 - math.min(0.28 * level + 0.3 * tremble, 0.9) * before
		floor.Visible = before > 0
		for index, entry in pips do
			local at = look.shakes[index]
			local on = level >= index
			local tried = t >= at and t < at + 0.18 -- a light the egg doesn't reach still flickers as it tries
			entry.pip.Visible = before > 0 and t >= look.land
			entry.pip.BackgroundColor3 = if on or tried then entry.colour else unlit
			entry.edge.Color = if on then WHITE else unlitEdge
			entry.size.Scale = if level == index then 1.3 else 1
			entry.halo.ImageTransparency = if level == index and before > 0 then 0.2 else 1
		end

		-- The burst.
		if t >= burstAt and once("burst") then
			sound("burst")
			scene.shake = if jackpot then 22 else 14
		end
		flash.BackgroundTransparency = if t < burstAt then 1 else seg(t, burstAt, 0.35)
		for index, entry in { { ringA, lineA, 0 }, { ringB, lineB, 0.06 } } do
			local u = seg(t, burstAt + entry[3], 0.45)
			local size = lerp(120, if index == 1 then 1500 else 1100, outCubic(u))
			entry[1].Size = UDim2.fromOffset(size, size)
			entry[2].Transparency = if u <= 0 or u >= 1 then 1 else u
		end

		-- The reveal.
		if t >= revealAt then
			if once("reveal") then
				reveal.Visible = true
				if jackpot then
					sound("jackpot")
				end
			end
			local shown = seg(t, revealAt, 0.3)
			rays.ImageTransparency = 1 - (if jackpot then 0.42 else 0.45) * shown
			glow.ImageTransparency = 1 - 0.65 * shown
			if gold then
				gold(0.55 * shown)
			end
			monsterSize.Scale = math.max(0.01, outBack(seg(t, revealAt, 0.45)))
			local titleIn = seg(t, revealAt + 0.15, 0.28)
			titleSize.Scale = slam(titleIn)
			if titleIn > 0 and once("title") then
				sound("slam")
				scene.shake = math.max(scene.shake, 5)
			end
			if sticker then
				local stamped = seg(t, revealAt + 0.45, 0.22)
				sticker.Scale = slam(stamped, 3)
				if stamped > 0 and once("sticker") then
					sound("slam", 1.2)
					scene.shake = math.max(scene.shake, 8)
				end
			end
			rowSize.Scale = math.max(0, outBack(seg(t, revealAt + 0.5, 0.25)))
			local counting = seg(t, revealAt + 0.7, 0.6)
			incomeSize.Scale = math.max(0, outBack(seg(t, revealAt + 0.7, 0.25)))
			local text = `+{Format.cash(moment.income * outCubic(counting))}/s`
			if text ~= lastIncome then
				lastIncome = text
				setIncome(text)
			end
			local buttons = math.max(0, outBack(seg(t, buttonsAt, 0.25)))
			againSize.Scale = buttons
			niceSize.Scale = buttons
		end
		-- NICE!, being left alone, or the next egg arriving ends it.
		return t >= buttonsAt and (choice ~= nil or t >= buttonsAt + look.closeAfter or #queue > 0)
	end)
	close(scene, if #queue > 0 then 0.12 else 0.25)
end

-- A GAME PASS MONSTER -----------------------------------------------------------------------------------------------

-- Back in the game: a red ring spreads once on the floor under the monster, if it's standing on the buyer's base.
local function floorRing(id: string)
	local look = ShopMoments.special.ring
	local plotIndex = player:GetAttribute("PlotIndex")
	for _, model in CollectionService:GetTagged(DinoLife.tag) do
		if model:IsA("Model") and model:IsDescendantOf(workspace) and model:GetAttribute("DinoId") == id and model:GetAttribute("PlotIndex") == plotIndex then
			local box = model:GetBoundingBox()
			local params = RaycastParams.new()
			params.FilterType = Enum.RaycastFilterType.Exclude
			params.FilterDescendantsInstances = { model }
			local hit = workspace:Raycast(box.Position, Vector3.new(0, -80, 0), params)
			if not hit then
				return
			end
			local plate = Instance.new("Part")
			plate.Name = "PurchaseRing"
			plate.Anchored = true
			plate.CanCollide = false
			plate.CanQuery = false
			plate.CanTouch = false
			plate.CastShadow = false
			plate.Transparency = 1
			plate.Size = Vector3.new(1, 0.1, 1)
			plate.CFrame = CFrame.new(hit.Position + Vector3.new(0, 0.12, 0))
			plate.Parent = workspace
			local surface = Instance.new("SurfaceGui")
			surface.Face = Enum.NormalId.Top
			surface.CanvasSize = Vector2.new(400, 400)
			surface.LightInfluence = 0
			surface.Parent = plate
			local circle = blank(surface, "Ring")
			circle.Position = UDim2.fromOffset(30, 30)
			circle.Size = UDim2.fromOffset(340, 340)
			ShopLook.round(circle, 0.5)
			local line = UiKit.stroke(circle, 26, hex(ShopMoments.special.colour))
			local start = os.clock()
			while true do
				local u = (os.clock() - start) / look.seconds
				if u >= 1 then
					break
				end
				local size = lerp(3, look.size, outCubic(u))
				plate.Size = Vector3.new(size, 0.1, size)
				line.Transparency = u * u
				RunService.RenderStepped:Wait()
			end
			plate:Destroy()
			return
		end
	end
end

local function playSpecial(moment)
	local look = ShopMoments.special
	local special = DinoStats.special(moment.id)
	if not special then
		return
	end
	hooks.closeShop() -- when the dark lifts, the game is there, not the Shop
	local red = hex(look.colour)
	local scene = newScene(special.name, true, hex("#050104"))
	local stage, fx = scene.stage, scene.fx
	local vignette = edges(scene.root, hex("#ff1f33"), 200 * scene.scale)

	local mist = ShopLook.image(stage, "glow", hex("#ff1f33"), 640, 340, 760, 420, 0)
	-- After the bite: rays and a glow behind it.
	local rays = fx.rays(stage, hex("#ff3b4f"), 640, 230, 820, 0)
	local glow = fx.glow(stage, red, 640, 230, 940, 680, 0)
	local emberLayer = blank(stage, "Embers")
	emberLayer.Size = UDim2.fromOffset(W, H)
	fx.embers(emberLayer, { { 250, 560, 7 }, { 1040, 480, 9 }, { 380, 300, 6 }, { 900, 260, 7 }, { 160, 420, 5 }, { 1120, 390, 6 }, { 520, 660, 6 }, { 820, 680, 7 } }, 240)

	-- Two eyes opening from slits in the dark.
	local eyes = {}
	for _, spec in { { 560, -14 }, { 720, 14 } } do
		local halo = ShopLook.image(stage, "glow", hex("#ff1f33"), spec[1], 336, 210, 130, 0)
		local eye = ShopLook.block(stage, "Eye", WHITE, spec[1], 336, 92, 2, 1, 13)
		eye.AnchorPoint = Vector2.new(0.5, 0.5)
		eye.Rotation = spec[2]
		ShopLook.paint(eye, { "#ff8a7a", "#ff1f33" })
		local glint = ShopLook.block(stage, "Glint", WHITE, spec[1] + (if spec[2] > 0 then -14 else 14), 332, 12, 8, 0, 0.5)
		glint.AnchorPoint = Vector2.new(0.5, 0.5)
		table.insert(eyes, { halo = halo, eye = eye, glint = glint })
	end

	local lines = ShopLook.image(stage, "speedLines", WHITE, 640, 380, 1900, 1900, 0)
	local monster, monsterSize = monsterView(stage, moment.id, 640, 215, 500, 430, math.rad(18))
	monster.Visible = false
	local flash = ShopLook.block(scene.root, "Red flash", hex("#ff3b4f"), 0, 0, 0, 0, 0)
	flash.Size = UDim2.fromScale(1, 1)
	flash.ZIndex = 3
	local slashes = {}
	for index, spec in { { -150, -10, 560 }, { 0, 30, 640 }, { 150, -10, 560 } } do
		local slash = ShopLook.block(stage, "Bite slash", WHITE, 640 + spec[1], 360 + spec[2], 26, 0, 1, 13)
		slash.AnchorPoint = Vector2.new(0.5, 0.5)
		slash.Rotation = 28
		slash.Visible = false
		local line = UiKit.stroke(slash, 5, hex("#ff1f33"))
		slashes[index] = { slash = slash, line = line, length = spec[3] }
	end

	for index, spot in { { 330, 130, 30 }, { 960, 90, 24 }, { 990, 330, 28 }, { 300, 340, 20 } } do
		fx.sparkle(stage, spot[1], spot[2], spot[3], index * 1.4).Visible = false
	end
	local _, nameSize = ShopLook.words(stage, string.upper(special.name), 112, 640, 436, { "#ffffff", "#ffc2c9" })
	nameSize.Scale = 0
	giftLine(stage, moment.from)
	local sticker = ribbon(stage, "IS YOURS FOREVER", "tagGold", 28, 640, 518, -2)
	local row, rowSize = popper(stage, "Share and income", 640, 580, 0, 52)
	row.AutomaticSize = Enum.AutomaticSize.X
	local rowLayout = Instance.new("UIListLayout")
	rowLayout.FillDirection = Enum.FillDirection.Horizontal
	rowLayout.VerticalAlignment = Enum.VerticalAlignment.Center
	rowLayout.Padding = UDim.new(0, 22)
	rowLayout.SortOrder = Enum.SortOrder.LayoutOrder
	rowLayout.Parent = row
	local share = UiKit.text(row, `{special.share * 100}% OF YOUR BEST`, 32)
	share.AutomaticSize = Enum.AutomaticSize.X
	share.Size = UDim2.fromScale(0, 1)
	share.LayoutOrder = 1
	ShopLook.paint(share, GOLD)
	local income = UiKit.text(row, "+$0/s", 40, UiKit.CASH)
	income.AutomaticSize = Enum.AutomaticSize.X
	income.Size = UDim2.fromScale(0, 1)
	income.LayoutOrder = 2
	local go, goSize = popButton(stage, "LET'S GO!", "green", 640, 662, 260, 68, 32)
	local done = false
	go.Activated:Connect(function()
		done = true
	end)

	local lungeAt = look.dark
	local biteAt = look.dark + look.bite * 0.6
	local yoursAt = look.dark + look.bite
	local buttonAt = yoursAt + look.buttonAfter
	local played: { [string]: boolean } = {}
	local function once(name: string): boolean
		if played[name] then
			return false
		end
		played[name] = true
		return true
	end
	local lastIncome = ""
	local sparkles = {}
	for _, child in stage:GetChildren() do
		if child.Name == "Sparkle" then
			table.insert(sparkles, child)
		end
	end

	run(scene, function(t)
		scene.tapped = false
		scene.veil.BackgroundTransparency = 1 - look.veil * seg(t, 0, 0.25)
		if once("dark") then
			sound("eyes")
		end
		-- Lights out: red edges, a red mist, the eyes open.
		vignette(lerp(0.3, 0.5, seg(t, lungeAt, look.bite * 0.6)) * seg(t, 0, 0.4) - 0.2 * seg(t, yoursAt, 0.5))
		mist.ImageTransparency = 1 - 0.22 * seg(t, 0.1, 0.4) * (1 - seg(t, lungeAt, 0.2))
		local opened = outCubic(seg(t, 0.25, 0.3)) * (1 - seg(t, lungeAt, 0.1))
		for _, entry in eyes do
			entry.eye.Size = UDim2.fromOffset(92, math.max(2, 26 * opened))
			entry.eye.BackgroundTransparency = if opened > 0 then 0 else 1
			entry.halo.ImageTransparency = 1 - opened * (0.75 + 0.15 * math.sin(t * 9))
			entry.glint.BackgroundTransparency = 1 - 0.9 * seg(opened, 0.6, 0.4)
		end

		-- It rushes at the camera, bites, then swims back and hangs there.
		if t >= lungeAt then
			monster.Visible = true
			local rush = seg(t, lungeAt, biteAt - lungeAt)
			local back = outCubic(seg(t, biteAt + 0.1, 0.4))
			local big = lerp(0.2, 3.6, rush * rush * rush)
			monsterSize.Scale = lerp(big, 1, back)
			monster.Position = UDim2.fromOffset(640, lerp(lerp(300, 420, rush), 215, back))
			lines.ImageTransparency = 1 - 0.3 * rush * (1 - seg(t, biteAt, 0.2))
			lines.Rotation = math.random(0, 3) * 90
		end
		if t >= biteAt and once("bite") then
			sound("bite")
			scene.shake = 24
		end
		flash.BackgroundTransparency = if t < biteAt then 1 else 1 - 0.75 * (1 - seg(t, biteAt, 0.35))
		for index, entry in slashes do
			local cut = seg(t, biteAt + (index - 1) * 0.03, 0.08)
			local gone = seg(t, biteAt + 0.2, 0.25)
			entry.slash.Visible = cut > 0 and gone < 1
			entry.slash.Size = UDim2.fromOffset(26, entry.length * cut)
			entry.slash.BackgroundTransparency = 0.05 + 0.95 * gone
			entry.line.Transparency = gone
		end

		-- It is yours.
		local shown = seg(t, biteAt + 0.15, 0.4)
		rays.ImageTransparency = 1 - 0.42 * shown
		glow.ImageTransparency = 1 - 0.6 * shown
		for _, star in sparkles do
			star.Visible = t >= yoursAt
		end
		local nameIn = seg(t, yoursAt + look.nameAfter, 0.28)
		nameSize.Scale = slam(nameIn)
		if nameIn > 0 and once("name") then
			sound("slam")
			scene.shake = math.max(scene.shake, 8)
		end
		local stamped = seg(t, yoursAt + look.ribbonAfter, 0.22)
		sticker.Scale = slam(stamped, 3)
		if stamped > 0 and once("ribbon") then
			sound("slam", 1.2)
		end
		local counted = seg(t, yoursAt + look.incomeAfter, 0.6)
		local pop = math.max(0, outBack(seg(t, yoursAt + look.incomeAfter, 0.25)))
		rowSize.Scale = pop
		local text = `+{Format.cash(moment.income * outCubic(counted))}/s`
		if text ~= lastIncome then
			lastIncome = text
			income.Text = text
		end
		goSize.Scale = math.max(0, outBack(seg(t, buttonAt, 0.25)))
		return t >= buttonAt and (done or t >= buttonAt + look.closeAfter)
	end)
	close(scene, 0.3)
	task.spawn(floorRing, moment.id)
end

-- A GAME PASS -------------------------------------------------------------------------------------------------------

local function playPass(moment)
	local look = ShopMoments.pass
	local style = look.looks[moment.key]
	local pass = nil
	for _, candidate in Gifts.passes do
		if candidate.key == moment.key then
			pass = candidate
		end
	end
	if not style or not pass then
		return
	end
	local colour, deep = hex(style.colours[1]), hex(style.colours[2])
	local scene = newScene("Pass unlocked", true)
	local stage, fx = scene.stage, scene.fx

	local rays = fx.rays(stage, colour, 640, 285, 760, 0)
	local glowDeep = fx.glow(stage, deep, 640, 285, 900, 700, 0)
	local glowLight = fx.glow(stage, WHITE, 640, 285, 520, 420, 0, 1)
	local confetti = fx.confetti(stage, look.confetti, { style.colours[1], "#ffffff", "#ffd23f" }, W, H, #moment.key)
	confetti.Visible = false
	local circle, line = ring(stage, 640, 285, WHITE, 8)
	local art, artSize = popper(stage, "Art", 572, 268, 300, 300)
	UiKit.art(art, pass.artKey, pass.art, { position = UDim2.new(), size = UDim2.fromScale(1, 1), yaw = math.rad(72) })
	local _, timesSize = ShopLook.words(stage, "x2", 170, 818, 272)
	timesSize.Scale = 0
	for index, spot in { { 330, 170, 30 }, { 960, 140, 24 }, { 990, 400, 28 }, { 300, 400, 20 } } do
		fx.sparkle(stage, spot[1], spot[2], spot[3], index * 1.4)
	end
	local _, labelSize = ShopLook.words(stage, style.label, 96, 640, 490, GOLD)
	labelSize.Scale = 0
	giftLine(stage, moment.from)
	local sticker = ribbon(stage, "UNLOCKED FOREVER", "tagGold", 30, 640, 590, -2)
	Sfx.play("powerUp")

	local played = false
	run(scene, function(t)
		local shown = seg(t, 0, 0.25)
		scene.veil.BackgroundTransparency = 1 - look.veil * shown
		rays.ImageTransparency = 1 - 0.5 * shown
		glowDeep.ImageTransparency = 1 - 0.45 * shown
		glowLight.ImageTransparency = 1 - 0.5 * shown
		confetti.Visible = t > 0.2
		-- The art spins in and lands with a bounce, x2 slams beside it, the word, then the ribbon stamps on.
		local landed = seg(t, 0.05, 0.45)
		artSize.Scale = math.max(0, outBack(landed))
		art.Rotation = -200 * (1 - outCubic(landed))
		local grown = seg(t, 0.1, 0.6)
		local size = lerp(160, 620, outCubic(grown))
		circle.Size = UDim2.fromOffset(size, size)
		line.Transparency = if grown <= 0 then 1 else 0.3 + 0.7 * grown
		local slammed = seg(t, 0.3, 0.25)
		timesSize.Scale = slam(slammed)
		if slammed > 0 and not played then
			played = true
			sound("slam")
			scene.shake = 7
		end
		labelSize.Scale = math.max(0, outBack(seg(t, 0.5, 0.25)))
		sticker.Scale = slam(seg(t, 0.75, 0.22), 3)
		return t >= look.seconds - 0.3 or (scene.tapped and t >= look.minimum)
	end)
	close(scene, 0.3)
end

-- CASH, POWER AND LUCK: A QUICK POP ---------------------------------------------------------------------------------

local function hudPart(guiName: string, childName: string): GuiObject?
	local playerGui = player:FindFirstChild("PlayerGui")
	local found = playerGui and playerGui:FindFirstChild(guiName)
	local child = found and found:FindFirstChild(childName)
	return if child and child:IsA("GuiObject") then child else nil
end

-- One thing that flies to the counter: a coin, a spark or a clover, `size` design pixels across.
local function flyer(parent: Instance, kind: string, size: number): GuiObject
	local piece: GuiObject
	if kind == "cash" then
		piece = ShopLook.block(parent, "Coin", WHITE, 0, 0, size, size, 1, 0.5)
		ShopLook.paint(piece, GOLD)
		UiKit.stroke(piece, math.max(2, size * 0.1))
		local shine = ShopLook.block(piece, "Shine", WHITE, 0, 0, 0, 0, 0.8, 0.5)
		shine.Position = UDim2.fromScale(0.2, 0.18)
		shine.Size = UDim2.fromScale(0.32, 0.22)
	elseif kind == "power" then
		piece = ShopLook.block(parent, "Spark", WHITE, 0, 0, size * 0.7, size * 0.7, 1, 4)
		piece.Rotation = 45
		ShopLook.paint(piece, GOLD, 45)
		UiKit.stroke(piece, 3)
	else
		local holder = blank(parent, "Clover")
		holder.Size = UDim2.fromOffset(size, size)
		UiKit.art(holder, "clover", "clover", { position = UDim2.new(), size = UDim2.fromScale(1, 1), yaw = math.rad(72) })
		piece = holder
	end
	piece.AnchorPoint = Vector2.new(0.5, 0.5)
	piece.Visible = false
	local scale = Instance.new("UIScale")
	scale.Name = "Size"
	scale.Parent = piece
	return piece
end

local function playPop(moment)
	local look = ShopMoments.pop
	local kind = moment.kind
	local colour, artKey, title, titleColours, detail, target, pieceKind, count, arriveSound
	if kind == "cash" then
		colour, artKey, pieceKind, count = look.colours.cash, moment.art or "cash_L", "cash", look.pieces.cash
		title, titleColours = `+{Format.cash(moment.amount)}`, UiKit.CASH
		target, arriveSound = hudPart("PlotHud", "CashStat"), "cash"
	elseif kind == "power" then
		colour, artKey, pieceKind, count = look.colours.power, moment.art or "bolts_L", "power", look.pieces.power
		title, titleColours = `+{Format.commas(moment.amount)} POWER`, GOLD
		target, arriveSound = hudPart("TrainingHud", "PowerStat"), "powerUp"
	elseif kind == "luck" then
		local big = moment.multiplier >= 500
		colour, artKey, pieceKind, count = if big then look.colours.luck500 else look.colours.luck100, "clover", "luck", look.pieces.luck
		title, titleColours = `x{moment.multiplier} LUCK`, if big then GOLD else { "#ffffff", "#dcb0ff" }
		detail = `+{moment.amount or 1} THROW`
		target, arriveSound = hudPart("BoostHud", "Corner"), "discovery"
	else
		colour, artKey, pieceKind, count = look.colours.serverLuck, "clover", "luck", look.pieces.luck
		title, titleColours = `x{Shop.serverLuck.multiplier} SERVER LUCK`, { "#ffffff", "#b8ff8a" }
		detail = `+{Shop.serverLuck.seconds // 60} MIN`
		target, arriveSound = hudPart("BoostHud", "Corner"), "discovery"
	end

	local scene = newScene("Quick pop", false)
	local root, stage, s = scene.root, scene.stage, scene.scale
	local glowEdges = edges(root, hex(colour), 130 * s)
	local flash = ShopLook.image(stage, "glow", WHITE, 640, 205, 520, 520, 0)
	local circle, line = ring(stage, 640, 205, WHITE, 12)
	local art, artSize = popper(stage, "Art", 640, 200, 210, 210)
	UiKit.art(art, artKey, artKey, { position = UDim2.new(), size = UDim2.fromScale(1, 1), yaw = math.rad(72) })
	local words = blank(stage, "Words")
	words.Size = UDim2.fromOffset(W, H)
	local _, titleSize = ShopLook.words(words, title, 104, 640, 356, titleColours)
	titleSize.Scale = 0
	if moment.from then
		detail = `A GIFT FROM {string.upper(moment.from)}`
	end
	local detailSize: UIScale? = nil
	if detail then
		local _, size = ShopLook.words(words, detail, 36, 640, 440, GOLD)
		size.Scale = 0
		detailSize = size
	end

	-- Where it flies from and to, in screen pixels.
	local screen = workspace.CurrentCamera.ViewportSize
	local from = screen / 2 + Vector2.new(0, 205 - H / 2) * s
	local to = from + Vector2.new(0, 400 * s)
	if target then
		local corner = target.AbsolutePosition - root.AbsolutePosition
		to = corner + Vector2.new(math.min(target.AbsoluteSize.X, target.AbsoluteSize.Y * 1.5), target.AbsoluteSize.Y) / 2
	end
	local control = Vector2.new(lerp(from.X, to.X, 0.75), from.Y - 90 * s)
	local arrival = ShopLook.image(root, "glow", hex(colour), to.X, to.Y, 320 * s, 320 * s, 0)
	local flyers = {}
	for index = 1, count do
		local piece = flyer(root, pieceKind, (if pieceKind == "luck" then 54 else 38) * s)
		flyers[index] = { piece = piece, size = piece:FindFirstChild("Size") :: UIScale, bend = Vector2.new((index % 3 - 1) * 60, (index % 2) * 50) * s }
	end

	Sfx.play("purchase")
	local flyAt = look.burst * 0.7
	local flight = look.seconds - flyAt - (count - 1) * 0.04
	local fadeWords: ((number) -> ())? = nil
	local arrived = false
	run(scene, function(t)
		-- It pops: a flash, a ring, the art, the amount slamming in, the screen's edges glowing.
		glowEdges(0.5 * seg(t, 0, 0.08) * (1 - seg(t, look.burst, look.seconds - look.burst)))
		flash.ImageTransparency = 1 - 0.9 * seg(t, 0, 0.05) * (1 - seg(t, 0.05, 0.4))
		local grown = seg(t, 0, 0.45)
		local size = lerp(140, 520, outCubic(grown))
		circle.Size = UDim2.fromOffset(size, size)
		line.Transparency = if grown >= 1 then 1 else 0.1 + 0.9 * grown
		artSize.Scale = math.max(0, outBack(seg(t, 0, 0.2))) * (1 - seg(t, look.burst + 0.1, 0.25))
		titleSize.Scale = slam(seg(t, 0.06, 0.22), 2.2)
		if detailSize then
			detailSize.Scale = math.max(0, outBack(seg(t, 0.2, 0.2)))
		end
		-- Then the words drift up and fade while it flies into its counter.
		local drift = seg(t, look.burst + 0.15, 0.55)
		if drift > 0 then
			fadeWords = fadeWords or ShopLook.fader(words)
			local fade = fadeWords :: (number) -> ()
			fade(1 - drift)
			words.Position = UDim2.fromOffset(0, -50 * drift)
		end
		for index, entry in flyers do
			local u = seg(t, flyAt + (index - 1) * 0.04, flight)
			entry.piece.Visible = u > 0 and u < 1
			local e = u * u * (3 - 2 * u)
			local bend = control + entry.bend
			local point = from:Lerp(bend, e):Lerp(bend:Lerp(to, e), e)
			entry.piece.Position = UDim2.fromOffset(point.X, point.Y)
			entry.size.Scale = 1 - 0.5 * e
		end
		local landing = flyAt + flight
		if t >= landing and not arrived then
			arrived = true
			Sfx.play(arriveSound)
			if target then
				PopText.punch(target)
			end
		end
		arrival.ImageTransparency = if t < landing then 1 else 1 - 0.85 * (1 - seg(t, landing, 0.35))
		return t >= look.seconds + 0.35
	end)
	scene.root:Destroy()
end

-- THE QUEUE ---------------------------------------------------------------------------------------------------------

local players = { prism = playPrism, special = playSpecial, pass = playPass }
local busy = false

-- The moments that take the screen play one after the other.
local function drain()
	busy = true
	while #queue > 0 do
		local moment = table.remove(queue, 1)
		local ok, problem = xpcall(players[moment.kind], debug.traceback, moment)
		if not ok then
			warn(`[PurchaseMoments] {moment.kind}: {problem}`)
			for _, child in layer():GetChildren() do
				if child.Name ~= "Quick pop" and child.Name ~= "Loaded pictures" then
					child:Destroy() -- never leave a veil over the game
				end
			end
		end
	end
	busy = false
end

-- Plays a moment: { kind = "prism" | "special" | "pass" | "cash" | "power" | "luck" | "serverLuck", ... } as
-- ShopService sends it.
function PurchaseMoments.play(moment)
	if typeof(moment) ~= "table" then
		return
	end
	if players[moment.kind] then
		table.insert(queue, moment)
		if not busy then
			task.spawn(drain)
		end
	elseif moment.kind == "cash" or moment.kind == "power" or moment.kind == "luck" or moment.kind == "serverLuck" then
		task.spawn(function()
			local ok, problem = xpcall(playPop, debug.traceback, moment)
			if not ok then
				warn(`[PurchaseMoments] {moment.kind}: {problem}`)
			end
		end)
	end
end

-- lent: closeShop (hides the Shop panel) and buyPrism (asks for another Prism Egg), from ShopController.
function PurchaseMoments.start(remote: RemoteEvent, lent: { closeShop: () -> (), buyPrism: () -> () })
	hooks = lent
	remote.OnClientEvent:Connect(PurchaseMoments.play)
	local ids = {}
	for _, found in ShopMoments.sounds do
		table.insert(ids, found.id)
	end
	SoundPool.preload(ids)
	-- The pictures the moments use stay loaded: each sits in the layer as a nearly see-through dot. A picture first
	-- shown as its moment starts would still be loading while a quick pop is already over.
	local warm = blank(layer(), "Loaded pictures")
	warm.Size = UDim2.fromOffset(1, 1)
	local wanted = { "clover" }
	for _, pass in Gifts.passes do
		table.insert(wanted, pass.artKey)
	end
	for _, packs in { Shop.cashPacks, Shop.powerPacks } do
		for _, pack in packs do
			table.insert(wanted, pack.art)
		end
	end
	for _, key in wanted do
		local picture = UiKit.iconImage(warm, key, {})
		if picture then
			picture.ImageTransparency = 0.99
		end
	end
	for key in ShopMoments.images do
		ShopLook.image(warm, key, WHITE, 0, 0, 1, 1, 0.01)
	end
	if Shop.prismEgg.productId ~= 0 then
		task.spawn(function()
			local ok, info = pcall(function()
				return MarketplaceService:GetProductInfo(Shop.prismEgg.productId, Enum.InfoType.Product)
			end)
			if ok and info.PriceInRobux then
				prismPrice = info.PriceInRobux
			end
		end)
	end
end

return PurchaseMoments
