def asse(*args, **kwargs):
    print(*args, **kwargs)

try:
    import builtins
    builtins.asse = asse
    asse("Programmer - Telegram: @LAEGER_MO - @sis_c")
except ImportError:
    __builtins__['asse'] = asse
    
    
