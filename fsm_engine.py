#!/usr/bin/env python3
"""fsm_engine - Finite state machine with guards, actions, and history."""
import sys

class FSM:
    def __init__(self, initial):
        self.state = initial
        self.transitions = {}  # (state, event) -> (next_state, guard, action)
        self.history = [initial]
        self.on_enter = {}
        self.on_exit = {}
    def add(self, src, event, dst, guard=None, action=None):
        self.transitions[(src, event)] = (dst, guard, action)
    def send(self, event):
        key = (self.state, event)
        if key not in self.transitions:
            return False
        dst, guard, action = self.transitions[key]
        if guard and not guard(): return False
        if self.state in self.on_exit:
            self.on_exit[self.state]()
        old = self.state
        self.state = dst
        self.history.append(dst)
        if action: action(old, event, dst)
        if dst in self.on_enter:
            self.on_enter[dst]()
        return True
    def can(self, event):
        key = (self.state, event)
        if key not in self.transitions: return False
        _, guard, _ = self.transitions[key]
        return guard() if guard else True

def test():
    log = []
    fsm = FSM("idle")
    fsm.add("idle", "start", "running", action=lambda s,e,d: log.append("started"))
    fsm.add("running", "pause", "paused")
    fsm.add("paused", "resume", "running")
    fsm.add("running", "stop", "idle")
    assert fsm.state == "idle"
    assert fsm.send("start")
    assert fsm.state == "running"
    assert log == ["started"]
    assert not fsm.send("start")  # invalid
    assert fsm.send("pause")
    assert fsm.state == "paused"
    assert fsm.can("resume")
    assert not fsm.can("stop")
    fsm.send("resume")
    fsm.send("stop")
    assert fsm.state == "idle"
    assert fsm.history == ["idle", "running", "paused", "running", "idle"]
    # Guard test
    locked = [True]
    fsm2 = FSM("locked")
    fsm2.add("locked", "unlock", "unlocked", guard=lambda: not locked[0])
    assert not fsm2.send("unlock")  # guard fails
    locked[0] = False
    assert fsm2.send("unlock")
    print("fsm_engine: all tests passed")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("Usage: fsm_engine.py --test")
