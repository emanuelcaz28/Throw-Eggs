-- Ready pop-ups (Config/ReadyPopup, Figma "Throw Eggs - Tutorial" Ready Pop-up): a card at the top of the screen when
-- the player can afford the next squat rack upgrade (UPGRADE buys it from anywhere) or the next egg (SHOP opens the
-- Egg Shop from anywhere). Each card shows once per upgrade or egg, one at a time, never during the tutorial or a
-- throw. Display and requests only: the server checks the price (TrainingService BuyUpgrade, EggService).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")

local Eggs = require(ReplicatedStorage.Shared.Config.Eggs)
local Format = require(ReplicatedStorage.Shared.Format)
local ReadyPopup = require(ReplicatedStorage.Shared.Config.ReadyPopup)
local Training = require(ReplicatedStorage.Shared.Config.Training)
local Tutorial = require(ReplicatedStorage.Shared.Config.Tutorial)
local UiKit = require(ReplicatedStorage.Shared.UiKit)
local EggShopController = require(script.Parent.EggShopController)

local player = Players.LocalPlayer

local ReadyPopupController = {}

local CHECK_INTERVAL = 0.5
local TOUCH = UserInputService.TouchEnabled and not UserInputService.KeyboardEnabled
local HEADER = if TOUCH then 76 else 56 -- design px; phones get a bigger X (memory mobile-ui-pitfalls)
local CLOSE = if TOUCH then 64 else 40
local BODY = 128
local TIMER = 6
local FOOT = 14 -- design px under the body for the timer bar
local ROUND = 26
local TILE = 96

type Offer = {
	key: string,
	kind: "rack" | "egg",
	title: string,
	item: string,
	detail: string,
	button: string,
	colour: Color3?, -- the egg's colour
}

local function attr(name: string): any
	return player:GetAttribute(name)
end

-- The rack upgrade the player can afford now, or nil.
local function rackOffer(): Offer?
	local price, upgrades, cash = attr("XpUpgradePrice"), attr("XpUpgrades"), attr("Cash")
	if typeof(price) ~= "number" or typeof(upgrades) ~= "number" or typeof(cash) ~= "number" or cash < price then
		return nil
	end
	local config = ReadyPopup.rack
	local now, after = Training.rackFor(upgrades), Training.rackFor(upgrades + 1)
	local perRep = attr("NextXpPerRep")
	local detail = Format.cash(price)
	if typeof(perRep) == "number" then
		-- Worded like the upgrade pad (TrainingController).
		detail ..= `   +{if perRep % 1 == 0 then Format.short(perRep) else string.format("%.1f", perRep)} XP per squat`
	end
	return {
		key = `rack:{upgrades}`,
		kind = "rack",
		title = if after ~= now then config.newRackTitle else config.title,
		item = `{string.upper(after.name)}  LV {upgrades + 1}`,
		detail = detail,
		button = config.button,
	}
end

-- The next egg in the shop, if the player can afford it now, or nil.
local function eggOffer(): Offer?
	local cash = attr("Cash")
	if typeof(cash) ~= "number" or next(EggShopController.owned) == nil then
		return nil -- not loaded yet
	end
	for _, egg in Eggs do
		if not EggShopController.owned[egg.id] then
			if cash < egg.price then
				return nil
			end
			return {
				key = `egg:{egg.id}`,
				kind = "egg",
				title = ReadyPopup.egg.title,
				item = string.upper(egg.name),
				detail = `{Format.cash(egg.price)}   x{egg.luckBonus} luck`,
				button = ReadyPopup.egg.button,
				colour = egg.color,
			}
		end
	end
	return nil
end

-- A squat rack drawn from frames (Figma Icon Tile): two posts and a yolk bar with plates.
local function drawRack(tile: Frame)
	local function bar(x: number, y: number, w: number, h: number, colour: Color3, round: number)
		local part = Instance.new("Frame")
		part.Position = UDim2.fromOffset(x, y)
		part.Size = UDim2.fromOffset(w, h)
		part.BackgroundColor3 = colour
		part.Parent = tile
		UiKit.corner(part, round)
		UiKit.stroke(part, 3)
	end
	bar(20, 22, 10, 60, Color3.fromRGB(233, 228, 255), 2)
	bar(66, 22, 10, 60, Color3.fromRGB(233, 228, 255), 2)
	bar(10, 34, 76, 8, UiKit.color("FFC93C"), 4)
	bar(6, 28, 10, 20, Color3.fromRGB(59, 51, 85), 3)
	bar(80, 28, 10, 20, Color3.fromRGB(59, 51, 85), 3)
end

local function drawEgg(tile: Frame, colour: Color3)
	local egg = Instance.new("Frame")
	egg.AnchorPoint = Vector2.new(0.5, 0.5)
	egg.Position = UDim2.fromScale(0.5, 0.52)
	egg.Size = UDim2.fromOffset(56, 70)
	egg.Parent = tile
	UiKit.gradient(egg, { colour:Lerp(Color3.new(1, 1, 1), 0.45):ToHex(), colour:ToHex() })
	local round = Instance.new("UICorner")
	round.CornerRadius = UDim.new(0.5, 0)
	round.Parent = egg
	UiKit.stroke(egg, 4)
end

local function buildCard(gui: ScreenGui)
	local width = ReadyPopup.width
	local card = Instance.new("Frame")
	card.Name = "ReadyCard"
	card.AnchorPoint = Vector2.new(0.5, 0)
	card.Size = UDim2.fromOffset(width, HEADER + BODY + FOOT)
	card.BackgroundColor3 = UiKit.PANEL
	card.Visible = false
	card.Parent = gui
	UiKit.corner(card, ROUND)
	UiKit.stroke(card, 5)
	local scale = Instance.new("UIScale")
	scale.Parent = card

	-- The header's top corners follow the card; a square strip under its rounded bottom corners carries on the same
	-- gradient, so the header meets the body in a straight line. (No CanvasGroup: one hides ViewportFrames drawn
	-- after it, memory viewport-canvasgroup-pitfall.)
	local header = Instance.new("Frame")
	header.Name = "Header"
	header.Size = UDim2.new(1, 0, 0, HEADER)
	header.BorderSizePixel = 0
	header.BackgroundColor3 = Color3.new(1, 1, 1)
	header.Parent = card
	UiKit.corner(header, ROUND)
	local headerGradient = Instance.new("UIGradient")
	headerGradient.Rotation = 90
	headerGradient.Parent = header
	local foot = Instance.new("Frame")
	foot.Name = "HeaderFoot"
	foot.Position = UDim2.fromOffset(0, HEADER - ROUND)
	foot.Size = UDim2.new(1, 0, 0, ROUND)
	foot.BorderSizePixel = 0
	foot.BackgroundColor3 = Color3.new(1, 1, 1)
	foot.Parent = card
	local footGradient = Instance.new("UIGradient")
	footGradient.Rotation = 90
	footGradient.Parent = foot
	header.ZIndex = 2 -- over the strip, so the title and X sit on top
	local title = UiKit.text(header, "", 26, nil, Enum.TextXAlignment.Left)
	title.Position = UDim2.fromOffset(20, 0)
	title.Size = UDim2.new(1, -40 - CLOSE, 1, 0)
	local close = UiKit.button(header, "X", "red", CLOSE, CLOSE, if TOUCH then 36 else 24)
	close.Name = "Close"
	close.AnchorPoint = Vector2.new(1, 0.5)
	close.Position = UDim2.new(1, -10, 0.5, 0)

	local tile = Instance.new("Frame")
	tile.Name = "IconTile"
	tile.Position = UDim2.fromOffset(16, HEADER + (BODY - TILE) / 2)
	tile.Size = UDim2.fromOffset(TILE, TILE)
	tile.Parent = card
	UiKit.corner(tile, 18)
	UiKit.stroke(tile, 4)

	local actionWidth = 150
	local infoX = 16 + TILE + 16
	local infoWidth = width - infoX - actionWidth - 32
	local function line(value: string, y: number, height: number, size: number, colour: Color3?, muted: boolean?)
		local label = if muted
			then UiKit.muted(card, value, size, Enum.TextXAlignment.Left)
			else UiKit.text(card, value, size, colour, Enum.TextXAlignment.Left)
		label.Position = UDim2.fromOffset(infoX, HEADER + y)
		label.Size = UDim2.fromOffset(infoWidth, height)
		label.TextScaled = not muted
		label.TextWrapped = false
		local limit = Instance.new("UITextSizeConstraint")
		limit.MaxTextSize = size
		limit.Parent = label
		return label
	end
	local lead = line("", 18, 24, 18, nil, true)
	local item = line("", 42, 38, 30, UiKit.GOLD)
	local detail = line("", 82, 28, 20, UiKit.CASH)

	local action = UiKit.button(card, "", "green", actionWidth, 60, 24)
	action.Name = "Action"
	action.AnchorPoint = Vector2.new(1, 0.5)
	action.Position = UDim2.new(1, -16, 0, HEADER + BODY / 2)

	-- Inset from the rounded bottom corners, so it needs no clipping.
	local timer = Instance.new("Frame")
	timer.Name = "Timer"
	timer.AnchorPoint = Vector2.new(0, 1)
	timer.Position = UDim2.new(0, ROUND, 1, -(FOOT - TIMER) / 2)
	timer.Size = UDim2.new(1, -2 * ROUND, 0, TIMER)
	timer.BorderSizePixel = 0
	timer.BackgroundColor3 = UiKit.color("FFC93C")
	timer.Parent = card
	UiKit.corner(timer, TIMER // 2)

	return {
		frame = card,
		scale = scale,
		headerGradient = headerGradient,
		footGradient = footGradient,
		title = title,
		close = close,
		tile = tile,
		lead = lead,
		item = item,
		detail = detail,
		action = action,
		timer = timer,
	}
end

local function fill(card, offer: Offer)
	local config = if offer.kind == "rack" then ReadyPopup.rack else ReadyPopup.egg
	local top, bottom = UiKit.color(config.header[1]), UiKit.color(config.header[2])
	card.headerGradient.Color = ColorSequence.new(top, bottom)
	card.footGradient.Color = ColorSequence.new(top:Lerp(bottom, (HEADER - ROUND) / HEADER), bottom)
	card.title.Text = offer.title
	card.lead.Text = config.lead
	card.item.Text = offer.item
	card.detail.Text = offer.detail
	card.action.Text = offer.button
	for _, child in card.tile:GetChildren() do
		if child:IsA("GuiObject") then
			child:Destroy()
		end
	end
	local tileGradient = card.tile:FindFirstChildOfClass("UIGradient")
	if tileGradient then
		tileGradient:Destroy()
	end
	if offer.kind == "rack" then
		UiKit.gradient(card.tile, ReadyPopup.rack.tile)
		drawRack(card.tile)
	else
		local colour = offer.colour or UiKit.GOLD
		UiKit.gradient(card.tile, { colour:Lerp(UiKit.PANEL, 0.55):ToHex(), colour:Lerp(UiKit.PANEL, 0.8):ToHex() })
		drawEgg(card.tile, colour)
	end
end

-- The card's size on this screen: design px scaled like the rest of the UI, bigger on touch screens, and never
-- wider than maxScreenShare of the screen.
local function cardScale(): number
	local scale = UiKit.scale() * (if TOUCH then ReadyPopup.touchBoost else 1)
	local widest = UiKit.screenSize().X * ReadyPopup.maxScreenShare / ReadyPopup.width
	return math.min(scale, widest)
end

function ReadyPopupController.start()
	local gui = Instance.new("ScreenGui")
	gui.Name = "ReadyPopupHud" -- ThrowController hides it while throwing (setHudsEnabled)
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 0 -- under the panels, so it never covers a panel's X
	gui.Parent = player:WaitForChild("PlayerGui")
	local card = buildCard(gui)
	local remotes = ReplicatedStorage:WaitForChild("TrainingRemotes")

	local shown: { [string]: boolean } = {} -- cards already shown this visit, by key
	local current: Offer? = nil
	local token = 0 -- the card on screen; a newer card or a close makes older timers stand down
	local lastClosed = 0
	local priceSince = os.clock() -- when the rack price last changed (buying on the pad)
	local readyAt = os.clock() + ReadyPopup.firstDelay

	local function hide()
		if not current then
			return
		end
		current = nil
		token += 1
		lastClosed = os.clock()
		local top = ReadyPopup.top * card.scale.Scale
		local away = TweenService:Create(card.frame, TweenInfo.new(0.2, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {
			Position = UDim2.new(0.5, 0, 0, -card.frame.AbsoluteSize.Y - top),
		})
		local mine = token
		away.Completed:Connect(function()
			if token == mine then
				card.frame.Visible = false
			end
		end)
		away:Play()
	end

	local function show(offer: Offer)
		current = offer
		shown[offer.key] = true
		token += 1
		local mine = token
		fill(card, offer)
		local scale = cardScale()
		card.scale.Scale = scale
		local height = (HEADER + BODY + FOOT) * scale
		card.frame.Position = UDim2.new(0.5, 0, 0, -height - 10)
		card.frame.Visible = true
		TweenService:Create(card.frame, TweenInfo.new(0.35, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {
			Position = UDim2.new(0.5, 0, 0, ReadyPopup.top * scale),
		}):Play()
		card.timer.Size = UDim2.new(1, -2 * ROUND, 0, TIMER)
		TweenService:Create(card.timer, TweenInfo.new(ReadyPopup.showFor, Enum.EasingStyle.Linear), {
			Size = UDim2.new(0, 0, 0, TIMER),
		}):Play()
		task.delay(ReadyPopup.showFor, function()
			if token == mine then
				hide()
			end
		end)
	end

	card.close.Activated:Connect(hide)
	card.action.Activated:Connect(function()
		local offer = current
		if not offer then
			return
		end
		if offer.kind == "rack" then
			remotes.BuyUpgrade:FireServer()
		else
			EggShopController.open()
		end
		hide()
	end)

	player:GetAttributeChangedSignal("XpUpgradePrice"):Connect(function()
		priceSince = os.clock()
	end)

	local function tutorialDone(): boolean
		local step = attr("TutorialStep")
		return typeof(step) == "number" and step >= Tutorial.doneStep
	end

	while true do
		task.wait(CHECK_INTERVAL)
		local now = os.clock()
		if current then
			-- A card that's no longer true goes (bought on the pad, or the cash was spent). One a panel opened over
			-- goes too, and comes back once the panels are closed, so it's never missed behind one.
			local still = if current.kind == "rack" then rackOffer() else eggOffer()
			if not still or still.key ~= current.key then
				hide()
			elseif UiKit.anyPanelOpen() then
				shown[current.key] = nil
				hide()
			end
		elseif gui.Enabled and now >= readyAt and now - lastClosed >= ReadyPopup.gap and tutorialDone() and not UiKit.anyPanelOpen() then
			local rack = rackOffer()
			-- A player buying upgrade after upgrade on the pad gets no card until they stop for a moment.
			if rack and not shown[rack.key] and now - priceSince >= ReadyPopup.settle then
				show(rack)
			else
				local egg = eggOffer()
				if egg and not shown[egg.key] then
					show(egg)
				end
			end
		end
	end
end

return ReadyPopupController
