"""
    description: nya, the best module manager of tgpy
    name: nya
    needs: {}
    needs_pip: []
    once: false
    origin: https://gist.github.com/miralushch/b43ce0642f89814981f341308ba9dac9
    priority: 0
    version: 0.28.0
    wants: {}
"""
import subprocess
import sys
try:
    from tgpy.message_design import get_code # type: ignore [import]
except ImportError:
    from tgpy.message_design import parse_message # type: ignore [import]
    def get_code(message):
        return parse_message(message).code
import gzip
try:
    import zstd # type: ignore [import]
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "zstd"], check=True)
    import zstd # type: ignore [import]
try:
    import brotli # type: ignore [import]
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "brotli"], check=True)
    import brotli # type: ignore [import]
import yaml
import base65536 # type: ignore [import]
try:
    import base65536 # type: ignore [import]
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "base65536"], check=True)
    import base65536 # type: ignore [import]
from telethon.tl.types import MessageEntityCode # type: ignore [import]
from telethon.errors.rpcerrorlist import MessageTooLongError # type: ignore [import]
import tgpy.api # type: ignore [import]
from datetime import datetime
try:
    from semver import VersionInfo # type: ignore [import]
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "semver"], check=True)
    from semver import VersionInfo # type: ignore [import]
from urllib.parse import urlparse
try:
    import python_minifier
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "python-minifier"], check=True)
    import python_minifier
from typing import Tuple, Dict, List, Set, Callable, Awaitable, Union
import io
from pathlib import Path
from enum import Enum
try:
    import gists # type: ignore [import]
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "gists.py"], check=True)
    import gists # type: ignore [import]
import aiohttp
from tgpy.modules import Module, delete_module_file, get_module_names, get_user_modules # type: ignore [import]

class DependencyException(Exception):
    """Exception raised when a dependency is not satisfied
    
    Attributes:
        name: the name of the dependency
        version: the version of the dependency; None if the dependency is not found
    """

    def __init__(self, name: str, version: str | None, message: str = "some dependency is not satisfied"):
        self.name = name
        self.version = version
        self.message = message
        super().__init__(self.message)


Codec = Enum("Codec", ["NONE", "GZIP", "ZSTD", "BROTLI"])


class Nya:
    """nya, the best module manager of tgpy"""

    def __init__(self):
        """DONT TOUCH THIS"""
        async def msg_handler(src: str) -> str:
            source = urlparse(src)
            chat: Union[str, int]
            chat, id = source.path[1:].split("/", 2)[-2:]
            if source.path[1] == "c":
                chat = int("-100" + chat)
            orig = await client.get_messages(chat, ids=int(id)) # type: ignore [name-defined]
            if orig.media is not None:
                f = io.BytesIO()
                await orig.download_media(f)
                f.seek(0)
                text = f.read().decode()
            else:
                text = get_code(orig) or orig.raw_text
            return text
        self.__gist_client = gists.Client()
        async def gist_handler(src: str) -> str:
            return (await self.__gist_client.get_gist(src.split("/")[-1])).files[0].content
        self.__aiohttp_session = aiohttp.ClientSession()
        async def plain_text_handler(src: str) -> str:
            return await (await self.__aiohttp_session.get(src)).text()
        self.__source_handlers: Dict[Tuple[str, str], Callable[[str], Awaitable[str]]] = {
            ("https", "t.me"): msg_handler,
            ("https", "gist.github.com"): gist_handler,
            ("https", "raw.githubusercontent.com"): plain_text_handler
        }
        if tgpy.api.config.get("registry") is None:
            tgpy.api.config.set("registry", dict())
            tgpy.api.config.save()
        if tgpy.api.config.get("share.codec") is None:
            tgpy.api.config.set("share.codec", Codec.NONE.value)
            tgpy.api.config.save()
        if tgpy.api.config.get("share.by_file") is None:
            tgpy.api.config.set("share.by_file", False)
            tgpy.api.config.save()
        if tgpy.api.config.get("share.minify") is None:
            tgpy.api.config.set("share.minify", False)
            tgpy.api.config.save()

    def __iter_registry(self):
        return iter(tgpy.api.config.get("registry").keys())

    async def __get_from(self, src: str):
        source = urlparse(src)
        return await self.__source_handlers[(source.scheme, source.netloc)](src)

    def __encode_code(self, code: str, codec: Codec, minify: bool) -> str:
        code = code.strip("\n")
        if minify:
            try:
                code = python_minifier.awslambda(code)
            except:
                pass
        if codec == Codec.BROTLI:
            return "ʌ" + base65536.encode(brotli.compress(code.encode(), brotli.MODE_TEXT, 11))
        elif codec == Codec.ZSTD:
            return "zstd:" + base65536.encode(zstd.compress(code.encode(), 22))
        elif codec == Codec.GZIP:
            return "b65536:" + base65536.encode(gzip.compress(code.encode(), 9))
        elif codec == Codec.NONE:
            return code
        else:
            raise ValueError(f"unknown codec: {codec}")

    def __decode_code(self, code: str) -> str:
        if code.startswith("b65536:"):
            return gzip.decompress(base65536.decode(code[7:])).decode()
        elif code.startswith("zstd:"):
            return zstd.decompress(base65536.decode(code[5:])).decode()
        elif code.startswith("ʌ"):
            return brotli.decompress(base65536.decode(code[1:])).decode()
        else:
            return code

    def __check_dep(self, name: str, version: str, dep: str, dep_version: str):
        if dep in modules: # type: ignore [name-defined]
            dep_module = modules[dep] # type: ignore [name-defined]
            curr_dep_version = VersionInfo.parse(dep_module.extra["version"]) if "version" in dep_module.extra else VersionInfo.parse("0.0.0")
            dep_version_parsed = VersionInfo.parse(dep_version)
            if curr_dep_version < dep_version_parsed or dep_version_parsed >= curr_dep_version.bump_major():
                raise DependencyException(dep, str(curr_dep_version), f"module {name} {version} needs module {dep} ^{dep_version}, but {dep} {curr_dep_version} found")
        else:
            raise DependencyException(dep, None, f"module {name} {version} needs module {dep} ^{dep_version}, but no {dep} found")
    
    def __regraph_rec(self, name: str, ordered: List[str], visited: Set[str], visiting: Set[str], deleted: Set[str]):
        if name == "nya" or name in visited or name in deleted:
            return
        module = modules[name] # type: ignore [name-defined]
        version = VersionInfo.parse(module.extra["version"]) if "version" in module.extra else VersionInfo.parse("0.0.0")
        is_invalid = False
        module = modules[name] # type: ignore [name-defined]
        needs = module.extra["needs"] if "needs" in module.extra else dict()
        wants = module.extra["wants"] if "wants" in module.extra else dict()
        visiting.add(name)
        for dep in needs:
            try:
                self.__check_dep(name, version, dep, needs[dep])
            except DependencyException as e:
                is_invalid = True
                if e.version:
                    print(f"module {name} {version} needs module {dep} ^{needs[dep]}, but {dep} {e.version} found")
                else:
                    print(f"module {name} {version} needs module {dep} ^{needs[dep]}, but no {dep} found")
                    continue
            if dep in visiting:
                for dep2 in visiting:
                    dep2_module = modules[dep2] # type: ignore [name-defined]
                    dep2_needs = dep2_module.extra["needs"] if "needs" in dep2_module.extra else dict()
                    dep2_wants = dep2_module.extra["wants"] if "wants" in dep2_module.extra else dict()
                    if dep in dep2_needs or dep in dep2_wants:
                        print(f"DEPENDENCY CYCLE: {dep} <-> {dep2}")
                        break
                visiting.discard(dep)
                ordered.append(dep)
                visited.add(dep)
            self.__regraph_rec(dep, ordered, visited, visiting, deleted)
            try:
                self.__check_dep(name, version, dep, needs[dep])
            except DependencyException as e:
                if e.version and not is_invalid:
                    print(f"module {name} {version} needs module {dep} ^{needs[dep]}, but {dep} {e.version} found")
                else:
                    print(f"module {name} {version} needs module {dep} ^{needs[dep]}, but no {dep} found")
                is_invalid = True
        for dep in wants:
            try:
                self.__check_dep(name, version, dep, wants[dep])
            except DependencyException as e:
                if e.version:
                    print(f"module {name} {version} wants module {dep} ^{wants[dep]}, but {dep} {e.version} found")
                    is_invalid = True
                else:
                    continue
            if dep in visiting:
                for dep2 in visiting:
                    dep2_module = modules[dep2] # type: ignore [name-defined]
                    dep2_needs = dep2_module.extra["needs"] if "needs" in dep2_module.extra else dict()
                    dep2_wants = dep2_module.extra["wants"] if "wants" in dep2_module.extra else dict()
                    if dep in dep2_needs or dep in dep2_wants:
                        print(f"DEPENDENCY CYCLE: {dep} <-> {dep2}")
                        break
                visiting.discard(dep)
                ordered.append(dep)
                visited.add(dep)
            self.__regraph_rec(dep, ordered, visited, visiting, deleted)
            try:
                self.__check_dep(name, version, dep, wants[dep])
            except DependencyException as e:
                if e.version and not is_invalid:
                    print(f"module {name} {version} wants module {dep} ^{wants[dep]}, but {dep} {e.version} found")
                    is_invalid = True
        visiting.discard(name)
        if is_invalid:
            self.remove(name)
            deleted.add(name)
        else:
            ordered.append(name)
            visited.add(name)

    def regraph(self):
        ordered, visited, visiting, deleted = ["nya"], set(), set(), set()
        for name in modules:
            self.__regraph_rec(name, ordered, visited, visiting, deleted)
        for i, name in enumerate(ordered):
            module = modules[name]
            module.priority = i
            module.save()

    def add_source_handler(self, domain: Tuple[str, str], handler: Callable[[str], Awaitable[str]]):
        """add a async source handler; domain is ({scheme}, {netloc})"""
        self.__source_handlers[domain] = handler

    async def install(self, origin: str, text: str, force: bool = False):
        """install module from provided {origin} and {text}; if {force} is True version will be ignored"""
        output: List[str] = []
        assert '"""' in text
        header = yaml.safe_load(text.split('"""', 2)[1].strip("\n"))
        name = header["name"]
        version = header["version"] if "version" in header else "0.0.0"
        description = header["description"] if "description" in header else ""
        needs = header["needs"] if "needs" in header else dict()
        wants = header["wants"] if "wants" in header else dict()
        needs_pip = header["needs_pip"] if "needs_pip" in header else []
        code = self.__decode_code(text.split('"""', 2)[2].strip("\n"))
        if name in modules: # type: ignore [name-defined]
            module = modules[name] # type: ignore [name-defined]
            current_version = VersionInfo.parse(module.extra["version"]) if "version" in module.extra else VersionInfo.parse("0.0.0")
            if current_version < VersionInfo.parse(version) or version == "0.0.0" or force:
                self.set_source(name, origin)
                for dep in needs:
                    try:
                        self.__check_dep(name, version, dep, needs[dep])
                    except DependencyException as e:
                        print(*output, sep="\n")
                        self.regraph()
                        raise e
                for dep in wants:
                    try:
                        self.__check_dep(name, str(version), dep, wants[dep])
                    except DependencyException as e:
                        if e.version:
                            print(*output, sep="\n")
                            self.regraph()
                            raise e
                for dep in needs_pip:
                    subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
                    output.append(f"installed pip module {dep}")
                module.code = code
                module.origin = origin
                module.extra["version"] = str(version)
                module.extra["description"] = description
                module.extra["needs"] = needs
                module.extra["wants"] = wants
                module.extra["needs_pip"] = needs_pip
                module.save()
                output.append(f"updated module {name}: {current_version} -> {version}")
                try:
                    await tgpy.api.tgpy_eval(code)
                    output.append(f"ran module {name} {version}")
                except:
                    output.append(f"failed to run module {name} {version}")
            else:
                output.append(f"module {name} is already up to date")
        else:
            self.set_source(name, origin)
            for dep in needs:
                try:
                    self.__check_dep(name, str(version), dep, needs[dep])
                except DependencyException as e:
                    print(*output, sep="\n")
                    self.regraph()
                    raise e
            for dep in wants:
                try:
                    self.__check_dep(name, str(version), dep, wants[dep])
                except DependencyException as e:
                    if e.version:
                        print(*output, sep="\n")
                        self.regraph()
                        raise e
            for dep in needs_pip:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
                output.append(f"installed pip module {dep}")
            module = Module(
                name=name,
                once=False,
                code=code,
                origin=origin,
                priority=int(datetime.now().timestamp()*1000),
                extra={
                    "version": str(version),
                    "description": description,
                    "needs": needs,
                    "wants": wants,
                    "needs_pip": needs_pip
                }
            )
            module.save()
            output.append(f"installed module {name} {version}")
            tgpy.api.config.set("nya.last_installed", name)
            tgpy.api.config.save()
            output.append(f"saved the name of last installed module: {name}")
            try:
                await tgpy.api.tgpy_eval(code)
                output.append(f"ran module {name} {version}")
            except:
                output.append(f"failed to run module {name} {version}")
        print(*output, sep="\n")
        self.regraph()

    async def reg_install(self, name: str):
        """install the module {name} using registry"""
        src = tgpy.api.config.get("registry")[name]
        await self.dep_install(src, await self.__get_from(src))

    async def dep_install(self, origin: str, text: str, force: bool = False, last_tried: str | None = None):
        """install the module {name} using registry"""
        try:
            await self.install(origin, text, force)
        except DependencyException as e:
            if e.name == last_tried:
                raise e
            else:
                await self.reg_install(e.name)
                await self.dep_install(origin, text, force, last_tried=e.name)

    async def update(self):
        """update all installed modules using registry"""
        for name in self.__iter_registry():
            if name in modules:
                await self.reg_install(name)
        await tgpy.api.tgpy_eval("")
        self.regraph()

    async def reg_pull_info(self, name: str):
        """get info about the module {name} using registry"""
        src = tgpy.api.config.get("registry")[name]
        self.pull_info(await self.__get_from(src))

    def print_list(self):
        """print the list of available modules"""
        print(*list(self.__iter_registry()), sep="\n")

    async def share_registry(self):
        """share the list of available modules; can be imported through nya.import_from_reply()"""
        ans = '"""\n    sources:\n' + "\n".join([f"        {name}: \"{tgpy.api.config.get('registry')[name]}\"" for name in list(self.__iter_registry())]) + '\n"""'
        await ctx.msg.respond(ans, formatting_entities=[MessageEntityCode(0, len(ans.encode('utf-16-le')) // 2)])

    def set_source(self, name: str, source: str):
        """set the source {source} of module {name} to the registry"""
        tgpy.api.config.set(f"registry.{name}", source)
        tgpy.api.config.save()

    def get_source(self, name: str) -> str:
        """get the source of module {name} from the registry"""
        return tgpy.api.config.get(f"registry.{name}")

    async def share_sources(self, names: List[str]):
        """share the sources of modules listed in {names} from the registry; can be imported through nya.import_from_reply()"""
        ans = '"""\n    sources:\n' + "\n".join([f"        {name}: \"{tgpy.api.config.get('registry')[name]}\"" for name in names]) + '\n"""'
        await ctx.msg.respond(ans, formatting_entities=[MessageEntityCode(0, len(ans.encode('utf-16-le')) // 2)]) # type: ignore [name-defined]

    async def set_src_to_reply(self):
        """set the source of replied module to the registry"""
        orig = await ctx.msg.get_reply_message()
        if orig.media is not None:
            f = io.BytesIO()
            await orig.download_media(f)
            f.seek(0)
            text = f.read().decode()
        else:
            text = get_code(orig) or orig.raw_text
        if orig.chat.username:
            origin = f"https://t.me/{orig.chat.username}/{orig.id}"
        else:
            origin = f"https://t.me/c/{orig.chat.id}/{orig.id}"
        assert '"""' in text
        header = yaml.safe_load(text.split('"""', 2)[1].strip("\n"))
        name = header["name"]
        self.set_source(name, origin)

    def import_src_list(self, text: str):
        """import the source list from {text} to the registry"""
        assert '"""' in text
        header = yaml.safe_load(text.split('"""', 2)[1].strip("\n"))
        sources = header["sources"]
        for name, source in sources.items():
            self.set_source(name, source)

    async def import_from_reply(self):
        """import the source list from reply to the registry"""
        orig = await ctx.msg.get_reply_message()
        text = get_code(orig) or orig.raw_text
        self.import_src_list(text)

    async def from_reply(self, force: bool = False):
        """install module from reply; if {force} is True version will be ignored"""
        orig = await ctx.msg.get_reply_message() # type: ignore [name-defined]
        if orig.media is not None:
            f = io.BytesIO()
            await orig.download_media(f)
            f.seek(0)
            text = f.read().decode()
        else:
            text = get_code(orig) or orig.raw_text
        if orig.chat.username:
            origin = f"https://t.me/{orig.chat.username}/{orig.id}"
        else:
            origin = f"https://t.me/c/{orig.chat.id}/{orig.id}"
        await self.dep_install(origin, text, force)

    def get_info(self, name: str):
        """get information about installed module {name}"""
        module = modules[name] # type: ignore [name-defined]
        origin = module.origin
        version = module.extra["version"] if "version" in module.extra else "0.0.0"
        description = module.extra["description"] if "description" in module.extra else ""
        needs = module.extra["needs"] if "needs" in module.extra else dict()
        wants = module.extra["wants"] if "wants" in module.extra else dict()
        needs_pip = module.extra["needs_pip"] if "needs_pip" in module.extra else dict()
        print(f"{name} {version} <{origin}> ({description})")
        if needs:
            print("needs:")
            for dep in needs:
                try:
                    self.__check_dep(name, version, dep, needs[dep])
                    print(f"    {dep}: {needs[dep]}")
                except DependencyException as e:
                    if e.version:
                        print(f"    {dep}: {needs[dep]} BROKEN: found invalid {dep} {e.version}")
                    else:
                        print(f"    {dep}: {needs[dep]} BROKEN: not found")
        if wants:
            print("wants:")
            for dep in wants:
                try:
                    self.__check_dep(name, version, dep, wants[dep])
                    print(f"    {dep}: {wants[dep]}")
                except DependencyException as e:
                    if e.version:
                        print(f"    {dep}: {wants[dep]} BROKEN: found invalid {dep} {e.version}")
                    else:
                        print(f"    {dep}: {wants[dep]} not satisfied")
        if needs_pip:
            print("needs_pip:")
            for dep in needs_pip:
                print(f"- {dep}")

    def pull_info(self, text: str):
        """get information about given module by {text}"""
        output: List[str] = []
        assert '"""' in text
        header = yaml.safe_load(text.split('"""', 2)[1].strip("\n"))
        name = header["name"]
        version = header["version"] if "version" in header else "0.0.0"
        description = header["description"] if "description" in header else ""
        needs = header["needs"] if "needs" in header else dict()
        wants = header["wants"] if "wants" in header else dict()
        needs_pip = header["needs_pip"] if "needs_pip" in header else []
        print(f"{name} {version} ({description})")
        if needs:
            print("needs:")
            for dep in needs:
                try:
                    self.__check_dep(name, version, dep, needs[dep])
                    print(f"    {dep}: {needs[dep]}")
                except DependencyException as e:
                    if e.version:
                        print(f"    {dep}: {needs[dep]} BROKEN: found invalid {dep} {e.version}")
                    else:
                        print(f"    {dep}: {needs[dep]} BROKEN: not found")
        if wants:
            print("wants:")
            for dep in wants:
                try:
                    self.__check_dep(name, version, dep, wants[dep])
                    print(f"    {dep}: {wants[dep]}")
                except DependencyException as e:
                    if e.version:
                        print(f"    {dep}: {wants[dep]} BROKEN: found invalid {dep} {e.version}")
                    else:
                        print(f"    {dep}: {wants[dep]} not satisfied")
        if needs_pip:
            print("needs_pip:")
            for dep in needs_pip:
                print(f"- {dep}")

    async def share(self, name: str, codec: Codec | None = None, by_file: bool | None = None, minify: bool | None = None):
        """share installed module {name}; to see list of available codecs run nya.codec_list()"""
        code = modules[name].code # type: ignore [name-defined]
        assert code.startswith('"""')
        header = yaml.safe_load(code.split('"""', 2)[1].strip("\n"))
        h = f'    name: {header["name"]}\n'
        if "version" in header and header["version"] != "0.0.0":
            h += f'    version: {header["version"]}\n'
        if "description" in header and header["description"]:
            h += f'    description: {header["description"]}\n'
        if "needs" in header and header["needs"]:
            h += f'    needs: {header["needs"]}\n'
        if "wants" in header and header["wants"]:
            h += f'    wants: {header["wants"]}\n'
        if "needs_pip" in header and header["needs_pip"]:
            h += f'    needs_pip: {header["needs_pip"]}\n'
        code = code.split('"""', 2)[2]
        if codec is None:
            codec = Codec(value=tgpy.api.config.get("share.codec"))
        if by_file is None:
            by_file = tgpy.api.config.get("share.by_file")
        if minify is None:
            minify = tgpy.api.config.get("share.minify")
        text = '"""\n' + h + '"""\n' + self.__encode_code(code, codec, minify)
        if by_file:
            text_metadata = '\n'.join(line.strip() for line in h.split('\n') if line.strip())
            f = io.BytesIO()
            f.name = f"{name}.py"
            f.write(text.encode())
            f.seek(0)
            await ctx.msg.respond(text_metadata, formatting_entities=[MessageEntityCode(0, len(text_metadata.encode('utf-16-le')) // 2)], file=f) # type: ignore [name-defined]
        else:
            await ctx.msg.respond(text, formatting_entities=[MessageEntityCode(0, len(text.encode('utf-16-le')) // 2)]) # type: ignore [name-defined]
    
    def codec_list(self):
        print(*[codec.name for codec in Codec], sep=", ")

    def set_default_codec(self, codec: Codec):
        """set the default codec for share"""
        tgpy.api.config.set("share.codec", codec.value)
        tgpy.api.config.save()

    def set_default_by_file(self, by_file: bool):
        """set the default by_file for share"""
        tgpy.api.config.set("share.by_file", by_file)
        tgpy.api.config.save()

    def set_default_minify(self, minify: bool):
        """set the default minify for share"""
        tgpy.api.config.set("share.minify", minify)
        tgpy.api.config.save()

    def remove(self, name: str | None = None):
        """remove module {name}; removes the last installed module if no name is specified"""
        if name is None:
            name = tgpy.api.config.get("nya.last_installed")
        delete_module_file(name)
        print(f"removed module {name}.")
        if name != "nya":
            self.regraph()

    def print_graph(self):
        """print dependency graph"""
        for name in modules:
            self.get_info(name)
            print()

    async def run(self, text: str):
        """run module from provided {text}"""
        output: List[str] = []
        assert '"""' in text
        header = yaml.safe_load(text.split('"""', 2)[1].strip("\n"))
        name = header["name"]
        version = VersionInfo.parse(header["version"]) if "version" in header else VersionInfo.parse("0.0.0")
        needs = header["needs"] if "needs" in header else dict()
        wants = header["wants"] if "wants" in header else dict()
        needs_pip = header["needs_pip"] if "needs_pip" in header else []
        code = self.__decode_code(text.split('"""', 2)[2].strip("\n"))
        for dep in needs:
            try:
                self.__check_dep(name, version, dep, needs[dep])
            except DependencyException as e:
                print(*output, sep="\n")
                raise e
        for dep in wants:
            try:
                self.__check_dep(name, str(version), dep, wants[dep])
            except DependencyException as e:
                if e.version:
                    print(*output, sep="\n")
                    self.regraph()
                    raise e
        for dep in needs_pip:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
        try:
            await tgpy.api.tgpy_eval(code)
            output.append(f"ran module {name} {version}")
        except:
            output.append(f"failed to run module {name} {version}")
        print(*output, sep="\n")
        self.regraph()

    async def run_from_reply(self):
        """run module from reply"""
        orig = await ctx.msg.get_reply_message()
        text = get_code(orig) or orig.raw_text
        try:
            origin = f"https://t.me/{orig.chat.username}/{orig.id}"
        except:
            f"https://t.me/c/{orig.chat.id}/{orig.id}"
        await self.run(text)


nya = Nya()

__all__ = ["nya", "Codec", "DependencyException"]
