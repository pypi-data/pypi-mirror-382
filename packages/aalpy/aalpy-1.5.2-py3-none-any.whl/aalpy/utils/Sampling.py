from functools import wraps
from random import randint, choices, random

from aalpy import MooreMachine, Dfa, NDMooreMachine, Mdp, MarkovChain
from aalpy.base import Automaton, DeterministicAutomaton

def get_io_traces(automaton: Automaton, input_traces: list) -> list:
    moore_automata = (MooreMachine, Dfa, NDMooreMachine, Mdp, MarkovChain)
    is_moore = isinstance(automaton, moore_automata)

    traces = []
    for input_trace in input_traces:
        output_trace = automaton.execute_sequence(automaton.initial_state, input_trace)
        trace = list(zip(input_trace, output_trace))
        if is_moore:
            trace = [automaton.initial_state.output] + trace
        traces.append(trace)
    return traces


def get_labeled_sequences(automaton: Automaton, input_traces: list) -> list:
    moore_automata = (MooreMachine, Dfa, NDMooreMachine, Mdp, MarkovChain)
    is_moore = isinstance(automaton, moore_automata)

    data = []
    for input_trace in input_traces:
        if len(input_trace) == 0:
            if not is_moore:
                raise ValueError("tried to get label of empty sequence for Mealy automaton.")
            output = automaton.initial_state.output
        else:
            output = automaton.execute_sequence(automaton.initial_state, input_trace)[-1]
        data.append((input_trace, output))
    return data


def get_data_from_input_sequence(automaton: Automaton, input_sequence: list, data_format: str = "io_sequences"):
    if data_format == "io_sequences":
        return get_io_traces(automaton, input_sequence)
    elif data_format == "labeled_sequences":
        return get_labeled_sequences(automaton, input_sequence)
    else:
        raise ValueError(f"invalid data_format {data_format}. must be 'io_sequences' or 'labeled_sequences'")


def support_automaton_arg(require_transform):
    def decorator(f):
        @wraps(f)
        def inner(alphabet, *args, include_outputs=False, **kwargs):
            automaton = None
            if isinstance(alphabet, Automaton):
                automaton = alphabet
                if require_transform:
                    alphabet = alphabet.get_input_alphabet()
            traces = f(alphabet, *args, **kwargs)
            if include_outputs:
                if automaton is None:
                    raise ValueError("automaton must be provided")
                traces = get_io_traces(automaton, traces)
            return traces
        return inner
    return decorator


@support_automaton_arg(True)
def sample_with_length_limits(alphabet, nr_samples, min_len, max_len):
    return [choices(alphabet, k = randint(min_len, max_len)) for _ in range(nr_samples)]


@support_automaton_arg(True)
def sample_with_term_prob(alphabet, nr_samples, term_prob):
    ret = []
    for _ in range(nr_samples):
        k = 0
        while term_prob < random():
            k += 1
        ret.append(choices(alphabet, k=k))
    return ret


@support_automaton_arg(False)
def get_complete_sample(automaton: DeterministicAutomaton):
    alphabet = automaton.get_input_alphabet()
    automaton.compute_prefixes()
    char_set = automaton.compute_characterization_set()
    infixes = [(x,) for x in alphabet] + [tuple()]
    return [state.prefix + infix + suffix for state in automaton.states for suffix in char_set for infix in infixes]
