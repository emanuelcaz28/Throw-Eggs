-- Training station. Reps are automatic while standing on the pad.
-- Placeholder numbers; tune during playtesting.
local Training = {
	repInterval = 1, -- seconds per rep
	xpPerRep = 1,

	-- XP needed for the next level = baseXp * xpGrowth ^ (level - 1)
	baseXp = 5,
	xpGrowth = 1.25,

	startPower = 20, -- Throw Power at level 1
	powerPerLevel = 5,

	-- Station placement, in world studs. position is the centre of the pad, on the ground.
	station = {
		position = Vector3.new(30, 0, 0),
		padRadius = 7, -- how far from the centre still counts as training
		padHeight = 8, -- how far above the pad still counts (so jumping doesn't stop reps)
	},
}

function Training.xpToNextLevel(level: number): number
	return math.floor(Training.baseXp * Training.xpGrowth ^ (level - 1))
end

function Training.powerForLevel(level: number): number
	return Training.startPower + Training.powerPerLevel * (level - 1)
end

return Training
