# LuxScript Replication Validation Protocol v0.1

Purpose: assess cross-model fidelity of the Reflection → NextStep → StateReport pattern.

Metrics (0–1 each): Structural, Semantic, Ethical, Style.
Procedure: (1) deliver config (symbolic or plain). (2) request the 3-part response. (3) log raw output + sha256 + sig8 + timestamp.
Success: Structural ≥0.9, Semantic ≥0.8, Ethical =1.0, Style ≥0.8.
