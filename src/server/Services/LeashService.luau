-- Leashes. A player leashes a monster on anyone's plot from any distance: it floats on a line wherever they point
-- for up to Config/Troll's maxSeconds, they throw it or it shakes itself off, and it walks home. Pure fun: the monster keeps earning for its
-- owner the whole time and nothing is saved [Owner, 2026-11-12]. Each monster rests between leashes (longer after a
-- stranger's), and a player's monsters can't be leashed while that player is at the throw.
--
-- The server only decides who holds which monster (the "LeashedBy" attribute on the monster, the holder's UserId).
-- Monsters live on each player's own screen (DinoLifeController), so the rope and the tumbling are drawn there too
-- (LeashController).
--
-- Throw area safety: nobody holding a leash can start a throw (ThrowService.isOnPad asks isHolding), and walking
-- into the throwing area lets the monster go. Its body can't get in either (RagdollService's wall).
local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local DinoLife = require(ReplicatedStorage.Shared.Config.DinoLife)
local Plot = require(ReplicatedStorage.Shared.Config.Plot)
local Troll = require(ReplicatedStorage.Shared.Config.Troll)
local Shop = require(ReplicatedStorage.Shared.Config.Shop)
local PlayerData = require(script.Parent.PlayerData)
local RagdollService = require(script.Parent.RagdollService)
local RemoteGuard = require(script.Parent.RemoteGuard)

local LeashService = {}

local TICK = 0.2

-- What each player holds: a monster (model, place, own) or, with the Player Leash pass, another player (victim and
-- the character they had when it began).
type Held = { startedAt: number, model: Model?, place: string?, own: boolean?, victim: Player?, character: Model? }
local holding: { [Player]: Held } = {}
local leashedBy: { [Player]: Player } = {} -- each leashed player's holder
local immuneUntil: { [Player]: number } = {} -- nobody can leash this player before then
local readyAt: { [string]: number } = {} -- by plot and monster key: when it can be leashed again
local holderReadyAt: { [Player]: number } = {}

function LeashService.isHolding(player: Player): boolean
	return holding[player] ~= nil
end

-- How much faster than the cursor swung it a monster leaves when its holder throws it: 1 with no Throw Power, more
-- with the holder's power by its number of digits, up to 1 + boost (Config/Troll leash.fling).
local function flingSpeed(player: Player): number
	local fling = Troll.leash.fling
	local power = player:GetAttribute("ThrowPower")
	power = if typeof(power) == "number" and power == power then math.max(power, 0) else 0
	local share = math.clamp(math.log10(power + 1) / math.log10(fling.fullPower + 1), 0, 1)
	return 1 + fling.boost * share
end

-- `thrown`: the holder let go on purpose (the button), so the monster is flung. Any other ending just drops it.
local function release(player: Player, thrown: boolean?)
	local held = holding[player]
	if not held then
		return
	end
	holding[player] = nil
	local victim = held.victim
	if victim then
		-- The victim's protection starts now, whoever let go and why.
		leashedBy[victim] = nil
		immuneUntil[victim] = os.clock() + Troll.playerLeash.immunity
		holderReadyAt[player] = os.clock() + Troll.playerLeash.cooldown
		if held.character and held.character.Parent then
			held.character:SetAttribute("LeashedBy", nil)
		end
		RagdollService.stop(victim) -- they get up
		return
	end
	local model = held.model :: Model
	readyAt[held.place :: string] = os.clock() + (if held.own then Troll.leash.cooldown else Troll.leash.cooldownOthers)
	holderReadyAt[player] = os.clock() + Troll.leash.holderCooldown
	if model.Parent then
		model:SetAttribute("LeashFling", if thrown then flingSpeed(player) else 0) -- first: screens read it as the rope goes
		model:SetAttribute("LeashedBy", nil)
	end
end

local function rootOf(player: Player): BasePart?
	local character = player.Character
	return character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
end

-- The walking monster on a plot with this key (not the one on the pedestal, not a carried one).
local function monsterOn(plotIndex: number, key: number): Model?
	for _, model in CollectionService:GetTagged(DinoLife.tag) do
		if model:GetAttribute("PlotIndex") == plotIndex and model:GetAttribute("DinoKey") == key
			and not model:GetAttribute("Stay") and not model:GetAttribute("Carried") and model:IsDescendantOf(workspace) then
			return model
		end
	end
	return nil
end

local function ownerOf(plotIndex: number): Player?
	for _, other in Players:GetPlayers() do
		if other:GetAttribute("PlotIndex") == plotIndex then
			return other
		end
	end
	return nil
end

local function onToggle(player: Player, plotIndex: any, key: any)
	local held = holding[player]
	if held then
		if os.clock() - held.startedAt >= Troll.leash.minSeconds then
			release(player, true)
		end
		return
	end
	local root = rootOf(player)
	if typeof(key) ~= "number" or key ~= key or typeof(plotIndex) ~= "number" or not root then
		return
	end
	if RagdollService.isRagdolled(player) or RagdollService.isBusy(player) or os.clock() < (holderReadyAt[player] or 0) then
		return
	end
	-- Anyone's plot, as long as its owner isn't at the throw (aiming, throwing or watching a reveal).
	local owner = ownerOf(plotIndex)
	if not owner or (owner ~= player and RagdollService.isAtThrow(owner)) then
		return
	end
	local centre = Plot.positions[plotIndex]
	if not centre or ((root.Position - centre) * Vector3.new(1, 0, 1)).Magnitude > Troll.leash.range then
		return
	end
	local place = `{plotIndex}:{key}`
	if os.clock() < (readyAt[place] or 0) then
		return
	end
	local model = monsterOn(plotIndex, key)
	if not model or model:GetAttribute("LeashedBy") then
		return
	end
	holding[player] = { model = model, startedAt = os.clock(), place = place, own = owner == player }
	model:SetAttribute("LeashAim", nil)
	model:SetAttribute("LeashedBy", player.UserId)
end

-- Leashing another player: the Player Leash pass only. Every check about the victim protects the victim.
local function onLeashPlayer(player: Player, userId: any)
	local held = holding[player]
	if held then
		if os.clock() - held.startedAt >= Troll.leash.minSeconds then
			release(player)
		end
		return
	end
	local now = os.clock()
	local root = rootOf(player)
	if typeof(userId) ~= "number" or not root or Shop.playerLeash.passId == 0 or player:GetAttribute("HasPlayerLeash") ~= true then
		return
	end
	if RagdollService.isRagdolled(player) or RagdollService.isBusy(player) or now < (holderReadyAt[player] or 0) then
		return
	end
	local victim = Players:GetPlayerByUserId(userId)
	local character = victim and victim.Character
	local victimRoot = victim and rootOf(victim)
	if not victim or victim == player or not character or not victimRoot then
		return
	end
	-- Not while they're leashed or limp already, at the throw, training, or still protected from the last time.
	if leashedBy[victim] or RagdollService.isRagdolled(victim) or RagdollService.isBusy(victim) or now < (immuneUntil[victim] or 0) then
		return
	end
	local data = PlayerData.get(victim)
	if not data or (typeof(data.settings) == "table" and data.settings.leashMe == false) then
		return -- "Let players leash me" is off (or their save isn't in yet)
	end
	if (victimRoot.Position - root.Position).Magnitude > Troll.playerLeash.reach then
		return
	end
	character:SetAttribute("LeashedBy", player.UserId) -- before they go limp, so their screen knows it's a leash
	if not RagdollService.force(victim) then
		character:SetAttribute("LeashedBy", nil)
		return
	end
	if holding[victim] then
		release(victim) -- whatever they were dragging goes free
	end
	holding[player] = { startedAt = now, victim = victim, character = character }
	leashedBy[victim] = player
end

-- Where the holder points, a few times a second, so every other screen can haul the monster to the same spot.
local function onAim(player: Player, spot: any)
	local held = holding[player]
	local root = rootOf(player)
	if not held or not held.model or not root or typeof(spot) ~= "Vector3" or spot ~= spot then
		return
	end
	local offset = spot - root.Position
	if offset.Magnitude > Troll.leash.aimRange then
		spot = root.Position + offset.Unit * Troll.leash.aimRange
	end
	held.model:SetAttribute("LeashAim", spot)
end

local function step()
	local now = os.clock()
	for player, held in holding do
		local root = rootOf(player)
		if held.victim then
			local victim = held.victim
			if now - held.startedAt >= Troll.playerLeash.maxSeconds
				or not root
				or victim.Character ~= held.character
				or not RagdollService.isRagdolled(victim) -- up again (the longest ragdoll), or gone
				or RagdollService.isBusy(player) -- the holder walked into the throwing area, started training, died
				or RagdollService.isRagdolled(player)
			then
				release(player)
			end
		elseif not (held.model :: Model).Parent -- sold, picked up, or the plot was rebuilt
			or now - held.startedAt >= Troll.leash.maxSeconds
			or not root
			or RagdollService.isBusy(player) -- walked into the throwing area, started training, died
			or RagdollService.isRagdolled(player) -- going limp drops the rope
		then
			release(player)
		end
	end
end

function LeashService.start()
	local remote = Instance.new("RemoteEvent")
	remote.Name = "LeashToggle"
	remote.Parent = ReplicatedStorage
	RemoteGuard.connect(remote, onToggle, 4, 6)

	local aimRemote = Instance.new("UnreliableRemoteEvent")
	aimRemote.Name = "LeashAim"
	aimRemote.Parent = ReplicatedStorage
	RemoteGuard.connect(aimRemote :: any, onAim, 20, 30)

	local playerRemote = Instance.new("RemoteEvent")
	playerRemote.Name = "LeashPlayer"
	playerRemote.Parent = ReplicatedStorage
	RemoteGuard.connect(playerRemote, onLeashPlayer, 4, 6)

	Players.PlayerRemoving:Connect(function(player)
		release(player)
		if leashedBy[player] then
			release(leashedBy[player])
		end
		holderReadyAt[player] = nil
		immuneUntil[player] = nil
	end)

	task.spawn(function()
		while true do
			task.wait(TICK)
			step()
		end
	end)
end

return LeashService
