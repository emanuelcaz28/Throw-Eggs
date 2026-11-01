# Throw Eggs for Dinosaurs 🦖🥚

Roblox game. Train your throw, launch eggs through prehistoric biomes, hatch rare dinos, and fill your plot.

- Design: [`docs/GDD.md`](docs/GDD.md)
- Notes for Claude Code: [`CLAUDE.md`](CLAUDE.md)

## Setup

1. Install [Rojo](https://rojo.space) (CLI + Roblox Studio plugin).
2. In this folder run `rojo serve`.
3. In Studio, open the Rojo plugin and click **Connect**.

## Layout

```
src/server   -> ServerScriptService (game logic, data saving)
src/client   -> StarterPlayerScripts (UI, camera, input)
src/shared   -> ReplicatedStorage.Shared (configs used by both)
```
