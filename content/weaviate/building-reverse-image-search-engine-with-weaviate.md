Title: Building Reverse Image Search Engine with Weaviate
Date: 2022-11-02 15:02
Author: Sam Stoelinga
Category: Weaviate
Tags: weaviate, vector database, reverse image
Slug: building-reverse-image-search-with-weaviate

Have you ever tried searching in Google with an image? Try it, you will see
it being able to find similar images. This blog post will show to
make something similar using a vector database like Weaviate. The use case
for this blog is identifying an animal by uploading a picture.

At a high-level the following things will be done:

1. Create and modify the dataset
1. Deploy Weaviate with image configuration
1. Define the Schema for our animal images
1. Import the Images into Weaviate
1. Create a web application that takes an image and shows related animal image

## Create and modify the dataset
The ideal dataset here would have a large variety of animals and each unique animal
should have multiple images. For this blog post, we are going to keep it simple and
use an existing dataset from Kaggle.
