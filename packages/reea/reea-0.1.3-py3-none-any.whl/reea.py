"""
Telegram: @LAEGER_MO
"""

import sys
import site
import os

def setup_reea():
    user_site = site.getusersitepackages()
    if not os.path.exists(user_site):
        os.makedirs(user_site)
    
    customize_content = '''
def reea(*args, **kwargs):
    print(*args, **kwargs)

try:
    import builtins
    builtins.reea = reea
except ImportError:
    try:
        import __builtins__ as builtins  
        builtins.reea = reea
    except:
        pass

print("✅ reea is ready! Telegram: @LAEGER_MO")
'''
    
    customize_file = os.path.join(user_site, 'usercustomize.py')
    with open(customize_file, 'w') as f:
        f.write(customize_content)
    
    print(f"[√] reea installed at: {customize_file}")

if __name__ == "__main__":
    setup_reea()