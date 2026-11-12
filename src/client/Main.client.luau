local Controllers = script.Parent.Controllers

require(Controllers.SettingsState).start() -- first: the volume groups every sound plays through

require(Controllers.SkyController).start()
require(Controllers.PropMotionController).start()
require(Controllers.TrainingController).start()
require(Controllers.SquatController).start()
require(Controllers.TrainingCamera).start()
require(Controllers.PlotController).start()
require(Controllers.DinoLifeController).start()
require(Controllers.MonsterTagController).start()
require(Controllers.EggShopController).start()
require(Controllers.IndexController).start()
require(Controllers.ShopController).start()
require(Controllers.EventController).start()
require(Controllers.BoostRowController).start()
require(Controllers.GiftToastController).start()
require(Controllers.DailyController).start()
require(Controllers.HomeController).start()
require(Controllers.WelcomeController).start()
require(Controllers.RevealController).start()
require(Controllers.LuckyBannerController).start()
require(Controllers.HookMessages).start()
require(Controllers.ThrowController).start()
require(Controllers.ThrowAreaPrivacy).start() -- other throwers hidden while you stand in the throwing area
task.spawn(require(Controllers.TutorialController).start) -- waits for the save, so it mustn't hold up the rest
task.spawn(require(Controllers.ReadyPopupController).start) -- its check loop never returns
task.spawn(require(Controllers.AdminController).start) -- waits until the server says this player is an admin
task.spawn(require(Controllers.AdminCommandController).start) -- the /give chat command, same wait
require(Controllers.UiClickSound).start()
require(Controllers.GameFeelSounds).start()
require(Controllers.GameFeelJuice).start()
require(Controllers.MusicController).start()
require(Controllers.SettingsController).start()
if require(game:GetService("ReplicatedStorage").Shared.Config.Troll).enabled then -- hidden while false (Config/Troll)
	require(Controllers.RagdollController).start() -- after Shop and Index: its button sits under theirs
	require(Controllers.LeashController).start() -- after DinoLife: it takes monsters off its hands
end
require(Controllers.PowerLimitController).start() -- after Training (its HUD button sits by Throw Power) and Index
