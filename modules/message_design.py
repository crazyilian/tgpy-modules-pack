"""
    name: message_design
    once: false
    origin: tgpy://module/message_design
    priority: 2
    save_locals: true
    description: replace default "TGPy>" prefix
"""
import tgpy._core.message_design as message_design

message_design.TITLE = "$>"

__all__ = []
