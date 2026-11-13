# Filming TikTok clips

Filming mode is a Studio-only switch. It never does anything in the live game.
Code: `Config/Filming`, `FilmingService`, `FilmingController`.

## What it does

- **Your real save, never written.** You play with all your progress, but nothing you do is kept and the leaderboards aren't touched.
- **No tutorial.**
- **A purple FILM button**, under ADMIN at the top left. It opens a panel where you pick:
  - the map
  - the monster (8/8 is the map's rarest)
  - the size
  - the colour

  The panel shows the real "1 in X" for what you picked.
- **"Every throw catches this: ON".** Every throw then lands in that map, whatever your power, and catches exactly that monster through the normal reveal. Throw again for another take. Set it to OFF for normal throws.
- **H hides the whole HUD** and Roblox's own buttons (chat, player list). The throw meter and the reveal stay on screen. Press H again to bring everything back.

## Turn it on (Studio)

1. Stay in Edit mode (not playing). Click **Workspace** in the Explorer.
2. In Properties, scroll to **Attributes** and click **+ (Add Attribute)**. Name it `StudioFilming`, type **boolean**, and tick it.
3. Press **Play**. The Output window says "Filming mode is ON".
4. When you're done filming, stop, then untick or delete `StudioFilming`. If you leave it on, normal tests run in filming mode too.

## Make the game view tall (9:16 for TikTok)

In Studio, open the **Test** tab and use the **Device** emulator. Pick a phone and switch it to portrait, so the game draws in a tall phone shape with the phone layout.

## Record with OBS (already installed)

1. The first time only: macOS asks OBS for screen-recording permission (System Settings > Privacy & Security > Screen & System Audio Recording). Turn it on and restart OBS.
2. OBS > Settings > Video: set **Base** and **Output** resolution to **1080x1920** and FPS to **60**.
3. OBS > Settings > Output > Recording: set the format to **mp4** and the path to this project's `recordings/` folder. That folder is ignored by git.
4. Sources > **+** > **macOS Screen Capture**, and choose the Roblox Studio window.
5. Hold **Option** and drag the red box's edges to crop it down to just the game view. Right-click > Transform > **Fit to screen**.
6. Settings > Audio: make sure desktop audio is captured, so the game's sounds are in the clip.
7. Press **Start Recording**, throw, let the whole reveal play, then **Stop Recording**. Record several takes.

## Then

Tell Claude which files in `recordings/` to use. Claude cuts the best moments with ffmpeg, adds zoom-ins and big on-screen text, and exports a vertical 1080x1920 mp4. Add a trending sound in the TikTok app when you post.

## What to film first

- **The reveal:** a map's rarest monster, Planet-Sized or Unit of Doom, with a Ghost or Shadow colour. Opening text like "I threw an egg... 1 in 1.6 TRILLION".
- **Tiny base, huge monster:** a giant monster standing on your plot.
- **A series:** "Rating every monster in my Roblox game, part 1", one map per video.

Every "1 in X" in a clip is the monster's real chance in the game. Don't say you caught it on a normal throw: say "the rarest monster in my game" instead.
