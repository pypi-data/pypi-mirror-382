# Noise-Based-Random-Number-Generator
This random number generator leverages the inherent noise found in images captured by low-tech cameras to produce truly random numbers.

## INSTALLATION

    pip install noiserandom

## How it works

The program captures multiple images in JPG format and randomly selects one to generate a random number.
It utilizes images because older, low-tech cameras often contain significant white noise, which is a result of different random effects. Since those phenomena are inherently random, and if the camera is pointed at a dynamic scene such as a fish tank, a street, a forest , etc, the combination of a randomly chosen image and naturally occurring noise makes the process extremely difficult to reverse engineer.


## Noises.

Each of these factors contributes to the overall noise level in the final image. In high-end cameras, many of these sources are mitigated through advanced sensor designs, cooling systems, and image processing algorithms. Low-tech cameras, however, often expose these weaknesses more clearly, resulting in images with a higher noise floor especially under conditions of low light or high gain.

This list should provide a clear overview of the effects that contribute to image noise in lower-performing camera systems.

* Shot Noise

    * What it is: This is the inherent randomness in the arrival of photons at the sensor. Because light itself is made up of particles, the number that hit each sensor element will fluctuate, causing noise.

    * Why it’s significant: In low-light or lower sensitivity cameras, these variations become more apparent due to a lower photon count.

* Dark Current Noise

    * What it is: Even in complete darkness, sensor pixels generate electrons due to thermal energy. This random generation, called dark current, results in noise.

    * Why it’s significant: Lower-tech sensors, which often lack sophisticated cooling or low-noise design, show higher dark current noise especially noticeable in long exposures or higher temperatures.

* Read Noise

    * What it is: This noise arises during the process of converting the sensor’s charge to a digital signal. It includes disturbances from the sensor’s electronics, such as amplifiers and analog-to-digital converters (ADCs).

    * Why it’s significant: Cameras with less advanced electronics and lower-quality ADCs tend to exhibit higher levels of read noise.

* Thermal (Johnson-Nyquist) Noise

    * What it is: Thermal agitation of electrons within the sensor’s circuits creates random fluctuations, commonly known as thermal noise.

    * Why it’s significant: This becomes a more dominant effect in systems without effective thermal management or when the sensor is operating at higher temperatures.

* Fixed-Pattern Noise (FPN)

    * What it is: FPN is a pattern of noise that remains constant across images it originates from slight variations in sensor pixel responses or electronic circuits.

    * Why it’s significant: In low tech cameras where calibration and compensation routines are less robust, fixed-pattern noise can be noticeable as persistent spots or patterns in images.

* Quantization Noise

    * What it is: During the analog-to-digital conversion process, continuous signals are approximated by discrete digital values. The rounding (quantization) errors introduce additional noise.

    * Why it’s significant: Lower-resolution ADCs or sensors with limited bit depth (which are common in older or simpler cameras) result in higher quantization noise.

* Amplifier Noise

    * What it is: In many imaging systems, signals from the sensor are amplified before being digitized. The amplification process, especially when not using low-noise amplifiers, can introduce additional noise.

    * Why it’s significant: Low-tech cameras may employ more basic amplification hardware, leading to more pronounced noise artifacts.

* Interference and External Noise

    * What it is: Electromagnetic interference from nearby electronic components or poor shielding can add stray signals into the sensor’s output.

    * Why it’s significant: In less advanced camera designs, insufficient electromagnetic shielding can result in visible noise patterns or erratic pixel behavior.

## How to use

### Example 1 (Random Integer)

    #Firts import it

    from noiserandom import NoiseRandom

    #Then write the path that the images are going to be saved

    path = "images" #This must be an existing folder

    #After that create your object
    noise_random = NoiseRandom(path=path,strength=10) #The strength is the number of images (min=1)

    #Get your random number

    random_number = noise_random.randomInt()

    #print your random number

    print(random_number)

### Example 2 (Random Integer with 2048 bits)

    #Firts import it

    from noiserandom import NoiseRandom

    #Then write the path that the images are going to be saved

    path = "images" #This must be an existing folder

    #After that create your object
    noise_random = NoiseRandom(path=path,strength=10) #The strength is the number of images (min=1)

    #Get your random number

    random_number = noise_random.random2048()

    #print your random number

    print(random_number)

### Example 3 (Random Prime Integer with 2048 bits)


    #Firts import it

    from noiserandom import NoiseRandom

    #Then write the path that the images are going to be saved

    path = "images" #This must be an existing folder

    #After that create your object
    noise_random = NoiseRandom(path=path,strength=10) #The strength is the number of images (min=1)

    #Get your random number

    random_number = noise_random.randomPrime2048()

    #print your random number

    print(random_number)

### Example 4 (Get the bytes of the image scrambled)


    #Firts import it

    from noiserandom import NoiseRandom

    #Then write the path that the images are going to be saved

    path = "images" #This must be an existing folder

    #After that create your object
    noise_random = NoiseRandom(path=path,strength=10) #The strength is the number of images (min=1)

    #Get your bytes

    random_bytes = noise_random.randomInt(True)

    #print your bytes

    print(random_bytes)