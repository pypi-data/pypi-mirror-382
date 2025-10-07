import os
from aws_lambda_powertools.logging import Logger


def test_init():
    from my_aws_helpers.cognito import Cognito

    os.environ["COGNITO_USER_POOL_ID"] = "fake-pool-id"
    cognito = Cognito()
    assert isinstance(cognito, Cognito) == True


def test_init_with_powertools_logger():
    os.environ["POWERTOOLS_SERVICE_NAME"] = "handler-logger"
    logger = Logger(service=os.environ["POWERTOOLS_SERVICE_NAME"])
    from my_aws_helpers.cognito import Cognito

    os.environ["COGNITO_USER_POOL_ID"] = "fake-pool-id"
    cognito = Cognito()
    assert isinstance(cognito, Cognito) == True
