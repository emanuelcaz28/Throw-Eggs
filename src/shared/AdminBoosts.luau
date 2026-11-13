-- Server boosts an admin starts from the admin panel (AdminBoostService on the server, Config/Admin): luck, power and
-- training XP, each a multiplier until a time. The server keeps them as attributes on ReplicatedStorage, so every
-- client can show them and the server's own rolls, throws and squats read the same numbers. Clients can't change them.
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local AdminBoosts = {}

AdminBoosts.kinds = { "luck", "power", "xp" }

local function attributes(kind: string): (string, string)
	return `Admin{kind}Boost`, `Admin{kind}BoostEndsAt`
end

-- The multiplier and the server time it ends, or nil when that boost isn't running.
function AdminBoosts.get(kind: string, now: number?): (number?, number?)
	local multiplierName, endsName = attributes(kind)
	local multiplier, endsAt = ReplicatedStorage:GetAttribute(multiplierName), ReplicatedStorage:GetAttribute(endsName)
	if typeof(multiplier) ~= "number" or typeof(endsAt) ~= "number" or endsAt <= (now or workspace:GetServerTimeNow()) then
		return nil, nil
	end
	return multiplier, endsAt
end

-- 1 when that boost isn't running.
function AdminBoosts.multiplier(kind: string, now: number?): number
	return AdminBoosts.get(kind, now) or 1
end

-- Server only (attributes set on the client don't reach anyone).
function AdminBoosts.set(kind: string, multiplier: number?, endsAt: number?)
	local multiplierName, endsName = attributes(kind)
	ReplicatedStorage:SetAttribute(multiplierName, multiplier)
	ReplicatedStorage:SetAttribute(endsName, endsAt)
end

-- Fires when an admin starts or stops any boost.
function AdminBoosts.changed(callback: () -> ()): { RBXScriptConnection }
	local connections = {}
	for _, kind in AdminBoosts.kinds do
		local _, endsName = attributes(kind)
		table.insert(connections, ReplicatedStorage:GetAttributeChangedSignal(endsName):Connect(callback))
	end
	return connections
end

return AdminBoosts
