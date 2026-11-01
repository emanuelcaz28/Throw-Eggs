-- Number text shared by the UI.
local Format = {}

local SUFFIXES = { "K", "M", "B", "T", "Qa", "Qi" }

-- 1234567 -> "1,234,567"
function Format.commas(value: number): string
	local text = tostring(math.floor(value))
	local grouped = text:reverse():gsub("(%d%d%d)", "%1,"):reverse()
	return (grouped:gsub("^,", ""))
end

-- 1080000 -> "$1.08M"
function Format.cash(value: number): string
	local tier = 0
	while value >= 1000 and tier < #SUFFIXES do
		value /= 1000
		tier += 1
	end
	if tier == 0 then
		return `${math.floor(value)}`
	end
	local text = string.format("%.2f", value):gsub("%.?0+$", "")
	return `${text}{SUFFIXES[tier]}`
end

return Format
