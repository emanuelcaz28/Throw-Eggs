-- The row of icons at the bottom of the screen, one for everything active right now: the timed event, Server Luck,
-- the x2 XP and each kind of lucky throw owned (Figma "Throw Eggs - Pop-up Text", "Active boosts"). Timed boosts
-- show a clock under the icon, lucky throws how many are left. Hovering an icon (PC) or tapping it (phone) opens
-- a card saying what it does. Display only: the server applies every boost.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")

local Boosts = require(ReplicatedStorage.Shared.Config.Boosts)
local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local Events = require(ReplicatedStorage.Shared.Config.Events)
local Format = require(ReplicatedStorage.Shared.Format)
local Index = require(ReplicatedStorage.Shared.Config.Index)
local LuckyThrows = require(ReplicatedStorage.Shared.LuckyThrows)
local Shop = require(ReplicatedStorage.Shared.Config.Shop)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local BoostRowController = {}

local ICON = 84 -- design pixels
local SLOT = Vector2.new(ICON + 12, ICON + 34)
local STRIDE = 100 -- from one icon to the next
local MARGIN = 16
-- On touch screens, lifted above the jump button in the bottom right. Roblox makes that button smaller and lower
-- on phones (screens 500 points or less on their short side) than on tablets; 190 on a phone put the icon on
-- the Dinos button.
local TOUCH_LIFT = 120
local PHONE_LIFT = 40
local MOUSE_LIFT = 50 -- design pixels: low enough to sit by the Monsters and Daily buttons, clear of the hotbar on the right
local CARD_GAP = 14
local TOUCH_CARD_WIDTH = 360
-- A card stays this far from the right of the row, clear of the Daily and Monsters buttons. Only the rightmost
-- icon's card goes further, to stay over its icon.
local CARD_INSET = 110
local SLIDE_SECONDS = 0.2
local TAP_WINDOW = 0.15 -- seconds: a tap that hit no icon in this time closes the card

local function isTouch(): boolean
	return UserInputService.TouchEnabled and not UserInputService.MouseEnabled
end

local function clock(seconds: number): string
	seconds = math.max(math.ceil(seconds), 0)
	return string.format("%d:%02d", seconds // 60, seconds % 60)
end

local function label(parent: Instance, size: number, color: Color3, stroke: number?): TextLabel
	local text = Instance.new("TextLabel")
	text.BackgroundTransparency = 1
	text.FontFace = UiKit.FONT
	text.TextSize = size
	text.TextColor3 = color
	text.TextXAlignment = Enum.TextXAlignment.Left
	text.AutomaticSize = Enum.AutomaticSize.XY
	text.Size = UDim2.new()
	text.Parent = parent
	if stroke then
		local outline = Instance.new("UIStroke")
		outline.Color = UiKit.INK
		outline.Thickness = stroke
		outline.LineJoinMode = Enum.LineJoinMode.Round
		outline.Parent = text
	end
	return text
end

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "BoostHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.Parent = player:WaitForChild("PlayerGui")

	-- Everything hangs from the bottom-right corner, sized in design pixels and scaled with the screen.
	local corner = Instance.new("Frame")
	corner.Name = "Corner"
	corner.BackgroundTransparency = 1
	corner.AnchorPoint = Vector2.new(1, 1)
	corner.Size = UDim2.fromOffset(SLOT.X, SLOT.Y)
	corner.Visible = false
	corner.Parent = gui
	local scale = Instance.new("UIScale")
	scale.Parent = corner

	-- The card has its own layer, so the rightmost icon's card opens over the Monsters button while the icons stay
	-- under every panel. cardCorner sits exactly on corner.
	local cardGui = Instance.new("ScreenGui")
	cardGui.Name = "BoostCardHud"
	cardGui.ResetOnSpawn = false
	cardGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	cardGui.DisplayOrder = 2
	cardGui.Parent = gui.Parent
	local cardCorner = corner:Clone()
	cardCorner.Visible = true
	cardCorner.Parent = cardGui
	local cardScale = cardCorner:FindFirstChildOfClass("UIScale")

	-- The card over the icon: what it does, and how long is left or how many.
	local card = Instance.new("Frame")
	card.Name = "Card"
	card.AnchorPoint = Vector2.new(1, 1)
	card.BackgroundColor3 = UiKit.PANEL
	card.Visible = false
	card.ZIndex = 2
	card.Parent = cardCorner
	UiKit.corner(card, 18)
	UiKit.stroke(card, 4)
	local cardPad = Instance.new("UIPadding")
	cardPad.PaddingLeft, cardPad.PaddingRight = UDim.new(0, 18), UDim.new(0, 18)
	cardPad.PaddingTop, cardPad.PaddingBottom = UDim.new(0, 12), UDim.new(0, 14)
	cardPad.Parent = card
	local list = Instance.new("UIListLayout")
	list.Padding = UDim.new(0, 4)
	list.SortOrder = Enum.SortOrder.LayoutOrder
	list.Parent = card
	local title = label(card, 34, Color3.new(1, 1, 1), 4)
	title.LayoutOrder = 1
	local what = label(card, 22, UiKit.TEXT)
	what.LayoutOrder = 2
	local when = label(card, 18, UiKit.MUTED)
	when.LayoutOrder = 3
	-- Phones have less room, so there the card keeps one width and its lines wrap.
	if isTouch() then
		card.Size = UDim2.fromOffset(TOUCH_CARD_WIDTH, 0)
		card.AutomaticSize = Enum.AutomaticSize.Y
		for _, line in { title, what, when } do
			line.Size = UDim2.fromScale(1, 0)
			line.AutomaticSize = Enum.AutomaticSize.Y
			line.TextWrapped = true
		end
	else
		card.AutomaticSize = Enum.AutomaticSize.XY
	end

	-- The point under the card: a square turned on its corner, with its top half hidden behind the card.
	local nub = Instance.new("Frame")
	nub.Name = "Nub"
	nub.AnchorPoint = Vector2.new(0.5, 0.5)
	nub.Size = UDim2.fromOffset(18, 18)
	nub.Rotation = 45
	nub.BackgroundColor3 = UiKit.PANEL
	nub.BorderSizePixel = 0
	nub.Visible = false
	nub.Parent = cardCorner

	local function place()
		local viewport = workspace.CurrentCamera.ViewportSize
		local phone = math.min(viewport.X, viewport.Y) <= 500
		scale.Scale = UiKit.scale()
		cardScale.Scale = scale.Scale
		local lift = if isTouch() then (if phone then PHONE_LIFT else TOUCH_LIFT) else MOUSE_LIFT * scale.Scale
		corner.Position = UDim2.new(1, -MARGIN, 1, -MARGIN - lift)
		cardCorner.Position = corner.Position
	end
	place()
	workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(place)

	return { corner = corner, scale = scale, card = card, nub = nub, title = title, what = what, when = when }
end

-- One icon with its pill. boost.art says what goes inside: a block clover, the bolt, or an emoji.
local function buildSlot(parent: Instance, boost)
	local slot = Instance.new("Frame")
	slot.Name = boost.id
	slot.BackgroundTransparency = 1
	slot.AnchorPoint = Vector2.new(1, 0)
	slot.Size = UDim2.fromOffset(SLOT.X, SLOT.Y)
	slot.Parent = parent

	local button = Instance.new("TextButton")
	button.Name = "Icon"
	button.AutoButtonColor = false
	button.AnchorPoint = Vector2.new(0.5, 0)
	button.Position = UDim2.fromScale(0.5, 0)
	button.Size = UDim2.fromOffset(ICON, ICON)
	button.BackgroundColor3 = UiKit.PANEL
	button.FontFace = UiKit.FONT
	button.TextSize = 44
	button.TextColor3 = Color3.new(1, 1, 1)
	button.Text = boost.emoji or ""
	button.ZIndex = 2
	button.Parent = slot
	local round = Instance.new("UICorner")
	round.CornerRadius = UDim.new(0.5, 0)
	round.Parent = button
	UiKit.stroke(button, 6).Color = boost.color
	-- The ink edge round the coloured ring, with its hard shadow: a darker disc behind the button.
	local edge = Instance.new("Frame")
	edge.Name = "Edge"
	edge.AnchorPoint = Vector2.new(0.5, 0)
	edge.Position = UDim2.new(0.5, 0, 0, -4)
	edge.Size = UDim2.fromOffset(ICON + 8, ICON + 12)
	edge.BackgroundColor3 = UiKit.INK
	edge.ZIndex = 1
	edge.Parent = slot
	round:Clone().Parent = edge

	local artSpot = { position = UDim2.fromOffset(5, -3), size = UDim2.fromOffset(74, 74) }
	if boost.art == "clover" then
		local art = UiKit.viewport(button, "clover", {
			position = artSpot.position,
			size = artSpot.size,
			tint = boost.tint,
			tintAmount = if boost.tint then 0.8 else nil,
		})
		art.ZIndex = 3
		art.Ambient = Color3.fromRGB(235, 235, 245) -- the disc is dark: a viewport's usual light left the clover dull
	elseif boost.art == "bolt" then
		UiKit.art(button, "bolts_S", "bolts_S", artSpot).ZIndex = 3
	end
	if boost.multiplier then
		local text = `x{boost.multiplier}`
		local multiplier = label(button, if #text > 2 then 20 else 26, Color3.new(1, 1, 1), 3)
		multiplier.Text = text
		multiplier.AnchorPoint = Vector2.new(0.5, 0)
		multiplier.Position = UDim2.new(0.5, 0, 0, 48)
		multiplier.ZIndex = 4
	end

	local pill = Instance.new("Frame")
	pill.Name = "TimeLeft"
	pill.AnchorPoint = Vector2.new(0.5, 0)
	pill.Position = UDim2.new(0.5, 0, 0, ICON - 10)
	pill.AutomaticSize = Enum.AutomaticSize.X
	pill.Size = UDim2.fromOffset(0, 30)
	pill.BackgroundColor3 = boost.color
	pill.ZIndex = 3
	pill.Parent = slot
	UiKit.corner(pill, 12)
	UiKit.stroke(pill, 3)
	local pad = Instance.new("UIPadding")
	pad.PaddingLeft, pad.PaddingRight = UDim.new(0, 10), UDim.new(0, 10)
	pad.Parent = pill
	local time = label(pill, 22, UiKit.INK)
	time.Size = UDim2.fromScale(0, 1)
	time.AutomaticSize = Enum.AutomaticSize.X
	time.ZIndex = 3

	return { frame = slot, button = button, time = time, order = nil }
end

local function luckyHitOf(multiplier: number): number?
	for _, hit in Catch.luckyHits do
		if hit.multiplier == multiplier then
			return hit.minOneIn
		end
	end
	return nil
end

-- Everything active right now, the rightmost icon first. The order never changes, so icons don't swap places.
local function activeBoosts()
	local list = {}
	local now = workspace:GetServerTimeNow()

	local event, eventEndsAt = Events.active(player)
	if event and eventEndsAt then
		local left = clock(eventEndsAt - Events.now())
		table.insert(list, {
			id = `Event{event.id}`,
			emoji = event.icon,
			color = event.color,
			pill = left,
			title = event.name:upper(),
			what = event.description,
			when = `Ends in {left} · next: {Events.upcoming().name}`,
		})
	end

	local luckEndsAt = ReplicatedStorage:GetAttribute("ServerLuckEndsAt")
	if luckEndsAt and luckEndsAt > now then
		local left = clock(luckEndsAt - now)
		local multiplier = Shop.serverLuck.multiplier
		table.insert(list, {
			id = "ServerLuck",
			art = "clover",
			multiplier = multiplier,
			color = Boosts.serverLuck.color,
			pill = left,
			title = `SERVER LUCK x{multiplier}`,
			what = `Rare monsters about {multiplier}x likelier for everyone here`,
			when = `Ends in {left} · buying more adds time`,
		})
	end

	local xpEndsAt = player:GetAttribute("XpBoostEndsAt")
	if xpEndsAt and xpEndsAt > now then
		local left = clock(xpEndsAt - now)
		local multiplier = Index.xpBoost.multiplier
		table.insert(list, {
			id = "XpBoost",
			art = "bolt",
			multiplier = multiplier,
			color = Boosts.xp.color,
			pill = left,
			title = `x{multiplier} XP`,
			what = `Every squat gives {multiplier}x XP`,
			when = `Ends in {left}`,
		})
	end

	-- The next free lucky throw for staying (Config/PlayGifts), counting down.
	local giftAt, giftLuck = player:GetAttribute("PlayGiftAt"), player:GetAttribute("PlayGiftLuck")
	if giftAt and giftLuck then
		local left = clock(giftAt - now)
		local look = Boosts.luckyThrows[giftLuck]
		table.insert(list, {
			id = `PlayGift{giftLuck}`,
			emoji = "🎁",
			color = if look then look.color else Boosts.serverLuck.color,
			pill = left,
			title = `FREE x{giftLuck} LUCKY THROW`,
			what = "A gift for playing: one throw with huge luck",
			when = `Yours in {left} · keep playing`,
		})
	end

	local nextThrow = LuckyThrows.nextOf(player)
	for _, multiplier in LuckyThrows.tiers do
		local count = LuckyThrows.count(player, multiplier)
		if count > 0 then
			local look = Boosts.luckyThrows[multiplier]
			local color = if look then look.color else Boosts.serverLuck.color
			local minOneIn = luckyHitOf(multiplier)
			table.insert(list, {
				id = `Lucky{multiplier}`,
				art = "clover",
				tint = color,
				multiplier = multiplier,
				color = color,
				pill = `{count} left`,
				title = `LUCKY THROW x{multiplier}`,
				what = if minOneIn then `A guaranteed 1 in {Format.short(minOneIn)}+ catch` else "A big luck bonus on one throw",
				when = if LuckyThrows.isPicked(multiplier)
					then `{count} left · tap USE on the throw meter`
					elseif multiplier == nextThrow then `{count} left · used on your next throw`
					else `{count} left · used after your x{nextThrow}s`,
			})
		end
	end
	return list
end

function BoostRowController.start()
	local hud = buildGui()
	local slots = {}
	local hoveredId: string? = nil
	local pinnedId: string? = nil
	local lastIconTap = 0

	local function slotFor(boost)
		local slot = slots[boost.id]
		if slot then
			return slot
		end
		slot = buildSlot(hud.corner, boost)
		slots[boost.id] = slot
		-- Hover opens the card on PC; a tap toggles it on phones (and a click does on PC too).
		slot.button.MouseEnter:Connect(function()
			if not isTouch() then
				hoveredId = boost.id
			end
		end)
		slot.button.MouseLeave:Connect(function()
			if hoveredId == boost.id then
				hoveredId = nil
			end
		end)
		slot.button.Activated:Connect(function()
			lastIconTap = os.clock()
			pinnedId = if pinnedId == boost.id then nil else boost.id
		end)
		return slot
	end

	-- A tap anywhere but on an icon closes the card. The icon's own tap may arrive just after this one.
	UserInputService.InputEnded:Connect(function(input)
		local kind = input.UserInputType
		if pinnedId and (kind == Enum.UserInputType.Touch or kind == Enum.UserInputType.MouseButton1) then
			task.delay(TAP_WINDOW, function()
				if os.clock() - lastIconTap > TAP_WINDOW * 2 then
					pinnedId = nil
				end
			end)
		end
	end)

	local function showCard(boost, order: number)
		hud.title.Text = boost.title
		hud.title.TextColor3 = boost.color
		hud.what.Text = boost.what
		hud.when.Text = boost.when
		-- How far left of the row's right edge: the icon's middle, then the card's right side.
		local middle = (order - 1) * STRIDE + SLOT.X / 2
		local width = hud.card.AbsoluteSize.X / hud.scale.Scale
		local right = math.max(if order == 1 then 0 else CARD_INSET, middle - width / 2)
		hud.card.Position = UDim2.new(1, -right, 0, -CARD_GAP)
		hud.nub.Position = UDim2.new(1, -middle, 0, -CARD_GAP)
	end

	RunService.Heartbeat:Connect(function()
		local list = activeBoosts()
		local openId = hoveredId or pinnedId
		local open = false
		local seen = {}
		for order, boost in list do
			seen[boost.id] = true
			local slot = slotFor(boost)
			slot.time.Text = boost.pill
			if slot.order ~= order then
				local goal = UDim2.new(1, -(order - 1) * STRIDE, 0, 0)
				if slot.order then
					TweenService:Create(slot.frame, TweenInfo.new(SLIDE_SECONDS, Enum.EasingStyle.Quad), { Position = goal }):Play()
				else
					slot.frame.Position = goal
				end
				slot.order = order
			end
			slot.frame.Visible = true
			if boost.id == openId then
				open = true
				showCard(boost, order)
			end
		end
		for id, slot in slots do
			if not seen[id] then
				slot.frame.Visible = false
				slot.order = nil
				if hoveredId == id then
					hoveredId = nil
				end
				if pinnedId == id then
					pinnedId = nil
				end
			end
		end
		hud.corner.Visible = #list > 0
		hud.card.Visible = open
		hud.nub.Visible = open
	end)
end

return BoostRowController
