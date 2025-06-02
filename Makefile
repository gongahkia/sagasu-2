all:config

config:
	@echo "Installing configuration..."
	@pip install -r requirements.txt
	@playwright install

start:
	python3 -m bot.bot