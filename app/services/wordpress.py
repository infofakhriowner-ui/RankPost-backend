# app/services/wordpress.py

import base64, json, re, requests
from io import BytesIO
from PIL import Image
from requests.auth import HTTPBasicAuth


def _compress_to_jpeg(b64: str, quality: int = 70) -> bytes:
    """Decode base64 → compress → return JPEG bytes"""
    raw = base64.b64decode(b64)
    img = Image.open(BytesIO(raw)).convert("RGB")
    buf = BytesIO()
    img.save(buf, "JPEG", optimize=True, quality=quality)
    return buf.getvalue()


def upload_post(
    wp_url: str,
    user: str,
    app_pass: str,
    title: str,
    content_html: str,
    image_b64: str | None = None
) -> str | None:
    """
    Upload a post (and optional featured image) to WordPress using REST API.
    - wp_url → must be JUST the site root URL (e.g. https://example.com)
    - user → WP username
    - app_pass → WP application password
    - title → post title
    - content_html → HTML content
    - image_b64 → optional base64 image for featured image
    """
    featured_media_id = None
    try:
        # ✅ Always start from site root
        base_url = wp_url.rstrip("/") + "/wp-json/wp/v2"

        # 1) Upload featured image if provided
        if image_b64:
            media_url = base_url + "/media"
            image_name = re.sub(r"[^a-zA-Z0-9]+", "-", title.lower())[:30] + ".jpg"
            img_bytes = _compress_to_jpeg(image_b64, quality=72)

            r = requests.post(
                media_url,
                headers={
                    "Content-Disposition": f"attachment; filename={image_name}",
                    "Content-Type": "image/jpeg"
                },
                data=img_bytes,
                auth=HTTPBasicAuth(user, app_pass),
                timeout=90
            )

            if r.status_code >= 400:
                print("[WP Upload] Media upload failed:", r.status_code, r.text)
                r.raise_for_status()

            featured_media_id = r.json().get("id")

        # 2) Create the post
        posts_url = base_url + "/posts"
        post_payload = {
            "title": title,
            "content": content_html,
            "status": "publish"
        }
        if featured_media_id:
            post_payload["featured_media"] = featured_media_id

        pr = requests.post(
            posts_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(post_payload),
            auth=HTTPBasicAuth(user, app_pass),
            timeout=90
        )

        if pr.status_code >= 400:
            print("[WP Upload] Post creation failed:", pr.status_code, pr.text)
            pr.raise_for_status()

        j = pr.json()
        return j.get("link") or j.get("guid", {}).get("rendered")

    except Exception as e:
        print("[WP Upload] error:", e)
        return None
