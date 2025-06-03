from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.onprem.container import Docker
from diagrams.onprem.inmemory import Redis
from diagrams.programming.language import Python, TypeScript
from diagrams.onprem.network import Internet, Nginx
from diagrams.onprem.queue import Celery
from diagrams.generic.device import Mobile

def unified_architecture():
    with Diagram("Sagasu2 Unified Architecture", show=False, filename="unified_arch", direction="LR"):
        internet = Internet("SMU Intranet")
        
        with Cluster("Telegram Bot Service (Heroku)"):
            mobile_user = Mobile("Telegram User")
            bot = Python("Bot Handler")
            telegram_redis = Redis("Credentials Storage")
            bot >> Edge(label="/start") << mobile_user
            bot >> Edge(label="Store/fetch") >> telegram_redis

        with Cluster("React Frontend (Vercel)"):
            web_user = User("Web User")
            react = TypeScript("Next.js App")
            nginx = Nginx("Static Server")
            web_user >> Edge(label="HTTP") >> nginx >> react

        with Cluster("Backend Services (AWS EC2)"):
            api = Python("FastAPI")
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