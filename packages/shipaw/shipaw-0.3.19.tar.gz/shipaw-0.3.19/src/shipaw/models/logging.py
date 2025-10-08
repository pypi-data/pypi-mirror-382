import json
import pprint
from datetime import datetime
from typing import Sequence, TYPE_CHECKING

from loguru import logger
from pydantic import BaseModel

from shipaw.config import ShipawSettings

if TYPE_CHECKING:
    from shipaw.fapi.requests import ShipmentRequest
    from shipaw.fapi.responses import ShipmentBookingResponse


def ndlog_dict(data: dict, ndjson_file=None):
    ndjson_file = ndjson_file or ShipawSettings.from_env().ndjson_log_file
    with open(ndjson_file, 'a') as jf:
        print(json.dumps(data, separators=(',', ':')), file=jf)


def log_obj_text(obj: BaseModel, message: str = None, *, level: str = 'DEBUG', logger_=logger):
    message = message or obj.__class__.__name__
    logger_.log(
        level,
        message
        + ':\n'
        + pprint.pformat(
            obj.model_dump(
                mode='json',
                exclude={
                    'label_data': ...,
                    'response': {'label_data'},
                },
            ),
            indent=2,
        ),
    )


def log_obj_json(obj: BaseModel, message: str = None, *, ndjson_file=None):
    ndjson_file = ndjson_file or ShipawSettings.from_env().ndjson_log_file
    timestamp = datetime.now().isoformat(timespec='seconds')
    logdict = {
        'data_type': type(obj).__name__,
        'timestamp': timestamp,
        'message': message,
        'obj_data': obj.model_dump(mode='json', exclude={'label_data': ..., 'response': {'label_data'}}),
    }
    ndlog_dict(logdict, ndjson_file=ndjson_file)


def log_obj(
    obj: BaseModel,
    message: str = None,
    level: str = 'DEBUG',
    logger_=logger,
    ndjson_file=None,
):
    ndjson_file = ndjson_file or ShipawSettings.from_env().ndjson_log_file
    log_obj_text(obj, message, level=level, logger_=logger_)
    log_obj_json(obj, message, ndjson_file=ndjson_file)


def log_booked_shipment(request: 'ShipmentRequest', response: 'ShipmentBookingResponse'):
    from shipaw.models.conversation import ShipmentConversation

    conversation = ShipmentConversation(request=request, response=response)
    ndlog_dict(conversation.model_dump(mode='json', exclude={'response': {'label_data'}}))


def log_objs(objs: Sequence[BaseModel], message: str = None):
    if message:
        logger.debug(message + ':\n')
    for obj in objs:
        log_obj_text(obj)
