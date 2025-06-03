from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.onprem.container import Docker
from diagrams.onprem.inmemory import Redis
from diagrams.programming.language import Python, TypeScript
from diagrams.onprem.network import Internet, Nginx
from diagrams.onprem.queue import Celery
from diagrams.generic.device import Mobile

def telegram_architecture():
    with Diagram("Sagasu2 Telegram Bot Architecture", show=False, filename="telegram_arch", direction="TB"):
        user = Mobile("Telegram User")
        
        with Cluster("Telegram Bot Service (Hosted on Heroku)"):
            bot = Python("Bot Handler\n(bot.py)")
            handlers = Python("Command Handlers\n(start, settings, scrape)")
            redis = Redis("Redis\nCredentials Storage")
            celery = Celery("Task Queue\n(scraper_service)")
            playwright = Docker("Playwright\nBrowser Instance")

        # Flows
        user >> Edge(label="/start") >> bot
        bot >> Edge(label="Store credentials") >> redis
        bot >> Edge(label="Trigger scrape_task.delay()") >> celery
        celery >> Edge(label="Execute scrape_smu_fbs()") >> playwright
        playwright >> Edge(label="SMU FBS API calls", color="firebrick") >> Internet("SMU Intranet")
        playwright >> Edge(label="Write results") >> redis
        redis >> Edge(label="Poll task status") >> bot
        bot >> Edge(label="Send formatted results") >> user

def react_architecture():
    with Diagram("Sagasu2 React Frontend Architecture", show=False, filename="react_arch", direction="LR"):
        user = User("Web User")
        
        with Cluster("Frontend Service (React Frontend Hosted on Vercel)"):
            react = TypeScript("React App\n(Next.js)")
            nginx = Nginx("Static Server")
        
        with Cluster("Backend Service (Hosted on AWS EC2)"):
            api = Python("FastAPI\n(main.py)")
            redis = Redis("Shared Redis\n(Session Storage)")
            celery = Celery("Celery Worker\n(scraper_service)")
            playwright = Docker("Playwright\nBrowser Instance")

        with Cluster("Browser"):
            browser = Docker("User Browser")
            websocket = Docker("WebSocket\nConnection")

        # Flows
        user >> Edge(label="HTTP Requests") >> nginx
        nginx >> Edge(label="Static Assets") << react
        react >> Edge(label="API Calls\n(Axios)") >> api
        api >> Edge(label="JWT Auth") >> redis
        api >> Edge(label="Trigger scrape_task.delay()") >> celery
        celery >> Edge(label="Execute scrape_smu_fbs()") >> playwright
        playwright >> Edge(label="SMU FBS API calls", color="firebrick") >> Internet("SMU Intranet")
        playwright >> Edge(label="Write results") >> redis
        redis >> Edge(label="Poll /tasks/{id}") << api
        api >> Edge(label="SSE Updates") >> websocket >> react

if __name__ == "__main__":
    telegram_architecture()
    react_architecture()
