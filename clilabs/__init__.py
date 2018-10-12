import inspect
import importlib
import sys


def cli(*argv):
    '''clilabs automates python callables parametered calls.

    Things starting with - will arrive in clilabs.context.

    Examples:

        clilabs help your.mod:funcname to get its docstring.
        clilabs debug your.mod -a --b --something='to see' how it=parses
        clilabs your.mod:funcname with your=args
    '''
    argv = argv if argv else sys.argv
    if len(argv) < 2:
        argv.append('help')

    cb = funcimp(argv[1])
    args, kwargs = expand(*argv[2:])
    return cb(*args, **kwargs)


def funcexpand(callback):
    import clilabs.builtins
    builtins = [
        a[0]
        for a in inspect.getmembers(clilabs.builtins)
        if callable(getattr(clilabs.builtins, a[0]))
    ]

    if callback in builtins:
        funcname = callback
        modname = 'clilabs.builtins'
    elif ':' not in callback:
        funcname = 'main'
        modname = callback
    else:
        modname, funcname = callback.split(':')
        if not modname:
            modname = 'clilabs.builtins'

    return modname, funcname


def modfuncimp(modname, funcname):
    ret = importlib.import_module(modname)
    for part in funcname.split('.'):
        if isinstance(ret, dict) and part in ret:
            ret = ret.get(part)
        elif isinstance(ret, list) and part.isnumeric():
            ret = ret[int(part)]
        else:
            ret = getattr(ret, part)

    return ret


def funcimp(callback):
    return modfuncimp(*funcexpand(callback))


def expand(*argvs):
    args, kwargs = list(), dict()

    for argv in argvs:
        if argv == '-':
            args.append(sys.stdin.read())
            continue

        if argv.startswith('-'):
            continue

        if '=' in argv:
            name, value = argv.split('=')
            if value == '-':
                value = sys.stdin.read()
            kwargs[name] = value
        else:
            args.append(argv)

    return args, kwargs


class Context:
    def __init__(self, *args, **kwargs):
        self.args = list(args)
        self.kwargs = kwargs

    @classmethod
    def factory(cls, argvs):
        context = cls()

        for argv in argvs:
            if not argv.startswith('-'):
                continue

            if argv == '--':
                context.args.append(sys.stdin.read())
                continue

            argv = argv.lstrip('-')

            if '=' in argv:
                key, value = argv.split('=')
                if value == '-':
                    value = sys.stdin.read()
                context.kwargs[key] = value

            else:
                context.args.append(argv)

        return context


context = Context.factory(sys.argv)
