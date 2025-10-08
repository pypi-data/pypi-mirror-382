import base64
import json
import logging
from copy import deepcopy

from mdps_ds_lib.lib.utils.json_validator import JsonValidator

API_GATEWAY_EVENT_SCHEMA = {
    'type': 'object',
    'required': [
        'requestContext',
        'headers',
        'httpMethod',
    ],
    'properties': {
        'requestContext': {
            'type': 'object',
            'required': [
                'path',
            ],
            'properties': {
                'path': {
                    'type': 'string'
                }
            }
        },
        'headers': {
            'type': 'object',
            'required': [
                'Host',
                'Authorization',
            ],
            'properties': {
                'Host': {
                    'type': 'string'
                },
                'Authorization': {
                    'type': 'string'
                }
            }
        },
        'httpMethod': {'type': 'string'},
    }
}
LOGGER = logging.getLogger(__name__)


SAMPLE = {
    "resource": "/am-uds-dapa/collections/{collectionId}",
    "path": "/am-uds-dapa/collections/CUMULUS_DAPA_UNIT_TEST___1665800977",
    "httpMethod": "GET",
    "headers": {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Authorization": "Bearer eyJraWQiOiJzdE42WWl0eGxWZmJnY1ByRnJLWVQ1MEdjVWRIZWNBaWFKQ09peUxLVHNZPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIwMGRkYTdmNy1mNjE4LTRmNDMtYWFmNC1iYmM4YmExNDc2ODAiLCJjb2duaXRvOmdyb3VwcyI6WyJVbml0eV9WaWV3ZXIiLCJUZXN0X0dyb3VwIiwiVW5pdHlfQWRtaW4iXSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLXdlc3QtMi5hbWF6b25hd3MuY29tXC91cy13ZXN0LTJfRkxEeVhFMm1PIiwiY2xpZW50X2lkIjoiN2ExZmdsbTJkNTRlb2dnajEzbGNjaXZwMjUiLCJvcmlnaW5fanRpIjoiNzc3YmZkNDEtZTY1OS00M2Y0LThmYzEtNGFkOTEwNDE1NDdiIiwiZXZlbnRfaWQiOiI5YjM3OGE3ZS03OWQxLTQyMmYtODEwZi1lM2Q2Mjk2ODNiZDEiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNjY1Nzc1Nzc3LCJleHAiOjE2NjU3NzkzNzcsImlhdCI6MTY2NTc3NTc3NywianRpIjoiMDk5OTA3YTMtMWVhNS00MmRiLTg4ZmMtNGU5MjQzM2FhOTA0IiwidXNlcm5hbWUiOiJ3cGh5byJ9.CiFHUKqz3q3TwW6XOPH2lkglfWO1LRk-ly-mB280GoFyGBhzSjnWHbo_U-NFmI7VsilywLMXFkif2IQ7AJSt9Cj2pja5ohrmDOFfQR_EuSSo-skSYElVaMYmIkRfVWfVa6gyByOGho5utANI0a6y9nnazvdp3ebXpdVUrNHC3yLns9-CijW-2jEvNDvEoaUZxQp06H29mcb4Iupc_SFYaVzNt3Xf_eumbyV2c0tdBEy-aRsNSOwhLXEREVJyGjHMsaSi8q2FUpHigj9ORfGtntjqESiCLCDc7wAhx6eqEZ8bfC87ck33UiFhYsamaNFHXbYTLl-uN8W5yyi8TAvJDA",
        "Host": "k3a3qmarxh.execute-api.us-west-2.amazonaws.com",
        "User-Agent": "python-requests/2.27.1",
        "X-Amzn-Trace-Id": "Root=1-6349b8e1-26c2c9e702a5cd546ba96c81",
        "X-Forwarded-For": "137.79.228.173",
        "X-Forwarded-Port": "443",
        "X-Forwarded-Proto": "https"
    },
    "multiValueHeaders": {
        "Accept": [
            "*/*"
        ],
        "Accept-Encoding": [
            "gzip, deflate"
        ],
        "Authorization": [
            "Bearer eyJraWQiOiJzdE42WWl0eGxWZmJnY1ByRnJLWVQ1MEdjVWRIZWNBaWFKQ09peUxLVHNZPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIwMGRkYTdmNy1mNjE4LTRmNDMtYWFmNC1iYmM4YmExNDc2ODAiLCJjb2duaXRvOmdyb3VwcyI6WyJVbml0eV9WaWV3ZXIiLCJUZXN0X0dyb3VwIiwiVW5pdHlfQWRtaW4iXSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLXdlc3QtMi5hbWF6b25hd3MuY29tXC91cy13ZXN0LTJfRkxEeVhFMm1PIiwiY2xpZW50X2lkIjoiN2ExZmdsbTJkNTRlb2dnajEzbGNjaXZwMjUiLCJvcmlnaW5fanRpIjoiNzc3YmZkNDEtZTY1OS00M2Y0LThmYzEtNGFkOTEwNDE1NDdiIiwiZXZlbnRfaWQiOiI5YjM3OGE3ZS03OWQxLTQyMmYtODEwZi1lM2Q2Mjk2ODNiZDEiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6ImF3cy5jb2duaXRvLnNpZ25pbi51c2VyLmFkbWluIiwiYXV0aF90aW1lIjoxNjY1Nzc1Nzc3LCJleHAiOjE2NjU3NzkzNzcsImlhdCI6MTY2NTc3NTc3NywianRpIjoiMDk5OTA3YTMtMWVhNS00MmRiLTg4ZmMtNGU5MjQzM2FhOTA0IiwidXNlcm5hbWUiOiJ3cGh5byJ9.CiFHUKqz3q3TwW6XOPH2lkglfWO1LRk-ly-mB280GoFyGBhzSjnWHbo_U-NFmI7VsilywLMXFkif2IQ7AJSt9Cj2pja5ohrmDOFfQR_EuSSo-skSYElVaMYmIkRfVWfVa6gyByOGho5utANI0a6y9nnazvdp3ebXpdVUrNHC3yLns9-CijW-2jEvNDvEoaUZxQp06H29mcb4Iupc_SFYaVzNt3Xf_eumbyV2c0tdBEy-aRsNSOwhLXEREVJyGjHMsaSi8q2FUpHigj9ORfGtntjqESiCLCDc7wAhx6eqEZ8bfC87ck33UiFhYsamaNFHXbYTLl-uN8W5yyi8TAvJDA"
        ],
        "Host": [
            "k3a3qmarxh.execute-api.us-west-2.amazonaws.com"
        ],
        "User-Agent": [
            "python-requests/2.27.1"
        ],
        "X-Amzn-Trace-Id": [
            "Root=1-6349b8e1-26c2c9e702a5cd546ba96c81"
        ],
        "X-Forwarded-For": [
            "137.79.228.173"
        ],
        "X-Forwarded-Port": [
            "443"
        ],
        "X-Forwarded-Proto": [
            "https"
        ]
    },
    "queryStringParameters": None,
    "multiValueQueryStringParameters": None,
    "pathParameters": {
        "collectionId": "CUMULUS_DAPA_UNIT_TEST___1665800977"
    },
    "stageVariables": {
        "VPCLINK": "czcxgk"
    },
    "requestContext": {
        "resourceId": "cv4985",
        "authorizer": {
            "numberKey": "123",
            "booleanKey": "true",
            "stringKey": "stringval",
            "principalId": "user",
            "integrationLatency": 303
        },
        "resourcePath": "/am-uds-dapa/collections/{collectionId}",
        "httpMethod": "GET",
        "extendedRequestId": "aAnTUHrSPHcFcGg=",
        "requestTime": "14/Oct/2022:19:30:41 +0000",
        "path": "/dev/am-uds-dapa/collections/CUMULUS_DAPA_UNIT_TEST___1665800977",
        "accountId": "884500545225",
        "protocol": "HTTP/1.1",
        "stage": "dev",
        "domainPrefix": "k3a3qmarxh",
        "requestTimeEpoch": 1665775841896,
        "requestId": "67b76cda-e49d-449e-ad3d-8ba6d42a4ce4",
        "identity": {
            "cognitoIdentityPoolId": None,
            "accountId": None,
            "cognitoIdentityId": None,
            "caller": None,
            "sourceIp": "137.79.228.173",
            "principalOrgId": None,
            "accessKey": None,
            "cognitoAuthenticationType": None,
            "cognitoAuthenticationProvider": None,
            "userArn": None,
            "userAgent": "python-requests/2.27.1",
            "user": None
        },
        "domainName": "k3a3qmarxh.execute-api.us-west-2.amazonaws.com",
        "apiId": "k3a3qmarxh"
    },
    "body": None,
    "isBase64Encoded": False
}

class LambdaApiGatewayUtils:
    def __init__(self, event: dict, default_limit: int = 10):
        self.__event = event
        self.__default_limit = default_limit
        api_gateway_event_validator_result = JsonValidator(API_GATEWAY_EVENT_SCHEMA).validate(event)
        if api_gateway_event_validator_result is not None:
            raise ValueError(f'invalid event: {api_gateway_event_validator_result}. event: {event}')

    def get_authorization_info(self):
        """
        :return:
        """
        action = self.__event['httpMethod']
        resource = self.__event['requestContext']['path']
        bearer_token = self.__event['headers']['Authorization']
        username_part = bearer_token.split('.')[1]
        jwt_decoded = base64.standard_b64decode(f'{username_part}========'.encode()).decode()
        jwt_decoded = json.loads(jwt_decoded)
        ldap_groups = jwt_decoded['cognito:groups']
        username = jwt_decoded['username']
        return {
            'username': username,
            'ldap_groups': list(set(ldap_groups)),
            'action': action,
            'resource': resource,
        }

    def __get_current_page(self):
        try:
            requesting_base_url = f"https://{self.__event['headers']['Host']}{self.__event['requestContext']['path']}"
            new_queries = deepcopy(self.__event['queryStringParameters']) if 'queryStringParameters' in self.__event and self.__event[
                'queryStringParameters'] is not None else {}
            limit = int(new_queries['limit'] if 'limit' in new_queries else self.__default_limit)
            offset = int(new_queries['offset'] if 'offset' in new_queries else 0)
            new_queries['limit'] = limit
            new_queries['offset'] = offset
            requesting_url = f"{requesting_base_url}?{'&'.join([f'{k}={v}' for k, v in new_queries.items()])}"
        except Exception as e:
            LOGGER.exception(f'error while getting current page URL')
            return f'unable to get current page URL, {str(e)}'
        return requesting_url

    def __get_next_page(self):
        try:
            requesting_base_url = f"https://{self.__event['headers']['Host']}{self.__event['requestContext']['path']}"
            new_queries = deepcopy(self.__event['queryStringParameters']) if 'queryStringParameters' in self.__event and self.__event[
                'queryStringParameters'] is not None else {}
            limit = int(new_queries['limit'] if 'limit' in new_queries else self.__default_limit)
            if limit == 0:
                return ''
            offset = int(new_queries['offset'] if 'offset' in new_queries else 0)
            offset += limit
            new_queries['limit'] = limit
            new_queries['offset'] = offset
            requesting_url = f"{requesting_base_url}?{'&'.join([f'{k}={v}' for k, v in new_queries.items()])}"
        except Exception as e:
            LOGGER.exception(f'error while getting next page URL')
            return f'unable to get next page URL, {str(e)}'
        return requesting_url

    def __get_prev_page(self):
        try:
            requesting_base_url = f"https://{self.__event['headers']['Host']}{self.__event['requestContext']['path']}"
            new_queries = deepcopy(self.__event['queryStringParameters']) if 'queryStringParameters' in self.__event and self.__event[
                'queryStringParameters'] is not None else {}
            limit = int(new_queries['limit'] if 'limit' in new_queries else self.__default_limit)
            if limit == 0:
                return ''
            offset = int(new_queries['offset'] if 'offset' in new_queries else 0)
            offset -= limit
            if offset < 0:
                offset = 0
            new_queries['limit'] = limit
            new_queries['offset'] = offset
            requesting_url = f"{requesting_base_url}?{'&'.join([f'{k}={v}' for k, v in new_queries.items()])}"
        except Exception as e:
            LOGGER.exception(f'error while getting previous page URL')
            return f'unable to get previous page URL, {str(e)}'
        return requesting_url

    def generate_pagination_links(self):
        return [
            {'rel': 'self', 'href': self.__get_current_page()},
            {'rel': 'root', 'href': f"https://{self.__event['headers']['Host']}"},
            {'rel': 'next', 'href': self.__get_next_page()},
            {'rel': 'prev', 'href': self.__get_prev_page()},
        ]
