# Roblox Game Growth, Design, & Analytics Master Playbook

> **Instructions for AI Assistant (Claude):** 
> Use this document as your core reference framework when helping design features, diagnose analytics, write `AnalyticsService` funnel scripts, plan game updates, or improve monetization and retention for our Roblox game. Every suggestion you make should align with the principles, benchmarks, and scientific frameworks detailed below.

---

## Part 1: The 5 Pillars of a Viral Roblox Game (Core Design)
*Sourced from Tizzy RBLX (Creator of "Build a Base and Steal", 60K+ CCU) & VuukStudios (24K+ CCU)*

To reach 10,000+ Concurrent Users (CCU), a Roblox project should be evaluated against five core design criteria before and during development:

### 1. A Clickable Idea & Strong Core Fantasy
* **Fulfilling Childhood Imagination:** Viral concepts tap into wild scenarios kids imagine while trying to fall asleep—similar to hit movies like *Zootopia* ("what if animals ran a city?") or *Toy Story* ("what if toys came alive?").
* **Instant Homepage Appeal:** Games like *Animal Hospital* or *Fly to Space* package a clear, irresistible fantasy so compelling that players scrolling their homepage feel forced to click.

### 2. Emotionally Invested Onboarding
* **Establish the "Why" in the First 90 Seconds:** Do not treat the tutorial as a boring checklist of UI buttons to click. Use the first 90 seconds (often via a short cutscene) to make the player emotionally care.
  * *Example (*Build a Base and Steal*):* Show the player's pet getting stolen immediately so they feel the threat and genuinely want to build defenses.
* **"Show, Don't Tell" (Cause and Effect):** Young players do not read walls of text or click small "Help" buttons. Teach through immediate action and visual cause-and-effect, just like teaching a toddler to catch a baseball by throwing it rather than lecturing them.
  * *Example (*Grow a Garden*):* A new player plants a seed and immediately watches it sprout into a carrot, learning the core loop without reading "seeds make carrots."
* **Pacing & Level Design:** Introduce one mechanic at a time without cluttering the screen with UI or monetization pop-ups (*Sell Lemons* is the gold standard for clean UI onboarding).
* **Visual Level Design:** Use the environment to communicate the objective instantly upon spawning.
  * *Example (*Escape Tsunami for Brainrots*):* A massive wave is immediately visible in the distance when the player spawns, requiring zero text explanation of the threat.

### 3. Built-In Socialization & FOMO
* **The Word-of-Mouth Flywheel:** Games that are significantly more fun with friends (*99 Nights*) trigger an organic viral loop where players invite friends, who then invite more friends.
* **Social Flexing & Envy:** Even in solo incremental or tycoon games, bake visible progression, player interaction, and leaderboards into the core loop. Seeing a high-level player zoom past you at spawn or flexing rare items creates FOMO (Fear Of Missing Out) and drives long-term retention.

### 4. Simple Mechanics with High Depth & Frictionless UX
* **Infinite Replayability:** Rely on a single, easy-to-grasp mechanic that makes every session feel fresh—such as voxel building (*Build a Plane*, *Build a Boat for Treasure*), roleplaying (*Brookhaven*), or surviving different base layouts.
* **Frictionless Mobile UX:** Deep mechanics must remain effortless on touchscreens. 
  * *Lesson Learned:* *Build a Base and Steal* was held back from 100K+ CCU because tapping repeatedly to place individual voxel blocks on mobile created too much friction compared to pre-built base games. Always optimize controls for mobile and console players.

### 5. Clippability & Community-Driven Content
* **Design for Creators:** Build mechanics that naturally generate funny, tense, or impressive moments for YouTubers and TikTokers (e.g., painting characters to blend into hiding spots in *Mecha Chameleon* clones like *Paint or Die* / *Paint and Seek*, or stealing pets from other players).
* **User-Generated Sustenance:** When a simple mechanic allows players to show off creations (like TikTok tutorials on building an F-22 Raptor in *Build a Plane*), community content sustains high CCU for years.

### Development Speed & Prototyping Rules
* **Fast Prototyping:** Never spend 5+ months building an unproven idea in isolation. Aim to build a playable base game MVP within a few weeks to a month.
* **Smart AI Use:** Use AI on internal/personal projects to speed up coding and prototyping workflows when short on time.

---

## Part 2: How the Roblox Algorithm Works & Ad Strategy
*Sourced from VuukStudios & Psuedon*

### 1. The 3 Core Pillars of the Algorithm
* The Roblox recommendation algorithm is an automated filter designed to maximize three things: **Player Engagement, Retention, and Monetization**.
* **Competition-Based:** If your game isn't getting homepage impressions, its data is signaling to Roblox that it generates less engagement or revenue than competing games in the same niche.
* **The 7-Day Rolling Window:** Roblox evaluates game performance over a rolling 7-day window. Even if an update doubles your stats today, homepage impressions will not jump overnight. The algorithm requires a full week of consistently improved data to outweigh previous stats.

### 2. Paid Ads vs. Organic Traffic
* **Separate Systems:** Paid ad traffic and organic homepage recommendations operate independently. Buying ads when organic traffic drops will not force the algorithm to pick up a struggling game.
* **Why Ads Can Hurt an Unoptimized Game:** Sponsored ads optimize for the cheapest possible click rather than engaged players or spenders. Pouring ad money into a flawed core loop simply pays to feed the algorithm negative performance data, proving to Roblox that players don't like the game.
* **Launch Ad Budgeting (For Initial Data & Visibility):**
  * Because a brand-new game rarely enters the algorithm with zero traffic, budget **30,000 to 60,000 Robux ($100–$200 USD)** spread across a 1-to-2-week launch campaign, or an absolute minimum of **10,000 to 20,000 Robux ($50 USD)** unless you already have massive community hype.
  * **Build During Ads:** Real work starts at launch. Ship improvements and bug fixes daily *while* launch ads are running to actively improve the metrics being fed into the algorithm.

### 3. Knowing When to Pivot vs. Scale
Monitor **Acquisition $\rightarrow$ Home Recommendations** during and after your initial 1–2 week ad campaign:
* **Scenario A: Zero Home Recommendations:** If there are 0 Home Recommendations after 1–2 weeks of ads, stop spending and move on to a new game idea.
* **Scenario B: Small Recommendation Push (1K–5K Impressions):** Push one major update specifically targeting your weakest metrics (like retention or playtime). If it still fails to take off after the 7-day rolling window, cut the project.
* **Scenario C: Exponential Growth (e.g., 5K $\rightarrow$ 15K $\rightarrow$ 50K daily):** Scale the game aggressively with weekly or bi-weekly content updates and silent, same-day bug patches.

---

## Part 3: Complete Metric Diagnostic & Actionable Fixes
*Sourced from Tizzy RBLX & Psuedon*

When checking the Creator Analytics Overview screen, target the weakest metrics (highlighted by orange bars below benchmark) using these specific diagnostics and fixes:

### 1. First Session Retention (New Users)
* **Target Benchmarks:** Aim for **~95% at 30 seconds** and **~65% at 5 minutes**.
* **The 5-Minute Timer Diagnostic Trick:** Open `Analytics -> Engagement` (set to a 7-day window) and check the *New User First Session Retention* curve (which works like a YouTube retention graph). Find the exact timestamp where a steep drop-off occurs (e.g., at 2 minutes and 30 seconds). Open a timer on your phone, join your game as a fresh account, play normally, and see what is happening at that exact second.
* **Fixes:** Remove early friction, ensure fast loading on older/low-end devices, add obvious visual breadcrumbs/pointers so players never have to guess what to do next, and smooth out early bottlenecks.

### 2. Average Play Time
* **The Diagnosis:** Low playtime means your core gameplay loop feels flat, repetitive, or unsatisfying—or your thumbnail is misleading clickbait (causing players to leave immediately when the game doesn't match the image).
* **Fix 1 ("Action and Response" Game Feel):** Every micro-action a player takes needs immediate, tactile audiovisual feedback. For example, swinging a pickaxe at a rock must trigger a crisp impact sound effect, particles, and a subtle camera shake.
* **Fix 2 (Constant Micro-Goals):** Implement quick, easy-to-complete quests and multiple parallel progression tracks (XP, currency, index/collectibles) so players always feel 30 seconds away from accomplishing something rather than logging off.
* **Fix 3 (Remove Tedious Micro-Management):** Automate or streamline repetitive bottlenecks (especially on mobile).

### 3. Day 1 (D1) Retention
* **Target Benchmark:** Aim for at least **~15%+** to gain real algorithmic traction (higher for top hits).
* **The Diagnosis:** Low D1 retention almost always means your onboarding tutorial is broken or players lack a compelling reason to return tomorrow.
* **Fix 1 (Funnel Optimization & Hands-On Onboarding):** Use step-by-step funnels to find tutorial drop-offs and convert text instructions into interactive "show, don't tell" actions.
* **Fix 2 (Return Hooks):** Set clear short-term targets or big timed rewards waiting for the player when they rejoin.
* **Fix 3 (Offline Progression):** Popularized by hits like *Grow a Garden* and *Hack a Business*, allow players to earn currency, resources, or progress while offline. Whenever they see your game in their "Recently Played" tab, curiosity about how much they've accumulated drives them to click back in.

### 4. Day 7 (D7) Retention
* **The Diagnosis:** Players are running out of content or social motivation after mastering the basics.
* **Fix 1 (Social Flexing):** Give veteran players visible ways to show off their status, rare items, or bases to newer players in the server.
* **Fix 2 (Mid-to-Late Game Depth):** Ensure sufficient progression tiers and rebirth/endgame mechanics.
* **Fix 3 (Live "Admin Abuses" & Server Events):** Run chaotic, fun live developer/admin events and global server events that build community hype and keep veteran players logging in.

### 5. Payer Conversion Rate
* **The Diagnosis:** Players aren't making their first Robux purchase.
* **Fix 1 (Cheap Starter Pack):** Always offer a high-value, low-cost Starter Pack with a limited-time feel.
* **Fix 2 (Low-Cost Repeatable Micro-Consumables in the Core Loop):** Weave impulse-buy developer products directly into natural moments of the core loop.
  * *High-Converting Example (*Hack a Business*):* Every time a player rejoins and clicks to claim their offline earnings, prompt them: *"Would you like to double your offline earnings for 19 Robux?"* This single contextual prompt dramatically increases conversion rate.

### 6. Average Revenue Per Paying User (ARPPU)
* **The Diagnosis:** Whales (high spenders) don't have enough high-ticket items to buy.
* **Fix (3-Tier "McDonald's Fries" Bundle Pricing):** Just like Small, Medium, and Large fries, structure your packs and gamepasses into three distinct price tiers so spenders of every budget can self-select:
  1. **Starter Pack** (Cheap entry point)
  2. **Pro Pack** (Mid-tier value)
  3. **OP Pack** (Expensive, high-ticket bundle for whales)

### 7. Qualified Play Through Rate (QPTR) / Playthrough Rate
* **The Diagnosis:** Poor packaging (low click-through) or technical failure upon joining.
* **Fixes:** Test and upgrade your game's **Thumbnail and Title** (packaging), and ensure fast initial load times and immediate transition into gameplay.

---

## Part 4: Roblox Funnel Analytics — Technical Implementation & Strategy
*Sourced from Official Roblox Creator Analytics Team (Peter & Andrew) & Tizzy RBLX*

### 1. Why Funnels Are Non-Negotiable
Funnels track step-by-step user progression (onboarding tutorials, core loops, shop checkouts, dungeon progression) to pinpoint the exact step where players drop off. Fixing these bottlenecks directly boosts D1 retention and session length.

### 2. The Two Types of Funnels
* **One-Time Funnels:** For flows a player only completes once ever (e.g., First-Time User Onboarding Tutorial, linear story progression).
* **Recurring Funnels:** For actions players repeat many times in a single session or across sessions (e.g., Shop Checkout Flow: *Open Shop $\rightarrow$ Select Item $\rightarrow$ Buy Item $\rightarrow$ Close Shop*, or upgrading weapons).

### 3. Critical Scripting Rules (`AnalyticsService`)
When implementing funnels in Luau via `AnalyticsService:LogOnboardingFunnelStepEvent()` or `AnalyticsService:LogFunnelStepEvent()`, strictly follow these technical rules:
1. **Manual Step 1 Logging:** Roblox does **not** automatically log Step 1 when a player joins. If your funnel starts on join, you must explicitly fire Step 1 inside a `Players.PlayerAdded` event.
2. **Unique `funnelSessionId` for Recurring Funnels:** Recurring funnels require a unique `funnelSessionId` (such as a `HttpService:GenerateGUID()` per shop session, or combining `player.UserId .. "_" .. itemName` when tracking upgrades for a specific item) to separate individual instances of a repeatable flow.
3. **Duplicate & Skipped Steps Behavior:**
   * If code accidentally fires the exact same step twice for a session, Roblox automatically collapses them into a single step.
   * If a player skips from Step 1 straight to Step 5, Roblox automatically marks Steps 2, 3, and 4 as completed.
4. **Custom Field Filtering Rule (CRITICAL):** You can pass up to 3 custom fields (`Enum.AnalyticsCustomFieldKeys`). However, the Roblox Analytics dashboard filter **only recognizes custom field values sent on Step 1** of the funnel. Changing or adding custom fields on Step 2 or later will be ignored by dashboard filters.
5. **Server-Side Security & Validation:** Never allow a `RemoteEvent` from the client to directly log funnel steps on the server without strict server-side state validation. Otherwise, exploiters can spam fake steps and corrupt your analytics charts.

### 4. Funnel Best Practices & Segmentation
* **Instrument Before Building a Tutorial:** Even if your game doesn't have an official tutorial yet, log the steps of your raw core loop first. Seeing where players naturally get stuck tells you exactly what your tutorial needs to focus on.
* **Slice by Device/Platform:** Always filter funnels by Platform (Mobile vs. PC vs. Console). A sharp drop-off on Mobile at a specific step usually reveals a broken touchscreen UI button or clunky mobile control (like voxel placement friction).
* **Slice by Age:** Younger players (Under 13) drop off at higher rates when steps rely on reading text instructions rather than visual arrows/breadcrumbs.
* **Spotting Difficulty Spikes (*Fabled Legacy* Case Study):** Track progression rooms/waves (*Join $\rightarrow$ Select Class $\rightarrow$ Load Dungeon $\rightarrow$ Room 1 $\rightarrow$ Room 2...*). In *Fabled Legacy*, a 21% drop-off at Room 2 revealed an early difficulty spike, allowing the devs to smooth enemy scaling or grant an earlier power-up.

---

## Part 5: The E-Commerce CRO Iterative Framework for Updates
*Sourced from Tizzy RBLX (Case Study: Scaling "Hack a Business" to 1,000+ CCU & $6K/mo in 2 weeks)*

Treat every game update like a high-stakes Conversion Rate Optimization (CRO) A/B test. Never push random updates blindly.

### 1. Updates as Scientific Hypotheses
Every update or hotfix you ship is an educated guess that must fit one of three templates:
1. *"If we **add** [Y feature/mechanic], then [X metric] will improve."*
2. *"If we **remove** [Y friction/feature], then [X metric] will improve."*
3. *"If we **improve** [Y feature/economy value], then [X metric] will improve."*

### 2. Triangulate 3 Data Sources Before Coding
To ensure your hypothesis has the highest probability of succeeding, cross-reference three distinct buckets of evidence:
1. **Qualitative Data ("Voice of the Player"):**
   * **Live Player Observation (Most Overlooked Method):** Join live public servers anonymously and watch real players play your game. See where they hesitate, get confused, or quit.
   * **Creator Dashboard Feedback Tab:** Read player thumbs-up/thumbs-down comments under `Audience -> Feedback`.
   * **Community Discord:** Read player suggestions and bug reports.
2. **Quantitative Data ("The Numbers"):**
   * Creator Dashboard retention curves (e.g., First Session Retention timestamp drop-offs), Funnel step drop-off percentages, and engagement benchmarks.
3. **Competitor Research:**
   * Study top-performing games in your exact genre/niche to see how they solved the same mechanic, pacing, or UI problem.

### 3. Real-World Case Study: Fixing Play Time in *Hack a Business*
* **Qualitative Evidence:** Players in Discord suggested allowing plot antennas to collect data from multiple servers automatically instead of manually collecting from one server at a time.
* **Competitor Evidence:** Looking at the genre inspiration (*Oil Empire*), the devs noticed *Oil Empire* allowed collecting gas from multiple refineries simultaneously.
* **Quantitative Evidence:** The *New User First Session Retention* graph showed a sharp drop-off at **2 minutes and 30 seconds**. Using the 5-minute timer trick, they saw 2:30 was the exact moment players got bored of tedious single-server collection.
* **The Hypothesis:** *"If we allow all servers to collect data at the same time, it will create a much smoother user experience—especially on mobile—and increase Average Play Time."*
* **The Result:** They shipped the update, verified that Average Play Time increased, and kept the feature.

### 4. The 4-Step Iterative Loop (Daily/Weekly Workflow)
Repeat this cycle continuously:
1. **Research:** Gather Qualitative (live observation, feedback, Discord), Quantitative (funnels, retention curves), and Competitor evidence.
2. **Form a Hypothesis:** Write a clear cause-and-effect prediction targeting a specific weak metric.
3. **Launch the Update:** Ship the change quickly (aim for daily or rapid iterative patches during launch).
4. **Check Results:** Measure whether the target stat actually improved.
   * **If YES:** Keep the update, return to Step 1, and target the next bottleneck.
   * **If NO:** **Revert the change**, return to Step 1, formulate a new hypothesis, and test again.