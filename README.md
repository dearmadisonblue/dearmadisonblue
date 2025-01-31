🐦 ———

Thinking of a command and control for LLMs: the idea is that an LLM
*always* writes Forth-like code to a socket to execute on the server
within a per-client dictionary, and the server always responds in
natural language; even when the LLM wants to talk to people it uses
Forth commands that mimic Twitter or IRC, which lets it communicate
values as well as text.

---

Both AIXI and computability logic use the concept of a computer
playing against an environment; while AIXI assumes the environment is
Turing-computable, computability logic allows the environment to be
arbitrary. Since "Turing-computable" means "first order computable"
it's a little strange to assume that the environment is
Turing-computable.

[From "The philosophy of computability logic":](http://www.csc.villanova.edu/~japaridz/CL/1.html):

> It is natural to require that the interaction strategies of the party
> that we have referred to as an “agent” be limited to algorithmic ones,
> allowing us to henceforth call that player a machine.  This is a
> minimum condition that any non-esoteric game semantics would have to
> satisfy. On the other hand, no restrictions can or should be imposed
> on the environment, who represents a capricious user, the blind forces
> of nature, or the devil himself. Algorithmic activities being
> synonymous to computations, games thus represent computational
> problems --- interactive tasks performed by computing agents, with
> computability meaning winnability, i.e. existence of a machine that
> wins the game against any possible (behavior of the) environment.

---

Geometric algebra + computability logic + interaction nets for deep
learning.

📖 ———

- Fundamentals of Computability Logic

> Computability is a property of computational problems and, before
> attempting to talk about the former, we need to agree on the precise
> meaning of the latter. According to the mainstream understanding
> going back to Church and Turing, a computational problem is a
> function—more precisely, the task of systematically generating the
> values of that function at different arguments. Such a view,
> however, as more and more researchers have been acknowledging, is
> too narrow. Most tasks performed by computers are interactive, far
> from being as simple as functional transformations from inputs to
> outputs. Think of the work of a network server for instance, where
> the task is to maintain a certain infinite process, with incoming
> (“input”) and outgoing (“output”) signals interleaved in some
> complex and probably unregulated fashion, depending on not only
> immediately preceding signals but also various events taken place in
> the past. In an attempt to advocate for the conventional view of
> computational problems, one might suggest to understand an
> interactive computational task as the task of repeatedly computing
> the value of a function whose argument is not just the latest input
> but the whole preceding interaction. This is hardly a good solution
> though, which becomes especially evident with computational
> complexity considerations in mind. If the task performed by your
> personal computer was like that, then you would have noticed its
> performance worsening after every use due to the need to read the
> ever longer history of interaction with you.
>
> Instead, computability logic postulates that a computational problem
> is a game between two agents: a machine and its environment,
> symbolically named ⊤ and ⊥, respectively. ⊤ is a mechanical device
> only capable of following algorithmic strategies, while there are no
> similar assumptions about ⊥ whose behavior can be
> arbitrary. Computational tasks in the traditional sense now become
> special cases of games with only two moves, where the first move
> (“input”) is by ⊥ and the second move (“output”) by ⊤.


- From Formulas to Cirquents in Computability Logic
- Introduction to Cirquent Calculus and Abstract Resource Semantics
- Cirquent Calculus Deepened

---

- Higher-Order Computability
- Notions of Computability at Higher Types I

> In elementary recursion theory, one begins with the question: what
> does it mean for an ordinary first order function on N to be
> “computable”? As is well known, many different approaches to
> defining a notion of computable function — via Turing machines,
> lambda calculus, recursion equations, Markov algorithms, flowcharts,
> etc. — lead to essentially the same answer, namely the class of
> (total or partial) recursive functions. Indeed, Church’s thesis
> proposes that for functions from N to N we identify the informal
> notion of an “effectively computable” function with the precise
> mathematical notion of a recursive function.
> 
> An important point here is that many prima facie independent
> mathematical constructions lead to the same class of
> functions. Whilst one can argue over whether this is good evidence
> that the recursive functions include all effectively computable
> functions (see Odifreddi [1989] for a discussion), it is certainly
> good evidence that they represent a mathematically natural and
> robust class of functions. And since no other serious contenders for
> a class of effectively computable functions are known, most of us
> are happy to accept Church’s thesis most of the time.
> 
> Now suppose we consider second order functions which map first order
> functions to natural numbers (say), and then third order functions
> which map second order functions to natural numbers, and so on. We
> will use the word functional to mean a function that takes functions
> of some kind as arguments. We may now ask: what might it mean at
> these higher types for a functional to be “computable”?
> 
> A moment’s reflection shows that a host of choices confront us if we
> wish to formulate a definition of higher type computability. For
> example:
>
> • Domain of definition. Do we wish to consider partial or total
> computable functionals? Do we want them to act on partial functions
> of the next type down, or just on total functions? Should they act
> only on the “computable” functions of this type, or on some wider
> class of functions?
>
> • Representation of functions. If we wish to perform “computations”
> on functions, how do we regard the functions as given to us? As
> infinite graphs? As algorithms or “programs” of some kind? Or as
> oracles or “black boxes”, for which we only have access to the
> input/output behaviour?
>
> • Protocol for computation. What ways of interacting with functions
> do we allow in computations? For example, do we insist that calls to
> functions are performed sequentially, or do we allow parallel
> function calls? Do we insist that terminating computations are in
> some sense finite mathematical objects, as must be the case if we
> are seeking a genuinely effective notion of computability — or do we
> allow infinite computations in accordance with the infinitistic
> nature of the arguments?
>
> • Extensionality. Do we want to restrict our attention to computable
> functions (as implicitly assumed in the preceding discussion)? Or do
> we want to consider computability for other, possibly
> non-extensional, operations of higher type? If the latter, what do
> we mean by an “operation”?
>
> The spirit in which we are asking these questions is not to demand
> definitive answers to them, but to make the point that many choices
> are possible. Indeed, as we shall see, many different responses to
> the above questions are exemplified by the definitions of higher
> type computability that have been proposed in the
> literature. Moreover, the effects of all these choices escalate
> rapidly as we climb up the types. For example, if two definitions
> yield different classes of computable functions of type ó, it may be
> difficult even to compare these definitions at type ó → N, since the
> domains of the functions may differ. Indeed, we often find that a
> question needs to have a positive answer at type ó in order to be
> even meaningful at type ó → N.
>
> It thus appears that very many approaches to defining higher type
> computability are possible, but it is not obvious a priori whether
> some approaches are more sensible than others, or which approaches
> lead to equivalent notions of computability. Moreover, in contrast
> to the first order situation, there does not seem to be a clear
> canonical pre-formal notion of “effective computability at higher
> types” to which we can refer for guidance. (This is hardly
> surprising, in view of the fact that there are several possible
> pre-formal conceptions of what a function is.)  In short, it is
> unclear in advance whether at higher types there is really just one
> natural notion of computability (as in ordinary recursion theory),
> or several, or indeed no really natural notions at all.

- Notions of Computability at Higher Types II

---

- Laws, Language and Life
- Closure to Efficient Causation, Computability and Artificial Life
- Computational Life: How Well-Formed, Self-Replicating Programs
Emerge from Simple Interaction
- Life as Evolving Software

---

- Emptiness and Becoming: Integrating Madhyamika Buddhism and Process Philosophy
