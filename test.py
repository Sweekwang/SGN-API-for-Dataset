from collections import Counter

def solution(A):
    # Count the frequency of each element in A
    freq = Counter(A)
    
    # Get the frequencies of each unique element
    freq_values = list(freq.values())
    
    # Sort frequencies in descending order
    freq_values.sort(reverse=True)
    
    # Set to track the unique frequencies we want to keep
    seen = set()
    deletions = 0
    
    # Iterate through the frequencies
    for f in freq_values:
        # Adjust the frequency until it's unique or becomes 0
        while f > 0 and f in seen:
            f -= 1
            deletions += 1
        
        # If f is unique, add it to the set
        if f > 0:
            seen.add(f)

    return deletions

# Example test cases
print(solution([1, 1, 1, 2, 2, 2]))  # Output: 1
print(solution([5, 3, 3, 2, 5, 2, 3, 2]))  # Output: 2
print(solution([127, 15, 3, 8, 10]))  # Output: 4
print(solution([10000000, 10000000, 5, 5, 5, 2, 2, 2, 0, 0]))  # Output: 4
