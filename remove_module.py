"""
    name: remove_module
    once: false
    origin: tgpy://module/remove_module
    priority: 300
    save_locals: true
"""
from tgpy.modules import get_sorted_modules
from collections.abc import Iterable
import yaml

def get_module_names(ms):
    names = []
    all_names = [m.name for m in get_sorted_modules()]
    for m in ms:
        if isinstance(m, int) and 0 <= m - 1 < len(all_names):
            names.append(all_names[m - 1])
        elif isinstance(m, str):
            names.append(m)
        elif isinstance(m, Iterable):
            names.extend(get_module_names(m))
        else:
            names.append(str(m))
    return names

async def remove_modules(*ms):
    names = get_module_names(ms)
    messages = []
    if ctx.msg.is_reply:
        orig = await ctx.msg.get_reply_message()
        text = orig.raw_text
        try:
            assert '"""' in text
            code = get_code(orig) or text
            header = yaml.safe_load(code.split('"""', 2)[1].strip("\n"))
            names.append(header["name"])
        except Exception as e:
            messages.append("Reply message is not a module")
    messages += [modules.remove(name) for name in names]
    return '\n'.join(messages)

remove_module = remove_modules
