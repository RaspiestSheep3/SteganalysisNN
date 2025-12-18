#include <opencv2/opencv.hpp>
#include <iostream>
#include <string>

int mainTemp2() {
    for (int i = 1; i < 10001; i++) {
        std::string inputPath  = "C:\\Users\\iniga\\Datasets\\BOWS2\\PGM Cover\\" + std::to_string(i) + ".pgm";
        std::string outputPath = "C:\\Users\\iniga\\Datasets\\BOWS2\\PNG Cover\\" + std::to_string(i + 9000) + ".png";

        // Read PGM (OpenCV supports P2 and P5 automatically)
        cv::Mat image = cv::imread(inputPath, cv::IMREAD_UNCHANGED);

        if (image.empty()) {
            std::cerr << "Error: Could not read input file: " << inputPath << "\n";
            return 1;
        }

        // Ensure grayscale 8-bit format
        if (image.type() != CV_8UC1) {
            std::cerr << "Warning: Input image is not 8-bit grayscale. Converting...\n";
            cv::Mat converted;
            image.convertTo(converted, CV_8UC1);
            image = converted;
        }

        // Write PNG
        if (!cv::imwrite(outputPath, image)) {
            std::cerr << "Error: Could not write output file: " << outputPath << "\n";
            return 1;
        }

        if (i % 100 == 0) std::cout << "Processed " << i << " images" << std::endl;
    }

    std::cout << "Converted all successfully.\n";
    return 0;
}