from .bases import Pys
from .buffer import PysCode

class PysObject(Pys):
    pass

class PysModule(PysObject):

    def __init__(self, name, doc=None):
        self.__name__ = name
        self.__doc__ = doc

    def __repr__(self):
        from .singletons import undefined

        file = getattr(self, '__file__', undefined)

        return '<module {!r}{}>'.format(
            self.__name__,
            '' if file is undefined else ' from {!r}'.format(file)
        )

class PysChainFunction(PysObject):

    def __init__(self, func):
        from .constants import DEFAULT

        self.__name__ = func.__name__
        self.__func__ = func
        self.__code__ = PysCode(position=None, context=None, flags=DEFAULT)

    def __repr__(self):
        return '<chain function {}>'.format(self.__name__)

    def __call__(self, *args, **kwargs):
        from .handlers import handle_call

        handle_call(self.__func__, self.__code__.context, self.__code__.position, self.__code__.flags)
        return self.__func__(self, *args, **kwargs)

class PysFunction(PysObject):

    def __init__(self, name, parameters, body, position, context):
        from .constants import DEFAULT

        self.__name__ = '<function>' if name is None else name
        self.__code__ = PysCode(
            parameters=parameters,
            body=body,
            position=position,
            context=context,

            call_context=context,
            flags=DEFAULT,
            prefix='',

            arg_names=tuple(item for item in parameters if not isinstance(item, tuple)),
            kwarg_names=tuple(item[0] for item in parameters if isinstance(item, tuple)),
            names=tuple(item[0] if isinstance(item, tuple) else item for item in parameters),
            kwargs={item[0]: item[1] for item in parameters if isinstance(item, tuple)}
        )

    def __repr__(self):
        return '<function {} at 0x{:016X}>'.format(self.__name__, id(self))

    def __get__(self, instance, owner):
        from types import MethodType

        self.__code__.prefix = owner.__name__ + '.'

        return self if instance is None else MethodType(self, instance)

    def __call__(self, *args, **kwargs):
        from .context import PysContext
        from .exceptions import PysException, PysShouldReturn
        from .interpreter import PysInterpreter
        from .results import PysRunTimeResult
        from .symtab import PysSymbolTable
        from .utils import join_with_conjunction

        result = PysRunTimeResult()

        context = PysContext(
            name=self.__name__,
            file=self.__code__.context.file,
            symbol_table=PysSymbolTable(self.__code__.context.symbol_table),
            parent=self.__code__.call_context,
            parent_entry_position=self.__code__.position
        )

        registered_args = set()

        for name, arg in zip(self.__code__.arg_names, args):
            context.symbol_table.set(name, arg)
            registered_args.add(name)

        combined_kwargs = self.__code__.kwargs | kwargs

        for name, arg in zip(self.__code__.kwarg_names, args[len(registered_args):]):
            context.symbol_table.set(name, arg)
            registered_args.add(name)
            combined_kwargs.pop(name, None)

        for name, value in combined_kwargs.items():

            if name in registered_args:
                raise PysShouldReturn(
                    result.failure(
                        PysException(
                            TypeError(
                                "{}{}() got multiple values for argument {!r}".format(
                                    self.__code__.prefix, self.__name__, name
                                )
                            ),
                            self.__code__.call_context,
                            self.__code__.position
                        )
                    )
                )

            elif name not in self.__code__.names:
                raise PysShouldReturn(
                    result.failure(
                        PysException(
                            TypeError(
                                "{}{}() got an unexpected keyword argument {!r}".format(
                                    self.__code__.prefix, self.__name__, name
                                )
                            ),
                            self.__code__.call_context,
                            self.__code__.position
                        )
                    )
                )

            context.symbol_table.set(name, value)
            registered_args.add(name)

        if len(registered_args) < len(self.__code__.parameters):
            missing_args = [name for name in self.__code__.names if name not in registered_args]
            total_missing = len(missing_args)

            raise PysShouldReturn(
                result.failure(
                    PysException(
                        TypeError(
                            "{}{}() missing {} required positional argument{}: {}".format(
                                self.__code__.prefix,
                                self.__name__,
                                total_missing,
                                '' if total_missing == 1 else 's',
                                join_with_conjunction(missing_args, func=repr, conjunction='and')
                            )
                        ),
                        self.__code__.call_context,
                        self.__code__.position
                    )
                )
            )

        elif len(registered_args) > len(self.__code__.parameters) or len(args) > len(self.__code__.parameters):
            total_args = len(args)
            total_parameter = len(self.__code__.parameters)

            given_args = total_args if total_args > total_parameter else len(registered_args)

            raise PysShouldReturn(
                result.failure(
                    PysException(
                        TypeError(
                            "{}{}() takes no arguments ({} given)".format(
                                self.__code__.prefix, self.__name__, given_args
                            ) if total_parameter == 0 else
                            "{}{}() takes {} positional argument{} but {} were given".format(
                                self.__code__.prefix,
                                self.__name__,
                                total_parameter,
                                '' if total_parameter == 1 else 's',
                                given_args
                            )
                        ),
                        self.__code__.call_context,
                        self.__code__.position
                    )
                )
            )

        interpreter = PysInterpreter(self.__code__.flags)

        result.register(interpreter.visit(self.__code__.body, context))
        if result.should_return() and not result.func_should_return:
            raise PysShouldReturn(result)

        return_value = result.func_return_value

        result.func_should_return = False
        result.func_return_value = None

        return return_value