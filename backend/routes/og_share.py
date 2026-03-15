"""OG share routes — dynamic meta tags + OG image generation for social sharing."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, Response
from bson import ObjectId
from PIL import Image, ImageDraw, ImageFont
import os
import io
import math

router = APIRouter()

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "philos")

from pymongo import MongoClient
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

SITE_URL = os.environ.get("SITE_URL", "https://philos-mvp.preview.emergentagent.com")

# Fonts
FONT_BOLD = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

CATEGORY_COLORS = {
    "education": (124, 58, 237), "environment": (16, 185, 129), "health": (244, 63, 94),
    "community": (0, 212, 255), "technology": (245, 158, 11), "mentorship": (236, 72, 153),
    "volunteering": (139, 92, 246), "other": (107, 114, 128),
}


def _get_action(action_id: str):
    try:
        oid = ObjectId(action_id)
    except Exception:
        return None
    action = db.impact_actions.find_one({"_id": oid})
    if not action:
        return None
    return {
        "id": str(action["_id"]),
        "user_name": action.get("user_name", "Anonymous"),
        "title": action.get("title", ""),
        "description": action.get("description", ""),
        "category": action.get("category", "other"),
        "community": action.get("community", ""),
        "trust_signal": action.get("trust_signal", 0),
        "reactions": action.get("reactions", {}),
    }


@router.get("/share/action/{action_id}", response_class=HTMLResponse)
async def share_action_page(action_id: str):
    """Serve HTML with OG meta tags for social crawlers. Redirects real users to SPA."""
    action = _get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    user_name = action["user_name"]
    title = action["title"]
    community = action["community"]
    trust = int(action["trust_signal"])
    category = action["category"]

    og_title = f"{user_name} helped {community} — {title}" if community else f"{user_name} — {title}"
    og_desc = f"Trust Score: {trust} • Category: {category.capitalize()}"
    og_image = f"{SITE_URL}/api/og/action/{action_id}/image"
    og_url = f"{SITE_URL}/api/share/action/{action_id}"
    spa_url = f"{SITE_URL}/app/action/{action_id}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <title>{_esc(og_title)}</title>
    <meta name="description" content="{_esc(og_desc)}" />

    <meta property="og:title" content="{_esc(og_title)}" />
    <meta property="og:description" content="{_esc(og_desc)}" />
    <meta property="og:image" content="{og_image}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:url" content="{og_url}" />
    <meta property="og:type" content="article" />
    <meta property="og:site_name" content="Philos Orientation System" />

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{_esc(og_title)}" />
    <meta name="twitter:description" content="{_esc(og_desc)}" />
    <meta name="twitter:image" content="{og_image}" />

    <meta http-equiv="refresh" content="0;url={spa_url}" />
</head>
<body>
    <p>Redirecting to <a href="{spa_url}">Philos</a>...</p>
</body>
</html>"""
    return HTMLResponse(content=html)


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


@router.get("/og/action/{action_id}/image")
async def og_action_image(action_id: str):
    """Generate a 1200x630 OG image for the action."""
    action = _get_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    img = _generate_og_image(action)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png",
                    headers={"Cache-Control": "public, max-age=3600"})


def _generate_og_image(action: dict) -> Image.Image:
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (6, 6, 18))
    draw = ImageDraw.Draw(img)

    # Gradient top bar
    for x in range(W):
        r = int(0 + (124 - 0) * x / W)
        g = int(212 + (58 - 212) * x / W)
        b = int(255 + (237 - 255) * x / W)
        draw.line([(x, 0), (x, 4)], fill=(r, g, b))

    # Load fonts
    try:
        font_title = ImageFont.truetype(FONT_BOLD, 38)
        font_subtitle = ImageFont.truetype(FONT_REGULAR, 22)
        font_small = ImageFont.truetype(FONT_REGULAR, 18)
        font_trust = ImageFont.truetype(FONT_BOLD, 56)
        font_badge = ImageFont.truetype(FONT_BOLD, 13)
        font_brand = ImageFont.truetype(FONT_BOLD, 16)
    except Exception:
        font_title = ImageFont.load_default()
        font_subtitle = font_small = font_trust = font_badge = font_brand = font_title

    pad_x = 72
    y = 50

    # "PHILOS IMPACT ACTION" badge
    draw.text((pad_x, y), "PHILOS IMPACT ACTION", fill=(255, 255, 255, 60), font=font_badge)
    y += 40

    # Avatar circle
    avatar_size = 52
    avatar_x, avatar_y = pad_x, y
    cat_color = CATEGORY_COLORS.get(action["category"], (0, 212, 255))
    _draw_circle(draw, avatar_x, avatar_y, avatar_size, (0, 212, 255), (124, 58, 237))
    initial = (action["user_name"] or "?")[0].upper()
    try:
        font_avatar = ImageFont.truetype(FONT_BOLD, 24)
    except Exception:
        font_avatar = font_title
    bbox = draw.textbbox((0, 0), initial, font=font_avatar)
    iw, ih = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((avatar_x + (avatar_size - iw) // 2, avatar_y + (avatar_size - ih) // 2 - 2),
              initial, fill=(255, 255, 255), font=font_avatar)

    # User name
    draw.text((pad_x + avatar_size + 16, y + 6), action["user_name"], fill=(255, 255, 255), font=font_subtitle)
    y += avatar_size + 30

    # Title (word-wrapped)
    title_text = action["title"]
    max_title_w = W - pad_x * 2 - 200
    lines = _wrap_text(draw, title_text, font_title, max_title_w)
    for line in lines[:3]:
        draw.text((pad_x, y), line, fill=(255, 255, 255), font=font_title)
        y += 48

    y += 12

    # Community
    if action["community"]:
        draw.text((pad_x, y), f"Community: {action['community']}", fill=(0, 212, 255), font=font_small)
        y += 30

    # Category
    draw.text((pad_x, y), f"Category: {action['category'].capitalize()}", fill=(160, 160, 180), font=font_small)
    y += 30

    # Reactions summary
    reactions = action.get("reactions", {})
    support_c = len(reactions.get("support", [])) if isinstance(reactions.get("support"), list) else reactions.get("support", 0)
    useful_c = len(reactions.get("useful", [])) if isinstance(reactions.get("useful"), list) else reactions.get("useful", 0)
    verified_c = len(reactions.get("verified", [])) if isinstance(reactions.get("verified"), list) else reactions.get("verified", 0)
    total_reactions = support_c + useful_c + verified_c
    if total_reactions > 0:
        rx_text = f"{support_c} Support · {useful_c} Useful · {verified_c} Verified"
        draw.text((pad_x, y), rx_text, fill=(120, 120, 140), font=font_small)

    # Trust Score (right side, large)
    trust = int(action["trust_signal"])
    if trust > 0:
        trust_str = str(trust)
        bbox = draw.textbbox((0, 0), trust_str, font=font_trust)
        tw = bbox[2] - bbox[0]
        tx = W - pad_x - tw
        ty = 140
        # Glow circle behind
        _draw_glow(draw, tx + tw // 2, ty + 30, 50, (245, 158, 11))
        draw.text((tx, ty), trust_str, fill=(245, 158, 11), font=font_trust)
        # Label
        bbox2 = draw.textbbox((0, 0), "Trust Score", font=font_small)
        lw = bbox2[2] - bbox2[0]
        draw.text((tx + (tw - lw) // 2, ty + 64), "Trust Score", fill=(200, 160, 80), font=font_small)

    # Bottom bar
    draw.line([(0, H - 60), (W, H - 60)], fill=(30, 30, 50), width=1)
    draw.text((pad_x, H - 44), "Philos Orientation System", fill=(0, 212, 255), font=font_brand)
    draw.text((W - pad_x - 200, H - 44), "philos-mvp.preview.emergentagent.com",
              fill=(80, 80, 100), font=font_small)

    return img


def _draw_circle(draw, x, y, size, color1, color2):
    for i in range(size):
        for j in range(size):
            dx, dy = i - size // 2, j - size // 2
            if dx * dx + dy * dy <= (size // 2) ** 2:
                t = i / size
                r = int(color1[0] + (color2[0] - color1[0]) * t)
                g = int(color1[1] + (color2[1] - color1[1]) * t)
                b = int(color1[2] + (color2[2] - color1[2]) * t)
                draw.point((x + i, y + j), fill=(r, g, b))


def _draw_glow(draw, cx, cy, radius, color):
    for r in range(radius, 0, -1):
        alpha = int(15 * (r / radius))
        c = (color[0], color[1], color[2])
        faded = (c[0] * alpha // 255, c[1] * alpha // 255, c[2] * alpha // 255)
        merged = (6 + faded[0], 6 + faded[1], 18 + faded[2])
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=merged)


def _wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
