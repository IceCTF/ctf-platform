"""
Imports and setup functionality
"""

import api.logger
import api.setup
import api.achievement
import api.user
import api.team
import api.group
import api.annotations
import api.auth
import api.common
import api.cache
import api.problem
import api.stats
import api.utilities
import api.autogen
import api.autogen_tools
import api.problem_feedback

# MUST BE LAST
import api.config

api.setup.index_mongo()
