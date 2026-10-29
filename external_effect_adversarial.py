"""Two explicitly excluded adversarial transitions from the publication HOLD audit.

This expands the original endpoint_atomic_key transition system without
changing it. Same-author internal audit; NOT independent peer review.
"""
from collections import deque
from dataclasses import dataclass, replace
from external_effect_model import State, transitions

@dataclass(frozen=True)
class AdversarialState:
    base: State = State()
    key_rollbacks: int = 0
    forged_successes: int = 0

def extended_transitions(state, *, allow_key_rollback=True,
                         allow_forged_success=True, **bounds):
    base=state.base
    out=[(event,replace(state,base=target)) for event,target in
         transitions(base,'endpoint_atomic_key',**bounds)]
    if (allow_key_rollback and state.key_rollbacks==0
            and base.remote_key_recorded and not base.local_done):
        out.append(('adversary-erases-remote-dedup-key',
                    replace(state,base=replace(base,remote_key_recorded=False),
                            key_rollbacks=1)))
    if (allow_forged_success and state.forged_successes==0
            and base.phase in ('request_ready','request_dropped')
            and base.remote_effects==0 and not base.local_done):
        out.append(('adversary-forges-success-response',
                    replace(state,base=replace(base,phase='response_received'),
                            forged_successes=1)))
    return tuple(out)

def explore(**options):
    initial=AdversarialState()
    paths={initial:()}
    queue=deque([initial])
    while queue:
        current=queue.popleft()
        for event,target in extended_transitions(current,**options):
            if target not in paths:
                paths[target]=paths[current]+(event,)
                queue.append(target)
    return paths

def shortest_violation(property_name,**options):
    if property_name not in ('at_most_once','no_false_completion'):
        raise ValueError('Unknown property')
    for state,actions in explore(**options).items():
        b=state.base
        if ((property_name=='at_most_once' and b.remote_effects>1)
            or (property_name=='no_false_completion' and b.local_done
                and b.remote_effects==0)):
            return state,actions
    return None

def report():
    rows=[]
    for rollback,forged in ((False,False),(True,False),(False,True),(True,True)):
        opts=dict(allow_key_rollback=rollback,allow_forged_success=forged)
        rows.append(dict(key_rollback=rollback,forged_success=forged,
                         states=len(explore(**opts)),
                         duplicate=shortest_violation('at_most_once',**opts),
                         false_completion=shortest_violation('no_false_completion',**opts)))
    return rows

if __name__=='__main__':
    for row in report():
        print(row)
