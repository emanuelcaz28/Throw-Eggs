-- Gifts for staying [Owner, 2026-11-12: keep a new player past 10 minutes]. Once per save, counted in seconds of
-- play after the tutorial ends (PlayGiftService; time offline doesn't count).
return {
	-- Free lucky throws, in order. The next one shows as a countdown in the row of icons at the bottom
	-- (BoostRowController). Multipliers must be ones the Shop sells or the daily reward gives (LuckyThrows.tiers).
	luckyThrows = {
		-- [Owner, 2026-11-13] The x500 comes 30 minutes after the x100 (was 12 minutes after): it arrived while a new map
		-- was minutes away, so nobody needed to buy one. Only for new players: see luckyThrowsBefore.
		{ at = 8 * 60, multiplier = 100 },
		{ at = 38 * 60, multiplier = 500 },
	},
	-- The times for saves that had already played before 2026-11-13 (save field playGiftPlan, PlayGiftService): players
	-- who already play keep the countdown they were shown. Same throws in the same order as luckyThrows.
	luckyThrowsBefore = {
		{ at = 8 * 60, multiplier = 100 },
		{ at = 20 * 60, multiplier = 500 },
	},
	-- The player's own first event: Config/Events come every 15 minutes, so many new players left before seeing one.
	-- At `at` this event (a Config/Events id) starts for this player only and runs as long as a normal one. Skipped
	-- when a real event is already running at that moment.
	firstEvent = { at = 5 * 60, id = "DoubleLuck" },
}
