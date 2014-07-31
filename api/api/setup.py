"""
Setup for the API
"""

import api

log = api.logger.use(__name__)

def index_mongo():
    """
    Ensure the mongo collections are indexed.
    """

    db = api.common.get_conn()

    log.debug("Ensuring mongo is indexed.")

    db.users.ensure_index("uid", unique=True, name="unique uid")
    db.groups.ensure_index("gid", unique=True, name="unique gid")
    db.problems.ensure_index("pid", unique=True, name="unique pid")
    db.submissions.ensure_index("tid", name="submission tids")
    db.cache.ensure_index("expireAt", expireAfterSeconds=0)
    db.cache.ensure_index("kwargs", name="kwargs")
    db.cache.ensure_index("args", name="args")
