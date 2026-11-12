-- The Settings panel (Figma "Throw Eggs - Settings UI", mock-ups 18 to 18c, built in design/ui-mockups/build.py): the gear
-- button in the top right corner opens a panel with a Music slider, a Sound effects slider and a switch that hides other
-- players' dinos. A change applies at once on this client (SettingsState) and is sent to the server to be saved with the
-- player's data (SettingsService). Display and requests only: the server checks every value.
local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local DinoLife = require(ReplicatedStorage.Shared.Config.DinoLife)
local Settings = require(ReplicatedStorage.Shared.Config.Settings)
local UiKit = require(ReplicatedStorage.Shared.UiKit)
local SettingsState = require(script.Parent.SettingsState)

local SettingsController = {}

local player = Players.LocalPlayer

local PANEL = Vector2.new(680, 560)
local ROW_WIDTH = PANEL.X - 44
local GEAR_PADDING = 8 -- px the gear stays inside the top bar row, top and bottom together
local SLIDER_WIDTH = 230
local KNOB = 38
local SEND_DELAY = 0.25 -- seconds: a drag sends its latest value this often, and once more when the finger lifts


-- A dark rounded row with its icon box on the left (Figma "Settings · rows").
local function row(parent: Instance, icon: string, height: number, order: number): (Frame, TextLabel)
	local frame = Instance.new("Frame")
	frame.Name = "Row"
	frame.BackgroundColor3 = UiKit.DEEP
	frame.Size = UDim2.fromOffset(ROW_WIDTH, height)
	frame.LayoutOrder = order
	frame.Parent = parent
	UiKit.corner(frame, 20)
	UiKit.stroke(frame, 4)
	local box = Instance.new("Frame")
	box.BackgroundColor3 = Color3.fromRGB(18, 13, 34)
	box.AnchorPoint = Vector2.new(0, 0.5)
	box.Position = UDim2.new(0, 18, 0.5, 0)
	box.Size = UDim2.fromOffset(62, 62)
	box.Parent = frame
	UiKit.corner(box, 18)
	UiKit.stroke(box, 4)
	local glyph = UiKit.text(box, icon, 36)
	glyph.Name = "Icon"
	glyph.AnchorPoint = Vector2.new(0.5, 0.5)
	glyph.Position = UDim2.fromScale(0.5, 0.5)
	glyph.Size = UDim2.fromScale(1, 1)
	return frame, glyph
end

local function title(frame: Frame, value: string, size: number, width: number): TextLabel
	local label = UiKit.text(frame, value, size, nil, Enum.TextXAlignment.Left)
	label.Name = "Title"
	label.Position = UDim2.fromOffset(94, 0)
	label.Size = UDim2.new(0, width, 1, 0)
	return label
end

-- A volume slider that follows the finger or the mouse, in steps (Config/Settings). Calls onChange(percent) as it moves
-- and onRelease() when it lets go.
local function slider(parent: Instance, start: number, onChange: (number) -> (), onRelease: () -> ()): (Frame, (number) -> ())
	local holder = Instance.new("Frame")
	holder.Name = "Slider"
	holder.BackgroundTransparency = 1
	holder.AnchorPoint = Vector2.new(1, 0.5)
	holder.Position = UDim2.new(1, -90, 0.5, 0)
	holder.Size = UDim2.fromOffset(SLIDER_WIDTH, KNOB + 6)
	holder.Parent = parent

	local bar = Instance.new("Frame")
	bar.Name = "Bar"
	bar.AnchorPoint = Vector2.new(0, 0.5)
	bar.Position = UDim2.fromScale(0, 0.5)
	bar.Size = UDim2.new(1, 0, 0, 30)
	bar.BackgroundColor3 = Color3.fromRGB(18, 13, 34)
	bar.Parent = holder
	UiKit.corner(bar, 15)
	UiKit.stroke(bar, 4)
	local fill = Instance.new("Frame")
	fill.Name = "Fill"
	fill.Position = UDim2.fromOffset(4, 4)
	fill.Size = UDim2.new(0, 0, 1, -8)
	fill.Parent = bar
	UiKit.gradient(fill, "green")
	UiKit.corner(fill, 11)

	local knob = Instance.new("Frame")
	knob.Name = "Knob"
	knob.AnchorPoint = Vector2.new(0.5, 0.5)
	knob.Size = UDim2.fromOffset(KNOB, KNOB)
	knob.BackgroundColor3 = Color3.new(1, 1, 1)
	knob.Parent = holder
	UiKit.corner(knob, KNOB)
	UiKit.stroke(knob, 4)
	UiKit.gradient(knob, { "#ffffff", "#d9d2f2" })

	-- Shows `percent`: the green fill and the knob move together.
	local function show(percent: number)
		local share = percent / 100
		fill.Size = UDim2.new(share, -8 * share, 1, -8)
		fill.Visible = percent > 0
		knob.Position = UDim2.new(share, 4 - 8 * share, 0.5, 0) -- on the fill's end: the bar's inner edge is 4 from each side
	end
	show(start)

	local dragging = false
	local function follow(x: number)
		local share = math.clamp((x - bar.AbsolutePosition.X) / math.max(bar.AbsoluteSize.X, 1), 0, 1)
		local percent = math.clamp(math.floor(share * 100 / Settings.step + 0.5) * Settings.step, 0, 100)
		show(percent)
		onChange(percent)
	end
	holder.InputBegan:Connect(function(input)
		if input.UserInputType == Enum.UserInputType.MouseButton1 or input.UserInputType == Enum.UserInputType.Touch then
			dragging = true
			follow(input.Position.X)
		end
	end)
	UserInputService.InputChanged:Connect(function(input)
		if dragging and (input.UserInputType == Enum.UserInputType.MouseMovement or input.UserInputType == Enum.UserInputType.Touch) then
			follow(input.Position.X)
		end
	end)
	UserInputService.InputEnded:Connect(function(input)
		if dragging and (input.UserInputType == Enum.UserInputType.MouseButton1 or input.UserInputType == Enum.UserInputType.Touch) then
			dragging = false
			onRelease()
		end
	end)
	return holder, show
end

local function valueLabel(frame: Frame): TextLabel
	local label = UiKit.text(frame, "", 24, nil, Enum.TextXAlignment.Right)
	label.Name = "Value"
	label.AnchorPoint = Vector2.new(1, 0.5)
	label.Position = UDim2.new(1, -18, 0.5, 0)
	label.Size = UDim2.fromOffset(64, 40)
	return label
end

-- The ON/OFF switch (Figma "Switch"): the knob slides right and the face turns green.
local function toggle(parent: Instance, start: boolean, onChange: (boolean) -> ()): (TextButton, (boolean) -> ())
	local width, height = 124, 56
	local button = Instance.new("TextButton")
	button.Name = "Switch"
	button.AutoButtonColor = false
	button.Text = ""
	button.AnchorPoint = Vector2.new(1, 0.5)
	button.Position = UDim2.new(1, -18, 0.5, 0)
	button.Size = UDim2.fromOffset(width, height)
	button.Parent = parent
	UiKit.corner(button, height // 2)
	UiKit.stroke(button, 4)
	local word = UiKit.text(button, "", 24)
	word.Name = "Word"
	word.Size = UDim2.new(0, 56, 1, 0)
	local knob = Instance.new("Frame")
	knob.Name = "Knob"
	knob.AnchorPoint = Vector2.new(0, 0.5)
	knob.Size = UDim2.fromOffset(height - 14, height - 14)
	knob.BackgroundColor3 = Color3.new(1, 1, 1)
	knob.Parent = button
	UiKit.corner(knob, height)
	UiKit.stroke(knob, 4)
	UiKit.gradient(knob, { "#ffffff", "#d9d2f2" })

	local function show(on: boolean)
		local existing = button:FindFirstChildOfClass("UIGradient")
		if existing then
			existing:Destroy()
		end
		if on then
			UiKit.gradient(button, "green")
			word.Text = "ON"
			word.TextColor3 = Color3.new(1, 1, 1)
			word.Position = UDim2.fromOffset(12, 0)
			knob.Position = UDim2.new(1, -(height - 14) - 8, 0.5, 0)
		else
			button.BackgroundColor3 = Color3.fromRGB(18, 13, 34)
			word.Text = "OFF"
			word.TextColor3 = Color3.fromRGB(143, 133, 179)
			word.Position = UDim2.new(1, -word.Size.X.Offset - 12, 0, 0)
			knob.Position = UDim2.fromOffset(6, height / 2)
		end
	end
	show(start)
	local on = start
	button.Activated:Connect(function()
		on = not on
		show(on)
		onChange(on)
	end)
	return button, show
end

-- Hides or shows one dino model for this player: only other players' dinos standing on their own plot. Your own dinos,
-- the best monster on its pedestal and monsters carried on a head always stay. The owner plates, signs and racks are
-- not dinos, so they stay too. The tag over a hidden dino stays away too (MonsterTagController reads HiddenForMe).
local function applyHidden(model: Instance)
	if not model:IsA("Model") then
		return
	end
	local plotIndex = model:GetAttribute("PlotIndex")
	local hide = SettingsState.get("hideDinos") == true
		and plotIndex ~= nil
		and plotIndex ~= player:GetAttribute("PlotIndex")
		and model:GetAttribute("Carried") ~= true
		and model:GetAttribute("Stay") ~= true
	model:SetAttribute("HiddenForMe", hide) -- set on this client only; the server and other players never see it
	local modifier = if hide then 1 else 0
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			part.LocalTransparencyModifier = modifier
		end
	end
end

local function applyAllHidden()
	for _, model in CollectionService:GetTagged(DinoLife.tag) do
		applyHidden(model)
	end
end

function SettingsController.start()
	local remote = ReplicatedStorage:WaitForChild("SetSetting") :: RemoteEvent

	local gui = Instance.new("ScreenGui")
	gui.Name = "SettingsHud"
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 4 -- above the other panels
	gui.Parent = player:WaitForChild("PlayerGui")

	local panel = UiKit.panel(gui, { name = "SettingsPanel", width = PANEL.X, height = PANEL.Y, header = "dark", title = "Settings", icon = "⚙️" })

	-- The gear, small, in the top right corner on Roblox's own top bar row, level with its menu buttons, so it never
	-- sits on a panel [Owner, 2026-11-08: was bigger and lower, over the panels' headers].
	local corner = Instance.new("ScreenGui")
	corner.Name = "SettingsButtonHud"
	corner.ResetOnSpawn = false
	corner.ScreenInsets = Enum.ScreenInsets.TopbarSafeInsets -- the top bar's row, beside Roblox's buttons
	corner.DisplayOrder = 4
	corner.Parent = player:WaitForChild("PlayerGui")
	local gear = Instance.new("TextButton")
	gear.Name = "OpenSettings"
	gear.AutoButtonColor = false
	gear.Text = ""
	gear.AnchorPoint = Vector2.new(1, 0.5)
	gear.Position = UDim2.new(1, -4, 0.5, 0)
	gear.SizeConstraint = Enum.SizeConstraint.RelativeYY -- square: both sides follow the top bar's height
	gear.Size = UDim2.new(1, -GEAR_PADDING, 1, -GEAR_PADDING)
	gear.Parent = corner
	UiKit.gradient(gear, "dark")
	local round = Instance.new("UICorner")
	round.CornerRadius = UDim.new(0.3, 0)
	round.Parent = gear
	UiKit.stroke(gear, 2)
	local gearIcon = UiKit.text(gear, "⚙️", 24)
	gearIcon.AnchorPoint = Vector2.new(0.5, 0.5)
	gearIcon.Position = UDim2.fromScale(0.5, 0.5)
	gearIcon.Size = UDim2.fromScale(0.75, 0.75)
	gearIcon.TextScaled = true
	local press = Instance.new("UIScale")
	press.Parent = gear
	gear.MouseButton1Down:Connect(function()
		press.Scale = 0.92
	end)
	gear.MouseButton1Up:Connect(function()
		press.Scale = 1
	end)
	gear.MouseLeave:Connect(function()
		press.Scale = 1
	end)
	gear.Activated:Connect(function()
		UiKit.togglePanel(panel)
	end)

	-- The body: a list of dividers and rows.
	local list = Instance.new("Frame")
	list.Name = "List"
	list.BackgroundTransparency = 1
	list.Position = UDim2.fromOffset(22, 6)
	list.Size = UDim2.new(1, -44, 1, -12)
	list.Parent = panel.body
	local layout = Instance.new("UIListLayout")
	layout.Padding = UDim.new(0, 10)
	layout.SortOrder = Enum.SortOrder.LayoutOrder
	layout.Parent = list

	UiKit.divider(list, "Sound", ROW_WIDTH).LayoutOrder = 1

	-- Sends the newest value of a setting at most every SEND_DELAY, and at once when asked to.
	local pending: { [string]: boolean } = {}
	local function send(key: string)
		pending[key] = nil
		remote:FireServer(key, SettingsState.get(key))
	end
	local function queue(key: string)
		if not pending[key] then
			pending[key] = true
			task.delay(SEND_DELAY, function()
				if pending[key] then
					send(key)
				end
			end)
		end
	end

	-- Music and sound effects: icon, title, slider and a percentage.
	local function volumeRow(key: string, name: string, order: number, glyph: (number) -> string)
		local frame, icon = row(list, glyph(SettingsState.get(key)), 88, order)
		title(frame, name, 28, 190)
		local value = valueLabel(frame)
		local function showValue(percent: number)
			value.Text = if percent == 0 then "OFF" else `{percent}%`
			icon.Text = glyph(percent)
		end
		local _, showSlider = slider(frame, SettingsState.get(key), function(percent)
			showValue(percent)
			SettingsState.set(key, percent)
			queue(key)
		end, function()
			send(key)
		end)
		showValue(SettingsState.get(key))
		-- A value that arrives after the panel was built (the saved one): the slider follows.
		SettingsState.changed:Connect(function(changedKey, percent)
			if changedKey == key then
				showSlider(percent)
				showValue(percent)
			end
		end)
	end
	volumeRow("music", "Music", 2, function(percent)
		return if percent == 0 then "🔇" else "🎵"
	end)
	volumeRow("sfx", "Sound effects", 3, function(percent)
		return if percent == 0 then "🔇" else "🔊"
	end)

	UiKit.divider(list, "Bases", ROW_WIDTH).LayoutOrder = 4

	-- Hide other players' dinos.
	local frame = row(list, "🦖", 104, 5)
	local label = title(frame, "Hide other players' dinos", 26, 290)
	label.Size = UDim2.new(0, 290, 0, 36)
	label.Position = UDim2.fromOffset(94, 16)
	local note = UiKit.muted(frame, "Other bases look empty to you. Helps on slow phones.", 16, Enum.TextXAlignment.Left)
	note.Position = UDim2.fromOffset(94, 54)
	note.Size = UDim2.new(0, 290, 0, 42)
	local _, showSwitch = toggle(frame, SettingsState.get("hideDinos") == true, function(on)
		SettingsState.set("hideDinos", on)
		send("hideDinos")
	end)
	SettingsState.changed:Connect(function(key, value)
		if key == "hideDinos" then
			showSwitch(value == true)
			applyAllHidden()
		end
	end)

	if require(ReplicatedStorage.Shared.Config.Troll).enabled then -- hidden with the rest of it while false
		-- Let players leash me (Config/Troll playerLeash). On unless the player turns it off.
		UiKit.divider(list, "Trolling", ROW_WIDTH).LayoutOrder = 60
		local leashFrame = row(list, "🪢", 104, 61)
		local leashLabel = title(leashFrame, "Let players leash me", 26, 290)
		leashLabel.Size = UDim2.new(0, 290, 0, 36)
		leashLabel.Position = UDim2.fromOffset(94, 16)
		local leashNote = UiKit.muted(leashFrame, "Off: nobody can leash you and drag you around.", 16, Enum.TextXAlignment.Left)
		leashNote.Position = UDim2.fromOffset(94, 54)
		leashNote.Size = UDim2.new(0, 290, 0, 42)
		local _, showLeash = toggle(leashFrame, SettingsState.get("leashMe") ~= false, function(on)
			SettingsState.set("leashMe", on)
			send("leashMe")
		end)
		SettingsState.changed:Connect(function(key, value)
			if key == "leashMe" then
				showLeash(value ~= false)
			end
		end)
	end

	-- Hiding follows the dinos as they appear, and the player's own plot as it's given.
	for _, model in CollectionService:GetTagged(DinoLife.tag) do
		task.defer(applyHidden, model)
	end
	CollectionService:GetInstanceAddedSignal(DinoLife.tag):Connect(function(model)
		task.defer(applyHidden, model) -- a frame later, so a model that's still arriving has its parts
	end)
	player:GetAttributeChangedSignal("PlotIndex"):Connect(applyAllHidden)
end

return SettingsController
