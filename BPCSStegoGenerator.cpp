#include <opencv2/opencv.hpp>
#include<fstream>
#include <iostream>
#include <vector>
#include <random>
#include <string>
#include <algorithm>

/*
    =============================================================
    PURPOSE
    -------------------------------------------------------------
    For EACH image in ./images:
      - Generate 9 stego images
      - 3 low embed rate   (0.1%  – 3%)
      - 3 medium embed     (3%    – 10%)
      - 3 high embed       (10%+)

    For the SAME set of 9:
      - 3 cutoffs  = 0.30
      - 3 cutoffs  = random in [0.35 – 0.40]
      - 2 cutoffs  = random in [0.40 – 0.45]
      - 1 cutoff   = random in [0.20 – 0.25]

    IMPORTANT:
      * Cutoff choice is RANDOMLY ASSIGNED to embed rates
      * No fixed correlation between payload size and cutoff

    NOTE:
      This is a CLEAN, WELL-LABELLED SCAFFOLD for BPCS-style
      experiments. The actual BPCS embedding logic is represented
      by a placeholder function so you can drop your own code in.
    =============================================================
*/

// ------------------------------------------------------------
// RANDOM UTILITIES
// ------------------------------------------------------------
std::mt19937 rng(std::random_device{}());

double randDouble(double min, double max) {
    std::uniform_real_distribution<double> dist(min, max);
    return dist(rng);
}

int randInt(int min, int max) {
    std::uniform_int_distribution<int> dist(min, max);
    return dist(rng);
}

// ------------------------------------------------------------
// EMBED RATE STRUCT
// ------------------------------------------------------------
struct EmbedConfig {
    double embedRate;   // fraction of total bits used
    double cutoff;      // BPCS complexity cutoff
    int index;          // 0–8 for labelling
};

// ------------------------------------------------------------
// PLACEHOLDER BPCS EMBED FUNCTION
// ------------------------------------------------------------
/*
    Replace this with your REAL BPCS implementation.

    Inputs:
      cover     - input image
      rate      - fraction of usable capacity (0.001 = 0.1%)
      cutoff    - BPCS complexity threshold

    Output:
      stego image
*/
cv::Mat embedBPCS(
    const cv::Mat& cover,
    double rate,
    double cutoff
) {
    cv::Mat stego = cover.clone();

    const int blockSize = 8;
    int rows = cover.rows;
    int cols = cover.cols;

    // ---------------------------------------------------------
    // HELPER: COMPUTE BPCS COMPLEXITY
    // ---------------------------------------------------------
    auto computeComplexity = [&](int plane[8][8]) {
        int transitions = 0;
        for (int y = 0; y < 8; y++) {
            for (int x = 0; x < 7; x++) {
                if (plane[y][x] != plane[y][x + 1]) transitions++;
                if (plane[x][y] != plane[x + 1][y]) transitions++;
            }
        }
        return static_cast<double>(transitions) / 112.0;
        };

    // ---------------------------------------------------------
    // CHECKERBOARD FOR CONJUGATION
    // ---------------------------------------------------------
    int checker[8][8];
    for (int y = 0; y < 8; y++)
        for (int x = 0; x < 8; x++)
            checker[y][x] = (x + y) & 1;

    // ---------------------------------------------------------
    // ENUMERATE *ALL* CANDIDATE BLOCKS (NO SPATIAL BIAS)
    // ---------------------------------------------------------
    struct BlockRef {
        int c, by, bx, plane;
    };

    std::vector<BlockRef> usableBlocks;

    for (int plane = 0; plane < 8; plane++) {
        for (int by = 0; by + blockSize <= rows; by += blockSize) {
            for (int bx = 0; bx + blockSize <= cols; bx += blockSize) {

                int block[8][8];
                for (int y = 0; y < 8; y++)
                    for (int x = 0; x < 8; x++) {
                        uchar px = cover.at<cv::Vec3b>(by + y, bx + x)[0];
                        block[y][x] = (px >> plane) & 1;
                    }

                if (computeComplexity(block) >= cutoff)
                    usableBlocks.push_back({ 0, by, bx, plane });
            }
        }
    }

    if (usableBlocks.empty())
        return stego;

    // ---------------------------------------------------------
    // TRUE BIT-RATE CAPACITY
    // ---------------------------------------------------------
    int bitsPerBlock = 64;
    int totalCapacityBits = usableBlocks.size() * bitsPerBlock;
    int targetBits = static_cast<int>(totalCapacityBits * rate);

    if (targetBits <= 0)
        return stego;

    int targetBlocks = targetBits / bitsPerBlock;
    if (targetBlocks == 0)
        return stego;

    // ---------------------------------------------------------
    // RANDOMISE BLOCK ORDER (REMOVES BIAS)
    // ---------------------------------------------------------
    std::shuffle(usableBlocks.begin(), usableBlocks.end(), rng);

    // ---------------------------------------------------------
    // GENERATE PAYLOAD BLOCKS
    // ---------------------------------------------------------
    std::vector<std::array<int, 64>> payload(targetBlocks);
    for (auto& block : payload)
        for (int& b : block)
            b = randInt(0, 1);

    // ---------------------------------------------------------
    // EMBEDDING LOOP
    // ---------------------------------------------------------
    for (int i = 0; i < targetBlocks; i++) {

        const auto& ref = usableBlocks[i];

        int payloadPlane[8][8];
        int idx = 0;
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 8; x++)
                payloadPlane[y][x] = payload[i][idx++];

        // Conjugate payload if needed
        if (computeComplexity(payloadPlane) < cutoff) {
            for (int y = 0; y < 8; y++)
                for (int x = 0; x < 8; x++)
                    payloadPlane[y][x] ^= checker[y][x];
        }

        // Embed full block
        for (int y = 0; y < 8; y++) {
            for (int x = 0; x < 8; x++) {
                uchar& px = stego.at<cv::Vec3b>(ref.by + y, ref.bx + x)[0];
                px = (px & ~(1 << ref.plane)) | (payloadPlane[y][x] << ref.plane);
                stego.at<cv::Vec3b>(ref.by + y, ref.bx + x)[1] = px;
                stego.at<cv::Vec3b>(ref.by + y, ref.bx + x)[2] = px;
            }
        }
    }

    return stego;
}

// ------------------------------------------------------------
// MAIN
// ------------------------------------------------------------

const int numCovers = 19000;
const std::string imagePath = "C:\\Users\\iniga\\Datasets\\Custom\\New Cover (Bossbase + Bows2)\\";
const std::string outputPath = "C:\\Users\\iniga\\Datasets\\Custom\\BPCS Stego";
const std::string textPath = "C:/Users/iniga/Datasets/Custom/DataOverviewBPCS.txt";

int main() {

    // --------------------------------------------------------
    // DEFINE EMBED RATE RANGES
    // --------------------------------------------------------
    auto lowRate = []() { return randDouble(0.001, 0.03); };
    auto mediumRate = []() { return randDouble(0.03, 0.10); };
    auto highRate = []() { return randDouble(0.10, 0.7); };

    // --------------------------------------------------------
    // DEFINE CUTOFF POOL (9 TOTAL)
    // --------------------------------------------------------

    // --------------------------------------------------------
    // ITERATE OVER IMAGES
    // --------------------------------------------------------
    std::vector<std::vector<EmbedConfig>> configsFull;

    for (int h = 1; h <= numCovers; h++) {
        std::vector<double> cutoffs = {
            0.30, 0.30, 0.30, // 3 fixed 
            randDouble(0.35, 0.40), randDouble(0.35, 0.40), // 2 mid
            randDouble(0.40, 0.45), randDouble(0.40, 0.45), // 2 high
            randDouble(0.25,0.30), //1 bridging 0.25 - 0.30
            randDouble(0.20, 0.25) // 1 low
        };

        cv::Mat cover = cv::imread(imagePath + std::to_string(h) + ".png");
        if (cover.empty()) continue;

        std::string baseName = std::to_string(h) + ".png";

        // ----------------------------------------------------
        // BUILD EMBED CONFIGS
        // ----------------------------------------------------
        std::vector<EmbedConfig> configs;

        for (int i = 0; i < 3; i++) configs.push_back({ lowRate(),    0.0, i });
        for (int i = 3; i < 6; i++) configs.push_back({ mediumRate(), 0.0, i });
        for (int i = 6; i < 9; i++) configs.push_back({ highRate(),   0.0, i });

        // RANDOMISE CUTOFF ASSIGNMENT
        std::shuffle(cutoffs.begin(), cutoffs.end(), rng);
        for (int i = 0; i < 9; i++) {
            configs[i].cutoff = cutoffs[i];
        }

        // ----------------------------------------------------
        // GENERATE STEGOS
        // ----------------------------------------------------

        for (int i = 0; i < 9; i++) {
            const auto& cfg = configs[i];

            cv::Mat stego = embedBPCS(
                cover,
                cfg.embedRate,
                cfg.cutoff
            );

            std::string outName = outputPath + "/" + std::to_string(h) + "_" + std::to_string(i + 1) + ".png";

            cv::imwrite(outName, stego);
        }

        configsFull.push_back(configs);

        if (h % 100 == 0) std::cout << "Processed " << h << " images out of " << numCovers << "=" << (h * 100) / numCovers << "%" << std::endl;
    }

    //Saving all images
    std::ofstream file(textPath);
    for (int i = 0; i < numCovers; i++) {
        for (int j = 0; j < 9; j++) {
            file << "[" + std::to_string((configsFull[i][j]).cutoff) + "," + std::to_string(configsFull[i][j].embedRate) + "]";
            if (j < 8) file << ",";
        }
        file << "\n";
    }

    return 0;
}