

class Cluster:
    def __init__(self):
        self.left = None
        self.dist = None
        self.right = None
    def __repr__(self):
        return '({} {} {})'.format(self.left, self.dist, self.right)
    def dump(self, indent=0):
        if isinstance(self.left, str):
            print(' ' * indent, self.left)
        else:
            self.left.dump(indent=indent+1)
        print(' ' * indent, self.dist)
        if isinstance(self.right, str):
            print(' ' * indent, self.right)
        else:
            self.right.dump(indent=indent+1)
    def __iter__(self):
        yield self
        if self.left:
            yield from self.left
        if self.right:
            yield from self.right
    def leaves(self):
        if isinstance(self.left, str):
            yield self.left
        else:
            yield from self.left.leaves()
        if isinstance(self.right, str):
            yield self.right
        else:
            yield from self.right.leaves()
    def distances(self):
        yield self.dist
        if isinstance(self.left, Cluster):
            yield from self.left.distances()
        if isinstance(self.right, Cluster):
            yield from self.right.distances()
    def clusters_by(self, dist):
        if self.dist <= dist:
            return list(self.leaves())
        else:
            return (self.left.clusters_by(dist),
                    self.right.clusters_by(dist))
    def add(self, clusters, grid, lefti, righti):
        self.left = clusters[lefti]
        self.right = clusters[righti]
        self.dist = sorted(grid[lefti])[1]
        # merge columns grid[row][righti] and row grid[righti] into corresponding lefti
        for r in grid:
            r[lefti] = min(r[lefti], r.pop(righti))
        grid[lefti] = list(map(min, zip(grid[lefti], grid.pop(righti))))
        clusters.pop(righti)
        return (clusters, grid)


def agglomerate(labels, grid):
    """
    given a list of labels and a 2-D grid of distances, iteratively agglomerate
    hierarchical Cluster
    """
    clusters = labels
    while len(clusters) > 1:
        # find 2 closest clusters
        # print(clusters)
        distances = [(1, 0, grid[1][0])]
        for i, row in enumerate(grid[2:]):
            distances += [(i + 2, j, c) for j, c in enumerate(row[:i+2])]
        j, i, _ = min(distances, key=lambda x: x[2])
        # merge i<-j
        c = Cluster()
        clusters, grid = c.add(clusters, grid, i, j)
        clusters[i] = c
    return clusters.pop()


def strdist(x, y):
    return levenshtein(x, y)
    

def strdist2(x, y, toks):
    tx = toks[x]
    ty = toks[y]
    return (sum(1 for t in tx if t not in ty) +
            sum(1 for t in ty if t not in tx))


def tokenize(w):
    return re.findall('[a-z]+|[A-Z]+|\d|.', w)
    

def cluster_input(l):

    # tokens = {w: tokenize(w) for w in l}
    # pprint(tokens)

    dist = []
    for i, x in enumerate(l):
        d = [strdist(x, y)
                for j, y in enumerate(l)]
        dist.append(d)

    clusters = agglomerate(l, dist)
    distances = list(clusters.distances())
    distcnt = len(distances)
    distsum = sum(distances)
    distmean = distsum / distcnt
    print('distcnt={} distsum={} distmean={:.2f} distances={}'.format(
        distcnt, distsum, distmean, distances))

    print(clusters)
    #print(list(clusters.leaves()))
    # # clusters.dump()
    #print(list(clusters.distances()))
    return clusters.clusters_by(distmean)

