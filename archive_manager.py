import os
import sys
import json
from datetime import datetime

# Ensure stdout handles UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class ArchiveManager:
    """Manages the lifecycle of weekly LinkedIn posts.
    Stores Monday through Friday posts in weekly_archive.json.
    Supplies the archive to Saturday's synthesis prompt, then cleanly removes it.
    """
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.archive_path = os.path.join(self.base_dir, "weekly_archive.json")

    def save_post(self, day_name, date_str, topic_name, post_text, verification_status="PASS"):
        """Save or update a weekday post in the weekly archive."""
        archive_data = self._load_raw_archive()
        if "posts" not in archive_data:
            archive_data["posts"] = {}

        archive_data["updated_at"] = datetime.now().isoformat()
        archive_data["posts"][day_name] = {
            "day": day_name,
            "date": date_str,
            "topic": topic_name,
            "content": post_text,
            "verification_status": verification_status,
            "saved_at": datetime.now().isoformat()
        }

        with open(self.archive_path, "w", encoding="utf-8") as f:
            json.dump(archive_data, f, indent=2, ensure_ascii=False)

        print(f"📦 Successfully archived {day_name}'s post into '{os.path.basename(self.archive_path)}'.")

    def get_weekly_archive(self):
        """Retrieve all archived posts for the week as a dictionary keyed by day."""
        archive_data = self._load_raw_archive()
        return archive_data.get("posts", {})

    def has_archive(self):
        """Check if any posts are currently archived."""
        posts = self.get_weekly_archive()
        return len(posts) > 0

    def cleanup_archive(self, include_drafts=True):
        """Delete weekly_archive.json and temporary draft files to keep storage 100% clean."""
        removed_files = []

        # Remove archive JSON
        if os.path.exists(self.archive_path):
            try:
                os.remove(self.archive_path)
                removed_files.append("weekly_archive.json")
            except Exception as e:
                print(f"⚠️ Notice: Could not remove weekly_archive.json: {e}")

        # Remove draft logs and temp media if requested
        if include_drafts:
            draft_files = [
                os.path.join(self.base_dir, "latest_posted_content.txt"),
                os.path.join(self.base_dir, "pollinations_flux_cover.jpg"),
                os.path.join(self.base_dir, "pollinations_flux_verified.jpg"),
                os.path.join(self.base_dir, "real_ai_flux_artwork.jpg"),
                os.path.join(self.base_dir, "test_1920_infographic.jpg"),
                os.path.join(self.base_dir, "unique_cartoon_test.jpg"),
                os.path.join(self.base_dir, "gemini_imagen_cover.jpg"),
                os.path.join(self.base_dir, "assets", "generated_infographic.jpg"),
                os.path.join(self.base_dir, "assets", "generated_cover.jpg"),
                os.path.join(self.base_dir, "assets", "cartoon_collage_cover.jpg")
            ]

            download_dir = os.path.join(self.base_dir, "assets", "downloaded_news_images")
            if os.path.exists(download_dir):
                for f in os.listdir(download_dir):
                    draft_files.append(os.path.join(download_dir, f))

            for f_path in draft_files:
                if os.path.exists(f_path):
                    try:
                        os.remove(f_path)
                        removed_files.append(os.path.basename(f_path))
                    except Exception:
                        pass

        print(f"🧹 Cleaned up {len(removed_files)} files. Storage is 100% clean! (Files removed: {', '.join(removed_files) if removed_files else 'None'})")

    def _load_raw_archive(self):
        if not os.path.exists(self.archive_path):
            return {"created_at": datetime.now().isoformat(), "posts": {}}
        try:
            with open(self.archive_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Warning: Failed to read existing archive file ({e}). Starting fresh.")
            return {"created_at": datetime.now().isoformat(), "posts": {}}


if __name__ == "__main__":
    manager = ArchiveManager()
    print("Archive exists:", manager.has_archive())
    posts = manager.get_weekly_archive()
    print(f"Archived days: {list(posts.keys())}")
