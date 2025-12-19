from __future__ import annotations

from src.application.ports import AppLogger, ReplyGenerator, ReviewFetcher, ReviewPublisher


def respond_on_reviews(
    *,
    review_fetcher: ReviewFetcher,
    reply_generator: ReplyGenerator,
    review_publisher: ReviewPublisher,
    logger: AppLogger,
) -> None:
    """
    High-level workflow: load pending reviews, ask an LLM for a reply, and publish it back.
    """

    reviews = review_fetcher.fetch_reviews()
    logger.info("Fetched {} pending reviews", len(reviews))

    for review in reviews:
        review_summary = review.summary
        logger.info(
            f"Preparing reply for review {review_summary}",
        )

        reply = reply_generator.generate(review)
        logger.info("Generated reply {}", reply)

        review_publisher.publish_reply(review.id, reply)
        logger.info("Published reply for review {}", review_summary)

    logger.info(f"Published {len(reviews)} pending reviews")
