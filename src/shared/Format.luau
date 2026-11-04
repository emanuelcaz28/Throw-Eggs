-- Number text shared by the UI.
local Format = {}

-- Number names up to 10^63, so the economy can grow as far as it likes (docs/GAME_SPEC.md section 12).
local SUFFIXES = { "K", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc", "No", "Dc", "Ud", "Dd", "Td", "Qad", "Qid", "Sxd", "Spd", "Ocd", "Nod", "Vg" }

-- 1234567 -> "1,234,567"
function Format.commas(value: number): string
	if value >= 1e15 then
		return Format.short(value) -- past this, whole numbers lose their last digits and print as 1e+15
	end
	local text = string.format("%d", math.floor(value))
	local grouped = text:reverse():gsub("(%d%d%d)", "%1,"):reverse()
	return (grouped:gsub("^,", ""))
end

-- 1080000 -> "1.08M"
function Format.short(value: number): string
	local tier = 0
	while value >= 1000 and tier < #SUFFIXES do
		value /= 1000
		tier += 1
	end
	if tier == 0 then
		return tostring(math.floor(value))
	end
	local text = string.format("%.2f", value):gsub("%.?0+$", "")
	return `{text}{SUFFIXES[tier]}`
end

-- 1080000 -> "$1.08M"
function Format.cash(value: number): string
	return `${Format.short(value)}`
end

return Format
