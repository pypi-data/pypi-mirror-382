import boto3


class running_stacks_info:
    """
    A utility class to get the running stacks from CloudFormation.
    """

    def __init__(self, region='us-west-2'):
        self.region = region.lower()
        self.cf_resource = boto3.resource(
            'cloudformation', region_name=self.region)

    @property
    def region(self):
        return self.__region

    @region.setter
    def region(self, region):
        self.__region = region

    def get_stack_names(self, product, environment):
        """
        For a given combination of product and environment returns a list of running stack names.
        Returns an empty list of there are no running stacks for the specified product and environment.
        Parameters
        ----------
        product: str
                The name of the desired product/application (e.g., sdap)
        environment: str
                The name of the desired environment (e.g., Test)
        Returns
        -------
                A list of running stack names for the specified product and environment.
        Exceptions
        ----------
        None
        """

        RUNNING_STATES = (
            'CREATE_COMPLETE,UPDATE_COMPLETE,UPDATE_ROLLBACK_COMPLETE'
        ).split(',')
        prod_name = product.lower()
        env_name = environment.capitalize()

        running_stacks_list = [
            stack.name for stack in self.cf_resource.stacks.all()
            if stack.stack_status in RUNNING_STATES
        ]

        desired_list = []
        for stack_name in running_stacks_list:
            if stack_name.find(prod_name) != -1 and stack_name.find(
                    env_name) != -1:
                desired_list.append(stack_name)

        return desired_list


def main():
    print('Now printing the running stacks:')
    for stack_name in running_stacks_info().get_stack_names('sdap', 'Dev'):
        print('\trunning stack name = {}'.format(stack_name))


if __name__ == '__main__':
    main()
