-- The game's UI look, from the Figma file "Throw Eggs for Dinosaurs - Game UI" (page "UI design
-- v2"): chunky outlined text, glossy 3D buttons, dark panels with bright headers, rarity tiles with
-- spinning block models, and the motion that keeps it lively (pulsing buy buttons, wiggling tags,
-- panels popping in, numbers counting up). Client only.
--
-- Panels and cards are laid out in design pixels for a 1280x720 screen; a UIScale on each panel
-- fits it to the real screen.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")

local BlockModel = require(script.Parent.BlockModel)
local DinoModel = require(script.Parent.DinoModel)
local EggModel = require(script.Parent.EggModel)
local DinoStats = require(script.Parent.DinoStats)
local Dinos = require(script.Parent.Config.Dinos)
local Icons = require(script.Parent.Config.Icons)

local UiKit = {}

UiKit.INK = Color3.fromRGB(27, 18, 48)
UiKit.PANEL = Color3.fromRGB(31, 26, 51)
UiKit.PANEL_EDGE = Color3.fromRGB(47, 39, 80)
UiKit.ROW = Color3.fromRGB(43, 36, 72)
UiKit.DEEP = Color3.fromRGB(18, 13, 34)
UiKit.TEXT = Color3.new(1, 1, 1)
UiKit.MUTED = Color3.fromRGB(203, 191, 240)
UiKit.CASH = Color3.fromRGB(141, 255, 90)
UiKit.POWER = Color3.fromRGB(111, 227, 255)
UiKit.GOLD = Color3.fromRGB(255, 224, 102)
UiKit.FONT = Font.new("rbxasset://fonts/families/FredokaOne.json")
UiKit.BODY = Font.new("rbxasset://fonts/families/BuilderSans.json", Enum.FontWeight.Bold)

-- Top and bottom colours of every gradient the kit uses.
UiKit.GRADIENTS = {
	green = { "#8af25a", "#3fbf22" },
	blue = { "#6cc4ff", "#2f8ce6" },
	red = { "#ff7a6b", "#e8392f" },
	yellow = { "#ffe066", "#f5a815" },
	grey = { "#a9a3bd", "#77708f" },
	purple = { "#c58bff", "#8a46e8" },
	sun = { "#ffd23f", "#ff8a1f" },
	berry = { "#ff4fb8", "#b13bff" },
	jungle = { "#7ee35a", "#1fa860" },
	sky = { "#4fe0ff", "#2f7fe6" },
	gold = { "#ffe066", "#ff9a1f" },
	tagGold = { "#fff1a8", "#ffc21a" },
	dark = { "#4a3a75", "#2a2045" },
	unseen = { "#d9dce3", "#9aa1ae" },
}

-- One tier per monster of a map, most common first; the map's boss is mythic (Figma "Throw Eggs - Index & Inventory").
UiKit.RARITY_ORDER = { "common", "uncommon", "rare", "epic", "legendary", "mythic" }
UiKit.RARITY = {
	common = { "#e6e9ef", "#a9b1bf" },
	uncommon = { "#b4f59c", "#52c43f" },
	rare = { "#9ad9ff", "#2f8fe6" },
	epic = { "#dcb0ff", "#9150e8" },
	legendary = { "#ffe58a", "#ff9a1f" },
	mythic = { "#ff9ec4", "#e8265a" },
}
-- A dino's name written in its rarity (reveal, lucky catch banner, My Dinos).
UiKit.RARITY_TEXT = {
	common = "#ffffff",
	uncommon = "#8dff5a",
	rare = "#6fd0ff",
	epic = "#d4a6ff",
	legendary = "#ffcf3f",
	mythic = "#ff7aa8",
}

local DESIGN = Vector2.new(1280, 720)
local MIN_SCALE, MAX_SCALE = 0.45, 1.4
local SPIN_SECONDS = 6 -- one full turn of a model tile
local PULSE_SECONDS = 1.2
local PULSE_AMOUNT = 0.05
local WIGGLE_SECONDS = 2
local WIGGLE_DEGREES = 5
local VIEW_PITCH = math.rad(16)
local VIEW_FOV = 26

-- Things that move every frame: spinning cameras, pulsing buttons, wiggling tags.
local moving: { { kind: string, object: Instance, data: any } } = {}
local loopStarted = false

local function startLoop()
	if loopStarted then
		return
	end
	loopStarted = true
	RunService.Heartbeat:Connect(function()
		local t = os.clock()
		for i = #moving, 1, -1 do
			local entry = moving[i]
			if not entry.object.Parent then
				table.remove(moving, i)
			elseif entry.kind == "spin" then
				local d = entry.data
				local angle = d.yaw + t * 2 * math.pi / SPIN_SECONDS
				local offset = Vector3.new(math.sin(angle), 0, math.cos(angle)) * math.cos(VIEW_PITCH) + Vector3.new(0, math.sin(VIEW_PITCH), 0)
				d.camera.CFrame = CFrame.lookAt(d.target + offset * d.distance, d.target)
			elseif entry.kind == "pulse" then
				if not entry.object:GetAttribute("Pressed") then
					entry.data.Scale = 1 + PULSE_AMOUNT * math.sin(t * 2 * math.pi / PULSE_SECONDS + entry.object.AbsolutePosition.X * 0.01)
				end
			elseif entry.kind == "wiggle" then
				entry.object.Rotation = entry.data + WIGGLE_DEGREES * math.sin(t * 2 * math.pi / WIGGLE_SECONDS)
			end
		end
	end)
end

local function track(kind: string, object: Instance, data)
	startLoop()
	table.insert(moving, { kind = kind, object = object, data = data })
end

-- The area our ScreenGuis lay out in: under Roblox's top bar and, on phones, inside the safe area (clear of the
-- notch and the home bar), measured with an empty ScreenGui. Phones play in landscape, but while a game loads the
-- screen can still read as portrait (the Roblox app is portrait on phones), and a size read then made the whole HUD
-- PC-sized on an iPhone. So on touch screens the first call waits (up to 3 s) for a landscape size that holds still
-- for half a second, and a portrait size is always read the landscape way round.
local probe: ScreenGui? = nil
local settling: "no" | "waiting" | "done" = "no"

function UiKit.screenSize(): Vector2
	if not probe then
		local gui = Instance.new("ScreenGui")
		gui.Name = "ScreenProbe"
		gui.ResetOnSpawn = false
		gui.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")
		probe = gui
	end
	local gui = probe :: ScreenGui
	while gui.AbsoluteSize.Y <= 1 do
		task.wait()
	end
	local touch = UserInputService.TouchEnabled and not UserInputService.KeyboardEnabled
	if touch and settling == "no" then
		settling = "waiting"
		local started, last, stillSince = os.clock(), gui.AbsoluteSize, os.clock()
		while os.clock() - started < 3 do
			task.wait(0.1)
			local now = gui.AbsoluteSize
			if now ~= last then
				last, stillSince = now, os.clock()
			elseif now.X > now.Y and os.clock() - stillSince >= 0.5 then
				break
			end
		end
		settling = "done"
	end
	while settling == "waiting" do
		task.wait(0.1)
	end
	local size = gui.AbsoluteSize
	if touch and size.Y > size.X then
		size = Vector2.new(size.Y, size.X)
	end
	return size
end

-- How big design pixels are on this screen.
function UiKit.scale(): number
	local size = UiKit.screenSize()
	return math.clamp(math.min(size.X / DESIGN.X, size.Y / DESIGN.Y), MIN_SCALE, MAX_SCALE)
end

function UiKit.color(hex: string): Color3
	return Color3.fromHex(hex)
end

function UiKit.corner(object: GuiObject, radius: number)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0, radius)
	c.Parent = object
	return c
end

function UiKit.stroke(object: GuiObject, thickness: number, color: Color3?)
	local s = Instance.new("UIStroke")
	s.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	s.Color = color or UiKit.INK
	s.Thickness = thickness
	s.Parent = object
	return s
end

-- colours is a GRADIENTS/RARITY key or a {top, bottom} pair; rotation 90 runs top to bottom.
function UiKit.gradient(object: GuiObject, colours, rotation: number?)
	local pair = if typeof(colours) == "string" then (UiKit.GRADIENTS[colours] or UiKit.RARITY[colours]) else colours
	object.BackgroundColor3 = Color3.new(1, 1, 1)
	local g = Instance.new("UIGradient")
	g.Color = ColorSequence.new(Color3.fromHex(pair[1]), Color3.fromHex(pair[2]))
	g.Rotation = rotation or 90
	g.Parent = object
	return g
end

-- Outlined display text. Position and Size are up to the caller (default: full width, one line).
function UiKit.text(parent: Instance, value: string, size: number, color: Color3?, align: Enum.TextXAlignment?): TextLabel
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.FontFace = UiKit.FONT
	label.Text = value
	label.TextSize = size
	label.TextColor3 = color or UiKit.TEXT
	label.TextXAlignment = align or Enum.TextXAlignment.Center
	label.Size = UDim2.new(1, 0, 0, math.ceil(size * 1.25))
	label.Parent = parent
	local s = Instance.new("UIStroke")
	s.ApplyStrokeMode = Enum.ApplyStrokeMode.Contextual
	s.Color = UiKit.INK
	s.Thickness = math.max(2, math.floor(size / 9 + 0.5))
	s.LineJoinMode = Enum.LineJoinMode.Round
	s.Parent = label
	return label
end

-- Plain softer text for descriptions.
function UiKit.muted(parent: Instance, value: string, size: number, align: Enum.TextXAlignment?): TextLabel
	local label = Instance.new("TextLabel")
	label.BackgroundTransparency = 1
	label.FontFace = UiKit.BODY
	label.Text = value
	label.TextSize = size
	label.TextColor3 = UiKit.MUTED
	label.TextWrapped = true
	label.TextXAlignment = align or Enum.TextXAlignment.Center
	label.Size = UDim2.new(1, 0, 0, math.ceil(size * 1.3))
	label.Parent = parent
	return label
end

-- A glossy button: gradient face, ink border, outlined label, squashes while pressed.
function UiKit.button(parent: Instance, value: string, style: string, width: number, height: number, textSize: number?): TextButton
	local button = Instance.new("TextButton")
	button.AutoButtonColor = false
	button.Size = UDim2.fromOffset(width, height)
	button.FontFace = UiKit.FONT
	button.Text = value
	button.TextSize = textSize or math.floor(height * 0.48)
	button.TextColor3 = UiKit.TEXT
	button.Parent = parent
	UiKit.gradient(button, style)
	UiKit.corner(button, math.min(18, height // 3))
	UiKit.stroke(button, 4)
	local label = Instance.new("UIStroke")
	label.ApplyStrokeMode = Enum.ApplyStrokeMode.Contextual
	label.Color = UiKit.INK
	label.Thickness = if button.TextSize < 22 then 2 else math.floor(button.TextSize / 9 + 0.5)
	label.Parent = button
	local shine = Instance.new("Frame")
	shine.Name = "Shine"
	shine.BackgroundColor3 = Color3.new(1, 1, 1)
	shine.BackgroundTransparency = 0.72
	shine.BorderSizePixel = 0
	shine.Position = UDim2.new(0, 8, 0, 4)
	shine.Size = UDim2.new(1, -16, 0, math.max(3, height // 10))
	shine.Parent = button
	UiKit.corner(shine, 4)
	local scale = Instance.new("UIScale")
	scale.Parent = button
	button.MouseButton1Down:Connect(function()
		button:SetAttribute("Pressed", true)
		scale.Scale = 0.94
	end)
	local function release()
		button:SetAttribute("Pressed", false)
		scale.Scale = 1
	end
	button.MouseButton1Up:Connect(release)
	button.MouseLeave:Connect(release)
	return button
end

-- Changes a button's colours and text in place (e.g. BUY -> OWNED).
function UiKit.restyle(button: TextButton, value: string, style: string)
	button.Text = value
	local pair = UiKit.GRADIENTS[style]
	local g = button:FindFirstChildOfClass("UIGradient")
	if g and pair then
		g.Color = ColorSequence.new(Color3.fromHex(pair[1]), Color3.fromHex(pair[2]))
	end
end

-- Robux and claim buttons breathe so the eye finds them.
function UiKit.pulse(button: GuiObject)
	track("pulse", button, button:FindFirstChildOfClass("UIScale"))
end

-- A small tilted sticker (BEST DEAL!, x2, OWNED) that rocks gently around its tilt (default -4°).
-- style is a GRADIENTS key or a {top, bottom} pair.
function UiKit.tag(parent: Instance, value: string, style: string | { string }, textSize: number?, tilt: number?): Frame
	tilt = tilt or -4
	local tag = Instance.new("Frame")
	tag.AutomaticSize = Enum.AutomaticSize.X
	tag.Size = UDim2.fromOffset(0, (textSize or 20) + 14)
	tag.Rotation = tilt
	tag.Parent = parent
	UiKit.gradient(tag, style)
	UiKit.corner(tag, 12)
	UiKit.stroke(tag, 4)
	local pad = Instance.new("UIPadding")
	pad.PaddingLeft = UDim.new(0, 12)
	pad.PaddingRight = UDim.new(0, 12)
	pad.Parent = tag
	local label = UiKit.text(tag, value, textSize or 20, if style == "tagGold" then UiKit.INK else UiKit.TEXT)
	label.AutomaticSize = Enum.AutomaticSize.X
	label.Size = UDim2.fromScale(0, 1)
	if style == "tagGold" then
		label:FindFirstChildOfClass("UIStroke").Enabled = false
	end
	track("wiggle", tag, tilt)
	return tag
end

-- A section label between two rules: ——— Packs ———
function UiKit.divider(parent: Instance, value: string, width: number): Frame
	local row = Instance.new("Frame")
	row.BackgroundTransparency = 1
	row.Size = UDim2.fromOffset(width, 52)
	row.Parent = parent
	for _, side in { 0, 1 } do
		local rule = Instance.new("Frame")
		rule.BackgroundColor3 = Color3.fromRGB(58, 48, 96)
		rule.BorderSizePixel = 0
		rule.AnchorPoint = Vector2.new(side, 0.5)
		rule.Position = UDim2.new(side, 0, 0.5, 0)
		rule.Size = UDim2.new(0.5, -110, 0, 5)
		rule.Parent = row
		UiKit.corner(rule, 3)
	end
	local pill = Instance.new("Frame")
	pill.AnchorPoint = Vector2.new(0.5, 0.5)
	pill.Position = UDim2.fromScale(0.5, 0.5)
	pill.Size = UDim2.fromOffset(196, 42)
	pill.BackgroundColor3 = UiKit.PANEL_EDGE
	pill.Parent = row
	UiKit.corner(pill, 16)
	UiKit.stroke(pill, 4)
	local label = UiKit.text(pill, value, 26)
	label.Size = UDim2.fromScale(1, 1)
	return row
end

-- A 3D block model shown live in the UI. spin turns the camera around it; silhouette shows it black.
-- The image for an icon key from Config/Icons, or nil while that key has no uploaded image yet.
-- options: position, size, anchor (all optional; the default fills the parent).
function UiKit.iconImage(parent: Instance, key: string, options): ImageLabel?
	local id = Icons[key]
	if not id or id == "" then
		return nil
	end
	options = options or {}
	local image = Instance.new("ImageLabel")
	image.Name = key
	image.BackgroundTransparency = 1
	image.Image = id
	image.ScaleType = Enum.ScaleType.Fit
	image.AnchorPoint = options.anchor or Vector2.zero
	image.Position = options.position or UDim2.fromScale(0, 0)
	image.Size = options.size or UDim2.fromScale(1, 1)
	image.Parent = parent
	return image
end

-- A pack's or pass's picture: its image from Config/Icons when set, else the 3D model's viewport.
-- options are the viewport's (position, size, spin, yaw), and the image takes the position and size.
function UiKit.art(parent: Instance, key: string, modelName: string, options): GuiObject
	return UiKit.iconImage(parent, key, { position = options.position, size = options.size }) or UiKit.viewport(parent, modelName, options)
end

local function newViewport(parent: Instance, options): ViewportFrame
	local frame = Instance.new("ViewportFrame")
	frame.BackgroundTransparency = 1
	frame.Size = options.size or UDim2.fromScale(1, 1)
	frame.Position = options.position or UDim2.new()
	frame.Ambient = Color3.fromRGB(150, 150, 172)
	frame.LightColor = Color3.new(1, 1, 1)
	frame.LightDirection = Vector3.new(-0.5, -1, -0.7)
	if options.silhouette then
		frame.ImageColor3 = Color3.fromRGB(21, 16, 42)
		frame.Ambient = Color3.new(0, 0, 0)
		frame.LightColor = Color3.new(0, 0, 0)
	end
	frame.Parent = parent
	return frame
end

-- Points a viewport's camera at target from yaw (round the upright, 0 looking along -Z), a little from above, far
-- enough back to fit a ball of this radius. spin turns it round slowly, starting from yaw.
local function aim(frame: ViewportFrame, target: Vector3, radius: number, yaw: number, options)
	local camera = Instance.new("Camera")
	camera.FieldOfView = VIEW_FOV
	camera.Parent = frame
	frame.CurrentCamera = camera
	local distance = radius * (options.zoom or 1.12) / math.tan(math.rad(VIEW_FOV / 2))
	local data = { camera = camera, target = target, distance = distance, yaw = yaw }
	-- Placed once even if it spins, so it looks right on the first frame.
	local offset = Vector3.new(math.sin(yaw), 0, math.cos(yaw)) * math.cos(VIEW_PITCH) + Vector3.new(0, math.sin(VIEW_PITCH), 0)
	camera.CFrame = CFrame.lookAt(target + offset * distance, target)
	if options.spin then
		track("spin", frame, data)
	end
end

-- A block model from ModelBlueprints, or for an egg (egg_<id>) its Blender model when the place has one (EggModel).
function UiKit.viewport(parent: Instance, modelName: string, options): ViewportFrame
	options = options or {}
	local frame = newViewport(parent, options)
	local eggId = string.match(modelName, "^egg_(.+)$")
	local blender = if eggId then EggModel.clone(eggId) else nil
	local model, target, e
	if blender then
		blender:PivotTo(CFrame.new()) -- its foot at the middle of the view's floor
		local box, size = blender:GetBoundingBox()
		model, target, e = blender, box.Position, size
	else
		model = BlockModel.build(modelName, Vector3.zero, options.tint, options.tintAmount)
		if not model then
			return frame
		end
		e = BlockModel.extents(modelName)
		target = Vector3.new(0, e.Y / 2, 0)
	end
	model.Parent = frame
	local radius = math.max(math.sqrt(e.X * e.X + e.Z * e.Z) / 2, e.Y / 2)
	local yaw = (options.yaw or math.rad(120)) + (if options.spin then math.random() * 2 * math.pi else 0) -- front three-quarter view
	aim(frame, target, radius, yaw, options)
	return frame
end

local MONSTER_TURN = math.rad(40) -- how far round from straight in front a monster is seen, towards its right
local MONSTER_MARGIN = 1.04 -- room left round a monster in its view

-- How far back the camera stands for a box of this size, seen from yaw, to just fit a view this many times wider
-- than tall. A turning view fits the box from every side.
local function fitDistance(size: Vector3, yaw: number, aspect: number, spin: boolean?): number
	local tanTall = math.tan(math.rad(VIEW_FOV / 2))
	local across, deep
	if spin then
		across = math.sqrt(size.X * size.X + size.Z * size.Z)
		deep = across
	else
		local s, c = math.abs(math.sin(yaw)), math.abs(math.cos(yaw))
		across = size.X * c + size.Z * s
		deep = size.X * s + size.Z * c
	end
	local tall = size.Y * math.cos(VIEW_PITCH) + deep * math.sin(VIEW_PITCH)
	-- Its near side is closer to the camera than its centre, so it looks a little bigger: step back a bit for that.
	return math.max(tall / 2 / tanTall, across / 2 / (tanTall * aspect)) + deep / 4
end

-- A monster's real model shown live in the UI, the same one that stands on the bases (DinoModel: its imported
-- Blender model, else its block model), seen from the front three-quarters and filling its view. options:
-- position, size, aspect (the view's width over its height, 1 if left out), zoom, spin, silhouette, and mutation
-- (a colour mutation's id, which recolours its skin as on a base).
-- live puts it in a WorldModel and returns it too, for the caller to animate (the Shop hands it to
-- DinoLifeController.showcase); turn changes how far round it's seen from (radians, default MONSTER_TURN).
function UiKit.monster(parent: Instance, dinoId: string, options): (ViewportFrame, Model)
	options = options or {}
	local frame = newViewport(parent, options)
	local model = DinoModel.build(dinoId, options.mutation, Vector3.zero, 1)
	if options.live then
		local world = Instance.new("WorldModel")
		world.Parent = frame
		model.Parent = world
	else
		model.Parent = frame
	end
	local centre, size = DinoModel.visibleBox(model)
	local yaw = (if DinoModel.facesBack(model) then 0 else math.pi) - (options.turn or MONSTER_TURN)
	local distance = fitDistance(size, yaw, options.aspect or 1, options.spin) * MONSTER_MARGIN * (options.zoom or 1)
	-- aim takes a radius; this one stands the camera at exactly that distance.
	aim(frame, centre, distance * math.tan(math.rad(VIEW_FOV / 2)), yaw, { zoom = 1, spin = options.spin })
	return frame, model
end

-- Which rarity tier a dino is: its place in its biome's list, most common first.
function UiKit.rarityOf(dinoId: string): string
	if DinoStats.special(dinoId) then
		return UiKit.RARITY_ORDER[#UiKit.RARITY_ORDER]
	end
	for _, list in Dinos do
		for index, dino in list do
			if dino.id == dinoId then
				return UiKit.RARITY_ORDER[math.min(index, #UiKit.RARITY_ORDER)]
			end
		end
	end
	return "common"
end

-- A rarity-coloured tile with a spinning dino, its name on top and optional text at the bottom.
-- found = false shows a black silhouette and "???". mutation (an id) recolours it.
function UiKit.dinoTile(parent: Instance, dinoId: string, name: string, width: number, height: number, options)
	options = options or {}
	local found = options.found ~= false
	local tile = Instance.new("Frame")
	tile.Size = UDim2.fromOffset(width, height)
	tile.Parent = parent
	UiKit.gradient(tile, if found then (options.rarity or UiKit.rarityOf(dinoId)) else "unseen")
	UiKit.corner(tile, math.min(20, height // 5))
	UiKit.stroke(tile, 4)
	local view = UiKit.monster(tile, dinoId, {
		spin = found and options.spin ~= false,
		silhouette = not found,
		mutation = options.mutation,
		position = UDim2.fromOffset(4, options.nameSize and options.nameSize - 2 or 0),
		size = UDim2.new(1, -8, 1, -(options.nameSize or 0) - (options.bottom and 14 or 0)),
	})
	view.ZIndex = 1
	if options.nameSize then
		local label = UiKit.text(tile, if found then name else "???", options.nameSize)
		label.Position = UDim2.fromOffset(0, 6)
		label.ZIndex = 2
	end
	if options.bottom then
		local bottom = UiKit.text(tile, options.bottom, options.bottomSize or 16)
		bottom.AnchorPoint = Vector2.new(0, 1)
		bottom.Position = UDim2.new(0, 0, 1, -4)
		bottom.ZIndex = 2
	end
	return tile
end

-- A centred panel with a bright header, a title and a close button. Returns {gui-facing parts}.
function UiKit.panel(gui: ScreenGui, options)
	local width, height = options.width, options.height
	local frame = Instance.new("Frame")
	frame.Name = options.name or "Panel"
	frame.AnchorPoint = options.anchor or Vector2.new(0.5, 0.5)
	frame.Position = options.position or UDim2.fromScale(0.5, 0.5)
	frame.Size = UDim2.fromOffset(width, height)
	frame.BackgroundColor3 = UiKit.PANEL
	frame.Visible = false
	frame.Parent = gui
	UiKit.corner(frame, 30)
	UiKit.stroke(frame, 5)
	local scale = Instance.new("UIScale")
	scale.Scale = UiKit.scale()
	scale.Parent = frame

	local edge = Instance.new("Frame")
	edge.BackgroundTransparency = 1
	edge.Position = UDim2.fromOffset(4, 4)
	edge.Size = UDim2.new(1, -8, 1, -8)
	edge.Parent = frame
	UiKit.corner(edge, 26)
	UiKit.stroke(edge, 4, UiKit.PANEL_EDGE)

	local header = Instance.new("Frame")
	header.Name = "Header"
	header.Size = UDim2.new(1, 0, 0, 88)
	header.ClipsDescendants = true
	header.Parent = frame
	UiKit.gradient(header, options.header or "sun", 0)
	UiKit.corner(header, 28)
	-- Square off the header's bottom corners and draw its ink edge.
	local filler = Instance.new("Frame")
	filler.Name = "Filler"
	filler.BorderSizePixel = 0
	filler.Position = UDim2.new(0, 0, 1, -30)
	filler.Size = UDim2.new(1, 0, 0, 30)
	filler.Parent = header
	UiKit.gradient(filler, options.header or "sun", 0)
	local line = Instance.new("Frame")
	line.BackgroundColor3 = UiKit.INK
	line.BorderSizePixel = 0
	line.Position = UDim2.new(0, 0, 1, -5)
	line.Size = UDim2.new(1, 0, 0, 5)
	line.ZIndex = 3
	line.Parent = header
	for i = 0, 4 do
		local stripe = Instance.new("Frame")
		stripe.BackgroundColor3 = Color3.new(1, 1, 1)
		stripe.BackgroundTransparency = 0.8
		stripe.BorderSizePixel = 0
		stripe.Rotation = 25
		stripe.Position = UDim2.new(0.55, i * 52, 0, -40)
		stripe.Size = UDim2.fromOffset(26, 170)
		stripe.Parent = header
	end
	-- The header's icon: its image from Config/Icons when there is one, else the emoji in the title.
	local image = options.iconKey and UiKit.iconImage(header, options.iconKey, { position = UDim2.fromOffset(24, 15), size = UDim2.fromOffset(58, 58) })
	if image then
		image.ZIndex = 2
	end
	local title = UiKit.text(header, (options.icon and not image and options.icon .. " " or "") .. options.title, options.titleSize or 46, nil, Enum.TextXAlignment.Left)
	title.Position = UDim2.fromOffset(image and 96 or 26, 14)
	title.Size = UDim2.new(1, image and -184 or -120, 0, 58)
	title.ZIndex = 2

	-- On phones the X fills the header, so it's still a finger-sized target once the panel is scaled down.
	local bigClose = UserInputService.TouchEnabled and not UserInputService.KeyboardEnabled
	local close = UiKit.button(frame, "X", "red", if bigClose then 84 else 58, if bigClose then 84 else 58, if bigClose then 46 else 30)
	close.Name = "Close"
	close.AnchorPoint = Vector2.new(1, 0)
	close.Position = if bigClose then UDim2.new(1, -6, 0, 2) else UDim2.new(1, -16, 0, 14)
	close.ZIndex = 4

	local body = Instance.new("Frame")
	body.Name = "Body"
	body.BackgroundTransparency = 1
	body.Position = UDim2.fromOffset(0, 92)
	if bigClose then
		title.Size += UDim2.fromOffset(-8, 0)
	end
	body.Size = UDim2.new(1, 0, 1, -92)
	body.Parent = frame

	-- closeInset: how far the X reaches in from the panel's right edge, for anything placed beside it in the header.
	local panel = { frame = frame, body = body, close = close, closeInset = if bigClose then 90 else 74, scale = scale, header = header }
	close.Activated:Connect(function()
		UiKit.closePanel(panel)
	end)
	return panel
end

-- Recolours a panel's header, e.g. to the rarity of the dino it shows.
function UiKit.setHeader(panel, style: string)
	local pair = UiKit.GRADIENTS[style] or UiKit.RARITY[style]
	local colours = ColorSequence.new(Color3.fromHex(pair[1]), Color3.fromHex(pair[2]))
	for _, part in { panel.header, panel.header.Filler } do
		part:FindFirstChildOfClass("UIGradient").Color = colours
	end
end

-- Opens with a small pop (85% to full size, overshooting a little).
-- One panel at a time: opening one closes any other that's open, so they never stack inside each other. A panel
-- with keepOpen set (Welcome back, closed only by its CLAIM) is left alone.
local openPanels = {}

function UiKit.openPanel(panel)
	for other in openPanels do
		if other ~= panel and not other.keepOpen then
			UiKit.closePanel(other)
		end
	end
	openPanels[panel] = true
	local full = UiKit.scale()
	panel.frame.Visible = true
	panel.scale.Scale = full * 0.85
	TweenService:Create(panel.scale, TweenInfo.new(0.25, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = full }):Play()
end

function UiKit.closePanel(panel)
	openPanels[panel] = nil
	panel.frame.Visible = false
end

function UiKit.togglePanel(panel)
	if panel.frame.Visible then
		UiKit.closePanel(panel)
	else
		UiKit.openPanel(panel)
	end
end

-- A vertical scrolling list that grows with its content.
function UiKit.scrollList(parent: Instance, position: UDim2, size: UDim2, gap: number): ScrollingFrame
	local list = Instance.new("ScrollingFrame")
	list.BackgroundTransparency = 1
	list.BorderSizePixel = 0
	list.Position = position
	list.Size = size
	list.AutomaticCanvasSize = Enum.AutomaticSize.Y
	list.CanvasSize = UDim2.new()
	list.ScrollBarThickness = 10
	list.ScrollBarImageColor3 = Color3.fromRGB(91, 74, 140)
	list.ScrollingDirection = Enum.ScrollingDirection.Y
	list.Parent = parent
	local layout = Instance.new("UIListLayout")
	layout.Padding = UDim.new(0, gap)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
	layout.Parent = list
	local pad = Instance.new("UIPadding")
	pad.PaddingTop = UDim.new(0, 6)
	pad.PaddingBottom = UDim.new(0, 12)
	pad.Parent = list
	return list
end

-- Rolls a number label up from `from` to `to`, writing it with format.
function UiKit.countUp(label: TextLabel, from: number, to: number, seconds: number, format: (number) -> string)
	local value = Instance.new("NumberValue")
	value.Value = from
	value.Changed:Connect(function(v)
		label.Text = format(v)
	end)
	label.Text = format(from)
	local tween = TweenService:Create(value, TweenInfo.new(seconds, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Value = to })
	tween.Completed:Once(function()
		label.Text = format(to)
		value:Destroy()
	end)
	tween:Play()
end

return UiKit
