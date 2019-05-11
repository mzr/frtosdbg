# FrtosDBG - FreeRTOS debugging made easy.

## Installation

```
git clone https://github.com/mzr/frtosdbg.git ~/frtosdbg
echo "source ~/frtosdbg/gdbinit.py" >> ~/.gdbinit
```

## Features

### Commands
- list all freertos-related commands `freertos`
- printing task lists `freertos tasks [ready|blocked|pending]`
- printing queues `freertos queues`

### Functions
- curtask function `$curtask()`

## It is easily extensible

- addition of new gdb commands and functions is as simple as writing a python 
function and using `@Command` on it.
- every in-memory C-struct can be represented as a python object using 
`structgen` function.
