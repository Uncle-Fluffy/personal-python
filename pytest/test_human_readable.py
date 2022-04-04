# This script converts long integers into simple human readable byte sizes
# It also shows how to inumerate through a dictionary
# and shows how to read the second item of a dictionary and compare

def human_readable_size(size, decimal_places=0):
    """Pad the byte sizes scraped from s3 to match what TCD has had historically"""
    for unit in ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return str(f"{size:.{decimal_places}f} {unit}")

def test_human_readable_sizes():
    bytes = {2: '2 Bytes', 2048: '2 KB', 2_000_000: '2 MB', 2_000_000_000: '2 GB', 2_000_000_000_000: '2 TB', 2_000_000_000_000_000: '2 PB'}
    for unit, value in bytes.items():
        print(unit)
        print(value)
        print(human_readable_size(unit))
        #print(bytes[unit])
        if human_readable_size(unit) == bytes[unit]:
            print("Matches")
        else:
            print("Failed ***")

test_human_readable_sizes()