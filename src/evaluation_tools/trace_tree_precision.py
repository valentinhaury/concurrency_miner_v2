from itertools import combinations, product

from src.data_structures.process_tree_operator import Operator


class TraceTreePrecision:

    BEFORE = "before"
    AFTER = "after"
    OVERLAP = "overlap"

    def __init__(self, trace):
        self.trace = trace

    # ============================================================
    # PUBLIC API
    # ============================================================

    def calculate_precision(self, tree):
        """
        Precision für genau einen Trace.
        """

        trace_steps = self.get_trace_steps()

        if not trace_steps:
            return 1.0

        model_states = {
            self.initial_model_state(tree)
        }

        total_model_steps = 0
        total_escaping_steps = 0

        for trace_step in trace_steps:

            observed_step = frozenset(
                event.get_label()
                for event in trace_step
            )

            # ----------------------------------------------------
            # Alle möglichen Modellschritte aus allen aktuell
            # möglichen Modellzuständen bestimmen.
            # ----------------------------------------------------

            all_model_steps = set()
            all_transitions = []

            for state in model_states:

                model_steps, next_states = \
                    self.get_model_steps(state)

                all_model_steps.update(model_steps)

                all_transitions.extend(next_states)

            # ----------------------------------------------------
            # Escaping Steps
            # ----------------------------------------------------

            escaping_steps = {
                step
                for step in all_model_steps
                if not self.step_matches(step, observed_step)
            }

            total_model_steps += len(all_model_steps)
            total_escaping_steps += len(escaping_steps)

            # ----------------------------------------------------
            # Nur Modellzustände behalten, die den beobachteten
            # Trace-Step erklären können.
            # ----------------------------------------------------

            matching_states = {
                next_state
                for step, next_state in all_transitions
                if self.step_matches(step, observed_step)
            }

            if not matching_states:
                return 0.0

            model_states = matching_states

        # --------------------------------------------------------
        # Escaping-Edges-Precision
        # --------------------------------------------------------

        if total_model_steps == 0:
            return 1.0

        return 1.0 - (
            total_escaping_steps /
            total_model_steps
        )

    # ------------------------------------------------------------
    # Precision über komplettes Event Log
    # ------------------------------------------------------------

    def calculate_log_precision(self, tree, traces):
        """
        Aggregiert die Precision über alle Traces.

        Jeder Trace wird entsprechend seiner Anzahl von
        beobachteten Modellschritten gewichtet.
        """

        total_model_steps = 0
        total_escaping_steps = 0

        for trace in traces:

            self.trace = trace

            trace_steps = self.get_trace_steps()

            if not trace_steps:
                continue

            model_states = {
                self.initial_model_state(tree)
            }

            for trace_step in trace_steps:

                observed_step = frozenset(
                    event.get_label()
                    for event in trace_step
                )

                all_model_steps = set()
                all_transitions = []

                for state in model_states:

                    model_steps, next_states = \
                        self.get_model_steps(state)

                    all_model_steps.update(model_steps)
                    all_transitions.extend(next_states)

                escaping_steps = {
                    step
                    for step in all_model_steps
                    if not self.step_matches(
                        step,
                        observed_step
                    )
                }

                total_model_steps += len(all_model_steps)
                total_escaping_steps += len(escaping_steps)

                matching_states = {
                    next_state
                    for step, next_state in all_transitions
                    if self.step_matches(
                        step,
                        observed_step
                    )
                }

                if not matching_states:
                    # Nicht-konformer Trace.
                    #
                    # Falls du Precision unabhängig von
                    # Conformance behandeln möchtest, kannst du
                    # diesen Trace stattdessen überspringen.
                    return 0.0

                model_states = matching_states

        if total_model_steps == 0:
            return 1.0

        return 1.0 - (
            total_escaping_steps /
            total_model_steps
        )

    # ============================================================
    # TRACE
    # ============================================================

    def get_trace_steps(self):
        """
        Zerlegt den Partial-Order-Trace in Parallel-Steps.

        Beispiel:

            A < C
            B < C
            A || B

        ergibt:

            [{A, B}, {C}]

        Nicht:

            [{A}, {B}, {C}]
        """

        remaining = set(self.trace.get_events())

        steps = []

        while remaining:

            enabled = {
                event
                for event in remaining
                if self.is_enabled(event, remaining)
            }

            if not enabled:
                raise ValueError(
                    "Partial order contains no executable next step."
                )

            # Alle gleichzeitig aktivierbaren Events bilden
            # aufgrund deiner Semantik EINEN Parallel-Step.
            steps.append(frozenset(enabled))

            remaining -= enabled

        return steps

    def is_enabled(self, event, remaining):
        """
        Ein Event ist enabled, wenn keiner seiner Vorgänger
        noch nicht ausgeführt wurde.
        """

        predecessors = self.get_predecessors(event)

        return not any(
            predecessor in remaining
            for predecessor in predecessors
        )

    def get_predecessors(self, event):
        """
        Liefert alle Vorgänger des Events aus dem strict partial
        order.

        Wir verwenden hier die transitive Ordnung.
        """

        order = self.trace.get_strict_partial_order()

        return {
            predecessor
            for predecessor, successor in order
            if successor == event
        }

    # ============================================================
    # RELATIONEN ZWISCHEN EVENTS
    # ============================================================

    def relation(self, e1, e2):

        if e1 == e2:
            return None

        order = self.trace.get_strict_partial_order()
        overlap = self.trace.get_overlapping_events()

        if (e1, e2) in order:
            return self.BEFORE

        if (e2, e1) in order:
            return self.AFTER

        if (e1, e2) in overlap:
            return self.OVERLAP

        if (e2, e1) in overlap:
            return self.OVERLAP

        # Deine Semantik:
        #
        # Wenn zwei Events nicht geordnet sind, sind sie
        # überlappend / parallel.
        return self.OVERLAP

    def all_before(self, events_a, events_b):

        return all(
            self.relation(a, b) == self.BEFORE
            for a in events_a
            for b in events_b
        )

    def all_overlap(self, events_a, events_b):

        return all(
            self.relation(a, b) == self.OVERLAP
            for a in events_a
            for b in events_b
        )

    def all_non_overlapping(self, events_a, events_b):

        return all(
            self.relation(a, b) in {
                self.BEFORE,
                self.AFTER
            }
            for a in events_a
            for b in events_b
        )

    # ============================================================
    # MODEL STATE
    # ============================================================

    def initial_model_state(self, tree):
        """
        Ein Modellzustand besteht aus dem aktuellen Node.

        Für zusammengesetzte Operatoren enthält der Zustand
        zusätzlich den Fortschritt der Kinder.
        """

        return self.make_state(tree)

    def make_state(self, node):
        """
        Erstellt einen initialen Zustand für einen Node.
        """

        # --------------------------------------------------------
        # Leaf
        # --------------------------------------------------------

        if len(node.children) == 0:
            return (
                "leaf",
                node.value
            )

        # --------------------------------------------------------
        # Sequence
        # --------------------------------------------------------

        if node.value == Operator.Sequence:

            return (
                "sequence",
                tuple(
                    self.make_state(child)
                    for child in node.children
                )
            )

        # --------------------------------------------------------
        # ArbitraryOrder
        # --------------------------------------------------------

        if node.value == Operator.Arbitrary:

            return (
                "arbitrary",
                tuple(
                    self.make_state(child)
                    for child in node.children
                )
            )

        # --------------------------------------------------------
        # Interleaving
        # --------------------------------------------------------

        if node.value == Operator.Interleaving:

            return (
                "interleaving",
                tuple(
                    self.make_state(child)
                    for child in node.children
                )
            )

        # --------------------------------------------------------
        # Concurrent
        # --------------------------------------------------------

        if node.value == Operator.Concurrent:

            return (
                "concurrent",
                tuple(
                    self.make_state(child)
                    for child in node.children
                )
            )

        # --------------------------------------------------------
        # Parallel
        # --------------------------------------------------------

        if node.value == Operator.Parallel:

            return (
                "parallel",
                tuple(
                    self.make_state(child)
                    for child in node.children
                )
            )

        # --------------------------------------------------------
        # Exclusive
        # --------------------------------------------------------

        if node.value == Operator.Exclusive:

            return (
                "exclusive",
                tuple(
                    self.make_state(child)
                    for child in node.children
                ),
                None
            )

        # --------------------------------------------------------
        # MultiInstance
        # --------------------------------------------------------

        if node.value == Operator.Multi:

            if len(node.children) != 1:
                raise ValueError(
                    "MultiInstance must have exactly one child."
                )

            child = node.children[0]

            if len(child.children) != 0:
                raise ValueError(
                    "MultiInstance child must be an activity."
                )

            if child.value == "tau":
                raise ValueError(
                    "MultiInstance child cannot be tau."
                )

            return (
                "multi_instance",
                child.value
            )

        # --------------------------------------------------------
        # Loop
        # --------------------------------------------------------

        if node.value == Operator.Loop:

            if len(node.children) < 2:
                raise ValueError(
                    "Loop must have at least two children."
                )

            body = self.make_state(node.children[0])

            redo = tuple(
                self.make_state(child)
                for child in node.children[1:]
            )

            return (
                "loop",
                body,
                redo,
                "body"
            )

        raise ValueError(
            f"Unknown operator: {node.value}"
        )

    # ============================================================
    # MODEL TRANSITIONS
    # ============================================================

    def get_model_steps(self, state):
        """
        Liefert:

            model_steps
            next_states

        model_steps:
            Menge der möglichen sichtbaren nächsten Steps.

        next_states:
            Liste von (step, next_state).
        """

        kind = state[0]

        # --------------------------------------------------------
        # Leaf
        # --------------------------------------------------------

        if kind == "leaf":

            label = state[1]

            if label == "tau":
                return set(), []

            step = frozenset({label})

            return (
                {step},
                [(step, ("done",))]
            )

        # --------------------------------------------------------
        # Done
        # --------------------------------------------------------

        if kind == "done":

            return set(), []

        # --------------------------------------------------------
        # Sequence
        # --------------------------------------------------------

        if kind == "sequence":

            children = list(state[1])

            # Fertige Kinder überspringen
            while children and children[0][0] == "done":
                children.pop(0)

            # Sequence komplett fertig
            if not children:
                return set(), []

            first = children[0]

            steps, transitions = \
                self.get_model_steps(first)

            next_states = []

            for step, next_child_state in transitions:

                new_children = (
                    [next_child_state] +
                    children[1:]
                )

                # tau / done kann dazu führen, dass die Sequence
                # direkt zum nächsten Kind weitergeht.
                new_state = (
                    "sequence",
                    tuple(new_children)
                )

                next_states.append(
                    (step, self.normalize_state(new_state))
                )

            return steps, next_states

        # --------------------------------------------------------
        # ArbitraryOrder
        # --------------------------------------------------------

        if kind == "arbitrary":

            children = list(state[1])

            children = [
                child
                for child in children
                if child[0] != "done"
            ]

            if not children:
                return set(), []

            model_steps = set()
            next_states = []

            for i, child in enumerate(children):

                steps, transitions = \
                    self.get_model_steps(child)

                for step, next_child_state in transitions:

                    new_children = children.copy()
                    new_children[i] = next_child_state

                    new_state = (
                        "arbitrary",
                        tuple(new_children)
                    )

                    new_state = self.normalize_state(
                        new_state
                    )

                    model_steps.add(step)
                    next_states.append(
                        (step, new_state)
                    )

            return model_steps, next_states

        # --------------------------------------------------------
        # Interleaving
        # --------------------------------------------------------

        if kind == "interleaving":

            children = list(state[1])

            children = [
                child
                for child in children
                if child[0] != "done"
            ]

            if not children:
                return set(), []

            model_steps = set()
            next_states = []

            for i, child in enumerate(children):

                steps, transitions = \
                    self.get_model_steps(child)

                for step, next_child_state in transitions:

                    new_children = children.copy()
                    new_children[i] = next_child_state

                    new_state = (
                        "interleaving",
                        tuple(new_children)
                    )

                    new_state = self.normalize_state(
                        new_state
                    )

                    model_steps.add(step)
                    next_states.append(
                        (step, new_state)
                    )

            return model_steps, next_states

        # --------------------------------------------------------
        # Concurrent
        # --------------------------------------------------------

        if kind == "concurrent":

            children = list(state[1])

            children = [
                child
                for child in children
                if child[0] != "done"
            ]

            if not children:
                return set(), []

            # Für jedes Kind:
            #
            # - entweder es macht in diesem Step nichts
            # - oder es macht einen möglichen Step
            #
            # Dadurch entstehen:
            #
            # {A}
            # {B}
            # {A,B}
            #
            # für Concurrent(A,B).

            child_options = []

            for child in children:

                steps, transitions = \
                    self.get_model_steps(child)

                options = [
                    (None, child)
                ]

                options.extend(
                    transitions
                )

                child_options.append(options)

            model_steps = set()
            next_states = []

            for combination in product(*child_options):

                selected = [
                    item
                    for item in combination
                    if item[0] is not None
                ]

                # Mindestens ein Kind muss einen sichtbaren Step
                # ausführen.
                if not selected:
                    continue

                combined_step = frozenset().union(
                    *(step for step, _ in selected)
                )

                new_children = []

                for original, option in zip(
                    children,
                    combination
                ):

                    step, next_state = option

                    if step is None:
                        new_children.append(original)
                    else:
                        new_children.append(next_state)

                new_state = (
                    "concurrent",
                    tuple(new_children)
                )

                new_state = self.normalize_state(
                    new_state
                )

                model_steps.add(combined_step)

                next_states.append(
                    (combined_step, new_state)
                )

            return model_steps, next_states

        # --------------------------------------------------------
        # Parallel
        # --------------------------------------------------------

        if kind == "parallel":

            children = list(state[1])

            children = [
                child
                for child in children
                if child[0] != "done"
            ]

            if not children:
                return set(), []

            child_transitions = []

            for child in children:

                steps, transitions = \
                    self.get_model_steps(child)

                # Ein nicht-tau Kinder muss einen sichtbaren
                # Step liefern.
                if not transitions:
                    return set(), []

                child_transitions.append(
                    transitions
                )

            model_steps = set()
            next_states = []

            for combination in product(
                *child_transitions
            ):

                combined_step = frozenset().union(
                    *(step for step, _ in combination)
                )

                new_children = [
                    next_state
                    for _, next_state in combination
                ]

                new_state = (
                    "parallel",
                    tuple(new_children)
                )

                new_state = self.normalize_state(
                    new_state
                )

                model_steps.add(combined_step)

                next_states.append(
                    (combined_step, new_state)
                )

            return model_steps, next_states

        # --------------------------------------------------------
        # Exclusive
        # --------------------------------------------------------

        if kind == "exclusive":

            children = state[1]
            selected = state[2]

            # Noch kein Zweig ausgewählt
            if selected is None:

                model_steps = set()
                next_states = []

                for child in children:

                    steps, transitions = \
                        self.get_model_steps(child)

                    for step, next_child_state in transitions:

                        new_state = (
                            "exclusive",
                            children,
                            next_child_state
                        )

                        model_steps.add(step)

                        next_states.append(
                            (step, new_state)
                        )

                return model_steps, next_states

            # Bereits ausgewählter Zweig
            steps, transitions = \
                self.get_model_steps(selected)

            return (
                steps,
                [
                    (
                        step,
                        (
                            "exclusive",
                            children,
                            next_state
                        )
                    )
                    for step, next_state in transitions
                ]
            )

        # --------------------------------------------------------
        # MultiInstance
        # --------------------------------------------------------

        if kind == "multi_instance":

            label = state[1]

            # Für Precision behandeln wir beliebig viele
            # parallele Instanzen desselben Labels als EINEN
            # Modell-Step.
            #
            # {A}
            #
            # repräsentiert also:
            #
            # A
            # A || A
            # A || A || A
            # usw.

            step = frozenset({label})

            return (
                {step},
                [
                    (
                        step,
                        state
                    )
                ]
            )

        # --------------------------------------------------------
        # Loop
        # --------------------------------------------------------

        if kind == "loop":

            body = state[1]
            redo_children = state[2]
            phase = state[3]

            # ----------------------------------------------------
            # Phase: body
            # ----------------------------------------------------

            if phase == "body":

                steps, transitions = \
                    self.get_model_steps(body)

                model_steps = set()
                next_states = []

                for step, next_body in transitions:

                    # Body ist fertig:
                    #
                    # Loop darf entweder enden oder ein redo
                    # ausführen.
                    if next_body[0] == "done":

                        # Loop kann hier enden.
                        model_steps.add(step)

                        next_states.append(
                            (step, ("done",))
                        )

                        # Oder danach in die redo-Phase gehen.
                        #
                        # Dafür müssen wir einen Zwischenzustand
                        # erzeugen.
                        if redo_children:

                            for redo in redo_children:

                                redo_steps, redo_transitions = \
                                    self.get_model_steps(redo)

                                for redo_step, next_redo in \
                                        redo_transitions:

                                    combined_step = frozenset(
                                        set(step) |
                                        set(redo_step)
                                    )

                                    # Diese Kombination wäre nur
                                    # dann ein gemeinsamer Step,
                                    # wenn Body und Redo parallel
                                    # wären. Das sind sie beim Loop
                                    # NICHT.
                                    #
                                    # Deshalb hier nur den Body-Step
                                    # als sichtbaren Übergang.
                                    #
                                    # Der Redo wird erst im nächsten
                                    # Modellzustand ausgeführt.

                                    new_state = (
                                        "loop",
                                        self.make_state_from_done_body(
                                            body
                                        ),
                                        redo_children,
                                        "redo"
                                    )

                                    model_steps.add(step)

                                    next_states.append(
                                        (step, new_state)
                                    )

                    else:

                        new_state = (
                            "loop",
                            next_body,
                            redo_children,
                            "body"
                        )

                        model_steps.add(step)

                        next_states.append(
                            (step, new_state)
                        )

                return model_steps, next_states

            # ----------------------------------------------------
            # Phase: redo
            # ----------------------------------------------------

            if phase == "redo":

                model_steps = set()
                next_states = []

                for redo in redo_children:

                    steps, transitions = \
                        self.get_model_steps(redo)

                    for step, next_redo in transitions:

                        new_state = (
                            "loop",
                            self.make_state_from_done_body(
                                body
                            ),
                            redo_children,
                            "body"
                        )

                        model_steps.add(step)

                        next_states.append(
                            (step, new_state)
                        )

                return model_steps, next_states

        raise ValueError(
            f"Unknown model state: {state}"
        )

    # ============================================================
    # STATE NORMALIZATION
    # ============================================================

    def normalize_state(self, state):
        """
        Entfernt abgeschlossene Zustände aus Operatoren.

        Wichtig für Sequence und andere Operatoren.
        """

        kind = state[0]

        if kind == "sequence":

            children = list(state[1])

            while children and children[0][0] == "done":
                children.pop(0)

            if not children:
                return ("done",)

            return (
                "sequence",
                tuple(children)
            )

        if kind == "arbitrary":

            children = tuple(
                child
                for child in state[1]
                if child[0] != "done"
            )

            if not children:
                return ("done",)

            return (
                "arbitrary",
                children
            )

        if kind == "interleaving":

            children = tuple(
                child
                for child in state[1]
                if child[0] != "done"
            )

            if not children:
                return ("done",)

            return (
                "interleaving",
                children
            )

        if kind == "concurrent":

            children = tuple(
                child
                for child in state[1]
                if child[0] != "done"
            )

            if not children:
                return ("done",)

            return (
                "concurrent",
                children
            )

        if kind == "parallel":

            children = tuple(
                child
                for child in state[1]
                if child[0] != "done"
            )

            if not children:
                return ("done",)

            return (
                "parallel",
                children
            )

        return state

    # ============================================================
    # LOOP HELPERS
    # ============================================================

    def make_state_from_done_body(self, body):
        """
        Erzeugt einen abgeschlossenen Body-Zustand.

        Wird für den Loop-Zustand benötigt.
        """

        return ("done",)

    # ============================================================
    # PARTITION HELPERS
    # ============================================================

    def partitions(self, events, k):
        """
        Erzeugt Partitionen eines Event-Sets in k nichtleere
        Teilmengen.

        Wird beispielsweise für Operatoren benötigt, bei denen
        mehrere Kinder Event-Teilsets erklären.
        """

        events = tuple(events)

        if k == 1:
            if events:
                yield (frozenset(events),)
            return

        if len(events) < k:
            return

        for size in range(
            1,
            len(events) - k + 2
        ):

            for subset in combinations(
                events,
                size
            ):

                first = frozenset(subset)

                remaining = (
                    frozenset(events) -
                    first
                )

                for rest in self.partitions(
                    remaining,
                    k - 1
                ):
                    yield (
                        first,
                    ) + rest

    # ============================================================
    # STEP COMPARISON
    # ============================================================

    def step_matches(
        self,
        model_step,
        observed_step
    ):
        """
        Prüft, ob ein Modell-Step zum beobachteten Trace-Step passt.

        Für normale Operatoren gilt:

            model_step == observed_step

        Dadurch ist beispielsweise:

            Parallel(A,B)

        kompatibel mit:

            {A,B}

        aber nicht mit:

            {A}

        MultiInstance wird bereits beim Generieren des
        Modell-Steps auf {A} normalisiert.
        """

        return model_step == observed_step
