-- The Power Limit [player feedback, 2026-11-08] (Config/PowerLimit): a LIMIT button beside Throw Power in the bottom left
-- opens a small panel where strong players set the farthest their eggs fly, so they can still land in earlier maps whose
-- monsters they haven't all caught. The panel has an ON/OFF switch, the limit as a big number with a slider, and a map
-- card between < and > buttons that jump the limit to the far end of the map before or after, showing how many of that
-- map's monsters you've caught. The values are saved settings (Config/Settings powerLimitOn, powerLimit): they change
-- at once here (SettingsState) and are sent to the server, which applies the limit to every throw (ThrowService).
-- Display and requests only.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local Dinos = require(ReplicatedStorage.Shared.Config.Dinos)
local Format = require(ReplicatedStorage.Shared.Format)
local HudStyle = require(ReplicatedStorage.Shared.HudStyle)
local Luck = require(ReplicatedStorage.Shared.Config.Luck)
local PowerLimit = require(ReplicatedStorage.Shared.Config.PowerLimit)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)
local UiKit = require(ReplicatedStorage.Shared.UiKit)
local IndexController = require(script.Parent.IndexController)
local SettingsState = require(script.Parent.SettingsState)

local PowerLimitController = {}

local player = Players.LocalPlayer

local PANEL = Vector2.new(620, 560)
local INNER = PANEL.X - 44 -- the rows' width
local SWITCH = Vector2.new(124, 56)
local KNOB = 40
local ARROW = 84 -- the < and > buttons' width
local OFF_TEXT = Color3.fromRGB(143, 133, 179)
local ALL_CAUGHT = Color3.fromRGB(141, 255, 90)

local function box(parent: Instance, y: number, height: number): Frame
	local frame = Instance.new("Frame")
	frame.BackgroundColor3 = UiKit.DEEP
	frame.Position = UDim2.fromOffset(22, y)
	frame.Size = UDim2.fromOffset(INNER, height)
	frame.Parent = parent
	UiKit.corner(frame, 20)
	UiKit.stroke(frame, 4)
	return frame
end

local function readable(color: Color3): Color3
	local _, _, brightness = color:ToHSV()
	return if brightness < 0.55 then color:Lerp(Color3.new(1, 1, 1), 0.5) else color
end

local function power(): number
	return player:GetAttribute("ThrowPower") or 0
end

-- The farthest the slider goes: your power, but no further than an egg can land.
local function sliderMax(): number
	return math.max(math.min(power(), Throw.farthestLanding()), PowerLimit.minimum + PowerLimit.step)
end

local function isOn(): boolean
	return SettingsState.get("powerLimitOn") == true
end

-- How far a PERFECT throw goes right now, limit and all.
local function landing(): number
	return math.min(PowerLimit.apply(power(), isOn(), SettingsState.get("powerLimit")), Throw.farthestLanding())
end

local function caught(biome): (number, number)
	local found, count = 0, 0
	for _, dino in Dinos[biome.id] or {} do
		count += 1
		if IndexController.discovered[dino.id] then
			found += 1
		end
	end
	return found, count
end

function PowerLimitController.start()
	local remote = ReplicatedStorage:WaitForChild("SetSetting") :: RemoteEvent

	local gui = Instance.new("ScreenGui")
	gui.Name = "PowerLimitHud" -- hidden with the other HUDs during throws (ThrowController setHudsEnabled)
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 4
	gui.Parent = player:WaitForChild("PlayerGui")

	local panel = UiKit.panel(gui, {
		name = "PowerLimitPanel",
		width = PANEL.X,
		height = PANEL.Y,
		header = "sky",
		title = "Power Limit",
		icon = "⚡",
		iconKey = "bolt",
	})
	local body = panel.body

	local function send(key: string)
		remote:FireServer(key, SettingsState.get(key))
	end
	local function setLimit(value: number)
		value = math.clamp(math.floor(value + 0.5), PowerLimit.minimum, sliderMax())
		SettingsState.set("powerLimit", value)
		if not isOn() then
			SettingsState.set("powerLimitOn", true)
			send("powerLimitOn")
		end
	end

	-- Row 1: the switch.
	local switchRow = box(body, 14, 96)
	local heading = UiKit.text(switchRow, "Limit my throws", 30, nil, Enum.TextXAlignment.Left)
	heading.Position = UDim2.fromOffset(24, 12)
	heading.Size = UDim2.new(1, -190, 0, 38)
	local note = UiKit.muted(switchRow, "Your eggs never fly past the limit.", 18, Enum.TextXAlignment.Left)
	note.Position = UDim2.fromOffset(24, 52)
	note.Size = UDim2.new(1, -190, 0, 28)

	local switch = Instance.new("TextButton")
	switch.Name = "Switch"
	switch.AutoButtonColor = false
	switch.Text = ""
	switch.AnchorPoint = Vector2.new(1, 0.5)
	switch.Position = UDim2.new(1, -20, 0.5, 0)
	switch.Size = UDim2.fromOffset(SWITCH.X, SWITCH.Y)
	switch.Parent = switchRow
	UiKit.corner(switch, SWITCH.Y // 2)
	UiKit.stroke(switch, 4)
	local switchGradient = UiKit.gradient(switch, "green")
	local switchWord = UiKit.text(switch, "", 24)
	switchWord.Size = UDim2.new(0, 56, 1, 0)
	local switchKnob = Instance.new("Frame")
	switchKnob.AnchorPoint = Vector2.new(0, 0.5)
	switchKnob.Size = UDim2.fromOffset(SWITCH.Y - 14, SWITCH.Y - 14)
	switchKnob.BackgroundColor3 = Color3.new(1, 1, 1)
	switchKnob.Parent = switch
	UiKit.corner(switchKnob, SWITCH.Y)
	UiKit.stroke(switchKnob, 4)
	UiKit.gradient(switchKnob, { "#ffffff", "#d9d2f2" })

	-- Row 2: the limit, big, and the slider.
	local amountRow = box(body, 124, 170)
	local amount = UiKit.text(amountRow, "", 64, UiKit.POWER)
	amount.Name = "Amount"
	amount.Position = UDim2.fromOffset(0, 6)
	amount.Size = UDim2.new(1, 0, 0, 76)
	local ofPower = UiKit.muted(amountRow, "", 20)
	ofPower.Position = UDim2.fromOffset(0, 80)
	ofPower.Size = UDim2.new(1, 0, 0, 26)

	local sliderHolder = Instance.new("Frame")
	sliderHolder.Name = "Slider"
	sliderHolder.BackgroundTransparency = 1
	sliderHolder.Position = UDim2.fromOffset(30, 114)
	sliderHolder.Size = UDim2.new(1, -60, 0, KNOB + 6)
	sliderHolder.Parent = amountRow
	local bar = Instance.new("Frame")
	bar.AnchorPoint = Vector2.new(0, 0.5)
	bar.Position = UDim2.fromScale(0, 0.5)
	bar.Size = UDim2.new(1, 0, 0, 28)
	bar.BackgroundColor3 = Color3.fromRGB(43, 36, 72)
	bar.Parent = sliderHolder
	UiKit.corner(bar, 14)
	UiKit.stroke(bar, 4)
	local fill = Instance.new("Frame")
	fill.Position = UDim2.fromOffset(4, 4)
	fill.Size = UDim2.new(0, 0, 1, -8)
	fill.Parent = bar
	local fillGradient = UiKit.gradient(fill, "sky")
	UiKit.corner(fill, 10)
	local knob = Instance.new("Frame")
	knob.AnchorPoint = Vector2.new(0.5, 0.5)
	knob.Size = UDim2.fromOffset(KNOB, KNOB)
	knob.BackgroundColor3 = Color3.new(1, 1, 1)
	knob.Parent = sliderHolder
	UiKit.corner(knob, KNOB)
	UiKit.stroke(knob, 4)
	UiKit.gradient(knob, { "#ffffff", "#d9d2f2" })

	-- Row 3: < map card >.
	local mapY = 308
	local prev = UiKit.button(body, "<", "sky", ARROW, 130, 56)
	prev.Name = "PreviousMap"
	prev.Position = UDim2.fromOffset(22, mapY)
	local nextButton = UiKit.button(body, ">", "sky", ARROW, 130, 56)
	nextButton.Name = "NextMap"
	nextButton.AnchorPoint = Vector2.new(1, 0)
	nextButton.Position = UDim2.new(1, -22, 0, mapY)
	local card = Instance.new("Frame")
	card.Name = "MapCard"
	card.BackgroundColor3 = UiKit.DEEP
	card.Position = UDim2.fromOffset(22 + ARROW + 12, mapY)
	card.Size = UDim2.fromOffset(INNER - 2 * (ARROW + 12), 130)
	card.Parent = body
	UiKit.corner(card, 20)
	UiKit.stroke(card, 4)
	local landsIn = UiKit.muted(card, "EGGS LAND IN", 18)
	landsIn.Position = UDim2.fromOffset(0, 10)
	landsIn.Size = UDim2.new(1, 0, 0, 24)
	local mapName = UiKit.text(card, "", 38)
	mapName.Position = UDim2.fromOffset(10, 34)
	mapName.Size = UDim2.new(1, -20, 0, 48)
	mapName.TextScaled = true
	local caughtLine = UiKit.text(card, "", 24)
	caughtLine.Position = UDim2.fromOffset(0, 88)
	caughtLine.Size = UDim2.new(1, 0, 0, 30)

	-- The HUD button, right of the Throw Power number (TrainingController builds that).
	local powerStat = player.PlayerGui:WaitForChild("TrainingHud"):WaitForChild("PowerStat")
	local powerValue = powerStat:WaitForChild("Value") :: TextLabel
	local statHeight = powerStat.Size.Y.Offset -- already scaled for small screens
	local pill = Instance.new("TextButton")
	pill.Name = "LimitButton"
	pill.AutoButtonColor = false
	pill.Text = ""
	pill.AnchorPoint = Vector2.new(0, 0.5)
	pill.AutomaticSize = Enum.AutomaticSize.X
	pill.Size = UDim2.fromOffset(0, math.floor(statHeight * 0.62))
	pill.Visible = false
	pill.Parent = powerStat
	UiKit.corner(pill, math.floor(statHeight * 0.2))
	UiKit.stroke(pill, math.max(2, math.floor(statHeight / 17)), HudStyle.INK)
	local pillGradient = UiKit.gradient(pill, "sun")
	-- The words sit on their own label: a UIGradient tints its own object's text too, not its children.
	local pillText = Instance.new("TextLabel")
	pillText.BackgroundTransparency = 1
	pillText.AutomaticSize = Enum.AutomaticSize.X
	pillText.Size = UDim2.fromScale(0, 1)
	pillText.FontFace = UiKit.FONT
	pillText.TextSize = math.floor(statHeight * 0.42)
	pillText.TextColor3 = UiKit.TEXT
	pillText.Parent = pill
	HudStyle.outline(pillText, math.max(1.5, statHeight / 24))
	local pillPadding = Instance.new("UIPadding")
	pillPadding.PaddingLeft = UDim.new(0, math.floor(statHeight * 0.22))
	pillPadding.PaddingRight = pillPadding.PaddingLeft
	pillPadding.Parent = pill

	local function setGradient(gradient: UIGradient, style: string)
		local pair = UiKit.GRADIENTS[style]
		gradient.Color = ColorSequence.new(Color3.fromHex(pair[1]), Color3.fromHex(pair[2]))
	end

	local function placePill()
		-- Right after the number's text, which TextScaled sizes to the label's height.
		local offset = powerValue.Position.X.Offset + powerValue.TextBounds.X + statHeight * 0.25
		pill.Position = UDim2.new(0, offset, 0.5, 0)
	end

	local function render()
		local on = isOn()
		local full = power()
		local limit = SettingsState.get("powerLimit") or 0
		local reach = landing()

		-- The switch.
		if on then
			switch.BackgroundColor3 = Color3.new(1, 1, 1) -- the gradient tints it
			switchGradient.Enabled = true
			switchWord.Text = "ON"
			switchWord.TextColor3 = UiKit.TEXT
			switchWord.Position = UDim2.fromOffset(12, 0)
			switchKnob.Position = UDim2.new(1, -(SWITCH.Y - 14) - 8, 0.5, 0)
		else
			switchGradient.Enabled = false
			switch.BackgroundColor3 = UiKit.DEEP
			switchWord.Text = "OFF"
			switchWord.TextColor3 = OFF_TEXT
			switchWord.Position = UDim2.new(1, -56 - 12, 0, 0)
			switchKnob.Position = UDim2.fromOffset(6, SWITCH.Y / 2)
		end

		-- The amount and the slider. Off, they show full power, greyed.
		local shown = if on then math.min(limit, full) else full
		amount.Text = Format.commas(math.floor(shown))
		amount.TextColor3 = if on then UiKit.POWER else OFF_TEXT
		ofPower.Text = if on then `of your {Format.commas(full)} power` else "Full power: no limit"
		local lowest, highest = PowerLimit.minimum, sliderMax()
		local share = math.clamp((math.min(shown, highest) - lowest) / (highest - lowest), 0, 1)
		fill.Size = UDim2.new(share, -8 * share, 1, -8)
		fill.Visible = share > 0
		setGradient(fillGradient, if on then "sky" else "grey")
		knob.Position = UDim2.new(share, 0, 0.5, 0)

		-- The map card, and which way the arrows can go.
		local biome = Luck.biomeAt(reach)
		local found, count = caught(biome)
		mapName.Text = string.upper(biome.name)
		mapName.TextColor3 = readable(biome.color)
		if count == 0 then
			caughtLine.Text = ""
		elseif found >= count then
			caughtLine.Text = "All caught!"
			caughtLine.TextColor3 = ALL_CAUGHT
		else
			caughtLine.Text = `{found} / {count} caught`
			caughtLine.TextColor3 = UiKit.GOLD
		end
		local stops = PowerLimit.stops(full)
		local canBack, canOn = false, false
		for _, stop in stops do
			canBack = canBack or stop.limit < reach - 1
			canOn = canOn or stop.limit > reach + 1
		end
		setGradient(prev:FindFirstChildOfClass("UIGradient"), if canBack then "sky" else "grey")
		setGradient(nextButton:FindFirstChildOfClass("UIGradient"), if canOn then "sky" else "grey")

		-- The HUD button: there once your power can skip the first map, or while a limit is on.
		pill.Visible = on or full >= PowerLimit.showFrom
		pillText.Text = if on then `LIMIT {Format.commas(math.floor(limit))}` else "LIMIT OFF"
		setGradient(pillGradient, if on then "sun" else "dark")
		placePill()
	end

	-- The slider follows the finger or the mouse; dragging it turns the limit on. Sent when it lets go.
	local dragging = false
	local function follow(x: number)
		local share = math.clamp((x - bar.AbsolutePosition.X) / math.max(bar.AbsoluteSize.X, 1), 0, 1)
		local lowest, highest = PowerLimit.minimum, sliderMax()
		local value = lowest + share * (highest - lowest)
		value = if share >= 1 then highest else math.floor(value / PowerLimit.step + 0.5) * PowerLimit.step
		setLimit(value)
	end
	sliderHolder.InputBegan:Connect(function(input)
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
			send("powerLimit")
		end
	end)

	-- < and >: the far end of the map before or after the one eggs land in now.
	local function jump(direction: number)
		local reach = landing()
		local stops = PowerLimit.stops(power())
		local target = nil
		if direction < 0 then
			for i = #stops, 1, -1 do
				if stops[i].limit < reach - 1 then
					target = stops[i].limit
					break
				end
			end
		else
			for _, stop in stops do
				if stop.limit > reach + 1 then
					target = stop.limit
					break
				end
			end
		end
		if target then
			setLimit(target)
			send("powerLimit")
		end
	end
	prev.Activated:Connect(function()
		jump(-1)
	end)
	nextButton.Activated:Connect(function()
		jump(1)
	end)

	-- Turning it on the first time puts the limit at the far end of the map before the one you reach now.
	switch.Activated:Connect(function()
		local turningOn = not isOn()
		if turningOn and (SettingsState.get("powerLimit") or 0) < PowerLimit.minimum then
			local stops = PowerLimit.stops(power())
			local start = if #stops >= 2 then stops[#stops - 1].limit else sliderMax()
			SettingsState.set("powerLimit", start)
			send("powerLimit")
		end
		SettingsState.set("powerLimitOn", turningOn)
		send("powerLimitOn")
	end)

	pill.Activated:Connect(function()
		if gui.Enabled then -- not mid-throw, when this HUD is hidden
			UiKit.togglePanel(panel)
		end
	end)

	SettingsState.changed:Connect(function(key)
		if key == "powerLimit" or key == "powerLimitOn" then
			render()
		end
	end)
	player:GetAttributeChangedSignal("ThrowPower"):Connect(render)
	powerValue:GetPropertyChangedSignal("TextBounds"):Connect(placePill)
	panel.frame:GetPropertyChangedSignal("Visible"):Connect(render) -- the caught counts may have changed since
	render()
end

return PowerLimitController
