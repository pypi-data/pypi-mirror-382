#!/usr/bin/env python3
"""
Media sending example for WAHA

This example demonstrates how to send different types of media messages.
"""

import os
from waha import WahaClient
from waha.types import Base64File, URLFile, ContactVcard


def send_media_examples():
    """Example of sending various media types."""
    print("📸 Media Sending Examples")
    print("========================")

    client = WahaClient(
        base_url=os.getenv("WAHA_URL", "http://localhost:3000"),
        api_key=os.getenv("WAHA_API_KEY"),
    )

    target_chat = os.getenv("TEST_CHAT_ID", "1234567890@c.us")
    session = "default"

    try:
        # 1. Send image from URL
        print("📷 Sending image from URL...")
        image_response = client.messages.send_image(
            chat_id=target_chat,
            file="https://picsum.photos/400/300",
            caption="Random image from the internet! 📸",
            session=session,
        )
        print(f"✅ Image sent successfully")

        # 2. Send document/file
        print("📄 Sending document...")
        doc_response = client.messages.send_file(
            chat_id=target_chat,
            file="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            caption="Sample PDF document 📋",
            session=session,
        )
        print(f"✅ Document sent successfully")

        # 3. Send location
        print("📍 Sending location...")
        location_response = client.messages.send_location(
            chat_id=target_chat,
            latitude=40.7128,
            longitude=-74.0060,
            title="New York City",
            session=session,
        )
        print(f"✅ Location sent successfully")

        # 4. Send contact vCard
        print("👤 Sending contact...")
        contact = ContactVcard(
            fullName="John Doe",
            displayName="Johnny",
            phoneNumber="+1234567890",
            email="john.doe@example.com",
            organization="ACME Corp",
        )
        contact_response = client.messages.send_contact_vcard(
            chat_id=target_chat, contacts=[contact], session=session
        )
        print(f"✅ Contact sent successfully")

        # 5. Send poll
        print("📊 Sending poll...")
        poll_response = client.messages.send_poll(
            chat_id=target_chat,
            poll_text="What's your favorite programming language?",
            options=["Python", "JavaScript", "Go", "Rust", "Other"],
            session=session,
        )
        print(f"✅ Poll sent successfully")

        # 6. Send buttons
        print("🔘 Sending buttons...")
        buttons = [
            {"id": "btn1", "title": "Option 1"},
            {"id": "btn2", "title": "Option 2"},
            {"id": "btn3", "title": "Option 3"},
        ]
        buttons_response = client.messages.send_buttons(
            chat_id=target_chat,
            text="Please choose an option:",
            buttons=buttons,
            footer="Made with WAHA",
            session=session,
        )
        print(f"✅ Buttons sent successfully")

        # 7. Example with Base64 encoded image
        print("🖼️  Sending base64 image...")
        # Create a simple 1x1 red pixel PNG in base64
        red_pixel_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

        base64_image = Base64File(
            mimetype="image/png", filename="red_pixel.png", data=red_pixel_base64
        )

        base64_response = client.messages.send_image(
            chat_id=target_chat,
            file=base64_image,
            caption="Tiny red pixel from base64! 🔴",
            session=session,
        )
        print(f"✅ Base64 image sent successfully")

    except Exception as e:
        print(f"❌ Error sending media: {e}")

    finally:
        client.close()


def main():
    """Main function."""
    print("🌟 WAHA Media Examples")
    print("==========================")

    send_media_examples()

    print("\n✨ Media examples completed!")


if __name__ == "__main__":
    main()
