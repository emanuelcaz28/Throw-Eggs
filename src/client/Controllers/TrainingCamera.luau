-- The lifter's own camera when training starts: one short glide from wherever the camera was to a wide view from
-- the front and above, with the lifter, the rack and the bases around them in it, and then the normal camera is theirs
-- again, at that spot. They can turn and zoom it, and see the other players and their monsters [Owner, 2026-11-09:
-- no black bars, no swaying, players mustn't feel shut off while training]. Numbers in Config/Training camera.
-- The server holds the player in place (TrainingService anchors them); this is only the view.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Training = require(ReplicatedStorage.Shared.Config.Training)

local TrainingCamera = {}

local player = Players.LocalPlayer
local settings = Training.camera
local FOCUS_HEIGHT = 1.5 -- the normal camera looks at about this far above the root

local function ease(t: number): number
	-- Smooth start and end (cubic in-out), so the glide never jerks.
	t = math.clamp(t, 0, 1)
	return if t < 0.5 then 4 * t ^ 3 else 1 - (-2 * t + 2) ^ 3 / 2
end

local function rootOf(): BasePart?
	local character = player.Character
	return character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
end

-- The wide view: looking at where the normal camera looks, from Config's offset (front, left, above), so the
-- normal camera can take over from exactly here.
local function wideView(root: BasePart): CFrame
	local flat = root.CFrame.LookVector * Vector3.new(1, 0, 1)
	local facing = if flat.Magnitude > 0.01 then CFrame.lookAt(root.Position, root.Position + flat) else root.CFrame
	local focus = root.Position + Vector3.new(0, FOCUS_HEIGHT, 0)
	local eye = facing:PointToWorldSpace(settings.offset)
	local look = (focus - eye).Unit
	return CFrame.lookAt(focus - look * settings.offset.Magnitude, focus)
end

function TrainingCamera.start()
	local camera = workspace.CurrentCamera
	local run = 0 -- goes up on every start and stop, so an old glide stops

	-- Hands the camera back at the wide view, at that distance: the zoom limits are pinned to it for a frame, which
	-- is the only way to set the normal camera's zoom, then put back.
	local function handBack(view: CFrame)
		local low, high = player.CameraMinZoomDistance, player.CameraMaxZoomDistance
		local distance = math.clamp(settings.offset.Magnitude, low, high)
		camera.CameraType = Enum.CameraType.Custom
		camera.CFrame = view
		player.CameraMinZoomDistance, player.CameraMaxZoomDistance = distance, distance
		RunService.RenderStepped:Wait()
		player.CameraMinZoomDistance, player.CameraMaxZoomDistance = low, high
	end

	local function enter()
		run += 1
		local mine = run
		local root = rootOf()
		if not root then
			return
		end
		local from = camera.CFrame
		local began = os.clock()
		camera.CameraType = Enum.CameraType.Scriptable
		while run == mine and os.clock() - began < settings.glideSeconds do
			root = rootOf()
			if not root then
				break
			end
			camera.CFrame = from:Lerp(wideView(root), ease((os.clock() - began) / settings.glideSeconds))
			RunService.RenderStepped:Wait()
		end
		if run == mine and root then
			handBack(wideView(root))
		elseif camera.CameraType == Enum.CameraType.Scriptable then
			camera.CameraType = Enum.CameraType.Custom
		end
	end

	local function leave()
		-- The camera is already the normal one; only a glide still running is stopped.
		run += 1
		if camera.CameraType == Enum.CameraType.Scriptable then
			camera.CameraType = Enum.CameraType.Custom
		end
	end

	local training = false
	local function render()
		local now = player:GetAttribute("IsTraining") == true
		if now == training then
			return
		end
		training = now
		if now then
			task.spawn(enter)
		else
			leave()
		end
	end
	player:GetAttributeChangedSignal("IsTraining"):Connect(render)
	render()
end

return TrainingCamera
