-- Daily reward (docs/GAME_SPEC.md section 8b): one claim per UTC day, each a lucky throw (one throw with
-- that much luck, kept until used, see Config/Shop luckyThrows). Each claim moves the streak on. [Owner, 2026-11-07] A missed
-- day only pauses it: you carry on from where you were. After day 7 it goes back to day 1.
return {
	daySeconds = 24 * 60 * 60,
	days = {
		{ luckyThrow = 50 },
		{ luckyThrow = 50 },
		{ luckyThrow = 50 },
		{ luckyThrow = 50 },
		{ luckyThrow = 50 },
		{ luckyThrow = 50 },
		{ luckyThrow = 500 },
	},
	openDelay = 3, -- seconds after joining before the panel opens by itself when a claim is waiting

	-- Three small goals a day, about 15 minutes of play (DailyTasks). Finishing all of them gives timed x2 XP (Config/Index).
	tasks = {
		{ id = "perfects", text = "Hit PERFECT", goal = 5 },
		{ id = "bubbles", text = "Tap x2 bubbles", goal = 25 },
		{ id = "catches", text = "Catch monsters", goal = 10 },
	},
	taskBoostSeconds = 15 * 60,
}
