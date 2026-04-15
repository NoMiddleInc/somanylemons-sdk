"""Minimal end-to-end example.

Run with:
    SML_API_KEY=sml_xxx python examples/quickstart.py
"""

from somanylemons import SMLClient


def main() -> None:
    with SMLClient() as client:  # reads SML_API_KEY from env
        # 1. List recent recordings
        jobs = client.jobs.list(limit=5)
        print(f"\nRecent recordings ({len(jobs)}):")
        for job in jobs:
            print(f"  {job.id} · {job.title[:60]:60} · {job.clip_count} clips · {job.status.value}")

        # 2. List brands
        brands = client.brands.list()
        print(f"\nBrand profiles ({len(brands)}):")
        for brand in brands:
            default_mark = " (default)" if brand.is_default else ""
            print(f"  {brand.id} · {brand.name:20} · {brand.primary_color}{default_mark}")

        # 3. Check usage
        usage = client.content.get_usage()
        print(
            f"\nUsage this period: {usage['renders_used']}/{usage['render_limit']} renders"
        )


if __name__ == "__main__":
    main()
