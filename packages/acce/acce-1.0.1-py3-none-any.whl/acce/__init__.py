"""
المبرمج: Telegram: @LAEGER_MO - @sis_c
"""

from .core import acce, install_global
install_global()
from .installer import install_all_versions, install_current_session

__all__ = ['acce', 'install_global', 'install_all_versions', 'install_current_session']
__version__ = '1.0.1'

try:
    acce("Welcome to the new version ")
except:
    pass