# -*- encoding: utf8 -*-
import logging

logger = logging.getLogger(__name__)


def add(x, y):
    logger.info("call with x=%s, y=%s", x, y)
    return x + y
