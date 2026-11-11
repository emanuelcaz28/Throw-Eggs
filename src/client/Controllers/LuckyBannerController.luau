-- The lucky catch banner (mock-ups 12 and 12b in design/ui-mockups/build.py): when anyone in the
-- server catches something rare, a big banner drops in at the top centre for everyone, even while
-- training. A clover overlaps its left side, a sticker with the luck tier sits on the top right,
-- and the panel takes the tier's colour. The look is CatchBannerLook's, shared with your own smaller
-- "YOU CAUGHT" banner.
--
-- One banner at a time; a rarer catch waiting in line goes first. Banners wait while your own
-- egg flies and your own reveal plays, and your own catch is queued once its reveal is over. The banner
-- sits over the top centre, where the flight shows the luck and the world's name: one already up when
-- your egg leaves the hand slides away at once and comes back afterwards [player feedback, 2026-11-08].
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

local Catch = require(ReplicatedStorage.Shared.Config.Catch)
local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local DinoStats = require(ReplicatedStorage.Shared.DinoStats)
local Format = require(ReplicatedStorage.Shared.Format)
local UiKit = require(ReplicatedStorage.Shared.UiKit)
local CatchBannerLook = require(script.Parent.CatchBannerLook)
local RevealController = require(script.Parent.RevealController)
local ThrowCinematic = require(script.Parent.ThrowCinematic)

local player = Players.LocalPlayer
local settings = Reveal.luckyBanner

local LuckyBannerController = {}

local HEIGHT = CatchBannerLook.HEIGHT

local hud = nil
local queue = {}
local showing = false

local function tween(instance: Instance, time: number, goal, style: Enum.EasingStyle?, direction: Enum.EasingDirection?)
	local created = TweenService:Create(
		instance,
		TweenInfo.new(time, style or Enum.EasingStyle.Quad, direction or Enum.EasingDirection.Out),
		goal
	)
	created:Play()
	return created
end

local function buildGui()
	local gui = Instance.new("ScreenGui")
	gui.Name = "LuckyBannerHud"
	gui.IgnoreGuiInset = true
	gui.ResetOnSpawn = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.DisplayOrder = 9 -- over the HUD and panels, under the reveal
	gui.Parent = player:WaitForChild("PlayerGui")

	local parts = CatchBannerLook.build(gui, "LuckyBanner", UiKit.scale())
	local clover = UiKit.art(parts.banner, "clover", "clover", {
		position = parts.artPosition,
		size = UDim2.fromOffset(CatchBannerLook.ART_SIZE, CatchBannerLook.ART_SIZE),
	})
	clover.ZIndex = 3
	parts.cloverModel = clover:FindFirstChildOfClass("Model")
	return parts
end

-- The catch line: size, mutation, then the dino, e.g. "HUGE DIAMOND SPINOSAURUS".
local function catchName(announcement): string
	local parts = {}
	local size = DinoStats.findOption(Catch.sizes, announcement.size)
	local mutation = DinoStats.findOption(Catch.mutations, announcement.mutation)
	if size then
		table.insert(parts, size.name)
	end
	if mutation then
		table.insert(parts, mutation.name)
	end
	table.insert(parts, string.upper(announcement.name))
	return table.concat(parts, " ")
end

-- The clover lands with a half turn.
local function spinClover()
	local model = hud.cloverModel
	if not model then
		return
	end
	local start = model:GetPivot()
	local began = os.clock()
	local connection
	connection = RunService.RenderStepped:Connect(function()
		local t = math.min((os.clock() - began) / settings.dropTime, 1)
		local eased = TweenService:GetValue(t, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
		model:PivotTo(start * CFrame.Angles(0, math.pi * (eased - 1), 0))
		if t >= 1 then
			connection:Disconnect()
		end
	end)
end

local function show(announcement)
	local stopRainbow = CatchBannerLook.paint(
		hud,
		`{announcement.player} CAUGHT`,
		catchName(announcement),
		announcement.id,
		`1 in {Format.short(announcement.oneIn)}`,
		announcement.oneIn
	)

	local hidden = UDim2.new(0.5, 0, 0, -(HEIGHT + 20) * hud.scale.Scale)
	hud.banner.Position = hidden
	hud.banner.Visible = true
	spinClover()
	tween(hud.banner, settings.dropTime, { Position = UDim2.new(0.5, 0, 0, 6) }, Enum.EasingStyle.Back)
	local waited = 0
	local cut = false
	while waited < settings.dropTime + settings.holdTime do
		if ThrowCinematic.isLuckPanelShown() then
			cut = true
			break
		end
		waited += task.wait()
	end
	tween(hud.banner, settings.leaveTime, { Position = hidden }, Enum.EasingStyle.Quad, Enum.EasingDirection.In).Completed:Wait()
	hud.banner.Visible = false
	stopRainbow()
	return cut
end

local function mustWait(): boolean
	return RevealController.isPlaying() or ThrowCinematic.isLuckPanelShown()
end

-- Shows queued banners one after another, rarest first, never during your own reveal.
local function runQueue()
	if showing then
		return
	end
	showing = true
	task.spawn(function()
		while #queue > 0 do
			while mustWait() do
				task.wait(0.2)
			end
			local announcement = table.remove(queue, 1)
			if show(announcement) then
				-- Cut short by a throw: shown again in full once the throw and its reveal are over.
				table.insert(queue, 1, announcement)
			end
			task.wait(settings.gap)
		end
		showing = false
	end)
end

function LuckyBannerController.announce(announcement)
	table.insert(queue, announcement)
	table.sort(queue, function(a, b)
		return a.oneIn > b.oneIn
	end)
	while #queue > settings.maxQueue do
		table.remove(queue)
	end
	runQueue()
end

function LuckyBannerController.start()
	hud = buildGui()

	local remotes = ReplicatedStorage:WaitForChild("ThrowRemotes")
	remotes:WaitForChild("LuckyCatch").OnClientEvent:Connect(LuckyBannerController.announce)

	-- Your own lucky catch, once you've tapped through its reveal.
	RevealController.finished:Connect(function(catch)
		if catch.oneIn >= settings.minOneIn then
			LuckyBannerController.announce({
				player = player.Name,
				id = catch.id,
				name = catch.name,
				size = catch.size,
				mutation = catch.mutation,
				oneIn = catch.oneIn,
			})
		end
	end)
end

return LuckyBannerController
