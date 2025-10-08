from mdps_ds_lib.lib.aws.aws_cred import AwsCred


class AwsCognito(AwsCred):
    def __init__(self, user_pool_id: str):
        super().__init__()
        self.__cognito = self.get_client('cognito-idp')
        self.__user_pool_id = user_pool_id

    def get_groups(self, username: str):
        response = self.__cognito.admin_list_groups_for_user(
            Username=username,
            UserPoolId=self.__user_pool_id,
            Limit=60,
            # NextToken='string'
        )
        if response is None or 'Groups' not in response:
            return []
        belonged_groups = [k['GroupName'] for k in response['Groups']]
        return belonged_groups

    def add_user_to_group(self, username: str, group_name: str):
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/admin_add_user_to_group.html

        response = self.__cognito.admin_add_user_to_group(
            UserPoolId=self.__user_pool_id,
            Username=username,
            GroupName=group_name,
        )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise RuntimeError(response)
        return response

    def remove_user_from_group(self, username: str, group_name: str):
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/admin_remove_user_from_group.html
        response = self.__cognito.admin_remove_user_from_group(
            UserPoolId=self.__user_pool_id,
            Username=username,
            GroupName=group_name,
        )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise RuntimeError(response)
        return response

    def add_group(self, group_name: str):
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/create_group.html
        response = self.__cognito.create_group(
            GroupName=group_name,
            UserPoolId=self.__user_pool_id,
            # Description='NA',
            # RoleArn='string',
        )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise RuntimeError(response)
        return response

    def delete_group(self, group_name: str):
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/delete_group.html
        response = self.__cognito.delete_group(
            GroupName=group_name,
            UserPoolId=self.__user_pool_id,
            # Description='NA',
            # RoleArn='string',
        )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise RuntimeError(response)
        return response
