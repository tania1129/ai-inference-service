"""Original labeled examples for a small English product-review demo."""

POSITIVE = [
    "I love this product and would buy it again",
    "Excellent quality and fast shipping",
    "The item worked perfectly out of the box",
    "Great value for the price",
    "The build feels solid and durable",
    "Setup was quick and easy",
    "The sound is clear and the battery lasts all day",
    "Very happy with my purchase",
    "Everything arrived in perfect condition",
    "This exceeded my expectations",
    "The design is comfortable and easy to use",
    "I am impressed by how well it works",
    "Customer service was helpful and friendly",
    "The replacement arrived quickly and works great",
    "A reliable product that feels well made",
    "Looks great and fits perfectly",
    "The instructions were clear and useful",
    "I would definitely recommend this product",
    "Good packaging and excellent performance",
    "This was worth every penny",
]

NEGATIVE = [
    "I regret buying this product",
    "Terrible quality and very slow shipping",
    "The item broke the first day",
    "A complete waste of money",
    "The build feels cheap and flimsy",
    "Setup was difficult and frustrating",
    "The sound is distorted and the battery dies quickly",
    "Very disappointed with my purchase",
    "It arrived damaged and missing parts",
    "This failed to meet my expectations",
    "The design is uncomfortable and awkward to use",
    "This product does not work at all",
    "Customer service was rude and unhelpful",
    "The replacement was defective too",
    "It stopped working after a week",
    "Poor finish and the size is wrong",
    "The instructions were confusing and incomplete",
    "I would never recommend this product",
    "Poor packaging and terrible performance",
    "I want my money back",
]

EXAMPLES = [(text, "positive") for text in POSITIVE]
EXAMPLES += [(text, "negative") for text in NEGATIVE]
