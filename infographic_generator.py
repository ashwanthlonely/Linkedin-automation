import os
import sys
import time
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

from news_fetcher import NewsFetcher

# Ensure UTF-8 stdout encoding on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class InfographicGenerator:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.logo_path = os.path.join(self.base_dir, "assets", "e2 logo (Custom).png")
        self.cartoons_dir = os.path.join(self.base_dir, "assets", "cartoons")
        self.news_fetcher = NewsFetcher(base_dir=self.base_dir)

    def create_infographic(self, topic_data=None, output_path=None):
        """Create a News Image Collage Banner compositing news images & EarEase Tech logo."""
        if not output_path:
            output_path = os.path.join(self.base_dir, "assets", "generated_infographic.jpg")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        print("🎨 Building News Image Collage Banner with extracted news images & EarEase Tech logo...")

        # 1. Fetch extracted news images
        news_images = self.news_fetcher.fetch_latest_news_and_images()

        # Canvas Size: 1200 x 750 (HD)
        canvas_w, canvas_h = 1200, 750
        header_h = 100
        footer_h = 42
        grid_h = canvas_h - header_h - footer_h

        # Palette
        bg_color = (15, 23, 42)        # slate-900
        header_bg = (30, 41, 59)      # slate-800
        card_bg = (30, 41, 59)        # slate-800
        card_border = (51, 65, 85)    # slate-700
        cyan_accent = (56, 189, 248)   # sky-400
        yellow_stat = (253, 224, 71)   # yellow-300
        text_primary = (255, 255, 255)
        text_muted = (148, 163, 184)  # slate-400

        canvas = Image.new("RGB", (canvas_w, canvas_h), bg_color)
        draw = ImageDraw.Draw(canvas)

        # Header Bar with Logo
        draw.rectangle([0, 0, canvas_w, header_h], fill=header_bg)
        draw.line([(0, header_h - 3), (canvas_w, header_h - 3)], fill=cyan_accent, width=3)

        logo_x, logo_y = 20, 15
        if os.path.exists(self.logo_path):
            try:
                logo = Image.open(self.logo_path).convert("RGBA")
                logo.thumbnail((70, 70))
                canvas.paste(logo, (logo_x, logo_y + (70 - logo.height) // 2), logo)
                text_left = 105
            except Exception:
                text_left = 25
        else:
            text_left = 25

        date_str = datetime.now().strftime("%B %d, %Y")
        draw.text((text_left, 20), "EarEase Tech  |  INDIAN MAJOR HEADLINES & GLOBAL PULSE", fill=text_primary)
        draw.text((text_left, 54), f"Extracted News Image Collage & Executive Summary  •  {date_str}", fill=cyan_accent)

        # 2. Render News Image Tiles Grid (2 rows x 3 cols)
        panel_w = (canvas_w - 32) // 3
        panel_h = (grid_h - 24) // 2

        # Grid configuration for 6 items
        grid_items = [
            {"title": "🚗 INDIAN AUTOMOBILE", "stat": "42% EV Growth", "img_info": news_images[0] if len(news_images) > 0 else None, "headline": "Tata & Mahindra Scaling Domestic EVs"},
            {"title": "🚀 INDIAN R&D & TECH", "stat": "ISRO & 5 Fabs", "img_info": news_images[1] if len(news_images) > 1 else None, "headline": "ISRO Space Expansion & Semiconductor Fabs"},
            {"title": "💰 INDIAN FINANCE & ECONOMY", "stat": "7.2% GDP | GIFT City", "img_info": news_images[2] if len(news_images) > 2 else None, "headline": "Macro Resilience & Strong GST Collection"},
            {"title": "🏛️ INDIAN POLITICS & POLICY", "stat": "Rs 1.97L Cr PLI", "img_info": news_images[3] if len(news_images) > 3 else None, "headline": "Cabinet Policy & Trade Corridor Alignment"},
            {"title": "🤖 AI & EMERGING TECH", "stat": "74% Enterprise AI", "img_info": news_images[4] if len(news_images) > 4 else None, "headline": "Agentic AI Systems & Sovereign Computing"},
            {"title": "🇮🇳 INDIA STRATEGIC VIEW", "stat": "#3 Global Tech Hub", "img_info": {"path": os.path.join(self.cartoons_dir, "india.jpg")}, "headline": "PLI Schemes & Sovereign AI Infra"}
        ]

        for idx, item in enumerate(grid_items):
            row = idx // 3
            col = idx % 3

            x1 = 8 + col * (panel_w + 8)
            y1 = header_h + 8 + row * (panel_h + 8)
            x2 = x1 + panel_w
            y2 = y1 + panel_h

            img_path = item["img_info"]["path"] if item["img_info"] and "path" in item["img_info"] else None

            # Paste News Image Tile
            if img_path and os.path.exists(img_path):
                try:
                    tile = Image.open(img_path).convert("RGB")
                    tw, th = tile.size
                    target_aspect = panel_w / panel_h
                    if tw / th > target_aspect:
                        nw = int(th * target_aspect)
                        tile = tile.crop(((tw - nw) // 2, 0, (tw - nw) // 2 + nw, th))
                    else:
                        nh = int(tw / target_aspect)
                        tile = tile.crop((0, (th - nh) // 2, tw, (th - nh) // 2 + nh))
                    tile = tile.resize((panel_w, panel_h))
                    canvas.paste(tile, (x1, y1))
                except Exception:
                    draw.rectangle([x1, y1, x2, y2], fill=card_bg)
            else:
                draw.rectangle([x1, y1, x2, y2], fill=card_bg)

            # Panel Border
            draw.rectangle([x1, y1, x2, y2], outline=card_border, width=2)

            # Top Badge Banner
            top_badge_h = 28
            draw.rectangle([x1, y1, x2, y1 + top_badge_h], fill=(15, 23, 42))
            draw.line([(x1, y1 + top_badge_h), (x2, y1 + top_badge_h)], fill=cyan_accent, width=1)
            draw.text((x1 + 8, y1 + 5), item["title"][:26], fill=(255, 255, 255))

            # Bottom Caption Overlay
            bot_box_h = 44
            draw.rectangle([x1, y2 - bot_box_h, x2, y2], fill=(15, 23, 42))
            draw.line([(x1, y2 - bot_box_h), (x2, y2 - bot_box_h)], fill=cyan_accent, width=1)
            draw.text((x1 + 8, y2 - bot_box_h + 4), f"STAT: {item['stat']}", fill=yellow_stat)
            draw.text((x1 + 8, y2 - bot_box_h + 24), f"• {item['headline'][:35]}", fill=text_muted)

        # 3. Footer Bar
        draw.rectangle([0, canvas_h - footer_h, canvas_w, canvas_h], fill=bg_color)
        draw.line([(0, canvas_h - footer_h), (canvas_w, canvas_h - footer_h)], fill=card_border, width=1)
        draw.text((25, canvas_h - 28), "EarEase Tech Pvt Ltd  •  Data Science & AI Leadership", fill=text_muted)
        draw.text((canvas_w - 260, canvas_h - 28), "Extracted News Image Collage", fill=cyan_accent)

        canvas.save(output_path, quality=95)
        print(f"✅ Generated News Image Collage Banner at '{output_path}'")
        return output_path


if __name__ == "__main__":
    gen = InfographicGenerator()
    out = gen.create_infographic()
    print("Created News Image Collage Banner at:", out)
