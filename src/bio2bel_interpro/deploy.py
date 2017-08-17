# -*- coding: utf-8 -*-

import logging

from pybel_tools.resources import get_today_arty_namespace, deploy_namespace, deploy_knowledge
from .run import MODULE_NAME, write_belns
from .tree import write_interpro_tree

log = logging.getLogger(__name__)

KNOWLEDGE_MODULE_NAME = 'interpro-hierarchy'


def deploy_to_arty(quit_fail_redeploy=True):
    """Gets the data, writes BEL namespace, and writes BEL knowledge to Artifactory"""

    file_name = get_today_arty_namespace(MODULE_NAME)

    with open(file_name, 'w') as file:
        write_belns(file)

    namespace_deploy_success = deploy_namespace(file_name, MODULE_NAME)

    if not namespace_deploy_success and quit_fail_redeploy:
        log.warning('did not redeploy')
        return False

    knowledge_file_name = get_today_arty_namespace(KNOWLEDGE_MODULE_NAME)

    with open(knowledge_file_name, 'w') as file:
        write_interpro_tree(file)

    deploy_knowledge(knowledge_file_name, KNOWLEDGE_MODULE_NAME)
