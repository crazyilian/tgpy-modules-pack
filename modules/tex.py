"""
    description: apply tex automatically and via .tex
    name: tex
    needs: {}
    needs_pip:
      unicodeit: unicodeit
    once: false
    origin: https://github.com/crazyilian/tgpy-modules/blob/main/modules/tex.py
    priority: 38
    version: 0.4.1
    wants: {}
"""
import telethon
import tgpy.api
import unicodeit

AUTOACTIVATE = ['^', r'\alpha', r'\beta', r'\Gamma', r'\gamma', r'\Delta', r'\delta', r'\epsilon', r'\varepsilon',
                r'\zeta', r'\eta', r'\Theta', r'\theta', r'\varthera', r'\iota', r'\kappa', r'\varkappa', r'\Lambda',
                r'\lambda', r'\mu', r'\nu', r'\Xi', r'\xi', r'\Pi', r'\pi', r'\varpi', r'\rho', r'\varrho', r'\Sigma',
                r'\sigma', r'\varsigma', r'\tau', r'\Upsilon', r'\upsilon', r'\Phi', r'\phi', r'\varphi', r'\chi',
                r'\Psi', r'\psi', r'\Omega', r'\omega', r'\mathbb', r'\mathcal', r'\ne', r'\approx', r'\le', r'\ge',
                r'\leqslant', r'\geqslant', r'\pm', r'\mp', r'\times', r'\cdot', r'\div', r'\sqrt', r'\angle', r'\perp',
                r'\parallel', r'\cong', r'\sim', r'\triangle', r'\equiv', r'\triangleq', r'\propto', r'\infty', r'\ll',
                r'\gg', r'\lfloor', r'\rfloor', r'\lceil', r'\rceil', r'\circ', r'\cap', r'\cup', r'\subseteq',
                r'\subset', r'\not', r'\supseteq', r'\supset', r'\in', r'\emptyset', r'\lor', r'\land', r'\neg',
                r'\oplus', r'\implies', r'\iff', r'\forall', r'\exists', r'\nexists', r'\therefore', r'\because',
                r'\int', r'\oint', r'\preceq', r'\prec', r'\succeq', r'\succ', r'\d', r'\vdots', r'\cdots', r'\ddots',
                r'\sum', r'\prod', r'\leftarrow', r'\rightarrow', r'\uparrow', r'\downarrow', r'\leftrightarrow',
                r'\updownarrow', r'\Leftarrow', r'\Rightarrow', r'\Uparrow', r'\Downarrow', r'\Leftrightarrow',
                r'\Updownarrow', r'\to', r'\mapsto', r'\nearrow', r'\searrow', r'\swarrow', r'\nwarrow',
                r'\hookleftarrow', r'\hookrightarrow', r'\leftharpoonup', r'\rightharpoonup', r'\leftharpoondown',
                r'\rightharpoondown', r'\langle', r'\rangle', r'\vee', r'\wedge', r'\bigvee', r'\bigwedge', r'\bigcap',
                r'\bigcup', r'\bigoplus', r'\nsubset', r'\nsubseteq', r'\notin', r'\square', r'\blacksquare', r'\ldots',
                r'\nsupset', r'\nsupseteq', r'\impliedby', r'\ni', r'\notni']

ALIAS = {'\\' + c * 2: f'\\mathbb{{{c}}}' for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}
ALIAS |= {r'\Alpha': 'A', r'\Beta': 'B', r'\Epsilon': 'E', r'\Zeta': 'Z', r'\Eta': 'H', r'\Iota': 'I', r'\Kappa': 'K',
          r'\Mu': 'M', r'\Nu': 'N', r'\Omicron': 'O', r'\Rho': 'P', r'\Tau': 'T', r'\Chi': 'X'}
ALIAS |= {
    r'\omicron': r'\mitomicron',
    r'\epsilon': r'ϵ',
    r'\superseteq': r'\supseteq',
    r'\superset': r'\supset',
    r'\nsuperseteq': r'\nsupseteq',
    r'\nsuperset': r'\nsupset',
    r'\dots': r'\ldots',
    r'\qed': r'\blacksquare',
    r'\divby': r'\vdots',
}

ALIAS |= {
    r'\not\in': r'\notin',
    r'\not\supseteq': r'\nsupseteq',
    r'\not\supset': r'\nsupset',
    r'\not\superseteq': r'\nsuperseteq',
    r'\not\superset': r'\nsuperset',
    r'\not\subseteq': r'\nsubseteq',
    r'\not\subset': r'\nsubset',
    r'\not\exists': r'\nexists'
}

AUTOACTIVATE.extend(ALIAS.keys())

REPLS = unicodeit.data.REPLACEMENTS
REPLS.remove(('\\not', '\u0338'))
REPLS_DICT = dict(REPLS)
unicodeit_REPLACEMENTS = REPLS.copy()

unicodeit.data.SUBSUPERSCRIPTS += [
    ('^/', '⸍'),
    ('_/', '⸝'),
    ('^\\', '⸌'),
    ('_\\', '⸜')
]

msg_state = {
    'tex': {key: set(value) for key, value in tgpy.api.config.get('tex.set_tex', {}).items()},
    'ntex': {key: set(value) for key, value in tgpy.api.config.get('tex.set_ntex', {}).items()}
}



def reset_replacements():
    global REPLS_DICT
    REPLS.clear()
    REPLS.extend(unicodeit_REPLACEMENTS.copy())
    REPLS_DICT = dict(REPLS)


def add_replacements(aliases):
    for (key, alias) in aliases.items():
        val = REPLS_DICT.get(alias, alias)
        REPLS_DICT[key] = val
    REPLS.clear()
    REPLS.extend(REPLS_DICT.items())
    REPLS.sort(key=lambda el: -len(el[0]))


def add_to_state(chat_id, msg_id, state):
    if state not in msg_state:
        return
    st = msg_state[state]
    if chat_id not in st:
        st[chat_id] = set()
    elif msg_id in st[chat_id]:
        return
    st[chat_id].add(msg_id)
    tgpy.api.config.set(f'tex.set_{state}.{chat_id}', list(st[chat_id]))


def remove_from_state(chat_id, msg_id, state):
    if state not in msg_state:
        return
    st = msg_state[state]
    if chat_id not in st or msg_id not in st[chat_id]:
        return
    st[chat_id].remove(msg_id)
    tgpy.api.config.set(f'tex.set_{state}.{chat_id}', list(st[chat_id]))


def get_state(chat_id, msg_id):
    is_tex = msg_id in msg_state['tex'].get(chat_id, [])
    is_ntex = msg_id in msg_state['ntex'].get(chat_id, [])
    if is_tex and not is_ntex:
        return 'tex'
    if is_ntex and not is_tex:
        return 'ntex'
    return None


async def tex_hook(message=None, is_edit=None):
    text = message.text
    chat_id = str(message.chat_id)
    msg_id = message.id
    if text.startswith(".tex ") or text.startswith(".tex\n"):
        remove_from_state(chat_id, msg_id, 'ntex')
        add_to_state(chat_id, msg_id, 'tex')
        text = text[5:]
    elif text.startswith(".ntex ") or text.startswith(".ntex\n"):
        remove_from_state(chat_id, msg_id, 'tex')
        add_to_state(chat_id, msg_id, 'ntex')
        return await message.edit(text[6:])
    else:
        state = get_state(chat_id, msg_id)
        if state == 'tex':
            pass
        elif state == 'ntex':
            return
        elif not is_autotex():
            return
        else:
            is_code_in_msg = any(
                isinstance(ent, (
                    telethon.tl.types.MessageEntityCode,
                    telethon.tl.types.MessageEntityPre
                )) for ent in (message.entities or [])
            )
            is_tex_text = any(c in text for c in AUTOACTIVATE)
            if not is_tex_text or is_code_in_msg:
                return

    reset_replacements()
    add_replacements(ALIAS)

    text = unicodeit.replace(text)
    if text != message.text:
        return await message.edit(text)


def autotex(flag=True):
    """set auto activation of .tex to `flag`"""
    tgpy.api.config.set('tex.auto_activate', flag)


def is_autotex():
    """get if auto activation of .tex is true"""
    return tgpy.api.config.get('tex.auto_activate', True)


tgpy.api.exec_hooks.add('tex', tex_hook)

__all__ = ['autotex', 'is_autotex']
