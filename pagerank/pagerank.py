import os
import random
import re
import sys
import numpy as np 

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    probability_dist = {}
    for x in corpus: # Initialise the base probability for every page in the corpus (weighted by 1-d)
        probability_dist[x] = (1-damping_factor) / len(corpus)

    if corpus[page]: # For page with outgoing links, 
        for x in corpus[page]:
            probability_dist[x] += damping_factor / len(corpus[page]) # We add more weight to the links on the given page
    else: # Otherwise return even probability distribution to all pages 
        for x in corpus:
            probability_dist[x] = 1 / len(corpus)

    return probability_dist # Normalise here or after?


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """ 

    sample = random.sample(sorted(corpus), 1)[0] # Selecting a random page from the corpus
    pagerank = {}

    visit_count = {}
    for page in corpus:
        visit_count[page] = 0 # Initialise count to 0

    for i in range(n):
        visit_count[sample] += 1 # Track number of page visits
        probability_dist = transition_model(corpus, sample, damping_factor) # Get the probability distribution for this sample
        sample = np.random.choice(list(probability_dist.keys()), p=list(probability_dist.values())) # Randomly select new page with weights

    for page in corpus:
        pagerank[page] = visit_count[page]/n

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    num_pages = len(corpus)
    pagerank = {page: 1 / num_pages for page in corpus} # Even initial distribution

    while True:  
        max_difference = 0  
        for page in corpus:
            new_rank = (1 - damping_factor) / num_pages

            # Calculate contribution from incoming links 
            linked_pages = [linked_page for linked_page, links in corpus.items() if page in links]
            if linked_pages:
                for linked_page in linked_pages:
                    new_rank += damping_factor * pagerank[linked_page] / len(corpus[linked_page])   
            else: # Handle dangling nodes (pages without links)
                for other_page in corpus:
                    new_rank += damping_factor * pagerank[other_page] / num_pages

            # Update PageRank and track maximum change
           
            difference = pagerank[page] - new_rank
            pagerank[page] = new_rank
            max_difference = max(max_difference, difference)

        # Check for convergence
        if max_difference < 0.001: 
            # Normalize PageRank scores
            norm_sum = sum(pagerank.values())  
            for page in pagerank:
                pagerank[page] /= norm_sum  
            break 

        
    return pagerank


if __name__ == "__main__":
    main()
