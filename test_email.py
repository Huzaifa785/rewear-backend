# test_email.py - Simple email test
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_welcome_email():
    """Test welcome email"""
    from app.services.email import email_service
    
    # Create test user
    class TestUser:
        def __init__(self):
            self.email = "immdhuzaifa@gmail.com"
            self.first_name = "Huzaifa"
            self.username = "huzaifa"
    
    test_user = TestUser()
    
    print("📧 Testing welcome email...")
    print(f"Sending to: {test_user.email}")
    
    try:
        success = await email_service.send_welcome_email(test_user)
        
        if success:
            print("✅ Welcome email sent successfully!")
            print("📱 Check your inbox!")
        else:
            print("❌ Email failed to send")
            
    except Exception as e:
        print(f"💥 Error: {e}")

async def test_simple_email():
    """Test simple email"""
    from app.services.email import email_service
    
    print("📧 Testing simple email...")
    
    try:
        success = await email_service.send_email_async(
            to_email="immdhuzaifa@gmail.com",
            subject="🧪 ReWear Test Email",
            html_content="""
            <h1>🎉 Email Test Successful!</h1>
            <p>Your ReWear email configuration is working perfectly!</p>
            <p>Welcome emails will now work! 📧</p>
            <hr>
            <p style="color: #666;">This is a test from ReWear email system</p>
            """
        )
        
        if success:
            print("✅ Simple email sent successfully!")
            print("📱 Check your inbox!")
        else:
            print("❌ Simple email failed")
            
    except Exception as e:
        print(f"💥 Error: {e}")

async def test_registration_flow():
    """Test the full registration flow with email"""
    print("📧 Testing registration flow...")
    
    try:
        from app.core.websockets import notification_service
        
        # Simulate sending welcome notification like in registration
        await notification_service.send_welcome_notification(
            user_id=999,
            user_email="immdhuzaifa@gmail.com",
            user_name="Huzaifa Test"
        )
        
        print("✅ Registration flow email sent!")
        print("📱 Check your inbox for welcome email!")
        
    except Exception as e:
        print(f"💥 Registration flow error: {e}")

async def main():
    """Run all email tests"""
    print("🚀 TESTING REWEAR EMAIL SYSTEM")
    print("=" * 50)
    
    # Test 1: Simple email
    print("\n1️⃣ SIMPLE EMAIL TEST:")
    await test_simple_email()
    
    # Test 2: Welcome email
    print("\n2️⃣ WELCOME EMAIL TEST:")
    await test_welcome_email()
    
    # Test 3: Registration flow
    print("\n3️⃣ REGISTRATION FLOW TEST:")
    await test_registration_flow()
    
    print("\n🎯 RESULTS:")
    print("=" * 50)
    print("If all tests passed, check immdhuzaifa@gmail.com")
    print("You should see 3 emails:")
    print("  📧 Simple test email")
    print("  📧 Welcome email (HTML formatted)")
    print("  📧 Registration flow welcome email")

if __name__ == "__main__":
    asyncio.run(main())