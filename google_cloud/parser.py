from google_cloud.ram_analyses_cloud import parse_read
import sys

if __name__ == "__main__":
    subj = sys.argv[1]
    file = sys.argv[2]

    print(parse_read('/scratch/francob/big_ram_analyses_alternatives/R{}/{}.pkl'.format(subj, file)))

