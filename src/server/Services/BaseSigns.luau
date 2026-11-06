-- What every base shows to everyone: the owner plate floating high above it (profile picture, name and
-- $/s) and the face of the upgrade sign on its front fence (size now › next and the price, or MAX). Both
-- follow the mock-ups in design/ui-mockups/build.py (13b "Owner plate", 14 "Base upgrade sign").
-- PlotService builds them with each base and tells them what to show.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Format = require(ReplicatedStorage.Shared.Format)
local Plot = require(ReplicatedStorage.Shared.Config.Plot)

local BaseSigns = {}

local FONT = Font.new("rbxasset://fonts/families/FredokaOne.json") -- UiKit.FONT
local INK = Color3.fromRGB(27, 18, 48)
local WHITE = Color3.new(1, 1, 1)
local CASH = Color3.fromRGB(141, 255, 90)
local SHORT = Color3.fromRGB(255, 107, 94) -- the price when the owner can't afford it yet
local NEXT = Color3.fromRGB(255, 224, 102)
local SIGN_CANVAS = Vector2.new(300, 224) -- the mock-up's pixels; the board is drawn at this size

local function gradient(object: GuiObject, top: string, bottom: string)
	object.BackgroundColor3 = WHITE
	local g = Instance.new("UIGradient")
	g.Color = ColorSequence.new(Color3.fromHex(top), Color3.fromHex(bottom))
	g.Rotation = 90
	g.Parent = object
end

local function corner(object: GuiObject, radius: UDim)
	local c = Instance.new("UICorner")
	c.CornerRadius = radius
	c.Parent = object
end

local function stroke(object: GuiObject, thickness: number, mode: Enum.ApplyStrokeMode)
	local s = Instance.new("UIStroke")
	s.ApplyStrokeMode = mode
	s.Color = INK
	s.Thickness = thickness
	s.LineJoinMode = Enum.LineJoinMode.Round
	s.Parent = object
	return s
end

local function label(parent: Instance, name: string, color: Color3, strokeThickness: number): TextLabel
	local text = Instance.new("TextLabel")
	text.Name = name
	text.BackgroundTransparency = 1
	text.FontFace = FONT
	text.TextColor3 = color
	text.TextScaled = true
	text.Parent = parent
	stroke(text, strokeThickness, Enum.ApplyStrokeMode.Contextual)
	return text
end

-- The owner plate: no panel behind it, just the picture in a white ring, the name and the $/s. Sized in
-- studs so it shrinks with distance like the world, and always on top so giant dinos can't hide it.
function BaseSigns.buildPlate(parent: Instance, plotIndex: number)
	local settings = Plot.ownerPlate
	local anchor = Instance.new("Part")
	anchor.Name = "OwnerPlateAnchor"
	anchor.Anchored = true
	anchor.CanCollide = false
	anchor.CanQuery = false
	anchor.CanTouch = false
	anchor.Transparency = 1
	anchor.Size = Vector3.one
	anchor.Position = Plot.positions[plotIndex] + Vector3.new(0, settings.height, 0)
	anchor.Parent = parent

	local gui = Instance.new("BillboardGui")
	gui.Name = "OwnerPlate"
	gui.Size = UDim2.fromScale(settings.size.X, settings.size.Y)
	gui.AlwaysOnTop = true
	gui.LightInfluence = 0
	gui.MaxDistance = settings.maxDistance
	gui.Enabled = false -- a base without an owner shows no plate
	gui.Parent = anchor

	local ring = Instance.new("Frame")
	ring.Name = "Ring"
	ring.AnchorPoint = Vector2.new(0.5, 0)
	ring.Position = UDim2.fromScale(0.5, 0)
	ring.Size = UDim2.fromScale(0.5, 0.5)
	ring.SizeConstraint = Enum.SizeConstraint.RelativeYY
	ring.BackgroundColor3 = WHITE
	ring.Parent = gui
	corner(ring, UDim.new(0.5, 0))
	stroke(ring, 3, Enum.ApplyStrokeMode.Border)

	local picture = Instance.new("ImageLabel")
	picture.Name = "Picture"
	picture.AnchorPoint = Vector2.new(0.5, 0.5)
	picture.Position = UDim2.fromScale(0.5, 0.5)
	picture.Size = UDim2.fromScale(0.86, 0.86)
	picture.BackgroundColor3 = Color3.fromRGB(111, 227, 255)
	picture.Parent = ring
	corner(picture, UDim.new(0.5, 0))

	local name = label(gui, "PlayerName", WHITE, 3)
	name.Position = UDim2.fromScale(0, 0.52)
	name.Size = UDim2.fromScale(1, 0.24)

	local income = label(gui, "Income", CASH, 3)
	income.Position = UDim2.fromScale(0, 0.75)
	income.Size = UDim2.fromScale(1, 0.21)

	-- The server medal (👑 #1, #2, #3), over the picture's top right; CompetitionService fills it in.
	local rank = label(gui, "Rank", WHITE, 3)
	rank.AnchorPoint = Vector2.new(0, 0.5)
	rank.Position = UDim2.fromScale(0.68, 0.06)
	rank.Size = UDim2.fromScale(0.32, 0.18)
	rank.Visible = false
end

-- Shows a player's plate on their base, or hides it when the base is free (player nil).
function BaseSigns.setPlate(plotModel: Model, player: Player?)
	local gui = plotModel.OwnerPlateAnchor.OwnerPlate
	gui.Enabled = player ~= nil
	if not player then
		return
	end
	gui.PlayerName.Text = player.Name
	gui.Income.Text = "$0/s"
	gui.Ring.Picture.Image = ""
	task.spawn(function()
		local ok, image = pcall(Players.GetUserThumbnailAsync, Players, player.UserId, Enum.ThumbnailType.HeadShot, Enum.ThumbnailSize.Size150x150)
		-- The base may have changed hands while the picture loaded.
		if ok and gui.Enabled and gui.PlayerName.Text == player.Name then
			gui.Ring.Picture.Image = image
		end
	end)
end

function BaseSigns.setPlateIncome(plotModel: Model, income: number)
	plotModel.OwnerPlateAnchor.OwnerPlate.Income.Text = `{Format.cash(income)}/s`
end

-- The face of the upgrade sign, drawn on the board's front: a blue board with the paw, "now › next" and
-- a dark price bar, or a gold MAX bar at the top level.
function BaseSigns.buildSignFace(board: BasePart, face: Enum.NormalId)
	local gui = Instance.new("SurfaceGui")
	gui.Name = "SignFace"
	gui.Face = face
	gui.SizingMode = Enum.SurfaceGuiSizingMode.FixedSize
	gui.CanvasSize = SIGN_CANVAS
	gui.LightInfluence = 0
	gui.Enabled = false -- blank until the base has an owner
	gui.Parent = board

	local card = Instance.new("Frame")
	card.Name = "Card"
	card.Position = UDim2.fromOffset(6, 6)
	card.Size = UDim2.new(1, -12, 1, -12)
	card.Parent = gui
	gradient(card, "#8ad8ff", "#2f8ce6")
	corner(card, UDim.new(0, 28))
	stroke(card, 6, Enum.ApplyStrokeMode.Border)

	local row = Instance.new("Frame")
	row.Name = "Row"
	row.BackgroundTransparency = 1
	row.Position = UDim2.fromOffset(12, 8)
	row.Size = UDim2.new(1, -24, 0, 112)
	row.Parent = card
	local layout = Instance.new("UIListLayout")
	layout.FillDirection = Enum.FillDirection.Horizontal
	layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	layout.VerticalAlignment = Enum.VerticalAlignment.Center
	layout.Padding = UDim.new(0, 4)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = row

	local function piece(name: string, text: string, color: Color3, width: number, order: number)
		local part = label(row, name, color, 5)
		part.Text = text
		part.TextScaled = false
		part.TextSize = 64
		part.Size = UDim2.fromOffset(width, 100)
		part.LayoutOrder = order
		return part
	end
	piece("Paw", "🐾", WHITE, 60, 1)
	piece("Now", "", WHITE, 74, 2)
	piece("Arrow", ">", WHITE, 26, 3) -- plain ">": phone fonts may lack "›"
	piece("Next", "", NEXT, 74, 4)

	local bar = Instance.new("Frame")
	bar.Name = "Bar"
	bar.Position = UDim2.fromOffset(12, 124)
	bar.Size = UDim2.new(1, -24, 1, -136)
	bar.BackgroundColor3 = Color3.fromRGB(18, 13, 34)
	bar.Parent = card
	corner(bar, UDim.new(0, 18))
	stroke(bar, 4, Enum.ApplyStrokeMode.Border)
	local barGradient = Instance.new("UIGradient")
	barGradient.Name = "Gold"
	barGradient.Color = ColorSequence.new(Color3.fromHex("#ffe066"), Color3.fromHex("#f5a815"))
	barGradient.Rotation = 90
	barGradient.Enabled = false
	barGradient.Parent = bar

	local price = label(bar, "Price", CASH, 4)
	price.Position = UDim2.fromScale(0.05, 0.12)
	price.Size = UDim2.fromScale(0.9, 0.76)
end

-- What the sign shows for its owner's save (nil: a free base, blank), and whether they can afford it.
function BaseSigns.setSignFace(board: BasePart, data, cash: number?)
	local gui = board:FindFirstChild("SignFace")
	if not gui then
		return
	end
	gui.Enabled = data ~= nil
	if not data then
		return
	end
	local card = gui.Card
	local capacity = Plot.capacity(data.plotUpgrades)
	local maxed = capacity >= Plot.maxSlots
	card.Row.Now.Text = tostring(capacity)
	card.Row.Arrow.Visible = not maxed
	card.Row.Next.Visible = not maxed
	card.Row.Next.Text = tostring(Plot.capacity(data.plotUpgrades + 1))
	card.Bar.Gold.Enabled = maxed
	card.Bar.BackgroundColor3 = if maxed then WHITE else Color3.fromRGB(18, 13, 34)
	if maxed then
		card.Bar.Price.Text = "MAX"
		card.Bar.Price.TextColor3 = WHITE
	else
		local cost = Plot.upgradePrice(data.plotUpgrades)
		card.Bar.Price.Text = Format.cash(cost) -- no "▲": phone fonts lack it
		card.Bar.Price.TextColor3 = if (cash or 0) >= cost then CASH else SHORT
	end
end

return BaseSigns
