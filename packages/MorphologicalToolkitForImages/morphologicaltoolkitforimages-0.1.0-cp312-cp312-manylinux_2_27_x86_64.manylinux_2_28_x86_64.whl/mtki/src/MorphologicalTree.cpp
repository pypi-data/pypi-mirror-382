#include "../include/MorphologicalTree.hpp"


/* Constructors */

MorphologicalTree::MorphologicalTree(py::array image, float adjacencyRadius, function<bool(uint32_t, uint32_t)> pixelSortCompare):
    adjacencyRadius(adjacencyRadius)
{
    // TODO: const uint8_t* ptr é acessível por índice (como é feito na função computeTree),
    // porém essa abordagem não limita o acesso em memória apenas no domínio da imagem.
    // Necessário encontrar um forma de limitar o número de índices acessíveis (Sugestão span)
    // Acessa os dados brutos da imagem
    py::buffer_info buf = image.request();
    const uint8_t* ptr = static_cast<uint8_t*>(buf.ptr);

    if(buf.format != py::format_descriptor<uint8_t>::format()){
        throw runtime_error("Image must be of type uint8_t.");
    }

    this->height = buf.shape[0];
    this->width = buf.shape[1];

    uint32_t size = static_cast<uint32_t>(this->width * this->height);

    this->pixelToSmallComponent.resize(size);

    unique_ptr unionFind = make_unique<UnionFind>(ptr, adjacencyRadius, this->width, this->height, size, pixelSortCompare);

    this->computeTree(ptr, unionFind->getSortedPixels(), unionFind->getParents());
}

MorphologicalTree::~MorphologicalTree(){
    delete this->root;
    this->nodes.clear();
    platform::free_unused_memory(); // Libera a memória para o SO
}


/* Aux Methods */

void MorphologicalTree::computeTree(const uint8_t* image, const vector<uint32_t>& sortedPixels, const vector<uint32_t>& parent){
    uint32_t nodeId {0};

    for(uint32_t i = sortedPixels.size(); i-- > 0;){
        uint32_t p = sortedPixels[i];
        uint32_t pParent = parent[p];
        Node* tempNode;

        Pixel pixel(p, this->width, this->height);

        // Geram nós, pois são pixels representantes
        if(p == pParent || image[p] != image[pParent]){
            if(p == pParent){
                this->root = new Node(nodeId, p, image[p], pixel);
                this->nodes[nodeId] = this->root;
            }
            else{
                this->nodes[nodeId] = new Node(nodeId, p, image[p], pixel, this->nodes[this->pixelToSmallComponent[pParent]]);
            }

            tempNode = this->nodes[nodeId];
            this->pixelToSmallComponent[p] = nodeId++;
        }
        // Não geram nós, só armazena os pixels, pois são apenas CNPs
        else{
            this->pixelToSmallComponent[p] = this->pixelToSmallComponent[pParent];
            tempNode = this->nodes[this->pixelToSmallComponent[p]];
        }

        tempNode->addCNP(p, pixel);
    }
}

vector<uint32_t> MorphologicalTree::getSubtreeIds(const Node* subtreeRoot) const{

    vector<Node*> subtreeNodes {subtreeRoot->getChildren()};

    vector<uint32_t> subtreeIds;

    subtreeIds.push_back(subtreeRoot->getId());

    for(Node* childNode : subtreeNodes){
        vector<uint32_t> childSubtreeIds = this->getSubtreeIds(childNode);

        subtreeIds.insert(
            subtreeIds.end(),
            childSubtreeIds.begin(),
            childSubtreeIds.end()
        );
    }

    return subtreeIds;
}

torch::Tensor MorphologicalTree::computeCompactJacobian(string_view deviceStr) const{
    vector<int64_t> rowIndices;
    vector<int64_t> colIndices;

    for(const Node *node : this->getNodes()){
        vector<uint32_t> subtreeIds = this->getSubtreeIds(node);

        for(uint32_t nodeId : subtreeIds){
            rowIndices.push_back(node->getId());
            colIndices.push_back(nodeId);
        }
    }

    // Verifica dispositivo
    torch::Device device = deviceStr == "cuda" && torch::cuda::is_available() ? torch::kCUDA : torch::kCPU;
    // torch::Device device = torch::kCPU;

    // Cria tensores de índices
    torch::Tensor row = torch::from_blob(rowIndices.data(), {static_cast<long>(rowIndices.size())}, torch::kInt64).clone();
    torch::Tensor col = torch::from_blob(colIndices.data(), {static_cast<long>(colIndices.size())}, torch::kInt64).clone();

    // Empilha os índices para formar shape (2, N)
    torch::Tensor indices = torch::stack({row, col});

    // Cria tensor de valores (todos 1s, tipo uint8)
    torch::Tensor values = torch::ones({static_cast<int64_t>(rowIndices.size())}, torch::TensorOptions().dtype(torch::kUInt8));

    // Define tamanho da matriz
    std::vector<int64_t> size = {static_cast<int64_t>(this->nodes.size()), static_cast<int64_t>(this->nodes.size())};

    // Cria tensor esparso do tipo uint8
    torch::Tensor J_sparse = torch::sparse_coo_tensor(indices, values, size, torch::TensorOptions().dtype(torch::kUInt8)).to(device);

    return J_sparse;
}

vector<map<string, InfoValue>> MorphologicalTree::getInfoToDataFrame(){
    vector<map<string, InfoValue>> treeInfoMap;

    for(const auto& node : this->nodes) {
        treeInfoMap.push_back(node.second->getInfoToDataFrame());
    }

    return treeInfoMap;
}


/* Getters e Setters */

Node* MorphologicalTree::getRoot() const{
    return this->root;
}

vector<Node*> MorphologicalTree::getNodes() const{
    vector<Node*> nodeLst;
    for(const auto& node : this->nodes) {
        nodeLst.push_back(node.second);
    }

    return nodeLst;
}

const float MorphologicalTree::getAdjacencyRadius() const{
    return this->adjacencyRadius;
}

torch::Tensor MorphologicalTree::getLevels() const{
    vector<uint8_t> levels(this->pixelToSmallComponent.size());

    for(const auto& node : this->nodes){
        levels.push_back(node.second->getResidue());
    }

    return torch::from_blob(
        (void*)levels.data(),               // ponteiro para os dados
        {static_cast<long>(levels.size())}, // shape
        torch::kUInt8
    ).clone();
}

torch::Tensor MorphologicalTree::getResidues() const{
    vector<int8_t> residues;

    for(const auto& node : this->nodes){
        residues.push_back(node.second->getResidue());
    }

    return torch::from_blob(
        (void*)residues.data(),               // ponteiro para os dados
        {static_cast<long>(residues.size())}, // shape
        torch::kInt8
    ).clone();
}

vector<uint32_t> MorphologicalTree::getSmallComponents() const{
    return this->pixelToSmallComponent;
}

uint32_t MorphologicalTree::getWidth() const{
    return this->width;
}

uint32_t MorphologicalTree::getHeight() const{
    return this->height;
}

vector<Node*> MorphologicalTree::getNodesById(vector<uint32_t> idList) const{
    vector<Node*> nodeLst;

    for(uint32_t id : idList) {
        nodeLst.push_back(this->nodes.at(id));
    }

    return nodeLst;
}

// torch::Tensor MorphologicalTree::getImage() const{

// }

