-- Feeding (docs/RETENTION_PLAN.md step 4): spare monsters and some cash make a favourite on the base grow. [Owner,
-- 2026-11-07] Feeding makes a monster bigger than its size mutation alone, up to the limits here, so a favourite can
-- end up spilling over the fence. Levels are saved on the monster (entry.chonk, and food towards the next in entry.food).
local Chonk = {
	maxLevel = 50,
	incomePerLevel = 0.05, -- +5% of its income a level, added up, not compounded: x3.5 at level 50
	scalePerLevel = 0.02, -- +2% of its size a level, added up: x2 at level 50, on top of its size mutation
	food = 1, -- what any monster is worth
	twinFood = 3, -- what one of the same kind is worth
	cashSeconds = 30, -- each monster fed costs this many seconds of what the fed monster earns
}

function Chonk.incomeMultiplier(level: number?): number
	return 1 + Chonk.incomePerLevel * (level or 0)
end

function Chonk.scaleMultiplier(level: number?): number
	return 1 + Chonk.scalePerLevel * (level or 0)
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
