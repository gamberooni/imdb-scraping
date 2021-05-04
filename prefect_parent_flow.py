from prefect import Flow, Parameter
from prefect.schedules import CronSchedule
from prefect.tasks.prefect import StartFlowRun
import pendulum
import datetime


weekly_monday = CronSchedule(
    "0 22 * * 1", start_date=pendulum.now()
)

scrape_date = Parameter('scrape_date', default=str(datetime.datetime.now().date()) + "/")

flow_a = StartFlowRun(flow_name="create_bucket", project_name="imdb-scraping")
flow_b = StartFlowRun(flow_name="create_schema", project_name="imdb-scraping")
flow_c = StartFlowRun(flow_name="scrape", project_name="imdb-scraping", wait=True)
flow_d = StartFlowRun(flow_name="populate_db", project_name="imdb-scraping", wait=True)

with Flow("parent-flow", schedule=weekly_monday) as flow:
    flow_c(parameters=dict(object_prefix=scrape_date))
    flow_d(parameters=dict(object_prefix=scrape_date))
    flow_c.set_upstream(flow_a)
    flow_c.set_upstream(flow_b)
    flow_d.set_upstream(flow_c)

flow.register("imdb-scraping")

