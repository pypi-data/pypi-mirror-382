import logging

from mdps_ds_lib.lib.aws.aws_cred import AwsCred
from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection
from mdps_ds_lib.lib.aws.es_middleware_abstract import ESMiddlewareAbstract

LOGGER = logging.getLogger(__name__)


class OsMiddlewareAws(ESMiddlewareAbstract):

    def __init__(self, index, base_url, port=443, use_ssl=True) -> None:
        super().__init__(index, base_url, port)
        base_url = base_url.replace('https://', '')  # hide https
        self._index = index
        aws_cred = AwsCred()
        service = 'es'
        credentials = aws_cred.get_session().get_credentials()
        # https://opensearch.org/blog/aws-sigv4-support-for-clients/
        # This works
        auth = AWSV4SignerAuth(credentials, aws_cred.region)

        self._engine = OpenSearch(
            hosts=[{'host': base_url, 'port': port}],
            http_auth=auth,
            use_ssl=use_ssl,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
