from app.summarizer import summarize_transcript

URL = "https://www.youtube.com/watch?v=UF8uR6Z6KLc"

print("Distill is summarizing the video... (10-15 seconds)")
summary = summarize_transcript(URL)

print("\n=== DISTILL SUMMARY ===")
print(f"\nTL;DR:\n{summary['tldr']}")
print(f"\nKey Concepts:")
for concept in summary["key_concepts"]:
    print(f"  • {concept}")
print(f"\nConclusion:\n{summary['conclusion']}")
