import os
import sys
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv

from post_generator import PostGenerator, WEEKLY_TOPICS
from verifier_agent import NewsVerifierAgent
from linkedin_publisher import LinkedInPublisher
from archive_manager import ArchiveManager

# Ensure UTF-8 stdout encoding on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

def cleanup_draft_files(base_dir=None):
    """Clean up temporary draft files and leftover test media."""
    if not base_dir:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    temp_files = [
        os.path.join(base_dir, "latest_posted_content.txt"),
        os.path.join(base_dir, "pollinations_flux_cover.jpg"),
        os.path.join(base_dir, "pollinations_flux_verified.jpg"),
        os.path.join(base_dir, "real_ai_flux_artwork.jpg"),
        os.path.join(base_dir, "test_1920_infographic.jpg"),
        os.path.join(base_dir, "unique_cartoon_test.jpg"),
        os.path.join(base_dir, "gemini_imagen_cover.jpg"),
        os.path.join(base_dir, "assets", "generated_infographic.jpg"),
        os.path.join(base_dir, "assets", "generated_cover.jpg"),
        os.path.join(base_dir, "assets", "cartoon_collage_cover.jpg")
    ]

    download_dir = os.path.join(base_dir, "assets", "downloaded_news_images")
    if os.path.exists(download_dir):
        for f in os.listdir(download_dir):
            temp_files.append(os.path.join(download_dir, f))

    cleaned_count = 0
    for file_path in temp_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                cleaned_count += 1
            except Exception:
                pass

    if cleaned_count > 0:
        print(f"🧹 Cleaned up {cleaned_count} temporary files. Storage remains clean!")

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Automation - 6-Day Single-Topic Deep Dive Suite")
    parser.add_argument("--verify-only", action="store_true", help="Generate post, run Fact-Checker, and preview without publishing")
    parser.add_argument("--auto-post", action="store_true", help="Publish directly to LinkedIn without interactive prompt")
    parser.add_argument("--day", type=str, choices=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                        help="Override current day of the week for testing or manual execution")
    parser.add_argument("--keep-files", action="store_true", help="Do not delete temporary draft files after posting")
    args = parser.parse_args()

    # Determine current day
    current_day = args.day or datetime.now().strftime("%A")
    date_str = datetime.now().strftime("%B %d, %Y")

    print(f"🚀 LinkedIn Deep Dive Suite initialized for {current_day}, {date_str}")

    # Sunday check: Rest day
    if current_day == "Sunday":
        print("☕ Sunday is designated as Rest Day. No post scheduled. Exiting cleanly.")
        return

    topic_info = WEEKLY_TOPICS.get(current_day)
    print(f"📌 Scheduled Theme: {topic_info['emoji']} {topic_info['title']}")

    archive_mgr = ArchiveManager()
    post_gen = PostGenerator()

    # Step 1: Generate Post Text
    print(f"\n📝 Generating executive content for {current_day}...")
    if current_day == "Saturday":
        archived_posts = archive_mgr.get_weekly_archive()
        print(f"📊 Retrieved {len(archived_posts)} weekday post(s) from weekly archive for synthesis.")
        post_text = post_gen.generate_saturday_synthesis(archived_posts=archived_posts, max_chars=2600)
    else:
        post_text = post_gen.generate_weekday_post(day_name=current_day, max_chars=2600)

    char_count = len(post_text)
    print(f"📏 Content generated: {char_count} characters (Target limit: 2600)")

    print("⏳ Pausing 5s for API buffer...")
    time.sleep(5)

    # Step 2: Fact-Checking Verification Agent
    print(f"\n🔍 Running Senior Fact-Checking Verification Agent on {topic_info['title']}...")
    verifier = NewsVerifierAgent()
    verification_res = verifier.verify_news_content(
        headline=f"{topic_info['title']} ({current_day})",
        article_text=post_text
    )
    status = verification_res.get("status", "PASS")
    report = verification_res.get("report", "")

    print("\n=================== SENIOR FACT-CHECKING REPORT ===================")
    print(report)
    print(f"VERIFICATION STATUS: {status}")
    print("===================================================================\n")

    print("\n=================== LINKEDIN TEXT-ONLY POST PREVIEW ===================")
    print(post_text)
    print("=======================================================================\n")

    # Save draft copy for local preview
    log_file = "latest_posted_content.txt"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"Day: {current_day}\n")
        f.write(f"Date: {date_str}\n")
        f.write(f"Theme: {topic_info['title']}\n")
        f.write(f"Verification Status: {status}\n")
        f.write(f"Character Count: {char_count} / 2600\n\n")
        f.write(f"VERIFICATION REPORT:\n{report}\n\n")
        f.write("POST CONTENT:\n")
        f.write(post_text)

    if args.verify_only:
        print("🔍 PREVIEW & VERIFICATION COMPLETE.")
        print(f"Text-only draft saved to '{log_file}'. Stopping before publishing.")
        return

    # Autonomous self-healing retry loop if fact-checker rejects draft
    if status == "REJECT" or "DO_NOT_PUBLISH" in report:
        print(f"\n🔄 Self-Healing Safety Net: Fact-Checking Agent flagged issues ({status}). Initiating automated correction loop...")
        post_text = post_gen.fix_post_with_corrections(
            post_text=post_text,
            verifier_report=report,
            day_name=current_day,
            max_chars=2600
        )
        char_count = len(post_text)
        print(f"📏 Corrected content generated: {char_count} characters. Re-verifying...")
        time.sleep(5)
        verification_res = verifier.verify_news_content(
            headline=f"{topic_info['title']} ({current_day} - Corrected)",
            article_text=post_text
        )
        status = verification_res.get("status", "PASS")
        report = verification_res.get("report", "")

        print("\n=================== RE-VERIFICATION REPORT ===================")
        print(report)
        print(f"RE-VERIFICATION STATUS: {status}")
        print("==============================================================\n")

        # Update log with corrected version
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"Day: {current_day}\nDate: {date_str}\nTheme: {topic_info['title']}\n")
            f.write(f"Verification Status: {status}\nCharacter Count: {char_count} / 2600\n\n")
            f.write(f"RE-VERIFICATION REPORT:\n{report}\n\nPOST CONTENT:\n{post_text}")

        if status == "REJECT" or "DO_NOT_PUBLISH" in report:
            print(f"⛔ CRITICAL: Fact-Checking Agent still recommended '{status}'. Aborting publishing.")
            return

    # Interactive confirmation if not automated
    if not args.auto_post:
        print("⚠️ PRE-PUBLISH CONFIRMATION:")
        confirm = input(f"Publish this verified {current_day} LinkedIn post now? (y/n) [y]: ").strip().lower()
        if confirm and confirm not in ['y', 'yes']:
            print("Publishing cancelled by user.")
            return

    # Step 3: Authenticate & Publish to LinkedIn
    print("\n🔐 Authenticating with LinkedIn API...")
    publisher = LinkedInPublisher()
    user_urn, user_profile = publisher.get_user_info()
    user_name = user_profile.get("name") or user_profile.get("localizedFirstName") or "User"
    print(f"Authenticated as: {user_name} ({user_urn})")

    print(f"\n📡 Publishing {current_day} text-only verified post to LinkedIn...")
    result = publisher.publish_feed_post(
        author_urn=user_urn,
        text_content=post_text,
        asset_urn=None
    )

    post_id = result.get("id")
    print(f"\n🎉 {current_day.upper()} POST PUBLISHED SUCCESSFULLY!")
    print(f"Post ID: {post_id}")
    print(f"View post on your LinkedIn feed: https://www.linkedin.com/feed/")

    # Step 4: Storage & Archive Lifecycle Management
    if current_day == "Saturday":
        # Saturday: Complete weekly lifecycle, clean up weekly_archive.json and temp drafts
        print("\n🧹 Saturday publish complete: Executing weekly archive cleanup...")
        archive_mgr.cleanup_archive(include_drafts=(not args.keep_files))
    else:
        # Monday to Friday: Archive post locally for Saturday synthesis
        archive_mgr.save_post(
            day_name=current_day,
            date_str=date_str,
            topic_name=topic_info['title'],
            post_text=post_text,
            verification_status=status
        )
        if not args.keep_files:
            cleanup_draft_files()

    print("\n✅ Daily deep dive workflow complete!")

if __name__ == "__main__":
    main()
