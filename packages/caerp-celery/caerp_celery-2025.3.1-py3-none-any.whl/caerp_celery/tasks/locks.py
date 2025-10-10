from caerp_celery.tasks import utils
from caerp_celery.transactional_task import task_tm
from caerp_celery.locks import release_lock

logger = utils.get_logger(__name__)


@task_tm
def release_lock_after_commit(lockname):
    """Delay the release of a lock after a commited transaction (used for numbering)"""
    logger.debug("Releasing lock {}".format(lockname))
    release_lock(lockname)
