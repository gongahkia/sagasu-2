from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.onprem.container import Docker
from diagrams.onprem.inmemory import Redis
from diagrams.programming.language import Python, TypeScript
from diagrams.onprem.network import Internet, Nginx
from diagrams.onprem.queue import Celery
from diagrams.generic.device import Mobile
from diagrams.custom import Custom

# Local logo paths (update these paths to your actual logo files)
VERCEL_LOGO = "./vercel-logo.png"
HEROKU_LOGO = "./heroku-logo.png"

def unified_architecture():
    with Diagram("Sagasu2 Unified Architecture", show=False, filename="unified_arch", direction="LR"):
        internet = Internet("SMU Intranet")
        
        # Hosting Providers as separate entities
        vercel = Custom("Vercel", VERCEL_LOGO)
        heroku = Custom("Heroku", HEROKU_LOGO)
        
        with Cluster("Telegram Bot Service"):
            mobile_user = Mobile("Telegram User")
            bot = Python("Bot Handler\n(bot.py)")
            telegram_redis = Redis("Credentials Storage")
            bot >> Edge(style="dashed", color="blue", label="Hosted at") >> heroku
            mobile_user >> Edge(label="/start") >> heroku
            bot >> Edge(label="Store/fetch") >> telegram_redis

        with Cluster("React Frontend"):
            web_user = User("Web User")
            react = TypeScript("Next.js App")
            nginx = Nginx("Static Server")
            nginx >> Edge(style="dashed", color="black", label="Served by") >> vercel
            web_user >> Edge(label="HTTP") >> nginx >> react

        with Cluster("Backend Services (AWS EC2)"):
            api = Python("FastAPI\n(main.py)")
            shared_redis = Redis("Shared Session Storage")
            celery = Celery("Celery Workers")
            playwright = Docker("Playwright")

            # Shared components
            api - Edge(style="dashed") - shared_redis
            celery - Edge(style="dashed") - playwright
            playwright >> Edge(label="SMU API", color="firebrick") >> internet

        # Cross-service connections
        bot >> Edge(label="Trigger task") >> celery
        react >> Edge(label="API calls") >> api
        api >> Edge(label="Queue task") >> celery
        celery >> Edge(label="Write results") >> shared_redis
        shared_redis >> Edge(label="Poll status") << [bot, api]
        api >> Edge(label="SSE/WS") >> react
        bot >> Edge(label="Send results") >> mobile_user

if __name__ == "__main__":
    unified_architecture()
