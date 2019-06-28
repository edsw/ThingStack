from aws_cdk import core


class PoolcontrollerStack(core.Stack):

    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id)

        # The code that defines your stack goes here
