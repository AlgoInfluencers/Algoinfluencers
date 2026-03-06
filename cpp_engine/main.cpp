#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

// Simple C++17 engine for graph metrics and Independent Cascade simulation
// Usage examples:
//  metrics:  ./engine --mode metrics --edges dataset/edges.txt --top 10
//  simulate: ./engine --mode simulate --edges dataset/edges.txt --seed 42 --p 0.15 --steps 8

struct Args {
    string mode = "metrics"; // or simulate
    string edgesPath = "";
    int seed = -1;           // original node label
    double p = 0.1;          // activation probability
    int steps = 5;           // max steps
    int top = 10;            // top-K for rankings
};

static bool hasFlag(int i, int argc, char** argv, const string& flag) {
    return (i + 1 < argc && string(argv[i]) == flag);
}

Args parseArgs(int argc, char** argv) {
    Args a;
    for (int i = 1; i < argc; ++i) {
        string s = argv[i];
        if (s == "--mode" && i + 1 < argc) { a.mode = argv[++i]; }
        else if (s == "--edges" && i + 1 < argc) { a.edgesPath = argv[++i]; }
        else if (s == "--seed" && i + 1 < argc) { a.seed = stoi(argv[++i]); }
        else if (s == "--p" && i + 1 < argc) { a.p = stod(argv[++i]); }
        else if (s == "--steps" && i + 1 < argc) { a.steps = stoi(argv[++i]); }
        else if (s == "--top" && i + 1 < argc) { a.top = stoi(argv[++i]); }
    }
    return a;
}

struct Graph {
    // Internal ids: 0..N-1
    vector<vector<int>> adj;       // directed graph
    vector<int> id2label;          // internal id -> original label
    unordered_map<int,int> label2id; // original label -> internal id
    long long E = 0;

    void add_edge_label(int uLabel, int vLabel) {
        int u = ensure_node(uLabel);
        int v = ensure_node(vLabel);
        adj[u].push_back(v);
        ++E;
    }

    int ensure_node(int label) {
        auto it = label2id.find(label);
        if (it != label2id.end()) return it->second;
        int nid = (int)id2label.size();
        label2id[label] = nid;
        id2label.push_back(label);
        adj.emplace_back();
        return nid;
    }

    int N() const { return (int)adj.size(); }
};

bool load_edges(const string& path, Graph& G) {
    ifstream fin(path);
    if (!fin.is_open()) return false;
    string line;
    int u, v;
    while (fin >> u >> v) {
        G.add_edge_label(u, v);
    }
    return true;
}

vector<int> degree_centrality(const Graph& G) {
    vector<int> deg(G.N(), 0);
    for (int u = 0; u < G.N(); ++u) {
        deg[u] = (int)G.adj[u].size();
    }
    return deg;
}

vector<double> pagerank(const Graph& G, double d = 0.85, int max_iter = 100, double tol = 1e-6) {
    int N = G.N();
    if (N == 0) return {};
    vector<double> pr(N, 1.0 / N);
    vector<int> outdeg(N, 0);
    for (int u = 0; u < N; ++u) outdeg[u] = (int)G.adj[u].size();

    vector<double> next(N, 0.0);
    for (int it = 0; it < max_iter; ++it) {
        fill(next.begin(), next.end(), (1.0 - d) / N);

        double dangling_sum = 0.0;
        for (int u = 0; u < N; ++u) if (outdeg[u] == 0) dangling_sum += pr[u];
        double dangling_contrib = d * dangling_sum / N;
        for (int v = 0; v < N; ++v) next[v] += dangling_contrib;

        for (int u = 0; u < N; ++u) {
            if (outdeg[u] == 0) continue;
            double share = d * pr[u] / outdeg[u];
            for (int v : G.adj[u]) next[v] += share;
        }

        double diff = 0.0;
        for (int i = 0; i < N; ++i) diff += fabs(next[i] - pr[i]);
        pr.swap(next);
        if (diff < tol) break;
    }

    // Normalize (optional)
    double sum = accumulate(pr.begin(), pr.end(), 0.0);
    if (sum > 0) for (double& x : pr) x /= sum;
    return pr;
}

struct ICSimResult {
    vector<int> activated_per_step; // counts per step
    int total = 0;
};

ICSimResult independent_cascade(const Graph& G, int seedLabel, double p, int max_steps) {
    ICSimResult res;
    if (G.N() == 0) return res;
    auto it = G.label2id.find(seedLabel);
    if (it == G.label2id.end()) return res;
    int seed = it->second;

    vector<char> active(G.N(), 0);
    vector<int> frontier;
    frontier.push_back(seed);
    active[seed] = 1;

    std::mt19937 rng((uint32_t)chrono::high_resolution_clock::now().time_since_epoch().count());
    std::uniform_real_distribution<double> dist(0.0, 1.0);

    int steps = 0;
    int total_activated = 1;

    while (!frontier.empty() && steps < max_steps) {
        vector<int> next_frontier;
        for (int u : frontier) {
            for (int v : G.adj[u]) {
                if (active[v]) continue;
                if (dist(rng) < p) {
                    active[v] = 1;
                    next_frontier.push_back(v);
                }
            }
        }
        res.activated_per_step.push_back((int)next_frontier.size());
        total_activated += (int)next_frontier.size();
        frontier.swap(next_frontier);
        steps++;
    }

    res.total = total_activated;
    return res;
}

// Helpers to print minimal JSON without third-party libs
static string json_escape(const string& s) {
    string out; out.reserve(s.size()+8);
    for (char c : s) {
        if (c == '"' || c == '\\') { out.push_back('\\'); out.push_back(c); }
        else if (c == '\n') { out += "\\n"; }
        else out.push_back(c);
    }
    return out;
}

static void print_metrics_json(const Graph& G, const vector<int>& deg, const vector<double>& pr, int topK) {
    int N = G.N();
    // Top degree
    vector<int> ids(N);
    iota(ids.begin(), ids.end(), 0);
    sort(ids.begin(), ids.end(), [&](int a, int b){ return deg[a] > deg[b]; });

    // Top PageRank
    vector<int> pr_ids(N);
    iota(pr_ids.begin(), pr_ids.end(), 0);
    sort(pr_ids.begin(), pr_ids.end(), [&](int a, int b){ return pr[a] > pr[b]; });

    cout << "{\n";
    cout << "  \"nodes\": " << N << ",\n";
    cout << "  \"edges\": " << G.E << ",\n";

    cout << "  \"top_degree\": [";
    for (int i = 0; i < min(topK, N); ++i) {
        int u = ids[i];
        if (i) cout << ", ";
        cout << "{\"node\": " << G.id2label[u] << ", \"degree\": " << deg[u] << "}";
    }
    cout << "],\n";

    cout << "  \"top_pagerank\": [";
    for (int i = 0; i < min(topK, N); ++i) {
        int u = pr_ids[i];
        if (i) cout << ", ";
        cout << fixed << setprecision(6);
        cout << "{\"node\": " << G.id2label[u] << ", \"score\": " << pr[u] << "}";
    }
    cout << "]\n";
    cout << "}\n";
}

static void print_sim_json(int seedLabel, double p, int steps, const ICSimResult& res) {
    cout << "{\n";
    cout << "  \"seed\": " << seedLabel << ",\n";
    cout << fixed << setprecision(4);
    cout << "  \"p\": " << p << ",\n";
    cout << "  \"steps\": " << steps << ",\n";
    cout << "  \"total_activated\": " << res.total << ",\n";
    cout << "  \"activated_per_step\": [";
    for (size_t i = 0; i < res.activated_per_step.size(); ++i) {
        if (i) cout << ", ";
        cout << res.activated_per_step[i];
    }
    cout << "]\n";
    cout << "}\n";
}

int main(int argc, char** argv) {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    Args args = parseArgs(argc, argv);
    if (args.edgesPath.empty()) {
        cerr << "Error: --edges <path> is required\n";
        return 1;
    }

    Graph G;
    if (!load_edges(args.edgesPath, G)) {
        cerr << "Error: failed to open edges file: " << args.edgesPath << "\n";
        return 1;
    }

    if (args.mode == "metrics") {
        auto deg = degree_centrality(G);
        auto pr = pagerank(G);
        print_metrics_json(G, deg, pr, args.top);
        return 0;
    } else if (args.mode == "simulate") {
        if (args.seed == -1) {
            // Default: pick highest degree node as seed
            auto deg = degree_centrality(G);
            int best = 0;
            for (int i = 1; i < (int)deg.size(); ++i) if (deg[i] > deg[best]) best = i;
            args.seed = G.id2label[best];
        }
        auto res = independent_cascade(G, args.seed, args.p, args.steps);
        print_sim_json(args.seed, args.p, args.steps, res);
        return 0;
    } else {
        cerr << "Error: --mode must be 'metrics' or 'simulate'\n";
        return 1;
    }
}
