-- The drawn backdrop behind a caught monster in the reveal's showcase (docs/GAME_SPEC.md section 7, Config/Reveal showcase
-- backdrop). [Owner, 2026-11-11: "make sure that monsters are visible... fill the screen with better visuals"] From the
-- unveil on, everything behind the monster is swapped for art in its rarity's colours, so it stands out on any world and
-- nothing far away distracts from it. It's a screen-sized picture standing in the 3D world just behind the monster, facing
-- the camera: the monster, its egg and the ground in front stay real and cover it; the far walls, the sky and the next
-- world are behind it. A dark monster gets a bright backdrop and a bright one a dark backdrop.
-- Four backdrops, one per camera angle: "burst" (turning rays and dots), "focus" (speed lines closing in on the face),
-- "streak" (lines flying sideways), "cosmos" (outer space with an eclipse, for the rarest). The art was drawn in Figma
-- "Throw Eggs - Reveal Showcase" and uploaded white, so the game tints it. RevealShowcase plays it. Display only.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Reveal = require(ReplicatedStorage.Shared.Config.Reveal)
local UiKit = require(ReplicatedStorage.Shared.UiKit)

local RevealBackdrop = {}

local settings = Reveal.showcase.backdrop
local images = settings.images
local WHITE = Color3.new(1, 1, 1)
local BLACK = Color3.new(0, 0, 0)
local SPACE = Color3.fromRGB(7, 5, 22)
local OVER = 1.3 -- the picture is this much bigger than the screen, so a shaking camera never shows its edge
local VIGNETTE = Reveal.walk.glow.darkImage -- built into Roblox: black at the edges, clear in the middle

-- How see-through each piece is in each backdrop; a piece left out is hidden.
local STYLES = {
	burst = { Burst = 0.82, Glow = 0.3, HalftoneBottom = 0.72, HalftoneTop = 0.86, Wall = true, Vignette = 0.5 },
	focus = { Lines = 0.12, Glow = 0.5, Vignette = 0.3 },
	streak = { StreaksA = 0.3, StreaksB = 0.6, Glow = 0.45, HalftoneBottom = 0.8, Vignette = 0.45 },
	cosmos = { StarsA = 0, StarsB = 0.4, NebulaA = 0.5, NebulaB = 0.6, Corona = 0, Disc = true, Burst = 0.9, Wall = true, Vignette = 0.4 },
}

local function brightness(color: Color3): number
	return 0.3 * color.R + 0.59 * color.G + 0.11 * color.B
end

-- `color` lifted towards white until it's at least `least` bright.
local function atLeast(color: Color3, least: number): Color3
	local now = brightness(color)
	return if now < least then color:Lerp(WHITE, (least - now) / (1 - now)) else color
end

-- `color` sunk towards black until it's at most `most` bright.
local function atMost(color: Color3, most: number): Color3
	local now = brightness(color)
	return if now > most then color:Lerp(BLACK, 1 - most / now) else color
end

-- How bright the monster is over all, 0 black to 1 white, from its parts' colours. Work it out before anything darkens
-- them (RevealDrama shade).
function RevealBackdrop.tone(model: Model): number
	local total, weight = 0, 0
	for _, part in model:GetDescendants() do
		if part:IsA("BasePart") and part.Transparency < 0.9 then
			local size = part.Size
			local area = size.X * size.Y + size.Y * size.Z + size.X * size.Z
			total += brightness(part.Color) * area
			weight += area
		end
	end
	return if weight > 0 then total / weight else 0.5
end

export type Backdrop = {
	style: (name: string) -> (),
	update: (now: number, camera: Camera) -> (),
	destroy: () -> (),
}

-- options: box, size (round the monster and its egg), light, deep (the rarity's colours), accent (its bright text
-- colour or the luck label's), tone (RevealBackdrop.tone), name (written in giant letters behind it, or nil), cosmos.
function RevealBackdrop.new(options): Backdrop
	local box: CFrame, size: Vector3 = options.box, options.size
	local light: Color3, deep: Color3, accent: Color3 = options.light, options.deep, options.accent
	local darkMonster = options.tone < settings.darkBelow

	-- The base colours, top and bottom, for each backdrop: bright behind a dark monster, dark behind a bright one.
	local bases = if darkMonster
		then {
			burst = { atLeast(deep:Lerp(light, 0.55), 0.55), atLeast(deep:Lerp(light, 0.1), 0.32) },
			focus = { atLeast(deep:Lerp(light, 0.45), 0.5), atLeast(deep, 0.3) },
			streak = { atLeast(deep:Lerp(light, 0.5), 0.52), atLeast(deep, 0.3) },
			cosmos = { SPACE, atMost(deep, 0.12):Lerp(SPACE, 0.3) },
		}
		else {
			burst = { atMost(deep:Lerp(BLACK, 0.25), 0.28), atMost(deep:Lerp(BLACK, 0.62), 0.13) },
			focus = { atMost(deep:Lerp(BLACK, 0.35), 0.22), atMost(deep:Lerp(BLACK, 0.75), 0.07) },
			streak = { atMost(deep:Lerp(BLACK, 0.35), 0.24), atMost(deep:Lerp(BLACK, 0.7), 0.1) },
			cosmos = { SPACE, atMost(deep, 0.12):Lerp(SPACE, 0.3) },
		}
	local rays = if darkMonster then WHITE else accent:Lerp(WHITE, 0.35)
	local lines = if darkMonster then atMost(deep:Lerp(BLACK, 0.5), 0.12) else accent:Lerp(WHITE, 0.5)
	local dots = atMost(deep:Lerp(BLACK, 0.6), 0.1)
	local halo = WHITE:Lerp(atLeast(light, 0.5), 0.55)

	local corners = {}
	for _, x in { -1, 1 } do
		for _, y in { -1, 1 } do
			for _, z in { -1, 1 } do
				table.insert(corners, box * (size / 2 * Vector3.new(x, y, z)))
			end
		end
	end
	local pad = size.Magnitude * settings.pad + 0.5
	local radius = size.Magnitude / 2 * 0.75
	local high = box.Position + Vector3.new(0, size.Y * 0.2, 0) -- where the eclipse sits: behind its shoulders

	local anchor = Instance.new("Part")
	anchor.Name = "RevealBackdrop"
	anchor.Anchored = true
	anchor.CanCollide = false
	anchor.CanQuery = false
	anchor.CanTouch = false
	anchor.CastShadow = false
	anchor.Transparency = 1
	anchor.Size = Vector3.one
	anchor.Parent = workspace

	local gui = Instance.new("BillboardGui")
	gui.Name = "RevealBackdrop"
	gui.Adornee = anchor
	gui.AlwaysOnTop = false -- the monster in front covers it
	gui.LightInfluence = 0
	gui.MaxDistance = math.huge
	gui.ClipsDescendants = true
	gui.ResetOnSpawn = false
	gui.Active = false
	gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
	gui.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")

	local canvas = Instance.new("Frame")
	canvas.Name = "Base"
	canvas.Size = UDim2.fromScale(1, 1)
	canvas.BackgroundColor3 = WHITE
	canvas.BorderSizePixel = 0
	canvas.Parent = gui
	local baseColors = Instance.new("UIGradient")
	baseColors.Rotation = 90
	baseColors.Parent = canvas

	local pieces: { [string]: ImageLabel } = {}
	local function piece(name: string, image: string, color: Color3, order: number, tiled: boolean?): ImageLabel
		local label = Instance.new("ImageLabel")
		label.Name = name
		label.AnchorPoint = Vector2.new(0.5, 0.5)
		label.Position = UDim2.fromScale(0.5, 0.5)
		label.BackgroundTransparency = 1
		label.Image = image
		label.ImageColor3 = color
		label.ImageTransparency = 1
		label.Visible = false
		label.ZIndex = order
		if tiled then
			label.ScaleType = Enum.ScaleType.Tile
		end
		label.Parent = canvas
		pieces[name] = label
		return label
	end
	piece("StarsB", images.stars, WHITE, 1, true)
	piece("StarsA", images.stars, WHITE, 2, true)
	piece("NebulaA", images.glow, accent, 3)
	piece("NebulaB", images.glow, atLeast(light, 0.35), 3)
	piece("HalftoneTop", images.halftone, dots, 4, true).Rotation = 180
	piece("HalftoneBottom", images.halftone, dots, 4, true)
	piece("StreaksB", images.streaks, lines, 5, true)
	piece("StreaksA", images.streaks, lines, 6, true)
	piece("Burst", images.sunburst, rays, 7)
	piece("Glow", images.glow, halo, 8)
	piece("Corona", images.corona, accent:Lerp(WHITE, 0.55), 10)
	piece("Lines", images.speedLines, lines, 13)
	piece("Vignette", VIGNETTE, BLACK, 14)

	-- The dark moon in front of the eclipse's light.
	local disc = Instance.new("Frame")
	disc.Name = "Disc"
	disc.AnchorPoint = Vector2.new(0.5, 0.5)
	disc.BackgroundColor3 = SPACE
	disc.BorderSizePixel = 0
	disc.Visible = false
	disc.ZIndex = 11
	disc.Parent = canvas
	local round = Instance.new("UICorner")
	round.CornerRadius = UDim.new(0.5, 0)
	round.Parent = disc

	-- The name in giant letters behind the monster, like a film poster.
	local wall: TextLabel? = nil
	if options.name then
		local label = Instance.new("TextLabel")
		label.Name = "Wall"
		label.AnchorPoint = Vector2.new(0.5, 0.5)
		label.BackgroundTransparency = 1
		label.FontFace = UiKit.FONT
		label.Text = options.name
		label.TextScaled = true
		label.TextWrapped = true
		label.Rotation = -4
		label.TextColor3 = if darkMonster then atMost(deep:Lerp(BLACK, 0.3), 0.2) else atLeast(light, 0.6)
		label.TextTransparency = 0.72
		label.Visible = false
		label.ZIndex = 12 -- in front of the eclipse: the monster still covers them
		label.Parent = canvas
		local outline = Instance.new("UIStroke")
		outline.Color = label.TextColor3
		outline.Transparency = 0.3
		outline.Thickness = 4
		outline.LineJoinMode = Enum.LineJoinMode.Round
		outline.Parent = label
		wall = label
	end

	local current = STYLES.burst
	local glowSize = 1 -- how big the light behind the monster is, against its usual size

	local function style(name: string)
		current = STYLES[name] or STYLES.burst
		local base = bases[name] or bases.burst
		baseColors.Color = ColorSequence.new(base[1], base[2])
		for pieceName, label in pieces do
			local seeThrough = current[pieceName]
			label.Visible = seeThrough ~= nil
			label.ImageTransparency = seeThrough or 1
		end
		-- A dark monster is read by its outline, so the light behind it is stronger. In space it gets no dark moon, which
		-- would swallow it [seen 2026-11-11: a Shadow Endless Grief was only teeth and eyes]: it stands in front of a
		-- blazing star instead.
		local star = darkMonster and name == "cosmos"
		glowSize = if star then 1.6 else 1
		if darkMonster then
			pieces.Glow.Visible = true
			pieces.Glow.ImageTransparency = if star then 0.05 else (current.Glow or 0.5) * 0.5
		end
		disc.Visible = current.Disc == true and not darkMonster
		if wall then
			wall.Visible = current.Wall == true
			-- Light letters on a dark backdrop, dark ones on a bright one.
			local lit = name == "cosmos" or not darkMonster
			local color = if lit then atLeast(light, 0.6) else atMost(deep:Lerp(BLACK, 0.3), 0.2)
			wall.TextColor3 = color
			local outline = wall:FindFirstChildOfClass("UIStroke")
			if outline then
				outline.Color = color
			end
		end
	end

	local function update(now: number, camera: Camera)
		local view = camera.CFrame
		local eye, look = view.Position, view.LookVector
		local viewport = camera.ViewportSize
		-- Just behind the monster's furthest point, straight ahead of the camera, so it fills the screen exactly.
		local depth = 1
		for _, corner in corners do
			depth = math.max(depth, (corner - eye):Dot(look))
		end
		anchor.CFrame = CFrame.new(eye + look * (depth + pad))
		local width, height = viewport.X * OVER, viewport.Y * OVER
		gui.Size = UDim2.fromOffset(width, height)

		-- Where the monster is on the screen, from its middle, and how big.
		local function spot(point: Vector3): Vector2
			local seen = camera:WorldToViewportPoint(point)
			if seen.Z <= 0 then
				return Vector2.zero
			end
			return Vector2.new(seen.X - viewport.X / 2, seen.Y - viewport.Y / 2)
		end
		local middle = spot(box.Position)
		local away = math.max((box.Position - eye):Dot(look), 1)
		local tanUp = math.tan(math.rad(camera.FieldOfView) / 2)
		local across = radius / away / tanUp * viewport.Y -- the monster's size on the screen, roughly, in pixels
		local diagonal = viewport.Magnitude
		local at = UDim2.new(0.5, middle.X, 0.5, middle.Y)

		local function square(label: GuiObject, side: number, where: UDim2)
			label.Size = UDim2.fromOffset(side, side)
			label.Position = where
		end
		if current.Burst then
			square(pieces.Burst, diagonal * 2.4, at)
			pieces.Burst.Rotation = (now * settings.spin) % 360
		end
		if pieces.Glow.Visible then
			square(pieces.Glow, math.max(across * 2.2, viewport.Y * 0.7) * glowSize, at)
		end
		if current.Lines then
			-- They jump round a few times a second, like the drawn lines of a comic.
			local jump = math.floor(now * settings.flicker)
			square(pieces.Lines, diagonal * (1.15 + 0.06 * (jump % 3)), UDim2.fromScale(0.5, 0.5)) -- round the face, mid-screen
			pieces.Lines.Rotation = (jump * 47) % 360
		end
		if current.HalftoneBottom then
			local band = height * 0.42
			pieces.HalftoneBottom.Size = UDim2.new(1, 0, 0, band)
			pieces.HalftoneBottom.Position = UDim2.new(0.5, 0, 1, -band / 2)
			pieces.HalftoneBottom.TileSize = UDim2.fromOffset(band, band)
		end
		if current.HalftoneTop then
			local band = height * 0.3
			pieces.HalftoneTop.Size = UDim2.new(1, 0, 0, band)
			pieces.HalftoneTop.Position = UDim2.new(0.5, 0, 0, band / 2)
			pieces.HalftoneTop.TileSize = UDim2.fromOffset(band, band)
		end
		-- A tiled layer sliding sideways for ever: it's one tile wider than the picture and jumps back a tile's width.
		local function slide(label: ImageLabel, tile: number, tileHeight: number, moved: number, down: number)
			label.Size = UDim2.new(1, tile * 2, 1, 0)
			label.TileSize = UDim2.fromOffset(tile, tileHeight)
			label.Position = UDim2.new(0.5, tile / 2 - moved % tile, 0.5, down)
		end
		if current.StreaksA then
			local speed = settings.streakSpeed * viewport.Y
			slide(pieces.StreaksA, height * 1.6, height * 0.8, now * speed, 0)
			slide(pieces.StreaksB, height * 1.1, height * 0.55, now * speed * 0.55, height * 0.07)
		end
		if current.StarsA then
			local drift = settings.starDrift * viewport.Y
			slide(pieces.StarsA, height * 1.1, height * 1.1, now * drift, 0)
			slide(pieces.StarsB, height * 0.7, height * 0.7, now * drift * 0.5, 0)
			square(pieces.NebulaA, viewport.Y * 1.5, UDim2.new(0.5, middle.X - viewport.X * 0.28, 0.5, middle.Y - viewport.Y * 0.1))
			square(pieces.NebulaB, viewport.Y * 1.3, UDim2.new(0.5, middle.X + viewport.X * 0.3, 0.5, middle.Y + viewport.Y * 0.16))
			-- The eclipse stands behind its shoulders, its ring of light showing all round it.
			local shoulders = spot(high)
			local ring = math.clamp(across * 1.9, viewport.Y * 0.7, viewport.Y * 2.4)
			local where = UDim2.new(0.5, shoulders.X, 0.5, shoulders.Y)
			square(pieces.Corona, ring, where)
			pieces.Corona.Rotation = (now * settings.spin * 0.4) % 360
			square(disc, ring * 0.495, where)
		end
		square(pieces.Vignette, math.max(width, height) * 1.25, UDim2.fromScale(0.5, 0.5))
		if wall and wall.Visible then
			wall.Size = UDim2.fromOffset(viewport.X * 0.94, viewport.Y * 0.5)
			wall.Position = UDim2.new(0.5, middle.X * 0.3, 0.5, middle.Y * 0.3 - viewport.Y * 0.14)
		end
	end

	style(if options.cosmos then "cosmos" else "burst")

	return {
		style = style,
		update = update,
		destroy = function()
			anchor:Destroy()
			gui:Destroy()
		end,
	}
end

return RevealBackdrop
