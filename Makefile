all:config

config:
	@echo "Installing configuration..."
	@pip install -r requirements.txt
	@playwright install
	@playwright install chromium

start:
	python3 -m src.bot