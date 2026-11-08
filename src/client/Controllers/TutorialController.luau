-- The new-player tutorial (Config/Tutorial): the reference game's flow with no instructions on screen. Glowing sparks
-- run from the player to where the step happens and an arrow bobs over it, with a word or two only where the spot
-- alone doesn't say what to do; a bobbing chevron points at a button when the step happens in a panel. Until it's
-- over, every HUD but cash, power, training and throwing is hidden (Tutorial.hiddenHuds). A step is done as soon as
-- what it asks for is true, read from attributes the server keeps (TutorialService, TrainingService, PlotService), so
-- doing things early skips ahead. Display only: the server decides the two tutorial catches.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Eggs = require(ReplicatedStorage.Shared.Config.Eggs)
local Hub = require(ReplicatedStorage.Shared.Config.Hub)
local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local Throw = require(ReplicatedStorage.Shared.Config.Throw)
local Training = require(ReplicatedStorage.Shared.Config.Training)
local Tutorial = require(ReplicatedStorage.Shared.Config.Tutorial)
local UiKit = require(ReplicatedStorage.Shared.UiKit)
local TutorialGuide = require(script.Parent.TutorialGuide)

local player = Players.LocalPlayer
local guide = Tutorial.guide

local TutorialController = {}

local CHECK_INTERVAL = 0.2 -- seconds between checks of the step
local CARRY_GRACE = 2 -- seconds a tutorial catch may sit in the backpack before it's put on the head here
local POINTER_SIZE = Vector2.new(64, 72)
local POINTER_SCALE = 1.3 -- the pointer read small next to the HUD's big buttons
local EDGE_MARGIN = 90 -- design px: a button this close to the top gets the pointer from below
local EDGE_SHARE = 0.8 -- a button past this share of the screen's width, from either side, gets it from the side
local NEXT_EGG = Eggs[2] -- the egg the egg step points at
local THROW_ARROW_LIFT = Vector3.new(0, 6, 0) -- over the platform's THROW HERE sign, not through it

local function attr(name: string): any
	return player:GetAttribute(name)
end

-- Throwing or watching a reveal: ThrowController turns the HUDs off then (setHudsEnabled).
local function busy(): boolean
	local hud = player.PlayerGui:FindFirstChild("PlotHud") :: ScreenGui?
	return hud ~= nil and not hud.Enabled
end

local function training(): boolean
	return attr("IsTraining") == true
end

local function placed(state: any): boolean
	return state == "plot" or state == "gone"
end

local function barsFilled(): boolean
	return (attr("TrainingLevel") or 1) >= 1 + Tutorial.trainBars
end

-- When each step is done (Config/Tutorial steps).
local CHECKS = {
	throw = function()
		return (attr("TutorialThrows") or 0) >= 1 and not busy()
	end,
	place = function()
		return placed(attr("TutorialFirst"))
	end,
	upgrade = function()
		return (attr("TutorialUpgrades") or 0) >= 1
	end,
	train = function()
		return barsFilled() and not training()
	end,
	egg = function()
		return (attr("TutorialEggs") or 1) >= 2
	end,
	throw2 = function()
		return (attr("TutorialThrows") or 0) >= 2 and not busy()
	end,
	place2 = function()
		return placed(attr("TutorialSecond"))
	end,
	throw3 = function()
		return (attr("TutorialThrows") or 0) >= 3 and not busy()
	end,
}

local function findGui(path: { string }): GuiObject?
	local node: Instance? = player.PlayerGui
	for _, name in path do
		node = node and node:FindFirstChild(name)
	end
	return node :: GuiObject?
end

local function insidePlot(): boolean
	local plotIndex = attr("PlotIndex")
	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not plotIndex or not root then
		return false
	end
	local centre = Plot.positions[plotIndex]
	return math.abs(root.Position.X - centre.X) < Plot.size.X / 2 and math.abs(root.Position.Z - centre.Z) < Plot.size.Z / 2
end

-- What a step shows right now: where the world guide points (with sparks there or not), the word over the arrow, and
-- which button the screen pointer points at.
type View = { point: Vector3?, trail: boolean?, word: string?, button: GuiObject? }

local function viewOf(step): View
	local id = step.id
	local view: View = { word = step.word }
	local plotIndex = attr("PlotIndex")
	if id == "throw" or id == "throw2" or id == "throw3" then
		view.point, view.trail = Throw.lane.zoneCenter + THROW_ARROW_LIFT, true
	elseif id == "place" or id == "place2" then
		-- Inside the base the carried monster's own placing ghost says it all; outside, lead the player home.
		if plotIndex and not insidePlot() then
			view.point, view.trail = Plot.positions[plotIndex] + Vector3.new(0, Plot.size.Y / 2, 0), true
		end
	elseif id == "upgrade" and plotIndex then
		view.point, view.trail = Training.xpPadPosition(plotIndex), true
	elseif id == "train" then
		if training() then
			-- Enough bars: point at STOP so the player gets up for the next step.
			if barsFilled() then
				view.button = findGui({ "TrainingHud", "TrainingGroup", "Stop" })
			end
		elseif plotIndex then
			view.point, view.trail = Training.rackPosition(plotIndex), true
		end
	elseif id == "egg" then
		local panel = findGui({ "EggShopHud", "ShopPanel" })
		if panel and panel.Visible then
			local card = panel:FindFirstChild(NEXT_EGG.id, true)
			view.button = card and card:FindFirstChild("Action") :: GuiObject?
		elseif plotIndex then
			view.point, view.trail = Hub.padPosition(Hub.stallCFrame(Hub.eggStall, plotIndex)), true
		end
	end
	return view
end

-- Hides every HUD the tutorial doesn't use, every frame, since other controllers turn theirs back on.
local function hideHuds()
	local gui = player.PlayerGui
	for _, path in Tutorial.hiddenHuds do
		local node: Instance? = gui
		for name in string.gmatch(path, "[^/]+") do
			node = node and node:FindFirstChild(name)
		end
		if node then
			if node:IsA("ScreenGui") then
				node.Enabled = false
			elseif node:IsA("GuiObject") then
				node.Visible = false
			end
		end
	end
end

-- Gives back what hideHuds hid, once the tutorial is over (ThrowController and the others keep them from then on).
local function showHuds()
	local gui = player.PlayerGui
	for _, path in Tutorial.hiddenHuds do
		local node: Instance? = gui
		for name in string.gmatch(path, "[^/]+") do
			node = node and node:FindFirstChild(name)
		end
		if node then
			if node:IsA("ScreenGui") then
				-- The throw meter's luck offer turns itself on when it has something to show (LuckOfferController).
				node.Enabled = node.Name ~= "LuckOffer"
			elseif node:IsA("GuiObject") then
				node.Visible = true
			end
		end
	end
end

-- The screen pointer (Figma "UI Pointer"): two yolk chevrons with ink edges, drawn from bars so they need no image.
local function buildPointer(gui: ScreenGui)
	local scale = UiKit.scale() * POINTER_SCALE
	local pointer = Instance.new("Frame")
	pointer.Name = "Pointer"
	pointer.AnchorPoint = Vector2.new(0.5, 0.5)
	pointer.BackgroundTransparency = 1
	pointer.Size = UDim2.fromOffset(POINTER_SIZE.X * scale, POINTER_SIZE.Y * scale)
	pointer.Visible = false
	pointer.Parent = gui
	for index, top in { 0, 30 } do
		for side = -1, 1, 2 do
			local bar = Instance.new("Frame")
			bar.Name = `Chevron{index}`
			bar.AnchorPoint = Vector2.new(0.5, 0.5)
			bar.Position = UDim2.new(0.5, side * 14 * scale, 0, (top + 18) * scale) -- inner ends meet at the tip
			bar.Size = UDim2.fromOffset(38 * scale, (if index == 2 then 15 else 12) * scale)
			bar.Rotation = -side * 40 -- clockwise on the left: the two bars meet in a V pointing down
			bar.BorderSizePixel = 0
			bar.Parent = pointer
			UiKit.gradient(bar, { "FFE27A", "FF9F1C" })
			local round = Instance.new("UICorner")
			round.CornerRadius = UDim.new(0.5, 0)
			round.Parent = bar
			UiKit.stroke(bar, math.max(2, 4 * scale))
			if index == 1 then
				bar.BackgroundTransparency = 0.25
			end
		end
	end
	return pointer
end

-- Points at a button. The chevrons point down at it from above; at the screen's left or right edge (the HUD's button
-- columns, where the buttons stack) they point at it from the side, and near the top from below.
local DIRECTIONS = {
	down = { rotation = 0, step = Vector2.new(0, 1) },
	up = { rotation = 180, step = Vector2.new(0, -1) },
	right = { rotation = -90, step = Vector2.new(1, 0) },
	left = { rotation = 90, step = Vector2.new(-1, 0) },
}
local function placePointer(gui: ScreenGui, pointer: Frame, button: GuiObject?)
	local targetGui = button and button:FindFirstAncestorOfClass("ScreenGui")
	if not button or not targetGui or not targetGui.Enabled or button.AbsoluteSize.X < 1 or not button:IsDescendantOf(player.PlayerGui) then
		pointer.Visible = false
		return
	end
	local offset = targetGui.AbsolutePosition - gui.AbsolutePosition
	local position = button.AbsolutePosition + offset
	local size = button.AbsoluteSize
	local screen = gui.AbsoluteSize
	local scale = UiKit.scale()
	local centre = position + size / 2
	local way = if centre.X > screen.X * EDGE_SHARE then "right"
		elseif centre.X < screen.X * (1 - EDGE_SHARE) then "left"
		elseif position.Y < EDGE_MARGIN * scale then "up"
		else "down"
	local direction = DIRECTIONS[way]
	-- The tip touches the button's edge facing the pointer, then bobs toward it.
	local half = size / 2
	local edge = centre - direction.step * Vector2.new(half.X, half.Y)
	local bob = math.abs(math.sin(os.clock() * math.pi / 0.6)) * guide.pointerBob * scale
	local length = POINTER_SIZE.Y * scale * POINTER_SCALE
	local middle = edge - direction.step * (length / 2 + bob)
	pointer.AnchorPoint = Vector2.new(0.5, 0.5)
	pointer.Rotation = direction.rotation
	pointer.Position = UDim2.fromOffset(middle.X, middle.Y)
	pointer.Visible = true
end

function TutorialController.start()
	local remote = ReplicatedStorage:WaitForChild("TutorialRemotes"):WaitForChild("Step") :: RemoteEvent
	local plotRemotes = ReplicatedStorage:WaitForChild("PlotRemotes")
	TutorialGuide.start()

	while attr("TutorialStep") == nil do
		player:GetAttributeChangedSignal("TutorialStep"):Wait()
	end
	if attr("TutorialStep") >= Tutorial.doneStep then
		return -- finished before: nothing to show, ever
	end

	-- The pointer goes over the panels. ThrowController turns it off while throwing (setHudsEnabled).
	local pointerGui = Instance.new("ScreenGui")
	pointerGui.Name = "TutorialPointerHud"
	pointerGui.ResetOnSpawn = false
	pointerGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	pointerGui.DisplayOrder = 6
	pointerGui.Parent = player:WaitForChild("PlayerGui")
	local pointer = buildPointer(pointerGui)
	-- The word over the arrow (Config/Tutorial steps): screen text kept over the arrow's top each frame.
	local word = UiKit.text(pointerGui, "", 40, guide.colours.yolk)
	word.Name = "Word"
	word.AnchorPoint = Vector2.new(0.5, 1)
	word.Size = UDim2.fromOffset(320, 50)
	word.Visible = false
	local wordScale = Instance.new("UIScale")
	wordScale.Scale = UiKit.scale()
	wordScale.Parent = word

	local step = attr("TutorialStep")
	local shownStep = 0
	local finished = false
	local view: View? = nil
	local backpackSince: number? = nil

	-- Over without a word: the hidden HUDs simply come back.
	local function finish()
		finished = true
		pointerGui:Destroy()
		TutorialGuide.set(nil)
		remote:FireServer(Tutorial.doneStep)
		showHuds()
	end

	-- Back from a rejoin or a dropped reveal, a tutorial catch waits in the backpack: carry it so it can be placed (the
	-- server does it after a reveal, so wait a moment first; equipping what is already carried would put it away).
	local function nudge(id: string, now: number)
		local key = if id == "place" then attr("TutorialFirstKey") elseif id == "place2" then attr("TutorialSecondKey") else nil
		local state = if id == "place" then attr("TutorialFirst") elseif id == "place2" then attr("TutorialSecond") else nil
		if key and state == "backpack" and attr("HeldDino") ~= key and not busy() and not training() then
			backpackSince = backpackSince or now
			if now - backpackSince >= CARRY_GRACE then
				backpackSince = nil
				plotRemotes.DinoAction:FireServer("equip", key)
			end
		else
			backpackSince = nil
		end
	end

	local function check()
		if finished then
			return
		end
		step = math.max(step, attr("TutorialStep") or 1)
		while step < Tutorial.doneStep and CHECKS[Tutorial.steps[step].id]() do
			step += 1
		end
		if step >= Tutorial.doneStep then
			finish()
			return
		end
		if step ~= shownStep then
			shownStep = step
			remote:FireServer(step)
		end
		local current = Tutorial.steps[step]
		nudge(current.id, os.clock())
		view = viewOf(current)
		TutorialGuide.set(view.point, view.trail)
	end

	task.spawn(function()
		while not finished do
			check()
			task.wait(CHECK_INTERVAL)
		end
	end)
	RunService.RenderStepped:Connect(function()
		if finished then
			return
		end
		hideHuds()
		TutorialGuide.setHidden(busy() or training())
		placePointer(pointerGui, pointer, if view then view.button else nil)
		local top = TutorialGuide.arrowTop()
		local camera = workspace.CurrentCamera
		local text = view and view.point and view.word
		if top and camera and text then
			local spot, onScreen = camera:WorldToViewportPoint(top)
			local offset = pointerGui.AbsolutePosition -- the viewport counts from the very top, the GUI from under the bar
			word.Text = text
			word.Position = UDim2.fromOffset(spot.X - offset.X, spot.Y - offset.Y)
			word.Visible = onScreen
		else
			word.Visible = false
		end
	end)
end

return TutorialController
