#!/usr/bin/env python3
"""
Basic usage example for WAHA

This example demonstrates the basic functionality of WAHA,
including session management and sending messages.
"""

import asyncio
import os
from waha import WahaClient, AsyncWahaClient


def sync_example():
    """Synchronous example usage."""
    print("🔄 Running synchronous example...")

    # Initialize the client
    client = WahaClient(
        base_url=os.getenv("WAHA_URL", "http://localhost:3000"),
        api_key=os.getenv("WAHA_API_KEY"),
    )

    try:
        # List existing sessions
        sessions = client.sessions.list()
        print(f"📋 Found {len(sessions)} sessions")

        # Start the default session
        session = client.sessions.start("default")
        print(f"🚀 Started session: {session.name} (Status: {session.status})")

        # Get QR code if needed
        if session.status == "SCAN_QR_CODE":
            qr_data = client.auth.get_qr_code("default", format="raw")
            print(f"📱 QR Code: {qr_data.qr}")

        # Get account information (after authentication)
        try:
            me = client.sessions.get_me("default")
            print(f"👤 Authenticated as: {me.id} ({me.pushName})")

            # Send a test message
            target_chat = os.getenv("TEST_CHAT_ID", "1234567890@c.us")
            message = client.messages.send_text(
                chat_id=target_chat, text="Hello from WAHA! 👋", session="default"
            )
            print(f"✅ Message sent: {message.id}")

            # Get recent chats
            chats = client.chats.list("default", limit=5)
            print(f"💬 Found {len(chats)} recent chats")

        except Exception as e:
            print(f"⚠️  Session not authenticated yet: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        client.close()


async def async_example():
    """Asynchronous example usage."""
    print("\n🔄 Running asynchronous example...")

    async with AsyncWahaClient(
        base_url=os.getenv("WAHA_URL", "http://localhost:3000"),
        api_key=os.getenv("WAHA_API_KEY"),
    ) as client:
        try:
            # List existing sessions
            sessions = await client.sessions.list()
            print(f"📋 Found {len(sessions)} sessions")

            # Start the default session
            session = await client.sessions.start("default")
            print(f"🚀 Started session: {session.name} (Status: {session.status})")

            # Get QR code if needed
            if session.status == "SCAN_QR_CODE":
                qr_data = await client.auth.get_qr_code("default", format="raw")
                print(f"📱 QR Code: {qr_data.qr}")

            # Get account information (after authentication)
            try:
                me = await client.sessions.get_me("default")
                print(f"👤 Authenticated as: {me.id} ({me.pushName})")

                # Send a test message
                target_chat = os.getenv("TEST_CHAT_ID", "1234567890@c.us")
                message = await client.messages.send_text(
                    chat_id=target_chat,
                    text="Hello from WAHA (async)! 🚀",
                    session="default",
                )
                print(f"✅ Message sent: {message.id}")

                # Get recent chats
                chats = await client.chats.list("default", limit=5)
                print(f"💬 Found {len(chats)} recent chats")

            except Exception as e:
                print(f"⚠️  Session not authenticated yet: {e}")

        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main function to run examples."""
    print("🌟 WAHA Examples")
    print("====================")

    # Run synchronous example
    sync_example()

    # Run asynchronous example
    asyncio.run(async_example())

    print("\n✨ Examples completed!")


if __name__ == "__main__":
    main()
