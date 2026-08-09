# Part 2 Findings — Chapter 2 (Harmony and Voice Leading)
Lines 1493-2980 of tymoczko_raw.txt

## What's Here
The mathematical foundations: pitch space as a continuous line (log-frequency), pitch-class space as a circle (octave equivalence), transposition and inversion as distance-preserving transformations, the OPTIC symmetry framework for chord classification, and voice-leading measurement.

## Rasa-Relevant Findings

### Finding 1: OPTIC Symmetries as Equivalence-Generating Operations
Tymoczko defines five symmetry operations (Octave, Permutation, Transposition, Inversion, Cardinality change) that generate all the equivalence classes we call "chords," "chord types," and "set classes." The idea: **musical abstraction IS symmetry identification**. You categorize two sounds as "the same chord" because they are related by specific transformations.

This maps directly to our Πᵢ (participant map) and Qᵢ (participant-specific invariances). The OPTIC symmetries define *equivalence relations* over raw pitch experience — they're what Wolfram would call the observer's coarse-graining map qᵢ. Musical perception is a process of imposing invariance structure on acoustic input.

In rasa terms: recognizing "this is a C major chord" IS applying an equivalence relation that ignores octave, order, doubling, and absolute pitch — leaving only the interval structure {4, 3, 5} semitones. The "flavor" of major is that specific interval sequence. This is literally a geometric invariant.

### Finding 2: Voice-Leading Size as a Metric on Experience Space
Voice-leading size is measured as the total distance voices move (in semitones, possibly with various norms: L1, L2, L∞). This gives a **metric on the space of chord sequences**: the distance between two chord progressions can be defined as the minimal voice-leading size connecting them.

For rasa: if felt quality = geometry, then the *distance* between two experiences in phenomenal space can be measured as the minimal "work" required to transform one into the other. Tymoczko gives us a concrete metric for auditory space. The testable prediction: phenomenal similarity should follow voice-leading distance — two chord progressions close in voice-leading space should feel more similar, independent of cultural learning.

### Finding 3: Near-Evenness as the Key to Consonance + Efficient Voice Leading
The chapter previews a crucial result developed later: nearly even chords (those dividing the octave into roughly equal parts) can be linked by efficient voice leading AND are acoustically consonant. Uneven chords (clusters) can't be linked efficiently but allow melodic activity within a static harmony.

This is the *geometric mechanism connecting consonant structure to temporal dynamics* — exactly the bridge between 𝒢ᵢ (field geometry) and τᵢ (temporal integration). The near-evenness of a chord simultaneously determines its consonance (instantaneous quality) and its contrapuntal potential (temporal behavior). Structure and dynamics are not separate properties of the chord — they're two aspects of the same geometric fact.

### Finding 4: Classification as Information Discarding
Tymoczko: "Musical classification proceeds by the progressive discarding of information." The hierarchy is: raw acoustic signal → pitches → pitch classes → chords → chord types → set classes. Each step applies more symmetries, losing more detail.

This is a model of how Dᵢ (the phenomenal field) is constructed from raw sensory input Σᵢ. The OPTIC operations are the *aperture's built-in equivalence relations* — the structure by which raw signal becomes organized experience. Recognition (T_rec) might be the process of reversing this — seeing through the symmetries to the raw signal, or seeing the symmetries themselves as operations rather than as the nature of reality.

### Finding 5: Inversion as Duality
Inversion (I) maps major ↔ minor, dominant ↔ half-diminished, etc. Inversionally related chords "sound reasonably similar" — they share the same interval sequence but in reverse direction. This is a *duality* within the phenomenal field — a structural pairing that is neither identity nor unrelatedness.

For rasa: inversionally related experiences (major vs minor, positive vs negative valence) might share a common geometric structure (same absolute distances) that differs only in direction (clockwise vs counterclockwise). The QRI valence hypothesis would predict that major and minor have the same absolute symmetry but different *orientation* — and indeed, major and minor chords have the same set of near-symmetries but different voice-leading behaviors. Valence might be direction-sensitive, not just magnitude-sensitive.

### Finding 6: The Pitch-Class Circle as Quotient Space
Pitch-class space is *formed out of* pitch space by quotienting out octave equivalence. This is literally Wolfram's observer quotient: Qᵢ(X) = X/∼ where ∼ is octave equivalence.

This gives a concrete example of how Πᵢ (participant map) operates: the auditory system automatically quotients raw frequency information by 2:1 ratios, producing the circular pitch-class space that all subsequent musical organization builds upon. This quotient is not culturally learned — octave equivalence appears to be innate and possibly universal across humans and some animals.

### Finding 7: Continuous vs Discrete Pitch Space
Tymoczko uses *continuous* pitch space (allowing microtones) rather than the usual 12-semitone discretization. The discrete chromatic scale is an *additional constraint* on top of the continuous geometry, not the geometry itself.

For rasa: the "resolution" of phenomenal space is not fixed — it can be finer or coarser depending on the aperture's state. The Vijñānabhairava's void practices (minimal differentiation) might correspond to reducing the resolution of phenomenal geometry — like switching from 12-tone to continuous space. Recognition could be the capacity to shift between resolution levels at will.

## Cool Things to Investigate

1. **Test voice-leading distance as a predictor of phenomenal similarity**: Have subjects rate similarity of chord pairs, compare to voice-leading distance. Does L1 vs L2 norm better predict similarity judgments?

2. **OPTIC symmetries in non-auditory modalities**: Do visual or tactile perception have analogous symmetry operations? If so, this would support cross-domain rasa.

3. **Inversion and valence**: Measure EEG responses to major vs minor chords. Are they inversionally symmetric in neural space? Does "inversion" in the neural response correlate with the valence flip?

4. **Quotient space theory of perception**: Model each sensory modality as a quotient of raw signal space by a set of equivalence relations (the OPTIC-like operations for that modality). Test whether the quotient structure predicts phenomenal structure.

5. **Continuous vs discrete phenomenal resolution**: Use microtonal stimuli to test whether listeners can discriminate finer-than-semitone pitch differences under different conditions (attention, arousal, meditation state).
