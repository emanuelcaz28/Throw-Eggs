-- The small gift notification at the top right (Figma "Throw Eggs - Pop-up Text", "Gift Toast" 20:140): free
-- lucky throws for playing (Config/PlayGifts) and gifts from other players (ShopRemotes.GiftToast). It slides in
-- from the right with a small overshoot, the gift tile pops, a shine sweeps once, it stays 4 s and slides out.
-- Tap closes it early. Several wait in a queue, and none shows during a reveal or the tutorial. Display only.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local Boosts = require(ReplicatedStorage.Shared.Config.Boosts)
local LuckyThrows = require(ReplicatedStorage.Shared.LuckyThrows)
local PlayGifts = require(ReplicatedStorage.Shared.Config.PlayGifts)
local Tutorial = require(ReplicatedStorage.Shared.Config.Tutorial)
local UiKit = require(ReplicatedStorage.Shared.UiKit)
local RevealController = require(script.Parent.RevealController)
local Sfx = require(script.Parent.Sfx)

local player = Players.LocalPlayer

local GiftToastController = {}

local CARD = Color3.fromRGB(31, 26, 51)
local DETAIL = Color3.fromRGB(203, 191, 240)
local PLAYER_GIFT = { Color3.fromRGB(255, 154, 213), Color3.fromRGB(214, 69, 127) }
local DEEP = { [100] = Color3.fromRGB(138, 63, 214), [500] = Color3.fromRGB(214, 138, 31) }
local SIZE = Vector2.new(480, 96) -- design pixels, like the Figma component
local PC_SCALE = 0.8 -- of UiKit.scale on screens with a mouse
local TOP = 12 -- design pixels under the Roblox top bar (the ScreenGui keeps clear of it)
local MARGIN = 16
local HOLD = 4 -- seconds on screen

type Toast = { title: string, detail: string, accent: Color3, deep: Color3 }

local queue: { Toast } = {}
local showing = false
local gui: ScreenGui

local function busy(): boolean
	local step = player:GetAttribute("TutorialStep")
	return RevealController.isPlaying() or (step ~= nil and step < Tutorial.doneStep)
end

local function giftIcon(parent: GuiObject, deep: Color3)
	-- The gift box from the Figma tile, in blocks: box, lid, ribbon, bow.
	local function block(x, y, w, h, color, radius)
		local f = Instance.new("Frame")
		f.Position = UDim2.fromOffset(x, y)
		f.Size = UDim2.fromOffset(w, h)
		f.BackgroundColor3 = color
		f.Parent = parent
		UiKit.corner(f, radius or 4)
		UiKit.stroke(f, 3)
		return f
	end
	block(17, 32, 38, 26, Color3.new(1, 1, 1), 5)
	block(13, 22, 46, 12, Color3.new(1, 1, 1), 4)
	block(31, 22, 10, 36, deep, 2)
	local bowLeft = block(20, 12, 14, 12, deep, 6)
	bowLeft.Rotation = -20
	local bowRight = block(38, 12, 14, 12, deep, 6)
	bowRight.Rotation = 20
end

local function build(toast: Toast): (Frame, UIScale, Frame, Frame)
	local card = Instance.new("TextButton")
	card.Name = "GiftToast"
	card.Text = ""
	card.AutoButtonColor = false
	card.AnchorPoint = Vector2.new(1, 0)
	card.Size = UDim2.fromOffset(SIZE.X, SIZE.Y)
	card.BackgroundColor3 = CARD
	card.ClipsDescendants = true
	card.Parent = gui
	UiKit.corner(card, 18)
	UiKit.stroke(card, 4)
	local scale = Instance.new("UIScale")
	scale.Parent = card

	local tile = Instance.new("Frame")
	tile.Name = "Tile"
	tile.AnchorPoint = Vector2.new(0.5, 0.5)
	tile.Position = UDim2.fromOffset(12 + 36, SIZE.Y / 2)
	tile.Size = UDim2.fromOffset(72, 72)
	tile.BackgroundColor3 = Color3.new(1, 1, 1)
	tile.Parent = card
	UiKit.corner(tile, 14)
	UiKit.stroke(tile, 4)
	local fill = Instance.new("UIGradient")
	fill.Color = ColorSequence.new(toast.accent, toast.deep)
	fill.Rotation = 90
	fill.Parent = tile
	local tileScale = Instance.new("UIScale")
	tileScale.Parent = tile
	giftIcon(tile, toast.deep)

	local title = UiKit.text(card, toast.title, 28, toast.accent, Enum.TextXAlignment.Left)
	title.Position = UDim2.fromOffset(98, 14)
	title.Size = UDim2.fromOffset(SIZE.X - 112, 36)
	title.TextScaled = true
	local limit = Instance.new("UITextSizeConstraint")
	limit.MaxTextSize = 28
	limit.Parent = title
	local detail = UiKit.text(card, toast.detail, 18, DETAIL, Enum.TextXAlignment.Left)
	detail.Position = UDim2.fromOffset(98, 54)
	detail.Size = UDim2.fromOffset(SIZE.X - 112, 26)
	detail.TextTruncate = Enum.TextTruncate.AtEnd
	local stroke = detail:FindFirstChildOfClass("UIStroke")
	if stroke then
		stroke:Destroy()
	end

	local shine = Instance.new("Frame")
	shine.Name = "Shine"
	shine.BackgroundColor3 = Color3.new(1, 1, 1)
	shine.BackgroundTransparency = 0.82
	shine.BorderSizePixel = 0
	shine.Rotation = -20
	shine.Size = UDim2.fromOffset(40, 180)
	shine.Position = UDim2.fromOffset(-90, -40)
	shine.Parent = card
	return card, scale, tile, shine
end

local function tween(object: Instance, seconds: number, goal, style: Enum.EasingStyle?, direction: Enum.EasingDirection?)
	local t = TweenService:Create(object, TweenInfo.new(seconds, style or Enum.EasingStyle.Quad, direction or Enum.EasingDirection.Out), goal)
	t:Play()
	return t
end

local function fade(card: GuiObject, to: number, seconds: number)
	for _, d in { card, unpack(card:GetDescendants()) } do
		if d:IsA("UIStroke") then
			tween(d, seconds, { Transparency = to })
		elseif d:IsA("TextLabel") then
			tween(d, seconds, { TextTransparency = to })
		elseif d:IsA("GuiObject") and d.Name ~= "Shine" then
			tween(d, seconds, { BackgroundTransparency = to })
		end
	end
end

local function show(toast: Toast)
	local card, scale, tile, shine = build(toast)
	local isMouse = game:GetService("UserInputService").MouseEnabled
	local s = UiKit.scale() * (if isMouse then PC_SCALE else 1)
	scale.Scale = s * 1.04
	local rest = UDim2.new(1, -MARGIN, 0, TOP * s)
	card.Position = rest + UDim2.fromOffset(SIZE.X * s + 40, 0)
	Sfx.play("step")

	-- In: slide with a small overshoot, then settle.
	tween(card, 0.18, { Position = rest - UDim2.fromOffset(14, 0) }, Enum.EasingStyle.Quad)
	task.wait(0.18)
	tween(card, 0.14, { Position = rest }, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut)
	tween(scale, 0.14, { Scale = s }, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut)
	-- The tile pops with a small wiggle, the shine sweeps once.
	local tileScale = tile:FindFirstChildOfClass("UIScale") :: UIScale
	tileScale.Scale = 0.6
	tween(tileScale, 0.22, { Scale = 1 }, Enum.EasingStyle.Back)
	tile.Rotation = -12
	tween(tile, 0.3, { Rotation = 0 }, Enum.EasingStyle.Elastic)
	task.delay(0.13, function()
		tween(shine, 0.45, { Position = UDim2.fromOffset(SIZE.X + 40, -40) }, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut)
	end)

	local closed = false
	local tapped = card.Activated:Connect(function()
		closed = true
	end)
	local t = 0
	while t < HOLD and not closed do
		t += task.wait(0.1)
	end
	tapped:Disconnect()
	-- Out: back to the right and fade.
	tween(card, 0.3, { Position = rest + UDim2.fromOffset(40, 0) }, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
	fade(card, 1, 0.3)
	task.wait(0.32)
	card:Destroy()
end

local function pump()
	if showing then
		return
	end
	showing = true
	task.spawn(function()
		while #queue > 0 do
			while busy() do
				task.wait(0.5)
			end
			show(table.remove(queue, 1))
			task.wait(0.15)
		end
		showing = false
	end)
end

function GiftToastController.push(title: string, detail: string, accent: Color3?, deep: Color3?)
	table.insert(queue, {
		title = title,
		detail = detail,
		accent = accent or PLAYER_GIFT[1],
		deep = deep or PLAYER_GIFT[2],
	})
	pump()
end

function GiftToastController.start()
	gui = Instance.new("ScreenGui")
	gui.Name = "GiftToasts"
	gui.ResetOnSpawn = false
	gui.ScreenInsets = Enum.ScreenInsets.CoreUISafeInsets
	gui.DisplayOrder = 9
	gui.Parent = player:WaitForChild("PlayerGui")

	-- A free lucky throw for playing has just arrived (PlayGiftService).
	player:GetAttributeChangedSignal("PlayGiftsGiven"):Connect(function()
		local gift = PlayGifts.luckyThrows[player:GetAttribute("PlayGiftsGiven")]
		if gift then
			local look = Boosts.luckyThrows[gift.multiplier]
			GiftToastController.push(
				`FREE x{gift.multiplier} LUCKY THROW`,
				if LuckyThrows.isPicked(gift.multiplier)
					then "A gift for playing · tap USE on the meter"
					else "A gift for playing · used on your next throw",
				if look then look.color else nil,
				DEEP[gift.multiplier]
			)
		end
	end)

	-- A gift from another player (ShopService announceGift).
	local remotes = ReplicatedStorage:WaitForChild("ShopRemotes")
	remotes:WaitForChild("GiftToast").OnClientEvent:Connect(function(title: string, detail: string)
		GiftToastController.push(title, detail)
	end)
end

return GiftToastController
