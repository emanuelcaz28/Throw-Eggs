-- The admin panel's server tools (AdminController, Config/Admin): boosts for the whole server you are in (luck, power,
-- training XP: any multiplier, any minutes), and gifts to one player here (x100 / x500 lucky throws, Throw Power).
-- Only admins can ask (AdminRemotes.Boost); every number is checked here. Boosts live on ReplicatedStorage
-- (AdminBoosts) and end with the server; gifts go into the player's save at once, like /give (AdminCommands).
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Admin = require(ReplicatedStorage.Shared.Config.Admin)
local AdminBoosts = require(ReplicatedStorage.Shared.AdminBoosts)
local Format = require(ReplicatedStorage.Shared.Format)
local LuckyThrows = require(ReplicatedStorage.Shared.LuckyThrows)
local AdminService = require(script.Parent.AdminService)
local PlayerData = require(script.Parent.PlayerData)
local PlotService = require(script.Parent.PlotService)
local RemoteGuard = require(script.Parent.RemoteGuard)
local ShopService = require(script.Parent.ShopService)
local TrainingService = require(script.Parent.TrainingService)

local AdminBoostService = {}

local remote: RemoteEvent
local generation: { [string]: number } = {} -- a newer start or stop of the same boost cancels the older one's end

local function reply(player: Player, text: string)
	remote:FireClient(player, text)
end

-- A whole number from `low` to `high`, or nil.
local function whole(value: any, low: number, high: number): number?
	if typeof(value) ~= "number" or value ~= value or value % 1 ~= 0 or value < low or value > high then
		return nil
	end
	return value
end

local function tellEveryone(text: string)
	for _, player in Players:GetPlayers() do
		PlotService.notify(player, text)
	end
end

local function startBoost(admin: Player, kind: any, multiplier: any, minutes: any)
	local look = typeof(kind) == "string" and Admin.boosts[kind]
	if not look then
		return
	end
	local times = whole(multiplier, 2, look.most)
	if not times then
		reply(admin, `{look.name}: the multiplier must be a whole number from 2 to {look.most}`)
		return
	end
	local length = whole(minutes, 1, Admin.mostMinutes)
	if not length then
		reply(admin, `{look.name}: the minutes must be a whole number from 1 to {Admin.mostMinutes}`)
		return
	end
	generation[kind] = (generation[kind] or 0) + 1
	local mine = generation[kind]
	AdminBoosts.set(kind, times, workspace:GetServerTimeNow() + length * 60)
	-- When it runs out, the attributes go, so everything that shows or uses it updates (AdminBoosts.changed).
	task.delay(length * 60, function()
		if generation[kind] == mine then
			AdminBoosts.set(kind, nil, nil)
		end
	end)
	print(`[AdminBoostService] {admin.Name} started {look.name} x{times} for {length} min`)
	tellEveryone(`{look.name} x{Format.short(times)} for everyone for {length} min!`)
	reply(admin, `{look.name} x{times} is on for {length} min`)
end

local function stopBoost(admin: Player, kind: any)
	local look = typeof(kind) == "string" and Admin.boosts[kind]
	if not look then
		return
	end
	generation[kind] = (generation[kind] or 0) + 1
	AdminBoosts.set(kind, nil, nil)
	print(`[AdminBoostService] {admin.Name} stopped {look.name}`)
	reply(admin, `{look.name} boost stopped`)
end

-- The players a gift goes to: one by UserId, or everyone here with 0.
local function targetsOf(userId: any): { Player }?
	if userId == 0 then
		return Players:GetPlayers()
	end
	local target = typeof(userId) == "number" and Players:GetPlayerByUserId(userId)
	return if target then { target } else nil
end

local function give(admin: Player, userId: any, what: any, amount: any)
	local targets = targetsOf(userId)
	if not targets then
		reply(admin, "That player isn't in this server any more")
		return
	end
	local name, apply
	if what == "power" then
		local power = whole(amount, 1, Admin.mostPower)
		if not power then
			reply(admin, `Power: a whole number from 1 to {Format.commas(Admin.mostPower)}`)
			return
		end
		name = `+{Format.commas(power)} Power`
		apply = function(target, data)
			TrainingService.addBonusPower(target, data, power)
		end
	else
		local multiplier = typeof(what) == "number" and table.find(LuckyThrows.tiers, what) and what
		local count = whole(amount, 1, Admin.mostLuckyThrows)
		if not multiplier then
			return
		end
		if not count then
			reply(admin, `Lucky throws: a whole number from 1 to {Admin.mostLuckyThrows}`)
			return
		end
		name = `{count} x Luck x{multiplier}`
		apply = function(target, data)
			ShopService.addLuckyThrows(target, data, multiplier, count)
		end
	end

	local lines = {}
	for _, target in targets do
		local data = PlayerData.get(target)
		if not data then
			table.insert(lines, `{target.Name}: still loading`)
			continue
		end
		apply(target, data)
		local saved = PlayerData.saveNow(target)
		if target ~= admin then
			PlotService.notify(target, `Gift: {name}!`)
		end
		print(`[AdminBoostService] {admin.Name} gave {target.Name} {name} (saved: {saved})`)
		table.insert(lines, `{target.Name}{if saved then "" else " (saves at the next autosave)"}`)
	end
	reply(admin, `Gave {name} to {table.concat(lines, ", ")}`)
end

local function onRequest(admin: Player, action: any, ...: any)
	if not AdminService.isAdmin(admin) then
		return
	end
	if action == "start" then
		startBoost(admin, ...)
	elseif action == "stop" then
		stopBoost(admin, ...)
	elseif action == "give" then
		give(admin, ...)
	end
end

function AdminBoostService.start()
	remote = Instance.new("RemoteEvent")
	remote.Name = "Boost"
	remote.Parent = ReplicatedStorage:WaitForChild("AdminRemotes") -- made by AdminService.start
	RemoteGuard.connect(remote, onRequest)
end

return AdminBoostService
