#!/usr/bin/env python3
"""
Complete Telegram Bot Setup and Run Script
This script will set up and run your Telegram bot completely
"""

import os
import sys
import subprocess
import time
import secrets

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_step(step, description):
    """Print a step with description"""
    print(f"\n{step}️⃣  {description}")
    print("-" * 40)

def generate_webhook_secret():
    """Generate a secure webhook secret"""
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(32))

def update_env_file(bot_token, webhook_secret, ngrok_url):
    """Update the .env file with all necessary values"""
    print_step("📝", "Updating .env file...")
    
    # Read current .env file
    with open('.env', 'r') as f:
        content = f.read()
    
    # Update values
    content = content.replace('YOUR_BOT_TOKEN_HERE', bot_token)
    content = content.replace('YOUR_GENERATED_SECRET_HERE', webhook_secret)
    content = content.replace('YOUR_WEBHOOK_URL_HERE', ngrok_url)
    
    # Write back
    with open('.env', 'w') as f:
        f.write(content)
    
    print(f"✅ Bot token updated")
    print(f"✅ Webhook secret: {webhook_secret}")
    print(f"✅ Webhook URL: {ngrok_url}")

def install_dependencies():
    """Install all required dependencies"""
    print_step("📦", "Installing dependencies...")
    
    try:
        print("Installing main requirements...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Main requirements installed")
        
        print("Installing backend app requirements...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'backend_app/requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Backend app requirements installed")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def test_configuration():
    """Test the configuration"""
    print_step("🧪", "Testing configuration...")
    
    try:
        result = subprocess.run([sys.executable, 'test_telegram_bot_quick.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Configuration test passed")
            print(result.stdout)
            return True
        else:
            print("❌ Configuration test failed")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

def start_application():
    """Start the FastAPI application"""
    print_step("🚀", "Starting FastAPI application...")
    
    print("Run this command in your terminal:")
    print("uvicorn backend_app.main:app --reload")
    print("\nOr use this script to start it:")
    print("python -c \"import uvicorn; uvicorn.run('backend_app.main:app', reload=True)\"")

def set_webhook(bot_token, webhook_url, webhook_secret):
    """Set the Telegram webhook"""
    print_step("🔗", "Setting Telegram webhook...")
    
    import requests
    
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    payload = {
        "url": webhook_url,
        "secret_token": webhook_secret
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        if data.get('ok'):
            print("✅ Webhook set successfully!")
            print(f"Webhook URL: {webhook_url}")
        else:
            print(f"❌ Failed to set webhook: {data.get('description')}")
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")

def main():
    """Main setup and run function"""
    print_header("TELEGRAM BOT COMPLETE SETUP")
    
    # Get bot token from user
    print_step("🔑", "Getting bot token...")
    bot_token = input("Please enter your Telegram bot token: ").strip()
    
    if not bot_token:
        print("❌ Bot token cannot be empty!")
        return
    
    # Generate webhook secret
    webhook_secret = generate_webhook_secret()
    print(f"✅ Generated webhook secret: {webhook_secret}")
    
    # Use the ngrok URL from the user's terminal
    ngrok_url = "https://00d7585dd459.ngrok-free.app/api/v1/telegram/webhooks/telegram"
    print(f"✅ Using ngrok URL: {ngrok_url}")
    
    # Update .env file
    update_env_file(bot_token, webhook_secret, ngrok_url)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        return
    
    # Test configuration
    if not test_configuration():
        print("❌ Setup failed during configuration test")
        return
    
    # Set webhook
    set_webhook(bot_token, ngrok_url, webhook_secret)
    
    # Start application
    start_application()
    
    print_header("🎉 SETUP COMPLETE!")
    
    print("\n📋 Final Steps:")
    print("1. Start your FastAPI application:")
    print("   uvicorn backend_app.main:app --reload")
    print("\n2. Keep ngrok running (it should already be running)")
    print("\n3. Test your bot on Telegram:")
    print("   - Send /high")
    print("   - Send /start") 
    print("   - Send /help")
    print("   - Send 'I'm looking for a job'")
    
    print("\n📖 Expected responses:")
    print("• /high → 'Hey there! 🌟 I'm here and ready to help!'")
    print("• /start → Welcome message with bot capabilities")
    print("• /help → List of available commands")
    print("• Job query → Job search assistance")
    
    print(f"\n🔧 Configuration Summary:")
    print(f"   Bot Token: {bot_token[:10]}...")
    print(f"   Webhook Secret: {webhook_secret}")
    print(f"   Webhook URL: {ngrok_url}")
    
    print(f"\n🌐 Health Check URL:")
    print(f"   {ngrok_url.replace('/webhooks/telegram', '/health')}")
    
    print(f"\n🤖 Test your bot now on Telegram!")

if __name__ == "__main__":
    main()