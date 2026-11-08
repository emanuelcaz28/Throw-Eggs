-- The admin chat command "/give <player|me|all> <item> [amount]" (AdminCommands on the server, Config/Admin). Only for
-- admins: this just forwards the typed text; the server checks who sent it and does everything. The server's answer is
-- shown in chat as a system message, only to the admin. "/give items" lists what can be given.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local StarterGui = game:GetService("StarterGui")
local TextChatService = game:GetService("TextChatService")

local player = Players.LocalPlayer

local AdminCommandController = {}

local function say(text: string)
	if TextChatService.ChatVersion == Enum.ChatVersion.TextChatService then
		local channels = TextChatService:WaitForChild("TextChannels", 10)
		local general = channels and channels:FindFirstChild("RBXGeneral")
		if general and general:IsA("TextChannel") then
			general:DisplaySystemMessage(text)
			return
		end
	end
	pcall(function()
		StarterGui:SetCore("ChatMakeSystemMessage", { Text = text })
	end)
end

function AdminCommandController.start()
	while not player:GetAttribute("IsAdmin") do
		player:GetAttributeChangedSignal("IsAdmin"):Wait()
	end
	local remote = ReplicatedStorage:WaitForChild("AdminRemotes"):WaitForChild("Give")
	remote.OnClientEvent:Connect(say)

	if TextChatService.ChatVersion == Enum.ChatVersion.TextChatService then
		local command = Instance.new("TextChatCommand")
		command.Name = "GiveCommand"
		command.PrimaryAlias = "/give"
		command.Triggered:Connect(function(_source, text)
			remote:FireServer(text)
		end)
		command.Parent = TextChatService
	else
		-- Old chat: the typed line comes back through Chatted.
		player.Chatted:Connect(function(message)
			if string.lower(string.sub(message, 1, 5)) == "/give" then
				remote:FireServer(message)
			end
		end)
	end
end

return AdminCommandController
