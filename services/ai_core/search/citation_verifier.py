import re
from typing import List, Tuple, Optional
from services.ai_core.search.search_base import SearchResultItem, GroundedCitation

class CitationVerifier:
    """Verifies that citations generated in AI responses genuinely correspond to retrieved sources."""

    @staticmethod
    def verify_citation(claim_quote: str, sources: List[SearchResultItem]) -> Tuple[bool, float, Optional[SearchResultItem]]:
        if not claim_quote or not sources:
            return False, 0.0, None

        claim_tokens = set(re.findall(r"\w+", claim_quote.lower()))
        if not claim_tokens:
            return False, 0.0, None

        best_score = 0.0
        best_source = None

        for src in sources:
            src_text = (src.title + " " + src.snippet).lower()
            src_tokens = set(re.findall(r"\w+", src_text))

            # Jaccard / containment overlap
            intersection = claim_tokens.intersection(src_tokens)
            overlap = len(intersection) / len(claim_tokens)

            if overlap > best_score:
                best_score = overlap
                best_source = src

        # Threshold: At least 40% lexical concept overlap in snippet
        is_verified = best_score >= 0.40
        return is_verified, round(best_score, 2), best_source

    def verify_all(
        self,
        citations_to_check: List[dict],
        sources: List[SearchResultItem]
    ) -> List[GroundedCitation]:
        verified_results = []
        for i, c in enumerate(citations_to_check):
            quote = c.get("quote", "")
            is_valid, conf, matched_source = self.verify_citation(quote, sources)

            if matched_source and is_valid:
                verified_results.append(GroundedCitation(
                    citation_id=i + 1,
                    source_url=matched_source.url,
                    source_title=matched_source.title,
                    quote=quote,
                    verified=True,
                    confidence=conf
                ))
            else:
                # Flag unverified citation
                verified_results.append(GroundedCitation(
                    citation_id=i + 1,
                    source_url=c.get("source_url", "about:blank"),
                    source_title="Unverified Source",
                    quote=quote,
                    verified=False,
                    confidence=conf
                ))
        return verified_results

citation_verifier = CitationVerifier()
