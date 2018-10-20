# IMPORT ORDER MATTERS!

# constants used by MetaCI
FAILED_TO_CREATE_SCRATCH_ORG = "Failed to create scratch org"

from cumulusci.core.config.BaseConfig import BaseConfig

# inherit from BaseConfig

from cumulusci.core.config.MergedConfig import MergedConfig
from cumulusci.core.config.MergedConfig import MergedYamlConfig


class ConnectedAppOAuthConfig(BaseConfig):
    """ Salesforce Connected App OAuth configuration """

    pass


class FlowConfig(BaseConfig):
    """ A flow with its configuration merged """

    pass


from cumulusci.core.config.OrgConfig import OrgConfig


class ServiceConfig(BaseConfig):
    pass


class TaskConfig(BaseConfig):
    """ A task with its configuration merged """

    pass


from cumulusci.core.config.BaseTaskFlowConfig import BaseTaskFlowConfig


# inherit from BaseTaskFlowConfig
from cumulusci.core.config.BaseProjectConfig import BaseProjectConfig

# inherit from OrgConfig
from cumulusci.core.config.ScratchOrgConfig import ScratchOrgConfig

# inherit from BaseProjectConfig
from cumulusci.core.config.YamlProjectConfig import YamlProjectConfig

from cumulusci.core.config.BaseGlobalConfig import BaseGlobalConfig


__all__ = [
    "FAILED_TO_CREATE_SCRATCH_ORG",
    "BaseConfig",
    "MergedConfig",
    "MergedYamlConfig",
    "ConnectedAppOAuthConfig",
    "FlowConfig",
    "OrgConfig",
    "TaskConfig",
    "ServiceConfig",
    "BaseTaskFlowConfig",
    "BaseGlobalConfig",
    "BaseProjectConfig",
    "ScratchOrgConfig",
    "YamlProjectConfig",
]
