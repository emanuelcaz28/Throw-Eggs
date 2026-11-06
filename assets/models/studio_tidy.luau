-- Tidies a map's freshly imported models in Studio (docs/MAP_RECIPE.md step 8); studio_tidy.py fills in
-- WORLD, COLOURS and NOSTUDS and runs it. Unwraps each import, moves its pivot (the Blender origin) to the world
-- origin, names parts by bare role, colours them, SmoothPlastic, anchored, the Studs material except on glowing
-- and face parts, then puts props in Assets.Maps.<WORLD>.Props, monsters in Assets.Dinos and eggs in Assets.Eggs.
local RS = game:GetService("ReplicatedStorage")
local assets = RS.Assets
-- Studs come from the shared "Studs" MaterialVariant in MaterialService (the Creator Store "Studs" image,
-- tiled in world studs, so studs stay the same size however big a model is scaled).
local maps = assets.Maps
local world = maps:FindFirstChild(WORLD) or Instance.new("Folder")
world.Name = WORLD
world.Parent = maps
local propsFolder = world:FindFirstChild("Props") or Instance.new("Folder")
propsFolder.Name = "Props"
propsFolder.Parent = world
local log, missing = {}, {}
local done = 0
for name, roles in COLOURS do
	local outer = workspace:FindFirstChild(name)
	if not outer then
		table.insert(missing, name)
		continue
	end
	local kids = outer:GetChildren()
	local model = outer
	if #kids == 1 and kids[1]:IsA("Model") and kids[1].Name == name then
		model = kids[1]
		model.Parent = workspace
		outer:Destroy()
	end
	model:PivotTo(CFrame.new())
	local isDino = name:match("^dino_") ~= nil
	local isEgg = name:match("^egg_") ~= nil -- the Egg Shop's eggs (build_eggs.py): their pivot, the world origin, is their foot
	local parts = 0
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") then
			part.Anchored = true
			if part.Name == "RootPart" then
				continue
			end
			local role = string.match(part.Name, "([^_]+)$")
			part.Name = role
			local hex = roles[role]
			if hex then
				part.Color = Color3.fromHex(hex)
			else
				table.insert(log, name .. ": no colour for " .. role)
			end
			part.Material = Enum.Material.SmoothPlastic
			if isDino or isEgg then
				part.CanCollide = false
			end
			for _, old in part:GetChildren() do
				if old:IsA("SurfaceAppearance") then old:Destroy() end
			end
			if not NOSTUDS[role] and role ~= "Front" then
				part.MaterialVariant = "Studs"
			end
			parts += 1
		end
	end
	local eggs = assets:FindFirstChild("Eggs")
	if isEgg and not eggs then
		eggs = Instance.new("Folder")
		eggs.Name = "Eggs"
		eggs.Parent = assets
	end
	local dest = if isDino then assets.Dinos elseif isEgg then eggs else propsFolder
	local old = dest:FindFirstChild(name)
	if old then old:Destroy() end
	model.Parent = dest
	done += 1
	table.insert(log, string.format("%s -> %s (%d parts)", name, dest:GetFullName(), parts))
end
table.sort(log)
return string.format("tidied %d, missing: %s\n", done, table.concat(missing, ",")) .. table.concat(log, "\n")
