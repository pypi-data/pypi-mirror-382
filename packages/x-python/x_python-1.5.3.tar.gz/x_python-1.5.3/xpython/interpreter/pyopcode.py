"""
Implementation of a part of the standard Python opcodes.

The rest, dealing with variables in optimized ways, is in nestedscope.py.
"""

from xpython.interpreter.baseobjspace import W_Root


CANNOT_CATCH_MSG = (
    "catching classes that don't inherit from BaseException " "is not allowed in 3.x"
)


def unaryoperation(operationname):
    def opimpl(self, *ignored):
        operation = getattr(self.space, operationname)
        w_1 = self.popvalue()
        w_result = operation(w_1)
        self.pushvalue(w_result)

    opimpl.unaryop = operationname

    return func_with_new_name(opimpl, f"opcode_impl_for_{operationname}")


def binaryoperation(operationname):
    def opimpl(self, *ignored):
        operation = getattr(self.space, operationname)
        w_2 = self.popvalue()
        w_1 = self.popvalue()
        w_result = operation(w_1, w_2)
        self.pushvalue(w_result)

    opimpl.binop = operationname

    return func_with_new_name(opimpl, f"opcode_impl_for_{operationname}")


class ExitFrame(Exception):
    pass


class Return(ExitFrame):
    """Raised when exiting a frame via a 'return' statement."""


class Yield(ExitFrame):
    """Raised when exiting a frame via a 'yield' statement."""


class RaiseWithExplicitTraceback(Exception):
    """Raised at interp-level by a 0-argument 'raise' statement."""

    def __init__(self, operr):
        self.operr = operr


# Frame Blocks


class SuspendedUnroller(W_Root):
    """Abstract base class for interpreter-level objects that
    instruct the interpreter to change the control flow and the
    block stack.

    The concrete subclasses correspond to the various values WHY_XXX
    values of the why_code enumeration in ceval.c:

                WHY_NOT,        OK, not this one :-)
                WHY_EXCEPTION,  SApplicationException
                WHY_RERAISE,    implemented differently, see Reraise
                WHY_RETURN,     SReturnValue
                WHY_BREAK,      SBreakLoop
                WHY_CONTINUE,   SContinueLoop
                WHY_YIELD       not needed
    """

    _immutable_ = True

    def nomoreblocks(self):
        raise BytecodeCorruption("misplaced bytecode - should not return")


class SReturnValue(SuspendedUnroller):
    """Signals a 'return' statement.
    Argument is the wrapped object to return."""

    _immutable_ = True
    kind = 0x01

    def __init__(self, w_returnvalue):
        self.w_returnvalue = w_returnvalue

    def nomoreblocks(self):
        return self.w_returnvalue


class SApplicationException(SuspendedUnroller):
    """Signals an application-level exception
    (i.e. an OperationException)."""

    _immutable_ = True
    kind = 0x02

    def __init__(self, operr):
        self.operr = operr

    def nomoreblocks(self):
        raise RaiseWithExplicitTraceback(self.operr)


class SBreakLoop(SuspendedUnroller):
    """Signals a 'break' statement."""

    _immutable_ = True
    kind = 0x04


SBreakLoop.singleton = SBreakLoop()


class SContinueLoop(SuspendedUnroller):
    """Signals a 'continue' statement.
    Argument is the bytecode position of the beginning of the loop."""

    _immutable_ = True
    kind = 0x08

    def __init__(self, jump_to):
        self.jump_to = jump_to


class FrameBlock(object):
    """Abstract base class for frame blocks from the blockstack,
    used by the SETUP_XXX and POP_BLOCK opcodes."""

    _immutable_ = True

    def __init__(self, valuestackdepth, handlerposition, previous):
        self.handlerposition = handlerposition
        self.valuestackdepth = valuestackdepth
        self.previous = previous  # this makes a linked list of blocks

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.handlerposition == other.handlerposition
            and self.valuestackdepth == other.valuestackdepth
        )

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.handlerposition, self.valuestackdepth))

    def cleanupstack(self, frame):
        frame.dropvaluesuntil(self.valuestackdepth)

    def pop_block(self, frame):
        "Clean up a frame when we normally exit the block."
        self.cleanupstack(frame)

    # internal pickling interface, not using the standard protocol
    def _get_state_(self, space):
        return space.newtuple(
            [
                space.newtext(self._opname),
                space.newint(self.handlerposition),
                space.newint(self.valuestackdepth),
            ]
        )

    def handle(self, frame, unroller):
        """Purely abstract method"""
        raise NotImplementedError


class LoopBlock(FrameBlock):
    """A loop block.  Stores the end-of-loop pointer in case of 'break'."""

    _immutable_ = True
    _opname = "SETUP_LOOP"
    handling_mask = SBreakLoop.kind | SContinueLoop.kind

    def handle(self, frame, unroller):
        if isinstance(unroller, SContinueLoop):
            # re-push the loop block without cleaning up the value stack,
            # and jump to the beginning of the loop, stored in the
            # exception's argument
            frame.append_block(self)
            jumpto = unroller.jump_to
            ec = frame.space.getexecutioncontext()
            return r_uint(frame.jump_absolute(jumpto, ec))
        else:
            # jump to the end of the loop
            self.cleanupstack(frame)
            return r_uint(self.handlerposition)


class SysExcInfoRestorer(FrameBlock):
    """
    This is a special, implicit block type which is created when entering a
    finally or except handler. It does not belong to any opcode
    """

    _immutable_ = True
    _opname = "SYS_EXC_INFO_RESTORER"  # it's not associated to any opcode
    handling_mask = 0  # this block is never handled, only popped by POP_EXCEPT

    def __init__(self, operr, previous):
        self.operr = operr
        self.previous = previous

    def pop_block(self, frame):
        assert False  # never called

    def handle(self, frame, unroller):
        assert False  # never called

    def cleanupstack(self, frame):
        ec = frame.space.getexecutioncontext()
        ec.set_sys_exc_info(self.operr)


class ExceptBlock(FrameBlock):
    """An try:except: block.  Stores the position of the exception handler."""

    _immutable_ = True
    _opname = "SETUP_EXCEPT"
    handling_mask = SApplicationException.kind

    def handle(self, frame, unroller):
        # push the exception to the value stack for inspection by the
        # exception handler (the code after the except:)
        self.cleanupstack(frame)
        # the stack setup is slightly different than in CPython:
        # instead of the traceback, we store the unroller object,
        # wrapped.
        assert isinstance(unroller, SApplicationException)
        operationerr = unroller.operr
        operationerr.normalize_exception(frame.space)
        frame.pushvalue(unroller)
        frame.pushvalue(operationerr.get_w_value(frame.space))
        frame.pushvalue(operationerr.w_type)
        # set the current value of sys_exc_info to operationerr,
        # saving the old value in a custom type of FrameBlock
        frame.save_and_change_sys_exc_info(operationerr)
        return r_uint(self.handlerposition)  # jump to the handler


class FinallyBlock(FrameBlock):
    """A try:finally: block.  Stores the position of the exception handler."""

    _immutable_ = True
    _opname = "SETUP_FINALLY"
    handling_mask = -1  # handles every kind of SuspendedUnroller

    def handle(self, frame, unroller):
        # any abnormal reason for unrolling a finally: triggers the end of
        # the block unrolling and the entering the finally: handler.
        # see comments in cleanup().
        self.cleanupstack(frame)
        operationerr = None
        if isinstance(unroller, SApplicationException):
            operationerr = unroller.operr
            operationerr.normalize_exception(frame.space)
        frame.pushvalue(unroller)
        # set the current value of sys_exc_info to operationerr,
        # saving the old value in a custom type of FrameBlock
        frame.save_and_change_sys_exc_info(operationerr)
        return r_uint(self.handlerposition)  # jump to the handler

    def pop_block(self, frame):
        self.cleanupstack(frame)
        frame.save_and_change_sys_exc_info(None)


block_classes = {
    "SYS_EXC_INFO_RESTORER": SysExcInfoRestorer,
    "SETUP_LOOP": LoopBlock,
    "SETUP_EXCEPT": ExceptBlock,
    "SETUP_FINALLY": FinallyBlock,
    "SETUP_WITH": FinallyBlock,
}


# class W_OperationError(W_Root):
#    """
#    Tiny applevel wrapper around an OperationError.
#    """
#
#    def __init__(self, operr):
#        self.operr = operr
#
#    def descr_reduce(self, space):
#        from pypy.interpreter.mixedmodule import MixedModule
#        w_mod = space.getbuiltinmodule('_pickle_support')
#        mod = space.interp_w(MixedModule, w_mod)
#        w_new_inst = mod.get('operationerror_new')
#        w_args = space.newtuple([])
#        operr = self.operr
#        if operr is None:
#            return space.newtuple([w_new_inst, w_args])
#        w_state = space.newtuple([operr.w_type, operr.get_w_value(space),
#                                  operr.get_traceback()])
#        return space.newtuple([w_new_inst, w_args, w_state])
#
#    def descr_setstate(self, space, w_state):
#        w_type, w_value, w_tb = space.fixedview(w_state, 3)
#        self.operr = OperationError(w_type, w_value, w_tb)


def ensure_ns(space, w_globals, w_locals, funcname, caller=None):
    """Ensure globals/locals exist and are of the correct type"""
    if not space.is_none(w_globals) and not space.isinstance_w(w_globals, space.w_dict):
        raise oefmt(
            space.w_TypeError, "%s() arg 2 must be a dict, not %T", funcname, w_globals
        )
    if not space.is_none(w_locals) and space.lookup(w_locals, "__getitem__") is None:
        raise oefmt(
            space.w_TypeError,
            "%s() arg 3 must be a mapping or None, not %T",
            funcname,
            w_locals,
        )

    if space.is_none(w_globals):
        if caller is None:
            caller = space.getexecutioncontext().gettopframe_nohidden()
        if caller is None:
            w_globals = space.newdict(module=True)
            if space.is_none(w_locals):
                w_locals = w_globals
        else:
            w_globals = caller.get_w_globals()
            if space.is_none(w_locals):
                w_locals = caller.getdictscope()
    elif space.is_none(w_locals):
        w_locals = w_globals

    return w_globals, w_locals
