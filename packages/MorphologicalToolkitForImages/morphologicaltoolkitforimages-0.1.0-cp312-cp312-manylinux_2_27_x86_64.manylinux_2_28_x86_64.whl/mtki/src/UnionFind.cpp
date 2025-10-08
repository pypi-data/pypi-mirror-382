#include "../include/UnionFind.hpp"

UnionFind::UnionFind(
    const uint8_t* image,
    const float& adjacencyRadius,
    uint32_t width,
    uint32_t height,
    uint32_t size,
    function<bool(uint8_t, uint8_t)> pixelSortCompare
):
    parent(size),
    pixelSortCompare(pixelSortCompare)
{
    vector<int32_t> offsets {computeOffsets(adjacencyRadius, width)};

    this->sortedPixels = this->sortPixels(image, size);

    // TODO: Otimizar essa ordenação para que ela exista apenas enquanto for necessária
    // vector<uint32_t> sortedPixels {this->sortPixels(image, size)};
    vector<optional<uint32_t>> zpar(size);


    for(uint32_t p : sortedPixels){
        int32_t px = static_cast<int32_t>(p / width);
        int32_t py = static_cast<int32_t>(p % width);

        this->parent[p] = p;
        zpar[p] = p;

        for(int32_t offset : offsets){
            int32_t q {offset + static_cast<int32_t>(p)};

            // Verifica se está dentro do domínio
            if(q < 0 || q >= size){
                continue;
            }

            // Verifica se zpar do pixel q tem algo
            if(!zpar[q].has_value()){
                continue;
            }

            int32_t qx = static_cast<int32_t>(q / width);
            int32_t qy = static_cast<int32_t>(q % width);

            // Verifica se é vizinho quando visualizados na matriz
            if(std::abs(px - qx) > adjacencyRadius || std::abs(py - qy) > adjacencyRadius){
                continue;
            }

            this->unionSets(p, q, zpar);
        }
    }

    this->canonize(image, sortedPixels);
}

UnionFind::~UnionFind(){}

vector<int32_t> UnionFind::computeOffsets(const float& adjacencyRadius, uint32_t width){
    vector<int32_t> offsets;

    int32_t auxRadius = static_cast<int32_t>(ceil(adjacencyRadius));
    float radiusSquared = adjacencyRadius * adjacencyRadius;

    int32_t w = static_cast<int32_t>(width);

    for(int32_t dy = -auxRadius; dy <= auxRadius; dy++){
        for(int32_t dx = -auxRadius; dx <= auxRadius; dx++){
            if(dx == 0 && dy == 0){ continue; }

            float distanceSquared = static_cast<float>(dx * dx + dy * dy);
            if(distanceSquared <= radiusSquared + 1e-6){
                offsets.push_back(dy * width + dx);
            }
        }
    }

    return offsets;
}

vector<uint32_t> UnionFind::sortPixels(const uint8_t* image, const uint32_t& size){
    vector<uint32_t> sortedPixels(size);
    iota(sortedPixels.begin(), sortedPixels.end(), 0);

    sort(sortedPixels.begin(), sortedPixels.end(), [&](uint32_t p, uint32_t q){
        if (image[p] != image[q]){
            return this->pixelSortCompare(image[p], image[q]);
        }
        return p < q;
    });

    return sortedPixels;
}

void UnionFind::unionSets(uint32_t p, int32_t q, vector<optional<uint32_t>>& zpar){
    uint32_t qRoot = this->findRoot(q, zpar);

    if(p != qRoot){
        this->parent[qRoot] = p;
        zpar[qRoot] = p;
    }
}

uint32_t UnionFind::findRoot(uint32_t q, vector<optional<uint32_t>>& zpar){
    if(zpar[q] != q){
        zpar[q] = this->findRoot(*zpar[q], zpar);
    }

    return *zpar[q]; // *zpar[q] -> Está como ponteiro pois zpar é um vector<optional<uint32_t>>
}

void UnionFind::canonize(const uint8_t* image, const vector<uint32_t>& sortedPixels){
    for(uint32_t i = sortedPixels.size(); i-- > 0;){
        uint32_t p = sortedPixels[i];
        uint32_t q = this->parent[p];

        if(image[this->parent[q]] == image[q]){
            this->parent[p] = this->parent[q];
        }
    }
}

vector<uint32_t> UnionFind::getSortedPixels() const {
    return this->sortedPixels;
}

vector<uint32_t> UnionFind::getParents() const {
    return this->parent;
}