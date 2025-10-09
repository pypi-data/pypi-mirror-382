import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="LexiDecay",
    version="1.0.0",
    author="Mohammad Taha Gorji",
    author_email="MohammadTahaGorjiProfile@gmail.com",
    description="LexiDecay is a semi-supervised lexical weighting model for unstructured text. It classifies content by adaptive word-frequency decay and soft lexical scoring. Fast (O(n·m)), language-flexible, and training-free — ideal for topic classification, semantic filtering, and intent detection. ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.1',
)