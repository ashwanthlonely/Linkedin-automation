import os
import sys
import base64
import random
import urllib.parse
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Ensure UTF-8 stdout encoding on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class ImageGenerator:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.logo_path = os.path.join(self.base_dir, "assets", "e2 logo (Custom).png")
        self.cartoons_dir = os.path.join(self.base_dir, "assets", "cartoons")
        self.gemini_key = (os.getenv("gemini_api_key") or os.getenv("GEMINI_API_KEY") or "").strip()
        self.hf_token = (os.getenv("huggingface_access_token") or "").strip()

    def generate_news_cover_image(self, headline_topic=None, news_summary=None, output_path=None):
        """Generate a 16:9 1920x1080 premium editorial AI visual data infographic cover image with brand logo."""
        if not output_path:
            output_path = os.path.join(self.base_dir, "assets", "generated_cover.jpg")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        topic = headline_topic or "Global & India Executive Pulse: AI, Auto, R&D, Finance & Geopolitics"
        summary = news_summary or "Agentic AI workflows scaling enterprise compute, Tata & Mahindra EV expansion, ISRO space milestones, 7.2% GDP growth, and GIFT City capital inflows."

        # Structured 16:9 editorial visual data prompt matching user's exact specification
        prompt = (
            f"Ultra premium editorial LinkedIn news infographic 16:9 format 1920x1080. "
            f"DESIGN PRIORITY: 80-90% VISUAL DATA, 10-20% TEXT. Use charts, maps, icons, stats, diagrams, timelines to tell story. "
            f"NEWS TOPIC: {topic}. CORE STORY: {summary}. "
            f"Bloomberg Reuters Financial Times visual data journalism style. Global news flowing into India world map. "
            f"Photorealistic 3D data visualization, clean charts, geographic nodes, sophisticated light editorial background, crisp composition, no watermark, 4k"
        )

        print("🎨 Generating 16:9 1920x1080 AI Editorial Data Infographic Cover (FLUX Model)...")

        # Method 1: FLUX.1 State-of-the-Art AI Engine (75s Timeout)
        flux_img = self._generate_flux_image(prompt)
        if flux_img:
            final_img = self._overlay_brand_logo_and_header(flux_img)
            final_img.save(output_path, quality=95)
            print(f"✅ Generated 16:9 1920x1080 AI Editorial Infographic Cover via FLUX.1 at '{output_path}'")
            return output_path

        # Method 2: Try Gemini API if available
        if self.gemini_key:
            gemini_img = self._generate_gemini_image(prompt)
            if gemini_img:
                final_img = self._overlay_brand_logo_and_header(gemini_img)
                final_img.save(output_path, quality=95)
                print(f"✅ Generated Editorial Data Infographic Cover via Gemini API at '{output_path}'")
                return output_path

        # Method 3: Rich Visual Composite Fallback
        poster_img = self._create_executive_poster()
        poster_img.save(output_path, quality=95)
        print(f"✅ Generated visual infographic cover at '{output_path}'")
        return output_path

    def _generate_flux_image(self, prompt):
        """Generate high-res 16:9 FLUX.1 AI artwork image (75s timeout to guarantee AI generation)."""
        models = ["flux", "flux-realism", "turbo"]
        for m in models:
            try:
                seed = random.randint(1000, 999999)
                encoded_prompt = urllib.parse.quote(prompt.strip())
                url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&model={m}&nologo=true&seed={seed}"
                print(f"📡 Requesting FLUX AI image model '{m}' (timeout 75s)...")
                r = requests.get(url, timeout=75)
                if r.status_code == 200 and len(r.content) > 10000:
                    from io import BytesIO
                    img = Image.open(BytesIO(r.content)).convert("RGB")
                    print(f"🎉 FLUX AI Image Model '{m}' returned AI artwork binary successfully! ({img.size})")
                    return img
            except Exception as e:
                print(f"Notice FLUX model {m}: {e}")
        return None

    def _generate_gemini_image(self, prompt):
        """Try generating image via Gemini API endpoints."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={self.gemini_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=25)
            if r.status_code == 200:
                data = r.json()
                if "candidates" in data:
                    parts = data["candidates"][0]["content"]["parts"]
                    for p in parts:
                        if "inlineData" in p or "inline_data" in p:
                            idat = p.get("inlineData") or p.get("inline_data")
                            img_bytes = base64.b64decode(idat["data"])
                            from io import BytesIO
                            return Image.open(BytesIO(img_bytes)).convert("RGB")
        except Exception:
            pass
        return None

    def _overlay_brand_logo_and_header(self, bg_img):
        """Overlay brand logo & editorial header typography onto 1920x1080 canvas."""
        canvas_w, canvas_h = 1920, 1080
        bg_img = bg_img.resize((canvas_w, canvas_h))

        canvas = Image.new("RGB", (canvas_w, canvas_h))
        canvas.paste(bg_img, (0, 0))

        header_h = 110
        header_overlay = Image.new("RGBA", (canvas_w, header_h), (15, 23, 42, 215))
        canvas.paste(header_overlay, (0, 0), header_overlay)

        draw = ImageDraw.Draw(canvas)
        draw.line([(0, header_h - 3), (canvas_w, header_h - 3)], fill=(56, 189, 248), width=3)

        # Paste Brand Logo
        logo_x, logo_y = 30, 15
        if os.path.exists(self.logo_path):
            try:
                logo = Image.open(self.logo_path).convert("RGBA")
                logo.thumbnail((80, 80))
                canvas.paste(logo, (logo_x, logo_y + (80 - logo.height) // 2), logo)
                text_left = 130
            except Exception:
                text_left = 35
        else:
            text_left = 35

        brand_header = (os.getenv("BRAND_HEADER") or "EXECUTIVE INTELLIGENCE  |  GLOBAL & INDIA PULSE").strip()
        date_str = datetime.now().strftime("%B %d, %Y")
        draw.text((text_left, 20), brand_header, fill=(255, 255, 255))
        draw.text((text_left, 60), f"Editorial Data Journalism Infographic (1920x1080 16:9)  •  {date_str}", fill=(56, 189, 248))

        return canvas

    def _create_executive_poster(self):
        """Fallback poster."""
        canvas_w, canvas_h = 1920, 1080
        canvas = Image.new("RGB", (canvas_w, canvas_h), (15, 23, 42))
        draw = ImageDraw.Draw(canvas)

        header_h = 110
        draw.rectangle([0, 0, canvas_w, header_h], fill=(30, 41, 59))
        draw.line([(0, header_h - 3), (canvas_w, header_h - 3)], fill=(56, 189, 248), width=3)

        if os.path.exists(self.logo_path):
            try:
                logo = Image.open(self.logo_path).convert("RGBA")
                logo.thumbnail((80, 80))
                canvas.paste(logo, (30, 15), logo)
            except Exception:
                pass

        brand_header = (os.getenv("BRAND_HEADER") or "EXECUTIVE INTELLIGENCE | GLOBAL & INDIA PULSE").strip()
        draw.text((130, 30), brand_header, fill=(255, 255, 255))
        return canvas


if __name__ == "__main__":
    gen = ImageGenerator()
    out = gen.generate_news_cover_image()
    print("16:9 AI Editorial Infographic Cover created:", out)
