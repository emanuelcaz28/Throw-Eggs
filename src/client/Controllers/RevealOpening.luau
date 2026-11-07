-- [Owner, 2026-11-07: the corridor's walls covered big monsters] A monster too wide for the corridor gets the room it
-- needs. The corridor is 88 studs wide and a Unit of Doom can be over 400, so its feet stood inside the walls and past the
-- island's edge. On the catcher's screen only, behind the first cut to black, the walls and everything on them slide
-- apart, the floor widens with them and the props spanning the corridor hide. Nobody else sees it, the server knows
-- nothing about it, and it all goes back at the end of the reveal. Numbers in Config/Reveal opening.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Map = require(ReplicatedStorage.Shared.Config.Map)
local PropMotionController = require(script.Parent.PropMotionController)
local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)

local RevealOpening = {}

local settings = Reveal.opening
local RIM_SLACK = 6 -- studs under the rim a prop can stand and still count as on it
local MAX_PART = 2000 -- studs: Roblox's limit for a part is 2,048

-- How far from the corridor's middle its walls stand for a monster `width` studs wide.
function RevealOpening.halfWidth(width: number): number
	local half = Map.platform.width / 2
	local wanted = width / 2 * settings.room
	return if wanted - half >= settings.minGap then wanted else half
end

-- A strip of floor beside `floor`, out to the walls on `side` (-1 or 1), in its own colours.
local function floorStrip(parent: Instance, floor: BasePart, inside: number, gap: number, side: number)
	local width = math.min(gap + settings.wallBack, MAX_PART)
	local strip = Instance.new("Part")
	strip.Name = "RevealFloor"
	strip.Anchored = true
	strip.CanCollide = false
	strip.CanQuery = false
	strip.CanTouch = false
	strip.CastShadow = false
	strip.Color = floor.Color
	strip.Material = floor.Material
	strip.MaterialVariant = floor.MaterialVariant
	strip.Size = Vector3.new(width, floor.Size.Y, floor.Size.Z)
	strip.CFrame = CFrame.new(side * (inside + width / 2), floor.Position.Y, floor.Position.Z)
	strip.Parent = parent
end

-- Opens the corridor out to `halfWidth` studs either side of its middle. Returns the function that puts it all back.
function RevealOpening.open(halfWidth: number): () -> ()
	local inside = Map.platform.width / 2
	local gap = halfWidth - inside
	local map = workspace:FindFirstChild("Map")
	local corridor = map and map:FindFirstChild("Corridor")
	if gap <= 0 or not corridor then
		return function() end
	end

	local slid = {}
	local function slide(piece: PVInstance, side: number)
		local offset = Vector3.new(side * gap, 0, 0)
		table.insert(slid, { piece = piece, offset = offset })
		piece:PivotTo(piece:GetPivot() + offset)
		PropMotionController.shift(piece, offset)
	end

	local folder = Instance.new("Folder")
	folder.Name = "RevealOpening"
	local stretched = {}
	for _, piece in corridor:GetChildren() do
		if piece.Name == "kit_WallWest" then
			slide(piece, -1)
		elseif piece.Name == "kit_WallEast" then
			slide(piece, 1)
		elseif piece.Name == "kit_Floor" then
			local floor = piece:FindFirstChildWhichIsA("BasePart", true)
			if floor then
				floorStrip(folder, floor, inside, gap, -1)
				floorStrip(folder, floor, inside, gap, 1)
			end
		elseif piece.Name == "EndWall" and piece:IsA("BasePart") then
			stretched[piece] = piece.Size
			piece.Size += Vector3.new(gap * 2, 0, 0)
		end
	end

	-- What stands on the rims goes with them; what spans the corridor can't, so it hides.
	local hidden = {}
	local function hide(part: Instance)
		if part:IsA("BasePart") and hidden[part] == nil then
			hidden[part] = part.LocalTransparencyModifier
			part.LocalTransparencyModifier = 1
		end
	end
	local decor = map:FindFirstChild("CorridorDecor")
	for _, prop in if decor then decor:GetChildren() else {} do
		if prop:IsA("PVInstance") then
			local position = prop:GetPivot().Position
			if position.Y >= Map.walls.rimY - RIM_SLACK then
				if math.abs(position.X) >= inside - 1 then
					slide(prop, if position.X < 0 then -1 else 1)
				else
					hide(prop)
					for _, part in prop:GetDescendants() do
						hide(part)
					end
				end
			end
		end
	end

	-- The lines across the floor reach the new walls too.
	local lane = workspace:FindFirstChild("ThrowLane")
	for _, marker in if lane then lane:GetChildren() else {} do
		if marker.Name == "Marker" and marker:IsA("BasePart") then
			stretched[marker] = marker.Size
			marker.Size = Vector3.new(math.min(halfWidth * 2, MAX_PART), marker.Size.Y, marker.Size.Z)
		end
	end

	folder.Parent = workspace

	return function()
		for _, entry in slid do
			if entry.piece.Parent then
				entry.piece:PivotTo(entry.piece:GetPivot() - entry.offset)
				PropMotionController.shift(entry.piece, -entry.offset)
			end
		end
		for part, size in stretched do
			part.Size = size
		end
		for part, modifier in hidden do
			part.LocalTransparencyModifier = modifier
		end
		folder:Destroy()
	end
end

return RevealOpening
