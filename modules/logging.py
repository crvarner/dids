def _init_log():
    """
    From http://article.gmane.org/gmane.comp.python.web2py/11091
    """

    import logging
    from logging.handlers import SysLogHandler

    logger = logging.getLogger(request.application)
    logger.setLevel(logging.DEBUG)
    handler = SysLogHandler(address='/dev/log')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(
        '%s' % request.application + '[%(process)d]: %(levelname)s:
    %(filename)s at line %(lineno)d: %(message)s'))'
    logger.addHandler(handler) return logger

logging=cache.ram('once',lambda:_init_log(),time_expire=99999999)