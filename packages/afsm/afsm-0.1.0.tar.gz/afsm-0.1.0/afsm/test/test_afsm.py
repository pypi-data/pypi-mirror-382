from logging import getLogger

from afsm import AFSM

import asyncio
import pytest

pytest_plugins = ('pytest_asyncio',)


logger = getLogger(__name__)

test_data_1 = """@startuml
scale 600 width

[*] -> State1
State1 --> State2 : on Succeeded
State1 --> [*] : on Aborted 2
State2 --> State3 : on Succeeded
State2 --> [*] : if Aborted
state "Accumulate Enough Data\\nLong State Name" as State3
State3 : loop Just a test
State3 --> State3 : on Failed
State3 --> [*] : on Succeeded / Save Result
State3 --> [*] : on Aborted
State3 --> State4 
State4 --> State3

@enduml
"""
test_data_2 = """@startuml
[*] -> State1

@enduml
"""

test_data_3 = """@startuml
[*] --> Unknown
Unknown --> Identified : on serial number obtained
Unknown --> Rejected : on boot notification
Rejected --> [*]
Identified --> Booted : on boot notification
Identified --> Booted : on cached boot notification
Identified --> Failed : on boot timeout
Failed --> [*]
Booted --> Closing : on reboot confirmed
Closing --> [*]
@enduml
"""

class testContext:
    pass

@pytest.mark.asyncio
async def test_data_set_1():
    # Dry run to generate testfsm_enums module
    fsm : AFSM = AFSM(uml=test_data_1,
                      context=testContext(),
                      se_factory=str,
                      debug_ply=True)
    fsm.write_enum_module("testfsm")
    # Test with all enums
    from testfsm_enums import testfsmState, testfsmCondition, testfsmEvent
    fsm : AFSM[testfsmState, testfsmCondition, testfsmEvent, testContext] = AFSM[testfsmState, testfsmCondition, 
                                                                                 testfsmEvent, testContext](uml=test_data_1,
                                                                                                            context=testContext(),
                                                                                                            se_factory=testfsmState,
                                                                                                            debug_ply=False)
    fsm.write_enum_module("testfsm")
    fsm.sm_states[testfsmState.state_2].conditions[testfsmCondition.if_aborted] = lambda x, x2: False
    fsm.on(testfsmState.state_1.on_exit, lambda event, old_state: logger.warning(f"{event=}, {old_state=}"))
    fsm.on(testfsmState.state_2.on_enter, lambda event, new_state: logger.warning(f"{event=}, {new_state=}"))
    await fsm.handle(testfsmEvent.on_succeeded)
    await fsm.loop()
    await fsm.handle(testfsmEvent.on_succeeded)
    await fsm.loop()

