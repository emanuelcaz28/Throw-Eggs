local Services = script.Parent.Services

require(Services.DinoLibrary).start() -- first: moves the monster models out of ReplicatedStorage before anyone joins
require(Services.LightingService).start()
require(Services.MapService).start()
require(Services.PlayerData).start()
require(Services.AdminService).start()
require(Services.TutorialService).start()
require(Services.TrainingService).start()
require(Services.IndexService).start()
require(Services.PlotService).start()
require(Services.EggService).start()
require(Services.HubService).start()
require(Services.ShopService).start()
require(Services.AdminCommands).start() -- after AdminService and ShopService
require(Services.DailyService).start()
require(Services.DailyTasks).start()
require(Services.LeaderboardService).start()
require(Services.BestCatchService).start()
require(Services.LeaderstatsService).start()
require(Services.CompetitionService).start()
require(Services.ThrowService).start()
require(Services.HomeService).start()
require(Services.SettingsService).start()
