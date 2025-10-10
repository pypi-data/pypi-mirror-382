# Superb_logger

**Superb Logger is a sleek and powerful logging utility built for Python applications.**

### Basic Usage

```python
from logging import Formatter

from superb_logger import Configurator, Level
from colorlog import ColoredFormatter

colored_formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
    log_colors={
        'DEBUG':    'light_black',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red',
    }
)

configurator = Configurator(
    base_level=Level.DEBUG, 
    console_formatter=colored_formatter
)
log = configurator.get_root_logger()
log.debug("Testing")
log.info("Testing")
log.error("Testing")
log.critical("Testing")
```

### License

MIT License — feel free to use it in any project! 🎉

### Documentation

[https://superb-logger.dkurchigin.ru/](https://superb-logger.dkurchigin.ru/)

### Author

Made with ❤️ by [@dkurchigin](https://gitverse.ru/dkurchigin)

### Gitverse

[https://gitverse.ru/dkurchigin/superb_logger](https://gitverse.ru/dkurchigin/superb_logger)
