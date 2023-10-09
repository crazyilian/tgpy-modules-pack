"""
    description: ''
    name: gachi
    needs:
      dot_hook: 0.0.1
    needs_pip: {}
    once: false
    origin: https://github.com/crazyilian/tgpy-modules/blob/main/modules/gachi.py
    priority: 35
    version: 0.0.1
    wants: {}
"""
@dot_hook('gachi')
async def gachi(text="", message=None, is_edit=None):
    if message is None:
        return
    await message.edit("♂️" + text + "♂️")
