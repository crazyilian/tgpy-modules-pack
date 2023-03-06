"""
    description: nya, the best module manager of tgpy
    name: nya
    needs: {}
    needs_pip: {}
    once: false
    origin: https://gist.github.com/miralushch/b43ce0642f89814981f341308ba9dac9
    priority: 0
    version: 0.32.8
    wants: {}
"""
from tgpy.modules import get_user_modules, get_module_names, delete_module_file, Module
from aiohttp import ClientSession
from enum import Enum
from pathlib import Path
from io import BytesIO
from typing import Tuple, Dict, List, Set, Callable, Awaitable, Union, TypeAlias
from types import ModuleType
from urllib.parse import urlparse
from datetime import datetime
from tgpy.api import config, parse_tgpy_message, tgpy_eval
from telethon.errors.rpcerrorlist import MessageTooLongError
from telethon.tl.types import MessageEntityCode
from yaml import safe_load
from gzip import compress, decompress
from subprocess import run
from sys import executable


def pip_install(lib: str, piplib: str | None = None, output: List[str] | None = None) -> ModuleType:
    try:
        return __import__(lib)
    except ImportError:
        run([executable, "-m", "pip",
             "install", piplib or lib], check=True)
        if output is not None:
            output.append(f"installed pip module {piplib}")
        return __import__(lib)


zstd = pip_install('zstd')
brotli = pip_install('brotli')
base65536 = pip_install('base65536')
VersionInfo: TypeAlias = pip_install(  # type: ignore [valid-type]
    'semver').VersionInfo
python_minifier = pip_install('python_minifier', 'python-minifier')
gists = pip_install('gists', 'gists.py')


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

    def __init__(self) -> None:
        """DONT TOUCH THIS"""
        async def msg_handler(src: str) -> str:
            source = urlparse(src)
            chat: Union[str, int]
            chat, id = source.path[1:].split("/", 2)[-2:]
            if source.path[1] == "c":
                chat = int("-100" + chat)
            orig = await client.get_messages(  # type: ignore [name-defined]
                chat, ids=int(id))
            if orig.media is not None:
                f = BytesIO()
                await orig.download_media(f)
                f.seek(0)
                text = f.read().decode()
            else:
                text = parse_tgpy_message(orig).code or orig.raw_text
            return text
        self.__gist_client = gists.Client()

        async def gist_handler(src: str) -> str:
            return (await self.__gist_client.get_gist(  # type: ignore [no-any-return]
                src.split("/")[-1])).files[0].content
        self.__aiohttp_session = ClientSession()

        async def plain_text_handler(src: str) -> str:
            return await (await self.__aiohttp_session.get(src)).text()
        self.__source_handlers: Dict[Tuple[str, str], Callable[[str], Awaitable[str]]] = {
            ("https", "t.me"): msg_handler,
            ("https", "gist.github.com"): gist_handler,
            ("https", "raw.githubusercontent.com"): plain_text_handler
        }
        if config.get("registry") is None:
            config.set("registry", dict())
            config.save()
        if config.get("share.codec") is None:
            config.set("share.codec", Codec.NONE.value)
            config.save()
        if config.get("share.by_file") is None:
            config.set("share.by_file", False)
            config.save()
        if config.get("share.minify") is None:
            config.set("share.minify", False)
            config.save()

    def __iter_registry(self) -> List[str]:
        return iter(config.get(  # type: ignore [no-any-return]
            "registry").keys())

    async def __get_from(self, src: str) -> str:
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
            return "ʌ" + base65536.encode(  # type: ignore [no-any-return]
                brotli.compress(code.encode(), brotli.MODE_TEXT, 11))
        elif codec == Codec.ZSTD:
            return "zstd:" + base65536.encode(  # type: ignore [no-any-return]
                zstd.compress(code.encode(), 22))
        elif codec == Codec.GZIP:
            return "b65536:" + base65536.encode(  # type: ignore [no-any-return]
                compress(code.encode(), 9))
        elif codec == Codec.NONE:
            return code
        else:
            raise ValueError(f"unknown codec: {codec}")

    def __decode_code(self, code: str) -> str:
        if code.startswith("b65536:"):
            return decompress(base65536.decode(code[7:])).decode()
        elif code.startswith("zstd:"):
            return zstd.decompress(  # type: ignore [no-any-return]
                base65536.decode(code[5:])).decode()
        elif code.startswith("ʌ"):
            return brotli.decompress(  # type: ignore [no-any-return]
                base65536.decode(code[1:])).decode()
        else:
            return code

    def __check_dep(self, name: str, version: str, dep: str, dep_version: str) -> None:
        if dep in modules:  # type: ignore [name-defined]
            dep_module = modules[dep]  # type: ignore [name-defined]
            curr_dep_version = VersionInfo.parse(
                dep_module.extra["version"]) if "version" in dep_module.extra else VersionInfo.parse("0.0.0")
            dep_version_parsed = VersionInfo.parse(dep_version)
            if curr_dep_version < dep_version_parsed or dep_version_parsed >= curr_dep_version.bump_major():
                raise DependencyException(dep, str(
                    curr_dep_version), f"module {name} {version} needs module {dep} ^{dep_version}, but {dep} {curr_dep_version} found")
        else:
            raise DependencyException(
                dep, None, f"module {name} {version} needs module {dep} ^{dep_version}, but no {dep} found")

    def __parse(self, text: str) -> Tuple[str, VersionInfo, str, Dict[str, str], Dict[str, str], Dict[str, str], str]:
        assert '"""' in text
        header = safe_load(text.split('"""', 2)[1].strip("\n"))
        name = header["name"]
        version = VersionInfo.parse(
            header["version"] if "version" in header else "0.0.0")
        description = header["description"] if "description" in header else ""
        needs = header["needs"] if "needs" in header else dict()
        wants = header["wants"] if "wants" in header else dict()
        needs_pip = header["needs_pip"] if "needs_pip" in header else dict()
        code = self.__decode_code(text.split('"""', 2)[2].strip("\n"))
        return name, version, description, needs, wants, needs_pip, code

    def __print_info(self, name: str, version: VersionInfo, description: str, needs: Dict[str, str], wants: Dict[str, str], needs_pip: Dict[str, str]) -> None:
        print(f"{name} {version} ({description})")
        if needs:
            print("needs:")
            for dep in needs:
                print(f"    {dep}: {needs[dep]}")
        if wants:
            print("wants:")
            for dep in wants:
                try:
                    self.__check_dep(name, version, dep, wants[dep])
                    print(f"    {dep}: {wants[dep]}")
                except DependencyException as e:
                    if e.version is None:
                        print(f"    {dep}: {wants[dep]} not satisfied")
        if needs_pip:
            print("needs_pip:")
            for dep in needs_pip:
                print(f"- {dep}")

    def __check_deps(self, name: str, version: VersionInfo, needs: Dict[str, str], wants: Dict[str, str], needs_pip: Dict[str, str], output: List[str]) -> None:
        for dep, ver in needs.items():
            try:
                self.__check_dep(name, version, dep, ver)
            except DependencyException as e:
                print(*output, sep="\n")
                self.regraph()
                raise e
        for dep, ver in wants.items():
            try:
                self.__check_dep(name, str(version), dep, ver)
            except DependencyException as e:
                if e.version:
                    print(*output, sep="\n")
                    self.regraph()
                    raise e
        for dep, pip in needs_pip.items():
            pip_install(dep, pip, output)

    async def __run(self, name: str, version: VersionInfo, code: str, output: List[str]) -> None:
        try:
            await tgpy_eval(code)
            output.append(f"ran module {name} {version}")
        except:
            output.append(f"failed to run module {name} {version}")

    def __regraph_rec(self, name: str, ordered: List[str], visited: Set[str], visiting: Set[str], deleted: Set[str]) -> None:
        if name == "nya" or name in visited or name in deleted:
            return
        module = modules[name]  # type: ignore [name-defined]
        version = VersionInfo.parse(
            module.extra["version"]) if "version" in module.extra else VersionInfo.parse("0.0.0")
        is_invalid = False
        module = modules[name]  # type: ignore [name-defined]
        needs = module.extra["needs"] if "needs" in module.extra else dict()
        wants = module.extra["wants"] if "wants" in module.extra else dict()
        visiting.add(name)
        for dep in needs:
            try:
                self.__check_dep(name, version, dep, needs[dep])
            except DependencyException as e:
                is_invalid = True
                if e.version:
                    print(
                        f"module {name} {version} needs module {dep} ^{needs[dep]}, but {dep} {e.version} found")
                else:
                    print(
                        f"module {name} {version} needs module {dep} ^{needs[dep]}, but no {dep} found")
                    continue
            if dep in visiting:
                for dep2 in visiting:
                    dep2_module = modules[dep2]  # type: ignore [name-defined]
                    dep2_needs = dep2_module.extra["needs"] if "needs" in dep2_module.extra else dict(
                    )
                    dep2_wants = dep2_module.extra["wants"] if "wants" in dep2_module.extra else dict(
                    )
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
                    print(
                        f"module {name} {version} needs module {dep} ^{needs[dep]}, but {dep} {e.version} found")
                else:
                    print(
                        f"module {name} {version} needs module {dep} ^{needs[dep]}, but no {dep} found")
                is_invalid = True
        for dep in wants:
            try:
                self.__check_dep(name, version, dep, wants[dep])
            except DependencyException as e:
                if e.version:
                    print(
                        f"module {name} {version} wants module {dep} ^{wants[dep]}, but {dep} {e.version} found")
                    is_invalid = True
                else:
                    continue
            if dep in visiting:
                for dep2 in visiting:
                    dep2_module = modules[dep2]  # type: ignore [name-defined]
                    dep2_needs = dep2_module.extra["needs"] if "needs" in dep2_module.extra else dict(
                    )
                    dep2_wants = dep2_module.extra["wants"] if "wants" in dep2_module.extra else dict(
                    )
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
                    print(
                        f"module {name} {version} wants module {dep} ^{wants[dep]}, but {dep} {e.version} found")
                    is_invalid = True
        visiting.discard(name)
        if is_invalid:
            self.remove(name)
            deleted.add(name)
        else:
            ordered.append(name)
            visited.add(name)

    def regraph(self) -> None:
        visited: Set[str]
        visiting: Set[str]
        deleted: Set[str]
        ordered, visited, visiting, deleted = ["nya"], set(), set(), set()
        for name in modules:  # type: ignore [name-defined]
            self.__regraph_rec(name, ordered, visited, visiting, deleted)
        for i, name in enumerate(ordered):
            module = modules[name]  # type: ignore [name-defined]
            module.priority = i
            module.save()

    def add_source_handler(self, domain: Tuple[str, str], handler: Callable[[str], Awaitable[str]]) -> None:
        """add a async source handler; domain is ({scheme}, {netloc})"""
        self.__source_handlers[domain] = handler

    async def install(self, origin: str, text: str, force: bool = False) -> None:
        """install module from provided {origin} and {text}; if {force} is True version will be ignored"""
        output: List[str] = []
        name, version, description, needs, wants, needs_pip, code = self.__parse(
            text)
        if name in modules:  # type: ignore [name-defined]
            module = modules[name]  # type: ignore [name-defined]
            current_version = VersionInfo.parse(
                module.extra["version"]) if "version" in module.extra else VersionInfo.parse("0.0.0")
            if current_version < version or version == "0.0.0" or force:
                self.set_source(name, origin)
                self.__check_deps(name, version, needs,
                                  wants, needs_pip, output)
                module.code = code
                module.origin = origin
                module.extra["version"] = str(version)
                module.extra["description"] = description
                module.extra["needs"] = needs
                module.extra["wants"] = wants
                module.extra["needs_pip"] = needs_pip
                module.save()
                output.append(
                    f"updated module {name}: {current_version} -> {version}")
                await self.__run(name, version, code, output)
            else:
                output.append(f"module {name} is already up to date")
        else:
            self.set_source(name, origin)
            self.__check_deps(name, version, needs, wants, needs_pip, output)
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
            config.set("nya.last_installed", name)
            config.save()
            output.append(f"saved the name of last installed module: {name}")
            await self.__run(name, version, code, output)
        print(*output, sep="\n")
        self.regraph()

    async def reg_install(self, name: str, force: bool = False) -> None:
        """install the module {name} using registry"""
        src = config.get("registry")[name]
        await self.dep_install(src, await self.__get_from(src), force)

    async def dep_install(self, origin: str, text: str, force: bool = False, last_tried: str | None = None) -> None:
        """install the module {name} using registry"""
        try:
            await self.install(origin, text, force)
        except DependencyException as e:
            if e.name == last_tried:
                raise e
            else:
                await self.reg_install(e.name)
                await self.dep_install(origin, text, force, last_tried=e.name)

    async def update(self) -> None:
        """update all installed modules using registry"""
        for name in self.__iter_registry():
            if name in modules:  # type: ignore [name-defined]
                await self.reg_install(name)
        await tgpy_eval("")
        self.regraph()

    async def reg_pull_info(self, name: str) -> None:
        """get info about the module {name} using registry"""
        src = config.get("registry")[name]
        self.pull_info(await self.__get_from(src))

    def print_list(self) -> None:
        """print the list of available modules"""
        print(*list(self.__iter_registry()), sep="\n")

    async def share_registry(self) -> None:
        """share the list of available modules; can be imported through nya.import_from_reply()"""
        ans = '"""\n    sources:\n' + \
            "\n".join([f"        {name}: \"{config.get('registry')[name]}\"" for name in list(
                self.__iter_registry())]) + '\n"""'
        await ctx.msg.respond(ans, formatting_entities=[MessageEntityCode(0, len(ans.encode('utf-16-le')) // 2)])  # type: ignore [name-defined]

    def set_source(self, name: str, source: str, overwrite: bool = True) -> None:
        """set the source {source} of module {name} to the registry"""
        if overwrite or name not in config.get(f"registry"):
            config.set(f"registry.{name}", source)
            config.save()

    def remove_source(self, name: str) -> None:
        """remove the source of module {name} from the registry"""
        config.unset(f"registry.{name}")
        config.save()

    def get_source(self, name: str) -> str:
        """get the source of module {name} from the registry"""
        return config.get(f"registry.{name}")  # type: ignore [no-any-return]

    async def share_sources(self, names: List[str]) -> None:
        """share the sources of modules listed in {names} from the registry; can be imported through nya.import_from_reply()"""
        ans = '"""\n    sources:\n' + \
            "\n".join(
                [f"        {name}: \"{config.get('registry')[name]}\"" for name in names]) + '\n"""'
        await ctx.msg.respond(ans, formatting_entities=[MessageEntityCode(0, len(ans.encode('utf-16-le')) // 2)])  # type: ignore [name-defined]

    async def set_src_to_reply(self, overwrite: bool = True) -> None:
        """set the source of replied module to the registry"""
        orig = await ctx.msg.get_reply_message()  # type: ignore [name-defined]
        if orig.media is not None:
            f = BytesIO()
            await orig.download_media(f)
            f.seek(0)
            text = f.read().decode()
        else:
            text = parse_tgpy_message(orig).code or orig.raw_text
        if orig.chat.username:
            origin = f"https://t.me/{orig.chat.username}/{orig.id}"
        else:
            origin = f"https://t.me/c/{orig.chat.id}/{orig.id}"
        assert '"""' in text
        header = safe_load(text.split('"""', 2)[1].strip("\n"))
        name = header["name"]
        self.set_source(name, origin, overwrite)

    def import_src_list(self, text: str, overwrite: bool = True) -> None:
        """import the source list from {text} to the registry"""
        assert '"""' in text
        header = safe_load(text.split('"""', 2)[1].strip("\n"))
        sources = header["sources"]
        for name, source in sources.items():
            self.set_source(name, source, overwrite)

    async def import_from_reply(self, overwrite: bool = True) -> None:
        """import the source list from reply to the registry"""
        orig = await ctx.msg.get_reply_message()  # type: ignore [name-defined]
        text = parse_tgpy_message(orig).code or orig.raw_text
        self.import_src_list(text, overwrite)

    async def import_from_src(self, src: str, overwrite: bool = True) -> None:
        """import the source list from the source {src} to the registry"""
        self.import_src_list(await self.__get_from(src), overwrite)

    async def from_reply(self, force: bool = False) -> None:
        """install module from reply; if {force} is True version will be ignored"""
        orig = await ctx.msg.get_reply_message()  # type: ignore [name-defined]
        if orig.media is not None:
            f = BytesIO()
            await orig.download_media(f)
            f.seek(0)
            text = f.read().decode()
        else:
            text = parse_tgpy_message(orig).code or orig.raw_text
        if orig.chat.username:
            origin = f"https://t.me/{orig.chat.username}/{orig.id}"
        else:
            origin = f"https://t.me/c/{orig.chat.id}/{orig.id}"
        await self.dep_install(origin, text, force)

    def get_info(self, name: str) -> None:
        """get information about installed module {name}"""
        self.__print_info(
            *self.__parse(modules[name].code)[:-1])  # type: ignore [name-defined]

    def pull_info(self, text: str) -> None:
        """get information about given module by {text}"""
        self.__print_info(*self.__parse(text)[:-1])

    async def share(self, name: str, codec: Codec | None = None, by_file: bool | None = None, minify: bool | None = None) -> None:
        """share installed module {name}; to see list of available codecs run nya.codec_list()"""
        code = modules[name].code  # type: ignore [name-defined]
        assert code.startswith('"""')
        header = safe_load(code.split('"""', 2)[1].strip("\n"))
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
            codec = Codec(value=config.get("share.codec"))
        if by_file is None:
            by_file = config.get("share.by_file")
        if minify is None:
            minify = config.get("share.minify")
        text = '"""\n' + h + '"""\n' + self.__encode_code(code, codec, minify)
        if by_file:
            text_metadata = '\n'.join(line.strip()
                                      for line in h.split('\n') if line.strip())
            f = BytesIO()
            f.name = f"{name}.py"
            f.write(text.encode())
            f.seek(0)
            fe = [MessageEntityCode(
                0, len(text_metadata.encode('utf-16-le')) // 2)]
            await ctx.msg.respond(  # type: ignore [name-defined]
                text_metadata, formatting_entities=fe, file=f)
        else:
            fe = [MessageEntityCode(
                0, len(text.encode('utf-16-le')) // 2)]
            await ctx.msg.respond(  # type: ignore [name-defined]
                text, formatting_entities=fe)

    def codec_list(self) -> None:
        print(*[codec.name for codec in Codec], sep=", ")

    def set_default_codec(self, codec: Codec) -> None:
        """set the default codec for share"""
        config.set("share.codec", codec.value)
        config.save()

    def set_default_by_file(self, by_file: bool) -> None:
        """set the default by_file for share"""
        config.set("share.by_file", by_file)
        config.save()

    def set_default_minify(self, minify: bool) -> None:
        """set the default minify for share"""
        config.set("share.minify", minify)
        config.save()

    def remove(self, name: str | None = None) -> None:
        """remove module {name}; removes the last installed module if no name is specified"""
        if name is None:
            name = config.get("nya.last_installed")
        delete_module_file(name)
        print(f"removed module {name}.")
        if name != "nya":
            self.regraph()

    def print_graph(self) -> None:
        """print dependency graph"""
        for name in modules:  # type: ignore [name-defined]
            self.get_info(name)
            print()

    async def run(self, text: str) -> None:
        """run module from provided {text}"""
        output: List[str] = []
        name, version, _, needs, wants, needs_pip, code = self.__parse(text)
        self.__check_deps(name, version, needs, wants, needs_pip, output)
        await self.__run(name, version, code, output)
        print(*output, sep="\n")
        self.regraph()

    async def run_from_reply(self) -> None:
        """run module from reply"""
        orig = await ctx.msg.get_reply_message()  # type: ignore [name-defined]
        text = parse_tgpy_message(orig).code or orig.raw_text
        try:
            origin = f"https://t.me/{orig.chat.username}/{orig.id}"
        except:
            f"https://t.me/c/{orig.chat.id}/{orig.id}"
        await self.run(text)


nya = Nya()

__all__ = ["nya", "Codec", "DependencyException"]
