# Ventricle

An async REST-server, scheduler and worker all in one. Highly customizable, as it is just wrapping other battle-tested libaries.

```python
from ventricle import Ventricle

app = Ventricle()

@app.worker()
async def hello_world_worker():
    print("I am actually just python threading")

@app.rest.get("/endpoint")
async def rest_endpoint():
    await hello_world_worker()
    return {"how": "I am actually just FastAPI"}

@app.scheduler.scheduled_job("cron", minute=0)
async def hourly_job():
    print("I am actually just APScheduler")

    
# start all of them
app.start(
    rest=True,
    schedular=True,
    worker=True
)
```