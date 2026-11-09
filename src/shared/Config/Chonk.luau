-- Feeding (docs/RETENTION_PLAN.md step 4): spare monsters and some cash make a favourite on the base grow. Levels are
-- saved on the monster (entry.chonk, and food towards the next in entry.food).
-- [Owner, 2026-11-08] Looks only: feeding never changes what a monster earns (it made every monster earn x3.5 and
-- Robux monsters, a share of the best, grew with it). Instead it climbs the size tiers (Config/Catch sizes) at the
-- levels below, each much further than the last, so a fed Unit of Doom is a long-term goal. A monster caught bigger
-- keeps its own size until feeding passes it. Its tag says FED next to the size word (MonsterTagController).
local Chonk = {
	maxLevel = 50,
	-- The Chonk level at which feeding reaches each size. Food per level grows by one (foodFor), so the total food
	-- is about level^2/2: Thicc 6, Absolute Unit 36, Chonker 120, Mega Chonk 325, Planet-Sized 741, Unit of Doom 1,275
	-- (a third of that in monsters of the same kind).
	sizeLevels = {
		{ size = "Thicc", level = 3 },
		{ size = "AbsoluteUnit", level = 8 },
		{ size = "Chonker", level = 15 },
		{ size = "MegaChonk", level = 25 },
		{ size = "PlanetSized", level = 38 },
		{ size = "UnitOfDoom", level = 50 },
	},
	food = 1, -- what any monster is worth
	twinFood = 3, -- what one of the same kind is worth
	cashSeconds = 30, -- each monster fed costs this many seconds of what the fed monster earns
}

-- The size feeding has reached at this level (a Config/Catch sizes id), or nil below the first.
function Chonk.sizeAt(level: number?): string?
	local reached = nil
	for _, step in Chonk.sizeLevels do
		if (level or 0) >= step.level then
			reached = step.size
		end
	end
	return reached
end

-- The next size feeding reaches above this level and the level it comes at, or nil once there are no more.
function Chonk.nextSize(level: number?): (string?, number?)
	for _, step in Chonk.sizeLevels do
		if (level or 0) < step.level then
			return step.size, step.level
		end
	end
	return nil, nil
end

-- Food to go from this level to the next: each level asks for one more than the last.
function Chonk.foodFor(level: number): number
	return level + 1
end

-- What a monster is worth to the one being fed.
function Chonk.foodOf(targetId: string, foodId: string): number
	return if targetId == foodId then Chonk.twinFood else Chonk.food
end

-- The level and food left over after this much more food.
function Chonk.grow(level: number, food: number, more: number): (number, number)
	food += more
	while level < Chonk.maxLevel and food >= Chonk.foodFor(level) do
		food -= Chonk.foodFor(level)
		level += 1
	end
	return level, if level >= Chonk.maxLevel then 0 else food
end

-- What feeding one monster costs while the fed one earns this much.
function Chonk.priceOf(income: number): number
	return math.ceil(income * Chonk.cashSeconds)
end

return Chonk
