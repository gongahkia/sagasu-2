from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.onprem.inmemory import Redis
from diagrams.programming.language import Python, TypeScript
from diagrams.onprem.network import Internet, Nginx
from diagrams.onprem.queue import Celery
from diagrams.generic.device import Mobile
from diagrams.custom import Custom

# Local logo paths (update these paths to your actual logo files)
VERCEL_LOGO = "./vercel-logo.png"
HEROKU_LOGO = "./heroku-logo.png"
PLAYWRIGHT_LOGO = "./playwright-logo.png"  # Place your Playwright PNG here

def unified_architecture():
    with Diagram("Sagasu2 Unified Architecture", show=False, filename="unified_arch", direction="TB"):
        internet = Internet("SMU Intranet")
        
        # Users
        with Cluster("Users"):
            mobile_user = Mobile("Telegram User")
            web_user = User("Web User")

        # Hosting Providers
        vercel = Custom("Vercel", VERCEL_LOGO)
        heroku = Custom("Heroku", HEROKU_LOGO)
            
        # Services
        with Cluster("Telegram Bot Service"):
            bot = Python("Bot Handler\n(bot.py)")
            telegram_redis = Redis("Credentials\nStorage")
            
        with Cluster("React Frontend"):
            react = TypeScript("Next.js App")
            nginx = Nginx("Static Server")
            
        with Cluster("Backend Services (AWS EC2)"):
            api = Python("FastAPI\n(main.py)")
            shared_redis = Redis("Shared Session\nStorage")
            celery = Celery("Celery Workers")
            playwright = Custom("Playwright", PLAYWRIGHT_LOGO)

        # User to Hosting Provider
        mobile_user >> Edge(label="/start command") >> heroku
        web_user >> Edge(label="HTTP Request") >> vercel

        # Hosting Provider to Service
        heroku >> Edge(label="Routes to") >> bot
        vercel >> Edge(label="Serves static\nassets") >> nginx >> react

        # Telegram bot logic
        bot >> Edge(label="Store/fetch") >> telegram_redis
        bot >> Edge(label="Trigger task") >> celery
        celery >> Edge(label="Execute scrape") >> playwright
        playwright >> Edge(label="SMU API calls", color="firebrick") >> internet
        playwright >> Edge(label="Write results") >> shared_redis
        shared_redis >> Edge(label="Poll status") >> bot
        bot >> Edge(label="Send results") >> mobile_user

        # React/Backend logic
        react >> Edge(label="API calls") >> api
        api >> Edge(label="Queue task") >> celery
        shared_redis << Edge(label="Poll status") >> api
        api >> Edge(label="SSE/WebSocket") >> react

if __name__ == "__main__":
    unified_architecture()