#!/usr/bin/env python3

import os
from movifex.utils import loadDataFromCSV, loadJsonFromUrl
from movifex.datasets.movielens.downloader import downloadMovielens25m
from movifex.datasets.scenesense.visualizer_metadata import visualizeGenresDictionary
from movifex.datasets.movielens.helper_ratings import mergeMainGenreMoviesDFWithRatingsDF
from movifex.datasets.scenesense.helper_visualfeats import packetAddressGenerator, fetchAllPackets
from movifex.datasets.scenesense.helper_metadata import countNumberOfMovies, fetchRandomMovie, fetchMovieById
from movifex.datasets.movielens.helper_movies import fetchAllUniqueGenres, fetchMoviesByGenre as fetchMoviesByGenreMovielens
from movifex.datasets.movielens.helper_movies import augmentMoviesDFWithBinarizedGenres, binarizeMovieGenres, filterMoviesWithMainGenres, mainGenres
from movifex.datasets.scenesense.helper_metadata import classifyYearsByCount, fetchMoviesByGenre, classifyMoviesByGenre, calculateAverageGenrePerMovie

# Sample variables
datasetName = "SceneSense-visual"
featureModels = ["incp3", "vgg19"]
featureSources = ["full_movies", "movie_shots", "movie_trailers"]
datasetRawFilesUrl = "https://huggingface.co/datasets/alitourani/moviefeats_visual/raw/main/"

def testMoViFexMetadata(configs: dict):
    """
    Runs the visual dataset pipeline (MoViFex dataset) for metadata processing

    Parameters
    ----------
    configs :dict
        The configurations dictionary
    """
    # Variables
    datasetName = configs['name']
    datasetMetadataUrl = configs['path_metadata']
    print(f"Running the visual dataset functions of '{datasetName}' for metadata (json) processing ...")
    # Pre-check fetch JSON data from the URL
    print(f"- Fetching the dataset metadata from '{datasetMetadataUrl}' ...")
    jsonData = loadJsonFromUrl(datasetMetadataUrl)
    # Test#1 - Movie Counting
    print(f"\n- Counting the number of movies in the dataset ...")
    moviesCount = countNumberOfMovies(jsonData)
    print(f"- The dataset contains '{moviesCount}' movies!")
    # Test#2 - Testing Random Movie Fetcher
    print(f"\n- Fetching a random movie from the dataset ...")
    randomMovie = fetchRandomMovie(jsonData)
    print(f"- The random movie:\n{randomMovie}")
    # Test#3 - Fetching a movie by ID
    givenMovieId = 6
    print(f"\n- Fetching a given movie by ID (given: {givenMovieId}) ...")
    movieById = fetchMovieById(jsonData, givenMovieId)
    print(f"- The fetched movie:\n{movieById}")
    # Test#4 - Fetching movies by genre
    givenGenre = "Romance"
    print(f"\n- Fetching all movie with the given genre (input: {givenGenre}) ...")
    moviesByGenre = fetchMoviesByGenre(jsonData, givenGenre)
    print(f"- Returned variable (list): {moviesByGenre}")
    # Test#5 - Year classification
    print(f"\n- Classifying release dates by count ...")
    yearsCount = classifyYearsByCount(jsonData)
    print(f"- Returned variable (dict): {yearsCount}")
    # Test#6 - Genre classification
    print(f"\n- Classifying movies by genre ...")
    moviesByGenre = classifyMoviesByGenre(jsonData)
    print(f"- Returned variable (dict): {moviesByGenre}")
    # Test#7 - Average genre per movie calculation
    print(f"\n- Calculating the average genre per movie ...")
    averageGenrePerMovie = calculateAverageGenrePerMovie(moviesByGenre, moviesCount)
    print(f"- Returned variable (float): {averageGenrePerMovie}")
    # Test#8 - Visualizations
    print(f"\n- Visualizing the classification results in a bar chart ...")
    visualizeGenresDictionary(moviesByGenre)

def testVisualDataProcess():
    print(f"This is an example provided for you to work with the visual packets of the '{datasetName}' dataset ... \n")
    # Fetch JSON data from the URL
    givenMovieId = 6
    print(f"- Generating a sample packet address file from '{datasetRawFilesUrl}' ...")
    packetAddress = packetAddressGenerator(datasetRawFilesUrl, featureSources[2], featureModels[0], givenMovieId, 1)
    print(f"- Generated address (str): {packetAddress}\n")
    # Fetch all packets of a movie
    print(f"- Fetching all packets of the movie #{givenMovieId}) ...")
    moviePackets = fetchAllPackets(datasetRawFilesUrl, featureSources[2], featureModels[0], givenMovieId)
    print(f"- Number of packets fetched (list): {len(moviePackets)}")

def testMovieLens25M(configs: dict):
    """
    Runs the text dataset pipeline (MovieLens 25M dataset)

    Parameters
    ----------
    configs :dict
        The configurations dictionary
    """
    print(f"Running the text dataset pipeline '{configs['name']}' ...")
    # Variables
    needDownloaded = configs['need_download']
    datasetPath = os.path.normpath(configs['download_path'])
    # Pre-check whether the dataset is already downloaded
    print(f"- Checking if the dataset needs to be downloaded (selected: {needDownloaded}) ...")
    if needDownloaded:
        print(f"- The dataset needs to be downloaded! It will be downloaded in '{datasetPath}' ...")
        isDownloadSuccessful = downloadMovielens25m(configs['url'], datasetPath)
        if not isDownloadSuccessful:
            return
        # Go inside the downloaded folder
        datasetPath = os.path.join(datasetPath, "ml-25m")
        print(f"- The dataset files are available in '{datasetPath}'!")
    else:
        # Else, the dataset is already downloaded (reading from the root folder)
        print(f"- The dataset is already downloaded! Trying to load it from '{datasetPath}' ...")
    # Some test functions
    print(f"\nRunning some functionalities provided in the framework for the '{configs['name']}' dataset ...")
    # Reading movies data
    print(f"- Reading dataset's movies and fetching them into a DataFrame ...")
    moviesDataFrame = loadDataFromCSV(os.path.join(datasetPath, "movies.csv"))
    if moviesDataFrame is None:
        print(f"- The dataset files could not be found! Checking the inner folder ...")
        # Go inside the 'ml-25m' folder
        datasetPath = os.path.join(datasetPath, "ml-25m")
        moviesDataFrame = loadDataFromCSV(os.path.join(datasetPath, "movies.csv"))
        if moviesDataFrame is None:
            print(f"- The dataset files could not be found! Exiting ...")
            return
    # Test#1 - Counting the number of movies
    moviesCount = len(moviesDataFrame)
    print(f"- The dataset contains {moviesCount} movies!")
    # Test#2 - Some samples of the movies
    print(f"- The structure of the movies data is as below:")
    print(moviesDataFrame.head(3))
    # Test#3 - Get all genres from the dataset in a list
    print(f"\n- Fetching all genres from the dataset ...")
    allGenres = fetchAllUniqueGenres(moviesDataFrame)
    print(f"- The dataset contains {len(allGenres)} genres, including: {allGenres}")
    # Test#4 - Get movies by a specific genre
    givenGenre = "Action"
    print(f"\n- Fetching movies by a specific genre (given: {givenGenre}) ...")
    moviesByGenre = fetchMoviesByGenreMovielens(moviesDataFrame, givenGenre)
    print(f"- The dataset contains {len(moviesByGenre)} movies with the genre '{givenGenre}'!")
    # Test#5 - Get movies by the main genres
    print(f"\n- Fetching movies by the main genres {mainGenres} ...")
    mainGenresMoviesDataFrame = filterMoviesWithMainGenres(moviesDataFrame)
    print(f"- The dataset contains {len(mainGenresMoviesDataFrame)} movies with the main genres!")
    print(f"- A sample of the movies with the main genres: \n{mainGenresMoviesDataFrame.head(3)}")
    # Test#6 - Model movies data with binarized genres
    moviesDFBinarizedGenres = binarizeMovieGenres(moviesDataFrame)
    print(f"\n- The movies data with binarized genres is as below: \n{moviesDFBinarizedGenres.head(3)}")
    # Test#7 - Augment the movies data with the binarized genres
    augmentedMoviesDataFrame = augmentMoviesDFWithBinarizedGenres(moviesDataFrame, moviesDFBinarizedGenres)
    print(f"\n- The movie data augmented with binary genres is as below: \n{augmentedMoviesDataFrame.head(3)}")
    # Test#8 - Reading user-driven data
    print(f"\n- Reading dataset's user-driven data and fetching them into a DataFrame ...")
    ratingsDataFrame = loadDataFromCSV(os.path.join(datasetPath, "ratings.csv"))
    if ratingsDataFrame is None:
        return
    # Test#9 - Counting the number of ratings
    ratingsCount = len(ratingsDataFrame)
    print(f"- The dataset contains {ratingsCount} ratings!")
    # Test#10 - Some samples of the movies
    print(f"- The structure of the user-ratings data is as below:\n{ratingsDataFrame.head(3)}")
    # Test#11 - Merging the movies and ratings DataFrames
    print(f"\n- Merging the movies (of the main genres) and ratings DataFrames ...")
    mergedDataFrame = mergeMainGenreMoviesDFWithRatingsDF(augmentedMoviesDataFrame, ratingsDataFrame)
    print(f"- The merged DataFrame has {len(mergedDataFrame)} items, such as:\n{mergedDataFrame.head(3)}")