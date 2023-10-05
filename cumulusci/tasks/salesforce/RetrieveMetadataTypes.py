import time

from cumulusci.salesforce_api.metadata import ApiListMetadataTypes
from cumulusci.tasks.salesforce import BaseRetrieveMetadata


class RetrieveMetadataTypes(BaseRetrieveMetadata):
    api_class = ApiListMetadataTypes
    task_options = {
        "api_version": {
            "description": "Override the API version used to list metadatatypes"
        },
    }

    def _init_options(self, kwargs):
        super(RetrieveMetadataTypes, self)._init_options(kwargs)
        if "api_version" not in self.options:
            self.options[
                "api_version"
            ] = self.project_config.project__package__api_version

    def _get_api(self):
        return self.api_class(self, self.options.get("api_version"))

    def _run_task(self):
        api_object = self._get_api()

        while api_object.status == "Pending":
            time.sleep(1)

        self.logger.info("Metadata Types supported by org:\n" + str(api_object()))
