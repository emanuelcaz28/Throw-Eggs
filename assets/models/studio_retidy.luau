-- Tidies RE-imported monsters in Studio (a monster already in Assets.Dinos, imported again after a geometry fix): each part
-- takes its look (colour, material, studs, glow) from the same role on the old model, bones the importer dropped (empty
-- marker bones like Drip) are copied back from the old model, then the old model is swapped out. Run through Studio's MCP
-- execute_luau in Edit, the re-imports still in Workspace. Set DRY = true first to only report.
local DRY = false
local D = game:GetService("ReplicatedStorage").Assets.Dinos
-- Blender names whose game model has a short id (Config/Dinos ids, the first map's first models).
local RENAME = { dino_Velociraptor = "dino_Raptor", dino_Pteranodon = "dino_Ptero", dino_Parasaurolophus = "dino_Parasaur",
	dino_Stegosaurus = "dino_Stego" }
-- Monsters rebuilt as new designs (other roles and bones than the old model): tidy those with studio_tidy.py instead.
local SKIP = { dino_Antagonist = true, dino_MorelPanic = true, dino_Sporantula = true, dino_ToadRage = true, dino_Gillotine = true,
	dino_Shroomageddon = true }

local log, done = {}, 0
for _, outer in workspace:GetChildren() do
	if string.sub(outer.Name, 1, 5) ~= "dino_" or not outer:IsA("Model") or SKIP[outer.Name] then
		continue
	end
	local target = RENAME[outer.Name] or outer.Name
	local old = D:FindFirstChild(target)
	if not old then
		table.insert(log, outer.Name .. ": no old model " .. target .. ", left in Workspace")
		continue
	end
	local model = outer
	local kids = outer:GetChildren()
	if #kids == 1 and kids[1]:IsA("Model") then
		model = kids[1]
	end
	local oldParts, oldBones, newBones = {}, {}, {}
	for _, p in old:GetChildren() do
		if p:IsA("BasePart") then oldParts[p.Name] = p end
	end
	for _, b in old:GetDescendants() do
		if b:IsA("Bone") then oldBones[b.Name] = b end
	end
	for _, b in model:GetDescendants() do
		if b:IsA("Bone") then newBones[b.Name] = b end
	end
	local missingRoles, addedBones = {}, {}
	for _, part in model:GetDescendants() do
		if not part:IsA("BasePart") or part.Name == "RootPart" then
			continue
		end
		local role = string.match(part.Name, "([^_]+)$")
		local from = oldParts[role]
		if not from then
			table.insert(missingRoles, role)
		elseif not DRY then
			part.Name = role
			part.Color = from.Color
			part.Material = from.Material
			part.MaterialVariant = from.MaterialVariant
			part.Transparency = from.Transparency
			part.Reflectance = from.Reflectance
			part.CastShadow = from.CastShadow
			part.CanCollide = from.CanCollide
			part.CanQuery = from.CanQuery
			part.CanTouch = from.CanTouch
			for _, c in part:GetChildren() do
				if c:IsA("SurfaceAppearance") then c:Destroy() end
			end
		end
	end
	-- Bones the old model has and the new one lost, put back under the same parent bone, same place.
	for name, b in oldBones do
		local parentBone = b.Parent
		if not newBones[name] and parentBone:IsA("Bone") and newBones[parentBone.Name] then
			table.insert(addedBones, name)
			if not DRY then
				local copy = b:Clone()
				for _, c in copy:GetChildren() do
					if c:IsA("Bone") then c:Destroy() end
				end
				copy.Parent = newBones[parentBone.Name]
			end
		end
	end
	if not DRY then
		for _, part in model:GetDescendants() do
			if part:IsA("BasePart") then part.Anchored = true end
		end
		model:PivotTo(CFrame.new())
		model.Name = target
		old:Destroy()
		model.Parent = D
		if model ~= outer then outer:Destroy() end
	end
	done += 1
	if #missingRoles > 0 or #addedBones > 0 then
		table.insert(log, target .. ": no old role " .. table.concat(missingRoles, ",") .. " | bones put back " .. table.concat(addedBones, ","))
	end
end
table.sort(log)
return string.format("%s %d\n", if DRY then "would tidy" else "tidied", done) .. table.concat(log, "\n")
