-- The looks the Shop panel and the purchase moments share (ShopController, PurchaseMoments), from Figma "Shop" page
-- "Shop v2": glows, light rays, sparkles, embers, confetti, gradient words. Display only.
-- Things that move are made through ShopLook.effects(): its owner calls step(now) every frame while it's on screen.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ShopMoments = require(ReplicatedStorage.Shared.Config.ShopMoments)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local ShopLook = {}

local WHITE = Color3.new(1, 1, 1)
local images = ShopMoments.images

function ShopLook.hex(value: string): Color3
	return Color3.fromHex(value)
end

function ShopLook.at<T>(object: T & GuiObject, x: number, y: number, w: number?, h: number?): T
	object.Position = UDim2.fromOffset(x, y)
	if w and h then
		object.Size = UDim2.fromOffset(w, h)
	end
	return object
end

-- Rounded corners: pixels, or 0.5 for a pill or an ellipse.
function ShopLook.round(object: GuiObject, radius: number)
	local corner = Instance.new("UICorner")
	corner.CornerRadius = if radius <= 0.5 then UDim.new(radius, 0) else UDim.new(0, radius)
	corner.Parent = object
end

function ShopLook.blank(parent: Instance, name: string): Frame
	local frame = Instance.new("Frame")
	frame.Name = name
	frame.BackgroundTransparency = 1
	frame.BorderSizePixel = 0
	frame.Parent = parent
	return frame
end

function ShopLook.sequence(colours: { string }): ColorSequence
	local keys = {}
	for index, colour in colours do
		table.insert(keys, ColorSequenceKeypoint.new((index - 1) / (#colours - 1), Color3.fromHex(colour)))
	end
	return ColorSequence.new(keys)
end

-- A gradient fill on a label's letters or a frame's face. rotation 90 runs top to bottom.
function ShopLook.paint(object: GuiObject, colours: { string }, rotation: number?): UIGradient
	local gradient = Instance.new("UIGradient")
	gradient.Color = ShopLook.sequence(colours)
	gradient.Rotation = rotation or 90
	gradient.Parent = object
	return gradient
end

-- A plain block of colour: a bar, a shade, an ellipse (radius 0.5). opacity 1 is solid.
function ShopLook.block(parent: Instance, name: string, colour: Color3, x: number, y: number, w: number, h: number, opacity: number?, radius: number?): Frame
	local frame = Instance.new("Frame")
	frame.Name = name
	frame.BackgroundColor3 = colour
	frame.BackgroundTransparency = 1 - (opacity or 1)
	frame.BorderSizePixel = 0
	frame.Position = UDim2.fromOffset(x, y)
	frame.Size = UDim2.fromOffset(w, h)
	frame.Parent = parent
	if radius then
		ShopLook.round(frame, radius)
	end
	return frame
end

-- Makes a block fade along itself: from and to are how see-through each end is (0 solid, 1 gone).
function ShopLook.fade(frame: GuiObject, from: number, to: number, rotation: number?): UIGradient
	local gradient = Instance.new("UIGradient")
	gradient.Rotation = rotation or 90
	gradient.Transparency = NumberSequence.new(from, to)
	gradient.Parent = frame
	return gradient
end

-- One of the white pictures (ShopMoments.images), tinted, its middle at (cx, cy).
function ShopLook.image(parent: Instance, key: string, colour: Color3, cx: number, cy: number, w: number, h: number, opacity: number): ImageLabel
	local picture = Instance.new("ImageLabel")
	picture.Name = key
	picture.BackgroundTransparency = 1
	picture.Image = images[key]
	picture.ImageColor3 = colour
	picture.ImageTransparency = 1 - opacity
	picture.AnchorPoint = Vector2.new(0.5, 0.5)
	picture.Position = UDim2.fromOffset(cx, cy)
	picture.Size = UDim2.fromOffset(w, h)
	picture.Parent = parent
	return picture
end

-- An ellipse, its middle at (cx, cy): Roblox's own white circle stretched and tinted (rounded corners only make pills).
function ShopLook.ellipse(parent: Instance, name: string, colour: Color3, cx: number, cy: number, w: number, h: number, opacity: number): ImageLabel
	local oval = Instance.new("ImageLabel")
	oval.Name = name
	oval.BackgroundTransparency = 1
	oval.Image = "rbxasset://textures/whiteCircle.png"
	oval.ImageColor3 = colour
	oval.ImageTransparency = 1 - opacity
	oval.AnchorPoint = Vector2.new(0.5, 0.5)
	oval.Position = UDim2.fromOffset(cx, cy)
	oval.Size = UDim2.fromOffset(w, h)
	oval.Parent = parent
	return oval
end

-- A dark ellipse on the floor under something.
function ShopLook.shadow(parent: Instance, cx: number, cy: number, w: number, h: number, opacity: number): ImageLabel
	return ShopLook.ellipse(parent, "Shadow", Color3.new(0, 0, 0), cx, cy, w, h, opacity)
end

-- A glowing ring on the floor that something stands on: a dark ellipse with a light rim.
function ShopLook.pedestal(parent: Instance, cx: number, cy: number, w: number, h: number, rim: Color3, thickness: number)
	ShopLook.ellipse(parent, "Pedestal rim", rim, cx, cy, w + 2 * thickness, h + 2 * thickness, 1)
	ShopLook.ellipse(parent, "Pedestal", Color3.fromHex("#150d2e"), cx, cy, w, h, 1)
end

-- A thin lighter edge just inside a card's ink edge: a colour, or a gradient of colours.
function ShopLook.innerEdge(card: GuiObject, radius: number, thickness: number, colours: { string } | Color3, opacity: number?): UIStroke
	local inner = ShopLook.blank(card, "Inner edge")
	inner.Position = UDim2.fromOffset(thickness, thickness)
	inner.Size = UDim2.new(1, -2 * thickness, 1, -2 * thickness)
	ShopLook.round(inner, math.max(radius - thickness, 2))
	local stroke = Instance.new("UIStroke")
	stroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	stroke.Thickness = thickness
	stroke.Transparency = 1 - (opacity or 1)
	stroke.Parent = inner
	if typeof(colours) == "Color3" then
		stroke.Color = colours
	else
		stroke.Color = WHITE
		ShopLook.paint(stroke :: any, colours, 90)
	end
	return stroke
end

-- Sets how solid everything under root is, 0 (gone) to 1 (as built), for fading a whole scene out. Collects what's
-- there when it's made, so make it once the scene is complete.
function ShopLook.fader(root: Instance): (number) -> ()
	local parts = {}
	for _, item in root:GetDescendants() do
		if item:IsA("TextLabel") or item:IsA("TextButton") then
			table.insert(parts, { item, "TextTransparency", item.TextTransparency })
			table.insert(parts, { item, "BackgroundTransparency", item.BackgroundTransparency })
		elseif item:IsA("ImageLabel") or item:IsA("ViewportFrame") then
			table.insert(parts, { item, "ImageTransparency", item.ImageTransparency })
		elseif item:IsA("UIStroke") then
			table.insert(parts, { item, "Transparency", item.Transparency })
		elseif item:IsA("Frame") then
			table.insert(parts, { item, "BackgroundTransparency", item.BackgroundTransparency })
		end
	end
	return function(opacity: number)
		for _, part in parts do
			(part[1] :: any)[part[2]] = 1 - (1 - part[3]) * opacity
		end
	end
end

export type Effects = {
	every: ((number) -> ()) -> (),
	step: (number) -> (),
	glow: (parent: Instance, colour: Color3, cx: number, cy: number, w: number, h: number, opacity: number, phase: number?) -> ImageLabel,
	rays: (parent: Instance, colour: Color3, cx: number, cy: number, radius: number, opacity: number, speed: number?) -> ImageLabel,
	sparkle: (parent: Instance, x: number, y: number, size: number, phase: number) -> Frame,
	embers: (parent: Instance, spots: { { number } }, rise: number) -> (),
	confetti: (parent: Instance, count: number, colours: { string }, w: number, h: number, seed: number) -> Frame,
}

-- A set of moving looks. Whoever makes it calls step(seconds) every frame while it shows.
function ShopLook.effects(): Effects
	local list: { (number) -> () } = {}
	local fx = {}

	function fx.every(effect: (number) -> ())
		table.insert(list, effect)
	end

	function fx.step(now: number)
		for _, effect in list do
			effect(now)
		end
	end

	-- A soft round glow that breathes.
	function fx.glow(parent: Instance, colour: Color3, cx: number, cy: number, w: number, h: number, opacity: number, phase: number?): ImageLabel
		local glow = ShopLook.image(parent, "glow", colour, cx, cy, w, h, opacity)
		local scale = Instance.new("UIScale")
		scale.Parent = glow
		fx.every(function(t)
			scale.Scale = 1 + 0.06 * math.sin(t * 2.4 + (phase or 0))
		end)
		return glow
	end

	-- Light rays from a point, turning slowly (speed: degrees a second).
	function fx.rays(parent: Instance, colour: Color3, cx: number, cy: number, radius: number, opacity: number, speed: number?): ImageLabel
		local burst = ShopLook.image(parent, "sunburst", colour, cx, cy, radius * 2, radius * 2, opacity)
		fx.every(function(t)
			burst.Rotation = (t * (speed or 7)) % 360
		end)
		return burst
	end

	-- A four-pointed sparkle that twinkles: grows, turns and shrinks away, then waits.
	function fx.sparkle(parent: Instance, x: number, y: number, size: number, phase: number): Frame
		local star = ShopLook.blank(parent, "Sparkle")
		star.AnchorPoint = Vector2.new(0.5, 0.5)
		ShopLook.at(star, x, y, size, size)
		star.ZIndex = 4
		for _, rotation in { 0, 90 } do
			local bar = ShopLook.block(star, "Bar", WHITE, 0, 0, 0, 0, 1, 0.5)
			bar.AnchorPoint = Vector2.new(0.5, 0.5)
			bar.Position = UDim2.fromScale(0.5, 0.5)
			bar.Size = UDim2.fromScale(1, 0.2)
			bar.Rotation = rotation
			bar.ZIndex = 4
			local taper = Instance.new("UIGradient")
			taper.Transparency = NumberSequence.new({
				NumberSequenceKeypoint.new(0, 1),
				NumberSequenceKeypoint.new(0.5, 0),
				NumberSequenceKeypoint.new(1, 1),
			})
			taper.Parent = bar
		end
		local scale = Instance.new("UIScale")
		scale.Parent = star
		fx.every(function(t)
			scale.Scale = math.max(0, math.sin(t * 1.7 + phase)) ^ 1.5
			star.Rotation = (t * 50 + phase * 40) % 360
		end)
		return star
	end

	-- Embers drifting up and fading, over and over. spots: { x, y, size } each; rise: how far one climbs.
	function fx.embers(parent: Instance, spots: { { number } }, rise: number)
		for index, spot in spots do
			local colour = Color3.fromHex(if index % 2 == 0 then "#ffd23f" else "#ff6a5a")
			local ember = ShopLook.block(parent, "Ember", colour, spot[1], spot[2], spot[3], spot[3], 0.8, 0.5)
			local speed = 0.18 + (index % 3) * 0.05
			fx.every(function(t)
				local u = (t * speed + index * 0.37) % 1
				ember.Position = UDim2.fromOffset(spot[1] + 10 * math.sin(u * 6 + index), spot[2] - u * rise)
				ember.BackgroundTransparency = 0.2 + 0.8 * u
			end)
		end
	end

	-- Confetti falling and tumbling across a w by h area, keeping clear of the middle third.
	function fx.confetti(parent: Instance, count: number, colours: { string }, w: number, h: number, seed: number): Frame
		local holder = ShopLook.blank(parent, "Confetti")
		holder.Size = UDim2.fromOffset(w, h)
		local random = Random.new(seed)
		for index = 1, count do
			local size = random:NextNumber(9, 20)
			local x = random:NextNumber(0, w)
			if x > w * 0.31 and x < w * 0.69 then
				x += if x < w / 2 then -w * 0.26 else w * 0.26
			end
			local y0 = random:NextNumber(0, h)
			local fall = random:NextNumber(70, 150)
			local spin = random:NextNumber(-220, 220)
			local sway = random:NextNumber(0, 6)
			local piece = ShopLook.block(holder, "Piece", Color3.fromHex(colours[(index - 1) % #colours + 1]), x, y0, size, size * 0.5, 0.92, 2)
			fx.every(function(t)
				piece.Position = UDim2.fromOffset(x + 14 * math.sin(t * 2 + sway), (y0 + fall * t) % (h + 40) - 20)
				piece.Rotation = spin * t
			end)
		end
		return holder
	end

	return fx
end

-- Big outlined words with a hard shadow under them, like the stickers in the design. Its middle sits at (cx, cy).
-- Sizes past Roblox's biggest text (100) are scaled up. Returns the holder, its UIScale (for slamming it in) and a
-- function that changes the words.
function ShopLook.words(parent: Instance, value: string, size: number, cx: number, cy: number, colours: ({ string } | Color3)?): (Frame, UIScale, (string) -> ())
	local holder = ShopLook.blank(parent, value)
	holder.AnchorPoint = Vector2.new(0.5, 0.5)
	holder.Position = UDim2.fromOffset(cx, cy)
	holder.Size = UDim2.fromOffset(10, 10)
	local scale = Instance.new("UIScale")
	scale.Parent = holder
	local textSize = math.min(size, 100)
	local body = ShopLook.blank(holder, "Body")
	body.AnchorPoint = Vector2.new(0.5, 0.5)
	body.Position = UDim2.fromScale(0.5, 0.5)
	body.Size = UDim2.fromOffset(1400, math.ceil(textSize * 1.3))
	if size > textSize then
		local grow = Instance.new("UIScale")
		grow.Scale = size / textSize
		grow.Parent = body
	end
	local shadow = UiKit.text(body, value, textSize, UiKit.INK)
	shadow.Name = "Shadow"
	shadow.Size = UDim2.fromScale(1, 1)
	shadow.Position = UDim2.fromOffset(0, math.max(2, math.round(textSize * 0.07)))
	local label = UiKit.text(body, value, textSize, if typeof(colours) == "Color3" then colours else nil)
	label.Name = "Words"
	label.Size = UDim2.fromScale(1, 1)
	if typeof(colours) == "table" then
		ShopLook.paint(label, colours)
	end
	return holder, scale, function(text: string)
		shadow.Text = text
		label.Text = text
	end
end

return ShopLook
