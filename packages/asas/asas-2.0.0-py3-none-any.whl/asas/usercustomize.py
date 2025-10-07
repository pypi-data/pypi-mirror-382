def asas(*args, **kwargs):
    print(*args, **kwargs)

try:
    import builtins
    builtins.asas = asas
    asas("Programmer - Telegram: @LAEGER_MO - @sis_c")
except ImportError:
    __builtins__['asas'] = asas
    
    
