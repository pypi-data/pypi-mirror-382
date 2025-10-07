"""Jenkins integration for DevOps MCPs."""

import logging

# Internal imports
from .utils.jenkins import (
  initialize_jenkins_client,
  set_jenkins_client_for_testing,
  jenkins_get_jobs,
  jenkins_get_build_log,
  jenkins_get_all_views,
  jenkins_get_build_parameters,
  jenkins_get_queue,
  jenkins_get_recent_failed_builds,
  _to_dict,
)

logger = logging.getLogger(__name__)

# Re-export Jenkins utilities for backward compatibility
__all__ = [
  "initialize_jenkins_client",
  "set_jenkins_client_for_testing",
  "jenkins_get_jobs",
  "jenkins_get_build_log",
  "jenkins_get_all_views",
  "jenkins_get_build_parameters",
  "jenkins_get_queue",
  "jenkins_get_recent_failed_builds",
  "_to_dict",
]
