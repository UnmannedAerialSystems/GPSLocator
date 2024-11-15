import random
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans


# Define the dimensions of the plot and the box
width = 150
height = 25
padding = 10

# target types
targets = {
    0: ('person', 'red', 'o'),          
    1: ('car', 'green', 'o'),           
    2: ('motorcycle', 'blue', 'o'),     
    3: ('airplane', 'orange', 'o'),     
    4: ('bus', 'purple', 'o'),          
    5: ('boat', 'brown', 'o'),          
    6: ('stop sign', 'pink', 'o'),      
    7: ('snowboard', 'gray', 'o'),          
    8: ('umbrella', 'cyan', 'o'),           
    9: ('sports ball', 'magenta', 'o'), 
    10: ('baseball bat', 'yellow', 'o'),    
    11: ('bed/mattress', 'red', 'x'),       
    12: ('tennis racket', 'green', 'x'),    
    13: ('suitcase', 'blue', 'x'),      
    14: ('skis', 'orange', 'x')
}



def generateTargets():
    # Randomly select 4 numbers from 0-14
    random_numbers = random.sample(range(15), 4)

    # Generate 4 random points within the box dimensions
    points = []
    for _ in range(4):

        # generate coordinates
        x = random.uniform(0, width)
        y = random.uniform(0, height)

        # generate label
        index = random.randint(0, len(random_numbers) - 1)
        class_vector = generateClassVector(random_numbers[index])
        del random_numbers[index] # remove the label from the list

        object_vector = [x, y] + class_vector

        points.append(object_vector)

    return points


def generateClassVector(true_label, error=False, error_size=0.1):
    # Initialize the class vector with small random scores
    class_vector = [random.uniform(0, 0.8) for _ in range(15)]
    
    if error:
        # Randomly select a label that is not the true label
        false_label = random.choice([label for label in range(15) if label != true_label])
        class_vector[false_label] = random.uniform(0.81, 0.999)
        class_vector[true_label] = random.uniform(0.8 - error_size, 0.8)
    else:
        # Set the score for the true label to a high value
        class_vector[true_label] = random.uniform(0.81, 0.999)  # High value for the true label
    
    return class_vector


def scramblePoint(point, scramble_range, correctness):

    x, y = point[:2]
    class_vector = point[2:]

    # Randomly select a new point within the range
    new_x = x + random.uniform(-scramble_range, scramble_range)
    new_y = y + random.uniform(-scramble_range, scramble_range)

    # Randomly change the label with a certain probability
    if random.random() > correctness:
        new_vector = generateClassVector(np.argmax(class_vector), error=True, error_size = 1 - correctness)
    else:
        new_vector = generateClassVector(np.argmax(class_vector))
    
    return [new_x, new_y] + new_vector


def scramblePoints(points, scramble_range, correctness, num_scrambles):

    new_points = []

    for point in points:
        for _ in range(num_scrambles):
            new_point = scramblePoint(point, scramble_range, correctness)
            new_points.append(new_point)
    
    return new_points


def plotScrambledPoints(points, new_points):
    # Calculate the center of the plot
    center_x = width / 2
    center_y = height / 2

    # Calculate the coordinates of the box
    box_x = center_x - width / 2
    box_y = center_y - height / 2

    # Create the plot
    plt.figure(figsize=((width + 2 * padding) / 10, (height + 2 * padding) / 10))

    # Add the box to the plot
    plt.gca().add_patch(plt.Rectangle((box_x, box_y), width, height, fill=None, edgecolor='black', linewidth=1.5))

    # Add the original points to the plot
    for point in points:
        x, y = point[:2]
        class_vector = point[2:]
        label = np.argmax(class_vector)
        target, color, _ = targets[label]
        plt.scatter(x, y, color=color, marker='*', label=target)

    # Add the new points to the plot
    for point in new_points:
        x, y = point[:2]
        class_vector = point[2:]
        label = np.argmax(class_vector)
        target, color, marker = targets[label]
        plt.scatter(x, y, color=color, marker=marker)

    plt.legend(title="Target Types")


    # Set the limits of the plot with padding
    plt.xlim(box_x - padding, box_x + width + padding)
    plt.ylim(box_y - padding, box_y + height + padding)

    plt.grid(True)
    plt.title('Randomly Generated Airdrop Targets')

    # Show the plot
    #plt.show()


def clusterPoints(points, n_clusters=4):

    # Convert the points to a numpy array
    data = np.array(points)
    
    # Perform K-Means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(data)
    
    # Get the cluster labels
    labels = kmeans.labels_

    # Add cluster labels to the points
    for point in points:
        point += [labels[points.index(point)]]
    
    return points


def plotClusteredPoints(points, clusteredPoints):
    # Calculate the center of the plot
    center_x = width / 2
    center_y = height / 2

    # Calculate the coordinates of the box
    box_x = center_x - width / 2
    box_y = center_y - height / 2

    # Create the plot
    plt.figure(figsize=((width + 2 * padding) / 10, (height + 2 * padding) / 10))

    # Add the box to the plot
    plt.gca().add_patch(plt.Rectangle((box_x, box_y), width, height, fill=None, edgecolor='black', linewidth=1.5))

    # Add the points to the plot
    for point in points:
        
        x, y = point[:2]
        class_vector = point[2:]
        label = np.argmax(class_vector)
        target, color, _ = targets[label]
        plt.scatter(x, y, color=color, marker='*', label=target)

    # Add the clusters to the plot
    for point in clusteredPoints:
        x, y = point[:2]
        class_vector = point[2:-1]
        label = point[-1]
        plt.scatter(x, y, color='black', marker='x')

    plt.legend(title="Target Types")

    # Set the limits of the plot with padding
    plt.xlim(box_x - padding, box_x + width + padding)
    plt.ylim(box_y - padding, box_y + height + padding)

    plt.grid(True)
    plt.title('Randomly Generated Airdrop Targets')

    # Show the plot
    plt.show()


def findCentroid(clusteredPoints, cluster):
    # Filter the points that belong to the cluster
    cluster_points = [point for point in clusteredPoints if point[-1] == cluster]

    centroid = np.zeros(17)
    for point in cluster_points:
        centroid += np.array(point[:-1])
    
    return centroid / len(cluster_points)


def plotCentroids(points, clusteredPoints, n_clusters=4):

    # Calculate the center of the plot
    center_x = width / 2
    center_y = height / 2

    # Calculate the coordinates of the box
    box_x = center_x - width / 2
    box_y = center_y - height / 2

    # Create the plot
    plt.figure(figsize=((width + 2 * padding) / 10, (height + 2 * padding) / 10))

    # Add the box to the plot
    plt.gca().add_patch(plt.Rectangle((box_x, box_y), width, height, fill=None, edgecolor='black', linewidth=1.5))

    for cluster in range(n_clusters):
        centroid = findCentroid(clusteredPoints, cluster)
        x, y = centroid[:2]
        class_vector = centroid[2:-1]
        label = np.argmax(class_vector)
        target, color, marker = targets[label]
        plt.scatter(x, y, color=color, marker=marker, label=f'Cluster {cluster}')

    for point in points:
        x, y = point[:2]
        class_vector = point[2:]
        label = np.argmax(class_vector)
        target, color, _ = targets[label]
        plt.scatter(x, y, color=color, marker='*', label=target)
    

    error = calculateError(points, clusteredPoints)
    plt.title(f'Error: {error}m')
    plt.legend(title="Target Types")
    plt.show()


def calculateError(points, clusteredPoints):

    centroids = []
    for cluster in range(4):
        centroid = findCentroid(clusteredPoints, cluster)
        centroids.append(centroid)
    
    error = 0

    # for each centroid
    for centroid in centroids:

        # find its class
        class_vector = centroid[2:-1]
        label = np.argmax(class_vector)

        match = False
        # find the point that matches the centroid
        for point in points:

            if np.argmax(point[2:]) == label:

                # add the distance between the point and the centroid to the error
                error += np.linalg.norm(centroid - point)
                match = True

        # If the centroid does not match any of the points
        if not match:
            error += 1
    
    # return the average error in meters
    return error / len(centroids)

        

def testScrambleCount(min_scrambles, max_scrambles, num_tests, scramble_range=5, correctness=0.8, num_clusters=4):

    errors = []

    for i in range(min_scrambles, max_scrambles + 1):

        error = 0

        for _ in range(num_tests):
            points = generateTargets()
            new_points = scramblePoints(points, scramble_range, correctness, i)
            clusteredPoints = clusterPoints(new_points, num_clusters)
            error += calculateError(points, clusteredPoints)
            print(f"Percent complete: {i * 100 // max_scrambles}%", end='\r')


        errors.append(error / num_tests)
    print(errors)

    plt.plot(range(min_scrambles, max_scrambles + 1), errors)
    plt.xlabel('Number of scrambles')
    plt.ylabel('Average error (m)')
    plt.title('Effect of more samples on clustering accuracy')
    plt.show()



def testScrambleRange(min_range, max_range, num_tests, scrambles=10, correctness=0.8, num_clusters=4):

    errors = []

    for i in range(min_range, max_range + 1):

        error = 0

        for _ in range(num_tests):
            points = generateTargets()
            new_points = scramblePoints(points, i, correctness, scrambles)
            clusteredPoints = clusterPoints(new_points, num_clusters)
            error += calculateError(points, clusteredPoints)
            print(f"Percent complete: {i * 100 // max_range}%", end='\r')


        errors.append(error / num_tests)
    print(errors)

    plt.plot(range(min_range, max_range + 1), errors)
    plt.xlabel('Scramble range')
    plt.ylabel('Average error (m)')
    plt.title('Effect of spatial accuracy on clustering error')
    plt.show()


def testScrambleCorrectness(min_correctness, max_correctness, num_tests, scrambles=10, scramble_range=5, num_clusters=4):

    errors = []
    accuracies = []

    for i in range(min_correctness, max_correctness + 1):

        error = 0
        correct = 0

        for _ in range(num_tests):
            points = generateTargets()
            new_points = scramblePoints(points, scramble_range, i / 10, scrambles)
            clusteredPoints = clusterPoints(new_points, num_clusters)
            error += calculateError(points, clusteredPoints)

            # Calculate the accuracy of the label
            true_labels = [np.argmax(point[2:]) for point in points]
            predicted_labels = [np.argmax(point[2:-1]) for point in clusteredPoints]

            # for each true label
            for true_label in true_labels:
                
                if true_label in predicted_labels:
                    correct += 1


            print(f"Percent complete: {i * 100 // max_correctness}%", end='\r')

        accuracies.append(correct / (num_tests * 4) * 100)
        errors.append(error / num_tests)

    print(errors)

    plt.plot(range(min_correctness, max_correctness + 1), errors, label='Error')
    plt.xlabel('Correctness')
    plt.ylabel('Average error (m)')
    plt.title('Effect of label accuracy on clustering error')
    plt.show()

    plt.plot(range(min_correctness, max_correctness + 1), accuracies, label='Accuracy')
    plt.xlabel('Correctness')
    plt.ylabel('Accuracy (%)')
    plt.title('Effect of label accuracy on clustering accuracy')
    plt.show()


def main():

    '''points = generateTargets()
    new_points = scramblePoints(points, 5, 0.8, 10)
    #plotScrambledPoints(points, new_points)
    clusteredPoints = clusterPoints(new_points, n_clusters=4)
    plotClusteredPoints(points, clusteredPoints)
    plotCentroids(points, clusteredPoints, n_clusters=4)
    '''

    testScrambleCorrectness(1, 10, 1000)

if __name__ == "__main__":
    main()