# Throw Eggs for Dinosaurs (Roblox)

Read `docs/GAME_SPEC.md` first: it's what the owner wants, and it wins over everything else.
Then `docs/GDD.md` for the details of what's built.
Making a new map (world)? Follow `docs/MAP_RECIPE.md` instead of studying the older maps.

## Owner
- First-time game developer, no prior coding background. Explain Studio steps plainly.
- Prompts written for Codex must be in English.

## Stack
- Luau, synced into Roblox Studio with Rojo (`default.project.json`).
- `src/server` → ServerScriptService, `src/client` → StarterPlayerScripts, `src/shared` → ReplicatedStorage.Shared.
- Tunable numbers (biomes, dinos, eggs, luck) live in `src/shared/Config/`, never hard-coded in services.

## Rules
- Server is authoritative: rolls, cash, power and throw distance are computed on the server.
  The client only sends the timing-meter result (clamped and validated server-side).
- Save player data with DataStoreService (session lock, retry on failure).
- Original names and models only; don't copy the reference game's assets or UI.
