"""Outreach flow: branded image quote for a prospect (Shamik's use case).

1. Create a brand profile tagged as "lead" with the prospect's colors
2. Submit their podcast/interview for transcription
3. Wait for transcript, extract quotes
4. Render an image quote pinned to a specific template for consistency
5. Save as draft

Run with:
    SML_API_KEY=sml_xxx python examples/outreach_flow.py
"""

from somanylemons import SMLClient

# Pin these once — outreach output stays consistent across leads
OUTREACH_TEMPLATE_ID = 42


def run_outreach_flow(
    client: SMLClient,
    *,
    prospect_name: str,
    prospect_company: str,
    primary_color: str,
    secondary_color: str,
    logo_url: str | None,
    podcast_url: str,
) -> None:
    # 1. Brand for the lead
    brand = client.brands.create(
        name=f"{prospect_company} (lead)",
        primary_color=primary_color,
        secondary_color=secondary_color,
        logo_url=logo_url,
        source="lead",
    )
    print(f"Brand created: #{brand.id} {brand.name}")

    # 2. Transcribe the podcast
    job = client.transcribe.create_and_wait(url=podcast_url, timeout=900)
    print(f"Transcription done: clip #{job.id}, {len(job.clips)} clips ready")

    # 3. Extract quotes
    quotes_resp = client.content.extract_quotes(
        text=job.transcript_preview or "",
        count=5,
    )
    quotes = quotes_resp.get("quotes", [])
    if not quotes:
        print("No quotes extracted.")
        return

    # 4. Render image quote with the pinned template
    best_quote = quotes[0]["text"] if isinstance(quotes[0], dict) else str(quotes[0])
    image = client.image_quotes.create(
        quote_text=best_quote,
        brand_profile_id=brand.id,
        speaker_name=prospect_name,
        speaker_title=f"{prospect_company} Leadership",
        template_id=OUTREACH_TEMPLATE_ID,
    )
    print(f"Image quote: {image.image_url}")

    # 5. Save as draft so it shows up in the outreach review queue
    draft = client.drafts.create(
        caption=f"Handpicked insight from {prospect_name}: {best_quote}",
        job_id=str(job.id),
    )
    print(f"Draft created: #{draft.id} ({draft.status.value})")


if __name__ == "__main__":
    with SMLClient() as client:
        run_outreach_flow(
            client,
            prospect_name="Jane Doe",
            prospect_company="Acme Corp",
            primary_color="#1a73e8",
            secondary_color="#ffffff",
            logo_url=None,
            podcast_url="https://example.com/acme-podcast.mp3",
        )
