-- Pop-up text: outlined words with a hard shadow and no panel behind them, that pop in, float and fade
-- (Figma "Throw Eggs - Pop-up Text"; looks and motion in Config/Pop). Float is for small gains and costs,
-- Shout for big moments, Notice for messages from the server, and Punch makes a label that's already on
-- screen punch in. Client only.
local GuiService = game:GetService("GuiService")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TextService = game:GetService("TextService")

local HudStyle = require(script.Parent.HudStyle)
local Pop = require(script.Parent.Config.Pop)
local UiKit = require(script.Parent.UiKit)

local PopText = {}

local GAP = 4 -- between a pop and the thing it pops from

-- How a move between two keyframes speeds up and slows down.
local EASE = {
	linear = function(x: number): number
		return x
	end,
	["in"] = function(x: number): number
		return x * x * x
	end,
	out = function(x: number): number
		return 1 - (1 - x) ^ 3
	end,
	inOut = function(x: number): number
		return if x < 0.5 then 4 * x * x * x else 1 - (2 - 2 * x) ^ 3 / 2
	end,
	outBack = function(x: number): number
		local overshoot = 1.70158
		return 1 + (overshoot + 1) * (x - 1) ^ 3 + overshoot * (x - 1) ^ 2
	end,
}

-- A keyframe track's value at t seconds (Config/Pop explains the tracks).
local function sample(track, t: number): number
	if t <= track[1][1] then
		return track[1][2]
	end
	for index = 2, #track do
		local from, to = track[index - 1], track[index]
		if t < to[1] then
			local share = (t - from[1]) / (to[1] - from[1])
			return from[2] + (to[2] - from[2]) * EASE[to[3] or "linear"](share)
		end
	end
	return track[#track][2]
end

-- When the last of these tracks ends.
local function lengthOf(...): number
	local length = 0
	for _, track in { ... } do
		length = math.max(length, track[#track][1])
	end
	return length
end

local layer: ScreenGui? = nil
local function getLayer(): ScreenGui
	if not layer then
		local gui = Instance.new("ScreenGui")
		gui.Name = "PopText"
		gui.IgnoreGuiInset = true
		gui.ResetOnSpawn = false
		gui.DisplayOrder = 7 -- over the HUD and panels, under Welcome Back, the lucky catch banner and the reveal
		gui.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")
		layer = gui
	end
	return layer :: ScreenGui
end

-- One outlined word with a hard ink shadow under it, centred on its position. look holds its size, outline
-- and shadow in design pixels; fill is a colour or a UiKit gradient name.
local function word(parent: Instance, text: string, look, fill: Color3 | string): Frame
	local bounds = TextService:GetTextSize(text, look.size, HudStyle.FONT, Vector2.new(10000, 10000))
	local holder = Instance.new("Frame")
	holder.Name = text
	holder.BackgroundTransparency = 1
	holder.AnchorPoint = Vector2.new(0.5, 0.5)
	holder.Size = UDim2.fromOffset(bounds.X + look.outline * 2, bounds.Y)
	holder.Parent = parent
	for _, isShadow in { true, false } do
		local label = Instance.new("TextLabel")
		label.Name = if isShadow then "Shadow" else "Text"
		label.BackgroundTransparency = 1
		label.FontFace = UiKit.FONT
		label.Text = text
		label.TextSize = look.size
		label.TextColor3 = if isShadow then UiKit.INK elseif typeof(fill) == "Color3" then fill else Color3.new(1, 1, 1)
		label.Size = UDim2.fromScale(1, 1)
		label.Position = UDim2.fromOffset(0, if isShadow then look.shadow else 0)
		label.ZIndex = if isShadow then 1 else 2
		label.Parent = holder
		local stroke = Instance.new("UIStroke")
		stroke.Color = UiKit.INK
		stroke.Thickness = look.outline
		stroke.LineJoinMode = Enum.LineJoinMode.Round
		stroke.Parent = label
		if not isShadow and typeof(fill) == "string" then
			UiKit.gradient(label, fill)
		end
	end
	return holder
end

-- How solid a pop is, outline and shadow included (1 = fully shown). The shadow fades faster than the text,
-- so it doesn't show through the half-faded letters.
local function setOpacity(holder: Instance, opacity: number)
	for _, label in holder:GetChildren() do
		if label:IsA("TextLabel") then
			local own = if label.Name == "Shadow" then opacity ^ 3 else opacity
			label.TextTransparency = 1 - own
			local stroke = label:FindFirstChildOfClass("UIStroke")
			if stroke then
				stroke.Transparency = 1 - own
			end
		end
	end
end

-- Calls step every frame with the seconds since the start, until length; then done. Returns a function
-- that stops it early (done still runs).
local function play(length: number, step: (number) -> (), done: () -> ()): () -> ()
	local startedAt = os.clock()
	local connection: RBXScriptConnection
	local function stop()
		if connection.Connected then
			connection:Disconnect()
			done()
		end
	end
	step(0)
	connection = RunService.RenderStepped:Connect(function()
		local elapsed = os.clock() - startedAt
		step(math.min(elapsed, length))
		if elapsed >= length then
			stop()
		end
	end)
	return stop
end

-- Places that show one pop at a time (the shout, the notice, a punched label): a new one cuts the old off.
local stopShowing: { [any]: () -> () } = {}
local function playOnly(spot: any, length: number, step: (number) -> (), done: () -> ())
	if stopShowing[spot] then
		stopShowing[spot]()
	end
	local stop
	stop = play(length, step, function()
		done()
		if stopShowing[spot] == stop then
			stopShowing[spot] = nil
		end
	end)
	stopShowing[spot] = stop
end

-- An element's top left corner on the whole screen, top bar included, which is how the pop layer measures.
local function screenPosition(element: GuiObject): Vector2
	local gui = element:FindFirstAncestorWhichIsA("ScreenGui")
	local inset = if gui and gui.IgnoreGuiInset then Vector2.zero else GuiService:GetGuiInset()
	return element.AbsolutePosition + inset
end

-- Where a float starts, and which point of it sits there: just above the middle of a GUI element...
function PopText.above(element: GuiObject): (Vector2, Vector2)
	return screenPosition(element) + Vector2.new(element.AbsoluteSize.X / 2, -GAP), Vector2.new(0.5, 1)
end

-- ...or just past the end of a label's text, level with its middle.
function PopText.after(label: TextLabel): (Vector2, Vector2)
	local width, textWidth = label.AbsoluteSize.X, label.TextBounds.X
	local textEnd = if label.TextXAlignment == Enum.TextXAlignment.Left
		then textWidth
		elseif label.TextXAlignment == Enum.TextXAlignment.Right then width
		else (width + textWidth) / 2
	return screenPosition(label) + Vector2.new(textEnd + GAP * 2, label.AbsoluteSize.Y / 2), Vector2.new(0, 0.5)
end

-- A small gain or cost floating up from a point on the screen, like "+$1.2K" by the cash. anchor is the point
-- of the text that starts there (PopText.above and PopText.after give both).
function PopText.float(text: string, color: Color3, at: Vector2, anchor: Vector2?)
	local look = Pop.float
	local holder = word(getLayer(), text, look, color)
	holder.AnchorPoint = anchor or Vector2.new(0.5, 0.5)
	holder.Rotation = (math.random() * 2 - 1) * look.tilt
	local size = Instance.new("UIScale")
	size.Parent = holder
	local scale = UiKit.scale()
	-- Floats starting beside something only spread away from it.
	local spread = if holder.AnchorPoint.X == 0.5 then math.random() * 2 - 1 else math.random()
	local x = at.X + spread * look.spread * scale
	play(lengthOf(look.scale, look.rise, look.opacity), function(t)
		size.Scale = scale * sample(look.scale, t)
		holder.Position = UDim2.fromOffset(x, at.Y - sample(look.rise, t) * scale)
		setOpacity(holder, sample(look.opacity, t))
	end, function()
		holder:Destroy()
	end)
end

-- A big moment in the upper middle of the screen: a title slamming in, with an optional detail line under it.
-- fill is a colour or a UiKit gradient name (gold if left out).
PopText.onShout = nil :: (() -> ())? -- set by the client's GameFeelSounds: the pop-up sound
function PopText.shout(title: string, detail: string?, fill: (Color3 | string)?)
	if PopText.onShout then
		PopText.onShout()
	end
	local look = Pop.shout
	local group = Instance.new("Frame")
	group.Name = "Shout"
	group.BackgroundTransparency = 1
	group.Position = UDim2.fromScale(0.5, look.height)
	group.Size = UDim2.fromOffset(0, 0)
	group.Parent = getLayer()
	local size = Instance.new("UIScale")
	size.Parent = group
	local titleWord = word(group, title, look.title, fill or "gold")
	titleWord.Rotation = -look.tilt
	local detailWord = if detail then word(group, detail, look.detail, Color3.new(1, 1, 1)) else nil
	local detailY = if detailWord then (titleWord.Size.Y.Offset + detailWord.Size.Y.Offset) / 2 - look.overlap else 0
	local scale = UiKit.scale()
	playOnly("shout", lengthOf(look.scale, look.opacity), function(t)
		size.Scale = scale * sample(look.scale, t)
		local opacity = sample(look.opacity, t)
		setOpacity(titleWord, opacity)
		if detailWord then
			detailWord.Position = UDim2.fromOffset(0, detailY + sample(look.detailRise, t))
			setOpacity(detailWord, opacity * sample(look.detailOpacity, t))
		end
	end, function()
		group:Destroy()
	end)
end

-- A message from the server above the hotbar: gold when something worked, red with a shake when it didn't.
function PopText.notice(text: string, good: boolean)
	local look = Pop.notice
	local holder = word(getLayer(), text, look, if good then Pop.colors.good else Pop.colors.bad)
	holder.AnchorPoint = Vector2.new(0.5, 1)
	local size = Instance.new("UIScale")
	size.Parent = holder
	local scale = UiKit.scale()
	local bottom = look.bottom * HudStyle.scale()
	local grow = if good then look.scale else look.badScale
	playOnly("notice", lengthOf(grow, look.lift, look.opacity), function(t)
		size.Scale = scale * sample(grow, t)
		local shake = if good then 0 else sample(look.shake, t) * scale
		holder.Position = UDim2.new(0.5, shake, 1, -bottom - sample(look.lift, t) * scale)
		setOpacity(holder, sample(look.opacity, t))
	end, function()
		holder:Destroy()
	end)
end

-- Makes a label that's already on screen punch in: from big with a twist, springing into place.
function PopText.punch(label: GuiObject)
	local look = Pop.punch
	local size = label:FindFirstChild("PunchScale") :: UIScale?
	if not size then
		local made = Instance.new("UIScale")
		made.Name = "PunchScale"
		made.Parent = label
		size = made
	end
	local punchScale = size :: UIScale
	playOnly(label, lengthOf(look.scale, look.twist), function(t)
		punchScale.Scale = sample(look.scale, t)
		label.Rotation = sample(look.twist, t)
	end, function()
		punchScale.Scale = 1
		label.Rotation = 0
	end)
end

-- The building blocks, for one-off big moments built elsewhere (PerfectMoment): an outlined word with its hard
-- shadow, fading a word, and reading a keyframe track ({ time, value, ease? }, ...) at a time.
PopText.word = word
PopText.setOpacity = setOpacity
PopText.sample = sample

return PopText
