from multiprocessing import Pool

def solve(inarg):
    return inarg*10

pool = Pool()
args = [2, 10,2,3,4]
results = pool.map(solve, args)
