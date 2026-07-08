DEAD ENDS IN SQUARE-FREE DIGIT WALKS
EVAN CHEN†
, CHRIS CUMMINS*
, BEN ELTSCHIG*
, DEJAN GRUBISIC*
, LEOPOLD HALLER*
,
LETONG HONG⋄
, ANDRANIK KURGHINYAN*
, KENNY LAU†*
, HUGH LEATHER*
, SEEWOO LEE†
,
ARAM MARKOSYAN*
, KEN ONO†
, MANOOSHREE PATEL*
, GAURANG PENDHARKAR*
,
VEDANT RATHI*
, ALEX SCHNEIDMAN*
, VOLKER SEEKER*
, SHUBHO SENGUPTA⋄
, ISHAN SINHA*
,
JIMMY XIN*
, AND JUJIAN ZHANG†*
Authors are listed alphabetically.
†Mathematical contributor, *Engineering contributor, ⋄Principal investigator.
Abstract. We study “dead ends” in square-free digit walks: square-free integers N such that, in
base b, every one-digit extension bN+d is non-square-free. In base 10, the stochastic independence
model of [5] suggests that infinite square-free walks occur with probability near 1, corresponding
to an asymptotic dead-end density of ≈ 5.218×10−5
. We prove that the true asymptotic dead-end
density satisfies
cdead ≈ 1.317 × 10−9
,
roughly a factor of ∼ 4 × 104
smaller than the prediction. For every base b ≥ 2, we prove
that dead-end densities exist and are given by a closed-form expression (as a finite alternating
sum of Euler products). The argument is fully formalized in Lean/Mathlib, and was produced
automatically by AxiomProver from a natural-language statement of the problem.
Update
After we posted the first version of this manuscript on the arXiv, we learned from Kannan
Soundararajan that the result in this paper was previously obtained by Mirsky in 1947 [6]. We
mistakenly assumed that the 2024 paper of Miller et al. [5] accurately represented the status
of this question. Their paper makes no reference to Mirsky [6]; that work seems to have been
forgotten. Although our Lean formalization still stands, this manuscript will not be submitted
for journal publication.
1. Introduction
For a positive integer N and a digit d ∈ {0, 1, . . . , 9}, define the right-append map
Td(N) := 10N + d.
A positive integer is square-free if it is not divisible by any perfect square > 1. We study squarefree walks. Starting with a square-free integer N0, we attempt to form a sequence N0, N1, N2, . . .
Axiom Math, 124 University Avenue, Palo Alto, CA 94301
E-mail addresses: evan@axiommath.ai, chris@axiommath.ai, ben@axiommath.ai,
dejan@axiommath.ai, leo@axiommath.ai, carina@axiommath.ai, andranik@axiommath.ai,
kenny@axiommath.ai, hugh@axiommath.ai, seewoo@axiommath.ai, am@axiommath.ai,
ken@axiommath.ai, manooshree@axiommath.ai, gaurang@axiommath.ai, vedant@axiommath.ai,
alex@axiommath.ai, volker@axiommath.ai, shubho@axiommath.ai, ishan@axiommath.ai,
jimmy@axiommath.ai, jujian@axiommath.ai.
2010 Mathematics Subject Classification. 11A63, 11B83, 11N05.
Key words and phrases. stochastic process, integer sequences.
1
arXiv:2602.05095v2 [math.CO] 6 Feb 2026
2 DEAD ENDS IN SQUARE-FREE DIGIT WALKS
by successively appending digits such that every term in the sequence remains square-free. For
example, starting with N = 5, we have
T6(5) = 56 = 23
· 7
Fail
−−→ (Divisible by the square 22
),
T1(5) = 51 = 3 · 17 Success
−−−−→ (Square-free).
So although T6(5) fails, we can continue with 51 and we find that
T3(51) = 513 = 33
· 19 Fail
−−→ (Divisible by the square 32
),
T9(51) = 519 = 3 · 173 Success
−−−−→ (Square-free).
Starting with any N0, this process defines a tree, where branches terminate when appending a
digit results in a non-square-free integer. This process inspires a natural question.
Question. Is it possible to continue such a walk indefinitely? In other words, can we walk to
infinity along the square-free integers? Are there trees with infinitely long branches?
This question is raised in [5] by Miller et al., and the following conjecture is posed.
Conjecture (Miller et al. [5]). There exists an infinite sequence of square-free integers
{N0, N1, N2, N3, . . . }
and digits dk+1 ∈ {0, 1, . . . , 9} such that Nk+1 = 10Nk + dk+1 for all k ≥ 0.
Remark. The paper by Miller et al. [5] considers further walks. A recent paper by Kominers [2]
proves that similar walks are impossible in the setting of Fibonacci numbers and Lucas numbers.
Despite its innocent appearance, this conjecture remains open. In particular, no one has
exhibited an explicit infinite sequence of digits that provably generates square-free integers at
every step, nor has the existence of such a walk been established.
Miller et al. [5] analyze this conjecture using a stochastic framework called the “Blind Unlimited
Model,” where square-freeness is treated as a random event with independent probability 6/π2
,
the asymptotic density of square-free integers among the positive integers. They model the 10
potential digit extensions as a branching process, and they calculate that the probability of the
entire tree going extinct is only ℓ ≈ 8.6 × 10−5
. This implies that an infinite walk from a given
N0 exists with probability ≈ 0.99991. To make this precise, we make the following definition.
Definition. A positive integer N is a dead end if
(1) N is square-free, and
(2) for every digit d ∈ {0, 1, . . . , 9}, the integer 10N + d is not square-free.
The stochastic heuristic predicts the asymptotic density of dead ends in terms of ρ := 6
π2 and
the counting function
(1) D(X) := # {1 ≤ N ≤ X : N is a dead end} .
Stochastic Prediction (Miller et al. [5]). If we define Pk to be the probability that the rooted
digit-walk tree generated from a square-free root has finite height at most k, then we have:
(1) P1 is the probability that the root has no square-free children (no digit can be added), so
P1 = (1 − ρ)
10
.
DEAD ENDS IN SQUARE-FREE DIGIT WALKS 3
(2) More generally, the tree has height ≤ k + 1 exactly when, for each digit d, either 10N + d
is not square-free (probability 1−ρ), or else 10N +d is square-free (probability ρ) and the
subtree rooted at 10N + d has height ≤ k (probability Pk). By the independence heuristic
across digits, this yields the recursion
Pk+1 =

(1 − ρ) + ρPk
10 (k ≥ 1).
The “extinction probability” (i.e. the probability that the entire tree is finite, equivalently that
there is no infinite square-free walk) is predicted to be the limit
ℓ := lim
k→∞
Pk ≈ 8.59502 × 10−5
.
Taking into account the possibility that N0 might not be square-free, the stochastic prediction for
the asymptotic density for dead ends is
lim
X→+∞
D(X)
X
≈
6
π
2
· P1 ≈ 5.21818 × 10−5
.
Although dead ends are expected to be very rare, occurring with near zero density, it is possible
to show explicit examples. Indeed, Miller et al. offer the example N = 231546210170694222,
where we find that
2315462101706942220 = 22
· 578865525426735555,
2315462101706942221 = 112
· 19136050427330101,
2315462101706942222 = 192
· 6414022442401502,
2315462101706942223 = 72
· 47254328606264127,
2315462101706942224 = 24
· 144716381356683889,
2315462101706942225 = 52
· 92618484068277689,
2315462101706942226 = 33
· 85757855618775638,
2315462101706942227 = 132
· 13700959181697883,
2315462101706942228 = 22
· 578865525426735557,
2315462101706942229 = 172
· 8011979590681461.
This motivates the following concrete, non-stochastic question about actual integers. Exactly how
rare are dead ends? Is the stochastic prediction correct? Despite the convincing evidence that
such stochastic models are accurate for many questions, here we prove that stochastic reasoning
gives the wrong answer when applied to dead ends. Dead ends are orders of magnitude rarer
than the stochastic prediction.
For convenience, we define D := {0, 1, 2, . . . , 9} to be the set of base 10 digits.
Theorem 1.1 (Asymptotic density of dead ends). For all X ≥ 3, we have
D(X) = cdead X + O

X
√
log X

,
where the constant is
cdead := X
S⊆D
(−1)|S| Y
p prime

1 −
νp(S)
p
2

,
4 DEAD ENDS IN SQUARE-FREE DIGIT WALKS
and where for each subset S ⊆ D we define
νp(S) := #n
n mod p
2
: p
2
| n or p
2
| (10n + d) for some d ∈ S
o
.
Moreover, have that cdead ≈ 1.3170 × 10−9
.
Remark. The main result of this paper shows that the stochastic prediction is far from the truth
for dead ends. The reason is arithmetic. For each prime p ≥ 7, the condition p
2
| (10n+d) forces
n into a single residue class modulo p
2
, so one prime square can “explain” at most one digit
obstruction at a time. For all ten digits to fail square-freeness simultaneously, many distinct
prime squares must be involved, creating strong dependence that the naive stochastic model
misses.
While Theorem 1.1 focuses on base 10, the phenomenon of unavoidable dead ends is universal.
The proof of Theorem 1.1 generalizes easily mutatis mutandis to give a general theorem for all
bases b ≥ 2. Specifically, we can restate the problem for general b ≥ 2 as follows.
Main Problem. Fix an integer base b ≥ 2, and let
Db := {0, 1, 2, . . . , b − 1}.
A positive integer N is a base b dead end if N is square-free and, for every digit d ∈ Db, the
integer bN + d is not square-free. Define the counting function
Db(X) := #{1 ≤ N ≤ X : N is a base-b dead end}.
Determine, with proof, the constant cdead(b) such that
Db(X) = cdead(b) X + ob(X).
Namely, we have following general theorem.
Theorem 1.2 (Asymptotic density of dead ends in base b). For all X ≥ 3, we have
Db(X) = cdead(b) X + Ob

X
√
log X

,
where cdead(b) is the well-defined positive constant
cdead(b) := X
S⊆Db
(−1)|S| Y
p prime

1 −
νp,b(S)
p
2

,
and for each prime p and each subset S ⊆ Db we define
νp,b(S) := #n
n mod p
2
: p
2
| n or p
2
| (bn + d) for some d ∈ S
o
.
Examples. Using the formulas in Theorem 1.2, we computed approximations for the dead-end
densities for the prime bases b ∈ {2, 3, 5, 7}.
b 2 3 5 7
cdead(b) 4.13253 × 10−2 9.44842 × 10−3 8.16352 × 10−5 3.08003 × 10−6
Table 1. Dead-end density constant cdead(b) for primes b ∈ {2, 3, 5, 7}.
DEAD ENDS IN SQUARE-FREE DIGIT WALKS 5
Remark. This work is a case study and test case for AxiomProver, an AI tool currently under
development, aimed at end-to-end automated theorem proving in mainstream mathematics. We
provided a natural-language formulation of the Main Problem. AxiomProver correctly discovered
the formula for cdead(b) without any further input, then generated a Lean/Mathlib statement
and a fully verified proof. Using that formal development as a reference point, we prepared the
exposition in the main text for a mathematical audience, aiming to supply context, motivation,
and a streamlined derivation that can be read independently of the Lean code.
This paper is organized as follows. In Section 2 we recall a few facts from elementary number theory that we then employ to prove Theorem 1.1. We also give a sketch of the proof of
Theorem 1.2. In Section 3 we document the formalization, clarifies the experimental conditions
under which the system was evaluated, and provides links to the relevant files for interested
readers (Mathematicians not interested in automated theorem proving can thus safely ignore
Section 3.) Finally, in the Appendix we give formulas that one can use to compute cdead to
arbitrary precision.
Acknowledgements
The authors thank Steven J. Miller and Scott Kominers for their comments on an earlier
version of this paper. We thank Kannan Soundararajan for informing us that the result in this
paper was previously obtained by Mirsky in 1947 [6] after the first version of this manuscript
was posted to the arXiv.
2. Proof of Theorems 1.1 and 1.2
This section collects the precise tools we will use. Everything here is standard elementary
multiplicative number theory (for example, see [1]). We require the M¨obius function µ : Z≥1 →
{−1, 0, 1} which is defined by µ(1) = 1 and for n ≥ 2 by
µ(n) = (
0, if p
2
| n for some prime p,
(−1)k
, if n = p1p2 · · · pk is a product of k distinct primes.
This function has many properties, and here we make use of the simple fact that for every integer
n ≥ 1, we have
(2) µ(n)
2 =
(
1 if n is square-free,
0 otherwise
.
In other words, the square of the M¨obius function is the square-free indicator function.
We will repeatedly use the elementary counting fact that for fixed integers M ≥ 1 and a, the
number of integers 1 ≤ n ≤ X with n ≡ a (mod M) equals X
M + O(1), with an absolute implied
constant. We shall also make critical use of this form of the Chinese Remainder Theorem.
Lemma 2.1 (Chinese remainder theorem (CRT)). Let M1, . . . , Mk be pairwise coprime moduli.
For each i, let Ai be a set of residue classes modulo Mi
. Then the number of residue classes
modulo M = M1 · · · Mk whose reduction modulo Mi
lies in Ai for all i is exactly Qk
i=1 |Ai
|.
Proof. The CRT states that the reduction map
Z/MZ −→ Y
k
i=1
Z/MiZ
6 DEAD ENDS IN SQUARE-FREE DIGIT WALKS
is a bijection. Therefore specifying residues modulo each Mi
independently specifies a unique
residue modulo M. Counting choices gives the product formula. □
2.1. Inclusion-Exclusion Framework. The proof of Theorems 1.1 and 1.2 is based on an
inclusion-exclusion argument, combined with some analytic number theory. For Theorem 1.1,
we have the digit set d ∈ D := {0, 1, . . . , 9}. Furthermore, define the statement
Ad(n) := “10n + d is square-free”.
Therefore, n is a dead end exactly when n is square-free and none of the Ad(n) hold. Using the
identity 1m square-free = µ(m)
2
(see (2)), we obtain the dead-end indicator identity
(3) 1n is a dead end = µ(n)
2 Y
d∈D

1 − µ(10n + d)
2

.
Indeed, the µ(n)
2
factor guarantees that n is square-free, while the vanishing of products requires
each of the 10n + d values is non-square-free.
Expanding this product by inclusion–exclusion yields the following closed formula for the
counting function D(X).
Proposition 2.2 (Exact digit inclusion–exclusion). For every X ≥ 1, we have
D(X) = X
S⊆D
(−1)|S| QS(X),
where
QS(X) := X
n≤X
µ(n)
2 Y
d∈S
µ(10n + d)
2
.
Proof. Expand Q
d∈D(1 − µ(10n + d)
2
) into a sum over subsets S ⊆ D, where choosing d ∈ S
contributes the factor −µ(10n+d)
2 and choosing d /∈ S contributes 1. Then sum over n ≤ X. □
Therefore, the proof of Theorem 1.1 reduces to asymptotics for QS(X) for each fixed S.
2.2. Asymptotics for QS(X). Fix a subset S ⊆ D and write r = |S|. Then QS(X) counts
those integers n ≤ X for which n and all one-digit extensions 10n + d (d ∈ S) are square-free:
(4)
QS(X) = X
n≤X
µ(n)
2 Y
d∈S
µ(10n + d)
2
= #{n ≤ X : n and 10n + d are square-free for all d ∈ S}.
A positive integer is square-free if and only if it is not divisible by p
2
for any prime p. Therefore,
the condition counted by QS(X) can be expressed prime-by-prime. Namely, for each prime p,
define the set of bad residues modulo p
2
Bp(S) := n
n mod p
2
: p
2
| n or p
2
| (10n + d) for some d ∈ S
o
,
and let νp(S) := |Bp(S)|.
To obtain asymptotics for QS(X), we carefully sift by finitely many prime squares. To this
end, let z ≥ 2 and set
P(z) := Y
p≤z
p prime
p and M(z) := P(z)
2
.
DEAD ENDS IN SQUARE-FREE DIGIT WALKS 7
Define the z–sifted counting function
QS(X; z) := #{n ≤ X : n mod p
2 ∈/ Bp(S) for every prime p ≤ z},
and the corresponding finite Euler product
(5) Cz(S) := Y
p≤z
p prime

1 −
νp(S)
p
2

.
Lemma 2.3 (Counting the z–sifted set). For every X ≥ 1 and every z ≥ 2, we have
QS(X; z) = Cz(S) X + O(M(z)).
Proof. For a fixed prime p ≤ z, the condition “n mod p
2 ∈/ Bp(S)” excludes exactly νp(S) residue
classes modulo p
2
, so it allows exactly p
2 − νp(S) residue classes modulo p
2
. Since the moduli p
2
are pairwise coprime as p varies over primes, the CRT (Lemma 2.1) implies that the number of
residue classes modulo
M(z) = Y
p≤z
p prime
p
2
that are simultaneously allowed for every prime p ≤ z is exactly
Gz(S) := Y
p≤z

p
2 − νp(S)

.
Each such residue class modulo M(z) contributes X
M(z) + O(1) integers n ≤ X. Summing over
the Gz(S) allowed classes gives
QS(X; z) = Gz(S)

X
M(z)
+ O(1)
=
Gz(S)
M(z)
X + O

Gz(S)

.
Finally, Gz(S) ≤ M(z), so the error term is O(M(z)), and
Gz(S)
M(z)
=
Y
p≤z

1 −
νp(S)
p
2

= Cz(S). □
The previous lemma only takes into account the primes p ≤ z. The next lemma bounds the
contributions to QS(X) from the larger primes.
Lemma 2.4 (Bounding the contribution of large prime squares). If z ≥ 5, then for every X ≥ 1
we have
QS(X) = QS(X; z) + O

(|S| + 1) 
X
z
+
√
X
 .
Proof. Any n counted by QS(X; z) but not counted by QS(X) has the property that for some
prime p > z at least one of the integers
n, 10n + d (d ∈ S)
is divisible by p
2
. Since 10n + d ≤ 10X + 9 for n ≤ X, such a prime must satisfy p
2 ≤ 10X + 9
(i.e. p ≤
√
10X + 9). Since z ≥ 5, every prime p > z satisfies p ≥ 7, and hence 10 is invertible
modulo p
2
. Therefore, for each d ∈ S the congruence p
2
| (10n + d) forces n into exactly one
residue class modulo p
2
, and the congruence p
2
| n forces n ≡ 0 (mod p
2
). In either case, the
number of solutions n ≤ X is X
p
2 + O(1).
8 DEAD ENDS IN SQUARE-FREE DIGIT WALKS
By the union bound, the number of n ≤ X excluded by primes p > z is therefore at most
X
p>z
p prime
X
forms L
L∈{n}∪{10n+d: d∈S}

X
p
2
+ O(1)
,
where the prime sum may be restricted to p ≤
√
10X + 9. There are exactly |S| + 1 forms L, so
this is
(|S| + 1)

X
X
z<p≤
√
10X+9
1
p
2
+ O

π(
√
10X + 9)

 ,
where π(y) denotes the number of primes ≤ y. We bound the two quantities crudely but explicitly:
X
z<p≤
√
10X+9
p prime
1
p
2
≤
X
n>z
1
n2 ≪
1
z
and π(
√
10X + 9) ≤
√
10X + 9 ≪
√
X.
Combining these bounds gives the claimed error term. □
It is important to consider the limiting behavior of the constants in (5) as z → +∞.
Lemma 2.5 (Convergence of the Euler product). The infinite product
C(S) := Y
p prime

1 −
νp(S)
p
2

converges absolutely. Moreover, for every z ≥ 7, we have
C(S) = Cz(S) + O

1
z

.
Proof. For the primes p ≤ 5, the factors 
1 −
νp(S)
p
2

are well-defined real numbers in [0, 1]. We
therefore focus on primes p ≥ 7. Since p ∤ 10, the number 10 is invertible modulo p
2
. Thus p
2
| n
forces n ≡ 0 (mod p
2
) (one residue class), and for each digit d ∈ S the congruence p
2
| (10n + d)
forces n into a single residue class modulo p
2
. Taking the union over d ∈ S shows that
νp(S) ≤ 1 + |S| ≤ 11.
In particular, for every p ≥ 7 we have 0 ≤ νp(S)/p2 ≤ 11/49 < 1/2.
Now consider the partial products over primes in [7, N]:
PN := Y
7≤p≤N
p prime

1 −
νp(S)
p
2

.
Taking logarithms and using the inequality |log(1 − u)| ≤ 2u valid for 0 ≤ u ≤ 1/2, we obtain
X
p≥7
p prime




log
1 −
νp(S)
p
2




≤ 2
X
p≥7
p prime
νp(S)
p
2 ≪
X
p≥7
p prime
1
p
2
< ∞.
DEAD ENDS IN SQUARE-FREE DIGIT WALKS 9
Therefore the series P
p≥7
log
1 −
νp(S)
p
2

converges absolutely, so the sequence log PN converges
as N → ∞, and hence PN converges to a finite nonzero limit. This proves absolute convergence
of C(S).
For the tail estimate, write
C(S) = Cz(S) ·
Y
p>z
p prime

1 −
νp(S)
p
2

.
For z ≥ 7, we have 0 ≤ νp(S)/p2 ≤ 11/49 < 1/2 for every p > z, so again using |log(1 − u)| ≤ 2u
gives







log


Y
p>z
p prime

1 −
νp(S)
p
2










≤ 2
X
p>z
p prime
νp(S)
p
2 ≪
X
n>z
1
n2 ≪
1
z
.
Exponentiating yields Q
p>z 
1 −
νp(S)
p
2

= 1 + O(1/z), and hence C(S) = Cz(S) + O(1/z). □
Assembling these observations, we obtain the final asymptotic for QS(X).
Proposition 2.6 (Asymptotic for QS(X)). For all X ≥ 3, we have
QS(X) = C(S) X + O

X
√
log X

,
where
C(S) = Y
p prime

1 −
νp(S)
p
2

.
Proof. Let z := max{7, ⌊
√
log X⌋}, so z ≥ 7 and z → ∞ as X → ∞. Combining Lemma 2.3
with Lemma 2.4, we obtain
QS(X) = Cz(S) X + O(M(z)) + O

(|S| + 1) 
X
z
+
√
X
 .
By Lemma 2.5, we have C(S) = Cz(S) + O(1/z), which in turn gives
Cz(S) X = C(S) X + O

X
z

.
Combining the last two expressions gives
QS(X) = C(S) X + O

M(z) + X
z
+
√
X

.
It remains to bound M(z) in terms of X. Since
P(z) = Y
p≤z
p ≤ z
π(z) ≤ z
z
we obtain
M(z) = P(z)
2 ≤ z
2z
.
With z = max{7, ⌊
√
log X⌋}, we have log z ≪ log log X, so
log M(z) ≤ 2z log z ≪
p
log X log log X = o(log X).
10 DEAD ENDS IN SQUARE-FREE DIGIT WALKS
In particular, M(z) = o

√
X
log X

as X → ∞. Also, since z ≍
√
log X and √
X = o

√
X
log X

, we
conclude that
QS(X) = C(S) X + O

X
√
log X

,
as claimed. □
2.3. Proof of Theorem 1.1. Finally, combine Proposition 2.2 with Proposition 2.6. We obtain
D(X) = X
S⊆D
(−1)|S|

C(S) X + O

X
√
log X
 =
 X
S⊆D
(−1)|S|C(S)
!
X + O

X
√
log X

.
The constant in parentheses is exactly cdead as defined in Theorem 1.1. Since there are only
2
10 = 1024 subsets S, the error term remains O

√
X
log X

. This completes the proof. □
2.4. Proof of Theorem 1.2. The proof is a direct adaptation of the base-10 argument in
Theorem 1.1, with the digit set and the relevant congruences replaced by their base-b analogues.
Here we explain how this is done.
Fix an integer base b ≥ 2 and write
Db := {0, 1, . . . , b − 1}.
A positive integer N is a base-b dead end if N is square-free and bN + d is not square-free for
every d ∈ Db. Using 1m square-free = µ(m)
2
, we obtain the modified indicator identity
1N is a base-b dead end = µ(N)
2 Y
d∈Db

1 − µ(bN + d)
2

,
and expanding the product yields the inclusion–exclusion formula
Db(X) = X
S⊆Db
(−1)|S| X
N≤X
µ(N)
2 Y
d∈S
µ(bN + d)
2
.
For each prime p and S ⊆ Db, define the local obstruction count
νp,b(S) := #n
n mod p
2
: p
2
| n or p
2
| (bn + d) for some d ∈ S
o
.
Exactly as in the proof of Theorem 1.1, one analyzes the congruences modulo p
2 and uses the
Chinese remainder theorem to conclude that the main term for each fixed S is an Euler product
with local factor 1 − νp,b(S)/p2
. Summing over S gives the constant cdead(b) from Theorem 1.2.
If p ∤ b, then b is invertible modulo p
2 and each condition p
2
| (bn + d) is equivalent to the
single congruence
n ≡ −d b−1
(mod p
2
).
Thus, for primes with p
2 > b these residue classes are distinct as d varies, so (up to the overlap
when d = 0) one has the same phenomenon as in base 10: a single prime square can obstruct at
most one digit at a time. This yields the base-b analogue of the computation of νp,b(S) for all
sufficiently large primes p ∤ b.
When p | b, b is not invertible modulo p
2
, so the congruence p
2
| (bn + d) requires separate
treatment (the analogue of our special handling of p = 2 and p = 5 in base 10). Likewise,
for the finitely many primes with p
2 ≤ b, distinct digits may collide modulo p
2
, and these are
again handled by a direct residue-class count. Since there are only finitely many such primes
DEAD ENDS IN SQUARE-FREE DIGIT WALKS 11
(depending on b), this only modifies finitely many Euler factors and does not affect the structure
of the argument.
Combining the inclusion–exclusion expansion with the prime-by-prime sieve computation, we
obtain the stated asymptotic
Db(X) = cdead(b) X + Ob

X
√
log X

,
with cdead(b) given by the finite alternating sum of Euler products in Theorem 1.2. □
3. AxiomProver
At Axiom Math, we are developing AxiomProver, an AI system for mathematical research via
formal proof. As an early test case in this effort, we present this case study, treating Theorem 1.2
as an end-to-end formalization target. We chose them because we believed that they are within
reach of today’s Mathlib.
This paper confirms that expectation: the proof is fully formalized in Lean/Mathlib (see [3, 4])
and was produced by AxiomProver from a natural-language statement of the Main Problem
(without the answer given). We now make precise what “produced” means, and describes the
end-to-end pipeline we used.
Process. The formal proofs provided in this work were developed and verified using Lean
4.26.0. Compatibility with earlier or later versions is not guaranteed due to the evolving nature
of the Lean 4 compiler and its core libraries. The relevant files are all posted in the following
repository:
https://github.com/AxiomMath/dead-ends
The input files were
• dead-ends.tex, a natural-language statement of the Main Problem for all bases b ≥ 2
(i.e. finding a formula for cdead(b) and proving its correctness);
• a task.md that contains the single line
Read dead-ends.tex.
• a configuration file .environment that contains the single line
lean-4.26.0
which specifies to AxiomProver which version of Lean should be used.
Given these three input files, AxiomProver autonomously provided the following output files:
• problem.lean, a Lean 4.26.0 formalization of the problem statement which includes the
autonomously computed formula for cdead(b); and
• solution.lean, a complete Lean 4.26.0 formalization of the proof.
After AxiomProver generated a solution, the human authors wrote this paper (without the
use of AI) for human readers. Indeed, a research paper is a narrative designed to communicate
ideas to humans, whereas a Lean files are designed to satisfy a computer kernel.
4. Appendix: Computing νp(S) and cdead
This appendix records two additional facts:
(A) one can compute νp(S) explicitly for each prime p and each digit subset S;
(B) using these formulas, one can evaluate cdead numerically to high precision.
12 DEAD ENDS IN SQUARE-FREE DIGIT WALKS
4.1. Explicit computation of νp(S). Here we explicitly compute the νp(S). For primes p ≥ 7,
this reduces to whether or not 0 is in S.
Proposition 4.1 (Primes p ≥ 7). Let p ≥ 7 be prime and let S ⊆ D. Then 10 is invertible
modulo p
2 and
νp(S) = 1 + |S| − 10∈S.
Proof. Modulo p
2
, the congruence p
2
| n forces n ≡ 0 (one residue class). For each d ∈ S, the
congruence p
2
| (10n + d) is equivalent to
n ≡ −d · 10−1
(mod p
2
),
so it specifies exactly one residue class. If d ̸= d
′
, then d ̸≡ d
′
(mod p
2
) because p
2 ≥ 49 > 9,
so these residue classes are distinct. The class for d = 0 coincides with n ≡ 0, giving the stated
union size. □
The primes 2, 3, 5 are special because 10 is not invertible modulo 4 or 25, and because 9 ≤ 10
introduces a collision modulo 9.
Proposition 4.2 (The prime p = 3). Since 10 ≡ 1 (mod 9),
ν3(S) = |{0} ∪ {−d mod 9 : d ∈ S}| .
Proof. We have 9 | (10n + d) if and only if 9 | (n + d), i.e. n ≡ −d (mod 9). Taking the union
over d ∈ S and adding n ≡ 0 (from 9 | n) gives the formula. □
Proposition 4.3 (The prime p = 2). The following are true.
(1) if d is odd, then 4 ∤ (10n + d) for all n (no solutions);
(2) if d ≡ 0 (mod 4) (i.e. d ∈ {0, 4, 8}), then 4 | (10n + d) holds for n ≡ 0, 2 (mod 4);
(3) if d ≡ 2 (mod 4) (i.e. d ∈ {2, 6}), then 4 | (10n + d) holds for n ≡ 1, 3 (mod 4).
Therefore, ν2(S) is the size of the union of these residue sets together with {0} (from 4 | n).
Proof. Solve 2n + d ≡ 0 (mod 4) case-by-case. If d is odd, the left-hand side is odd so has no
solutions. If d is even, divide by 2 to obtain a condition modulo 2, which lifts to two classes
modulo 4. □
Proposition 4.4 (The prime p = 5). The following are true:
(1) 25 | (10n) if and only if 5 | n, i.e. n ≡ 0 (mod 5) (five classes modulo 25);
(2) 25 | (10n + 5) if and only if n ≡ 2 (mod 5) (five classes modulo 25).
Therefore, ν5(S) is the size of the union of these residue sets together with {0} (from 25 | n).
Proof. If 5 ∤ d, then 10n + d is not divisible by 5, hence cannot be divisible by 25. If d = 0,
then 25 | 10n is equivalent to 5 | n. If d = 5, then 25 | (10n + 5) = 5(2n + 1) is equivalent to
5 | (2n + 1), i.e. n ≡ 2 (mod 5). Each congruence class modulo 5 lifts to exactly five classes
modulo 25. □
4.2. Computing cdead numerically. Using the explicit formulas above, one can compute cdead
to high precision. A convenient simplification is the observation that for every prime p ≥ 7 the
local factor depends on S only through |S| and whether 0 ∈ S. This reduces the 1024 Euler
products to a linear combination of only 22 products.
DEAD ENDS IN SQUARE-FREE DIGIT WALKS 13
The decimal shown in Theorem 1.1 was obtained by evaluating these products using the rapidly
convergent identity, valid for p ≥ 7 and 1 ≤ a ≤ 9,
X
p≥7
log
1 −
a
p
2

= −
X
k≥1
a
k
k
X
p≥7
1
p
2k
,
and truncating the k-sum at a point where the tail is far below the displayed precision. (The
ratio a/p2 ≤ 9/49 ensures very fast geometric decay.)
References
[1] T. Apostol, Introduction to Analytic Number Theory, New York, Springer, 1976.
[2] S. D. Kominers, Uniform bounds for digit-appending Fibonacci walks, (https://arxiv.org/abs/2512.06446)
[3] L. de Moura, S. Kong, J. Avigad, F. van Doorn, and J. von Raumer, The Lean theorem prover (system
description), in Automated Deduction – CADE-25, Lecture Notes in Computer Science 9195, Springer, 2015,
378–388.
[4] The mathlib Community, The Lean mathematical library, in Proceedings of the 9th ACM SIGPLAN International Conference on Certified Programs and Proofs (CPP 2020), ACM, 2020.
[5] S. Miller, Y. Peng, I. Popescu, K. S¸iktar, and S. Wattanawanichkul, Walking to infinity along number theory
sequences, Integers 24 (2024).
[6] L. Mirsky, Note on an asympotic formula connected with r-free integers, The Quarterly Journal of Mathematics, Oxford, 18 (1947), 178-182.

---

# SANSKRIT PROOF ENGINE — MANDALA GEOMETRY

*Mathematical basis for layered proof visualization. Informs SCHEMA.md and frontend.*

## 1. Mandala Proof Space

**Definition 1.1 (Base disk).** Let D²_R = {(r, θ) : 0 ≤ r ≤ R, θ ∈ [0, 2π)} be the closed disk of radius R in polar coordinates. This is **Layer 0** — the flat surface on which gold text (Sanskrit) is rendered.

**Definition 1.2 (Proof graph).** A proof graph is G = (N, E, B) where:
- N = set of nodes (claims)
- E ⊆ N × N = parent-child edges (decomposition)
- B ⊆ N × N = bridge relation (same Lean type, different traditions)

**Definition 1.3 (Layer assignment).** The depth function d: N → ℕ is defined by:
- d(n) = 0 if n has no parent (root)
- d(n) = d(parent(n)) + 1 otherwise

**Definition 1.4 (Mandala proof space).** A mandala proof space is M = (G, p, R) where:
- G = proof graph
- p: N → D²_R = placement map (node positions on the disk)
- R > 0 = disk radius

## 2. Placement Rules

**2.1 Radial by tradition.** Let T = set of traditions. Partition [0, 2π) into |T| sectors. For tradition t, sector S_t = [2π·k/|T|, 2π·(k+1)/|T|) for some ordering k. Place node n in sector S_{tradition(n)}.

**2.2 Concentric by depth.** For node n at depth d(n), set r(n) = R · (1 − α^d(n)) for some α ∈ (0,1). Roots at outer edge (r ≈ R), deeper nodes inward. Or invert: roots at center, leaves at edge.

**2.3 Hybrid.** θ(n) from tradition sector; r(n) from depth. So p(n) = (r(d(n)), θ(tradition(n)) + jitter).

## 3. Layer-k Geometry (Connection-Induced)

**Definition 3.1 (Connection layer).** For k ≥ 1, Layer k is the set of geometric elements induced by edges whose child has depth k:

L_k = { (u, v) ∈ E : d(v) = k }

**Definition 3.2 (Vertical element).** For each (u, v) ∈ L_k, create a vertical element: a pillar, petal, or cone rising from the disk at p(u), extending to height h·k, and optionally connecting to p(v) at that height.

**Definition 3.3 (Layer-k surface).** The Layer-k geometry is the union of all vertical elements for edges in L_k. Formally:

Γ_k = ⋃_{(u,v) ∈ L_k} V(u, v, k)

where V(u, v, k) is the vertical element (e.g. cylinder from (p(u), 0) to (p(u), h·k), or a curved petal from p(u) to p(v) at height h·k).

## 4. Bridge Geometry

**Definition 4.1 (Bridge arc).** For (n₁, n₂) ∈ B, create an arc or ribbon connecting p(n₁) to p(n₂) at a height above the disk. Bridges lie on a distinct layer (e.g. Layer ½ or a separate "bridge layer") to avoid occlusion.

**4.2 Bridge placement.** Option A: arc in the plane of the disk (flat). Option B: arc at height h_bridge, forming a catenary or minimal surface between the two points.

## 5. Recursive Structure (Inclusion-Exclusion Analogue)

The dead-ends paper uses inclusion-exclusion over digit subsets S ⊆ D. Here we have an analogous structure:

**Proposition 5.1 (Layer recursion).** The geometry at Layer k depends only on edges with child-depth k. Layers are independent in the sense that Γ_k ∩ Γ_{k'} = ∅ for k ≠ k' (if vertical elements are disjoint in height).

**Proposition 5.2 (Node count at depth k).** Let N_k = {n ∈ N : d(n) = k}. Then |N_k| ≤ |N_{k-1}| · max out-degree. The radial placement r(n) = R · (1 − α^k) ensures no overlap for sufficiently small α.

## 6. Symmetry

**Definition 6.1 (n-fold mandala).** If traditions (or roots) have natural n-fold symmetry, place n anchor nodes at θ = 2πj/n for j = 0, …, n−1. Children inherit sector from parent.

**6.2 Tradition sectors.** |T| = 5 (Nyāya, Buddhist, Kashmir Shaivism, Advaita, Mīmāṃsā) → 5 sectors of 72° each.

## 7. Schema Integration

| Schema concept | Mandala geometry |
|----------------|------------------|
| Node | Point on disk + optional vertical element |
| parent_id | Edge (u,v) → vertical element in L_{d(v)} |
| Bridge | Arc between two nodes |
| Tradition | Sector (θ range) |
| Status | Material/glow (PROVED = luminous, etc.) |
| Kāṇḍa | Optional: Kāṇḍa 3 nodes on inner ring or distinct layer |

**7.1 Rendering order.** Draw Layer 0 (disk + gold text) first. Then Layer 1, 2, … from bottom to top. Bridges last.

## 8. Parameters

| Symbol | Meaning | Default |
|--------|---------|---------|
| R | Disk radius | 1 |
| h | Height scale per layer | 0.2 |
| α | Radial decay (r = R(1−α^d)) | 0.3 |
| n | Symmetry fold (if applicable) | \|T\| |