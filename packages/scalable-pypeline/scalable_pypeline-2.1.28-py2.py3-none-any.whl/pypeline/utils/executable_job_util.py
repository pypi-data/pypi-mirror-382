from dramatiq.broker import get_broker

from pypeline.utils.config_utils import retrieve_executable_job_config
from pypeline.utils.dramatiq_utils import register_lazy_actor, LazyActor
from pypeline.utils.module_utils import get_callable


def execute_job(fn, *args, **kwargs):
    executable_jobs_config = retrieve_executable_job_config()

    module_path = kwargs.get("module_path", None)

    job = None

    for j in executable_jobs_config or []:
        if module_path and module_path == j["config"]["task"]:
            job = j
            break
        elif fn.__name__ in j["config"]["task"]:
            if job:
                raise ValueError(
                    f"Multiple matches found in yaml for {fn.__name__}, "
                    f"Consider passing module_path as a kwarg to avoid ambiguity."
                )
            job = j

    if job is None:
        raise ValueError(f"No match found in yaml for {fn.__name__} function.")

    pipeline_meta = {"queue": job["config"].get("queue", "default")}
    tmp_handler = get_callable(job["config"]["task"])

    actor: LazyActor = register_lazy_actor(get_broker(), tmp_handler, pipeline_meta, None)

    return actor.send(*args, **kwargs)
