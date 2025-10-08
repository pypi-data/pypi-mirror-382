"""
Telegram: @LAEGER_MO
"""

def rree(*args, **kwargs):
    print(*args, **kwargs)
try:
    import builtins
    builtins.rree = rree
except ImportError:
    try:
        import __builtins__ as builtins
        builtins.rree = rree
    except:
        pass

print("[√] rree initialized - Telegram: @LAEGER_MO")