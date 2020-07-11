import boto3
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info('REQUEST:\n %s', event)
    # detail = event['detail']
    # event_name = detail['eventName']

    # except Exception as error:
    #     logger.info(str(error))
