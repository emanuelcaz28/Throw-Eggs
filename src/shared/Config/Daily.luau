-- Daily reward (docs/GAME_SPEC.md section 8b): one claim per UTC day, each a lucky throw (one throw with
-- that much luck, kept until used, see Config/Shop luckyThrows). Claiming on the next day moves the
-- streak on; missing a day starts it again at day 1. After day 7 it goes back to day 1.
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
}
