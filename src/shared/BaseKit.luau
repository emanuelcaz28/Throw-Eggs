-- The pieces that stand at every base, modelled in Blender (assets/models/build_base_kit.py) and kept in
-- ReplicatedStorage.Assets.Maps.FernValley.Base: base_Stall, base_SquatRack, base_XpButton,
-- base_FencePost, base_FenceRails and base_UpgradeSign. Each one's pivot is its floor centre and its
-- front faces the pivot's LookVector, so placing one is a single PivotTo. Server and client both use it.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local BaseKit = {}

local folder: Instance? = nil

local function pieces(): Instance?
	if not folder then
		local assets = ReplicatedStorage:WaitForChild("Assets")
		local maps = assets:WaitForChild("Maps")
		folder = maps:WaitForChild("FernValley"):FindFirstChild("Base")
	end
	return folder
end

-- A copy of a piece standing at `at` (its floor centre, front along at.LookVector), anchored, with any
-- colour roles in `colors` recoloured (part names are the roles, as in the Blender file). Returns nil
-- with a warning when the piece hasn't been imported.
function BaseKit.place(name: string, at: CFrame, parent: Instance, colors: { [string]: Color3 }?): Model?
	local source = pieces()
	local original = source and source:FindFirstChild(name)
	if not original then
		warn(`[BaseKit] {name} is missing from ReplicatedStorage.Assets.Maps.FernValley.Base: import kit_Base from assets/models/fbx`)
		return nil
	end
	local model = original:Clone()
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			part.Anchored = true
			local color = colors and colors[part.Name]
			if color then
				part.Color = color
			end
		end
	end
	model:PivotTo(at)
	model.Parent = parent
	return model
end

-- Which face of a part points most along a world direction (for SurfaceGuis on a piece's front).
function BaseKit.faceToward(part: BasePart, direction: Vector3): Enum.NormalId
	local best, bestDot = Enum.NormalId.Front, -math.huge
	for _, face in Enum.NormalId:GetEnumItems() do
		local dot = part.CFrame:VectorToWorldSpace(Vector3.FromNormalId(face)):Dot(direction)
		if dot > bestDot then
			best, bestDot = face, dot
		end
	end
	return best
end

return BaseKit
