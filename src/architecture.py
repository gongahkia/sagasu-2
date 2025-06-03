from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.onprem.inmemory import Redis
from diagrams.programming.language import Python, TypeScript
from diagrams.onprem.network import Internet, Nginx
from diagrams.onprem.queue import Celery
from diagrams.generic.device import Mobile
from diagrams.custom import Custom

VERCEL_LOGO = "./vercel-logo.png"
HEROKU_LOGO = "./heroku-logo.png"
PLAYWRIGHT_LOGO = "./playwright-logo.png"

def unified_architecture():
    with Diagram("Sagasu2 Architecture", show=False, filename="unified_arch", direction="TB"):
        internet = Internet("SMU Intranet")
        with Cluster("Users"):
            mobile_user = Mobile("Telegram User")
            web_user = User("Web User")
        with Cluster("Hosting Providers"):
            vercel = Custom("Vercel", VERCEL_LOGO)
            heroku = Custom("Heroku", HEROKU_LOGO)
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
        mobile_user >> Edge(label="/start command") >> heroku
        web_user >> Edge(label="HTTP Request") >> vercel
        heroku >> Edge(label="Routes to") >> bot
        vercel >> Edge(label="Serves static\nassets") >> nginx
        nginx >> Edge(label="Loads") >> react
        bot >> Edge(label="Store/fetch") >> telegram_redis
        bot >> Edge(label="Trigger task") >> celery
        celery >> Edge(label="Execute scrape") >> playwright
        playwright >> Edge(label="SMU API calls", color="firebrick") >> internet
        playwright >> Edge(label="Write results") >> shared_redis
        shared_redis >> Edge(label="Poll status") >> bot
        bot >> Edge(label="Send results") >> mobile_user
        react >> Edge(label="API calls") >> api
        api >> Edge(label="Queue task") >> celery
        shared_redis >> Edge(label="Poll status") >> api
        api >> Edge(label="SSE/WebSocket") >> react

if __name__ == "__main__":
    unified_architecture()