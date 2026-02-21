---
date: November 25, 2025
time: 9:00–10:00 PM Eastern
season: Fall 2025
speaker: Kenichi Shimizu
affiliation: University of Alberta
zoom: https://iu.zoom.us/j/84596323706
---

# Scalable Estimation of Multinomial Response Models with Random Consideration Sets

A common assumption in the fitting of unordered multinomial response models for J mutually exclusive categories is that the responses arise from the same set of J categories across subjects. However, when responses measure a choice made by the subject, it is more appropriate to condition the distribution of multinomial responses on a subject-specific consideration set, drawn from the power set of {1,2,...,J}. This leads to a mixture of multinomial response models governed by a probability distribution over the J* = 2^J - 1 consideration sets.

We introduce a novel method for estimating such generalized multinomial response models based on the fundamental result that any mass distribution over J* consideration sets can be represented as a mixture of products of J component specific inclusion-exclusion probabilities. Moreover, under time-invariant consideration sets, the conditional posterior distribution of consideration sets is sparse. These features enable a scalable MCMC algorithm for sampling the posterior distribution of parameters, random effects, and consideration sets.

Under regularity conditions, the posterior distributions of the marginal response probabilities and the model parameters satisfy consistency. The methodology is demonstrated in a longitudinal data set on weekly cereal purchases that cover J = 101 brands, a dimension substantially beyond the reach of existing methods.
