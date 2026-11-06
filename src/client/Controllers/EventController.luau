-- The timed events (Config/Events), display only: a shout in the event's colour when one starts, a light tint
-- on the world while it runs, and an icon at the bottom right with the time left (Figma "Throw Eggs - Pop-up
-- Text", "Event icon" and "Event tooltip"). Hovering it (PC) or tapping it (phone) opens a card saying what the
-- event does. The server applies the boosts itself.
local Lighting = game:GetService("Lighting")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")

local Events = require(ReplicatedStorage.Shared.Config.Events)
local PopText = require(ReplicatedStorage.Shared.PopText)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local player = Players.LocalPlayer

local EventController = {}

local TINT_STRENGTH = 0.12 -- how far the world's colour moves towards the event's
local TINT_FADE = 2 -- seconds
local ICON = 84 -- design pixels
local MARGIN = 16
-- On touch screens, lifted above the jump button in the bottom right. Roblox makes that button smaller and lower
-- on phones (screens 500 points or less on their short side) than on tablets; 190 on a phone put the icon on
-- the Dinos button.
local TOUCH_LIFT = 190
local PHONE_LIFT = 80
local CARD_GAP = 14

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
	gui.Name = "EventHud"
	gui.ResetOnSpawn = false
	gui.Parent = player:WaitForChild("PlayerGui")

	-- Everything hangs from the bottom-right corner, sized in design pixels and scaled with the screen.
	local corner = Instance.new("Frame")
	corner.Name = "Corner"
	corner.BackgroundTransparency = 1
	corner.AnchorPoint = Vector2.new(1, 1)
	corner.Size = UDim2.fromOffset(ICON + 12, ICON + 34)
	corner.Visible = false
	corner.Parent = gui
	local scale = Instance.new("UIScale")
	scale.Parent = corner

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
	button.Parent = corner
	local round = Instance.new("UICorner")
	round.CornerRadius = UDim.new(0.5, 0)
	round.Parent = button
	button.ZIndex = 2
	local ring = UiKit.stroke(button, 6) -- in the event's colour
	-- The ink edge round the coloured ring, with its hard shadow: a darker disc behind the button.
	local edge = Instance.new("Frame")
	edge.Name = "Edge"
	edge.AnchorPoint = Vector2.new(0.5, 0)
	edge.Position = UDim2.new(0.5, 0, 0, -4)
	edge.Size = UDim2.fromOffset(ICON + 8, ICON + 12)
	edge.BackgroundColor3 = UiKit.INK
	edge.ZIndex = 1
	edge.Parent = corner
	local edgeRound = round:Clone()
	edgeRound.Parent = edge

	local pill = Instance.new("Frame")
	pill.Name = "TimeLeft"
	pill.AnchorPoint = Vector2.new(0.5, 0)
	pill.Position = UDim2.new(0.5, 0, 0, ICON - 10)
	pill.AutomaticSize = Enum.AutomaticSize.X
	pill.Size = UDim2.fromOffset(0, 30)
	pill.ZIndex = 3
	pill.Parent = corner
	UiKit.corner(pill, 12)
	UiKit.stroke(pill, 3)
	local pad = Instance.new("UIPadding")
	pad.PaddingLeft, pad.PaddingRight = UDim.new(0, 10), UDim.new(0, 10)
	pad.Parent = pill
	local time = label(pill, 22, UiKit.INK)
	time.Size = UDim2.fromScale(0, 1)
	time.AutomaticSize = Enum.AutomaticSize.X
	time.ZIndex = 3

	-- The card over the icon: what the event does, how long is left and what comes next.
	local card = Instance.new("Frame")
	card.Name = "Card"
	card.AnchorPoint = Vector2.new(1, 1)
	card.Position = UDim2.new(1, 0, 0, -CARD_GAP)
	card.AutomaticSize = Enum.AutomaticSize.XY
	card.BackgroundColor3 = UiKit.PANEL
	card.Visible = false
	card.Parent = corner
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

	local function place()
		local viewport = workspace.CurrentCamera.ViewportSize
		local phone = math.min(viewport.X, viewport.Y) <= 500
		local lift = if UserInputService.TouchEnabled and not UserInputService.MouseEnabled then (if phone then PHONE_LIFT else TOUCH_LIFT) else 0
		corner.Position = UDim2.new(1, -MARGIN, 1, -MARGIN - lift)
		scale.Scale = UiKit.scale()
	end
	place()
	workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(place)

	return {
		corner = corner,
		button = button,
		ring = ring,
		pill = pill,
		time = time,
		card = card,
		title = title,
		what = what,
		when = when,
	}
end

function EventController.start()
	local hud = buildGui()
	local tint = Instance.new("ColorCorrectionEffect")
	tint.Name = "EventTint"
	tint.Parent = Lighting

	-- Hover opens the card on PC; a tap toggles it on phones (and a click does on PC too).
	local hovering, pinned = false, false
	hud.button.MouseEnter:Connect(function()
		hovering = true
	end)
	hud.button.MouseLeave:Connect(function()
		hovering = false
	end)
	hud.button.Activated:Connect(function()
		pinned = not pinned
	end)

	local shownId: string? = nil
	local joined = false -- an event already running when you join gets its icon and tint but no shout
	RunService.Heartbeat:Connect(function()
		local event, endsAt = Events.active()
		local id = if event then event.id else nil
		if id ~= shownId then
			shownId = id
			pinned = false
			local tintColor = if event then Color3.new(1, 1, 1):Lerp(event.color, TINT_STRENGTH) else Color3.new(1, 1, 1)
			TweenService:Create(tint, TweenInfo.new(TINT_FADE), { TintColor = tintColor }):Play()
			if event then
				if joined then
					PopText.shout(`{event.name:upper()}!`, `{event.description} for {Events.seconds // 60} minutes`, event.color)
				end
				hud.button.Text = event.icon
				hud.ring.Color = event.color
				hud.pill.BackgroundColor3 = event.color
				hud.title.Text = event.name:upper()
				hud.title.TextColor3 = event.color
				hud.what.Text = event.description
			end
			hud.corner.Visible = event ~= nil
		end
		joined = true
		if event and endsAt then
			local left = clock(endsAt - Events.now())
			hud.time.Text = left
			local nextEvent = Events.upcoming()
			hud.when.Text = `Ends in {left} · next: {nextEvent.name}`
		end
		hud.card.Visible = event ~= nil and (hovering or pinned)
	end)
end

return EventController
