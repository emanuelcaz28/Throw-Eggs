local Services = script.Parent.Services

require(Services.DinoLibrary).start() -- first: moves the monster models out of ReplicatedStorage before anyone joins
require(Services.LightingService).start()
require(Services.MapService).start()
require(Services.PlayerData).start()
require(Services.AdminService).start()
require(Services.FilmingService).start() -- Studio only, Workspace StudioFilming (Config/Filming)
require(Services.TutorialService).start()
if require(game:GetService("ReplicatedStorage").Shared.Config.Troll).enabled then -- hidden while false (Config/Troll)
	require(Services.RagdollService).start() -- before Training and Throw, which ask it who is ragdolled
	require(Services.LeashService).start() -- after Ragdoll
end
require(Services.TrainingService).start()
require(Services.IndexService).start()
require(Services.PlotService).start()
require(Services.EggService).start()
require(Services.HubService).start()
require(Services.ShopService).start()
require(Services.AdminCommands).start() -- after AdminService and ShopService
require(Services.AdminBoostService).start() -- the admin panel's server boosts and gifts, same order
require(Services.DailyService).start()
require(Services.DailyTasks).start()
require(Services.PlayGiftService).start()
require(Services.LeaderboardService).start()
require(Services.BestCatchService).start()
require(Services.LeaderstatsService).start()
require(Services.CompetitionService).start()
require(Services.ThrowService).start()
require(Services.HomeService).start()
require(Services.SettingsService).start()
