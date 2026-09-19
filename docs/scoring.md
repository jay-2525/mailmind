# Scoring Formulations: MailMind (InboxGuard)

## 1. Storage Waste Score Formulation

The system avoids naive age-based deletion by computing a multi-signal decision score:

$$\text{Storage Waste Score} = \min\left(100, \max\left(0, \sum w_i \cdot s_i - \sum v_j \cdot p_j\right)\right)$$

### Penalty Signals ($s_i$) & Configurable Weights ($w_i$):
1. **Payload Size Penalty ($w_{\text{size}} = 0.25$)**:
   - $> 15\text{ MB} \implies +30\text{ pts}$
   - $> 5\text{ MB} \implies +20\text{ pts}$
   - $> 1\text{ MB} \implies +10\text{ pts}$
2. **Promotional Category Penalty ($w_{\text{promo}} = 0.25$)**:
   - Categorized as Promotion, Newsletter, or Shopping $\implies +25\text{ pts}$
3. **Redundancy Penalty ($w_{\text{redundancy}} = 0.20$)**:
   - Semantic duplicate cosine similarity $\ge 0.88 \implies +25\text{ pts}$
   - Moderate similarity $\ge 0.70 \implies +15\text{ pts}$
4. **Inactivity / Age Penalty ($w_{\text{age}} = 0.15$)**:
   - Inactive $> 180\text{ days} \implies +20\text{ pts}$
   - Inactive $> 60\text{ days} \implies +12\text{ pts}$
5. **Low Actionability Penalty ($w_{\text{low\_action}} = 0.15$)**:
   - Zero pending tasks or commitments $\implies +15\text{ pts}$

### Value Protection Signals ($p_j$):
- Contains active unfulfilled task/commitment: $-20\text{ pts}$
- Future legal/financial value (Receipts, contracts, credentials): $-15\text{ pts}$

---

## 2. Job Match Score Formulation

$$\text{Job Match Score} = 0.35 S_{\text{req}} + 0.15 S_{\text{pref}} + 0.20 S_{\text{sem}} + 0.15 S_{\text{exp}} + 0.15 S_{\text{edu}}$$

- **$S_{\text{req}}$**: Mandatory skills coverage percentage ($|\text{Matched}_{\text{req}}| / |\text{Job}_{\text{req}}| \cdot 100$).
- **$S_{\text{pref}}$**: Preferred skills coverage percentage.
- **$S_{\text{sem}}$**: Cosine similarity between resume vector and job description vector.
- **$S_{\text{exp}}$**: Experience alignment ratio ($\min(1.0, \text{CandidateYears} / \text{JobYears}) \cdot 100$).
- **$S_{\text{edu}}$**: Education tier compatibility score.

---

## 3. Recruiter Trust & Risk Scoring

$$\text{Trust Score} = \max(0, 100 - \sum \text{Risk Penalties})$$

- Free webmail sender (@gmail, @yahoo) for alleged enterprise recruiter: $-20\text{ pts}$
- Sender domain mismatch with company name: $-15\text{ pts}$
- Fake equipment check deposit / advance-fee scam keyword patterns: $-40\text{ pts}$
- Demands cryptocurrency, wire transfer, or gift cards: $-35\text{ pts}$
- Upfront SSN or bank account request before interview: $-35\text{ pts}$
- Masked/shortened URL destination: $-15\text{ pts}$

Categorization:
- $\ge 80$: `LOW_RISK_SIGNALS`
- $50 - 79$: `REVIEW_REQUIRED`
- $< 50$: `HIGH_RISK_SIGNALS`
