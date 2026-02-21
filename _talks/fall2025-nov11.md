---
date: November 11, 2025
time: 6:00–7:00 PM Eastern
season: Fall 2025
zoom: https://usc.zoom.us/j/95561331935
speaker: Yuyan Wang
affiliation: Stanford Graduate School of Business
---

# Beyond Black-Box: Structuring Landing Page Recommender Systems Using Predicted Intents

Modern recommender systems rely on black-box machine learning models to predict consumer choices. However, because these models do not explicitly represent the underlying data-generating process (DGP), they often struggle to generalize beyond observed data. A growing body of work advocates for incorporating consumer intent into personalization systems to improve generalization.

Yet in the context of **landing page recommendations**—the most common and challenging personalization setting—a **list** of recommendations must be generated immediately when a consumer enters the platform, *before* any explicit intent signal is available.

We propose the *Intent-Structured Landing-Page Recommender System (ISRec)*, a principled framework that incorporates intent-based structure into multi-stage landing page recommender systems *without* requiring explicit consumer input and while satisfying industrial latency constraints. ISRec defines intent as a consumer's dynamic *receptiveness* to subsets of content, allowing intent labels to be inferred directly from observed behavior.

It consists of three stages: intent prediction, intent-aware reward modeling, and intent-aware whole-page optimization, serving as the *optimal* greedy solution to the original NP-hard intent-aware recommendation problem with provable regret-bound guarantees.

We evaluate ISRec on YouTube, the world's largest video recommendation platform, and find that it significantly improves daily active users (DAU) by 0.05% and overall user enjoyment by 0.09%, among the largest business metric gains observed in recent YouTube experiments, corresponding to an estimated $32.5 million in annual ads revenue.

Our findings provide empirical evidence that even without knowing the true DGP, enforcing a partial structure aligned with it can help the model generalize. Managerially, ISRec offers a principled and generalizable framework for integrating behavioral and structural insights into real-time industrial personalization systems, paving the way for human-in-the-loop AI design.
