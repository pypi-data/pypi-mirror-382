"""
SPDX-License-Identifier: LGPL-3.0-or-later
Copyright (C) 2025 Lappeenrannan-Lahden teknillinen yliopisto LUT
Author: Aleksei Romanenko <aleksei.romanenko@lut.fi>

Funded by the European Union and UKRI. Views and opinions expressed are however those of the author(s) 
only and do not necessarily reflect those of the European Union, CINEA or UKRI. Neither the European 
Union nor the granting authority can be held responsible for them.
"""
import dataclasses
import filecmp
import re
import shutil
from collections import deque
from dataclasses import dataclass
import logging
from collections.abc import Callable
from os import unlink
from typing import Any, Generic, TypeVar

from pyee.asyncio import AsyncIOEventEmitter

from .state_base import StateBase
from beartype import beartype

from slugify import slugify as helper_slugify
from pathlib import Path

def slugify(x : str, separator="_"):
    assert type(x) is str
    for_caps=re.compile(r"([a-z0-9])([A-Z])")
    for_numbers=re.compile(r"([a-zA-Z])([0-9])")
    x = re.sub(for_caps, r"\1"+separator+r"\2", x)
    x = re.sub(for_numbers, r"\1"+separator+r"\2", x)
    return helper_slugify(x,separator=separator)



logger = logging.getLogger(__name__)


StatesEnumType = TypeVar("StatesEnumType", bound=StateBase)
EventsEnumType = TypeVar("EventsEnumType")
ConditionsEnumType = TypeVar("ConditionsEnumType")
FSMContextType = TypeVar("FSMContextType")


states = (('quoteds', 'exclusive'),
          ('colons', 'exclusive'),)

tokens = ('STARTUML', 'ENDUML', 'START_END', 'NAME', 'AS', 'ESCAPED_ESCAPE', 'ESCAPED_NEWLINE', 'NEWLINE', 'ESCAPED_QUOTE',
          'QUOTE', 'LONG_ARROW', 'ARROW', 'COLON', 'WS', 'NUMBER', 'LBRACKET', 'RBRACKET', 'STRING')

t_STARTUML = r"@startuml"
t_ENDUML = r"@enduml"
t_START_END = r"\[\*\]"
t_AS = r"as"
t_ESCAPED_ESCAPE = r"\\\\"
t_ESCAPED_QUOTE = r'\\"'
t_ESCAPED_NEWLINE = r"\\n"
t_LONG_ARROW = r"-->"
t_ARROW = r"->"
t_WS = r"[ \t]+"
t_NUMBER = r"[0-9]+"
t_LBRACKET = r"{"
t_RBRACKET = r"}"
t_STRING = r"[a-zA-Z0-9_\/]+"

def t_NAME(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.value = slugify(t.value, separator="_")
    return t

def t_QUOTE(t):
    r'"'
    t.lexer.begin('quoteds')
    t.lexer.quoteds_start = t.lexer.lexpos

def t_COLON(t):
    r":[ \t]*"
    t.lexer.begin('colons')
    t.lexer.colons_start = t.lexer.lexpos
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    return t

def t_error(t):
    raise Exception(f"Illegal character '{t.value[0]}'")

def t_quoteds_ESCAPED_QUOTE(t):
    r'\\"'
    t.lexer.skip(1)

def t_quoteds_QUOTE(t):
    r'"'
    t.value = t.lexer.lexdata[t.lexer.quoteds_start:t.lexer.lexpos+1]
    t.type = "STRING"
    t.lexer.begin('INITIAL')
    return t

def t_quoteds_NEWLINE(t):
    r'\n+'
    raise Exception(f"Illegal newline while parsing "
                    f"string from {t.lexer.quoteds_start} "
                    f"at line {t.lexer.lineno}")

def t_colons_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    t.value = t.lexer.lexdata[t.lexer.colons_start:t.lexer.lexpos-1]
    t.type = "STRING"
    t.lexer.begin('INITIAL')
    return t

def t_quoteds_error(t):
    t.lexer.skip(1)

def t_colons_error(t):
    t.lexer.skip(1)

import ply.lex as lex
lexer = lex.lex()


@dataclass
class TransitionEvent(Generic[StatesEnumType, EventsEnumType]):
    name : str
    target_state : str

@dataclass
class TransitionCondition(Generic[StatesEnumType, ConditionsEnumType]):
    name : str
    target_state : str

@dataclass
class StateInfo(Generic[StatesEnumType, ConditionsEnumType, EventsEnumType, FSMContextType]):
    name : StatesEnumType | None = None
    transition_events : list[TransitionEvent[StatesEnumType, EventsEnumType]] = dataclasses.field(default_factory=list)
    transition_conditions : list[TransitionCondition[StatesEnumType, ConditionsEnumType]] = dataclasses.field(default_factory=list)
    is_initial : bool = False
    on_enter : str | None = None
    on_exit : str | None = None
    on_loop : str | None = None
    default_transition : StatesEnumType | None = None
    condition_context : Any = None
    conditions : dict[str, Callable[[FSMContextType, Any], bool]] = dataclasses.field(default_factory=dict)


def p_document(p):
    '''document : startuml expressions enduml
                | document NEWLINE'''
    p[0] = p[2]

def p_startuml(p):
    '''startuml : STARTUML NEWLINE '''
    p[0] = None

def p_enduml(p):
    '''enduml : ENDUML NEWLINE '''
    p[0] = None


def p_expressions(p):
    '''expressions : expressions expression'''
    p[0] = p[1]

    if type(p[2]) is list:
        p[0] += p[2]
    else:
        if p[2] is not None:
            p[0].append(p[2])

def p_expressions_promote(p):
    '''expressions : expression'''
    p[0] = list()
    if p[1] is not None:
        p[0].append(p[1])

def p_expression(p):
    '''expression : state_name arrow state_name colon_string
                  | NAME arrow state_name colon_string
    '''
    fname = p[4]
    p[0] = ("add_transition", tuple(p), fname)

def p_expression_default(p):
    '''expression : state_name arrow state_name NEWLINE
                  | state_name arrow NAME NEWLINE
                  | NAME arrow state_name NEWLINE
                  | NAME arrow NAME NEWLINE
    '''
    fname = "default"
    p[0] = ("add_transition", tuple(p), fname)


def add_transition(sm_states, p, fname, _se, _ce, _ee):
    if p[1] is not None:
        if p[1] not in sm_states:
            sm_states[p[1]] = StateInfo()
            sm_states[p[1]].name = p[1]
    if p[3] not in sm_states:
        sm_states[p[3]] = StateInfo()
        sm_states[p[3]].name = p[3]

    if p[1] is None:
        sm_states[p[3]].is_initial = True
        for k in sm_states:
            if k != p[3]:
                assert not sm_states[k].is_initial, (f"More than one state "
                                                     f"has been marked as "
                                                     f"initial. This is not "
                                                     f"allowed. Conflicting "
                                                     f"states are {p[3]} and {k}.")
        return

    if fname == "default":
        assert  sm_states[p[1]].default_transition is None, (
            f"States cannot have more than one default transition. In state {p[1]}")
        sm_states[p[1]].default_transition = p[3]
    elif fname.lower().startswith("on ") or fname.lower().startswith("when "):
        ti = TransitionEvent[_se, _ee](
                            name=slugify(fname, separator="_"),
                            target_state=p[3])
        sm_states[p[1]].transition_events.append(ti)
    elif fname.lower().startswith("if "):
        ti = TransitionCondition[_se, _ce](
                            name=slugify(fname, separator="_"),
                            target_state=p[3])
        sm_states[p[1]].transition_conditions.append(ti)
    else:
        raise Exception(f"Invalid syntax. State comment must "
                        f"start with on/when/if. In state {p[1]}. Bad value was: {fname}")


def p_expression_as(p):
    '''expression : state_name string state_name NAME NEWLINE
    '''
    assert p[1] == "state", f"unknown syntax {''.join(p)}"
    assert p[3] == "as", f"unknown syntax {''.join(p)}"
    p[0] = ("declare_state", p[2], p[4])


def declare_state(sm_states, p3, p7, state_info_cls):
    if p7 not in sm_states:
        sm_states[p7] = state_info_cls()
    sm_states[p7].name = p3


def p_expression_colon(p):
    '''expression : state_name COLON STRING
    '''
    valid_prefices = ["enter ", "exit ", "loop "]
    for valid_prefix in valid_prefices:
        if p[3].lower().startswith(valid_prefix):
            p[0] = ("state_actions", p[1], p[3].split(" ")[0], slugify(" ".join(p[3].split(" ")[1:]), separator="_"))
            return
    raise Exception(f"Invalid syntax in state {p[1]} action {p[4]} must start with one of: {valid_prefices}")

def state_actions(sm_states, p1, slot, action, state_info_cls):
    if p1 not in sm_states:
        sm_states[p1] = state_info_cls()
    if slot == "enter":
        sm_states[p1].on_enter = action
    if slot == "exit":
        sm_states[p1].on_exit = action
    if slot == "loop":
        sm_states[p1].on_loop = action

def p_expression_other(p):
    '''expression : state_name string state_name NEWLINE
    '''
    p[0] = None

def p_string(p):
    '''string : STRING WS
              | STRING
    '''
    p[0] = p[1]

def p_state_name(p):
    '''state_name : state_name WS
                  | START_END
                  | NAME
    '''
    if p[1] is None:
        p[0] = None
    elif p[1] == r"[*]":
        p[0] = None
    else:
        p[0] = slugify(p[1], separator="_")

def p_arrow(p):
    '''arrow : ARROW WS
             | ARROW
             | LONG_ARROW WS
             | LONG_ARROW
    '''
    p[0] = p[1]

def p_colon_string(p):
    '''colon_string : COLON STRING
    '''
    p[0] = p[2]

def p_error(t):
    if t is not None:
        raise Exception(f"Syntax error at {t}")


import ply.yacc as yacc

@beartype
class AFSM(Generic[StatesEnumType, ConditionsEnumType, EventsEnumType, FSMContextType]):

    def __init__(self, uml, se_factory: Callable[[str], StatesEnumType], context: FSMContextType, debug_ply=False, *args, **kwargs):
        super().__init__()
        self.uml = uml
        self._events = AsyncIOEventEmitter()

        self.terminated = False
        self.in_transit = False
        self.deferred_events = deque()

        self.sm_states : dict[StatesEnumType, StateInfo[StatesEnumType, ConditionsEnumType, EventsEnumType, FSMContextType]] = dict()

        self.context : FSMContextType = context


        self.se_factory = se_factory

        parser = yacc.yacc()

        ast = parser.parse(uml, debug=debug_ply)

        for command in ast:
            if command[0] == "declare_state":
                declare_state(self.sm_states, command[1], command[2], StateInfo[StatesEnumType, ConditionsEnumType, EventsEnumType, FSMContextType])
            elif command[0] == "state_actions":
                state_actions(self.sm_states, command[1], command[2], command[3], StateInfo[StatesEnumType, ConditionsEnumType, EventsEnumType, FSMContextType])
            elif command[0] == "add_transition":
                add_transition(self.sm_states, command[1], command[2], StatesEnumType, ConditionsEnumType, EventsEnumType)
            else:
                raise Exception(f"Unknown command {command[0]}")

        for k, v in self.sm_states.items():
            if v.default_transition:
                v.default_transition = self.se_factory(v.default_transition)

        self.current_state : StatesEnumType | None = None

        for k, st in self.sm_states.items():
            if st.is_initial:
                if isinstance(k, str):
                    k = self.se_factory(k)
                self.current_state = k
                break
            for transition in st.transition_conditions:
                assert transition.name in st.conditions, (f"State machine condition tester {transition.name} for state {self.current_state} "
                                                              f"was left uninitialized. Add one to .conditions.")

        logger.info(f"FSM initial state is { self.current_state }")
        assert self.current_state is not None, "FSM did not have any state marked as initial. Please add one using transition from [*] pseudo-state"


    def write_enum_module(self, module_name, location=None):
        if location is None:
            actual_name = slugify(module_name, separator="_") + "_enums.py"
        else:
            actual_name = location
        shadow_name = actual_name + ".shadow"
        with open(shadow_name, "w") as f:
            f.write("from enum import Enum\n")
            f.write(f"""from atfsm.state_base import StateBase

class {module_name}State(StateBase, str, Enum):
""")
            stub = True
            for st in self.sm_states:
                if st is not None:
                    f.write(f"    {st}='{st}'\n")
                    stub = False
            if stub:
                f.write(f"    pass'\n")
            f.write(f"""
class {module_name}Condition(str, Enum):
""")
            stub = True
            stv : StateInfo[StatesEnumType, ConditionsEnumType, EventsEnumType]
            uniques = set()
            for st, stv in self.sm_states.items():
                for tr in stv.transition_conditions:
                    if tr.name not in uniques:
                        uniques |= {tr.name}
                        f.write(f"    {tr.name}='{tr.name}'\n")
                        stub = False
            if stub:
                f.write(f"    pass\n")
            f.write(f"""

class {module_name}Event(str, Enum):
    on_state_changed = 'on_state_changed'
""")
            uniques = set()
            for st, stv in self.sm_states.items():
                for tr in stv.transition_events:
                    if tr.name not in uniques:
                        uniques |= {tr.name}
                        f.write(f"    {tr.name}='{tr.name}'\n")
                        stub = False
        if not Path(actual_name).exists() or not filecmp.cmp(shadow_name, actual_name, shallow=False):
            shutil.move(shadow_name, actual_name)
        else:
            unlink(shadow_name)

    def on(self, event, callback):
        logger.debug(f"New subscription to {event}")
        self._events.on(event, callback)

    def apply_context_to_all_states(self, context):
        for k, st in self.sm_states.items():
            st.condition_context = context


    def apply_to_all_conditions(self, condition_name : ConditionsEnumType, callback):
        for k, st in self.sm_states.items():
            for transition in st.transition_conditions:
                if transition.name == condition_name.name:
                    st.conditions[transition.name] = callback


    async def loop(self):
        if self.terminated:
            logger.error("Attempted looping a finished FSM")
            return
        if self.current_state is None:
            raise Exception("Trying to loop before current_state is set is not allowed.")

        await self.handle_deferred_signals()

        st = self.sm_states[self.current_state]
        transition : TransitionCondition[StatesEnumType, ConditionsEnumType]
        for transition in st.transition_conditions:
            assert transition.name in st.conditions, (f"State machine condition tester {transition.name} for state {self.current_state} "
                                                          f"was left uninitialized. Add one to .conditions.")
            #assert isinstance(transition.name, Type[CE])
            if st.conditions[ transition.name ](self.context, st.condition_context):
                await self.transition_to_new_state(st, self.se_factory(transition.target_state) if transition.target_state is not None else None)
                logger.info(f"FSM after conditional transition is { self.current_state }")
                return
        if st.default_transition is not None:
            await self.transition_to_new_state(st, self.se_factory(st.default_transition))
            logger.info(f"FSM after default transition is { self.current_state }")



    async def handle(self, event : EventsEnumType):
        if self.current_state is None:
            logger.warning(f"Attempted to handle an event before current_state is set.")
            return
        if self.terminated:
            logger.error("Attempted looping a finished FSM")
            return
        if self.in_transit:
            await self.handle_as_deferred(event)
            return
        logger.info(f"FSM on event {event}")
        self._events.emit(str(event), event, self.current_state)
        st = self.sm_states[self.current_state]
        for transition in st.transition_events:
            if transition.name == event:
                await self.transition_to_new_state(st, self.se_factory(transition.target_state))
                logger.info(f"FSM after event state is { self.current_state }")
                break

    async def handle_as_deferred(self, event):
        logger.info(f"Got new event {event} during state transit. Deferring.")
        self.deferred_events.append(event)

    async def handle_deferred_signals(self):
        while self.deferred_events:
            event = self.deferred_events.popleft()
            logger.info(f"Processing deferred event {event}")
            await self.handle(event)

    async def transition_to_new_state(self, st, target_state : StatesEnumType | None):
        if self.current_state is None:
            logger.error("Attempted transitioning a FSM without current_state")
            return

        assert isinstance(target_state, StateBase) or target_state is None, f"{type(target_state)}"

        if self.terminated:
            logger.error("Attempted transitioning a finished FSM")
            return

        self.in_transit = True
        if target_state is None:
            logger.warning("FSM reached its termination point")
            self.terminated = True
            self.current_state = target_state
            self._events.emit("on_terminated", "on_terminated")
            self.in_transit = False
            await self.handle_deferred_signals()
            return

        self_current_state : StatesEnumType = self.current_state
        if target_state == self_current_state:

            if st.on_loop is not None:
                self._events.emit(st.on_loop, st.on_loop, self_current_state)
            else:
                self._events.emit(self_current_state.on_loop, self_current_state.on_loop, self_current_state)
        else:

            if st.on_exit is not None:
                self._events.emit(st.on_exit, st.on_exit, self.current_state)
            else:
                self._events.emit(self.current_state.on_exit, self.current_state.on_exit, self.current_state)

            self.current_state = target_state
            self_current_state : StatesEnumType = self.current_state

            st = self.sm_states[self_current_state]
            if st.on_enter is not None:
                self._events.emit(st.on_enter, st.on_enter, self_current_state)
            else:
                self._events.emit(self_current_state.on_enter, self_current_state.on_enter,
                                  self_current_state)
            self._events.emit("on_state_changed", "on_state_changed")
        self.in_transit = False
        await self.handle_deferred_signals()

