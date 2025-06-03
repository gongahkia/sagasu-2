from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.onprem.inmemory import Redis
from diagrams.programming.language import Python, TypeScript
from diagrams.onprem.network import Internet, Nginx
from diagrams.onprem.queue import Celery
from diagrams.generic.device import Mobile
from diagrams.custom import Custom
from diagrams.generic.blank import Blank

VERCEL_LOGO = "./vercel-logo.png"
HEROKU_LOGO = "./heroku-logo.png"
PLAYWRIGHT_LOGO = "./playwright-logo.png"
AWS_EC2_LOGO = "./aws-ec2-logo.png"

def unified_architecture():
    with Diagram("Sagasu 2 Architecture", show=False, filename="unified_arch", direction="TB"):
        internet = Internet("SMU Intranet")
        with Cluster("Users"):
            mobile_user = Mobile("Telegram User")
            web_user = User("Web User")
        with Cluster("Hosting Providers"):
            heroku = Custom("Heroku", HEROKU_LOGO)
            vercel = Custom("Vercel", VERCEL_LOGO)
            aws_ec2 = Custom("AWS EC2", AWS_EC2_LOGO)
        with Cluster("Telegram Bot Service", direction="TB"):
            bot = Python("Bot Handler\n(bot.py)")
            telegram_redis = Redis("Credentials\nStorage")
        with Cluster("React Frontend", direction="TB"):
            nginx = Nginx("Static Server")
            react = TypeScript("Next.js App")
        with Cluster("Backend Services", direction="TB"):
            api = Python("FastAPI\n(main.py)")
            celery = Celery("Celery Workers")
            playwright = Custom("Playwright", PLAYWRIGHT_LOGO)
            shared_redis = Redis("Shared Session\nStorage")

        # User to Hosting Providers
        mobile_user >> Edge(label="/start command") >> heroku
        web_user >> Edge(label="HTTP Request") >> vercel

        # Hosting Providers to Services
        heroku >> Edge(label="Routes to") >> bot
        vercel >> Edge(label="Serves static assets") >> nginx
        aws_ec2 >> Edge(label="Hosts") >> api
        aws_ec2 >> Edge(label="Hosts") >> celery
        aws_ec2 >> Edge(label="Hosts") >> playwright
        aws_ec2 >> Edge(label="Hosts") >> shared_redis

        # React frontend flow
        nginx >> Edge(label="Loads") >> react
        react >> Edge(label="API calls") >> api
        api >> Edge(label="SSE/WebSocket") >> react

        # Telegram bot flow
        bot >> Edge(label="Store/fetch") >> telegram_redis
        bot >> Edge(label="Trigger task") >> celery
        celery >> Edge(label="Execute scrape") >> playwright
        playwright >> Edge(label="SMU API calls", color="firebrick") >> internet
        playwright >> Edge(label="Write results") >> shared_redis
        shared_redis >> Edge(label="Poll status") >> bot
        bot >> Edge(label="Send results") >> mobile_user

        # Backend API task queue and polling
        api >> Edge(label="Queue task") >> celery
        shared_redis >> Edge(label="Poll status") >> api

if __name__ == "__main__":
    unified_architecture()
