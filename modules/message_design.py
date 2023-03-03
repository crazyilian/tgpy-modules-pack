"""
    description: replace default "TGPy>" prefix
    name: message_design
    needs: {}
    needs_pip: {}
    once: false
    origin: https://raw.githubusercontent.com/crazyilian/tgpy-modules/main/modules-src/message_design.py
    priority: 18
    version: 0.0.0
    wants: {}
"""
import tgpy._core.message_design as message_design

message_design.TITLE = "$>"

__all__ = []
