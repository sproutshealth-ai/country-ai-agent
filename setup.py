"""
Setup script for Country Information AI Agent
Run this to automatically set up the project
"""
import os
import sys
import subprocess


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def check_python_version():
    """Check if Python version is 3.8 or higher"""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        sys.exit(1)

    print("✅ Python version is compatible")


def install_dependencies():
    """Install Python dependencies"""
    print_header("Installing Dependencies")
    print("Installing packages from requirements.txt...")

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("\n✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("\n❌ Failed to install dependencies")
        print("Try running manually: pip install -r requirements.txt")
        sys.exit(1)


def setup_env_file():
    """Set up .env file"""
    print_header("Setting Up Environment Variables")

    if os.path.exists(".env"):
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("Skipping .env setup")
            return

    print("\nLet's set up your API key...")
    print("Choose your LLM provider:")
    print("1. OpenAI (GPT-4o-mini) - Recommended")
    print("2. Anthropic (Claude)")

    choice = input("\nEnter your choice (1 or 2): ").strip()

    if choice == "1":
        api_key = input("\nEnter your OpenAI API key: ").strip()
        model = "gpt-4o-mini"

        with open(".env", "w") as f:
            f.write(f"# OpenAI Configuration\n")
            f.write(f"OPENAI_API_KEY={api_key}\n")
            f.write(f"MODEL_NAME={model}\n\n")
            f.write("# Server Configuration\n")
            f.write("HOST=0.0.0.0\n")
            f.write("PORT=8000\n")

    elif choice == "2":
        api_key = input("\nEnter your Anthropic API key: ").strip()
        model = "claude-3-5-sonnet-20241022"

        with open(".env", "w") as f:
            f.write(f"# Anthropic Configuration\n")
            f.write(f"ANTHROPIC_API_KEY={api_key}\n")
            f.write(f"MODEL_NAME={model}\n\n")
            f.write("# Server Configuration\n")
            f.write("HOST=0.0.0.0\n")
            f.write("PORT=8000\n")

    else:
        print("❌ Invalid choice")
        sys.exit(1)

    print("\n✅ .env file created successfully")


def run_tests():
    """Ask if user wants to run tests"""
    print_header("Testing Setup")
    response = input("Do you want to run tests now? (y/N): ").lower()

    if response == 'y':
        print("\nRunning tests...")
        try:
            subprocess.check_call([sys.executable, "test_agent.py"])
        except subprocess.CalledProcessError:
            print("\n⚠️  Some tests failed. Please check your API key.")
        except FileNotFoundError:
            print("\n⚠️  test_agent.py not found")


def main():
    """Main setup function"""
    print_header("Country Information AI Agent - Setup")
    print("This script will help you set up the project\n")

    check_python_version()
    install_dependencies()
    setup_env_file()
    run_tests()

    print_header("Setup Complete!")
    print("🎉 Your Country Information AI Agent is ready to use!\n")
    print("Next steps:")
    print("  1. Start the server: python app.py")
    print("  2. Open your browser: http://localhost:8000")
    print("  3. Try asking questions about countries!\n")
    print("For deployment instructions, see DEPLOYMENT.md")
    print("For video recording guide, see VIDEO_GUIDE.md\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {str(e)}")
        sys.exit(1)
