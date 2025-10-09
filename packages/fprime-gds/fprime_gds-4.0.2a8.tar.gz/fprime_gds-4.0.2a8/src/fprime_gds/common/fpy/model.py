from __future__ import annotations
from enum import Enum
import inspect
import math
import struct
import typing
from fprime_gds.common.fpy.bytecode.directives import (
    AllocateDirective,
    AndDirective,
    ConstCmdDirective,
    Directive,
    ExitDirective,
    FloatAddDirective,
    FloatDivideDirective,
    FloatExponentDirective,
    FloatFloorDivideDirective,
    FloatModuloDirective,
    FloatMultiplyDirective,
    FloatSubtractDirective,
    GotoDirective,
    MemCompareDirective,
    SignedIntDivideDirective,
    SignedModuloDirective,
    UnsignedIntDivideDirective,
    IntMultiplyDirective,
    FloatLogDirective,
    DiscardDirective,
    StackCmdDirective,
    StorePrmDirective,
    StoreTlmValDirective,
    IfDirective,
    IntAddDirective,
    IntEqualDirective,
    IntNotEqualDirective,
    IntSubtractDirective,
    LoadDirective,
    NoOpDirective,
    NotDirective,
    OrDirective,
    PushValDirective,
    StoreDirective,
    UnsignedLessThanDirective,
    UnsignedLessThanOrEqualDirective,
    UnsignedGreaterThanDirective,
    UnsignedGreaterThanOrEqualDirective,
    SignedGreaterThanDirective,
    SignedGreaterThanOrEqualDirective,
    SignedIntToFloatDirective,
    SignedLessThanDirective,
    SignedLessThanOrEqualDirective,
    UnsignedIntToFloatDirective,
    FloatEqualDirective,
    FloatExtendDirective,
    FloatGreaterThanDirective,
    FloatGreaterThanOrEqualDirective,
    FloatLessThanDirective,
    FloatLessThanOrEqualDirective,
    FloatNotEqualDirective,
    FloatToSignedIntDirective,
    FloatToUnsignedIntDirective,
    FloatTruncateDirective,
    UnsignedModuloDirective,
    WaitAbsDirective,
    WaitRelDirective,
    IntegerZeroExtend16To64Directive,
    IntegerZeroExtend32To64Directive,
    IntegerZeroExtend8To64Directive,
    IntegerSignedExtend16To64Directive,
    IntegerSignedExtend32To64Directive,
    IntegerSignedExtend8To64Directive,
    IntegerTruncate64To16Directive,
    IntegerTruncate64To32Directive,
    IntegerTruncate64To8Directive,
)
from fprime_gds.common.templates.cmd_template import CmdTemplate
from fprime.common.models.serialize.type_base import BaseType

debug = True

WORD_SIZE = 8
# store return addr and prev stack frame offset in stack frame header
STACK_FRAME_HEADER_SIZE = 2 * WORD_SIZE
MAX_INT64 = 2**63 - 1
MIN_INT64 = -(2**63)
MASK_64_BIT = 2**64 - 1


def overflow_check(val: int) -> int:
    masked_val = val & MASK_64_BIT
    if masked_val > MAX_INT64:
        return masked_val - 2**64
    return masked_val


class DirectiveErrorCode(Enum):
    NO_ERROR = 0
    DIR_OUT_OF_BOUNDS = 1
    TLM_GET_NOT_CONNECTED = 2
    TLM_NOT_FOUND = 3
    TLM_ACCESS_OUT_OF_BOUNDS = 4
    PRM_GET_NOT_CONNECTED = 5
    PRM_NOT_FOUND = 6
    PRM_ACCESS_OUT_OF_BOUNDS = 7
    CMD_SERIALIZE_FAILURE = 8
    DELIBERATE_FAILURE = 9
    STACK_OVERFLOW = 10
    STACK_UNDERFLOW = 11
    INVALID_ARGUMENT = 12
    DIVIDE_BY_ZERO = 13


class FpySequencerModel:

    def __init__(
        self, stack_size=4096, cmd_dict: dict[int, CmdTemplate] = None
    ) -> None:
        self.stack = bytearray()
        self.max_stack_size = stack_size
        self.stack_frame_start = 0
        self.cmd_dict = cmd_dict

        self.dirs: list[Directive] = None
        self.next_dir_idx = 0
        self.tlm_db: dict[int, bytearray] = {}
        self.prm_db: dict[int, bytearray] = {}

    def reset(self):
        self.stack = bytearray()
        self.stack_frame_start = 0

        self.dirs: list[Directive] = None
        self.next_dir_idx = 0
        self.tlm_db: dict[int, bytearray] = {}
        self.prm_db: dict[int, bytearray] = {}

    def dispatch(self, dir: Directive) -> DirectiveErrorCode:
        opcode = dir.opcode
        opcode_name = opcode.name

        handler_fn = None
        for name, func in inspect.getmembers(type(self), inspect.isfunction):
            if not name.startswith("handle"):
                # not a dir handler
                continue
            signature = inspect.signature(func)
            params = list(signature.parameters.values())
            assert len(params) == 2
            assert params[1].annotation is not None
            annotations = typing.get_type_hints(func)
            param_type = annotations[params[1].name]
            if isinstance(dir, param_type):
                handler_fn = func
                break

        if handler_fn is None:
            raise NotImplementedError(opcode_name + " not implemented")

        # otherwise call the handler
        ret = handler_fn(self, dir)
        if ret is None:
            return DirectiveErrorCode.NO_ERROR
        return ret

    def run(self, dirs: list[Directive], tlm: dict[int, bytearray] = None):
        if tlm is None:
            tlm = {}
        self.reset()
        self.dirs = dirs
        self.tlm_db = tlm
        if debug:
            # begin the sequence at dir 0
            print("stack", len(self.stack))
            for byte in range(0, len(self.stack)):

                print(
                    type(self.stack[byte]),
                    end=" ",
                )
            print()
        while self.next_dir_idx < len(self.dirs):
            next_dir = self.dirs[self.next_dir_idx]
            if debug:
                print(f"{self.next_dir_idx}:", next_dir)
            self.next_dir_idx += 1
            result = self.dispatch(next_dir)
            if result != DirectiveErrorCode.NO_ERROR:
                return result
            if debug:
                print("stack", len(self.stack))
                for byte in range(0, len(self.stack)):

                    print(
                        self.stack[byte],
                        end=" ",
                    )
                print()
        return DirectiveErrorCode.NO_ERROR

    def get_int_fmt_str(self, size: int, signed: bool) -> str:
        fmt_char = None
        if size == 1:
            fmt_char = "b"
        elif size == 2:
            fmt_char = "h"
        elif size == 4:
            fmt_char = "i"
        elif size == 8:
            fmt_char = "q"
        else:
            assert False, size
        if not signed:
            fmt_char = fmt_char.upper()

        return ">" + fmt_char

    def push(
        self, val: int | float | bytes | bytearray | bool, signed=True, size=WORD_SIZE
    ):
        if isinstance(val, (bytes, bytearray)):
            self.stack += val
        elif isinstance(val, bool):
            # push a byte onto stack
            self.push(b"\xff" if val else b"\x00")
        elif isinstance(val, float):
            self.push(struct.pack(">d", val))
        else:
            assert isinstance(val, int), val
            # first convert the int into bits
            # have to do some stupid python stuff to deal with negatives
            if val < 0:
                # this should give us the right bit repr for two's complement
                val = val + (1 << (size * 8))

            bits = bin(val)[2:]  # remove "0b"
            # okay now truncate if necessary
            bits = bits[-(size * 8) :]
            self.stack += int(bits, 2).to_bytes(size, byteorder="big", signed=False)

    def pop(self, type=int, signed=True, size=WORD_SIZE) -> int | float | bytearray:
        """pops one word off the stack and interprets it as an int or float, of
        the specified signedness (if applicable) and bit width (if applicable)"""
        value = self.stack[-size:]
        self.stack = self.stack[:-size]
        if type == int:
            fmt_str = self.get_int_fmt_str(size, signed)
            return struct.unpack(fmt_str, value)[0]
        elif type == float:
            if size == 8:
                return struct.unpack(">d", value)[0]
            assert size == 4, size
            return struct.unpack(">f", value)[0]
        elif type == bytes or type == bytearray:
            # compiler knows best. always let them have the last word ;)
            return value
        elif type == bool:
            assert size == 1, size
            return bool(value[0])
        else:
            assert False, type

    def validate_cmd(self, opcode: int, args: bytes) -> bool:
        if self.cmd_dict is None:
            # the user didn't load a command dictionary, just ignore verifying cmds
            return True

        if opcode not in self.cmd_dict:
            print("invalid opcode", opcode)
            return False

        cmd = self.cmd_dict[opcode]
        offset = 0
        for arg in cmd.arguments:
            arg_name, arg_desc, arg_type = arg
            arg_type: type[BaseType]
            arg_value = arg_type()
            arg_value.deserialize(args, offset)
            offset += arg_value.getSize()

        return offset == len(args)

    def handle_allocate_stack(self, dir: AllocateDirective):
        if len(self.stack) + dir.size > self.max_stack_size:
            return DirectiveErrorCode.STACK_OVERFLOW

        self.stack += bytearray(0 for i in range(0, dir.size))

    def handle_no_op(self, dir: NoOpDirective):
        pass

    def handle_pop_discard(self, dir: DiscardDirective):
        if len(self.stack) < WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        self.pop(size=dir.size, type=bytes)

    def handle_load(self, dir: LoadDirective):
        if len(self.stack) + dir.size > self.max_stack_size:
            return DirectiveErrorCode.STACK_OVERFLOW

        if dir.lvar_offset + self.stack_frame_start + dir.size > len(self.stack):
            return DirectiveErrorCode.STACK_OVERFLOW

        # grab a word beginning at lvar start and put on operand stack
        value = self.stack[
            self.stack_frame_start
            + dir.lvar_offset : (self.stack_frame_start + dir.lvar_offset + dir.size)
        ]
        self.push(value)

    def handle_store(self, dir: StoreDirective):
        if len(self.stack) < dir.size:
            return DirectiveErrorCode.STACK_UNDERFLOW

        if dir.lvar_offset + self.stack_frame_start + dir.size > len(self.stack):
            return DirectiveErrorCode.STACK_OVERFLOW

        # get the last `dir.size` bytes of the stack
        value = self.stack[-dir.size :]
        # remove them from top of stack
        self.stack = self.stack[: -dir.size]
        # put into lvar array at the given offset
        for i in range(0, len(value)):
            self.stack[dir.lvar_offset + self.stack_frame_start + i] = value[i]

    def handle_push_val(self, dir: PushValDirective):
        if len(self.stack) + WORD_SIZE > self.max_stack_size:
            return DirectiveErrorCode.STACK_OVERFLOW
        self.push(dir.val)

    def handle_wait_rel(self, dir: WaitRelDirective):
        if len(self.stack) < 8:
            return DirectiveErrorCode.STACK_UNDERFLOW

        useconds = self.pop(size=4)
        seconds = self.pop(size=4)

        print("wait rel", seconds, useconds)

    def handle_wait_abs(self, dir: WaitAbsDirective):
        if len(self.stack) < 11:
            return DirectiveErrorCode.STACK_UNDERFLOW
        useconds = self.pop(size=4)
        seconds = self.pop(size=4)
        time_context = self.pop(size=1)
        time_base = self.pop(size=2)

        print("wait abs", time_context, time_base, seconds, useconds)

    def handle_const_cmd(self, dir: ConstCmdDirective):
        print("cmd opcode", dir.cmd_opcode, "args", dir.args)
        # always push CmdResponse.OK
        if not self.validate_cmd(dir.cmd_opcode, dir.args):
            raise RuntimeError("Invalid cmd")
        self.push(0, size=4)

    def handle_stack_cmd(self, dir: StackCmdDirective):
        if len(self.stack) < dir.args_size + 4:
            return DirectiveErrorCode.STACK_UNDERFLOW

        cmd = self.stack[-(dir.args_size + 4) :]
        self.stack = self.stack[: -(dir.args_size + 4)]
        opcode = int.from_bytes(cmd[-4:], signed=False, byteorder="big")

        print(
            "cmd opcode",
            opcode,
            "args",
            cmd[:-4],
        )
        if not self.validate_cmd(opcode, cmd[:-4]):
            raise RuntimeError("Invalid cmd")
        # always push CmdResponse.OK
        self.push(0, size=4)

    def handle_goto(self, dir: GotoDirective):
        if dir.dir_idx > len(self.dirs):
            return DirectiveErrorCode.DIR_OUT_OF_BOUNDS
        self.next_dir_idx = dir.dir_idx

    def handle_if(self, dir: IfDirective):
        if dir.false_goto_dir_index > len(self.dirs):
            return DirectiveErrorCode.DIR_OUT_OF_BOUNDS
        if len(self.stack) < 1:
            return DirectiveErrorCode.STACK_UNDERFLOW
        conditional = self.pop(type=bool, size=1)
        if not conditional:
            self.next_dir_idx = dir.false_goto_dir_index

    def handle_store_tlm_val(self, dir: StoreTlmValDirective):
        whole_value: bytearray = self.tlm_db.get(dir.chan_id, None)
        if whole_value is None:
            return DirectiveErrorCode.TLM_NOT_FOUND

        if (
            self.stack_frame_start + dir.lvar_offset + len(whole_value)
            > self.max_stack_size
        ):
            return DirectiveErrorCode.STACK_OVERFLOW

        self.stack[
            self.stack_frame_start
            + dir.lvar_offset : (
                self.stack_frame_start + dir.lvar_offset + len(whole_value)
            )
        ] = whole_value

    def handle_store_prm(self, dir: StorePrmDirective):
        whole_value: bytearray = self.prm_db.get(dir.prm_id, None)
        if whole_value is None:
            return DirectiveErrorCode.PRM_NOT_FOUND

        if (
            self.stack_frame_start + dir.lvar_offset + len(whole_value)
            > self.max_stack_size
        ):
            return DirectiveErrorCode.STACK_OVERFLOW

        self.stack[
            self.stack_frame_start
            + dir.lvar_offset : (
                self.stack_frame_start + dir.lvar_offset + len(whole_value)
            )
        ] = whole_value

    def handle_or(self, dir: OrDirective):
        if len(self.stack) < 2:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(type=bool, size=1)
        lhs = self.pop(type=bool, size=1)
        self.push(lhs or rhs)

    def handle_and(self, dir: AndDirective):
        if len(self.stack) < 2:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(type=bool, size=1)
        lhs = self.pop(type=bool, size=1)
        self.push(lhs and rhs)

    def handle_ieq(self, dir: IntEqualDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        self.push(self.pop() == self.pop())

    def handle_ine(self, dir: IntNotEqualDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        self.push(self.pop() != self.pop())

    def handle_ult(self, dir: UnsignedLessThanDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(signed=False)
        lhs = self.pop(signed=False)
        self.push(lhs < rhs)

    def handle_ule(self, dir: UnsignedLessThanOrEqualDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(signed=False)
        lhs = self.pop(signed=False)
        self.push(lhs <= rhs)

    def handle_ugt(self, dir: UnsignedGreaterThanDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(signed=False)
        lhs = self.pop(signed=False)
        self.push(lhs > rhs)

    def handle_uge(self, dir: UnsignedGreaterThanOrEqualDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(signed=False)
        lhs = self.pop(signed=False)
        self.push(lhs >= rhs)

    def handle_slt(self, dir: SignedLessThanDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop()
        lhs = self.pop()
        self.push(lhs < rhs)

    def handle_sle(self, dir: SignedLessThanOrEqualDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop()
        lhs = self.pop()
        self.push(lhs <= rhs)

    def handle_sgt(self, dir: SignedGreaterThanDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop()
        lhs = self.pop()
        self.push(lhs > rhs)

    def handle_sge(self, dir: SignedGreaterThanOrEqualDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop()
        lhs = self.pop()
        self.push(lhs >= rhs)

    def handle_feq(self, dir: FloatEqualDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(type=float)
        lhs = self.pop(type=float)
        print(rhs, lhs, rhs == lhs)
        self.push(lhs == rhs)

    def handle_fne(self, dir: FloatNotEqualDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        self.push(self.pop(type=float) != self.pop(type=float))

    def handle_flt(self, dir: FloatLessThanDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(type=float)
        lhs = self.pop(type=float)
        self.push(lhs < rhs)

    def handle_fle(self, dir: FloatLessThanOrEqualDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(type=float)
        lhs = self.pop(type=float)
        self.push(lhs <= rhs)

    def handle_fgt(self, dir: FloatGreaterThanDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(type=float)
        lhs = self.pop(type=float)
        self.push(lhs > rhs)

    def handle_fge(self, dir: FloatGreaterThanOrEqualDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(type=float)
        lhs = self.pop(type=float)
        self.push(lhs >= rhs)

    def handle_not(self, dir: NotDirective):
        if len(self.stack) < 1:
            return DirectiveErrorCode.STACK_UNDERFLOW
        val = self.pop(type=bool, size=1)
        if val:
            self.push(False)
        else:
            self.push(True)

    def handle_fpext(self, dir: FloatExtendDirective):
        if len(self.stack) < 4:
            return DirectiveErrorCode.STACK_UNDERFLOW
        val_bytes = self.stack[-4:]
        self.stack = self.stack[:-4]
        val_as_float = struct.unpack(">f", val_bytes)[0]

        self.push(val_as_float)

    def handle_siext_8_64(self, dir: IntegerSignedExtend8To64Directive):
        if len(self.stack) < 1:
            return DirectiveErrorCode.STACK_UNDERFLOW
        if len(self.stack) + 7 > self.max_stack_size:
            return DirectiveErrorCode.STACK_OVERFLOW

        # pop val off stack
        val = self.pop(type=int, signed=True, size=1)

        self.push(val, signed=True, size=8)

    def handle_siext_16_64(self, dir: IntegerSignedExtend16To64Directive):
        if len(self.stack) < 2:
            return DirectiveErrorCode.STACK_UNDERFLOW
        if len(self.stack) + 6 > self.max_stack_size:
            return DirectiveErrorCode.STACK_OVERFLOW

        # pop val off stack
        val = self.pop(type=int, signed=True, size=2)

        self.push(val, signed=True, size=8)

    def handle_siext_32_64(self, dir: IntegerSignedExtend32To64Directive):
        if len(self.stack) < 4:
            return DirectiveErrorCode.STACK_UNDERFLOW
        if len(self.stack) + 4 > self.max_stack_size:
            return DirectiveErrorCode.STACK_OVERFLOW

        # pop val off stack
        val = self.pop(type=int, signed=True, size=4)

        self.push(val, signed=True, size=8)

    def handle_ziext_8_64(self, dir: IntegerZeroExtend8To64Directive):
        if len(self.stack) < 1:
            return DirectiveErrorCode.STACK_UNDERFLOW
        if len(self.stack) + 7 > self.max_stack_size:
            return DirectiveErrorCode.STACK_OVERFLOW

        # pop val off stack
        val = self.pop(type=int, signed=False, size=1)

        self.push(val, signed=False, size=8)

    def handle_ziext_16_64(self, dir: IntegerZeroExtend16To64Directive):
        if len(self.stack) < 2:
            return DirectiveErrorCode.STACK_UNDERFLOW
        if len(self.stack) + 6 > self.max_stack_size:
            return DirectiveErrorCode.STACK_OVERFLOW

        # pop val off stack
        val = self.pop(type=int, signed=False, size=2)

        self.push(val, signed=False, size=8)

    def handle_ziext_32_64(self, dir: IntegerZeroExtend32To64Directive):
        if len(self.stack) < 4:
            return DirectiveErrorCode.STACK_UNDERFLOW
        if len(self.stack) + 4 > self.max_stack_size:
            return DirectiveErrorCode.STACK_OVERFLOW

        # pop val off stack
        val = self.pop(type=int, signed=False, size=4)

        self.push(val, signed=False, size=8)

    def handle_fptrunc(self, dir: FloatTruncateDirective):
        if len(self.stack) < WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        val_64 = self.pop(type=float)
        val_32_bytes = struct.pack(">f", val_64)
        self.push(val_32_bytes)

    def handle_itrunc_64_8(self, dir: IntegerTruncate64To8Directive):
        if len(self.stack) < 8:
            return DirectiveErrorCode.STACK_UNDERFLOW

        val = self.pop(type=bytes, size=8)
        val = val[-1:]
        self.push(val)

    def handle_itrunc_64_16(self, dir: IntegerTruncate64To16Directive):
        if len(self.stack) < 8:
            return DirectiveErrorCode.STACK_UNDERFLOW

        val = self.pop(type=bytes, size=8)
        val = val[-2:]
        self.push(val)

    def handle_itrunc_64_32(self, dir: IntegerTruncate64To32Directive):
        if len(self.stack) < 8:
            return DirectiveErrorCode.STACK_UNDERFLOW

        val = self.pop(type=bytes, size=8)
        val = val[-4:]
        self.push(val)

    def handle_fptosi(self, dir: FloatToSignedIntDirective):
        if len(self.stack) < WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        val = self.pop(type=float)
        self.push(val)

    def handle_fptoui(self, dir: FloatToUnsignedIntDirective):
        if len(self.stack) < WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        val = self.pop(type=float)
        self.push(val)

    def handle_sitofp(self, dir: SignedIntToFloatDirective):
        if len(self.stack) < WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        val = self.pop()
        self.push(float(val))

    def handle_uitofp(self, dir: UnsignedIntToFloatDirective):
        if len(self.stack) < WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        val = self.pop(signed=False)
        self.push(float(val))

    def handle_iadd(self, dir: IntAddDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop()
        lhs = self.pop()
        self.push(overflow_check(lhs + rhs))

    def handle_isub(self, dir: IntSubtractDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop()
        lhs = self.pop()
        self.push(overflow_check(lhs - rhs))

    def handle_imul(self, dir: IntMultiplyDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop()
        lhs = self.pop()
        self.push(overflow_check(lhs * rhs))

    def handle_udiv(self, dir: UnsignedIntDivideDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(signed=False)
        lhs = self.pop(signed=False)

        # credit to gemini
        if rhs == 0:
            # C++ behavior for division by zero is undefined.
            return DirectiveErrorCode.DIVIDE_BY_ZERO

        # Perform division, truncating towards zero
        # This is different from Python's // which floors.
        python_quotient = int(lhs / rhs)

        # For division, overflow detection isn't typically done with the mask on the result
        # because the quotient itself is within range
        self.push(python_quotient)

    def handle_sdiv(self, dir: SignedIntDivideDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(signed=True)
        lhs = self.pop(signed=True)

        # credit to gemini
        if rhs == 0:
            # C++ behavior for division by zero is undefined.
            return DirectiveErrorCode.DIVIDE_BY_ZERO

        # Special overflow case: MIN_INT64 / -1
        # This results in MAX_INT64 + 1, which overflows to MIN_INT64 in C++.
        if lhs == MIN_INT64 and rhs == -1:
            self.push(MIN_INT64)  # C++ specific overflow behavior
            return

        python_quotient = int(lhs / rhs)

        self.push(python_quotient)

    def handle_fadd(self, dir: FloatAddDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(type=float)
        lhs = self.pop(type=float)
        self.push(lhs + rhs)

    def handle_fsub(self, dir: FloatSubtractDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(type=float)
        lhs = self.pop(type=float)
        self.push(lhs - rhs)

    def handle_fmul(self, dir: FloatMultiplyDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(type=float)
        lhs = self.pop(type=float)
        self.push(lhs * rhs)

    def handle_fdiv(self, dir: FloatDivideDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(type=float)
        lhs = self.pop(type=float)
        self.push(lhs / rhs)

    def handle_smod(self, dir: SignedModuloDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(signed=True)
        lhs = self.pop(signed=True)
        self.push(lhs % rhs, signed=True)

    def handle_umod(self, dir: UnsignedModuloDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(signed=False)
        lhs = self.pop(signed=False)
        self.push(lhs % rhs, signed=False)

    def handle_fmod(self, dir: FloatModuloDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(type=float)
        lhs = self.pop(type=float)
        self.push(lhs % rhs)

    def handle_fpow(self, dir: FloatExponentDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(type=float)
        lhs = self.pop(type=float)
        self.push(lhs**rhs)

    def handle_log(self, dir: FloatLogDirective):
        if len(self.stack) < WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        operand = self.pop(type=float)
        self.push(math.log(operand))

    def handle_float_floor_div(self, dir: FloatFloorDivideDirective):
        if len(self.stack) < 2 * WORD_SIZE:
            return DirectiveErrorCode.STACK_UNDERFLOW
        rhs = self.pop(type=float)
        lhs = self.pop(type=float)
        self.push(lhs // rhs)

    def handle_exit(self, dir: ExitDirective):
        if len(self.stack) < 1:
            return DirectiveErrorCode.STACK_UNDERFLOW
        success = self.pop(type=bool, size=1)
        if success:
            self.next_dir_idx = len(self.dirs)
        else:
            return DirectiveErrorCode.DELIBERATE_FAILURE

    def handle_memcmp(self, dir: MemCompareDirective):
        if len(self.stack) < dir.size * 2:
            return DirectiveErrorCode.STACK_UNDERFLOW

        rhs = self.pop(type=bytes, size=dir.size)
        lhs = self.pop(type=bytes, size=dir.size)
        print(rhs, lhs)
        self.push(rhs == lhs)
