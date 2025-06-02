all:config

config:
	@echo "Installing configuration..."
	@pip install -r requirements.txt
	@playwright install
	@playwright install chromium

start:
	@echo "Starting bot..."
	@python3 src/bot.py