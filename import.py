"""
    name: import
    once: false
    origin: tgpy://module/import
    priority: 100
    save_locals: true
"""
try:
    from tgpy.message_design import get_code
except ImportError:
    from tgpy.message_design import parse_message
    def get_code(message):
        return parse_message(message).code

import gzip
import yaml

async def import_module():
    orig = await ctx.msg.get_reply_message()
    text = orig.raw_text
    assert '"""' in text
    code = get_code(orig) or text
    header = yaml.safe_load(code.split('"""', 2)[1].strip("\n"))
    name = header["name"]
    text = code.split('"""', 2)[2].strip("\n")
    if text.startswith("b65536:"):
        import base65536
        text = gzip.decompress(base65536.decode(text[7:])).decode()
    return await modules.add(name, text)
