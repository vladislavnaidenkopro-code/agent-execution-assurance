"""Alternative declarative event specification, independently structured from
the procedural transition implementation. Same-author work; NOT peer review.
"""
from dataclasses import replace
from external_effect_model import State, MODES, PHASES

EVENTS = (
 'begin-request', 'network-drops-request', 'remote-dedup-suppresses-effect',
 'remote-effect-before-key-record', 'remote-commits-effect',
 'remote-server-crashes-before-key-record', 'remote-persist-key-record',
 'request-times-out', 'response-arrives', 'response-is-lost',
 'mark-local-outbox-done', 'client-crashes-losing-volatile-progress',
 'endpoint-idempotency-key-expires',
)

def spec_step(s, mode, event, *, max_attempts=2, max_client_crashes=1,
              max_server_crashes=1, max_key_expirations=1):
    """One declarative guard and post-state for a named event; None if disabled."""
    if mode not in MODES or event not in EVENTS or s.phase not in PHASES:
        raise ValueError('Unknown mode/event/phase')
    if min(max_attempts,max_client_crashes,max_server_crashes,max_key_expirations)<0:
        raise ValueError('Negative bound')
    if s.attempts<0 or s.remote_effects<0 or (s.local_done and s.phase!='finished'):
        raise ValueError('Invalid state')
    if s.phase == 'finished':
        return None
    p=s.phase
    active={
      'begin-request':p=='idle' and s.attempts<max_attempts,
      'network-drops-request':p=='request_ready',
      'remote-dedup-suppresses-effect':p=='request_ready' and mode!='outbox_only' and s.remote_key_recorded,
      'remote-effect-before-key-record':p=='request_ready' and mode=='endpoint_nonatomic_key' and not s.remote_key_recorded,
      'remote-commits-effect':p=='request_ready' and (mode=='outbox_only' or (not s.remote_key_recorded and mode!='endpoint_nonatomic_key')),
      'remote-server-crashes-before-key-record':p=='remote_unmarked' and s.server_crashes<max_server_crashes,
      'remote-persist-key-record':p=='remote_unmarked',
      'request-times-out':p=='request_dropped',
      'response-arrives':p in ('remote_committed','remote_deduped'),
      'response-is-lost':p in ('remote_committed','remote_deduped'),
      'mark-local-outbox-done':p=='response_received',
      'client-crashes-losing-volatile-progress':p in ('request_ready','request_dropped','remote_committed','remote_deduped','response_received') and s.client_crashes<max_client_crashes,
      'endpoint-idempotency-key-expires':mode=='endpoint_expiring_key' and s.remote_key_recorded and s.key_expirations<max_key_expirations,
    }
    if not active[event]:
        return None
    changes={
      'begin-request':dict(phase='request_ready',attempts=s.attempts+1),
      'network-drops-request':dict(phase='request_dropped'),
      'remote-dedup-suppresses-effect':dict(phase='remote_deduped'),
      'remote-effect-before-key-record':dict(phase='remote_unmarked',remote_effects=s.remote_effects+1),
      'remote-commits-effect':dict(phase='remote_committed',remote_effects=s.remote_effects+1,remote_key_recorded=mode!='outbox_only'),
      'remote-server-crashes-before-key-record':dict(phase='idle',server_crashes=s.server_crashes+1),
      'remote-persist-key-record':dict(phase='remote_committed',remote_key_recorded=True),
      'request-times-out':dict(phase='idle'),
      'response-arrives':dict(phase='response_received'),
      'response-is-lost':dict(phase='idle'),
      'mark-local-outbox-done':dict(phase='finished',local_done=True),
      'client-crashes-losing-volatile-progress':dict(phase='idle',client_crashes=s.client_crashes+1),
      'endpoint-idempotency-key-expires':dict(remote_key_recorded=False,key_expirations=s.key_expirations+1),
    }
    return replace(s,**changes[event])

def spec_edges(state,mode,**bounds):
    return frozenset((event,next_state) for event in EVENTS
                     if (next_state:=spec_step(state,mode,event,**bounds)) is not None)
