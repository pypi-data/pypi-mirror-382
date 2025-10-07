import traceback
import sys
from .handle_path import scan_dir, find_in_path
import itertools

original_traceback_TracebackException_init = traceback.TracebackException.__init__

major, minor = sys.version_info[:2]


def _compute_suggestion_error(exc_value, tb, wrong_name):
    if wrong_name is None or not isinstance(wrong_name, str):
        return None
    if isinstance(exc_value, AttributeError):
        obj = exc_value.obj
        try:
            try:
                d = dir(obj)
            except TypeError:  # Attributes are unsortable, e.g. int and str
                d = list(obj.__class__.__dict__.keys()) + list(obj.__dict__.keys())
            d = sorted([x for x in d if isinstance(x, str)])
            hide_underscored = (wrong_name[:1] != '_')
            if hide_underscored and tb is not None:
                while tb.tb_next is not None:
                    tb = tb.tb_next
                frame = tb.tb_frame
                if 'self' in frame.f_locals and frame.f_locals['self'] is obj:
                    hide_underscored = False
            if hide_underscored:
                d = [x for x in d if x[:1] != '_']
        except Exception:
            return None
    elif isinstance(exc_value, ImportError):
        if isinstance(exc_value, ModuleNotFoundError):
            return _handle_module(exc_value)
        try:
            mod = __import__(exc_value.name)
            try:
                d = dir(mod)
            except TypeError:  # Attributes are unsortable, e.g. int and str
                d = list(mod.__dict__.keys())
            d = sorted([x for x in d if isinstance(x, str)])
            if wrong_name[:1] != '_':
                d = [x for x in d if x[:1] != '_']
        except Exception:
            return None
    else:
        assert isinstance(exc_value, NameError)
        # find most recent frame
        if tb is None:
            return None
        while tb.tb_next is not None:
            tb = tb.tb_next
        frame = tb.tb_frame
        d = (
                list(frame.f_locals)
                + list(frame.f_globals)
                + list(frame.f_builtins)
        )
        d = [x for x in d if isinstance(x, str)]

        # Check first if we are in a method and the instance
        # has the wrong name as attribute
        if 'self' in frame.f_locals:
            self = frame.f_locals['self']
            try:
                has_wrong_name = hasattr(self, wrong_name)
            except Exception:
                has_wrong_name = False
            if has_wrong_name:
                return f"self.{wrong_name}"

    suggestion = _calculate_closed_name(wrong_name, d)
    if minor >= 14:
        # If no direct attribute match found, check for nested attributes
        from contextlib import suppress
        from traceback import _check_for_nested_attribute
        if not suggestion and isinstance(exc_value, AttributeError):
            with suppress(Exception):
                nested_suggestion = _check_for_nested_attribute(exc_value.obj, wrong_name, d)
                if nested_suggestion:
                    return nested_suggestion

    return suggestion


try:
    _MAX_STRING_SIZE = traceback._MAX_STRING_SIZE
    _MAX_CANDIDATE_ITEMS = traceback._MAX_CANDIDATE_ITEMS
    _MOVE_COST = traceback._MOVE_COST
    _CASE_COST = traceback._CASE_COST
except:
    _MAX_CANDIDATE_ITEMS = 750
    _MAX_STRING_SIZE = 40
    _MOVE_COST = 2
    _CASE_COST = 1


def _handle_module(exc_value):
    if not isinstance(exc_value, ModuleNotFoundError):
        return None
    return _suggestion_for_module(exc_value.name, original_exc_value=exc_value)


def add_note(exc_value, note):
    if minor >= 11:
        exc_value.add_note(note)
    else:
        if not hasattr(exc_value, "__notes__") or not isinstance(BaseException.__getattribute__(exc_value, "__notes__"), list):
            BaseException.__setattr__(exc_value, "__notes__", [])
        BaseException.__getattribute__(exc_value, "__notes__").append(note)


def _import_error_set(err, result=None, _seen=None):
    if not isinstance(result, set):
        result = set()
    if not isinstance(_seen, set):
        _seen = set()
    if not err or id(err) in _seen:
        return result
    _seen.add(id(err))
    if isinstance(err, ImportError):
        result.add(id(err))
    if minor >= 11 and isinstance(err, BaseExceptionGroup):
        for e in err.exceptions:
            _import_error_set(e, result, _seen)
    if err.__cause__ is not None:
        _import_error_set(err.__cause__, result, _seen)
    if err.__context__ is not None:
        _import_error_set(err.__context__, result, _seen)
    return result


def _copy_BaseExceptionGroup(exca, excb):
    BaseExceptionGroup.__setattr__(exca, "__cause__", BaseExceptionGroup.__getattribute__(excb, "__cause__"))
    BaseExceptionGroup.__setattr__(exca, "__context__", BaseExceptionGroup.__getattribute__(excb, "__context__"))
    BaseExceptionGroup.__setattr__(exca, "__suppress_context__",
                                   BaseExceptionGroup.__getattribute__(excb, "__suppress_context__"))
    BaseExceptionGroup.__setattr__(exca, "__traceback__", BaseExceptionGroup.__getattribute__(excb, "__traceback__"))
    try:
        BaseExceptionGroup.__setattr__(exca, "__notes__", BaseExceptionGroup.__getattribute__(excb, "__notes__"))
    except:
        BaseExceptionGroup.__setattr__(exca, "__notes__", None)

    exca.__dict__.update(excb.__dict__)  # BaseException must have the attribute '__dict__'
    if hasattr(excb, "__slots__"):
        try:
            for i in excb.__slots__:
                try:
                    BaseExceptionGroup.__setattr__(exca, i, getattr(excb, i))
                except:
                    pass
        except:
            pass


def cache_decorator(func):
    cache = {}
    verify = {}

    def wrapper(exc, exceptions):
        key = (id(exc), tuple(id(i) for i in exceptions))
        try:
            if key in cache and key in verify:
                cache_value = verify[key]
                if cache_value[0] is exc and len(cache_value[1]) == len(exceptions):
                    for i, j in zip(cache_value[1], exceptions):
                        if i is not j:
                            break
                    else:
                        return cache[key]
        except:
            pass
        result = func(exc, exceptions)
        cache[key] = result
        verify[key] = (exc, exceptions)
        return result

    return wrapper


@cache_decorator
def creat_BaseExceptionGroup(exc, exceptions):
    try:
        return BaseExceptionGroup.__new__(type(exc),
                                          BaseExceptionGroup.__getattribute__(exc, "message"),
                                          exceptions)
    except:
        return BaseExceptionGroup(BaseExceptionGroup.__getattribute__(exc, "message"),
                                  exceptions)


def _remove_exception(exc_value, other_exc_value, _seen=None):
    if not isinstance(_seen, set):
        _seen = set()
    if id(exc_value) in _seen:
        return False, exc_value, []
    _seen.add(id(exc_value))
    if isinstance(BaseException.__getattribute__(exc_value, "__cause__"), BaseException):
        if BaseException.__getattribute__(exc_value, "__cause__") is other_exc_value:
            BaseException.__setattr__(exc_value, "__cause__", None)
        else:
            result = _remove_exception(BaseException.__getattribute__(exc_value, "__cause__"), other_exc_value, _seen)
            if result[0]:
                BaseException.__setattr__(exc_value, "__cause__",
                                          creat_BaseExceptionGroup(result[1], result[2]))
                _copy_BaseExceptionGroup(BaseException.__getattribute__(exc_value, "__cause__"), result[1])
    if isinstance(BaseException.__getattribute__(exc_value, "__context__"), BaseException):
        if exc_value.__context__ is other_exc_value:
            BaseException.__setattr__(exc_value, "__context__", None)
        else:
            result = _remove_exception(BaseException.__getattribute__(exc_value, "__context__"), other_exc_value, _seen)
            if result[0]:
                BaseException.__setattr__(exc_value, "__context__",
                                          creat_BaseExceptionGroup(result[1], result[2]))
                _copy_BaseExceptionGroup(BaseException.__getattribute__(exc_value, "__context__"), result[1])
    if minor >= 11 and isinstance(exc_value, BaseExceptionGroup):
        new_exceptions = []
        change = False
        for e in exc_value.exceptions:
            if e is not other_exc_value:
                result = _remove_exception(e, other_exc_value, _seen)
                if result[0]:
                    e = creat_BaseExceptionGroup(result[1], result[2])
                    _copy_BaseExceptionGroup(e, result[1])
                    _seen.add(id(e))
                    change = True
                new_exceptions.append(e)
            else:
                change = True

        return change, exc_value, new_exceptions  # BaseExceptionGroup.exceptions is readonly
    else:
        return False, exc_value, []


def _suggestion_for_module(name, mod="normal", original_exc_value=None):
    kwargs = {}
    if mod == "all":
        kwargs = {"namespace_package": True}
    elif mod == "run_module":
        kwargs = {"need_main_py": True}

    all_result = []
    parent, _, child = name.rpartition('.')
    if len(child) > _MAX_STRING_SIZE:
        return None
    suggest_list = []
    for i in sys.meta_path:
        if isinstance(i, type):
            iname = i.__name__
            imodule = i.__module__
        else:
            iname = type(i).__name__
            imodule = type(i).__module__
        try:
            func = getattr(i, '__find__', None)
            if callable(func):
                list_d = func(parent)
                if child in list_d:
                    if original_exc_value:
                        add_note(original_exc_value,
                                 f"The child name found in '{iname}.__find__' "
                                 "but it cannot imported by it. "
                                 "Please check it. \n"
                                 f"{iname!r} is in module {imodule!r}")
                    return child
                if list_d:
                    suggest_list.append(list_d)
        except:
            if original_exc_value:
                try:
                    new_type, new_value, new_tb = sys.exc_info()
                    _remove_exception(new_value,
                                      original_exc_value)  # avoid to analyse the original ModuleNotFoundError
                    import_error_set = _import_error_set(new_value)
                    if import_error_set:
                        frames = []
                        for frame, lineno in traceback.walk_tb(new_tb):
                            if "idlelib" not in frame.f_code.co_filename and "friendly_module_not_found_error" not in frame.f_code.co_filename:
                                frames.append(traceback.FrameSummary(frame.f_code.co_filename,
                                                                     lineno,
                                                                     frame.f_code.co_name))
                        add_note(original_exc_value, f"\nImportError found in '{iname}.__find__' module {imodule!r}:")
                        add_note(original_exc_value, "".join(traceback.format_list(frames)))
                        add_note(original_exc_value, "Don't import any modules in the method '__find__'")
                        continue
                    tb_exception = traceback.TracebackException(new_type, new_value, new_tb)
                    add_note(original_exc_value, f"\nException ignored in '{iname}.__find__' module {imodule!r}:\n"
                             + "".join(tb_exception.format()))
                except:
                    add_note(original_exc_value, "\n<handle error failed in '{iname}.__find__' module {imodule!r}>\n")

    if not parent:
        for paths in sys.path:
            suggest_list.append(scan_dir(paths, **kwargs))
    else:
        suggest_list.append(find_in_path(parent, mod=mod))
    for i in suggest_list:
        if child in i:
            return child
        result = _calculate_closed_name(child, i)
        if result:
            all_result.append(result)
    return _calculate_closed_name(child, sorted(all_result))


def _find_wrong_hook(name):
    parent, _, child = name.rpartition('.')
    for i in sys.meta_path:
        try:
            func = getattr(i, '__find__', None)
            if callable(func):
                list_d = func(parent)
                if child in list_d:
                    return i
        except:
            pass
    return None


try:
    _levenshtein_distance = traceback._levenshtein_distance
except Exception:
    def _levenshtein_distance(a, b, max_cost):
        # A Python implementation of Python/suggestions.c:levenshtein_distance.

        # Both strings are the same
        if a == b:
            return 0

        # Trim away common affixes
        pre = 0
        while a[pre:] and b[pre:] and a[pre] == b[pre]:
            pre += 1
        a = a[pre:]
        b = b[pre:]
        post = 0
        while a[:post or None] and b[:post or None] and a[post - 1] == b[post - 1]:
            post -= 1
        a = a[:post or None]
        b = b[:post or None]
        if not a or not b:
            return _MOVE_COST * (len(a) + len(b))
        if len(a) > _MAX_STRING_SIZE or len(b) > _MAX_STRING_SIZE:
            return max_cost + 1

        # Prefer shorter buffer
        if len(b) < len(a):
            a, b = b, a

        # Quick fail when a match is impossible
        if (len(b) - len(a)) * _MOVE_COST > max_cost:
            return max_cost + 1

        # Instead of producing the whole traditional len(a)-by-len(b)
        # matrix, we can update just one row in place.
        # Initialize the buffer row
        row = list(range(_MOVE_COST, _MOVE_COST * (len(a) + 1), _MOVE_COST))

        result = 0
        for bindex in range(len(b)):
            bchar = b[bindex]
            distance = result = bindex * _MOVE_COST
            minimum = sys.maxsize
            for index in range(len(a)):
                # 1) Previous distance in this row is cost(b[:b_index], a[:index])
                substitute = distance + _substitution_cost(bchar, a[index])
                # 2) cost(b[:b_index], a[:index+1]) from previous row
                distance = row[index]
                # 3) existing result is cost(b[:b_index+1], a[index])

                insert_delete = min(result, distance) + _MOVE_COST
                result = min(insert_delete, substitute)

                # cost(b[:b_index+1], a[:index+1])
                row[index] = result
                if result < minimum:
                    minimum = result
            if minimum > max_cost:
                # Everything in this row is too big, so bail early.
                return max_cost + 1
        return result


    def _substitution_cost(ch_a, ch_b):
        if ch_a == ch_b:
            return 0
        if ch_a.lower() == ch_b.lower():
            return _CASE_COST
        return _MOVE_COST


def _calculate_closed_name(wrong_name, d):
    try:
        import _suggestions  # type: ignore
    except ImportError:
        pass
    else:
        result = _suggestions._generate_suggestions(d, wrong_name)
        if result:
            return result

    # Compute the closest match

    if len(d) > _MAX_CANDIDATE_ITEMS:
        return None
    wrong_name_len = len(wrong_name)
    if wrong_name_len > _MAX_STRING_SIZE:
        return None
    best_distance = wrong_name_len
    suggestion = None
    for possible_name in d:
        if possible_name == wrong_name:
            # A missing attribute is "found". Don't suggest it (see GH-88821).
            continue
        # No more than 1/3 of the involved characters should need changed.
        max_distance = (len(possible_name) + wrong_name_len + 3) * _MOVE_COST // 6
        # Don't take matches we've already beaten.
        max_distance = min(max_distance, best_distance - 1)
        current_distance = _levenshtein_distance(wrong_name, possible_name, max_distance)
        if current_distance > max_distance:
            continue
        if not suggestion or current_distance < best_distance:
            suggestion = possible_name
            best_distance = current_distance
    return suggestion


StackSummary = traceback.StackSummary
try:
    _walk_tb_with_full_positions = traceback._walk_tb_with_full_positions
except:
    walk_tb = traceback.walk_tb


    def _walk_tb_with_full_positions(tb):
        # Internal version of walk_tb that yields full code positions including
        # end line and column information.
        while tb is not None:
            positions = _get_code_position(tb.tb_frame.f_code, tb.tb_lasti)
            # Yield tb_lineno when co_positions does not have a line number to
            # maintain behavior with walk_tb.
            if positions[0] is None:
                yield tb.tb_frame, (tb.tb_lineno,) + positions[1:]
            else:
                yield tb.tb_frame, positions
            tb = tb.tb_next


    def _get_code_position(code, instruction_index):
        if instruction_index < 0:
            return None, None, None, None
        positions_gen = code.co_positions()
        return next(itertools.islice(positions_gen, instruction_index // 2, None))

try:
    _safe_string = traceback._safe_string
except:
    def _safe_string(value, what, func=str):
        try:
            return func(value)
        except:
            return f'<{what} {func.__name__}() failed>'

TracebackException = traceback.TracebackException


def handle_except(self, exc_type, exc_value, exc_traceback):
    if exc_type and issubclass(exc_type, ModuleNotFoundError) and \
            getattr(exc_value, "name", None) and \
            "None in sys.modules" not in self._str and \
            "is not a package" not in self._str:
        wrong_name = getattr(exc_value, "name", None)
        parent, _, child = wrong_name.rpartition('.')
        suggestion = _compute_suggestion_error(exc_value, exc_traceback, wrong_name)
        if suggestion == child:
            wrong_hook = _find_wrong_hook(wrong_name)
            if wrong_hook is not None:
                if isinstance(wrong_hook, type):
                    wrong_hook_name = wrong_hook.__name__
                else:
                    wrong_hook_name = type(wrong_hook).__name__
                self._str += (f", but it appear in the final result from '{wrong_hook_name}.__find__'. "
                              f"Is the code in '{wrong_hook_name}.__find__' or '{wrong_hook_name}.find_spec' wrong "
                              "or is the wrong in the environment?")
        elif suggestion:
            self._str += f". Did you mean: '{suggestion}'?"
        if minor >= 14:
            top = wrong_name.partition('.')[0]
            if sys.flags.no_site and not parent and top not in sys.stdlib_module_names:
                if not self._str.endswith('?'):
                    self._str += "."
                self._str += (" Site initialization is disabled, did you forget to "
                              + "add the site-packages directory to sys.path?")
    elif exc_type and issubclass(exc_type, ImportError) and \
            getattr(exc_value, "name_from", None) is not None:
        wrong_name = getattr(exc_value, "name_from", None)
        suggestion = _compute_suggestion_error(exc_value, exc_traceback, wrong_name)
        if suggestion:
            self._str += f". Did you mean: '{suggestion}'?"
    elif exc_type and issubclass(exc_type, (NameError, AttributeError)) and \
            getattr(exc_value, "name", None) is not None:
        wrong_name = getattr(exc_value, "name", None)
        suggestion = _compute_suggestion_error(exc_value, exc_traceback, wrong_name)
        if suggestion:
            self._str += f". Did you mean: '{suggestion}'?"
        if issubclass(exc_type, NameError):
            wrong_name = getattr(exc_value, "name", None)
            if wrong_name is not None and wrong_name in sys.stdlib_module_names:
                if suggestion:
                    self._str += f" Or did you forget to import '{wrong_name}'?"
                else:
                    self._str += f". Did you forget to import '{wrong_name}'?"


def remove_stack(tb_exception):
    frames = [frame for frame in tb_exception.stack
              if "friendly_module_not_found_error" not in frame.filename]

    tb_exception.stack = traceback.StackSummary.from_list(frames)


def _extract_stack_and_str(exc_value, exc_traceback,
                           limit, lookup_lines, capture_locals,
                           use_extended=False, safe_str=False):
    if use_extended:
        stack = StackSummary._extract_from_extended_frame_gen(
            _walk_tb_with_full_positions(exc_traceback),
            limit=limit, lookup_lines=lookup_lines,
            capture_locals=capture_locals)
    else:
        stack = StackSummary.extract(
            walk_tb(exc_traceback), limit=limit, lookup_lines=lookup_lines,
            capture_locals=capture_locals)

    if safe_str:
        _str = _safe_string(exc_value, 'exception')
    else:
        _str = traceback._some_str(exc_value)
    return stack, _str


def _handle_syntax_error_fields_common(self, exc_type, exc_value):
    if exc_type and issubclass(exc_type, SyntaxError):
        self.filename = exc_value.filename
        lno = exc_value.lineno
        self.lineno = str(lno) if lno is not None else None
        if hasattr(exc_value, "end_lineno"):
            end_lno = exc_value.end_lineno
            self.end_lineno = str(end_lno) if end_lno is not None else None
        self.text = exc_value.text
        self.offset = exc_value.offset
        if hasattr(exc_value, "end_offset"):
            self.end_offset = exc_value.end_offset
        self.msg = exc_value.msg
        self._is_syntax_error = True
        return True
    self._is_syntax_error = False
    return False


def _init_v7(self, exc_type, exc_value, exc_traceback, *,
             limit=None, lookup_lines=True, capture_locals=False, _seen=None):
    if _seen is None:
        _seen = set()
    _seen.add(id(exc_value))

    if (exc_value and exc_value.__cause__ is not None
            and id(exc_value.__cause__) not in _seen):
        cause = TracebackException(
            type(exc_value.__cause__),
            exc_value.__cause__,
            exc_value.__cause__.__traceback__,
            limit=limit,
            lookup_lines=False,
            capture_locals=capture_locals,
            _seen=_seen)
    else:
        cause = None

    if (exc_value and exc_value.__context__ is not None
            and id(exc_value.__context__) not in _seen):
        context = TracebackException(
            type(exc_value.__context__),
            exc_value.__context__,
            exc_value.__context__.__traceback__,
            limit=limit,
            lookup_lines=False,
            capture_locals=capture_locals,
            _seen=_seen)
    else:
        context = None

    self.exc_traceback = exc_traceback
    self.__cause__ = cause
    self.__context__ = context
    self.__suppress_context__ = exc_value.__suppress_context__ if exc_value else False

    self.stack, self._str = _extract_stack_and_str(exc_value, exc_traceback,
                                                   limit, lookup_lines, capture_locals,
                                                   use_extended=False, safe_str=False)

    self.exc_type = exc_type

    if not _handle_syntax_error_fields_common(self, exc_type, exc_value):
        handle_except(self, exc_type, exc_value, exc_traceback)
    self.__notes__ = getattr(exc_value, "__notes__", None)
    if lookup_lines:
        self._load_lines()
    remove_stack(self)


def _init_v8(self, exc_type, exc_value, exc_traceback, *,
             limit=None, lookup_lines=True, capture_locals=False, _seen=None):
    if _seen is None:
        _seen = set()
    _seen.add(id(exc_value))

    if (exc_value and exc_value.__cause__ is not None
            and id(exc_value.__cause__) not in _seen):
        cause = TracebackException(
            type(exc_value.__cause__),
            exc_value.__cause__,
            exc_value.__cause__.__traceback__,
            limit=limit,
            lookup_lines=False,
            capture_locals=capture_locals,
            _seen=_seen)
    else:
        cause = None

    if (exc_value and exc_value.__context__ is not None
            and id(exc_value.__context__) not in _seen):
        context = TracebackException(
            type(exc_value.__context__),
            exc_value.__context__,
            exc_value.__context__.__traceback__,
            limit=limit,
            lookup_lines=False,
            capture_locals=capture_locals,
            _seen=_seen)
    else:
        context = None

    self.__cause__ = cause
    self.__context__ = context
    self.__suppress_context__ = exc_value.__suppress_context__ if exc_value else False

    self.stack, self._str = _extract_stack_and_str(exc_value, exc_traceback,
                                                   limit, lookup_lines, capture_locals,
                                                   use_extended=False, safe_str=False)
    self.exc_type = exc_type

    if not _handle_syntax_error_fields_common(self, exc_type, exc_value):
        handle_except(self, exc_type, exc_value, exc_traceback)
    self.__notes__ = getattr(exc_value, "__notes__", None)
    if lookup_lines:
        self._load_lines()
    remove_stack(self)


def _init_v9(self, exc_type, exc_value, exc_traceback, *,
             limit=None, lookup_lines=True, capture_locals=False, _seen=None):
    if _seen is None:
        _seen = set()
    _seen.add(id(exc_value))
    self._truncated = False
    try:
        if (exc_value and exc_value.__cause__ is not None
                and id(exc_value.__cause__) not in _seen):
            cause = TracebackException(
                type(exc_value.__cause__),
                exc_value.__cause__,
                exc_value.__cause__.__traceback__,
                limit=limit,
                lookup_lines=False,
                capture_locals=capture_locals,
                _seen=_seen)
        else:
            cause = None
        if (exc_value and exc_value.__context__ is not None
                and id(exc_value.__context__) not in _seen):
            context = TracebackException(
                type(exc_value.__context__),
                exc_value.__context__,
                exc_value.__context__.__traceback__,
                limit=limit,
                lookup_lines=False,
                capture_locals=capture_locals,
                _seen=_seen)
        else:
            context = None
    except RecursionError:
        self._truncated = True
        cause = None
        context = None

    self.__cause__ = cause
    self.__context__ = context
    self.__suppress_context__ = exc_value.__suppress_context__ if exc_value else False

    self.stack, self._str = _extract_stack_and_str(exc_value, exc_traceback,
                                                   limit, lookup_lines, capture_locals,
                                                   use_extended=False, safe_str=False)
    self.exc_type = exc_type

    if not _handle_syntax_error_fields_common(self, exc_type, exc_value):
        handle_except(self, exc_type, exc_value, exc_traceback)
    self.__notes__ = getattr(exc_value, "__notes__", None)
    if lookup_lines:
        self._load_lines()
    remove_stack(self)


def _init_v10(self, exc_type, exc_value, exc_traceback, *,
              limit=None, lookup_lines=True, capture_locals=False, compact=False, _seen=None):
    is_recursive_call = _seen is not None
    if _seen is None:
        _seen = set()
    _seen.add(id(exc_value))

    self.stack, self._str = _extract_stack_and_str(exc_value, exc_traceback,
                                                   limit, lookup_lines, capture_locals,
                                                   use_extended=False, safe_str=False)
    self.exc_type = exc_type

    if not _handle_syntax_error_fields_common(self, exc_type, exc_value):
        handle_except(self, exc_type, exc_value, exc_traceback)

    self.__notes__ = getattr(exc_value, "__notes__", None)

    if lookup_lines:
        self._load_lines()

    self.__suppress_context__ = exc_value.__suppress_context__ if exc_value else False

    if not is_recursive_call:
        queue = [(self, exc_value)]
        while queue:
            te, e = queue.pop()
            if (e and e.__cause__ is not None
                    and id(e.__cause__) not in _seen):
                cause = TracebackException(
                    type(e.__cause__),
                    e.__cause__,
                    e.__cause__.__traceback__,
                    limit=limit,
                    lookup_lines=lookup_lines,
                    capture_locals=capture_locals,
                    _seen=_seen)
            else:
                cause = None

            if compact:
                need_context = (cause is None and e is not None and not e.__suppress_context__)
            else:
                need_context = True

            if (e and e.__context__ is not None
                    and need_context and id(e.__context__) not in _seen):
                context = TracebackException(
                    type(e.__context__),
                    e.__context__,
                    e.__context__.__traceback__,
                    limit=limit,
                    lookup_lines=lookup_lines,
                    capture_locals=capture_locals,
                    _seen=_seen)
            else:
                context = None

            te.__cause__ = cause
            te.__context__ = context
            if cause:
                queue.append((te.__cause__, e.__cause__))
            if context:
                queue.append((te.__context__, e.__context__))
    remove_stack(self)


def _init_v11(self, exc_type, exc_value, exc_traceback, *,
              limit=None, lookup_lines=True, capture_locals=False,
              compact=False, max_group_width=15, max_group_depth=10, _seen=None):
    is_recursive_call = _seen is not None
    if _seen is None:
        _seen = set()
    _seen.add(id(exc_value))

    self.max_group_width = max_group_width
    self.max_group_depth = max_group_depth

    self.stack, self._str = _extract_stack_and_str(exc_value, exc_traceback,
                                                   limit, lookup_lines, capture_locals,
                                                   use_extended=True, safe_str=True)

    self.exc_type = exc_type
    if not _handle_syntax_error_fields_common(self, exc_type, exc_value):
        handle_except(self, exc_type, exc_value, exc_traceback)

    self.__notes__ = getattr(exc_value, '__notes__', None)

    if lookup_lines:
        self._load_lines()

    self.__suppress_context__ = exc_value.__suppress_context__ if exc_value is not None else False

    if not is_recursive_call:
        queue = [(self, exc_value)]
        while queue:
            te, e = queue.pop()

            if (e and e.__cause__ is not None
                    and id(e.__cause__) not in _seen):
                cause = TracebackException(
                    type(e.__cause__),
                    e.__cause__,
                    e.__cause__.__traceback__,
                    limit=limit,
                    lookup_lines=lookup_lines,
                    capture_locals=capture_locals,
                    max_group_width=max_group_width, max_group_depth=max_group_depth,
                    _seen=_seen)
            else:
                cause = None

            if compact:
                need_context = (cause is None and e is not None and not e.__suppress_context__)
            else:
                need_context = True

            if (e and e.__context__ is not None
                    and need_context and id(e.__context__) not in _seen):
                context = TracebackException(
                    type(e.__context__),
                    e.__context__,
                    e.__context__.__traceback__,
                    limit=limit,
                    lookup_lines=lookup_lines,
                    capture_locals=capture_locals,
                    max_group_width=max_group_width, max_group_depth=max_group_depth,
                    _seen=_seen)
            else:
                context = None

            if e and isinstance(e, BaseExceptionGroup):
                exceptions = []
                for exc in e.exceptions:
                    texc = TracebackException(
                        type(exc),
                        exc,
                        exc.__traceback__,
                        limit=limit,
                        lookup_lines=lookup_lines,
                        capture_locals=capture_locals,
                        max_group_width=max_group_width, max_group_depth=max_group_depth,
                        _seen=_seen)
                    exceptions.append(texc)
            else:
                exceptions = None

            te.__cause__ = cause
            te.__context__ = context
            te.exceptions = exceptions

            if cause:
                queue.append((te.__cause__, e.__cause__))
            if context:
                queue.append((te.__context__, e.__context__))
            if exceptions:
                queue.extend(zip(te.exceptions, e.exceptions))
    remove_stack(self)


def _init_v12(self, exc_type, exc_value, exc_traceback, *,
              limit=None, lookup_lines=True, capture_locals=False,
              compact=False, max_group_width=15, max_group_depth=10, _seen=None):
    is_recursive_call = _seen is not None
    if _seen is None:
        _seen = set()
    _seen.add(id(exc_value))

    self.max_group_width = max_group_width
    self.max_group_depth = max_group_depth

    self.stack, self._str = _extract_stack_and_str(exc_value, exc_traceback,
                                                   limit, lookup_lines, capture_locals,
                                                   use_extended=True, safe_str=True)

    self.exc_type = exc_type
    if not _handle_syntax_error_fields_common(self, exc_type, exc_value):
        handle_except(self, exc_type, exc_value, exc_traceback)

    try:
        self.__notes__ = getattr(exc_value, '__notes__', None)
    except Exception as e:
        __notes__ = "__notes__"
        self.__notes__ = [f'Ignored error getting __notes__: {_safe_string(e, __notes__, repr)}']

    if lookup_lines:
        self._load_lines()

    self.__suppress_context__ = exc_value.__suppress_context__ if exc_value is not None else False

    if not is_recursive_call:
        queue = [(self, exc_value)]
        while queue:
            te, e = queue.pop()

            if (e and e.__cause__ is not None
                    and id(e.__cause__) not in _seen):
                cause = TracebackException(
                    type(e.__cause__),
                    e.__cause__,
                    e.__cause__.__traceback__,
                    limit=limit,
                    lookup_lines=lookup_lines,
                    capture_locals=capture_locals,
                    max_group_width=max_group_width, max_group_depth=max_group_depth,
                    _seen=_seen)
            else:
                cause = None

            if compact:
                need_context = (cause is None and e is not None and not e.__suppress_context__)
            else:
                need_context = True

            if (e and e.__context__ is not None
                    and need_context and id(e.__context__) not in _seen):
                context = TracebackException(
                    type(e.__context__),
                    e.__context__,
                    e.__context__.__traceback__,
                    limit=limit,
                    lookup_lines=lookup_lines,
                    capture_locals=capture_locals,
                    max_group_width=max_group_width, max_group_depth=max_group_depth,
                    _seen=_seen)
            else:
                context = None

            if e and isinstance(e, BaseExceptionGroup):
                exceptions = []
                for exc in e.exceptions:
                    texc = TracebackException(
                        type(exc),
                        exc,
                        exc.__traceback__,
                        limit=limit,
                        lookup_lines=lookup_lines,
                        capture_locals=capture_locals,
                        max_group_width=max_group_width, max_group_depth=max_group_depth,
                        _seen=_seen)
                    exceptions.append(texc)
            else:
                exceptions = None

            te.__cause__ = cause
            te.__context__ = context
            te.exceptions = exceptions

            if cause:
                queue.append((te.__cause__, e.__cause__))
            if context:
                queue.append((te.__context__, e.__context__))
            if exceptions:
                queue.extend(zip(te.exceptions, e.exceptions))
    remove_stack(self)


def _init_v13(self, exc_type, exc_value, exc_traceback, *,
              limit=None, lookup_lines=True, capture_locals=False,
              compact=False, max_group_width=15, max_group_depth=10,
              save_exc_type=True, _seen=None):
    is_recursive_call = _seen is not None
    if _seen is None:
        _seen = set()
    _seen.add(id(exc_value))

    self.max_group_width = max_group_width
    self.max_group_depth = max_group_depth

    self.stack, self._str = _extract_stack_and_str(exc_value, exc_traceback,
                                                   limit, lookup_lines, capture_locals,
                                                   use_extended=True, safe_str=True)

    self._exc_type = exc_type if save_exc_type else None
    self._have_exc_type = exc_type is not None
    if exc_type is not None:
        self.exc_type_qualname = exc_type.__qualname__
        self.exc_type_module = exc_type.__module__
    else:
        self.exc_type_qualname = None
        self.exc_type_module = None

    if not _handle_syntax_error_fields_common(self, exc_type, exc_value):
        handle_except(self, exc_type, exc_value, exc_traceback)

    try:
        self.__notes__ = getattr(exc_value, "__notes__", None)
    except Exception as e:
        __notes__ = "__notes__"
        self.__notes__ = [f'Ignored error getting __notes__: {_safe_string(e, __notes__, repr)}']

    if lookup_lines:
        self._load_lines()

    self.__suppress_context__ = exc_value.__suppress_context__ if exc_value is not None else False

    if not is_recursive_call:
        queue = [(self, exc_value)]
        while queue:
            te, e = queue.pop()

            if (e is not None and e.__cause__ is not None
                    and id(e.__cause__) not in _seen):
                cause = TracebackException(
                    type(e.__cause__),
                    e.__cause__,
                    e.__cause__.__traceback__,
                    limit=limit,
                    lookup_lines=lookup_lines,
                    capture_locals=capture_locals,
                    max_group_width=max_group_width, max_group_depth=max_group_depth,
                    _seen=_seen)
            else:
                cause = None

            if compact:
                need_context = (cause is None and e is not None and not e.__suppress_context__)
            else:
                need_context = True

            if (e is not None and e.__context__ is not None
                    and need_context and id(e.__context__) not in _seen):
                context = TracebackException(
                    type(e.__context__),
                    e.__context__,
                    e.__context__.__traceback__,
                    limit=limit,
                    lookup_lines=lookup_lines,
                    capture_locals=capture_locals,
                    max_group_width=max_group_width, max_group_depth=max_group_depth,
                    _seen=_seen)
            else:
                context = None

            if e is not None and isinstance(e, BaseExceptionGroup):
                exceptions = []
                for exc in e.exceptions:
                    texc = TracebackException(
                        type(exc),
                        exc,
                        exc.__traceback__,
                        limit=limit,
                        lookup_lines=lookup_lines,
                        capture_locals=capture_locals,
                        max_group_width=max_group_width, max_group_depth=max_group_depth,
                        _seen=_seen)
                    exceptions.append(texc)
            else:
                exceptions = None

            te.__cause__ = cause
            te.__context__ = context
            te.exceptions = exceptions

            if cause:
                queue.append((te.__cause__, e.__cause__))
            if context:
                queue.append((te.__context__, e.__context__))
            if exceptions:
                queue.extend(zip(te.exceptions, e.exceptions))
    remove_stack(self)


def _init_v14_plus(self, *args, **kwargs):
    _init_v13(self, *args, **kwargs)
    if getattr(self, "_is_syntax_error", False):
        exc_value = args[1] if len(args) > 1 else kwargs.get('exc_value', None)
        self._exc_metadata = getattr(exc_value, "_metadata", None)


_version_map = {
    7: _init_v7,
    8: _init_v8,
    9: _init_v9,
    10: _init_v10,
    11: _init_v11,
    12: _init_v12,
    13: _init_v13,
}
new_init = _version_map.get(minor, _init_v14_plus if minor >= 14 else traceback.TracebackException.__init__)
traceback.TracebackException.__init__ = new_init
original_TracebackException_format_exception_only = traceback.TracebackException.format_exception_only

if minor <= 10:
    import collections.abc


    def new_format_exception_ony(self, *, _depth=0):
        yield from original_TracebackException_format_exception_only(self)
        if hasattr(self, '__notes__'):
            indent = 3 * _depth * ' '
            if (
                    isinstance(self.__notes__, collections.abc.Sequence)
                    and not isinstance(self.__notes__, (str, bytes))
            ):
                for note in self.__notes__:
                    note = _safe_string(note, 'note')
                    yield from [indent + l + '\n' for l in note.split('\n')]
            elif self.__notes__ is not None:
                yield indent + "{}\n".format(_safe_string(self.__notes__, '__notes__', func=repr))


    traceback.TracebackException.format_exception_only = new_format_exception_ony
else:
    new_format_exception_ony = traceback.TracebackException.format_exception_only
