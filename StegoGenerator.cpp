#include <opencv2/opencv.hpp>
#include <fstream>
#include <iostream>
#include <string>
#include <random>
#include <tuple>
#include <cmath>
#include <algorithm>

const std::string imagePath = "C:/Users/iniga/Datasets/Custom";
const std::string textPath = "C:/Users/iniga/Datasets/Custom/DataOverview.txt";

//Note : for each image we will generate 1 cover, 3 low stego, 3 med stego and 3 high stego
const int lowStegoSplitBytes[2] = {100, 2500};
const int medStegoSplitBytes[2] = {2501, 5700};
const int highStegoSplitBytes[2]= {5701, 8000};

int disPointsMax = (256 * 256) - 1;

struct imageStruct {
    int id;
    int stegoAmounts[9];

    // Constructors
    imageStruct(int _id, int amounts[9]) : id(_id) {
        for (int i = 0; i < 9; ++i)
            stegoAmounts[i] = amounts[i];
    }
    imageStruct() : id(0) {
        for (int i = 0; i < 9; ++i) stegoAmounts[i] = 0;
    }
};

const std::string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-";

imageStruct imageStructs[9000];

std::string randomString(int length, std::mt19937& gen, const std::string& chars) {
    std::string result;
    result.resize(length); 
    std::uniform_int_distribution<> dis(0, chars.size() - 1);
    for (int i = 0; i < length; ++i)
        result[i] = chars[dis(gen)];
    return result;
}

std::vector<std::tuple<int, int>> generateAllTuples() {
    std::vector<std::tuple<int, int>> output;

    for (int i = 0; i < 256; i++) {
        for (int j = 0; j < 256; j++) output.push_back(std::tuple<int, int>(i, j));
    }

    return output;
}

int main() {
    std::random_device rd;
    std::mt19937 gen(rd()); // seed

    std::uniform_int_distribution<> disLow(lowStegoSplitBytes[0], lowStegoSplitBytes[1]);
    std::uniform_int_distribution<> disMed(medStegoSplitBytes[0], medStegoSplitBytes[1]);
    std::uniform_int_distribution<> disHigh(highStegoSplitBytes[0], highStegoSplitBytes[1]);
    std::uniform_int_distribution<> disPoints(0, disPointsMax);

    std::vector<std::tuple<int, int>> allTuplesCopiable = generateAllTuples();

    for (int i = 1; i < 9001; i++) {
        // Load image
        cv::Mat image = cv::imread(imagePath + "/Cover/" + std::to_string(i) + ".png");

        if (image.empty()) {
            std::cerr << "Error: could not open image\n";
            return 1;
        }

        //Generating our lengths
        int lengths[9] = {disLow(gen), disLow(gen), disLow(gen), disMed(gen), disMed(gen), disMed(gen), disHigh(gen), disHigh(gen), disHigh(gen)};

        //Generating our random strings
        std::string strings[9] = { randomString(lengths[0], gen, chars), randomString(lengths[1], gen, chars), randomString(lengths[2], gen, chars),
                                  randomString(lengths[3], gen, chars), randomString(lengths[4], gen, chars), randomString(lengths[5], gen, chars),
                                  randomString(lengths[6], gen, chars), randomString(lengths[7], gen, chars), randomString(lengths[8], gen, chars) };

        cv::Mat result;

        for (int j = 0; j < 9; j++) {

            //Finding our points
            std::shuffle(allTuplesCopiable.begin(), allTuplesCopiable.begin() + lengths[j] * 8, gen);
            size_t tupleIndex = 0;
            std::vector<std::tuple<int, int, int>> tuples;

            for (int targetChar : strings[j]) {
                //Creating 8 points
                for (int k = 0; k < 8; k++) {
                    int bit = (targetChar >> k) & 1;
                    
                    std::tuple<int, int> pos = allTuplesCopiable[tupleIndex];
                    tupleIndex++;

                    tuples.emplace_back(std::get<0>(pos), std::get<1>(pos), bit);
                }
            }

            // Create a copy for output
            result = image.clone();

            for (int k = 0; k < tuples.size(); k++) {
                std::tuple<int, int, int> targetTuple = tuples[k];
                cv::Vec3b& pixel = result.at<cv::Vec3b>(std::get<0>(targetTuple), std::get<1>(targetTuple));
                if (std::get<2>(targetTuple) == 1) {
                    for (int c = 0; c < 3; c++) {
                        int newValue = pixel[c] | std::get<2>(targetTuple);
                        pixel[c] = static_cast<uchar>(newValue);
                    }
                }
                else {
                    for (int c = 0; c < 3; c++) {
                        int newValue = pixel[c] & (~std::get<2>(targetTuple));
                        pixel[c] = static_cast<uchar>(newValue);
                    }
                }
            }

            // Save to new file
            cv::imwrite(imagePath + "/Stego/" + std::to_string(i) + "_" + std::to_string(j) + ".png", result);
            //std::cout << "Saved for j = " << j << std::endl;
        }

        imageStructs[i - 1] = imageStruct(i - 1, lengths);

        std::cout << "Saved edited images " + std::to_string(i) + "\n";
    }

    //Saving the image structs
    std::ofstream file(textPath);
    for (int i = 0; i < 9000; i++) {
        for (int j = 0; j < 9; j++) {
            file << (imageStructs[i].stegoAmounts)[j];
            if (j < 8) file << ",";
        }
        file << "\n"; 
    }

    return 0;
}