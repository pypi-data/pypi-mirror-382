import json

from mdps_ds_lib.lib.aws.aws_cred import AwsCred


class AwsLambda(AwsCred):
    def __init__(self):
        super().__init__()
        self.__lambda_client = self.get_client('lambda')

    def invoke_function(self, function_name: str, payload: dict):
        response = self.__lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='Event',  # 'Event' = async | 'RequestResponse' = sync | 'DryRun',
            LogType='None',  # 'None' = async | 'Tail =  sync',
            ClientContext='',  # Up to 3583 bytes of base64-encoded data
            Payload=json.dumps(payload).encode(),
            # Qualifier='string'
        )
        return response
